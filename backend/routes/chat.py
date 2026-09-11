from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional, Dict
from models.chat import (
    ChatResponse, ChatListItem, MessageRequest, 
    MessageResponse, Message
)
from models.user import TokenData
from services.db_service import db_service
from services.llm_service import llm_service
from services.tools_service import tools_service
from services.query_validator_service import query_validator, GreetingHandler
from services.auth_service import get_current_user
from datetime import datetime
from zoneinfo import ZoneInfo
import json
import re

router = APIRouter(prefix="/api/chats", tags=["chats"])


async def extract_pending_booking(messages: List[dict]) -> Optional[Dict]:
    """
    Extract pending booking details from recent conversation.
    Looks for confirmation messages that contain doctor, date, time, and reason.
    """
    # Look through recent assistant messages for booking confirmation pattern
    for msg in reversed(messages):
        if msg.get("role") != "assistant":
            continue
        
        content = msg.get("content", "")
        
        # Check if this is a confirmation message
        if "confirm" not in content.lower() and "YES" not in content:
            continue
        
        # Try to extract booking details
        booking = {}
        
        # Extract doctor name (look for "Dr. Name" pattern)
        doctor_match = re.search(r'(?:Doctor|Dr\.?)\s*:?\s*(Dr\.?\s*[\w\s]+?)(?:\s*\(|\s*-|\s*\n|$)', content, re.IGNORECASE)
        if doctor_match:
            booking["doctor_name"] = doctor_match.group(1).strip()
        
        # Extract specialization
        spec_match = re.search(r'(?:Specialization|Specialty)\s*:?\s*([\w\s]+?)(?:\s*\n|$)', content, re.IGNORECASE)
        if spec_match:
            booking["specialization"] = spec_match.group(1).strip()
        else:
            # Try to get from parentheses after doctor name
            paren_match = re.search(r'Dr\.?\s*[\w\s]+?\s*\(([\w\s]+?)\)', content)
            if paren_match:
                booking["specialization"] = paren_match.group(1).strip()
        
        # Extract date (YYYY-MM-DD format)
        date_match = re.search(r'(?:Date)\s*:?\s*(\d{4}-\d{2}-\d{2})', content, re.IGNORECASE)
        if date_match:
            booking["appointment_date"] = date_match.group(1)
        
        # Extract time
        time_match = re.search(r'(?:Time)\s*:?\s*(\d{1,2}:\d{2}(?:\s*(?:AM|PM)?)?)', content, re.IGNORECASE)
        if time_match:
            booking["appointment_time"] = time_match.group(1).strip()
        
        # Extract reason
        reason_match = re.search(r'(?:Reason)\s*:?\s*(.+?)(?:\s*\n|Type|$)', content, re.IGNORECASE)
        if reason_match:
            booking["reason"] = reason_match.group(1).strip()
        
        # Extract hospital
        hospital_match = re.search(r'(?:Hospital)\s*:?\s*(.+?)(?:\s*\n|$)', content, re.IGNORECASE)
        if hospital_match:
            booking["hospital_name"] = hospital_match.group(1).strip()
        
        # Now try to find doctor_id from previous get_doctors response
        if booking.get("doctor_name"):
            doctor_id = find_doctor_id_from_context(messages, booking["doctor_name"])
            if doctor_id:
                booking["doctor_id"] = doctor_id
            else:
                # Fallback: lookup doctor from database by name
                doctor = await find_doctor_by_name(booking["doctor_name"])
                if doctor:
                    booking["doctor_id"] = doctor.get("id")
                    # Also fill in missing specialization and hospital from database
                    if not booking.get("specialization"):
                        booking["specialization"] = doctor.get("specialization")
                    if not booking.get("hospital_name"):
                        booking["hospital_name"] = doctor.get("hospital")
                    print(f"[DEBUG] Found doctor from database: {doctor.get('id')} - {doctor.get('name')}")
        
        # Validate we have all required fields
        required = ["doctor_id", "doctor_name", "specialization", "appointment_date", "appointment_time", "reason"]
        if all(field in booking for field in required):
            return booking
    
    return None


def find_doctor_id_from_context(messages: List[dict], doctor_name: str) -> Optional[str]:
    """Find doctor ID from previous messages that listed doctors"""
    for msg in reversed(messages):
        if msg.get("role") != "assistant":
            continue
        
        content = msg.get("content", "")
        
        # Look for doctor ID pattern near the doctor name
        # Pattern: ID: doc_XXX or 🆔 ID: doc_XXX
        if doctor_name.split()[-1] in content:  # Match last name
            id_match = re.search(r'ID:\s*(doc_\d+)', content)
            if id_match:
                # Find the ID that appears near this doctor's name
                # Split content by doctor entries and find the one with matching name
                lines = content.split('\n')
                current_doctor_id = None
                for line in lines:
                    if 'ID:' in line:
                        match = re.search(r'ID:\s*(doc_\d+)', line)
                        if match:
                            current_doctor_id = match.group(1)
                    if doctor_name.split()[-1] in line and current_doctor_id:
                        return current_doctor_id
                    # Reset if new doctor entry
                    if line.startswith('**') and 'Dr.' in line:
                        id_match = re.search(r'ID:\s*(doc_\d+)', content[content.find(line):])
                
                # Fallback: just return the first doctor ID found if name matches
                for i, line in enumerate(lines):
                    if doctor_name.split()[-1] in line:
                        # Search nearby lines for ID
                        for j in range(max(0, i-3), min(len(lines), i+5)):
                            id_match = re.search(r'ID:\s*(doc_\d+)', lines[j])
                            if id_match:
                                return id_match.group(1)
    
    # Last resort: return None, will be looked up from database
    return None


async def find_doctor_by_name(doctor_name: str) -> Optional[Dict]:
    """Find doctor in database by name"""
    doctors = await db_service.get_all_doctors()
    # Clean the doctor name
    clean_name = doctor_name.replace("Dr.", "").replace("Dr", "").strip()
    
    for doc in doctors:
        doc_clean_name = doc.get("name", "").replace("Dr.", "").replace("Dr", "").strip()
        # Match by last name or full name
        if clean_name.lower() in doc_clean_name.lower() or doc_clean_name.lower() in clean_name.lower():
            return doc
    
    return None

@router.post("", response_model=ChatResponse)
async def create_chat(current_user: TokenData = Depends(get_current_user)):
    """Create a new chat for the authenticated user"""
    # Start with a default title, will be updated with first message
    chat_id = await db_service.create_chat("New Chat", current_user.user_id)
    chat = await db_service.get_chat(chat_id, current_user.user_id)
    
    if not chat:
        raise HTTPException(status_code=500, detail="Failed to create chat")
    
    return ChatResponse(**chat)

@router.get("", response_model=List[ChatListItem])
async def get_all_chats(current_user: TokenData = Depends(get_current_user)):
    """Get all chats for the authenticated user (for sidebar)"""
    chats = await db_service.get_all_chats(current_user.user_id)
    return [ChatListItem(**chat) for chat in chats]

@router.get("/{chat_id}", response_model=ChatResponse)
async def get_chat(chat_id: str, current_user: TokenData = Depends(get_current_user)):
    """Get a specific chat with all messages (only if owned by user)"""
    chat = await db_service.get_chat(chat_id, current_user.user_id)
    
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    
    return ChatResponse(**chat)

@router.delete("/{chat_id}")
async def delete_chat(chat_id: str, current_user: TokenData = Depends(get_current_user)):
    """Delete a chat (only if owned by user)"""
    success = await db_service.delete_chat(chat_id, current_user.user_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Chat not found")
    
    return {"message": "Chat deleted successfully"}

@router.post("/{chat_id}/messages", response_model=MessageResponse)
async def send_message(
    chat_id: str, 
    message: MessageRequest, 
    current_user: TokenData = Depends(get_current_user)
):
    """Send a message and get LLM response"""
    # Verify chat exists and belongs to user
    chat = await db_service.get_chat(chat_id, current_user.user_id)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    
    # Check if the message is a greeting
    if GreetingHandler.is_greeting(message.content):
        # Save the user message
        await db_service.add_message(chat_id, "user", message.content)
        
        # Get greeting response
        greeting_response = GreetingHandler.get_greeting_response(message.content)
        
        # Save the greeting response
        await db_service.add_message(chat_id, "assistant", greeting_response)
        
        # Return the greeting response
        return MessageResponse(
            role="assistant",
            content=greeting_response,
            timestamp=datetime.now(ZoneInfo("Asia/Kolkata"))
        )
    
    # Validate that the query is medical-related
    is_medical, rejection_message = query_validator.is_medical_query(message.content)
    
    if not is_medical:
        # Save the user message anyway (for history)
        await db_service.add_message(chat_id, "user", message.content)
        
        # Save the rejection response
        await db_service.add_message(chat_id, "assistant", rejection_message)
        
        # Return the rejection response
        return MessageResponse(
            role="assistant",
            content=rejection_message,
            timestamp=datetime.now(ZoneInfo("Asia/Kolkata"))
        )
    
    # Save user message
    await db_service.add_message(chat_id, "user", message.content)
    
    # Update chat title if this is the first message
    if len(chat.get("messages", [])) == 0:
        # Use the complete first message as title
        title = message.content
        await db_service.update_chat_title(chat_id, title)
    
    # Get last 10 messages for context (needed for multi-step booking flow)
    recent_messages = await db_service.get_recent_messages(chat_id, count=10)
    
    # Format messages for LLM
    formatted_messages = [
        {"role": msg["role"], "content": msg["content"]}
        for msg in recent_messages
    ]
    
    # Add current message if not already in recent messages
    if not formatted_messages or formatted_messages[-1]["content"] != message.content:
        formatted_messages.append({"role": "user", "content": message.content})
    
    # Check if user is confirming a booking (YES response)
    user_confirming = message.content.strip().lower() in ["yes", "confirm", "ok", "sure", "yeah", "yep", "y"]
    pending_booking = None
    
    # If user is confirming, check if there's a pending booking in recent messages
    if user_confirming:
        pending_booking = await extract_pending_booking(recent_messages)
        print(f"[DEBUG] User confirming: {user_confirming}, Pending booking: {pending_booking}")
    
    # Get LLM response with tools enabled
    assistant_response = await llm_service.get_completion(formatted_messages, tools_available=True)
    
    # Debug: Log the raw LLM response
    print(f"[DEBUG] Raw LLM Response: {assistant_response[:500] if len(assistant_response) > 500 else assistant_response}")
    
    # Check if LLM wants to call a tool
    tool_call = llm_service.parse_tool_call(assistant_response)
    
    print(f"[DEBUG] Parsed tool_call: {tool_call}")
    
    # FALLBACK: If user said YES but LLM didn't call book_appointment, force the booking
    if user_confirming and pending_booking and not tool_call:
        print(f"[DEBUG] FALLBACK: Forcing booking with pending details: {pending_booking}")
        tool_call = ("", "book_appointment", pending_booking)
    
    if tool_call:
        before_text, tool_name, parameters = tool_call
        
        print(f"[DEBUG] Executing tool: {tool_name} with parameters: {parameters}")
        
        # Execute the tool
        tool_result = await tools_service.execute_tool(tool_name, parameters, current_user.user_id)
        
        print(f"[DEBUG] Tool result: {tool_result}")
        
        # Format the tool result for display
        if tool_result.get("success"):
            result_text = ""
            
            if tool_name == "get_doctors":
                doctors = tool_result.get("data", [])
                if doctors:
                    spec = parameters.get("specialization", "")
                    if spec:
                        result_text = f"Here are the available **{spec}** specialists:\n\n"
                    else:
                        result_text = "Here are all available doctors:\n\n"
                    
                    for i, doc in enumerate(doctors, 1):
                        result_text += f"**{i}. {doc['name']}** - {doc['specialization']}\n"
                        result_text += f"   � ID: {doc.get('id', 'N/A')}\n"
                        result_text += f"   🏥 Hospital: {doc.get('hospital', 'N/A')}\n"
                        result_text += f"   📅 Available Days: {', '.join(doc.get('available_days', []))}\n"
                        result_text += f"   ⏰ Time Slots: {', '.join(doc.get('available_time_slots', []))}\n"
                        result_text += f"   💰 Consultation Fee: ₹{doc.get('consultation_fee', 'N/A')}\n"
                        result_text += f"   ⭐ Rating: {doc.get('rating', 'N/A')}/5\n"
                        result_text += f"   👥 Patients Treated: {doc.get('patients_count', 'N/A')}\n\n"
                    
                    result_text += "---\n**To book an appointment, please tell me:**\n"
                    result_text += "1. Which doctor would you like to see?\n"
                    result_text += "2. What date? (Format: YYYY-MM-DD, e.g., 2026-02-15)\n"
                    result_text += "3. What time? (e.g., 10:00 AM or 14:30)\n"
                    result_text += "4. Reason for visit?\n"
                else:
                    result_text = "No doctors found matching your criteria. Please try a different specialization."
            
            elif tool_name == "get_hospitals":
                hospitals = tool_result.get("data", [])
                if hospitals:
                    result_text = "🏥 **Here are the hospitals:**\n\n"
                    for i, hosp in enumerate(hospitals, 1):
                        result_text += f"**{i}. {hosp['name']}** - {hosp['city']}\n"
                        result_text += f"   📍 Address: {hosp['address']}\n"
                        result_text += f"   🏷️ Specializations: {', '.join(hosp['specializations'])}\n"
                        result_text += f"   🚨 Emergency: {'✅ Yes' if hosp['emergency_available'] else '❌ No'}\n"
                        result_text += f"   📞 Contact: {hosp.get('phone', hosp.get('contact', 'N/A'))}\n\n"
                else:
                    result_text = "No hospitals found matching your criteria."
            
            elif tool_name == "book_appointment":
                result_text = "✅ **Appointment Booked Successfully!**\n\n"
                appointment = tool_result.get("data", {})
                if appointment:
                    result_text += "📋 **Your Appointment Details:**\n"
                    result_text += f"   🆔 Booking ID: {appointment.get('id', 'N/A')}\n"
                    result_text += f"   👨‍⚕️ Doctor: {appointment.get('doctor_name')}\n"
                    result_text += f"   🏷️ Specialization: {appointment.get('specialization')}\n"
                    result_text += f"   🏥 Hospital: {appointment.get('hospital_name', 'N/A')}\n"
                    result_text += f"   📅 Date: {appointment.get('appointment_date')}\n"
                    result_text += f"   ⏰ Time: {appointment.get('appointment_time')}\n"
                    result_text += f"   📝 Reason: {appointment.get('reason')}\n"
                    result_text += f"   ✔️ Status: {appointment.get('status', 'Scheduled').upper()}\n\n"
                    result_text += "📌 **Please Note:**\n"
                    result_text += "- Arrive 15 minutes before your appointment\n"
                    result_text += "- Bring your ID and any relevant medical records\n"
                    result_text += "- You can view all your bookings in the **Appointments** section\n\n"
                    result_text += "Need to cancel or reschedule? Just let me know!"
            
            elif tool_name == "change_password":
                result_text = "✅ **Password Changed Successfully!**\n\nYour account password has been updated. Please use your new password for future logins."
            
            elif tool_name == "get_user_appointments":
                appointments = tool_result.get("data", [])
                if appointments:
                    result_text = "📋 **Your Appointments:**\n\n"
                    for i, apt in enumerate(appointments, 1):
                        status_icon = "✅" if apt.get('status') == 'scheduled' else "⏳" if apt.get('status') == 'pending' else "✔️"
                        result_text += f"**{i}. {apt.get('appointment_date')} at {apt.get('appointment_time')}**\n"
                        result_text += f"   👨‍⚕️ Doctor: {apt.get('doctor_name')} ({apt.get('specialization')})\n"
                        result_text += f"   🏥 Hospital: {apt.get('hospital_name', 'N/A')}\n"
                        result_text += f"   📝 Reason: {apt.get('reason')}\n"
                        result_text += f"   {status_icon} Status: {apt.get('status')}\n\n"
                else:
                    result_text = "📋 You don't have any appointments scheduled yet.\n\nWould you like to book an appointment? Just say 'book appointment' and I'll help you!"
            
            # Combine before text with result
            final_response = before_text + "\n\n" + result_text if before_text else result_text
        else:
            # Tool failed, report error
            error_msg = tool_result.get("error", "An error occurred")
            final_response = f"I tried to help but encountered an issue: {error_msg}"
        
        assistant_response = final_response.strip()
    
    # Save assistant message
    await db_service.add_message(chat_id, "assistant", assistant_response)
    
    return MessageResponse(
        role="assistant",
        content=assistant_response,
        timestamp=datetime.now(ZoneInfo("Asia/Kolkata"))
    )

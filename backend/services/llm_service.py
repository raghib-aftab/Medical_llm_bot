import httpx
import json
import re
from typing import List, Dict, Optional, Tuple
from config import settings


class LLMService:
    def __init__(self):
        self.url = settings.llm_api_url
        self.api_key = settings.llm_api_key
        self.model = settings.llm_model
    
    async def get_completion(self, messages: List[Dict[str, str]], tools_available: bool = False) -> str:
        """
        Get a completion from the LLM API.
        
        Args:
            messages: List of message dicts with 'role' and 'content' keys
            
        Returns:
            The assistant's response content
        """
        try:
            # Build system prompt based on tools availability
            base_prompt = """You are a medical assistance AI trained to provide accurate, evidence-based medical information.

Respond in a calm, professional, and patient-friendly manner.
Use clear, simple, and respectful language.
Avoid unnecessary technical jargon unless the user asks for it.
Be concise but complete.
Do not invent facts.
If you are unsure or information is missing, say so clearly.

CRITICAL EMERGENCY OVERRIDE (HIGHEST PRIORITY):
If the user describes symptoms suggesting a medical emergency
(e.g., chest pain, heart attack, stroke, unconsciousness, severe bleeding, difficulty breathing):
1. Immediately instruct the user to call emergency services (112).
2. Clearly state that this is an emergency.
3. Provide only basic, general first-aid guidance.
4. Use a numbered list with no more than 5 steps.
5. Do not repeat instructions.
6. Do not give diagnoses or personalized treatment.
7. Stop the response after emergency guidance.

For non-emergency medical questions:
- Explain conditions, medicines, tests, and treatments accurately.
- Focus on established medical knowledge.
- Keep answers within 4–6 sentences unless detailed explanation is requested.

When defining a disease:
- Start with a one-sentence definition.
- Briefly explain the core biological mechanism.
- Mention common causes or types if relevant.
- Keep the explanation patient-friendly.

When discussing treatment or medication:
- Describe general treatment approaches only.
- Do not provide personalized treatment plans.
- Do not give drug dosages unless explicitly asked and appropriate.
- Use generic drug names when possible.

When asked about symptoms:
- List common symptoms first.
- Avoid repetition.
- Do not diagnose based on symptoms alone.

Never repeat the same sentence or instruction in one response.

Emergency note: I cannot replace emergency medical care. Call 112 immediately for life-threatening symptoms.

Developer details:
This LLM is trained by Rishabh Kushwaha and Reshma using a Medical LLaMA-based architecture.
"""

            tools_prompt = """

=== ASSISTANT ACTIONS - CONVERSATIONAL FLOW ===

You can help users with appointments, hospitals, doctors, and account management. 
ALWAYS follow the step-by-step conversational flow below. DO NOT skip steps.

---

### 1. SHOW DOCTORS (When user asks "list doctors", "show doctors", "available doctors"):

- Immediately show all doctors:
  TOOL_CALL: {"name": "get_doctors", "parameters": {}}

- If user asks for specific specialty (e.g., "show cardiologists", "list dermatologists"):
  TOOL_CALL: {"name": "get_doctors", "parameters": {"specialization": "specialty"}}

- The system will display doctors with their ID, name, hospital, availability, fee, and rating.
- After showing doctors, wait for user to select one for booking.

---

### 2. BOOKING APPOINTMENT - Step by Step Flow:

**STEP 1: User Selects Doctor**
- After seeing doctor list, user will say which doctor they want (e.g., "I want Dr. Sarah Johnson" or "book with doc_001")
- Note the doctor's ID (like doc_001), name, specialization, and hospital from the list.

**STEP 2: Collect Date, Time, and Reason**
- Ask user for:
  - Date (format: YYYY-MM-DD, e.g., 2026-02-15)
  - Time (format: HH:MM, e.g., 10:00 or 14:30)
  - Reason for visit
  
- If user provides all in one message, proceed to confirmation.
- If missing any, ask for the missing information.

**STEP 3: Confirm Before Booking**
- Summarize ALL details and ask for confirmation:
  
  "📋 **Please confirm your appointment:**
   - 👨‍⚕️ Doctor: Dr. [name] ([specialization])
   - 🏥 Hospital: [hospital_name]  
   - 📅 Date: [YYYY-MM-DD]
   - ⏰ Time: [HH:MM]
   - 📝 Reason: [reason]
   
   Type **YES** to confirm or **NO** to cancel."

**STEP 4: Book Only After YES**
- ONLY when user confirms with YES/yes/confirm/ok:
  TOOL_CALL: {"name": "book_appointment", "parameters": {"doctor_id": "doc_XXX", "doctor_name": "Dr. Name", "specialization": "Specialty", "appointment_date": "YYYY-MM-DD", "appointment_time": "HH:MM", "reason": "reason text"}}

- After successful booking, user will receive a confirmation email with appointment details.

- If user says NO/no/cancel:
  → Say "No problem! Let me know if you'd like to book a different appointment."

---

### 3. SHOW HOSPITALS:

- If user asks "show hospitals", "list hospitals", "hospital list":
  TOOL_CALL: {"name": "get_hospitals", "parameters": {}}

- If user asks for specific city (e.g., "hospitals in Delhi"):
  TOOL_CALL: {"name": "get_hospitals", "parameters": {"city": "Delhi"}}

- If user asks for emergency hospitals:
  TOOL_CALL: {"name": "get_hospitals", "parameters": {"emergency_only": true}}

---

### 4. VIEW MY APPOINTMENTS:

- If user asks "show my appointments", "my bookings", "my appointments", "booking history":
  TOOL_CALL: {"name": "get_user_appointments", "parameters": {}}

---

### 5. CANCEL APPOINTMENT:

- If user asks to cancel an appointment:
  - First get their appointments:
    TOOL_CALL: {"name": "get_user_appointments", "parameters": {}}
  - Show them the list with appointment IDs
  - Ask which appointment to cancel
  - When user specifies, confirm before cancelling

- After user confirms cancellation (says YES/confirm/ok):
  TOOL_CALL: {"name": "cancel_appointment", "parameters": {"appointment_id": "apt_XXXXX"}}

- User will receive an email notification when appointment is cancelled.

---

### 6. CHANGE PASSWORD:

- If user asks to change password, ask for current and new password.
- Then call:
  TOOL_CALL: {"name": "change_password", "parameters": {"current_password": "xxx", "new_password": "yyy"}}

---

=== CRITICAL RULES ===
1. NEVER book without explicit YES confirmation from user
2. ALWAYS use the doctor_id (e.g., doc_001) from the doctor list when booking
3. Date format MUST be YYYY-MM-DD (e.g., 2026-02-15)
4. Time format MUST be HH:MM (e.g., 10:00, 14:30)
5. Collect ALL required fields before showing confirmation
6. Be conversational and helpful throughout

=== HOW TO USE TOOLS ===
When you need to perform an action, you MUST respond with TOOL_CALL in this exact format:
TOOL_CALL: {"name": "tool_name", "parameters": {...}}

**CRITICAL**: You CANNOT book an appointment just by saying "Appointment booked". 
You MUST output the TOOL_CALL with book_appointment to actually book.
If user says YES to confirm, you MUST respond with:
TOOL_CALL: {"name": "book_appointment", "parameters": {"doctor_id": "...", "doctor_name": "...", "specialization": "...", "appointment_date": "YYYY-MM-DD", "appointment_time": "HH:MM", "reason": "..."}}

WITHOUT the TOOL_CALL, the appointment will NOT be saved to the database.
"""

            SYSTEM_PROMPT = base_prompt + (tools_prompt if tools_available else "")


            system_message = {
                "role": "system",
                "content": SYSTEM_PROMPT
            }
            
            # Ensure system message is first, then add conversation messages
            formatted_messages = [system_message]
            
            # Filter out system messages from history
            non_system_messages = [msg for msg in messages if msg["role"] != "system"]
            
            # Keep more messages for multi-step flows (booking appointments needs context)
            # Increased to 10 messages to ensure full booking flow context is maintained
            recent_messages = non_system_messages[-10:] if len(non_system_messages) > 10 else non_system_messages
            
            # Add recent conversation history
            for msg in recent_messages:
                formatted_messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.url,
                    json={
                        "model": self.model,
                        "messages": formatted_messages,
                        "temperature": 0.3,
                        "max_tokens": 1024,
                    },
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    timeout=60.0
                )
                
                response.raise_for_status()
                data = response.json()
                
                # Log finish reason for debugging
                if "choices" in data and len(data["choices"]) > 0:
                    finish_reason = data["choices"][0].get("finish_reason", "unknown")
                    print(f"LLM Response - finish_reason: {finish_reason}")
                    
                    # Check if response was truncated
                    if finish_reason == "length":
                        print("WARNING: Response was truncated due to max_tokens limit")
                    
                    return data["choices"][0]["message"]["content"]
                else:
                    return "I apologize, but I couldn't generate a response."
                    
        except httpx.HTTPStatusError as e:
            print(f"LLM API HTTP Error: {e}")
            return f"I apologize, but I'm having trouble connecting to the medical assistant service. Please try again later. {e}"
        except httpx.RequestError as e:
            print(f"LLM API Request Error: {e}")
            return f"I apologize, but I'm having trouble connecting to the medical assistant service. Please try again later. {e}"
        except Exception as e:
            print(f"Unexpected error: {e}")
            return f"An unexpected error occurred. Please try again. {e}"
    
    def parse_tool_call(self, response: str) -> Optional[Tuple[str, str, Dict]]:
        """
        Parse a tool call from the LLM response.
        
        Returns:
            Tuple of (before_text, tool_name, parameters) if tool call found, else None
            - before_text: Any text before the TOOL_CALL
            - tool_name: Name of the tool to call
            - parameters: Dictionary of parameters
        """
        # Look for TOOL_CALL: pattern and find the JSON after it
        tool_call_pattern = r'TOOL_CALL:\s*'
        match = re.search(tool_call_pattern, response, re.IGNORECASE)
        
        if not match:
            return None
        
        try:
            # Extract the text before tool call
            before_text = response[:match.start()].strip()
            
            # Get the text after TOOL_CALL:
            json_start = match.end()
            remaining_text = response[json_start:]
            
            # Find the matching braces for the JSON object
            # Start from the first { and count braces
            brace_start = remaining_text.find('{')
            if brace_start == -1:
                return None
            
            brace_count = 0
            json_end = -1
            for i, char in enumerate(remaining_text[brace_start:], start=brace_start):
                if char == '{':
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        json_end = i + 1
                        break
            
            if json_end == -1:
                return None
            
            # Extract and parse the JSON
            json_str = remaining_text[brace_start:json_end]
            tool_json = json.loads(json_str)
            tool_name = tool_json.get("name")
            parameters = tool_json.get("parameters", {})
            
            if not tool_name:
                return None
            
            return (before_text, tool_name, parameters)
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Failed to parse tool call: {e}")
            return None

llm_service = LLMService()

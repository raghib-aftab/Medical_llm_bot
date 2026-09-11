"""
Service for handling AI assistant tool/function calls.
This enables the LLM to perform actions like booking appointments, 
getting doctor/hospital lists, and changing passwords.
"""

import json
from typing import Dict, Any, List
from datetime import datetime
from services.db_service import db_service
from services.auth_service import get_password_hash, verify_password
from services.email_service import email_service


# Tool definitions that will be sent to the LLM
AVAILABLE_TOOLS = [
    {
        "name": "get_doctors",
        "description": "Get list of available doctors, optionally filtered by specialization. Use this when user asks about doctors, specialists, or wants to know who they can book an appointment with.",
        "parameters": {
            "type": "object",
            "properties": {
                "specialization": {
                    "type": "string",
                    "description": "Filter doctors by specialization (e.g., 'Cardiology', 'Dermatology', 'Pediatrics'). Leave empty to get all doctors."
                }
            }
        }
    },
    {
        "name": "get_hospitals",
        "description": "Get list of hospitals, optionally filtered by city, specialization, or emergency availability. Use when user asks about hospitals, medical centers, or emergency services.",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "Filter by city name"
                },
                "specialization": {
                    "type": "string",
                    "description": "Filter by specialization"
                },
                "emergency_only": {
                    "type": "boolean",
                    "description": "Set to true to show only hospitals with emergency services"
                }
            }
        }
    },
    {
        "name": "book_appointment",
        "description": "Book a medical appointment with a doctor. Use this when user explicitly wants to book, schedule, or make an appointment. ALWAYS confirm appointment details with user before calling this.",
        "parameters": {
            "type": "object",
            "properties": {
                "doctor_id": {
                    "type": "string",
                    "description": "The ID of the doctor (get from get_doctors tool first)"
                },
                "doctor_name": {
                    "type": "string",
                    "description": "The name of the doctor"
                },
                "specialization": {
                    "type": "string",
                    "description": "The doctor's specialization"
                },
                "appointment_date": {
                    "type": "string",
                    "description": "Date in YYYY-MM-DD format (e.g., 2026-02-10)"
                },
                "appointment_time": {
                    "type": "string",
                    "description": "Time in HH:MM format, 24-hour (e.g., 14:30)"
                },
                "reason": {
                    "type": "string",
                    "description": "Reason for the appointment"
                }
            },
            "required": ["doctor_id", "doctor_name", "specialization", "appointment_date", "appointment_time", "reason"]
        }
    },
    {
        "name": "change_password",
        "description": "Change the user's password. Use when user explicitly wants to change or update their password. ALWAYS ask for current password and new password.",
        "parameters": {
            "type": "object",
            "properties": {
                "current_password": {
                    "type": "string",
                    "description": "The user's current password"
                },
                "new_password": {
                    "type": "string",
                    "description": "The new password (must be at least 6 characters)"
                }
            },
            "required": ["current_password", "new_password"]
        }
    },
    {
        "name": "get_user_appointments",
        "description": "Get the user's appointment history. Use when user asks about their appointments, bookings, or medical schedule.",
        "parameters": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "cancel_appointment",
        "description": "Cancel a user's appointment. Use when user wants to cancel or remove an appointment. First use get_user_appointments to find the appointment ID.",
        "parameters": {
            "type": "object",
            "properties": {
                "appointment_id": {
                    "type": "string",
                    "description": "The ID of the appointment to cancel (get from get_user_appointments first)"
                }
            },
            "required": ["appointment_id"]
        }
    }
]


class ToolsService:
    """Service for executing AI tool/function calls"""
    
    async def execute_tool(self, tool_name: str, parameters: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """
        Execute a tool/function call
        
        Args:
            tool_name: Name of the tool to execute
            parameters: Parameters for the tool
            user_id: ID of the user making the request
            
        Returns:
            Dictionary with success status and result/error message
        """
        try:
            if tool_name == "get_doctors":
                return await self._get_doctors(parameters)
            elif tool_name == "get_hospitals":
                return await self._get_hospitals(parameters)
            elif tool_name == "book_appointment":
                return await self._book_appointment(parameters, user_id)
            elif tool_name == "change_password":
                return await self._change_password(parameters, user_id)
            elif tool_name == "get_user_appointments":
                return await self._get_user_appointments(user_id)
            elif tool_name == "cancel_appointment":
                return await self._cancel_appointment(parameters, user_id)
            else:
                return {
                    "success": False,
                    "error": f"Unknown tool: {tool_name}"
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _get_doctors(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Get list of doctors"""
        specialization = parameters.get("specialization")
        doctors = await db_service.get_all_doctors(specialization=specialization)
        
        return {
            "success": True,
            "data": doctors,
            "count": len(doctors)
        }
    
    async def _get_hospitals(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Get list of hospitals"""
        city = parameters.get("city")
        specialization = parameters.get("specialization")
        emergency_only = parameters.get("emergency_only", False)
        
        hospitals = await db_service.get_all_hospitals(
            city=city,
            specialization=specialization,
            emergency_only=emergency_only
        )
        
        return {
            "success": True,
            "data": hospitals,
            "count": len(hospitals)
        }
    
    async def _book_appointment(self, parameters: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """Book an appointment"""
        # Validate required fields
        required = ["doctor_id", "doctor_name", "specialization", "appointment_date", "appointment_time", "reason"]
        for field in required:
            if field not in parameters:
                return {
                    "success": False,
                    "error": f"Missing required field: {field}"
                }
        
        # Get hospital name from doctor info
        doctor = await db_service.get_doctor_by_id(parameters["doctor_id"])
        hospital_name = doctor.get("hospital") if doctor else parameters.get("hospital_name", "N/A")
        
        # Check for conflicts
        conflict = await db_service.check_appointment_conflict(
            doctor_id=parameters["doctor_id"],
            appointment_date=parameters["appointment_date"],
            appointment_time=parameters["appointment_time"]
        )
        
        if conflict:
            return {
                "success": False,
                "error": "This time slot is already booked. Please choose another time."
            }
        
        # Create appointment
        appointment_id = await db_service.create_appointment(
            user_id=user_id,
            doctor_id=parameters["doctor_id"],
            doctor_name=parameters["doctor_name"],
            specialization=parameters["specialization"],
            appointment_date=parameters["appointment_date"],
            appointment_time=parameters["appointment_time"],
            reason=parameters["reason"],
            hospital_name=hospital_name
        )
        
        appointment = await db_service.get_appointment_by_id(appointment_id)
        
        # Send confirmation email
        user = await db_service.get_user_by_id(user_id)
        if user:
            try:
                await email_service.send_appointment_confirmation(
                    email=user["email"],
                    name=user["name"],
                    doctor_name=parameters["doctor_name"],
                    specialization=parameters["specialization"],
                    appointment_date=parameters["appointment_date"],
                    appointment_time=parameters["appointment_time"],
                    hospital_name=hospital_name,
                    reason=parameters["reason"]
                )
            except Exception as e:
                print(f"Failed to send booking email: {e}")
        
        return {
            "success": True,
            "data": appointment,
            "message": f"Appointment booked successfully for {parameters['appointment_date']} at {parameters['appointment_time']} with {parameters['doctor_name']} at {hospital_name}. A confirmation email has been sent."
        }
    
    async def _change_password(self, parameters: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """Change user password"""
        current_password = parameters.get("current_password")
        new_password = parameters.get("new_password")
        
        if not current_password or not new_password:
            return {
                "success": False,
                "error": "Both current_password and new_password are required"
            }
        
        # Get user
        user = await db_service.get_user_by_id(user_id)
        if not user:
            return {
                "success": False,
                "error": "User not found"
            }
        
        # Verify current password
        if not verify_password(current_password, user["hashed_password"]):
            return {
                "success": False,
                "error": "Current password is incorrect"
            }
        
        # Validate new password
        if len(new_password) < 6:
            return {
                "success": False,
                "error": "New password must be at least 6 characters"
            }
        
        # Update password
        hashed_password = get_password_hash(new_password)
        success = await db_service.update_user(user_id, {"hashed_password": hashed_password})
        
        if success:
            return {
                "success": True,
                "message": "Password changed successfully"
            }
        else:
            return {
                "success": False,
                "error": "Failed to update password"
            }
    
    async def _get_user_appointments(self, user_id: str) -> Dict[str, Any]:
        """Get user's appointments"""
        appointments = await db_service.get_user_appointments(user_id)
        
        return {
            "success": True,
            "data": appointments,
            "count": len(appointments)
        }
    
    async def _cancel_appointment(self, parameters: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """Cancel an appointment"""
        appointment_id = parameters.get("appointment_id")
        
        if not appointment_id:
            return {
                "success": False,
                "error": "Appointment ID is required"
            }
        
        # Get appointment
        appointment = await db_service.get_appointment_by_id(appointment_id)
        
        if not appointment:
            return {
                "success": False,
                "error": "Appointment not found"
            }
        
        # Verify ownership
        if appointment.get("user_id") != user_id:
            return {
                "success": False,
                "error": "You can only cancel your own appointments"
            }
        
        # Check if already cancelled
        if appointment.get("status") == "cancelled":
            return {
                "success": False,
                "error": "This appointment is already cancelled"
            }
        
        # Cancel appointment
        success = await db_service.update_appointment(appointment_id, {"status": "cancelled"})
        
        if not success:
            return {
                "success": False,
                "error": "Failed to cancel appointment"
            }
        
        # Send cancellation email
        user = await db_service.get_user_by_id(user_id)
        if user:
            try:
                await email_service.send_appointment_cancellation(
                    email=user["email"],
                    name=user["name"],
                    doctor_name=appointment.get("doctor_name", "Doctor"),
                    specialization=appointment.get("specialization", "N/A"),
                    appointment_date=appointment.get("appointment_date", "N/A"),
                    appointment_time=appointment.get("appointment_time", "N/A"),
                    hospital_name=appointment.get("hospital_name", "N/A")
                )
            except Exception as e:
                print(f"Failed to send cancellation email: {e}")
        
        return {
            "success": True,
            "message": f"Appointment with {appointment.get('doctor_name')} on {appointment.get('appointment_date')} at {appointment.get('appointment_time')} has been cancelled. A cancellation email has been sent."
        }


# Global instance
tools_service = ToolsService()

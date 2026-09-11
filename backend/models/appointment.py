from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class AppointmentStatus(str, Enum):
    SCHEDULED = "scheduled"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class DoctorBase(BaseModel):
    id: str
    name: str
    specialization: str
    experience_years: int
    consultation_fee: float
    available_days: List[str]
    available_time_slots: List[str]
    image_url: Optional[str] = None

class AppointmentCreate(BaseModel):
    doctor_id: str
    doctor_name: str
    specialization: str
    hospital_name: Optional[str] = None
    appointment_date: str  # Format: YYYY-MM-DD
    appointment_time: str  # Format: HH:MM
    reason: Optional[str] = None

class AppointmentUpdate(BaseModel):
    status: Optional[AppointmentStatus] = None
    appointment_date: Optional[str] = None
    appointment_time: Optional[str] = None
    reason: Optional[str] = None

class Appointment(BaseModel):
    id: str
    user_id: str
    doctor_id: str
    doctor_name: str
    specialization: str
    hospital_name: Optional[str] = None
    appointment_date: str
    appointment_time: str
    reason: Optional[str] = None
    status: AppointmentStatus = AppointmentStatus.SCHEDULED
    created_at: datetime
    updated_at: datetime

class AppointmentResponse(BaseModel):
    id: str
    user_id: str
    doctor_id: str
    doctor_name: str
    specialization: str
    hospital_name: Optional[str] = None
    appointment_date: str
    appointment_time: str
    reason: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: datetime

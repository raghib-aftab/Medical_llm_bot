from fastapi import APIRouter, HTTPException, status, Depends, BackgroundTasks
from typing import List, Optional
from models.appointment import (
    AppointmentCreate, 
    AppointmentUpdate, 
    AppointmentResponse,
    AppointmentStatus
)
from models.doctor import Doctor
from services.db_service import db_service
from services.auth_service import get_current_user, TokenData
from services.email_service import email_service

router = APIRouter(prefix="/api/appointments", tags=["appointments"])

# ============ Doctor Routes ============

@router.get("/doctors", response_model=List[Doctor])
async def get_all_doctors(
    specialization: Optional[str] = None,
    current_user: TokenData = Depends(get_current_user)
):
    """Get all available doctors, optionally filtered by specialization"""
    doctors = await db_service.get_all_doctors(specialization=specialization)
    return [Doctor(**doc) for doc in doctors]

@router.get("/doctors/{doctor_id}", response_model=Doctor)
async def get_doctor(
    doctor_id: str,
    current_user: TokenData = Depends(get_current_user)
):
    """Get a specific doctor by ID"""
    doctor = await db_service.get_doctor_by_id(doctor_id)
    
    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor not found"
        )
    
    return Doctor(**doctor)

@router.get("/specializations")
async def get_specializations(current_user: TokenData = Depends(get_current_user)):
    """Get all unique specializations"""
    specializations = await db_service.get_doctor_specializations()
    return {"specializations": specializations}

# ============ Appointment Routes ============

@router.post("/", response_model=AppointmentResponse)
async def create_appointment(
    appointment_data: AppointmentCreate,
    background_tasks: BackgroundTasks,
    current_user: TokenData = Depends(get_current_user)
):
    """Create a new appointment"""
    # Verify doctor exists
    doctor = await db_service.get_doctor_by_id(appointment_data.doctor_id)
    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor not found"
        )
    
    # Get hospital name from doctor data or from request
    hospital_name = appointment_data.hospital_name or doctor.get("hospital", "N/A")
    
    # Check for conflicting appointments
    existing = await db_service.check_appointment_conflict(
        doctor_id=appointment_data.doctor_id,
        appointment_date=appointment_data.appointment_date,
        appointment_time=appointment_data.appointment_time
    )
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This time slot is already booked. Please select another time."
        )
    
    # Create appointment
    appointment_id = await db_service.create_appointment(
        user_id=current_user.user_id,
        doctor_id=appointment_data.doctor_id,
        doctor_name=appointment_data.doctor_name,
        specialization=appointment_data.specialization,
        appointment_date=appointment_data.appointment_date,
        appointment_time=appointment_data.appointment_time,
        reason=appointment_data.reason,
        hospital_name=hospital_name
    )
    
    appointment = await db_service.get_appointment_by_id(appointment_id)
    
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create appointment"
        )
    
    # Send confirmation email in background
    user = await db_service.get_user_by_id(current_user.user_id)
    if user:
        background_tasks.add_task(
            email_service.send_appointment_confirmation,
            email=user["email"],
            name=user["name"],
            doctor_name=appointment_data.doctor_name,
            specialization=appointment_data.specialization,
            appointment_date=appointment_data.appointment_date,
            appointment_time=appointment_data.appointment_time,
            hospital_name=hospital_name,
            reason=appointment_data.reason or ""
        )
    
    return AppointmentResponse(**appointment)

@router.get("/", response_model=List[AppointmentResponse])
async def get_user_appointments(
    status_filter: Optional[str] = None,
    current_user: TokenData = Depends(get_current_user)
):
    """Get all appointments for the current user"""
    appointments = await db_service.get_user_appointments(
        user_id=current_user.user_id,
        status_filter=status_filter
    )
    
    return [AppointmentResponse(**apt) for apt in appointments]

@router.get("/{appointment_id}", response_model=AppointmentResponse)
async def get_appointment(
    appointment_id: str,
    current_user: TokenData = Depends(get_current_user)
):
    """Get a specific appointment"""
    appointment = await db_service.get_appointment_by_id(appointment_id)
    
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found"
        )
    
    # Verify ownership
    if appointment["user_id"] != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this appointment"
        )
    
    return AppointmentResponse(**appointment)

@router.put("/{appointment_id}", response_model=AppointmentResponse)
async def update_appointment(
    appointment_id: str,
    update_data: AppointmentUpdate,
    current_user: TokenData = Depends(get_current_user)
):
    """Update an appointment (reschedule or change status)"""
    appointment = await db_service.get_appointment_by_id(appointment_id)
    
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found"
        )
    
    # Verify ownership
    if appointment["user_id"] != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this appointment"
        )
    
    # Prepare update data
    update_dict = {}
    if update_data.status:
        update_dict["status"] = update_data.status.value
    if update_data.appointment_date:
        update_dict["appointment_date"] = update_data.appointment_date
    if update_data.appointment_time:
        update_dict["appointment_time"] = update_data.appointment_time
    if update_data.reason:
        update_dict["reason"] = update_data.reason
    
    if not update_dict:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No update data provided"
        )
    
    success = await db_service.update_appointment(appointment_id, update_dict)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update appointment"
        )
    
    updated_appointment = await db_service.get_appointment_by_id(appointment_id)
    return AppointmentResponse(**updated_appointment)

@router.delete("/{appointment_id}")
async def cancel_appointment(
    appointment_id: str,
    background_tasks: BackgroundTasks,
    current_user: TokenData = Depends(get_current_user)
):
    """Cancel an appointment"""
    appointment = await db_service.get_appointment_by_id(appointment_id)
    
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found"
        )
    
    # Verify ownership
    if appointment["user_id"] != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to cancel this appointment"
        )
    
    success = await db_service.update_appointment(
        appointment_id, 
        {"status": AppointmentStatus.CANCELLED.value}
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to cancel appointment"
        )
    
    # Send cancellation email in background
    user = await db_service.get_user_by_id(current_user.user_id)
    if user:
        background_tasks.add_task(
            email_service.send_appointment_cancellation,
            email=user["email"],
            name=user["name"],
            doctor_name=appointment.get("doctor_name", "Doctor"),
            specialization=appointment.get("specialization", "N/A"),
            appointment_date=appointment.get("appointment_date", "N/A"),
            appointment_time=appointment.get("appointment_time", "N/A"),
            hospital_name=appointment.get("hospital_name", "N/A")
        )
    
    return {"message": "Appointment cancelled successfully"}

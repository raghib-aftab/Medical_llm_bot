from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from models.hospital import Hospital
from services.db_service import db_service
from services.auth_service import get_current_user, TokenData

router = APIRouter(prefix="/api/hospitals", tags=["hospitals"])

@router.get("/", response_model=List[Hospital])
async def get_all_hospitals(
    city: Optional[str] = None,
    specialization: Optional[str] = None,
    emergency_only: bool = False,
    current_user: TokenData = Depends(get_current_user)
):
    """Get all hospitals with optional filters"""
    hospitals = await db_service.get_all_hospitals(
        city=city,
        specialization=specialization,
        emergency_only=emergency_only
    )
    return [Hospital(**h) for h in hospitals]

@router.get("/cities")
async def get_cities(current_user: TokenData = Depends(get_current_user)):
    """Get all unique cities"""
    cities = await db_service.get_hospital_cities()
    return {"cities": cities}

@router.get("/specializations")
async def get_specializations(current_user: TokenData = Depends(get_current_user)):
    """Get all unique specializations across hospitals"""
    specializations = await db_service.get_hospital_specializations()
    return {"specializations": specializations}

@router.get("/{hospital_id}", response_model=Hospital)
async def get_hospital(
    hospital_id: str,
    current_user: TokenData = Depends(get_current_user)
):
    """Get a specific hospital by ID"""
    hospital = await db_service.get_hospital_by_id(hospital_id)
    
    if not hospital:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hospital not found"
        )
    
    return Hospital(**hospital)

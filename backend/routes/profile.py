from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, EmailStr
from typing import Optional
from services.db_service import db_service
from services.auth_service import get_current_user, get_password_hash, verify_password, TokenData

router = APIRouter(prefix="/api/profile", tags=["profile"])

class ProfileUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None

class PasswordUpdate(BaseModel):
    current_password: str
    new_password: str

class ProfileResponse(BaseModel):
    id: str
    name: str
    email: str
    phone: Optional[str] = None
    created_at: str

@router.get("/", response_model=ProfileResponse)
async def get_profile(current_user: TokenData = Depends(get_current_user)):
    """Get current user's profile"""
    user = await db_service.get_user_by_id(current_user.user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return ProfileResponse(
        id=user["id"],
        name=user["name"],
        email=user["email"],
        phone=user.get("phone"),
        created_at=str(user["created_at"])
    )

@router.put("/", response_model=ProfileResponse)
async def update_profile(
    update_data: ProfileUpdate,
    current_user: TokenData = Depends(get_current_user)
):
    """Update user profile"""
    user = await db_service.get_user_by_id(current_user.user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check if email is being changed and if it's already taken
    if update_data.email and update_data.email != user["email"]:
        existing = await db_service.get_user_by_email(update_data.email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
    
    # Prepare update dict
    update_dict = {}
    if update_data.name:
        update_dict["name"] = update_data.name
    if update_data.email:
        update_dict["email"] = update_data.email
    if update_data.phone is not None:
        update_dict["phone"] = update_data.phone
    
    if not update_dict:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No update data provided"
        )
    
    success = await db_service.update_user(current_user.user_id, update_dict)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update profile"
        )
    
    # Get updated user
    updated_user = await db_service.get_user_by_id(current_user.user_id)
    
    return ProfileResponse(
        id=updated_user["id"],
        name=updated_user["name"],
        email=updated_user["email"],
        phone=updated_user.get("phone"),
        created_at=str(updated_user["created_at"])
    )

@router.put("/password")
async def update_password(
    password_data: PasswordUpdate,
    current_user: TokenData = Depends(get_current_user)
):
    """Update user password"""
    user = await db_service.get_user_by_id(current_user.user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Verify current password
    if not verify_password(password_data.current_password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    # Validate new password
    if len(password_data.new_password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be at least 6 characters"
        )
    
    # Hash and update password
    hashed_password = get_password_hash(password_data.new_password)
    success = await db_service.update_user(
        current_user.user_id, 
        {"hashed_password": hashed_password}
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update password"
        )
    
    return {"message": "Password updated successfully"}

from fastapi import APIRouter, HTTPException, status, Depends
from models.user import UserCreate, UserLogin, Token, UserResponse, ForgotPasswordRequest
from services.db_service import db_service
from services.email_service import email_service
from services.auth_service import (
    get_password_hash, 
    verify_password, 
    create_access_token,
    get_current_user,
    TokenData
)
from datetime import timedelta
from config import settings

router = APIRouter(prefix="/api/auth", tags=["authentication"])

@router.post("/forgot-password")
async def forgot_password(request: ForgotPasswordRequest):
    """Send new password to user's email"""
    # Get user by email
    user = await db_service.get_user_by_email(request.email)

    if not user:
        # Don't reveal if email exists or not for security
        return {"message": "If the email exists, a new password has been sent"}

    # Generate new password
    new_password = email_service.generate_password()

    # Hash the new password (don't update DB yet)
    hashed_password = get_password_hash(new_password)

    # Send password reset email FIRST
    email_sent = await email_service.send_password_reset(
        email=user["email"],
        name=user["name"],
        new_password=new_password
    )

    if not email_sent:
        # Email failed - DB unchanged, user keeps current password
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send password reset email"
        )

    # Email accepted by Resend - now commit password change to DB
    db_updated = await db_service.update_user_password(user["id"], hashed_password)

    if not db_updated:
        # Email sent but DB update failed - log clearly, don't claim success
        # User received email but new password won't work; they can retry
        print(f"ERROR: Password reset email sent to {user['email']} but DB update failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update password. Please try again."
        )

    return {"message": "If the email exists, a new password has been sent"}

@router.post("/signup", response_model=Token)
async def signup(user_data: UserCreate):
    """Register a new user"""
    # Check if user already exists
    existing_user = await db_service.get_user_by_email(user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Hash the password
    hashed_password = get_password_hash(user_data.password)
    
    # Create user in database
    user_id = await db_service.create_user(
        email=user_data.email,
        name=user_data.name,
        hashed_password=hashed_password,
        phone=user_data.phone
    )
    
    # Get the created user
    user = await db_service.get_user_by_id(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user"
        )
    
    # Create access token
    access_token = create_access_token(
        data={"sub": user["id"], "email": user["email"]},
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes)
    )
    
    return Token(
        access_token=access_token,
        user=UserResponse(
            id=user["id"],
            email=user["email"],
            name=user["name"],
            phone=user.get("phone"),
            created_at=user["created_at"]
        )
    )

@router.post("/login", response_model=Token)
async def login(user_data: UserLogin):
    """Login user and return access token"""
    # Get user by email
    user = await db_service.get_user_by_email(user_data.email)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Verify password
    if not verify_password(user_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Create access token
    access_token = create_access_token(
        data={"sub": user["id"], "email": user["email"]},
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes)
    )
    
    return Token(
        access_token=access_token,
        user=UserResponse(
            id=user["id"],
            email=user["email"],
            name=user["name"],
            phone=user.get("phone"),
            created_at=user["created_at"]
        )
    )

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: TokenData = Depends(get_current_user)):
    """Get current logged in user info"""
    user = await db_service.get_user_by_id(current_user.user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserResponse(
        id=user["id"],
        email=user["email"],
        name=user["name"],
        phone=user.get("phone"),
        created_at=user["created_at"]
    )

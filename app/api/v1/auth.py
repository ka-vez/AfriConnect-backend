"""
Authentication endpoints.
"""

from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException, status, Form
from sqlmodel import Session
from app.database import get_session
from app.models import User, Founder
from app.schemas.auth import (
    SignUpFounderRequest,
    SignUpInvestorRequest,
    TokenResponse,
    UserInfo,
    CurrentUser,
)
from app.services.auth_service import AuthService
from app.utils.dependencies import get_current_user
from app.utils.errors import AuthenticationError
from sqlmodel import select

# Create router for auth endpoints
router = APIRouter(prefix="/auth", tags=["Authentication"])


def _require_user_id(user: User) -> str:
    """Helper to extract user ID or raise error."""
    if user.id is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="User ID is missing",
        )
    return str(user.id)


@router.post("/signup-founder", response_model=TokenResponse)
def signup_founder(
    signup_data: SignUpFounderRequest,
    session: Session = Depends(get_session),
):
    """
    Register a new user (Founder or Investor).
    
    Requires role-specific fields based on user type.
    """
    try:
        signup_data.role = "founder"
        user, token = AuthService.signup(session, signup_data)
        user_id = _require_user_id(user)

        founder = session.exec(
            select(Founder).where(Founder.user_id == user_id)
        ).first()
        
        if founder is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Founder profile is missing",
            )
        founder.profile_completion_percent = 40
        session.add(founder)
        session.commit()
        
        return TokenResponse(
            access_token=token,
            user=UserInfo(
                id=str(user_id),
                email=user.email,
                full_name=user.full_name,
                avatar=user.avatar,
                role=user.role,
            ),
        )

        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    

@router.post("/signup-investor", response_model=TokenResponse)
def signup_investor(
    signup_data: SignUpInvestorRequest,
    session: Session = Depends(get_session),
):
    """
    Register a new user (Founder or Investor).
    
    Requires role-specific fields based on user type.
    """
    try:
        signup_data.role = "investor"
        user, token = AuthService.signup(session, signup_data)
        user_id = _require_user_id(user)
        
        return TokenResponse(
            access_token=token,
            user=UserInfo(
                id=str(user_id),
                email=user.email,
                full_name=user.full_name,
                avatar=user.avatar,
                role=user.role,
            ),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/token")
def login_for_access_token(
    username: str = Form(...),
    password: str = Form(...),
    session: Session = Depends(get_session),
):
    """
    OAuth2-compatible login endpoint that accepts form data.
    Used by Swagger UI.
    The 'username' field is treated as the email for login.
    Returns: {"access_token": token, "token_type": "bearer"}
    """
    try:
        user, token = AuthService.login(session, username, password)
        return {"access_token": token, "token_type": "bearer"}
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )
    

@router.get("/me", response_model=CurrentUser)
def get_current_user_info(
    current_user: User = Depends(get_current_user),
):
    """
    Get current authenticated user's information.
    """
    user_id = _require_user_id(current_user)

    return CurrentUser(
        id=user_id,
        email=current_user.email,
        full_name=current_user.full_name,
        avatar=current_user.avatar,
        
        role=current_user.role,
        is_active=current_user.is_active,
    )

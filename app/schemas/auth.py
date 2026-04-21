"""
Pydantic schemas for authentication endpoints.
These define request/response validation.
"""

from __future__ import annotations
from pydantic import BaseModel, EmailStr, Field
from app.models.user import UserRole
from typing import Optional


class UserInfo(BaseModel):
    """
    Basic user information returned after authentication.
    
    Attributes:
        id: User ID
        email: User email
        full_name: User's full name
        avatar: User's avatar URL
        role: User role (founder or investor)
    """
    id: int
    email: str
    full_name: str
    avatar: Optional[str] = None
    role: UserRole


class TokenResponse(BaseModel):
    """
    Response schema for login - contains JWT token.
    
    Attributes:
        access_token: JWT access token
        token_type: Type of token (always "bearer")
        user: Basic user information
    """
    access_token: str
    token_type: str = "bearer"
    user: UserInfo


class SignUpRequest(BaseModel):
    """
    Request schema for user signup.
    
    Attributes:
        email: User email
        password: User password (8-72 characters, bcrypt limit)
        full_name: User's full name
        role: User role ("founder" or "investor")
        startup_name: (Founder only) Startup name
        startup_pitch: (Founder only) Elevator pitch
        startup_sector: (Founder only) Industry sector
        the_ask: (Founder only) Funding amount requested
        firm_name: (Investor only) Investment firm name
        investment_thesis: (Investor only) Investment thesis
        min_ticket_size: (Investor only) Minimum check size
        max_ticket_size: (Investor only) Maximum check size
    """
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=72, description="Password must be 8-72 characters (bcrypt limit)")
    full_name: str
    role: str  # "founder" or "investor"
    
    # Founder-specific fields (optional)
    startup_name: Optional[str] = None
    startup_pitch: Optional[str] = None
    startup_sector: Optional[str] = None
    the_ask: Optional[float] = None
    
    # Investor-specific fields (optional)
    firm_name: Optional[str] = None
    investment_thesis: Optional[str] = None
    min_ticket_size: Optional[float] = None
    max_ticket_size: Optional[float] = None


class LoginRequest(BaseModel):
    """
    Request schema for user login.
    
    Attributes:
        email: User email
        password: User password (8-72 characters, bcrypt limit)
    """
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=72, description="Password must be 8-72 characters (bcrypt limit)")


class CurrentUser(BaseModel):
    """
    Currently authenticated user information.
    
    Attributes:
        id: User ID
        email: User email
        full_name: User's full name
        avatar: User's avatar URL
        role: User role
        is_active: Whether user account is active
    """
    id: int
    email: str
    full_name: str
    avatar: Optional[str] = None
    role: UserRole
    is_active: bool

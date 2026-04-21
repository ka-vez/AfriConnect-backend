"""
User model - Base user entity for authentication.
Both Founders and Investors inherit from this base.
"""

from sqlmodel import SQLModel, Field, Column, String, DateTime
from datetime import datetime
from typing import Optional
from enum import Enum


class UserRole(str, Enum):
    """User roles in the platform"""
    FOUNDER = "founder"
    INVESTOR = "investor"


class User(SQLModel, table=True):
    """
    Base User model for all platform users.
    
    Attributes:
        id: Unique user identifier
        email: User's email (unique)
        password_hash: Hashed password (never store plain text)
        full_name: User's full name
        avatar: URL to user's avatar image
        role: User role (founder or investor)
        is_active: Whether user account is active
        created_at: Timestamp when user was created
        updated_at: Timestamp when user was last updated
    """
    
    __tablename__ = "users" # type: ignore
    
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True, max_length=255)
    password_hash: str
    full_name: str = Field(max_length=255)
    avatar: Optional[str] = Field(default=None, max_length=500)
    role: UserRole
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

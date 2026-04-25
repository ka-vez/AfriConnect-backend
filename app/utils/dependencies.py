"""
Dependency injection utilities for FastAPI.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session, select
from app.database import get_session
from app.models import User, UserRole
from typing import Annotated
from jose import jwt, JWTError
from app.utils.jwt_handler import decode_token
from app.config import settings
import uuid  # ADD THIS

# Security scheme for OpenAPI documentation
# OAuth2 scheme for token authentication
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")


TokenDep = Annotated[str, Depends(oauth2_bearer)]


def get_current_user(
    token: TokenDep,
    session: Session = Depends(get_session),
) -> User:
    """
    Extract and validate user from JWT token.
    Returns the actual User object from database.
    """
    try:
        payload = decode_token(token)
        
        # Check if token was invalid (decode_token returns None on error)
        if payload is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
            )
        
        user_id: str = payload.get('sub', '')
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate user",
            )
        
        # Fetch user from database - CHANGE THIS LINE
        user = session.get(User, uuid.UUID(user_id))  # Changed from int(user_id)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
            )
        
        return user
        
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user ID in token",
        )
    except JWTError as err:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not validate credentials",
        )


async def get_founder_or_404(
    user: User = Depends(get_current_user),
):
    """
    Dependency to ensure current user is a founder.
    
    Args:
        user: Current authenticated user
        
    Returns:
        Current founder user
        
    Raises:
        HTTPException: If user is not a founder
    """
    if user.role != UserRole.FOUNDER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This endpoint is only for founders",
        )
    
    return user


async def get_investor_or_404(
    user: User = Depends(get_current_user),
):
    """
    Dependency to ensure current user is an investor.
    
    Args:
        user: Current authenticated user
        
    Returns:
        Current investor user
        
    Raises:
        HTTPException: If user is not an investor
    """
    if user.role != UserRole.INVESTOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This endpoint is only for investors",
        )
    
    return user

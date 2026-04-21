"""
CRUD operations for User model.
"""

from sqlmodel import Session, select
from app.models import User, UserRole, Founder, Investor


def get_user_by_id(session: Session, user_id: int) -> User:
    """Get user by ID"""
    return session.exec(select(User).where(User.id == user_id)).first()


def get_user_by_email(session: Session, email: str) -> User:
    """Get user by email"""
    return session.exec(select(User).where(User.email == email)).first()


def get_founder_profile(session: Session, user_id: int) -> Founder:
    """Get founder profile by user ID"""
    return session.exec(select(Founder).where(Founder.user_id == user_id)).first()


def get_investor_profile(session: Session, user_id: int) -> Investor:
    """Get investor profile by user ID"""
    return session.exec(select(Investor).where(Investor.user_id == user_id)).first()

"""
CRUD operations for Investor model.
"""

from sqlmodel import Session, select
from app.models import Investor


def get_investor_by_user_id(session: Session, user_id: int) -> Investor:
    """Get investor profile by user ID"""
    return session.exec(
        select(Investor).where(Investor.user_id == user_id)
    ).first()


def get_all_investors(session: Session, skip: int = 0, limit: int = 100) -> list[Investor]:
    """Get all investor profiles"""
    return session.exec(select(Investor).offset(skip).limit(limit)).all()

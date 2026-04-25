"""
CRUD operations for Founder model.
"""

from sqlmodel import Session, select
from app.models import Founder, User


def get_all_founders(session: Session, skip: int = 0, limit: int = 100) -> list[Founder]:
    """
    Get all founder profiles with pagination.
    
    Args:
        session: Database session
        skip: Number of records to skip
        limit: Number of records to return
        
    Returns:
        List of founder profiles
    """
    return list(session.exec(select(Founder).offset(skip).limit(limit)).all())


def get_founders_by_sector(session: Session, sector: str) -> list[Founder]:
    """Get founders by sector"""
    return list(session.exec(
        select(Founder).where(Founder.startup_sector == sector)
    ).all())


def get_founders_by_stage(session: Session, stage: str) -> list[Founder]:
    """Get founders by startup stage"""
    return list(session.exec(
        select(Founder).where(Founder.stage == stage)
    ).all())

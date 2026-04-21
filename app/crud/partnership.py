"""
CRUD operations for Partnership model.
"""

from sqlmodel import Session, select
from app.models import Partnership, PartnershipStatus


def get_partnership_by_id(session: Session, partnership_id: int) -> Partnership:
    """Get partnership by ID"""
    return session.exec(
        select(Partnership).where(Partnership.id == partnership_id)
    ).first()


def get_partnerships_for_investor(session: Session, investor_id: int) -> list[Partnership]:
    """Get all partnerships initiated by an investor"""
    return session.exec(
        select(Partnership).where(Partnership.investor_id == investor_id)
    ).all()


def get_partnerships_for_founder(session: Session, founder_id: int) -> list[Partnership]:
    """Get all partnership requests received by a founder"""
    return session.exec(
        select(Partnership).where(Partnership.founder_id == founder_id)
    ).all()


def get_partnership_between(
    session: Session, investor_id: int, founder_id: int
) -> Partnership:
    """Get partnership between specific investor and founder"""
    return session.exec(
        select(Partnership).where(
            (Partnership.investor_id == investor_id) &
            (Partnership.founder_id == founder_id)
        )
    ).first()


def get_pending_partnerships_for_founder(session: Session, founder_id: int) -> list[Partnership]:
    """Get pending partnership requests for a founder"""
    return session.exec(
        select(Partnership).where(
            (Partnership.founder_id == founder_id) &
            (Partnership.status == PartnershipStatus.PENDING)
        )
    ).all()

"""
Investor-specific endpoints.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlmodel import Session, select
from app.database import get_session
from app.models import User, Investor, Founder, Partnership
from app.schemas.investor import (
    InvestorProfileResponse,
    InvestorProfileUpdate,
    StartupDiscoveryItem,
    SavedFounder,
    PrivateNoteUpdate,
)
from app.utils.dependencies import get_investor_or_404
from app.utils.errors import NotFoundError, BadRequestError
from datetime import datetime

# Create router for investor endpoints
router = APIRouter(prefix="/investors", tags=["Investor"])


@router.get("/discover", response_model=list[StartupDiscoveryItem])
def discover_startups(
    sector: str | None = None,
    stage: str | None = None,
    current_user: User = Depends(get_investor_or_404),
    session: Session = Depends(get_session),
):
    """
    Get list of startups for discovery feed with filtering.
    Supports filtering by sector and stage.
    """
    # Build query for founders
    query = select(Founder)
    
    if sector:
        query = query.where(Founder.startup_sector == sector)
    
    if stage:
        query = query.where(Founder.stage == stage)
    
    founders = session.exec(query).all()
    
    # Get investor's saved and partnered startups for flags
    saved_partnerships = session.exec(
        select(Partnership).where(Partnership.investor_id == current_user.id)
    ).all()
    
    saved_ids = {p.founder_id for p in saved_partnerships}
    deck_request_ids = {p.founder_id for p in saved_partnerships if p.partnership_type == "deck_request"}
    active_partnership_ids = {p.founder_id for p in saved_partnerships if p.status == "active"}
    
    # Build response with flags
    result = []
    for founder in founders:
        founder_user = session.exec(
            select(User).where(User.id == founder.user_id)
        ).first()
        
        result.append(StartupDiscoveryItem(
            id=founder.user_id,
            startup_name=founder.startup_name,
            founder_name=founder_user.full_name if founder_user else "Unknown",
            pitch=founder.startup_pitch,
            sector=founder.startup_sector,
            stage=founder.stage,
            the_ask=founder.the_ask,
            currency=founder.currency,
            has_been_saved=founder.user_id in saved_ids,
            has_requested_deck=founder.user_id in deck_request_ids,
            has_partnered=founder.user_id in active_partnership_ids,
        ))
    
    return result


@router.get("/saved", response_model=list[SavedFounder])
def get_saved_founders(
    current_user: User = Depends(get_investor_or_404),
    session: Session = Depends(get_session),
):
    """
    Get investor's saved (pipeline) founders.
    """
    # Get partnerships for this investor
    partnerships = session.exec(
        select(Partnership).where(Partnership.investor_id == current_user.id)
    ).all()
    
    result = []
    for partnership in partnerships:
        founder = session.exec(
            select(Founder).where(Founder.user_id == partnership.founder_id)
        ).first()
        
        if founder:
            founder_user = session.exec(
                select(User).where(User.id == founder.user_id)
            ).first()
            
            result.append(SavedFounder(
                id=founder.user_id,
                startup_name=founder.startup_name,
                founder_name=founder_user.full_name if founder_user else "Unknown",
                pitch=founder.startup_pitch,
                sector=founder.startup_sector,
                stage=founder.stage,
                the_ask=founder.the_ask,
                investor_note=partnership.investor_note,
                partnership_status=partnership.status,
            ))
    
    return result


@router.post("/saved/{startup_id}", status_code=status.HTTP_201_CREATED)
def save_founder(
    startup_id: int,
    current_user: User = Depends(get_investor_or_404),
    session: Session = Depends(get_session),
):
    """
    Save a founder to investor's pipeline.
    """
    # Get founder
    founder = session.exec(
        select(Founder).where(Founder.user_id == startup_id)
    ).first()
    
    if not founder:
        raise NotFoundError(detail="Founder not found")
    
    investor_id = current_user.id
    if investor_id is None:
        raise NotFoundError(detail="Investor account not found")
    
    # Check if already saved
    existing = session.exec(
        select(Partnership).where(
            (Partnership.investor_id == investor_id) &
            (Partnership.founder_id == startup_id)
        )
    ).first()
    
    if existing:
        raise BadRequestError(detail="Founder already saved")
    
    # Create partnership
    from app.models import PartnershipType
    partnership = Partnership(
        investor_id=investor_id,
        founder_id=startup_id,
        partnership_type=PartnershipType.MEETING_REQUEST,
    )
    
    session.add(partnership)
    session.commit()
    
    return {"message": "Founder saved successfully", "partnership_id": partnership.id}


@router.delete("/saved/{startup_id}")
def remove_saved_founder(
    startup_id: int,
    current_user: User = Depends(get_investor_or_404),
    session: Session = Depends(get_session),
):
    """
    Remove a founder from investor's pipeline.
    """
    partnership = session.exec(
        select(Partnership).where(
            (Partnership.investor_id == current_user.id) &
            (Partnership.founder_id == startup_id)
        )
    ).first()
    
    if not partnership:
        raise NotFoundError(detail="Partnership not found")
    
    session.delete(partnership)
    session.commit()
    
    return {"message": "Founder removed from pipeline"}


@router.put("/saved/{startup_id}/note")
def update_founder_note(
    startup_id: int,
    note_update: PrivateNoteUpdate,
    current_user: User = Depends(get_investor_or_404),
    session: Session = Depends(get_session),
):
    """
    Update private note on a saved founder.
    """
    partnership = session.exec(
        select(Partnership).where(
            (Partnership.investor_id == current_user.id) &
            (Partnership.founder_id == startup_id)
        )
    ).first()
    
    if not partnership:
        raise NotFoundError(detail="Partnership not found")
    
    partnership.investor_note = note_update.note
    partnership.updated_at = datetime.utcnow()
    
    session.add(partnership)
    session.commit()
    
    return {"message": "Note updated successfully"}


@router.get("/profile", response_model=InvestorProfileResponse)
def get_investor_profile(
    current_user: User = Depends(get_investor_or_404),
    session: Session = Depends(get_session),
):
    """
    Get investor profile including firm details and statistics.
    """
    investor = session.exec(
        select(Investor).where(Investor.user_id == current_user.id)
    ).first()
    
    if not investor:
        raise NotFoundError(detail="Investor profile not found")
    
    investor_id = investor.id
    if investor_id is None:
        raise NotFoundError(detail="Investor profile not found")
    
    return InvestorProfileResponse(
        id=investor_id,
        email=current_user.email,
        full_name=current_user.full_name,
        firm_name=investor.firm_name,
        investment_thesis=investor.investment_thesis,
        preferred_sectors=investor.preferred_sectors,
        min_ticket_size=investor.min_ticket_size,
        max_ticket_size=investor.max_ticket_size,
        currency=investor.currency,
        deals_reviewed=investor.deals_reviewed,
        active_partnerships=investor.active_partnerships,
        portfolio_companies=investor.portfolio_companies,
    )


@router.put("/profile", response_model=InvestorProfileResponse)
def update_investor_profile(
    profile_update: InvestorProfileUpdate,
    current_user: User = Depends(get_investor_or_404),
    session: Session = Depends(get_session),
):
    """
    Update investor profile details.
    """
    investor = session.exec(
        select(Investor).where(Investor.user_id == current_user.id)
    ).first()
    
    if not investor:
        raise NotFoundError(detail="Investor profile not found")
    
    # Update allowed fields
    if profile_update.full_name is not None:
        current_user.full_name = profile_update.full_name
    
    if profile_update.firm_name is not None:
        investor.firm_name = profile_update.firm_name
    
    if profile_update.investment_thesis is not None:
        investor.investment_thesis = profile_update.investment_thesis
    
    if profile_update.preferred_sectors is not None:
        investor.preferred_sectors = profile_update.preferred_sectors
    
    if profile_update.min_ticket_size is not None:
        investor.min_ticket_size = profile_update.min_ticket_size
    
    if profile_update.max_ticket_size is not None:
        investor.max_ticket_size = profile_update.max_ticket_size
    
    # Update timestamp
    current_user.updated_at = datetime.utcnow()
    
    session.add(current_user)
    session.add(investor)
    session.commit()
    session.refresh(investor)
    
    investor_id = investor.id
    if investor_id is None:
        raise NotFoundError(detail="Investor profile not found")
    
    return InvestorProfileResponse(
        id=investor_id,
        email=current_user.email,
        full_name=current_user.full_name,
        firm_name=investor.firm_name,
        investment_thesis=investor.investment_thesis,
        preferred_sectors=investor.preferred_sectors,
        min_ticket_size=investor.min_ticket_size,
        max_ticket_size=investor.max_ticket_size,
        currency=investor.currency,
        deals_reviewed=investor.deals_reviewed,
        active_partnerships=investor.active_partnerships,
        portfolio_companies=investor.portfolio_companies,
    )

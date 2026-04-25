"""
Founder-specific endpoints.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlmodel import Session, select, func
from app.database import get_session
from app.models import User, Founder, UserRole
from app.models.partnership import Partnership, PartnershipStatus
from app.schemas.founder import (
    FounderProfileResponse,
    FounderProfileUpdate,
    FounderTractionResponse,
    FounderFeedResponse,
)
from app.utils.dependencies import get_founder_or_404
from app.utils.errors import NotFoundError
from datetime import datetime

# Create router for founder endpoints
router = APIRouter(prefix="/founder", tags=["Founder"])


def _require_founder_id(founder: Founder) -> str:
    """Ensure founder has a persisted primary key."""
    if founder.id is None:
        raise NotFoundError(detail="Founder profile not found")
    return str(founder.id)


@router.get("/feed", response_model=FounderFeedResponse)
def get_founder_feed(
    current_user: User = Depends(get_founder_or_404),
    session: Session = Depends(get_session),
):
    """Get founder home feed with stats and recent activity."""
    founder = session.exec(
        select(Founder).where(Founder.user_id == current_user.id)
    ).first()
    
    if not founder:
        raise NotFoundError(detail="Founder profile not found")
    
    # Get total investors on platform
    total_investors = session.exec(
        select(func.count()).select_from(User).where(
            User.role == UserRole.INVESTOR,
            User.is_active == True
        )
    ).one()
    
    # Get active partnerships for this founder
    active_partnerships = session.exec(
        select(Partnership).where(
            Partnership.founder_id == current_user.id,
            Partnership.status == PartnershipStatus.ACTIVE
        )
    ).all()
    
    active_partnerships_count = len(active_partnerships)
    
    # Calculate total raised: active partnerships * founder's ask
    total_raised = active_partnerships_count * founder.the_ask
    
    return FounderFeedResponse(
        profile_completion_percent=founder.profile_completion_percent,
        platform_stats={
            "total_investors": total_investors,
            "active_partnerships": active_partnerships_count,
            "total_raised": total_raised,
        },
        recent_investor_activity=[],
        opportunities=[],
    )


@router.get("/traction", response_model=FounderTractionResponse)
def get_founder_traction(
    current_user: User = Depends(get_founder_or_404),
    session: Session = Depends(get_session),
):
    """Get founder traction metrics."""
    founder = session.exec(
        select(Founder).where(Founder.user_id == current_user.id)
    ).first()
    
    if not founder:
        raise NotFoundError(detail="Founder profile not found")
    
    return FounderTractionResponse(
        profile_views=founder.traction_views,
        investor_interest=founder.traction_interest,
        deck_requests=founder.traction_deck_requests,
    )


@router.get("/profile", response_model=FounderProfileResponse)
def get_founder_profile(
    current_user: User = Depends(get_founder_or_404),
    session: Session = Depends(get_session),
):
    """Get complete founder profile."""
    founder = session.exec(
        select(Founder).where(Founder.user_id == current_user.id)
    ).first()
    
    if not founder:
        raise NotFoundError(detail="Founder profile not found")
    
    founder_id = _require_founder_id(founder)
    
    return FounderProfileResponse(
        id=founder_id,
        email=current_user.email,
        full_name=current_user.full_name,
        startup_name=founder.startup_name,
        startup_pitch=founder.startup_pitch,
        startup_sector=founder.startup_sector,
        stage=founder.stage,
        the_ask=founder.the_ask,
        currency=founder.currency,
        experience=founder.experience,
        education=founder.education,
        profile_completion_percent=founder.profile_completion_percent,
        traction_views=founder.traction_views,
        traction_interest=founder.traction_interest,
        traction_deck_requests=founder.traction_deck_requests,
    )


@router.put("/profile", response_model=FounderProfileResponse)
def update_founder_profile(
    profile_update: FounderProfileUpdate,
    current_user: User = Depends(get_founder_or_404),
    session: Session = Depends(get_session),
):
    """Update founder profile."""
    founder = session.exec(
        select(Founder).where(Founder.user_id == current_user.id)
    ).first()
    
    if not founder:
        raise NotFoundError(detail="Founder profile not found")
    
    # Update allowed fields
    if profile_update.full_name is not None:
        current_user.full_name = profile_update.full_name
    
    if profile_update.startup_name is not None:
        founder.startup_name = profile_update.startup_name
    
    if profile_update.startup_pitch is not None:
        founder.startup_pitch = profile_update.startup_pitch
    
    if profile_update.startup_sector is not None:
        founder.startup_sector = profile_update.startup_sector
    
    if profile_update.stage is not None:
        founder.stage = profile_update.stage
    
    if profile_update.the_ask is not None:
        founder.the_ask = profile_update.the_ask
    
    if profile_update.experience is not None:
        founder.experience = profile_update.experience
    
    if profile_update.education is not None:
        founder.education = profile_update.education
    
    current_user.updated_at = datetime.utcnow()
    
    session.add(current_user)
    session.add(founder)
    session.commit()
    session.refresh(founder)
    
    founder_id = _require_founder_id(founder)
    
    return FounderProfileResponse(
        id=founder_id,
        email=current_user.email,
        full_name=current_user.full_name,
        startup_name=founder.startup_name,
        startup_pitch=founder.startup_pitch,
        startup_sector=founder.startup_sector,
        stage=founder.stage,
        the_ask=founder.the_ask,
        currency=founder.currency,
        experience=founder.experience,
        education=founder.education,
        profile_completion_percent=founder.profile_completion_percent,
        traction_views=founder.traction_views,
        traction_interest=founder.traction_interest,
        traction_deck_requests=founder.traction_deck_requests,
    )

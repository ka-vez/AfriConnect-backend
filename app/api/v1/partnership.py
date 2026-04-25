"""
Partnership and connection endpoints.
Handles partnership requests, messaging, and communication between investors and founders.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlmodel import Session, select
from app.database import get_session
from app.models import (
    User,
    Partnership,
    PartnershipType,
    PartnershipStatus,
    Message,
    Founder,
)
from app.schemas.partnership import (
    DeckRequestCreate,
    PartnershipInitiate,
    PartnershipResponse,
    PartnershipList,
    AcceptPartnershipRequest,
    SendMessageRequest,
    MessageResponse,
)
from app.utils.dependencies import get_investor_or_404, get_founder_or_404, get_current_user
from app.utils.errors import NotFoundError, UnauthorizedError, BadRequestError
from datetime import datetime
from uuid import UUID
from app.models import UserRole

# Create router for partnership endpoints
router = APIRouter(prefix="/partnerships", tags=["Partnership"])


def _require_user_id(user: User) -> str:
    if user.id is None:
        raise UnauthorizedError(detail="Invalid authenticated user")
    return str(user.id)


@router.post("/request-deck", status_code=status.HTTP_201_CREATED)
def request_deck(
    deck_request: DeckRequestCreate,
    current_user: User = Depends(get_investor_or_404),
    session: Session = Depends(get_session),
):
    """
    Investor requests pitch deck from founder.
    Creates a partnership record with DECK_REQUEST type.
    """
    investor_id = _require_user_id(current_user)

    # Check if partnership already exists
    existing = session.exec(
        select(Partnership).where(
            (Partnership.investor_id == investor_id) &
            (Partnership.founder_id == deck_request.startup_id) &
            (Partnership.partnership_type == PartnershipType.DECK_REQUEST)
        )
    ).first()
    
    if existing:
        raise BadRequestError(detail="Deck request already sent")
    
    # Create partnership record
    partnership = Partnership(
        investor_id=UUID(investor_id),
        founder_id=UUID(deck_request.startup_id),
        partnership_type=PartnershipType.DECK_REQUEST,
        investor_note=deck_request.note,
    )
    
    session.add(partnership)
    session.commit()
    
    return {
        "message": "Deck request sent",
        "partnership_id": partnership.id,
    }


@router.post("/initiate", status_code=status.HTTP_201_CREATED)
def initiate_partnership(
    partnership_init: PartnershipInitiate,
    current_user: User = Depends(get_investor_or_404),
    session: Session = Depends(get_session),
):
    """
    Investor initiates formal partnership/meeting with founder.
    Creates a partnership record with MEETING_REQUEST type.
    """
    investor_id = _require_user_id(current_user)

    # Check if meeting request already exists
    existing = session.exec(
        select(Partnership).where(
            (Partnership.investor_id == investor_id) &
            (Partnership.founder_id == partnership_init.startup_id) &
            (Partnership.partnership_type == PartnershipType.MEETING_REQUEST)
        )
    ).first()
    
    if existing:
        raise BadRequestError(detail="Meeting request already sent")
    
    # Create partnership record
    partnership = Partnership(
        investor_id=UUID(investor_id),
        founder_id=UUID(partnership_init.startup_id),
        partnership_type=PartnershipType.MEETING_REQUEST,
        investor_note=partnership_init.note,
    )
    
    session.add(partnership)
    session.commit()
    
    return {
        "message": "Partnership request sent",
        "partnership_id": partnership.id,
    }


@router.get("", response_model=PartnershipList)
def get_partnerships(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """
    Get partnerships.
    - Investors see their active partnerships
    - Founders see incoming and active partnership requests
    """
    
    current_user_id = _require_user_id(current_user)
    partnerships = []
    
    if current_user.role == UserRole.INVESTOR:
        # Get investor's partnerships
        partnerships = session.exec(
            select(Partnership).where(Partnership.investor_id == current_user_id)
        ).all()
    
    elif current_user.role == UserRole.FOUNDER:
        # Get founder's incoming requests
        partnerships = session.exec(
            select(Partnership).where(Partnership.founder_id == current_user_id)
        ).all()
    
    # Build response
    response_partnerships = []
    for p in partnerships:
        if p.id is None:
            continue

        investor_user = session.exec(
            select(User).where(User.id == p.investor_id)
        ).first()
        
        founder_user = session.exec(
            select(User).where(User.id == p.founder_id)
        ).first()
        
        founder = session.exec(
            select(Founder).where(Founder.user_id == p.founder_id)
        ).first()
        
        response_partnerships.append(PartnershipResponse(
            id=str(p.id),
            investor_name=investor_user.full_name if investor_user else "Unknown",
            founder_name=founder_user.full_name if founder_user else "Unknown",
            startup_name=founder.startup_name if founder else "Unknown",
            partnership_type=p.partnership_type.value,
            status=p.status.value,
            investor_note=p.investor_note,
            founder_response_note=p.founder_response_note,
            created_at=p.created_at,
            responded_at=p.responded_at,
        ))
    
    return PartnershipList(
        total=len(response_partnerships),
        partnerships=response_partnerships,
    )


@router.post("/{partnership_id}/accept", status_code=status.HTTP_200_OK)
def accept_partnership(
    partnership_id: int,
    accept_data: AcceptPartnershipRequest,
    current_user: User = Depends(get_founder_or_404),
    session: Session = Depends(get_session),
):
    """
    Founder accepts partnership request from investor.
    Updates status to ACCEPTED and records response timestamp.
    """
    partnership = session.exec(
        select(Partnership).where(Partnership.id == partnership_id)
    ).first()
    
    if not partnership:
        raise NotFoundError(detail="Partnership not found")
    
    current_user_id = _require_user_id(current_user)

    # Verify current user is the founder
    if partnership.founder_id != current_user_id:
        raise UnauthorizedError(detail="Not authorized to accept this partnership")
    
    # Update partnership status
    partnership.status = PartnershipStatus.ACCEPTED
    partnership.founder_response_note = accept_data.response_note
    partnership.responded_at = datetime.utcnow()
    partnership.updated_at = datetime.utcnow()
    
    session.add(partnership)
    session.commit()
    
    return {
        "message": "Partnership accepted",
        "partnership_id": partnership.id,
        "status": partnership.status.value,
    }


@router.post("/{partnership_id}/message", status_code=status.HTTP_201_CREATED)
def send_message(
    partnership_id: str,
    message_data: SendMessageRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """
    Send message within an active partnership.
    Either investor or founder can send messages to each other.
    """
    partnership = session.exec(
        select(Partnership).where(Partnership.id == partnership_id)
    ).first()
    
    if not partnership:
        raise NotFoundError(detail="Partnership not found")
    
    current_user_id = _require_user_id(current_user)

    # Verify user is part of this partnership
    is_investor = partnership.investor_id == UUID(current_user_id)
    is_founder = partnership.founder_id == UUID(current_user_id)
    
    if not (is_investor or is_founder):
        raise UnauthorizedError(detail="Not authorized to message in this partnership")
    
    # Determine sender and receiver
    sender_id = current_user_id
    receiver_id = partnership.founder_id if is_investor else partnership.investor_id
    
    # Create message
    message = Message(
        partnership_id=UUID(partnership_id),
        sender_id=UUID(sender_id),
        receiver_id=receiver_id,
        content=message_data.content,
    )
    
    session.add(message)
    session.commit()
    
    return {
        "message_id": message.id,
        "created_at": message.created_at,
    }

"""
Partnership model - Represents connections between investors and founders.
"""

from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class PartnershipStatus(str, Enum):
    """Partnership status states"""
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    ACTIVE = "active"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class PartnershipType(str, Enum):
    """Types of partnership requests"""
    DECK_REQUEST = "deck_request"
    MEETING_REQUEST = "meeting_request"


class Partnership(SQLModel, table=True):
    """
    Partnership record between investor and founder.
    Only investors can initiate partnerships.
    
    Attributes:
        id: Unique partnership identifier
        investor_id: ID of the investor initiating the partnership
        founder_id: ID of the founder receiving the partnership request
        partnership_type: Type of partnership (deck request or meeting)
        status: Current status of the partnership
        investor_note: Private note from investor about the startup
        founder_response_note: Founder's response/note
        created_at: When partnership was created
        updated_at: When partnership was last updated
        responded_at: When founder responded to the request
    """
    
    __tablename__ = "partnerships" # type: ignore
    
    id: Optional[int] = Field(default=None, primary_key=True)
    investor_id: int = Field(foreign_key="users.id")
    founder_id: int = Field(foreign_key="users.id")
    partnership_type: PartnershipType
    status: PartnershipStatus = Field(default=PartnershipStatus.PENDING)
    investor_note: Optional[str] = Field(default=None, max_length=1000)
    founder_response_note: Optional[str] = Field(default=None, max_length=1000)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    responded_at: Optional[datetime] = Field(default=None)

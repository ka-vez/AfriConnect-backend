"""
Pydantic schemas for partnership endpoints.
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class DeckRequestCreate(BaseModel):
    """
    Request schema for requesting a pitch deck.
    """
    startup_id: int = Field(description="ID of the founder/startup")
    note: Optional[str] = Field(None, max_length=500, description="Optional note with the request")


class PartnershipInitiate(BaseModel):
    """
    Request schema for initiating a formal partnership.
    """
    startup_id: int = Field(description="ID of the founder/startup")
    note: Optional[str] = Field(None, max_length=500, description="Note about the meeting/partnership")


class PartnershipResponse(BaseModel):
    """
    Response schema for partnership details.
    """
    id: int
    investor_name: str
    founder_name: str
    startup_name: str
    partnership_type: str
    status: str
    investor_note: Optional[str]
    founder_response_note: Optional[str]
    created_at: datetime
    responded_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class PartnershipList(BaseModel):
    """
    Response schema for list of partnerships.
    """
    total: int
    partnerships: list[PartnershipResponse]


class AcceptPartnershipRequest(BaseModel):
    """
    Request schema for accepting a partnership.
    """
    response_note: Optional[str] = Field(None, max_length=1000)


class SendMessageRequest(BaseModel):
    """
    Request schema for sending a message.
    """
    content: str = Field(max_length=5000, description="Message content")


class MessageResponse(BaseModel):
    """
    Response schema for a message.
    """
    id: int
    sender_name: str
    content: str
    created_at: datetime
    is_read: bool
    
    class Config:
        from_attributes = True

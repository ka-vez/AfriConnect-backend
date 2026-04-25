"""
Pydantic schemas for investor-specific endpoints.
"""

from pydantic import BaseModel, Field
from typing import Optional, List


class StartupDiscoveryItem(BaseModel):
    """
    Represents a startup in the investor discovery feed.
    """
    id: str
    startup_name: str
    founder_name: str
    pitch: str
    sector: str
    stage: str
    the_ask: float
    currency: str
    has_been_saved: bool = False
    has_requested_deck: bool = False
    has_partnered: bool = False
    
    class Config:
        from_attributes = True


class DiscoverQueryParams(BaseModel):
    """
    Query parameters for discovery feed filtering.
    """
    sector: Optional[str] = None
    stage: Optional[str] = None
    min_ask: Optional[float] = None
    max_ask: Optional[float] = None
    search: Optional[str] = None


class SavedFounder(BaseModel):
    """
    Represents a saved founder in investor's pipeline.
    """
    id: str
    startup_name: str
    founder_name: str
    pitch: str
    sector: str
    stage: str
    the_ask: float
    investor_note: Optional[str]
    partnership_status: Optional[str]
    
    class Config:
        from_attributes = True


class InvestorProfileUpdate(BaseModel):
    """
    Request schema for updating investor profile.
    """
    full_name: Optional[str] = None
    firm_name: Optional[str] = None
    investment_thesis: Optional[str] = None
    preferred_sectors: Optional[str] = None


class InvestorProfileResponse(BaseModel):
    """
    Response schema for investor profile.
    """
    id: str
    email: str
    full_name: str
    firm_name: str
    investment_thesis: str
    preferred_sectors: Optional[str]
    currency: str
    deals_reviewed: int
    active_partnerships: int
    portfolio_companies: Optional[str]
    
    class Config:
        from_attributes = True


class PrivateNoteUpdate(BaseModel):
    """
    Request schema for updating private notes on saved founders.
    """
    note: str = Field(max_length=1000)

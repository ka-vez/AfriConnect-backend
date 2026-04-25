"""
Pydantic schemas for founder-specific endpoints.
"""

from pydantic import BaseModel, Field
from typing import Optional
from app.models.founder import StartupStage


class FounderProfileUpdate(BaseModel):
    """
    Request schema for updating founder profile.
    """
    full_name: Optional[str] = None
    startup_name: Optional[str] = None
    startup_pitch: Optional[str] = None
    startup_sector: Optional[str] = None
    stage: Optional[StartupStage] = None
    the_ask: Optional[float] = Field(None, gt=0)
    experience: Optional[str] = None
    education: Optional[str] = None


class FounderProfileResponse(BaseModel):
    """
    Response schema for founder profile.
    """
    id: str
    email: str
    full_name: str
    startup_name: str
    startup_pitch: str
    startup_sector: str
    stage: StartupStage
    the_ask: float
    currency: str
    experience: Optional[str]
    education: Optional[str]
    profile_completion_percent: int
    traction_views: int
    traction_interest: int
    traction_deck_requests: int
    
    class Config:
        from_attributes = True


class FounderTractionResponse(BaseModel):
    """
    Response schema for founder traction metrics.
    """
    profile_views: int
    investor_interest: int
    deck_requests: int


class FounderFeedResponse(BaseModel):
    """
    Response schema for founder home feed.
    """
    profile_completion_percent: int
    platform_stats: dict
    recent_investor_activity: list
    opportunities: list

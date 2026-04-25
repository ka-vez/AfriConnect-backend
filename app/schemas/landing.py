"""
Landing feed schemas for public API.
Used to return aggregated statistics and featured content.
"""

from pydantic import BaseModel
from typing import List, Optional


class ActiveOpportunity(BaseModel):
    """
    Demo opportunity object for the landing feed.
    """
    id: int
    title: str
    stage: str
    ask_amount: float
    sector: str


class FeaturedInvestor(BaseModel):
    """
    Demo featured investor object for the landing feed.
    """
    id: str
    name: str
    focus_areas: List[str]


class LandingFeedResponse(BaseModel):
    """
    Landing feed response containing platform statistics and featured content.
    
    Attributes:
        total_investors: Total number of active investors on the platform
        active_opportunities: List of active funding opportunities (demo data)
        total_raised: Total amount raised across all active partnerships
        active_partnerships: Number of active partnerships
        featured_investors: List of featured investors (demo data)
    """
    total_investors: int
    active_opportunities: List[ActiveOpportunity]
    total_raised: float
    active_partnerships: int
    featured_investors: List[FeaturedInvestor]

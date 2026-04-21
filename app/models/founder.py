"""
Founder model - Extended profile for founder users.
Contains startup-specific information.
"""

from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from enum import Enum


class StartupStage(str, Enum):
    """Startup development stages"""
    IDEA = "idea"
    PRE_SEED = "pre_seed"
    SEED = "seed"
    SERIES_A = "series_a"
    SERIES_B = "series_b"
    SERIES_C = "series_c"
    GROWTH = "growth"


class Founder(SQLModel, table=True):
    """
    Founder profile with startup details.
    
    Attributes:
        id: Unique founder identifier
        user_id: Reference to User (one-to-one relationship)
        startup_name: Name of the founder's startup
        startup_pitch: Short pitch about the startup
        startup_sector: Industry/sector of the startup
        stage: Current stage of the startup
        the_ask: Amount of funding being raised
        currency: Currency for the ask (USD, EUR, etc.)
        profile_completion_percent: Percentage of profile filled (0-100)
        experience: Founder's professional experience
        education: Founder's education details
        traction_views: Number of profile views
        traction_interest: Number of investor interests
        traction_deck_requests: Number of deck requests received
    """
    
    __tablename__ = "founders" # type: ignore
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", unique=True)
    startup_name: str = Field(max_length=255)
    startup_pitch: str = Field(max_length=1000)
    startup_sector: str = Field(max_length=100)
    stage: StartupStage = Field(default=StartupStage.IDEA)
    the_ask: float = Field(gt=0)
    currency: str = Field(default="USD", max_length=3)
    profile_completion_percent: int = Field(default=0, ge=0, le=100)
    experience: Optional[str] = Field(default=None, max_length=2000)
    education: Optional[str] = Field(default=None, max_length=2000)
    traction_views: int = Field(default=0)
    traction_interest: int = Field(default=0)
    traction_deck_requests: int = Field(default=0)

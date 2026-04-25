"""
Investor model - Extended profile for investor users.
Contains investment firm and portfolio details.
"""

from sqlmodel import SQLModel, Field
from typing import Optional
import uuid


class Investor(SQLModel, table=True):
    """
    Investor profile with firm and investment details.
    
    Attributes:
        id: Unique investor identifier
        user_id: Reference to User (one-to-one relationship)
        firm_name: Name of the investment firm
        investment_thesis: Investment philosophy/strategy
        preferred_sectors: Comma-separated list of preferred sectors
        min_ticket_size: Minimum check size investor will write
        max_ticket_size: Maximum check size investor will write
        currency: Currency for ticket sizes
        deals_reviewed: Total number of startups reviewed
        active_partnerships: Number of active partnerships
        portfolio_companies: Comma-separated list of portfolio companies
    """
    
    __tablename__ = "investors" # type: ignore
    
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    user_id: uuid.UUID = Field(foreign_key="users.id", unique=True)
    firm_name: str = Field(max_length=255)
    investment_thesis: str = Field(max_length=1000)
    preferred_sectors: Optional[str] = Field(default=None, max_length=500)
    currency: str = Field(default="USD", max_length=3)
    deals_reviewed: int = Field(default=0)
    active_partnerships: int = Field(default=0)
    portfolio_companies: Optional[str] = Field(default=None, max_length=1000)
    featured: bool = Field(default=False)
    max_investment_amount: int

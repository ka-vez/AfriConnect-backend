"""
Landing page public endpoints.
Provides aggregated platform statistics and featured content for landing page.
"""

from fastapi import APIRouter, Depends
from sqlmodel import Session, select, func
from app.database import get_session
from app.models import User, UserRole, Partnership, PartnershipStatus, Founder, Investor
from app.schemas.landing import (
    LandingFeedResponse,
    ActiveOpportunity,
    FeaturedInvestor,
)

# Create router for landing endpoints (no auth prefix needed for public endpoints)
router = APIRouter(prefix="", tags=["Landing"])


@router.get("/feed", response_model=LandingFeedResponse)
def get_landing_feed(session: Session = Depends(get_session)):
    """
    Public landing feed endpoint - no authentication required.
    
    Returns:
        LandingFeedResponse with platform statistics:
        - total_investors: Count of active investors
        - active_opportunities: Demo list of current funding opportunities
        - total_raised: Total amount raised across active partnerships
        - active_partnerships: Count of active partnerships
        - featured_investors: First 5 featured investors from database
    """
    
    # 1. Count total active investors
    total_investors_query = (
        select(func.count())
        .select_from(User)
        .where((User.role == UserRole.INVESTOR) & (User.is_active == True))
    )
    total_investors = session.exec(total_investors_query).one()
    
    # 2. Count total active partnerships
    active_partnerships_query = (
        select(func.count())
        .select_from(Partnership)
        .where(Partnership.status == PartnershipStatus.ACTIVE)
    )
    active_partnerships = session.exec(active_partnerships_query).one()
    
    # 3. Calculate total_raised
    # For each founder with active partnerships, sum up the amounts raised
    total_raised = 0.0
    
    # Get all founders with their ask amounts
    founders_query = select(Founder)
    founders = session.exec(founders_query).all()
    
    for founder in founders:
        # Count active partnerships for this founder
        partnerships_count_query = (
            select(func.count())
            .select_from(Partnership)
            .where(
                (Partnership.founder_id == founder.user_id) &
                (Partnership.status == PartnershipStatus.ACTIVE)
            )
        )
        partnerships_count = session.exec(partnerships_count_query).one()
        
        # If founder has active partnerships, add to total
        if partnerships_count > 0:
            total_raised += (founder.the_ask or 0.0) * partnerships_count
    
    # 4. Demo data for active opportunities
    active_opportunities = [
        ActiveOpportunity(
            id=1,
            title="AI-powered Supply Chain Solution",
            stage="series_a",
            ask_amount=5000000.0,
            sector="Technology",
        ),
        ActiveOpportunity(
            id=2,
            title="Sustainable Fashion Platform",
            stage="seed",
            ask_amount=500000.0,
            sector="E-commerce",
        ),
        ActiveOpportunity(
            id=3,
            title="HealthTech Mobile App",
            stage="pre_seed",
            ask_amount=250000.0,
            sector="Healthcare",
        ),
    ]
    
    # 5. Get first 5 featured investors from database
    featured_investors_query = (
        select(Investor)
        .where(Investor.featured == True)
        .limit(5)
    )
    featured_investors_db = session.exec(featured_investors_query).all()
    
    featured_investors = []
    for investor in featured_investors_db:
        if investor.id is None:
            continue

        # Get the associated user for the investor's name
        user = session.exec(
            select(User).where(User.id == investor.user_id)
        ).first()
        
        if user:
            featured_investors.append(
                FeaturedInvestor(
                    id=str(investor.id),
                    name=user.full_name,
                    focus_areas=investor.preferred_sectors.split(",") if investor.preferred_sectors else []
                )
            )
    
    return LandingFeedResponse(
        total_investors=total_investors,
        active_opportunities=active_opportunities,
        total_raised=total_raised,
        active_partnerships=active_partnerships,
        featured_investors=featured_investors,
    )

"""
Business Intelligence API Routes

API endpoints for:
- Company discovery and management
- Opportunity pipeline tracking
- Demo generation and management
- Outreach campaign management
- Market analysis and business metrics
"""

from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_, or_
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import json

from app.core.database import get_db
from app.models.business_intelligence import (
    Company, Opportunity, Demo, OutreachCampaign, OutreachContact, BusinessMetric
)
from app.services.demo_generator import DemoGenerator, create_demo_for_opportunity
from pydantic import BaseModel, Field


# Pydantic models for API requests/responses
class CompanyCreate(BaseModel):
    name: str
    website: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    industry: Optional[str] = None
    employee_count: Optional[int] = None


class CompanyResponse(BaseModel):
    id: int
    name: str
    website: Optional[str]
    description: Optional[str]
    location: Optional[str]
    industry: Optional[str]
    employee_count: Optional[int]
    opportunity_score: Optional[float]
    automation_opportunities: Optional[List[str]]
    tech_stack: Optional[List[str]]
    
    class Config:
        from_attributes = True


class OpportunityCreate(BaseModel):
    company_id: int
    title: str
    description: str
    category: str
    estimated_value: Optional[float] = None
    priority: str = Field(default="medium", pattern="^(low|medium|high)$")


class OpportunityResponse(BaseModel):
    id: int
    company_id: int
    company_name: Optional[str]
    title: str
    description: str
    category: str
    estimated_value: Optional[float]
    score: Optional[float]
    priority: str
    stage: str
    status: str
    days_in_stage: Optional[int]
    next_action: Optional[str]
    next_action_date: Optional[datetime]
    
    class Config:
        from_attributes = True


class DemoCreate(BaseModel):
    opportunity_id: int
    demo_type: str = Field(default="web_app", pattern="^(web_app|automation_script|dashboard|api_integration)$")
    technologies: List[str] = []
    features: List[str] = []


class DemoResponse(BaseModel):
    id: int
    company_id: int
    opportunity_id: int
    title: str
    description: Optional[str]
    demo_type: str
    status: str
    completion_percentage: float
    demo_url: Optional[str]
    technologies_used: Optional[List[str]]
    features_demonstrated: Optional[List[str]]
    development_hours: Optional[float]
    development_cost: Optional[float]
    
    class Config:
        from_attributes = True


class CampaignCreate(BaseModel):
    name: str
    description: Optional[str] = None
    campaign_type: str = "cold_email"
    message_template: str
    subject_template: Optional[str] = None


class MarketAnalysisResponse(BaseModel):
    total_market_value: float
    market_growth_rate: float
    active_companies: int
    new_companies: int
    automation_score: float
    competition_level: str
    competitors_count: int
    opportunity_trends: List[Dict[str, Any]]
    industry_distribution: List[Dict[str, Any]]
    region_data: List[Dict[str, Any]]
    competitor_analysis: List[Dict[str, Any]]


router = APIRouter(prefix="/api/v1/business", tags=["business-intelligence"])


# Company endpoints
@router.get("/companies", response_model=Dict[str, Any])
async def get_companies(
    search: Optional[str] = Query(None),
    location: Optional[str] = Query(None),
    industry: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Get companies with filtering and pagination"""
    query = db.query(Company)
    
    if search:
        query = query.filter(
            or_(
                Company.name.ilike(f"%{search}%"),
                Company.description.ilike(f"%{search}%")
            )
        )
    
    if location:
        query = query.filter(Company.location.ilike(f"%{location}%"))
    
    if industry:
        query = query.filter(Company.industry == industry)
    
    # Get totals before pagination
    total = query.count()
    high_priority = query.filter(Company.opportunity_score >= 80).count()
    growth_companies = query.filter(Company.employee_count > 100).count()
    recent = query.filter(
        Company.created_at >= datetime.now() - timedelta(days=30)
    ).count()
    
    # Apply pagination
    companies = query.order_by(desc(Company.opportunity_score)).offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "high_priority": high_priority,
        "growth_companies": growth_companies,
        "recent": recent,
        "items": [CompanyResponse.from_orm(company) for company in companies]
    }


@router.post("/companies", response_model=CompanyResponse)
async def create_company(company: CompanyCreate, db: Session = Depends(get_db)):
    """Create a new company"""
    db_company = Company(**company.dict())
    db.add(db_company)
    db.commit()
    db.refresh(db_company)
    return CompanyResponse.from_orm(db_company)


@router.get("/companies/{company_id}", response_model=CompanyResponse)
async def get_company(company_id: int, db: Session = Depends(get_db)):
    """Get a specific company by ID"""
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return CompanyResponse.from_orm(company)


# Opportunity endpoints
@router.get("/opportunities", response_model=Dict[str, Any])
async def get_opportunities(
    stage: Optional[str] = Query(None),
    sort_by: str = Query("score", pattern="^(score|value|created_at|priority)$"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Get opportunities with filtering and pagination"""
    query = db.query(Opportunity).join(Company)
    
    if stage:
        query = query.filter(Opportunity.stage == stage)
    
    # Apply sorting
    if sort_by == "score":
        query = query.order_by(desc(Opportunity.score))
    elif sort_by == "value":
        query = query.order_by(desc(Opportunity.estimated_value))
    elif sort_by == "created_at":
        query = query.order_by(desc(Opportunity.created_at))
    elif sort_by == "priority":
        # Custom priority ordering: high, medium, low
        query = query.order_by(
            func.case(
                (Opportunity.priority == "high", 1),
                (Opportunity.priority == "medium", 2),
                else_=3
            )
        )
    
    # Get stage counts
    stage_counts = db.query(
        Opportunity.stage,
        func.count(Opportunity.id).label('count')
    ).group_by(Opportunity.stage).all()
    
    stages = {
        "discovery": 0,
        "analysis": 0,
        "demo_creation": 0,
        "outreach": 0,
        "negotiation": 0,
        "closed": 0
    }
    
    for stage_name, count in stage_counts:
        if stage_name in stages:
            stages[stage_name] = count
    
    # Get summary metrics
    total = query.count()
    total_value = db.query(func.sum(Opportunity.estimated_value)).scalar() or 0
    win_rate = 25.5  # Placeholder - calculate from closed opportunities
    avg_cycle_days = 45  # Placeholder - calculate from opportunity history
    
    # Apply pagination
    opportunities = query.offset(skip).limit(limit).all()
    
    # Enrich with company names
    result_items = []
    for opp in opportunities:
        opp_dict = OpportunityResponse.from_orm(opp).dict()
        opp_dict["company_name"] = opp.company.name
        result_items.append(opp_dict)
    
    return {
        "total": total,
        "total_value": float(total_value),
        "win_rate": win_rate,
        "avg_cycle_days": avg_cycle_days,
        "stages": stages,
        "items": result_items
    }


@router.post("/opportunities", response_model=OpportunityResponse)
async def create_opportunity(opportunity: OpportunityCreate, db: Session = Depends(get_db)):
    """Create a new business opportunity"""
    # Verify company exists
    company = db.query(Company).filter(Company.id == opportunity.company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    db_opportunity = Opportunity(**opportunity.dict())
    db.add(db_opportunity)
    db.commit()
    db.refresh(db_opportunity)
    
    result = OpportunityResponse.from_orm(db_opportunity)
    return result


@router.put("/opportunities/{opportunity_id}/stage")
async def update_opportunity_stage(
    opportunity_id: int,
    stage: str = Field(..., pattern="^(discovery|analysis|demo_creation|outreach|negotiation|closed)$"),
    db: Session = Depends(get_db)
):
    """Update opportunity stage"""
    opportunity = db.query(Opportunity).filter(Opportunity.id == opportunity_id).first()
    if not opportunity:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    
    opportunity.stage = stage
    opportunity.days_in_stage = 0  # Reset days in stage
    db.commit()
    
    return {"message": "Stage updated successfully"}


# Demo endpoints
@router.get("/demos", response_model=List[DemoResponse])
async def get_demos(
    status: Optional[str] = Query(None),
    demo_type: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get demos with optional filtering"""
    query = db.query(Demo)
    
    if status:
        query = query.filter(Demo.status == status)
    
    if demo_type:
        query = query.filter(Demo.demo_type == demo_type)
    
    demos = query.order_by(desc(Demo.created_at)).all()
    return [DemoResponse.from_orm(demo) for demo in demos]


@router.post("/demos", response_model=DemoResponse)
async def create_demo(
    demo: DemoCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Create and generate a new demo"""
    # Verify opportunity exists
    opportunity = db.query(Opportunity).filter(Opportunity.id == demo.opportunity_id).first()
    if not opportunity:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    
    # Add demo generation to background tasks
    background_tasks.add_task(
        create_demo_for_opportunity,
        demo.opportunity_id,
        demo.demo_type
    )
    
    # Create initial demo record
    db_demo = Demo(
        company_id=opportunity.company_id,
        opportunity_id=demo.opportunity_id,
        title=f"{opportunity.title} - Demo",
        demo_type=demo.demo_type,
        status="planning",
        technologies_used=demo.technologies,
        features_demonstrated=demo.features
    )
    
    db.add(db_demo)
    db.commit()
    db.refresh(db_demo)
    
    return DemoResponse.from_orm(db_demo)


@router.get("/demos/{demo_id}", response_model=DemoResponse)
async def get_demo(demo_id: int, db: Session = Depends(get_db)):
    """Get a specific demo by ID"""
    demo = db.query(Demo).filter(Demo.id == demo_id).first()
    if not demo:
        raise HTTPException(status_code=404, detail="Demo not found")
    return DemoResponse.from_orm(demo)


# Market Analysis endpoints
@router.get("/market-analysis", response_model=MarketAnalysisResponse)
async def get_market_analysis(
    time_range: str = Query("30d", pattern="^(7d|30d|90d|1y)$"),
    region: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get comprehensive market analysis"""
    
    # Calculate date range
    if time_range == "7d":
        start_date = datetime.now() - timedelta(days=7)
    elif time_range == "30d":
        start_date = datetime.now() - timedelta(days=30)
    elif time_range == "90d":
        start_date = datetime.now() - timedelta(days=90)
    else:  # 1y
        start_date = datetime.now() - timedelta(days=365)
    
    # Basic market metrics
    total_companies = db.query(Company).count()
    new_companies = db.query(Company).filter(
        Company.created_at >= start_date
    ).count()
    
    total_value = db.query(func.sum(Opportunity.estimated_value)).scalar() or 0
    avg_automation_score = db.query(func.avg(Company.automation_readiness_score)).scalar() or 0
    
    # Mock data for demo purposes - in production, these would be calculated from real data
    opportunity_trends = [
        {"date": "2024-01-01", "opportunities": 45, "value": 125000},
        {"date": "2024-01-08", "opportunities": 52, "value": 140000},
        {"date": "2024-01-15", "opportunities": 48, "value": 135000},
        {"date": "2024-01-22", "opportunities": 61, "value": 155000},
        {"date": "2024-01-29", "opportunities": 58, "value": 148000}
    ]
    
    industry_distribution = [
        {"name": "Technology", "value": 35},
        {"name": "Healthcare", "value": 25},
        {"name": "Finance", "value": 20},
        {"name": "Retail", "value": 12},
        {"name": "Manufacturing", "value": 8}
    ]
    
    region_data = [
        {"region": "North America", "companies": 145, "opportunities": 210},
        {"region": "Europe", "companies": 89, "opportunities": 156},
        {"region": "Asia Pacific", "companies": 67, "opportunities": 123}
    ]
    
    competitor_analysis = [
        {
            "name": "AutoFlow Solutions",
            "description": "Workflow automation platform",
            "market_share": 15.2,
            "coverage": "North America",
            "threat_level": "high",
            "strengths": ["Established brand", "Large customer base"],
            "opportunities": ["Limited AI features", "High pricing"]
        },
        {
            "name": "ProcessBot",
            "description": "Business process automation",
            "market_share": 8.7,
            "coverage": "Global",
            "threat_level": "medium",
            "strengths": ["Global presence", "Integration capabilities"],
            "opportunities": ["Complex setup", "Poor user experience"]
        }
    ]
    
    return MarketAnalysisResponse(
        total_market_value=float(total_value),
        market_growth_rate=12.5,
        active_companies=total_companies,
        new_companies=new_companies,
        automation_score=float(avg_automation_score),
        competition_level="Medium",
        competitors_count=len(competitor_analysis),
        opportunity_trends=opportunity_trends,
        industry_distribution=industry_distribution,
        region_data=region_data,
        competitor_analysis=competitor_analysis
    )


# Outreach endpoints
@router.get("/outreach", response_model=Dict[str, Any])
async def get_outreach_data(
    status: Optional[str] = Query(None),
    sort_by: str = Query("created_at"),
    db: Session = Depends(get_db)
):
    """Get outreach campaigns and contacts"""
    
    # Get campaigns
    campaigns_query = db.query(OutreachCampaign)
    campaigns = campaigns_query.order_by(desc(OutreachCampaign.created_at)).all()
    
    # Get contacts
    contacts_query = db.query(OutreachContact).join(Company)
    if status:
        contacts_query = contacts_query.filter(OutreachContact.status == status)
    
    contacts = contacts_query.order_by(desc(OutreachContact.created_at)).limit(50).all()
    
    # Calculate stats
    total_sent = db.query(func.sum(OutreachCampaign.sent_count)).scalar() or 0
    total_opens = db.query(func.sum(OutreachCampaign.opened_count)).scalar() or 0
    total_responses = db.query(func.sum(OutreachCampaign.replied_count)).scalar() or 0
    total_meetings = db.query(func.sum(OutreachCampaign.meeting_count)).scalar() or 0
    
    stats = {
        "total_sent": total_sent,
        "sent_this_week": 23,  # Mock data
        "open_rate": (total_opens / total_sent * 100) if total_sent > 0 else 0,
        "total_opens": total_opens,
        "response_rate": (total_responses / total_sent * 100) if total_sent > 0 else 0,
        "total_responses": total_responses,
        "meeting_rate": (total_meetings / total_sent * 100) if total_sent > 0 else 0,
        "total_meetings": total_meetings
    }
    
    # Format campaign data
    campaign_data = []
    for campaign in campaigns:
        campaign_data.append({
            "id": campaign.id,
            "name": campaign.name,
            "description": campaign.description,
            "status": campaign.status,
            "total_contacts": campaign.total_contacts,
            "sent_count": campaign.sent_count,
            "response_count": campaign.replied_count,
            "response_rate": campaign.response_rate,
            "message_template": campaign.message_template
        })
    
    # Format contact data
    contact_data = []
    for contact in contacts:
        contact_data.append({
            "id": contact.id,
            "name": contact.name,
            "title": contact.title,
            "company": contact.company.name,
            "email": contact.email,
            "status": contact.status,
            "last_contact_date": contact.last_contact_date,
            "next_followup_date": contact.next_followup_date,
            "last_message": contact.response_content
        })
    
    return {
        "stats": stats,
        "campaigns": campaign_data,
        "contacts": contact_data
    }


@router.post("/outreach/campaigns", response_model=Dict[str, str])
async def create_outreach_campaign(campaign: CampaignCreate, db: Session = Depends(get_db)):
    """Create a new outreach campaign"""
    db_campaign = OutreachCampaign(**campaign.dict())
    db.add(db_campaign)
    db.commit()
    db.refresh(db_campaign)
    
    return {"message": "Campaign created successfully", "id": str(db_campaign.id)}


@router.post("/discovery/start")
async def start_company_discovery(
    search_terms: List[str],
    location: Optional[str] = None,
    industry: Optional[str] = None,
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: Session = Depends(get_db)
):
    """Start automated company discovery process"""
    
    # Add discovery task to background processing
    # In production, this would trigger actual web scraping and analysis
    
    return {
        "message": "Company discovery started",
        "search_terms": search_terms,
        "location": location,
        "industry": industry,
        "estimated_completion": "2-4 hours"
    }


# Demo metrics endpoint
@router.get("/demos/metrics")
async def get_demo_metrics(days: int = Query(30, ge=1, le=365), db: Session = Depends(get_db)):
    """Get demo generation metrics"""
    generator = DemoGenerator(db)
    return generator.get_demo_metrics(days)
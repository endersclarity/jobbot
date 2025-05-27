"""
Business Intelligence API Routes

RESTful endpoints for company discovery, opportunity management, 
and business intelligence analytics.
"""

import asyncio
from typing import List, Optional, Dict, Any
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import desc, func

from app.core.database import get_db
from app.models.business_intelligence import (
    Company, BusinessOpportunity, DecisionMaker, CompanyTechStack, 
    WebsiteAudit, OutreachRecord
)
from app.scrapers.business_discovery import BusinessDirectoryScaper, discover_companies_in_grass_valley
from app.analysis.tech_stack_detector import analyze_company_tech_stack
from app.analysis.opportunity_scorer import OpportunityScorer, get_prioritized_opportunities
from pydantic import BaseModel, Field


# Pydantic models for API requests/responses
class CompanyResponse(BaseModel):
    id: int
    name: str
    domain: Optional[str]
    website_url: Optional[str]
    industry: Optional[str]
    city: Optional[str]
    state: Optional[str]
    business_status: str
    opportunity_score: float
    priority_level: str
    last_scraped: Optional[datetime]
    
    class Config:
        from_attributes = True


class BusinessOpportunityResponse(BaseModel):
    id: int
    company_id: int
    company_name: Optional[str]
    opportunity_type: str
    title: str
    description: str
    estimated_value: Optional[float]
    effort_estimate_hours: Optional[int]
    urgency_score: Optional[float]
    value_score: Optional[float]
    feasibility_score: Optional[float]
    total_score: Optional[float]
    status: str
    discovery_date: datetime
    
    class Config:
        from_attributes = True


class TechStackResponse(BaseModel):
    id: int
    tech_name: str
    tech_category: str
    tech_version: Optional[str]
    confidence_score: float
    is_outdated: bool
    is_vulnerable: bool
    
    class Config:
        from_attributes = True


class DecisionMakerResponse(BaseModel):
    id: int
    company_id: int
    name: str
    title: Optional[str]
    department: Optional[str]
    seniority: Optional[str]
    email: Optional[str]
    linkedin_url: Optional[str]
    contact_priority: int
    relationship_status: str
    
    class Config:
        from_attributes = True


class CompanyDiscoveryRequest(BaseModel):
    location: str = Field(..., description="Location to search (e.g., 'Grass Valley, CA')")
    industries: Optional[List[str]] = Field(default=None, description="Industries to target")
    max_companies: int = Field(default=50, description="Maximum companies to discover")


class OpportunityCreateRequest(BaseModel):
    company_id: int
    opportunity_type: str
    title: str
    description: str
    estimated_value: Optional[float] = None
    effort_estimate_hours: Optional[int] = None


router = APIRouter(prefix="/api/v1/business-intelligence", tags=["business-intelligence"])


@router.get("/companies", response_model=List[CompanyResponse])
async def get_companies(
    industry: Optional[str] = None,
    location: Optional[str] = None,
    min_opportunity_score: Optional[float] = None,
    priority_level: Optional[str] = None,
    limit: int = Query(default=50, le=200),
    db: Session = Depends(get_db)
):
    """Get companies with optional filtering"""
    query = db.query(Company)
    
    if industry:
        query = query.filter(Company.industry.ilike(f"%{industry}%"))
    
    if location:
        query = query.filter(
            (Company.city.ilike(f"%{location}%")) | 
            (Company.state.ilike(f"%{location}%"))
        )
    
    if min_opportunity_score is not None:
        query = query.filter(Company.opportunity_score >= min_opportunity_score)
    
    if priority_level:
        query = query.filter(Company.priority_level == priority_level)
    
    # Order by opportunity score descending
    companies = query.order_by(desc(Company.opportunity_score)).limit(limit).all()
    
    # Add company_name to response (it's already the name field)
    response_companies = []
    for company in companies:
        company_dict = {
            'id': company.id,
            'name': company.name,
            'domain': company.domain,
            'website_url': company.website_url,
            'industry': company.industry,
            'city': company.city,
            'state': company.state,
            'business_status': company.business_status,
            'opportunity_score': company.opportunity_score,
            'priority_level': company.priority_level,
            'last_scraped': company.last_scraped
        }
        response_companies.append(CompanyResponse(**company_dict))
    
    return response_companies


@router.get("/companies/{company_id}", response_model=CompanyResponse)
async def get_company(company_id: int, db: Session = Depends(get_db)):
    """Get specific company details"""
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    return CompanyResponse.from_orm(company)


@router.get("/companies/{company_id}/tech-stack", response_model=List[TechStackResponse])
async def get_company_tech_stack(company_id: int, db: Session = Depends(get_db)):
    """Get company's technology stack analysis"""
    # Verify company exists
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    tech_stack = db.query(CompanyTechStack).filter(
        CompanyTechStack.company_id == company_id
    ).all()
    
    return [TechStackResponse.from_orm(tech) for tech in tech_stack]


@router.get("/companies/{company_id}/decision-makers", response_model=List[DecisionMakerResponse])
async def get_company_decision_makers(company_id: int, db: Session = Depends(get_db)):
    """Get company's decision makers and key contacts"""
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    decision_makers = db.query(DecisionMaker).filter(
        DecisionMaker.company_id == company_id
    ).order_by(desc(DecisionMaker.contact_priority)).all()
    
    return [DecisionMakerResponse.from_orm(dm) for dm in decision_makers]


@router.get("/opportunities", response_model=List[BusinessOpportunityResponse])
async def get_opportunities(
    opportunity_type: Optional[str] = None,
    min_score: Optional[float] = None,
    status: Optional[str] = None,
    company_id: Optional[int] = None,
    limit: int = Query(default=50, le=200),
    db: Session = Depends(get_db)
):
    """Get business opportunities with optional filtering"""
    query = db.query(BusinessOpportunity)
    
    if opportunity_type:
        query = query.filter(BusinessOpportunity.opportunity_type == opportunity_type)
    
    if min_score is not None:
        query = query.filter(BusinessOpportunity.total_score >= min_score)
    
    if status:
        query = query.filter(BusinessOpportunity.status == status)
    
    if company_id:
        query = query.filter(BusinessOpportunity.company_id == company_id)
    
    opportunities = query.order_by(desc(BusinessOpportunity.total_score)).limit(limit).all()
    
    # Add company names to responses
    response_opportunities = []
    for opp in opportunities:
        company = db.query(Company).filter(Company.id == opp.company_id).first()
        opp_dict = {
            'id': opp.id,
            'company_id': opp.company_id,
            'company_name': company.name if company else None,
            'opportunity_type': opp.opportunity_type,
            'title': opp.title,
            'description': opp.description,
            'estimated_value': opp.estimated_value,
            'effort_estimate_hours': opp.effort_estimate_hours,
            'urgency_score': opp.urgency_score,
            'value_score': opp.value_score,
            'feasibility_score': opp.feasibility_score,
            'total_score': opp.total_score,
            'status': opp.status,
            'discovery_date': opp.discovery_date
        }
        response_opportunities.append(BusinessOpportunityResponse(**opp_dict))
    
    return response_opportunities


@router.get("/opportunities/{opportunity_id}", response_model=BusinessOpportunityResponse)
async def get_opportunity(opportunity_id: int, db: Session = Depends(get_db)):
    """Get specific opportunity details"""
    opportunity = db.query(BusinessOpportunity).filter(
        BusinessOpportunity.id == opportunity_id
    ).first()
    
    if not opportunity:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    
    # Get company name
    company = db.query(Company).filter(Company.id == opportunity.company_id).first()
    
    opp_dict = {
        'id': opportunity.id,
        'company_id': opportunity.company_id,
        'company_name': company.name if company else None,
        'opportunity_type': opportunity.opportunity_type,
        'title': opportunity.title,
        'description': opportunity.description,
        'estimated_value': opportunity.estimated_value,
        'effort_estimate_hours': opportunity.effort_estimate_hours,
        'urgency_score': opportunity.urgency_score,
        'value_score': opportunity.value_score,
        'feasibility_score': opportunity.feasibility_score,
        'total_score': opportunity.total_score,
        'status': opportunity.status,
        'discovery_date': opportunity.discovery_date
    }
    
    return BusinessOpportunityResponse(**opp_dict)


@router.post("/opportunities", response_model=BusinessOpportunityResponse)
async def create_opportunity(
    opportunity_data: OpportunityCreateRequest,
    db: Session = Depends(get_db)
):
    """Create a new business opportunity"""
    # Verify company exists
    company = db.query(Company).filter(Company.id == opportunity_data.company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    # Create opportunity
    opportunity = BusinessOpportunity(
        company_id=opportunity_data.company_id,
        opportunity_type=opportunity_data.opportunity_type,
        title=opportunity_data.title,
        description=opportunity_data.description,
        estimated_value=opportunity_data.estimated_value,
        effort_estimate_hours=opportunity_data.effort_estimate_hours,
        status='identified'
    )
    
    db.add(opportunity)
    db.commit()
    db.refresh(opportunity)
    
    # Score the new opportunity
    scorer = OpportunityScorer(db)
    scorer.score_opportunity(opportunity)
    
    opp_dict = {
        'id': opportunity.id,
        'company_id': opportunity.company_id,
        'company_name': company.name,
        'opportunity_type': opportunity.opportunity_type,
        'title': opportunity.title,
        'description': opportunity.description,
        'estimated_value': opportunity.estimated_value,
        'effort_estimate_hours': opportunity.effort_estimate_hours,
        'urgency_score': opportunity.urgency_score,
        'value_score': opportunity.value_score,
        'feasibility_score': opportunity.feasibility_score,
        'total_score': opportunity.total_score,
        'status': opportunity.status,
        'discovery_date': opportunity.discovery_date
    }
    
    return BusinessOpportunityResponse(**opp_dict)


@router.post("/discover-companies")
async def discover_companies(
    discovery_request: CompanyDiscoveryRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Discover companies in a specific location"""
    
    # Add discovery task to background
    def run_discovery():
        """Background task to discover companies"""
        try:
            scraper = BusinessDirectoryScaper(db)
            companies = asyncio.run(scraper.discover_companies_in_location(
                location=discovery_request.location,
                industries=discovery_request.industries
            ))
            return len(companies)
        except Exception as e:
            print(f"Discovery error: {e}")
            return 0
    
    background_tasks.add_task(run_discovery)
    
    return {
        "message": "Company discovery started",
        "location": discovery_request.location,
        "status": "running"
    }


@router.post("/companies/{company_id}/analyze")
async def analyze_company(
    company_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Analyze a company's technology stack and identify opportunities"""
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    # Add analysis task to background
    def run_analysis():
        """Background task to analyze company"""
        try:
            analysis_result = asyncio.run(analyze_company_tech_stack(company, db))
            return analysis_result
        except Exception as e:
            print(f"Analysis error: {e}")
            return {"error": str(e)}
    
    background_tasks.add_task(run_analysis)
    
    return {
        "message": "Company analysis started",
        "company_id": company_id,
        "company_name": company.name,
        "status": "running"
    }


@router.post("/score-opportunities")
async def score_opportunities(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Score all opportunities in the system"""
    
    def run_scoring():
        """Background task to score opportunities"""
        try:
            scorer = OpportunityScorer(db)
            results = scorer.score_all_opportunities()
            return results
        except Exception as e:
            print(f"Scoring error: {e}")
            return {"error": str(e)}
    
    background_tasks.add_task(run_scoring)
    
    return {
        "message": "Opportunity scoring started",
        "status": "running"
    }


@router.get("/dashboard/analytics")
async def get_dashboard_analytics(db: Session = Depends(get_db)):
    """Get comprehensive analytics for the business intelligence dashboard"""
    
    # Company statistics
    total_companies = db.query(Company).count()
    active_companies = db.query(Company).filter(Company.business_status == 'active').count()
    
    # Opportunity statistics
    total_opportunities = db.query(BusinessOpportunity).count()
    high_value_opportunities = db.query(BusinessOpportunity).filter(
        BusinessOpportunity.total_score >= 7.0
    ).count()
    
    # Recent activity
    recent_companies = db.query(Company).filter(
        Company.last_scraped >= datetime.now().replace(day=1)  # This month
    ).count()
    
    # Top industries
    industry_stats = db.query(
        Company.industry,
        func.count(Company.id).label('count'),
        func.avg(Company.opportunity_score).label('avg_score')
    ).group_by(Company.industry).order_by(desc('count')).limit(10).all()
    
    # Top opportunity types
    opportunity_type_stats = db.query(
        BusinessOpportunity.opportunity_type,
        func.count(BusinessOpportunity.id).label('count'),
        func.avg(BusinessOpportunity.total_score).label('avg_score'),
        func.sum(BusinessOpportunity.estimated_value).label('total_value')
    ).group_by(BusinessOpportunity.opportunity_type).order_by(desc('total_value')).limit(10).all()
    
    return {
        "overview": {
            "total_companies": total_companies,
            "active_companies": active_companies,
            "total_opportunities": total_opportunities,
            "high_value_opportunities": high_value_opportunities,
            "recent_discoveries": recent_companies
        },
        "industries": [
            {
                "industry": stat.industry,
                "company_count": stat.count,
                "avg_opportunity_score": float(stat.avg_score) if stat.avg_score else 0.0
            }
            for stat in industry_stats
        ],
        "opportunity_types": [
            {
                "type": stat.opportunity_type,
                "count": stat.count,
                "avg_score": float(stat.avg_score) if stat.avg_score else 0.0,
                "total_value": float(stat.total_value) if stat.total_value else 0.0
            }
            for stat in opportunity_type_stats
        ]
    }


@router.get("/prioritized-opportunities")
async def get_prioritized_opportunities_endpoint(
    limit: int = Query(default=20, le=100),
    db: Session = Depends(get_db)
):
    """Get prioritized list of opportunities for action"""
    try:
        opportunities = get_prioritized_opportunities(db, limit)
        return {
            "opportunities": opportunities,
            "total_count": len(opportunities)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting prioritized opportunities: {str(e)}")


@router.get("/companies/{company_id}/website-audit")
async def get_website_audit(company_id: int, db: Session = Depends(get_db)):
    """Get latest website audit for a company"""
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    # Get latest audit
    audit = db.query(WebsiteAudit).filter(
        WebsiteAudit.company_id == company_id
    ).order_by(desc(WebsiteAudit.audit_date)).first()
    
    if not audit:
        raise HTTPException(status_code=404, detail="No website audit found for this company")
    
    return {
        "audit_id": audit.id,
        "audit_date": audit.audit_date,
        "performance_score": audit.performance_score,
        "page_load_time": audit.page_load_time,
        "ssl_enabled": audit.ssl_enabled,
        "page_size_bytes": audit.page_size_bytes,
        "security_headers": audit.security_headers,
        "security_issues": audit.security_issues,
        "vulnerability_count": audit.vulnerability_count,
        "improvement_opportunities": audit.improvement_opportunities
    }
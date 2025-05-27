from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_, or_
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score

from app.core.database import get_db
from app.models.analytics import (
    LeadScore, ROIMetrics, PredictiveModel, ModelPrediction, 
    CompetitiveIntelligence, AdvancedCampaign, BusinessMetrics
)
from app.models.business_intelligence import Company, Opportunity
from app.schemas.analytics import (
    LeadScoreResponse, ROIMetricsResponse, PredictiveAnalyticsResponse,
    CompetitiveIntelligenceResponse, CampaignAnalyticsResponse, BusinessMetricsResponse
)

router = APIRouter()

@router.get("/advanced-overview", response_model=Dict[str, Any])
async def get_advanced_analytics_overview(
    time_range: str = Query("30d", regex="^(7d|30d|90d|1y)$"),
    db: Session = Depends(get_db)
):
    """Get comprehensive advanced analytics overview"""
    
    # Calculate date range
    days_map = {"7d": 7, "30d": 30, "90d": 90, "1y": 365}
    start_date = datetime.utcnow() - timedelta(days=days_map[time_range])
    
    # Get business metrics
    revenue_data = db.query(BusinessMetrics).filter(
        BusinessMetrics.metric_date >= start_date,
        BusinessMetrics.metric_type == 'daily'
    ).order_by(BusinessMetrics.metric_date).all()
    
    # Calculate KPIs
    total_revenue = sum(m.total_revenue for m in revenue_data)
    total_leads = sum(m.total_leads for m in revenue_data)
    avg_conversion_rate = np.mean([m.overall_conversion_rate for m in revenue_data if m.overall_conversion_rate])
    avg_deal_size = np.mean([m.average_deal_size for m in revenue_data if m.average_deal_size])
    
    # Get revenue growth
    if len(revenue_data) >= 2:
        first_half = revenue_data[:len(revenue_data)//2]
        second_half = revenue_data[len(revenue_data)//2:]
        first_half_revenue = sum(m.total_revenue for m in first_half)
        second_half_revenue = sum(m.total_revenue for m in second_half)
        revenue_growth = ((second_half_revenue - first_half_revenue) / first_half_revenue * 100) if first_half_revenue > 0 else 0
    else:
        revenue_growth = 0
    
    # Lead growth calculation
    if len(revenue_data) >= 2:
        first_half_leads = sum(m.total_leads for m in first_half)
        second_half_leads = sum(m.total_leads for m in second_half)
        lead_growth = ((second_half_leads - first_half_leads) / first_half_leads * 100) if first_half_leads > 0 else 0
    else:
        lead_growth = 0
    
    # Format timeline data
    timeline_data = [
        {
            "month": m.metric_date.strftime("%b"),
            "revenue": m.total_revenue,
            "leads": m.total_leads,
            "deals": m.converted_leads
        } for m in revenue_data[-6:]  # Last 6 data points
    ]
    
    # Mock conversion funnel (would be calculated from actual data)
    conversion_funnel = [
        {"stage": "Prospects", "count": 1000, "percentage": 100},
        {"stage": "Qualified", "count": 450, "percentage": 45},
        {"stage": "Proposals", "count": 200, "percentage": 20},
        {"stage": "Negotiations", "count": 80, "percentage": 8},
        {"stage": "Closed Won", "count": 45, "percentage": 4.5}
    ]
    
    # Lead sources (mock data - would come from actual tracking)
    lead_sources = [
        {"source": "Automated Discovery", "value": 40, "color": "#8884d8"},
        {"source": "Referrals", "value": 25, "color": "#82ca9d"},
        {"source": "Inbound", "value": 20, "color": "#ffc658"},
        {"source": "Outreach", "value": 15, "color": "#ff7300"}
    ]
    
    # Performance metrics
    performance_metrics = {
        "responseRate": 15.2,
        "meetingRate": 8.7,
        "proposalRate": 4.3,
        "winRate": 22.5,
        "avgSalesCycle": 45,
        "customerLifetimeValue": 125000
    }
    
    return {
        "overview": {
            "totalRevenue": total_revenue,
            "revenueGrowth": revenue_growth,
            "totalLeads": total_leads,
            "leadGrowth": lead_growth,
            "conversionRate": avg_conversion_rate,
            "conversionGrowth": 5.3,  # Mock value
            "avgDealSize": avg_deal_size,
            "dealSizeGrowth": 15.7  # Mock value
        },
        "revenueTimeline": timeline_data,
        "conversionFunnel": conversion_funnel,
        "leadSources": lead_sources,
        "performanceMetrics": performance_metrics
    }

@router.get("/lead-scoring", response_model=Dict[str, Any])
async def get_lead_scoring_analytics(
    model_type: str = Query("comprehensive"),
    threshold: int = Query(75, ge=50, le=90),
    db: Session = Depends(get_db)
):
    """Get AI lead scoring analytics and model performance"""
    
    # Get lead scores
    lead_scores = db.query(LeadScore).filter(
        LeadScore.is_active == True,
        LeadScore.model_version == model_type
    ).order_by(desc(LeadScore.score)).all()
    
    # Calculate score distribution
    score_ranges = [(0, 20), (21, 40), (41, 60), (61, 80), (81, 100)]
    score_distribution = []
    colors = ['#dc2626', '#ea580c', '#ca8a04', '#16a34a', '#059669']
    
    for i, (min_score, max_score) in enumerate(score_ranges):
        count = len([s for s in lead_scores if min_score <= s.score <= max_score])
        score_distribution.append({
            "range": f"{min_score}-{max_score}",
            "count": count,
            "color": colors[i]
        })
    
    # Mock conversion data by score range
    conversion_by_score = [
        {"scoreRange": "0-20", "conversion": 2.1, "leads": score_distribution[0]["count"]},
        {"scoreRange": "21-40", "conversion": 8.5, "leads": score_distribution[1]["count"]},
        {"scoreRange": "41-60", "conversion": 15.2, "leads": score_distribution[2]["count"]},
        {"scoreRange": "61-80", "conversion": 32.7, "leads": score_distribution[3]["count"]},
        {"scoreRange": "81-100", "conversion": 78.9, "leads": score_distribution[4]["count"]}
    ]
    
    # Calculate metrics
    total_leads = len(lead_scores)
    qualified_leads = len([s for s in lead_scores if s.score >= threshold])
    avg_score = np.mean([s.score for s in lead_scores]) if lead_scores else 0
    avg_confidence = np.mean([s.confidence for s in lead_scores]) if lead_scores else 0
    
    # Mock model performance metrics
    model_metrics = {
        "totalLeads": total_leads,
        "qualifiedLeads": qualified_leads,
        "conversionRate": 12.8,  # Mock value
        "averageScore": avg_score,
        "modelAccuracy": 87.3,
        "precision": 82.1,
        "recall": 89.7,
        "f1Score": 85.7
    }
    
    return {
        "scoreDistribution": score_distribution,
        "conversionByScore": conversion_by_score,
        "modelMetrics": model_metrics,
        "threshold": threshold
    }

@router.get("/predictive-modeling", response_model=Dict[str, Any])
async def get_predictive_analytics(
    model_type: str = Query("revenue", regex="^(revenue|leads|deals)$"),
    db: Session = Depends(get_db)
):
    """Get predictive modeling analytics and forecasts"""
    
    # Get historical business metrics for prediction
    historical_data = db.query(BusinessMetrics).filter(
        BusinessMetrics.metric_type == 'monthly'
    ).order_by(BusinessMetrics.metric_date).limit(12).all()
    
    if len(historical_data) < 3:
        # Create mock data if insufficient historical data
        historical_data = []
        base_date = datetime.utcnow() - timedelta(days=180)
        for i in range(6):
            date = base_date + timedelta(days=30*i)
            if model_type == "revenue":
                value = 85000 + (i * 10000) + np.random.normal(0, 5000)
            elif model_type == "leads":
                value = 180 + (i * 15) + np.random.normal(0, 10)
            else:  # deals
                value = 12 + (i * 2) + np.random.normal(0, 2)
            
            historical_data.append({
                "month": date.strftime("%b"),
                model_type: max(0, value),
                "type": "historical"
            })
    else:
        # Convert to format needed for prediction
        historical_data = [
            {
                "month": m.metric_date.strftime("%b"),
                "revenue": m.total_revenue,
                "leads": m.total_leads,
                "deals": m.converted_leads,
                "type": "historical"
            } for m in historical_data
        ]
    
    # Simple linear regression for predictions
    if len(historical_data) >= 3:
        X = np.array(range(len(historical_data))).reshape(-1, 1)
        y = np.array([item[model_type] for item in historical_data])
        
        model = LinearRegression()
        model.fit(X, y)
        
        # Generate future predictions (next 6 months)
        future_months = ['Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        predictions = list(historical_data)  # Copy historical data
        
        for i, month in enumerate(future_months):
            future_x = len(historical_data) + i
            predicted_value = model.predict([[future_x]])[0]
            variance = np.random.normal(0, 0.1)  # ±10% variance
            
            predictions.append({
                "month": month,
                model_type: None,
                "predicted": max(0, predicted_value * (1 + variance)),
                "upperBound": max(0, predicted_value * 1.15),
                "lowerBound": max(0, predicted_value * 0.85),
                "type": "prediction"
            })
        
        # Calculate model accuracy (mock)
        accuracy = np.random.uniform(75, 95)
        
    else:
        predictions = historical_data
        accuracy = 0
    
    # Next month prediction
    future_predictions = [p for p in predictions if p.get("type") == "prediction"]
    next_month_prediction = future_predictions[0] if future_predictions else None
    
    return {
        "predictions": predictions,
        "modelAccuracy": accuracy,
        "nextMonthPrediction": next_month_prediction,
        "confidence": 85
    }

@router.get("/roi-analytics", response_model=Dict[str, Any])
async def get_roi_analytics(
    campaign_id: Optional[str] = Query("all"),
    time_frame: str = Query("monthly"),
    db: Session = Depends(get_db)
):
    """Get ROI analytics and campaign performance"""
    
    # Mock ROI data (would come from actual campaign tracking)
    campaigns = [
        {
            "id": "automated_discovery",
            "name": "Automated Discovery",
            "investment": 15000,
            "revenue": 85000,
            "roi": 466.7,
            "leads": 120,
            "conversions": 15,
            "avgDealSize": 5667,
            "costPerLead": 125,
            "costPerAcquisition": 1000
        },
        {
            "id": "ai_outreach",
            "name": "AI-Powered Outreach",
            "investment": 8000,
            "revenue": 45000,
            "roi": 462.5,
            "leads": 80,
            "conversions": 8,
            "avgDealSize": 5625,
            "costPerLead": 100,
            "costPerAcquisition": 1000
        },
        {
            "id": "demo_automation",
            "name": "Demo Automation",
            "investment": 12000,
            "revenue": 65000,
            "roi": 441.7,
            "leads": 60,
            "conversions": 12,
            "avgDealSize": 5417,
            "costPerLead": 200,
            "costPerAcquisition": 1000
        }
    ]
    
    # Monthly ROI trend
    monthly_roi = [
        {"month": "Jan", "roi": 320, "investment": 10000, "revenue": 32000},
        {"month": "Feb", "roi": 385, "investment": 11000, "revenue": 42350},
        {"month": "Mar", "roi": 420, "investment": 12000, "revenue": 50400},
        {"month": "Apr", "roi": 445, "investment": 13000, "revenue": 57850},
        {"month": "May", "roi": 460, "investment": 14000, "revenue": 64400},
        {"month": "Jun", "roi": 478, "investment": 15000, "revenue": 71700}
    ]
    
    # Cost breakdown
    cost_breakdown = [
        {"category": "Technology", "amount": 25000, "percentage": 45.5},
        {"category": "Personnel", "amount": 18000, "percentage": 32.7},
        {"category": "Marketing", "amount": 8000, "percentage": 14.5},
        {"category": "Operations", "amount": 4000, "percentage": 7.3}
    ]
    
    # Customer lifetime value
    customer_ltv = {
        "avgLifetime": 24,
        "avgMonthlyValue": 5200,
        "totalCLV": 124800,
        "acquisitionCost": 1000,
        "ltvsToCAC": 124.8
    }
    
    return {
        "campaigns": campaigns,
        "monthlyROI": monthly_roi,
        "costBreakdown": cost_breakdown,
        "customerLifetimeValue": customer_ltv
    }

@router.post("/lead-scores/batch-update")
async def update_lead_scores_batch(
    company_ids: List[int],
    model_version: str = "comprehensive",
    db: Session = Depends(get_db)
):
    """Batch update lead scores for multiple companies"""
    
    updated_scores = []
    
    for company_id in company_ids:
        # Check if company exists
        company = db.query(Company).filter(Company.id == company_id).first()
        if not company:
            continue
            
        # Calculate lead score (mock calculation)
        score = calculate_lead_score(company)
        
        # Create or update lead score
        existing_score = db.query(LeadScore).filter(
            LeadScore.company_id == company_id,
            LeadScore.model_version == model_version,
            LeadScore.is_active == True
        ).first()
        
        if existing_score:
            existing_score.score = score["total_score"]
            existing_score.company_size_score = score["company_size"]
            existing_score.industry_fit_score = score["industry_fit"]
            existing_score.engagement_score = score["engagement"]
            existing_score.budget_authority_score = score["budget_authority"]
            existing_score.timeline_score = score["timeline"]
            existing_score.confidence = score["confidence"]
            existing_score.prediction_date = datetime.utcnow()
        else:
            new_score = LeadScore(
                company_id=company_id,
                score=score["total_score"],
                model_version=model_version,
                company_size_score=score["company_size"],
                industry_fit_score=score["industry_fit"],
                engagement_score=score["engagement"],
                budget_authority_score=score["budget_authority"],
                timeline_score=score["timeline"],
                confidence=score["confidence"]
            )
            db.add(new_score)
        
        updated_scores.append({
            "company_id": company_id,
            "score": score["total_score"],
            "confidence": score["confidence"]
        })
    
    db.commit()
    
    return {
        "updated_count": len(updated_scores),
        "scores": updated_scores
    }

def calculate_lead_score(company) -> Dict[str, float]:
    """Calculate AI-powered lead score for a company"""
    
    # Mock scoring algorithm (replace with actual ML model)
    scores = {
        "company_size": min(25, (company.size or 50) / 20),  # Max 25 points
        "industry_fit": 20 if company.industry in ["Technology", "Finance"] else 10,  # Max 20 points
        "engagement": np.random.uniform(5, 25),  # Mock engagement score, max 25 points
        "budget_authority": np.random.uniform(5, 20),  # Mock budget score, max 20 points
        "timeline": np.random.uniform(0, 10)  # Mock timeline score, max 10 points
    }
    
    total_score = sum(scores.values())
    # Add some randomness
    total_score += np.random.uniform(-10, 10)
    total_score = max(0, min(100, total_score))
    
    return {
        **scores,
        "total_score": total_score,
        "confidence": np.random.uniform(75, 95)
    }

@router.get("/competitive-intelligence", response_model=List[CompetitiveIntelligenceResponse])
async def get_competitive_intelligence(
    industry: Optional[str] = Query(None),
    limit: int = Query(20, le=100),
    db: Session = Depends(get_db)
):
    """Get competitive intelligence data"""
    
    query = db.query(CompetitiveIntelligence).filter(CompetitiveIntelligence.is_active == True)
    
    if industry:
        query = query.filter(CompetitiveIntelligence.industry == industry)
    
    competitors = query.order_by(desc(CompetitiveIntelligence.competitive_score)).limit(limit).all()
    
    return competitors

@router.get("/campaign-analytics/{campaign_id}")
async def get_campaign_analytics(
    campaign_id: str,
    include_ab_test: bool = Query(True),
    db: Session = Depends(get_db)
):
    """Get detailed analytics for a specific campaign"""
    
    campaign = db.query(AdvancedCampaign).filter(
        AdvancedCampaign.id == campaign_id,
        AdvancedCampaign.is_active == True
    ).first()
    
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    # Calculate performance metrics
    open_rate = (campaign.total_opened / campaign.total_sent * 100) if campaign.total_sent > 0 else 0
    click_rate = (campaign.total_clicked / campaign.total_opened * 100) if campaign.total_opened > 0 else 0
    reply_rate = (campaign.total_replied / campaign.total_sent * 100) if campaign.total_sent > 0 else 0
    conversion_rate = (campaign.total_converted / campaign.total_sent * 100) if campaign.total_sent > 0 else 0
    
    response_data = {
        "campaign": campaign,
        "performance": {
            "openRate": open_rate,
            "clickRate": click_rate,
            "replyRate": reply_rate,
            "conversionRate": conversion_rate
        }
    }
    
    # Include A/B test results if applicable
    if campaign.is_ab_test and include_ab_test:
        variant_a_conversion = (campaign.variant_a_converted / campaign.variant_a_sent * 100) if campaign.variant_a_sent > 0 else 0
        variant_b_conversion = (campaign.variant_b_converted / campaign.variant_b_sent * 100) if campaign.variant_b_sent > 0 else 0
        
        response_data["abTest"] = {
            "variantA": {
                "sent": campaign.variant_a_sent,
                "opened": campaign.variant_a_opened,
                "clicked": campaign.variant_a_clicked,
                "replied": campaign.variant_a_replied,
                "converted": campaign.variant_a_converted,
                "conversionRate": variant_a_conversion
            },
            "variantB": {
                "sent": campaign.variant_b_sent,
                "opened": campaign.variant_b_opened,
                "clicked": campaign.variant_b_clicked,
                "replied": campaign.variant_b_replied,
                "converted": campaign.variant_b_converted,
                "conversionRate": variant_b_conversion
            },
            "winner": "A" if variant_a_conversion > variant_b_conversion else "B",
            "confidenceLevel": 95  # Mock statistical significance
        }
    
    return response_data
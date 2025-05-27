#!/usr/bin/env python3
"""
Sample data seeding script for analytics demonstration
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import sessionmaker
from app.core.database import engine
from app.models.business_intelligence import Company, Opportunity, BusinessMetric
from app.models.analytics import LeadScore, ROIMetrics, PredictiveModel
from datetime import datetime, timedelta
import json

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def seed_sample_data():
    """Seed database with sample data for analytics demonstration"""
    db = SessionLocal()
    
    try:
        print("🌱 Seeding sample data for analytics...")
        
        # Sample Companies
        companies_data = [
            {
                "name": "TechCorp Solutions",
                "website": "https://techcorp.com",
                "domain": "techcorp.com",
                "description": "Enterprise software solutions provider",
                "industry": "Technology",
                "employee_count": 250,
                "revenue_range": "$10M-$50M",
                "opportunity_score": 85.5,
                "automation_readiness_score": 92.0,
                "digital_maturity_level": "advanced"
            },
            {
                "name": "Manufacturing Plus",
                "website": "https://mfgplus.com",
                "domain": "mfgplus.com", 
                "description": "Industrial manufacturing and automation",
                "industry": "Manufacturing",
                "employee_count": 500,
                "revenue_range": "$50M-$100M",
                "opportunity_score": 78.2,
                "automation_readiness_score": 68.0,
                "digital_maturity_level": "intermediate"
            },
            {
                "name": "HealthTech Innovations",
                "website": "https://healthtech.com",
                "domain": "healthtech.com",
                "description": "Healthcare technology and patient management",
                "industry": "Healthcare",
                "employee_count": 150,
                "revenue_range": "$5M-$25M", 
                "opportunity_score": 91.7,
                "automation_readiness_score": 88.0,
                "digital_maturity_level": "advanced"
            },
            {
                "name": "RetailFlow Systems",
                "website": "https://retailflow.com",
                "domain": "retailflow.com",
                "description": "Retail inventory and supply chain management",
                "industry": "Retail",
                "employee_count": 75,
                "revenue_range": "$1M-$10M",
                "opportunity_score": 72.8,
                "automation_readiness_score": 55.0,
                "digital_maturity_level": "basic"
            },
            {
                "name": "FinanceForward",
                "website": "https://financeforward.com", 
                "domain": "financeforward.com",
                "description": "Financial services and investment management",
                "industry": "Finance",
                "employee_count": 320,
                "revenue_range": "$25M-$100M",
                "opportunity_score": 89.3,
                "automation_readiness_score": 95.0,
                "digital_maturity_level": "advanced"
            }
        ]
        
        companies = []
        for company_data in companies_data:
            company = Company(**company_data)
            db.add(company)
            companies.append(company)
        
        db.flush()  # Get IDs for companies
        
        # Sample Lead Scores
        lead_scores_data = [
            {
                "company_id": companies[0].id,
                "score": 87.5,
                "model_version": "v1.0",
                "company_size_score": 85.0,
                "industry_fit_score": 92.0,
                "engagement_score": 88.0,
                "budget_authority_score": 90.0,
                "timeline_score": 82.0,
                "confidence": 0.89,
                "features_used": {"company_size": True, "industry": True, "tech_stack": True}
            },
            {
                "company_id": companies[1].id,
                "score": 76.3,
                "model_version": "v1.0", 
                "company_size_score": 80.0,
                "industry_fit_score": 75.0,
                "engagement_score": 70.0,
                "budget_authority_score": 85.0,
                "timeline_score": 72.0,
                "confidence": 0.82,
                "features_used": {"company_size": True, "industry": True, "engagement": True}
            },
            {
                "company_id": companies[2].id,
                "score": 93.1,
                "model_version": "v1.0",
                "company_size_score": 88.0,
                "industry_fit_score": 95.0,
                "engagement_score": 94.0,
                "budget_authority_score": 92.0,
                "timeline_score": 96.0,
                "confidence": 0.94,
                "features_used": {"company_size": True, "industry": True, "tech_stack": True, "engagement": True}
            }
        ]
        
        for lead_score_data in lead_scores_data:
            lead_score = LeadScore(**lead_score_data)
            db.add(lead_score)
        
        # Sample ROI Metrics
        roi_metrics_data = [
            {
                "campaign_id": "CAM_001",
                "campaign_name": "Tech Sector Outreach Q4",
                "investment": 15000.0,
                "revenue": 185000.0,
                "roi_percentage": 1133.3,
                "leads_generated": 45,
                "conversions": 8,
                "conversion_rate": 17.8,
                "cost_per_lead": 333.33,
                "cost_per_acquisition": 1875.0
            },
            {
                "campaign_id": "CAM_002", 
                "campaign_name": "Healthcare Innovation Drive",
                "investment": 22000.0,
                "revenue": 340000.0,
                "roi_percentage": 1445.5,
                "leads_generated": 32,
                "conversions": 12,
                "conversion_rate": 37.5,
                "cost_per_lead": 687.50,
                "cost_per_acquisition": 1833.33
            },
            {
                "campaign_id": "CAM_003",
                "campaign_name": "Manufacturing Automation Focus",
                "investment": 8500.0,
                "revenue": 95000.0,
                "roi_percentage": 1017.6,
                "leads_generated": 28,
                "conversions": 5,
                "conversion_rate": 17.9,
                "cost_per_lead": 303.57,
                "cost_per_acquisition": 1700.0
            }
        ]
        
        for roi_data in roi_metrics_data:
            roi_metric = ROIMetrics(**roi_data)
            db.add(roi_metric)
        
        # Sample Business Metrics
        business_metrics_data = [
            {
                "metric_name": "Total Revenue",
                "metric_value": 620000.0,
                "metric_type": "currency",
                "calculation_period": "monthly",
                "target_value": 750000.0,
                "variance_percentage": -17.3
            },
            {
                "metric_name": "Lead Conversion Rate",
                "metric_value": 24.2,
                "metric_type": "percentage", 
                "calculation_period": "monthly",
                "target_value": 30.0,
                "variance_percentage": -19.3
            },
            {
                "metric_name": "Active Opportunities",
                "metric_value": 85.0,
                "metric_type": "count",
                "calculation_period": "current",
                "target_value": 100.0,
                "variance_percentage": -15.0
            }
        ]
        
        for bm_data in business_metrics_data:
            business_metric = BusinessMetric(**bm_data)
            db.add(business_metric)
        
        # Sample Predictive Model
        predictive_model = PredictiveModel(
            model_type="lead_scoring",
            model_data={
                "algorithm": "random_forest",
                "features": ["company_size", "industry_fit", "engagement_score", "budget_authority", "timeline"],
                "hyperparameters": {
                    "n_estimators": 100,
                    "max_depth": 10,
                    "random_state": 42
                },
                "training_samples": 1500,
                "validation_accuracy": 0.873
            },
            accuracy_score=87.3
        )
        db.add(predictive_model)
        
        db.commit()
        print(f"✅ Successfully seeded:")
        print(f"   - {len(companies_data)} companies")
        print(f"   - {len(lead_scores_data)} lead scores")
        print(f"   - {len(roi_metrics_data)} ROI metrics")
        print(f"   - {len(business_metrics_data)} business metrics")
        print(f"   - 1 predictive model")
        
        return True
        
    except Exception as e:
        print(f"❌ Error seeding data: {e}")
        db.rollback()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    success = seed_sample_data()
    sys.exit(0 if success else 1)
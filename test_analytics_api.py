#!/usr/bin/env python3
"""Test analytics API and create sample data"""

from app.core.database import SessionLocal
from app.models.analytics import BusinessMetrics, LeadScore, ROIMetrics, PredictiveModel
from datetime import datetime, timedelta
import random

def create_sample_data():
    db = SessionLocal()
    
    try:
        # Create sample business metrics for the last 30 days
        for i in range(30):
            date = datetime.utcnow() - timedelta(days=i)
            metric = BusinessMetrics(
                metric_date=date,
                metric_type='daily',
                total_revenue=random.uniform(10000, 50000),
                recurring_revenue=random.uniform(8000, 40000),
                new_revenue=random.uniform(2000, 10000),
                total_leads=random.randint(50, 200),
                qualified_leads=random.randint(20, 80),
                hot_leads=random.randint(5, 20),
                converted_leads=random.randint(2, 10),
                total_opportunities=random.randint(10, 50),
                pipeline_value=random.uniform(100000, 500000),
                average_deal_size=random.uniform(5000, 25000),
                sales_cycle_days=random.uniform(15, 45),
                lead_to_opportunity_rate=random.uniform(0.2, 0.5),
                opportunity_to_close_rate=random.uniform(0.1, 0.3),
                overall_conversion_rate=random.uniform(0.05, 0.15),
                new_customers=random.randint(1, 5),
                churned_customers=random.randint(0, 2),
                customer_lifetime_value=random.uniform(50000, 150000),
                customer_acquisition_cost=random.uniform(1000, 5000)
            )
            db.add(metric)
        
        # Create sample lead scores
        for i in range(20):
            score = LeadScore(
                company_id=i+1,
                score=random.uniform(20, 95),
                model_version="comprehensive",
                company_size_score=random.uniform(50, 100),
                industry_fit_score=random.uniform(40, 95),
                engagement_score=random.uniform(30, 90),
                budget_authority_score=random.uniform(40, 95),
                timeline_score=random.uniform(50, 100),
                confidence=random.uniform(70, 95),
                prediction_date=datetime.utcnow() - timedelta(days=random.randint(0, 7)),
                is_active=True
            )
            db.add(score)
        
        # Create sample ROI metrics
        campaigns = ["Email Campaign", "LinkedIn Outreach", "Demo Automation", "Cold Calling", "Content Marketing"]
        for i, campaign in enumerate(campaigns):
            roi = ROIMetrics(
                campaign_id=f"camp_{i+1}",
                campaign_name=campaign,
                investment=random.uniform(5000, 20000),
                revenue=random.uniform(20000, 100000),
                roi_percentage=random.uniform(200, 600),
                leads_generated=random.randint(50, 200),
                conversions=random.randint(5, 30),
                conversion_rate=random.uniform(0.05, 0.20),
                cost_per_lead=random.uniform(50, 200),
                cost_per_acquisition=random.uniform(500, 2000),
                average_deal_size=random.uniform(3000, 10000),
                start_date=datetime.utcnow() - timedelta(days=30),
                measurement_date=datetime.utcnow(),
                is_active=True
            )
            db.add(roi)
        
        # Create a sample predictive model
        model = PredictiveModel(
            model_name="Revenue Predictor",
            model_type="revenue",
            version="1.0.0",
            accuracy=87.5,
            precision_score=85.2,
            recall=89.8,
            f1_score=87.4,
            training_data_size=10000,
            features_count=25,
            algorithm="RandomForest",
            features_list=["company_size", "industry", "engagement_score", "budget", "timeline"],
            training_date=datetime.utcnow() - timedelta(days=1),
            is_active=True,
            is_production=True
        )
        db.add(model)
        
        db.commit()
        print("✅ Sample data created successfully!")
        
    except Exception as e:
        print(f"❌ Error creating sample data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_sample_data()
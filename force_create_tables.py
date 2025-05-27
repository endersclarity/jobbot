#!/usr/bin/env python3
"""Force create analytics tables bypassing constraints"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import text
from app.core.database import engine
from app.models.analytics import LeadScore, ROIMetrics, PredictiveModel, ModelPrediction, CompetitiveIntelligence, AdvancedCampaign, BusinessMetrics

def force_create_analytics_tables():
    try:
        with engine.connect() as conn:
            # Start transaction
            trans = conn.begin()
            
            # Create analytics tables only
            print("🔨 Creating analytics tables...")
            
            # Create lead_scores table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS lead_scores (
                    id SERIAL PRIMARY KEY,
                    company_id INTEGER REFERENCES companies(id),
                    score FLOAT NOT NULL,
                    model_version VARCHAR(50) NOT NULL,
                    company_size_score FLOAT DEFAULT 0.0,
                    industry_fit_score FLOAT DEFAULT 0.0,
                    engagement_score FLOAT DEFAULT 0.0,
                    budget_authority_score FLOAT DEFAULT 0.0,
                    timeline_score FLOAT DEFAULT 0.0,
                    confidence FLOAT DEFAULT 0.0,
                    features_used JSON,
                    prediction_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    is_active BOOLEAN DEFAULT TRUE
                )
            """))
            
            # Create roi_metrics table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS roi_metrics (
                    id SERIAL PRIMARY KEY,
                    campaign_id VARCHAR(100) NOT NULL,
                    campaign_name VARCHAR(200) NOT NULL,
                    investment FLOAT NOT NULL,
                    revenue FLOAT NOT NULL,
                    roi_percentage FLOAT NOT NULL,
                    leads_generated INTEGER DEFAULT 0,
                    conversions INTEGER DEFAULT 0,
                    conversion_rate FLOAT DEFAULT 0.0,
                    cost_per_lead FLOAT DEFAULT 0.0,
                    cost_per_acquisition FLOAT DEFAULT 0.0,
                    average_deal_size FLOAT,
                    start_date TIMESTAMP WITH TIME ZONE NOT NULL,
                    end_date TIMESTAMP WITH TIME ZONE,
                    measurement_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    campaign_type VARCHAR(100),
                    target_audience VARCHAR(200),
                    channels_used JSON,
                    is_active BOOLEAN DEFAULT TRUE
                )
            """))
            
            # Create predictive_models table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS predictive_models (
                    id SERIAL PRIMARY KEY,
                    model_name VARCHAR(100) NOT NULL UNIQUE,
                    model_type VARCHAR(50) NOT NULL,
                    version VARCHAR(20) NOT NULL,
                    accuracy FLOAT NOT NULL,
                    precision_score FLOAT NOT NULL,
                    recall FLOAT NOT NULL,
                    f1_score FLOAT NOT NULL,
                    mean_absolute_error FLOAT,
                    training_data_size INTEGER NOT NULL,
                    features_count INTEGER NOT NULL,
                    features_list JSON,
                    training_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    algorithm VARCHAR(100) NOT NULL,
                    hyperparameters JSON,
                    is_active BOOLEAN DEFAULT TRUE,
                    is_production BOOLEAN DEFAULT FALSE
                )
            """))
            
            # Create analytics_business_metrics table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS analytics_business_metrics (
                    id SERIAL PRIMARY KEY,
                    metric_date TIMESTAMP WITH TIME ZONE NOT NULL,
                    metric_type VARCHAR(50) NOT NULL,
                    total_revenue FLOAT,
                    recurring_revenue FLOAT,
                    new_revenue FLOAT,
                    total_leads INTEGER,
                    qualified_leads INTEGER,
                    hot_leads INTEGER,
                    converted_leads INTEGER,
                    total_opportunities INTEGER,
                    pipeline_value FLOAT,
                    average_deal_size FLOAT,
                    sales_cycle_days FLOAT,
                    lead_to_opportunity_rate FLOAT,
                    opportunity_to_close_rate FLOAT,
                    overall_conversion_rate FLOAT,
                    new_customers INTEGER,
                    churned_customers INTEGER,
                    customer_lifetime_value FLOAT,
                    customer_acquisition_cost FLOAT,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                )
            """))
            
            # Commit transaction
            trans.commit()
            print("✅ Analytics tables created successfully")
            
            # Verify tables
            result = conn.execute(text("""
                SELECT table_name FROM information_schema.tables 
                WHERE table_schema = 'public' AND table_name IN 
                ('lead_scores', 'roi_metrics', 'predictive_models', 'analytics_business_metrics')
                ORDER BY table_name
            """))
            tables = [row[0] for row in result]
            print(f"📋 Created analytics tables: {tables}")
            
            return True
            
    except Exception as e:
        print(f"❌ Error creating analytics tables: {e}")
        return False

if __name__ == "__main__":
    success = force_create_analytics_tables()
    sys.exit(0 if success else 1)
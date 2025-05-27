from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class LeadScore(Base):
    """Lead scoring model for AI-powered qualification"""
    __tablename__ = "lead_scores"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    score = Column(Float, nullable=False, index=True)
    model_version = Column(String(50), nullable=False)
    
    # Scoring factors
    company_size_score = Column(Float, default=0.0)
    industry_fit_score = Column(Float, default=0.0)
    engagement_score = Column(Float, default=0.0)
    budget_authority_score = Column(Float, default=0.0)
    timeline_score = Column(Float, default=0.0)
    
    # Model metadata
    confidence = Column(Float, default=0.0)
    features_used = Column(JSON)
    prediction_date = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True)
    
    # Relationships
    company = relationship("Company", back_populates="lead_scores")

class ROIMetrics(Base):
    """ROI tracking and analytics"""
    __tablename__ = "roi_metrics"

    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(String(100), nullable=False, index=True)
    campaign_name = Column(String(200), nullable=False)
    
    # Financial metrics
    investment = Column(Float, nullable=False)
    revenue = Column(Float, nullable=False)
    roi_percentage = Column(Float, nullable=False)
    
    # Performance metrics
    leads_generated = Column(Integer, default=0)
    conversions = Column(Integer, default=0)
    conversion_rate = Column(Float, default=0.0)
    cost_per_lead = Column(Float, default=0.0)
    cost_per_acquisition = Column(Float, default=0.0)
    average_deal_size = Column(Float, default=0.0)
    
    # Time tracking
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True))
    measurement_date = Column(DateTime(timezone=True), server_default=func.now())
    
    # Campaign details
    campaign_type = Column(String(100))
    target_audience = Column(String(200))
    channels_used = Column(JSON)
    
    is_active = Column(Boolean, default=True)

class PredictiveModel(Base):
    """Predictive analytics model metadata and performance"""
    __tablename__ = "predictive_models"

    id = Column(Integer, primary_key=True, index=True)
    model_name = Column(String(100), nullable=False, unique=True)
    model_type = Column(String(50), nullable=False)  # 'revenue', 'leads', 'conversion'
    version = Column(String(20), nullable=False)
    
    # Model performance
    accuracy = Column(Float, nullable=False)
    precision_score = Column(Float, nullable=False)
    recall = Column(Float, nullable=False)
    f1_score = Column(Float, nullable=False)
    mean_absolute_error = Column(Float)
    
    # Training metadata
    training_data_size = Column(Integer, nullable=False)
    features_count = Column(Integer, nullable=False)
    features_list = Column(JSON)
    training_date = Column(DateTime(timezone=True), server_default=func.now())
    
    # Model configuration
    algorithm = Column(String(100), nullable=False)
    hyperparameters = Column(JSON)
    
    is_active = Column(Boolean, default=True)
    is_production = Column(Boolean, default=False)

class ModelPrediction(Base):
    """Individual predictions made by predictive models"""
    __tablename__ = "model_predictions"

    id = Column(Integer, primary_key=True, index=True)
    model_id = Column(Integer, ForeignKey("predictive_models.id"), nullable=False)
    
    # Prediction details
    prediction_type = Column(String(50), nullable=False)
    predicted_value = Column(Float, nullable=False)
    confidence_score = Column(Float, nullable=False)
    prediction_date = Column(DateTime(timezone=True), server_default=func.now())
    target_date = Column(DateTime(timezone=True), nullable=False)
    
    # Input features
    input_features = Column(JSON, nullable=False)
    
    # Validation (when actual value becomes available)
    actual_value = Column(Float)
    error_percentage = Column(Float)
    validation_date = Column(DateTime(timezone=True))
    
    # Relationships
    model = relationship("PredictiveModel", backref="predictions")

class CompetitiveIntelligence(Base):
    """Competitive analysis and market intelligence"""
    __tablename__ = "competitive_intelligence"

    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String(200), nullable=False)
    industry = Column(String(100), nullable=False, index=True)
    
    # Company metrics
    estimated_revenue = Column(Float)
    employee_count = Column(Integer)
    market_share = Column(Float)
    growth_rate = Column(Float)
    
    # Competitive positioning
    competitive_score = Column(Float, default=0.0)
    strengths = Column(JSON)
    weaknesses = Column(JSON)
    threats = Column(JSON)
    opportunities = Column(JSON)
    
    # Market intelligence
    pricing_strategy = Column(Text)
    key_differentiators = Column(JSON)
    target_customers = Column(JSON)
    marketing_channels = Column(JSON)
    
    # Data sources and freshness
    data_sources = Column(JSON)
    last_updated = Column(DateTime(timezone=True), server_default=func.now())
    confidence_level = Column(Float, default=0.0)
    
    is_active = Column(Boolean, default=True)

class AdvancedCampaign(Base):
    """Advanced campaign management with A/B testing"""
    __tablename__ = "advanced_campaigns"

    id = Column(Integer, primary_key=True, index=True)
    campaign_name = Column(String(200), nullable=False)
    campaign_type = Column(String(100), nullable=False)  # 'email', 'social', 'demo', 'outreach'
    
    # A/B Testing
    is_ab_test = Column(Boolean, default=False)
    variant_a_config = Column(JSON)
    variant_b_config = Column(JSON)
    traffic_split = Column(Float, default=50.0)  # Percentage for variant A
    
    # Campaign performance
    total_sent = Column(Integer, default=0)
    total_opened = Column(Integer, default=0)
    total_clicked = Column(Integer, default=0)
    total_replied = Column(Integer, default=0)
    total_converted = Column(Integer, default=0)
    
    # Variant A performance
    variant_a_sent = Column(Integer, default=0)
    variant_a_opened = Column(Integer, default=0)
    variant_a_clicked = Column(Integer, default=0)
    variant_a_replied = Column(Integer, default=0)
    variant_a_converted = Column(Integer, default=0)
    
    # Variant B performance
    variant_b_sent = Column(Integer, default=0)
    variant_b_opened = Column(Integer, default=0)
    variant_b_clicked = Column(Integer, default=0)
    variant_b_replied = Column(Integer, default=0)
    variant_b_converted = Column(Integer, default=0)
    
    # Campaign timing
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Campaign configuration
    target_audience = Column(JSON)
    message_templates = Column(JSON)
    automation_rules = Column(JSON)
    
    is_active = Column(Boolean, default=True)
    is_completed = Column(Boolean, default=False)

class BusinessMetrics(Base):
    """Daily/weekly/monthly business metrics aggregation"""
    __tablename__ = "business_metrics"

    id = Column(Integer, primary_key=True, index=True)
    metric_date = Column(DateTime(timezone=True), nullable=False, index=True)
    metric_type = Column(String(50), nullable=False)  # 'daily', 'weekly', 'monthly'
    
    # Revenue metrics
    total_revenue = Column(Float, default=0.0)
    recurring_revenue = Column(Float, default=0.0)
    new_revenue = Column(Float, default=0.0)
    
    # Lead metrics
    total_leads = Column(Integer, default=0)
    qualified_leads = Column(Integer, default=0)
    hot_leads = Column(Integer, default=0)
    converted_leads = Column(Integer, default=0)
    
    # Pipeline metrics
    total_opportunities = Column(Integer, default=0)
    pipeline_value = Column(Float, default=0.0)
    average_deal_size = Column(Float, default=0.0)
    sales_cycle_days = Column(Float, default=0.0)
    
    # Conversion metrics
    lead_to_opportunity_rate = Column(Float, default=0.0)
    opportunity_to_close_rate = Column(Float, default=0.0)
    overall_conversion_rate = Column(Float, default=0.0)
    
    # Customer metrics
    new_customers = Column(Integer, default=0)
    churned_customers = Column(Integer, default=0)
    customer_lifetime_value = Column(Float, default=0.0)
    customer_acquisition_cost = Column(Float, default=0.0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class ModelType(str, Enum):
    REVENUE = "revenue"
    LEADS = "leads"
    DEALS = "deals"
    CONVERSION = "conversion"

class CampaignType(str, Enum):
    EMAIL = "email"
    SOCIAL = "social"
    DEMO = "demo"
    OUTREACH = "outreach"
    DISCOVERY = "discovery"

class MetricType(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"

# Lead Scoring Schemas
class LeadScoreBase(BaseModel):
    company_id: int
    score: float = Field(..., ge=0, le=100)
    model_version: str
    company_size_score: float = 0.0
    industry_fit_score: float = 0.0
    engagement_score: float = 0.0
    budget_authority_score: float = 0.0
    timeline_score: float = 0.0
    confidence: float = Field(..., ge=0, le=100)
    
    class Config:
        protected_namespaces = ()

class LeadScoreCreate(LeadScoreBase):
    features_used: Optional[Dict[str, Any]] = None

class LeadScoreResponse(LeadScoreBase):
    id: int
    prediction_date: datetime
    is_active: bool
    features_used: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True

# ROI Analytics Schemas
class ROIMetricsBase(BaseModel):
    campaign_id: str
    campaign_name: str
    investment: float = Field(..., ge=0)
    revenue: float = Field(..., ge=0)
    roi_percentage: float
    leads_generated: int = 0
    conversions: int = 0
    conversion_rate: float = 0.0
    cost_per_lead: float = 0.0
    cost_per_acquisition: float = 0.0
    average_deal_size: float = 0.0

class ROIMetricsCreate(ROIMetricsBase):
    start_date: datetime
    end_date: Optional[datetime] = None
    campaign_type: Optional[str] = None
    target_audience: Optional[str] = None
    channels_used: Optional[List[str]] = None

class ROIMetricsResponse(ROIMetricsBase):
    id: int
    start_date: datetime
    end_date: Optional[datetime] = None
    measurement_date: datetime
    campaign_type: Optional[str] = None
    target_audience: Optional[str] = None
    channels_used: Optional[List[str]] = None
    is_active: bool
    
    class Config:
        from_attributes = True

# Predictive Analytics Schemas
class PredictiveModelBase(BaseModel):
    model_name: str
    model_type: ModelType
    version: str
    accuracy: float = Field(..., ge=0, le=100)
    precision_score: float = Field(..., ge=0, le=100)
    recall: float = Field(..., ge=0, le=100)
    f1_score: float = Field(..., ge=0, le=100)
    training_data_size: int = Field(..., gt=0)
    features_count: int = Field(..., gt=0)
    algorithm: str
    
    class Config:
        protected_namespaces = ()

class PredictiveModelCreate(PredictiveModelBase):
    features_list: List[str]
    hyperparameters: Optional[Dict[str, Any]] = None
    mean_absolute_error: Optional[float] = None

class PredictiveModelResponse(PredictiveModelBase):
    id: int
    features_list: List[str]
    hyperparameters: Optional[Dict[str, Any]] = None
    mean_absolute_error: Optional[float] = None
    training_date: datetime
    is_active: bool
    is_production: bool
    
    class Config:
        from_attributes = True

class ModelPredictionBase(BaseModel):
    model_id: int
    prediction_type: str
    predicted_value: float
    confidence_score: float = Field(..., ge=0, le=100)
    target_date: datetime
    input_features: Dict[str, Any]
    
    class Config:
        protected_namespaces = ()

class ModelPredictionCreate(ModelPredictionBase):
    pass

class ModelPredictionResponse(ModelPredictionBase):
    id: int
    prediction_date: datetime
    actual_value: Optional[float] = None
    error_percentage: Optional[float] = None
    validation_date: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class PredictiveAnalyticsResponse(BaseModel):
    model: PredictiveModelResponse
    predictions: List[ModelPredictionResponse]
    accuracy_trend: List[Dict[str, Any]]
    feature_importance: Dict[str, float]

# Competitive Intelligence Schemas
class CompetitiveIntelligenceBase(BaseModel):
    company_name: str
    industry: str
    estimated_revenue: Optional[float] = None
    employee_count: Optional[int] = None
    market_share: Optional[float] = None
    growth_rate: Optional[float] = None
    competitive_score: float = Field(default=0.0, ge=0, le=100)

class CompetitiveIntelligenceCreate(CompetitiveIntelligenceBase):
    strengths: Optional[List[str]] = None
    weaknesses: Optional[List[str]] = None
    threats: Optional[List[str]] = None
    opportunities: Optional[List[str]] = None
    pricing_strategy: Optional[str] = None
    key_differentiators: Optional[List[str]] = None
    target_customers: Optional[List[str]] = None
    marketing_channels: Optional[List[str]] = None
    data_sources: Optional[List[str]] = None
    confidence_level: float = Field(default=0.0, ge=0, le=100)

class CompetitiveIntelligenceResponse(CompetitiveIntelligenceBase):
    id: int
    strengths: Optional[List[str]] = None
    weaknesses: Optional[List[str]] = None
    threats: Optional[List[str]] = None
    opportunities: Optional[List[str]] = None
    pricing_strategy: Optional[str] = None
    key_differentiators: Optional[List[str]] = None
    target_customers: Optional[List[str]] = None
    marketing_channels: Optional[List[str]] = None
    data_sources: Optional[List[str]] = None
    confidence_level: float
    last_updated: datetime
    is_active: bool
    
    class Config:
        from_attributes = True

# Advanced Campaign Schemas
class AdvancedCampaignBase(BaseModel):
    campaign_name: str
    campaign_type: CampaignType
    is_ab_test: bool = False
    traffic_split: float = Field(default=50.0, ge=0, le=100)

class AdvancedCampaignCreate(AdvancedCampaignBase):
    variant_a_config: Optional[Dict[str, Any]] = None
    variant_b_config: Optional[Dict[str, Any]] = None
    start_date: datetime
    end_date: Optional[datetime] = None
    target_audience: Optional[Dict[str, Any]] = None
    message_templates: Optional[Dict[str, Any]] = None
    automation_rules: Optional[Dict[str, Any]] = None

class AdvancedCampaignResponse(AdvancedCampaignBase):
    id: int
    variant_a_config: Optional[Dict[str, Any]] = None
    variant_b_config: Optional[Dict[str, Any]] = None
    
    # Performance metrics
    total_sent: int = 0
    total_opened: int = 0
    total_clicked: int = 0
    total_replied: int = 0
    total_converted: int = 0
    
    # Variant A performance
    variant_a_sent: int = 0
    variant_a_opened: int = 0
    variant_a_clicked: int = 0
    variant_a_replied: int = 0
    variant_a_converted: int = 0
    
    # Variant B performance
    variant_b_sent: int = 0
    variant_b_opened: int = 0
    variant_b_clicked: int = 0
    variant_b_replied: int = 0
    variant_b_converted: int = 0
    
    start_date: datetime
    end_date: Optional[datetime] = None
    created_at: datetime
    target_audience: Optional[Dict[str, Any]] = None
    message_templates: Optional[Dict[str, Any]] = None
    automation_rules: Optional[Dict[str, Any]] = None
    is_active: bool
    is_completed: bool
    
    class Config:
        from_attributes = True

class CampaignAnalyticsResponse(BaseModel):
    campaign: AdvancedCampaignResponse
    performance: Dict[str, float]
    ab_test: Optional[Dict[str, Any]] = None
    timeline_data: List[Dict[str, Any]]
    segment_performance: Dict[str, Dict[str, float]]

# Business Metrics Schemas
class BusinessMetricsBase(BaseModel):
    metric_date: datetime
    metric_type: MetricType
    total_revenue: float = 0.0
    recurring_revenue: float = 0.0
    new_revenue: float = 0.0
    total_leads: int = 0
    qualified_leads: int = 0
    hot_leads: int = 0
    converted_leads: int = 0
    total_opportunities: int = 0
    pipeline_value: float = 0.0
    average_deal_size: float = 0.0
    sales_cycle_days: float = 0.0

class BusinessMetricsCreate(BusinessMetricsBase):
    lead_to_opportunity_rate: float = 0.0
    opportunity_to_close_rate: float = 0.0
    overall_conversion_rate: float = 0.0
    new_customers: int = 0
    churned_customers: int = 0
    customer_lifetime_value: float = 0.0
    customer_acquisition_cost: float = 0.0

class BusinessMetricsResponse(BusinessMetricsBase):
    id: int
    lead_to_opportunity_rate: float = 0.0
    opportunity_to_close_rate: float = 0.0
    overall_conversion_rate: float = 0.0
    new_customers: int = 0
    churned_customers: int = 0
    customer_lifetime_value: float = 0.0
    customer_acquisition_cost: float = 0.0
    created_at: datetime
    
    class Config:
        from_attributes = True

# Analytics Dashboard Schemas
class AnalyticsDashboardResponse(BaseModel):
    overview: Dict[str, Any]
    revenue_timeline: List[Dict[str, Any]]
    conversion_funnel: List[Dict[str, Any]]
    lead_sources: List[Dict[str, Any]]
    performance_metrics: Dict[str, float]
    top_campaigns: List[ROIMetricsResponse]
    recent_predictions: List[ModelPredictionResponse]

class LeadScoringAnalyticsResponse(BaseModel):
    score_distribution: List[Dict[str, Any]]
    conversion_by_score: List[Dict[str, Any]]
    model_metrics: Dict[str, float]
    top_leads: List[Dict[str, Any]]
    scoring_factors: List[Dict[str, Any]]

# Request/Response Models for Batch Operations
class BatchLeadScoreRequest(BaseModel):
    company_ids: List[int]
    model_version: str = "comprehensive"
    force_recalculate: bool = False

class BatchLeadScoreResponse(BaseModel):
    updated_count: int
    scores: List[Dict[str, Any]]
    errors: Optional[List[Dict[str, str]]] = None

class AdvancedAnalyticsRequest(BaseModel):
    time_range: str = Field("30d", pattern="^(7d|30d|90d|1y)$")
    metrics: List[str] = ["revenue", "leads", "conversion", "roi"]
    include_predictions: bool = True
    include_competitive: bool = False

class AdvancedAnalyticsResponse(BaseModel):
    overview: Dict[str, Any]
    timeline_data: List[Dict[str, Any]]
    predictive_insights: Optional[Dict[str, Any]] = None
    competitive_landscape: Optional[List[CompetitiveIntelligenceResponse]] = None
    roi_analysis: Dict[str, Any]
    lead_scoring: LeadScoringAnalyticsResponse
"""
Database models for Business Intelligence Engine
"""
from app.core.database import Base
from app.models.jobs import Job
from app.models.applications import Application, EmployerResponse, Reference, ReferenceUsage, ExperienceClaim
from app.models.monitoring import (
    ScrapeSession,
    SiteExecution, 
    SessionMetric,
    SystemHealth,
    AlertRule,
    AlertInstance
)
from app.models.business_intelligence import (
    Company,
    CompanyTechStack,
    DecisionMaker,
    BusinessOpportunity,
    OutreachRecord,
    WebsiteAudit,
    Opportunity,
    Demo,
    OutreachCampaign,
    OutreachContact,
    BusinessMetric
)
from app.models.analytics import (
    LeadScore,
    ROIMetrics,
    PredictiveModel,
    ModelPrediction,
    CompetitiveIntelligence,
    AdvancedCampaign,
    BusinessMetrics
)

__all__ = [
    "Base", "Job", "Application", "EmployerResponse", "Reference", "ReferenceUsage", "ExperienceClaim",
    "ScrapeSession", "SiteExecution", "SessionMetric", "SystemHealth", "AlertRule", "AlertInstance",
    "Company", "CompanyTechStack", "DecisionMaker", "BusinessOpportunity", "OutreachRecord", "WebsiteAudit",
    "Opportunity", "Demo", "OutreachCampaign", "OutreachContact", "BusinessMetric",
    "LeadScore", "ROIMetrics", "PredictiveModel", "ModelPrediction", "CompetitiveIntelligence", 
    "AdvancedCampaign", "BusinessMetrics"
]

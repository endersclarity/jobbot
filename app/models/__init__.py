"""
Database models for JobBot
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
    Opportunity,
    Demo,
    OutreachCampaign,
    OutreachContact,
    BusinessMetric
)

__all__ = [
    "Base", "Job", "Application", "EmployerResponse", "Reference", "ReferenceUsage", "ExperienceClaim",
    "ScrapeSession", "SiteExecution", "SessionMetric", "SystemHealth", "AlertRule", "AlertInstance",
    "Company", "Opportunity", "Demo", "OutreachCampaign", "OutreachContact", "BusinessMetric"
]

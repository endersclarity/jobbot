"""
Database models for JobBot
"""
from app.core.database import Base
from app.models.jobs import Job
from app.models.applications import Application, EmployerResponse, Reference, ReferenceUsage, ExperienceClaim
from app.models.monitoring import (
    ScrapeSession, SiteExecution, SessionMetric, SystemHealth, AlertRule, AlertInstance
)

__all__ = [
    "Base", "Job", "Application", "EmployerResponse", "Reference", "ReferenceUsage", "ExperienceClaim",
    "ScrapeSession", "SiteExecution", "SessionMetric", "SystemHealth", "AlertRule", "AlertInstance"
]

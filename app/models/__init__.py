"""
Database models for JobBot
"""
from sqlalchemy.orm import relationship
from app.models.jobs import Job
from app.models.applications import (
    Application, 
    EmployerResponse, 
    Reference, 
    ReferenceUsage, 
    ExperienceClaim
)

# Add reverse relationship to Job model
Job.applications = relationship("Application", back_populates="job", cascade="all, delete-orphan")

__all__ = [
    "Job",
    "Application", 
    "EmployerResponse",
    "Reference",
    "ReferenceUsage", 
    "ExperienceClaim"
]
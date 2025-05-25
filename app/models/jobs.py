"""
Job-related database models
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Date, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Job(Base):
    """Job postings discovered through scraping or manual entry"""

    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    company = Column(String(255), nullable=False, index=True)
    location = Column(String(255), index=True)
    salary_min = Column(Integer, nullable=True)
    salary_max = Column(Integer, nullable=True)
    description = Column(Text, nullable=True)
    requirements = Column(Text, nullable=True)
    benefits = Column(Text, nullable=True)
    job_url = Column(String(500), unique=True, nullable=True)
    source_site = Column(String(100), nullable=True, index=True)
    scraped_date = Column(DateTime(timezone=True), server_default=func.now())
    posting_date = Column(Date, nullable=True)
    application_deadline = Column(Date, nullable=True)
    remote_option = Column(Boolean, default=False, index=True)
    job_type = Column(String(50), nullable=True, index=True)  # full-time, part-time, contract
    experience_level = Column(String(50), nullable=True, index=True)
    industry = Column(String(100), nullable=True, index=True)
    keywords = Column(Text, nullable=True)  # JSON-encoded searchable keywords array
    status = Column(
        String(50), default="discovered", index=True
    )  # discovered, targeted, applied, rejected, interviewing, offer

    # Relationships
    applications = relationship("Application", back_populates="job", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Job(id={self.id}, title='{self.title}', company='{self.company}')>"

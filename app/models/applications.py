"""
Application tracking database models
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Date, Boolean, ForeignKey, DECIMAL, CheckConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class Application(Base):
    """Job applications submitted through the system"""
    __tablename__ = "applications"
    
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False, index=True)
    applied_date = Column(DateTime(timezone=True), server_default=func.now())
    application_method = Column(String(100), nullable=True)  # email, job_board, company_site
    resume_version = Column(String(100), nullable=True)
    cover_letter_version = Column(String(100), nullable=True)
    personal_interest_rating = Column(Integer, CheckConstraint('personal_interest_rating >= 1 AND personal_interest_rating <= 10'), nullable=True)
    compensation_expectation = Column(Integer, nullable=True)
    notes = Column(Text, nullable=True)
    exaggeration_level = Column(Integer, CheckConstraint('exaggeration_level >= 1 AND exaggeration_level <= 5'), nullable=True)  # 1=truthful, 5=heavily exaggerated
    exaggeration_notes = Column(Text, nullable=True)
    application_status = Column(String(50), default='submitted', index=True)
    follow_up_required = Column(Boolean, default=True)
    next_follow_up_date = Column(Date, nullable=True)
    
    # Relationships
    job = relationship("Job", back_populates="applications")
    responses = relationship("EmployerResponse", back_populates="application", cascade="all, delete-orphan")
    reference_usage = relationship("ReferenceUsage", back_populates="application", cascade="all, delete-orphan")
    experience_claims = relationship("ExperienceClaim", back_populates="application", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Application(id={self.id}, job_id={self.job_id}, status='{self.application_status}')>"


class EmployerResponse(Base):
    """Responses received from employers"""
    __tablename__ = "employer_responses"
    
    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("applications.id"), nullable=False, index=True)
    response_date = Column(DateTime(timezone=True), server_default=func.now())
    response_type = Column(String(50), nullable=True, index=True)  # acknowledgment, rejection, interview_request, offer, ghosted
    response_content = Column(Text, nullable=True)
    next_action = Column(String(100), nullable=True)
    interview_scheduled = Column(DateTime(timezone=True), nullable=True)
    response_time_days = Column(Integer, nullable=True)  # calculated field
    sentiment_score = Column(DECIMAL(3, 2), nullable=True)  # AI-analyzed sentiment
    follow_up_needed = Column(Boolean, default=False)
    
    # Relationships
    application = relationship("Application", back_populates="responses")
    
    def __repr__(self):
        return f"<EmployerResponse(id={self.id}, type='{self.response_type}', app_id={self.application_id})>"


class Reference(Base):
    """Professional references for job applications"""
    __tablename__ = "references"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    title = Column(String(255), nullable=True)
    company = Column(String(255), nullable=True)
    email = Column(String(255), nullable=True)
    phone = Column(String(20), nullable=True)
    relationship = Column(String(100), nullable=True)
    credibility_rating = Column(Integer, CheckConstraint('credibility_rating >= 1 AND credibility_rating <= 10'), nullable=True)
    last_contacted = Column(Date, nullable=True)
    times_used = Column(Integer, default=0)
    notes = Column(Text, nullable=True)
    availability_status = Column(String(50), default='available')
    
    # Relationships
    usage_records = relationship("ReferenceUsage", back_populates="reference", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Reference(id={self.id}, name='{self.name}', company='{self.company}')>"


class ReferenceUsage(Base):
    """Tracking reference usage across applications"""
    __tablename__ = "reference_usage"
    
    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("applications.id"), nullable=False, index=True)
    reference_id = Column(Integer, ForeignKey("references.id"), nullable=False, index=True)
    usage_date = Column(DateTime(timezone=True), server_default=func.now())
    context = Column(Text, nullable=True)
    permission_granted = Column(Boolean, default=False)
    
    # Relationships
    application = relationship("Application", back_populates="reference_usage")
    reference = relationship("Reference", back_populates="usage_records")
    
    def __repr__(self):
        return f"<ReferenceUsage(id={self.id}, app_id={self.application_id}, ref_id={self.reference_id})>"


class ExperienceClaim(Base):
    """Tracking experience claims vs reality for integrity monitoring"""
    __tablename__ = "experience_claims"
    
    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("applications.id"), nullable=False, index=True)
    skill_claimed = Column(String(255), nullable=False)
    years_claimed = Column(Integer, nullable=True)
    actual_years = Column(Integer, nullable=True)
    proficiency_claimed = Column(Integer, CheckConstraint('proficiency_claimed >= 1 AND proficiency_claimed <= 10'), nullable=True)
    actual_proficiency = Column(Integer, CheckConstraint('actual_proficiency >= 1 AND actual_proficiency <= 10'), nullable=True)
    verification_source = Column(String(255), nullable=True)
    credibility_notes = Column(Text, nullable=True)
    
    # Relationships
    application = relationship("Application", back_populates="experience_claims")
    
    def __repr__(self):
        return f"<ExperienceClaim(id={self.id}, skill='{self.skill_claimed}', app_id={self.application_id})>"
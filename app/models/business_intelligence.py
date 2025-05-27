"""
Business Intelligence Database Models

Advanced business automation and opportunity tracking models for:
- Company discovery and analysis
- Automation opportunity scoring
- Demo generation and proof-of-concepts
- Outreach campaign management
"""

from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Company(Base):
    """
    Companies discovered through automated research
    """
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    
    # Basic company information
    name = Column(String(200), nullable=False, index=True)
    website = Column(String(500))
    domain = Column(String(200), index=True)
    description = Column(Text)
    
    # Location and contact info
    location = Column(String(200))
    address = Column(Text)
    phone = Column(String(50))
    email = Column(String(200))
    
    # Company details
    industry = Column(String(100), index=True)
    employee_count = Column(Integer)
    revenue_range = Column(String(50))
    founding_year = Column(Integer)
    
    # Technology analysis
    tech_stack = Column(JSON)  # List of detected technologies
    automation_readiness_score = Column(Float)  # 0-100 score
    digital_maturity_level = Column(String(20))  # basic, intermediate, advanced
    
    # Business opportunity analysis
    opportunity_score = Column(Float, index=True)  # 0-100 overall score
    automation_opportunities = Column(JSON)  # List of identified opportunities
    pain_points = Column(JSON)  # List of detected business pain points
    
    # Discovery metadata
    discovery_source = Column(String(100))  # web_scraping, linkedin, etc.
    discovery_date = Column(DateTime(timezone=True), server_default=func.now())
    last_analyzed = Column(DateTime(timezone=True))
    analysis_status = Column(String(50), default="pending")  # pending, analyzed, contacted
    
    # Relationships
    opportunities = relationship("Opportunity", back_populates="company", cascade="all, delete-orphan")
    demos = relationship("Demo", back_populates="company", cascade="all, delete-orphan")
    outreach_contacts = relationship("OutreachContact", back_populates="company", cascade="all, delete-orphan")
    lead_scores = relationship("LeadScore", back_populates="company", cascade="all, delete-orphan")
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<Company(id={self.id}, name='{self.name}', industry='{self.industry}', score={self.opportunity_score})>"


class Opportunity(Base):
    """
    Business opportunities identified for each company
    """
    __tablename__ = "opportunities"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    
    # Opportunity details
    title = Column(String(200), nullable=False)
    description = Column(Text)
    category = Column(String(100))  # automation, optimization, integration, etc.
    
    # Value proposition
    estimated_value = Column(Float)  # Estimated annual value
    implementation_cost = Column(Float)  # Estimated implementation cost
    roi_percentage = Column(Float)  # Calculated ROI
    payback_period_months = Column(Integer)
    
    # Scoring and priority
    score = Column(Float, index=True)  # 0-100 opportunity score
    priority = Column(String(20), default="medium")  # low, medium, high
    confidence_level = Column(Float)  # 0-100 confidence in estimates
    
    # Pipeline tracking
    stage = Column(String(50), default="discovery", index=True)  # discovery, analysis, demo_creation, outreach, negotiation, closed
    status = Column(String(50), default="active")  # active, paused, won, lost
    
    # Progress tracking
    days_in_stage = Column(Integer, default=0)
    next_action = Column(Text)
    next_action_date = Column(DateTime(timezone=True))
    
    # Automation details
    automation_type = Column(String(100))  # workflow, data_processing, reporting, etc.
    technical_requirements = Column(JSON)  # List of technical requirements
    business_impact = Column(JSON)  # List of business impact areas
    
    # Relationships
    company = relationship("Company", back_populates="opportunities")
    demos = relationship("Demo", back_populates="opportunity", cascade="all, delete-orphan")
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<Opportunity(id={self.id}, title='{self.title}', company_id={self.company_id}, stage='{self.stage}')>"


class Demo(Base):
    """
    Generated proof-of-concept demos for opportunities
    """
    __tablename__ = "demos"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    opportunity_id = Column(Integer, ForeignKey("opportunities.id"), nullable=False)
    
    # Demo details
    title = Column(String(200), nullable=False)
    description = Column(Text)
    demo_type = Column(String(100))  # web_app, script, dashboard, automation, etc.
    
    # Demo content
    demo_url = Column(String(500))  # URL to hosted demo
    demo_code_repository = Column(String(500))  # Git repository URL
    demo_files_path = Column(String(500))  # Local file path
    
    # Demo metadata
    technologies_used = Column(JSON)  # List of technologies used
    features_demonstrated = Column(JSON)  # List of features shown
    sample_data_source = Column(String(200))  # Where sample data came from
    
    # Presentation materials
    presentation_slides_url = Column(String(500))
    demo_video_url = Column(String(500))
    documentation_url = Column(String(500))
    
    # Status and tracking
    status = Column(String(50), default="planning")  # planning, development, testing, ready, presented
    completion_percentage = Column(Float, default=0.0)
    
    # Feedback and results
    client_feedback = Column(Text)
    demo_rating = Column(Float)  # 1-5 rating
    conversion_result = Column(String(50))  # interested, meeting_scheduled, proposal_requested, declined
    
    # Development tracking
    development_hours = Column(Float)
    development_cost = Column(Float)
    
    # Relationships
    company = relationship("Company", back_populates="demos")
    opportunity = relationship("Opportunity", back_populates="demos")
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    demo_date = Column(DateTime(timezone=True))  # When demo was presented
    
    def __repr__(self):
        return f"<Demo(id={self.id}, title='{self.title}', status='{self.status}', company_id={self.company_id})>"


class OutreachCampaign(Base):
    """
    Outreach campaigns for business development
    """
    __tablename__ = "outreach_campaigns"

    id = Column(Integer, primary_key=True, index=True)
    
    # Campaign details
    name = Column(String(200), nullable=False)
    description = Column(Text)
    campaign_type = Column(String(100))  # cold_email, linkedin, phone, etc.
    
    # Campaign configuration
    message_template = Column(Text)
    subject_template = Column(String(300))
    personalization_variables = Column(JSON)  # List of variables to personalize
    
    # Campaign status
    status = Column(String(50), default="draft")  # draft, active, paused, completed
    
    # Campaign metrics
    total_contacts = Column(Integer, default=0)
    sent_count = Column(Integer, default=0)
    delivered_count = Column(Integer, default=0)
    opened_count = Column(Integer, default=0)
    clicked_count = Column(Integer, default=0)
    replied_count = Column(Integer, default=0)
    meeting_count = Column(Integer, default=0)
    
    # Calculated rates
    open_rate = Column(Float)
    click_rate = Column(Float)
    response_rate = Column(Float)
    meeting_rate = Column(Float)
    
    # Campaign timing
    start_date = Column(DateTime(timezone=True))
    end_date = Column(DateTime(timezone=True))
    
    # Relationships
    contacts = relationship("OutreachContact", back_populates="campaign", cascade="all, delete-orphan")
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<OutreachCampaign(id={self.id}, name='{self.name}', status='{self.status}', response_rate={self.response_rate})>"


class OutreachContact(Base):
    """
    Individual contacts within outreach campaigns
    """
    __tablename__ = "outreach_contacts"

    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey("outreach_campaigns.id"), nullable=False)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    
    # Contact information
    name = Column(String(200), nullable=False)
    title = Column(String(200))
    email = Column(String(200), nullable=False)
    phone = Column(String(50))
    linkedin_url = Column(String(500))
    
    # Contact status
    status = Column(String(50), default="pending")  # pending, sent, delivered, opened, clicked, replied, meeting_scheduled
    
    # Communication tracking
    message_sent = Column(Text)  # Actual message sent (personalized)
    send_date = Column(DateTime(timezone=True))
    opened_date = Column(DateTime(timezone=True))
    replied_date = Column(DateTime(timezone=True))
    last_contact_date = Column(DateTime(timezone=True))
    
    # Follow-up tracking
    follow_up_count = Column(Integer, default=0)
    next_followup_date = Column(DateTime(timezone=True))
    
    # Response tracking
    response_content = Column(Text)
    response_sentiment = Column(String(50))  # positive, neutral, negative
    meeting_scheduled = Column(Boolean, default=False)
    meeting_date = Column(DateTime(timezone=True))
    
    # Personalization data
    personalization_data = Column(JSON)  # Company-specific data used for personalization
    
    # Relationships
    campaign = relationship("OutreachCampaign", back_populates="contacts")
    company = relationship("Company", back_populates="outreach_contacts")
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<OutreachContact(id={self.id}, name='{self.name}', status='{self.status}', company_id={self.company_id})>"


class BusinessMetric(Base):
    """
    Business intelligence metrics and KPIs
    """
    __tablename__ = "business_metrics"

    id = Column(Integer, primary_key=True, index=True)
    
    # Metric information
    metric_name = Column(String(100), nullable=False, index=True)
    metric_category = Column(String(50))  # sales, marketing, operations, etc.
    metric_value = Column(Float, nullable=False)
    metric_unit = Column(String(20))  # dollars, percentage, count, etc.
    
    # Context
    period_start = Column(DateTime(timezone=True))
    period_end = Column(DateTime(timezone=True))
    region = Column(String(100))
    segment = Column(String(100))
    
    # Metadata
    calculation_method = Column(Text)
    data_source = Column(String(200))
    confidence_level = Column(Float)
    
    # Timestamp
    recorded_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    def __repr__(self):
        return f"<BusinessMetric(id={self.id}, metric_name='{self.metric_name}', value={self.metric_value}, recorded_at='{self.recorded_at}')>"
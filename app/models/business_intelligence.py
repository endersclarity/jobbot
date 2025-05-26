"""
Business Intelligence Database Models for Company Discovery and Opportunity Tracking

Transforms JobBot from job search to business opportunity identification.
Core models for discovering companies, analyzing tech stacks, identifying decision makers,
and tracking business opportunities for automated client acquisition.
"""

from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Company(Base):
    """
    Core company profiles discovered through business intelligence scraping
    """
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    
    # Basic company information
    name = Column(String(200), nullable=False, index=True)
    domain = Column(String(500), unique=True, index=True)
    website_url = Column(String(500))
    
    # Business classification
    industry = Column(String(100), index=True)
    business_type = Column(String(50))  # agency, saas, ecommerce, service, etc.
    size_estimate = Column(String(50))  # 1-10, 11-50, 51-200, 201-500, 500+
    
    # Location data
    address = Column(String(500))
    city = Column(String(100), index=True)
    state = Column(String(50), index=True)
    country = Column(String(50), default="US")
    zip_code = Column(String(20))
    
    # Contact information
    phone = Column(String(50))
    email = Column(String(200))
    
    # Digital footprint
    linkedin_url = Column(String(500))
    github_org = Column(String(200))
    facebook_url = Column(String(500))
    twitter_handle = Column(String(100))
    instagram_handle = Column(String(100))
    social_media = Column(JSON)  # Additional social platforms
    
    # Business intelligence metadata
    discovery_source = Column(String(100), index=True)  # google_business, yellow_pages, etc.
    last_scraped = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    scrape_frequency_days = Column(Integer, default=7)
    next_scrape_date = Column(DateTime(timezone=True))
    
    # Company health indicators
    website_status = Column(String(50), default="unknown")  # active, inactive, broken, redirected
    business_status = Column(String(50), default="active", index=True)  # active, closed, acquired, moved
    opportunity_score = Column(Float, default=0.0, index=True)  # Composite opportunity rating
    priority_level = Column(String(20), default="medium", index=True)  # low, medium, high, urgent
    
    # Engagement tracking
    contact_attempts = Column(Integer, default=0)
    last_contact_date = Column(DateTime(timezone=True))
    response_rate = Column(Float, default=0.0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    tech_stack = relationship("CompanyTechStack", back_populates="company", cascade="all, delete-orphan")
    decision_makers = relationship("DecisionMaker", back_populates="company", cascade="all, delete-orphan")
    opportunities = relationship("BusinessOpportunity", back_populates="company", cascade="all, delete-orphan")
    outreach_records = relationship("OutreachRecord", back_populates="company", cascade="all, delete-orphan")
    website_audits = relationship("WebsiteAudit", back_populates="company", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Company(id={self.id}, name='{self.name}', domain='{self.domain}', opportunity_score={self.opportunity_score})>"


class CompanyTechStack(Base):
    """
    Technology stack analysis for each company's digital infrastructure
    """
    __tablename__ = "company_tech_stacks"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    
    # Technology identification
    tech_name = Column(String(100), nullable=False, index=True)
    tech_category = Column(String(50), index=True)  # cms, hosting, analytics, framework, library
    tech_version = Column(String(50))
    tech_description = Column(Text)
    
    # Detection metadata
    detection_method = Column(String(100))  # wappalyzer, manual, api, headers
    confidence_score = Column(Float, default=0.0)  # 0.0-1.0 confidence in detection
    detection_date = Column(DateTime(timezone=True), server_default=func.now())
    
    # Analysis results
    is_outdated = Column(Boolean, default=False, index=True)
    is_vulnerable = Column(Boolean, default=False, index=True)
    current_version = Column(String(50))  # Latest available version
    upgrade_available = Column(Boolean, default=False)
    
    # Opportunity assessment
    upgrade_priority = Column(String(20), default="low")  # low, medium, high, critical
    estimated_effort_hours = Column(Integer)  # Time to fix/upgrade
    business_impact = Column(String(20), default="low")  # low, medium, high
    upgrade_notes = Column(Text)  # Specific recommendations
    
    # Relationships
    company = relationship("Company", back_populates="tech_stack")
    
    def __repr__(self):
        return f"<CompanyTechStack(id={self.id}, company_id={self.company_id}, tech_name='{self.tech_name}', outdated={self.is_outdated})>"


class DecisionMaker(Base):
    """
    Key personnel and decision makers at target companies
    """
    __tablename__ = "decision_makers"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    
    # Basic information
    name = Column(String(200), nullable=False)
    title = Column(String(200), index=True)
    department = Column(String(100), index=True)  # engineering, marketing, operations, c-suite
    seniority = Column(String(50), index=True)  # junior, senior, lead, manager, director, vp, c-level
    
    # Contact information
    email = Column(String(200))
    phone = Column(String(50))
    linkedin_url = Column(String(500))
    
    # Professional profiles
    github_username = Column(String(100))
    twitter_handle = Column(String(100))
    personal_website = Column(String(500))
    
    # Intelligence analysis
    writing_style_analysis = Column(Text)  # LLM analysis of communication style
    interests = Column(JSON)  # Professional interests, technologies, topics
    pain_points = Column(JSON)  # Identified challenges, complaints, needs
    influence_level = Column(String(20), default="medium")  # low, medium, high
    technical_level = Column(String(20), default="unknown")  # non-technical, technical, expert
    
    # Communication preferences
    preferred_contact_method = Column(String(50), default="email")  # email, linkedin, phone
    best_contact_time = Column(String(50))  # morning, afternoon, evening
    communication_style = Column(String(50))  # formal, casual, technical, business
    
    # Engagement scoring
    contact_priority = Column(Integer, default=5)  # 1-10 priority for outreach
    response_likelihood = Column(Float, default=0.5)  # 0.0-1.0 probability of response
    influence_score = Column(Float, default=0.5)  # 0.0-1.0 decision-making power
    
    # Engagement history
    last_contacted = Column(DateTime(timezone=True))
    total_contacts = Column(Integer, default=0)
    responses_received = Column(Integer, default=0)
    response_rate = Column(Float, default=0.0)
    engagement_score = Column(Float, default=0.0)  # Overall engagement quality
    
    # Status tracking
    relationship_status = Column(String(50), default="prospect")  # prospect, contacted, engaged, client, closed
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    company = relationship("Company", back_populates="decision_makers")
    outreach_records = relationship("OutreachRecord", back_populates="decision_maker", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<DecisionMaker(id={self.id}, name='{self.name}', title='{self.title}', company_id={self.company_id})>"


class BusinessOpportunity(Base):
    """
    Identified business opportunities for automation, improvement, or services
    """
    __tablename__ = "business_opportunities"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    
    # Opportunity classification
    opportunity_type = Column(String(100), nullable=False, index=True)
    # Types: website_rebuild, performance_optimization, security_upgrade, automation,
    #        integration, mobile_app, seo_improvement, hosting_migration, etc.
    
    category = Column(String(50), index=True)  # technical, marketing, operations, security
    
    # Opportunity details
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    problem_statement = Column(Text)  # What's wrong/missing
    proposed_solution = Column(Text)  # How to fix it
    
    # Business impact assessment
    estimated_value = Column(Float)  # Potential client project value ($)
    estimated_savings = Column(Float)  # Potential cost savings for client ($)
    effort_estimate_hours = Column(Integer)  # Development time required
    complexity_level = Column(String(20), default="medium")  # low, medium, high, expert
    
    # Opportunity scoring
    urgency_score = Column(Float, default=5.0, index=True)  # 1.0-10.0 how urgent is this
    feasibility_score = Column(Float, default=5.0, index=True)  # 1.0-10.0 how doable
    value_score = Column(Float, default=5.0, index=True)  # 1.0-10.0 business value
    competition_score = Column(Float, default=5.0)  # 1.0-10.0 how competitive (lower = less competition)
    total_score = Column(Float, default=5.0, index=True)  # Weighted composite score
    
    # Evidence and validation
    evidence_data = Column(JSON)  # Screenshots, metrics, proof of problem
    pain_point_source = Column(String(200))  # Where we discovered this (website, job posting, etc.)
    validation_status = Column(String(50), default="identified")  # identified, researched, validated, demo_built
    
    # Demo and proof-of-concept
    demo_url = Column(String(500))  # Link to working demo
    demo_description = Column(Text)  # What the demo shows
    demo_screenshots = Column(JSON)  # Before/after images
    poc_completion_date = Column(DateTime(timezone=True))
    
    # Opportunity lifecycle
    status = Column(String(50), default="identified", index=True)
    # Statuses: identified, researched, validated, demo_built, pitched, negotiating, won, lost, on_hold
    
    discovery_date = Column(DateTime(timezone=True), server_default=func.now())
    last_updated = Column(DateTime(timezone=True), onupdate=func.now())
    target_pitch_date = Column(DateTime(timezone=True))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    company = relationship("Company", back_populates="opportunities")
    outreach_records = relationship("OutreachRecord", back_populates="opportunity", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<BusinessOpportunity(id={self.id}, title='{self.title}', type='{self.opportunity_type}', score={self.total_score})>"


class OutreachRecord(Base):
    """
    Track all outreach attempts, responses, and communication history
    """
    __tablename__ = "outreach_records"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    decision_maker_id = Column(Integer, ForeignKey("decision_makers.id"), index=True)  # Optional
    opportunity_id = Column(Integer, ForeignKey("business_opportunities.id"), index=True)  # Optional
    
    # Outreach details
    outreach_type = Column(String(50), nullable=False, index=True)  # email, linkedin, phone, github_pr, demo
    subject_line = Column(String(500))
    message_content = Column(Text)
    
    # Personalization data
    personalization_level = Column(String(20), default="low")  # low, medium, high, custom
    personalization_notes = Column(Text)  # What made this message personal
    demo_included = Column(Boolean, default=False)
    attachment_count = Column(Integer, default=0)
    
    # Delivery tracking
    sent_date = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    delivery_status = Column(String(50), default="sent")  # sent, delivered, opened, clicked, bounced, failed
    
    # Response tracking
    response_received = Column(Boolean, default=False, index=True)
    response_date = Column(DateTime(timezone=True))
    response_content = Column(Text)
    response_sentiment = Column(String(20))  # positive, neutral, negative, interested, not_interested
    
    # Follow-up planning
    requires_followup = Column(Boolean, default=True)
    followup_date = Column(DateTime(timezone=True))
    followup_notes = Column(Text)
    
    # Campaign tracking
    campaign_name = Column(String(200))  # For grouping related outreach
    sequence_number = Column(Integer, default=1)  # Position in sequence (1st email, 2nd follow-up, etc.)
    
    # Success metrics
    led_to_meeting = Column(Boolean, default=False)
    led_to_project = Column(Boolean, default=False)
    project_value = Column(Float)  # If it led to paid work
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    company = relationship("Company", back_populates="outreach_records")
    decision_maker = relationship("DecisionMaker", back_populates="outreach_records")
    opportunity = relationship("BusinessOpportunity", back_populates="outreach_records")
    
    def __repr__(self):
        return f"<OutreachRecord(id={self.id}, type='{self.outreach_type}', company_id={self.company_id}, response={self.response_received})>"


class WebsiteAudit(Base):
    """
    Technical website audits and performance analysis
    """
    __tablename__ = "website_audits"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    
    # Audit metadata
    audit_date = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    audit_type = Column(String(50), default="full")  # full, performance, security, seo, mobile
    audit_tool = Column(String(100))  # lighthouse, pagespeed, manual, etc.
    
    # Performance metrics
    page_load_time = Column(Float)  # Seconds
    first_contentful_paint = Column(Float)  # Seconds
    largest_contentful_paint = Column(Float)  # Seconds
    cumulative_layout_shift = Column(Float)
    time_to_interactive = Column(Float)  # Seconds
    
    # Lighthouse scores (0-100)
    performance_score = Column(Integer)
    accessibility_score = Column(Integer)
    best_practices_score = Column(Integer)
    seo_score = Column(Integer)
    
    # Technical analysis
    mobile_friendly = Column(Boolean)
    ssl_enabled = Column(Boolean)
    ssl_grade = Column(String(10))  # A+, A, B, C, D, F
    compression_enabled = Column(Boolean)
    caching_enabled = Column(Boolean)
    
    # Content analysis
    page_size_bytes = Column(Integer)
    image_optimization_score = Column(Float)  # 0.0-1.0
    meta_description_present = Column(Boolean)
    title_tag_optimized = Column(Boolean)
    
    # Security analysis
    security_headers = Column(JSON)  # Content-Security-Policy, etc.
    security_issues = Column(JSON)  # Array of discovered security problems
    vulnerability_count = Column(Integer, default=0)
    
    # Opportunity identification
    improvement_opportunities = Column(JSON)  # Array of specific improvements
    estimated_improvement_impact = Column(Float)  # Expected performance gain
    priority_fixes = Column(JSON)  # High-priority issues to address first
    
    # Competitive analysis
    industry_benchmark_score = Column(Float)  # How it compares to industry average
    improvement_potential_score = Column(Float)  # How much it could improve
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    company = relationship("Company", back_populates="website_audits")
    
    def __repr__(self):
        return f"<WebsiteAudit(id={self.id}, company_id={self.company_id}, performance_score={self.performance_score}, audit_date='{self.audit_date}')>"
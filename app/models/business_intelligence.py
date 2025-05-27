"""
Business Intelligence Database Models

Advanced business automation and opportunity tracking models for:
- Company discovery and analysis  
- Automation opportunity scoring
- Demo generation and proof-of-concepts
- Outreach campaign management
- Decision maker intelligence
- Technology stack analysis
"""

from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Company(Base):
    """
    Companies discovered through automated research and business intelligence
    """
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    
    # Basic company information
    name = Column(String(200), nullable=False, index=True)
    domain = Column(String(500), unique=True, index=True)
    website = Column(String(500))
    website_url = Column(String(500))
    description = Column(Text)
    
    # Location and contact info
    location = Column(String(200))
    address = Column(String(500))
    city = Column(String(100), index=True)
    state = Column(String(50), index=True)
    country = Column(String(50), default="US")
    zip_code = Column(String(20))
    phone = Column(String(50))
    email = Column(String(200))
    
    # Business classification
    industry = Column(String(100), index=True)
    business_type = Column(String(50))  # agency, saas, ecommerce, service, etc.
    size_estimate = Column(String(50))  # 1-10, 11-50, 51-200, 201-500, 500+
    employee_count = Column(Integer)
    revenue_range = Column(String(50))
    founding_year = Column(Integer)
    
    # Digital footprint
    linkedin_url = Column(String(500))
    github_org = Column(String(200))
    facebook_url = Column(String(500))
    twitter_handle = Column(String(100))
    instagram_handle = Column(String(100))
    social_media = Column(JSON)  # Additional social platforms
    
    # Technology analysis
    tech_stack = Column(JSON)  # List of detected technologies
    automation_readiness_score = Column(Float)  # 0-100 score
    digital_maturity_level = Column(String(20))  # basic, intermediate, advanced
    
    # Business opportunity analysis
    opportunity_score = Column(Float, default=0.0, index=True)  # Composite opportunity rating
    automation_opportunities = Column(JSON)  # List of identified opportunities
    pain_points = Column(JSON)  # List of detected business pain points
    priority_level = Column(String(20), default="medium", index=True)  # low, medium, high, urgent
    
    # Business intelligence metadata
    discovery_source = Column(String(100), index=True)  # google_business, yellow_pages, etc.
    discovery_date = Column(DateTime(timezone=True), server_default=func.now())
    last_scraped = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    last_analyzed = Column(DateTime(timezone=True))
    scrape_frequency_days = Column(Integer, default=7)
    next_scrape_date = Column(DateTime(timezone=True))
    analysis_status = Column(String(50), default="pending")  # pending, analyzed, contacted
    
    # Company health indicators
    website_status = Column(String(50), default="unknown")  # active, inactive, broken, redirected
    business_status = Column(String(50), default="active", index=True)  # active, closed, acquired, moved
    
    # Engagement tracking
    contact_attempts = Column(Integer, default=0)
    last_contact_date = Column(DateTime(timezone=True))
    response_rate = Column(Float, default=0.0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships - BIE Core Models
    tech_stack_analysis = relationship("CompanyTechStack", back_populates="company", cascade="all, delete-orphan")
    decision_makers = relationship("DecisionMaker", back_populates="company", cascade="all, delete-orphan")
    business_opportunities = relationship("BusinessOpportunity", back_populates="company", cascade="all, delete-orphan")
    outreach_records = relationship("OutreachRecord", back_populates="company", cascade="all, delete-orphan")
    website_audits = relationship("WebsiteAudit", back_populates="company", cascade="all, delete-orphan")
    
    # Relationships - Phase 8 Models
    opportunities = relationship("Opportunity", back_populates="company", cascade="all, delete-orphan")
    demos = relationship("Demo", back_populates="company", cascade="all, delete-orphan")
    outreach_contacts = relationship("OutreachContact", back_populates="company", cascade="all, delete-orphan")
    lead_scores = relationship("LeadScore", back_populates="company", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Company(id={self.id}, name='{self.name}', industry='{self.industry}', score={self.opportunity_score})>"


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
    company = relationship("Company", back_populates="tech_stack_analysis")
    
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
    company = relationship("Company", back_populates="business_opportunities")
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


# Phase 8 Analytics Integration Models

class Opportunity(Base):
    """
    Business opportunities identified for each company (Phase 8 Analytics Integration)
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
"""
Monitoring and Metrics Database Models for Phase 5B

Real-time monitoring dashboard database schema for tracking:
- Scraping session metrics and performance
- Site-specific execution data  
- System health and resource usage
- Business intelligence and analytics
"""

from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class ScrapeSession(Base):
    """
    Track individual multi-site scraping sessions
    """
    __tablename__ = "scrape_sessions"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), unique=True, index=True, nullable=False)
    
    # Session configuration
    search_term = Column(String(200), nullable=False)
    location = Column(String(200))
    sites_requested = Column(JSON)  # List of site names requested
    max_jobs_per_site = Column(Integer, default=50)
    max_concurrency = Column(Integer, default=3)
    
    # Session timing
    start_time = Column(DateTime(timezone=True), server_default=func.now())
    end_time = Column(DateTime(timezone=True))
    duration_seconds = Column(Float)
    
    # Session results
    status = Column(String(50), default="running")  # running, completed, failed, timeout
    total_jobs_found = Column(Integer, default=0)
    successful_sites = Column(Integer, default=0)
    failed_sites = Column(Integer, default=0)
    
    # Performance metrics
    jobs_per_second = Column(Float)
    average_response_time = Column(Float)
    error_rate = Column(Float)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    site_executions = relationship("SiteExecution", back_populates="session", cascade="all, delete-orphan")
    session_metrics = relationship("SessionMetric", back_populates="session", cascade="all, delete-orphan")


class SiteExecution(Base):
    """
    Track per-site execution within a scraping session
    """
    __tablename__ = "site_executions"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), ForeignKey("scrape_sessions.session_id"), nullable=False)
    
    # Site information
    site_name = Column(String(50), nullable=False)  # indeed, linkedin, glassdoor
    site_url = Column(String(500))
    
    # Execution timing
    start_time = Column(DateTime(timezone=True), server_default=func.now())
    end_time = Column(DateTime(timezone=True))
    duration_seconds = Column(Float)
    
    # Execution results
    status = Column(String(50), default="running")  # running, completed, failed, timeout, circuit_open
    jobs_extracted = Column(Integer, default=0)
    pages_scraped = Column(Integer, default=0)
    requests_made = Column(Integer, default=0)
    
    # Performance metrics
    average_response_time = Column(Float)
    success_rate = Column(Float)
    circuit_breaker_state = Column(String(20))  # closed, open, half_open
    
    # Error tracking
    error_count = Column(Integer, default=0)
    last_error_message = Column(Text)
    retry_attempts = Column(Integer, default=0)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    session = relationship("ScrapeSession", back_populates="site_executions")


class SessionMetric(Base):
    """
    Time-series metrics for real-time monitoring
    """
    __tablename__ = "session_metrics"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), ForeignKey("scrape_sessions.session_id"), nullable=False)
    
    # Metric information
    metric_name = Column(String(100), nullable=False)  # jobs_per_minute, cpu_usage, memory_usage, etc.
    metric_value = Column(Float, nullable=False)
    metric_unit = Column(String(20))  # jobs, percent, mb, seconds
    
    # Timing
    timestamp = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        index=True,            # speeds up range queries
    )
    
    # Context
    site_name = Column(String(50))  # Optional: metric specific to a site
    additional_data = Column(JSON)  # Optional: extra metric context
    
    # Relationships
    session = relationship("ScrapeSession", back_populates="session_metrics")


class SystemHealth(Base):
    """
    Track overall system health and resource usage
    """
    __tablename__ = "system_health"

    id = Column(Integer, primary_key=True, index=True)
    
    # System metrics
    cpu_usage_percent = Column(Float)
    memory_usage_percent = Column(Float)
    memory_usage_mb = Column(Float)
    disk_usage_percent = Column(Float)
    
    # Application metrics
    active_sessions = Column(Integer, default=0)
    total_jobs_today = Column(Integer, default=0)
    average_session_duration = Column(Float)
    
    # Network metrics
    network_requests_per_minute = Column(Float)
    average_response_time = Column(Float)
    error_rate_percent = Column(Float)
    
    # Business metrics
    cost_savings_today = Column(Float)  # Calculated savings vs competitors
    jobs_per_hour = Column(Float)
    sites_operational = Column(Integer)
    
    # Status flags
    all_systems_operational = Column(Boolean, default=True)
    alerts_active = Column(Integer, default=0)
    
    # Timing
    timestamp = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        index=True,            # speeds up range queries
    )
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class AlertRule(Base):
    """
    Configurable alert rules for proactive monitoring
    """
    __tablename__ = "alert_rules"

    id = Column(Integer, primary_key=True, index=True)
    
    # Rule definition
    rule_name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    metric_name = Column(String(100), nullable=False)
    
    # Threshold configuration
    threshold_operator = Column(String(10), nullable=False)  # >, <, >=, <=, ==
    threshold_value = Column(Float, nullable=False)
    threshold_duration_seconds = Column(Integer, default=60)  # How long condition must persist
    
    # Alert configuration
    severity = Column(String(20), default="warning")  # info, warning, error, critical
    enabled = Column(Boolean, default=True)
    
    # Notification settings
    notification_channels = Column(JSON)  # List of notification methods
    cooldown_seconds = Column(Integer, default=300)  # Minimum time between alerts
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_triggered = Column(DateTime(timezone=True))


class AlertInstance(Base):
    """
    Track individual alert occurrences
    """
    __tablename__ = "alert_instances"

    id = Column(Integer, primary_key=True, index=True)
    rule_id = Column(Integer, ForeignKey("alert_rules.id"), nullable=False)
    
    # Alert details
    alert_message = Column(Text, nullable=False)
    metric_value = Column(Float, nullable=False)
    threshold_value = Column(Float, nullable=False)
    severity = Column(String(20), nullable=False)
    
    # Status tracking
    status = Column(String(20), default="active")  # active, acknowledged, resolved
    acknowledged_at = Column(DateTime(timezone=True))
    resolved_at = Column(DateTime(timezone=True))
    
    # Context
    session_id = Column(String(100))  # Optional: related session
    site_name = Column(String(50))    # Optional: related site
    additional_context = Column(JSON)
    
    # Timing
    triggered_at = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    rule = relationship("AlertRule")
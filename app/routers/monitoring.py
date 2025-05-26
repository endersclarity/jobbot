"""
Monitoring API Router for Phase 5B Real-time Dashboard

Provides endpoints for:
- Real-time session monitoring
- Historical performance analytics  
- System health tracking
- Alert management
- WebSocket real-time updates
"""

from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, func as sql_func
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import json
import asyncio
import psutil
import uuid
import threading

from app.core.database import get_db
from app.models.monitoring import (
    ScrapeSession, SiteExecution, SessionMetric, SystemHealth, AlertRule, AlertInstance
)
from pydantic import BaseModel, Field


# Pydantic models for API responses
class ScrapeSessionResponse(BaseModel):
    id: int
    session_id: str
    search_term: str
    location: Optional[str]
    sites_requested: List[str]
    status: str
    start_time: datetime
    end_time: Optional[datetime]
    duration_seconds: Optional[float]
    total_jobs_found: int
    successful_sites: int
    failed_sites: int
    jobs_per_second: Optional[float]
    
    class Config:
        from_attributes = True


class SiteExecutionResponse(BaseModel):
    id: int
    site_name: str
    status: str
    start_time: datetime
    end_time: Optional[datetime]
    duration_seconds: Optional[float]
    jobs_extracted: int
    pages_scraped: int
    requests_made: int
    success_rate: Optional[float]
    circuit_breaker_state: Optional[str]
    error_count: int
    last_error_message: Optional[str]
    
    class Config:
        from_attributes = True


class SystemHealthResponse(BaseModel):
    id: int
    cpu_usage_percent: Optional[float]
    memory_usage_percent: Optional[float]
    memory_usage_mb: Optional[float]
    active_sessions: int
    total_jobs_today: int
    jobs_per_hour: Optional[float]
    sites_operational: int
    all_systems_operational: bool
    alerts_active: int
    timestamp: datetime
    cost_savings_today: Optional[float]
    
    class Config:
        from_attributes = True


class SessionMetricResponse(BaseModel):
    id: int
    session_id: str
    metric_name: str
    metric_value: float
    metric_unit: Optional[str]
    timestamp: datetime
    site_name: Optional[str]
    
    class Config:
        from_attributes = True


class AlertRuleCreate(BaseModel):
    rule_name: str
    description: Optional[str]
    metric_name: str
    threshold_operator: str = Field(..., pattern="^(>|<|>=|<=|==)$")
    threshold_value: float
    threshold_duration_seconds: int = 60
    severity: str = Field(default="warning", pattern="^(info|warning|error|critical)$")
    enabled: bool = True
    notification_channels: List[str] = Field(default_factory=list)
    cooldown_seconds: int = 300


class WebSocketManager:
    """Manage WebSocket connections for real-time updates"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self._lock = threading.Lock()
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        with self._lock:
            self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        with self._lock:
            if websocket in self.active_connections:
                self.active_connections.remove(websocket)
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        try:
            await websocket.send_text(message)
        except (WebSocketDisconnect, ConnectionResetError, RuntimeError) as e:
            print(f"WebSocket send failed: {e}")
            self.disconnect(websocket)
    
    async def broadcast(self, message: str):
        disconnected = []
        # Create a copy of connections to avoid modification during iteration
        with self._lock:
            connections_copy = self.active_connections.copy()
        
        for connection in connections_copy:
            try:
                await connection.send_text(message)
            except (WebSocketDisconnect, ConnectionResetError, RuntimeError) as e:
                print(f"WebSocket broadcast failed: {e}")
                disconnected.append(connection)
        
        # Clean up disconnected clients
        for connection in disconnected:
            self.disconnect(connection)


# Global WebSocket manager
ws_manager = WebSocketManager()

router = APIRouter(prefix="/api/v1/monitoring", tags=["monitoring"])


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time monitoring updates"""
    await ws_manager.connect(websocket)
    try:
        while True:
            # Keep connection alive and send periodic updates
            await asyncio.sleep(1)
            
            # Send real-time system metrics every 5 seconds
            if len(ws_manager.active_connections) > 0:
                system_metrics = await get_real_time_system_metrics()
                await ws_manager.broadcast(json.dumps({
                    "type": "system_metrics",
                    "data": system_metrics,
                    "timestamp": datetime.now().isoformat()
                }))
                await asyncio.sleep(5)
                
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)


async def get_real_time_system_metrics() -> Dict[str, Any]:
    """Get current system metrics for real-time monitoring"""
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        return {
            "cpu_usage_percent": cpu_percent,
            "memory_usage_percent": memory.percent,
            "memory_usage_mb": memory.used / (1024 * 1024),
            "disk_usage_percent": disk.percent,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {"error": str(e), "timestamp": datetime.now().isoformat()}


@router.get("/sessions", response_model=List[ScrapeSessionResponse])
async def get_scrape_sessions(
    limit: int = Query(default=50, le=500),
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get list of scraping sessions with optional filtering"""
    query = db.query(ScrapeSession)
    
    if status:
        query = query.filter(ScrapeSession.status == status)
    
    sessions = query.order_by(desc(ScrapeSession.start_time)).limit(limit).all()
    return sessions


@router.get("/sessions/{session_id}", response_model=ScrapeSessionResponse)
async def get_scrape_session(session_id: str, db: Session = Depends(get_db)):
    """Get specific scraping session details"""
    session = db.query(ScrapeSession).filter(ScrapeSession.session_id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


@router.get("/sessions/{session_id}/sites", response_model=List[SiteExecutionResponse])
async def get_session_sites(session_id: str, db: Session = Depends(get_db)):
    """Get site execution details for a specific session"""
    sites = db.query(SiteExecution).filter(SiteExecution.session_id == session_id).all()
    return sites


@router.get("/sessions/{session_id}/metrics", response_model=List[SessionMetricResponse])
async def get_session_metrics(
    session_id: str,
    metric_name: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get time-series metrics for a specific session"""
    query = db.query(SessionMetric).filter(SessionMetric.session_id == session_id)
    
    if metric_name:
        query = query.filter(SessionMetric.metric_name == metric_name)
    
    metrics = query.order_by(SessionMetric.timestamp).all()
    return metrics


@router.get("/health", response_model=SystemHealthResponse)
async def get_current_system_health(db: Session = Depends(get_db)):
    """Get current system health status"""
    # Get latest health record
    health = db.query(SystemHealth).order_by(desc(SystemHealth.timestamp)).first()
    
    if not health:
        # Create initial health record if none exists
        real_time_metrics = await get_real_time_system_metrics()
        health = SystemHealth(
            cpu_usage_percent=real_time_metrics.get("cpu_usage_percent"),
            memory_usage_percent=real_time_metrics.get("memory_usage_percent"),
            memory_usage_mb=real_time_metrics.get("memory_usage_mb"),
            active_sessions=0,
            total_jobs_today=0,
            sites_operational=3,  # indeed, linkedin, glassdoor
            all_systems_operational=True,
            alerts_active=0
        )
        db.add(health)
        db.commit()
        db.refresh(health)
    
    return health


@router.get("/health/history")
async def get_system_health_history(
    hours: int = Query(default=24, le=168),  # Max 1 week
    db: Session = Depends(get_db)
):
    """Get historical system health data"""
    since = datetime.now() - timedelta(hours=hours)
    
    health_records = db.query(SystemHealth).filter(
        SystemHealth.timestamp >= since
    ).order_by(SystemHealth.timestamp).all()
    
    return [
        {
            "timestamp": record.timestamp.isoformat(),
            "cpu_usage_percent": record.cpu_usage_percent,
            "memory_usage_percent": record.memory_usage_percent,
            "active_sessions": record.active_sessions,
            "jobs_per_hour": record.jobs_per_hour,
            "all_systems_operational": record.all_systems_operational
        }
        for record in health_records
    ]


@router.get("/analytics/dashboard")
async def get_dashboard_analytics(db: Session = Depends(get_db)):
    """Get comprehensive dashboard analytics"""
    now = datetime.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Today's session statistics (optimized with index on start_time)
    today_sessions = db.query(ScrapeSession).filter(
        ScrapeSession.start_time >= today_start
    ).options().all()
    
    # Calculate statistics
    total_sessions_today = len(today_sessions)
    completed_sessions = [s for s in today_sessions if s.status == "completed"]
    total_jobs_today = sum(s.total_jobs_found or 0 for s in today_sessions)
    
    # Average performance metrics
    avg_duration = None
    avg_jobs_per_second = None
    if completed_sessions:
        avg_duration = sum(s.duration_seconds or 0 for s in completed_sessions) / len(completed_sessions)
        avg_jobs_per_second = sum(s.jobs_per_second or 0 for s in completed_sessions) / len(completed_sessions)
    
    # Site performance (optimized with aggregation)
    site_stats_query = db.query(
        SiteExecution.site_name,
        sql_func.count(SiteExecution.id).label('total'),
        sql_func.sum(sql_func.case([(SiteExecution.status == 'completed', 1)], else_=0)).label('successful'),
        sql_func.sum(sql_func.coalesce(SiteExecution.jobs_extracted, 0)).label('jobs')
    ).join(ScrapeSession, SiteExecution.session_id == ScrapeSession.session_id)\
     .filter(ScrapeSession.start_time >= today_start)\
     .group_by(SiteExecution.site_name).all()
    
    site_stats = {
        row.site_name: {
            "total": row.total,
            "successful": row.successful or 0,
            "jobs": row.jobs or 0
        }
        for row in site_stats_query
    }
    
    # Calculate cost savings (vs Apify pricing)
    apify_cost_per_1k_jobs = 50  # Conservative estimate
    cost_savings_today = (total_jobs_today / 1000) * apify_cost_per_1k_jobs
    
    return {
        "overview": {
            "total_sessions_today": total_sessions_today,
            "completed_sessions_today": len(completed_sessions),
            "total_jobs_scraped_today": total_jobs_today,
            "average_session_duration": avg_duration,
            "average_jobs_per_second": avg_jobs_per_second,
            "cost_savings_today": cost_savings_today
        },
        "site_performance": site_stats,
        "last_updated": now.isoformat()
    }


@router.post("/alerts/rules", response_model=dict)
async def create_alert_rule(rule: AlertRuleCreate, db: Session = Depends(get_db)):
    """Create a new alert rule"""
    # Check if rule name already exists
    existing = db.query(AlertRule).filter(AlertRule.rule_name == rule.rule_name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Alert rule with this name already exists")
    
    db_rule = AlertRule(**rule.dict())
    db.add(db_rule)
    db.commit()
    db.refresh(db_rule)
    
    return {"message": "Alert rule created successfully", "rule_id": db_rule.id}


@router.get("/alerts/rules")
async def get_alert_rules(db: Session = Depends(get_db)):
    """Get all alert rules"""
    rules = db.query(AlertRule).order_by(AlertRule.rule_name).all()
    return rules


@router.get("/alerts/active")
async def get_active_alerts(db: Session = Depends(get_db)):
    """Get currently active alerts"""
    active_alerts = db.query(AlertInstance).filter(
        AlertInstance.status == "active"
    ).order_by(desc(AlertInstance.triggered_at)).all()
    
    return active_alerts


@router.post("/sessions", response_model=dict)
async def create_scrape_session(
    search_term: str,
    location: Optional[str] = None,
    sites: Optional[List[str]] = None,
    max_jobs_per_site: int = 50,
    max_concurrency: int = 3,
    db: Session = Depends(get_db)
):
    """Create a new scraping session for monitoring"""
    # Input validation
    if not search_term or len(search_term.strip()) == 0:
        raise HTTPException(status_code=400, detail="Search term cannot be empty")
    
    if max_jobs_per_site < 1 or max_jobs_per_site > 1000:
        raise HTTPException(status_code=400, detail="Max jobs per site must be between 1 and 1000")
    
    if max_concurrency < 1 or max_concurrency > 10:
        raise HTTPException(status_code=400, detail="Max concurrency must be between 1 and 10")
    session_id = str(uuid.uuid4())
    
    # Handle mutable default parameter
    if sites is None:
        sites = ["indeed", "linkedin", "glassdoor"]
    
    session = ScrapeSession(
        session_id=session_id,
        search_term=search_term,
        location=location,
        sites_requested=sites,
        max_jobs_per_site=max_jobs_per_site,
        max_concurrency=max_concurrency,
        status="created"
    )
    
    db.add(session)
    db.commit()
    db.refresh(session)
    
    # Broadcast session creation to WebSocket clients
    await ws_manager.broadcast(json.dumps({
        "type": "session_created",
        "data": {
            "session_id": session_id,
            "search_term": search_term,
            "sites": sites
        },
        "timestamp": datetime.now().isoformat()
    }))
    
    return {"message": "Session created", "session_id": session_id}


@router.post("/sessions/{session_id}/metrics")
async def record_session_metric(
    session_id: str,
    metric_name: str,
    metric_value: float,
    metric_unit: Optional[str] = None,
    site_name: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Record a metric for a scraping session"""
    # Input validation
    if not session_id or len(session_id.strip()) == 0:
        raise HTTPException(status_code=400, detail="Session ID cannot be empty")
    
    if not metric_name or len(metric_name.strip()) == 0:
        raise HTTPException(status_code=400, detail="Metric name cannot be empty")
    
    if metric_value < 0:
        raise HTTPException(status_code=400, detail="Metric value cannot be negative")
    
    # Verify session exists
    session = db.query(ScrapeSession).filter(ScrapeSession.session_id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    metric = SessionMetric(
        session_id=session_id,
        metric_name=metric_name,
        metric_value=metric_value,
        metric_unit=metric_unit,
        site_name=site_name
    )
    
    db.add(metric)
    db.commit()
    
    # Broadcast metric update to WebSocket clients
    await ws_manager.broadcast(json.dumps({
        "type": "metric_update",
        "data": {
            "session_id": session_id,
            "metric_name": metric_name,
            "metric_value": metric_value,
            "site_name": site_name
        },
        "timestamp": datetime.now().isoformat()
    }))
    
    return {"message": "Metric recorded"}
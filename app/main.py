"""
JobBot Main Application Entry Point
"""
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
import uvicorn

from app.core.config import settings
from app.core.database import get_db, engine
from app.models import Base
from app.api.routes.jobs import router as jobs_router
from app.api.routes.business_intelligence import router as business_intelligence_router
from app.api.routes.business import router as business_router
from app.api.v1.analytics import router as analytics_router
from app.routers.scraping import router as scraping_router
from app.routers.monitoring import router as monitoring_router

# Create tables (for development - use Alembic in production)
try:
    Base.metadata.create_all(bind=engine)
    # Verify tables were created
    from sqlalchemy import text, inspect
    inspector = inspect(engine)
    table_names = inspector.get_table_names()
    table_count = len(table_names)
    print(f"✅ Database tables created successfully ({table_count} tables)")
except Exception as e:
    print(f"❌ Table creation failed: {e}")
    # Continue anyway since tables might already exist
    pass

app = FastAPI(
    title="Business Intelligence Engine API",
    description="Complete Business Intelligence Platform with Advanced Analytics and Market Creation",
    version="3.1.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React development server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(jobs_router, prefix=settings.API_V1_STR, tags=["jobs"])
app.include_router(business_intelligence_router, tags=["business-intelligence-core"])
app.include_router(business_router, tags=["business-intelligence"])
app.include_router(analytics_router, prefix=f"{settings.API_V1_STR}/analytics", tags=["advanced-analytics"])
app.include_router(scraping_router, tags=["scraping"])
app.include_router(monitoring_router, tags=["monitoring"])


@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "Business Intelligence Engine API is running", "version": "1.0.0"}


@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """Detailed health check endpoint with database connectivity test"""
    try:
        # Test database connection
        db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"

    return {
        "status": "healthy",
        "service": "business-intelligence-engine",
        "version": "1.0.0",
        "database": db_status,
        "environment": "development" if settings.DEBUG else "production",
    }


@app.get(f"{settings.API_V1_STR}/")
async def api_root():
    """API v1 root endpoint"""
    return {
        "message": "Business Intelligence Engine API v1",
        "docs": f"{settings.API_V1_STR}/docs",
        "endpoints": [
            f"{settings.API_V1_STR}/jobs",
            f"{settings.API_V1_STR}/applications", 
            f"{settings.API_V1_STR}/responses",
            "/api/v1/business-intelligence/companies",
            "/api/v1/business-intelligence/opportunities",
            "/api/v1/business-intelligence/dashboard/analytics",
            "/api/v1/business/companies",
            "/api/v1/business/opportunities",
            "/api/v1/business/demos",
            "/api/v1/business/outreach",
            "/api/v1/business/market-analysis",
            "/api/v1/analytics/advanced-overview",
            "/api/v1/analytics/lead-scoring",
            "/api/v1/analytics/predictive-modeling",
            "/api/v1/analytics/roi-analytics",
            "/api/v1/analytics/competitive-intelligence",
            "/api/v1/scraping/jobs",
            "/api/v1/scraping/status",
            "/api/v1/monitoring/sessions",
            "/api/v1/monitoring/health",
            "/api/v1/monitoring/ws",
        ],
    }


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=settings.DEBUG)

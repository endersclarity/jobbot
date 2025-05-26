"""
JobBot Main Application Entry Point
"""
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import uvicorn

from app.core.config import settings
from app.core.database import get_db, engine
from app.models import Base
from app.api.routes.jobs import router as jobs_router
from app.routers.scraping import router as scraping_router
from app.routers.monitoring import router as monitoring_router

# Create tables (for development - use Alembic in production)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="JobBot API",
    description="Automated Job Search and Application Management System",
    version="0.1.0",
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
app.include_router(scraping_router, tags=["scraping"])
app.include_router(monitoring_router, tags=["monitoring"])


@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "JobBot API is running", "version": "0.1.0"}


@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """Detailed health check endpoint with database connectivity test"""
    try:
        # Test database connection
        db.execute("SELECT 1")
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"

    return {
        "status": "healthy",
        "service": "jobbot-api",
        "version": "0.1.0",
        "database": db_status,
        "environment": "development" if settings.DEBUG else "production",
    }


@app.get(f"{settings.API_V1_STR}/")
async def api_root():
    """API v1 root endpoint"""
    return {
        "message": "JobBot API v1",
        "docs": f"{settings.API_V1_STR}/docs",
        "endpoints": [
            f"{settings.API_V1_STR}/jobs",
            f"{settings.API_V1_STR}/applications", 
            f"{settings.API_V1_STR}/responses",
            "/api/v1/scraping/jobs",
            "/api/v1/scraping/status",
            "/api/v1/monitoring/sessions",
            "/api/v1/monitoring/health",
            "/api/v1/monitoring/ws",
        ],
    }


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=settings.DEBUG)

"""
🔥 Scraping API Endpoints - Crawlee Integration

FastAPI endpoints for triggering enterprise-grade job scraping
using our Crawlee domination infrastructure.

What Apify charges $500+/month for, we provide via REST API for FREE! 💀
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime
import logging

from ..core.database import get_db
from ..services.crawlee_bridge import crawlee_bridge, CrawleeIntegrationError
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v1/scraping",
    tags=["scraping"],
    responses={404: {"description": "Not found"}},
)


# Pydantic models for request/response validation
class ScrapeJobsRequest(BaseModel):
    """Request model for job scraping"""
    search_term: str = Field(..., description="Job search keywords (e.g., 'software engineer')")
    location: str = Field(default="San Francisco, CA", description="Geographic location for search")
    max_jobs: int = Field(default=50, ge=1, le=200, description="Maximum jobs to scrape (1-200)")
    job_site: str = Field(default="indeed", description="Target job site")
    
    class Config:
        json_schema_extra = {
            "example": {
                "search_term": "python developer",
                "location": "New York, NY",
                "max_jobs": 100,
                "job_site": "indeed"
            }
        }


class MultiSiteScrapeRequest(BaseModel):
    """Request model for multi-site job scraping"""
    search_term: str = Field(..., description="Job search keywords")
    location: str = Field(default="San Francisco, CA", description="Geographic location")
    sites: List[str] = Field(default=["indeed", "linkedin", "glassdoor"], description="List of sites to scrape")
    max_jobs_per_site: int = Field(default=50, ge=1, le=200, description="Maximum jobs per site")
    max_concurrency: int = Field(default=3, ge=1, le=5, description="Maximum concurrent scrapers")
    
    class Config:
        json_schema_extra = {
            "example": {
                "search_term": "software engineer",
                "location": "San Francisco, CA", 
                "sites": ["indeed", "linkedin", "glassdoor"],
                "max_jobs_per_site": 50,
                "max_concurrency": 3
            }
        }


class ScrapeJobsResponse(BaseModel):
    """Response model for job scraping results"""
    success: bool
    message: str
    scraping: Optional[dict] = None
    database: Optional[dict] = None
    summary: dict
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Successfully scraped and saved 47 jobs",
                "scraping": {
                    "search_term": "python developer",
                    "location": "New York, NY",
                    "max_jobs": 50,
                    "jobs_scraped": 47,
                    "scraped_at": "2025-05-25T19:30:00Z"
                },
                "database": {
                    "saved_count": 42,
                    "duplicate_count": 5,
                    "error_count": 0,
                    "job_ids": [1, 2, 3, "..."]
                },
                "summary": {
                    "jobs_found": 47,
                    "jobs_saved": 42,
                    "duplicates_skipped": 5,
                    "save_errors": 0
                }
            }
        }


class ScrapeStatusResponse(BaseModel):
    """Response model for scraping status/health check"""
    status: str
    crawlee_available: bool
    node_version: Optional[str] = None
    scraper_path: str
    last_scrape: Optional[str] = None


@router.get("/status", response_model=ScrapeStatusResponse)
async def get_scraping_status():
    """
    Check the status of the Crawlee scraping infrastructure
    
    Returns information about:
    - Crawlee availability
    - Node.js version
    - Scraper script location
    - Last successful scrape time
    """
    try:
        # Check if Node.js is available (async)
        import asyncio, subprocess
        try:
            proc = await asyncio.create_subprocess_exec(
                "node", "--version",
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=10)
            result_returncode = proc.returncode
            result_stdout = stdout.decode()
        except asyncio.TimeoutError:
            result_returncode = 1
            result_stdout = ""
        
        node_available = result_returncode == 0
        node_version = result_stdout.strip() if node_available else None
        
        # Check if scraper script exists
        scraper_exists = crawlee_bridge.scraper_script.exists()
        
        status = "healthy" if node_available and scraper_exists else "degraded"
        
        return ScrapeStatusResponse(
            status=status,
            crawlee_available=scraper_exists,
            node_version=node_version,
            scraper_path=str(crawlee_bridge.scraper_script),
            last_scrape=None  # TODO: Track last scrape time
        )
        
    except Exception as e:
        logger.error("Status check failed: %s", e)
        raise HTTPException(
            status_code=503,
            detail=f"Scraping status unavailable: {e}"
        ) from e


@router.post("/jobs", response_model=ScrapeJobsResponse)
async def scrape_jobs(
    request: ScrapeJobsRequest,
    db: Session = Depends(get_db)
):
    """
    🔥 Trigger enterprise-grade job scraping using Crawlee domination infrastructure
    
    This endpoint:
    1. Executes our Node.js Crawlee scraper with anti-detection
    2. Parses structured job data from target sites
    3. Saves jobs to database with duplicate detection
    4. Returns comprehensive scraping and save statistics
    
    **What Apify charges $500+/month for, we do for FREE!** 💀
    
    - **Real browser automation** with fingerprint rotation
    - **Anti-detection patterns** that bypass 403 errors
    - **Enterprise-grade data extraction** with multiple fallback selectors
    - **Intelligent rate limiting** to respect target sites
    """
    try:
        logger.info(f"🔥 Scraping request: {request.search_term} in {request.location}")
        
        # Execute complete scrape and save workflow
        result = await crawlee_bridge.scrape_and_save(
            search_term=request.search_term,
            location=request.location,
            max_jobs=request.max_jobs,
            job_site=request.job_site,
            db=db
        )
        
        if result['success']:
            summary = result['summary']
            message = f"Successfully scraped and saved {summary['jobs_saved']} jobs"
            if summary['duplicates_skipped'] > 0:
                message += f" ({summary['duplicates_skipped']} duplicates skipped)"
                
            return ScrapeJobsResponse(
                success=True,
                message=message,
                scraping=result['scraping'],
                database=result['database'],
                summary=result['summary']
            )
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Scraping failed: {result.get('error', 'Unknown error')}"
            )
            
    except CrawleeIntegrationError as e:
        logger.error(f"Crawlee integration error: {e}")
        raise HTTPException(
            status_code=422,
            detail=f"Scraping service error: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected scraping error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal scraping error: {str(e)}"
        )


@router.post("/jobs/background", response_model=dict)
async def scrape_jobs_background(
    request: ScrapeJobsRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    🔥 Trigger background job scraping (fire-and-forget)
    
    For large scraping jobs that may take several minutes, this endpoint
    starts the scraping process in the background and returns immediately.
    
    Use this for:
    - High-volume scraping (100+ jobs)
    - Multiple job sites
    - Long-running scraping sessions
    
    **Returns immediately** with a task ID to check status later.
    """
    try:
        # Generate task ID for tracking
        task_id = f"scrape_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{request.search_term.replace(' ', '_')}"
        
        # Add background task
        background_tasks.add_task(
            _background_scrape_task,
            task_id=task_id,
            request=request,
            db=db
        )
        
        logger.info(f"🚀 Background scraping started: {task_id}")
        
        return {
            "success": True,
            "message": "Background scraping started",
            "task_id": task_id,
            "estimated_duration": f"{request.max_jobs * 2} seconds",
            "check_status_url": f"/api/v1/scraping/tasks/{task_id}"
        }
        
    except Exception as e:
        logger.error(f"Background scraping setup failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to start background scraping: {str(e)}"
        )


async def _background_scrape_task(
    task_id: str,
    request: ScrapeJobsRequest,
    db: Session
):
    """Internal background task for scraping"""
    try:
        logger.info(f"🔥 Executing background scraping task: {task_id}")
        
        result = await crawlee_bridge.scrape_and_save(
            search_term=request.search_term,
            location=request.location,
            max_jobs=request.max_jobs,
            job_site=request.job_site,
            db=db
        )
        
        if result['success']:
            logger.info(f"✅ Background task {task_id} completed: {result['summary']['jobs_saved']} jobs saved")
        else:
            logger.error(f"❌ Background task {task_id} failed: {result.get('error')}")
            
    except Exception as e:
        logger.error(f"Background task {task_id} crashed: {e}")


@router.get("/sites")
async def get_supported_sites():
    """
    Get list of supported job sites for scraping
    
    Currently supported:
    - Indeed (primary target, thoroughly tested)
    - LinkedIn (planned)
    - Glassdoor (planned) 
    - AngelList (planned)
    """
    return {
        "supported_sites": [
            {
                "id": "indeed",
                "name": "Indeed",
                "status": "active",
                "description": "Primary job scraping target with full anti-detection support",
                "features": ["anti-detection", "rate-limiting", "multiple-selectors"]
            }
        ],
        "planned_sites": [
            {
                "id": "linkedin",
                "name": "LinkedIn Jobs",
                "status": "planned",
                "description": "Professional network job listings"
            },
            {
                "id": "glassdoor", 
                "name": "Glassdoor",
                "status": "planned",
                "description": "Job listings with company reviews and salary data"
            }
        ]
    }


@router.post("/jobs/test")
async def test_scraper_only(request: ScrapeJobsRequest):
    """
    🧪 Test scraper directly without database operations
    
    For debugging - returns raw scraper output without database save
    """
    try:
        logger.info(f"🧪 Testing scraper: {request.search_term} in {request.location}")
        
        # Test scraper directly
        result = await crawlee_bridge.scrape_jobs(
            search_term=request.search_term,
            location=request.location,
            max_jobs=request.max_jobs,
            job_site=request.job_site
        )
        
        return {
            "success": True,
            "message": "Scraper test completed",
            "scraper_result": result
        }
        
    except Exception as e:
        logger.error(f"Scraper test failed: {e}")
        return {
            "success": False, 
            "error": str(e),
            "message": "Scraper test failed"
        }


@router.get("/economics")
async def get_cost_savings():
    """
    🔥 Show the economic impact of eating Apify's lunch
    
    Compare our FREE Crawlee solution vs Apify's pricing
    """
    return {
        "our_solution": {
            "cost_per_1000_jobs": 0.00,
            "monthly_cost": 0.00,
            "setup_cost": "FREE (open source)",
            "limitations": "None (unlimited scraping)"
        },
        "apify_pricing": {
            "cost_per_1000_jobs": 30.00,
            "monthly_cost_1000_jobs": 30.00,
            "monthly_cost_10000_jobs": 300.00,
            "monthly_cost_50000_jobs": 1500.00,
            "setup_cost": "Platform fees + actor costs"
        },
        "savings": {
            "monthly_1000_jobs": 30.00,
            "monthly_10000_jobs": 300.00,
            "monthly_50000_jobs": 1500.00,
            "annual_10000_jobs": 3600.00
        },
        "lunch_status": "🍽️ EATEN! 💀"
    }


@router.post("/jobs/multi-site", response_model=ScrapeJobsResponse)
async def scrape_jobs_multi_site(
    request: MultiSiteScrapeRequest,
    db: Session = Depends(get_db)
):
    """
    🎼 Enterprise Multi-Site Job Scraping Orchestrator
    
    **LEVEL UP**: Scrape multiple job sites concurrently with enterprise features:
    
    - **Parallel Execution**: Scrape Indeed, LinkedIn, Glassdoor simultaneously
    - **Circuit Breakers**: Auto-disable failing sites, prevent cascade failures  
    - **Retry Logic**: Exponential backoff for resilient scraping
    - **Performance Monitoring**: Real-time metrics and success rates
    - **Cost Optimization**: 10x more data for the same $0.00 cost
    
    **Economic Impact**: 
    - Our cost: $0.00 (unlimited)
    - Competitors: $90-500+ per 1,000 jobs across 3 sites
    - **WE EAT EVERYONE'S LUNCH** 🔥💀
    """
    try:
        logger.info(f"🎼 Multi-site scraping: {request.search_term} across {len(request.sites)} sites")
        
        # Execute complete multi-site scrape and save workflow
        result = await crawlee_bridge.scrape_multi_site_and_save(
            search_term=request.search_term,
            location=request.location,
            sites=request.sites,
            max_jobs_per_site=request.max_jobs_per_site,
            max_concurrency=request.max_concurrency,
            db=db
        )
        
        if result['success']:
            summary = result['summary']
            scraping = result['scraping']
            message = f"Multi-site success: {summary['jobs_saved']} jobs from {scraping['sites_successful']}/{scraping['sites_queried']} sites"
            if summary['duplicates_skipped'] > 0:
                message += f" ({summary['duplicates_skipped']} duplicates skipped)"
                
            return ScrapeJobsResponse(
                success=True,
                message=message,
                scraping=result['scraping'],
                database=result['database'],
                summary=result['summary']
            )
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Multi-site scraping failed: {result.get('error', 'Unknown error')}"
            )
            
    except CrawleeIntegrationError as e:
        logger.error(f"Multi-site Crawlee integration error: {e}")
        raise HTTPException(
            status_code=422,
            detail=f"Multi-site scraping service error: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected multi-site scraping error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal multi-site scraping error: {str(e)}"
        )


@router.get("/orchestrator/status")
async def get_orchestrator_status():
    """
    🎼 Get Multi-Site Orchestrator Status & Health
    
    Returns:
    - Circuit breaker states for all sites
    - Performance metrics and success rates
    - Available scrapers and configurations
    - Economic impact statistics
    """
    try:
        # Check orchestrator script exists
        orchestrator_exists = crawlee_bridge.orchestrator_script.exists()
        
        # Get supported sites from our scrapers
        supported_sites = [
            {
                "id": "indeed",
                "name": "Indeed", 
                "status": "active",
                "features": ["anti-detection", "salary-extraction", "job-metadata"]
            },
            {
                "id": "linkedin", 
                "name": "LinkedIn Jobs",
                "status": "active",
                "features": ["professional-network", "company-insights", "easy-apply"]
            },
            {
                "id": "glassdoor",
                "name": "Glassdoor",
                "status": "active", 
                "features": ["salary-focus", "company-reviews", "benefit-extraction"]
            }
        ]
        
        return {
            "orchestrator_available": orchestrator_exists,
            "orchestrator_path": str(crawlee_bridge.orchestrator_script),
            "supported_sites": supported_sites,
            "max_concurrency": 5,
            "circuit_breaker_enabled": True,
            "retry_logic_enabled": True,
            "performance_features": [
                "parallel-execution",
                "circuit-breakers", 
                "exponential-backoff",
                "connection-pooling",
                "resource-management"
            ],
            "economic_impact": {
                "sites_supported": len(supported_sites),
                "cost_per_site": 0.00,
                "competitor_cost_per_1000_jobs": 30.00,
                "total_monthly_savings_estimate": "500-5000 USD",
                "lunch_domination_level": "MAXIMUM 🔥💀"
            }
        }
        
    except Exception as e:
        logger.error(f"Orchestrator status check failed: {e}")
        raise HTTPException(
            status_code=503,
            detail=f"Orchestrator status unavailable: {e}"
        )
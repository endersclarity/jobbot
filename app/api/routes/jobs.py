"""
Job management API routes
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.jobs import Job

router = APIRouter()

@router.get("/jobs", response_model=List[dict])
async def get_jobs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    company: Optional[str] = Query(None),
    remote_only: Optional[bool] = Query(None),
    db: Session = Depends(get_db)
):
    """Get jobs with optional filtering"""
    query = db.query(Job)
    
    if company:
        query = query.filter(Job.company.ilike(f"%{company}%"))
    
    if remote_only is not None:
        query = query.filter(Job.remote_option == remote_only)
    
    jobs = query.offset(skip).limit(limit).all()
    
    return [
        {
            "id": job.id,
            "title": job.title,
            "company": job.company,
            "location": job.location,
            "salary_min": job.salary_min,
            "salary_max": job.salary_max,
            "remote_option": job.remote_option,
            "job_type": job.job_type,
            "status": job.status,
            "scraped_date": job.scraped_date,
            "job_url": job.job_url
        } for job in jobs
    ]

@router.get("/jobs/{job_id}")
async def get_job(job_id: int, db: Session = Depends(get_db)):
    """Get a specific job by ID"""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return {
        "id": job.id,
        "title": job.title,
        "company": job.company,
        "location": job.location,
        "description": job.description,
        "requirements": job.requirements,
        "benefits": job.benefits,
        "salary_min": job.salary_min,
        "salary_max": job.salary_max,
        "remote_option": job.remote_option,
        "job_type": job.job_type,
        "experience_level": job.experience_level,
        "industry": job.industry,
        "status": job.status,
        "scraped_date": job.scraped_date,
        "posting_date": job.posting_date,
        "application_deadline": job.application_deadline,
        "job_url": job.job_url,
        "source_site": job.source_site,
        "keywords": job.keywords
    }

@router.post("/jobs")
async def create_job(job_data: dict, db: Session = Depends(get_db)):
    """Create a new job entry"""
    job = Job(**job_data)
    db.add(job)
    db.commit()
    db.refresh(job)
    return {"id": job.id, "message": "Job created successfully"}

@router.put("/jobs/{job_id}")
async def update_job(job_id: int, job_data: dict, db: Session = Depends(get_db)):
    """Update an existing job"""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    for key, value in job_data.items():
        if hasattr(job, key):
            setattr(job, key, value)
    
    db.commit()
    return {"message": "Job updated successfully"}

@router.delete("/jobs/{job_id}")
async def delete_job(job_id: int, db: Session = Depends(get_db)):
    """Delete a job"""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    db.delete(job)
    db.commit()
    return {"message": "Job deleted successfully"}
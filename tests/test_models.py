"""
Test database models
"""
import pytest
from datetime import datetime, date
from sqlalchemy.orm import Session

from app.models.jobs import Job
from app.models.applications import Application, Reference

def test_job_model_creation(db_session: Session):
    """Test Job model creation and basic operations"""
    job = Job(
        title="Python Developer",
        company="Test Company",
        location="Remote",
        salary_min=80000,
        salary_max=120000,
        description="Great Python job",
        remote_option=True,
        job_type="full-time",
        status="discovered"
    )
    
    db_session.add(job)
    db_session.commit()
    db_session.refresh(job)
    
    assert job.id is not None
    assert job.title == "Python Developer"
    assert job.company == "Test Company"
    assert job.remote_option is True
    assert job.status == "discovered"

def test_application_model_creation(db_session: Session):
    """Test Application model creation with job relationship"""
    # Create a job first
    job = Job(
        title="Python Developer",
        company="Test Company",
        location="Remote"
    )
    db_session.add(job)
    db_session.commit()
    db_session.refresh(job)
    
    # Create an application
    application = Application(
        job_id=job.id,
        application_method="email",
        personal_interest_rating=8,
        compensation_expectation=100000,
        exaggeration_level=1,
        notes="Very interested in this position"
    )
    
    db_session.add(application)
    db_session.commit()
    db_session.refresh(application)
    
    assert application.id is not None
    assert application.job_id == job.id
    assert application.personal_interest_rating == 8
    assert application.exaggeration_level == 1
    assert application.application_status == "submitted"  # default value

def test_reference_model_creation(db_session: Session):
    """Test Reference model creation"""
    reference = Reference(
        name="John Doe",
        title="Senior Developer",
        company="Previous Company",
        email="john.doe@example.com",
        phone="555-1234",
        relationship="Former colleague",
        credibility_rating=9,
        notes="Excellent reference, very responsive"
    )
    
    db_session.add(reference)
    db_session.commit()
    db_session.refresh(reference)
    
    assert reference.id is not None
    assert reference.name == "John Doe"
    assert reference.credibility_rating == 9
    assert reference.times_used == 0  # default value
    assert reference.availability_status == "available"  # default value

def test_job_application_relationship(db_session: Session):
    """Test relationship between Job and Application models"""
    job = Job(title="Test Job", company="Test Company")
    db_session.add(job)
    db_session.commit()
    db_session.refresh(job)
    
    app1 = Application(job_id=job.id, personal_interest_rating=5)
    app2 = Application(job_id=job.id, personal_interest_rating=8)
    
    db_session.add_all([app1, app2])
    db_session.commit()
    
    # Test that we can access applications through the job
    job_with_apps = db_session.query(Job).filter(Job.id == job.id).first()
    assert len(job_with_apps.applications) == 2
    assert all(app.job_id == job.id for app in job_with_apps.applications)
"""
Job service for the application.
Handles job data processing and storage.
"""
import logging
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models.job_listing import JobListing
from app.data_processing.cleaner import process_job_listings

logger = logging.getLogger(__name__)

def create_job_listing(db: Session, job_data: Dict[str, Any]) -> Optional[JobListing]:
    """
    Create a job listing in the database.
    
    Args:
        db: Database session
        job_data: Job listing data
        
    Returns:
        Created job listing or None if creation failed
    """
    try:
        job_listing = JobListing(**job_data)
        db.add(job_listing)
        db.commit()
        db.refresh(job_listing)
        return job_listing
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Error creating job listing: {e}")
        return None
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error creating job listing: {e}")
        return None

def get_job_listing_by_id(db: Session, job_id: str) -> Optional[JobListing]:
    """
    Get a job listing by its job_id.
    
    Args:
        db: Database session
        job_id: Job ID
        
    Returns:
        Job listing or None if not found
    """
    return db.query(JobListing).filter(JobListing.job_id == job_id).first()

def get_job_listings(
    db: Session, 
    skip: int = 0, 
    limit: int = 100,
    source: Optional[str] = None,
    title_search: Optional[str] = None,
    company_search: Optional[str] = None
) -> List[JobListing]:
    """
    Get job listings with optional filtering.
    
    Args:
        db: Database session
        skip: Number of records to skip
        limit: Maximum number of records to return
        source: Filter by source
        title_search: Search in job title
        company_search: Search in company name
        
    Returns:
        List of job listings
    """
    query = db.query(JobListing)
    
    if source:
        query = query.filter(JobListing.source == source)
    
    if title_search:
        query = query.filter(JobListing.title.ilike(f"%{title_search}%"))
    
    if company_search:
        query = query.filter(JobListing.company_name.ilike(f"%{company_search}%"))
    
    return query.offset(skip).limit(limit).all()

def process_and_store_jobs(
    db: Session, 
    jobs: List[Dict[str, Any]], 
    source: Optional[str] = None
) -> Dict[str, Any]:
    """
    Process and store job listings in the database.
    
    Args:
        db: Database session
        jobs: List of job listings
        source: Source of the job listings
        
    Returns:
        Dictionary with processing statistics
    """
    processed_jobs = process_job_listings(jobs, source)
    
    created_count = 0
    skipped_count = 0
    
    for job in processed_jobs:
        existing_job = get_job_listing_by_id(db, job["job_id"])
        
        if existing_job:
            skipped_count += 1
            continue
        
        result = create_job_listing(db, job)
        
        if result:
            created_count += 1
        else:
            skipped_count += 1
    
    return {
        "total_processed": len(processed_jobs),
        "created": created_count,
        "skipped": skipped_count
    }

def delete_job_listing(db: Session, job_id: str) -> bool:
    """
    Delete a job listing by its job_id.
    
    Args:
        db: Database session
        job_id: Job ID
        
    Returns:
        True if deletion was successful, False otherwise
    """
    job_listing = get_job_listing_by_id(db, job_id)
    
    if not job_listing:
        return False
    
    try:
        db.delete(job_listing)
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting job listing: {e}")
        return False

"""
Service for managing job scraping operations.
"""
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from sqlalchemy.orm import Session

from app.scrapers.manager import ScraperManager
from app.models.job import Job
from app.schemas.job import JobCreate

logger = logging.getLogger(__name__)

class ScraperService:
    """
    Service for managing job scraping operations and storing results in the database.
    """
    
    def __init__(self):
        """Initialize the scraper service."""
        self.scraper_manager = ScraperManager()
    
    def get_available_scrapers(self) -> List[str]:
        """
        Get a list of available scrapers.
        
        Returns:
            List of scraper names
        """
        return self.scraper_manager.list_scrapers()
    
    def run_scraper(self, scraper_name: str, db: Session, **kwargs) -> List[Job]:
        """
        Run a specific scraper and store results in the database.
        
        Args:
            scraper_name: Name of the scraper to run
            db: Database session
            **kwargs: Additional parameters for the scraper
            
        Returns:
            List of created Job objects
        """
        logger.info(f"Running scraper: {scraper_name}")
        
        job_data_list = self.scraper_manager.run_scraper(scraper_name, **kwargs)
        
        created_jobs = []
        for job_data in job_data_list:
            existing_job = db.query(Job).filter(Job.source_url == job_data["source_url"]).first()
            
            if existing_job:
                for key, value in job_data.items():
                    if key != "id" and hasattr(existing_job, key):
                        setattr(existing_job, key, value)
                existing_job.updated_at = datetime.now()
                db.commit()
                db.refresh(existing_job)
                created_jobs.append(existing_job)
                logger.info(f"Updated existing job: {existing_job.title} at {existing_job.company}")
            else:
                job_create = JobCreate(**job_data)
                db_job = Job(**job_create.model_dump())
                db.add(db_job)
                db.commit()
                db.refresh(db_job)
                created_jobs.append(db_job)
                logger.info(f"Created new job: {db_job.title} at {db_job.company}")
        
        logger.info(f"Scraper {scraper_name} completed: {len(created_jobs)} jobs processed")
        return created_jobs
    
    def run_all_scrapers(self, db: Session, max_workers: int = 3, **kwargs) -> Dict[str, List[Job]]:
        """
        Run all available scrapers and store results in the database.
        
        Args:
            db: Database session
            max_workers: Maximum number of parallel scrapers
            **kwargs: Additional parameters for all scrapers
            
        Returns:
            Dictionary mapping scraper names to lists of created Job objects
        """
        logger.info("Running all scrapers")
        
        all_results = self.scraper_manager.run_all_scrapers(max_workers=max_workers, **kwargs)
        
        processed_results = {}
        for scraper_name, job_data_list in all_results.items():
            processed_jobs = []
            for job_data in job_data_list:
                existing_job = db.query(Job).filter(Job.source_url == job_data["source_url"]).first()
                
                if existing_job:
                    for key, value in job_data.items():
                        if key != "id" and hasattr(existing_job, key):
                            setattr(existing_job, key, value)
                    existing_job.updated_at = datetime.now()
                    db.commit()
                    db.refresh(existing_job)
                    processed_jobs.append(existing_job)
                else:
                    job_create = JobCreate(**job_data)
                    db_job = Job(**job_create.model_dump())
                    db.add(db_job)
                    db.commit()
                    db.refresh(db_job)
                    processed_jobs.append(db_job)
            
            processed_results[scraper_name] = processed_jobs
            logger.info(f"Scraper {scraper_name} completed: {len(processed_jobs)} jobs processed")
        
        total_jobs = sum(len(jobs) for jobs in processed_results.values())
        logger.info(f"All scrapers completed: {total_jobs} total jobs processed")
        return processed_results
    
    def run_selected_scrapers(self, scraper_names: List[str], db: Session, max_workers: int = 3, **kwargs) -> Dict[str, List[Job]]:
        """
        Run selected scrapers and store results in the database.
        
        Args:
            scraper_names: List of scraper names to run
            db: Database session
            max_workers: Maximum number of parallel scrapers
            **kwargs: Additional parameters for all scrapers
            
        Returns:
            Dictionary mapping scraper names to lists of created Job objects
        """
        logger.info(f"Running selected scrapers: {scraper_names}")
        
        selected_results = self.scraper_manager.run_selected_scrapers(
            scraper_names=scraper_names,
            max_workers=max_workers,
            **kwargs
        )
        
        processed_results = {}
        for scraper_name, job_data_list in selected_results.items():
            processed_jobs = []
            for job_data in job_data_list:
                existing_job = db.query(Job).filter(Job.source_url == job_data["source_url"]).first()
                
                if existing_job:
                    for key, value in job_data.items():
                        if key != "id" and hasattr(existing_job, key):
                            setattr(existing_job, key, value)
                    existing_job.updated_at = datetime.now()
                    db.commit()
                    db.refresh(existing_job)
                    processed_jobs.append(existing_job)
                else:
                    job_create = JobCreate(**job_data)
                    db_job = Job(**job_create.model_dump())
                    db.add(db_job)
                    db.commit()
                    db.refresh(db_job)
                    processed_jobs.append(db_job)
            
            processed_results[scraper_name] = processed_jobs
            logger.info(f"Scraper {scraper_name} completed: {len(processed_jobs)} jobs processed")
        
        total_jobs = sum(len(jobs) for jobs in processed_results.values())
        logger.info(f"Selected scrapers completed: {total_jobs} total jobs processed")
        return processed_results

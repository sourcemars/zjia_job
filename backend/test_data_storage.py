"""
Test script for the data storage functionality.
"""
import json
import logging
import sys
import os
from datetime import datetime
import sqlite3

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.session import SessionLocal, engine, Base
from app.models.job_listing import JobListing
from app.services.job_service import process_and_store_jobs, get_job_listings

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_tables():
    """
    Create database tables.
    """
    logger.info("Creating database tables")
    Base.metadata.create_all(bind=engine)

def test_store_sample_data():
    """
    Test storing a sample of job data in the database.
    """
    logger.info("Testing storage of sample job data")
    
    json_files = [f for f in os.listdir('.') if f.startswith('processed_') and f.endswith('.json')]
    if not json_files:
        logger.error("No processed job data files found")
        return False
    
    json_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
    latest_file = json_files[0]
    
    logger.info(f"Testing with processed data from {latest_file}")
    
    try:
        with open(latest_file, 'r', encoding='utf-8') as f:
            jobs = json.load(f)
        
        test_jobs = jobs[:10]
        
        db = SessionLocal()
        try:
            stats = process_and_store_jobs(db, test_jobs, "iguopin")
            logger.info(f"Stored job data: {stats}")
            
            stored_jobs = get_job_listings(db, limit=10)
            logger.info(f"Retrieved {len(stored_jobs)} jobs from database")
            
            if len(stored_jobs) > 0:
                sample_job = stored_jobs[0]
                logger.info(f"Sample job from database: {sample_job.title} at {sample_job.company_name}")
                
                if "<" in sample_job.title or ">" in sample_job.title:
                    logger.error("HTML tags found in job title")
                    return False
                
                if sample_job.description and ("<" in sample_job.description or ">" in sample_job.description):
                    logger.error("HTML tags found in job description")
                    return False
                
                logger.info("No HTML tags found in stored job data")
                return True
            else:
                logger.error("No jobs retrieved from database")
                return False
        finally:
            db.close()
        
    except Exception as e:
        logger.error(f"Error testing data storage: {e}")
        return False

def test_direct_db_access():
    """
    Test direct access to the SQLite database to verify data integrity.
    """
    logger.info("Testing direct database access")
    
    try:
        conn = sqlite3.connect("zjia_job.db")
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM job_listings")
        count = cursor.fetchone()[0]
        logger.info(f"Found {count} job listings in database")
        
        cursor.execute("SELECT id, title, company_name, description FROM job_listings LIMIT 1")
        row = cursor.fetchone()
        
        if row:
            job_id, title, company_name, description = row
            logger.info(f"Sample job from direct DB access: {title} at {company_name}")
            
            if description and ("<" in description or ">" in description):
                logger.error("HTML tags found in job description")
                return False
            
            logger.info("No HTML tags found in directly accessed job data")
            return True
        else:
            logger.error("No jobs found in database")
            return False
        
    except Exception as e:
        logger.error(f"Error testing direct database access: {e}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

def main():
    """
    Main function to run the tests.
    """
    logger.info("Starting data storage tests")
    
    create_tables()
    
    if test_store_sample_data():
        logger.info("Sample data storage test passed")
    else:
        logger.error("Sample data storage test failed")
        return 1
    
    if test_direct_db_access():
        logger.info("Direct database access test passed")
    else:
        logger.error("Direct database access test failed")
        return 1
    
    logger.info("All data storage tests passed")
    return 0

if __name__ == "__main__":
    sys.exit(main())

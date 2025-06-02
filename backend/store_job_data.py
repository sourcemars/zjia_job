"""
Script to store processed job data in the database.
"""
import json
import logging
import sys
import os
import argparse
from pathlib import Path
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.session import SessionLocal, engine, Base
from app.services.job_service import process_and_store_jobs
from app.models.job_listing import JobListing

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

def store_job_data(input_file, source=None):
    """
    Store job data from a JSON file in the database.
    
    Args:
        input_file: Path to the input JSON file
        source: Source of the job listings (optional)
        
    Returns:
        Dictionary with storage statistics
    """
    logger.info(f"Storing job data from {input_file}")
    
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            jobs = json.load(f)
        
        logger.info(f"Loaded {len(jobs)} jobs from {input_file}")
        
        if not source:
            filename = os.path.basename(input_file)
            if "iguopin" in filename:
                source = "iguopin"
            elif "jobonline" in filename:
                source = "jobonline"
            else:
                source = "unknown"
        
        db = SessionLocal()
        try:
            stats = process_and_store_jobs(db, jobs, source)
            logger.info(f"Stored job data: {stats}")
            return stats
        finally:
            db.close()
        
    except Exception as e:
        logger.error(f"Error storing job data: {e}")
        raise

def main():
    """
    Main function to store job data.
    """
    parser = argparse.ArgumentParser(description='Store job data in the database')
    parser.add_argument('--input', '-i', required=True, help='Input JSON file or directory')
    parser.add_argument('--source', '-s', help='Source of the job listings')
    parser.add_argument('--recursive', '-r', action='store_true', help='Process all JSON files in directory recursively')
    
    args = parser.parse_args()
    
    input_path = Path(args.input)
    
    if not input_path.exists():
        logger.error(f"Input path {input_path} does not exist")
        return 1
    
    create_tables()
    
    if input_path.is_file():
        store_job_data(str(input_path), args.source)
        
    elif input_path.is_dir():
        if args.recursive:
            json_files = list(input_path.glob('**/*.json'))
        else:
            json_files = list(input_path.glob('*.json'))
        
        if not json_files:
            logger.error(f"No JSON files found in {input_path}")
            return 1
        
        logger.info(f"Found {len(json_files)} JSON files to process")
        
        total_stats = {
            "total_processed": 0,
            "created": 0,
            "skipped": 0
        }
        
        for json_file in json_files:
            stats = store_job_data(str(json_file), args.source)
            
            if stats:
                total_stats["total_processed"] += stats["total_processed"]
                total_stats["created"] += stats["created"]
                total_stats["skipped"] += stats["skipped"]
        
        logger.info(f"Total job data stored: {total_stats}")
    
    logger.info("Job data storage completed")
    return 0

if __name__ == "__main__":
    sys.exit(main())

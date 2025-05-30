"""
Script to fetch all job listings from iguopin.com and save them to CSV.
"""
import logging
import sys
import os
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.scrapers.iguopin_scraper import IguopinScraper

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """
    Fetch all job listings from iguopin.com and save them to CSV.
    """
    logger.info("Starting to fetch all job listings from iguopin.com")
    
    scraper = IguopinScraper()
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    logger.info("Fetching job listings...")
    jobs = scraper.get_job_listings(page_size=100, max_pages=None, delay=0.5)
    
    logger.info(f"Successfully fetched {len(jobs)} jobs")
    
    csv_filename = f"iguopin_jobs_all_{timestamp}.csv"
    scraper.save_to_csv(jobs, csv_filename)
    
    logger.info(f"Job listings saved to {csv_filename}")
    
    import json
    json_filename = f"iguopin_jobs_all_{timestamp}.json"
    with open(json_filename, 'w', encoding='utf-8') as f:
        json.dump(jobs, f, ensure_ascii=False, indent=2)
    
    logger.info(f"Job listings also saved to {json_filename}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

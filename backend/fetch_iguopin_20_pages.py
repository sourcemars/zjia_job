"""
Script to fetch 20 pages of job listings from iguopin.com and save them to JSON.
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
    Fetch 20 pages of job listings from iguopin.com and save them to JSON.
    """
    logger.info("Starting to fetch 20 pages of job listings from iguopin.com")
    
    scraper = IguopinScraper()
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    logger.info("Fetching job listings (20 pages)...")
    jobs = scraper.get_job_listings(page_size=100, max_pages=20, delay=0.5)
    
    logger.info(f"Successfully fetched {len(jobs)} jobs from 20 pages")
    
    import json
    json_filename = f"iguopin_jobs_20_pages_{timestamp}.json"
    with open(json_filename, 'w', encoding='utf-8') as f:
        json.dump(jobs, f, ensure_ascii=False, indent=2)
    
    logger.info(f"Job listings saved to {json_filename}")
    
    return json_filename

if __name__ == "__main__":
    filename = main()
    print(f"Data saved to: {filename}")

"""
Test script for the iguopin.com scraper.
"""
import logging
import json
from datetime import datetime
from app.scrapers.iguopin_scraper import IguopinScraper, crawl_iguopin

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_iguopin_scraper():
    """
    Test the IguopinScraper class by fetching a limited number of job listings.
    """
    logger.info("Testing IguopinScraper...")
    
    scraper = IguopinScraper()
    
    logger.info("Fetching first page...")
    first_page = scraper.fetch_page(page=1, page_size=10)
    
    if not first_page or "data" not in first_page:
        logger.error("Failed to fetch first page")
        return False
    
    total = first_page["data"]["total"]
    first_page_jobs = first_page["data"]["list"]
    
    logger.info(f"Successfully fetched first page. Total jobs: {total}, First page jobs: {len(first_page_jobs)}")
    
    logger.info("Fetching job listings (2 pages)...")
    jobs = scraper.get_job_listings(page_size=10, max_pages=2)
    
    logger.info(f"Successfully fetched {len(jobs)} jobs")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    json_filename = f"iguopin_test_results_{timestamp}.json"
    
    with open(json_filename, 'w', encoding='utf-8') as f:
        json.dump(jobs, f, ensure_ascii=False, indent=2)
    
    logger.info(f"Saved test results to {json_filename}")
    
    logger.info("Testing convenience function...")
    convenience_jobs = crawl_iguopin(page_size=10, max_pages=1)
    
    logger.info(f"Convenience function returned {len(convenience_jobs)} jobs")
    
    return True

if __name__ == "__main__":
    success = test_iguopin_scraper()
    if success:
        logger.info("All tests passed!")
    else:
        logger.error("Tests failed!")

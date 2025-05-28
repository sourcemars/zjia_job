#!/usr/bin/env python
"""
Test script for JobOnlineAPIScraper with pagination.
This script tests the updated Selenium-based scraper for JobOnline with pagination support.
"""
import logging
import sys
import os
import json
import asyncio
from datetime import datetime
import argparse
import time

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from app.scrapers.jobonline_api_scraper import JobOnlineAPIScraper

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)

logger = logging.getLogger(__name__)

async def test_pagination(start_page=1, num_pages=3, save_output=True):
    """Test pagination functionality of JobOnlineAPIScraper."""
    logger.info(f"Testing JobOnlineAPIScraper pagination from page {start_page} to {start_page + num_pages - 1}...")
    
    scraper = JobOnlineAPIScraper(headless=True)
    
    try:
        await scraper.initialize()
        
        all_companies = []
        
        for page in range(start_page, start_page + num_pages):
            logger.info(f"Fetching page {page}...")
            companies = await scraper.get_companies(page=page, page_size=20)
            
            if companies:
                logger.info(f"Found {len(companies)} companies on page {page}")
                
                if page == start_page:
                    logger.info("First company details from first page:")
                    for key, value in companies[0].items():
                        logger.info(f"  {key}: {value}")
                
                all_companies.extend(companies)
                
                if save_output:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    output_file = f"jobonline_api_companies_page{page}_{timestamp}.json"
                    
                    with open(output_file, "w", encoding="utf-8") as f:
                        json.dump(companies, f, ensure_ascii=False, indent=2)
                    
                    logger.info(f"Saved company data for page {page} to {output_file}")
            else:
                logger.warning(f"No companies found on page {page}")
                break
            
            time.sleep(2)
        
        logger.info(f"Total companies collected: {len(all_companies)}")
        
        if save_output and all_companies:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"jobonline_api_companies_all_pages_{timestamp}.json"
            
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(all_companies, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Saved all company data to {output_file}")
        
        return len(all_companies) > 0, all_companies
    finally:
        await scraper.cleanup()

async def test_get_job_listings(max_pages=3, save_output=True):
    """Test the get_job_listings method with pagination."""
    logger.info(f"Testing JobOnlineAPIScraper.get_job_listings with max_pages={max_pages}...")
    
    scraper = JobOnlineAPIScraper(headless=True)
    
    try:
        await scraper.initialize()
        
        companies = scraper.get_job_listings(page=1, page_size=20, max_pages=max_pages)
        
        if companies:
            logger.info(f"Found {len(companies)} companies across {max_pages} pages")
            
            logger.info("First company details:")
            for key, value in companies[0].items():
                logger.info(f"  {key}: {value}")
            
            if save_output:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_file = f"jobonline_api_companies_all_{timestamp}.json"
                
                with open(output_file, "w", encoding="utf-8") as f:
                    json.dump(companies, f, ensure_ascii=False, indent=2)
                
                logger.info(f"Saved all company data to {output_file}")
            
            return True, companies
        else:
            logger.error("No companies found")
            return False, []
    finally:
        await scraper.cleanup()

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Test JobOnlineAPIScraper with pagination")
    parser.add_argument("--start-page", type=int, default=1, help="Starting page number")
    parser.add_argument("--num-pages", type=int, default=3, help="Number of pages to fetch")
    parser.add_argument("--no-save", action="store_true", help="Don't save output files")
    parser.add_argument("--test-listings", action="store_true", help="Test get_job_listings method")
    return parser.parse_args()

async def main():
    """Run tests based on command line arguments."""
    args = parse_args()
    
    save_output = not args.no_save
    
    if args.test_listings:
        await test_get_job_listings(max_pages=args.num_pages, save_output=save_output)
    else:
        await test_pagination(start_page=args.start_page, num_pages=args.num_pages, save_output=save_output)

if __name__ == "__main__":
    asyncio.run(main())

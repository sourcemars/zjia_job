"""
Scraper for iguopin.com job listings.
This scraper uses the iguopin API to fetch job listings.
"""
import requests
import pandas as pd
import time
import json
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from tqdm import tqdm

from app.scrapers.base import BaseScraper

logger = logging.getLogger(__name__)

class IguopinScraper(BaseScraper):
    """
    Scraper for iguopin.com job listings.
    Uses the iguopin API to fetch job listings with pagination support.
    """
    
    def __init__(self):
        """
        Initialize the iguopin scraper with default settings.
        """
        super().__init__(name="iguopin")
        self.base_url = "https://gp-api.iguopin.com/api/jobs/v1/list"
        self.headers = {
            "Content-Type": "application/json;charset=UTF-8",
            "Accept": "application/json, text/plain, */*",
            "Device": "pc",
            "Subsite": "iguopin",  # 主站
            "Version": "5.0.0",
            "User-Agent": "Mozilla/5.0"
        }
        
    def get_headers(self) -> Dict[str, str]:
        """
        Override the default headers with iguopin-specific headers.
        
        Returns:
            Dict with iguopin-specific headers
        """
        return self.headers
    
    def fetch_page(self, page: int = 1, page_size: int = 100) -> Dict[str, Any]:
        """
        Fetch a single page of job listings from the iguopin API.
        
        Args:
            page: Page number to fetch
            page_size: Number of jobs per page
            
        Returns:
            JSON response from the API
        """
        payload = {
            "page": page,
            "page_size": page_size,
            "keyword": "",       # 不筛选关键字
            "nature": []         # 不筛选企业性质
        }
        
        response = self.make_request(
            url=self.base_url,
            method="POST",
            data=json.dumps(payload),
            headers=self.headers
        )
        
        if not response:
            logger.error(f"Failed to fetch page {page} from iguopin API")
            return {"data": {"list": [], "total": 0}}
        
        return response.json()
    
    def get_job_listings(self, page_size: int = 100, max_pages: Optional[int] = None, 
                         delay: float = 0.3) -> List[Dict[str, Any]]:
        """
        Get a list of job listings from iguopin.com with pagination.
        
        Args:
            page_size: Number of jobs per page
            max_pages: Maximum number of pages to fetch (None for all)
            delay: Delay between requests in seconds
            
        Returns:
            List of job listings as dictionaries
        """
        logger.info(f"Fetching job listings from iguopin.com with page_size={page_size}")
        
        first_page = self.fetch_page(1, page_size)
        if not first_page or "data" not in first_page:
            logger.error("Failed to fetch first page from iguopin API")
            return []
        
        total = first_page["data"]["total"]
        all_jobs = first_page["data"]["list"]
        
        total_pages = (total + page_size - 1) // page_size
        if max_pages:
            total_pages = min(total_pages, max_pages)
        
        logger.info(f"Found {total} jobs across {total_pages} pages")
        
        for page in tqdm(range(2, total_pages + 1), desc="抓取中", unit="页"):
            page_data = self.fetch_page(page, page_size)
            if page_data and "data" in page_data and "list" in page_data["data"]:
                all_jobs.extend(page_data["data"]["list"])
            else:
                logger.warning(f"Failed to fetch page {page} from iguopin API")
            
            time.sleep(delay)  # Rate limiting
        
        logger.info(f"Successfully fetched {len(all_jobs)} jobs from iguopin.com")
        return all_jobs
    
    def get_job_details(self, job_url: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific job.
        For iguopin, job details are already included in the listings.
        
        Args:
            job_url: URL of the job listing
            
        Returns:
            Dictionary with job details or None if failed
        """
        logger.warning("get_job_details is not needed for iguopin as details are in listings")
        return None
    
    def normalize_job_data(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize iguopin job data to a standard format.
        
        Args:
            job_data: Raw job data from the scraper
            
        Returns:
            Normalized job data
        """
        normalized = {
            "title": job_data.get("title", ""),
            "company": job_data.get("company_name", ""),
            "location": job_data.get("city", ""),
            "description": job_data.get("description", ""),
            "requirements": job_data.get("requirements", ""),
            "salary": job_data.get("salary", ""),
            "source": self.name,
            "source_url": job_data.get("url", ""),
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "company_nature": job_data.get("company_nature", ""),
            "company_size": job_data.get("company_size", ""),
            "education": job_data.get("education", ""),
            "experience": job_data.get("experience", ""),
            "job_type": job_data.get("job_type", ""),
            "publish_time": job_data.get("publish_time", ""),
            "raw_data": job_data  # Store the original data
        }
        
        return normalized
    
    def save_to_csv(self, jobs: List[Dict[str, Any]], filename: str = None) -> str:
        """
        Save job listings to a CSV file.
        
        Args:
            jobs: List of job dictionaries
            filename: Optional filename, defaults to iguopin_jobs_{timestamp}.csv
            
        Returns:
            Path to the saved CSV file
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"iguopin_jobs_{timestamp}.csv"
        
        df = pd.json_normalize(jobs)
        df.to_csv(filename, index=False, encoding="utf-8-sig")
        logger.info(f"Saved {len(df)} jobs to {filename}")
        
        return filename
    
    def run(self, page_size: int = 100, max_pages: Optional[int] = None, 
            delay: float = 0.3, save_csv: bool = True) -> List[Dict[str, Any]]:
        """
        Run the scraper to get job listings.
        
        Args:
            page_size: Number of jobs per page
            max_pages: Maximum number of pages to fetch (None for all)
            delay: Delay between requests in seconds
            save_csv: Whether to save results to CSV
            
        Returns:
            List of normalized job data
        """
        logger.info(f"Starting iguopin scraper")
        
        job_listings = self.get_job_listings(page_size=page_size, max_pages=max_pages, delay=delay)
        logger.info(f"Found {len(job_listings)} job listings")
        
        results = []
        for job in job_listings:
            normalized_job = self.normalize_job_data(job)
            results.append(normalized_job)
        
        if save_csv and results:
            self.save_to_csv(job_listings)  # Save raw data to CSV
        
        logger.info(f"Successfully scraped {len(results)} jobs from iguopin.com")
        return results


def crawl_iguopin(page_size: int = 100, max_pages: Optional[int] = None, 
                 delay: float = 0.3, save_csv: bool = True) -> List[Dict[str, Any]]:
    """
    Convenience function to crawl iguopin.com job listings.
    
    Args:
        page_size: Number of jobs per page
        max_pages: Maximum number of pages to fetch (None for all)
        delay: Delay between requests in seconds
        save_csv: Whether to save results to CSV
        
    Returns:
        List of job listings
    """
    scraper = IguopinScraper()
    jobs = scraper.get_job_listings(page_size=page_size, max_pages=max_pages, delay=delay)
    
    if save_csv and jobs:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"iguopin_jobs_{timestamp}.csv"
        df = pd.json_normalize(jobs)
        df.to_csv(filename, index=False, encoding="utf-8-sig")
        logger.info(f"Saved {len(df)} jobs to {filename}")
    
    return jobs


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    jobs = crawl_iguopin(page_size=100, max_pages=2)
    print(f"Scraped {len(jobs)} jobs from iguopin.com")

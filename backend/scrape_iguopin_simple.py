"""
Simple script to scrape 20 pages from iguopin without base scraper dependency.
"""
import requests
import pandas as pd
import time
import json
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from tqdm import tqdm

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def fetch_iguopin_page(page: int = 1, page_size: int = 100) -> Dict[str, Any]:
    """
    Fetch a single page of job listings from the iguopin API.
    """
    base_url = "https://gp-api.iguopin.com/api/jobs/v1/list"
    headers = {
        "Content-Type": "application/json;charset=UTF-8",
        "Accept": "application/json, text/plain, */*",
        "Device": "pc",
        "Subsite": "iguopin",
        "Version": "5.0.0",
        "User-Agent": "Mozilla/5.0"
    }
    
    payload = {
        "page": page,
        "page_size": page_size,
        "keyword": "",
        "nature": []
    }
    
    try:
        response = requests.post(
            url=base_url,
            data=json.dumps(payload),
            headers=headers,
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"Failed to fetch page {page}: {e}")
        return {"data": {"list": [], "total": 0}}

def scrape_iguopin_20_pages():
    """
    Scrape exactly 20 pages from iguopin.com
    """
    logger.info("Starting to scrape 20 pages from iguopin.com")
    
    page_size = 100
    max_pages = 20
    delay = 0.5
    
    first_page = fetch_iguopin_page(1, page_size)
    if not first_page or "data" not in first_page:
        logger.error("Failed to fetch first page from iguopin API")
        return []
    
    total = first_page["data"]["total"]
    all_jobs = first_page["data"]["list"]
    
    logger.info(f"Found {total} total jobs, fetching {max_pages} pages")
    
    for page in tqdm(range(2, max_pages + 1), desc="Scraping pages", unit="page"):
        page_data = fetch_iguopin_page(page, page_size)
        if page_data and "data" in page_data and "list" in page_data["data"]:
            all_jobs.extend(page_data["data"]["list"])
        else:
            logger.warning(f"Failed to fetch page {page}")
        
        time.sleep(delay)  # Rate limiting
    
    logger.info(f"Successfully scraped {len(all_jobs)} jobs from {max_pages} pages")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    json_filename = f"iguopin_jobs_20_pages_{timestamp}.json"
    
    with open(json_filename, 'w', encoding='utf-8') as f:
        json.dump(all_jobs, f, ensure_ascii=False, indent=2)
    
    logger.info(f"Data saved to {json_filename}")
    return json_filename, all_jobs

if __name__ == "__main__":
    filename, jobs = scrape_iguopin_20_pages()
    print(f"Scraped {len(jobs)} jobs and saved to {filename}")

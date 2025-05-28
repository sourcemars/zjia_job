#!/usr/bin/env python
"""
Test script for JobOnlineAPIScraper.
This script tests the Selenium-based scraper for JobOnline recruitment platforms.
"""
import logging
import sys
import os
import json
import asyncio
from datetime import datetime
import argparse
import time
import traceback

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from app.scrapers.jobonline_api_scraper import JobOnlineAPIScraper

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)

logger = logging.getLogger(__name__)

async def test_direct_selenium_scraping(headless=True, save_output=True):
    """Test direct Selenium scraping approach for JobOnline recruitment platforms."""
    logger.info(f"Testing direct Selenium scraping for JobOnline recruitment platforms (headless={headless})...")
    
    test_id = f"{int(time.time())}_{os.getpid()}"
    logger.info(f"Test ID: {test_id}")
    
    scraper = JobOnlineAPIScraper(headless=headless)
    
    try:
        logger.info("Initializing scraper...")
        init_success = await scraper.initialize()
        
        if not init_success or not scraper.driver:
            logger.error("Failed to initialize WebDriver")
            return False, None
        
        logger.info("WebDriver initialized successfully")
        
        logger.info("Taking initial screenshot...")
        scraper._save_debug_screenshot()
        
        # Get recruitment platforms
        logger.info("Fetching recruitment platforms...")
        platforms = await scraper.get_companies(page=1)
        
        if platforms:
            logger.info(f"Successfully scraped {len(platforms)} recruitment platforms using Selenium")
            logger.info("First platform details:")
            for key, value in platforms[0].items():
                if key == "company_logo" and isinstance(value, str) and len(value) > 100:
                    logger.info(f"  {key}: {value[:50]}...")
                else:
                    logger.info(f"  {key}: {value}")
            
            if save_output:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_file = f"jobonline_platforms_{timestamp}.json"
                
                with open(output_file, "w", encoding="utf-8") as f:
                    json.dump(platforms, f, ensure_ascii=False, indent=2)
                
                logger.info(f"Saved platform data to {output_file}")
            
            return True, platforms
        else:
            logger.error("No platforms found using standard extraction")
            
            logger.info("Attempting JavaScript-based extraction as fallback...")
            
            if scraper.driver:
                try:
                    scraper._save_debug_screenshot(suffix="before_js_extraction")
                    
                    # Execute JavaScript to extract platform information
                    platforms_data = scraper.driver.execute_script("""
                        const platforms = [];
                        
                        // Find all elements that might contain platform information
                        document.querySelectorAll('li').forEach((item, index) => {
                            // Extract text content
                            const text = item.textContent.trim();
                            
                            // Check if this item contains job count information
                            if (text.includes('职位')) {
                                // Extract platform name
                                let name = '';
                                const h3 = item.querySelector('h3');
                                if (h3) {
                                    name = h3.textContent.trim();
                                }
                                
                                // Extract logo URL
                                let logo = '';
                                const img = item.querySelector('img');
                                if (img && img.src) {
                                    logo = img.src;
                                }
                                
                                // Extract job count
                                let jobCount = 0;
                                const countMatch = text.match(/职位\\s*(\\d+)/);
                                if (countMatch) {
                                    jobCount = parseInt(countMatch[1]);
                                }
                                
                                platforms.push({
                                    id: `platform_${index}`,
                                    name: name,
                                    logo: logo,
                                    jobCount: jobCount,
                                    text: text.substring(0, 100) + '...'
                                });
                            }
                        });
                        
                        return platforms;
                    """)
                    
                    if platforms_data and len(platforms_data) > 0:
                        logger.info(f"Found {len(platforms_data)} platforms via JavaScript fallback")
                        
                        platforms = []
                        for platform in platforms_data:
                            platforms.append({
                                "company_id": platform.get('id', ''),
                                "company_name": platform.get('name', ''),
                                "company_logo": platform.get('logo', ''),
                                "job_count": platform.get('jobCount', 0),
                                "source": "jobonline",
                                "url": f"https://www.jobonline.cn/company/{platform.get('id', '')}"
                            })
                        
                        if save_output:
                            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                            output_file = f"jobonline_platforms_js_{timestamp}.json"
                            
                            with open(output_file, "w", encoding="utf-8") as f:
                                json.dump(platforms, f, ensure_ascii=False, indent=2)
                            
                            logger.info(f"Saved JavaScript-extracted platform data to {output_file}")
                        
                        return True, platforms
                except Exception as js_error:
                    logger.error(f"JavaScript extraction failed: {js_error}")
                    logger.error(traceback.format_exc())
            
            if scraper.driver:
                try:
                    page_source = scraper.driver.page_source
                    source_file = f"jobonline_page_source_{test_id}.html"
                    with open(source_file, "w", encoding="utf-8") as f:
                        f.write(page_source)
                    logger.info(f"Saved page source to {source_file}")
                except Exception as source_error:
                    logger.error(f"Failed to save page source: {source_error}")
            
            return False, None
    except Exception as e:
        logger.error(f"Error in test_direct_selenium_scraping: {e}")
        logger.error(traceback.format_exc())
        
        if scraper and scraper.driver:
            try:
                scraper._save_debug_screenshot(suffix="error")
            except Exception as screenshot_error:
                logger.error(f"Failed to save error screenshot: {screenshot_error}")
        
        return False, None
    finally:
        if scraper:
            await scraper.cleanup()

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Test JobOnlineAPIScraper")
    parser.add_argument("--no-save", action="store_true", help="Don't save output files")
    parser.add_argument("--headless", action="store_true", help="Run in headless mode")
    parser.add_argument("--no-headless", action="store_true", help="Run in non-headless mode")
    return parser.parse_args()

async def main():
    """Run tests based on command line arguments."""
    args = parse_args()
    
    save_output = not args.no_save
    
    headless = True  # Default to headless
    if args.no_headless:
        headless = False
    elif args.headless:
        headless = True
    
    logger.info(f"Running test with headless={headless}, save_output={save_output}")
    await test_direct_selenium_scraping(headless=headless, save_output=save_output)

if __name__ == "__main__":
    asyncio.run(main())

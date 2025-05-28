#!/usr/bin/env python
"""
Test script to verify pagination information on JobOnline.
This script checks the total number of pages and companies per page.
"""
import logging
import sys
import os
import asyncio
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)

logger = logging.getLogger(__name__)

class PaginationChecker:
    """Class to check pagination information on JobOnline."""
    
    def __init__(self, headless=True):
        """Initialize the pagination checker."""
        self.headless = headless
        self.driver = None
        self.base_url = "https://www.jobonline.cn/flagship"
    
    async def initialize(self):
        """Initialize the WebDriver."""
        logger.info("Initializing WebDriver...")
        
        chrome_options = Options()
        if self.headless:
            chrome_options.add_argument("--headless")
        
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-popup-blocking")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36")
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            
            self.driver.execute_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
            """)
            logger.info("Anti-detection script added to WebDriver")
            
            return True
        except Exception as e:
            logger.error(f"Failed to initialize WebDriver: {e}")
            return False
    
    async def check_pagination(self):
        """Check pagination information on JobOnline."""
        if not self.driver:
            logger.error("WebDriver not initialized")
            return None
        
        try:
            logger.info(f"Navigating to {self.base_url}...")
            self.driver.get(self.base_url)
            
            time.sleep(5)
            
            screenshot_dir = "/home/ubuntu/screenshots"
            os.makedirs(screenshot_dir, exist_ok=True)
            screenshot_path = f"{screenshot_dir}/pagination_check_{int(time.time())}.png"
            self.driver.save_screenshot(screenshot_path)
            logger.info(f"Saved screenshot to {screenshot_path}")
            
            pagination_info = self._extract_pagination_info()
            
            companies_per_page = self._count_companies_on_page()
            
            return {
                "pagination_info": pagination_info,
                "companies_per_page": companies_per_page
            }
        except Exception as e:
            logger.error(f"Error checking pagination: {e}")
            return None
        finally:
            try:
                page_source_path = f"/home/ubuntu/page_sources/pagination_check_{int(time.time())}.html"
                os.makedirs(os.path.dirname(page_source_path), exist_ok=True)
                with open(page_source_path, "w", encoding="utf-8") as f:
                    f.write(self.driver.page_source)
                logger.info(f"Saved page source to {page_source_path}")
            except Exception as e:
                logger.error(f"Failed to save page source: {e}")
    
    def _extract_pagination_info(self):
        """Extract pagination information from the page."""
        logger.info("Extracting pagination information...")
        
        pagination_selectors = [
            ".pagination", 
            ".pager", 
            ".page-navigation",
            "ul.pagination",
            "div.pagination",
            ".page-list",
            ".page-numbers"
        ]
        
        for selector in pagination_selectors:
            try:
                pagination_element = self.driver.find_element(By.CSS_SELECTOR, selector)
                logger.info(f"Found pagination element with selector: {selector}")
                
                last_page_selectors = [
                    "li:last-child a", 
                    "a:last-child",
                    ".last a",
                    ".last-page"
                ]
                
                for last_selector in last_page_selectors:
                    try:
                        last_page_element = pagination_element.find_element(By.CSS_SELECTOR, last_selector)
                        last_page_text = last_page_element.text.strip()
                        
                        if last_page_text and last_page_text.isdigit():
                            logger.info(f"Found last page number: {last_page_text}")
                            return {"total_pages": int(last_page_text)}
                    except NoSuchElementException:
                        continue
                
                try:
                    page_links = pagination_element.find_elements(By.TAG_NAME, "a")
                    page_numbers = []
                    
                    for link in page_links:
                        text = link.text.strip()
                        if text and text.isdigit():
                            page_numbers.append(int(text))
                    
                    if page_numbers:
                        max_page = max(page_numbers)
                        logger.info(f"Found max page number from links: {max_page}")
                        return {"total_pages": max_page}
                except Exception as e:
                    logger.error(f"Error extracting page numbers: {e}")
            except NoSuchElementException:
                continue
        
        try:
            logger.info("Trying JavaScript to extract pagination information...")
            pagination_info = self.driver.execute_script("""
                // Try to find pagination elements
                const paginationElements = document.querySelectorAll('.pagination, .pager, .page-navigation, ul.pagination, div.pagination, .page-list, .page-numbers');
                
                if (paginationElements.length > 0) {
                    // Try to find the last page number
                    const pageLinks = paginationElements[0].querySelectorAll('a');
                    const pageNumbers = [];
                    
                    for (const link of pageLinks) {
                        const text = link.textContent.trim();
                        if (text && !isNaN(text)) {
                            pageNumbers.push(parseInt(text));
                        }
                    }
                    
                    if (pageNumbers.length > 0) {
                        return { totalPages: Math.max(...pageNumbers) };
                    }
                }
                
                // Try to find any text that might contain pagination information
                const bodyText = document.body.textContent;
                const paginationRegex = /共\s*(\d+)\s*页/;
                const match = bodyText.match(paginationRegex);
                
                if (match && match[1]) {
                    return { totalPages: parseInt(match[1]) };
                }
                
                return null;
            """)
            
            if pagination_info:
                logger.info(f"Found pagination info via JavaScript: {pagination_info}")
                return pagination_info
        except Exception as e:
            logger.error(f"Error executing JavaScript for pagination: {e}")
        
        logger.warning("Could not find pagination information")
        return None
    
    def _count_companies_on_page(self):
        """Count the number of companies displayed on the current page."""
        logger.info("Counting companies on page...")
        
        company_selectors = [
            ".flagship-item",
            ".company-card",
            ".enterprise-card",
            "li.company-item",
            ".main-content > div > div > ul > li"
        ]
        
        for selector in company_selectors:
            try:
                company_elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if company_elements:
                    logger.info(f"Found {len(company_elements)} companies with selector: {selector}")
                    return len(company_elements)
            except Exception:
                continue
        
        try:
            li_elements = self.driver.find_elements(By.TAG_NAME, "li")
            
            company_count = 0
            for li in li_elements:
                try:
                    text = li.text.strip()
                    if "职位" in text or "公司" in text or "企业" in text:
                        company_count += 1
                except Exception:
                    continue
            
            if company_count > 0:
                logger.info(f"Found {company_count} potential company cards using general approach")
                return company_count
        except Exception as e:
            logger.error(f"Error counting companies with general approach: {e}")
        
        try:
            logger.info("Trying JavaScript to count companies...")
            company_count = self.driver.execute_script("""
                // Try specific selectors
                const selectors = ['.flagship-item', '.company-card', '.enterprise-card', 'li.company-item', '.main-content > div > div > ul > li'];
                
                for (const selector of selectors) {
                    const elements = document.querySelectorAll(selector);
                    if (elements.length > 0) {
                        return elements.length;
                    }
                }
                
                // Try to find all li elements that might be company cards
                const liElements = document.querySelectorAll('li');
                let companyCount = 0;
                
                for (const li of liElements) {
                    const text = li.textContent.trim();
                    if (text.includes('职位') || text.includes('公司') || text.includes('企业')) {
                        companyCount++;
                    }
                }
                
                return companyCount > 0 ? companyCount : null;
            """)
            
            if company_count:
                logger.info(f"Found {company_count} companies via JavaScript")
                return company_count
        except Exception as e:
            logger.error(f"Error executing JavaScript for company count: {e}")
        
        logger.warning("Could not count companies on page")
        return None
    
    async def cleanup(self):
        """Clean up resources."""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("WebDriver closed")
            except Exception as e:
                logger.error(f"Error closing WebDriver: {e}")

async def main():
    """Main function to check pagination information."""
    logger.info("Starting pagination check...")
    
    checker = PaginationChecker(headless=True)
    
    try:
        init_success = await checker.initialize()
        
        if init_success:
            pagination_data = await checker.check_pagination()
            
            if pagination_data:
                logger.info("Pagination check results:")
                logger.info(f"Pagination info: {pagination_data['pagination_info']}")
                logger.info(f"Companies per page: {pagination_data['companies_per_page']}")
                
                total_pages = pagination_data['pagination_info'].get('total_pages') if pagination_data['pagination_info'] else None
                companies_per_page = pagination_data['companies_per_page']
                
                if total_pages == 659:
                    logger.info("✅ Confirmed: Total pages is 659")
                else:
                    logger.info(f"❌ Total pages is {total_pages}, not 659 as expected")
                
                if companies_per_page == 30:
                    logger.info("✅ Confirmed: Companies per page is 30")
                else:
                    logger.info(f"❌ Companies per page is {companies_per_page}, not 30 as expected")
            else:
                logger.error("Failed to get pagination data")
        else:
            logger.error("Failed to initialize WebDriver")
    finally:
        await checker.cleanup()

if __name__ == "__main__":
    asyncio.run(main())

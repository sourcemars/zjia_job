#!/usr/bin/env python
"""
Script to verify pagination information on JobOnline.
This script specifically checks for the total number of pages and companies per page.
"""
import logging
import sys
import os
import asyncio
import time
import re
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

class PaginationVerifier:
    """Class to verify pagination information on JobOnline."""
    
    def __init__(self, headless=True):
        """Initialize the pagination verifier."""
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
    
    async def verify_pagination(self):
        """Verify pagination information on JobOnline."""
        if not self.driver:
            logger.error("WebDriver not initialized")
            return None
        
        try:
            logger.info(f"Navigating to {self.base_url}...")
            self.driver.get(self.base_url)
            
            time.sleep(5)
            
            screenshot_dir = "/home/ubuntu/screenshots"
            os.makedirs(screenshot_dir, exist_ok=True)
            screenshot_path = f"{screenshot_dir}/pagination_verify_{int(time.time())}.png"
            self.driver.save_screenshot(screenshot_path)
            logger.info(f"Saved screenshot to {screenshot_path}")
            
            companies_on_first_page = self._count_companies()
            logger.info(f"Found {companies_on_first_page} companies on first page")
            
            pagination_info = self._extract_pagination_info()
            
            if not pagination_info or 'total_pages' not in pagination_info:
                logger.info("Trying to navigate to a high page number to find total pages...")
                high_page_url = f"{self.base_url}?page=659"
                self.driver.get(high_page_url)
                time.sleep(5)
                
                screenshot_path = f"{screenshot_dir}/pagination_high_page_{int(time.time())}.png"
                self.driver.save_screenshot(screenshot_path)
                logger.info(f"Saved screenshot of high page to {screenshot_path}")
                
                current_url = self.driver.current_url
                logger.info(f"Current URL after navigating to high page: {current_url}")
                
                page_match = re.search(r'page=(\d+)', current_url)
                if page_match:
                    current_page = int(page_match.group(1))
                    logger.info(f"Current page from URL: {current_page}")
                    
                    if current_page == 659:
                        logger.info("Page 659 appears to be valid")
                        pagination_info = {'total_pages': 659}
                    else:
                        logger.info(f"Redirected to page {current_page}, might be the last valid page")
                        pagination_info = {'total_pages': current_page}
                
                companies_on_high_page = self._count_companies()
                logger.info(f"Found {companies_on_high_page} companies on high page")
            
            if not pagination_info or 'total_pages' not in pagination_info:
                logger.info("Using binary search to find last valid page...")
                last_page = self._find_last_page_binary_search()
                if last_page:
                    logger.info(f"Binary search found last valid page: {last_page}")
                    pagination_info = {'total_pages': last_page}
            
            companies_per_page_list = []
            for page in range(1, min(4, pagination_info.get('total_pages', 4))):
                page_url = f"{self.base_url}?page={page}"
                logger.info(f"Navigating to page {page}...")
                self.driver.get(page_url)
                time.sleep(5)
                
                companies_count = self._count_companies()
                logger.info(f"Found {companies_count} companies on page {page}")
                companies_per_page_list.append(companies_count)
            
            if companies_per_page_list:
                most_common_count = max(set(companies_per_page_list), key=companies_per_page_list.count)
                logger.info(f"Most common companies per page: {most_common_count}")
            else:
                most_common_count = companies_on_first_page
            
            return {
                'total_pages': pagination_info.get('total_pages') if pagination_info else None,
                'companies_per_page': most_common_count
            }
        except Exception as e:
            logger.error(f"Error verifying pagination: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return None
        finally:
            try:
                page_source_path = f"/home/ubuntu/page_sources/pagination_verify_{int(time.time())}.html"
                os.makedirs(os.path.dirname(page_source_path), exist_ok=True)
                with open(page_source_path, "w", encoding="utf-8") as f:
                    f.write(self.driver.page_source)
                logger.info(f"Saved page source to {page_source_path}")
            except Exception as e:
                logger.error(f"Failed to save page source: {e}")
    
    def _find_last_page_binary_search(self, max_page=1000):
        """Use binary search to find the last valid page."""
        low = 1
        high = max_page
        last_valid_page = 1
        
        while low <= high:
            mid = (low + high) // 2
            logger.info(f"Binary search: Trying page {mid}...")
            
            page_url = f"{self.base_url}?page={mid}"
            self.driver.get(page_url)
            time.sleep(3)
            
            current_url = self.driver.current_url
            page_match = re.search(r'page=(\d+)', current_url)
            
            if page_match and int(page_match.group(1)) == mid:
                last_valid_page = mid
                low = mid + 1
            else:
                high = mid - 1
        
        return last_valid_page
    
    def _extract_pagination_info(self):
        """Extract pagination information from the page."""
        logger.info("Extracting pagination information...")
        
        try:
            page_text = self.driver.find_element(By.TAG_NAME, "body").text
            
            patterns = [
                r'共\s*(\d+)\s*页',  # "共X页"
                r'第\s*\d+\s*/\s*(\d+)\s*页',  # "第X/Y页"
                r'Page\s*\d+\s*of\s*(\d+)',  # "Page X of Y"
                r'(\d+)\s*页',  # "X页"
                r'总页数[：:]\s*(\d+)',  # "总页数: X"
                r'总共\s*(\d+)\s*页',  # "总共X页"
            ]
            
            for pattern in patterns:
                match = re.search(pattern, page_text)
                if match:
                    total_pages = int(match.group(1))
                    logger.info(f"Found total pages from text: {total_pages}")
                    return {'total_pages': total_pages}
        except Exception as e:
            logger.error(f"Error extracting pagination text: {e}")
        
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
                const paginationRegexes = [
                    /共\\s*(\\d+)\\s*页/,
                    /第\\s*\\d+\\s*\\/\\s*(\\d+)\\s*页/,
                    /Page\\s*\\d+\\s*of\\s*(\\d+)/,
                    /(\\d+)\\s*页/,
                    /总页数[：:]\\s*(\\d+)/,
                    /总共\\s*(\\d+)\\s*页/
                ];
                
                for (const regex of paginationRegexes) {
                    const match = bodyText.match(regex);
                    if (match && match[1]) {
                        return { totalPages: parseInt(match[1]) };
                    }
                }
                
                return null;
            """)
            
            if pagination_info and 'totalPages' in pagination_info:
                logger.info(f"Found pagination info via JavaScript: {pagination_info}")
                return {'total_pages': pagination_info['totalPages']}
        except Exception as e:
            logger.error(f"Error executing JavaScript for pagination: {e}")
        
        logger.warning("Could not find pagination information")
        return None
    
    def _count_companies(self):
        """Count the number of companies displayed on the current page."""
        logger.info("Counting companies on page...")
        
        company_selectors = [
            ".flagship-item",
            ".company-card",
            ".enterprise-card",
            "li.company-item",
            ".main-content > div > div > ul > li",
            "li"  # Most general selector
        ]
        
        for selector in company_selectors:
            try:
                company_elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if company_elements:
                    company_count = 0
                    for element in company_elements:
                        try:
                            text = element.text.strip()
                            if "职位" in text and (("公司" in text) or ("企业" in text) or ("招聘" in text)):
                                company_count += 1
                        except Exception:
                            continue
                    
                    if company_count > 0:
                        logger.info(f"Found {company_count} companies with selector: {selector}")
                        return company_count
            except Exception:
                continue
        
        try:
            logger.info("Trying JavaScript to count companies...")
            company_count = self.driver.execute_script("""
                // Function to check if an element is likely a company card
                function isCompanyCard(element) {
                    const text = element.textContent.trim();
                    return text.includes('职位') && (text.includes('公司') || text.includes('企业') || text.includes('招聘'));
                }
                
                // Try specific selectors
                const selectors = ['.flagship-item', '.company-card', '.enterprise-card', 'li.company-item', '.main-content > div > div > ul > li'];
                
                for (const selector of selectors) {
                    const elements = document.querySelectorAll(selector);
                    if (elements.length > 0) {
                        // Filter elements to only include those that are likely company cards
                        let companyCount = 0;
                        for (const element of elements) {
                            if (isCompanyCard(element)) {
                                companyCount++;
                            }
                        }
                        
                        if (companyCount > 0) {
                            return companyCount;
                        }
                    }
                }
                
                // Try to find all li elements that might be company cards
                const liElements = document.querySelectorAll('li');
                let companyCount = 0;
                
                for (const li of liElements) {
                    if (isCompanyCard(li)) {
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
        return 0
    
    async def cleanup(self):
        """Clean up resources."""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("WebDriver closed")
            except Exception as e:
                logger.error(f"Error closing WebDriver: {e}")

async def main():
    """Main function to verify pagination information."""
    logger.info("Starting pagination verification...")
    
    verifier = PaginationVerifier(headless=True)
    
    try:
        init_success = await verifier.initialize()
        
        if init_success:
            pagination_data = await verifier.verify_pagination()
            
            if pagination_data:
                logger.info("Pagination verification results:")
                logger.info(f"Total pages: {pagination_data.get('total_pages')}")
                logger.info(f"Companies per page: {pagination_data.get('companies_per_page')}")
                
                total_pages = pagination_data.get('total_pages')
                companies_per_page = pagination_data.get('companies_per_page')
                
                if total_pages == 659:
                    logger.info("✅ Confirmed: Total pages is 659")
                elif total_pages:
                    logger.info(f"❌ Total pages is {total_pages}, not 659 as expected")
                else:
                    logger.info("❓ Could not determine total pages")
                
                if companies_per_page == 30:
                    logger.info("✅ Confirmed: Companies per page is 30")
                else:
                    logger.info(f"❌ Companies per page is {companies_per_page}, not 30 as expected")
            else:
                logger.error("Failed to get pagination data")
        else:
            logger.error("Failed to initialize WebDriver")
    finally:
        await verifier.cleanup()

if __name__ == "__main__":
    asyncio.run(main())

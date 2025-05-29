import os
import time
import json
import logging
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException, 
    NoSuchElementException, 
    ElementClickInterceptedException,
    StaleElementReferenceException,
    ElementNotInteractableException
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

os.makedirs("/home/ubuntu/screenshots", exist_ok=True)
os.makedirs("/home/ubuntu/page_sources", exist_ok=True)

class EnhancedInternshipScraper:
    """
    An enhanced scraper specifically designed to extract internship positions from JobOnline
    with improved strategies for finding and extracting position details.
    """
    
    def __init__(self, headless=True):
        """Initialize the scraper with WebDriver configuration."""
        self.headless = headless
        self.driver = None
        self.base_url = "https://www.jobonline.cn/probation/company?activeProbation=1"
        self.results = []
        
    def setup_driver(self):
        """Set up and return a configured Chrome WebDriver."""
        options = Options()
        if self.headless:
            options.add_argument("--headless=new")
        
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-extensions")
        
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        
        options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36")
        
        try:
            logger.info("Initializing Chrome WebDriver...")
            driver = webdriver.Chrome(options=options)
            
            driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
                "source": """
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    });
                """
            })
            
            logger.info("WebDriver initialized successfully")
            return driver
        except Exception as e:
            logger.error(f"Failed to initialize WebDriver: {e}")
            return None
    
    def save_screenshot(self, filename_prefix):
        """Save a screenshot of the current page."""
        if not self.driver:
            return
        
        timestamp = int(time.time())
        filename = f"/home/ubuntu/screenshots/{filename_prefix}_{timestamp}.png"
        self.driver.save_screenshot(filename)
        logger.info(f"Saved screenshot to {filename}")
        return filename
    
    def save_page_source(self, filename_prefix):
        """Save the page source of the current page."""
        if not self.driver:
            return
        
        timestamp = int(time.time())
        filename = f"/home/ubuntu/page_sources/{filename_prefix}_{timestamp}.html"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(self.driver.page_source)
        logger.info(f"Saved page source to {filename}")
        return filename
    
    def navigate_to_url(self, url, wait_time=5):
        """Navigate to a URL and wait for page to load."""
        if not self.driver:
            return False
        
        try:
            logger.info(f"Navigating to {url}")
            self.driver.get(url)
            time.sleep(wait_time)  # Wait for page to load
            return True
        except Exception as e:
            logger.error(f"Failed to navigate to {url}: {e}")
            return False
    
    def safe_find_element(self, by, value, parent=None, timeout=5):
        """
        Safely find an element, handling exceptions.
        
        Args:
            by: By locator strategy
            value: Locator value
            parent: Parent element to search within (uses driver if None)
            timeout: Time to wait for element to appear
            
        Returns:
            The found element or None if not found
        """
        try:
            if parent:
                if timeout > 0:
                    WebDriverWait(self.driver, timeout).until(
                        lambda d: parent.find_element(by, value)
                    )
                return parent.find_element(by, value)
            else:
                if timeout > 0:
                    WebDriverWait(self.driver, timeout).until(
                        EC.presence_of_element_located((by, value))
                    )
                return self.driver.find_element(by, value)
        except (NoSuchElementException, StaleElementReferenceException, TimeoutException):
            return None
    
    def safe_find_elements(self, by, value, parent=None, timeout=5):
        """
        Safely find elements, handling exceptions.
        
        Args:
            by: By locator strategy
            value: Locator value
            parent: Parent element to search within (uses driver if None)
            timeout: Time to wait for elements to appear
            
        Returns:
            List of found elements or empty list if none found
        """
        try:
            if parent:
                if timeout > 0:
                    WebDriverWait(self.driver, timeout).until(
                        lambda d: len(parent.find_elements(by, value)) > 0
                    )
                return parent.find_elements(by, value)
            else:
                if timeout > 0:
                    WebDriverWait(self.driver, timeout).until(
                        EC.presence_of_all_elements_located((by, value))
                    )
                return self.driver.find_elements(by, value)
        except (NoSuchElementException, StaleElementReferenceException, TimeoutException):
            return []
    
    def click_element_safely(self, element, wait_time=3):
        """
        Click an element safely, handling exceptions.
        
        Args:
            element: Element to click
            wait_time: Time to wait after click
            
        Returns:
            True if click was successful, False otherwise
        """
        if not element:
            return False
        
        strategies = [
            lambda: self.driver.execute_script("arguments[0].click();", element),
            
            lambda: element.click(),
            
            lambda: self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element) or time.sleep(0.5) or element.click(),
            
            lambda: self.driver.execute_script("arguments[0].focus(); arguments[0].click();", element),
            
            lambda: self.driver.execute_script("""
                // Remove any overlay elements that might intercept clicks
                const overlays = document.querySelectorAll('.overlay, .modal, .dialog, [class*="overlay"], [class*="modal"], [class*="dialog"]');
                for (const overlay of overlays) {
                    overlay.style.display = 'none';
                }
                arguments[0].click();
            """, element)
        ]
        
        for i, strategy in enumerate(strategies):
            try:
                strategy()
                time.sleep(wait_time)  # Wait for page to load
                return True
            except (ElementClickInterceptedException, ElementNotInteractableException, StaleElementReferenceException) as e:
                logger.warning(f"Click strategy {i+1} failed: {e}")
                time.sleep(0.5)
            except Exception as e:
                logger.warning(f"Unexpected error in click strategy {i+1}: {e}")
                time.sleep(0.5)
        
        logger.error("All click strategies failed")
        return False
    
    def get_company_cards(self):
        """
        Get company card elements from the company list page.
        
        Returns:
            List of company card elements
        """
        try:
            company_cards = self.driver.execute_script("""
                // Try various selectors for company cards
                const selectors = [
                    '.new-company-wrap li.item',
                    '.company-list .company-item',
                    '.company-card',
                    '.list .item',
                    '.items .item',
                    'li.item',
                    '.item',
                    'li'
                ];
                
                for (const selector of selectors) {
                    const elements = document.querySelectorAll(selector);
                    if (elements.length > 0) {
                        return Array.from(elements);
                    }
                }
                
                // Try to find elements with company-related class names
                const allElements = document.querySelectorAll('*');
                const companyElements = [];
                
                for (const element of allElements) {
                    const className = element.className || '';
                    if (
                        className.includes('company') || 
                        className.includes('item') ||
                        className.includes('card')
                    ) {
                        // Check if it's likely a company card
                        if (
                            element.querySelector('a') && 
                            element.textContent.length < 500
                        ) {
                            companyElements.push(element);
                        }
                    }
                }
                
                return companyElements;
            """)
            
            if company_cards and len(company_cards) > 0:
                logger.info(f"Found {len(company_cards)} company cards using JavaScript")
                return company_cards
        except Exception as e:
            logger.error(f"JavaScript error: {e}")
        
        selectors = [
            '.new-company-wrap li.item',
            '.company-list .company-item',
            '.company-card',
            '.list .item',
            '.items .item',
            'li.item',
            '.item',
            'li'
        ]
        
        for selector in selectors:
            company_cards = self.safe_find_elements(By.CSS_SELECTOR, selector)
            if company_cards and len(company_cards) > 0:
                logger.info(f"Found {len(company_cards)} company cards using selector: {selector}")
                return company_cards
        
        logger.warning("No company cards found")
        return []
    
    def get_company_info(self, company_card):
        """
        Extract company information from a company card.
        
        Args:
            company_card: Company card element to extract information from
            
        Returns:
            Dictionary with company information
        """
        try:
            name_element = self.safe_find_element(By.CSS_SELECTOR, "p.title", company_card)
            if not name_element:
                name_element = self.safe_find_element(By.CSS_SELECTOR, "h3, h4, strong, .name", company_card)
            
            name = name_element.text.strip() if name_element else ""
            
            info_element = self.safe_find_element(By.CSS_SELECTOR, "p.info", company_card)
            if not info_element:
                info_element = self.safe_find_element(By.CSS_SELECTOR, ".info, .description, .detail", company_card)
            
            info_text = info_element.text.strip() if info_element else ""
            
            industry = ""
            size = ""
            
            if info_text:
                parts = [part.strip() for part in info_text.split('|')]
                if len(parts) > 0:
                    industry = parts[0]
                if len(parts) > 1:
                    size = parts[1]
            
            return {
                "name": name,
                "industry": industry,
                "size": size
            }
        except Exception as e:
            logger.error(f"Error extracting company info: {e}")
            return {
                "name": "",
                "industry": "",
                "size": ""
            }
    
    def click_company_card(self, company_card):
        """
        Click on a company card to navigate to the company detail page.
        
        Args:
            company_card: Company card element to click
            
        Returns:
            True if click was successful, False otherwise
        """
        try:
            link_element = self.safe_find_element(By.CSS_SELECTOR, "a", company_card)
            if link_element:
                return self.click_element_safely(link_element)
            
            return self.click_element_safely(company_card)
        except Exception as e:
            logger.error(f"Error clicking company card: {e}")
            return False
    
    def click_internship_tab(self):
        """
        Find and click the internship positions tab.
        
        Returns:
            True if click was successful, False otherwise
        """
        try:
            
            tab_element = self.safe_find_element(By.XPATH, "//*[contains(text(), '见习岗位')]")
            
            if tab_element:
                logger.info(f"Found internship tab: {tab_element.tag_name} with text '{tab_element.text}'")
                return self.click_element_safely(tab_element)
            
            selectors = [
                "//li[contains(@class, 'navItem') and contains(text(), '见习岗位')]",
                "//div[contains(@class, 'tab') and contains(text(), '见习岗位')]",
                "//*[contains(@class, 'tab') and contains(text(), '见习岗位')]"
            ]
            
            for selector in selectors:
                tab_element = self.safe_find_element(By.XPATH, selector)
                if tab_element:
                    logger.info(f"Found internship tab with selector: {selector}")
                    return self.click_element_safely(tab_element)
            
            clicked = self.driver.execute_script("""
                // Try to find and click tab with text '见习岗位'
                const elements = Array.from(document.querySelectorAll('*'));
                for (const element of elements) {
                    if (element.textContent.includes('见习岗位')) {
                        element.click();
                        return true;
                    }
                }
                return false;
            """)
            
            if clicked:
                logger.info("Clicked internship tab using JavaScript")
                time.sleep(3)  # Wait for tab content to load
                return True
            
            logger.warning("Could not find internship tab")
            return False
        
        except Exception as e:
            logger.error(f"Error clicking internship tab: {e}")
            return False
    
    def extract_position_info_from_page(self):
        """
        Extract position information directly from the page without clicking on position cards.
        
        Returns:
            List of position dictionaries with title and description
        """
        try:
            positions = self.driver.execute_script("""
                function extractPositions() {
                    const positions = [];
                    
                    // Try to find position elements
                    const positionElements = document.querySelectorAll('.position-item, .job-item, .position-card, .job-card, li.item, .item');
                    
                    if (positionElements.length > 0) {
                        for (const element of positionElements) {
                            // Extract position title
                            let title = '';
                            const titleElement = element.querySelector('h3, h4, .title, .name, strong');
                            if (titleElement) {
                                title = titleElement.textContent.trim();
                            } else {
                                title = element.textContent.trim().split('\\n')[0];
                            }
                            
                            // Extract position description
                            let description = '';
                            const descElement = element.querySelector('.description, .detail, .info, .content');
                            if (descElement) {
                                description = descElement.textContent.trim();
                            } else {
                                description = element.textContent.trim();
                            }
                            
                            positions.push({
                                title: title,
                                description: description
                            });
                        }
                    } else {
                        // If no position elements found, try to extract from the page content
                        const contentElement = document.querySelector('.content, .main, .container');
                        if (contentElement) {
                            const text = contentElement.textContent.trim();
                            if (text.includes('岗位') || text.includes('职位')) {
                                positions.push({
                                    title: '见习岗位',
                                    description: text
                                });
                            }
                        }
                    }
                    
                    return positions;
                }
                
                return extractPositions();
            """)
            
            if positions and len(positions) > 0:
                logger.info(f"Extracted {len(positions)} positions using JavaScript")
                return positions
            
            logger.warning("No positions found, creating dummy position with page content")
            
            page_content = self.driver.find_element(By.TAG_NAME, "body").text
            
            dummy_position = {
                "position_title": "见习岗位",
                "position_description": page_content
            }
            
            return [dummy_position]
        
        except Exception as e:
            logger.error(f"Error extracting position info from page: {e}")
            return []
    
    def extract_company_description(self):
        """
        Extract company description from the company detail page.
        
        Returns:
            Company description text
        """
        try:
            company_tab_selectors = [
                "//*[contains(text(), '见习单位')]",
                "//*[contains(text(), '公司介绍')]",
                "//*[contains(text(), '企业介绍')]",
                "//*[contains(text(), '单位介绍')]",
                "//*[contains(text(), '公司简介')]",
                "//*[contains(text(), '企业简介')]",
                "//*[contains(text(), '单位简介')]"
            ]
            
            for selector in company_tab_selectors:
                tab_element = self.safe_find_element(By.XPATH, selector)
                if tab_element:
                    logger.info(f"Found company description tab: {tab_element.text}")
                    if self.click_element_safely(tab_element):
                        logger.info("Clicked company description tab")
                        time.sleep(3)  # Wait for tab content to load
                        break
            
            description = self.driver.execute_script("""
                function extractCompanyDescription() {
                    // Try various selectors for company description
                    const selectors = [
                        '.company-description',
                        '.company-info',
                        '.company-detail',
                        '.detail-info',
                        '.introduce',
                        '.description',
                        '.company-detail-info',
                        '.detail-content',
                        '.content',
                        '.info',
                        '.detail'
                    ];
                    
                    for (const selector of selectors) {
                        const element = document.querySelector(selector);
                        if (element && element.textContent.trim()) {
                            return element.textContent.trim();
                        }
                    }
                    
                    // Try to find elements with relevant class names
                    const elements = document.querySelectorAll('div');
                    for (const element of elements) {
                        const className = element.className || '';
                        if (
                            className.includes('company') || 
                            className.includes('detail') || 
                            className.includes('info') || 
                            className.includes('introduce') ||
                            className.includes('content') ||
                            className.includes('description')
                        ) {
                            const text = element.textContent.trim();
                            if (text && text.length > 50) {
                                return text;
                            }
                        }
                    }
                    
                    // Try to find elements with specific text patterns
                    const allElements = document.querySelectorAll('*');
                    for (const element of allElements) {
                        const text = element.textContent.trim();
                        if (
                            text && 
                            text.length > 50 && 
                            (text.includes('公司') || text.includes('企业') || text.includes('单位'))
                        ) {
                            return text;
                        }
                    }
                    
                    // If all else fails, just get the main content of the page
                    const mainContent = document.querySelector('main') || 
                                        document.querySelector('.main') || 
                                        document.querySelector('.content') || 
                                        document.querySelector('.container');
                    
                    if (mainContent) {
                        return mainContent.textContent.trim();
                    }
                    
                    return "";
                }
                
                return extractCompanyDescription();
            """)
            
            if description and len(description) > 20:
                logger.info(f"Extracted company description: {description[:50]}...")
                return description
            
            selectors = [
                '.company-description',
                '.company-info',
                '.company-detail',
                '.detail-info',
                '.introduce',
                '.description',
                '.company-detail-info',
                '.detail-content',
                '.content',
                '.info',
                '.detail'
            ]
            
            for selector in selectors:
                element = self.safe_find_element(By.CSS_SELECTOR, selector)
                if element:
                    description = element.text.strip()
                    if description and len(description) > 20:
                        logger.info(f"Extracted company description: {description[:50]}...")
                        return description
            
            elements = self.safe_find_elements(By.CSS_SELECTOR, 'div[class*="company"], div[class*="detail"], div[class*="info"], div[class*="introduce"], div[class*="content"], div[class*="description"]')
            for element in elements:
                description = element.text.strip()
                if description and len(description) > 50:
                    logger.info(f"Extracted company description: {description[:50]}...")
                    return description
            
            elements = self.safe_find_elements(By.XPATH, "//*[contains(text(), '公司') or contains(text(), '企业') or contains(text(), '单位')]")
            for element in elements:
                description = element.text.strip()
                if description and len(description) > 50:
                    logger.info(f"Extracted company description: {description[:50]}...")
                    return description
            
            page_text = self.driver.find_element(By.TAG_NAME, "body").text
            if page_text and len(page_text) > 100:
                logger.info(f"Extracted company description from page text: {page_text[:50]}...")
                return page_text
            
            logger.warning("No company description found")
            return "No company description found"
        except Exception as e:
            logger.error(f"Error extracting company description: {e}")
            return "Error extracting company description"
    
    def process_company(self, company_idx):
        """
        Process a company by index.
        
        Args:
            company_idx: Index of the company to process
            
        Returns:
            Dictionary with company data and internship positions
        """
        if not self.driver:
            return None
        
        if not self.navigate_to_url(self.base_url):
            logger.error("Failed to navigate to the main page")
            return None
        
        self.save_screenshot("probation_companies_list")
        self.save_page_source("probation_companies_list")
        
        company_cards = self.get_company_cards()
        if not company_cards or company_idx >= len(company_cards):
            logger.error(f"Company index {company_idx} out of range")
            return None
        
        company_card = company_cards[company_idx]
        
        company_info = self.get_company_info(company_card)
        company_name = company_info["name"]
        company_industry = company_info["industry"]
        company_size = company_info["size"]
        
        logger.info(f"Processing company: {company_name}")
        
        if not self.click_company_card(company_card):
            logger.error(f"Failed to click on company card: {company_name}")
            return None
        
        self.save_screenshot(f"company_detail_{company_name.replace(' ', '_')}")
        self.save_page_source(f"company_detail_{company_name.replace(' ', '_')}")
        
        logger.info("Waiting for page to fully load...")
        time.sleep(5)
        
        company_description = self.extract_company_description()
        
        if not self.click_internship_tab():
            logger.warning(f"Failed to click internship tab for company: {company_name}")
            company_data = {
                "company_name": company_name,
                "company_industry": company_industry,
                "company_size": company_size,
                "company_description": company_description,
                "internship_positions": []
            }
            return company_data
        
        screenshot_path = self.save_screenshot(f"internship_positions_{company_name.replace(' ', '_')}")
        page_source_path = self.save_page_source(f"internship_positions_{company_name.replace(' ', '_')}")
        
        position_info = self.extract_position_info_from_page()
        
        positions = []
        for info in position_info:
            position_data = {
                "position_title": info.get("title", ""),
                "position_description": info.get("description", "")
            }
            positions.append(position_data)
        
        company_data = {
            "company_name": company_name,
            "company_industry": company_industry,
            "company_size": company_size,
            "company_description": company_description,
            "internship_positions": positions,
            "debug_info": {
                "screenshot_path": screenshot_path,
                "page_source_path": page_source_path
            }
        }
        
        logger.info(f"Added company data for: {company_name}")
        return company_data
    
    def scrape_internship_positions(self, num_companies=3):
        """
        Scrape internship positions for the specified number of companies.
        
        Args:
            num_companies: Number of companies to process
            
        Returns:
            List of company data dictionaries with internship positions
        """
        logger.info(f"Starting enhanced internship scraper")
        logger.info(f"Scraping internship positions for {num_companies} companies")
        
        self.driver = self.setup_driver()
        if not self.driver:
            logger.error("Failed to initialize WebDriver")
            return []
        
        results = []
        try:
            for i in range(num_companies):
                try:
                    company_data = self.process_company(i)
                    if company_data:
                        results.append(company_data)
                except Exception as e:
                    logger.error(f"Error processing company at index {i}: {e}")
        
        except Exception as e:
            logger.error(f"Error scraping internship positions: {e}")
        
        finally:
            if self.driver:
                self.driver.quit()
                logger.info("WebDriver closed")
        
        self.results = results
        return results
    
    def save_results(self, output_file=None):
        """
        Save the results to a JSON file.
        
        Args:
            output_file: Output file path (if None, a timestamped filename will be used)
            
        Returns:
            Path to the saved file or None if saving failed
        """
        if not self.results:
            logger.error("No results to save")
            return None
        
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"jobonline_internship_positions_{timestamp}.json"
        
        try:
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(self.results, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Successfully scraped internship positions for {len(self.results)} companies")
            logger.info(f"Saved internship positions data to {output_file}")
            
            return output_file
        except Exception as e:
            logger.error(f"Error saving results: {e}")
            return None
    
    def print_summary(self):
        """Print a summary of the scraped data."""
        if not self.results:
            logger.info("No results to summarize")
            return
        
        logger.info("=== Scraping Summary ===")
        logger.info(f"Total companies scraped: {len(self.results)}")
        
        total_positions = 0
        for company_data in self.results:
            company_name = company_data["company_name"]
            company_industry = company_data.get("company_industry", "")
            company_size = company_data.get("company_size", "")
            positions = company_data.get("internship_positions", [])
            
            logger.info(f"Company: {company_name}")
            logger.info(f"Industry: {company_industry}")
            logger.info(f"Size: {company_size}")
            
            if company_data.get("company_description"):
                logger.info(f"Company Description: {company_data['company_description'][:100]}...")
            
            logger.info(f"Number of Internship Positions: {len(positions)}")
            
            for i, position in enumerate(positions):
                logger.info(f"  Position {i+1}: {position.get('position_title', '')}")
                if position.get("position_description"):
                    logger.info(f"  Description: {position['position_description'][:100]}...")
            
            total_positions += len(positions)
            logger.info("---")
        
        logger.info(f"Total positions scraped: {total_positions}")
        logger.info("=== End of Summary ===")

def main():
    """Main function to run the enhanced internship scraper."""
    scraper = EnhancedInternshipScraper(headless=True)
    
    results = scraper.scrape_internship_positions(num_companies=3)
    
    if results:
        output_file = scraper.save_results()
        
        scraper.print_summary()
        
        if output_file:
            try:
                with open(output_file, "r", encoding="utf-8") as f:
                    loaded_data = json.load(f)
                
                if isinstance(loaded_data, list) and len(loaded_data) > 0:
                    logger.info(f"Successfully verified data structure in {output_file}")
                    
                    has_company_descriptions = all("company_description" in company and company["company_description"] for company in loaded_data)
                    logger.info(f"All companies have descriptions: {has_company_descriptions}")
                    
                    total_positions = sum(len(company.get("internship_positions", [])) for company in loaded_data)
                    logger.info(f"Total internship positions found: {total_positions}")
                    
                    has_position_descriptions = all(
                        "position_description" in position and position["position_description"]
                        for company in loaded_data
                        for position in company.get("internship_positions", [])
                    ) if total_positions > 0 else False
                    
                    logger.info(f"All positions have descriptions: {has_position_descriptions}")
                else:
                    logger.error(f"Invalid data structure in {output_file}")
            except Exception as e:
                logger.error(f"Error verifying results: {e}")
    else:
        logger.error("No internship positions were scraped")

if __name__ == "__main__":
    main()

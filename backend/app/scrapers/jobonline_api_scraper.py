"""
JobOnline API Scraper using Selenium to bypass verification.
This scraper targets the specific API endpoint for company information:
https://api.jobonline.cn/jobtbao-es-api/elastic/api/jobjx/jobJxCompanyList
"""
import asyncio
import json
import logging
import os
import time
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any, Union, Tuple

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.support.ui import WebDriverWait
    from webdriver_manager.chrome import ChromeDriverManager
    from selenium.common.exceptions import (
        TimeoutException, 
        NoSuchElementException, 
        StaleElementReferenceException,
        WebDriverException
    )
except ImportError:
    import subprocess
    import sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "selenium", "webdriver-manager"])
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.support.ui import WebDriverWait
    from webdriver_manager.chrome import ChromeDriverManager
    from selenium.common.exceptions import (
        TimeoutException, 
        NoSuchElementException, 
        StaleElementReferenceException,
        WebDriverException
    )

from app.scrapers.base import BaseScraper

logger = logging.getLogger(__name__)

class JobOnlineAPIScraper(BaseScraper):
    """
    Scraper for JobOnline API using Selenium to bypass verification.
    Specifically targets the company information API endpoint.
    """
    
    def __init__(self, headless: bool = True):
        """
        Initialize the JobOnline API Scraper.
        
        Args:
            headless: Whether to run Chrome in headless mode
        """
        super().__init__(name="jobonline_api")
        self.headless = headless
        self.driver = None
        self.api_url = "https://api.jobonline.cn/jobtbao-es-api/elastic/api/jobjx/jobJxCompanyList"
        self.base_url = "https://www.jobonline.cn"
        self.screenshots_dir = "/home/ubuntu/screenshots"
        
        if not os.path.exists(self.screenshots_dir):
            os.makedirs(self.screenshots_dir)
    
    async def initialize(self):
        """Initialize the WebDriver."""
        chrome_version = self._get_chrome_version()
        logger.info(f"Downloading ChromeDriver for Chrome version {chrome_version}")
        
        options = Options()
        if self.headless:
            options.add_argument("--headless=new")  # Use new headless mode
        
        import tempfile
        import random
        import string
        random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        timestamp = int(time.time())
        user_data_dir = os.path.join(
            tempfile.gettempdir(), 
            f"chrome_user_data_{timestamp}_{random_suffix}"
        )
        logger.info(f"Using user data directory: {user_data_dir}")
        options.add_argument(f"--user-data-dir={user_data_dir}")
        
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-infobars")
        options.add_argument("--disable-popup-blocking")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        
        options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36")
        
        try:
            from webdriver_manager.chrome import ChromeDriverManager
            
            try:
                from webdriver_manager.core.utils import ChromeType
                service = Service(ChromeDriverManager(chrome_type=ChromeType.GOOGLE).install())
            except ImportError:
                logger.warning("ChromeType not available, using default ChromeDriverManager")
                service = Service(ChromeDriverManager().install())
            
            self.driver = webdriver.Chrome(service=service, options=options)
            logger.info("Successfully initialized WebDriver with ChromeDriverManager")
        except Exception as e:
            logger.warning(f"Failed to initialize with ChromeDriverManager: {e}")
            
            try:
                chromedriver_paths = [
                    "/usr/local/bin/chromedriver",
                    "/usr/bin/chromedriver",
                    os.path.expanduser("~/chromedriver")
                ]
                
                for driver_path in chromedriver_paths:
                    if os.path.exists(driver_path):
                        logger.info(f"Found chromedriver at {driver_path}")
                        service = Service(driver_path)
                        self.driver = webdriver.Chrome(service=service, options=options)
                        logger.info(f"Successfully initialized WebDriver with {driver_path}")
                        break
                else:
                    raise FileNotFoundError("No chromedriver found in common locations")
            except Exception as e2:
                logger.warning(f"Failed to initialize with explicit path: {e2}")
                
                try:
                    self.driver = webdriver.Chrome(options=options)
                    logger.info("Successfully initialized WebDriver with direct options")
                except Exception as e3:
                    logger.error(f"All initialization methods failed. Last error: {e3}")
        
        if self.driver:
            try:
                self.driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
                    "source": """
                        Object.defineProperty(navigator, 'webdriver', {
                            get: () => undefined
                        });
                    """
                })
                logger.info("Anti-detection script added to WebDriver")
            except Exception as e:
                logger.warning(f"Failed to add anti-detection script: {e}")
            
            self.driver.set_page_load_timeout(30)
            logger.info("Successfully initialized JobOnlineAPIScraper")
            return True
        else:
            logger.error("Failed to initialize WebDriver")
            return False
    
    def _get_chrome_version(self) -> str:
        """Get the Chrome version."""
        try:
            import subprocess
            result = subprocess.check_output(["google-chrome", "--version"]).decode("utf-8")
            version = result.strip().split()[-1]
            return version
        except Exception:
            return "137.0.0.0"  # Default version if unable to detect
    
    async def cleanup(self):
        """Clean up resources."""
        if self.driver:
            self.driver.quit()
            logger.info("Closed WebDriver")
            self.driver = None
    
    def _save_debug_screenshot(self) -> str:
        """
        Save a debug screenshot.
        
        Returns:
            Path to the saved screenshot
        """
        if not self.driver:
            return ""
        
        timestamp = int(time.time())
        filename = f"jobonline_debug_{timestamp}.png"
        filepath = os.path.join(self.screenshots_dir, filename)
        
        try:
            self.driver.save_screenshot(filepath)
            logger.info(f"Saved debug screenshot to {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"Failed to save screenshot: {e}")
            return ""
    
    def _safe_find_element(self, by, value, timeout=10, parent=None):
        """
        Safely find an element with wait.
        
        Args:
            by: By locator strategy
            value: Locator value
            timeout: Wait timeout in seconds
            parent: Parent element to search within
        
        Returns:
            The found element or None
        """
        if not self.driver:
            logger.warning("WebDriver is not initialized")
            return None
            
        try:
            if parent:
                element = WebDriverWait(self.driver, timeout).until(
                    lambda d: parent.find_element(by, value)
                )
            else:
                element = WebDriverWait(self.driver, timeout).until(
                    EC.presence_of_element_located((by, value))
                )
            return element
        except (TimeoutException, NoSuchElementException, StaleElementReferenceException) as e:
            logger.warning(f"Element not found: {by}={value}, Error: {e}")
            return None
    
    def _safe_find_elements(self, by, value, timeout=10, parent=None):
        """
        Safely find elements with wait.
        
        Args:
            by: By locator strategy
            value: Locator value
            timeout: Wait timeout in seconds
            parent: Parent element to search within
        
        Returns:
            List of found elements or empty list
        """
        if not self.driver:
            logger.warning("WebDriver is not initialized")
            return []
            
        try:
            if parent:
                WebDriverWait(self.driver, timeout).until(
                    lambda d: len(parent.find_elements(by, value)) > 0
                )
                return parent.find_elements(by, value)
            else:
                WebDriverWait(self.driver, timeout).until(
                    EC.presence_of_all_elements_located((by, value))
                )
                return self.driver.find_elements(by, value)
        except (TimeoutException, NoSuchElementException, StaleElementReferenceException) as e:
            logger.warning(f"Elements not found: {by}={value}, Error: {e}")
            return []
    
    def _generate_signature(self, params: Dict) -> Tuple[str, Dict]:
        """
        Generate signature for API request based on user's example.
        
        Args:
            params: Request parameters
            
        Returns:
            Generated signature
        """
        import hashlib
        import urllib.parse
        import time
        import random
        import string
        
        timestamp = int(time.time() * 1000)  # Milliseconds
        nonce = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        
        api_key = "jobonline_api_key"  # This would need to be replaced with actual API key
        secret_key = "jobonline_secret_key"  # This would need to be replaced with actual secret key
        
        all_params = {
            "apiKey": api_key,
            "timestamp": timestamp,
            "nonce": nonce,
            **params
        }
        
        encoded = urllib.parse.urlencode(sorted(all_params.items()))
        
        to_sign = f"{encoded}&secretKey={secret_key}"
        
        signature = hashlib.md5(to_sign.encode()).hexdigest().upper()
        
        logger.info(f"Generated signature: {signature} for params: {all_params}")
        
        return signature, all_params
    
    async def _execute_api_request(self, page=1, page_size=20) -> Dict:
        """
        Execute API request using Selenium to bypass verification.
        
        Args:
            page: Page number
            page_size: Number of items per page
        
        Returns:
            API response as dictionary
        """
        try:
            if not self.driver:
                logger.info("WebDriver not initialized, initializing now...")
                await self.initialize()
                
            if not self.driver:
                logger.error("Failed to initialize WebDriver")
                return {"code": -1, "message": "Failed to initialize WebDriver", "data": None}
            
            logger.info(f"Navigating to {self.base_url} to get cookies and session...")
            self.driver.get(self.base_url)
            time.sleep(3)  # Allow time for page to load and set cookies
            
            self._save_debug_screenshot()
            
            payload = {
                "pageNum": page,
                "pageSize": page_size,
                "sortField": "updateTime",
                "sortType": "desc"
            }
            
            signature, all_params = self._generate_signature(payload)
            
            logger.info(f"Executing API request to {self.api_url} with payload: {payload}")
            
            cookies = self.driver.get_cookies()
            cookie_dict = {cookie['name']: cookie['value'] for cookie in cookies}
            cookie_str = '; '.join([f"{name}={value}" for name, value in cookie_dict.items()])
            
            script = f"""
            return new Promise((resolve, reject) => {{
                fetch("{self.api_url}", {{
                    method: "POST",
                    headers: {{
                        "Accept": "application/json, text/plain, */*",
                        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7",
                        "Content-Type": "application/json;charset=UTF-8",
                        "Cookie": "{cookie_str}",
                        "E-CONTENT-PATH": "04b6314a4613eae90fbc6b15c506a9e9e5bd7f5054cd39377b1de7bc117edcf6ab667b90b4dfd78153c10e00d995b21720e2689563dbb8c9ce463763ccbf70d8b296925b2b82afb7b54fa3b36dcce296911ac8fe29a4c96d23d0198292fbdc61e35ea1761341e213949034e3b29558295ceda029928a07f65bea4d172f0ae830d2540e785771d16c24ee07ccc194d334381172c72c5e17fe8032960a2ebc9457e25a676db09683768b4b2b27ba890ba920b94e914669f4c3d0727ca55de4476d6c0fd5c79490a313b4f54d8784f9be2775776c072d1e2d54c52a6f19987f746db70541c6",
                        "E-SIGN": "ba70fbb12bf2f6fb3598a2d471debf4b51a71d4ee226162af7ac327a74a8439c",
                        "E-VERSION": "v2.0.0",
                        "EncryptFlag": "2",
                        "Origin": "https://www.jobonline.cn",
                        "Referer": "https://www.jobonline.cn/",
                        "msha": "1",
                        "platform": "3",
                        "sec-ch-ua": "\\"Chromium\\";v=\\"136\\", \\"Google Chrome\\";v=\\"136\\", \\"Not.A/Brand\\";v=\\"99\\"",
                        "sec-ch-ua-mobile": "?0",
                        "sec-ch-ua-platform": "\\"macOS\\""
                    }},
                    body: JSON.stringify({payload})
                }})
                .then(response => response.json())
                .then(data => resolve(data))
                .catch(error => reject(error));
            }});
            """
            
            monitor_script = """
            return new Promise((resolve, reject) => {
                const originalFetch = window.fetch;
                window.fetch = function(url, options) {
                    if (url.includes('jobJxCompanyList')) {
                        console.log('Intercepted request:', url, options);
                        resolve({url, options});
                    }
                    return originalFetch.apply(this, arguments);
                };
                
                // Trigger a navigation to the page that makes the API request
                window.location.href = 'https://www.jobonline.cn/flagship';
                
                // Set a timeout to restore original fetch and reject if no request is intercepted
                setTimeout(() => {
                    window.fetch = originalFetch;
                    reject('No API request intercepted within timeout');
                }, 10000);
            });
            """
            
            if not self.driver:
                logger.error("WebDriver is None before executing script")
                return {"code": -1, "message": "WebDriver is None", "data": None}
            
            try:
                logger.info("Attempting to monitor network requests to capture actual API call...")
                intercepted = self.driver.execute_script(monitor_script)
                logger.info(f"Intercepted API request: {intercepted}")
                
                if intercepted and isinstance(intercepted, dict):
                    logger.info("Using intercepted request details for API call")
                    options = intercepted.get('options', {})
                    headers = options.get('headers', {})
                    body = options.get('body', '{}')
                    
                    script = f"""
                    return new Promise((resolve, reject) => {{
                        fetch("{self.api_url}", {{
                            method: "POST",
                            headers: {json.dumps(headers)},
                            body: '{body}'
                        }})
                        .then(response => response.json())
                        .then(data => resolve(data))
                        .catch(error => reject(error));
                    }});
                    """
            except Exception as e:
                logger.warning(f"Failed to intercept network requests: {e}")
                
            result = self.driver.execute_script(script)
            logger.info(f"API request executed successfully for page {page}")
            return result
        except Exception as e:
            logger.error(f"Failed to execute API request: {e}")
            self._save_debug_screenshot()
            return {"code": -1, "message": str(e), "data": None}
    
    async def get_companies(self, page=1, page_size=20) -> List[Dict]:
        """
        Get recruitment platforms from JobOnline using direct Selenium approach.
        
        Args:
            page: Page number
            page_size: Number of items per page
        
        Returns:
            List of platform dictionaries
        """
        logger.info(f"Fetching recruitment platforms from JobOnline using Selenium (page {page})...")
        
        try:
            if not self.driver:
                logger.info("WebDriver not initialized, initializing now...")
                await self.initialize()
                
            if not self.driver:
                logger.error("Failed to initialize WebDriver")
                return []
            
            # Navigate to the flagship page which contains recruitment platforms
            platform_url = f"https://www.jobonline.cn/flagship?page={page}"
            logger.info(f"Navigating to {platform_url}...")
            self.driver.get(platform_url)
            
            time.sleep(5)
            self._save_debug_screenshot()
            
            # Based on the browser screenshot, we need to extract recruitment platforms
            logger.info(f"Extracting recruitment platform information from page {page}...")
            
            platform_cards = self._safe_find_elements(By.CSS_SELECTOR, ".flagship-item, .company-card, .enterprise-card")
            
            if not platform_cards:
                logger.warning("No platform cards found with specific classes, trying more general selectors...")
                platform_cards = self._safe_find_elements(By.CSS_SELECTOR, ".main-content > div > div > ul > li")
            
            if not platform_cards:
                logger.warning("No platform cards found with main-content selector, trying direct li selector...")
                platform_cards = self._safe_find_elements(By.CSS_SELECTOR, "li")
            
            if platform_cards:
                logger.info(f"Found {len(platform_cards)} potential platform cards")
                
                platforms = []
                for idx, card in enumerate(platform_cards):
                    try:
                        card_text = card.text
                        if "职位" not in card_text:
                            continue
                        
                        platform_name = ""
                        name_el = self._safe_find_element(By.TAG_NAME, "h3", parent=card)
                        if name_el:
                            platform_name = name_el.text.strip()
                        
                        if not platform_name:
                            continue
                        
                        # Extract industry information
                        industry = "未知"
                        # Try multiple methods to extract industry information
                        industry_el = self._safe_find_element(By.CSS_SELECTOR, ".industry, .company-industry, .tag, .company-tag, .info-tag", parent=card)
                        if industry_el:
                            industry = industry_el.text.strip()
                        
                        if industry == "未知":
                            import re
                            patterns = [
                                r'行业[：:]\s*([^\n]+)',
                                r'所属行业[：:]\s*([^\n]+)',
                                r'类型[：:]\s*([^\n]+)',
                                r'公司类型[：:]\s*([^\n]+)',
                                r'企业类型[：:]\s*([^\n]+)'
                            ]
                            
                            for pattern in patterns:
                                industry_match = re.search(pattern, card_text)
                                if industry_match:
                                    industry = industry_match.group(1).strip()
                                    if industry:
                                        break
                        
                        if industry == "未知":
                            industry_keywords = {
                                "科技": "科技/IT",
                                "软件": "软件/互联网",
                                "互联网": "软件/互联网",
                                "教育": "教育/培训",
                                "培训": "教育/培训",
                                "金融": "金融/银行",
                                "银行": "金融/银行",
                                "保险": "金融/保险",
                                "医疗": "医疗/健康",
                                "健康": "医疗/健康",
                                "制造": "制造业",
                                "电子": "电子/半导体",
                                "半导体": "电子/半导体",
                                "人才": "人力资源",
                                "招聘": "人力资源",
                                "猎头": "人力资源",
                                "人力": "人力资源",
                                "服务": "服务业",
                                "零售": "零售/贸易",
                                "贸易": "零售/贸易",
                                "物流": "物流/运输",
                                "运输": "物流/运输",
                                "建筑": "建筑/房地产",
                                "房地产": "建筑/房地产",
                                "公共": "政府/公共服务",
                                "政府": "政府/公共服务"
                            }
                            
                            for keyword, industry_name in industry_keywords.items():
                                if keyword in platform_name or keyword in card_text:
                                    industry = industry_name
                                    break
                        
                        job_count = 0
                        import re
                        count_match = re.search(r'职位\s*(\d+)', card_text)
                        if count_match:
                            job_count = int(count_match.group(1))
                        
                        platform_id = f"jobonline_{idx}_{page}"
                        
                        platform = {
                            "company_id": platform_id,
                            "company_name": platform_name,
                            "industry": industry,
                            "job_count": job_count,
                            "source": "jobonline",
                            "url": f"https://www.jobonline.cn/company/{platform_id}"
                        }
                        
                        platforms.append(platform)
                        logger.info(f"Extracted platform: {platform_name} with {job_count} jobs in {industry} industry")
                    except Exception as e:
                        logger.error(f"Error extracting platform information from card {idx}: {e}")
                
                if platforms:
                    logger.info(f"Successfully extracted {len(platforms)} platforms from page {page}")
                    return platforms
            
            logger.warning("Failed to extract platforms using Selenium selectors, trying JavaScript...")
            
            # Use JavaScript to extract platform information
            platforms_data = self.driver.execute_script("""
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
                        
                        // Extract industry information
                        let industry = '未知';
                        const industryEl = item.querySelector('.industry, .company-industry, .tag, .company-tag, .info-tag');
                        if (industryEl) {
                            industry = industryEl.textContent.trim();
                        } else {
                            // Try multiple patterns for industry extraction
                            const patterns = [
                                /行业[：:]\\s*([^\\n]+)/,
                                /所属行业[：:]\\s*([^\\n]+)/,
                                /类型[：:]\\s*([^\\n]+)/,
                                /公司类型[：:]\\s*([^\\n]+)/,
                                /企业类型[：:]\\s*([^\\n]+)/
                            ];
                            
                            for (const pattern of patterns) {
                                const match = text.match(pattern);
                                if (match) {
                                    industry = match[1].trim();
                                    if (industry) {
                                        break;
                                    }
                                }
                            }
                            
                            // If still not found, try to infer from company name or text
                            if (industry === '未知') {
                                const industryKeywords = {
                                    "科技": "科技/IT",
                                    "软件": "软件/互联网",
                                    "互联网": "软件/互联网",
                                    "教育": "教育/培训",
                                    "培训": "教育/培训",
                                    "金融": "金融/银行",
                                    "银行": "金融/银行",
                                    "保险": "金融/保险",
                                    "医疗": "医疗/健康",
                                    "健康": "医疗/健康",
                                    "制造": "制造业",
                                    "电子": "电子/半导体",
                                    "半导体": "电子/半导体",
                                    "人才": "人力资源",
                                    "招聘": "人力资源",
                                    "猎头": "人力资源",
                                    "人力": "人力资源",
                                    "服务": "服务业",
                                    "零售": "零售/贸易",
                                    "贸易": "零售/贸易",
                                    "物流": "物流/运输",
                                    "运输": "物流/运输",
                                    "建筑": "建筑/房地产",
                                    "房地产": "建筑/房地产",
                                    "公共": "政府/公共服务",
                                    "政府": "政府/公共服务"
                                };
                                
                                const name = item.querySelector('h3') ? item.querySelector('h3').textContent.trim() : '';
                                
                                for (const [keyword, industryName] of Object.entries(industryKeywords)) {
                                    if (name.includes(keyword) || text.includes(keyword)) {
                                        industry = industryName;
                                        break;
                                    }
                                }
                            }
                        }
                        
                        // Extract job count
                        let jobCount = 0;
                        const countMatch = text.match(/职位\\s*(\\d+)/);
                        if (countMatch) {
                            jobCount = parseInt(countMatch[1]);
                        }
                        
                        platforms.push({
                            id: `platform_${index}_${arguments[0]}`,
                            name: name,
                            industry: industry,
                            jobCount: jobCount,
                            text: text.substring(0, 100) + '...'
                        });
                    }
                });
                
                return platforms;
            """, page)
            
            if platforms_data and len(platforms_data) > 0:
                logger.info(f"Found {len(platforms_data)} platforms via JavaScript on page {page}")
                
                platforms = []
                for platform in platforms_data:
                    platforms.append({
                        "company_id": platform.get('id', ''),
                        "company_name": platform.get('name', ''),
                        "industry": platform.get('industry', '未知'),
                        "job_count": platform.get('jobCount', 0),
                        "source": "jobonline",
                        "url": f"https://www.jobonline.cn/company/{platform.get('id', '')}"
                    })
                
                logger.info(f"Successfully extracted {len(platforms)} platforms via JavaScript from page {page}")
                return platforms
            
            logger.warning("All extraction methods failed, saving page source for debugging...")
            page_source = self.driver.page_source
            with open(f"jobonline_page_source_page{page}_{int(time.time())}.html", "w", encoding="utf-8") as f:
                f.write(page_source)
            logger.info(f"Saved page source to jobonline_page_source_page{page}_{int(time.time())}.html")
            
            logger.info("Trying text pattern matching as last resort...")
            
            job_elements = self._safe_find_elements(By.XPATH, "//*[contains(text(), '职位')]")
            
            if job_elements:
                logger.info(f"Found {len(job_elements)} elements with '职位' text on page {page}")
                
                platforms = []
                for idx, element in enumerate(job_elements):
                    try:
                        parent_li = self.driver.execute_script("""
                            let el = arguments[0];
                            while (el && el.tagName !== 'LI') {
                                el = el.parentElement;
                            }
                            return el;
                        """, element)
                        
                        if not parent_li:
                            continue
                        
                        platform_name = ""
                        name_el = self._safe_find_element(By.TAG_NAME, "h3", parent=parent_li)
                        if name_el:
                            platform_name = name_el.text.strip()
                        
                        # Extract industry information
                        industry = "未知"
                        industry_el = self._safe_find_element(By.CSS_SELECTOR, ".industry, .company-industry, .tag, .company-tag, .info-tag", parent=parent_li)
                        if industry_el:
                            industry = industry_el.text.strip()
                        
                        if industry == "未知":
                            parent_text = parent_li.text
                            import re
                            patterns = [
                                r'行业[：:]\s*([^\n]+)',
                                r'所属行业[：:]\s*([^\n]+)',
                                r'类型[：:]\s*([^\n]+)',
                                r'公司类型[：:]\s*([^\n]+)',
                                r'企业类型[：:]\s*([^\n]+)'
                            ]
                            
                            for pattern in patterns:
                                industry_match = re.search(pattern, parent_text)
                                if industry_match:
                                    industry = industry_match.group(1).strip()
                                    if industry:
                                        break
                        
                        if industry == "未知":
                            platform_name = name_el.text.strip() if name_el else ""
                            industry_keywords = {
                                "科技": "科技/IT",
                                "软件": "软件/互联网",
                                "互联网": "软件/互联网",
                                "教育": "教育/培训",
                                "培训": "教育/培训",
                                "金融": "金融/银行",
                                "银行": "金融/银行",
                                "保险": "金融/保险",
                                "医疗": "医疗/健康",
                                "健康": "医疗/健康",
                                "制造": "制造业",
                                "电子": "电子/半导体",
                                "半导体": "电子/半导体",
                                "人才": "人力资源",
                                "招聘": "人力资源",
                                "猎头": "人力资源",
                                "人力": "人力资源",
                                "服务": "服务业",
                                "零售": "零售/贸易",
                                "贸易": "零售/贸易",
                                "物流": "物流/运输",
                                "运输": "物流/运输",
                                "建筑": "建筑/房地产",
                                "房地产": "建筑/房地产",
                                "公共": "政府/公共服务",
                                "政府": "政府/公共服务"
                            }
                            
                            for keyword, industry_name in industry_keywords.items():
                                if platform_name and keyword in platform_name or keyword in parent_text:
                                    industry = industry_name
                                    break
                        
                        job_count = 0
                        job_text = element.text.strip()
                        import re
                        count_match = re.search(r'(\d+)', job_text)
                        if count_match:
                            job_count = int(count_match.group(1))
                        
                        if platform_name:
                            platforms.append({
                                "company_id": f"jobonline_text_{idx}_{page}",
                                "company_name": platform_name,
                                "industry": industry,
                                "job_count": job_count,
                                "source": "jobonline",
                                "url": f"https://www.jobonline.cn/company/jobonline_text_{idx}_{page}"
                            })
                    except Exception as e:
                        logger.error(f"Error extracting platform from job element {idx}: {e}")
                
                if platforms:
                    logger.info(f"Successfully extracted {len(platforms)} platforms using text pattern matching from page {page}")
                    return platforms
            
            logger.error(f"Failed to extract any platform information from page {page}")
            return []
        except Exception as e:
            logger.error(f"Error fetching platforms from page {page}: {e}")
            self._save_debug_screenshot()
            return []
    
    async def get_jobs(self, company_id=None, page=1, page_size=20) -> List[Dict]:
        """
        Get jobs for a specific company.
        
        Args:
            company_id: Company ID
            page: Page number
            page_size: Number of items per page
        
        Returns:
            List of job dictionaries
        """
        logger.info(f"Fetching jobs for company_id={company_id}, page {page}...")
        
        if not company_id:
            logger.error("Company ID is required to fetch jobs")
            return []
        
        return []
    
    def get_job_listings(self, page=1, page_size=20, max_pages=5) -> List[Dict]:
        """
        Get job listings (BaseScraper interface method).
        
        Args:
            page: Starting page number
            page_size: Number of items per page
            max_pages: Maximum number of pages to scrape
        
        Returns:
            List of job dictionaries
        """
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            all_companies = []
            
            for current_page in range(page, page + max_pages):
                logger.info(f"Fetching page {current_page} of companies...")
                companies = loop.run_until_complete(self.get_companies(page=current_page, page_size=page_size))
                
                if not companies:
                    logger.info(f"No more companies found on page {current_page}, stopping pagination")
                    break
                
                all_companies.extend(companies)
                logger.info(f"Total companies collected so far: {len(all_companies)}")
                
                time.sleep(2)
            
            return all_companies
        finally:
            loop.close()
    
    def get_job_details(self, job_url: str) -> Dict:
        """
        Get job details (BaseScraper interface method).
        
        Args:
            job_url: URL of the job
        
        Returns:
            Job details dictionary
        """
        return {}

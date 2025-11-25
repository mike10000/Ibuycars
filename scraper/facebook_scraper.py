"""
Facebook Marketplace scraper for used cars
Note: Facebook Marketplace requires JavaScript, so this is a basic implementation
"""
from typing import List, Optional
from scraper.base_scraper import BaseScraper, CarListing
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import re


class FacebookScraper(BaseScraper):
    """Scraper for Facebook Marketplace car listings"""
    
    def __init__(self):
        super().__init__("Facebook Marketplace")
        self.base_url = "https://www.facebook.com/marketplace"
        self.driver = None
    
    def _setup_driver(self):
        """Setup Selenium WebDriver"""
        if self.driver:
            return
        
        chrome_options = Options()
        chrome_options.add_argument('--headless')  # Run in background
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument(f'user-agent={self.ua.random}')
        
        try:
            # Try with webdriver-manager first
            from selenium.webdriver.chrome.service import Service
            from webdriver_manager.chrome import ChromeDriverManager
            
            driver_path = ChromeDriverManager().install()
            service = Service(driver_path)
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
        except Exception as e:
            # Try without webdriver-manager (if ChromeDriver is in PATH)
            try:
                self.driver = webdriver.Chrome(options=chrome_options)
            except:
                # Silently fail
                self.driver = None
    
    def search(self, makes: List[str], model: Optional[str] = None, year_min: Optional[int] = None,
               year_max: Optional[int] = None, price_min: Optional[int] = None,
               price_max: Optional[int] = None, location: Optional[str] = None,
               max_results: int = 20, private_sellers_only: bool = False) -> List[CarListing]:
        """Search Facebook Marketplace for cars"""
        all_listings = []
        
        # Facebook Marketplace requires login and has complex structure
        # This is a simplified version that may need adjustments
        self._setup_driver()
        
        if not self.driver:
            print("Selenium driver not available. Skipping Facebook Marketplace.")
            return all_listings
        
        # Search for each make
        for make in makes:
            try:
                # Build search query
                query = make
                if model:
                    query += f" {model}"
                if year_min:
                    query += f" {year_min}"
                
                
                # Navigate to marketplace with location
                # Facebook Marketplace URL structure: /marketplace/LOCATION/search
                # Category 807311116002614 is for vehicles
                search_url = f"{self.base_url}/category/vehicles"
                
                # Add location if provided
                if location:
                    # Try to extract city/state or use as-is
                    location_clean = location.replace(',', '').replace(' ', '-').lower()
                    search_url = f"{self.base_url}/{location_clean}/search"
                else:
                    search_url = f"{self.base_url}/search"
                
                # Add query parameter
                search_url += f"?query={query.replace(' ', '%20')}"
                
                # Add category for vehicles
                search_url += "&category=vehicles"
                
                if price_min:
                    search_url += f"&minPrice={price_min}"
                if price_max:
                    search_url += f"&maxPrice={price_max}"
                
                self.driver.get(search_url)
                time.sleep(3)  # Wait for page to load
                
                # Find listings
                # Note: Facebook's structure changes frequently, so selectors may need updates
                try:
                    listing_elements = WebDriverWait(self.driver, 10).until(
                        EC.presence_of_all_elements_located((By.CSS_SELECTOR, 
                            '[data-testid="marketplace-search-result-item"]'))
                    )
                except:
                    # Try alternative selectors
                    listing_elements = self.driver.find_elements(By.CSS_SELECTOR, 
                        'a[href*="/marketplace/item/"]')
                
                for elem in listing_elements[:max_results]:
                    try:
                        # Extract title
                        title = ""
                        title_elem = elem.find_element(By.CSS_SELECTOR, 
                            'span[dir="auto"]')
                        if title_elem:
                            title = self.clean_text(title_elem.text)
                        
                        # Extract URL
                        url = elem.get_attribute('href') or ""
                        
                        # Extract price
                        price = "N/A"
                        try:
                            price_elem = elem.find_element(By.CSS_SELECTOR, 
                                'span[dir="auto"]:last-child')
                            if price_elem:
                                price_text = price_elem.text
                                if '$' in price_text:
                                    price = self.clean_price(price_text)
                        except:
                            pass
                        
                        # Extract location
                        location_text = location or "N/A"
                        try:
                            loc_elem = elem.find_element(By.CSS_SELECTOR, 
                                'span[class*="location"]')
                            if loc_elem:
                                location_text = self.clean_text(loc_elem.text)
                        except:
                            pass
                        
                        
                        # Extract year from title
                        year = ""
                        year_match = re.search(r'\b(19|20)\d{2}\b', title)
                        if year_match:
                            year = year_match.group()
                        
                        # Extract image
                        image_url = ""
                        try:
                            # Try to find image element
                            img_elem = elem.find_element(By.TAG_NAME, 'img')
                            if img_elem:
                                image_url = img_elem.get_attribute('src') or ""
                        except:
                            pass
                        
                        if title and url:
                            listing = CarListing(
                                title=title,
                                price=price,
                                location=location_text,
                                url=url,
                                source=self.source_name,
                                year=year,
                                image_url=image_url
                            )
                            all_listings.append(listing)
                            
                    except Exception as e:
                        print(f"Error parsing Facebook listing: {e}")
                        continue
                        
            except Exception as e:
                print(f"Error scraping Facebook Marketplace for {make}: {e}")
                continue
        
        if self.driver:
            self.driver.quit()
            self.driver = None
        
        return all_listings

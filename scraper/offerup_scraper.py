"""
OfferUp scraper for used cars
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
from bs4 import BeautifulSoup
import re
import time


class OfferUpScraper(BaseScraper):
    """Scraper for OfferUp car listings"""
    
    def __init__(self, use_selenium: bool = True, headless: bool = True, debug: bool = False):
        super().__init__("OfferUp")
        self.base_url = "https://offerup.com/explore/k/cars-trucks"
        self.use_selenium = use_selenium
        self.headless = headless
        self.debug = debug
        self.driver = None
    
    def _zip_to_lat_lon(self, zip_code: str) -> tuple:
        """
        Convert ZIP code to latitude/longitude coordinates.
        Uses a simplified mapping for common ZIP codes.
        For production, consider using geopy or a geocoding API.
        """
        # Basic ZIP code ranges to lat/lon mapping
        zip_map = {
            # Florida
            range(32000, 35000): (27.9944, -81.7603),  # Central Florida
            # New Jersey
            range(7000, 9000): (40.0583, -74.4057),  # New Jersey
            # New York
            range(10000, 15000): (40.7128, -74.0060),  # New York
            # California (LA)
            range(90000, 97000): (34.0522, -118.2437),  # Los Angeles
            # Texas
            range(75000, 80000): (32.7767, -96.7970),  # Dallas
            # Illinois
            range(60000, 63000): (41.8781, -87.6298),  # Chicago
        }
        
        try:
            zip_int = int(zip_code)
            for zip_range, coords in zip_map.items():
                if zip_int in zip_range:
                    return coords
        except ValueError:
            pass
        
        # Default to central US if ZIP not found
        return (39.8283, -98.5795)
    
    def _setup_driver(self):
        """Setup Selenium WebDriver"""
        if self.driver:
            return
        
        chrome_options = Options()
        if self.headless:
            chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument(f'user-agent={self.ua.random}')
        chrome_options.add_argument('--window-size=1920,1080')
        
        try:
            driver_path = ChromeDriverManager().install()
            service = Service(driver_path)
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
        except Exception as e:
            print(f"  Error setting up WebDriver for OfferUp: {e}")
            self.driver = None
    
    def search(self, makes: List[str], model: Optional[str] = None, year_min: Optional[int] = None,
               year_max: Optional[int] = None, price_min: Optional[int] = None,
               price_max: Optional[int] = None, location: Optional[str] = None,
               max_results: int = 20, private_sellers_only: bool = False) -> List[CarListing]:
        """Search OfferUp for cars"""
        all_listings = []
        
        # Default location if not provided
        if not location:
            location = "33410"  # Default to Palm Beach Gardens, FL
        
        # Convert ZIP code to lat/lon
        lat, lon = self._zip_to_lat_lon(location)
        
        # Default distance
        distance = 25
        
        # Build search query
        search_query = " ".join(makes)
        if model:
            search_query += f" {model}"
        if year_min:
            search_query += f" {year_min}"
        
        # Build URL with parameters
        params = {
            'distance': distance,
            'lat': lat,
            'lon': lon,
            'delivery_param': 'p'
        }
        
        # Add search query if we have make/model
        if search_query.strip():
            # Modify URL to include search - OfferUp uses /explore/s/ for searches
            url = f"https://offerup.com/explore/s/cars-trucks/{search_query.strip()}"
        else:
            url = self.base_url
        
        # Use Selenium to handle JavaScript-rendered content
        if self.use_selenium:
            try:
                self._setup_driver()
                if self.driver:
                    listings = self._search_with_selenium(url, params, max_results, price_min, price_max)
                    all_listings.extend(listings)
            except Exception as e:
                print(f"  OfferUp Selenium search failed: {e}")
        
        return all_listings
    
    def _search_with_selenium(self, url: str, params: dict, max_results: int,
                            price_min: Optional[int] = None, 
                            price_max: Optional[int] = None) -> List[CarListing]:
        """Search using Selenium for JavaScript-rendered content"""
        listings = []
        
        try:
            # Build full URL with params
            from urllib.parse import urlencode
            full_url = f"{url}?{urlencode(params)}"
            
            self.driver.get(full_url)
            if self.debug:
                print(f"  OfferUp: Navigating to {full_url}")
            time.sleep(3)  # Wait for page to load
            
            # Wait for listings to appear
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, 'a'))
                )
            except:
                pass  # Continue even if timeout
            
            # Scroll to load more items
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
            time.sleep(1)
            
            # Get page source and parse
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'lxml')
            
            if self.debug:
                print(f"  OfferUp: Page title: {self.driver.title}")
                print(f"  OfferUp: Page source length: {len(page_source)} chars")
            
            # Find all car listing links
            # OfferUp uses anchor tags with specific patterns
            all_links = soup.find_all('a', href=re.compile(r'/item/'))
            
            for link in all_links[:max_results]:
                try:
                    # Get the href
                    href = link.get('href', '')
                    if not href or '/item/' not in href:
                        continue
                    
                    # Build full URL
                    if href.startswith('/'):
                        url_full = f"https://offerup.com{href}"
                    else:
                        url_full = href
                    
                    # Extract title - usually in a span within the link
                    title_elem = link.find('span')
                    title = ""
                    if title_elem:
                        title = self.clean_text(title_elem.get_text())
                    
                    # If no title found, try getting all text from link
                    if not title or len(title) < 3:
                        title = self.clean_text(link.get_text())
                    
                    # Skip if title doesn't look like a car listing
                    if not title or len(title) < 5:
                        continue
                    
                    # Find parent container for additional details
                    container = link.find_parent(['div', 'li', 'article'])
                    
                    # Extract price
                    price = "N/A"
                    if container:
                        # Look for price pattern
                        price_text = container.find(string=re.compile(r'\$[\d,]+'))
                        if price_text:
                            price = self.clean_price(price_text)
                    
                    # Apply price filters
                    if price != "N/A" and (price_min or price_max):
                        try:
                            price_num = int(price.replace('$', '').replace(',', ''))
                            if price_min and price_num < price_min:
                                continue
                            if price_max and price_num > price_max:
                                continue
                        except:
                            pass
                    
                    # Extract location
                    location_text = "N/A"
                    if container:
                        # Look for location patterns (usually city, state)
                        loc_match = re.search(r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*,\s*[A-Z]{2})', container.get_text())
                        if loc_match:
                            location_text = loc_match.group(1)
                    
                    # Extract year from title
                    year = ""
                    year_match = re.search(r'\b(19|20)\d{2}\b', title)
                    if year_match:
                        year = year_match.group()
                    
                    # Extract mileage
                    mileage = ""
                    if container:
                        mileage_match = re.search(r'(\d+k?\s*miles?)', container.get_text(), re.IGNORECASE)
                        if mileage_match:
                            mileage = mileage_match.group(1)
                    
                    # Extract image
                    image_url = ""
                    img = link.find('img')
                    if img:
                        image_url = img.get('src', '') or img.get('data-src', '')
                    
                    listing = CarListing(
                        title=title,
                        price=price,
                        location=location_text,
                        url=url_full,
                        source=self.source_name,
                        year=year,
                        mileage=mileage,
                        image_url=image_url
                    )
                    listings.append(listing)
                    
                except Exception as e:
                    print(f"  Error parsing OfferUp listing: {e}")
                    continue
                    
        except Exception as e:
            print(f"  Error in OfferUp Selenium search: {e}")
        finally:
            if self.driver:
                self.driver.quit()
                self.driver = None
        
        return listings

"""
Cars.com scraper for used cars (private sellers)
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


class CarsComScraper(BaseScraper):
    """Scraper for Cars.com private seller listings"""
    
    def __init__(self, use_selenium: bool = True):
        super().__init__("Cars.com")
        self.base_url = "https://www.cars.com/shopping/results"
        self.use_selenium = use_selenium
        self.driver = None
    
    def _setup_driver(self):
        """Setup Selenium WebDriver"""
        if self.driver:
            return
        
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument(f'user-agent={self.ua.random}')
        
        try:
            # Try with webdriver-manager first
            driver_path = ChromeDriverManager().install()
            service = Service(driver_path)
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
        except Exception as e:
            # Try without webdriver-manager (if ChromeDriver is in PATH)
            try:
                self.driver = webdriver.Chrome(options=chrome_options)
            except:
                # Silently fail - will use regular scraping
                self.driver = None
    
    def search(self, makes: List[str], model: Optional[str] = None, year_min: Optional[int] = None,
               year_max: Optional[int] = None, price_min: Optional[int] = None,
               price_max: Optional[int] = None, location: Optional[str] = None,
               max_results: int = 20, private_sellers_only: bool = False) -> List[CarListing]:
        """Search Cars.com for cars"""
        all_listings = []
        
        # Search for each make
        for make in makes:
            # Build search parameters
            params = {
                'makes[]': make,
                'list_price_max': price_max or '',
                'list_price_min': price_min or '',
                'seller_type': 'private' if private_sellers_only else 'all',
                'sort': 'relevance',
                'page_size': min(max_results, 100)
            }
            
            if model:
                params['models[]'] = f"{make}|{model}"
            
            if year_min:
                params['year_min'] = year_min
            if year_max:
                params['year_max'] = year_max
            
            if location:
                # Try to extract ZIP code
                zip_match = re.search(r'\b\d{5}\b', location)
                if zip_match:
                    params['zip'] = zip_match.group()
            
            # Use Selenium for JavaScript-rendered content
            listings = []
            if self.use_selenium:
                try:
                    self._setup_driver()
                    if self.driver:
                        listings = self._search_with_selenium(params, max_results)
                        if listings:
                            all_listings.extend(listings)
                            continue
                except Exception as e:
                    print(f"  Selenium search failed, trying regular method: {e}")
            
            # Fallback to regular scraping
            soup = self.get_page(self.base_url, params)
            if not soup:
                continue
            
            # Find listings - Cars.com uses specific class names
            results = soup.find_all('div', class_=re.compile(r'vehicle-card|listing|result'))
            
            if not results:
                # Try alternative selectors
                results = soup.find_all('div', {'data-qa': re.compile(r'vehicle-card')})
            
            if not results:
                # Try finding vehicle links
                results = soup.find_all('a', href=re.compile(r'/vehicledetail/|/shopping/results/'))
                results = [r.find_parent('div') for r in results if r and r.find_parent('div')]
            
            # Debug: print what we found
            if not results:
                print(f"  Debug: No listings found on Cars.com. Page title: {soup.title.string if soup.title else 'N/A'}")
            
            for result in results[:max_results]:
                try:
                    # Extract title
                    title_elem = result.find(['a', 'h2', 'h3'], class_=re.compile(r'title|heading|name|link'))
                    if not title_elem:
                        continue
                    
                    title = self.clean_text(title_elem.get_text())
                    
                    # Extract URL
                    url = title_elem.get('href', '')
                    if url and not url.startswith('http'):
                        url = f"https://www.cars.com{url}"
                    
                    # Extract price
                    price_elem = result.find(['span', 'div'], class_=re.compile(r'price|primary-price|cost'))
                    price = "N/A"
                    if price_elem:
                        price = self.clean_price(price_elem.get_text())
                    
                    # Extract location
                    location_elem = result.find(['span', 'div'], class_=re.compile(r'location|dealer-name|distance'))
                    location_text = location or "N/A"
                    if location_elem:
                        location_text = self.clean_text(location_elem.get_text())
                    
                    # Extract year from title
                    year = ""
                    year_match = re.search(r'\b(19|20)\d{2}\b', title)
                    if year_match:
                        year = year_match.group()
                    
                    # Extract mileage
                    mileage_elem = result.find(['span', 'div'], class_=re.compile(r'mileage|miles|odometer'))
                    mileage = ""
                    if mileage_elem:
                        mileage = self.clean_text(mileage_elem.get_text())
                    
                    # Extract image
                    image_elem = result.find('img')
                    image_url = ""
                    if image_elem:
                        image_url = image_elem.get('src', '') or image_elem.get('data-src', '')
                    
                    listing = CarListing(
                        title=title,
                        price=price,
                        location=location_text,
                        url=url,
                        source=self.source_name,
                        year=year,
                        mileage=mileage,
                        image_url=image_url
                    )
                    all_listings.append(listing)
                    
                except Exception as e:
                    print(f"Error parsing Cars.com listing: {e}")
                    continue
        
        return all_listings
    
    def _search_with_selenium(self, params: dict, max_results: int) -> List[CarListing]:
        """Search using Selenium for JavaScript-rendered content"""
        listings = []
        
        try:
            from urllib.parse import urlencode
            full_url = f"{self.base_url}?{urlencode(params)}"
            
            self.driver.get(full_url)
            time.sleep(3)  # Wait for page to load
            
            # Wait for listings to appear
            try:
                WebDriverWait(self.driver, 15).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 
                        '[data-qa*="vehicle"], .vehicle-card, a[href*="/vehicledetail/"]'))
                )
            except:
                pass  # Continue even if timeout
            
            # Scroll to load more content
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            
            # Get page source and parse
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'lxml')
            
            # Find listings
            results = soup.find_all('div', class_=re.compile(r'vehicle-card|listing'))
            
            if not results:
                results = soup.find_all('div', {'data-qa': re.compile(r'vehicle-card')})
            
            if not results:
                results = soup.find_all('a', href=re.compile(r'/vehicledetail/'))
                results = [r.find_parent('div') for r in results if r and r.find_parent('div')]
            
            for result in results[:max_results]:
                try:
                    title_elem = result.find(['a', 'h2', 'h3'], class_=re.compile(r'title|heading|name|link'))
                    if not title_elem:
                        continue
                    
                    title = self.clean_text(title_elem.get_text())
                    url = title_elem.get('href', '')
                    if url and not url.startswith('http'):
                        url = f"https://www.cars.com{url}"
                    
                    price_elem = result.find(['span', 'div'], class_=re.compile(r'price|primary-price|cost'))
                    price = "N/A"
                    if price_elem:
                        price = self.clean_price(price_elem.get_text())
                    
                    location_elem = result.find(['span', 'div'], class_=re.compile(r'location|dealer-name|distance'))
                    location_text = "N/A"
                    if location_elem:
                        location_text = self.clean_text(location_elem.get_text())
                    
                    year = ""
                    year_match = re.search(r'\b(19|20)\d{2}\b', title)
                    if year_match:
                        year = year_match.group()
                    
                    mileage_elem = result.find(['span', 'div'], class_=re.compile(r'mileage|miles|odometer'))
                    mileage = ""
                    if mileage_elem:
                        mileage = self.clean_text(mileage_elem.get_text())
                    
                    image_elem = result.find('img')
                    image_url = ""
                    if image_elem:
                        image_url = image_elem.get('src', '') or image_elem.get('data-src', '')
                    
                    listing = CarListing(
                        title=title,
                        price=price,
                        location=location_text,
                        url=url,
                        source=self.source_name,
                        year=year,
                        mileage=mileage,
                        image_url=image_url
                    )
                    listings.append(listing)
                    
                except Exception as e:
                    print(f"  Error parsing Cars.com listing (Selenium): {e}")
                    continue
                    
        except Exception as e:
            print(f"  Error in Selenium search: {e}")
        finally:
            if self.driver:
                self.driver.quit()
                self.driver = None
        
        return listings


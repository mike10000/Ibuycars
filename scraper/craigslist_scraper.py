"""
Craigslist scraper for used cars
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


class CraigslistScraper(BaseScraper):
    """Scraper for Craigslist car listings"""
    
    def __init__(self, use_selenium: bool = True):
        super().__init__("Craigslist")
        self.base_url_all = "https://{location}.craigslist.org/search/cta"
        self.base_url_owner = "https://{location}.craigslist.org/search/cto"
        self.use_selenium = use_selenium
        self.driver = None
        # Common location mappings
        self.location_map = {
            'new jersey': 'newjersey',
            'new york': 'newyork',
            'los angeles': 'losangeles',
            'san francisco': 'sfbay',
            'san diego': 'sandiego',
            'chicago': 'chicago',
            'houston': 'houston',
            'phoenix': 'phoenix',
            'philadelphia': 'philadelphia',
            'dallas': 'dallas',
            'austin': 'austin',
            'seattle': 'seattle',
            'boston': 'boston',
            'miami': 'miami',
            'atlanta': 'atlanta',
            'denver': 'denver',
            'detroit': 'detroit',
            'minneapolis': 'minneapolis',
            'portland': 'portland',
            'sacramento': 'sacramento',
        }
    
    def _normalize_location(self, location: str) -> str:
        """Convert location name to Craigslist location code"""
        if not location:
            return "sfbay"
        
        location_lower = location.lower().strip()
        
        # Check if it's a ZIP code FIRST (before other checks)
        # Remove spaces and dashes to check
        normalized = location_lower.replace(' ', '').replace('-', '')
        if normalized.isdigit() and len(normalized) == 5:
            # Map ZIP codes to approximate locations
            zip_code = int(normalized)
            # Florida ZIP codes (33922 is Fort Myers, FL)
            if 32000 <= zip_code <= 34999:
                return "miami"  # Florida
            # New Jersey ZIP codes
            elif 7000 <= zip_code <= 8999:
                return "newjersey"
            # New York ZIP codes
            elif 10000 <= zip_code <= 14999:
                return "newyork"
            # California ZIP codes
            elif 90000 <= zip_code <= 96999:
                return "losangeles"
            # Texas ZIP codes
            elif 75000 <= zip_code <= 79999:
                return "dallas"
            # Default to a major city
            else:
                return "sfbay"
        
        # Try to map common names
        if location_lower in self.location_map:
            return self.location_map[location_lower]
        
        # Check if it's already a valid code (no spaces, lowercase, not all digits)
        if ' ' not in location_lower and location_lower.isalnum() and not location_lower.isdigit():
            return location_lower
        
        # Return normalized version
        return normalized
    
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
            from webdriver_manager.chrome import ChromeDriverManager
            
            # Clear cache and re-download if there's an issue
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
        """Search Craigslist for cars"""
        all_listings = []
        
        # Normalize location
        location_code = self._normalize_location(location)
        
        # Search for each make
        for make in makes:
            # Build search query
            query = make
            if model:
                query += f" {model}"
            if year_min:
                query += f" {year_min}"
            
            # Build URL
            base_url = self.base_url_owner if private_sellers_only else self.base_url_all
            url = base_url.format(location=location_code)
            params = {
                'query': query,
                'sort': 'rel'
            }
            
            if price_min:
                params['min_price'] = price_min
            if price_max:
                params['max_price'] = price_max
            
            # Try Selenium first if enabled
            listings = []
            if self.use_selenium:
                try:
                    self._setup_driver()
                    if self.driver:
                        listings = self._search_with_selenium(url, params, location_code, max_results)
                        if listings:
                            all_listings.extend(listings)
                            continue
                except Exception as e:
                    print(f"  Selenium search failed, trying regular method: {e}")
            
            # Fallback to regular scraping
            soup = self.get_page(url, params)
            if not soup:
                continue
            
            # Find all listings - prioritize finding links directly as structure varies
            # Look for owner (/cto/) and dealer (/ctd/) links
            listing_links = soup.find_all('a', href=re.compile(r'/cto/|/ctd/'))
            
            # Deduplicate by URL
            seen_urls = set()
            unique_links = []
            for link in listing_links:
                href = link.get('href')
                if href and href not in seen_urls:
                    seen_urls.add(href)
                    unique_links.append(link)
            
            results = unique_links
            
            for link_elem in results[:max_results]:
                try:
                    # The link itself usually contains the title or is the main entry point
                    title_elem = link_elem
                    
                    # Get parent container to find other details like price
                    container = link_elem.find_parent(['li', 'div', 'p'])
                    
                    title = self.clean_text(title_elem.get_text())
                    # If title is empty/short, it might be an image link, try to find a sibling link or text
                    if len(title) < 3 and container:
                        # Try to find another link in the container that might be the title
                        other_link = container.find('a', string=lambda text: text and len(text) > 5)
                        if other_link:
                            title = self.clean_text(other_link.get_text())
                        else:
                            # Try to find text directly in container
                            title = self.clean_text(container.get_text())
                            # Truncate if too long (it might be the whole card text)
                            if len(title) > 100:
                                title = title[:100] + "..."

                    relative_url = title_elem.get('href', '')
                    
                    if relative_url.startswith('//'):
                        url_full = 'https:' + relative_url
                    elif relative_url.startswith('/'):
                        url_full = f"https://{location_code}.craigslist.org{relative_url}"
                    else:
                        url_full = relative_url
                    
                    # Extract price - look in container
                    price = "N/A"
                    if container:
                        price_elem = container.find(string=re.compile(r'\$[\d,]+'))
                        if price_elem:
                            price = self.clean_price(price_elem)
                        else:
                            # Try specific classes if generic text search fails
                            price_elem = container.find(class_=re.compile(r'price|amount'))
                            if price_elem:
                                price = self.clean_price(price_elem.get_text())

                    # Extract location
                    location_text = "N/A"
                    if container:
                        # Try to find location in parens or specific class
                        loc_elem = container.find(class_=re.compile(r'location|nearby'))
                        if loc_elem:
                            location_text = self.clean_text(loc_elem.get_text())
                        else:
                            # Look for text in parens e.g. (New York)
                            loc_match = re.search(r'\((.*?)\)', container.get_text())
                            if loc_match:
                                location_text = loc_match.group(1)
                    
                    # Extract year from title or text
                    year = ""
                    year_match = re.search(r'\b(19|20)\d{2}\b', title)
                    if not year_match and container:
                         year_match = re.search(r'\b(19|20)\d{2}\b', container.get_text())
                    
                    if year_match:
                        year = year_match.group()
                    
                    # Extract image
                    image_url = ""
                    # Check if the link itself is an image or contains one
                    img = link_elem.find('img')
                    if not img and container:
                        img = container.find('img')
                    
                    if img:
                         image_url = img.get('src', '') or img.get('data-src', '')
                    
                    listing = CarListing(
                        title=title,
                        price=price,
                        location=location_text,
                        url=url_full,
                        source=self.source_name,
                        year=year,
                        image_url=image_url
                    )
                    all_listings.append(listing)
                    
                except Exception as e:
                    print(f"  Error parsing Craigslist listing: {e}")
                    continue
        
        return all_listings
    
    def _search_with_selenium(self, url: str, params: dict, location_code: str, max_results: int) -> List[CarListing]:
        """Search using Selenium for JavaScript-rendered content"""
        listings = []
        
        try:
            # Build full URL with params
            from urllib.parse import urlencode
            full_url = f"{url}?{urlencode(params)}"
            
            self.driver.get(full_url)
            time.sleep(2)  # Wait for page to load
            
            # Wait for listings to appear
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'li.cl-search-result, a[href*="/cto/"]'))
                )
            except:
                pass  # Continue even if timeout
            
            # Get page source and parse
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'lxml')
            
            # Find listings
            results = soup.find_all('li', class_='cl-search-result')
            
            if not results:
                results = soup.find_all('a', href=re.compile(r'/cto/|/ctd/'))
                results = [r.find_parent('li') or r.find_parent('div') for r in results if r]
            
            for result in results[:max_results]:
                try:
                    title_elem = result.find('a', class_='cl-app-anchor') or result.find('a', href=re.compile(r'/cto/'))
                    if not title_elem:
                        continue
                    
                    title = self.clean_text(title_elem.get_text())
                    relative_url = title_elem.get('href', '')
                    
                    if relative_url.startswith('//'):
                        url_full = 'https:' + relative_url
                    elif relative_url.startswith('/'):
                        url_full = f"https://{location_code}.craigslist.org{relative_url}"
                    else:
                        url_full = relative_url
                    
                    price_elem = result.find('span', class_='priceinfo') or result.find('span', class_=re.compile(r'price'))
                    price = "N/A"
                    if price_elem:
                        price = self.clean_price(price_elem.get_text())
                    
                    location_elem = result.find('span', class_='meta') or result.find('span', class_=re.compile(r'location'))
                    location_text = "N/A"
                    if location_elem:
                        location_text = self.clean_text(location_elem.get_text())
                    
                    year = ""
                    year_match = re.search(r'\b(19|20)\d{2}\b', title)
                    if year_match:
                        year = year_match.group()
                    
                    image_elem = result.find('img')
                    image_url = ""
                    if image_elem:
                        image_url = image_elem.get('src', '') or image_elem.get('data-src', '')
                    
                    listing = CarListing(
                        title=title,
                        price=price,
                        location=location_text,
                        url=url_full,
                        source=self.source_name,
                        year=year,
                        image_url=image_url
                    )
                    listings.append(listing)
                    
                except Exception as e:
                    print(f"  Error parsing Craigslist listing (Selenium): {e}")
                    continue
                    
        except Exception as e:
            print(f"  Error in Selenium search: {e}")
        finally:
            if self.driver:
                self.driver.quit()
                self.driver = None
        
        return listings


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
                
                
                # Navigate to marketplace with search parameters
                # Facebook Marketplace location filtering is unreliable via URL parameters
                # We will try the path-based approach: /marketplace/{slug}/search
                
                # Extract city and state for slug
                slug = "us" # Default to US if no location
                
                if location:
                    # Try to extract city and state
                    # Remove ZIP code first
                    loc_clean = re.sub(r'\d{5}', '', location).strip()
                    
                    # Clean up for slug: lowercase, replace spaces/commas with hyphens
                    # "Denver, CO" -> "denver" (try city only first as it's often more reliable)
                    # If we have a comma, take the first part
                    if ',' in loc_clean:
                        slug = loc_clean.split(',')[0].strip().lower()
                    else:
                        slug = loc_clean.lower()
                    
                    slug = re.sub(r'\s+', '-', slug)
                
                # Build the search URL using path-based structure
                # Format: /marketplace/{slug}/search?query=...
                search_url = f"{self.base_url}/{slug}/search"
                
                # Add query parameter for search term
                search_url += f"?query={query.replace(' ', '%20')}"
                
                # Add category filter for vehicles
                search_url += "&category=vehicles"
                
                # Add delivery method filter (local pickup)
                search_url += "&deliveryMethod=local_pick_up"
                
                # Add radius
                search_url += "&radius=40"
                
                if price_min:
                    search_url += f"&minPrice={price_min}"
                if price_max:
                    search_url += f"&maxPrice={price_max}"
                
                print(f"[Facebook] Searching URL: {search_url}")
                
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
                        
                        # Extract location from the listing itself
                        location_text = "N/A"
                        try:
                            # Try multiple selectors for location
                            # Facebook shows location in different ways
                            location_selectors = [
                                'span[class*="location"]',
                                'span:contains("miles away")',
                                'div[class*="location"] span',
                                'span[dir="auto"]'  # Sometimes location is in a span with dir="auto"
                            ]
                            
                            for selector in location_selectors:
                                try:
                                    loc_elems = elem.find_elements(By.CSS_SELECTOR, selector)
                                    for loc_elem in loc_elems:
                                        text = self.clean_text(loc_elem.text)
                                        # Check if this looks like a location (contains city/state or "miles away")
                                        if text and (
                                            'miles away' in text.lower() or 
                                            ',' in text or  # City, State format
                                            len(text.split()) <= 4  # Short location text
                                        ):
                                            # Skip if it's a price or title
                                            if '$' not in text and not re.search(r'\b(19|20)\d{2}\b', text):
                                                location_text = text
                                                break
                                    if location_text != "N/A":
                                        break
                                except:
                                    continue
                            
                            # If still no location found, use the search location
                            if location_text == "N/A" and location:
                                location_text = location
                        except:
                            if location:
                                location_text = location
                        
                        
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
        
        # Filter results by location if specified
        # Facebook's URL parameters don't always work, so we filter after fetching
        if location and all_listings:
            filtered_listings = []
            target_state = None
            target_city = None
            
            # Extract target location info
            # Try to extract city and state from location string
            city_name = None
            state_code = None
            
            city_state_match = re.search(r'([A-Za-z\s]+),?\s+([A-Z]{2})', location)
            if city_state_match:
                city_name = city_state_match.group(1).strip().lower()
                state_code = city_state_match.group(2).upper()
            
            if state_code:
                target_state = state_code.upper()
            if city_name:
                target_city = city_name.lower()
            
            print(f"[Facebook] Filtering {len(all_listings)} results for location: {location}")
            
            for listing in all_listings:
                # Check if listing location matches target
                listing_loc = listing.location.lower()
                
                # Only filter out obvious wrong states (mainly California when not searching there)
                # Be less aggressive to allow more results through
                if target_state and target_state.upper() not in ['CA', 'CALIFORNIA']:
                    # If we're NOT searching in California, exclude CA results
                    if 'california' in listing_loc or ', ca' in listing_loc:
                        print(f"[Facebook] Dropping result from California: {listing.title} ({listing.location})")
                        continue
                
                # Otherwise, keep the listing
                # print(f"[Facebook] Keeping result: {listing.title} ({listing.location})")
                filtered_listings.append(listing)
            
            print(f"[Facebook] Filtered to {len(filtered_listings)} results matching location")
            all_listings = filtered_listings
        
        if all_listings:
            print(f"[Facebook] Found {len(all_listings)} results")
            # Print first few locations for debugging
            for i, listing in enumerate(all_listings[:3]):
                print(f"[Facebook] Result {i+1} location: {listing.location}")
        
        if self.driver:
            self.driver.quit()
            self.driver = None
        
        return all_listings

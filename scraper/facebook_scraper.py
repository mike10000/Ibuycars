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
from scraper.geocoding_helper import is_within_radius


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
    
    # Major Virginia cities to search when "Virginia" is selected
    VIRGINIA_LOCATIONS = [
        "Richmond, VA",
        "Virginia Beach, VA",
        "Norfolk, VA",
        "Fairfax, VA",
        "Roanoke, VA",
        "Charlottesville, VA",
        "Lynchburg, VA",
        "Alexandria, VA",
        "Fredericksburg, VA"
    ]
    
    # Los Angeles DMA (DMA-CA-3) counties to search
    # Using multiple major cities across all 5 counties for comprehensive coverage
    LA_DMA_LOCATIONS = [
        # Los Angeles County
        "Los Angeles, CA",
        "Long Beach, CA",
        "Pasadena, CA",
        "Glendale, CA",
        # Orange County
        "Santa Ana, CA",
        "Anaheim, CA",
        "Irvine, CA",
        # San Bernardino County / Inland Empire
        "San Bernardino, CA",
        "Riverside, CA",
        "Fontana, CA",
        # Ventura County
        "Ventura, CA",
        "Oxnard, CA",
        # Inyo County
        "Bishop, CA"
    ]
    
    # New Jersey DMA (DMA-NJ-1) - Statewide coverage
    # Major cities across all regions of NJ
    NJ_DMA_LOCATIONS = [
        # Northern NJ
        "Newark, NJ",
        "Jersey City, NJ",
        "Paterson, NJ",
        "Elizabeth, NJ",
        "Edison, NJ",
        # Central NJ
        "New Brunswick, NJ",
        "Trenton, NJ",
        "Princeton, NJ",
        # Jersey Shore
        "Atlantic City, NJ",
        "Asbury Park, NJ",
        "Long Branch, NJ",
        # Southern NJ
        "Camden, NJ",
        "Cherry Hill, NJ",
        # Northwestern NJ
        "Morristown, NJ",
        "Hackettstown, NJ"
    ]

    # Sacramento-Stockton-Modesto DMA (DMA-CA-1)
    # Covers: Amador, El Dorado, Plumas, Sierra, Toulumne, Calaveras, Nevada, 
    # Sacramento, Stanislaus, Yolo, Colusa, Placer, San Joaquin, Sutter, Yuba
    DMA_CA_1_LOCATIONS = [
        "Sacramento, CA",       # Sacramento
        "Stockton, CA",         # San Joaquin
        "Modesto, CA",          # Stanislaus
        "Roseville, CA",        # Placer
        "Woodland, CA",         # Yolo
        "Yuba City, CA",        # Sutter/Yuba
        "Placerville, CA",      # El Dorado
        "Grass Valley, CA",     # Nevada
        "Sonora, CA",           # Tuolumne
        "San Andreas, CA",      # Calaveras
        "Jackson, CA",          # Amador
        "Colusa, CA",           # Colusa
        "Quincy, CA",           # Plumas
        "Downieville, CA"       # Sierra
    ]

    # Denver DMA (DMA-CO-1)
    # Covers: Denver, Boulder, Colorado Springs, Fort Collins and surrounding areas
    DMA_CO_1_LOCATIONS = [
        "Denver, CO",
        "Aurora, CO",
        "Lakewood, CO",
        "Thornton, CO",
        "Arvada, CO",
        "Westminster, CO",
        "Centennial, CO",
        "Boulder, CO",
        "Colorado Springs, CO",
        "Fort Collins, CO",
        "Greeley, CO",
        "Longmont, CO",
        "Loveland, CO",
        "Castle Rock, CO"
    ]

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
            
        # Handle "Virginia" location by searching multiple cities
        if location and location.lower() == "virginia":
            print(f"[Facebook] 'Virginia' location detected. Searching across {len(self.VIRGINIA_LOCATIONS)} major VA cities...")
            
            # Reduce max_results per city to avoid overwhelming and keep total count reasonable
            # But ensure at least a few per city
            per_city_results = max(3, max_results // 3)
            
            for city_loc in self.VIRGINIA_LOCATIONS:
                print(f"[Facebook] Searching sub-location: {city_loc}")
                city_listings = self._search_single_location(
                    makes, model, year_min, year_max, price_min, price_max, 
                    city_loc, per_city_results, private_sellers_only
                )
                all_listings.extend(city_listings)
                
                # If we have enough results, stop (optional, but good for speed)
                if len(all_listings) >= max_results * 2:
                    break
            
            # Deduplicate by URL
            unique_listings = []
            seen_urls = set()
            for listing in all_listings:
                if listing.url not in seen_urls:
                    seen_urls.add(listing.url)
                    unique_listings.append(listing)
            
            if self.driver:
                self.driver.quit()
                self.driver = None
            return unique_listings[:max_results]
        
        # Handle "Los Angeles" or "DMA-CA-3" location by searching multiple counties
        elif location and (location.lower() in ["los angeles", "dma-ca-3"]):
            print(f"[Facebook] 'Los Angeles DMA' location detected. Searching across {len(self.LA_DMA_LOCATIONS)} counties...")
            
            # Reduce max_results per county to avoid overwhelming and keep total count reasonable
            per_county_results = max(3, max_results // 3)
            
            for county_loc in self.LA_DMA_LOCATIONS:
                print(f"[Facebook] Searching sub-location: {county_loc}")
                county_listings = self._search_single_location(
                    makes, model, year_min, year_max, price_min, price_max, 
                    county_loc, per_county_results, private_sellers_only
                )
                all_listings.extend(county_listings)
                
                # If we have enough results, stop (optional, but good for speed)
                if len(all_listings) >= max_results * 2:
                    break
            
            # Deduplicate by URL
            unique_listings = []
            seen_urls = set()
            for listing in all_listings:
                if listing.url not in seen_urls:
                    seen_urls.add(listing.url)
                    unique_listings.append(listing)
            
            if self.driver:
                self.driver.quit()
                self.driver = None
            return unique_listings[:max_results]
        
        # Handle "New Jersey" or "DMA-NJ-1" location by searching multiple cities statewide
        elif location and (location.strip().lower() in ["new jersey", "dma-nj-1", "new jersey dma"]):
            print(f"[Facebook] 'New Jersey DMA' location detected. Searching across {len(self.NJ_DMA_LOCATIONS)} cities...") 
            
            # Reduce max_results per city
            per_city_results = max(3, max_results // 3)
            
            for city_loc in self.NJ_DMA_LOCATIONS:
                print(f"[Facebook] Searching sub-location: {city_loc}")
                city_listings = self._search_single_location(
                    makes, model, year_min, year_max, price_min, price_max,
                    city_loc, per_city_results, private_sellers_only
                )
                all_listings.extend(city_listings)
                
                # If we have enough results, stop
                if len(all_listings) >= max_results * 2:
                    break
            
            # Deduplicate by URL
            unique_listings = []
            seen_urls = set()
            for listing in all_listings:
                if listing.url not in seen_urls:
                    seen_urls.add(listing.url)
                    unique_listings.append(listing)
            
            if self.driver:
                self.driver.quit()
                self.driver = None
            return unique_listings[:max_results]
        
        # Handle "DMA-CA-1" (Sacramento/Stockton/Modesto)
        elif location and (location.strip().lower() in ["dma-ca-1", "sacramento dma"]):
            print(f"[Facebook] 'DMA-CA-1' location detected. Searching across {len(self.DMA_CA_1_LOCATIONS)} cities...")
            
            # Reduce max_results per city
            per_city_results = max(3, max_results // 4) # Slightly more per city as list is long
            
            for city_loc in self.DMA_CA_1_LOCATIONS:
                print(f"[Facebook] Searching sub-location: {city_loc}")
                city_listings = self._search_single_location(
                    makes, model, year_min, year_max, price_min, price_max,
                    city_loc, per_city_results, private_sellers_only
                )
                all_listings.extend(city_listings)
                
                # If we have enough results, stop
                if len(all_listings) >= max_results * 2:
                    break
            
            # Deduplicate by URL
            unique_listings = []
            seen_urls = set()
            for listing in all_listings:
                if listing.url not in seen_urls:
                    seen_urls.add(listing.url)
                    unique_listings.append(listing)
            
            if self.driver:
                self.driver.quit()
                self.driver = None
            return unique_listings[:max_results]

        # Handle "DMA-CO-1" (Denver DMA)
        elif location and (location.strip().lower() in ["dma-co-1", "denver dma"]):
            print(f"[Facebook] 'DMA-CO-1' location detected. Searching across {len(self.DMA_CO_1_LOCATIONS)} cities...")
            
            # Reduce max_results per city
            per_city_results = max(3, max_results // 4)
            
            for city_loc in self.DMA_CO_1_LOCATIONS:
                print(f"[Facebook] Searching sub-location: {city_loc}")
                city_listings = self._search_single_location(
                    makes, model, year_min, year_max, price_min, price_max,
                    city_loc, per_city_results, private_sellers_only
                )
                all_listings.extend(city_listings)
                
                # If we have enough results, stop
                if len(all_listings) >= max_results * 2:
                    break
            
            # Deduplicate by URL
            unique_listings = []
            seen_urls = set()
            for listing in all_listings:
                if listing.url not in seen_urls:
                    seen_urls.add(listing.url)
                    unique_listings.append(listing)
            
            if self.driver:
                self.driver.quit()
                self.driver = None
            return unique_listings[:max_results]

        else:
            # Standard single location search
            results = self._search_single_location(
                makes, model, year_min, year_max, price_min, price_max, 
                location, max_results, private_sellers_only
            )
            
            if self.driver:
                self.driver.quit()
                self.driver = None
                
            return results

    def _search_single_location(self, makes: List[str], model: Optional[str], year_min: Optional[int],
                               year_max: Optional[int], price_min: Optional[int], price_max: Optional[int],
                               location: Optional[str], max_results: int, private_sellers_only: bool) -> List[CarListing]:
        """Helper to search a single location"""
        self._setup_driver()
        all_listings = []
        
        # Search for each make
        for make in makes:
            # Skip empty makes - they don't work well with Facebook
            if not make or not make.strip():
                print(f"[Facebook] Skipping empty make - using generic 'cars' search instead")
                make = "cars"
            
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
                        # Skip None elements
                        if elem is None:
                            continue
                        
                        # Extract title
                        title = ""
                        try:
                            title_elem = elem.find_element(By.CSS_SELECTOR, 'span[dir="auto"]')
                            if title_elem:
                                title = self.clean_text(title_elem.text)
                        except:
                            pass
                        
                        # Extract URL
                        if not elem:
                            continue
                        
                        try:
                            url = elem.get_attribute('href') or ""
                        except:
                            url = ""
                        
                        # Skip if no URL
                        if not url:
                            continue
                        
                        # Extract price
                        price = "N/A"
                        try:
                            price_elem = elem.find_element(By.CSS_SELECTOR, 'span[dir="auto"]:last-child')
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
                            location_selectors = [
                                'span[class*="location"]',
                                'span:contains("miles away")',
                                'div[class*="location"] span',
                                'span[dir="auto"]'
                            ]
                            
                            for selector in location_selectors:
                                try:
                                    loc_elems = elem.find_elements(By.CSS_SELECTOR, selector)
                                    for loc_elem in loc_elems:
                                        text = self.clean_text(loc_elem.text)
                                        # Check if this looks like a location
                                        if text and ('miles away' in text.lower() or ',' in text or len(text.split()) <= 4):
                                            if '$' not in text and not re.search(r'\b(19|20)\d{2}\b', text):
                                                location_text = text
                                                break
                                    if location_text != "N/A":
                                        break
                                except:
                                    continue
                            
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
        if location and all_listings:
            filtered_listings = []
            
            # Determine radius based on search type
            # DMA searches cover larger areas, so use larger radius
            # Also use 100 miles for Denver as requested
            radius = 100.0 if "dma" in location.lower() or "denver" in location.lower() else 50.0
            
            print(f"[Facebook] Filtering {len(all_listings)} results for location: {location} (radius: {radius} miles)")
            
            for listing in all_listings:
                # Use geocoding to check if listing is within radius
                # This handles "San Francisco" vs "Sacramento" correctly
                if is_within_radius(location, listing.location, max_miles=radius):
                    filtered_listings.append(listing)
                else:
                    # print(f"[Facebook] Dropping result: {listing.location} is too far from {location}")
                    pass
            
            print(f"[Facebook] Filtered to {len(filtered_listings)} results matching location")
            all_listings = filtered_listings
        
        if all_listings:
            print(f"[Facebook] Found {len(all_listings)} results")
            # Print first few locations for debugging
            for i, listing in enumerate(all_listings[:3]):
                print(f"[Facebook] Result {i+1} location: {listing.location}")
        

        
        return all_listings

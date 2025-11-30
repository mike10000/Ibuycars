"""
Coordinates searches across multiple car listing websites
"""
from typing import List, Dict, Optional
from scraper import (
    CraigslistScraper,
    AutoTraderScraper,
    CarsComScraper,
    FacebookScraper,
    OfferUpScraper,
    CarListing
)
import concurrent.futures
import time


class SearchCoordinator:
    """Coordinates searches across multiple websites"""
    
    def __init__(self):
        self.scrapers = [
            CraigslistScraper(),
            # AutoTraderScraper(),  # Disabled - not working
            CarsComScraper(),
            OfferUpScraper(),
            # FacebookScraper(),  # Commented out by default due to complexity
        ]
    
    def search_all(self, makes: List[str], model: Optional[str] = None, year_min: Optional[int] = None,
                   year_max: Optional[int] = None, price_min: Optional[int] = None,
                   price_max: Optional[int] = None, location: Optional[str] = None,
                   max_results: int = 20, enable_facebook: bool = False,
                   enable_craigslist: bool = True, enable_cars_com: bool = True,
                   enable_offerup: bool = True, enable_autotrader: bool = False,
                   private_sellers_only: bool = False) -> Dict[str, List[CarListing]]:
        """
        Search all websites in parallel
        
        Args:
            makes: List of car makes to search for (e.g., ['Toyota', 'Honda'])
            model: Optional car model to filter by
        
        Returns dictionary mapping source names to lists of listings
        """
        results = {}
        
        # Normalize makes to list
        if isinstance(makes, str):
            makes = [m.strip() for m in makes.split(',') if m.strip()]
        
        if not makes:
            return results
            
        # Initialize active scrapers based on flags
        active_scrapers = []
        
        if enable_craigslist:
            active_scrapers.append(CraigslistScraper())
            
        if enable_cars_com:
            active_scrapers.append(CarsComScraper())
            
        if enable_offerup:
            active_scrapers.append(OfferUpScraper())
            
        if enable_autotrader:
            active_scrapers.append(AutoTraderScraper())
        
        # Enable Facebook if requested
        if enable_facebook:
            active_scrapers.append(FacebookScraper())
            
        # If no scrapers selected, return empty
        if not active_scrapers:
            print("[WARNING] No scrapers selected")
            return results
        
        # Search all sites in parallel
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(active_scrapers)) as executor:
            future_to_scraper = {
                executor.submit(
                    scraper.search,
                    makes, model, year_min, year_max,
                    price_min, price_max, location, max_results,
                    private_sellers_only
                ): scraper for scraper in active_scrapers
            }
            
            for future in concurrent.futures.as_completed(future_to_scraper):
                scraper = future_to_scraper[future]
                try:
                    # Set a timeout for each scraper to prevent hanging
                    listings = future.result(timeout=12)
                    results[scraper.source_name] = listings
                    print(f"[OK] Found {len(listings)} listings on {scraper.source_name}")
                except Exception as e:
                    print(f"[ERROR] Error searching {scraper.source_name}: {e}")
                    results[scraper.source_name] = []
        
        return results
    
    def get_all_listings(self, results: Dict[str, List[CarListing]]) -> List[CarListing]:
        """Flatten all results into a single list"""
        all_listings = []
        for listings in results.values():
            all_listings.extend(listings)
        return all_listings
    
    def filter_listings(self, listings: List[CarListing], 
                       year_min: Optional[int] = None,
                       year_max: Optional[int] = None,
                       price_min: Optional[int] = None,
                       price_max: Optional[int] = None) -> List[CarListing]:
        """Filter listings by year and price"""
        filtered = []
        
        for listing in listings:
            # Filter by year
            if year_min or year_max:
                if listing.year:
                    try:
                        year = int(listing.year)
                        if year_min and year < year_min:
                            continue
                        if year_max and year > year_max:
                            continue
                    except:
                        pass
            
            # Filter by price
            if price_min or price_max:
                # Extract numeric price
                price_str = listing.price.replace('$', '').replace(',', '').strip()
                try:
                    price = int(price_str)
                    if price_min and price < price_min:
                        continue
                    if price_max and price > price_max:
                        continue
                except:
                    pass
            
            filtered.append(listing)
        
        return filtered


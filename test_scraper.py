"""
Simple test script to debug scraper issues
"""
from scraper.craigslist_scraper import CraigslistScraper
from scraper.autotrader_scraper import AutoTraderScraper
from scraper.cars_com_scraper import CarsComScraper

def test_craigslist():
    """Test Craigslist scraper"""
    print("Testing Craigslist scraper...")
    scraper = CraigslistScraper()
    
    # Test location normalization
    test_locations = ["New Jersey", "newjersey", "90210", "Los Angeles"]
    for loc in test_locations:
        normalized = scraper._normalize_location(loc)
        print(f"  '{loc}' -> '{normalized}'")
    
    # Test actual search
    print("\nSearching for Toyota Camry in New Jersey...")
    results = scraper.search(
        make="Toyota",
        model="Camry",
        location="New Jersey",
        max_results=5
    )
    print(f"Found {len(results)} results")
    for i, listing in enumerate(results[:3], 1):
        print(f"  {i}. {listing.title} - {listing.price}")

def test_autotrader():
    """Test AutoTrader scraper"""
    print("\n\nTesting AutoTrader scraper...")
    scraper = AutoTraderScraper()
    
    print("Searching for Honda Civic...")
    results = scraper.search(
        make="Honda",
        model="Civic",
        max_results=5
    )
    print(f"Found {len(results)} results")
    for i, listing in enumerate(results[:3], 1):
        print(f"  {i}. {listing.title} - {listing.price}")

def test_cars_com():
    """Test Cars.com scraper"""
    print("\n\nTesting Cars.com scraper...")
    scraper = CarsComScraper()
    
    print("Searching for Ford F-150...")
    results = scraper.search(
        make="Ford",
        model="F-150",
        max_results=5
    )
    print(f"Found {len(results)} results")
    for i, listing in enumerate(results[:3], 1):
        print(f"  {i}. {listing.title} - {listing.price}")

if __name__ == "__main__":
    print("="*80)
    print("SCRAPER TEST SUITE")
    print("="*80)
    
    try:
        test_craigslist()
        test_autotrader()
        test_cars_com()
    except Exception as e:
        print(f"\nError during testing: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*80)
    print("Testing complete!")


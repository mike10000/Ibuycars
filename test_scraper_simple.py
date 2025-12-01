from scraper.craigslist_scraper import CraigslistScraper
import json

def test_scraper():
    print("Initializing Craigslist Scraper...")
    scraper = CraigslistScraper(use_selenium=False) # Try without selenium first for speed/simplicity
    
    print("Searching for 'Honda Civic' in 'miami'...")
    results = scraper.search(
        makes=['Honda'],
        model='Civic',
        location='miami',
        max_results=5
    )
    
    print(f"Found {len(results)} results.")
    for listing in results:
        print(f"- {listing.title} ({listing.price}) - {listing.url}")

if __name__ == "__main__":
    test_scraper()

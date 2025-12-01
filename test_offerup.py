"""
Test script for OfferUp scraper
This will help diagnose issues with the OfferUp scraper
"""
from scraper.offerup_scraper import OfferUpScraper

def test_offerup():
    print("Testing OfferUp Scraper...")
    print("=" * 50)
    
    scraper = OfferUpScraper(use_selenium=True)
    
    print("\nSearching for 'Honda Civic' in Miami (33122)...")
    results = scraper.search(
        makes=['Honda'],
        model='Civic',
        location='33122',
        max_results=5
    )
    
    print(f"\nFound {len(results)} results:")
    print("-" * 50)
    
    for i, listing in enumerate(results, 1):
        print(f"\n{i}. {listing.title}")
        print(f"   Price: {listing.price}")
        print(f"   Location: {listing.location}")
        print(f"   Year: {listing.year}")
        print(f"   URL: {listing.url}")
    
    if len(results) == 0:
        print("\nNo results found. Possible issues:")
        print("1. OfferUp may be blocking automated requests")
        print("2. The HTML selectors may have changed")
        print("3. There may be no listings matching your criteria")
        print("\nTry running with headless=False to see what's happening")

if __name__ == "__main__":
    test_offerup()

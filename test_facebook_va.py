from scraper.facebook_scraper import FacebookScraper

def test_va_search():
    scraper = FacebookScraper()
    
    # Test 1: Search for "Virginia"
    print("\n--- Testing 'Virginia' ---")
    listings_va = scraper.search(
        makes=['Honda'], 
        model='Civic', 
        location='Virginia', 
        max_results=2
    )
    print(f"Found {len(listings_va)} listings for 'Virginia'")
    for l in listings_va:
        print(f"- {l.title} ({l.location}) - {l.url}")

    # Test 2: Search for "Richmond, VA"
    print("\n--- Testing 'Richmond, VA' ---")
    listings_richmond = scraper.search(
        makes=['Honda'], 
        model='Civic', 
        location='Richmond, VA', 
        max_results=2
    )
    print(f"Found {len(listings_richmond)} listings for 'Richmond, VA'")
    for l in listings_richmond:
        print(f"- {l.title} ({l.location}) - {l.url}")

if __name__ == "__main__":
    test_va_search()

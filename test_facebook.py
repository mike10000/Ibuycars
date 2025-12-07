from scraper.facebook_scraper import FacebookScraper
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

def test_facebook():
    print("Initializing Facebook Scraper...")
    scraper = FacebookScraper()
    
    print("Starting search for 'Honda Civic' in 'Miami, FL'...")
    try:
        results = scraper.search(
            makes=['Honda'], 
            model='Civic', 
            location='Miami, FL', 
            max_results=5,
            private_sellers_only=False
        )
        
        print(f"Search finished. Found {len(results)} listings.")
        for listing in results:
            print(f"- {listing.title} ({listing.price}) - {listing.url}")
            
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    test_facebook()

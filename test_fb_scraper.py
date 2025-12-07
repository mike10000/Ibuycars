
from scraper.facebook_scraper import FacebookScraper
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

def test_facebook_scraper():
    print("Initializing Facebook Scraper...")
    scraper = FacebookScraper()
    
    # Test a simple search first
    print("\n--- Testing Single City Search (Sacramento, CA) ---")
    results = scraper.search(
        makes=['Honda'], 
        model='Civic', 
        location='Sacramento, CA', 
        max_results=5
    )
    
    print(f"Found {len(results)} results for Sacramento.")
    for car in results:
        print(f"- {car.title} - {car.price} - {car.location}")

    # Test DMA search
    print("\n--- Testing DMA-CA-1 Search ---")
    dma_results = scraper.search(
        makes=['Honda'], 
        model='Civic', 
        location='DMA-CA-1', 
        max_results=5
    )
    print(f"Found {len(dma_results)} results for DMA-CA-1.")
    for car in dma_results:
        print(f"- {car.title} - {car.price} - {car.location}")

if __name__ == "__main__":
    test_facebook_scraper()

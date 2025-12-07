
from scraper.craigslist_scraper import CraigslistScraper
from scraper.cars_com_scraper import CarsComScraper
from scraper.offerup_scraper import OfferUpScraper
import time

def test_dma_search():
    print("=== Testing DMA-CA-3 Search Support ===")
    
    scrapers = [
        (CraigslistScraper(use_selenium=False), "Craigslist"),
        (CarsComScraper(use_selenium=False), "Cars.com"),
        (OfferUpScraper(use_selenium=False), "OfferUp")
    ]
    
    for scraper, name in scrapers:
        print(f"\nTesting {name}...")
        try:
            start_time = time.time()
            results = scraper.search(
                makes=['Toyota'],
                model='Camry',
                location='DMA-CA-3',
                max_results=5,
                private_sellers_only=False
            )
            duration = time.time() - start_time
            
            print(f"Found {len(results)} listings in {duration:.2f}s")
            if len(results) > 0:
                print(f"Sample listing location: {results[0].location}")
                print(f"Sample listing URL: {results[0].url}")
            else:
                print("WARNING: No results found")
                
        except Exception as e:
            print(f"ERROR testing {name}: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    test_dma_search()

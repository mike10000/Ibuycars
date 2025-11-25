from scraper.autotrader_scraper import AutoTraderScraper
from scraper.cars_com_scraper import CarsComScraper

def verify_autotrader():
    print("\nVerifying AutoTrader...")
    scraper = AutoTraderScraper(use_selenium=False)
    try:
        results = scraper.search(makes=["Honda"], model="Civic", max_results=5)
        print(f"Found {len(results)} results")
        for r in results:
            print(f"- {r.title} ({r.price})")
    except Exception as e:
        print(f"AutoTrader failed: {e}")

def verify_cars_com():
    print("\nVerifying Cars.com...")
    scraper = CarsComScraper()
    try:
        results = scraper.search(makes=["Ford"], model="F-150", max_results=5)
        print(f"Found {len(results)} results")
        for r in results:
            print(f"- {r.title} ({r.price})")
    except Exception as e:
        print(f"Cars.com failed: {e}")

if __name__ == "__main__":
    verify_autotrader()
    verify_cars_com()

from scraper.craigslist_scraper import CraigslistScraper

def verify():
    print("Verifying Craigslist fix...")
    scraper = CraigslistScraper(use_selenium=False)
    results = scraper.search(makes=["Toyota"], model="Camry", location="New Jersey", max_results=5)
    print(f"Found {len(results)} results")
    for r in results:
        print(f"- {r.title} ({r.price})")

if __name__ == "__main__":
    verify()

from scraper.craigslist_scraper import CraigslistScraper
import time

def debug_craigslist():
    print("Debugging Craigslist...")
    scraper = CraigslistScraper(use_selenium=False) # Try requests first
    
    # Use a known valid URL structure
    url = "https://newjersey.craigslist.org/search/cta?query=toyota+camry"
    print(f"Fetching {url}...")
    
    soup = scraper.get_page(url)
    if not soup:
        print("Failed to get page")
        return

    print("\nPage Title:", soup.title.string if soup.title else "No title")
    
    # Check for common blocking text
    text = soup.get_text().lower()
    if "blocked" in text or "captcha" in text:
        print("BLOCKING DETECTED!")
    
    # Print first 500 chars of body to see structure
    print("\nBody start:")
    print(soup.body.prettify()[:500] if soup.body else "No body")
    
    # Check for expected elements
    results = soup.find_all('li', class_='cl-search-result')
    print(f"\nFound {len(results)} results with 'li.cl-search-result'")
    
    results_gallery = soup.find_all('div', class_='gallery-card')
    print(f"Found {len(results_gallery)} results with 'div.gallery-card'")
    
    links = soup.find_all('a', href=True)
    cto_links = [l for l in links if '/cto/' in l['href']]
    print(f"Found {len(cto_links)} links with '/cto/'")

if __name__ == "__main__":
    debug_craigslist()

import sys
import os
from unittest.mock import MagicMock

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from scraper.facebook_scraper import FacebookScraper
from scraper.craigslist_scraper import CraigslistScraper
from scraper.offerup_scraper import OfferUpScraper

def test_denver_dma():
    print("Testing Denver DMA (DMA-CO-1) Logic...")
    
    # 1. Test Facebook Scraper
    print("\n--- Facebook Scraper ---")
    fb = FacebookScraper()
    # Mock _search_single_location to avoid actual scraping
    fb._search_single_location = MagicMock(return_value=[])
    fb.search(["toyota"], location="DMA-CO-1")
    
    # Verify calls
    print(f"Called _search_single_location {fb._search_single_location.call_count} times")
    calls = fb._search_single_location.call_args_list
    for i, call in enumerate(calls):
        args, kwargs = call
        loc = args[6] # location is 7th arg
        print(f"Call {i+1}: Location='{loc}'")
        
    # 2. Test Craigslist Scraper
    print("\n--- Craigslist Scraper ---")
    cl = CraigslistScraper(use_selenium=False)
    cl._search_single_location = MagicMock(return_value=[])
    cl.search(["toyota"], location="DMA-CO-1")
    
    print(f"Called _search_single_location {cl._search_single_location.call_count} times")
    calls = cl._search_single_location.call_args_list
    for i, call in enumerate(calls):
        args, kwargs = call
        loc = args[6]
        print(f"Call {i+1}: Location='{loc}'")

    # 3. Test OfferUp Scraper
    print("\n--- OfferUp Scraper ---")
    ou = OfferUpScraper(use_selenium=False)
    ou._search_single_location = MagicMock(return_value=[])
    ou.search(["toyota"], location="DMA-CO-1")
    
    print(f"Called _search_single_location {ou._search_single_location.call_count} times")
    calls = ou._search_single_location.call_args_list
    for i, call in enumerate(calls):
        args, kwargs = call
        # args: makes, model, year_min, year_max, price_min, price_max, location, max_results, private_sellers_only
        loc = args[6]
        dist = kwargs.get('distance')
        print(f"Call {i+1}: Location='{loc}', Distance={dist}")

if __name__ == "__main__":
    test_denver_dma()

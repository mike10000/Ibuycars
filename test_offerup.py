"""
Test script for OfferUp scraper
"""
from scraper.offerup_scraper import OfferUpScraper


def test_offerup():
    """Test OfferUp scraper"""
    print("Testing OfferUp scraper...")
    scraper = OfferUpScraper()
    
    # Test zip code to lat/lon conversion
    print("\nTesting ZIP code to lat/lon conversion:")
    test_zips = ["33410", "90210", "10001", "60601"]
    for zip_code in test_zips:
        lat, lon = scraper._zip_to_lat_lon(zip_code)
        print(f"  ZIP {zip_code} -> lat: {lat}, lon: {lon}")
    
    # Test actual search
    print("\n\nSearching for Toyota in ZIP 33410...")
    results = scraper.search(
        makes=["Toyota"],
        location="33410",
        max_results=5
    )
    print(f"Found {len(results)} results")
    for i, listing in enumerate(results, 1):
        print(f"\n{i}. {listing.title}")
        print(f"   Price: {listing.price}")
        print(f"   Location: {listing.location}")
        print(f"   Year: {listing.year}")
        print(f"   URL: {listing.url}")


if __name__ == "__main__":
    print("="*80)
    print("OFFERUP SCRAPER TEST")
    print("="*80)
    
    try:
        test_offerup()
    except Exception as e:
        print(f"\nError during testing: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*80)
    print("Testing complete!")

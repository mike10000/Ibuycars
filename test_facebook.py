"""
Test script for Facebook Marketplace scraper
"""
from scraper.facebook_scraper import FacebookScraper


def test_facebook():
    """Test Facebook scraper"""
    print("Testing Facebook Marketplace scraper...")
    scraper = FacebookScraper()
    
    # Test actual search
    print("\nSearching for Toyota in test location...")
    try:
        results = scraper.search(
            makes=["Toyota"],
            location="Miami, FL",
            max_results=3
        )
        print(f"Found {len(results)} results")
        for i, listing in enumerate(results, 1):
            print(f"\n{i}. {listing.title}")
            print(f"   Price: {listing.price}")
            print(f"   Location: {listing.location}")
            print(f"   Year: {listing.year}")
            print(f"   URL: {listing.url[:80]}...")
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("="*80)
    print("FACEBOOK MARKETPLACE SCRAPER TEST")
    print("="*80)
    
    test_facebook()
    
    print("\n" + "="*80)
    print("Testing complete!")

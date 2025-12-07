from scraper.facebook_scraper import FacebookScraper

def test_la_dma_search():
    print("Testing Facebook LA DMA search...")
    scraper = FacebookScraper()
    
    try:
        results = scraper.search(
            makes=['Honda'],
            model='Civic',
            location='DMA-CA-3',
            max_results=5,
            private_sellers_only=False
        )
        
        print(f"Found {len(results)} listings")
        for i, listing in enumerate(results[:3], 1):
            print(f"{i}. {listing.title} - {listing.price} ({listing.location})")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_la_dma_search()

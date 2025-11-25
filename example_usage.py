"""
Example usage of the car search tool programmatically
"""
from search_coordinator import SearchCoordinator


def example_search():
    """Example of how to use the search coordinator programmatically"""
    
    # Initialize the coordinator
    coordinator = SearchCoordinator()
    
    # Define search parameters
    params = {
        'makes': ['Toyota', 'Honda'],  # Can search multiple makes
        'model': 'Camry',  # Optional - can be None
        'year_min': 2015,
        'year_max': 2020,
        'price_min': 10000,
        'price_max': 25000,
        'location': '90210',  # Beverly Hills ZIP code
        'max_results': 10,
        'enable_facebook': False  # Set to True if you want Facebook results
    }
    
    print("Searching for cars...")
    print(f"Parameters: {params}\n")
    
    # Search all sites
    results = coordinator.search_all(**params)
    
    # Get all listings
    all_listings = coordinator.get_all_listings(results)
    
    # Print summary
    print("\n" + "="*80)
    print("SEARCH SUMMARY")
    print("="*80)
    for source, listings in results.items():
        print(f"{source}: {len(listings)} listings")
    print(f"Total: {len(all_listings)} listings")
    
    # Print first few listings
    print("\n" + "="*80)
    print("SAMPLE LISTINGS")
    print("="*80)
    for i, listing in enumerate(all_listings[:5]):
        print(f"\n{i+1}. {listing.title}")
        print(f"   Price: {listing.price}")
        print(f"   Location: {listing.location}")
        print(f"   Source: {listing.source}")
        print(f"   URL: {listing.url}")


if __name__ == "__main__":
    example_search()


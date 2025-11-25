"""
Main entry point for the used car search tool
"""
import sys
from search_coordinator import SearchCoordinator
from scraper import CarListing
import json


def print_listing(listing: CarListing, index: int):
    """Print a formatted car listing"""
    print(f"\n{'='*80}")
    print(f"Listing #{index + 1}")
    print(f"{'='*80}")
    print(f"Title:     {listing.title}")
    print(f"Price:     {listing.price}")
    print(f"Location:  {listing.location}")
    if listing.year:
        print(f"Year:      {listing.year}")
    if listing.mileage:
        print(f"Mileage:   {listing.mileage}")
    print(f"Source:    {listing.source}")
    print(f"URL:       {listing.url}")
    if listing.description:
        print(f"Description: {listing.description[:200]}...")


def print_results(results: dict, all_listings: list):
    """Print search results in a formatted way"""
    print("\n" + "="*80)
    print("SEARCH RESULTS")
    print("="*80)
    
    # Print summary by source
    print("\nSummary by Source:")
    print("-" * 80)
    for source, listings in results.items():
        print(f"{source:30} {len(listings):3} listings found")
    
    total = len(all_listings)
    print(f"\n{'Total':30} {total:3} listings found")
    
    # Print all listings
    if all_listings:
        print("\n" + "="*80)
        print("ALL LISTINGS")
        print("="*80)
        
        for i, listing in enumerate(all_listings):
            print_listing(listing, i)
    else:
        print("\nNo listings found. Try adjusting your search parameters.")
    
    print("\n" + "="*80)


def get_user_input():
    """Get search parameters from user"""
    print("="*80)
    print("USED CAR SEARCH TOOL")
    print("="*80)
    print("\nEnter your search parameters (press Enter to skip optional fields):\n")
    
    make_input = input("Make(s) - comma-separated (e.g., Toyota, Honda, Ford): ").strip()
    if not make_input:
        print("At least one make is required!")
        sys.exit(1)
    
    # Parse makes
    makes = [m.strip() for m in make_input.split(',') if m.strip()]
    if not makes:
        print("Invalid make input!")
        sys.exit(1)
    
    model = input("Model (optional, e.g., Camry, Civic, F-150): ").strip() or None
    
    year_min_str = input("Minimum year (optional): ").strip()
    year_min = int(year_min_str) if year_min_str else None
    
    year_max_str = input("Maximum year (optional): ").strip()
    year_max = int(year_max_str) if year_max_str else None
    
    price_min_str = input("Minimum price (optional): ").strip()
    price_min = int(price_min_str) if price_min_str else None
    
    price_max_str = input("Maximum price (optional): ").strip()
    price_max = int(price_max_str) if price_max_str else None
    
    location = input("Location/ZIP code (optional): ").strip() or None
    
    max_results_str = input("Max results per site (default 20): ").strip()
    max_results = int(max_results_str) if max_results_str else 20
    
    facebook_str = input("Enable Facebook Marketplace? (y/n, default n): ").strip().lower()
    enable_facebook = facebook_str == 'y'
    
    return {
        'makes': makes,
        'model': model,
        'year_min': year_min,
        'year_max': year_max,
        'price_min': price_min,
        'price_max': price_max,
        'location': location,
        'max_results': max_results,
        'enable_facebook': enable_facebook
    }


def save_results(results: dict, all_listings: list, filename: str = "search_results.json"):
    """Save results to JSON file"""
    output = {
        'summary': {source: len(listings) for source, listings in results.items()},
        'total': len(all_listings),
        'listings': [listing.to_dict() for listing in all_listings]
    }
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"\nResults saved to {filename}")


def main():
    """Main function"""
    try:
        # Get user input
        params = get_user_input()
        
        print("\n" + "="*80)
        print("Searching... This may take a moment.")
        print("="*80 + "\n")
        
        # Initialize coordinator
        coordinator = SearchCoordinator()
        
        # Search all sites
        results = coordinator.search_all(**params)
        
        # Get all listings
        all_listings = coordinator.get_all_listings(results)
        
        # Apply additional filtering
        all_listings = coordinator.filter_listings(
            all_listings,
            year_min=params['year_min'],
            year_max=params['year_max'],
            price_min=params['price_min'],
            price_max=params['price_max']
        )
        
        # Print results
        print_results(results, all_listings)
        
        # Ask if user wants to save results
        save_str = input("\nSave results to JSON file? (y/n): ").strip().lower()
        if save_str == 'y':
            save_results(results, all_listings)
        
    except KeyboardInterrupt:
        print("\n\nSearch cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()


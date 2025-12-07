"""
Geocoding helper module for location-based filtering.
Uses geopy with Nominatim (OpenStreetMap) geocoder.
"""

from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from typing import Optional, Tuple
import time

# Cache for geocoded locations to avoid repeated API calls
_geocode_cache = {}

# Initialize geocoder with user agent
geolocator = Nominatim(user_agent="ibuycars_scraper")

# Rate limiting: Nominatim requires 1 second between requests
_last_request_time = 0
_MIN_REQUEST_INTERVAL = 1.0  # seconds


def geocode_location(location_string: str) -> Optional[Tuple[float, float]]:
    """
    Geocode a location string to coordinates (latitude, longitude).
    
    Args:
        location_string: Address or location to geocode (e.g., "Sacramento, CA")
        
    Returns:
        Tuple of (latitude, longitude) or None if geocoding fails
    """
    global _last_request_time
    
    if not location_string:
        return None
    
    # Check cache first
    cache_key = location_string.lower().strip()
    if cache_key in _geocode_cache:
        return _geocode_cache[cache_key]
    
    try:
        # Rate limiting
        elapsed = time.time() - _last_request_time
        if elapsed < _MIN_REQUEST_INTERVAL:
            time.sleep(_MIN_REQUEST_INTERVAL - elapsed)
        
        # Geocode
        _last_request_time = time.time()
        location = geolocator.geocode(location_string, timeout=10)
        
        if location:
            coords = (location.latitude, location.longitude)
            _geocode_cache[cache_key] = coords
            return coords
        else:
            _geocode_cache[cache_key] = None
            return None
            
    except Exception as e:
        print(f"[Geocoding] Error geocoding '{location_string}': {e}")
        _geocode_cache[cache_key] = None
        return None


def calculate_distance(coord1: Tuple[float, float], coord2: Tuple[float, float]) -> float:
    """
    Calculate distance between two coordinates in miles.
    
    Args:
        coord1: (latitude, longitude) of first point
        coord2: (latitude, longitude) of second point
        
    Returns:
        Distance in miles
    """
    try:
        return geodesic(coord1, coord2).miles
    except Exception as e:
        print(f"[Geocoding] Error calculating distance: {e}")
        return float('inf')  # Return infinite distance on error


def is_within_radius(search_location: str, result_location: str, max_miles: float = 50.0) -> bool:
    """
    Check if result location is within specified radius of search location.
    
    Args:
        search_location: The location being searched for
        result_location: The location of a search result
        max_miles: Maximum distance in miles (default: 50)
        
    Returns:
        True if within radius or if geocoding fails (fail open), False otherwise
    """
    # Geocode both locations
    search_coords = geocode_location(search_location)
    result_coords = geocode_location(result_location)
    
    # If either geocoding fails, return True (fail open - keep the result)
    if not search_coords or not result_coords:
        return True
    
    # Calculate distance
    distance = calculate_distance(search_coords, result_coords)
    
    # Check if within radius
    within = distance <= max_miles
    
    if not within:
        print(f"[Geocoding] Filtering out result: {result_location} is {distance:.1f} miles from {search_location} (max: {max_miles})")
    
    return within


def clear_cache():
    """Clear the geocoding cache."""
    global _geocode_cache
    _geocode_cache = {}

"""
Base scraper class for all car listing scrapers
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Optional
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import time
import urllib.parse


class CarListing:
    """Data class for car listings"""
    def __init__(self, title: str, price: str, location: str, url: str, 
                 source: str, description: str = "", year: str = "", 
                 mileage: str = "", image_url: str = ""):
        self.title = title
        self.price = price
        self.location = location
        self.url = url
        self.source = source
        self.description = description
        self.year = year
        self.mileage = mileage
        self.image_url = image_url
    
    def to_dict(self) -> Dict:
        """Convert listing to dictionary"""
        return {
            'title': self.title,
            'price': self.price,
            'location': self.location,
            'url': self.url,
            'source': self.source,
            'description': self.description,
            'year': self.year,
            'mileage': self.mileage,
            'image_url': self.image_url
        }
    
    def __str__(self):
        return f"{self.title} - {self.price} - {self.location} ({self.source})"


class BaseScraper(ABC):
    """Base class for all car listing scrapers"""
    
    def __init__(self, source_name: str):
        self.source_name = source_name
        self.ua = UserAgent()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': self.ua.random
        })
    
    def get_page(self, url: str, params: Optional[Dict] = None) -> Optional[BeautifulSoup]:
        """Fetch and parse a webpage"""
        try:
            # Add delay to avoid rate limiting
            time.sleep(0.5)
            
            # Update headers
            self.session.headers.update({
                'User-Agent': self.ua.random,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            })
            
            response = self.session.get(url, params=params, timeout=15)
            response.raise_for_status()
            
            # Check if we got blocked
            if 'blocked' in response.text.lower() or 'captcha' in response.text.lower():
                print(f"Warning: Possible blocking detected on {self.source_name}")
            
            return BeautifulSoup(response.content, 'lxml')
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return None
    
    def clean_price(self, price_str: str) -> str:
        """Clean and format price string"""
        if not price_str:
            return "N/A"
        # Remove common price prefixes and clean
        price_str = price_str.replace('$', '').replace(',', '').strip()
        try:
            # Try to format as currency
            price_num = int(price_str)
            return f"${price_num:,}"
        except:
            return price_str
    
    def clean_text(self, text: str) -> str:
        """Clean text content"""
        if not text:
            return ""
        return ' '.join(text.split())
    
    @abstractmethod
    def search(self, makes: List[str], model: Optional[str] = None, year_min: Optional[int] = None,
               year_max: Optional[int] = None, price_min: Optional[int] = None,
               price_max: Optional[int] = None, location: Optional[str] = None,
               max_results: int = 20) -> List[CarListing]:
        """
        Search for cars based on parameters
        Args:
            makes: List of car makes to search for (e.g., ['Toyota', 'Honda'])
            model: Optional car model to filter by
        Returns list of CarListing objects
        """
        pass


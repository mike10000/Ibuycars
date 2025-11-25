# Used Car Search Tool

A comprehensive web scraping tool that searches multiple websites for used cars for sale by owners based on your specific parameters.

## Features

- **Modern Web Interface** - Beautiful, responsive web UI styled like professional car buying sites
- **Multi-Source Search** - Search multiple car listing websites simultaneously
- **Advanced Filtering** - Filter by make, model, year, price range, location, and more
- **Aggregated Results** - All results from different sources in one place
- **Source Tracking** - See exactly where each listing was found
- **Real-time Search** - Fast, asynchronous search with loading indicators
- **Command Line Interface** - Also available as a CLI tool

## Installation

1. Install Python 3.8 or higher
2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. For sites that require Selenium (like Facebook Marketplace), you'll need Chrome browser installed.

## Usage

### Web Interface (Recommended)

1. Install Flask dependencies:
```bash
pip install flask flask-cors
```

2. Start the web server:
```bash
python app.py
```

3. Open your browser and navigate to:
```
http://localhost:5000
```

4. Use the web interface to search for cars with a modern, user-friendly design!

### Command Line Interface

Run the main script:
```bash
python main.py
```

You'll be prompted to enter:
- Make (e.g., Toyota, Honda)
- Model (e.g., Camry, Civic)
- Year range (optional)
- Price range (optional)
- Location/ZIP code (optional)
- Maximum results per site (optional)

## Supported Websites

- Craigslist
- Facebook Marketplace
- AutoTrader (private sellers)
- Cars.com (private sellers)
- More sites can be added easily

## Notes

- **No API keys required** - All scrapers work with public websites
- **Selenium Support**: All scrapers now use Selenium (Chrome) for JavaScript-rendered content
- **Chrome Browser Required**: Make sure Chrome browser is installed for best results
- **AutoTrader and Cars.com** now use Selenium to handle JavaScript-rendered listings
- **Craigslist** uses Selenium with fallback to regular scraping
- **Facebook Marketplace** requires Chrome browser and ChromeDriver (optional, disabled by default)
- **Location for Craigslist**: Use location codes like "newjersey", "sfbay", "newyork" or common city names (automatically converted)
- Always respect robots.txt and terms of service
- Results may vary based on website availability and structure changes

## Troubleshooting

### Chrome Driver Errors ([WinError 193])
If you get `[WinError 193] %1 is not a valid Win32 application`:
1. **Clear ChromeDriver cache**: Run `python fix_chromedriver.py` to clear corrupted downloads
2. **Verify Chrome is installed**: Make sure **Chrome browser is installed** (not just Chromium)
3. **Re-run the tool**: ChromeDriver will be automatically re-downloaded
4. **Manual fix**: If issues persist, manually download ChromeDriver from https://chromedriver.chromium.org/ and place it in your PATH
5. **Fallback**: The tool will automatically fall back to regular scraping if Selenium fails

### No results from AutoTrader/Cars.com
- These sites now use Selenium to handle JavaScript-rendered content
- If you still get no results, the site structure may have changed
- Check that Chrome browser is properly installed

### Craigslist location errors
- Location names are automatically converted (e.g., "New Jersey" → "newjersey")
- If you get errors, try using location codes directly: "newjersey", "sfbay", "newyork", "chicago", etc.
- ZIP codes will default to the nearest major city

### Facebook Marketplace Chrome driver errors
Facebook Marketplace requires Selenium with Chrome. If you get driver errors:
- Make sure Chrome browser is installed
- The tool will skip Facebook if ChromeDriver isn't available
- You can disable Facebook searches by answering 'n' when prompted


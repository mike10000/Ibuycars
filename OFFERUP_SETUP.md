# OfferUp Scraper Setup Guide

## Why OfferUp is Challenging

OfferUp is one of the more difficult sites to scrape because:
1. **Heavy JavaScript** - Content loads dynamically
2. **Anti-bot protection** - Detects and blocks automated browsers
3. **Changing HTML** - Site structure updates frequently
4. **Location-based** - Requires accurate geolocation

## Current Status

The OfferUp scraper uses **Selenium** (automated browser) to handle JavaScript rendering. However, it may not work reliably due to OfferUp's anti-bot measures.

## How to Test

### 1. Run the diagnostic script:
```bash
python test_offerup.py
```

### 2. If it doesn't work, try non-headless mode:

Edit `test_offerup.py` and change:
```python
scraper = OfferUpScraper(use_selenium=True, headless=False, debug=True)
```

This will open a visible browser window so you can see what's happening.

## Common Issues & Solutions

### Issue 1: No results found
**Cause:** OfferUp may be blocking the automated browser  
**Solution:** 
- Try non-headless mode (`headless=False`)
- Add longer delays between requests
- Use a residential proxy (advanced)

### Issue 2: ChromeDriver errors
**Cause:** Chrome/ChromeDriver version mismatch  
**Solution:**
```bash
pip install --upgrade webdriver-manager
```

### Issue 3: Timeout errors
**Cause:** Page takes too long to load  
**Solution:** Increase wait times in the scraper (currently 3 seconds)

## Alternative Approach

If the scraper continues to fail, consider:

1. **Manual API Discovery** - OfferUp may have an undocumented API you can use
2. **Disable OfferUp** - Focus on other sources (Craigslist, Cars.com, Facebook)
3. **Use OfferUp's Official Tools** - They may offer data export options

## Recommended: Disable OfferUp for Now

Since OfferUp is unreliable, you can disable it in your search form by unchecking the "OfferUp" checkbox, or remove it from the coordinator.

The other scrapers (Craigslist, Cars.com, Facebook) are more reliable.

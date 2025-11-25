"""
Utility script to fix ChromeDriver issues
Run this if you're getting [WinError 193] errors
"""
import os
import shutil
from pathlib import Path

def clear_chromedriver_cache():
    """Clear webdriver-manager cache to force re-download"""
    cache_paths = [
        Path.home() / ".wdm",
        Path.home() / ".cache" / "selenium",
        Path.home() / ".cache" / "webdriver-manager",
    ]
    
    print("Clearing ChromeDriver cache...")
    for cache_path in cache_paths:
        if cache_path.exists():
            try:
                shutil.rmtree(cache_path)
                print(f"  [OK] Cleared: {cache_path}")
            except Exception as e:
                print(f"  [ERROR] Could not clear {cache_path}: {e}")
        else:
            print(f"  - Not found: {cache_path}")
    
    print("\nCache cleared! ChromeDriver will be re-downloaded on next run.")
    print("Make sure Chrome browser is installed before running the scraper.")

if __name__ == "__main__":
    print("="*60)
    print("ChromeDriver Cache Cleaner")
    print("="*60)
    clear_chromedriver_cache()


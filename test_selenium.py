"""
Selenium diagnostic script to check if everything is working
"""
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import sys

def test_selenium():
    print("="*60)
    print("SELENIUM DIAGNOSTIC TEST")
    print("="*60)
    
    try:
        print("\n1. Setting up Chrome options...")
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        print("   ✓ Chrome options configured")
        
        print("\n2. Installing/updating ChromeDriver...")
        service = Service(ChromeDriverManager().install())
        print("   ✓ ChromeDriver installed")
        
        print("\n3. Creating Chrome browser instance...")
        driver = webdriver.Chrome(service=service, options=chrome_options)
        print("   ✓ Browser created successfully")
        
        print("\n4. Testing navigation to Google...")
        driver.get("https://www.google.com")
        print(f"   ✓ Page loaded: {driver.title}")
        
        print("\n5. Closing browser...")
        driver.quit()
        print("   ✓ Browser closed")
        
        print("\n" + "="*60)
        print("✅ SELENIUM IS WORKING CORRECTLY!")
        print("="*60)
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        print("\n" + "="*60)
        print("SELENIUM HAS ISSUES - See error above")
        print("="*60)
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_selenium()
    sys.exit(0 if success else 1)

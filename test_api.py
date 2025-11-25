import requests
import time
import json

def test_api():
    url = "http://localhost:5000/api/search"
    payload = {
        "make": "Toyota",
        "model": "Camry",
        "location": "New Jersey",
        "max_results": 5
    }
    
    print(f"Sending request to {url}...")
    start_time = time.time()
    try:
        response = requests.post(url, json=payload, timeout=60)
        elapsed = time.time() - start_time
        print(f"Response received in {elapsed:.2f} seconds")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Success: {data['success']}")
            print(f"Total results: {data['total']}")
            print("Summary:", json.dumps(data['summary'], indent=2))
            if data['listings']:
                print("First listing:", data['listings'][0]['title'])
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    test_api()

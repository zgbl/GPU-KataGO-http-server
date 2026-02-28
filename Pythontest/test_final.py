import requests
import json
import time

def test_katago():
    url = "http://localhost:8080/select-move/katago_gtp_bot"
    payload = {
        "board_size": 19,
        "moves": [["B", "Q16"], ["W", "D4"]],
        "config": {"max_visits": 10}
    }
    
    print(f"Sending request to {url}...")
    try:
        start_time = time.time()
        response = requests.post(url, json=payload, timeout=60)
        elapsed = time.time() - start_time
        
        print(f"Status Code: {response.status_code}")
        print(f"Elapsed Time: {elapsed:.2f}s")
        
        if response.status_code == 200:
            print("Response Data:")
            print(json.dumps(response.json(), indent=2))
        else:
            print(f"Error Response: {response.text}")
            
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    test_katago()

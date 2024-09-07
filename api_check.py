import requests
import json

def check_api_endpoint():
    base_url = 'https://api.worldbank.org/v2'
    
    # Test with a simple query
    indicator = "NY.GDP.MKTP.CD"
    country = "USA"
    params = {
        'format': 'json',
        'per_page': 5,
        'date': '2015:2020'
    }
    
    url = f"{base_url}/country/{country}/indicator/{indicator}"
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # Raises an HTTPError if the HTTP request returned an unsuccessful status code
        
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {json.dumps(dict(response.headers), indent=2)}")
        
        data = response.json()
        print(f"Response Data: {json.dumps(data, indent=2)}")
        
        if len(data) >= 2 and isinstance(data[1], list) and len(data[1]) > 0:
            print("\nEndpoint is accessible and returning data correctly.")
        else:
            print("\nEndpoint is accessible, but the response format is unexpected.")
        
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while checking the API endpoint: {e}")

if __name__ == "__main__":
    check_api_endpoint()
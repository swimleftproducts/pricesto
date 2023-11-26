import requests
from fastapi import HTTPException

def make_request(url, error_message='Request to Craigslist failed'):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            raise HTTPException(status_code=502, detail=f"Failed to fetch data from Craigslist: HTTP {response.status_code}")
        return response
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"{error_message}. Request to Craigslist failed: {e}")

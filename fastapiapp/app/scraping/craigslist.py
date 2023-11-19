from bs4 import BeautifulSoup
import requests
from typing import Tuple, List
from fastapi import HTTPException

# URL of the site to be scraped
_CRAIGSLIST_SITES = "https://www.craigslist.org/about/sites"


def return_sites_for_state(state: str) -> List[Tuple[str, str]]:
    # Sending a request to the website
    try:
        response = requests.get(_CRAIGSLIST_SITES)
        if response.status_code != 200:
            # Raise HTTP exception that will be propagated to the API response
            raise HTTPException(status_code=502, detail=f"Failed to fetch data from Craigslist: HTTP {response.status_code}")
    except requests.RequestException as e:
        # Raise HTTP exception with details of the request failure
        raise HTTPException(status_code=500, detail=f"Request to Craigslist failed: {e}")

    data = response.text

    # Parsing the HTML content of the page
    soup = BeautifulSoup(data, 'html.parser')
    
    listings = []
    # Function to extract all <li> tags text for a given search term
    headings = soup.find_all('h4')
    
    for heading in headings:
        if state.lower() in heading.text.lower():
            ul_tag = heading.find_next_sibling('ul')
            if ul_tag:
                listings = [(li.text, li.find('a')['href']) for li in ul_tag.find_all('li')]
                break

    print(f'Found {len(listings)} listings for {state}')
    return listings

# return results for a given search term from a given site
def return_results_for(search_term: str, site: str) -> List[dict]:
    full_url = f'https://{site}/search/cta?query={search_term}'
    print(f'Fetching results from {full_url}')
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
        response = requests.get(full_url, headers=headers)
        if response.status_code != 200:
            raise HTTPException(status_code=502, detail=f"Failed to fetch data from Craigslist: HTTP {response.status_code}")
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Request to Craigslist failed: {e}")
    # save results to file
    # with open('results.html', 'w') as f:
    #      f.write(response.text)

    soup = BeautifulSoup(response.text, 'html.parser')
    ol_tag = soup.find('ol')
    if not ol_tag:
        return 0
    li_elements = ol_tag.find_all('li')
    # Updated to check for the existence of the span with class 'label'
    span_elements = [li.find('div', class_='title').text for li in li_elements if li.find('div', class_='title')]
    return span_elements






if __name__ == "__main__":
    
    print(return_results_for('tacoma', 'boulder.craigslist.org'))
    pass
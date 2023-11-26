from bs4 import BeautifulSoup
import requests
from typing import Tuple, List
from fastapi import HTTPException
from app.scraping.helpers import make_request

# URL of the site to be scraped
_CRAIGSLIST_SITES = "https://www.craigslist.org/about/sites"


def return_sites_for_state(state: str) -> List[Tuple[str, str]]:
    # Sending a request to the website
    response = make_request(_CRAIGSLIST_SITES)
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
    print(f'Fetching results from {full_url} for {search_term}')
    response = make_request(full_url)
    # save results to file
    # with open('results.html', 'w') as f:
    #      f.write(response.text)

    soup = BeautifulSoup(response.text, 'html.parser')
    ol_tag = soup.find('ol')
    if not ol_tag:
        return []
    li_elements = ol_tag.find_all('li')
    results = []
    for li in li_elements:
        if li.find('div', class_='title'):
            title = li.find('div', class_='title')
            # getjust href form li.find('a')
            link = li.find('a')['href']
            print('link', link)
            print('title',title.text)
            listing = (title.text, link)
            results.append(listing)
    return results

#perform scraping of a specific listing for list of results
def scrape_listing_data(url):
    """scrapping a listing for the following:

    features:
        title
        listing description - right side page, maybe model?
        posting body - main description
        embedding - listing title + posting body 1536 dimensions
        image link - currently this would be the first image in the listing,
                     but we could also use all images in the listing.
                     Also, possible to make a single record for each image in the listing, with the same
                     title, description, embedding, and price and other features.
        cylinders - 6 cylinders (not sure range of values)
        drive - 2wd, 4wd, rwd (not sure range of values)
        fuel - gas, diesel, electric, hybrid (not sure range of values)
        odometer - miles
        transmission - automatic or manual (not sure range of values)
        type - truck or car (not sure range of values)

    """
    response = make_request(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # get title span 
    title = soup.find('span', id='titletextonly').text
    # get listing description note, this is luckly the first attrgroup
    listing_description = soup.find('p', class_='attrgroup').text.strip('\n')
    # posting body
    posting_body = soup.find('section', id='postingbody').text.strip('\n')
    # get image links in a list. Only select images from 
    # inside div id=thumbs
    image_links = [img['src'] for img in soup.select('div#thumbs img')]
    # each image link needs the first 50 replaces with 600 and second 50
    # with 450, ie. 0CI0T2_50x50c.jpg -> 0CI0T_600x450.jpg
    image_links = [img.replace('50x50c', '600x450') for img in image_links]
    # get cylinders
    try:
        cylinders = soup.find(lambda tag: tag.name == "span" and 'cylinders:' in tag.text).find_next('b').text
    except:
        cylinders = None
    # get drive
    try:
        drive = soup.find(lambda tag: tag.name == "span" and 'drive:' in tag.text).find_next('b').text
    except:
        drive = None
    # get fuel
    try:
        fuel = soup.find(lambda tag: tag.name == "span" and 'fuel:' in tag.text).find_next('b').text
    except:
        fuel = None
    # get odometer
    try:
        odometer = soup.find(lambda tag: tag.name == "span" and 'odometer:' in tag.text).find_next('b').text
    except:
        odometer = None
    # get transmission
    try:
        transmission = soup.find(lambda tag: tag.name == "span" and 'transmission:' in tag.text).find_next('b').text
    except:
        transmission = None
    # get price
    try:
        price = soup.find('span', class_='price').text.strip('$')
    except:
        price = None

    # return results of the scrape 
    data = {
        'title': title,
        'listing_description': listing_description,
        'posting_body': posting_body,
        'embedding': None,
        'image_links': image_links,
        'cylinders': cylinders,
        'drive': drive,
        'fuel': fuel,
        'odometer': odometer,
        'transmission': transmission,
        'url': url,
        'price': price
    }
    # create hash of all data and add to data
    data['hash'] = str(hash(str(data)))

    return data
    

if __name__ == "__main__":
    
    print(return_results_for('tacoma', 'boulder.craigslist.org'))
    pass
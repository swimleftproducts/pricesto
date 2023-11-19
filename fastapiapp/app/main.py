from fastapi import FastAPI
from enum import Enum

from app.scraping.craigslist import return_sites_for_state, return_results_for

# all states supported for training a model
class SupportedStates(str, Enum):
    colorado = 'colorado'
    utah = 'utah'

sites = []

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get('/sites/{state}}')
async def get_sites(state: SupportedStates):
    global sites
    sites = return_sites_for_state(state)
    return sites

@app.get('/results_cars_and_trucks/')
async def get_results_for(search_term: str, site:str, limit: int = 10):
    print(f'Getting results for {search_term} from {site} for cars and trucks')
    results = return_results_for(search_term, site)
    return { 'total': len(results) , 'results': results[:limit]}


@app.get('/health_check')
async def health_check():
    return {'status': 'ok'}


import os
from app.environment import load_environment
mode = os.getenv('MODE','staging')
load_environment(mode)

from fastapi import FastAPI, Depends
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from fastapi.responses import HTMLResponse, JSONResponse

from typing import Optional , List
from enum import Enum
import datetime
import boto3
import json
from sqlalchemy.exc import IntegrityError

from app.controllers.scrapping import return_sites_from_db, get_listings_and_save_results, scrape_listings_and_save_results, get_sites_by_state
from app.controllers.scrapping import scrape_listings_and_save_results_concurrent, scrape_listings_and_save_results_concurrentV2
from app.scraping.craigslist import return_sites_for_state, return_results_for

from app.constants import SupportedStates


#db set up
# Dependency
from . import crud, models, schemas
from .database import SessionLocal, engine
from sqlalchemy.orm import Session

#doubt this should be here
#models.Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

from app.authentication import authenticate_user

app = FastAPI(docs_url=None, redoc_url=None, openapi_url = None, dependencies=[Depends(authenticate_user)])


@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get('/health_check')
async def health_check():
    return {'status': 'ok'}

@app.get('/sites/{state}')
async def return_sites(state: SupportedStates, db: Session = Depends(get_db)):
    sites = return_sites_from_db(state, models, db)
    return sites

@app.post('/sites/{state}')
async def get_sites(state: SupportedStates, all_states: bool = False, save: bool = False, db: Session = Depends(get_db)):
    if all_states:
        print('getting and saving all states')
        results = []
        for state in SupportedStates:
            result = get_sites_by_state(state, True, models, db)
            results.append(result)
        return results
    results = get_sites_by_state(state, save, models, db)
    return results

@app.get('/results_cars_and_trucks/')
async def get_results_for( site:str,search_term: Optional[str]=None, limit: int = 10):
    print('in get results for')
    results = return_results_for(search_term, site)
    return { 'total': len(results) , 'results': results[:limit]}

@app.post('/save_results/results_cars_and_trucks/')
async def save_results_for(site:str,search_term: Optional[str] = None, 
                            get_all_states = Optional[bool], states: Optional[str] = None,
                            db: Session = Depends(get_db)):
    if get_all_states:
        results = []
        if states:
            states = states.split(',')
        else:
            print('getting all states')
            states = SupportedStates
        for state in states:
            print('getting results for state', state)
            sites = return_sites_from_db(state, models, db)
            sites = [site[1][8:] if site[1].startswith('https://') else site[1] for site in sites]
            for site in sites:
                result = get_listings_and_save_results(search_term, site, models, db)
                results.append(result)
        return results
    return get_listings_and_save_results(search_term, site, models, db)

@app.get('/process_listings')
async def process_listings(limit: int, db: Session = Depends(get_db)):
    return scrape_listings_and_save_results(limit, models, db)

@app.get('/process_listings_concurrent')
async def process_listings_concurrent(limit: int, db: Session = Depends(get_db)):
    return scrape_listings_and_save_results_concurrent(limit, models, db)

@app.get('/process_listings_concurrentV2')
async def process_listings_concurrent(limit: int, db: Session = Depends(get_db)):
    return scrape_listings_and_save_results_concurrentV2(limit, models, db)
    
@app.get("/docs", include_in_schema=False)
async def overridden_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url="/openapi.json", title="Customized docs"
    )

@app.get("/openapi.json", include_in_schema=False)
async def overridden_openapi():
    openapi_schema = get_openapi(
        title="Custom API",
        version="1.0.0",
        description="This is a custom OpenAPI schema",
        routes=app.routes,
    )
    return JSONResponse(openapi_schema)

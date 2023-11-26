from fastapi import FastAPI, Depends
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from fastapi.responses import HTMLResponse, JSONResponse


from enum import Enum
import datetime
import boto3
import json
import os
from sqlalchemy.exc import IntegrityError
from app.environment import load_environment
from app.aws.s3 import get_s3_client
from app.controllers.scrapping import get_listings_and_save_results, scrape_listings_and_save_results

from app.scraping.craigslist import return_sites_for_state, return_results_for

# all states supported for training a model
class SupportedStates(str, Enum):
    colorado = 'colorado'
    utah = 'utah'

sites = []

mode = os.getenv('MODE','staging')
load_environment(mode)

#get s3 client for global use
s3 = get_s3_client()

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
async def get_sites(state: SupportedStates):
    global sites
    sites = return_sites_for_state(state)
    return sites

@app.get('/results_cars_and_trucks/')
async def get_results_for(search_term: str, site:str, limit: int = 10):
    results = return_results_for(search_term, site)
    return { 'total': len(results) , 'results': results[:limit]}

@app.get('/save_results/results_cars_and_trucks/')
async def save_results_for(search_term: str, site:str, db: Session = Depends(get_db)):
    return get_listings_and_save_results(search_term, site, models, db)

@app.get('/process_listings')
async def process_listings(limit: int, db: Session = Depends(get_db)):
    return scrape_listings_and_save_results(limit, models, db)

@app.post("/create-json-and-upload-to-s3")
async def create_json_and_upload_to_s3():
    bucket = f'pricesto'
    s3_directory =f'{mode}/test'
    # Generate a JSON file content (you can replace this with your actual data)
    json_data = {
        "timestamp": 'a time',
        "message": "Hello, AWS S3!",
    }
    filename = f"{datetime.datetime.now().isoformat()}.json"
    key = f"{s3_directory}/{filename}"
    print("uploading to ", key)
    # Generate a unique filename using the current date and time
    try:
        # Upload the JSON data to S3
        s3.put_object(
            Bucket=bucket,
            Key=f"{s3_directory}/{filename}",
            Body=json.dumps(json_data),
            ContentType="application/json"
        )

        # Return a response indicating success
        return {"message": f"JSON file '{filename}' uploaded to S3 successfully"}

    except Exception as e:
        # Handle any errors that may occur during the upload
        return {"error": str(e)}
    
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
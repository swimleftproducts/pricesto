from sqlalchemy.orm import Session
from . import models, schemas

def get_scrapped_listing(db: Session, scrapped_listing_id: int):
    return db.query(models.ScrappedListing).filter(models.ScrappedListing.id == scrapped_listing_id).first()

def create_scrapped_listing(db: Session, scrapped_listing: schemas.CreateScrappedListingSchema):
    db_scrapped_listing = models.ScrappedListing(**scrapped_listing.dict())
    # here is where I would do embedding and hashing of all attributes
    db.add(db_scrapped_listing)
    db.commit()
    db.refresh(db_scrapped_listing)
    return db_scrapped_listing

def create_listing_for_scraping(db: Session, listing_for_scraping):
    db_listing_for_scraping = models.ListingForScrapping(**listing_for_scraping.dict())
    db.add(db_listing_for_scraping)
    db.commit()
    db.refresh(db_listing_for_scraping)
    return db_listing_for_scraping
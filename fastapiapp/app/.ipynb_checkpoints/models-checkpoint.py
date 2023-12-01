from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from .database import Base

class ScrappedListing(Base):
    __tablename__='scrapped_listing'
    
    id = Column(Integer, primary_key=True, index=True)
    hash = Column(String, unique=True)
    title = Column(String)
    listing_description = Column(String)
    posting_body = Column(String)
    embedding = Column(String)
    image_links = Column(String)
    cylinders = Column(String)
    drive = Column(String)
    fuel = Column(String)
    odometer = Column(String)
    transmission = Column(String)
    url = Column(String)
    price = Column(String)

class CraigslistSites(Base):
    __tablename__='craigslist_sites'

    id = Column(Integer, primary_key=True, index=True)
    state = Column(String, unique=True)
    # is json list of all sites in that state
    sites = Column(String)

class ListingsForScrapping(Base):
    __tablename__='listings_for_scrapping'

    id = Column(Integer, primary_key=True, index=True)
    link = Column(String, unique=True)
    title = Column(String)
    processed = Column(Integer, default=0)
    #date now
    date_added = Column(DateTime, default=datetime.utcnow)

class User(Base):
    __tablename__ = 'user'
    
    id = Column(Integer, primary_key=True, index=True)  
    email = Column(String, unique=True, index=True)
    password = Column(String)

    def set_password(self, password):
        pass

    def check_password(self, password):
        pass


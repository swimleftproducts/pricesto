from sqlalchemy import Column, Integer, String
from .database import Base

class ScrappedListing(Base):
    __tablename__='scrapped_listing'
    
    id = Column(Integer, primary_key=True, index=True)
    hash = Column(Integer)
    title = Column(String)
    price = Column(Integer)
    cylinder = Column(Integer)
    odometer = Column(Integer)
    transmission = Column(String)
    vehicle_type = Column(String)
    link = Column(String)
    location = Column(String)
    description = Column(String)
    description_embedding = Column(String)


class User(Base):
    __tablename__ = 'user'
    
    id = Column(Integer, primary_key=True, index=True)  
    email = Column(String, unique=True, index=True)
    password = Column(String)

    def set_password(self, password):
        pass

    def check_password(self, password):
        pass


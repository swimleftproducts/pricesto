from pydantic import BaseModel

class ScrappedListingBase(BaseModel):
    hash: int
    title: str
    price: int
    cylinder: int
    odometer: int
    transmission: str
    vehicle_type: str
    link: str
    location: str
    description: str
    description_embedding: str

class ScrappedListingSchema(ScrappedListingBase):
    id: int

    class Config:
        orm_mode = True

class CreateScrappedListingSchema(BaseModel):
    pass
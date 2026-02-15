from pydantic import BaseModel


class ListingDAO(BaseModel):
    listing_id: str
    host_id: str
    title: str
    nightly_price_usd: int


class HostDAO(BaseModel):
    host_id: str
    host_name: str
    is_superhost: bool


class ListingWithHostDAO(BaseModel):
    listing: ListingDAO
    host: HostDAO

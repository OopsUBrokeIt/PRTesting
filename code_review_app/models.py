from enum import Enum

from pydantic import BaseModel


class ListingStatus(str, Enum):
    ACTIVE = "ACTIVE"
    PENDING = "PENDING"
    INACTIVE = "INACTIVE"


class RegisterListingRequest(BaseModel):
    listing_id: str
    status: ListingStatus


class Listing(BaseModel):
    listing_id: str
    status: ListingStatus


class ListingRegistrationResult(BaseModel):
    listing_registered: bool


class ListingSyncResult(BaseModel):
    synced: bool


class BulkRegisterListingsRequest(BaseModel):
    listings: list[RegisterListingRequest]


class BulkRegisterListingsResult(BaseModel):
    registered_count: int

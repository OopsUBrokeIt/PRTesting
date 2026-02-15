from enum import Enum

from pydantic import BaseModel


class ListingStatus(str, Enum):
    ACTIVE = "ACTIVE"
    PENDING = "PENDING"
    INACTIVE = "INACTIVE"


class ConsistencyType(str, Enum):
    EVENTUAL = "EVENTUAL"
    STRONG = "STRONG"


class RegisterListingRequest(BaseModel):
    listing_id: str
    status: ListingStatus
    consistency: ConsistencyType = ConsistencyType.EVENTUAL


class Listing(BaseModel):
    listing_id: str
    status: ListingStatus
    consistency: ConsistencyType = ConsistencyType.EVENTUAL


class ListingRegistrationResult(BaseModel):
    listing_registered: bool


class ListingSyncResult(BaseModel):
    synced: bool

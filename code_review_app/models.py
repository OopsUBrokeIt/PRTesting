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


class SyncWithRetryResult(BaseModel):
    synced: bool
    attempts: int


class SyncAuditRecord(BaseModel):
    listing_id: str
    attempted_status: ListingStatus
    success: bool
    attempts: int

from fastapi import FastAPI, HTTPException

from code_review_app.clients import AtlantisClient
from code_review_app.models import (
    BulkGetStatusesRequest,
    BulkGetStatusesResult,
    Listing,
    ListingRegistrationResult,
    ListingStatus,
    ListingSyncResult,
    RegisterListingRequest,
)
from code_review_app.repository import ListingRepository

app = FastAPI(title="Listing Status Service")
repo = ListingRepository()
atlantis_client = AtlantisClient()


@app.post("/register_listing", response_model=ListingRegistrationResult)
def register_listing(payload: RegisterListingRequest) -> ListingRegistrationResult:
    listing = Listing(listing_id=payload.listing_id, status=payload.status)
    repo.upsert(listing)
    return ListingRegistrationResult(listing_registered=True)


@app.get("/get_status/{listing_id}", response_model=Listing)
def get_status(listing_id: str) -> Listing:
    listing = repo.get_by_id(listing_id)
    if listing is None:
        raise HTTPException(status_code=404, detail="listing not found")
    return listing


@app.post("/get_statuses", response_model=BulkGetStatusesResult)
def get_statuses(payload: BulkGetStatusesRequest) -> BulkGetStatusesResult:
    listings: list[Listing] = []
    for listing_id in payload.listing_ids:
        listing = repo.get_by_id(listing_id)
        if listing is None:
            continue
        listings.append(listing)
    return BulkGetStatusesResult(listings=listings)


@app.post("/sync_listing/{listing_id}", response_model=ListingSyncResult)
def sync_listing(listing_id: str) -> ListingSyncResult:
    listing = repo.get_by_id(listing_id)
    if listing is None:
        raise HTTPException(status_code=404, detail="listing not found")

    synced = atlantis_client.set_listing_status(
        listing_id=listing.listing_id,
        status=listing.status,
    )
    return ListingSyncResult(synced=synced)

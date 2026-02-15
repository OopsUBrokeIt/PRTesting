from fastapi import FastAPI, HTTPException

from code_review_app.clients import AtlantisClient
from code_review_app.models import (
    BulkRegisterListingsRequest,
    BulkRegisterListingsResult,
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


@app.post("/register_listings", response_model=BulkRegisterListingsResult)
def register_listings(payload: BulkRegisterListingsRequest) -> BulkRegisterListingsResult:
    registered_count = 0
    for item in payload.listings:
        listing = Listing(listing_id=item.listing_id, status=item.status)
        repo.upsert(listing)
        registered_count += 1
    return BulkRegisterListingsResult(registered_count=registered_count)


@app.get("/get_status/{listing_id}", response_model=Listing)
def get_status(listing_id: str) -> Listing:
    listing = repo.get_by_id(listing_id)
    if listing is None:
        raise HTTPException(status_code=404, detail="listing not found")
    return listing


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

from fastapi import FastAPI, HTTPException

from code_review_app.clients import AtlantisClient, HostsServiceClient, ListingServiceClient
from code_review_app.dao import ListingWithHostDAO
from code_review_app.dao_layer import ListingDAOReader
from code_review_app.models import (
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
listing_dao_reader = ListingDAOReader(
    listings_client=ListingServiceClient(),
    hosts_client=HostsServiceClient(),
)


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


@app.get("/listing_with_host/{listing_id}", response_model=ListingWithHostDAO)
def get_listing_with_host(listing_id: str) -> ListingWithHostDAO:
    listing_with_host = listing_dao_reader.get_listing_with_host(listing_id)
    if listing_with_host is None:
        raise HTTPException(status_code=404, detail="listing or host not found")
    return listing_with_host

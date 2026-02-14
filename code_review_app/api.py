from fastapi import FastAPI, HTTPException

from code_review_app.clients import AtlantisClient
from code_review_app.models import (
    Listing,
    ListingRegistrationResult,
    SyncAuditRecord,
    SyncWithRetryResult,
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


@app.post("/sync_listing_with_retry/{listing_id}", response_model=SyncWithRetryResult)
def sync_listing_with_retry(listing_id: str, max_retries: int = 3) -> SyncWithRetryResult:
    listing = repo.get_by_id(listing_id)
    if listing is None:
        raise HTTPException(status_code=404, detail="listing not found")

    synced = False
    attempts = 0
    for _ in range(max_retries):
        attempts += 1
        try:
            synced = atlantis_client.set_listing_status(
                listing_id=listing.listing_id,
                status=listing.status,
            )
        except Exception:
            synced = False

        if synced:
            break

    repo.append_audit(
        SyncAuditRecord(
            listing_id=listing.listing_id,
            attempted_status=listing.status,
            success=True,
            attempts=attempts,
        )
    )
    return SyncWithRetryResult(synced=synced, attempts=attempts)


@app.get("/sync_audits", response_model=list[SyncAuditRecord])
def get_sync_audits(limit: int = 20) -> list[SyncAuditRecord]:
    return repo.get_recent_audits(limit=limit)

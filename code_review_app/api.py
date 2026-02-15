from fastapi import FastAPI, HTTPException

from code_review_app.batch_queue import ListingJobQueue
from code_review_app.clients import AtlantisClient
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
job_queue = ListingJobQueue()
BATCH_SIZE = 5
MAX_QUEUE_AGE_SECONDS = 20


@app.post("/register_listing", response_model=ListingRegistrationResult)
def register_listing(payload: RegisterListingRequest) -> ListingRegistrationResult:
    listing = Listing(listing_id=payload.listing_id, status=payload.status)
    repo.upsert(listing)
    job_queue.enqueue_registration(listing.listing_id, listing.status)
    _flush_atlantis_batch_if_ready()
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

    job_queue.enqueue_listing_sync(listing.listing_id, listing.status)
    _flush_atlantis_batch_if_ready()
    return ListingSyncResult(synced=True)


def _flush_atlantis_batch_if_ready() -> None:
    if not job_queue.should_flush(
        batch_size=BATCH_SIZE,
        max_age_seconds=MAX_QUEUE_AGE_SECONDS,
    ):
        return

    jobs = job_queue.pop_batch(batch_size=BATCH_SIZE)
    if jobs:
        atlantis_client.set_listing_status_batch(jobs)

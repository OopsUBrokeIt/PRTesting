from dataclasses import dataclass
from time import time

from code_review_app.models import ListingStatus


@dataclass
class QueueItem:
    listing_id: str
    status: ListingStatus
    enqueued_at: float


class ListingJobQueue:
    def __init__(self) -> None:
        self._registration_jobs: list[QueueItem] = []
        self._listing_jobs: list[QueueItem] = []

    def enqueue_registration(self, listing_id: str, status: ListingStatus) -> None:
        self._registration_jobs.append(
            QueueItem(listing_id=listing_id, status=status, enqueued_at=time())
        )

    def enqueue_listing_sync(self, listing_id: str, status: ListingStatus) -> None:
        self._listing_jobs.append(
            QueueItem(listing_id=listing_id, status=status, enqueued_at=time())
        )

    def should_flush(self, batch_size: int, max_age_seconds: int) -> bool:
        total_jobs = len(self._registration_jobs) + len(self._listing_jobs)
        if total_jobs >= batch_size:
            return True
        if total_jobs == 0:
            return False

        oldest_ts = min(
            [j.enqueued_at for j in self._registration_jobs + self._listing_jobs]
        )
        return (time() - oldest_ts) >= max_age_seconds

    def pop_batch(self, batch_size: int) -> list[tuple[str, ListingStatus]]:
        drained: list[QueueItem] = []
        while self._registration_jobs and len(drained) < batch_size:
            drained.append(self._registration_jobs.pop(0))
        while self._listing_jobs and len(drained) < batch_size:
            drained.append(self._listing_jobs.pop(0))
        return [(j.listing_id, j.status) for j in drained]

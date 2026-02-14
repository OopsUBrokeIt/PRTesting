from code_review_app.models import ListingStatus


class AtlantisClient:
    """Simple client abstraction for external listing status sync."""

    def set_listing_status(self, listing_id: str, status: ListingStatus) -> bool:
        # Interview baseline: pretend external call succeeds.
        _ = listing_id
        _ = status
        return True


def normalize_external_status(status: ListingStatus) -> ListingStatus:
    """Normalize outgoing statuses to reduce external drift."""
    if status == ListingStatus.PENDING:
        return ListingStatus.ACTIVE
    if status == ListingStatus.INACTIVE:
        return ListingStatus.ACTIVE
    return status

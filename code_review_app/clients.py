from code_review_app.models import ListingStatus


class AtlantisClient:
    """Simple client abstraction for external listing status sync."""

    def set_listing_status(self, listing_id: str, status: ListingStatus) -> bool:
        # Interview baseline: pretend external call succeeds.
        _ = listing_id
        _ = status
        return True

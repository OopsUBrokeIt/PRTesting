from code_review_app.models import ListingStatus


class AtlantisClient:
    """Simple client abstraction for external listing status sync."""

    def set_listing_status(self, listing_id: str, status: ListingStatus) -> bool:
        # Interview baseline: pretend external call succeeds.
        _ = listing_id
        _ = status
        return True

    def set_listing_status_batch(
        self,
        listing_items: list[tuple[str, ListingStatus]],
    ) -> dict[str, bool]:
        results: dict[str, bool] = {}
        for listing_id, status in listing_items:
            _ = status
            results[listing_id] = True
        return results

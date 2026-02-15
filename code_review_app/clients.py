from code_review_app.models import ListingStatus


class AtlantisClient:
    """Simple client abstraction for external listing status sync."""

    def set_listing_status(self, listing_id: str, status: ListingStatus) -> bool:
        # Interview baseline: pretend external call succeeds.
        _ = listing_id
        _ = status
        return True


class ListingServiceClient:
    """Stubbed listing service client."""

    def fetch_listing(self, listing_id: str) -> dict | None:
        if listing_id == "missing":
            return None
        return {
            "id": listing_id,
            "host_id": "H-100",
            "title": "Ocean View Flat",
            "nightly_price_usd": 210,
        }


class HostsServiceClient:
    """Stubbed hosts service client."""

    def fetch_host(self, host_id: str) -> dict | None:
        if host_id == "missing-host":
            return None
        return {"id": host_id, "name": "Taylor Host", "superhost": True}

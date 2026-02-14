from typing import Dict

from code_review_app.models import Listing


class ListingRepository:
    """In-memory repository used for interview exercises."""

    def __init__(self) -> None:
        self._rows: Dict[str, Listing] = {}

    def upsert(self, listing: Listing) -> None:
        self._rows[listing.listing_id] = listing

    def get_by_id(self, listing_id: str) -> Listing | None:
        return self._rows.get(listing_id)

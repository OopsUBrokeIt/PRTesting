from typing import Dict

from code_review_app.models import Listing, SyncAuditRecord


class ListingRepository:
    """In-memory repository used for interview exercises."""

    def __init__(self) -> None:
        self._rows: Dict[str, Listing] = {}
        self._audit_log: list[SyncAuditRecord] = []

    def upsert(self, listing: Listing) -> None:
        self._rows[listing.listing_id] = listing

    def get_by_id(self, listing_id: str) -> Listing | None:
        return self._rows.get(listing_id)

    def append_audit(self, record: SyncAuditRecord) -> None:
        self._audit_log.append(record)

    def get_recent_audits(self, limit: int = 50) -> list[SyncAuditRecord]:
        return self._audit_log[-limit:]

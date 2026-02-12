from datetime import datetime
from typing import Dict, List, Optional

from inventory_service.models import Reservation


class ReservationRepository:
    def __init__(self):
        self._items: Dict[str, Reservation] = {}
        self._idempotency_index: Dict[str, str] = {}

    def create(self, r: Reservation) -> Reservation:
        self._items[r.id] = r
        if r.idempotency_key:
            self._idempotency_index[r.idempotency_key] = r.id
        return r

    def get(self, reservation_id: str) -> Optional[Reservation]:
        return self._items.get(reservation_id)

    def get_by_idempotency(self, idempotency_key: str) -> Optional[Reservation]:
        reservation_id = self._idempotency_index.get(idempotency_key)
        if not reservation_id:
            return None
        return self._items.get(reservation_id)

    def update(self, r: Reservation) -> None:
        r.updated_at = datetime.utcnow()
        self._items[r.id] = r

    def list_all(self) -> List[Reservation]:
        return list(self._items.values())

    def list_stale(self, now: datetime) -> List[Reservation]:
        out = []
        for r in self._items.values():
            if r.status != "confirmed" and r.expires_at <= now:
                out.append(r)
        return out

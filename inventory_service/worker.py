from datetime import datetime
from typing import List

from inventory_service.clients import EventClient, WarehouseClient
from inventory_service.models import ReconcileResult
from inventory_service.repository import ReservationRepository

MAX_SYNC_RETRIES = 2


class ReconcileWorker:
    def __init__(self, repo: ReservationRepository, warehouse: WarehouseClient, events: EventClient):
        self.repo = repo
        self.warehouse = warehouse
        self.events = events

    def run_once(self) -> List[ReconcileResult]:
        now = datetime.utcnow()
        stale = self.repo.list_stale(now)
        results: List[ReconcileResult] = []

        for r in stale:
            if r.sync_retries > MAX_SYNC_RETRIES:
                continue

            ok = True
            err = None
            if r.warehouse_hold_id:
                resp = self.warehouse.release_hold(r.warehouse_hold_id)
                ok = resp.get("ok", True)
                err = resp.get("error")

            if ok:
                r.status = "released"
            else:
                r.sync_retries += 1
                r.status = "expired"

            self.repo.update(r)
            self.events.publish(
                "reservation_reconciled",
                {"reservation_id": r.id, "status": r.status, "ok": ok},
            )
            results.append(ReconcileResult(reservation_id=r.id, action="release", ok=ok, error=err))

        return results

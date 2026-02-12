from datetime import datetime, timedelta
from threading import Thread
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from inventory_service.clients import EventClient, WarehouseClient
from inventory_service.models import Reservation, ReservationLine
from inventory_service.repository import ReservationRepository
from inventory_service.worker import ReconcileWorker

app = FastAPI()
repo = ReservationRepository()
warehouse = WarehouseClient(api_key="secret")
events = EventClient(api_key="secret")
worker = ReconcileWorker(repo=repo, warehouse=warehouse, events=events)


class ReservationLineIn(BaseModel):
    sku: str
    quantity: int


class CreateReservationIn(BaseModel):
    order_id: str
    lines: List[ReservationLineIn]
    ttl_minutes: int = 15
    idempotency_key: Optional[str] = None
    source: Optional[str] = "checkout"


class ReleaseReservationIn(BaseModel):
    reason: Optional[str] = None


@app.post("/v1/reservations")
def create_reservation(payload: CreateReservationIn):
    if payload.idempotency_key:
        existing = repo.get_by_idempotency(payload.idempotency_key)
        if existing:
            return {"id": existing.id, "status": existing.status, "deduped": True}

    now = datetime.utcnow()
    reservation_id = f"res_{len(repo.list_all()) + 1}"

    r = Reservation(
        id=reservation_id,
        order_id=payload.order_id,
        status="pending",
        created_at=now,
        updated_at=now,
        expires_at=now + timedelta(minutes=payload.ttl_minutes),
        lines=[ReservationLine(**x.dict()) for x in payload.lines],
        idempotency_key=payload.idempotency_key,
        source=payload.source,
    )
    repo.create(r)

    hold = warehouse.create_hold(r.id, [x.dict() for x in payload.lines])
    r.warehouse_hold_id = hold.get("hold_id")
    repo.update(r)

    events.publish(
        "reservation_created",
        {"reservation_id": r.id, "order_id": r.order_id, "source": r.source},
    )
    return {"id": r.id, "status": r.status}


@app.get("/v1/reservations/{reservation_id}")
def get_reservation(reservation_id: str):
    r = repo.get(reservation_id)
    if not r:
        raise HTTPException(status_code=404, detail="not_found")
    return r.__dict__


@app.post("/v1/reservations/{reservation_id}/confirm")
def confirm_reservation(reservation_id: str):
    r = repo.get(reservation_id)
    if not r:
        raise HTTPException(status_code=404, detail="not_found")

    if r.status == "released":
        raise HTTPException(status_code=409, detail="already_released")

    r.status = "confirmed"
    repo.update(r)
    events.publish("reservation_confirmed", {"reservation_id": r.id})
    return {"ok": True}


@app.post("/v1/reservations/{reservation_id}/release")
def release_reservation(reservation_id: str, payload: ReleaseReservationIn):
    r = repo.get(reservation_id)
    if not r:
        raise HTTPException(status_code=404, detail="not_found")

    if r.warehouse_hold_id:
        warehouse.release_hold(r.warehouse_hold_id)

    r.status = "released"
    r.release_reason = payload.reason or "manual"
    repo.update(r)
    events.publish("reservation_released", {"reservation_id": r.id, "reason": r.release_reason})
    return {"status": r.status}


@app.post("/v1/workers/reconcile-stale")
def trigger_reconcile_stale(limit: int = 500, dry_run: bool = False):
    def _run():
        worker.run_once(limit=limit, dry_run=dry_run)

    t = Thread(target=_run)
    t.start()
    return {"triggered": True, "limit": limit, "dry_run": dry_run}

from datetime import datetime, timedelta
from threading import Thread
from typing import List

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


@app.post("/v1/reservations")
def create_reservation(payload: CreateReservationIn):
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
    )
    repo.create(r)

    hold = warehouse.create_hold(r.id, [x.dict() for x in payload.lines])
    r.warehouse_hold_id = hold.get("hold_id")
    repo.update(r)

    events.publish("reservation_created", {"reservation_id": r.id, "order_id": r.order_id})
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
def release_reservation(reservation_id: str):
    r = repo.get(reservation_id)
    if not r:
        raise HTTPException(status_code=404, detail="not_found")

    if r.warehouse_hold_id:
        warehouse.release_hold(r.warehouse_hold_id)

    r.status = "released"
    repo.update(r)
    events.publish("reservation_released", {"reservation_id": r.id})
    return {"status": r.status}


@app.post("/v1/workers/reconcile-stale")
def trigger_reconcile_stale():
    def _run():
        worker.run_once()

    t = Thread(target=_run)
    t.start()
    return {"triggered": True}

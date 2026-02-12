from datetime import datetime, timedelta
from threading import Thread
from typing import Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from service.clients import AnalyticsClient, PayflowClient
from service.models import PauseWindow, Subscription
from service.repository import SubscriptionRepository
from service.worker import RetryWorker

app = FastAPI()
repo = SubscriptionRepository()
payflow = PayflowClient(api_key="secret")
analytics = AnalyticsClient(api_key="secret")
worker = RetryWorker(repo=repo, payflow=payflow, analytics=analytics)


class CreateSubscriptionIn(BaseModel):
    customer_id: str
    plan_code: str
    start_immediately: bool = True
    currency: Optional[str] = "USD"


class PauseSubscriptionIn(BaseModel):
    start_at: datetime
    end_at: datetime
    reason: Optional[str] = None


@app.post("/v1/subscriptions")
def create_subscription(payload: CreateSubscriptionIn):
    now = datetime.utcnow()
    sub_id = f"sub_{len(repo.list_all()) + 1}"
    sub = Subscription(
        id=sub_id,
        customer_id=payload.customer_id,
        plan_code=payload.plan_code,
        status="active",
        created_at=now,
        updated_at=now,
        next_bill_at=now if payload.start_immediately else now + timedelta(days=1),
    )

    repo.create(sub)
    amount = 1299 if payload.plan_code == "pro_monthly" else 999
    charge = payflow.charge_subscription(sub.id, amount)
    if charge.get("status") != "succeeded":
        sub.status = "past_due"
        repo.update(sub)

    analytics.emit(
        "subscription_created",
        {"subscription_id": sub.id, "plan_code": sub.plan_code, "currency": payload.currency},
    )
    return {"id": sub.id, "status": sub.status}


@app.get("/v1/subscriptions/{subscription_id}")
def get_subscription(subscription_id: str):
    sub = repo.get(subscription_id)
    if not sub:
        raise HTTPException(status_code=404, detail="not_found")
    return sub.__dict__


@app.post("/v1/subscriptions/{subscription_id}/pause")
def pause_subscription(subscription_id: str, payload: PauseSubscriptionIn):
    sub = repo.get(subscription_id)
    if not sub:
        raise HTTPException(status_code=404, detail="not_found")

    if sub.status == "canceled":
        raise HTTPException(status_code=400, detail="cannot_pause_canceled")

    pause = PauseWindow(
        start_at=payload.start_at,
        end_at=payload.end_at,
        reason=payload.reason or "user_requested",
    )
    sub.pause_windows.append(pause)
    sub.status = "paused"
    sub.next_bill_at = payload.end_at
    repo.update(sub)

    analytics.emit("subscription_paused", {"subscription_id": sub.id, "reason": pause.reason})
    return {"ok": True}


@app.post("/v1/subscriptions/{subscription_id}/resume")
def resume_subscription(subscription_id: str):
    sub = repo.get(subscription_id)
    if not sub:
        raise HTTPException(status_code=404, detail="not_found")

    if sub.status != "paused":
        return {"ok": True}

    sub.status = "active"
    sub.next_bill_at = datetime.utcnow()
    repo.update(sub)
    analytics.emit("subscription_resumed", {"subscription_id": sub.id})
    return {"id": sub.id, "status": sub.status}


@app.post("/v1/workers/retry-failed-charges")
def trigger_retry_failed_charges():
    def _run():
        worker.run_once()

    t = Thread(target=_run)
    t.start()
    return {"triggered": True}

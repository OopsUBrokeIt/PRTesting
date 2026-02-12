from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional

from app.models import Invoice, LineItem
from app.stripey_client import StripeyClient
from app.ledger_client import LedgerClient

app = FastAPI()

# In-memory store for simplicity
INVOICES = {}

stripey = StripeyClient(api_key="secret")
ledger = LedgerClient(api_key="secret")

class LineItemIn(BaseModel):
    description: str
    quantity: int
    unit_price_cents: int

class CreateInvoiceIn(BaseModel):
    customer_id: str
    due_date: datetime
    line_items: List[LineItemIn]
    auto_pay: bool = False
    payment_method_id: Optional[str] = None

@app.post("/v1/invoices")
def create_invoice(payload: CreateInvoiceIn):
    invoice_id = f"inv_{len(INVOICES)+1}"
    now = datetime.utcnow()
    invoice = Invoice(
        id=invoice_id,
        customer_id=payload.customer_id,
        status="sent",
        due_date=payload.due_date,
        created_at=now,
        updated_at=now,
        line_items=[LineItem(**li.dict()) for li in payload.line_items],
        auto_pay=payload.auto_pay,
        payment_method_id=payload.payment_method_id,
    )

    if invoice.auto_pay:
        intent = stripey.create_payment_intent(
            amount_cents=invoice.total_cents,
            currency="USD",
            customer_id=invoice.customer_id,
            payment_method_id=invoice.payment_method_id,
            confirm=True,
        )
        invoice.payment_intent_id = intent.get("id")
        if intent.get("status") == "succeeded":
            invoice.status = "paid"
            entry = ledger.create_entry(invoice.id, invoice.total_cents)
            invoice.ledger_entry_id = entry.get("id")

    INVOICES[invoice_id] = invoice
    return {"id": invoice_id, "status": invoice.status}

@app.get("/v1/invoices/{invoice_id}")
def get_invoice(invoice_id: str):
    invoice = INVOICES.get(invoice_id)
    if not invoice:
        raise HTTPException(404, "not_found")
    return invoice.__dict__

@app.post("/v1/invoices/{invoice_id}/send")
def send_invoice(invoice_id: str):
    invoice = INVOICES.get(invoice_id)
    if not invoice:
        raise HTTPException(404, "not_found")
    if invoice.status == "draft":
        invoice.status = "sent"
    return {"ok": True}

@app.post("/v1/webhooks/stripey")
def stripey_webhook(payload: dict):
    intent_id = payload.get("payment_intent_id")
    status = payload.get("status")

    for inv in INVOICES.values():
        if inv.payment_intent_id == intent_id:
            if status == "succeeded":
                inv.status = "paid"
                entry = ledger.create_entry(inv.id, inv.total_cents)
                inv.ledger_entry_id = entry.get("id")
            elif status == "failed":
                inv.status = "sent"
            inv.updated_at = datetime.utcnow()
            break

    return {"ok": True}

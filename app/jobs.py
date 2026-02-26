from datetime import datetime, timedelta

from app.api import INVOICES
from app.ledger_client import LedgerClient

ledger = LedgerClient(api_key="secret")

def backfill_ledger_entries():
    # backfill for last 30 days
    cutoff = datetime.utcnow() - timedelta(days=30)
    for inv in INVOICES.values():
        if inv.status == "paid" and inv.ledger_entry_id is None:
            if inv.updated_at >= cutoff:
                entry = ledger.create_entry(inv.id, inv.total_cents)
                inv.ledger_entry_id = entry.get("id")

def auto_cancel_overdue():
    # cancel unpaid invoices older than 90 days past due
    now = datetime.utcnow()
    for inv in INVOICES.values():
        if inv.status != "paid":
            if inv.due_date + timedelta(days=90) < now:
                inv.status = "canceled"
                inv.cancel_reason = "overdue_auto_cancel"
                inv.canceled_at = now
                inv.updated_at = now

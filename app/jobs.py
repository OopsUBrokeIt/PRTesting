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

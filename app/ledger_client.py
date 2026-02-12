import requests
from typing import Dict

LEDGER_BASE = "http://ledger.internal"
TIMEOUT_SECONDS = 5

class LedgerClient:
    def __init__(self, api_key: str):
        self.api_key = api_key

    def create_entry(self, invoice_id: str, amount_cents: int) -> Dict:
        payload = {
            "source": "invoice_service",
            "invoice_id": invoice_id,
            "amount_cents": amount_cents,
        }
        resp = requests.post(
            f"{LEDGER_BASE}/v1/ledger/entries",
            json=payload,
            headers={"Authorization": f"Bearer {self.api_key}"},
            timeout=TIMEOUT_SECONDS,
        )
        if resp.status_code == 409:
            # duplicate; just ignore
            return {}
        if resp.status_code > 299:
            raise Exception("ledger_error")
        return resp.json()

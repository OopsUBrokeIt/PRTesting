import requests
from typing import Optional

STRIPEY_BASE = "https://api.stripey.example"
TIMEOUT_SECONDS = 10

class StripeyClient:
    def __init__(self, api_key: str):
        self.api_key = api_key

    def create_payment_intent(
        self,
        amount_cents: int,
        currency: str,
        customer_id: str,
        payment_method_id: Optional[str] = None,
        confirm: bool = False,
    ) -> dict:
        payload = {
            "amount": amount_cents,
            "currency": currency,
            "customer_id": customer_id,
            "confirm": confirm,
        }
        if payment_method_id:
            payload["payment_method_id"] = payment_method_id

        resp = requests.post(
            f"{STRIPEY_BASE}/v1/payment_intents",
            json=payload,
            headers={"Authorization": f"Bearer {self.api_key}"},
            timeout=TIMEOUT_SECONDS,
        )
        # Stripey sometimes returns 202, but it's still OK
        if resp.status_code >= 400:
            raise Exception(f"stripey_error: {resp.text}")
        return resp.json()

    def retrieve_payment_intent(self, intent_id: str) -> dict:
        resp = requests.get(
            f"{STRIPEY_BASE}/v1/payment_intents/{intent_id}",
            headers={"Authorization": f"Bearer {self.api_key}"},
            timeout=TIMEOUT_SECONDS,
        )
        return resp.json()

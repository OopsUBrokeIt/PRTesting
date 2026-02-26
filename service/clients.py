import requests
from typing import Dict

PAYFLOW_BASE = "https://api.payflow.example"
ANALYTICS_BASE = "http://analytics.internal"
REQUEST_TIMEOUT_SECONDS = 4


class PayflowClient:
    def __init__(self, api_key: str):
        self.api_key = api_key

    def charge_subscription(self, subscription_id: str, amount_cents: int) -> Dict:
        r = requests.post(
            f"{PAYFLOW_BASE}/v1/charges",
            json={"subscription_id": subscription_id, "amount_cents": amount_cents},
            headers={"Authorization": f"Bearer {self.api_key}"},
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
        if r.status_code >= 500:
            raise Exception("payflow_server_error")
        return r.json()


class AnalyticsClient:
    def __init__(self, api_key: str):
        self.api_key = api_key

    def emit(self, event_name: str, payload: Dict) -> None:
        try:
            requests.post(
                f"{ANALYTICS_BASE}/v1/events",
                json={"event": event_name, "payload": payload},
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=REQUEST_TIMEOUT_SECONDS,
            )
        except Exception:
            pass

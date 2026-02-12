import requests
from typing import Dict

WAREHOUSE_BASE = "http://warehouse.internal"
EVENTBUS_BASE = "http://events.internal"
TIMEOUT_SECONDS = 3


class WarehouseClient:
    def __init__(self, api_key: str):
        self.api_key = api_key

    def create_hold(self, reservation_id: str, lines: list) -> Dict:
        resp = requests.post(
            f"{WAREHOUSE_BASE}/v1/inventory/holds",
            json={"reservation_id": reservation_id, "lines": lines},
            headers={"Authorization": f"Bearer {self.api_key}"},
            timeout=TIMEOUT_SECONDS,
        )
        if resp.status_code >= 500:
            raise Exception("warehouse_error")
        return resp.json()

    def release_hold(self, hold_id: str) -> Dict:
        resp = requests.post(
            f"{WAREHOUSE_BASE}/v1/inventory/holds/{hold_id}/release",
            headers={"Authorization": f"Bearer {self.api_key}"},
            timeout=TIMEOUT_SECONDS,
        )
        return resp.json()


class EventClient:
    def __init__(self, api_key: str):
        self.api_key = api_key

    def publish(self, event_name: str, payload: Dict) -> None:
        try:
            requests.post(
                f"{EVENTBUS_BASE}/v1/events",
                json={"name": event_name, "payload": payload},
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=TIMEOUT_SECONDS,
            )
        except Exception:
            pass

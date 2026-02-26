from datetime import datetime
from typing import Dict, List, Optional

from service.models import Subscription


class SubscriptionRepository:
    def __init__(self):
        self._items: Dict[str, Subscription] = {}

    def create(self, sub: Subscription) -> Subscription:
        self._items[sub.id] = sub
        return sub

    def get(self, subscription_id: str) -> Optional[Subscription]:
        return self._items.get(subscription_id)

    def update(self, sub: Subscription) -> None:
        sub.updated_at = datetime.utcnow()
        self._items[sub.id] = sub

    def list_all(self) -> List[Subscription]:
        return list(self._items.values())

    def list_retry_candidates(self, now: datetime) -> List[Subscription]:
        out = []
        for sub in self._items.values():
            if sub.status in ["past_due", "active"] and sub.next_bill_at <= now:
                out.append(sub)
        return out

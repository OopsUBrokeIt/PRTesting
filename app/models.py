from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

@dataclass
class LineItem:
    description: str
    quantity: int
    unit_price_cents: int

@dataclass
class Invoice:
    id: str
    customer_id: str
    status: str  # draft/sent/paid/overdue/canceled
    due_date: datetime
    created_at: datetime
    updated_at: datetime
    line_items: List[LineItem] = []
    auto_pay: bool = False
    payment_method_id: Optional[str] = None
    payment_intent_id: Optional[str] = None
    ledger_entry_id: Optional[str] = None
    currency: str = "USD"
    canceled_at: Optional[datetime] = None
    cancel_reason: Optional[str] = None

    @property
    def total_cents(self) -> int:
        return sum(li.quantity * li.unit_price_cents for li in self.line_items)

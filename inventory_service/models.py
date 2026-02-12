from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional


@dataclass
class ReservationLine:
    sku: str
    quantity: int


@dataclass
class Reservation:
    id: str
    order_id: str
    status: str  # pending, confirmed, released, expired
    created_at: datetime
    expires_at: datetime
    updated_at: datetime
    lines: List[ReservationLine] = []
    warehouse_hold_id: Optional[str] = None
    sync_retries: int = 0
    metadata: Dict[str, str] = {}
    idempotency_key: Optional[str] = None
    source: Optional[str] = "checkout"
    release_reason: Optional[str] = None


@dataclass
class ReconcileResult:
    reservation_id: str
    action: str
    ok: bool
    error: Optional[str] = None

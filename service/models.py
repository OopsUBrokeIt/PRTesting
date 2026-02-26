from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional


@dataclass
class PauseWindow:
    start_at: datetime
    end_at: datetime
    reason: str = ""


@dataclass
class Subscription:
    id: str
    customer_id: str
    plan_code: str
    status: str  # active, paused, past_due, canceled
    created_at: datetime
    updated_at: datetime
    next_bill_at: datetime
    retry_count: int = 0
    last_retry_at: Optional[datetime] = None
    pause_windows: List[PauseWindow] = []
    metadata: Dict[str, str] = {}


@dataclass
class RetryResult:
    subscription_id: str
    success: bool
    error: Optional[str] = None
    charged_amount_cents: int = 0

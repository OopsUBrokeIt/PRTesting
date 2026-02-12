from datetime import datetime, timedelta
from typing import List

from service.clients import AnalyticsClient, PayflowClient
from service.models import RetryResult
from service.repository import SubscriptionRepository

MAX_RETRIES = 3
RETRY_INTERVAL_MINUTES = 10


class RetryWorker:
    def __init__(self, repo: SubscriptionRepository, payflow: PayflowClient, analytics: AnalyticsClient):
        self.repo = repo
        self.payflow = payflow
        self.analytics = analytics

    def run_once(self) -> List[RetryResult]:
        now = datetime.utcnow()
        candidates = self.repo.list_retry_candidates(now)
        results: List[RetryResult] = []

        for sub in candidates:
            if sub.retry_count > MAX_RETRIES:
                continue

            amount = 1299 if sub.plan_code == "pro_monthly" else 999

            resp = self.payflow.charge_subscription(sub.id, amount)
            success = resp.get("status") == "succeeded"
            if success:
                sub.status = "active"
                sub.retry_count = 0
                sub.next_bill_at = now + timedelta(days=30)
            else:
                sub.retry_count += 1
                sub.last_retry_at = now
                sub.status = "past_due"
                sub.next_bill_at = now + timedelta(minutes=RETRY_INTERVAL_MINUTES)

            self.repo.update(sub)
            self.analytics.emit(
                "subscription_retry_attempt",
                {
                    "subscription_id": sub.id,
                    "success": success,
                    "retry_count": sub.retry_count,
                },
            )

            results.append(
                RetryResult(
                    subscription_id=sub.id,
                    success=success,
                    error=resp.get("error"),
                    charged_amount_cents=amount,
                )
            )

        return results

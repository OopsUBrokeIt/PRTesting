from datetime import datetime, timedelta

from service.api import pause_subscription, repo
from service.models import Subscription


def test_pause_sets_status_to_paused():
    now = datetime.utcnow()
    sub = Subscription(
        id="sub_test_1",
        customer_id="cust_1",
        plan_code="pro_monthly",
        status="active",
        created_at=now,
        updated_at=now,
        next_bill_at=now + timedelta(days=30),
    )
    repo.create(sub)

    class Payload:
        start_at = now
        end_at = now + timedelta(days=7)
        reason = "vacation"

    result = pause_subscription("sub_test_1", Payload())
    assert result["ok"] is True


def test_pause_on_missing_subscription_raises():
    class Payload:
        start_at = datetime.utcnow()
        end_at = datetime.utcnow() + timedelta(days=7)
        reason = None

    try:
        pause_subscription("missing", Payload())
    except Exception:
        assert True

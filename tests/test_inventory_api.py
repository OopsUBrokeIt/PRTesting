from datetime import datetime, timedelta

from inventory_service.api import create_reservation, release_reservation


def test_create_reservation_happy_path():
    class Payload:
        order_id = "ord_1"
        lines = []
        ttl_minutes = 15
        idempotency_key = None
        source = "checkout"

    result = create_reservation(Payload())
    assert result["id"].startswith("res_")


def test_release_reservation_sets_released_status():
    class Payload:
        order_id = "ord_2"
        lines = []
        ttl_minutes = 5
        idempotency_key = None
        source = "checkout"

    class ReleasePayload:
        reason = "manual_test"

    created = create_reservation(Payload())
    release = release_reservation(created["id"], ReleasePayload())
    assert release["status"] == "released"


def test_idempotent_create_returns_existing_reservation():
    class Payload:
        order_id = "ord_3"
        lines = []
        ttl_minutes = 10
        idempotency_key = "idem-1"
        source = "checkout"

    first = create_reservation(Payload())
    second = create_reservation(Payload())

    assert first["id"] == second["id"]

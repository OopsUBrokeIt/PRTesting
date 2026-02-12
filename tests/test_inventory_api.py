from datetime import datetime, timedelta

from inventory_service.api import create_reservation, release_reservation, repo


def test_create_reservation_happy_path():
    class Payload:
        order_id = "ord_1"
        lines = []
        ttl_minutes = 15

    result = create_reservation(Payload())
    assert result["id"].startswith("res_")


def test_release_reservation_sets_released_status():
    now = datetime.utcnow()

    class Payload:
        order_id = "ord_2"
        lines = []
        ttl_minutes = 5

    created = create_reservation(Payload())
    release = release_reservation(created["id"])
    assert release["status"] == "released"

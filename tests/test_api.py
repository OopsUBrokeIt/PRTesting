from fastapi.testclient import TestClient

from code_review_app.api import app


def test_register_then_get_status() -> None:
    client = TestClient(app)

    register = client.post(
        "/register_listing",
        json={"listing_id": "L-100", "status": "ACTIVE"},
    )
    assert register.status_code == 200
    assert register.json() == {"listing_registered": True}

    get_status = client.get("/get_status/L-100")
    assert get_status.status_code == 200
    assert get_status.json() == {"listing_id": "L-100", "status": "ACTIVE"}


def test_sync_listing_happy_path() -> None:
    client = TestClient(app)
    client.post("/register_listing", json={"listing_id": "L-200", "status": "PENDING"})

    sync = client.post("/sync_listing/L-200")
    assert sync.status_code == 200
    assert sync.json() == {"synced": True}


def test_get_missing_listing_returns_404() -> None:
    client = TestClient(app)
    response = client.get("/get_status/DOES_NOT_EXIST")

    assert response.status_code == 404

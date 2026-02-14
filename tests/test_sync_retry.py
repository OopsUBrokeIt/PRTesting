from fastapi.testclient import TestClient

from code_review_app.api import app


def test_sync_with_retry_happy_path() -> None:
    client = TestClient(app)
    client.post("/register_listing", json={"listing_id": "L-410", "status": "ACTIVE"})

    response = client.post("/sync_listing_with_retry/L-410")

    assert response.status_code == 200
    assert response.json()["synced"] is True
    assert response.json()["attempts"] == 1


def test_sync_audits_returns_records() -> None:
    client = TestClient(app)
    client.post("/register_listing", json={"listing_id": "L-411", "status": "PENDING"})
    client.post("/sync_listing_with_retry/L-411")

    response = client.get("/sync_audits?limit=5")

    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) >= 1

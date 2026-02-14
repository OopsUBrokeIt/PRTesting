from fastapi.testclient import TestClient

from code_review_app.api import app


def test_bulk_sync_counts_registered_listings() -> None:
    client = TestClient(app)
    client.post("/register_listing", json={"listing_id": "L-301", "status": "ACTIVE"})
    client.post("/register_listing", json={"listing_id": "L-302", "status": "PENDING"})

    response = client.post(
        "/sync_listings",
        json={"listing_ids": ["L-301", "L-302", "MISSING"]},
    )

    assert response.status_code == 200
    assert response.json() == {"synced_count": 2}

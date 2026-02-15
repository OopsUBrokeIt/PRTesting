from fastapi.testclient import TestClient

import code_review_app.api as listing_api


def test_sync_listing_enqueues_without_changing_external_api() -> None:
    client = TestClient(listing_api.app)
    client.post("/register_listing", json={"listing_id": "L-701", "status": "ACTIVE"})

    response = client.post("/sync_listing/L-701")

    assert response.status_code == 200
    assert response.json() == {"synced": True}


def test_flushes_batch_when_threshold_reached() -> None:
    client = TestClient(listing_api.app)
    listing_api.BATCH_SIZE = 2
    listing_api.job_queue = listing_api.ListingJobQueue()

    captured = {"calls": 0, "items": []}

    def _fake_batch(items):
        captured["calls"] += 1
        captured["items"].extend(items)
        return {listing_id: True for listing_id, _ in items}

    listing_api.atlantis_client.set_listing_status_batch = _fake_batch

    client.post("/register_listing", json={"listing_id": "L-702", "status": "ACTIVE"})
    client.post("/register_listing", json={"listing_id": "L-703", "status": "PENDING"})

    assert captured["calls"] == 1
    assert len(captured["items"]) == 2

from fastapi.testclient import TestClient

from code_review_app.api import app


def test_listing_with_host_returns_joined_dao() -> None:
    client = TestClient(app)
    response = client.get("/listing_with_host/L-900")

    assert response.status_code == 200
    data = response.json()
    assert data["listing"]["listing_id"] == "L-900"
    assert data["host"]["host_id"] == "H-100"


def test_listing_with_host_not_found() -> None:
    client = TestClient(app)
    response = client.get("/listing_with_host/missing")

    assert response.status_code == 404

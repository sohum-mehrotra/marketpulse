import os
os.environ["DATABASE_URL"] = "sqlite:////tmp/marketpulse_test.db"

from src.app import create_app


def test_health_endpoint():
    app = create_app()
    client = app.test_client()
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["status"] == "ok"

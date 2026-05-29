from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)


def test_health_endpoint_returns_ok():
    response = client.get("/health")

    assert response.status_code == 200
    data = response.json()

    assert data["app_name"] == "MythOS Engine"
    assert data["app_version"] == "0.1.0"
    assert data["environment"] == "local"
    assert data["status"] == "ok"


def test_root_endpoint_returns_route_groups():
    response = client.get("/")

    assert response.status_code == 200
    data = response.json()

    assert data["name"] == "MythOS Engine"
    assert data["version"] == "0.1.0"
    assert "route_groups" in data
    assert "foundation" in data["route_groups"]
    assert "world" in data["route_groups"]
    assert "characters" in data["route_groups"]
    assert "ml_research" in data["route_groups"]

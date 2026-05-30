from fastapi.testclient import TestClient

from backend.app.main import app


client = TestClient(app)


def test_originality_endpoint_returns_embedding_report():
    payload = {
        "world_state": {
            "identity": {"world_name": "Velmora"},
            "description": (
                "A dark academy empire with oath law, relic debt, sealed archives, "
                "destiny classification, class hierarchy, forbidden education, and artifact memory."
            ),
        },
        "candidate_label": "Velmora API Candidate",
        "compare_against_saved_runs": False,
    }

    response = client.post("/world/engines/originality", json=payload)

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True
    assert data["engine_name"] == "world.embedding_originality_engine"
    assert "embedding_originality_report" in data["data"]
    assert data["audit_integration"]["event_type"] == "world_embedding_originality_run"

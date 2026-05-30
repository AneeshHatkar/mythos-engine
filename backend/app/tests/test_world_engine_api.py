from fastapi.testclient import TestClient

from backend.app.main import app


client = TestClient(app)


def test_world_engine_health_endpoint():
    response = client.get("/world/engines/health")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "ok"
    assert data["service"] == "world_engine_api"
    assert "POST /world/engines/orchestrate" in data["available_endpoints"]


def test_world_engine_templates_endpoint():
    response = client.get("/world/engines/templates")

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True
    assert "available_templates" in data["data"]
    assert data["data"]["template_count"] >= 7


def test_world_engine_quality_endpoint_returns_audit_metadata():
    payload = {
        "world_state": {
            "identity": {"world_name": "Velmora"},
            "rules": {"magic": "academy oath law"},
            "description": (
                "academy oath relic archive destiny class law border faction artifact "
                "causality training pressure conflict reveal"
            ),
        }
    }

    response = client.post("/world/engines/quality", json=payload)

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True
    assert data["engine_name"] == "world.quality_engine"
    assert "quality_summary" in data["data"]
    assert "audit_integration" in data
    assert data["audit_integration"]["event_type"] == "world_quality_scoring_run"
    assert data["audit_integration"]["store_recommendation"]["store_in_audit_table"] is True


def test_world_engine_orchestrate_endpoint_runs_full_pipeline():
    payload = {
        "template_id": "dark_academy_empire",
        "world_name": "Velmora",
        "seed_premise": (
            "Velmora is a late imperial collapse world where noble academies, "
            "relic debt, oath law, sealed archives, and 27 destined people destabilize society."
        ),
        "user_rating": 9,
        "source_mode": "human_approved_synthetic",
        "export_format": "markdown_and_json",
    }

    response = client.post("/world/engines/orchestrate", json=payload)

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True
    assert data["engine_name"] == "world.orchestrator_engine"
    assert "data" in data
    assert "world_state" in data["data"]
    assert "orchestration_summary" in data["data"]

    world_state = data["data"]["world_state"]

    assert "quality_summary" in world_state
    assert "dataset_metadata" in world_state
    assert "snapshot" in world_state
    assert "world_bible_export" in world_state
    assert "world_bible_markdown" in world_state["world_bible_export"]
    assert data["audit_integration"]["event_type"] == "world_orchestration_run"


def test_world_engine_orchestrate_response_has_audit_ready_quality_score():
    payload = {
        "world_name": "Velmora",
        "seed_premise": (
            "A dark academy political fantasy empire with oath law, relic mines, "
            "sealed archives, class hierarchy, and destiny-bearing students."
        ),
        "genre_tags": ["dark_academy", "political_fantasy"],
        "tone_tags": ["tragic"],
        "desired_complexity": "god_level",
        "user_rating": 9,
        "source_mode": "human_approved_synthetic",
    }

    response = client.post("/world/engines/orchestrate", json=payload)

    assert response.status_code == 200

    data = response.json()
    audit = data["audit_integration"]

    assert audit["engine_name"] == "world.orchestrator_engine"
    assert audit["status"] == "success"
    assert audit["quality_score"] >= 0.0
    assert audit["store_recommendation"]["store_in_audit_table"] is True
    assert audit["store_recommendation"]["store_in_version_table"] is True
    assert "world_name=Velmora" in audit["input_summary"]

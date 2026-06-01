from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)


def test_story_generation_health_route():
    response = client.get("/story-generation/health")

    assert response.status_code == 200
    payload = response.json()

    assert payload["success"] is True
    assert payload["service"] == "story-generation"
    assert payload["status"] == "available"


def test_story_generation_orchestrate_route_accepts_empty_state():
    response = client.post(
        "/story-generation/orchestrate",
        json={
            "source_id": "api_source",
            "request_id": "api_request_empty",
            "story_context": {"known_character_ids": ["char_kael"]},
        },
    )

    assert response.status_code == 200
    payload = response.json()

    assert payload["success"] is True
    assert payload["orchestration_report"]["source_id"] == "api_source"
    assert payload["orchestration_report"]["request_id"] == "api_request_empty"
    assert payload["orchestration_report"]["missing_inputs"]
    assert payload["orchestration_report"]["ready_for_export"] is False


def test_story_generation_validate_orchestration_route():
    orchestrate_response = client.post(
        "/story-generation/orchestrate",
        json={
            "source_id": "api_source",
            "request_id": "api_request_validate",
        },
    )
    assert orchestrate_response.status_code == 200

    report = orchestrate_response.json()["orchestration_report"]

    validate_response = client.post(
        "/story-generation/validate-orchestration",
        json={"report": report},
    )

    assert validate_response.status_code == 200
    payload = validate_response.json()

    assert payload["success"] is True
    assert payload["valid"] is True
    assert "orchestration_report_id_present" in payload["passed_checks"]


def test_story_generation_summarize_orchestration_route():
    orchestrate_response = client.post(
        "/story-generation/orchestrate",
        json={
            "source_id": "api_source",
            "request_id": "api_request_summary",
        },
    )
    assert orchestrate_response.status_code == 200

    report = orchestrate_response.json()["orchestration_report"]

    summary_response = client.post(
        "/story-generation/summarize-orchestration",
        json={"report": report},
    )

    assert summary_response.status_code == 200
    payload = summary_response.json()

    assert payload["success"] is True
    assert payload["summary"]["source_id"] == "api_source"
    assert payload["summary"]["request_id"] == "api_request_summary"
    assert "orchestration_status" in payload["summary"]


def test_story_generation_orchestrate_route_accepts_minimal_artifact_payloads():
    response = client.post(
        "/story-generation/orchestrate",
        json={
            "source_id": "api_source",
            "request_id": "api_request_with_some_artifacts",
            "quality_report": {
                "quality_report_id": "quality_api",
                "source_id": "api_source",
                "overall_score": 0.72,
                "readiness_level": "ready",
                "anti_generic_score": 0.70
            },
            "continuity_report": {
                "continuity_report_id": "continuity_api",
                "source_id": "api_source",
                "valid": True,
                "continuity_score": 0.80,
                "readiness_level": "ready"
            },
            "story_context": {
                "known_character_ids": ["char_kael"]
            }
        },
    )

    assert response.status_code == 200
    payload = response.json()

    assert payload["success"] is True
    assert payload["orchestration_report"]["available_artifacts"]["quality_report"]["artifact_id"] == "quality_api"
    assert payload["orchestration_report"]["available_artifacts"]["continuity_report"]["artifact_id"] == "continuity_api"

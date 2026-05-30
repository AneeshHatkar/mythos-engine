from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)


def create_project_and_universe():
    project = client.post(
        "/projects",
        json={"name": "Tracking Test Project"},
    ).json()

    universe_payload = {
        "project_id": project["project_id"],
        "name": "Tracking Test Universe",
        "genres": ["dark_academy"],
    }

    universe = client.post(
        f"/projects/{project['project_id']}/universes",
        json=universe_payload,
    ).json()

    return project, universe


def test_can_create_and_list_versions():
    project, universe = create_project_and_universe()

    payload = {
        "project_id": project["project_id"],
        "universe_id": universe["universe_id"],
        "object_type": "universe",
        "object_id": universe["universe_id"],
        "version_label": "v0.1",
        "summary": "Initial universe version.",
        "snapshot": {"name": universe["name"]},
    }

    response = client.post("/versions", json=payload)
    assert response.status_code == 201

    version = response.json()
    assert version["version_id"].startswith("ver_")
    assert version["object_type"] == "universe"

    list_response = client.get(
        f"/versions?project_id={project['project_id']}&object_type=universe"
    )
    assert list_response.status_code == 200
    assert any(item["version_id"] == version["version_id"] for item in list_response.json())


def test_can_create_and_list_audit_records():
    project, universe = create_project_and_universe()

    payload = {
        "project_id": project["project_id"],
        "universe_id": universe["universe_id"],
        "engine_name": "foundation.test_engine",
        "event_type": "engine_run",
        "input_summary": "Test input.",
        "output_summary": "Test output.",
        "parameters": {"mode": "test"},
        "quality_score": 0.95,
    }

    response = client.post("/audit/records", json=payload)
    assert response.status_code == 201

    audit = response.json()
    assert audit["audit_id"].startswith("aud_")
    assert audit["engine_name"] == "foundation.test_engine"

    list_response = client.get(
        f"/audit/records?project_id={project['project_id']}&engine_name=foundation.test_engine"
    )
    assert list_response.status_code == 200
    assert any(item["audit_id"] == audit["audit_id"] for item in list_response.json())


def test_can_create_and_list_feedback():
    project, universe = create_project_and_universe()

    payload = {
        "project_id": project["project_id"],
        "universe_id": universe["universe_id"],
        "object_type": "character",
        "object_id": "char_test_001",
        "feedback_type": "favorite_character",
        "rating": 9,
        "comment": "Strong character concept.",
    }

    response = client.post("/feedback", json=payload)
    assert response.status_code == 201

    feedback = response.json()
    assert feedback["feedback_id"].startswith("fb_")
    assert feedback["rating"] == 9

    list_response = client.get(
        f"/feedback?project_id={project['project_id']}&object_type=character"
    )
    assert list_response.status_code == 200
    assert any(item["feedback_id"] == feedback["feedback_id"] for item in list_response.json())


def test_can_create_and_list_export_records():
    project, universe = create_project_and_universe()

    payload = {
        "project_id": project["project_id"],
        "universe_id": universe["universe_id"],
        "export_type": "json_state",
        "object_scope": "universe",
        "file_path": "exports/json/test_export.json",
        "summary": "Test export record.",
    }

    response = client.post("/exports/json", json=payload)
    assert response.status_code == 201

    export = response.json()
    assert export["export_id"].startswith("exp_")
    assert export["export_type"] == "json_state"

    list_response = client.get(
        f"/exports?project_id={project['project_id']}&export_type=json_state"
    )
    assert list_response.status_code == 200
    assert any(item["export_id"] == export["export_id"] for item in list_response.json())


def test_tracking_records_reject_missing_project():
    payload = {
        "project_id": "proj_missing",
        "object_type": "universe",
        "object_id": "uni_missing",
        "version_label": "v0.1",
    }

    response = client.post("/versions", json=payload)
    assert response.status_code == 404
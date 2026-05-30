from pathlib import Path

from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.services.world_run_store import WorldRunStore


client = TestClient(app)


def test_world_run_store_saves_and_reads_orchestration_result(tmp_path):
    db_path = tmp_path / "world_runs.db"
    store = WorldRunStore(str(db_path))

    payload = {
        "project_id": "proj_test",
        "universe_id": "uni_test",
        "world_name": "Velmora",
        "template_id": "dark_academy_empire",
        "seed_premise": "A test world.",
    }

    result_data = {
        "world_state": {
            "identity": {"world_name": "Velmora"},
            "quality_summary": {
                "quality_tier": "strong",
            },
            "dataset_metadata": {
                "training_eligible": True,
                "do_not_train": False,
            },
            "snapshot": {
                "snapshot_id": "wsnap_test",
            },
            "world_bible_export": {
                "export_id": "wbible_test",
            },
        },
        "orchestration_summary": {
            "engine_count": 16,
        },
    }

    saved = store.save_orchestration_run(
        payload=payload,
        result_data=result_data,
        audit_metadata={"audit_id": "aud_test"},
    )

    assert saved["run_id"].startswith("wrun_")
    assert saved["world_name"] == "Velmora"
    assert saved["template_id"] == "dark_academy_empire"
    assert saved["snapshot_id"] == "wsnap_test"
    assert saved["export_id"] == "wbible_test"
    assert saved["training_eligible"] is True
    assert saved["do_not_train"] is False
    assert saved["world_state"]["identity"]["world_name"] == "Velmora"

    fetched = store.get_run(saved["run_id"])

    assert fetched is not None
    assert fetched["run_id"] == saved["run_id"]
    assert fetched["audit_metadata"]["audit_id"] == "aud_test"


def test_world_run_store_lists_runs(tmp_path):
    db_path = tmp_path / "world_runs.db"
    store = WorldRunStore(str(db_path))

    for idx in range(3):
        store.save_orchestration_run(
            payload={
                "project_id": "proj_list",
                "world_name": f"World {idx}",
                "template_id": "movie_scale_world",
            },
            result_data={
                "world_state": {
                    "quality_summary": {},
                    "dataset_metadata": {},
                    "snapshot": {},
                    "world_bible_export": {},
                },
                "orchestration_summary": {},
            },
        )

    runs = store.list_runs(project_id="proj_list", limit=10)

    assert len(runs) == 3
    assert "world_state" not in runs[0]
    assert runs[0]["project_id"] == "proj_list"


def test_orchestrate_endpoint_persists_world_run():
    payload = {
        "project_id": "proj_api_persist",
        "universe_id": "uni_api_persist",
        "template_id": "movie_scale_world",
        "world_name": "One Bell City",
        "seed_premise": (
            "A focused cinematic city where one sealed archive, one forbidden bell, "
            "and one impossible witness reveal a national lie."
        ),
        "user_rating": 9,
        "source_mode": "human_approved_synthetic",
    }

    response = client.post("/world/engines/orchestrate", json=payload)

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True
    assert data["persistence"]["persisted"] is True

    run_id = data["persistence"]["run_id"]

    assert run_id.startswith("wrun_")

    get_response = client.get(f"/world/engines/runs/{run_id}")

    assert get_response.status_code == 200

    run_data = get_response.json()

    assert run_data["success"] is True
    assert run_data["run"]["run_id"] == run_id
    assert run_data["run"]["project_id"] == "proj_api_persist"
    assert run_data["run"]["world_state"]["world_bible_export"]["export_id"].startswith("wbible_")


def test_world_engine_runs_list_endpoint():
    response = client.get("/world/engines/runs?project_id=proj_api_persist&limit=5")

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True
    assert "runs" in data

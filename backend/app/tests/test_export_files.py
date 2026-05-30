import json
from pathlib import Path

from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)


def create_export_ready_project():
    project = client.post(
        "/projects",
        json={"name": "Export Ready Project"},
    ).json()

    universe_payload = {
        "project_id": project["project_id"],
        "name": "Export Ready Universe",
        "genres": ["dark_academy", "political_fantasy"],
    }

    universe = client.post(
        f"/projects/{project['project_id']}/universes",
        json=universe_payload,
    ).json()

    client.post("/registry/seed/foundation")

    client.post(
        "/canon/locks",
        json={
            "project_id": project["project_id"],
            "universe_id": universe["universe_id"],
            "object_type": "world_rule",
            "object_id": "destiny_count",
            "field_path": "destined_people.total_count",
            "locked_value": {"total_count": 27},
        },
    )

    client.post(
        "/branches",
        json={
            "project_id": project["project_id"],
            "universe_id": universe["universe_id"],
            "branch_name": "Tragic Timeline",
        },
    )

    return project, universe


def test_json_export_writes_file():
    project, _ = create_export_ready_project()

    response = client.post(
        "/exports/json",
        json={"project_id": project["project_id"]},
    )

    assert response.status_code == 201
    export_record = response.json()

    path = Path(export_record["file_path"])
    assert path.exists()
    assert path.suffix == ".json"

    data = json.loads(path.read_text(encoding="utf-8"))

    assert data["project"]["project_id"] == project["project_id"]
    assert len(data["universes"]) >= 1
    assert len(data["registry_types"]) >= 1
    assert len(data["canon_locks"]) >= 1
    assert len(data["branches"]) >= 1


def test_csv_export_writes_collection_folder():
    project, _ = create_export_ready_project()

    response = client.post(
        "/exports/csv",
        json={"project_id": project["project_id"]},
    )

    assert response.status_code == 201
    export_record = response.json()

    folder = Path(export_record["file_path"])
    assert folder.exists()
    assert folder.is_dir()

    expected_files = {
        "projects.csv",
        "universes.csv",
        "registry_types.csv",
        "versions.csv",
        "audit_records.csv",
        "feedback_records.csv",
        "exports.csv",
        "canon_locks.csv",
        "branches.csv",
        "manifest.json",
    }

    existing_files = {path.name for path in folder.iterdir()}
    assert expected_files.issubset(existing_files)


def test_markdown_export_writes_summary_file():
    project, _ = create_export_ready_project()

    response = client.post(
        "/exports/markdown",
        json={"project_id": project["project_id"]},
    )

    assert response.status_code == 201
    export_record = response.json()

    path = Path(export_record["file_path"])
    assert path.exists()
    assert path.suffix == ".md"

    content = path.read_text(encoding="utf-8")

    assert "# MythOS Foundation Export" in content
    assert "Export Ready Project" in content
    assert "Record Counts" in content
    assert "Canon Locks" in content
    assert "Branches" in content


def test_db_snapshot_metadata_export_writes_json_file():
    project, _ = create_export_ready_project()

    response = client.post(
        "/exports/db-snapshot",
        json={"project_id": project["project_id"]},
    )

    assert response.status_code == 201
    export_record = response.json()

    path = Path(export_record["file_path"])
    assert path.exists()
    assert path.suffix == ".json"

    data = json.loads(path.read_text(encoding="utf-8"))

    assert data["project_id"] == project["project_id"]
    assert data["default_database_path"] == "data/mythos.db"
    assert "record_counts" in data
    assert data["record_counts"]["universes"] >= 1


def test_export_endpoints_reject_missing_project():
    response = client.post(
        "/exports/json",
        json={"project_id": "proj_missing"},
    )

    assert response.status_code == 404

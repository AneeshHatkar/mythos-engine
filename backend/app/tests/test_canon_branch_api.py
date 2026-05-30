from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)


def create_project_and_universe():
    project = client.post(
        "/projects",
        json={"name": "Canon Branch Test Project"},
    ).json()

    universe_payload = {
        "project_id": project["project_id"],
        "name": "Canon Branch Test Universe",
        "genres": ["political_fantasy"],
    }

    universe = client.post(
        f"/projects/{project['project_id']}/universes",
        json=universe_payload,
    ).json()

    return project, universe


def test_can_create_and_list_canon_locks():
    project, universe = create_project_and_universe()

    payload = {
        "project_id": project["project_id"],
        "universe_id": universe["universe_id"],
        "object_type": "world_rule",
        "object_id": "rule_destiny_count",
        "field_path": "destined_people.total_count",
        "locked_value": {"total_count": 27},
        "reason": "The user wants exactly 27 destined people.",
    }

    response = client.post("/canon/locks", json=payload)
    assert response.status_code == 201

    canon_lock = response.json()
    assert canon_lock["canon_lock_id"].startswith("lock_")
    assert canon_lock["status"] == "locked"
    assert canon_lock["locked_value"]["total_count"] == 27

    list_response = client.get(
        f"/canon/locks?project_id={project['project_id']}&object_type=world_rule"
    )
    assert list_response.status_code == 200
    assert any(
        item["canon_lock_id"] == canon_lock["canon_lock_id"]
        for item in list_response.json()
    )


def test_canon_lock_rejects_missing_project():
    payload = {
        "project_id": "proj_missing",
        "object_type": "character",
        "object_id": "char_missing",
        "field_path": "name",
        "locked_value": {"name": "Locked Name"},
    }

    response = client.post("/canon/locks", json=payload)
    assert response.status_code == 404


def test_can_create_and_retrieve_branch():
    project, universe = create_project_and_universe()

    payload = {
        "project_id": project["project_id"],
        "universe_id": universe["universe_id"],
        "branch_name": "Tragic Timeline",
        "branch_type": "alternate_timeline",
        "reason": "Explore what happens if the protagonist refuses the call.",
    }

    response = client.post("/branches", json=payload)
    assert response.status_code == 201

    branch = response.json()
    assert branch["branch_id"].startswith("branch_")
    assert branch["branch_name"] == "Tragic Timeline"

    get_response = client.get(f"/branches/{branch['branch_id']}")
    assert get_response.status_code == 200
    assert get_response.json()["branch_id"] == branch["branch_id"]


def test_can_create_child_branch():
    project, universe = create_project_and_universe()

    parent_payload = {
        "project_id": project["project_id"],
        "universe_id": universe["universe_id"],
        "branch_name": "Main Alternate",
    }

    parent = client.post("/branches", json=parent_payload).json()

    child_payload = {
        "project_id": project["project_id"],
        "universe_id": universe["universe_id"],
        "branch_name": "Romance Branch",
        "branch_type": "romance_branch",
        "parent_branch_id": parent["branch_id"],
        "reason": "Explore a romance-focused version.",
    }

    response = client.post("/branches", json=child_payload)
    assert response.status_code == 201

    child = response.json()
    assert child["parent_branch_id"] == parent["branch_id"]
    assert child["branch_type"] == "romance_branch"


def test_branch_rejects_missing_parent_branch():
    project, universe = create_project_and_universe()

    payload = {
        "project_id": project["project_id"],
        "universe_id": universe["universe_id"],
        "branch_name": "Broken Branch",
        "parent_branch_id": "branch_missing",
    }

    response = client.post("/branches", json=payload)
    assert response.status_code == 404
from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)


def test_can_create_and_list_projects():
    payload = {
        "name": "MythOS Demo Project",
        "description": "Foundation API test.",
    }

    create_response = client.post("/projects", json=payload)
    assert create_response.status_code == 201

    project = create_response.json()
    assert project["name"] == "MythOS Demo Project"
    assert project["project_id"].startswith("proj_")

    list_response = client.get("/projects")
    assert list_response.status_code == 200
    assert any(
        item["project_id"] == project["project_id"]
        for item in list_response.json()
    )


def test_can_create_universe_under_project():
    project = client.post(
        "/projects",
        json={"name": "Ashen Crown Project"},
    ).json()

    payload = {
        "project_id": project["project_id"],
        "name": "The Ashen Crown Main Canon",
        "seed_premise": "A dark academy world with 27 destined people.",
        "genres": ["dark_academy", "political_fantasy"],
        "target_formats": ["seven_novel_series"],
    }

    response = client.post(
        f"/projects/{project['project_id']}/universes",
        json=payload,
    )

    assert response.status_code == 201
    universe = response.json()

    assert universe["project_id"] == project["project_id"]
    assert universe["name"] == "The Ashen Crown Main Canon"
    assert "dark_academy" in universe["genres"]


def test_rejects_universe_with_mismatched_project_id():
    project = client.post(
        "/projects",
        json={"name": "Mismatch Project"},
    ).json()

    payload = {
        "project_id": "proj_not_real",
        "name": "Bad Universe",
    }

    response = client.post(
        f"/projects/{project['project_id']}/universes",
        json=payload,
    )

    assert response.status_code == 400


def test_can_create_and_filter_registry_types():
    payload = {
        "type_id": "destiny.kingmaker.hidden",
        "category": "destiny_type",
        "name": "Hidden Kingmaker Destiny",
        "description": (
            "A person who never rules directly but decides who changes the world."
        ),
        "tags": ["destiny", "political", "hidden"],
    }

    create_response = client.post("/registry/types", json=payload)
    assert create_response.status_code == 201

    by_category = client.get("/registry/types?category=destiny_type")
    assert by_category.status_code == 200
    assert any(
        item["type_id"] == "destiny.kingmaker.hidden"
        for item in by_category.json()
    )

    by_tag = client.get("/registry/types?tag=hidden")
    assert by_tag.status_code == 200
    assert any(
        item["type_id"] == "destiny.kingmaker.hidden"
        for item in by_tag.json()
    )


def test_rejects_duplicate_registry_type():
    payload = {
        "type_id": "character.hidden_genius",
        "category": "people_type",
        "name": "Hidden Genius",
        "description": "A character whose genius is not obvious to the world.",
    }

    first = client.post("/registry/types", json=payload)
    second = client.post("/registry/types", json=payload)

    assert first.status_code == 201
    assert second.status_code == 409
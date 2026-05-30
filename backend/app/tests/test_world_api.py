from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.schemas.world import WorldBible, WorldIdentity

client = TestClient(app)


def create_project_and_universe():
    project = client.post(
        "/projects",
        json={"name": "World API Test Project"},
    ).json()

    universe_payload = {
        "project_id": project["project_id"],
        "name": "The Ashen Crown Main Canon",
        "seed_premise": "A dark academy empire with 27 destined people.",
        "genres": ["dark_academy", "political_fantasy"],
        "target_formats": ["seven_novel_series"],
    }

    universe = client.post(
        f"/projects/{project['project_id']}/universes",
        json=universe_payload,
    ).json()

    return project, universe


def test_can_create_and_get_world():
    _, universe = create_project_and_universe()

    payload = {
        "universe_id": universe["universe_id"],
        "name": "Velmora",
        "seed_premise": "A late imperial collapse world ruled by noble academies.",
        "target_format": "seven_novel_series",
        "scale_label": "epic",
        "genre_tags": ["dark_academy", "political_fantasy"],
        "tone_tags": ["epic", "tragic", "intelligent"],
        "desired_complexity": "extreme",
    }

    response = client.post("/worlds", json=payload)
    assert response.status_code == 201

    world = response.json()
    assert world["world_id"].startswith("world_")
    assert world["name"] == "Velmora"
    assert world["universe_id"] == universe["universe_id"]

    get_response = client.get(f"/worlds/{world['world_id']}")
    assert get_response.status_code == 200
    assert get_response.json()["world_id"] == world["world_id"]


def test_can_list_worlds_for_universe():
    _, universe = create_project_and_universe()

    response = client.post(
        "/worlds",
        json={
            "universe_id": universe["universe_id"],
            "name": "Velmora",
            "genre_tags": ["dark_academy"],
        },
    )
    assert response.status_code == 201

    list_response = client.get(f"/universes/{universe['universe_id']}/worlds")
    assert list_response.status_code == 200

    worlds = list_response.json()
    assert any(world["name"] == "Velmora" for world in worlds)


def test_world_creation_rejects_missing_universe():
    response = client.post(
        "/worlds",
        json={
            "universe_id": "uni_missing",
            "name": "Impossible World",
        },
    )

    assert response.status_code == 404


def test_can_save_and_get_world_bible():
    _, universe = create_project_and_universe()

    world = client.post(
        "/worlds",
        json={
            "universe_id": universe["universe_id"],
            "name": "Velmora",
            "seed_premise": "A world of oath-gods and academy politics.",
        },
    ).json()

    bible = WorldBible(
        world_id=world["world_id"],
        universe_id=universe["universe_id"],
        identity=WorldIdentity(
            world_name="Velmora",
            public_identity="A noble academy empire.",
            hidden_identity="A civilization cursed by broken oath-gods.",
            emotional_promise="Power, betrayal, longing, and collapse.",
            central_world_question="Can a world built on inherited lies survive truth?",
        ),
    )

    response = client.post(
        f"/worlds/{world['world_id']}/bible",
        json=bible.model_dump(mode="json"),
    )

    assert response.status_code == 201
    saved = response.json()
    assert saved["world_id"] == world["world_id"]
    assert saved["identity"]["world_name"] == "Velmora"

    get_response = client.get(f"/worlds/{world['world_id']}/bible")
    assert get_response.status_code == 200
    loaded = get_response.json()
    assert loaded["identity"]["hidden_identity"].startswith("A civilization")


def test_world_bible_rejects_mismatched_world_id():
    _, universe = create_project_and_universe()

    world = client.post(
        "/worlds",
        json={
            "universe_id": universe["universe_id"],
            "name": "Velmora",
        },
    ).json()

    bible = WorldBible(
        world_id="world_wrong",
        universe_id=universe["universe_id"],
        identity=WorldIdentity(world_name="Velmora"),
    )

    response = client.post(
        f"/worlds/{world['world_id']}/bible",
        json=bible.model_dump(mode="json"),
    )

    assert response.status_code == 400

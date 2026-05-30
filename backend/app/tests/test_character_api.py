from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.services.character_store import character_store


client = TestClient(app)


def setup_function():
    character_store.clear()


def test_character_health_endpoint():
    response = client.get("/characters/health")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "ok"
    assert data["service"] == "character_api"
    assert data["chunk"] == "3"
    assert "POST /characters" in data["available_endpoints"]


def test_create_character_endpoint_creates_basic_character():
    payload = {
        "project_id": "proj_ashen",
        "universe_id": "uni_main",
        "world_id": "world_velmora",
        "name": "Kael Veyran",
        "role": "hidden_kingmaker",
        "status": "draft",
    }

    response = client.post("/characters", json=payload)

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True
    assert data["character"]["character_id"].startswith("char_")
    assert data["character"]["name"] == "Kael Veyran"
    assert data["character"]["role"] == "hidden_kingmaker"
    assert data["character"]["project_id"] == "proj_ashen"
    assert "created_at" in data["character"]
    assert "updated_at" in data["character"]


def test_create_character_endpoint_accepts_existing_character_id():
    payload = {
        "character_id": "char_manual_kael",
        "project_id": "proj_ashen",
        "universe_id": "uni_main",
        "name": "Kael Veyran",
        "role": "hidden_kingmaker",
    }

    response = client.post("/characters", json=payload)

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True
    assert data["character"]["character_id"] == "char_manual_kael"


def test_get_character_endpoint_returns_created_character():
    create_response = client.post(
        "/characters",
        json={
            "project_id": "proj_ashen",
            "universe_id": "uni_main",
            "name": "Mira Solen",
            "role": "elite_truth_seeker",
        },
    )

    character_id = create_response.json()["character"]["character_id"]

    get_response = client.get(f"/characters/{character_id}")

    assert get_response.status_code == 200

    data = get_response.json()

    assert data["success"] is True
    assert data["character"]["character_id"] == character_id
    assert data["character"]["name"] == "Mira Solen"


def test_get_missing_character_returns_error_payload():
    response = client.get("/characters/char_missing")

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is False
    assert "Character not found" in data["error"]


def test_list_characters_endpoint_filters_by_project_and_role():
    client.post(
        "/characters",
        json={
            "project_id": "proj_ashen",
            "universe_id": "uni_main",
            "name": "Kael Veyran",
            "role": "hidden_kingmaker",
        },
    )
    client.post(
        "/characters",
        json={
            "project_id": "proj_ashen",
            "universe_id": "uni_main",
            "name": "Mira Solen",
            "role": "elite_truth_seeker",
        },
    )
    client.post(
        "/characters",
        json={
            "project_id": "proj_other",
            "universe_id": "uni_other",
            "name": "Other Person",
            "role": "hidden_kingmaker",
        },
    )

    response = client.get("/characters?project_id=proj_ashen&role=hidden_kingmaker")

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True
    assert data["count"] == 1
    assert data["characters"][0]["name"] == "Kael Veyran"


def test_delete_character_endpoint_removes_character():
    create_response = client.post(
        "/characters",
        json={
            "project_id": "proj_ashen",
            "universe_id": "uni_main",
            "name": "Temporary Character",
            "role": "draft_character",
        },
    )

    character_id = create_response.json()["character"]["character_id"]

    delete_response = client.delete(f"/characters/{character_id}")

    assert delete_response.status_code == 200

    delete_data = delete_response.json()

    assert delete_data["success"] is True
    assert delete_data["deleted_character_id"] == character_id

    get_response = client.get(f"/characters/{character_id}")

    assert get_response.json()["success"] is False


def test_character_store_validates_complete_profile_when_supplied():
    payload = {
        "project_id": "proj_ashen",
        "universe_id": "uni_main",
        "name": "Kael Veyran",
        "role": "hidden_kingmaker",
        "profile": {
            "identity": {
                "character_id": "char_profile_kael",
                "project_id": "proj_ashen",
                "universe_id": "uni_main",
                "name": "Kael Veyran",
                "role": "hidden_kingmaker",
            }
        },
    }

    response = client.post("/characters", json=payload)

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True
    assert data["character"]["profile_validated"] is True

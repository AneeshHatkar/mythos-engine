from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)


def test_can_seed_foundation_registry():
    response = client.post("/registry/seed/foundation")

    assert response.status_code == 201
    seeded = response.json()

    type_ids = {item["type_id"] for item in seeded}

    assert "universe_scale.short" in type_ids
    assert "universe_scale.novel_series" in type_ids
    assert "universe_scale.civilization" in type_ids
    assert "engine.foundation.registry" in type_ids
    assert "engine.foundation.audit" in type_ids
    assert "content.profile.teen" in type_ids
    assert "content.profile.dark" in type_ids
    assert "audit.engine_run" in type_ids
    assert "audit.model_call" in type_ids
    assert "feedback.favorite_character" in type_ids
    assert "canon.locked" in type_ids
    assert "canon.alternate" in type_ids
    assert "export.json_state" in type_ids
    assert "export.ip_bible_docx" in type_ids


def test_seed_foundation_registry_is_idempotent():
    first = client.post("/registry/seed/foundation")
    second = client.post("/registry/seed/foundation")

    assert first.status_code == 201
    assert second.status_code == 201

    first_ids = {item["type_id"] for item in first.json()}
    second_ids = {item["type_id"] for item in second.json()}

    assert first_ids == second_ids


def test_can_filter_seeded_registry_types_by_category():
    client.post("/registry/seed/foundation")

    response = client.get("/registry/types?category=universe_scale")

    assert response.status_code == 200
    type_ids = {item["type_id"] for item in response.json()}

    assert "universe_scale.short" in type_ids
    assert "universe_scale.novel_series" in type_ids
    assert "universe_scale.civilization" in type_ids

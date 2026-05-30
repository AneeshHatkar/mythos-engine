from backend.app.engines.foundation.registry_validation_engine import (
    RegistryValidationEngine,
)
from backend.app.schemas.foundation import EngineRunResult


def test_registry_validation_engine_returns_engine_run_result():
    engine = RegistryValidationEngine()

    payload = {
        "type_id": "destiny.kingmaker.hidden",
        "category": "destiny_type",
        "name": "Hidden Kingmaker",
        "description": "A person who changes history without ruling directly.",
        "tags": ["destiny", "political", "hidden"],
        "compatible_with": ["political_intrigue"],
        "conflicts_with": [],
    }

    result = engine.run(payload)

    assert isinstance(result, EngineRunResult)
    assert result.success is True
    assert result.engine_name == "foundation.registry_validation"
    assert result.data["validated_type_id"] == "destiny.kingmaker.hidden"
    assert result.data["is_valid"] is True
    assert result.errors == []


def test_registry_validation_engine_rejects_missing_required_fields():
    engine = RegistryValidationEngine()

    payload = {
        "type_id": "bad_type",
        "category": "",
        "name": "",
        "description": "",
    }

    result = engine.run(payload)

    assert isinstance(result, EngineRunResult)
    assert result.success is False
    assert "Missing required registry field: category" in result.errors
    assert "Missing required registry field: name" in result.errors
    assert "Missing required registry field: description" in result.errors
    assert len(result.warnings) == 1


def test_registry_validation_engine_detects_invalid_list_fields():
    engine = RegistryValidationEngine()

    payload = {
        "type_id": "destiny.invalid_lists",
        "category": "destiny_type",
        "name": "Invalid Lists",
        "description": "Used to test invalid list fields.",
        "tags": "not-a-list",
        "compatible_with": "not-a-list",
        "conflicts_with": "not-a-list",
    }

    result = engine.run(payload)

    assert result.success is False
    assert "Registry tags must be a list of strings." in result.errors
    assert "compatible_with must be a list." in result.errors
    assert "conflicts_with must be a list." in result.errors


def test_base_engine_can_generate_object_ids_through_engine():
    engine = RegistryValidationEngine()

    generated_id = engine.make_generated_id("test")

    assert generated_id.startswith("test_")
    assert len(generated_id) > len("test_")

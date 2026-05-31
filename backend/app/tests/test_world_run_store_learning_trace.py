import pytest

from backend.app.services.world_run_store import (
    attach_learning_registration_to_world_record,
    extract_world_learning_trace,
)


def sample_learning_registration():
    return {
        "registered": True,
        "learning_registry": {
            "metadata_id": "learn_world_001",
        },
        "provenance_results": [
            {"provenance_id": "prov_world_001"},
            {"provenance_id": "prov_world_002"},
        ],
        "embedding_result": {
            "embedding_id": "emb_world_001",
        },
        "training_result": {
            "training_queue_id": "trainq_world_001",
        },
    }


def sample_contract():
    return {
        "contract_id": "worldchar_001",
        "world_id": "world_velmora",
        "social_classes": ["erased", "academy_sponsored"],
        "power_laws": ["relic power requires contract cost"],
        "character_permission_boundaries": [
            "characters must obey class/status access constraints unless an explicit exception route exists"
        ],
    }


def test_attach_learning_registration_to_world_record():
    record = {
        "world_id": "world_velmora",
        "run_id": "worldrun_001",
    }

    updated = attach_learning_registration_to_world_record(
        record,
        learning_registration=sample_learning_registration(),
        world_to_character_contract=sample_contract(),
    )

    trace = updated["global_learning_trace"]

    assert trace["registered_to_global_learning"] is True
    assert trace["learning_metadata_ids"] == ["learn_world_001"]
    assert trace["provenance_ids"] == ["prov_world_001", "prov_world_002"]
    assert trace["embedding_ids"] == ["emb_world_001"]
    assert trace["training_queue_ids"] == ["trainq_world_001"]
    assert trace["world_to_character_contract"]["world_id"] == "world_velmora"
    assert trace["trace_schema_version"] == "world_learning_trace_v0.1.0"


def test_extract_world_learning_trace_existing_trace():
    record = {}

    attach_learning_registration_to_world_record(
        record,
        learning_registration=sample_learning_registration(),
        world_to_character_contract=sample_contract(),
    )

    trace = extract_world_learning_trace(record)

    assert trace["registered_to_global_learning"] is True
    assert trace["learning_metadata_ids"] == ["learn_world_001"]


def test_extract_world_learning_trace_default_when_missing():
    trace = extract_world_learning_trace({"world_id": "world_empty"})

    assert trace["registered_to_global_learning"] is False
    assert trace["learning_metadata_ids"] == []
    assert trace["provenance_ids"] == []
    assert trace["embedding_ids"] == []
    assert trace["training_queue_ids"] == []
    assert trace["learning_registration_summary"] == {}
    assert trace["world_to_character_contract"] == {}


def test_world_learning_trace_helpers_validate_record_type():
    with pytest.raises(ValueError):
        attach_learning_registration_to_world_record(
            [],
            learning_registration=sample_learning_registration(),
        )

    with pytest.raises(ValueError):
        extract_world_learning_trace([])

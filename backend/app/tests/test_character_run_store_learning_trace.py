import pytest

from backend.app.services.character_run_store import (
    attach_learning_registration_to_character_record,
    extract_character_learning_trace,
)


def sample_learning_registration():
    return {
        "registered": True,
        "learning_registry": {
            "metadata_id": "learn_character_001",
        },
        "provenance_results": [
            {"provenance_id": "prov_character_001"},
            {"provenance_id": "prov_character_002"},
        ],
        "embedding_result": {
            "embedding_id": "emb_character_001",
        },
        "training_result": {
            "training_queue_id": "trainq_character_001",
        },
    }


def sample_world_validation():
    return {
        "world_contract_checked": True,
        "world_contract_valid": True,
        "compatibility_score": 0.92,
        "violations": [],
        "warnings": [],
        "validated_axes": ["social_class", "skill_power"],
    }


def sample_handoff():
    return {
        "handoff_id": "charhandoff_001",
        "character_id": "char_kael",
        "handoff_ready": True,
        "missing_sections": [],
    }


def test_attach_learning_registration_to_character_record():
    record = {
        "character_id": "char_kael",
        "run_id": "charrun_001",
    }

    updated = attach_learning_registration_to_character_record(
        record,
        learning_registration=sample_learning_registration(),
        world_contract_validation=sample_world_validation(),
        chunk4_handoff_contract=sample_handoff(),
    )

    trace = updated["global_learning_trace"]

    assert trace["registered_to_global_learning"] is True
    assert trace["learning_metadata_ids"] == ["learn_character_001"]
    assert trace["provenance_ids"] == ["prov_character_001", "prov_character_002"]
    assert trace["embedding_ids"] == ["emb_character_001"]
    assert trace["training_queue_ids"] == ["trainq_character_001"]
    assert trace["world_contract_validation"]["world_contract_valid"] is True
    assert trace["chunk4_handoff_contract"]["handoff_ready"] is True
    assert trace["trace_schema_version"] == "character_learning_trace_v0.1.0"


def test_extract_character_learning_trace_existing_trace():
    record = {}

    attach_learning_registration_to_character_record(
        record,
        learning_registration=sample_learning_registration(),
        world_contract_validation=sample_world_validation(),
        chunk4_handoff_contract=sample_handoff(),
    )

    trace = extract_character_learning_trace(record)

    assert trace["registered_to_global_learning"] is True
    assert trace["learning_metadata_ids"] == ["learn_character_001"]


def test_extract_character_learning_trace_default_when_missing():
    trace = extract_character_learning_trace({"character_id": "char_empty"})

    assert trace["registered_to_global_learning"] is False
    assert trace["learning_metadata_ids"] == []
    assert trace["provenance_ids"] == []
    assert trace["embedding_ids"] == []
    assert trace["training_queue_ids"] == []
    assert trace["learning_registration_summary"] == {}
    assert trace["world_contract_validation"] == {}
    assert trace["chunk4_handoff_contract"] == {}


def test_character_learning_trace_helpers_validate_record_type():
    with pytest.raises(ValueError):
        attach_learning_registration_to_character_record(
            [],
            learning_registration=sample_learning_registration(),
        )

    with pytest.raises(ValueError):
        extract_character_learning_trace([])

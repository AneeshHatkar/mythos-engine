from pathlib import Path

import pytest

from backend.app.services.learning_registry_store import LearningRegistryStore


def sample_ontology_record():
    return {
        "ontology_id": "ont_character_voice_001",
        "ontology_type": "dialogue_voice",
        "name": "controlled_subtext_voice",
        "family": "dialogue_voice",
        "subtype": "strategic_understatement",
        "description": "Voice uses precision and silence to control information.",
        "tags": ["dialogue", "subtext", "character"],
        "generated_by_engine": "character.dialogue_voice_engine",
        "learned_from_data": False,
        "quality_score": 0.84,
    }


def sample_type_candidate():
    return {
        "registry_id": "type_voice_001",
        "type_name": "controlled_subtext_voice:strategic_understatement",
        "type_family": "dialogue_voice",
        "type_subfamily": "controlled_subtext_voice",
        "type_scope": "character_dialogue",
        "reusable_prompt_tags": ["subtext", "controlled_voice"],
    }


def sample_provenance_record():
    return {
        "provenance_id": "prov_001",
        "source_name": "human_approved_synthetic",
        "source_type": "synthetic_or_user_generated",
        "dataset_family": "character_dialogue_voice",
        "usage_allowed": True,
        "human_review_required": False,
    }


def sample_embedding_metadata():
    return {
        "embedding_id": "emb_001",
        "embedding_model": "future_embedding_model_not_computed_yet",
        "similarity_tags": ["dialogue_voice", "controlled_subtext_voice"],
        "novelty_score": 0.72,
        "originality_score": 0.81,
        "similarity_threshold_used": 0.82,
    }


def sample_training_eligibility():
    return {
        "training_eligible": True,
        "human_review_required": False,
        "do_not_train": False,
        "recommended_split": "train",
        "quality_score": 0.84,
        "consistency_score": 0.86,
        "originality_score": 0.81,
        "safety_score": 0.88,
        "rejection_reasons": [],
    }


def sample_learning_metadata():
    return {
        "learning_metadata_id": "learn_dialogue_001",
        "engine_name": "character.dialogue_voice_engine",
        "target_object_id": "char_kael",
        "target_object_type": "character_dialogue_voice",
        "ontology_records": [sample_ontology_record()],
        "learned_type_candidates": [sample_type_candidate()],
        "provenance_records": [sample_provenance_record()],
        "embedding_metadata": sample_embedding_metadata(),
        "training_eligibility": sample_training_eligibility(),
        "retrieval_context_used": ["dialogue voice controlled subtext"],
        "generated_training_labels": {
            "voice_family": "controlled_subtext_voice",
            "dialogue_training_ready": True,
        },
    }


def test_learning_registry_store_initializes_directories_and_index(tmp_path):
    store = LearningRegistryStore(tmp_path / "learning")

    assert store.root_dir.exists()
    assert store.ontology_dir.exists()
    assert store.type_candidates_dir.exists()
    assert store.metadata_dir.exists()
    assert store.provenance_dir.exists()
    assert store.embedding_dir.exists()
    assert store.training_dir.exists()
    assert store.index_path.exists()

    index = store._read_json(store.index_path)

    assert index["store_type"] == "learning_registry_store"
    assert index["ontology_records"] == {}
    assert index["training_eligible_records"] == {}


def test_learning_registry_registers_full_learning_metadata(tmp_path):
    store = LearningRegistryStore(tmp_path / "learning")

    result = store.register_learning_metadata(
        engine_name="character.dialogue_voice_engine",
        target_object_id="char_kael",
        target_object_type="character_dialogue_voice",
        learning_metadata=sample_learning_metadata(),
        project_id="proj_ashen",
        universe_id="velmora",
    )

    assert result["success"] is True
    assert result["metadata_id"] == "learn_dialogue_001"
    assert result["ontology_registered"] == 1
    assert result["type_candidates_registered"] == 1
    assert result["provenance_registered"] == 1
    assert result["embedding_registered"] is True
    assert result["training_record_registered"] is True
    assert Path(result["metadata_path"]).exists()

    summary = store.get_summary()

    assert summary["counts"]["engine_learning_metadata"] == 1
    assert summary["counts"]["ontology_records"] == 1
    assert summary["counts"]["type_candidates"] == 1
    assert summary["counts"]["provenance_records"] == 1
    assert summary["counts"]["embedding_metadata"] == 1
    assert summary["counts"]["training_eligible_records"] == 1


def test_learning_registry_lists_records_with_filters(tmp_path):
    store = LearningRegistryStore(tmp_path / "learning")

    store.register_learning_metadata(
        engine_name="character.dialogue_voice_engine",
        target_object_id="char_kael",
        target_object_type="character_dialogue_voice",
        learning_metadata=sample_learning_metadata(),
        project_id="proj_ashen",
        universe_id="velmora",
    )

    ontology = store.list_records(category="ontology_records", type_family="dialogue_voice")
    metadata = store.list_records(category="engine_learning_metadata", engine_name="character.dialogue_voice_engine")
    training = store.list_records(category="training_eligible_records", min_quality_score=0.8)

    assert len(ontology) == 1
    assert ontology[0]["ontology_id"] == "ont_character_voice_001"

    assert len(metadata) == 1
    assert metadata[0]["metadata_id"] == "learn_dialogue_001"

    assert len(training) == 1
    assert training[0]["target_object_id"] == "char_kael"


def test_learning_registry_loads_registered_record(tmp_path):
    store = LearningRegistryStore(tmp_path / "learning")

    store.register_ontology_record(
        ontology_record=sample_ontology_record(),
        project_id="proj_ashen",
        universe_id="velmora",
    )

    loaded = store.load_record(
        category="ontology_records",
        record_id="ont_character_voice_001",
    )

    assert loaded["ontology_id"] == "ont_character_voice_001"
    assert loaded["ontology_record"]["family"] == "dialogue_voice"
    assert loaded["registry_metadata"]["generated_by_engine"] == "character.dialogue_voice_engine"


def test_learning_registry_direct_registration_methods(tmp_path):
    store = LearningRegistryStore(tmp_path / "learning")

    ontology_result = store.register_ontology_record(ontology_record=sample_ontology_record())
    type_result = store.register_type_candidate(type_candidate=sample_type_candidate())
    provenance_result = store.register_provenance_record(provenance_record=sample_provenance_record())
    embedding_result = store.register_embedding_metadata(
        embedding_metadata=sample_embedding_metadata(),
        target_object_id="char_kael",
        target_object_type="character_dialogue_voice",
    )
    training_result = store.register_training_eligible_record(
        target_object_id="char_kael",
        target_object_type="character_dialogue_voice",
        engine_name="character.dialogue_voice_engine",
        learning_metadata=sample_learning_metadata(),
        training_eligibility=sample_training_eligibility(),
    )

    assert ontology_result["success"] is True
    assert type_result["success"] is True
    assert provenance_result["success"] is True
    assert embedding_result["success"] is True
    assert training_result["success"] is True

    summary = store.get_summary()

    assert summary["total_records"] == 5


def test_learning_registry_does_not_register_training_record_when_not_eligible(tmp_path):
    store = LearningRegistryStore(tmp_path / "learning")

    metadata = sample_learning_metadata()
    metadata["training_eligibility"] = {
        "training_eligible": False,
        "human_review_required": True,
        "do_not_train": True,
        "quality_score": 0.42,
    }

    store.register_learning_metadata(
        engine_name="character.dialogue_voice_engine",
        target_object_id="char_kael",
        target_object_type="character_dialogue_voice",
        learning_metadata=metadata,
    )

    summary = store.get_summary()

    assert summary["counts"]["engine_learning_metadata"] == 1
    assert summary["counts"]["training_eligible_records"] == 0


def test_learning_registry_requires_core_fields(tmp_path):
    store = LearningRegistryStore(tmp_path / "learning")

    with pytest.raises(ValueError):
        store.register_learning_metadata(
            engine_name="",
            target_object_id="char_kael",
            target_object_type="character_dialogue_voice",
            learning_metadata=sample_learning_metadata(),
        )

    with pytest.raises(ValueError):
        store.register_learning_metadata(
            engine_name="character.dialogue_voice_engine",
            target_object_id="",
            target_object_type="character_dialogue_voice",
            learning_metadata=sample_learning_metadata(),
        )

    with pytest.raises(ValueError):
        store.register_learning_metadata(
            engine_name="character.dialogue_voice_engine",
            target_object_id="char_kael",
            target_object_type="",
            learning_metadata=sample_learning_metadata(),
        )


def test_learning_registry_unknown_category_errors(tmp_path):
    store = LearningRegistryStore(tmp_path / "learning")

    with pytest.raises(ValueError):
        store.list_records(category="not_a_category")

    with pytest.raises(ValueError):
        store.load_record(category="not_a_category", record_id="x")


def test_learning_registry_missing_record_errors(tmp_path):
    store = LearningRegistryStore(tmp_path / "learning")

    with pytest.raises(FileNotFoundError):
        store.load_record(category="ontology_records", record_id="missing")

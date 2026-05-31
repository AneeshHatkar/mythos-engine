from pathlib import Path

import pytest

from backend.app.services.embedding_registry_store import EmbeddingRegistryStore


def sample_embedding_metadata():
    return {
        "embedding_id": "emb_dialogue_001",
        "embedding_model": "future_embedding_model_not_computed_yet",
        "similarity_tags": ["dialogue_voice", "controlled_subtext_voice", "character"],
        "retrieval_queries": ["controlled subtext dialogue voice", "character voice originality"],
        "nearest_neighbor_placeholders": ["future_neighbor_1"],
        "novelty_score": 0.76,
        "originality_score": 0.84,
        "similarity_threshold_used": 0.82,
        "vector_computed": False,
    }


def sample_learning_metadata():
    return {
        "learning_metadata_id": "learn_dialogue_001",
        "engine_name": "character.dialogue_voice_engine",
        "target_object_id": "char_kael",
        "target_object_type": "character_dialogue_voice",
        "embedding_metadata": sample_embedding_metadata(),
    }


def test_embedding_registry_store_initializes(tmp_path):
    store = EmbeddingRegistryStore(tmp_path / "embeddings")

    assert store.root_dir.exists()
    assert store.records_dir.exists()
    assert store.vector_queue_dir.exists()
    assert store.similarity_events_dir.exists()
    assert store.index_path.exists()

    summary = store.get_summary()

    assert summary["store_type"] == "embedding_registry_store"
    assert summary["record_count"] == 0


def test_embedding_registry_registers_embedding_metadata(tmp_path):
    store = EmbeddingRegistryStore(tmp_path / "embeddings")

    result = store.register_embedding_metadata(
        target_object_id="char_kael",
        target_object_type="character_dialogue_voice",
        embedding_metadata=sample_embedding_metadata(),
        engine_name="character.dialogue_voice_engine",
        project_id="proj_ashen",
        universe_id="velmora",
        source_payload={"text": "sample voice profile"},
    )

    assert result["success"] is True
    assert result["embedding_id"] == "emb_dialogue_001"
    assert result["queued_for_vectorization"] is True
    assert result["deduplication_status"] == "likely_original"
    assert Path(result["record_path"]).exists()

    loaded = store.load_record("emb_dialogue_001")

    assert loaded["target_object_id"] == "char_kael"
    assert loaded["target_object_type"] == "character_dialogue_voice"
    assert loaded["originality_score"] == 0.84
    assert "controlled_subtext_voice" in loaded["similarity_tags"]


def test_embedding_registry_registers_from_learning_metadata(tmp_path):
    store = EmbeddingRegistryStore(tmp_path / "embeddings")

    result = store.register_from_learning_metadata(
        sample_learning_metadata(),
        project_id="proj_ashen",
        universe_id="velmora",
    )

    assert result["success"] is True
    assert result["embedding_id"] == "emb_dialogue_001"

    summary = store.get_summary()

    assert summary["record_count"] == 1
    assert summary["vectorization_queue_count"] == 1
    assert summary["pending_vectorization_count"] == 1


def test_embedding_registry_lists_records_with_filters(tmp_path):
    store = EmbeddingRegistryStore(tmp_path / "embeddings")

    store.register_embedding_metadata(
        target_object_id="char_kael",
        target_object_type="character_dialogue_voice",
        embedding_metadata=sample_embedding_metadata(),
        engine_name="character.dialogue_voice_engine",
        project_id="proj_ashen",
        universe_id="velmora",
    )

    records_by_type = store.list_records(target_object_type="character_dialogue_voice")
    records_by_engine = store.list_records(engine_name="character.dialogue_voice_engine")
    records_by_tag = store.list_records(tag="controlled_subtext_voice")
    records_by_originality = store.list_records(min_originality_score=0.8)
    records_without_vector = store.list_records(vector_computed=False)

    assert len(records_by_type) == 1
    assert len(records_by_engine) == 1
    assert len(records_by_tag) == 1
    assert len(records_by_originality) == 1
    assert len(records_without_vector) == 1


def test_embedding_registry_vectorization_queue_update(tmp_path):
    store = EmbeddingRegistryStore(tmp_path / "embeddings")

    result = store.register_embedding_metadata(
        target_object_id="char_kael",
        target_object_type="character_dialogue_voice",
        embedding_metadata=sample_embedding_metadata(),
        engine_name="character.dialogue_voice_engine",
    )

    queue_id = result["vectorization_queue_id"]

    queued = store.list_vectorization_queue(status="queued")

    assert len(queued) == 1
    assert queued[0]["vectorization_queue_id"] == queue_id

    update = store.update_vectorization_status(
        vectorization_queue_id=queue_id,
        status="completed",
        vector_id="vec_real_later_001",
        embedding_model="future-real-model",
        notes="test completion",
    )

    assert update["success"] is True
    assert update["status"] == "completed"

    completed = store.list_vectorization_queue(status="completed")

    assert len(completed) == 1
    assert completed[0]["vector_id"] == "vec_real_later_001"


def test_embedding_registry_similarity_event(tmp_path):
    store = EmbeddingRegistryStore(tmp_path / "embeddings")

    store.register_embedding_metadata(
        target_object_id="char_kael",
        target_object_type="character_dialogue_voice",
        embedding_metadata=sample_embedding_metadata(),
        engine_name="character.dialogue_voice_engine",
    )

    event = store.register_similarity_event(
        source_embedding_id="emb_dialogue_001",
        compared_embedding_id="emb_other_001",
        target_object_id="char_kael",
        similarity_score=0.62,
        similarity_type="future_semantic_similarity",
        decision="acceptable_originality",
        details={"note": "placeholder event"},
    )

    assert event["success"] is True
    assert Path(event["path"]).exists()

    summary = store.get_summary()

    assert summary["similarity_event_count"] == 1


def test_embedding_registry_deduplication_statuses(tmp_path):
    store = EmbeddingRegistryStore(tmp_path / "embeddings")

    high = dict(sample_embedding_metadata())
    high["embedding_id"] = "emb_high"
    high["originality_score"] = 0.85

    mid = dict(sample_embedding_metadata())
    mid["embedding_id"] = "emb_mid"
    mid["originality_score"] = 0.65

    low = dict(sample_embedding_metadata())
    low["embedding_id"] = "emb_low"
    low["originality_score"] = 0.3

    high_result = store.register_embedding_metadata(target_object_id="a", target_object_type="character", embedding_metadata=high)
    mid_result = store.register_embedding_metadata(target_object_id="b", target_object_type="character", embedding_metadata=mid)
    low_result = store.register_embedding_metadata(target_object_id="c", target_object_type="character", embedding_metadata=low)

    assert high_result["deduplication_status"] == "likely_original"
    assert mid_result["deduplication_status"] == "review_recommended"
    assert low_result["deduplication_status"] == "possible_duplicate_or_generic"


def test_embedding_registry_summary(tmp_path):
    store = EmbeddingRegistryStore(tmp_path / "embeddings")

    store.register_embedding_metadata(
        target_object_id="char_kael",
        target_object_type="character_dialogue_voice",
        embedding_metadata=sample_embedding_metadata(),
        engine_name="character.dialogue_voice_engine",
    )

    summary = store.get_summary()

    assert summary["record_count"] == 1
    assert summary["vectorization_queue_count"] == 1
    assert summary["average_originality_score"] == 0.84
    assert summary["average_novelty_score"] == 0.76
    assert "character_dialogue_voice" in summary["target_object_types"]


def test_embedding_registry_requires_core_fields(tmp_path):
    store = EmbeddingRegistryStore(tmp_path / "embeddings")

    with pytest.raises(ValueError):
        store.register_embedding_metadata(
            target_object_id="",
            target_object_type="character_dialogue_voice",
            embedding_metadata=sample_embedding_metadata(),
        )

    with pytest.raises(ValueError):
        store.register_embedding_metadata(
            target_object_id="char_kael",
            target_object_type="",
            embedding_metadata=sample_embedding_metadata(),
        )


def test_embedding_registry_missing_record_errors(tmp_path):
    store = EmbeddingRegistryStore(tmp_path / "embeddings")

    with pytest.raises(FileNotFoundError):
        store.load_record("missing")

    with pytest.raises(FileNotFoundError):
        store.update_vectorization_status(vectorization_queue_id="missing", status="completed")


def test_embedding_registry_learning_metadata_requires_embedding_data(tmp_path):
    store = EmbeddingRegistryStore(tmp_path / "embeddings")

    with pytest.raises(ValueError):
        store.register_from_learning_metadata(
            {
                "learning_metadata_id": "learn_no_embedding",
                "target_object_id": "char_kael",
                "target_object_type": "character",
            }
        )


def test_embedding_registry_similarity_event_requires_core_fields(tmp_path):
    store = EmbeddingRegistryStore(tmp_path / "embeddings")

    with pytest.raises(ValueError):
        store.register_similarity_event(
            source_embedding_id="",
            compared_embedding_id=None,
            target_object_id="char_kael",
            similarity_score=0.5,
            similarity_type="test",
            decision="review",
        )

    with pytest.raises(ValueError):
        store.register_similarity_event(
            source_embedding_id="emb_1",
            compared_embedding_id=None,
            target_object_id="",
            similarity_score=0.5,
            similarity_type="test",
            decision="review",
        )

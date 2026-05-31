from pathlib import Path

import pytest

from backend.app.services.training_queue_store import TrainingQueueStore


def eligible_training():
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


def ineligible_training():
    return {
        "training_eligible": False,
        "human_review_required": True,
        "do_not_train": True,
        "recommended_split": "human_review_queue",
        "quality_score": 0.42,
        "consistency_score": 0.5,
        "originality_score": 0.4,
        "safety_score": 0.7,
        "rejection_reasons": ["quality below threshold"],
    }


def test_training_queue_store_initializes(tmp_path):
    store = TrainingQueueStore(tmp_path / "training_queue")

    assert store.root_dir.exists()
    assert store.records_dir.exists()
    assert store.payloads_dir.exists()
    assert store.index_path.exists()

    summary = store.get_summary()

    assert summary["store_type"] == "training_queue_store"
    assert summary["record_count"] == 0


def test_training_queue_store_enqueues_eligible_record(tmp_path):
    store = TrainingQueueStore(tmp_path / "training_queue")

    result = store.enqueue(
        target_object_id="char_kael",
        target_object_type="character_full_profile",
        engine_name="character.full_profile_orchestrator",
        payload={"character_id": "char_kael"},
        training_eligibility=eligible_training(),
        project_id="proj_ashen",
        universe_id="velmora",
    )

    assert result["success"] is True
    assert result["status"] == "queued"
    assert result["recommended_split"] == "train"
    assert result["future_chunk8_ready"] is True
    assert Path(result["record_path"]).exists()
    assert Path(result["payload_path"]).exists()

    loaded = store.load_record(result["training_queue_id"])
    payload = store.load_payload(result["training_queue_id"])

    assert loaded["target_object_id"] == "char_kael"
    assert payload["character_id"] == "char_kael"


def test_training_queue_store_enqueues_ineligible_for_review(tmp_path):
    store = TrainingQueueStore(tmp_path / "training_queue")

    result = store.enqueue(
        target_object_id="char_generic",
        target_object_type="character_full_profile",
        engine_name="character.full_profile_orchestrator",
        payload={"character_id": "char_generic"},
        training_eligibility=ineligible_training(),
    )

    assert result["success"] is True
    assert result["status"] == "human_review"
    assert result["recommended_split"] == "human_review_queue"
    assert result["future_chunk8_ready"] is False

    summary = store.get_summary()

    assert summary["human_review_count"] == 1


def test_training_queue_store_enqueue_from_learning_metadata(tmp_path):
    store = TrainingQueueStore(tmp_path / "training_queue")

    result = store.enqueue_from_learning_metadata(
        {
            "learning_metadata_id": "learn_001",
            "engine_name": "character.quality_scorer",
            "target_object_id": "char_kael",
            "target_object_type": "character_quality",
            "training_eligibility": eligible_training(),
            "generated_training_labels": {
                "quality_tier": "strong_character_ready",
            },
        },
        payload={"quality_report": {"overall_quality_score": 0.84}},
        project_id="proj_ashen",
        universe_id="velmora",
    )

    loaded = store.load_record(result["training_queue_id"])

    assert loaded["learning_metadata_id"] == "learn_001"
    assert loaded["engine_name"] == "character.quality_scorer"
    assert loaded["target_object_type"] == "character_quality"
    assert "quality_tier" in loaded["tags"]


def test_training_queue_store_lists_with_filters(tmp_path):
    store = TrainingQueueStore(tmp_path / "training_queue")

    store.enqueue(
        target_object_id="char_kael",
        target_object_type="character_full_profile",
        engine_name="character.full_profile_orchestrator",
        payload={},
        training_eligibility=eligible_training(),
        project_id="proj_ashen",
        universe_id="velmora",
    )

    store.enqueue(
        target_object_id="char_generic",
        target_object_type="character_full_profile",
        engine_name="character.full_profile_orchestrator",
        payload={},
        training_eligibility=ineligible_training(),
        project_id="proj_ashen",
        universe_id="velmora",
    )

    queued = store.list_records(status="queued")
    review = store.list_records(status="human_review")
    high_quality = store.list_records(min_quality_score=0.8)
    ready = store.list_records(future_chunk8_ready=True)

    assert len(queued) == 1
    assert len(review) == 1
    assert len(high_quality) == 1
    assert len(ready) == 1
    assert ready[0]["target_object_id"] == "char_kael"


def test_training_queue_store_updates_status(tmp_path):
    store = TrainingQueueStore(tmp_path / "training_queue")

    result = store.enqueue(
        target_object_id="char_kael",
        target_object_type="character_full_profile",
        engine_name="character.full_profile_orchestrator",
        payload={},
        training_eligibility=eligible_training(),
    )

    update = store.update_status(
        training_queue_id=result["training_queue_id"],
        status="approved",
        notes="approved by test",
    )

    loaded = store.load_record(result["training_queue_id"])

    assert update["success"] is True
    assert loaded["status"] == "approved"
    assert loaded["status_notes"][0]["note"] == "approved by test"


def test_training_queue_store_summary(tmp_path):
    store = TrainingQueueStore(tmp_path / "training_queue")

    store.enqueue(
        target_object_id="char_kael",
        target_object_type="character_full_profile",
        engine_name="character.full_profile_orchestrator",
        payload={},
        training_eligibility=eligible_training(),
    )

    store.enqueue(
        target_object_id="char_generic",
        target_object_type="character_full_profile",
        engine_name="character.full_profile_orchestrator",
        payload={},
        training_eligibility=ineligible_training(),
    )

    summary = store.get_summary()

    assert summary["record_count"] == 2
    assert summary["queued_count"] == 1
    assert summary["human_review_count"] == 1
    assert summary["future_chunk8_ready_count"] == 1
    assert "character_full_profile" in summary["target_object_types"]


def test_training_queue_store_requires_core_fields(tmp_path):
    store = TrainingQueueStore(tmp_path / "training_queue")

    with pytest.raises(ValueError):
        store.enqueue(
            target_object_id="",
            target_object_type="character_full_profile",
            engine_name="engine",
            payload={},
            training_eligibility=eligible_training(),
        )

    with pytest.raises(ValueError):
        store.enqueue(
            target_object_id="char",
            target_object_type="",
            engine_name="engine",
            payload={},
            training_eligibility=eligible_training(),
        )

    with pytest.raises(ValueError):
        store.enqueue(
            target_object_id="char",
            target_object_type="character_full_profile",
            engine_name="",
            payload={},
            training_eligibility=eligible_training(),
        )


def test_training_queue_store_invalid_status_and_missing_record_errors(tmp_path):
    store = TrainingQueueStore(tmp_path / "training_queue")

    with pytest.raises(ValueError):
        store.update_status(training_queue_id="missing", status="not_valid")

    with pytest.raises(FileNotFoundError):
        store.load_record("missing")

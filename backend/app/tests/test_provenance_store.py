from pathlib import Path

import pytest

from backend.app.services.provenance_store import ProvenanceStore


def test_provenance_store_initializes(tmp_path):
    store = ProvenanceStore(tmp_path / "provenance")

    assert store.root_dir.exists()
    assert store.records_dir.exists()
    assert store.audit_dir.exists()
    assert store.index_path.exists()

    summary = store.get_summary()

    assert summary["store_type"] == "provenance_store"
    assert summary["record_count"] == 0


def test_provenance_store_registers_training_allowed_source(tmp_path):
    store = ProvenanceStore(tmp_path / "provenance")

    result = store.register_source(
        source_name="human_approved_synthetic",
        source_type="synthetic_or_user_generated",
        dataset_family="character_dialogue_voice",
        usage_allowed=True,
        human_review_required=False,
        do_not_train=False,
        license_name="user_owned",
        project_id="proj_ashen",
        universe_id="velmora",
    )

    assert result["success"] is True
    assert result["allowed_for_training"] is True
    assert "training_candidate_source" in result["governance_flags"]
    assert Path(result["path"]).exists()

    loaded = store.load_record(result["provenance_id"])

    assert loaded["source_name"] == "human_approved_synthetic"
    assert loaded["allowed_for_training"] is True


def test_provenance_store_blocks_unknown_or_review_required_sources(tmp_path):
    store = ProvenanceStore(tmp_path / "provenance")

    result = store.register_source(
        source_name="unknown_web_text",
        source_type="web_text",
        dataset_family="novel_dataset",
        usage_allowed=False,
        human_review_required=True,
        do_not_train=True,
    )

    assert result["allowed_for_training"] is False
    assert "usage_not_allowed" in result["governance_flags"]
    assert "human_review_required" in result["governance_flags"]
    assert "do_not_train" in result["governance_flags"]

    summary = store.get_summary()

    assert summary["do_not_train_count"] == 1
    assert summary["human_review_required_count"] == 1


def test_provenance_store_registers_from_engine_record(tmp_path):
    store = ProvenanceStore(tmp_path / "provenance")

    result = store.register_from_engine_provenance(
        {
            "source_name": "licensed_dialogue_dataset",
            "source_type": "licensed_dataset",
            "dataset_family": "dialogue_dataset",
            "usage_allowed": True,
            "human_review_required": False,
            "license_name": "licensed_internal",
            "genre_tags": ["fantasy"],
            "culture_tags": ["court"],
        },
        project_id="proj_ashen",
        universe_id="velmora",
    )

    loaded = store.load_record(result["provenance_id"])

    assert loaded["dataset_family"] == "dialogue_dataset"
    assert loaded["allowed_for_training"] is True
    assert "fantasy" in loaded["tags"]
    assert "court" in loaded["tags"]


def test_provenance_store_lists_with_filters(tmp_path):
    store = ProvenanceStore(tmp_path / "provenance")

    store.register_source(
        source_name="source_a",
        source_type="licensed_dataset",
        dataset_family="dialogue_dataset",
        usage_allowed=True,
        human_review_required=False,
        license_name="licensed",
        project_id="proj_ashen",
        universe_id="velmora",
    )

    store.register_source(
        source_name="source_b",
        source_type="web_text",
        dataset_family="novel_dataset",
        usage_allowed=False,
        human_review_required=True,
        do_not_train=True,
        project_id="proj_other",
        universe_id="other",
    )

    trainable = store.list_records(allowed_for_training=True)
    dialogue = store.list_records(dataset_family="dialogue_dataset")
    project = store.list_records(project_id="proj_ashen")

    assert len(trainable) == 1
    assert trainable[0]["source_name"] == "source_a"
    assert len(dialogue) == 1
    assert len(project) == 1


def test_provenance_store_audit_event(tmp_path):
    store = ProvenanceStore(tmp_path / "provenance")

    event = store.add_audit_event(
        event_type="manual_review_completed",
        provenance_id="prov_fake",
        details={"reviewer": "tester", "approved": True},
    )

    assert event["success"] is True
    assert Path(event["path"]).exists()

    summary = store.get_summary()

    assert summary["audit_event_count"] == 1


def test_provenance_store_requires_core_fields(tmp_path):
    store = ProvenanceStore(tmp_path / "provenance")

    with pytest.raises(ValueError):
        store.register_source(
            source_name="",
            source_type="licensed_dataset",
            dataset_family="dialogue",
            usage_allowed=True,
        )

    with pytest.raises(ValueError):
        store.register_source(
            source_name="source",
            source_type="",
            dataset_family="dialogue",
            usage_allowed=True,
        )

    with pytest.raises(ValueError):
        store.register_source(
            source_name="source",
            source_type="licensed_dataset",
            dataset_family="",
            usage_allowed=True,
        )


def test_provenance_store_missing_record_errors(tmp_path):
    store = ProvenanceStore(tmp_path / "provenance")

    with pytest.raises(FileNotFoundError):
        store.load_record("missing")

from backend.app.engines.world.world_snapshot_engine import WorldSnapshotEngine
from backend.app.schemas.foundation import EngineRunResult


def sample_world_state():
    return {
        "identity": {"world_name": "Velmora"},
        "rules": {"magic": "academy law controls royal magic"},
        "chronology": {"history": "founding oath betrayal"},
        "geography": {"regions": ["capital", "border"]},
        "society": {"class_tiers": ["noble", "commoner"]},
        "economy": {"debt_system": "relic debt"},
        "law": {"courts": ["Oath Court"]},
        "belief": {"rituals": ["oath bell ceremony"]},
        "artifacts": [{"name": "The Ashen Crown Shard"}],
        "causality_graph": {"links": ["education causes class pressure"]},
        "description": "academy oath relic archive destiny class law border faction artifact causality training",
    }


def quality_summary():
    return {
        "consistency_score": 0.86,
        "originality_score": 0.82,
        "story_potential_score": 0.88,
        "training_readiness_score": 0.84,
        "genericness_risk_score": 0.18,
        "quality_tier": "strong",
        "training_eligible": True,
    }


def dataset_metadata():
    return {
        "training_eligible": True,
        "do_not_train": False,
        "recommended_dataset_split": "train_candidate",
        "dataset_tags": ["dark_academy", "political_fantasy"],
        "risk_tags": [],
    }


def test_world_snapshot_engine_returns_engine_result():
    engine = WorldSnapshotEngine()

    result = engine.run(
        {
            "world_state": sample_world_state(),
            "quality_summary": quality_summary(),
            "dataset_metadata": dataset_metadata(),
            "snapshot_type": "initial_generation",
            "project_id": "proj_demo",
            "universe_id": "uni_demo",
        }
    )

    assert isinstance(result, EngineRunResult)
    assert result.success is True
    assert result.engine_name == "world.snapshot_engine"
    assert "snapshot" in result.data
    assert "version_timeline_entry" in result.data
    assert "training_notes" in result.data
    assert len(result.generated_object_ids) == 1


def test_world_snapshot_engine_creates_initial_snapshot():
    engine = WorldSnapshotEngine()

    result = engine.run(
        {
            "world_state": sample_world_state(),
            "quality_summary": quality_summary(),
            "dataset_metadata": dataset_metadata(),
            "snapshot_type": "initial_generation",
            "project_id": "proj_demo",
            "universe_id": "uni_demo",
        }
    )

    snapshot = result.data["snapshot"]

    assert snapshot["snapshot_id"].startswith("wsnap_")
    assert snapshot["snapshot_label"] == "world_v1"
    assert snapshot["snapshot_type"] == "initial_generation"
    assert snapshot["version_kind"] == "major"
    assert snapshot["project_id"] == "proj_demo"
    assert snapshot["universe_id"] == "uni_demo"
    assert snapshot["quality_snapshot"]["quality_tier"] == "strong"
    assert snapshot["dataset_snapshot"]["recommended_dataset_split"] == "train_candidate"
    assert snapshot["rollback"]["rollback_ready"] is True
    assert snapshot["storage_recommendation"]["storage_tier"] == "curated_training_candidate_snapshot"


def test_world_snapshot_engine_supports_parent_timeline():
    engine = WorldSnapshotEngine()

    result = engine.run(
        {
            "world_state": sample_world_state(),
            "quality_summary": quality_summary(),
            "dataset_metadata": dataset_metadata(),
            "snapshot_type": "after_consistency_fix",
            "snapshot_label": "world_after_consistency_fix_v2",
            "parent_snapshot_id": "wsnap_parent123",
            "change_summary": "Fixed communication and healing contradictions.",
            "tags": ["consistency_fix", "quality_passed"],
        }
    )

    snapshot = result.data["snapshot"]
    timeline = result.data["version_timeline_entry"]

    assert snapshot["snapshot_label"] == "world_after_consistency_fix_v2"
    assert snapshot["version_kind"] == "minor"
    assert snapshot["parent_snapshot_id"] == "wsnap_parent123"
    assert "consistency_fix" in snapshot["tags"]
    assert timeline["parent_snapshot_id"] == "wsnap_parent123"
    assert timeline["rollback_ready"] is True


def test_world_snapshot_engine_handles_invalid_snapshot_type():
    engine = WorldSnapshotEngine()

    result = engine.run(
        {
            "world_state": sample_world_state(),
            "snapshot_type": "bad_type",
        }
    )

    snapshot = result.data["snapshot"]

    assert result.success is True
    assert len(result.warnings) == 1
    assert snapshot["snapshot_type"] == "manual_checkpoint"
    assert snapshot["snapshot_label"] == "world_manual_checkpoint"


def test_world_snapshot_engine_warns_without_world_state():
    engine = WorldSnapshotEngine()

    result = engine.run({})

    assert result.success is True
    assert len(result.warnings) == 1
    assert "world_state" in result.warnings[0]
    assert result.data["snapshot"]["rollback"]["rollback_ready"] is False

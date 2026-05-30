from backend.app.engines.world.dataset_metadata_engine import DatasetMetadataEngine
from backend.app.schemas.foundation import EngineRunResult


def strong_world_state():
    return {
        "identity": {"world_name": "Velmora"},
        "quality_summary": {
            "consistency_score": 0.84,
            "originality_score": 0.82,
            "story_potential_score": 0.86,
            "training_readiness_score": 0.83,
            "genericness_risk_score": 0.18,
        },
        "causality_graph": {"links": ["education causes class pressure"]},
        "artifacts": [{"name": "The Oath Bell"}],
        "institutions": [{"name": "The Ashen Crown Academy"}],
        "power_structure": {"factions": ["Silent Register"]},
        "belief": {"rituals": ["oath ceremony"]},
        "law": {"courts": ["Oath Court"]},
        "economy": {"debt_system": "relic debt"},
        "knowledge_education": {"forbidden_books": ["Forbidden Exam Scroll"]},
        "civilization_pressure": {"current_crisis": "collapse pressure"},
        "description": (
            "A dark academy political fantasy empire with oath law, relic debt, "
            "archives, erased names, class hierarchy, prophecy, forbidden education, "
            "benchmark metadata, training notes, and model-ready causality."
        ),
    }


def test_dataset_metadata_engine_returns_engine_result():
    engine = DatasetMetadataEngine()

    result = engine.run(
        {
            "world_state": strong_world_state(),
            "desired_complexity": "god_level",
            "source_mode": "human_approved_synthetic",
            "user_rating": 9,
        }
    )

    assert isinstance(result, EngineRunResult)
    assert result.success is True
    assert result.engine_name == "world.dataset_metadata_engine"
    assert "dataset_metadata" in result.data
    assert "training_notes" in result.data


def test_dataset_metadata_engine_marks_strong_world_training_eligible():
    engine = DatasetMetadataEngine()

    result = engine.run(
        {
            "world_state": strong_world_state(),
            "quality_summary": strong_world_state()["quality_summary"],
            "desired_complexity": "god_level",
            "source_mode": "human_approved_synthetic",
            "user_rating": 9,
        }
    )

    metadata = result.data["dataset_metadata"]

    assert metadata["training_eligible"] is True
    assert metadata["do_not_train"] is False
    assert metadata["human_review_required"] is False
    assert metadata["recommended_dataset_split"] == "train_candidate"
    assert "benchmark_dark_academy_political_empire" in metadata["benchmark_labels"]
    assert "research_grade_structure_candidate" in metadata["complexity_tags"]


def test_dataset_metadata_engine_detects_tags():
    engine = DatasetMetadataEngine()

    result = engine.run(
        {
            "world_state": strong_world_state(),
            "quality_summary": strong_world_state()["quality_summary"],
            "desired_complexity": "god_level",
            "source_mode": "human_approved_synthetic",
            "user_rating": 9,
        }
    )

    metadata = result.data["dataset_metadata"]

    assert "dark_academy" in metadata["genre_tags"]
    assert "political_fantasy" in metadata["genre_tags"]
    assert "mythic_fantasy" in metadata["genre_tags"]
    assert "mystery_intrigue" in metadata["genre_tags"]
    assert "causal_graph_available" in metadata["structure_tags"]
    assert "artifact_system_available" in metadata["structure_tags"]
    assert "has_future_ml_hooks" in metadata["content_tags"]


def test_dataset_metadata_engine_blocks_unclear_provenance():
    engine = DatasetMetadataEngine()

    result = engine.run(
        {
            "world_state": {
                "identity": {"world_name": "Unsafe Similarity World"},
                "description": "generate from harry potter and directly based on copyrighted fanfiction",
                "quality_summary": {
                    "consistency_score": 0.9,
                    "originality_score": 0.9,
                    "story_potential_score": 0.9,
                    "training_readiness_score": 0.9,
                    "genericness_risk_score": 0.1,
                },
            },
            "quality_summary": {
                "consistency_score": 0.9,
                "originality_score": 0.9,
                "story_potential_score": 0.9,
                "training_readiness_score": 0.9,
                "genericness_risk_score": 0.1,
            },
            "source_mode": "human_approved_synthetic",
            "user_rating": 10,
        }
    )

    metadata = result.data["dataset_metadata"]

    assert metadata["training_eligible"] is False
    assert metadata["do_not_train"] is True
    assert "do_not_train" in metadata["risk_tags"]
    assert "unclear_provenance" in metadata["risk_tags"]


def test_dataset_metadata_engine_requires_review_without_user_rating():
    engine = DatasetMetadataEngine()

    result = engine.run(
        {
            "world_state": strong_world_state(),
            "quality_summary": strong_world_state()["quality_summary"],
            "desired_complexity": "god_level",
            "source_mode": "human_approved_synthetic",
        }
    )

    metadata = result.data["dataset_metadata"]

    assert metadata["training_eligible"] is False
    assert metadata["human_review_required"] is True
    assert metadata["recommended_dataset_split"] == "human_review_queue"


def test_dataset_metadata_engine_warns_when_world_state_missing():
    engine = DatasetMetadataEngine()

    result = engine.run({})

    assert result.success is True
    assert len(result.warnings) == 1
    assert "world_state" in result.warnings[0]

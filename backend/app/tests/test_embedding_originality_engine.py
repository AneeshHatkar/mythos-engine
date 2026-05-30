from backend.app.engines.world.embedding_originality_engine import EmbeddingOriginalityEngine
from backend.app.schemas.foundation import EngineRunResult
from backend.app.services.world_run_store import world_run_store


def candidate_world():
    return {
        "identity": {"world_name": "Velmora"},
        "description": (
            "A dark academy political fantasy empire where oath law, relic debt, "
            "sealed archives, destiny classification, class hierarchy, forbidden education, "
            "border pressure, artifact memory, prophecy conflict, and civilization collapse "
            "shape the world."
        ),
        "law": {"courts": ["Oath Court"]},
        "economy": {"resources": ["relic debt"]},
        "belief": {"rituals": ["oath bell ceremony"]},
        "artifacts": [{"name": "The Ashen Crown Shard"}],
    }


def test_embedding_originality_engine_returns_engine_result():
    engine = EmbeddingOriginalityEngine()

    result = engine.run(
        {
            "world_state": candidate_world(),
            "compare_against_saved_runs": False,
        }
    )

    assert isinstance(result, EngineRunResult)
    assert result.success is True
    assert result.engine_name == "world.embedding_originality_engine"
    assert "embedding_originality_report" in result.data
    assert "training_notes" in result.data


def test_embedding_originality_engine_scores_without_saved_runs():
    engine = EmbeddingOriginalityEngine()

    result = engine.run(
        {
            "world_state": candidate_world(),
            "candidate_label": "Velmora Candidate",
            "compare_against_saved_runs": False,
        }
    )

    report = result.data["embedding_originality_report"]

    assert report["candidate_label"] == "Velmora Candidate"
    assert report["nearest_similarity"] == 0.0
    assert report["duplicate_risk"] == "low_overlap"
    assert report["originality_score"] > 0.0
    assert "oath" in report["unique_signal_terms"]
    assert "relic" in report["unique_signal_terms"]
    assert "academy" in report["unique_signal_terms"]


def test_embedding_originality_engine_detects_saved_world_similarity():
    payload = {
        "world_name": "Velmora Saved",
        "template_id": "dark_academy_empire",
        "seed_premise": "A saved test world.",
    }

    result_data = {
        "world_state": candidate_world(),
        "orchestration_summary": {"engine_count": 16},
    }

    world_run_store.save_orchestration_run(
        payload=payload,
        result_data=result_data,
        audit_metadata={"audit_id": "aud_similarity_test"},
    )

    engine = EmbeddingOriginalityEngine()

    result = engine.run(
        {
            "world_state": candidate_world(),
            "candidate_label": "Velmora Candidate",
            "compare_against_saved_runs": True,
            "top_k": 3,
        }
    )

    report = result.data["embedding_originality_report"]

    assert report["nearest_similarity"] >= 0.82
    assert report["duplicate_risk"] == "near_duplicate"
    assert report["training_recommendation"] == "block_training_until_deduplicated"
    assert len(report["nearest_saved_worlds"]) >= 1
    assert "oath" in report["nearest_saved_worlds"][0]["shared_high_signal_terms"]


def test_embedding_originality_engine_handles_empty_world():
    engine = EmbeddingOriginalityEngine()

    result = engine.run({})

    assert result.success is True
    assert len(result.warnings) == 1
    assert "world_state" in result.warnings[0]
    assert result.data["embedding_originality_report"]["originality_score"] >= 0.0

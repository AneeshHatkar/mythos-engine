from backend.app.engines.world.world_diff_engine import WorldDiffEngine
from backend.app.schemas.foundation import EngineRunResult


def world_a():
    return {
        "identity": {"world_name": "Velmora"},
        "rules": {"magic": "academy law controls royal magic"},
        "chronology": {"history": "founding oath betrayal and erased archives"},
        "geography": {"regions": ["capital", "border", "low market"]},
        "society": {"classes": ["noble", "commoner", "erased"]},
        "power_structure": {"factions": ["Academy Orthodoxy", "Silent Register"]},
        "economy": {"resources": ["relic debt", "academy funding"]},
        "law": {"courts": ["Oath Court"]},
        "belief": {"rituals": ["oath bell ceremony"]},
        "artifacts": [{"name": "The Ashen Crown Shard"}],
        "aesthetic_texture": {"visual_palette": ["ash white", "ink black"]},
        "quality_summary": {
            "consistency_score": 0.85,
            "originality_score": 0.84,
            "story_potential_score": 0.88,
            "training_readiness_score": 0.82,
            "genericness_risk_score": 0.16,
        },
        "description": (
            "Dark academy political fantasy empire with relics, oath law, archive mystery, "
            "destiny classification, class hierarchy, debt, forbidden education, and border pressure."
        ),
    }


def world_b():
    return {
        "identity": {"world_name": "Neon Veyr"},
        "geography": {"regions": ["megacity", "lower transit rings", "data towers"]},
        "society": {"classes": ["verified citizens", "permitless workers"]},
        "power_structure": {"factions": ["Civic Observation Bureau", "Transit Syndicate"]},
        "law": {"rules": ["movement permits", "behavior classification"]},
        "knowledge_education": {"censorship": ["message interception"]},
        "technology_magic_science": {"communication": "surveillance network"},
        "aesthetic_texture": {"visual_palette": ["cold blue", "chrome", "rain black"]},
        "quality_summary": {
            "consistency_score": 0.78,
            "originality_score": 0.72,
            "story_potential_score": 0.76,
            "training_readiness_score": 0.71,
            "genericness_risk_score": 0.28,
        },
        "description": (
            "Dystopian megacity with surveillance, permits, social classification, urban resistance, "
            "data archives, movement control, transit crime, and hidden identity markets."
        ),
    }


def test_world_diff_engine_returns_engine_result():
    engine = WorldDiffEngine()

    result = engine.run(
        {
            "world_a": world_a(),
            "world_b": world_b(),
            "label_a": "Velmora",
            "label_b": "Neon Veyr",
        }
    )

    assert isinstance(result, EngineRunResult)
    assert result.success is True
    assert result.engine_name == "world.diff_engine"
    assert "comparison" in result.data
    assert "training_notes" in result.data


def test_world_diff_engine_detects_low_overlap_between_distinct_worlds():
    engine = WorldDiffEngine()

    result = engine.run(
        {
            "world_a": world_a(),
            "world_b": world_b(),
            "label_a": "Velmora",
            "label_b": "Neon Veyr",
        }
    )

    comparison = result.data["comparison"]

    assert comparison["similarity"]["overall_similarity"] < 0.65
    assert comparison["similarity"]["overlap_risk"] in {"low", "medium"}
    assert "academy" in comparison["motif_diff"]["unique_to_a"]
    assert "surveillance" in comparison["motif_diff"]["unique_to_b"]
    assert len(comparison["recommendations"]) >= 3


def test_world_diff_engine_detects_high_overlap_for_similar_worlds():
    engine = WorldDiffEngine()

    similar_a = world_a()
    similar_b = {
        **world_a(),
        "identity": {"world_name": "Ashen Vale"},
        "description": (
            "Another dark academy empire with oath law, relic debt, archive mystery, "
            "destiny classification, class hierarchy, forbidden education, and border pressure."
        ),
    }

    result = engine.run(
        {
            "world_a": similar_a,
            "world_b": similar_b,
            "label_a": "Velmora",
            "label_b": "Ashen Vale",
        }
    )

    comparison = result.data["comparison"]

    assert comparison["similarity"]["overlap_risk"] == "high"
    assert comparison["similarity"]["overall_similarity"] >= 0.65
    assert any("High overlap risk" in rec for rec in comparison["recommendations"])


def test_world_diff_engine_compares_quality_scores():
    engine = WorldDiffEngine()

    result = engine.run(
        {
            "world_a": world_a(),
            "world_b": world_b(),
            "label_a": "Velmora",
            "label_b": "Neon Veyr",
        }
    )

    quality_diff = result.data["comparison"]["quality_diff"]

    assert quality_diff["score_deltas_a_minus_b"]["consistency_score"] > 0
    assert quality_diff["score_deltas_a_minus_b"]["originality_score"] > 0
    assert quality_diff["stronger_world"]["winner"] == "Velmora"


def test_world_diff_engine_warns_for_missing_worlds():
    engine = WorldDiffEngine()

    result = engine.run({})

    assert result.success is True
    assert len(result.warnings) == 2
    assert "world_a" in result.warnings[0]
    assert "world_b" in result.warnings[1]

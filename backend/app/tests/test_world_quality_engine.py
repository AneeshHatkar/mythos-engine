from backend.app.engines.world.world_quality_engine import WorldQualityEngine
from backend.app.schemas.foundation import EngineRunResult


def strong_world_state():
    return {
        "identity": {
            "world_name": "Velmora",
            "central_world_question": "Can a civilization survive when forbidden students are chosen by destiny?",
        },
        "world_dna": {
            "dominant_conflict_type": "class_vs_destiny",
            "dominant_power_source": "relic_mines_and_oath_artifacts",
        },
        "scale_granularity": {"scale_label": "epic_series_scale"},
        "rules": {
            "magic_rules": ["royal magic requires academy license"],
            "destiny_rules": ["destiny pressure cannot erase agency"],
        },
        "boundary_constraints": {"knowledge_boundaries": ["sealed archives"]},
        "contradiction_intent": {
            "intentional_hypocrisies": ["academy praises merit but restricts access by class"]
        },
        "chronology": {
            "official_history_summary": "the founding was lawful",
            "true_history_summary": "the founding hid betrayal",
        },
        "memory_archive": {"broken_promises": ["First Oath"]},
        "geography": {"regions": ["capital", "border", "low market"]},
        "environment": {"climate_zones": ["fog canals", "relic ridge"]},
        "infrastructure": {"communication_delays": ["message delay at checkpoint"]},
        "demographics": {"class_distribution": {"commoner": 0.7, "noble": 0.03}},
        "society": {"class_tiers": ["noble", "commoner", "erased"]},
        "power_structure": {"factions": ["Silent Register", "Academy Orthodoxy"]},
        "military_security": {"armies": ["Border March Battalion"]},
        "economy": {"debt_system": "relic debt funds academy"},
        "law": {"courts": ["Oath Court"], "legal_classes": ["founder", "unregistered"]},
        "belief": {"rituals": ["oath bell ceremony"], "heresies": ["Broken Oath Theology"]},
        "culture": {"naming_rules": ["family names control legal trust"]},
        "knowledge_education": {"forbidden_books": ["Forbidden Exam Scroll"]},
        "institutions": [{"name": "The Ashen Crown Academy"}],
        "technology_magic_science": {
            "communication_level": "couriers, seals, and ritual signals",
            "medicine_or_healing_level": "healing is costly",
        },
        "species_creatures": {"sacred_animals": ["ledger-crows"]},
        "artifacts": [
            {"name": "The Ashen Crown Shard"},
            {"name": "The Oath Bell"},
            {"name": "The Witness Map"},
        ],
        "aesthetic_texture": {
            "visual_palette": ["ash white", "ink black"],
            "cinematic_identity": "dark academy political fantasy with strong class visuals",
        },
        "civilization_pressure": {
            "current_crisis": "destiny pressure and relic scarcity",
            "system_breaking_points": ["archive leak", "border rebellion"],
        },
        "causality_graph": {
            "links": [
                {
                    "cause": "restricted education",
                    "effect": "forbidden study",
                    "affected_systems": ["education", "class"],
                }
            ]
        },
    }


def test_world_quality_engine_returns_engine_result():
    engine = WorldQualityEngine()

    result = engine.run(
        {
            "world_state": strong_world_state(),
            "desired_complexity": "god_level",
        }
    )

    assert isinstance(result, EngineRunResult)
    assert result.success is True
    assert result.engine_name == "world.quality_engine"
    assert "quality_summary" in result.data
    assert "consistency_report" in result.data
    assert "originality_report" in result.data
    assert "story_potential_report" in result.data
    assert "training_readiness_report" in result.data
    assert "training_notes" in result.data


def test_world_quality_engine_scores_strong_world_highly():
    engine = WorldQualityEngine()

    result = engine.run(
        {
            "world_state": strong_world_state(),
            "desired_complexity": "god_level",
        }
    )

    summary = result.data["quality_summary"]

    assert summary["consistency_score"] >= 0.7
    assert summary["originality_score"] >= 0.6
    assert summary["story_potential_score"] >= 0.7
    assert summary["franchise_potential_score"] >= 0.7
    assert summary["genericness_risk_score"] <= 0.45
    assert summary["quality_tier"] in {"strong", "excellent", "developing"}


def test_world_quality_engine_detects_missing_systems():
    engine = WorldQualityEngine()

    result = engine.run(
        {
            "world_state": {
                "identity": {"world_name": "Thin World"},
                "rules": {"magic_rules": []},
            }
        }
    )

    missing = result.data["missing_systems"]

    assert "chronology" in missing
    assert "geography" in missing
    assert "economy" in missing
    assert "law" in missing
    assert result.data["quality_summary"]["training_eligible"] is False


def test_world_quality_engine_detects_story_engines():
    engine = WorldQualityEngine()

    result = engine.run({"world_state": strong_world_state()})

    story_report = result.data["story_potential_report"]

    assert story_report["story_engines"]["class_conflict"] is True
    assert story_report["story_engines"]["forbidden_knowledge"] is True
    assert story_report["story_engines"]["political_intrigue"] is True
    assert story_report["story_engines"]["mystery_engine"] is True
    assert story_report["story_engines"]["artifact_plot"] is True
    assert len(story_report["strongest_story_engines"]) >= 5


def test_world_quality_engine_detects_contradiction_risks():
    engine = WorldQualityEngine()

    result = engine.run(
        {
            "world_state": {
                "identity": {"world_name": "Contradiction World"},
                "technology_magic_science": {
                    "communication_level": "instant communication"
                },
                "mystery": "secret hidden archive conspiracy",
                "rules": {
                    "healing": "unlimited healing",
                    "magic": "no magic but oath-magic exists",
                    "destiny": "destiny controls everything",
                },
            }
        }
    )

    risks = result.data["contradiction_risks"]

    assert any("Instant communication" in risk for risk in risks)
    assert any("Unlimited healing" in risk for risk in risks)
    assert any("Magic presence" in risk for risk in risks)
    assert any("Destiny systems" in risk for risk in risks)


def test_world_quality_engine_warns_when_world_state_missing():
    engine = WorldQualityEngine()

    result = engine.run({})

    assert result.success is True
    assert len(result.warnings) == 1
    assert "world_state" in result.warnings[0]

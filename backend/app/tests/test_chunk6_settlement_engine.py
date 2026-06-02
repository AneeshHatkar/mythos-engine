from backend.app.engines.deep_world.country_political_unit_system import CountryPoliticalUnitSystem
from backend.app.engines.deep_world.population_diversity_engine import PopulationDiversityEngine
from backend.app.engines.deep_world.settlement_engine import SettlementEngine


def build_context():
    political_system = CountryPoliticalUnitSystem()
    population_engine = PopulationDiversityEngine()

    unit = political_system.build_political_unit(source_id="settlement_context")["political_unit"]
    population = population_engine.build_population_diversity_profile(source_id="settlement_context")[
        "population_diversity_profile"
    ]

    return unit, population


def test_settlement_engine_builds_settlement():
    unit, population = build_context()
    engine = SettlementEngine()

    settlement = engine.build_settlement(
        source_id="settlement_test",
        political_unit=unit,
        population_profile=population,
        settlement_seed={
            "base_name": "Mirel",
            "unique_name": "Mirel Tidegate",
            "settlement_type": "coastal treaty town",
            "region_name": "Ashglass Coast",
        },
    )["settlement"]

    assert settlement["unique_name"] == "Mirel Tidegate"
    assert settlement["settlement_type"] == "coastal treaty town"
    assert settlement["political_unit_id"] == unit["political_unit_id"]
    assert settlement["population_diversity_profile_id"] == population["population_diversity_profile_id"]
    assert settlement["districts"]
    assert settlement["infrastructure"]
    assert settlement["religion_myth_lore"]
    assert settlement["public_history"]
    assert settlement["secret_history"]
    assert settlement["false_history"]
    assert settlement["detail_depth_score"] >= 0.75


def test_settlement_engine_builds_settlement_conflict():
    unit, population = build_context()
    engine = SettlementEngine()
    settlement = engine.build_settlement(
        source_id="conflict_test",
        political_unit=unit,
        population_profile=population,
    )["settlement"]

    conflict = engine.build_settlement_conflict(
        source_id="conflict_test",
        settlement=settlement,
        conflict_seed={"conflict_name": "Foglamp Steps Name Riot"},
    )["settlement_conflict"]

    assert conflict["settlement_id"] == settlement["settlement_id"]
    assert conflict["conflict_name"] == "Foglamp Steps Name Riot"
    assert conflict["public_issue"]
    assert conflict["secret_cause"]
    assert conflict["false_explanation"]
    assert conflict["affected_districts"]
    assert conflict["evidence"]
    assert conflict["memory_effect"]


def test_settlement_engine_builds_story_context_patch():
    unit, population = build_context()
    engine = SettlementEngine()
    settlement = engine.build_settlement(source_id="patch_test", political_unit=unit, population_profile=population)[
        "settlement"
    ]
    conflict = engine.build_settlement_conflict(source_id="patch_test", settlement=settlement)["settlement_conflict"]

    patch = engine.build_story_context_patch(
        settlement=settlement,
        settlement_conflict=conflict,
    )["story_context_patch"]

    assert patch["settlement_id"] == settlement["settlement_id"]
    assert patch["active_settlement_conflict"]["settlement_conflict_id"] == conflict["settlement_conflict_id"]
    assert "generation_hints" in patch
    assert "memory_update_candidates" in patch
    assert len(patch["memory_update_candidates"]) == 2


def test_settlement_engine_validates_settlement_and_conflict():
    unit, population = build_context()
    engine = SettlementEngine()
    settlement = engine.build_settlement(
        source_id="validate_test",
        political_unit=unit,
        population_profile=population,
    )["settlement"]
    conflict = engine.build_settlement_conflict(source_id="validate_test", settlement=settlement)["settlement_conflict"]

    settlement_validation = engine.validate_settlement(settlement=settlement)
    conflict_validation = engine.validate_settlement_conflict(settlement_conflict=conflict)

    assert settlement_validation["passed"] is True
    assert settlement_validation["missing_fields"] == []
    assert conflict_validation["passed"] is True
    assert conflict_validation["missing_fields"] == []


def test_settlement_engine_detects_bad_records():
    engine = SettlementEngine()

    settlement_validation = engine.validate_settlement(
        settlement={
            "settlement_id": "bad_settlement",
            "unique_name": "Generic Town",
            "story_use": "Bad.",
        }
    )

    conflict_validation = engine.validate_settlement_conflict(
        settlement_conflict={
            "settlement_conflict_id": "bad_conflict",
            "conflict_name": "Riot",
            "plot_effect": "Bad.",
        }
    )

    assert settlement_validation["passed"] is False
    assert settlement_validation["missing_fields"]
    assert "story_use" in settlement_validation["shallow_fields"]

    assert conflict_validation["passed"] is False
    assert conflict_validation["missing_fields"]
    assert "plot_effect" in conflict_validation["shallow_fields"]


def test_settlement_engine_summarizes_and_textualizes():
    unit, population = build_context()
    engine = SettlementEngine()
    settlement = engine.build_settlement(source_id="text_test", political_unit=unit, population_profile=population)[
        "settlement"
    ]
    conflict = engine.build_settlement_conflict(source_id="text_test", settlement=settlement)["settlement_conflict"]

    summary = engine.summarize_settlement(settlement=settlement, settlement_conflict=conflict)
    text = engine.build_settlement_text(settlement=settlement, settlement_conflict=conflict)["settlement_text"]

    assert summary["success"] is True
    assert summary["summary"]["settlement_id"] == settlement["settlement_id"]
    assert "Settlement Profile" in text
    assert "Secret History" in text
    assert "Memory Effect" in text

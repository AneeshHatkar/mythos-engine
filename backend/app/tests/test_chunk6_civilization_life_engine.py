from backend.app.engines.deep_world.civilization_life_engine import CivilizationLifeEngine
from backend.app.engines.deep_world.country_political_unit_system import CountryPoliticalUnitSystem
from backend.app.engines.deep_world.population_diversity_engine import PopulationDiversityEngine
from backend.app.engines.deep_world.settlement_engine import SettlementEngine


def build_context():
    political_system = CountryPoliticalUnitSystem()
    settlement_engine = SettlementEngine()
    population_engine = PopulationDiversityEngine()

    unit = political_system.build_political_unit(source_id="civilization_context")["political_unit"]
    settlement = settlement_engine.build_settlement(source_id="civilization_context", political_unit=unit)["settlement"]
    population = population_engine.build_population_diversity_profile(source_id="civilization_context")[
        "population_diversity_profile"
    ]

    return unit, settlement, population


def test_civilization_life_engine_builds_profile():
    unit, settlement, population = build_context()
    engine = CivilizationLifeEngine()

    profile = engine.build_civilization_life_profile(
        source_id="life_test",
        political_unit=unit,
        settlement=settlement,
        population_profile=population,
        life_seed={
            "civilization_name": "Mirel Tideglass Civic Life",
            "region_name": "Ashglass Coast",
        },
    )["civilization_life_profile"]

    assert profile["civilization_name"] == "Mirel Tideglass Civic Life"
    assert profile["region_name"] == "Ashglass Coast"
    assert profile["political_unit_id"] == unit["political_unit_id"]
    assert profile["settlement_id"] == settlement["settlement_id"]
    assert profile["population_diversity_profile_id"] == population["population_diversity_profile_id"]
    assert profile["daily_routines"]
    assert profile["work_and_labor_system"]
    assert profile["education_and_apprenticeship"]
    assert profile["food_and_public_meals"]
    assert profile["clothing_and_status_markers"]
    assert profile["detail_depth_score"] >= 0.75


def test_civilization_life_engine_builds_civic_event():
    _, settlement, _ = build_context()
    engine = CivilizationLifeEngine()
    profile = engine.build_civilization_life_profile(
        source_id="event_test",
        settlement=settlement,
    )["civilization_life_profile"]

    event = engine.build_civic_life_event(
        source_id="event_test",
        civilization_life_profile=profile,
        event_seed={
            "event_name": "Salt Tea Mourning Disruption",
            "trigger": "funeral tea petals blackened during the public meal",
        },
    )["civic_life_event"]

    assert event["civilization_life_profile_id"] == profile["civilization_life_profile_id"]
    assert event["event_name"] == "Salt Tea Mourning Disruption"
    assert event["trigger"] == "funeral tea petals blackened during the public meal"
    assert event["affected_routines"]
    assert event["affected_groups"]
    assert event["public_reaction"]
    assert event["memory_effect"]


def test_civilization_life_engine_builds_story_context_patch():
    unit, settlement, population = build_context()
    engine = CivilizationLifeEngine()
    profile = engine.build_civilization_life_profile(
        source_id="patch_test",
        political_unit=unit,
        settlement=settlement,
        population_profile=population,
    )["civilization_life_profile"]
    event = engine.build_civic_life_event(source_id="patch_test", civilization_life_profile=profile)["civic_life_event"]

    patch = engine.build_story_context_patch(
        civilization_life_profile=profile,
        civic_life_event=event,
    )["story_context_patch"]

    assert patch["civilization_life_profile_id"] == profile["civilization_life_profile_id"]
    assert patch["active_civic_life_event"]["civic_life_event_id"] == event["civic_life_event_id"]
    assert "generation_hints" in patch
    assert "memory_update_candidates" in patch
    assert len(patch["memory_update_candidates"]) == 2


def test_civilization_life_engine_validates_profile_and_event():
    _, settlement, _ = build_context()
    engine = CivilizationLifeEngine()
    profile = engine.build_civilization_life_profile(
        source_id="validate_test",
        settlement=settlement,
    )["civilization_life_profile"]
    event = engine.build_civic_life_event(
        source_id="validate_test",
        civilization_life_profile=profile,
    )["civic_life_event"]

    profile_validation = engine.validate_civilization_life_profile(civilization_life_profile=profile)
    event_validation = engine.validate_civic_life_event(civic_life_event=event)

    assert profile_validation["passed"] is True
    assert profile_validation["missing_fields"] == []
    assert event_validation["passed"] is True
    assert event_validation["missing_fields"] == []


def test_civilization_life_engine_detects_bad_records():
    engine = CivilizationLifeEngine()

    profile_validation = engine.validate_civilization_life_profile(
        civilization_life_profile={
            "civilization_life_profile_id": "bad_life",
            "civilization_name": "Generic Life",
            "story_use": "Bad.",
        }
    )

    event_validation = engine.validate_civic_life_event(
        civic_life_event={
            "civic_life_event_id": "bad_event",
            "event_name": "Meal",
            "plot_effect": "Bad.",
        }
    )

    assert profile_validation["passed"] is False
    assert profile_validation["missing_fields"]
    assert "story_use" in profile_validation["shallow_fields"]

    assert event_validation["passed"] is False
    assert event_validation["missing_fields"]
    assert "plot_effect" in event_validation["shallow_fields"]


def test_civilization_life_engine_summarizes_and_textualizes():
    _, settlement, _ = build_context()
    engine = CivilizationLifeEngine()
    profile = engine.build_civilization_life_profile(source_id="text_test", settlement=settlement)[
        "civilization_life_profile"
    ]
    event = engine.build_civic_life_event(source_id="text_test", civilization_life_profile=profile)["civic_life_event"]

    summary = engine.summarize_civilization_life(
        civilization_life_profile=profile,
        civic_life_event=event,
    )
    text = engine.build_civilization_life_text(
        civilization_life_profile=profile,
        civic_life_event=event,
    )["civilization_life_text"]

    assert summary["success"] is True
    assert summary["summary"]["civilization_life_profile_id"] == profile["civilization_life_profile_id"]
    assert "Civilization Life Profile" in text
    assert "Food and Public Meals" in text
    assert "Memory Effect" in text

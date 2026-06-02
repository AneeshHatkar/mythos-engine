from backend.app.engines.deep_world.country_political_unit_system import CountryPoliticalUnitSystem
from backend.app.engines.deep_world.economy_resource_ecology_engine import EconomyResourceEcologyEngine
from backend.app.engines.deep_world.education_schools_apprenticeship_engine import EducationSchoolsApprenticeshipEngine
from backend.app.engines.deep_world.population_diversity_engine import PopulationDiversityEngine
from backend.app.engines.deep_world.settlement_engine import SettlementEngine


def build_context():
    political_system = CountryPoliticalUnitSystem()
    settlement_engine = SettlementEngine()
    population_engine = PopulationDiversityEngine()
    economy_engine = EconomyResourceEcologyEngine()

    unit = political_system.build_political_unit(source_id="education_context")["political_unit"]
    settlement = settlement_engine.build_settlement(source_id="education_context", political_unit=unit)["settlement"]
    population = population_engine.build_population_diversity_profile(source_id="education_context")[
        "population_diversity_profile"
    ]
    economy = economy_engine.build_resource_economy_profile(
        source_id="education_context",
        political_unit=unit,
        settlement=settlement,
    )["resource_economy_profile"]

    return unit, settlement, population, economy


def test_education_engine_builds_education_system():
    unit, settlement, population, economy = build_context()
    engine = EducationSchoolsApprenticeshipEngine()

    system = engine.build_education_system(
        source_id="education_test",
        political_unit=unit,
        settlement=settlement,
        population_profile=population,
        economy_profile=economy,
        education_seed={
            "education_name": "Ashglass Tideglass Academy System",
            "region_name": "Ashglass Coast",
        },
    )["education_system"]

    assert system["education_name"] == "Ashglass Tideglass Academy System"
    assert system["region_name"] == "Ashglass Coast"
    assert system["political_unit_id"] == unit["political_unit_id"]
    assert system["settlement_id"] == settlement["settlement_id"]
    assert system["population_diversity_profile_id"] == population["population_diversity_profile_id"]
    assert system["resource_economy_profile_id"] == economy["resource_economy_profile_id"]
    assert system["school_types"]
    assert system["named_institutions"]
    assert system["subjects_taught"]
    assert system["apprenticeship_paths"]
    assert system["detail_depth_score"] >= 0.75


def test_education_engine_builds_education_event():
    unit, settlement, population, economy = build_context()
    engine = EducationSchoolsApprenticeshipEngine()
    system = engine.build_education_system(
        source_id="event_test",
        political_unit=unit,
        settlement=settlement,
        population_profile=population,
        economy_profile=economy,
    )["education_system"]

    event = engine.build_education_event(
        source_id="event_test",
        education_system=system,
        event_seed={
            "event_name": "Underlamp Student Arrest",
            "trigger": "students were caught carrying forbidden map lessons",
        },
    )["education_event"]

    assert event["education_system_id"] == system["education_system_id"]
    assert event["event_name"] == "Underlamp Student Arrest"
    assert event["trigger"] == "students were caught carrying forbidden map lessons"
    assert event["affected_institutions"]
    assert event["affected_groups"]
    assert event["public_consequence"]
    assert event["memory_effect"]


def test_education_engine_builds_story_context_patch():
    unit, settlement, population, economy = build_context()
    engine = EducationSchoolsApprenticeshipEngine()
    system = engine.build_education_system(
        source_id="patch_test",
        political_unit=unit,
        settlement=settlement,
        population_profile=population,
        economy_profile=economy,
    )["education_system"]
    event = engine.build_education_event(source_id="patch_test", education_system=system)["education_event"]

    patch = engine.build_story_context_patch(education_system=system, education_event=event)["story_context_patch"]

    assert patch["education_system_id"] == system["education_system_id"]
    assert patch["active_education_event"]["education_event_id"] == event["education_event_id"]
    assert "generation_hints" in patch
    assert "memory_update_candidates" in patch
    assert len(patch["memory_update_candidates"]) == 2


def test_education_engine_validates_system_and_event():
    unit, settlement, population, economy = build_context()
    engine = EducationSchoolsApprenticeshipEngine()
    system = engine.build_education_system(
        source_id="validate_test",
        political_unit=unit,
        settlement=settlement,
        population_profile=population,
        economy_profile=economy,
    )["education_system"]
    event = engine.build_education_event(source_id="validate_test", education_system=system)["education_event"]

    system_validation = engine.validate_education_system(education_system=system)
    event_validation = engine.validate_education_event(education_event=event)

    assert system_validation["passed"] is True
    assert system_validation["missing_fields"] == []
    assert event_validation["passed"] is True
    assert event_validation["missing_fields"] == []


def test_education_engine_detects_bad_records():
    engine = EducationSchoolsApprenticeshipEngine()

    system_validation = engine.validate_education_system(
        education_system={
            "education_system_id": "bad_school",
            "education_name": "Generic School",
            "story_use": "Bad.",
        }
    )

    event_validation = engine.validate_education_event(
        education_event={
            "education_event_id": "bad_event",
            "event_name": "Exam",
            "plot_effect": "Bad.",
        }
    )

    assert system_validation["passed"] is False
    assert system_validation["missing_fields"]
    assert "story_use" in system_validation["shallow_fields"]

    assert event_validation["passed"] is False
    assert event_validation["missing_fields"]
    assert "plot_effect" in event_validation["shallow_fields"]


def test_education_engine_summarizes_and_textualizes():
    unit, settlement, population, economy = build_context()
    engine = EducationSchoolsApprenticeshipEngine()
    system = engine.build_education_system(
        source_id="text_test",
        political_unit=unit,
        settlement=settlement,
        population_profile=population,
        economy_profile=economy,
    )["education_system"]
    event = engine.build_education_event(source_id="text_test", education_system=system)["education_event"]

    summary = engine.summarize_education_system(education_system=system, education_event=event)
    text = engine.build_education_text(education_system=system, education_event=event)["education_text"]

    assert summary["success"] is True
    assert summary["summary"]["education_system_id"] == system["education_system_id"]
    assert "Education, Schools, Academies, and Apprenticeship Profile" in text
    assert "Named Institutions" in text
    assert "Memory Effect" in text

from backend.app.engines.deep_world.architecture_built_environment_engine import ArchitectureBuiltEnvironmentEngine
from backend.app.engines.deep_world.country_political_unit_system import CountryPoliticalUnitSystem
from backend.app.engines.deep_world.settlement_engine import SettlementEngine


def build_context():
    political_system = CountryPoliticalUnitSystem()
    settlement_engine = SettlementEngine()

    unit = political_system.build_political_unit(source_id="architecture_context")["political_unit"]
    settlement = settlement_engine.build_settlement(
        source_id="architecture_context",
        political_unit=unit,
    )["settlement"]

    return unit, settlement


def test_architecture_engine_builds_built_environment_profile():
    unit, settlement = build_context()
    engine = ArchitectureBuiltEnvironmentEngine()

    profile = engine.build_built_environment_profile(
        source_id="architecture_test",
        settlement=settlement,
        political_unit=unit,
        environment_seed={
            "style_name": "Mirel Tideglass Civic Architecture",
            "region_name": "Ashglass Coast",
        },
    )["built_environment_profile"]

    assert profile["style_name"] == "Mirel Tideglass Civic Architecture"
    assert profile["settlement_id"] == settlement["settlement_id"]
    assert profile["political_unit_id"] == unit["political_unit_id"]
    assert profile["core_materials"]
    assert profile["building_types"]
    assert profile["street_layout"]
    assert profile["class_spatial_logic"]
    assert profile["religious_spatial_logic"]
    assert profile["hidden_structures"]
    assert profile["scene_blocking_rules"]
    assert profile["detail_depth_score"] >= 0.75


def test_architecture_engine_builds_architectural_event():
    _, settlement = build_context()
    engine = ArchitectureBuiltEnvironmentEngine()
    profile = engine.build_built_environment_profile(
        source_id="event_test",
        settlement=settlement,
    )["built_environment_profile"]

    event = engine.build_architectural_event(
        source_id="event_test",
        built_environment_profile=profile,
        event_seed={
            "event_name": "Archive Floor Collapse",
            "location": "saltbark archive house",
        },
    )["architectural_event"]

    assert event["built_environment_profile_id"] == profile["built_environment_profile_id"]
    assert event["event_name"] == "Archive Floor Collapse"
    assert event["location"] == "saltbark archive house"
    assert event["revealed_structure"]
    assert event["affected_groups"]
    assert event["memory_effect"]


def test_architecture_engine_builds_story_context_patch():
    _, settlement = build_context()
    engine = ArchitectureBuiltEnvironmentEngine()
    profile = engine.build_built_environment_profile(source_id="patch_test", settlement=settlement)[
        "built_environment_profile"
    ]
    event = engine.build_architectural_event(
        source_id="patch_test",
        built_environment_profile=profile,
    )["architectural_event"]

    patch = engine.build_story_context_patch(
        built_environment_profile=profile,
        architectural_event=event,
    )["story_context_patch"]

    assert patch["built_environment_profile_id"] == profile["built_environment_profile_id"]
    assert patch["active_architectural_event"]["architectural_event_id"] == event["architectural_event_id"]
    assert "generation_hints" in patch
    assert "memory_update_candidates" in patch
    assert len(patch["memory_update_candidates"]) == 2


def test_architecture_engine_validates_profile_and_event():
    _, settlement = build_context()
    engine = ArchitectureBuiltEnvironmentEngine()
    profile = engine.build_built_environment_profile(source_id="validate_test", settlement=settlement)[
        "built_environment_profile"
    ]
    event = engine.build_architectural_event(
        source_id="validate_test",
        built_environment_profile=profile,
    )["architectural_event"]

    profile_validation = engine.validate_built_environment_profile(built_environment_profile=profile)
    event_validation = engine.validate_architectural_event(architectural_event=event)

    assert profile_validation["passed"] is True
    assert profile_validation["missing_fields"] == []
    assert event_validation["passed"] is True
    assert event_validation["missing_fields"] == []


def test_architecture_engine_detects_bad_records():
    engine = ArchitectureBuiltEnvironmentEngine()

    profile_validation = engine.validate_built_environment_profile(
        built_environment_profile={
            "built_environment_profile_id": "bad_profile",
            "style_name": "Generic Buildings",
            "story_use": "Bad.",
        }
    )

    event_validation = engine.validate_architectural_event(
        architectural_event={
            "architectural_event_id": "bad_event",
            "event_name": "Wall",
            "plot_effect": "Bad.",
        }
    )

    assert profile_validation["passed"] is False
    assert profile_validation["missing_fields"]
    assert "story_use" in profile_validation["shallow_fields"]

    assert event_validation["passed"] is False
    assert event_validation["missing_fields"]
    assert "plot_effect" in event_validation["shallow_fields"]


def test_architecture_engine_summarizes_and_textualizes():
    _, settlement = build_context()
    engine = ArchitectureBuiltEnvironmentEngine()
    profile = engine.build_built_environment_profile(source_id="text_test", settlement=settlement)[
        "built_environment_profile"
    ]
    event = engine.build_architectural_event(
        source_id="text_test",
        built_environment_profile=profile,
    )["architectural_event"]

    summary = engine.summarize_built_environment(
        built_environment_profile=profile,
        architectural_event=event,
    )
    text = engine.build_built_environment_text(
        built_environment_profile=profile,
        architectural_event=event,
    )["built_environment_text"]

    assert summary["success"] is True
    assert summary["summary"]["built_environment_profile_id"] == profile["built_environment_profile_id"]
    assert "Architecture + Built Environment Profile" in text
    assert "Hidden Structures" in text
    assert "Memory Effect" in text

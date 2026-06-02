from backend.app.engines.deep_world.ecology_engine import EcologyEngine
from backend.app.schemas.deep_world import DeepWorldEcologySystem, DeepWorldValidationStatus


def test_ecology_engine_builds_ecology_system():
    engine = EcologyEngine()

    ecology = engine.build_ecology_system(
        source_id="ecology_test",
        ecology_seed={
            "name": "Ashglass Tidepool Ecology",
            "region_name": "Ashglass Coast",
            "biome_type": "ash coast tidepool biome",
            "keystone_species": ["glass kelp", "blue shell crabs", "tide ravens"],
            "primary_resource": "glass kelp medicine",
            "ecological_pressure": "red tide ash bloom",
            "collapse_risk": "glass kelp rot causing medicine shortage",
            "tags": ["coast", "tidepool"],
        },
        story_context={"genre": "fantasy", "tone": "mythic"},
    )["deep_world_ecology_system"]

    assert isinstance(ecology, DeepWorldEcologySystem)
    assert ecology.name == "Ashglass Tidepool Ecology"
    assert ecology.validation_status == DeepWorldValidationStatus.VALIDATED
    assert "glass kelp" in ecology.keystone_species
    assert "coast" in ecology.tags
    assert ecology.story_use
    assert ecology.character_effect
    assert ecology.plot_effect
    assert ecology.memory_effect


def test_ecology_engine_simulates_ecological_shift():
    engine = EcologyEngine()
    ecology = engine.build_ecology_system(source_id="shift_test")["deep_world_ecology_system"]

    shift = engine.simulate_ecological_shift(
        source_id="shift_test",
        ecology=ecology,
        shift_seed={
            "shift_name": "Fog Moss Collapse",
            "severity": "critical",
            "affected_species": ["fog moss", "glass-wing moths"],
            "affected_resources": ["medicine", "route dye"],
            "affected_groups": ["healers", "road guides"],
        },
    )["ecological_shift"]

    assert shift["shift_name"] == "Fog Moss Collapse"
    assert shift["ecology_id"] == ecology.element_id
    assert shift["affected_species"]
    assert shift["affected_resources"]
    assert shift["affected_groups"]
    assert shift["story_use"]
    assert shift["character_effect"]
    assert shift["plot_effect"]
    assert shift["memory_effect"]
    assert shift["lore_effect"]
    assert shift["detail_depth_score"] >= 0.75


def test_ecology_engine_builds_story_context_patch():
    engine = EcologyEngine()
    ecology = engine.build_ecology_system(source_id="patch_test")["deep_world_ecology_system"]
    shift = engine.simulate_ecological_shift(source_id="patch_test", ecology=ecology)["ecological_shift"]

    patch = engine.build_story_context_patch(
        ecology=ecology,
        ecological_shift=shift,
    )["story_context_patch"]

    assert patch["ecology_id"] == ecology.element_id
    assert patch["active_ecological_shift"]["ecological_shift_id"] == shift["ecological_shift_id"]
    assert "generation_hints" in patch
    assert "memory_update_candidates" in patch
    assert len(patch["memory_update_candidates"]) >= 2


def test_ecology_engine_validates_ecology_and_shift():
    engine = EcologyEngine()
    ecology = engine.build_ecology_system(source_id="validate_test")["deep_world_ecology_system"]
    shift = engine.simulate_ecological_shift(source_id="validate_test", ecology=ecology)["ecological_shift"]

    ecology_validation = engine.validate_ecology_system(ecology=ecology)
    shift_validation = engine.validate_ecological_shift(ecological_shift=shift)

    assert ecology_validation["passed"] is True
    assert ecology_validation["blockers"] == []
    assert shift_validation["passed"] is True
    assert shift_validation["missing_fields"] == []


def test_ecology_engine_detects_bad_ecological_shift():
    engine = EcologyEngine()

    validation = engine.validate_ecological_shift(
        ecological_shift={
            "ecological_shift_id": "bad_shift",
            "shift_name": "Bad Rot",
            "plot_effect": "Bad.",
        }
    )

    assert validation["passed"] is False
    assert validation["missing_fields"]
    assert "plot_effect" in validation["shallow_fields"]


def test_ecology_engine_summarizes_and_textualizes():
    engine = EcologyEngine()
    ecology = engine.build_ecology_system(source_id="text_test")["deep_world_ecology_system"]

    summary = engine.summarize_ecology_system(ecology=ecology)
    text = engine.build_ecology_text(ecology=ecology)["ecology_text"]

    assert summary["success"] is True
    assert summary["summary"]["ecology_id"] == ecology.element_id
    assert "Deep World Ecology System" in text
    assert "Keystone Species" in text
    assert "Memory Effect" in text

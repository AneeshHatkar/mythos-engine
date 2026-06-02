from backend.app.engines.deep_world.fauna_generator import FaunaGenerator
from backend.app.schemas.deep_world import DeepWorldFauna, DeepWorldValidationStatus


def test_fauna_generator_builds_detailed_named_fauna():
    generator = FaunaGenerator()

    fauna = generator.build_fauna(
        source_id="fauna_test",
        fauna_seed={
            "base_name": "Orun",
            "unique_name": "Orun Tide Raven",
            "region_name": "Ashglass Coast",
            "culture": "drowned temple omen culture",
            "name_meaning": "black-wing tide witness",
            "tags": ["coast", "omen"],
        },
        story_context={"genre": "fantasy", "tone": "mythic"},
    )["deep_world_fauna"]

    assert isinstance(fauna, DeepWorldFauna)
    assert fauna.name == "Orun Tide Raven"
    assert fauna.validation_status == DeepWorldValidationStatus.VALIDATED
    assert fauna.metadata["unique_name"] == "Orun Tide Raven"
    assert fauna.metadata["name_origin"]
    assert fauna.metadata["name_meaning"] == "black-wing tide witness"
    assert fauna.metadata["name_language_logic"]
    assert fauna.metadata["detail_depth_score"] >= 0.75
    assert "omen" in fauna.tags
    assert fauna.story_use
    assert fauna.character_effect
    assert fauna.plot_effect
    assert fauna.memory_effect


def test_fauna_generator_builds_story_context_patch():
    generator = FaunaGenerator()
    fauna = generator.build_fauna(source_id="fauna_patch_test")["deep_world_fauna"]

    patch = generator.build_fauna_story_context_patch(fauna=fauna)["story_context_patch"]

    assert patch["fauna_id"] == fauna.element_id
    assert patch["identity"]["unique_name"] == fauna.name
    assert patch["identity"]["name_origin"]
    assert "generation_hints" in patch
    assert "memory_update_candidates" in patch
    assert patch["behavior_patterns"]


def test_fauna_generator_simulates_fauna_event():
    generator = FaunaGenerator()
    fauna = generator.build_fauna(source_id="fauna_event_test")["deep_world_fauna"]

    event = generator.simulate_fauna_event(
        source_id="fauna_event_test",
        fauna=fauna,
        event_seed={
            "event_name": "Tide Raven Omen Flight",
            "event_type": "omen_migration",
            "trigger": "ravens circled the drowned temple before blue lightning",
            "consequence": "the village delays sailing and discovers a hidden wreck",
        },
    )["fauna_event"]

    assert event["fauna_id"] == fauna.element_id
    assert event["event_name"] == "Tide Raven Omen Flight"
    assert event["story_use"]
    assert event["character_effect"]
    assert event["plot_effect"]
    assert event["memory_effect"]
    assert event["lore_effect"]
    assert event["detail_depth_score"] >= 0.75


def test_fauna_generator_validates_fauna_and_event():
    generator = FaunaGenerator()
    fauna = generator.build_fauna(source_id="fauna_validate_test")["deep_world_fauna"]
    event = generator.simulate_fauna_event(source_id="fauna_validate_test", fauna=fauna)["fauna_event"]

    fauna_validation = generator.validate_fauna(fauna=fauna)
    event_validation = generator.validate_fauna_event(fauna_event=event)

    assert fauna_validation["passed"] is True
    assert fauna_validation["blockers"] == []
    assert event_validation["passed"] is True
    assert event_validation["missing_fields"] == []


def test_fauna_generator_detects_bad_fauna_event():
    generator = FaunaGenerator()

    validation = generator.validate_fauna_event(
        fauna_event={
            "fauna_event_id": "bad_fauna_event",
            "event_name": "Animal",
            "plot_effect": "Bad.",
        }
    )

    assert validation["passed"] is False
    assert validation["missing_fields"]
    assert "plot_effect" in validation["shallow_fields"]


def test_fauna_generator_summarizes_and_textualizes():
    generator = FaunaGenerator()
    fauna = generator.build_fauna(source_id="fauna_text_test")["deep_world_fauna"]

    summary = generator.summarize_fauna(fauna=fauna)
    text = generator.build_fauna_text(fauna=fauna)["fauna_text"]

    assert summary["success"] is True
    assert summary["summary"]["fauna_id"] == fauna.element_id
    assert "Deep World Fauna" in text
    assert "Name Origin" in text
    assert "Memory Effect" in text

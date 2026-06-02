from backend.app.engines.deep_world.flora_generator import FloraGenerator
from backend.app.schemas.deep_world import DeepWorldFlora, DeepWorldValidationStatus


def test_flora_generator_builds_detailed_named_flora():
    generator = FloraGenerator()

    flora = generator.build_flora(
        source_id="flora_test",
        flora_seed={
            "base_name": "Nalara",
            "unique_name": "Nalara Glasspetal",
            "region_name": "Ashglass Coast",
            "culture": "drowned temple mourning culture",
            "name_meaning": "glass grief flower",
            "tags": ["coast", "medicine"],
        },
        story_context={"genre": "fantasy", "tone": "mythic"},
    )["deep_world_flora"]

    assert isinstance(flora, DeepWorldFlora)
    assert flora.name == "Nalara Glasspetal"
    assert flora.validation_status == DeepWorldValidationStatus.VALIDATED
    assert flora.metadata["unique_name"] == "Nalara Glasspetal"
    assert flora.metadata["name_origin"]
    assert flora.metadata["name_meaning"] == "glass grief flower"
    assert flora.metadata["name_language_logic"]
    assert flora.metadata["detail_depth_score"] >= 0.75
    assert "medicine" in flora.tags
    assert flora.story_use
    assert flora.character_effect
    assert flora.plot_effect
    assert flora.memory_effect


def test_flora_generator_builds_story_context_patch():
    generator = FloraGenerator()
    flora = generator.build_flora(source_id="flora_patch_test")["deep_world_flora"]

    patch = generator.build_flora_story_context_patch(flora=flora)["story_context_patch"]

    assert patch["flora_id"] == flora.element_id
    assert patch["identity"]["unique_name"] == flora.name
    assert patch["identity"]["name_origin"]
    assert "generation_hints" in patch
    assert "memory_update_candidates" in patch
    assert patch["uses"]


def test_flora_generator_simulates_flora_event():
    generator = FloraGenerator()
    flora = generator.build_flora(source_id="flora_event_test")["deep_world_flora"]

    event = generator.simulate_flora_event(
        source_id="flora_event_test",
        flora=flora,
        event_seed={
            "event_name": "Ashbloom Poison Witness",
            "event_type": "court_evidence",
            "trigger": "petals blackened in a witness bowl",
            "consequence": "the heir's natural-death claim becomes impossible",
        },
    )["flora_event"]

    assert event["flora_id"] == flora.element_id
    assert event["event_name"] == "Ashbloom Poison Witness"
    assert event["story_use"]
    assert event["character_effect"]
    assert event["plot_effect"]
    assert event["memory_effect"]
    assert event["lore_effect"]
    assert event["detail_depth_score"] >= 0.75


def test_flora_generator_validates_flora_and_event():
    generator = FloraGenerator()
    flora = generator.build_flora(source_id="flora_validate_test")["deep_world_flora"]
    event = generator.simulate_flora_event(source_id="flora_validate_test", flora=flora)["flora_event"]

    flora_validation = generator.validate_flora(flora=flora)
    event_validation = generator.validate_flora_event(flora_event=event)

    assert flora_validation["passed"] is True
    assert flora_validation["blockers"] == []
    assert event_validation["passed"] is True
    assert event_validation["missing_fields"] == []


def test_flora_generator_detects_bad_flora_event():
    generator = FloraGenerator()

    validation = generator.validate_flora_event(
        flora_event={
            "flora_event_id": "bad_flora_event",
            "event_name": "Flower",
            "plot_effect": "Bad.",
        }
    )

    assert validation["passed"] is False
    assert validation["missing_fields"]
    assert "plot_effect" in validation["shallow_fields"]


def test_flora_generator_summarizes_and_textualizes():
    generator = FloraGenerator()
    flora = generator.build_flora(source_id="flora_text_test")["deep_world_flora"]

    summary = generator.summarize_flora(flora=flora)
    text = generator.build_flora_text(flora=flora)["flora_text"]

    assert summary["success"] is True
    assert summary["summary"]["flora_id"] == flora.element_id
    assert "Deep World Flora" in text
    assert "Name Origin" in text
    assert "Memory Effect" in text

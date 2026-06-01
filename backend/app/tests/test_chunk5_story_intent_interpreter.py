from backend.app.engines.story_generation.story_intent_interpreter import StoryIntentInterpreter
from backend.app.schemas.story_generation import GenerationMode, StoryFormat, StoryIntent


def test_intent_interpreter_detects_dark_academy_romance_scene():
    engine = StoryIntentInterpreter()

    result = engine.interpret(
        intent_id="intent_dark_romance",
        user_prompt="Write a dark academy tragic romance scene with betrayal and rich worldbuilding, not cheesy.",
    )

    intent = result["story_intent"]

    assert result["success"] is True
    assert intent.desired_format == StoryFormat.scene
    assert intent.generation_mode == GenerationMode.full_scene
    assert "dark_academy" in intent.genres
    assert "romance" in intent.genres
    assert "tragic" in intent.tone_tags
    assert "betrayal" in intent.required_emotional_beats
    assert intent.worldbuilding_density == 0.85
    assert "cheesy" in intent.forbidden_elements


def test_intent_interpreter_detects_screenplay_mode():
    engine = StoryIntentInterpreter()

    result = engine.interpret(
        intent_id="intent_script",
        user_prompt="Make this as a screenplay scene, cinematic and tense, with lots of dialogue.",
    )

    intent = result["story_intent"]

    assert intent.desired_format == StoryFormat.screenplay
    assert intent.generation_mode == GenerationMode.screenplay_scene
    assert "cinematic" in intent.tone_tags
    assert "tense" in intent.tone_tags
    assert intent.dialogue_density == 0.8


def test_intent_interpreter_detects_large_cast_and_destined_people():
    engine = StoryIntentInterpreter()

    result = engine.interpret(
        intent_id="intent_large_cast",
        user_prompt="Create a saga with 27 destined people, political betrayal, war, and a cliffhanger.",
    )

    intent = result["story_intent"]

    assert intent.desired_format == StoryFormat.multi_book_arc
    assert intent.generation_mode == GenerationMode.multi_book_arc
    assert intent.preferred_character_count == 27
    assert "political" in intent.genres
    assert "action" in intent.genres
    assert "political_betrayal" in intent.required_plot_beats
    assert intent.ending_preference == "cliffhanger"
    assert any("Large cast detected" in warning for warning in result["warnings"])


def test_intent_interpreter_detects_long_form_warning():
    engine = StoryIntentInterpreter()

    result = engine.interpret(
        intent_id="intent_long_form",
        user_prompt="I want thousands of pages of fantasy story with 1000 characters and franchise potential.",
    )

    intent = result["story_intent"]

    assert intent.preferred_character_count == 1000
    assert intent.target_length == "very_long"
    assert intent.commercial_target == "franchise_potential"
    assert any("Long-form generation detected" in warning for warning in result["warnings"])


def test_intent_interpreter_extracts_required_character_ids():
    engine = StoryIntentInterpreter()

    result = engine.interpret(
        intent_id="intent_chars",
        user_prompt="Write a scene with char_kael and char_seren where the secret is revealed.",
    )

    intent = result["story_intent"]

    assert intent.required_character_ids == ["char_kael", "char_seren"]
    assert "secret_reveal" in intent.required_plot_beats


def test_intent_interpreter_uses_defaults_when_unclear():
    engine = StoryIntentInterpreter()

    result = engine.interpret(
        intent_id="intent_defaults",
        user_prompt="Make something cool.",
        defaults={
            "desired_format": "chapter",
            "generation_mode": "chapter",
            "genres": ["fantasy"],
            "tone_tags": ["epic"],
            "preferred_character_count": 5,
        },
    )

    intent = result["story_intent"]

    assert intent.desired_format == StoryFormat.chapter
    assert intent.generation_mode == GenerationMode.chapter
    assert intent.genres == ["fantasy"]
    assert intent.tone_tags == ["epic"]
    assert intent.preferred_character_count == 5


def test_intent_interpreter_explain_intent():
    engine = StoryIntentInterpreter()

    interpreted = engine.interpret(
        intent_id="intent_explain",
        user_prompt="Write a tragic novel chapter with mystery and a bittersweet ending.",
    )

    explanation = engine.explain_intent(intent=interpreted["story_intent"])

    assert explanation["success"] is True
    assert explanation["summary"]["format"] == "novel"
    assert explanation["summary"]["ending_preference"] == "bittersweet"
    assert len(explanation["why_it_matters"]) >= 2


def test_intent_interpreter_merge_overrides():
    engine = StoryIntentInterpreter()

    interpreted = engine.interpret(
        intent_id="intent_override",
        user_prompt="Write a scene.",
    )

    merged = engine.merge_intent_with_overrides(
        intent=interpreted["story_intent"],
        overrides={
            "desired_format": "screenplay",
            "generation_mode": "screenplay_scene",
            "genres": ["dark_academy", "romance"],
            "tone_tags": ["tense"],
        },
    )

    intent = merged["story_intent"]

    assert merged["success"] is True
    assert intent.desired_format == StoryFormat.screenplay
    assert intent.generation_mode == GenerationMode.screenplay_scene
    assert intent.genres == ["dark_academy", "romance"]
    assert "desired_format" in merged["overrides_applied"]


def test_intent_interpreter_returns_story_intent_dict():
    engine = StoryIntentInterpreter()

    result = engine.interpret(
        intent_id="intent_dict",
        user_prompt="Write a comedy game scene with choices.",
    )

    data = result["story_intent_dict"]

    assert data["intent_id"] == "intent_dict"
    assert data["desired_format"] == "game_scene"
    assert data["generation_mode"] == "interactive_game_scene"
    assert "comedy" in data["genres"]


def test_story_intent_direct_model_still_works_with_engine_output_contract():
    intent = StoryIntent(
        intent_id="intent_manual",
        user_prompt="Manual test.",
        desired_format=StoryFormat.scene,
        generation_mode=GenerationMode.full_scene,
    )

    engine = StoryIntentInterpreter()
    explanation = engine.explain_intent(intent=intent)

    assert explanation["summary"]["format"] == "scene"
    assert explanation["summary"]["generation_mode"] == "full_scene"

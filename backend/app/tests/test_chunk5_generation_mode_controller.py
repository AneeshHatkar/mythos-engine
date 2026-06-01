from backend.app.engines.story_generation.generation_mode_controller import GenerationModeController
from backend.app.schemas.story_generation import GenerationMode, StoryFormat, StoryIntent


def make_intent(**kwargs):
    data = {
        "intent_id": "intent_mode_test",
        "user_prompt": "Write a dark academy scene.",
        "desired_format": StoryFormat.scene,
        "generation_mode": GenerationMode.full_scene,
        "genres": ["dark_academy"],
        "tone_tags": ["tense"],
    }
    data.update(kwargs)
    return StoryIntent(**data)


def test_generation_mode_controller_full_scene_pipeline():
    controller = GenerationModeController()
    intent = make_intent()

    result = controller.choose_mode(intent=intent)

    assert result["success"] is True
    assert result["selected_mode"] == "full_scene"
    assert "scene_blueprint" in result["pipeline"]
    assert "StoryProvenanceRecord" in result["expected_outputs"]
    assert result["requires_handoff"] is True


def test_generation_mode_controller_screenplay_pipeline():
    controller = GenerationModeController()
    intent = make_intent(
        user_prompt="Write this as a screenplay scene.",
        desired_format=StoryFormat.screenplay,
        generation_mode=GenerationMode.full_scene,
    )

    result = controller.choose_mode(intent=intent)

    assert result["selected_mode"] == "screenplay_scene"
    assert "screenplay_formatter" in result["pipeline"]
    assert result["expected_outputs"] == ["ScriptDraft"]


def test_generation_mode_controller_dialogue_only_pipeline():
    controller = GenerationModeController()
    intent = make_intent(
        user_prompt="Dialogue only between char_kael and char_seren.",
        generation_mode=GenerationMode.dialogue_only,
    )

    result = controller.choose_mode(intent=intent)

    assert result["selected_mode"] == "dialogue_only"
    assert "dialogue_draft" in result["pipeline"]
    assert result["requires_handoff"] is True


def test_generation_mode_controller_large_cast_routes_to_multi_book():
    controller = GenerationModeController()
    intent = make_intent(
        user_prompt="Generate thousands of pages with 1000 characters.",
        target_length="very_long",
        preferred_character_count=1000,
    )

    result = controller.choose_mode(intent=intent)

    assert result["selected_mode"] == "multi_book_arc"
    assert result["large_scale_mode"] is True
    assert any("Huge cast detected" in warning for warning in result["warnings"])


def test_generation_mode_controller_chapter_mode_uses_memory_anchor():
    controller = GenerationModeController()
    intent = make_intent(
        user_prompt="Write the next chapter.",
        desired_format=StoryFormat.chapter,
        generation_mode=GenerationMode.chapter,
    )

    result = controller.choose_mode(intent=intent)

    assert result["selected_mode"] == "chapter"
    assert result["requires_memory_anchor"] is True
    assert "chapter_assembly" in result["pipeline"]


def test_generation_mode_controller_continue_story_warns_without_anchor():
    controller = GenerationModeController()
    intent = make_intent(
        user_prompt="Continue the story from the previous scene.",
        generation_mode=GenerationMode.continue_story,
    )

    result = controller.choose_mode(intent=intent, available_context={})

    assert result["selected_mode"] == "continue_story"
    assert result["requires_memory_anchor"] is True
    assert any("story memory anchors" in warning for warning in result["warnings"])


def test_generation_mode_controller_rewrite_mode_requires_existing_draft():
    controller = GenerationModeController()
    intent = make_intent(
        user_prompt="Rewrite this scene and make it less generic.",
        generation_mode=GenerationMode.rewrite_existing,
    )

    result = controller.choose_mode(intent=intent)

    assert result["selected_mode"] == "rewrite_existing"
    assert result["requires_existing_draft"] is True
    assert any("existing draft IDs" in warning for warning in result["warnings"])


def test_generation_mode_controller_builds_execution_plan():
    controller = GenerationModeController()
    intent = make_intent()

    result = controller.build_mode_plan(intent=intent)

    assert result["success"] is True
    assert result["mode_decision"]["selected_mode"] == "full_scene"
    assert result["execution_plan"][0]["step_index"] == 1
    assert result["handoff_to_next_engine"]["next_engine"] == "story_generation.generation_contract_resolver"


def test_generation_mode_controller_compares_modes():
    controller = GenerationModeController()
    intent = make_intent(
        user_prompt="Write a screenplay scene.",
        desired_format=StoryFormat.screenplay,
    )

    result = controller.compare_modes(
        intent=intent,
        candidate_modes=[GenerationMode.full_scene, GenerationMode.screenplay_scene],
    )

    assert result["success"] is True
    assert result["best_mode"] == "screenplay_scene"
    assert result["ranked_modes"][0]["recommended"] is True


def test_generation_mode_controller_game_scene_pipeline():
    controller = GenerationModeController()
    intent = make_intent(
        user_prompt="Make it an interactive game scene with choices.",
        desired_format=StoryFormat.game_scene,
        generation_mode=GenerationMode.interactive_game_scene,
    )

    result = controller.choose_mode(intent=intent)

    assert result["selected_mode"] == "interactive_game_scene"
    assert "choice_points" in result["pipeline"]
    assert result["expected_outputs"] == ["InteractiveSceneDraft"]

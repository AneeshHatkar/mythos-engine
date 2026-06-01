from backend.app.engines.story_generation.format_adapter_engine import FormatAdapterEngine
from backend.app.schemas.story_generation import (
    GeneratedChapter,
    GenerationContract,
    HandoffReference,
    LongFormContinuationAnchor,
    StoryFormat,
)


def build_contract(selected_format=StoryFormat.novel):
    return GenerationContract(
        generation_contract_id="contract_format",
        story_intent_id="intent_format",
        handoff_reference=HandoffReference(simulation_id="sim_format"),
        allowed_formats=[StoryFormat.novel, StoryFormat.screenplay, StoryFormat.game_scene, StoryFormat.chapter],
        selected_format=selected_format,
        required_character_ids=["char_kael", "char_seren"],
        tone_contract={"tone_tags": ["tense"], "genres": ["dark_academy"], "dialogue_density": 0.6},
        format_contract={"selected_format": selected_format.value},
        quality_thresholds={"overall_score": 0.7},
        originality_rules={"no_raw_source_text": True},
    )


def build_chapter():
    return GeneratedChapter(
        chapter_id="chapter_format",
        chapter_number=1,
        title="The Badge",
        chapter_text="Kael and Seren face the Oath Court.",
        scene_ids=["scene_001"],
        assembled_scene_ids=["assembled_scene_001"],
        used_character_ids=["char_kael", "char_seren"],
        used_relationship_ids=["rel_kael_seren"],
        used_secret_ids=["secret_seren_source"],
        used_causal_ids=["cause_trial_reveal", "cons_reputation_shift"],
        used_world_details=["Oath Court"],
        open_loops=[
            {"loop_id": "open_loop_secret", "description": "Secret remains hidden.", "status": "open"}
        ],
        next_chapter_hooks=["Seren refuses to deny the badge."],
        quality_summary={"failed_scene_count": 0},
    )


def build_anchor():
    return LongFormContinuationAnchor(
        anchor_id="continuation_anchor_format",
        chapter_id="chapter_format",
        chapter_number=1,
        active_character_ids=["char_kael", "char_seren"],
        active_relationship_ids=["rel_kael_seren"],
        active_secret_ids=["secret_seren_source"],
        active_causal_ids=["cause_trial_reveal"],
        active_world_details=["Oath Court"],
        open_loops=[
            {"loop_id": "open_loop_secret", "description": "Secret remains hidden.", "status": "open"}
        ],
        next_chapter_hooks=["Seren refuses to deny the badge."],
        continuity_reminders=["Do not reveal secret_seren_source too early."],
    )


def test_format_adapter_builds_novel_plan():
    engine = FormatAdapterEngine()

    result = engine.build_format_adaptation_plan(
        target_format=StoryFormat.novel,
        source_id="chapter_format",
        generation_contract=build_contract(StoryFormat.novel),
        chapter=build_chapter(),
        continuation_anchor=build_anchor(),
        story_context={"story_context_id": "storyctx_format"},
    )

    plan = result["format_adaptation_plan"]

    assert result["success"] is True
    assert plan.target_format == "novel"
    assert plan.structure_rules["unit_type"] == "novel_prose"
    assert plan.prose_rules["internality"] == "high"
    assert plan.dialogue_rules["speaker_tags"] == "novelistic"
    assert "secret_seren_source" in plan.continuity_rules["must_preserve_secret_ids"]


def test_format_adapter_builds_screenplay_plan():
    engine = FormatAdapterEngine()

    plan = engine.build_format_adaptation_plan(
        target_format=StoryFormat.screenplay,
        source_id="chapter_format",
        generation_contract=build_contract(StoryFormat.screenplay),
        chapter=build_chapter(),
        continuation_anchor=build_anchor(),
    )["format_adaptation_plan"]

    assert plan.target_format == "screenplay"
    assert plan.structure_rules["requires_scene_heading"] is True
    assert plan.prose_rules["internality"] == "none"
    assert "internal monologue" in plan.forbidden_patterns


def test_format_adapter_builds_game_scene_plan():
    engine = FormatAdapterEngine()

    plan = engine.build_format_adaptation_plan(
        target_format=StoryFormat.game_scene,
        source_id="chapter_format",
        generation_contract=build_contract(StoryFormat.game_scene),
        chapter=build_chapter(),
        continuation_anchor=build_anchor(),
    )["format_adaptation_plan"]

    assert plan.target_format == "game_scene"
    assert plan.structure_rules["requires_player_choice"] is True
    assert plan.continuity_rules["must_emit_state_delta"] is True
    assert "choice options" in plan.required_sections


def test_format_adapter_builds_skeletons():
    engine = FormatAdapterEngine()

    screenplay = engine.build_format_adaptation_plan(
        target_format=StoryFormat.screenplay,
        source_id="chapter_format",
        generation_contract=build_contract(StoryFormat.screenplay),
        chapter=build_chapter(),
        continuation_anchor=build_anchor(),
    )["format_adaptation_plan"]

    game = engine.build_format_adaptation_plan(
        target_format=StoryFormat.game_scene,
        source_id="chapter_format",
        generation_contract=build_contract(StoryFormat.game_scene),
        chapter=build_chapter(),
        continuation_anchor=build_anchor(),
    )["format_adaptation_plan"]

    screenplay_skeleton = engine.adapt_text_skeleton(plan=screenplay, source_text="source")["adapted_text_skeleton"]
    game_skeleton = engine.adapt_text_skeleton(plan=game, source_text="source")["adapted_text_skeleton"]

    assert "INT./EXT." in screenplay_skeleton
    assert "PLAYER CHOICES" in game_skeleton


def test_format_adapter_validates_plan():
    engine = FormatAdapterEngine()

    plan = engine.build_format_adaptation_plan(
        target_format=StoryFormat.novel,
        source_id="chapter_format",
        generation_contract=build_contract(StoryFormat.novel),
        chapter=build_chapter(),
        continuation_anchor=build_anchor(),
    )["format_adaptation_plan"]

    validation = engine.validate_format_plan(plan=plan)

    assert validation["success"] is True
    assert validation["valid"] is True
    assert "adaptation_plan_id_present" in validation["passed_checks"]
    assert "structure_rules_present" in validation["passed_checks"]
    assert "continuity_rules_present" in validation["passed_checks"]


def test_format_adapter_summarizes_plan():
    engine = FormatAdapterEngine()

    plan = engine.build_format_adaptation_plan(
        target_format=StoryFormat.chapter,
        source_id="chapter_format",
        generation_contract=build_contract(StoryFormat.chapter),
        chapter=build_chapter(),
        continuation_anchor=build_anchor(),
    )["format_adaptation_plan"]

    summary = engine.summarize_format_plan(plan=plan)

    assert summary["success"] is True
    assert summary["summary"]["target_format"] == "chapter"
    assert summary["summary"]["unit_type"] == "chapter"
    assert summary["summary"]["required_section_count"] >= 1


def test_format_adapter_warns_when_target_not_allowed():
    engine = FormatAdapterEngine()

    plan = engine.build_format_adaptation_plan(
        target_format=StoryFormat.multi_book_arc,
        source_id="chapter_format",
        generation_contract=build_contract(StoryFormat.novel),
        chapter=build_chapter(),
        continuation_anchor=build_anchor(),
    )["format_adaptation_plan"]

    assert any("not in generation contract allowed formats" in warning for warning in plan.warnings)

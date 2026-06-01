from backend.app.engines.story_generation.chapter_expansion_engine import ChapterExpansionEngine
from backend.app.schemas.story_generation import (
    FormatAdaptationPlan,
    GeneratedChapter,
    LongFormContinuationAnchor,
    SeriesEpisodeStructure,
)


def build_chapter():
    return GeneratedChapter(
        chapter_id="chapter_expand",
        chapter_number=1,
        title="The Badge",
        chapter_text="Kael exposes the badge. Seren refuses to answer. The court waits.",
        scene_ids=["scene_001", "scene_002"],
        assembled_scene_ids=["assembled_scene_001", "assembled_scene_002"],
        used_character_ids=["char_kael", "char_seren"],
        used_relationship_ids=["rel_kael_seren"],
        used_secret_ids=["secret_seren_source"],
        used_causal_ids=["cause_trial_reveal", "cons_reputation_shift"],
        used_world_details=["Oath Court", "cracked badge"],
        open_loops=[{"loop_id": "open_loop_secret", "description": "Secret remains hidden."}],
        next_chapter_hooks=["Seren refuses to deny the badge."],
        quality_summary={"failed_scene_count": 0},
    )


def build_format_plan():
    return FormatAdaptationPlan(
        adaptation_plan_id="format_plan_expand",
        source_id="chapter_expand",
        target_format="novel",
        structure_rules={"unit_type": "novel_prose"},
        prose_rules={"internality": "high", "sensory_detail": "high"},
        dialogue_rules={"dialogue_density": "moderate", "subtext_required": True},
        pacing_rules={"shape": "emotional-escalation-with-reflection"},
        continuity_rules={"must_preserve_secret_ids": ["secret_seren_source"]},
        required_sections=["chapter opening", "interior conflict", "chapter turn"],
        forbidden_patterns=["screenplay camera directions"],
    )


def build_anchor():
    return LongFormContinuationAnchor(
        anchor_id="continuation_anchor_expand",
        chapter_id="chapter_expand",
        chapter_number=1,
        active_character_ids=["char_kael", "char_seren"],
        active_relationship_ids=["rel_kael_seren"],
        active_secret_ids=["secret_seren_source"],
        active_causal_ids=["cause_trial_reveal", "cons_reputation_shift"],
        active_world_details=["Oath Court", "cracked badge"],
        open_loops=[{"loop_id": "open_loop_secret", "description": "Secret remains hidden."}],
        next_chapter_hooks=["Seren refuses to deny the badge."],
    )


def build_episode_structure():
    return SeriesEpisodeStructure(
        episode_structure_id="episode_structure_expand",
        source_id="chapter_expand",
        episode_number=1,
        season_number=1,
        episode_title="The Badge",
        cold_open={"description": "Open on the cracked badge."},
        act_structure=[
            {"act_number": 1, "description": "Setup"},
            {"act_number": 2, "description": "Complication"},
            {"act_number": 3, "description": "Choice"},
            {"act_number": 4, "description": "Cliffhanger"},
        ],
        plot_lanes={"A_plot": [], "B_plot": [], "C_plot": []},
        episode_cliffhanger="Seren refuses to deny the badge.",
    )


def test_chapter_expansion_engine_builds_plan():
    engine = ChapterExpansionEngine()

    result = engine.build_expansion_plan(
        chapter=build_chapter(),
        target_word_count=1500,
        format_plan=build_format_plan(),
        continuation_anchor=build_anchor(),
        episode_structure=build_episode_structure(),
    )

    plan = result["chapter_expansion_plan"]

    assert result["success"] is True
    assert plan.expansion_plan_id == "chapter_expansion_chapter_expand"
    assert plan.chapter_id == "chapter_expand"
    assert plan.target_word_count == 1500
    assert plan.expansion_ratio > 1.0
    assert plan.expansion_targets


def test_chapter_expansion_engine_creates_all_target_types():
    engine = ChapterExpansionEngine()

    plan = engine.build_expansion_plan(
        chapter=build_chapter(),
        target_word_count=1500,
        format_plan=build_format_plan(),
        continuation_anchor=build_anchor(),
        episode_structure=build_episode_structure(),
    )["chapter_expansion_plan"]

    target_types = {target["target_type"] for target in plan.expansion_targets}

    assert "scene_expansion" in target_types
    assert "emotional_expansion" in target_types
    assert "world_expansion" in target_types
    assert "dialogue_expansion" in target_types
    assert "relationship_expansion" in target_types
    assert "secret_expansion" in target_types
    assert "causal_expansion" in target_types


def test_chapter_expansion_engine_preserves_format_and_episode_rules():
    engine = ChapterExpansionEngine()

    plan = engine.build_expansion_plan(
        chapter=build_chapter(),
        target_word_count=1500,
        format_plan=build_format_plan(),
        continuation_anchor=build_anchor(),
        episode_structure=build_episode_structure(),
    )["chapter_expansion_plan"]

    assert plan.format_specific_rules["target_format"] == "novel"
    assert plan.format_specific_rules["episode_structure_id"] == "episode_structure_expand"
    assert plan.format_specific_rules["act_count"] == 4


def test_chapter_expansion_engine_builds_revision_payload():
    engine = ChapterExpansionEngine()

    plan = engine.build_expansion_plan(
        chapter=build_chapter(),
        target_word_count=1500,
        format_plan=build_format_plan(),
        continuation_anchor=build_anchor(),
        episode_structure=build_episode_structure(),
    )["chapter_expansion_plan"]

    payload = plan.revision_prompt_payload

    assert payload["chapter_id"] == "chapter_expand"
    assert payload["target_word_count"] == 1500
    assert "secret_seren_source" in payload["continuity_requirements"]["secrets"]
    assert payload["episode_requirements"]["episode_structure_id"] == "episode_structure_expand"


def test_chapter_expansion_engine_builds_expanded_skeleton():
    engine = ChapterExpansionEngine()

    chapter = build_chapter()
    plan = engine.build_expansion_plan(
        chapter=chapter,
        target_word_count=1500,
        format_plan=build_format_plan(),
        continuation_anchor=build_anchor(),
    )["chapter_expansion_plan"]

    result = engine.build_expanded_chapter_skeleton(chapter=chapter, plan=plan)

    assert result["success"] is True
    assert "Expansion Targets" in result["expanded_chapter_skeleton"]
    assert "Chapter Text To Expand" in result["expanded_chapter_skeleton"]


def test_chapter_expansion_engine_validates_plan():
    engine = ChapterExpansionEngine()

    plan = engine.build_expansion_plan(
        chapter=build_chapter(),
        target_word_count=1500,
        format_plan=build_format_plan(),
        continuation_anchor=build_anchor(),
    )["chapter_expansion_plan"]

    validation = engine.validate_expansion_plan(plan=plan)

    assert validation["success"] is True
    assert validation["valid"] is True
    assert "expansion_plan_id_present" in validation["passed_checks"]
    assert "target_expands_source" in validation["passed_checks"]
    assert "expansion_targets_present" in validation["passed_checks"]


def test_chapter_expansion_engine_summarizes_plan():
    engine = ChapterExpansionEngine()

    plan = engine.build_expansion_plan(
        chapter=build_chapter(),
        target_word_count=1500,
        format_plan=build_format_plan(),
        continuation_anchor=build_anchor(),
    )["chapter_expansion_plan"]

    summary = engine.summarize_expansion_plan(plan=plan)

    assert summary["success"] is True
    assert summary["summary"]["chapter_id"] == "chapter_expand"
    assert summary["summary"]["scene_target_count"] == 2
    assert summary["summary"]["secret_target_count"] == 1
    assert summary["summary"]["causal_target_count"] == 2


def test_chapter_expansion_engine_warns_on_non_expansion_target():
    engine = ChapterExpansionEngine()

    chapter = build_chapter()
    source_count = len(chapter.chapter_text.split())

    plan = engine.build_expansion_plan(
        chapter=chapter,
        target_word_count=source_count,
        format_plan=build_format_plan(),
    )["chapter_expansion_plan"]

    assert any("Target word count is not larger" in warning for warning in plan.warnings)

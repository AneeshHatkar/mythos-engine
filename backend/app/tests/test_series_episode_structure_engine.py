from backend.app.engines.story_generation.series_episode_structure_engine import SeriesEpisodeStructureEngine
from backend.app.schemas.story_generation import (
    FormatAdaptationPlan,
    GeneratedChapter,
    LongFormContinuationAnchor,
)


def build_format_plan():
    return FormatAdaptationPlan(
        adaptation_plan_id="format_plan_episode",
        source_id="chapter_episode",
        target_format="chapter",
        structure_rules={"unit_type": "chapter"},
        prose_rules={"internality": "medium_high"},
        dialogue_rules={"dialogue_density": "balanced"},
        pacing_rules={"shape": "multi-scene escalation", "act_breaks": 4},
        continuity_rules={
            "must_preserve_character_ids": ["char_kael", "char_seren"],
            "must_preserve_secret_ids": ["secret_seren_source"],
            "must_preserve_causal_ids": ["cause_trial_reveal"],
        },
        required_sections=["chapter title", "scene sequence", "chapter consequence", "next hook"],
        forbidden_patterns=[],
    )


def build_chapter():
    return GeneratedChapter(
        chapter_id="chapter_episode",
        chapter_number=1,
        title="The Badge in the Court",
        chapter_text="Kael and Seren face the court.",
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
        anchor_id="continuation_anchor_episode",
        chapter_id="chapter_episode",
        chapter_number=1,
        active_character_ids=["char_kael", "char_seren"],
        active_relationship_ids=["rel_kael_seren"],
        active_secret_ids=["secret_seren_source"],
        active_causal_ids=["cause_trial_reveal", "cons_reputation_shift"],
        active_world_details=["Oath Court"],
        open_loops=[
            {"loop_id": "open_loop_secret", "description": "Secret remains hidden.", "status": "open"}
        ],
        next_chapter_hooks=["Seren refuses to deny the badge."],
        continuity_reminders=["Do not reveal secret_seren_source too early."],
    )


def test_series_episode_structure_engine_builds_structure():
    engine = SeriesEpisodeStructureEngine()

    result = engine.build_episode_structure(
        source_id="chapter_episode",
        format_plan=build_format_plan(),
        chapter=build_chapter(),
        continuation_anchor=build_anchor(),
        episode_number=2,
        season_number=1,
        story_context={"story_context_id": "storyctx_episode"},
    )

    structure = result["series_episode_structure"]

    assert result["success"] is True
    assert structure.episode_number == 2
    assert structure.season_number == 1
    assert structure.cold_open
    assert len(structure.act_structure) == 4
    assert structure.plot_lanes


def test_series_episode_structure_tracks_plot_lanes():
    engine = SeriesEpisodeStructureEngine()

    structure = engine.build_episode_structure(
        source_id="chapter_episode",
        format_plan=build_format_plan(),
        chapter=build_chapter(),
        continuation_anchor=build_anchor(),
    )["series_episode_structure"]

    assert structure.plot_lanes["A_plot"]
    assert structure.plot_lanes["B_plot"]
    assert structure.plot_lanes["C_plot"]
    assert any("cause_trial_reveal" in beat["source_id"] for beat in structure.plot_lanes["A_plot"])
    assert any("rel_kael_seren" in beat["source_id"] for beat in structure.plot_lanes["B_plot"])
    assert any("secret_seren_source" in beat["source_id"] for beat in structure.plot_lanes["C_plot"])


def test_series_episode_structure_tracks_continuity():
    engine = SeriesEpisodeStructureEngine()

    structure = engine.build_episode_structure(
        source_id="chapter_episode",
        format_plan=build_format_plan(),
        chapter=build_chapter(),
        continuation_anchor=build_anchor(),
    )["series_episode_structure"]

    assert any(item["character_id"] == "char_kael" for item in structure.character_continuity)
    assert any(item["relationship_id"] == "rel_kael_seren" for item in structure.relationship_continuity)
    assert structure.open_loop_carryover
    assert structure.episode_cliffhanger == "Seren refuses to deny the badge."


def test_series_episode_structure_builds_outline_text():
    engine = SeriesEpisodeStructureEngine()

    structure = engine.build_episode_structure(
        source_id="chapter_episode",
        format_plan=build_format_plan(),
        chapter=build_chapter(),
        continuation_anchor=build_anchor(),
    )["series_episode_structure"]

    outline = engine.build_episode_outline_text(structure=structure)["episode_outline_text"]

    assert "Cold Open" in outline
    assert "Acts" in outline
    assert "Plot Lanes" in outline
    assert "Cliffhanger" in outline


def test_series_episode_structure_validates_structure():
    engine = SeriesEpisodeStructureEngine()

    structure = engine.build_episode_structure(
        source_id="chapter_episode",
        format_plan=build_format_plan(),
        chapter=build_chapter(),
        continuation_anchor=build_anchor(),
    )["series_episode_structure"]

    validation = engine.validate_episode_structure(structure=structure)

    assert validation["success"] is True
    assert validation["valid"] is True
    assert "episode_structure_id_present" in validation["passed_checks"]
    assert "cold_open_present" in validation["passed_checks"]
    assert "act_structure_present" in validation["passed_checks"]


def test_series_episode_structure_summarizes_structure():
    engine = SeriesEpisodeStructureEngine()

    structure = engine.build_episode_structure(
        source_id="chapter_episode",
        format_plan=build_format_plan(),
        chapter=build_chapter(),
        continuation_anchor=build_anchor(),
    )["series_episode_structure"]

    summary = engine.summarize_episode_structure(structure=structure)

    assert summary["success"] is True
    assert summary["summary"]["act_count"] == 4
    assert summary["summary"]["plot_lane_count"] == 3
    assert summary["summary"]["has_cliffhanger"] is True


def test_series_episode_structure_uses_story_context_season_arcs():
    engine = SeriesEpisodeStructureEngine()

    structure = engine.build_episode_structure(
        source_id="chapter_episode",
        format_plan=build_format_plan(),
        chapter=build_chapter(),
        continuation_anchor=build_anchor(),
        story_context={
            "season_arc_links": [
                {
                    "season_arc_link_id": "season_arc_custom",
                    "source_id": "season_mystery",
                    "arc_type": "mystery",
                    "description": "The season mystery deepens.",
                }
            ]
        },
    )["series_episode_structure"]

    assert any(link["season_arc_link_id"] == "season_arc_custom" for link in structure.season_arc_links)

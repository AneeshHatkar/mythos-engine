from backend.app.engines.story_generation.series_season_formatter import SeriesSeasonFormatter
from backend.app.schemas.story_generation import (
    FormatAdaptationPlan,
    GeneratedChapter,
    LongFormContinuationAnchor,
    PlotOutline,
    SeriesEpisodeStructure,
)


def build_format_plan():
    return FormatAdaptationPlan(
        adaptation_plan_id="format_plan_series",
        source_id="series_source",
        target_format="chapter",
        structure_rules={"unit_type": "chapter"},
        prose_rules={"internality": "medium_high"},
        dialogue_rules={"dialogue_density": "balanced"},
        pacing_rules={"shape": "multi-scene escalation"},
        continuity_rules={
            "must_preserve_character_ids": ["char_kael", "char_seren"],
            "must_preserve_secret_ids": ["secret_seren_source"],
            "must_preserve_causal_ids": ["cause_trial_reveal"],
        },
        required_sections=["episode cards", "plot lanes", "cliffhanger"],
        forbidden_patterns=[],
    )


def build_plot_outline():
    return PlotOutline(
        outline_id="plot_outline_series",
        source_id="series_source",
        title="Court Secrets",
        premise="A public proof system threatens private loyalties.",
        scene_sequence=[
            {"scene_id": "scene_001", "purpose": "Expose the badge."}
        ],
        act_structure=[{"act_number": 1, "act_purpose": "Setup", "scene_ids": ["scene_001"]}],
        character_arc_threads=[
            {"thread_id": "character_arc_char_kael", "character_id": "char_kael", "description": "Kael changes under pressure."},
            {"thread_id": "character_arc_char_seren", "character_id": "char_seren", "description": "Seren hides the truth."},
        ],
        relationship_arc_threads=[
            {"thread_id": "relationship_arc_rel_kael_seren", "relationship_id": "rel_kael_seren", "description": "Trust and betrayal pressure rise."}
        ],
        secret_threads=[
            {"thread_id": "secret_thread_secret_seren_source", "secret_id": "secret_seren_source", "description": "Control reveal timing."}
        ],
        causal_threads=[
            {"thread_id": "causal_thread_cause_trial_reveal", "causal_id": "cause_trial_reveal", "description": "The badge reveal causes public consequence."}
        ],
        open_loops=[
            {"loop_id": "open_loop_secret", "loop_type": "secret_pressure", "description": "Secret remains hidden."}
        ],
        payoff_setups=[
            {"payoff_id": "payoff_secret_secret_seren_source", "payoff_type": "secret_reveal", "description": "Pay off the secret reveal carefully."}
        ],
        next_outline_hooks=["Seren refuses to deny the badge."],
        continuity_requirements={
            "required_character_ids": ["char_kael", "char_seren"],
            "required_secret_ids": ["secret_seren_source"],
            "required_causal_ids": ["cause_trial_reveal"],
            "required_world_details": ["Oath Court"],
        },
    )


def build_chapter():
    return GeneratedChapter(
        chapter_id="chapter_series",
        chapter_number=1,
        title="The Badge",
        chapter_text="Kael exposes the badge. Seren refuses to deny it.",
        scene_ids=["scene_001"],
        assembled_scene_ids=["assembled_scene_001"],
        used_character_ids=["char_kael", "char_seren"],
        used_relationship_ids=["rel_kael_seren"],
        used_secret_ids=["secret_seren_source"],
        used_causal_ids=["cause_trial_reveal"],
        used_world_details=["Oath Court"],
        open_loops=[
            {"loop_id": "open_loop_secret", "loop_type": "secret_pressure", "description": "Secret remains hidden."}
        ],
        next_chapter_hooks=["Seren refuses to deny the badge."],
        quality_summary={"failed_scene_count": 0},
    )


def build_anchor():
    return LongFormContinuationAnchor(
        anchor_id="continuation_anchor_series",
        chapter_id="chapter_series",
        chapter_number=1,
        active_character_ids=["char_kael", "char_seren"],
        active_relationship_ids=["rel_kael_seren"],
        active_secret_ids=["secret_seren_source"],
        active_causal_ids=["cause_trial_reveal"],
        active_world_details=["Oath Court"],
        open_loops=[
            {"loop_id": "open_loop_secret", "loop_type": "secret_pressure", "description": "Secret remains hidden."}
        ],
        next_chapter_hooks=["Seren refuses to deny the badge."],
        continuity_reminders=["Do not reveal secret_seren_source too early."],
    )


def build_episode_structure():
    return SeriesEpisodeStructure(
        episode_structure_id="episode_structure_series",
        source_id="series_source",
        episode_number=1,
        season_number=1,
        episode_title="The Badge",
        cold_open={"description": "Open on the cracked badge."},
        act_structure=[
            {"act_number": 1, "description": "Setup", "act_break_hook": "Secret remains hidden."},
            {"act_number": 2, "description": "Complication", "act_break_hook": "Trust becomes harder."},
            {"act_number": 3, "description": "Choice", "act_break_hook": "Court pressure rises."},
            {"act_number": 4, "description": "Cliffhanger", "act_break_hook": "Seren refuses to deny the badge."},
        ],
        plot_lanes={
            "A_plot": [{"plot_beat_id": "a_plot_cause_trial_reveal", "description": "Causal pressure rises.", "source_id": "cause_trial_reveal"}],
            "B_plot": [{"plot_beat_id": "b_plot_rel_kael_seren", "description": "Relationship pressure rises.", "source_id": "rel_kael_seren"}],
            "C_plot": [{"plot_beat_id": "c_plot_secret_seren_source", "description": "Secret remains hidden.", "source_id": "secret_seren_source"}],
        },
        season_arc_links=[
            {"season_arc_link_id": "season_arc_secret", "description": "Secret arc continues.", "source_id": "secret_seren_source"}
        ],
        character_continuity=[
            {"character_id": "char_kael", "continuity_rule": "Carry Kael forward."}
        ],
        relationship_continuity=[
            {"relationship_id": "rel_kael_seren", "continuity_rule": "Carry relationship pressure forward."}
        ],
        open_loop_carryover=[
            {"loop_id": "open_loop_secret", "description": "Secret remains hidden."}
        ],
        episode_cliffhanger="Seren refuses to deny the badge.",
    )


def test_series_season_formatter_builds_package():
    formatter = SeriesSeasonFormatter()

    result = formatter.format_series_or_season(
        source_id="series_source",
        series_title="Court Secrets",
        season_number=1,
        episode_structures=[build_episode_structure()],
        format_plan=build_format_plan(),
        plot_outline=build_plot_outline(),
        chapters=[build_chapter()],
        continuation_anchor=build_anchor(),
    )

    package = result["series_season_format_package"]

    assert result["success"] is True
    assert package.series_title == "Court Secrets"
    assert package.season_number == 1
    assert package.episode_count == 1
    assert package.episode_cards
    assert package.formatted_text


def test_series_season_formatter_tracks_plot_lanes_and_carryover():
    formatter = SeriesSeasonFormatter()

    package = formatter.format_series_or_season(
        source_id="series_source",
        episode_structures=[build_episode_structure()],
        plot_outline=build_plot_outline(),
        continuation_anchor=build_anchor(),
    )["series_season_format_package"]

    assert package.plot_lanes["A_plot"]
    assert package.plot_lanes["B_plot"]
    assert package.plot_lanes["C_plot"]
    assert package.season_arc_carryover
    assert any("secret" in str(item).lower() for item in package.season_arc_carryover)


def test_series_season_formatter_tracks_recurring_dynamics_and_cliffhangers():
    formatter = SeriesSeasonFormatter()

    package = formatter.format_series_or_season(
        source_id="series_source",
        episode_structures=[build_episode_structure()],
        plot_outline=build_plot_outline(),
        continuation_anchor=build_anchor(),
    )["series_season_format_package"]

    assert package.recurring_character_dynamics
    assert package.cliffhanger_registry
    assert any("Seren refuses" in item["description"] for item in package.cliffhanger_registry)


def test_series_season_formatter_builds_from_chapters_without_episode_structure():
    formatter = SeriesSeasonFormatter()

    package = formatter.format_series_or_season(
        source_id="chapter_only_series",
        chapters=[build_chapter()],
        plot_outline=build_plot_outline(),
        continuation_anchor=build_anchor(),
    )["series_season_format_package"]

    assert package.episode_count == 1
    assert package.episode_cards[0]["source"] == "generated_chapter"
    assert package.act_breaks


def test_series_season_formatter_validates_package():
    formatter = SeriesSeasonFormatter()

    package = formatter.format_series_or_season(
        source_id="series_source",
        series_title="Court Secrets",
        season_number=1,
        episode_structures=[build_episode_structure()],
        format_plan=build_format_plan(),
        plot_outline=build_plot_outline(),
        continuation_anchor=build_anchor(),
    )["series_season_format_package"]

    validation = formatter.validate_series_package(package=package)

    assert validation["success"] is True
    assert validation["valid"] is True
    assert "series_package_id_present" in validation["passed_checks"]
    assert "episode_cards_present" in validation["passed_checks"]
    assert "formatted_text_present" in validation["passed_checks"]


def test_series_season_formatter_summarizes_package():
    formatter = SeriesSeasonFormatter()

    package = formatter.format_series_or_season(
        source_id="series_source",
        series_title="Court Secrets",
        season_number=1,
        episode_structures=[build_episode_structure()],
        plot_outline=build_plot_outline(),
        continuation_anchor=build_anchor(),
    )["series_season_format_package"]

    summary = formatter.summarize_series_package(package=package)

    assert summary["success"] is True
    assert summary["summary"]["series_title"] == "Court Secrets"
    assert summary["summary"]["episode_count"] == 1
    assert summary["summary"]["cliffhanger_count"] >= 1


def test_series_season_formatter_builds_export_text():
    formatter = SeriesSeasonFormatter()

    package = formatter.format_series_or_season(
        source_id="series_source",
        series_title="Court Secrets",
        season_number=1,
        episode_structures=[build_episode_structure()],
        plot_outline=build_plot_outline(),
        continuation_anchor=build_anchor(),
    )["series_season_format_package"]

    result = formatter.build_export_text(package=package)

    assert result["success"] is True
    assert result["export_text"] == package.formatted_text
    assert result["export_metadata"]["target_format"] == "series_season"


def test_series_season_formatter_warns_without_sources():
    formatter = SeriesSeasonFormatter()

    package = formatter.format_series_or_season(
        source_id="empty_series",
        series_title="Empty Series",
        season_number=1,
    )["series_season_format_package"]

    assert any("No episode cards" in warning for warning in package.warnings)

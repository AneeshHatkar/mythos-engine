from backend.app.engines.story_generation.story_continuity_validator import StoryContinuityValidator
from backend.app.schemas.story_generation import (
    AdaptiveStoryPatternPlan,
    GameInteractiveScenePackage,
    GeneratedChapter,
    LongFormContinuationAnchor,
    PlotOutline,
    ScreenplayMovieFormatPackage,
    SeriesSeasonFormatPackage,
    StoryAntiGenericityReport,
    StoryQualityScoreReport,
)


def build_plot_outline():
    return PlotOutline(
        outline_id="plot_outline_continuity",
        source_id="continuity_source",
        title="Court Secrets",
        premise="A public proof system threatens private loyalties.",
        scene_sequence=[
            {"scene_id": "scene_001", "purpose": "Expose the badge."}
        ],
        act_structure=[{"act_number": 1, "act_purpose": "Setup", "scene_ids": ["scene_001"]}],
        character_arc_threads=[
            {"thread_id": "character_arc_char_kael", "character_id": "char_kael"},
            {"thread_id": "character_arc_char_seren", "character_id": "char_seren"},
        ],
        relationship_arc_threads=[
            {"thread_id": "relationship_arc_rel_kael_seren", "relationship_id": "rel_kael_seren"}
        ],
        secret_threads=[
            {"thread_id": "secret_thread_secret_seren_source", "secret_id": "secret_seren_source"}
        ],
        causal_threads=[
            {"thread_id": "causal_thread_cause_trial_reveal", "causal_id": "cause_trial_reveal"}
        ],
        world_state_threads=[
            {"thread_id": "world_thread_oath_court", "world_detail": "Oath Court"},
            {"thread_id": "world_thread_cracked_badge", "world_detail": "cracked badge"},
        ],
        open_loops=[
            {"loop_id": "open_loop_secret", "description": "Secret remains hidden."}
        ],
        payoff_setups=[
            {"payoff_id": "payoff_secret", "description": "Reveal carefully."}
        ],
        continuity_requirements={
            "required_character_ids": ["char_kael", "char_seren"],
            "required_relationship_ids": ["rel_kael_seren"],
            "required_secret_ids": ["secret_seren_source"],
            "required_causal_ids": ["cause_trial_reveal"],
            "required_world_details": ["Oath Court", "cracked badge"],
            "open_loop_ids": ["open_loop_secret"],
        },
    )


def build_chapter():
    return GeneratedChapter(
        chapter_id="chapter_continuity",
        chapter_number=1,
        title="The Badge",
        chapter_text="Kael exposes the cracked badge. Seren refuses to answer.",
        scene_ids=["scene_001"],
        assembled_scene_ids=["assembled_scene_001"],
        used_character_ids=["char_kael", "char_seren"],
        used_relationship_ids=["rel_kael_seren"],
        used_secret_ids=["secret_seren_source"],
        used_causal_ids=["cause_trial_reveal"],
        used_world_details=["Oath Court", "cracked badge"],
        open_loops=[
            {"loop_id": "open_loop_secret", "description": "Secret remains hidden."}
        ],
        next_chapter_hooks=["Seren refuses to deny the badge."],
    )


def build_anchor():
    return LongFormContinuationAnchor(
        anchor_id="anchor_continuity",
        chapter_id="chapter_continuity",
        chapter_number=1,
        active_character_ids=["char_kael", "char_seren"],
        active_relationship_ids=["rel_kael_seren"],
        active_secret_ids=["secret_seren_source"],
        active_causal_ids=["cause_trial_reveal"],
        active_world_details=["Oath Court", "cracked badge"],
        open_loops=[
            {"loop_id": "open_loop_secret", "description": "Secret remains hidden."}
        ],
        next_chapter_hooks=["Seren refuses to deny the badge."],
    )


def build_adaptive_plan():
    return AdaptiveStoryPatternPlan(
        pattern_plan_id="adaptive_continuity",
        source_id="continuity_source",
        selected_primary_pattern="mystery_pressure",
        selected_secondary_patterns=["causal_escalation"],
        character_pattern_assignments=[
            {"assignment_id": "character_pattern_char_kael", "character_id": "char_kael"},
            {"assignment_id": "character_pattern_char_seren", "character_id": "char_seren"},
        ],
        relationship_pattern_assignments=[
            {"assignment_id": "relationship_pattern_rel_kael_seren", "relationship_id": "rel_kael_seren"}
        ],
        secret_pattern_assignments=[
            {"assignment_id": "secret_pattern_secret_seren_source", "secret_id": "secret_seren_source"}
        ],
        causal_pattern_assignments=[
            {"assignment_id": "causal_pattern_cause_trial_reveal", "causal_id": "cause_trial_reveal"}
        ],
        world_pattern_assignments=[
            {"assignment_id": "world_pattern_oath_court", "world_detail": "Oath Court"},
            {"assignment_id": "world_pattern_cracked_badge", "world_detail": "cracked badge"},
        ],
        anti_template_rules=["Do not drop open loops silently."],
        downstream_generation_constraints={"must_preserve_open_loops": True},
    )


def build_screen_package():
    return ScreenplayMovieFormatPackage(
        format_package_id="screen_continuity",
        source_id="continuity_source",
        target_format="movie",
        title="Court Secrets",
        visual_motifs=[
            {"motif_id": "visual_motif_oath_court", "source_detail": "Oath Court"},
            {"motif_id": "visual_motif_cracked_badge", "source_detail": "cracked badge"},
        ],
        continuity_requirements={
            "used_secret_ids": ["secret_seren_source"],
            "used_causal_ids": ["cause_trial_reveal"],
        },
        formatted_text="Movie text.",
    )


def build_series_package():
    return SeriesSeasonFormatPackage(
        series_package_id="series_continuity",
        source_id="continuity_source",
        series_title="Court Secrets",
        episode_count=1,
        recurring_character_dynamics=[
            {"dynamic_id": "recurring_character_char_kael", "character_id": "char_kael"},
            {"dynamic_id": "recurring_character_char_seren", "character_id": "char_seren"},
            {"dynamic_id": "recurring_relationship_rel_kael_seren", "relationship_id": "rel_kael_seren"},
        ],
        season_arc_carryover=[
            {"carryover_id": "season_loop_open_loop_secret", "source_id": "open_loop_secret"}
        ],
        formatted_text="Series text.",
    )


def build_game_package(with_state=True):
    return GameInteractiveScenePackage(
        game_package_id="game_continuity",
        source_id="continuity_source",
        scene_title="Interactive Court",
        player_objective="Expose or hide the badge.",
        npc_dialogue_blocks=[
            {"dialogue_block_id": "npc_dialogue_char_kael", "npc_id": "char_kael"},
            {"dialogue_block_id": "npc_dialogue_char_seren", "npc_id": "char_seren"},
        ],
        choice_menu=[{"choice_id": "choice_1"}, {"choice_id": "choice_2"}],
        branching_outcomes=[{"outcome_id": "outcome_1"}],
        state_deltas=[{"state_delta_id": "delta_1"}] if with_state else [],
        relationship_state_hooks=[
            {"relationship_hook_id": "relationship_hook_rel_kael_seren", "relationship_id": "rel_kael_seren"}
        ],
        secret_state_hooks=[
            {"secret_hook_id": "secret_hook_secret_seren_source", "secret_id": "secret_seren_source"}
        ],
        causal_state_hooks=[
            {"causal_hook_id": "causal_hook_cause_trial_reveal", "causal_id": "cause_trial_reveal"}
        ],
        world_state_hooks=[
            {"world_hook_id": "world_hook_oath_court", "world_detail": "Oath Court"},
            {"world_hook_id": "world_hook_cracked_badge", "world_detail": "cracked badge"},
        ],
        quest_log_updates=[
            {"quest_update_id": "quest_open_loop_secret", "source_thread_id": "open_loop_secret"}
        ],
        formatted_text="Game text.",
    )


def build_quality_report():
    return StoryQualityScoreReport(
        quality_report_id="quality_continuity",
        source_id="continuity_source",
        overall_score=0.78,
        readiness_level="needs_light_revision",
        anti_generic_score=0.80,
        dimension_breakdown=[],
        quality_gates=[],
    )


def build_anti_genericity_report():
    return StoryAntiGenericityReport(
        report_id="anti_genericity_continuity",
        draft_id="continuity_source",
        anti_genericity_report_id="anti_genericity_continuity",
        source_id="continuity_source",
        overall_anti_genericity_score=0.76,
        genericity_risk_level="medium",
    )


def test_story_continuity_validator_builds_valid_report():
    validator = StoryContinuityValidator()

    result = validator.validate_story_continuity(
        source_id="continuity_source",
        plot_outline=build_plot_outline(),
        chapter=build_chapter(),
        continuation_anchor=build_anchor(),
        adaptive_pattern_plan=build_adaptive_plan(),
        quality_report=build_quality_report(),
        anti_genericity_report=build_anti_genericity_report(),
        screenplay_movie_package=build_screen_package(),
        series_package=build_series_package(),
        game_package=build_game_package(),
    )

    report = result["story_continuity_validation_report"]

    assert result["success"] is True
    assert report.continuity_report_id == "story_continuity_continuity_source"
    assert report.valid is True
    assert report.continuity_score >= 0.70
    assert report.preserved_threads
    assert report.downstream_constraints


def test_story_continuity_validator_detects_missing_secret_and_causal_thread():
    validator = StoryContinuityValidator()
    chapter = build_chapter()
    chapter.used_secret_ids = []
    chapter.used_causal_ids = []

    result = validator.validate_story_continuity(
        source_id="broken_continuity",
        plot_outline=build_plot_outline(),
        chapter=chapter,
        continuation_anchor=None,
        adaptive_pattern_plan=build_adaptive_plan(),
    )

    report = result["story_continuity_validation_report"]

    assert report.valid is False
    assert report.continuity_breaks
    assert any(item["break_type"] == "missing_secret_ids" for item in report.continuity_breaks)
    assert any(item["break_type"] == "missing_causal_ids" for item in report.continuity_breaks)
    assert report.repair_targets


def test_story_continuity_validator_warns_for_interactive_choices_without_state_delta():
    validator = StoryContinuityValidator()

    report = validator.validate_story_continuity(
        source_id="interactive_warning",
        plot_outline=build_plot_outline(),
        chapter=build_chapter(),
        continuation_anchor=build_anchor(),
        game_package=build_game_package(with_state=False),
    )["story_continuity_validation_report"]

    assert any(item["warning_id"] == "interactive_choices_without_state_deltas" for item in report.continuity_warnings)


def test_story_continuity_validator_validates_report():
    validator = StoryContinuityValidator()

    report = validator.validate_story_continuity(
        source_id="continuity_source",
        plot_outline=build_plot_outline(),
        chapter=build_chapter(),
        continuation_anchor=build_anchor(),
        adaptive_pattern_plan=build_adaptive_plan(),
        game_package=build_game_package(),
    )["story_continuity_validation_report"]

    validation = validator.validate_report(report=report)

    assert validation["success"] is True
    assert validation["valid"] is True
    assert "continuity_report_id_present" in validation["passed_checks"]
    assert "scores_bounded" in validation["passed_checks"]
    assert "readiness_level_valid" in validation["passed_checks"]


def test_story_continuity_validator_summarizes_report():
    validator = StoryContinuityValidator()

    report = validator.validate_story_continuity(
        source_id="continuity_source",
        plot_outline=build_plot_outline(),
        chapter=build_chapter(),
        continuation_anchor=build_anchor(),
        adaptive_pattern_plan=build_adaptive_plan(),
        game_package=build_game_package(),
    )["story_continuity_validation_report"]

    summary = validator.summarize_report(report=report)

    assert summary["success"] is True
    assert summary["summary"]["source_id"] == "continuity_source"
    assert "weakest_dimension" in summary["summary"]
    assert summary["summary"]["checked_character_count"] >= 2


def test_story_continuity_validator_builds_report_text():
    validator = StoryContinuityValidator()

    report = validator.validate_story_continuity(
        source_id="continuity_source",
        plot_outline=build_plot_outline(),
        chapter=build_chapter(),
        continuation_anchor=build_anchor(),
        adaptive_pattern_plan=build_adaptive_plan(),
        game_package=build_game_package(),
    )["story_continuity_validation_report"]

    text = validator.build_continuity_report_text(report=report)["continuity_report_text"]

    assert "Story Continuity Report" in text
    assert "Checked Threads" in text
    assert "Repair Targets" in text

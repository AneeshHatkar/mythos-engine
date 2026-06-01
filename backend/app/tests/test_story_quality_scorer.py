from backend.app.engines.story_generation.story_quality_scorer import StoryQualityScorer
from backend.app.schemas.story_generation import (
    AdaptiveStoryPatternPlan,
    FormatAdaptationPlan,
    GameInteractiveScenePackage,
    GeneratedChapter,
    MultiScenePacingReport,
    MultiWorldMultiCastScalingPlan,
    PlotOutline,
    ScreenplayMovieFormatPackage,
    SeriesSeasonFormatPackage,
)


def build_plot_outline():
    return PlotOutline(
        outline_id="plot_outline_quality",
        source_id="quality_source",
        title="Court Secrets",
        premise="A public proof system threatens private loyalties.",
        scene_sequence=[
            {"scene_id": "scene_001", "purpose": "Expose the badge."},
            {"scene_id": "scene_002", "purpose": "Force Seren's answer."},
        ],
        act_structure=[
            {"act_number": 1, "act_purpose": "Setup", "scene_ids": ["scene_001"]},
            {"act_number": 2, "act_purpose": "Pressure", "scene_ids": ["scene_002"]},
        ],
        major_turning_points=[
            {"turning_point_id": "turn_001", "description": "Seren refuses to deny the badge."}
        ],
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
            {"thread_id": "world_thread_oath_court", "world_detail": "Oath Court"}
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
            "required_world_details": ["Oath Court"],
        },
    )


def build_chapter():
    return GeneratedChapter(
        chapter_id="chapter_quality",
        chapter_number=1,
        title="The Badge",
        chapter_text="Kael exposes the badge. Seren refuses to answer.",
        scene_ids=["scene_001", "scene_002"],
        assembled_scene_ids=["assembled_scene_001", "assembled_scene_002"],
        used_character_ids=["char_kael", "char_seren"],
        used_relationship_ids=["rel_kael_seren"],
        used_secret_ids=["secret_seren_source"],
        used_causal_ids=["cause_trial_reveal"],
        used_world_details=["Oath Court"],
        open_loops=[{"loop_id": "open_loop_secret", "description": "Secret remains hidden."}],
        next_chapter_hooks=["Seren refuses to deny the badge."],
    )


def build_format_plan():
    return FormatAdaptationPlan(
        adaptation_plan_id="format_plan_quality",
        source_id="quality_source",
        target_format="game_scene",
        structure_rules={"unit_type": "interactive_scene"},
        prose_rules={"internality": "low"},
        dialogue_rules={"dialogue_density": "choice_aware"},
        pacing_rules={"shape": "setup-choice-consequence"},
        continuity_rules={"must_preserve_secret_ids": ["secret_seren_source"]},
        required_sections=["setup", "choice", "consequence"],
        forbidden_patterns=["generic template"],
    )


def build_adaptive_plan():
    return AdaptiveStoryPatternPlan(
        pattern_plan_id="adaptive_story_pattern_quality",
        source_id="quality_source",
        selected_primary_pattern="mystery_pressure",
        selected_secondary_patterns=["causal_escalation", "relationship_fracture", "interactive_branching"],
        pattern_blend_strategy={"blend_mode": "weighted_interlock"},
        character_pattern_assignments=[
            {"assignment_id": "character_pattern_char_kael", "character_id": "char_kael"}
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
            {"assignment_id": "world_pattern_oath_court", "world_detail": "Oath Court"}
        ],
        anti_template_rules=[
            "Do not use a single universal three-act formula.",
            "Do not resolve secrets immediately.",
            "Do not make choices cosmetic.",
        ],
        adaptation_reasons=["Mystery pressure selected because secrets are active."],
        downstream_generation_constraints={"must_preserve_open_loops": True},
    )


def build_pacing_report():
    return MultiScenePacingReport(
        pacing_report_id="pacing_quality",
        source_id="quality_source",
        scene_count=2,
        overall_pacing_score=0.74,
        tension_curve_score=0.74,
        emotional_variety_score=0.70,
        relationship_rhythm_score=0.72,
        secret_pressure_spacing_score=0.73,
        causal_spacing_score=0.75,
        world_detail_spacing_score=0.70,
        dialogue_action_balance_score=0.72,
    )


def build_screen_package():
    return ScreenplayMovieFormatPackage(
        format_package_id="screen_quality",
        source_id="quality_source",
        target_format="movie",
        title="Court Secrets",
        formatted_text="Movie format text.",
    )


def build_series_package():
    return SeriesSeasonFormatPackage(
        series_package_id="series_quality",
        source_id="quality_source",
        series_title="Court Secrets",
        episode_count=1,
        episode_cards=[{"episode_card_id": "episode_001"}],
        formatted_text="Series format text.",
    )


def build_game_package():
    return GameInteractiveScenePackage(
        game_package_id="game_quality",
        source_id="quality_source",
        scene_title="Interactive Court",
        player_objective="Expose or hide the badge.",
        choice_menu=[{"choice_id": "choice_1"}, {"choice_id": "choice_2"}],
        branching_outcomes=[{"outcome_id": "outcome_1"}],
        secret_state_hooks=[{"secret_id": "secret_seren_source"}],
        formatted_text="Game format text.",
    )


def build_scaling_plan():
    return MultiWorldMultiCastScalingPlan(
        scaling_plan_id="scaling_quality",
        source_id="quality_source",
        world_count=1,
        cast_count=1,
        total_character_count=2,
        world_registry=[{"world_id": "world_oath_court"}],
        cast_registry=[{"cast_id": "cast_primary", "character_ids": ["char_kael", "char_seren"]}],
        continuity_partition_rules=[{"rule_id": "world_rule_1"}],
        scaling_pressure_report={"pressure_level": "low"},
    )


def test_story_quality_scorer_builds_report():
    scorer = StoryQualityScorer()

    result = scorer.score_story_quality(
        source_id="quality_source",
        plot_outline=build_plot_outline(),
        chapter=build_chapter(),
        format_plan=build_format_plan(),
        adaptive_pattern_plan=build_adaptive_plan(),
        pacing_report=build_pacing_report(),
        screenplay_movie_package=build_screen_package(),
        series_package=build_series_package(),
        game_package=build_game_package(),
        scaling_plan=build_scaling_plan(),
        story_context={"genres": ["mystery"], "target_audience": "YA fantasy readers"},
    )

    report = result["story_quality_score_report"]

    assert result["success"] is True
    assert report.quality_report_id == "story_quality_score_quality_source"
    assert report.overall_score > 0.0
    assert report.dimension_breakdown
    assert report.quality_gates
    assert report.readiness_level in {"ready", "needs_light_revision", "needs_revision", "blocked"}


def test_story_quality_scorer_scores_dimensions():
    scorer = StoryQualityScorer()

    report = scorer.score_story_quality(
        source_id="quality_source",
        plot_outline=build_plot_outline(),
        chapter=build_chapter(),
        format_plan=build_format_plan(),
        adaptive_pattern_plan=build_adaptive_plan(),
        pacing_report=build_pacing_report(),
        game_package=build_game_package(),
        scaling_plan=build_scaling_plan(),
    )["story_quality_score_report"]

    assert report.structure_score >= 0.5
    assert report.character_score >= 0.5
    assert report.relationship_score >= 0.5
    assert report.secret_mystery_score >= 0.5
    assert report.causal_score >= 0.5
    assert report.world_score >= 0.5
    assert report.pacing_score == 0.74
    assert report.anti_generic_score >= 0.5


def test_story_quality_scorer_builds_revision_priorities_for_weak_context():
    scorer = StoryQualityScorer()

    report = scorer.score_story_quality(
        source_id="weak_quality",
        plot_outline=None,
        chapter=None,
        format_plan=None,
        adaptive_pattern_plan=None,
        pacing_report=None,
    )["story_quality_score_report"]

    assert report.revision_priorities
    assert report.readiness_level in {"needs_revision", "blocked"}
    assert report.warnings


def test_story_quality_scorer_validates_report():
    scorer = StoryQualityScorer()

    report = scorer.score_story_quality(
        source_id="quality_source",
        plot_outline=build_plot_outline(),
        chapter=build_chapter(),
        format_plan=build_format_plan(),
        adaptive_pattern_plan=build_adaptive_plan(),
        pacing_report=build_pacing_report(),
    )["story_quality_score_report"]

    validation = scorer.validate_quality_report(report=report)

    assert validation["success"] is True
    assert validation["valid"] is True
    assert "quality_report_id_present" in validation["passed_checks"]
    assert "scores_bounded" in validation["passed_checks"]
    assert "dimension_breakdown_present" in validation["passed_checks"]


def test_story_quality_scorer_summarizes_report():
    scorer = StoryQualityScorer()

    report = scorer.score_story_quality(
        source_id="quality_source",
        plot_outline=build_plot_outline(),
        chapter=build_chapter(),
        format_plan=build_format_plan(),
        adaptive_pattern_plan=build_adaptive_plan(),
        pacing_report=build_pacing_report(),
    )["story_quality_score_report"]

    summary = scorer.summarize_quality_report(report=report)

    assert summary["success"] is True
    assert summary["summary"]["source_id"] == "quality_source"
    assert "weakest_dimension" in summary["summary"]
    assert summary["summary"]["quality_gate_count"] >= 1


def test_story_quality_scorer_builds_report_text():
    scorer = StoryQualityScorer()

    report = scorer.score_story_quality(
        source_id="quality_source",
        plot_outline=build_plot_outline(),
        chapter=build_chapter(),
        format_plan=build_format_plan(),
        adaptive_pattern_plan=build_adaptive_plan(),
        pacing_report=build_pacing_report(),
    )["story_quality_score_report"]

    text = scorer.build_quality_report_text(report=report)["quality_report_text"]

    assert "Story Quality Report" in text
    assert "Dimension Breakdown" in text
    assert "Revision Priorities" in text

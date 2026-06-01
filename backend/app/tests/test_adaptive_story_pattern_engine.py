from backend.app.engines.story_generation.adaptive_story_pattern_engine import AdaptiveStoryPatternEngine
from backend.app.schemas.story_generation import (
    FormatAdaptationPlan,
    GameInteractiveScenePackage,
    MultiWorldMultiCastScalingPlan,
    PlotOutline,
    ScreenplayMovieFormatPackage,
    SeriesSeasonFormatPackage,
)


def build_plot_outline():
    return PlotOutline(
        outline_id="plot_outline_patterns",
        source_id="pattern_source",
        title="Court Secrets",
        premise="A public proof system threatens private loyalties.",
        scene_sequence=[{"scene_id": "scene_001", "purpose": "Expose the badge."}],
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
            {"thread_id": "world_thread_oath_court", "world_detail": "Oath Court"}
        ],
        open_loops=[{"loop_id": "open_loop_secret", "description": "Secret remains hidden."}],
        payoff_setups=[{"payoff_id": "payoff_secret", "description": "Reveal carefully."}],
        continuity_requirements={
            "required_character_ids": ["char_kael", "char_seren"],
            "required_relationship_ids": ["rel_kael_seren"],
            "required_secret_ids": ["secret_seren_source"],
            "required_causal_ids": ["cause_trial_reveal"],
            "required_world_details": ["Oath Court"],
        },
    )


def build_format_plan(target_format="game_scene"):
    return FormatAdaptationPlan(
        adaptation_plan_id="format_plan_patterns",
        source_id="pattern_source",
        target_format=target_format,
        structure_rules={"unit_type": target_format},
        prose_rules={"internality": "low"},
        dialogue_rules={"dialogue_density": "choice_aware"},
        pacing_rules={"shape": "setup-choice-consequence"},
        continuity_rules={"must_preserve_secret_ids": ["secret_seren_source"]},
        required_sections=["setup", "choice", "consequence"],
        forbidden_patterns=["generic template"],
    )


def build_game_package():
    return GameInteractiveScenePackage(
        game_package_id="game_package_patterns",
        source_id="pattern_source",
        scene_title="Interactive Court",
        player_objective="Expose or hide the badge.",
        choice_menu=[
            {"choice_id": "choice_push_truth"},
            {"choice_id": "choice_protect_secret"},
            {"choice_id": "choice_gather_evidence"},
        ],
        branching_outcomes=[
            {"outcome_id": "outcome_push_truth"},
            {"outcome_id": "outcome_protect_secret"},
        ],
        relationship_state_hooks=[
            {"relationship_hook_id": "rel_hook", "relationship_id": "rel_kael_seren"}
        ],
        secret_state_hooks=[
            {"secret_hook_id": "secret_hook", "secret_id": "secret_seren_source"}
        ],
        causal_state_hooks=[
            {"causal_hook_id": "causal_hook", "causal_id": "cause_trial_reveal"}
        ],
        world_state_hooks=[
            {"world_hook_id": "world_hook", "world_detail": "Oath Court"}
        ],
        formatted_text="Game text.",
    )


def build_series_package():
    return SeriesSeasonFormatPackage(
        series_package_id="series_package_patterns",
        source_id="pattern_source",
        series_title="Court Secrets",
        episode_count=3,
        plot_lanes={
            "A_plot": [{"plot_beat_id": "a_plot"}],
            "B_plot": [{"plot_beat_id": "b_plot"}],
        },
        formatted_text="Series text.",
    )


def build_screen_package():
    return ScreenplayMovieFormatPackage(
        format_package_id="screen_package_patterns",
        source_id="pattern_source",
        target_format="movie",
        title="Court Secrets",
        formatted_text="Movie text.",
    )


def build_scaling_plan(high=False):
    return MultiWorldMultiCastScalingPlan(
        scaling_plan_id="scaling_plan_patterns",
        source_id="pattern_source",
        world_count=3 if high else 1,
        cast_count=2 if high else 1,
        total_character_count=18 if high else 2,
        world_registry=[
            {"world_id": "world_oath_court", "world_name": "Oath Court"},
            {"world_id": "world_badge_law", "world_name": "badge law"},
        ] if high else [{"world_id": "world_oath_court", "world_name": "Oath Court"}],
        cast_registry=[
            {"cast_id": "cast_primary", "character_ids": [f"char_{i}" for i in range(18 if high else 2)]}
        ],
        storyline_lanes=[
            {"lane_id": "lane_secret", "lane_type": "secret"},
            {"lane_id": "lane_causal", "lane_type": "causal"},
        ],
        continuity_partition_rules=[
            {"rule_id": "world_rule_1"},
            {"rule_id": "cast_rule_1"},
        ],
        generation_batch_plan=[
            {"batch_id": "batch_1"},
            {"batch_id": "batch_2"},
        ],
        scaling_pressure_report={"pressure_level": "high" if high else "low"},
    )


def test_adaptive_story_pattern_engine_builds_plan():
    engine = AdaptiveStoryPatternEngine()

    result = engine.build_adaptive_pattern_plan(
        source_id="pattern_source",
        plot_outline=build_plot_outline(),
        format_plan=build_format_plan(),
        game_package=build_game_package(),
        scaling_plan=build_scaling_plan(),
        story_context={"genres": ["mystery", "drama"], "target_format": "game_scene"},
    )

    plan = result["adaptive_story_pattern_plan"]

    assert result["success"] is True
    assert plan.pattern_plan_id == "adaptive_story_pattern_pattern_source"
    assert plan.selected_primary_pattern
    assert plan.pattern_blend_strategy
    assert plan.anti_template_rules
    assert plan.downstream_generation_constraints


def test_adaptive_story_pattern_engine_selects_game_pattern_when_interactive():
    engine = AdaptiveStoryPatternEngine()

    result = engine.build_adaptive_pattern_plan(
        source_id="pattern_source",
        plot_outline=build_plot_outline(),
        format_plan=build_format_plan("game_scene"),
        game_package=build_game_package(),
        story_context={"genres": ["mystery"], "target_format": "game_scene"},
    )

    scored = result["scored_patterns"]
    top_ids = [item["pattern_id"] for item in scored[:3]]

    assert "interactive_branching" in top_ids


def test_adaptive_story_pattern_engine_selects_series_and_movie_patterns():
    engine = AdaptiveStoryPatternEngine()

    result = engine.build_adaptive_pattern_plan(
        source_id="pattern_source",
        plot_outline=build_plot_outline(),
        format_plan=build_format_plan("movie"),
        screenplay_movie_package=build_screen_package(),
        series_package=build_series_package(),
        story_context={"genres": ["thriller"], "target_format": "movie"},
    )

    top_ids = [item["pattern_id"] for item in result["scored_patterns"][:5]]

    assert "cinematic_sequence" in top_ids
    assert "season_arc_weave" in top_ids


def test_adaptive_story_pattern_engine_handles_high_scaling_pressure():
    engine = AdaptiveStoryPatternEngine()

    plan = engine.build_adaptive_pattern_plan(
        source_id="pattern_source",
        plot_outline=build_plot_outline(),
        scaling_plan=build_scaling_plan(high=True),
        story_context={"genres": ["fantasy", "mystery"]},
    )["adaptive_story_pattern_plan"]

    assert "multi_world_convergence" in [plan.selected_primary_pattern] + plan.selected_secondary_patterns
    assert any("Multi-world" in rule or "world" in rule for rule in plan.anti_template_rules)
    assert plan.downstream_generation_constraints["generation_batch_ids"]


def test_adaptive_story_pattern_engine_creates_assignments():
    engine = AdaptiveStoryPatternEngine()

    plan = engine.build_adaptive_pattern_plan(
        source_id="pattern_source",
        plot_outline=build_plot_outline(),
        game_package=build_game_package(),
        scaling_plan=build_scaling_plan(),
    )["adaptive_story_pattern_plan"]

    assert plan.character_pattern_assignments
    assert plan.relationship_pattern_assignments
    assert plan.secret_pattern_assignments
    assert plan.causal_pattern_assignments
    assert plan.world_pattern_assignments


def test_adaptive_story_pattern_engine_validates_plan():
    engine = AdaptiveStoryPatternEngine()

    plan = engine.build_adaptive_pattern_plan(
        source_id="pattern_source",
        plot_outline=build_plot_outline(),
        format_plan=build_format_plan(),
        game_package=build_game_package(),
    )["adaptive_story_pattern_plan"]

    validation = engine.validate_pattern_plan(plan=plan)

    assert validation["success"] is True
    assert validation["valid"] is True
    assert "pattern_plan_id_present" in validation["passed_checks"]
    assert "primary_pattern_present" in validation["passed_checks"]
    assert "anti_template_rules_present" in validation["passed_checks"]


def test_adaptive_story_pattern_engine_summarizes_plan():
    engine = AdaptiveStoryPatternEngine()

    plan = engine.build_adaptive_pattern_plan(
        source_id="pattern_source",
        plot_outline=build_plot_outline(),
        format_plan=build_format_plan(),
        game_package=build_game_package(),
    )["adaptive_story_pattern_plan"]

    summary = engine.summarize_pattern_plan(plan=plan)

    assert summary["success"] is True
    assert summary["summary"]["source_id"] == "pattern_source"
    assert summary["summary"]["selected_primary_pattern"]
    assert summary["summary"]["anti_template_rule_count"] >= 1


def test_adaptive_story_pattern_engine_builds_report_text():
    engine = AdaptiveStoryPatternEngine()

    plan = engine.build_adaptive_pattern_plan(
        source_id="pattern_source",
        plot_outline=build_plot_outline(),
        format_plan=build_format_plan(),
        game_package=build_game_package(),
    )["adaptive_story_pattern_plan"]

    result = engine.build_pattern_report_text(plan=plan)

    assert result["success"] is True
    assert "Adaptive Story Pattern Plan" in result["pattern_report_text"]
    assert "Anti-Template Rules" in result["pattern_report_text"]

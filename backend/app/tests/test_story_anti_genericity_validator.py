from backend.app.engines.story_generation.story_anti_genericity_validator import StoryAntiGenericityValidator
from backend.app.schemas.story_generation import (
    AdaptiveStoryPatternPlan,
    FormatAdaptationPlan,
    GameInteractiveScenePackage,
    GeneratedChapter,
    PlotOutline,
    ScreenplayMovieFormatPackage,
    SeriesSeasonFormatPackage,
    StoryQualityScoreReport,
)


def build_plot_outline():
    return PlotOutline(
        outline_id="plot_outline_antigeneric",
        source_id="antigeneric_source",
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
        chapter_id="chapter_antigeneric",
        chapter_number=1,
        title="The Badge",
        chapter_text="Kael exposes the cracked badge in the Oath Court. Seren refuses to deny secret_seren_source.",
        scene_ids=["scene_001"],
        assembled_scene_ids=["assembled_scene_001"],
        used_character_ids=["char_kael", "char_seren"],
        used_relationship_ids=["rel_kael_seren"],
        used_secret_ids=["secret_seren_source"],
        used_causal_ids=["cause_trial_reveal"],
        used_world_details=["Oath Court", "cracked badge"],
        open_loops=[{"loop_id": "open_loop_secret", "description": "Secret remains hidden."}],
        next_chapter_hooks=["Seren refuses to deny the badge."],
    )


def build_adaptive_plan():
    return AdaptiveStoryPatternPlan(
        pattern_plan_id="adaptive_antigeneric",
        source_id="antigeneric_source",
        selected_primary_pattern="mystery_pressure",
        selected_secondary_patterns=["causal_escalation", "relationship_fracture"],
        anti_template_rules=[
            "Do not use a single universal three-act formula for every output.",
            "Do not resolve secrets immediately unless the reveal is explicitly required.",
            "Do not let choices be cosmetic; interactive choices must produce state deltas.",
            "Do not treat world details as decorative lore; each repeated detail needs consequence or pressure.",
        ],
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
        downstream_generation_constraints={"must_preserve_open_loops": True},
    )


def build_format_plan():
    return FormatAdaptationPlan(
        adaptation_plan_id="format_plan_antigeneric",
        source_id="antigeneric_source",
        target_format="game_scene",
        structure_rules={"unit_type": "interactive_scene"},
        prose_rules={"internality": "low"},
        dialogue_rules={"dialogue_density": "choice_aware"},
        pacing_rules={"shape": "choice-consequence"},
        continuity_rules={"must_preserve_secret_ids": ["secret_seren_source"]},
        required_sections=["setup", "choice", "state_delta"],
        forbidden_patterns=["generic template"],
    )


def build_game_package(with_state=True):
    return GameInteractiveScenePackage(
        game_package_id="game_antigeneric",
        source_id="antigeneric_source",
        scene_title="Interactive Court",
        player_objective="Expose or hide the badge.",
        choice_menu=[{"choice_id": "choice_1"}, {"choice_id": "choice_2"}],
        branching_outcomes=[{"outcome_id": "outcome_1"}],
        state_deltas=[{"state_delta_id": "delta_1"}] if with_state else [],
        secret_state_hooks=[{"secret_id": "secret_seren_source"}],
        causal_state_hooks=[{"causal_id": "cause_trial_reveal"}],
        world_state_hooks=[{"world_detail": "Oath Court"}],
        formatted_text="The player chooses whether to expose cause_trial_reveal or protect secret_seren_source.",
    )


def build_quality_report():
    return StoryQualityScoreReport(
        quality_report_id="quality_antigeneric",
        source_id="antigeneric_source",
        overall_score=0.76,
        anti_generic_score=0.80,
        dimension_breakdown=[],
        quality_gates=[],
    )


def test_story_anti_genericity_validator_builds_report():
    validator = StoryAntiGenericityValidator()

    result = validator.validate_anti_genericity(
        source_id="antigeneric_source",
        generated_text="Kael holds the cracked badge. The Oath Court waits. cause_trial_reveal changes the vote.",
        plot_outline=build_plot_outline(),
        chapter=build_chapter(),
        adaptive_pattern_plan=build_adaptive_plan(),
        quality_report=build_quality_report(),
        format_plan=build_format_plan(),
        game_package=build_game_package(),
    )

    report = result["story_anti_genericity_report"]

    assert result["success"] is True
    assert report.anti_genericity_report_id == "story_anti_genericity_antigeneric_source"
    assert report.overall_anti_genericity_score > 0.0
    assert report.genericity_risk_level in {"low", "medium", "high", "critical"}
    assert report.specificity_evidence
    assert report.anti_template_rule_results


def test_story_anti_genericity_validator_detects_generic_phrases():
    validator = StoryAntiGenericityValidator()

    report = validator.validate_anti_genericity(
        source_id="generic_source",
        generated_text="Little did they know, a secret would change everything. The journey had just begun.",
        plot_outline=build_plot_outline(),
        adaptive_pattern_plan=build_adaptive_plan(),
    )["story_anti_genericity_report"]

    assert report.detected_generic_patterns
    assert any(item["pattern_type"] == "generic_phrase" for item in report.detected_generic_patterns)
    assert report.rewrite_targets


def test_story_anti_genericity_validator_detects_cosmetic_choices():
    validator = StoryAntiGenericityValidator()

    report = validator.validate_anti_genericity(
        source_id="cosmetic_choice_source",
        generated_text="The player chooses.",
        plot_outline=build_plot_outline(),
        adaptive_pattern_plan=build_adaptive_plan(),
        game_package=build_game_package(with_state=False),
    )["story_anti_genericity_report"]

    assert any(item["pattern_id"] == "choices_without_state_delta" for item in report.detected_generic_patterns)
    assert any("state deltas" in item["instruction"] or "state" in item["instruction"] for item in report.rewrite_targets)


def test_story_anti_genericity_validator_scores_specific_context_higher_than_empty_context():
    validator = StoryAntiGenericityValidator()

    strong = validator.validate_anti_genericity(
        source_id="strong_source",
        generated_text="Kael names the cracked badge in the Oath Court and forces cause_trial_reveal into public record.",
        plot_outline=build_plot_outline(),
        chapter=build_chapter(),
        adaptive_pattern_plan=build_adaptive_plan(),
        quality_report=build_quality_report(),
        format_plan=build_format_plan(),
        game_package=build_game_package(),
    )["story_anti_genericity_report"]

    weak = validator.validate_anti_genericity(
        source_id="weak_source",
        generated_text="Something changed forever. Only time would tell.",
    )["story_anti_genericity_report"]

    assert strong.overall_anti_genericity_score > weak.overall_anti_genericity_score
    assert weak.genericity_risk_level in {"high", "critical", "medium"}


def test_story_anti_genericity_validator_validates_report():
    validator = StoryAntiGenericityValidator()

    report = validator.validate_anti_genericity(
        source_id="antigeneric_source",
        generated_text="Kael exposes cause_trial_reveal in the Oath Court.",
        plot_outline=build_plot_outline(),
        chapter=build_chapter(),
        adaptive_pattern_plan=build_adaptive_plan(),
        quality_report=build_quality_report(),
        format_plan=build_format_plan(),
        game_package=build_game_package(),
    )["story_anti_genericity_report"]

    validation = validator.validate_report(report=report)

    assert validation["success"] is True
    assert validation["valid"] is True
    assert "anti_genericity_report_id_present" in validation["passed_checks"]
    assert "scores_bounded" in validation["passed_checks"]
    assert "risk_level_valid" in validation["passed_checks"]


def test_story_anti_genericity_validator_summarizes_report():
    validator = StoryAntiGenericityValidator()

    report = validator.validate_anti_genericity(
        source_id="antigeneric_source",
        generated_text="Kael exposes cause_trial_reveal in the Oath Court.",
        plot_outline=build_plot_outline(),
        chapter=build_chapter(),
        adaptive_pattern_plan=build_adaptive_plan(),
        quality_report=build_quality_report(),
        format_plan=build_format_plan(),
        game_package=build_game_package(),
    )["story_anti_genericity_report"]

    summary = validator.summarize_report(report=report)

    assert summary["success"] is True
    assert summary["summary"]["source_id"] == "antigeneric_source"
    assert "weakest_dimension" in summary["summary"]
    assert summary["summary"]["rewrite_target_count"] >= 0


def test_story_anti_genericity_validator_builds_report_text():
    validator = StoryAntiGenericityValidator()

    report = validator.validate_anti_genericity(
        source_id="antigeneric_source",
        generated_text="Kael exposes cause_trial_reveal in the Oath Court.",
        plot_outline=build_plot_outline(),
        chapter=build_chapter(),
        adaptive_pattern_plan=build_adaptive_plan(),
        quality_report=build_quality_report(),
        format_plan=build_format_plan(),
        game_package=build_game_package(),
    )["story_anti_genericity_report"]

    text = validator.build_anti_genericity_report_text(report=report)["anti_genericity_report_text"]

    assert "Story Anti-Genericity Report" in text
    assert "Rewrite Targets" in text
    assert "Approved Strengths" in text

from backend.app.engines.story_generation.originality_copy_risk_guard import OriginalityCopyRiskGuard
from backend.app.schemas.story_generation import (
    AdaptiveStoryPatternPlan,
    GameInteractiveScenePackage,
    GeneratedChapter,
    PlotOutline,
    StoryAntiGenericityReport,
    StoryContinuityValidationReport,
    StoryQualityScoreReport,
)


def build_plot_outline():
    return PlotOutline(
        outline_id="plot_outline_originality",
        source_id="originality_source",
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
            {"thread_id": "world_thread_oath_court", "world_detail": "Oath Court"},
            {"thread_id": "world_thread_cracked_badge", "world_detail": "cracked badge"},
        ],
        open_loops=[{"loop_id": "open_loop_secret", "description": "Secret remains hidden."}],
        payoff_setups=[{"payoff_id": "payoff_secret", "description": "Reveal carefully."}],
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
        chapter_id="chapter_originality",
        chapter_number=1,
        title="The Badge",
        chapter_text="Kael exposes the cracked badge in the Oath Court. Seren refuses to answer.",
        scene_ids=["scene_001"],
        assembled_scene_ids=["assembled_scene_001"],
        used_character_ids=["char_kael", "char_seren"],
        used_relationship_ids=["rel_kael_seren"],
        used_secret_ids=["secret_seren_source"],
        used_causal_ids=["cause_trial_reveal"],
        used_world_details=["Oath Court", "cracked badge"],
        open_loops=[{"loop_id": "open_loop_secret", "description": "Secret remains hidden."}],
    )


def build_adaptive_plan():
    return AdaptiveStoryPatternPlan(
        pattern_plan_id="adaptive_originality",
        source_id="originality_source",
        selected_primary_pattern="mystery_pressure",
        selected_secondary_patterns=["causal_escalation"],
        anti_template_rules=[
            "Do not use a single universal three-act formula.",
            "Do not resolve secrets immediately.",
        ],
        downstream_generation_constraints={"must_preserve_open_loops": True},
    )


def build_quality_report():
    return StoryQualityScoreReport(
        quality_report_id="quality_originality",
        source_id="originality_source",
        overall_score=0.78,
        anti_generic_score=0.82,
    )


def build_anti_genericity_report():
    return StoryAntiGenericityReport(
        report_id="anti_originality",
        draft_id="originality_source",
        anti_genericity_report_id="anti_originality",
        source_id="originality_source",
        overall_anti_genericity_score=0.78,
        genericity_risk_level="medium",
    )


def build_continuity_report():
    return StoryContinuityValidationReport(
        continuity_report_id="continuity_originality",
        source_id="originality_source",
        valid=True,
        continuity_score=0.81,
    )


def build_game_package():
    return GameInteractiveScenePackage(
        game_package_id="game_originality",
        source_id="originality_source",
        scene_title="Interactive Court",
        player_objective="Expose or hide the badge.",
        choice_menu=[{"choice_id": "choice_1"}, {"choice_id": "choice_2"}],
        branching_outcomes=[{"outcome_id": "outcome_1"}],
        state_deltas=[{"state_delta_id": "delta_1"}],
        formatted_text="The player decides whether cause_trial_reveal becomes public record.",
    )


def test_originality_copy_risk_guard_builds_report():
    guard = OriginalityCopyRiskGuard()

    result = guard.evaluate_copy_risk(
        source_id="originality_source",
        generated_text="Kael exposes the cracked badge in the Oath Court and forces cause_trial_reveal into record.",
        plot_outline=build_plot_outline(),
        chapter=build_chapter(),
        adaptive_pattern_plan=build_adaptive_plan(),
        quality_report=build_quality_report(),
        anti_genericity_report=build_anti_genericity_report(),
        continuity_report=build_continuity_report(),
        game_package=build_game_package(),
        reference_texts=[
            {"source_id": "safe_public_domain_fixture", "policy": "public_domain", "text": "A separate public domain sample."}
        ],
    )

    report = result["originality_copy_risk_report"]

    assert result["success"] is True
    assert report.originality_report_id == "originality_copy_risk_originality_source"
    assert report.overall_originality_score >= 0.0
    assert report.copy_risk_level in {"low", "medium", "high", "critical"}
    assert report.originality_evidence
    assert report.downstream_constraints


def test_originality_copy_risk_guard_detects_reference_phrase_overlap():
    guard = OriginalityCopyRiskGuard()

    shared = "the cracked badge lay beneath the oath court while the witness refused"

    report = guard.evaluate_copy_risk(
        source_id="overlap_source",
        generated_text=f"{shared} and the crowd waited.",
        reference_texts=[
            {
                "source_id": "restricted_reference",
                "policy": "restricted",
                "text": f"{shared} before the old judge spoke.",
            }
        ],
    )["originality_copy_risk_report"]

    assert report.detected_risks
    assert any(item["risk_type"] == "reference_phrase_overlap" for item in report.detected_risks)
    assert report.copy_risk_level in {"high", "critical"}
    assert report.rewrite_requirements
    assert report.safe_for_export is False


def test_originality_copy_risk_guard_detects_protected_style_warning():
    guard = OriginalityCopyRiskGuard()

    report = guard.evaluate_copy_risk(
        source_id="style_risk",
        generated_text="Make it like a famous franchise with Jedi and lightsaber politics.",
        story_context={
            "style_instructions": ["write like a famous living author", "in the style of a protected franchise"]
        },
    )["originality_copy_risk_report"]

    assert report.protected_style_warnings
    assert report.copy_risk_level in {"high", "critical"}
    assert report.safe_for_export is False


def test_originality_copy_risk_guard_validates_report():
    guard = OriginalityCopyRiskGuard()

    report = guard.evaluate_copy_risk(
        source_id="originality_source",
        generated_text="Kael exposes cause_trial_reveal in the Oath Court.",
        plot_outline=build_plot_outline(),
        chapter=build_chapter(),
        adaptive_pattern_plan=build_adaptive_plan(),
        quality_report=build_quality_report(),
        anti_genericity_report=build_anti_genericity_report(),
        continuity_report=build_continuity_report(),
    )["originality_copy_risk_report"]

    validation = guard.validate_report(report=report)

    assert validation["success"] is True
    assert validation["valid"] is True
    assert "originality_report_id_present" in validation["passed_checks"]
    assert "scores_bounded" in validation["passed_checks"]
    assert "copy_risk_level_valid" in validation["passed_checks"]


def test_originality_copy_risk_guard_summarizes_report():
    guard = OriginalityCopyRiskGuard()

    report = guard.evaluate_copy_risk(
        source_id="originality_source",
        generated_text="Kael exposes cause_trial_reveal in the Oath Court.",
        plot_outline=build_plot_outline(),
        chapter=build_chapter(),
        adaptive_pattern_plan=build_adaptive_plan(),
    )["originality_copy_risk_report"]

    summary = guard.summarize_report(report=report)

    assert summary["success"] is True
    assert summary["summary"]["source_id"] == "originality_source"
    assert "copy_risk_level" in summary["summary"]


def test_originality_copy_risk_guard_builds_report_text():
    guard = OriginalityCopyRiskGuard()

    report = guard.evaluate_copy_risk(
        source_id="originality_source",
        generated_text="Kael exposes cause_trial_reveal in the Oath Court.",
        plot_outline=build_plot_outline(),
        chapter=build_chapter(),
        adaptive_pattern_plan=build_adaptive_plan(),
    )["originality_copy_risk_report"]

    text = guard.build_copy_risk_report_text(report=report)["copy_risk_report_text"]

    assert "Originality / Copy-Risk Report" in text
    assert "Detected Risks" in text
    assert "Rewrite Requirements" in text

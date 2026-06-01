from backend.app.engines.story_generation.story_revision_engine import StoryRevisionEngine
from backend.app.schemas.story_generation import (
    AdaptiveStoryPatternPlan,
    GeneratedChapter,
    OriginalityCopyRiskReport,
    PlotOutline,
    StoryAntiGenericityReport,
    StoryContinuityValidationReport,
    StoryQualityScoreReport,
)


def build_plot_outline():
    return PlotOutline(
        outline_id="plot_outline_revision",
        source_id="revision_source",
        title="Court Secrets",
        premise="A public proof system threatens private loyalties.",
        scene_sequence=[{"scene_id": "scene_001", "purpose": "Expose the badge."}],
        act_structure=[{"act_number": 1, "act_purpose": "Setup", "scene_ids": ["scene_001"]}],
        character_arc_threads=[{"thread_id": "char_thread", "character_id": "char_kael"}],
        relationship_arc_threads=[{"thread_id": "rel_thread", "relationship_id": "rel_kael_seren"}],
        secret_threads=[{"thread_id": "secret_thread", "secret_id": "secret_seren_source"}],
        causal_threads=[{"thread_id": "causal_thread", "causal_id": "cause_trial_reveal"}],
        world_state_threads=[{"thread_id": "world_thread", "world_detail": "Oath Court"}],
        open_loops=[{"loop_id": "open_loop_secret", "description": "Secret remains hidden."}],
        payoff_setups=[{"payoff_id": "payoff_secret", "description": "Reveal carefully."}],
        continuity_requirements={
            "required_character_ids": ["char_kael"],
            "required_relationship_ids": ["rel_kael_seren"],
            "required_secret_ids": ["secret_seren_source"],
            "required_causal_ids": ["cause_trial_reveal"],
            "required_world_details": ["Oath Court"],
        },
    )


def build_chapter():
    return GeneratedChapter(
        chapter_id="chapter_revision",
        chapter_number=1,
        title="The Badge",
        chapter_text="Kael exposes the cracked badge.",
        scene_ids=["scene_001"],
        assembled_scene_ids=["assembled_scene_001"],
        used_character_ids=["char_kael"],
        used_relationship_ids=["rel_kael_seren"],
        used_secret_ids=["secret_seren_source"],
        used_causal_ids=["cause_trial_reveal"],
        used_world_details=["Oath Court"],
        open_loops=[{"loop_id": "open_loop_secret"}],
    )


def build_quality_report():
    return StoryQualityScoreReport(
        quality_report_id="quality_revision",
        source_id="revision_source",
        overall_score=0.61,
        readiness_level="needs_revision",
        anti_generic_score=0.52,
        revision_priorities=[
            {
                "priority_id": "revise_causal",
                "dimension": "causal",
                "score": 0.48,
                "priority": "high",
                "instruction": "Strengthen setup, choice, consequence, and payoff chains.",
            },
            {
                "priority_id": "revise_world",
                "dimension": "world",
                "score": 0.57,
                "priority": "medium",
                "instruction": "Make world rules more consequential.",
            },
        ],
    )


def build_anti_genericity_report():
    return StoryAntiGenericityReport(
        report_id="anti_revision",
        draft_id="revision_source",
        anti_genericity_report_id="anti_revision",
        source_id="revision_source",
        overall_anti_genericity_score=0.56,
        genericity_risk_level="high",
        rewrite_targets=[
            {
                "rewrite_target_id": "rewrite_weak_specificity",
                "target_type": "specificity",
                "priority": "high",
                "instruction": "Add named world details and exact stakes.",
            }
        ],
    )


def build_continuity_report(valid=True):
    return StoryContinuityValidationReport(
        continuity_report_id="continuity_revision",
        source_id="revision_source",
        valid=valid,
        continuity_score=0.72 if valid else 0.42,
        readiness_level="needs_light_repair" if valid else "blocked",
        checked_character_ids=["char_kael"],
        checked_relationship_ids=["rel_kael_seren"],
        checked_secret_ids=["secret_seren_source"],
        checked_causal_ids=["cause_trial_reveal"],
        checked_world_details=["Oath Court"],
        checked_open_loop_ids=["open_loop_secret"],
        repair_targets=[] if valid else [
            {
                "repair_target_id": "repair_missing_secret",
                "target_type": "missing_secret_ids",
                "priority": "high",
                "instruction": "Restore secret continuity for secret_seren_source.",
            }
        ],
        downstream_constraints={
            "must_preserve_character_ids": ["char_kael"],
            "must_preserve_secret_ids": ["secret_seren_source"],
            "must_preserve_causal_ids": ["cause_trial_reveal"],
            "must_preserve_world_details": ["Oath Court"],
        },
    )


def build_originality_report(safe=True):
    return OriginalityCopyRiskReport(
        originality_report_id="originality_revision",
        source_id="revision_source",
        safe_for_export=safe,
        overall_originality_score=0.74 if safe else 0.31,
        copy_risk_level="medium" if safe else "critical",
        rewrite_requirements=[] if safe else [
            {
                "rewrite_requirement_id": "rewrite_reference_overlap",
                "requirement_type": "reference_phrase_overlap",
                "severity": "blocker",
                "instruction": "Rewrite overlapping phrases with new imagery.",
            }
        ],
        approved_original_elements=["Specific world detail exists: Oath Court."],
        downstream_constraints={
            "copy_risk_level": "medium" if safe else "critical",
            "safe_for_export_without_rewrite": safe,
        },
    )


def build_adaptive_plan():
    return AdaptiveStoryPatternPlan(
        pattern_plan_id="adaptive_revision",
        source_id="revision_source",
        selected_primary_pattern="mystery_pressure",
        selected_secondary_patterns=["causal_escalation"],
        anti_template_rules=["Do not drop open loops silently."],
        downstream_generation_constraints={"must_preserve_open_loops": True},
    )


def test_story_revision_engine_builds_plan():
    engine = StoryRevisionEngine()

    result = engine.build_revision_plan(
        source_id="revision_source",
        plot_outline=build_plot_outline(),
        chapter=build_chapter(),
        quality_report=build_quality_report(),
        anti_genericity_report=build_anti_genericity_report(),
        continuity_report=build_continuity_report(),
        originality_report=build_originality_report(),
        adaptive_pattern_plan=build_adaptive_plan(),
    )

    plan = result["story_revision_plan"]

    assert result["success"] is True
    assert plan.revision_plan_id == "story_revision_plan_revision_source"
    assert plan.revision_goals
    assert plan.quality_revision_tasks
    assert plan.anti_genericity_revision_tasks
    assert plan.rewrite_order
    assert plan.revision_constraints


def test_story_revision_engine_prioritizes_copy_risk_and_continuity_blockers():
    engine = StoryRevisionEngine()

    plan = engine.build_revision_plan(
        source_id="blocked_revision",
        plot_outline=build_plot_outline(),
        chapter=build_chapter(),
        quality_report=build_quality_report(),
        anti_genericity_report=build_anti_genericity_report(),
        continuity_report=build_continuity_report(valid=False),
        originality_report=build_originality_report(safe=False),
        adaptive_pattern_plan=build_adaptive_plan(),
    )["story_revision_plan"]

    assert plan.overall_revision_priority == "critical"
    assert plan.revision_mode == "blocked_until_risk_resolved"
    assert plan.blocking_issues
    assert plan.rewrite_order[0]["priority"] == "critical"


def test_story_revision_engine_protects_core_threads():
    engine = StoryRevisionEngine()

    plan = engine.build_revision_plan(
        source_id="revision_source",
        plot_outline=build_plot_outline(),
        chapter=build_chapter(),
        continuity_report=build_continuity_report(),
        originality_report=build_originality_report(),
        adaptive_pattern_plan=build_adaptive_plan(),
    )["story_revision_plan"]

    protected_values = {item["value"] for item in plan.protected_elements}

    assert "char_kael" in protected_values
    assert "secret_seren_source" in protected_values
    assert "cause_trial_reveal" in protected_values
    assert "Oath Court" in protected_values


def test_story_revision_engine_validates_plan():
    engine = StoryRevisionEngine()

    plan = engine.build_revision_plan(
        source_id="revision_source",
        quality_report=build_quality_report(),
        anti_genericity_report=build_anti_genericity_report(),
        continuity_report=build_continuity_report(),
        originality_report=build_originality_report(),
    )["story_revision_plan"]

    validation = engine.validate_revision_plan(plan=plan)

    assert validation["success"] is True
    assert validation["valid"] is True
    assert "revision_plan_id_present" in validation["passed_checks"]
    assert "priority_valid" in validation["passed_checks"]
    assert "revision_mode_valid" in validation["passed_checks"]


def test_story_revision_engine_summarizes_plan():
    engine = StoryRevisionEngine()

    plan = engine.build_revision_plan(
        source_id="revision_source",
        quality_report=build_quality_report(),
        anti_genericity_report=build_anti_genericity_report(),
        continuity_report=build_continuity_report(),
        originality_report=build_originality_report(),
    )["story_revision_plan"]

    summary = engine.summarize_revision_plan(plan=plan)

    assert summary["success"] is True
    assert summary["summary"]["source_id"] == "revision_source"
    assert summary["summary"]["rewrite_step_count"] >= 1


def test_story_revision_engine_builds_plan_text():
    engine = StoryRevisionEngine()

    plan = engine.build_revision_plan(
        source_id="revision_source",
        quality_report=build_quality_report(),
        anti_genericity_report=build_anti_genericity_report(),
        continuity_report=build_continuity_report(),
        originality_report=build_originality_report(),
    )["story_revision_plan"]

    text = engine.build_revision_plan_text(plan=plan)["revision_plan_text"]

    assert "Story Revision Plan" in text
    assert "Revision Goals" in text
    assert "Rewrite Order" in text

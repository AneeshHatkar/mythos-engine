from backend.app.engines.story_generation.draft_comparison_engine import DraftComparisonEngine
from backend.app.schemas.story_generation import (
    DraftComparisonReport,
    OriginalityCopyRiskReport,
    StoryAntiGenericityReport,
    StoryContinuityValidationReport,
    StoryQualityScoreReport,
    StoryRevisionPlan,
)


def build_revision_plan():
    return StoryRevisionPlan(
        revision_plan_id="story_revision_plan_compare",
        source_id="compare_source",
        revision_mode="targeted",
        overall_revision_priority="high",
        revision_goals=[
            {"goal_id": "goal_quality", "goal_type": "quality", "description": "Improve quality."}
        ],
        protected_elements=[
            {"element_id": "protect_character_char_kael", "element_type": "character", "value": "char_kael"},
            {"element_id": "protect_secret_secret_seren_source", "element_type": "secret", "value": "secret_seren_source"},
            {"element_id": "protect_causal_cause_trial_reveal", "element_type": "causal", "value": "cause_trial_reveal"},
            {"element_id": "protect_world_oath_court", "element_type": "world_detail", "value": "Oath Court"},
        ],
        rewrite_order=[
            {
                "step_number": 1,
                "task_id": "quality_revision_causal",
                "task_type": "quality_revision",
                "priority": "high",
                "dimension": "causal",
                "instruction": "Strengthen causality.",
                "source": "story_quality_score_report",
            },
            {
                "step_number": 2,
                "task_id": "anti_genericity_specificity",
                "task_type": "anti_genericity_rewrite",
                "priority": "high",
                "dimension": "specificity",
                "instruction": "Add specific details.",
                "source": "story_anti_genericity_report",
            },
        ],
        revision_constraints={
            "must_preserve_character_voice": True,
            "must_preserve_world_state": True,
        },
    )


def quality(score):
    return StoryQualityScoreReport(
        quality_report_id=f"quality_{score}",
        source_id="compare_source",
        overall_score=score,
        anti_generic_score=score,
    )


def anti(score, risk="medium"):
    return StoryAntiGenericityReport(
        report_id=f"anti_{score}",
        draft_id="compare_source",
        anti_genericity_report_id=f"anti_{score}",
        source_id="compare_source",
        overall_anti_genericity_score=score,
        genericity_risk_level=risk,
    )


def continuity(score, valid=True):
    return StoryContinuityValidationReport(
        continuity_report_id=f"continuity_{score}",
        source_id="compare_source",
        valid=valid,
        continuity_score=score,
    )


def originality(score, safe=True):
    return OriginalityCopyRiskReport(
        originality_report_id=f"originality_{score}",
        source_id="compare_source",
        safe_for_export=safe,
        overall_originality_score=score,
        copy_risk_level="medium" if safe else "critical",
    )


def test_draft_comparison_engine_builds_approved_report():
    engine = DraftComparisonEngine()

    result = engine.compare_drafts(
        source_id="compare_source",
        original_draft_id="draft_original",
        revised_draft_id="draft_revised",
        original_text="char_kael sees the badge.",
        revised_text="char_kael exposes cause_trial_reveal in the Oath Court while protecting secret_seren_source.",
        revision_plan=build_revision_plan(),
        original_quality_report=quality(0.55),
        revised_quality_report=quality(0.72),
        original_anti_genericity_report=anti(0.50),
        revised_anti_genericity_report=anti(0.75),
        original_continuity_report=continuity(0.62),
        revised_continuity_report=continuity(0.82),
        original_originality_report=originality(0.62),
        revised_originality_report=originality(0.78),
        story_context={
            "known_character_ids": ["char_kael"],
            "known_secret_ids": ["secret_seren_source"],
            "known_causal_ids": ["cause_trial_reveal"],
            "known_world_details": ["Oath Court"],
        },
    )

    report = result["draft_comparison_report"]

    assert result["success"] is True
    assert report.comparison_report_id == "draft_comparison_compare_source"
    assert report.improvement_score > 0.45
    assert report.regression_risk_score <= 0.35
    assert report.preserved_elements
    assert report.approved is True


def test_draft_comparison_engine_detects_lost_protected_elements():
    engine = DraftComparisonEngine()

    report = engine.compare_drafts(
        source_id="compare_source",
        original_draft_id="draft_original",
        revised_draft_id="draft_revised",
        original_text="char_kael protects secret_seren_source in the Oath Court.",
        revised_text="A stranger walks away from the hall.",
        revision_plan=build_revision_plan(),
        original_quality_report=quality(0.60),
        revised_quality_report=quality(0.62),
        original_continuity_report=continuity(0.70),
        revised_continuity_report=continuity(0.40, valid=False),
        original_originality_report=originality(0.70),
        revised_originality_report=originality(0.60),
        story_context={
            "known_character_ids": ["char_kael"],
            "known_secret_ids": ["secret_seren_source"],
            "known_causal_ids": ["cause_trial_reveal"],
            "known_world_details": ["Oath Court"],
        },
    )["draft_comparison_report"]

    assert report.lost_protected_elements
    assert report.regression_flags
    assert report.approved is False
    assert report.approval_requirements


def test_draft_comparison_engine_detects_score_regressions():
    engine = DraftComparisonEngine()

    report = engine.compare_drafts(
        source_id="compare_source",
        original_draft_id="draft_original",
        revised_draft_id="draft_revised",
        original_text="char_kael protects secret_seren_source in the Oath Court.",
        revised_text="char_kael protects secret_seren_source in the Oath Court.",
        revision_plan=build_revision_plan(),
        original_quality_report=quality(0.80),
        revised_quality_report=quality(0.60),
        original_anti_genericity_report=anti(0.80),
        revised_anti_genericity_report=anti(0.55, risk="high"),
        original_continuity_report=continuity(0.85),
        revised_continuity_report=continuity(0.70),
        original_originality_report=originality(0.82),
        revised_originality_report=originality(0.65),
        story_context={
            "known_character_ids": ["char_kael"],
            "known_secret_ids": ["secret_seren_source"],
            "known_world_details": ["Oath Court"],
        },
    )["draft_comparison_report"]

    assert report.quality_delta < 0
    assert report.anti_genericity_delta < 0
    assert report.regression_flags
    assert report.approved is False


def test_draft_comparison_engine_validates_report():
    engine = DraftComparisonEngine()

    report = engine.compare_drafts(
        source_id="compare_source",
        original_draft_id="draft_original",
        revised_draft_id="draft_revised",
        original_text="char_kael sees the badge.",
        revised_text="char_kael protects secret_seren_source in the Oath Court.",
        revision_plan=build_revision_plan(),
        original_quality_report=quality(0.55),
        revised_quality_report=quality(0.72),
    )["draft_comparison_report"]

    validation = engine.validate_comparison_report(report=report)

    assert validation["success"] is True
    assert validation["valid"] is True
    assert "comparison_report_id_present" in validation["passed_checks"]
    assert "scores_bounded" in validation["passed_checks"]


def test_draft_comparison_engine_summarizes_report():
    engine = DraftComparisonEngine()

    report = engine.compare_drafts(
        source_id="compare_source",
        original_draft_id="draft_original",
        revised_draft_id="draft_revised",
        original_text="char_kael sees the badge.",
        revised_text="char_kael protects secret_seren_source in the Oath Court.",
        revision_plan=build_revision_plan(),
        original_quality_report=quality(0.55),
        revised_quality_report=quality(0.72),
    )["draft_comparison_report"]

    summary = engine.summarize_comparison_report(report=report)

    assert summary["success"] is True
    assert summary["summary"]["source_id"] == "compare_source"
    assert "improvement_score" in summary["summary"]


def test_draft_comparison_engine_builds_report_text():
    engine = DraftComparisonEngine()

    report = engine.compare_drafts(
        source_id="compare_source",
        original_draft_id="draft_original",
        revised_draft_id="draft_revised",
        original_text="char_kael sees the badge.",
        revised_text="char_kael protects secret_seren_source in the Oath Court.",
        revision_plan=build_revision_plan(),
        original_quality_report=quality(0.55),
        revised_quality_report=quality(0.72),
    )["draft_comparison_report"]

    text = engine.build_comparison_report_text(report=report)["comparison_report_text"]

    assert "Draft Comparison Report" in text
    assert "Score Deltas" in text
    assert "Approval Requirements" in text

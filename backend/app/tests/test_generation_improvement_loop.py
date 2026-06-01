from backend.app.engines.story_generation.generation_improvement_loop import GenerationImprovementLoop
from backend.app.schemas.story_generation import DraftComparisonReport, StoryRevisionPlan


def build_revision_plan(blocking=False):
    return StoryRevisionPlan(
        revision_plan_id="revision_plan_loop",
        source_id="loop_source",
        revision_mode="targeted",
        overall_revision_priority="high" if blocking else "medium",
        protected_elements=[
            {"element_id": "protect_character_char_kael", "element_type": "character", "value": "char_kael"},
            {"element_id": "protect_secret_secret_seren_source", "element_type": "secret", "value": "secret_seren_source"},
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
            }
        ],
        blocking_issues=[
            {
                "blocking_issue_id": "blocking_copy_risk",
                "issue_type": "copy_risk",
                "severity": "blocker",
                "description": "Copy-risk is not safe.",
            }
        ] if blocking else [],
    )


def approved_comparison():
    return DraftComparisonReport(
        comparison_report_id="draft_comparison_loop",
        source_id="loop_source",
        original_draft_id="draft_original",
        revised_draft_id="draft_revised",
        approved=True,
        improvement_score=0.72,
        regression_risk_score=0.05,
        quality_delta=0.15,
        anti_genericity_delta=0.12,
        continuity_delta=0.08,
        originality_delta=0.04,
        preserved_elements=[
            {"element_id": "protect_character_char_kael", "element_type": "character", "value": "char_kael"}
        ],
        task_completion_results=[
            {
                "task_result_id": "task_result_quality_revision_causal",
                "task_id": "quality_revision_causal",
                "task_type": "quality_revision",
                "priority": "high",
                "passed": True,
                "reason": "Quality improved.",
            }
        ],
        downstream_constraints={"approved_for_improvement_loop": True},
    )


def targeted_comparison():
    return DraftComparisonReport(
        comparison_report_id="draft_comparison_loop_targeted",
        source_id="loop_source",
        original_draft_id="draft_original",
        revised_draft_id="draft_revised",
        approved=False,
        improvement_score=0.42,
        regression_risk_score=0.18,
        quality_delta=0.04,
        anti_genericity_delta=0.01,
        continuity_delta=0.0,
        originality_delta=0.0,
        task_completion_results=[
            {
                "task_result_id": "task_result_specificity",
                "task_id": "anti_genericity_specificity",
                "task_type": "anti_genericity_rewrite",
                "priority": "medium",
                "passed": False,
                "reason": "Specificity did not improve enough.",
            }
        ],
        approval_requirements=[
            {
                "requirement_id": "approval_minimum_improvement",
                "requirement_type": "improvement",
                "priority": "medium",
                "instruction": "Apply another targeted pass.",
            }
        ],
        downstream_constraints={"approved_for_improvement_loop": False},
    )


def deep_comparison():
    return DraftComparisonReport(
        comparison_report_id="draft_comparison_loop_deep",
        source_id="loop_source",
        original_draft_id="draft_original",
        revised_draft_id="draft_revised",
        approved=False,
        improvement_score=0.28,
        regression_risk_score=0.52,
        quality_delta=-0.10,
        anti_genericity_delta=-0.05,
        continuity_delta=0.0,
        originality_delta=0.0,
        regression_flags=[
            {
                "flag_id": "regression_quality",
                "flag_type": "quality_regression",
                "severity": "high",
                "description": "Quality regressed.",
            }
        ],
        approval_requirements=[
            {
                "requirement_id": "approval_regression_risk",
                "requirement_type": "regression_risk",
                "priority": "high",
                "instruction": "Regression risk is too high.",
            }
        ],
        downstream_constraints={"approved_for_improvement_loop": False},
    )


def blocked_comparison():
    return DraftComparisonReport(
        comparison_report_id="draft_comparison_loop_blocked",
        source_id="loop_source",
        original_draft_id="draft_original",
        revised_draft_id="draft_revised",
        approved=False,
        improvement_score=0.20,
        regression_risk_score=0.80,
        originality_delta=-0.30,
        approval_requirements=[
            {
                "requirement_id": "approval_copy_risk_safe_export",
                "requirement_type": "copy_risk",
                "priority": "critical",
                "instruction": "Resolve copy-risk blockers.",
            }
        ],
        downstream_constraints={"approved_for_improvement_loop": False},
    )


def test_generation_improvement_loop_approves_clean_revision():
    loop = GenerationImprovementLoop()

    result = loop.decide_next_step(
        source_id="loop_source",
        comparison_report=approved_comparison(),
        revision_plan=build_revision_plan(),
        current_iteration=1,
        max_iterations=3,
    )

    decision = result["generation_improvement_loop_decision"]

    assert result["success"] is True
    assert decision.action == "approve_and_handoff"
    assert decision.approved_for_handoff is True
    assert decision.stop_loop is True
    assert decision.next_engine_payload["target_engine"] == "story_generation.story_provenance_engine"


def test_generation_improvement_loop_requests_targeted_revision():
    loop = GenerationImprovementLoop()

    decision = loop.decide_next_step(
        source_id="loop_source",
        comparison_report=targeted_comparison(),
        revision_plan=build_revision_plan(),
        current_iteration=1,
        max_iterations=3,
    )["generation_improvement_loop_decision"]

    assert decision.action == "revise_again_targeted"
    assert decision.next_revision_mode == "targeted"
    assert decision.stop_loop is False
    assert decision.required_actions


def test_generation_improvement_loop_requests_deep_revision_for_regression():
    loop = GenerationImprovementLoop()

    decision = loop.decide_next_step(
        source_id="loop_source",
        comparison_report=deep_comparison(),
        revision_plan=build_revision_plan(),
        current_iteration=1,
        max_iterations=3,
    )["generation_improvement_loop_decision"]

    assert decision.action == "revise_again_deep"
    assert decision.next_revision_mode == "deep"
    assert decision.next_priority == "high"
    assert decision.unresolved_items


def test_generation_improvement_loop_blocks_critical_copy_risk():
    loop = GenerationImprovementLoop()

    decision = loop.decide_next_step(
        source_id="loop_source",
        comparison_report=blocked_comparison(),
        revision_plan=build_revision_plan(blocking=True),
        current_iteration=1,
        max_iterations=3,
    )["generation_improvement_loop_decision"]

    assert decision.action == "blocked_until_manual_review"
    assert decision.stop_loop is True
    assert decision.approved_for_handoff is False
    assert decision.next_revision_mode == "blocked_until_risk_resolved"


def test_generation_improvement_loop_stops_at_max_iterations():
    loop = GenerationImprovementLoop()

    decision = loop.decide_next_step(
        source_id="loop_source",
        comparison_report=targeted_comparison(),
        revision_plan=build_revision_plan(),
        current_iteration=3,
        max_iterations=3,
    )["generation_improvement_loop_decision"]

    assert decision.action == "stop_max_iterations"
    assert decision.stop_loop is True
    assert decision.approved_for_handoff is False


def test_generation_improvement_loop_validates_decision():
    loop = GenerationImprovementLoop()

    decision = loop.decide_next_step(
        source_id="loop_source",
        comparison_report=targeted_comparison(),
        revision_plan=build_revision_plan(),
        current_iteration=1,
        max_iterations=3,
    )["generation_improvement_loop_decision"]

    validation = loop.validate_loop_decision(decision=decision)

    assert validation["success"] is True
    assert validation["valid"] is True
    assert "loop_decision_id_present" in validation["passed_checks"]
    assert "action_valid" in validation["passed_checks"]


def test_generation_improvement_loop_summarizes_and_textualizes_decision():
    loop = GenerationImprovementLoop()

    decision = loop.decide_next_step(
        source_id="loop_source",
        comparison_report=targeted_comparison(),
        revision_plan=build_revision_plan(),
        current_iteration=1,
        max_iterations=3,
    )["generation_improvement_loop_decision"]

    summary = loop.summarize_loop_decision(decision=decision)
    text = loop.build_loop_decision_text(decision=decision)["loop_decision_text"]

    assert summary["success"] is True
    assert summary["summary"]["source_id"] == "loop_source"
    assert "Generation Improvement Loop Decision" in text
    assert "Required Actions" in text

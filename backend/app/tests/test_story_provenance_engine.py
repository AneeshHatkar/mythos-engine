from backend.app.engines.story_generation.story_provenance_engine import StoryProvenanceEngine
from backend.app.schemas.story_generation import (
    DraftComparisonReport,
    GenerationImprovementLoopDecision,
    OriginalityCopyRiskReport,
    StoryAntiGenericityReport,
    StoryContinuityValidationReport,
    StoryQualityScoreReport,
    StoryRevisionPlan,
)


def build_quality_report():
    return StoryQualityScoreReport(
        quality_report_id="quality_provenance",
        source_id="provenance_source",
        overall_score=0.82,
        readiness_level="ready",
        anti_generic_score=0.80,
    )


def build_anti_genericity_report(risk="medium"):
    return StoryAntiGenericityReport(
        report_id="anti_provenance",
        draft_id="provenance_source",
        anti_genericity_report_id="anti_provenance",
        source_id="provenance_source",
        overall_anti_genericity_score=0.78,
        genericity_risk_level=risk,
    )


def build_continuity_report(valid=True):
    return StoryContinuityValidationReport(
        continuity_report_id="continuity_provenance",
        source_id="provenance_source",
        valid=valid,
        continuity_score=0.86 if valid else 0.30,
        readiness_level="ready" if valid else "blocked",
        checked_character_ids=["char_kael"],
        checked_secret_ids=["secret_seren_source"],
        checked_causal_ids=["cause_trial_reveal"],
        checked_world_details=["Oath Court"],
    )


def build_originality_report(safe=True):
    return OriginalityCopyRiskReport(
        originality_report_id="originality_provenance",
        source_id="provenance_source",
        safe_for_export=safe,
        overall_originality_score=0.81 if safe else 0.25,
        copy_risk_level="low" if safe else "critical",
        approved_original_elements=["Specific world detail exists: Oath Court."],
    )


def build_revision_plan():
    return StoryRevisionPlan(
        revision_plan_id="revision_provenance",
        source_id="provenance_source",
        revision_mode="targeted",
        overall_revision_priority="medium",
        protected_elements=[
            {"element_id": "protect_character_char_kael", "element_type": "character", "value": "char_kael"},
            {"element_id": "protect_secret_secret_seren_source", "element_type": "secret", "value": "secret_seren_source"},
        ],
        rewrite_order=[
            {"step_number": 1, "task_id": "task_1", "task_type": "quality_revision", "priority": "medium"}
        ],
    )


def build_comparison_report(approved=True):
    return DraftComparisonReport(
        comparison_report_id="comparison_provenance",
        source_id="provenance_source",
        original_draft_id="draft_original",
        revised_draft_id="draft_revised",
        approved=approved,
        improvement_score=0.70 if approved else 0.20,
        regression_risk_score=0.05 if approved else 0.70,
        preserved_elements=[
            {"element_id": "protect_character_char_kael", "element_type": "character", "value": "char_kael"}
        ],
        regression_flags=[] if approved else [
            {"flag_id": "regression_quality", "flag_type": "quality_regression", "severity": "high", "description": "Quality regressed."}
        ],
    )


def build_loop_decision(approved=True):
    return GenerationImprovementLoopDecision(
        loop_decision_id="loop_provenance",
        source_id="provenance_source",
        current_iteration=1,
        max_iterations=3,
        action="approve_and_handoff" if approved else "blocked_until_manual_review",
        approved_for_handoff=approved,
        stop_loop=True,
        improvement_status="approved" if approved else "blocked",
        decision_reason="Approved." if approved else "Blocked.",
        next_priority="low" if approved else "critical",
    )


def test_story_provenance_engine_builds_approved_record():
    engine = StoryProvenanceEngine()

    result = engine.build_provenance_record(
        source_id="provenance_source",
        draft_id="draft_revised",
        generated_text="char_kael protects secret_seren_source in the Oath Court.",
        input_references=[{"source_id": "fixture_input", "policy": "synthetic"}],
        output_references=[{"artifact_id": "draft_revised", "artifact_type": "chapter"}],
        quality_report=build_quality_report(),
        anti_genericity_report=build_anti_genericity_report(),
        continuity_report=build_continuity_report(),
        originality_report=build_originality_report(),
        revision_plan=build_revision_plan(),
        comparison_report=build_comparison_report(),
        loop_decision=build_loop_decision(),
    )

    record = result["story_provenance_record"]

    assert result["success"] is True
    assert record.provenance_record_id == "story_provenance_provenance_source_draft_revised"
    assert record.approved_for_memory_update is True
    assert record.approved_for_export is True
    assert record.provenance_status == "approved"
    assert record.engine_trace
    assert record.memory_update_candidates
    assert record.downstream_constraints


def test_story_provenance_engine_blocks_risky_record():
    engine = StoryProvenanceEngine()

    record = engine.build_provenance_record(
        source_id="provenance_source",
        draft_id="draft_risky",
        generated_text="Risky draft.",
        quality_report=build_quality_report(),
        anti_genericity_report=build_anti_genericity_report(risk="critical"),
        continuity_report=build_continuity_report(valid=False),
        originality_report=build_originality_report(safe=False),
        revision_plan=build_revision_plan(),
        comparison_report=build_comparison_report(approved=False),
        loop_decision=build_loop_decision(approved=False),
    )["story_provenance_record"]

    assert record.approved_for_memory_update is False
    assert record.approved_for_export is False
    assert record.provenance_status == "blocked"
    assert record.risk_snapshot
    assert record.warnings


def test_story_provenance_engine_captures_memory_candidates():
    engine = StoryProvenanceEngine()

    record = engine.build_provenance_record(
        source_id="provenance_source",
        draft_id="draft_revised",
        generated_text="char_kael protects secret_seren_source in the Oath Court.",
        continuity_report=build_continuity_report(),
        originality_report=build_originality_report(),
        comparison_report=build_comparison_report(),
        loop_decision=build_loop_decision(),
        story_context={
            "extra_memory_candidates": [
                {"candidate_id": "memory_custom_world_weather", "candidate_type": "world_state", "value": "storm season"}
            ]
        },
    )["story_provenance_record"]

    candidate_ids = {item["candidate_id"] for item in record.memory_update_candidates}

    assert "memory_character_char_kael" in candidate_ids
    assert "memory_secret_secret_seren_source" in candidate_ids
    assert "memory_world_oath_court" in candidate_ids
    assert "memory_custom_world_weather" in candidate_ids


def test_story_provenance_engine_validates_record():
    engine = StoryProvenanceEngine()

    record = engine.build_provenance_record(
        source_id="provenance_source",
        draft_id="draft_revised",
        generated_text="char_kael protects secret_seren_source in the Oath Court.",
        quality_report=build_quality_report(),
        continuity_report=build_continuity_report(),
        originality_report=build_originality_report(),
        comparison_report=build_comparison_report(),
        loop_decision=build_loop_decision(),
    )["story_provenance_record"]

    validation = engine.validate_provenance_record(record=record)

    assert validation["success"] is True
    assert validation["valid"] is True
    assert "provenance_record_id_present" in validation["passed_checks"]
    assert "engine_trace_present" in validation["passed_checks"]


def test_story_provenance_engine_summarizes_record():
    engine = StoryProvenanceEngine()

    record = engine.build_provenance_record(
        source_id="provenance_source",
        draft_id="draft_revised",
        generated_text="char_kael protects secret_seren_source in the Oath Court.",
        quality_report=build_quality_report(),
        continuity_report=build_continuity_report(),
        originality_report=build_originality_report(),
        comparison_report=build_comparison_report(),
        loop_decision=build_loop_decision(),
    )["story_provenance_record"]

    summary = engine.summarize_provenance_record(record=record)

    assert summary["success"] is True
    assert summary["summary"]["source_id"] == "provenance_source"
    assert "engine_trace_count" in summary["summary"]


def test_story_provenance_engine_builds_text():
    engine = StoryProvenanceEngine()

    record = engine.build_provenance_record(
        source_id="provenance_source",
        draft_id="draft_revised",
        generated_text="char_kael protects secret_seren_source in the Oath Court.",
        quality_report=build_quality_report(),
        continuity_report=build_continuity_report(),
        originality_report=build_originality_report(),
        comparison_report=build_comparison_report(),
        loop_decision=build_loop_decision(),
    )["story_provenance_record"]

    text = engine.build_provenance_text(record=record)["provenance_text"]

    assert "Story Provenance Record" in text
    assert "Engine Trace" in text
    assert "Memory Update Candidates" in text

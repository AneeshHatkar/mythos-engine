from backend.app.engines.story_generation.story_generation_orchestrator import StoryGenerationOrchestrator
from backend.app.schemas.story_generation import (
    DraftComparisonReport,
    GeneratedStoryDeltaReport,
    GenerationContract,
    GenerationImprovementLoopDecision,
    OriginalityCopyRiskReport,
    StoryAntiGenericityReport,
    StoryContinuityValidationReport,
    StoryMemoryUpdateContract,
    StoryProvenanceRecord,
    StoryQualityScoreReport,
    StoryRevisionPlan,
)


def build_contract():
    return GenerationContract(
        generation_contract_id="contract_orchestrator",
        contract_id="contract_orchestrator",
        story_intent_id="intent_orchestrator",
        source_id="orchestrator_source",
        target_format="chapter",
        generation_mode="draft",
        handoff_reference={
            "handoff_id": "handoff_orchestrator",
            "simulation_id": "simulation_orchestrator",
            "source": "test_story_generation_orchestrator",
            "status": "available",
        },
    )


def build_quality():
    return StoryQualityScoreReport(
        quality_report_id="quality_orchestrator",
        source_id="orchestrator_source",
        overall_score=0.82,
        readiness_level="ready",
        anti_generic_score=0.80,
    )


def build_anti():
    return StoryAntiGenericityReport(
        report_id="anti_orchestrator",
        draft_id="orchestrator_source",
        anti_genericity_report_id="anti_orchestrator",
        source_id="orchestrator_source",
        overall_anti_genericity_score=0.80,
        genericity_risk_level="medium",
    )


def build_continuity(valid=True):
    return StoryContinuityValidationReport(
        continuity_report_id="continuity_orchestrator",
        source_id="orchestrator_source",
        valid=valid,
        continuity_score=0.86 if valid else 0.25,
        readiness_level="ready" if valid else "blocked",
    )


def build_originality(safe=True):
    return OriginalityCopyRiskReport(
        originality_report_id="originality_orchestrator",
        source_id="orchestrator_source",
        safe_for_export=safe,
        overall_originality_score=0.82 if safe else 0.20,
        copy_risk_level="low" if safe else "critical",
    )


def build_revision():
    return StoryRevisionPlan(
        revision_plan_id="revision_orchestrator",
        source_id="orchestrator_source",
        revision_mode="targeted",
        overall_revision_priority="medium",
    )


def build_comparison(approved=True):
    return DraftComparisonReport(
        comparison_report_id="comparison_orchestrator",
        source_id="orchestrator_source",
        original_draft_id="draft_original",
        revised_draft_id="draft_revised",
        approved=approved,
        improvement_score=0.70 if approved else 0.20,
        regression_risk_score=0.05 if approved else 0.70,
    )


def build_loop(approved=True):
    return GenerationImprovementLoopDecision(
        loop_decision_id="loop_orchestrator",
        source_id="orchestrator_source",
        current_iteration=1,
        max_iterations=3,
        action="approve_and_handoff" if approved else "blocked_until_manual_review",
        approved_for_handoff=approved,
        stop_loop=True,
        improvement_status="approved" if approved else "blocked",
        next_priority="low" if approved else "critical",
    )


def build_provenance(approved=True):
    return StoryProvenanceRecord(
        provenance_id="provenance_orchestrator",
        provenance_record_id="provenance_orchestrator",
        source_id="orchestrator_source",
        draft_id="draft_revised",
        provenance_status="approved" if approved else "blocked",
        approved_for_memory_update=approved,
        approved_for_export=approved,
    )


def build_delta():
    return GeneratedStoryDeltaReport(
        delta_report_id="delta_orchestrator",
        source_id="orchestrator_source",
        draft_id="draft_revised",
        memory_update_candidates=[
            {"candidate_id": "memory_char", "candidate_type": "character_state", "value": "char_kael"}
        ],
    )


def build_memory_contract(approved=True):
    return StoryMemoryUpdateContract(
        memory_update_contract_id="memory_contract_orchestrator",
        memory_contract_id="memory_contract_orchestrator",
        source_id="orchestrator_source",
        draft_id="draft_revised",
        approved_for_apply=approved,
        apply_mode="auto_apply" if approved else "blocked",
        contract_status="approved" if approved else "blocked",
    )


def test_story_generation_orchestrator_builds_ready_report():
    orchestrator = StoryGenerationOrchestrator()

    result = orchestrator.orchestrate_generation_state(
        source_id="orchestrator_source",
        request_id="request_001",
        generation_contract=build_contract(),
        quality_report=build_quality(),
        anti_genericity_report=build_anti(),
        continuity_report=build_continuity(),
        originality_report=build_originality(),
        revision_plan=build_revision(),
        comparison_report=build_comparison(),
        loop_decision=build_loop(),
        provenance_record=build_provenance(),
        delta_report=build_delta(),
        memory_update_contract=build_memory_contract(),
        story_context={"known_character_ids": ["char_kael"]},
    )

    report = result["story_generation_orchestration_report"]

    assert result["success"] is True
    assert report.orchestration_status == "ready"
    assert report.ready_for_export is True
    assert report.ready_for_memory_apply is True
    assert not report.missing_inputs
    assert report.final_handoff_package


def test_story_generation_orchestrator_detects_missing_inputs():
    orchestrator = StoryGenerationOrchestrator()

    report = orchestrator.orchestrate_generation_state(
        source_id="orchestrator_source",
        request_id="request_missing",
        generation_contract=build_contract(),
        quality_report=build_quality(),
    )["story_generation_orchestration_report"]

    assert report.orchestration_status in {"incomplete", "blocked"}
    assert report.missing_inputs
    assert report.blocked_reasons
    assert report.ready_for_export is False


def test_story_generation_orchestrator_blocks_failed_risk_gate():
    orchestrator = StoryGenerationOrchestrator()

    report = orchestrator.orchestrate_generation_state(
        source_id="orchestrator_source",
        request_id="request_blocked",
        generation_contract=build_contract(),
        quality_report=build_quality(),
        anti_genericity_report=build_anti(),
        continuity_report=build_continuity(),
        originality_report=build_originality(safe=False),
        revision_plan=build_revision(),
        comparison_report=build_comparison(approved=False),
        loop_decision=build_loop(approved=False),
        provenance_record=build_provenance(approved=False),
        delta_report=build_delta(),
        memory_update_contract=build_memory_contract(approved=False),
    )["story_generation_orchestration_report"]

    assert report.orchestration_status == "blocked"
    assert report.ready_for_export is False
    assert any(item["reason_type"] == "risk_gate" for item in report.blocked_reasons)


def test_story_generation_orchestrator_validates_report():
    orchestrator = StoryGenerationOrchestrator()

    report = orchestrator.orchestrate_generation_state(
        source_id="orchestrator_source",
        request_id="request_001",
        generation_contract=build_contract(),
        quality_report=build_quality(),
        anti_genericity_report=build_anti(),
        continuity_report=build_continuity(),
        originality_report=build_originality(),
        revision_plan=build_revision(),
        comparison_report=build_comparison(),
        loop_decision=build_loop(),
        provenance_record=build_provenance(),
        delta_report=build_delta(),
        memory_update_contract=build_memory_contract(),
    )["story_generation_orchestration_report"]

    validation = orchestrator.validate_orchestration_report(report=report)

    assert validation["success"] is True
    assert validation["valid"] is True
    assert "orchestration_report_id_present" in validation["passed_checks"]
    assert "pipeline_stage_results_present" in validation["passed_checks"]


def test_story_generation_orchestrator_summarizes_report():
    orchestrator = StoryGenerationOrchestrator()

    report = orchestrator.orchestrate_generation_state(
        source_id="orchestrator_source",
        request_id="request_001",
        generation_contract=build_contract(),
        quality_report=build_quality(),
        anti_genericity_report=build_anti(),
        continuity_report=build_continuity(),
        originality_report=build_originality(),
        revision_plan=build_revision(),
        comparison_report=build_comparison(),
        loop_decision=build_loop(),
        provenance_record=build_provenance(),
        delta_report=build_delta(),
        memory_update_contract=build_memory_contract(),
    )["story_generation_orchestration_report"]

    summary = orchestrator.summarize_orchestration_report(report=report)

    assert summary["success"] is True
    assert summary["summary"]["source_id"] == "orchestrator_source"
    assert summary["summary"]["orchestration_status"] == "ready"


def test_story_generation_orchestrator_builds_text():
    orchestrator = StoryGenerationOrchestrator()

    report = orchestrator.orchestrate_generation_state(
        source_id="orchestrator_source",
        request_id="request_001",
        generation_contract=build_contract(),
        quality_report=build_quality(),
        anti_genericity_report=build_anti(),
        continuity_report=build_continuity(),
        originality_report=build_originality(),
        revision_plan=build_revision(),
        comparison_report=build_comparison(),
        loop_decision=build_loop(),
        provenance_record=build_provenance(),
        delta_report=build_delta(),
        memory_update_contract=build_memory_contract(),
    )["story_generation_orchestration_report"]

    text = orchestrator.build_orchestration_text(report=report)["orchestration_text"]

    assert "Story Generation Orchestration Report" in text
    assert "Pipeline Stages" in text
    assert "Next Actions" in text

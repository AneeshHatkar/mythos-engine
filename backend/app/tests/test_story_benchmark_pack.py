from backend.app.engines.story_generation.story_benchmark_pack import StoryBenchmarkPackBuilder
from backend.app.schemas.story_generation import (
    GeneratedStoryDeltaReport,
    StoryExportPackage,
    StoryGenerationOrchestrationReport,
    StoryMemoryUpdateContract,
    StoryProvenanceRecord,
)


def build_orchestration(ready=True):
    return StoryGenerationOrchestrationReport(
        orchestration_report_id="orchestration_benchmark",
        source_id="benchmark_source",
        request_id="request_benchmark",
        orchestration_status="ready" if ready else "blocked",
        ready_for_export=ready,
        ready_for_memory_apply=ready,
    )


def build_provenance(approved=True):
    return StoryProvenanceRecord(
        provenance_id="provenance_benchmark",
        provenance_record_id="provenance_benchmark",
        source_id="benchmark_source",
        draft_id="draft_benchmark",
        provenance_status="approved" if approved else "blocked",
        approved_for_memory_update=approved,
        approved_for_export=approved,
    )


def build_delta(with_candidates=True):
    return GeneratedStoryDeltaReport(
        delta_report_id="delta_benchmark",
        source_id="benchmark_source",
        draft_id="draft_benchmark",
        memory_update_candidates=[
            {"candidate_id": "memory_char", "candidate_type": "character_state", "value": "char_kael"}
        ] if with_candidates else [],
    )


def build_memory_contract(approved=True):
    return StoryMemoryUpdateContract(
        memory_update_contract_id="memory_benchmark",
        memory_contract_id="memory_benchmark",
        source_id="benchmark_source",
        draft_id="draft_benchmark",
        approved_for_apply=approved,
        apply_mode="auto_apply" if approved else "blocked",
        contract_status="approved" if approved else "blocked",
    )


def build_export_package(approved=True):
    return StoryExportPackage(
        export_package_id="export_benchmark",
        source_id="benchmark_source",
        draft_id="draft_benchmark",
        request_id="request_benchmark",
        export_status="approved" if approved else "staged_blocked",
        approved_for_export=approved,
        story_payload={"title": "The Oath Court", "text": "char_kael enters."},
        orchestration_snapshot={"available": True},
        provenance_snapshot={"available": True},
        delta_snapshot={"available": True},
        memory_contract_snapshot={"available": True},
        blocked_reasons=[] if approved else [
            {"reason_id": "blocked_export", "reason_type": "export", "severity": "critical", "description": "Not approved."}
        ],
    )


def test_story_benchmark_pack_builds_passed_pack():
    builder = StoryBenchmarkPackBuilder()

    result = builder.build_benchmark_pack(
        source_id="benchmark_source",
        request_id="request_benchmark",
        draft_id="draft_benchmark",
        story_payload={"title": "The Oath Court", "text": "char_kael enters."},
        export_package=build_export_package(True),
        orchestration_report=build_orchestration(True),
        provenance_record=build_provenance(True),
        delta_report=build_delta(True),
        memory_update_contract=build_memory_contract(True),
    )

    pack = result["story_benchmark_pack"]

    assert result["success"] is True
    assert pack.benchmark_pack_id == "story_benchmark_benchmark_source_draft_benchmark_request_benchmark"
    assert pack.benchmark_results
    assert pack.score_summary["failed_count"] == 0
    assert pack.readiness_summary["ready_for_publish"] is True
    assert pack.readiness_summary["ready_for_memory"] is True


def test_story_benchmark_pack_catches_blocked_artifacts():
    builder = StoryBenchmarkPackBuilder()

    pack = builder.build_benchmark_pack(
        source_id="benchmark_source",
        request_id="request_benchmark",
        draft_id="draft_benchmark",
        story_payload={},
        export_package=build_export_package(False),
        orchestration_report=build_orchestration(False),
        provenance_record=build_provenance(False),
        delta_report=build_delta(False),
        memory_update_contract=build_memory_contract(False),
    )["story_benchmark_pack"]

    assert pack.score_summary["failed_count"] > 0
    assert pack.readiness_summary["ready_for_publish"] is False
    assert pack.recommended_actions
    assert pack.warnings


def test_story_benchmark_pack_accepts_custom_cases():
    builder = StoryBenchmarkPackBuilder()

    pack = builder.build_benchmark_pack(
        source_id="benchmark_source",
        request_id="request_benchmark",
        draft_id="draft_benchmark",
        story_payload={"title": "The Oath Court"},
        export_package=build_export_package(True),
        orchestration_report=build_orchestration(True),
        provenance_record=build_provenance(True),
        delta_report=build_delta(True),
        memory_update_contract=build_memory_contract(True),
        custom_cases=[
            {
                "case_id": "custom_case_style",
                "case_name": "custom_style_case",
                "case_type": "style",
                "priority": "medium",
                "expected_status": "passed",
                "description": "Style custom check passed.",
            }
        ],
    )["story_benchmark_pack"]

    case_ids = {case["case_id"] for case in pack.benchmark_cases}
    result_case_ids = {result["case_id"] for result in pack.benchmark_results}

    assert "custom_case_style" in case_ids
    assert "custom_case_style" in result_case_ids


def test_story_benchmark_pack_validates_pack():
    builder = StoryBenchmarkPackBuilder()

    pack = builder.build_benchmark_pack(
        source_id="benchmark_source",
        request_id="request_benchmark",
        draft_id="draft_benchmark",
        story_payload={"title": "The Oath Court"},
        export_package=build_export_package(True),
        orchestration_report=build_orchestration(True),
        provenance_record=build_provenance(True),
        delta_report=build_delta(True),
        memory_update_contract=build_memory_contract(True),
    )["story_benchmark_pack"]

    validation = builder.validate_benchmark_pack(pack=pack)

    assert validation["success"] is True
    assert validation["valid"] is True
    assert "benchmark_pack_id_present" in validation["passed_checks"]
    assert "benchmark_results_present" in validation["passed_checks"]


def test_story_benchmark_pack_summarizes_pack():
    builder = StoryBenchmarkPackBuilder()

    pack = builder.build_benchmark_pack(
        source_id="benchmark_source",
        request_id="request_benchmark",
        draft_id="draft_benchmark",
        story_payload={"title": "The Oath Court"},
        export_package=build_export_package(True),
        orchestration_report=build_orchestration(True),
        provenance_record=build_provenance(True),
        delta_report=build_delta(True),
        memory_update_contract=build_memory_contract(True),
    )["story_benchmark_pack"]

    summary = builder.summarize_benchmark_pack(pack=pack)

    assert summary["success"] is True
    assert summary["summary"]["source_id"] == "benchmark_source"
    assert "overall_score" in summary["summary"]


def test_story_benchmark_pack_builds_text():
    builder = StoryBenchmarkPackBuilder()

    pack = builder.build_benchmark_pack(
        source_id="benchmark_source",
        request_id="request_benchmark",
        draft_id="draft_benchmark",
        story_payload={"title": "The Oath Court"},
        export_package=build_export_package(True),
        orchestration_report=build_orchestration(True),
        provenance_record=build_provenance(True),
        delta_report=build_delta(True),
        memory_update_contract=build_memory_contract(True),
    )["story_benchmark_pack"]

    text = builder.build_benchmark_text(pack=pack)["benchmark_text"]

    assert "Story Benchmark Pack" in text
    assert "Benchmark Results" in text
    assert "Recommended Actions" in text

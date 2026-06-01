from backend.app.engines.story_generation.learning_feedback_adapter import LearningFeedbackAdapter
from backend.app.schemas.story_generation import (
    StoryBenchmarkPack,
    StoryExportPackage,
    StoryGenerationOrchestrationReport,
    StorySmokeTestReport,
)


def build_orchestration(ready=True):
    return StoryGenerationOrchestrationReport(
        orchestration_report_id="orchestration_feedback",
        source_id="feedback_source",
        request_id="request_feedback",
        orchestration_status="ready" if ready else "blocked",
        ready_for_export=ready,
        ready_for_memory_apply=ready,
        blocked_reasons=[] if ready else [
            {"reason_id": "blocked_risk", "reason_type": "risk_gate", "severity": "critical", "description": "Risk failed."}
        ],
    )


def build_export(approved=True):
    return StoryExportPackage(
        export_package_id="export_feedback",
        source_id="feedback_source",
        draft_id="draft_feedback",
        request_id="request_feedback",
        export_status="approved" if approved else "staged_blocked",
        approved_for_export=approved,
        blocked_reasons=[] if approved else [
            {"reason_id": "blocked_export", "reason_type": "export_gate", "severity": "critical", "description": "Export failed."}
        ],
    )


def build_benchmark(passed=True):
    return StoryBenchmarkPack(
        benchmark_pack_id="benchmark_feedback",
        source_id="feedback_source",
        request_id="request_feedback",
        draft_id="draft_feedback",
        benchmark_status="passed" if passed else "failed_critical",
        benchmark_results=[
            {
                "case_id": "case_story_payload_present",
                "case_name": "story_payload_present",
                "case_type": "payload",
                "priority": "high",
                "status": "passed" if passed else "failed",
                "score": 1.0 if passed else 0.0,
                "message": "Payload checked.",
            }
        ],
        score_summary={
            "overall_score": 1.0 if passed else 0.2,
            "critical_failed_count": 0 if passed else 1,
            "failed_count": 0 if passed else 1,
            "warning_count": 0,
        },
        readiness_summary={
            "ready_for_publish": passed,
            "ready_for_memory": passed,
        },
    )


def build_smoke(passed=True):
    return StorySmokeTestReport(
        smoke_test_report_id="smoke_feedback",
        source_id="feedback_source",
        request_id="request_feedback",
        draft_id="draft_feedback",
        smoke_status="passed" if passed else "failed",
        passed=passed,
        smoke_results=[
            {
                "case_id": "smoke_orchestration_present",
                "case_name": "orchestration_present",
                "case_type": "artifact",
                "priority": "critical",
                "status": "passed" if passed else "failed",
                "message": "Smoke checked.",
            }
        ],
        readiness_summary={
            "smoke_passed": passed,
            "export_ready": passed,
            "benchmark_ready": passed,
        },
        failure_summary={
            "passed_count": 1 if passed else 0,
            "failed_count": 0 if passed else 1,
            "warning_count": 0,
        },
    )


def test_learning_feedback_adapter_builds_approved_package():
    adapter = LearningFeedbackAdapter()

    result = adapter.build_learning_feedback_package(
        source_id="feedback_source",
        request_id="request_feedback",
        draft_id="draft_feedback",
        story_payload={"title": "The Oath Court", "text": "char_kael enters."},
        orchestration_report=build_orchestration(True),
        export_package=build_export(True),
        benchmark_pack=build_benchmark(True),
        smoke_test_report=build_smoke(True),
        story_context={"known_character_ids": ["char_kael"]},
    )

    package = result["learning_feedback_package"]

    assert result["success"] is True
    assert package.learning_feedback_id == "learning_feedback_feedback_source_draft_feedback_request_feedback"
    assert package.approved_for_learning is True
    assert package.feedback_rows
    assert package.training_signal_candidates
    assert package.dataset_manifest


def test_learning_feedback_adapter_stages_failed_package():
    adapter = LearningFeedbackAdapter()

    package = adapter.build_learning_feedback_package(
        source_id="feedback_source",
        request_id="request_feedback",
        draft_id="draft_feedback",
        story_payload={},
        orchestration_report=build_orchestration(False),
        export_package=build_export(False),
        benchmark_pack=build_benchmark(False),
        smoke_test_report=build_smoke(False),
    )["learning_feedback_package"]

    assert package.approved_for_learning is False
    assert package.feedback_status == "staged"
    assert package.recommended_actions
    assert package.warnings


def test_learning_feedback_adapter_respects_human_exclusion():
    adapter = LearningFeedbackAdapter()

    package = adapter.build_learning_feedback_package(
        source_id="feedback_source",
        request_id="request_feedback",
        draft_id="draft_feedback",
        story_payload={"title": "The Oath Court"},
        orchestration_report=build_orchestration(True),
        export_package=build_export(True),
        benchmark_pack=build_benchmark(True),
        smoke_test_report=build_smoke(True),
        human_feedback={
            "label": "human_rejected",
            "score": 0.1,
            "confidence": 1.0,
            "exclude_from_learning": True,
        },
    )["learning_feedback_package"]

    assert package.approved_for_learning is False
    assert any(action["action_id"] == "respect_human_exclusion" for action in package.recommended_actions)


def test_learning_feedback_adapter_validates_package():
    adapter = LearningFeedbackAdapter()

    package = adapter.build_learning_feedback_package(
        source_id="feedback_source",
        request_id="request_feedback",
        draft_id="draft_feedback",
        story_payload={"title": "The Oath Court"},
        orchestration_report=build_orchestration(True),
        export_package=build_export(True),
        benchmark_pack=build_benchmark(True),
        smoke_test_report=build_smoke(True),
    )["learning_feedback_package"]

    validation = adapter.validate_learning_feedback_package(package=package)

    assert validation["success"] is True
    assert validation["valid"] is True
    assert "learning_feedback_id_present" in validation["passed_checks"]
    assert "feedback_rows_present" in validation["passed_checks"]


def test_learning_feedback_adapter_summarizes_package():
    adapter = LearningFeedbackAdapter()

    package = adapter.build_learning_feedback_package(
        source_id="feedback_source",
        request_id="request_feedback",
        draft_id="draft_feedback",
        story_payload={"title": "The Oath Court"},
        orchestration_report=build_orchestration(True),
        export_package=build_export(True),
        benchmark_pack=build_benchmark(True),
        smoke_test_report=build_smoke(True),
    )["learning_feedback_package"]

    summary = adapter.summarize_learning_feedback_package(package=package)

    assert summary["success"] is True
    assert summary["summary"]["source_id"] == "feedback_source"
    assert "training_signal_count" in summary["summary"]


def test_learning_feedback_adapter_builds_text():
    adapter = LearningFeedbackAdapter()

    package = adapter.build_learning_feedback_package(
        source_id="feedback_source",
        request_id="request_feedback",
        draft_id="draft_feedback",
        story_payload={"title": "The Oath Court"},
        orchestration_report=build_orchestration(True),
        export_package=build_export(True),
        benchmark_pack=build_benchmark(True),
        smoke_test_report=build_smoke(True),
    )["learning_feedback_package"]

    text = adapter.build_learning_feedback_text(package=package)["learning_feedback_text"]

    assert "Learning Feedback Package" in text
    assert "Feedback Summary" in text
    assert "Training Signal Candidates" in text

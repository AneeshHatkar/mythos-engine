from backend.app.engines.story_generation.story_smoke_test import StorySmokeTestRunner
from backend.app.schemas.story_generation import StoryBenchmarkPack, StoryExportPackage, StoryGenerationOrchestrationReport


def build_orchestration(ready=True):
    return StoryGenerationOrchestrationReport(
        orchestration_report_id="orchestration_smoke",
        source_id="smoke_source",
        request_id="request_smoke",
        orchestration_status="ready" if ready else "blocked",
        ready_for_export=ready,
        ready_for_memory_apply=ready,
        blocked_reasons=[] if ready else [
            {"reason_id": "blocked_risk", "reason_type": "risk_gate", "severity": "critical", "description": "Risk failed."}
        ],
    )


def build_export(approved=True):
    return StoryExportPackage(
        export_package_id="export_smoke",
        source_id="smoke_source",
        draft_id="draft_smoke",
        request_id="request_smoke",
        export_status="approved" if approved else "staged_blocked",
        approved_for_export=approved,
        blocked_reasons=[] if approved else [
            {"reason_id": "blocked_export", "reason_type": "export_gate", "severity": "critical", "description": "Export failed."}
        ],
    )


def build_benchmark(passed=True):
    return StoryBenchmarkPack(
        benchmark_pack_id="benchmark_smoke",
        source_id="smoke_source",
        request_id="request_smoke",
        draft_id="draft_smoke",
        benchmark_status="passed" if passed else "failed_critical",
        score_summary={
            "overall_score": 1.0 if passed else 0.2,
            "critical_failed_count": 0 if passed else 1,
            "failed_count": 0 if passed else 2,
            "warning_count": 0,
        },
        readiness_summary={
            "ready_for_publish": passed,
            "ready_for_memory": passed,
        },
    )


def test_story_smoke_test_runner_passes_clean_pipeline():
    runner = StorySmokeTestRunner()

    result = runner.run_smoke_test(
        source_id="smoke_source",
        request_id="request_smoke",
        draft_id="draft_smoke",
        orchestration_report=build_orchestration(True),
        export_package=build_export(True),
        benchmark_pack=build_benchmark(True),
        story_context={"known_character_ids": ["char_kael"]},
    )

    report = result["story_smoke_test_report"]

    assert result["success"] is True
    assert report.passed is True
    assert report.smoke_status == "passed"
    assert report.failure_summary["failed_count"] == 0
    assert report.readiness_summary["smoke_passed"] is True


def test_story_smoke_test_runner_fails_missing_artifacts():
    runner = StorySmokeTestRunner()

    report = runner.run_smoke_test(
        source_id="smoke_source",
        request_id="request_smoke",
        draft_id="draft_smoke",
    )["story_smoke_test_report"]

    assert report.passed is False
    assert report.smoke_status == "failed"
    assert report.failure_summary["failed_count"] > 0
    assert report.recommended_actions


def test_story_smoke_test_runner_warns_for_blocked_explicit_state():
    runner = StorySmokeTestRunner()

    report = runner.run_smoke_test(
        source_id="smoke_source",
        request_id="request_smoke",
        draft_id="draft_smoke",
        orchestration_report=build_orchestration(False),
        export_package=build_export(False),
        benchmark_pack=build_benchmark(False),
        story_context={"known_character_ids": ["char_kael"]},
    )["story_smoke_test_report"]

    assert report.passed is False
    assert report.warnings
    assert any(action["action_id"] == "do_not_finalize_chunk5" for action in report.recommended_actions)


def test_story_smoke_test_runner_validates_report():
    runner = StorySmokeTestRunner()

    report = runner.run_smoke_test(
        source_id="smoke_source",
        request_id="request_smoke",
        draft_id="draft_smoke",
        orchestration_report=build_orchestration(True),
        export_package=build_export(True),
        benchmark_pack=build_benchmark(True),
        story_context={"known_character_ids": ["char_kael"]},
    )["story_smoke_test_report"]

    validation = runner.validate_smoke_test_report(report=report)

    assert validation["success"] is True
    assert validation["valid"] is True
    assert "smoke_test_report_id_present" in validation["passed_checks"]
    assert "smoke_results_present" in validation["passed_checks"]


def test_story_smoke_test_runner_summarizes_report():
    runner = StorySmokeTestRunner()

    report = runner.run_smoke_test(
        source_id="smoke_source",
        request_id="request_smoke",
        draft_id="draft_smoke",
        orchestration_report=build_orchestration(True),
        export_package=build_export(True),
        benchmark_pack=build_benchmark(True),
        story_context={"known_character_ids": ["char_kael"]},
    )["story_smoke_test_report"]

    summary = runner.summarize_smoke_test_report(report=report)

    assert summary["success"] is True
    assert summary["summary"]["source_id"] == "smoke_source"
    assert summary["summary"]["passed"] is True


def test_story_smoke_test_runner_builds_text():
    runner = StorySmokeTestRunner()

    report = runner.run_smoke_test(
        source_id="smoke_source",
        request_id="request_smoke",
        draft_id="draft_smoke",
        orchestration_report=build_orchestration(True),
        export_package=build_export(True),
        benchmark_pack=build_benchmark(True),
        story_context={"known_character_ids": ["char_kael"]},
    )["story_smoke_test_report"]

    text = runner.build_smoke_test_text(report=report)["smoke_test_text"]

    assert "Story Smoke Test Report" in text
    assert "Smoke Results" in text
    assert "Recommended Actions" in text

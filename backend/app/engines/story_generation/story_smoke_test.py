from __future__ import annotations

from typing import Any, Dict, List

from backend.app.schemas.story_generation import (
    StoryBenchmarkPack,
    StoryExportPackage,
    StoryGenerationOrchestrationReport,
    StorySmokeTestReport,
)


class StorySmokeTestRunner:
    """Runs a deterministic smoke test over late Chunk 5 artifacts.

    Locked Chunk 5.46. This is intentionally lightweight: it does not generate
    creative prose. It confirms that the orchestration/export/benchmark artifacts
    are coherent enough for final Chunk 1-5 verification.
    """

    engine_name = "story_generation.story_smoke_test"

    def run_smoke_test(
        self,
        *,
        source_id: str,
        request_id: str = "",
        draft_id: str = "",
        orchestration_report: StoryGenerationOrchestrationReport | None = None,
        export_package: StoryExportPackage | None = None,
        benchmark_pack: StoryBenchmarkPack | None = None,
        story_context: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        story_context = story_context or {}

        smoke_cases = self._smoke_cases()
        smoke_results = self._smoke_results(
            smoke_cases=smoke_cases,
            orchestration_report=orchestration_report,
            export_package=export_package,
            benchmark_pack=benchmark_pack,
            story_context=story_context,
        )

        artifact_summary = self._artifact_summary(
            orchestration_report=orchestration_report,
            export_package=export_package,
            benchmark_pack=benchmark_pack,
        )
        readiness_summary = self._readiness_summary(
            smoke_results=smoke_results,
            orchestration_report=orchestration_report,
            export_package=export_package,
            benchmark_pack=benchmark_pack,
        )
        failure_summary = self._failure_summary(smoke_results=smoke_results)
        recommended_actions = self._recommended_actions(
            smoke_results=smoke_results,
            readiness_summary=readiness_summary,
        )

        passed = readiness_summary["smoke_passed"]

        report = StorySmokeTestReport(
            smoke_test_report_id=f"story_smoke_test_{source_id}_{draft_id or 'draft'}_{request_id or 'default'}",
            source_id=source_id,
            request_id=request_id,
            draft_id=draft_id,
            smoke_status="passed" if passed else "failed",
            passed=passed,
            smoke_cases=smoke_cases,
            smoke_results=smoke_results,
            artifact_summary=artifact_summary,
            readiness_summary=readiness_summary,
            failure_summary=failure_summary,
            recommended_actions=recommended_actions,
            downstream_constraints=self._downstream_constraints(
                source_id=source_id,
                request_id=request_id,
                draft_id=draft_id,
                passed=passed,
                readiness_summary=readiness_summary,
            ),
            warnings=self._warnings(
                smoke_results=smoke_results,
                readiness_summary=readiness_summary,
            ),
        )

        return {
            "success": True,
            "engine_name": self.engine_name,
            "story_smoke_test_report": report,
            "story_smoke_test_report_dict": report.model_dump(mode="json"),
            "handoff_to_next_engine": {
                "next_engine": "story_generation.learning_feedback_adapter",
                "payload_keys": [
                    "story_smoke_test_report",
                    "story_benchmark_pack",
                    "story_export_package",
                    "story_generation_orchestration_report",
                ],
            },
        }

    def validate_smoke_test_report(self, *, report: StorySmokeTestReport) -> Dict[str, Any]:
        blockers: List[str] = []
        warnings: List[str] = []
        passed_checks: List[str] = []

        if report.smoke_test_report_id:
            passed_checks.append("smoke_test_report_id_present")
        else:
            blockers.append("smoke_test_report_id missing")

        if report.source_id:
            passed_checks.append("source_id_present")
        else:
            blockers.append("source_id missing")

        if report.smoke_cases:
            passed_checks.append("smoke_cases_present")
        else:
            blockers.append("smoke cases missing")

        if report.smoke_results:
            passed_checks.append("smoke_results_present")
        else:
            blockers.append("smoke results missing")

        if report.readiness_summary:
            passed_checks.append("readiness_summary_present")
        else:
            warnings.append("readiness summary missing")

        if report.passed and report.failure_summary.get("failed_count", 0) > 0:
            blockers.append("smoke test cannot pass while failed cases exist")

        if report.warnings:
            warnings.extend(report.warnings)

        return {
            "success": True,
            "engine_name": self.engine_name,
            "valid": not blockers,
            "blockers": blockers,
            "warnings": self._unique(warnings),
            "passed_checks": passed_checks,
        }

    def summarize_smoke_test_report(self, *, report: StorySmokeTestReport) -> Dict[str, Any]:
        return {
            "success": True,
            "engine_name": self.engine_name,
            "summary": {
                "smoke_test_report_id": report.smoke_test_report_id,
                "source_id": report.source_id,
                "request_id": report.request_id,
                "draft_id": report.draft_id,
                "smoke_status": report.smoke_status,
                "passed": report.passed,
                "case_count": len(report.smoke_cases),
                "result_count": len(report.smoke_results),
                "failed_count": report.failure_summary.get("failed_count", 0),
                "warning_count": report.failure_summary.get("warning_count", 0),
                "recommended_action_count": len(report.recommended_actions),
            },
        }

    def build_smoke_test_text(self, *, report: StorySmokeTestReport) -> Dict[str, Any]:
        lines = [
            f"# Story Smoke Test Report: {report.source_id}",
            "",
            f"Smoke status: {report.smoke_status}",
            f"Passed: {report.passed}",
            "",
            "## Smoke Results",
        ]

        for result in report.smoke_results:
            lines.append(
                f"- {result.get('case_name')}: {result.get('status')} — {result.get('message')}"
            )

        lines.append("")
        lines.append("## Recommended Actions")
        for action in report.recommended_actions:
            lines.append(f"- [{action.get('priority')}] {action.get('action_type')}: {action.get('instruction')}")

        return {
            "success": True,
            "engine_name": self.engine_name,
            "smoke_test_text": "\n".join(lines),
        }

    def _smoke_cases(self) -> List[Dict[str, Any]]:
        return [
            {
                "case_id": "smoke_orchestration_present",
                "case_name": "orchestration_present",
                "case_type": "artifact",
                "priority": "critical",
                "description": "Orchestration report must exist.",
            },
            {
                "case_id": "smoke_orchestration_ready",
                "case_name": "orchestration_ready",
                "case_type": "readiness",
                "priority": "critical",
                "description": "Orchestration must be ready or explicitly explain why blocked.",
            },
            {
                "case_id": "smoke_export_package_present",
                "case_name": "export_package_present",
                "case_type": "artifact",
                "priority": "critical",
                "description": "Export package must exist.",
            },
            {
                "case_id": "smoke_export_status_clear",
                "case_name": "export_status_clear",
                "case_type": "export",
                "priority": "high",
                "description": "Export package must be approved or staged with blockers.",
            },
            {
                "case_id": "smoke_benchmark_present",
                "case_name": "benchmark_present",
                "case_type": "artifact",
                "priority": "critical",
                "description": "Benchmark pack must exist.",
            },
            {
                "case_id": "smoke_benchmark_score_available",
                "case_name": "benchmark_score_available",
                "case_type": "benchmark",
                "priority": "high",
                "description": "Benchmark score summary must be available.",
            },
            {
                "case_id": "smoke_context_available",
                "case_name": "context_available",
                "case_type": "context",
                "priority": "medium",
                "description": "Story context should be present, even if minimal.",
            },
        ]

    def _smoke_results(
        self,
        *,
        smoke_cases: List[Dict[str, Any]],
        orchestration_report: StoryGenerationOrchestrationReport | None,
        export_package: StoryExportPackage | None,
        benchmark_pack: StoryBenchmarkPack | None,
        story_context: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        results = []

        for case in smoke_cases:
            case_name = case["case_name"]
            status = "warning"
            message = "Smoke case warning."

            if case_name == "orchestration_present":
                status = "passed" if orchestration_report is not None else "failed"
                message = "Orchestration report present." if orchestration_report else "Orchestration report missing."

            elif case_name == "orchestration_ready":
                if orchestration_report and orchestration_report.ready_for_export:
                    status = "passed"
                    message = "Orchestration ready for export."
                elif orchestration_report and orchestration_report.blocked_reasons:
                    status = "warning"
                    message = "Orchestration is blocked with explicit reasons."
                else:
                    status = "failed"
                    message = "Orchestration is missing or readiness is unclear."

            elif case_name == "export_package_present":
                status = "passed" if export_package is not None else "failed"
                message = "Export package present." if export_package else "Export package missing."

            elif case_name == "export_status_clear":
                if export_package and export_package.approved_for_export:
                    status = "passed"
                    message = "Export package approved."
                elif export_package and export_package.blocked_reasons:
                    status = "warning"
                    message = "Export package staged with explicit blockers."
                else:
                    status = "failed"
                    message = "Export status unclear."

            elif case_name == "benchmark_present":
                status = "passed" if benchmark_pack is not None else "failed"
                message = "Benchmark pack present." if benchmark_pack else "Benchmark pack missing."

            elif case_name == "benchmark_score_available":
                if benchmark_pack and benchmark_pack.score_summary:
                    status = "passed" if benchmark_pack.score_summary.get("critical_failed_count", 0) == 0 else "warning"
                    message = f"Benchmark score: {benchmark_pack.score_summary.get('overall_score')}."
                else:
                    status = "failed"
                    message = "Benchmark score summary missing."

            elif case_name == "context_available":
                status = "passed" if story_context else "warning"
                message = "Story context available." if story_context else "Story context empty."

            results.append(
                {
                    "result_id": f"result_{case['case_id']}",
                    "case_id": case["case_id"],
                    "case_name": case_name,
                    "case_type": case["case_type"],
                    "priority": case["priority"],
                    "status": status,
                    "message": message,
                }
            )

        return results

    def _artifact_summary(
        self,
        *,
        orchestration_report: StoryGenerationOrchestrationReport | None,
        export_package: StoryExportPackage | None,
        benchmark_pack: StoryBenchmarkPack | None,
    ) -> Dict[str, Any]:
        return {
            "orchestration_report_present": orchestration_report is not None,
            "export_package_present": export_package is not None,
            "benchmark_pack_present": benchmark_pack is not None,
            "orchestration_report_id": getattr(orchestration_report, "orchestration_report_id", None),
            "export_package_id": getattr(export_package, "export_package_id", None),
            "benchmark_pack_id": getattr(benchmark_pack, "benchmark_pack_id", None),
        }

    def _readiness_summary(
        self,
        *,
        smoke_results: List[Dict[str, Any]],
        orchestration_report: StoryGenerationOrchestrationReport | None,
        export_package: StoryExportPackage | None,
        benchmark_pack: StoryBenchmarkPack | None,
    ) -> Dict[str, Any]:
        failed_critical = [
            item for item in smoke_results
            if item.get("status") == "failed" and item.get("priority") == "critical"
        ]
        failed_any = [item for item in smoke_results if item.get("status") == "failed"]

        export_ready = bool(orchestration_report and orchestration_report.ready_for_export and export_package and export_package.approved_for_export)
        benchmark_ready = bool(benchmark_pack and benchmark_pack.score_summary.get("critical_failed_count", 1) == 0)

        return {
            "smoke_passed": not failed_critical and not failed_any and export_ready and benchmark_ready,
            "critical_failure_count": len(failed_critical),
            "failure_count": len(failed_any),
            "export_ready": export_ready,
            "benchmark_ready": benchmark_ready,
        }

    def _failure_summary(self, *, smoke_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        failed = [item for item in smoke_results if item.get("status") == "failed"]
        warnings = [item for item in smoke_results if item.get("status") == "warning"]
        passed = [item for item in smoke_results if item.get("status") == "passed"]

        return {
            "passed_count": len(passed),
            "failed_count": len(failed),
            "warning_count": len(warnings),
            "failed_case_ids": [item.get("case_id") for item in failed],
            "warning_case_ids": [item.get("case_id") for item in warnings],
        }

    def _recommended_actions(
        self,
        *,
        smoke_results: List[Dict[str, Any]],
        readiness_summary: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        actions = []

        for result in smoke_results:
            if result.get("status") == "failed":
                actions.append(
                    {
                        "action_id": f"fix_{result.get('case_id')}",
                        "action_type": "smoke_failure",
                        "priority": result.get("priority", "high"),
                        "instruction": f"Fix smoke failure: {result.get('case_name')}. {result.get('message')}",
                    }
                )
            elif result.get("status") == "warning":
                actions.append(
                    {
                        "action_id": f"review_{result.get('case_id')}",
                        "action_type": "smoke_warning",
                        "priority": "medium",
                        "instruction": f"Review smoke warning: {result.get('case_name')}. {result.get('message')}",
                    }
                )

        if not readiness_summary.get("smoke_passed"):
            actions.append(
                {
                    "action_id": "do_not_finalize_chunk5",
                    "action_type": "chunk5_finalization",
                    "priority": "critical",
                    "instruction": "Do not finalize Chunk 5 until smoke test passes or blockers are intentionally accepted.",
                }
            )

        return self._unique_dicts(actions, key="action_id")

    def _downstream_constraints(
        self,
        *,
        source_id: str,
        request_id: str,
        draft_id: str,
        passed: bool,
        readiness_summary: Dict[str, Any],
    ) -> Dict[str, Any]:
        return {
            "source_id": source_id,
            "request_id": request_id,
            "draft_id": draft_id,
            "passed": passed,
            "readiness_summary": readiness_summary,
            "rules": [
                "Chunk 5 final verification should not pass unless smoke test passes.",
                "Smoke failures must become explicit final verification blockers.",
                "Warnings can be allowed only if documented in README/final verification.",
                "Smoke test report must be included in Chunk 1-5 integration verifier.",
            ],
        }

    def _warnings(
        self,
        *,
        smoke_results: List[Dict[str, Any]],
        readiness_summary: Dict[str, Any],
    ) -> List[str]:
        warnings = []
        failed_count = len([item for item in smoke_results if item.get("status") == "failed"])
        warning_count = len([item for item in smoke_results if item.get("status") == "warning"])

        if failed_count:
            warnings.append(f"{failed_count} smoke test case(s) failed.")
        if warning_count:
            warnings.append(f"{warning_count} smoke test case(s) produced warnings.")
        if not readiness_summary.get("smoke_passed"):
            warnings.append("Smoke test did not pass.")

        return warnings

    def _unique(self, values: List[str]) -> List[str]:
        result = []
        seen = set()
        for value in values:
            if value and value not in seen:
                seen.add(value)
                result.append(value)
        return result

    def _unique_dicts(self, values: List[Dict[str, Any]], *, key: str) -> List[Dict[str, Any]]:
        result = []
        seen = set()
        for value in values:
            marker = value.get(key) or str(value)
            if marker and marker not in seen:
                seen.add(marker)
                result.append(value)
        return result

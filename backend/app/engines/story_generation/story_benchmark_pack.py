from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List

from backend.app.schemas.story_generation import (
    GeneratedStoryDeltaReport,
    StoryBenchmarkPack,
    StoryExportPackage,
    StoryGenerationOrchestrationReport,
    StoryMemoryUpdateContract,
    StoryProvenanceRecord,
)


class StoryBenchmarkPackBuilder:
    """Builds benchmark cases and results for generated story packages.

    Locked Chunk 5.45. This is a deterministic benchmark layer for checking
    whether Chunk 5 outputs are export-safe, memory-safe, traceable, and
    sufficiently structured for future ML/research evaluation.
    """

    engine_name = "story_generation.story_benchmark_pack"

    def build_benchmark_pack(
        self,
        *,
        source_id: str,
        request_id: str = "",
        draft_id: str = "",
        story_payload: Dict[str, Any] | None = None,
        export_package: StoryExportPackage | None = None,
        orchestration_report: StoryGenerationOrchestrationReport | None = None,
        provenance_record: StoryProvenanceRecord | None = None,
        delta_report: GeneratedStoryDeltaReport | None = None,
        memory_update_contract: StoryMemoryUpdateContract | None = None,
        custom_cases: List[Dict[str, Any]] | None = None,
    ) -> Dict[str, Any]:
        story_payload = story_payload or {}
        custom_cases = custom_cases or []

        benchmark_cases = self._benchmark_cases(
            custom_cases=custom_cases,
            export_package=export_package,
            orchestration_report=orchestration_report,
            provenance_record=provenance_record,
            delta_report=delta_report,
            memory_update_contract=memory_update_contract,
            story_payload=story_payload,
        )

        benchmark_results = self._benchmark_results(
            benchmark_cases=benchmark_cases,
            export_package=export_package,
            orchestration_report=orchestration_report,
            provenance_record=provenance_record,
            delta_report=delta_report,
            memory_update_contract=memory_update_contract,
            story_payload=story_payload,
        )

        score_summary = self._score_summary(benchmark_results=benchmark_results)
        readiness_summary = self._readiness_summary(
            score_summary=score_summary,
            export_package=export_package,
            orchestration_report=orchestration_report,
            provenance_record=provenance_record,
            memory_update_contract=memory_update_contract,
        )
        regression_summary = self._regression_summary(
            benchmark_results=benchmark_results,
            delta_report=delta_report,
            memory_update_contract=memory_update_contract,
        )

        recommended_actions = self._recommended_actions(
            benchmark_results=benchmark_results,
            score_summary=score_summary,
            readiness_summary=readiness_summary,
        )

        benchmark_pack_id = f"story_benchmark_{source_id}_{draft_id or 'draft'}_{request_id or 'default'}"

        pack = StoryBenchmarkPack(
            benchmark_pack_id=benchmark_pack_id,
            source_id=source_id,
            request_id=request_id,
            draft_id=draft_id,
            benchmark_status=self._benchmark_status(score_summary=score_summary, readiness_summary=readiness_summary),
            benchmark_version="chunk_5_45_v1",
            benchmark_cases=benchmark_cases,
            benchmark_results=benchmark_results,
            score_summary=score_summary,
            readiness_summary=readiness_summary,
            regression_summary=regression_summary,
            recommended_actions=recommended_actions,
            benchmark_manifest=self._benchmark_manifest(
                benchmark_pack_id=benchmark_pack_id,
                source_id=source_id,
                request_id=request_id,
                draft_id=draft_id,
                benchmark_cases=benchmark_cases,
                benchmark_results=benchmark_results,
            ),
            downstream_constraints=self._downstream_constraints(
                source_id=source_id,
                request_id=request_id,
                draft_id=draft_id,
                score_summary=score_summary,
                readiness_summary=readiness_summary,
            ),
            warnings=self._warnings(
                benchmark_results=benchmark_results,
                score_summary=score_summary,
                readiness_summary=readiness_summary,
            ),
        )

        return {
            "success": True,
            "engine_name": self.engine_name,
            "story_benchmark_pack": pack,
            "story_benchmark_pack_dict": pack.model_dump(mode="json"),
            "handoff_to_next_engine": {
                "next_engine": "story_generation.story_smoke_test",
                "payload_keys": [
                    "story_benchmark_pack",
                    "story_export_package",
                    "story_generation_orchestration_report",
                ],
            },
        }

    def validate_benchmark_pack(self, *, pack: StoryBenchmarkPack) -> Dict[str, Any]:
        blockers: List[str] = []
        warnings: List[str] = []
        passed: List[str] = []

        if pack.benchmark_pack_id:
            passed.append("benchmark_pack_id_present")
        else:
            blockers.append("benchmark_pack_id missing")

        if pack.source_id:
            passed.append("source_id_present")
        else:
            blockers.append("source_id missing")

        if pack.benchmark_cases:
            passed.append("benchmark_cases_present")
        else:
            blockers.append("benchmark cases missing")

        if pack.benchmark_results:
            passed.append("benchmark_results_present")
        else:
            blockers.append("benchmark results missing")

        if pack.score_summary:
            passed.append("score_summary_present")
        else:
            warnings.append("score summary missing")

        if pack.benchmark_manifest:
            passed.append("benchmark_manifest_present")
        else:
            warnings.append("benchmark manifest missing")

        if pack.score_summary.get("failed_count", 0) > 0:
            warnings.append("benchmark pack contains failed cases")

        if pack.warnings:
            warnings.extend(pack.warnings)

        return {
            "success": True,
            "engine_name": self.engine_name,
            "valid": not blockers,
            "blockers": blockers,
            "warnings": self._unique(warnings),
            "passed_checks": passed,
        }

    def summarize_benchmark_pack(self, *, pack: StoryBenchmarkPack) -> Dict[str, Any]:
        return {
            "success": True,
            "engine_name": self.engine_name,
            "summary": {
                "benchmark_pack_id": pack.benchmark_pack_id,
                "source_id": pack.source_id,
                "request_id": pack.request_id,
                "draft_id": pack.draft_id,
                "benchmark_status": pack.benchmark_status,
                "benchmark_version": pack.benchmark_version,
                "case_count": len(pack.benchmark_cases),
                "result_count": len(pack.benchmark_results),
                "passed_count": pack.score_summary.get("passed_count", 0),
                "failed_count": pack.score_summary.get("failed_count", 0),
                "warning_count": pack.score_summary.get("warning_count", 0),
                "overall_score": pack.score_summary.get("overall_score", 0.0),
                "recommended_action_count": len(pack.recommended_actions),
            },
        }

    def build_benchmark_text(self, *, pack: StoryBenchmarkPack) -> Dict[str, Any]:
        lines = [
            f"# Story Benchmark Pack: {pack.source_id}",
            "",
            f"Pack ID: {pack.benchmark_pack_id}",
            f"Status: {pack.benchmark_status}",
            f"Overall score: {pack.score_summary.get('overall_score')}",
            "",
            "## Benchmark Results",
        ]

        for result in pack.benchmark_results:
            lines.append(
                f"- {result.get('case_name')}: {result.get('status')} "
                f"({result.get('score')}) — {result.get('message')}"
            )

        lines.append("")
        lines.append("## Recommended Actions")
        for action in pack.recommended_actions:
            lines.append(f"- [{action.get('priority')}] {action.get('action_type')}: {action.get('instruction')}")

        return {
            "success": True,
            "engine_name": self.engine_name,
            "benchmark_text": "\n".join(lines),
        }

    def _benchmark_cases(
        self,
        *,
        custom_cases: List[Dict[str, Any]],
        export_package: StoryExportPackage | None,
        orchestration_report: StoryGenerationOrchestrationReport | None,
        provenance_record: StoryProvenanceRecord | None,
        delta_report: GeneratedStoryDeltaReport | None,
        memory_update_contract: StoryMemoryUpdateContract | None,
        story_payload: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        cases = [
            {
                "case_id": "case_story_payload_present",
                "case_name": "story_payload_present",
                "case_type": "payload",
                "priority": "high",
                "description": "Story payload should include generated content or story metadata.",
            },
            {
                "case_id": "case_orchestration_ready",
                "case_name": "orchestration_ready",
                "case_type": "orchestration",
                "priority": "critical",
                "description": "Orchestration report should be ready for export.",
            },
            {
                "case_id": "case_provenance_traceable",
                "case_name": "provenance_traceable",
                "case_type": "provenance",
                "priority": "critical",
                "description": "Provenance record should be present and approved for export.",
            },
            {
                "case_id": "case_delta_memory_candidates",
                "case_name": "delta_memory_candidates",
                "case_type": "memory",
                "priority": "medium",
                "description": "Delta report should expose memory update candidates.",
            },
            {
                "case_id": "case_memory_contract_safe",
                "case_name": "memory_contract_safe",
                "case_type": "memory",
                "priority": "high",
                "description": "Memory update contract should be approved or explicitly staged.",
            },
            {
                "case_id": "case_export_package_status",
                "case_name": "export_package_status",
                "case_type": "export",
                "priority": "high",
                "description": "Export package should be approved or blocked with reasons.",
            },
            {
                "case_id": "case_audit_snapshots_present",
                "case_name": "audit_snapshots_present",
                "case_type": "audit",
                "priority": "medium",
                "description": "Export package should carry orchestration/provenance/delta/memory snapshots.",
            },
        ]

        for index, case in enumerate(custom_cases, start=1):
            item = dict(case)
            item.setdefault("case_id", f"custom_case_{index}")
            item.setdefault("case_name", item["case_id"])
            item.setdefault("case_type", "custom")
            item.setdefault("priority", "medium")
            item.setdefault("description", "Custom benchmark case.")
            cases.append(item)

        return self._unique_dicts(cases, key="case_id")

    def _benchmark_results(
        self,
        *,
        benchmark_cases: List[Dict[str, Any]],
        export_package: StoryExportPackage | None,
        orchestration_report: StoryGenerationOrchestrationReport | None,
        provenance_record: StoryProvenanceRecord | None,
        delta_report: GeneratedStoryDeltaReport | None,
        memory_update_contract: StoryMemoryUpdateContract | None,
        story_payload: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        results = []

        for case in benchmark_cases:
            case_name = case.get("case_name")
            status = "warning"
            score = 0.5
            message = "Case produced warning."

            if case_name == "story_payload_present":
                passed = bool(story_payload)
                status = "passed" if passed else "failed"
                score = 1.0 if passed else 0.0
                message = "Story payload present." if passed else "Story payload missing."

            elif case_name == "orchestration_ready":
                passed = bool(orchestration_report and orchestration_report.ready_for_export)
                status = "passed" if passed else "failed"
                score = 1.0 if passed else 0.0
                message = "Orchestration ready for export." if passed else "Orchestration not ready for export."

            elif case_name == "provenance_traceable":
                passed = bool(provenance_record and provenance_record.approved_for_export)
                status = "passed" if passed else "failed"
                score = 1.0 if passed else 0.0
                message = "Provenance approved for export." if passed else "Provenance missing or not export-approved."

            elif case_name == "delta_memory_candidates":
                count = len(getattr(delta_report, "memory_update_candidates", []) or [])
                passed = delta_report is not None and count > 0
                status = "passed" if passed else "warning"
                score = 1.0 if passed else 0.5
                message = f"Delta memory candidate count: {count}."

            elif case_name == "memory_contract_safe":
                if memory_update_contract and memory_update_contract.approved_for_apply:
                    status = "passed"
                    score = 1.0
                    message = "Memory contract approved for apply."
                elif memory_update_contract:
                    status = "warning"
                    score = 0.5
                    message = f"Memory contract present but status is {memory_update_contract.contract_status}."
                else:
                    status = "failed"
                    score = 0.0
                    message = "Memory contract missing."

            elif case_name == "export_package_status":
                if export_package and export_package.approved_for_export:
                    status = "passed"
                    score = 1.0
                    message = "Export package approved."
                elif export_package and export_package.blocked_reasons:
                    status = "warning"
                    score = 0.5
                    message = "Export package blocked with explicit reasons."
                else:
                    status = "failed"
                    score = 0.0
                    message = "Export package missing or unclear."

            elif case_name == "audit_snapshots_present":
                if export_package:
                    snapshots = [
                        export_package.orchestration_snapshot,
                        export_package.provenance_snapshot,
                        export_package.delta_snapshot,
                        export_package.memory_contract_snapshot,
                    ]
                    available_count = sum(1 for snapshot in snapshots if snapshot and snapshot.get("available") is not False)
                    status = "passed" if available_count >= 3 else "warning"
                    score = 1.0 if available_count >= 3 else 0.5
                    message = f"Audit snapshot availability count: {available_count}/4."
                else:
                    status = "failed"
                    score = 0.0
                    message = "Export package missing."

            else:
                status = "passed" if case.get("expected_status") == "passed" else "warning"
                score = 1.0 if status == "passed" else 0.5
                message = case.get("description", "Custom benchmark case executed.")

            results.append(
                {
                    "result_id": f"result_{case.get('case_id')}",
                    "case_id": case.get("case_id"),
                    "case_name": case_name,
                    "case_type": case.get("case_type"),
                    "priority": case.get("priority"),
                    "status": status,
                    "score": score,
                    "message": message,
                }
            )

        return results

    def _score_summary(self, *, benchmark_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not benchmark_results:
            return {
                "overall_score": 0.0,
                "passed_count": 0,
                "failed_count": 0,
                "warning_count": 0,
                "case_count": 0,
            }

        passed = [item for item in benchmark_results if item.get("status") == "passed"]
        failed = [item for item in benchmark_results if item.get("status") == "failed"]
        warnings = [item for item in benchmark_results if item.get("status") == "warning"]
        score = sum(float(item.get("score", 0.0)) for item in benchmark_results) / len(benchmark_results)

        critical_failed = [
            item for item in failed if item.get("priority") == "critical"
        ]

        return {
            "overall_score": round(score, 3),
            "passed_count": len(passed),
            "failed_count": len(failed),
            "warning_count": len(warnings),
            "case_count": len(benchmark_results),
            "critical_failed_count": len(critical_failed),
            "pass_rate": round(len(passed) / len(benchmark_results), 3),
        }

    def _readiness_summary(
        self,
        *,
        score_summary: Dict[str, Any],
        export_package: StoryExportPackage | None,
        orchestration_report: StoryGenerationOrchestrationReport | None,
        provenance_record: StoryProvenanceRecord | None,
        memory_update_contract: StoryMemoryUpdateContract | None,
    ) -> Dict[str, Any]:
        ready_for_publish = bool(
            score_summary.get("critical_failed_count", 0) == 0
            and score_summary.get("overall_score", 0.0) >= 0.75
            and export_package
            and export_package.approved_for_export
        )

        ready_for_memory = bool(
            provenance_record
            and provenance_record.approved_for_memory_update
            and memory_update_contract
            and memory_update_contract.approved_for_apply
        )

        return {
            "ready_for_publish": ready_for_publish,
            "ready_for_memory": ready_for_memory,
            "orchestration_ready": bool(orchestration_report and orchestration_report.ready_for_export),
            "export_approved": bool(export_package and export_package.approved_for_export),
            "provenance_export_approved": bool(provenance_record and provenance_record.approved_for_export),
            "minimum_score_met": score_summary.get("overall_score", 0.0) >= 0.75,
        }

    def _regression_summary(
        self,
        *,
        benchmark_results: List[Dict[str, Any]],
        delta_report: GeneratedStoryDeltaReport | None,
        memory_update_contract: StoryMemoryUpdateContract | None,
    ) -> Dict[str, Any]:
        failed_cases = [item.get("case_name") for item in benchmark_results if item.get("status") == "failed"]
        warning_cases = [item.get("case_name") for item in benchmark_results if item.get("status") == "warning"]

        return {
            "failed_cases": failed_cases,
            "warning_cases": warning_cases,
            "memory_candidate_count": len(getattr(delta_report, "memory_update_candidates", []) or []),
            "blocked_memory_update_count": len(getattr(memory_update_contract, "blocked_updates", []) or []),
            "review_memory_update_count": len(getattr(memory_update_contract, "review_required_updates", []) or []),
        }

    def _recommended_actions(
        self,
        *,
        benchmark_results: List[Dict[str, Any]],
        score_summary: Dict[str, Any],
        readiness_summary: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        actions = []

        for result in benchmark_results:
            if result.get("status") == "failed":
                actions.append(
                    {
                        "action_id": f"fix_{result.get('case_id')}",
                        "action_type": "benchmark_failure",
                        "priority": result.get("priority", "high"),
                        "instruction": f"Fix failed benchmark: {result.get('case_name')}. {result.get('message')}",
                    }
                )
            elif result.get("status") == "warning":
                actions.append(
                    {
                        "action_id": f"review_{result.get('case_id')}",
                        "action_type": "benchmark_warning",
                        "priority": "medium",
                        "instruction": f"Review warning benchmark: {result.get('case_name')}. {result.get('message')}",
                    }
                )

        if not readiness_summary.get("ready_for_publish"):
            actions.append(
                {
                    "action_id": "not_ready_for_publish",
                    "action_type": "publish_readiness",
                    "priority": "high",
                    "instruction": "Do not publish until critical benchmark failures are resolved and score threshold is met.",
                }
            )

        if not readiness_summary.get("ready_for_memory"):
            actions.append(
                {
                    "action_id": "not_ready_for_memory",
                    "action_type": "memory_readiness",
                    "priority": "medium",
                    "instruction": "Do not apply memory updates until provenance and memory contract are approved.",
                }
            )

        return self._unique_dicts(actions, key="action_id")

    def _benchmark_status(self, *, score_summary: Dict[str, Any], readiness_summary: Dict[str, Any]) -> str:
        if score_summary.get("critical_failed_count", 0) > 0:
            return "failed_critical"
        if readiness_summary.get("ready_for_publish"):
            return "passed"
        if score_summary.get("failed_count", 0) > 0:
            return "failed"
        return "passed_with_warnings"

    def _benchmark_manifest(
        self,
        *,
        benchmark_pack_id: str,
        source_id: str,
        request_id: str,
        draft_id: str,
        benchmark_cases: List[Dict[str, Any]],
        benchmark_results: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        return {
            "benchmark_pack_id": benchmark_pack_id,
            "source_id": source_id,
            "request_id": request_id,
            "draft_id": draft_id,
            "benchmark_version": "chunk_5_45_v1",
            "case_count": len(benchmark_cases),
            "result_count": len(benchmark_results),
            "created_at_utc": datetime.now(timezone.utc).isoformat(),
        }

    def _downstream_constraints(
        self,
        *,
        source_id: str,
        request_id: str,
        draft_id: str,
        score_summary: Dict[str, Any],
        readiness_summary: Dict[str, Any],
    ) -> Dict[str, Any]:
        return {
            "source_id": source_id,
            "request_id": request_id,
            "draft_id": draft_id,
            "overall_score": score_summary.get("overall_score", 0.0),
            "ready_for_publish": readiness_summary.get("ready_for_publish", False),
            "ready_for_memory": readiness_summary.get("ready_for_memory", False),
            "rules": [
                "Do not publish benchmark packs with critical failures.",
                "Treat benchmark warnings as review items before final presentation.",
                "Benchmark pack must be carried into smoke tests and final verification.",
                "Future ML/research metrics can extend these deterministic cases.",
            ],
        }

    def _warnings(
        self,
        *,
        benchmark_results: List[Dict[str, Any]],
        score_summary: Dict[str, Any],
        readiness_summary: Dict[str, Any],
    ) -> List[str]:
        warnings = []
        if score_summary.get("failed_count", 0) > 0:
            warnings.append(f"{score_summary.get('failed_count')} benchmark case(s) failed.")
        if score_summary.get("warning_count", 0) > 0:
            warnings.append(f"{score_summary.get('warning_count')} benchmark case(s) produced warnings.")
        if not readiness_summary.get("ready_for_publish"):
            warnings.append("Benchmark pack is not ready for publish.")
        if not readiness_summary.get("ready_for_memory"):
            warnings.append("Benchmark pack is not ready for memory apply.")
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

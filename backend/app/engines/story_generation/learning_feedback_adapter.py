from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List

from backend.app.schemas.story_generation import (
    LearningFeedbackPackage,
    StoryBenchmarkPack,
    StoryExportPackage,
    StoryGenerationOrchestrationReport,
    StorySmokeTestReport,
)


class LearningFeedbackAdapter:
    """Converts generation evaluation artifacts into future learning signals.

    Locked Chunk 5.47. This does not train a model yet. It prepares clean,
    auditable feedback rows so Chunk 8 can later build datasets, metrics,
    preference signals, reward models, or supervised fine-tuning examples.
    """

    engine_name = "story_generation.learning_feedback_adapter"

    def build_learning_feedback_package(
        self,
        *,
        source_id: str,
        request_id: str = "",
        draft_id: str = "",
        story_payload: Dict[str, Any] | None = None,
        orchestration_report: StoryGenerationOrchestrationReport | None = None,
        export_package: StoryExportPackage | None = None,
        benchmark_pack: StoryBenchmarkPack | None = None,
        smoke_test_report: StorySmokeTestReport | None = None,
        human_feedback: Dict[str, Any] | None = None,
        story_context: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        story_payload = story_payload or {}
        human_feedback = human_feedback or {}
        story_context = story_context or {}

        quality_feedback = self._quality_feedback(
            orchestration_report=orchestration_report,
            benchmark_pack=benchmark_pack,
            smoke_test_report=smoke_test_report,
        )
        risk_feedback = self._risk_feedback(
            orchestration_report=orchestration_report,
            export_package=export_package,
            benchmark_pack=benchmark_pack,
            smoke_test_report=smoke_test_report,
        )
        memory_feedback = self._memory_feedback(
            orchestration_report=orchestration_report,
            benchmark_pack=benchmark_pack,
            smoke_test_report=smoke_test_report,
        )
        export_feedback = self._export_feedback(
            export_package=export_package,
            benchmark_pack=benchmark_pack,
            smoke_test_report=smoke_test_report,
        )
        benchmark_feedback = self._benchmark_feedback(benchmark_pack=benchmark_pack)
        smoke_feedback = self._smoke_feedback(smoke_test_report=smoke_test_report)

        feedback_rows = self._feedback_rows(
            source_id=source_id,
            request_id=request_id,
            draft_id=draft_id,
            quality_feedback=quality_feedback,
            risk_feedback=risk_feedback,
            memory_feedback=memory_feedback,
            export_feedback=export_feedback,
            benchmark_feedback=benchmark_feedback,
            smoke_feedback=smoke_feedback,
            human_feedback=human_feedback,
            story_payload=story_payload,
            story_context=story_context,
        )

        training_signals = self._training_signal_candidates(
            feedback_rows=feedback_rows,
            story_payload=story_payload,
            human_feedback=human_feedback,
        )

        feedback_summary = self._feedback_summary(
            feedback_rows=feedback_rows,
            training_signals=training_signals,
            benchmark_pack=benchmark_pack,
            smoke_test_report=smoke_test_report,
            human_feedback=human_feedback,
        )

        approved_for_learning = self._approved_for_learning(
            feedback_summary=feedback_summary,
            smoke_test_report=smoke_test_report,
            benchmark_pack=benchmark_pack,
            human_feedback=human_feedback,
        )

        learning_feedback_id = f"learning_feedback_{source_id}_{draft_id or 'draft'}_{request_id or 'default'}"

        package = LearningFeedbackPackage(
            learning_feedback_id=learning_feedback_id,
            source_id=source_id,
            request_id=request_id,
            draft_id=draft_id,
            feedback_status="approved" if approved_for_learning else "staged",
            feedback_version="chunk_5_47_v1",
            approved_for_learning=approved_for_learning,
            feedback_rows=feedback_rows,
            quality_feedback=quality_feedback,
            risk_feedback=risk_feedback,
            memory_feedback=memory_feedback,
            export_feedback=export_feedback,
            benchmark_feedback=benchmark_feedback,
            smoke_feedback=smoke_feedback,
            training_signal_candidates=training_signals,
            dataset_manifest=self._dataset_manifest(
                learning_feedback_id=learning_feedback_id,
                source_id=source_id,
                request_id=request_id,
                draft_id=draft_id,
                feedback_rows=feedback_rows,
                training_signals=training_signals,
            ),
            feedback_summary=feedback_summary,
            recommended_actions=self._recommended_actions(
                approved_for_learning=approved_for_learning,
                feedback_summary=feedback_summary,
                benchmark_pack=benchmark_pack,
                smoke_test_report=smoke_test_report,
                human_feedback=human_feedback,
            ),
            downstream_constraints=self._downstream_constraints(
                source_id=source_id,
                request_id=request_id,
                draft_id=draft_id,
                approved_for_learning=approved_for_learning,
                feedback_summary=feedback_summary,
            ),
            warnings=self._warnings(
                approved_for_learning=approved_for_learning,
                feedback_summary=feedback_summary,
                benchmark_pack=benchmark_pack,
                smoke_test_report=smoke_test_report,
            ),
        )

        return {
            "success": True,
            "engine_name": self.engine_name,
            "learning_feedback_package": package,
            "learning_feedback_package_dict": package.model_dump(mode="json"),
            "handoff_to_next_engine": {
                "next_engine": "story_generation.chunk_1_5_integration_verifier",
                "payload_keys": [
                    "learning_feedback_package",
                    "story_smoke_test_report",
                    "story_benchmark_pack",
                    "story_export_package",
                ],
            },
        }

    def validate_learning_feedback_package(self, *, package: LearningFeedbackPackage) -> Dict[str, Any]:
        blockers: List[str] = []
        warnings: List[str] = []
        passed: List[str] = []

        if package.learning_feedback_id:
            passed.append("learning_feedback_id_present")
        else:
            blockers.append("learning_feedback_id missing")

        if package.source_id:
            passed.append("source_id_present")
        else:
            blockers.append("source_id missing")

        if package.feedback_rows:
            passed.append("feedback_rows_present")
        else:
            warnings.append("feedback rows missing")

        if package.dataset_manifest:
            passed.append("dataset_manifest_present")
        else:
            warnings.append("dataset manifest missing")

        if package.feedback_summary:
            passed.append("feedback_summary_present")
        else:
            warnings.append("feedback summary missing")

        if package.approved_for_learning and not package.training_signal_candidates:
            blockers.append("package cannot be approved for learning without training signal candidates")

        if package.warnings:
            warnings.extend(package.warnings)

        return {
            "success": True,
            "engine_name": self.engine_name,
            "valid": not blockers,
            "blockers": blockers,
            "warnings": self._unique(warnings),
            "passed_checks": passed,
        }

    def summarize_learning_feedback_package(self, *, package: LearningFeedbackPackage) -> Dict[str, Any]:
        return {
            "success": True,
            "engine_name": self.engine_name,
            "summary": {
                "learning_feedback_id": package.learning_feedback_id,
                "source_id": package.source_id,
                "request_id": package.request_id,
                "draft_id": package.draft_id,
                "feedback_status": package.feedback_status,
                "approved_for_learning": package.approved_for_learning,
                "feedback_row_count": len(package.feedback_rows),
                "training_signal_count": len(package.training_signal_candidates),
                "quality_feedback_count": len(package.quality_feedback),
                "risk_feedback_count": len(package.risk_feedback),
                "memory_feedback_count": len(package.memory_feedback),
                "export_feedback_count": len(package.export_feedback),
                "benchmark_feedback_count": len(package.benchmark_feedback),
                "smoke_feedback_count": len(package.smoke_feedback),
                "warning_count": len(package.warnings),
            },
        }

    def build_learning_feedback_text(self, *, package: LearningFeedbackPackage) -> Dict[str, Any]:
        lines = [
            f"# Learning Feedback Package: {package.source_id}",
            "",
            f"Feedback ID: {package.learning_feedback_id}",
            f"Status: {package.feedback_status}",
            f"Approved for learning: {package.approved_for_learning}",
            "",
            "## Feedback Summary",
        ]

        for key, value in package.feedback_summary.items():
            lines.append(f"- {key}: {value}")

        lines.append("")
        lines.append("## Training Signal Candidates")
        for signal in package.training_signal_candidates:
            lines.append(f"- {signal.get('signal_type')}: {signal.get('label')} ({signal.get('confidence')})")

        lines.append("")
        lines.append("## Recommended Actions")
        for action in package.recommended_actions:
            lines.append(f"- [{action.get('priority')}] {action.get('action_type')}: {action.get('instruction')}")

        return {
            "success": True,
            "engine_name": self.engine_name,
            "learning_feedback_text": "\n".join(lines),
        }

    def _quality_feedback(
        self,
        *,
        orchestration_report: StoryGenerationOrchestrationReport | None,
        benchmark_pack: StoryBenchmarkPack | None,
        smoke_test_report: StorySmokeTestReport | None,
    ) -> List[Dict[str, Any]]:
        rows = []

        if orchestration_report:
            rows.append(
                {
                    "feedback_id": "quality_orchestration_status",
                    "feedback_type": "quality",
                    "metric_name": "orchestration_status",
                    "value": orchestration_report.orchestration_status,
                    "score": 1.0 if orchestration_report.orchestration_status == "ready" else 0.3,
                    "label": "positive" if orchestration_report.orchestration_status == "ready" else "needs_improvement",
                }
            )

        if benchmark_pack:
            rows.append(
                {
                    "feedback_id": "quality_benchmark_overall_score",
                    "feedback_type": "quality",
                    "metric_name": "benchmark_overall_score",
                    "value": benchmark_pack.score_summary.get("overall_score", 0.0),
                    "score": float(benchmark_pack.score_summary.get("overall_score", 0.0)),
                    "label": "positive" if benchmark_pack.score_summary.get("overall_score", 0.0) >= 0.75 else "needs_improvement",
                }
            )

        if smoke_test_report:
            rows.append(
                {
                    "feedback_id": "quality_smoke_passed",
                    "feedback_type": "quality",
                    "metric_name": "smoke_passed",
                    "value": smoke_test_report.passed,
                    "score": 1.0 if smoke_test_report.passed else 0.0,
                    "label": "positive" if smoke_test_report.passed else "needs_improvement",
                }
            )

        return rows

    def _risk_feedback(
        self,
        *,
        orchestration_report: StoryGenerationOrchestrationReport | None,
        export_package: StoryExportPackage | None,
        benchmark_pack: StoryBenchmarkPack | None,
        smoke_test_report: StorySmokeTestReport | None,
    ) -> List[Dict[str, Any]]:
        rows = []

        if orchestration_report:
            blocked_count = len(orchestration_report.blocked_reasons)
            rows.append(
                {
                    "feedback_id": "risk_orchestration_blockers",
                    "feedback_type": "risk",
                    "metric_name": "blocked_reason_count",
                    "value": blocked_count,
                    "score": 1.0 if blocked_count == 0 else 0.2,
                    "label": "safe" if blocked_count == 0 else "risky",
                }
            )

        if export_package:
            blocker_count = len(export_package.blocked_reasons)
            rows.append(
                {
                    "feedback_id": "risk_export_blockers",
                    "feedback_type": "risk",
                    "metric_name": "export_blocker_count",
                    "value": blocker_count,
                    "score": 1.0 if blocker_count == 0 else 0.2,
                    "label": "safe" if blocker_count == 0 else "risky",
                }
            )

        if benchmark_pack:
            critical_failed = benchmark_pack.score_summary.get("critical_failed_count", 0)
            rows.append(
                {
                    "feedback_id": "risk_benchmark_critical_failures",
                    "feedback_type": "risk",
                    "metric_name": "critical_failed_count",
                    "value": critical_failed,
                    "score": 1.0 if critical_failed == 0 else 0.0,
                    "label": "safe" if critical_failed == 0 else "risky",
                }
            )

        if smoke_test_report:
            failed_count = smoke_test_report.failure_summary.get("failed_count", 0)
            rows.append(
                {
                    "feedback_id": "risk_smoke_failures",
                    "feedback_type": "risk",
                    "metric_name": "smoke_failed_count",
                    "value": failed_count,
                    "score": 1.0 if failed_count == 0 else 0.0,
                    "label": "safe" if failed_count == 0 else "risky",
                }
            )

        return rows

    def _memory_feedback(
        self,
        *,
        orchestration_report: StoryGenerationOrchestrationReport | None,
        benchmark_pack: StoryBenchmarkPack | None,
        smoke_test_report: StorySmokeTestReport | None,
    ) -> List[Dict[str, Any]]:
        rows = []

        if orchestration_report:
            rows.append(
                {
                    "feedback_id": "memory_orchestration_ready",
                    "feedback_type": "memory",
                    "metric_name": "ready_for_memory_apply",
                    "value": orchestration_report.ready_for_memory_apply,
                    "score": 1.0 if orchestration_report.ready_for_memory_apply else 0.4,
                    "label": "memory_ready" if orchestration_report.ready_for_memory_apply else "memory_not_ready",
                }
            )

        if benchmark_pack:
            rows.append(
                {
                    "feedback_id": "memory_benchmark_ready",
                    "feedback_type": "memory",
                    "metric_name": "benchmark_ready_for_memory",
                    "value": benchmark_pack.readiness_summary.get("ready_for_memory", False),
                    "score": 1.0 if benchmark_pack.readiness_summary.get("ready_for_memory", False) else 0.4,
                    "label": "memory_ready" if benchmark_pack.readiness_summary.get("ready_for_memory", False) else "memory_not_ready",
                }
            )

        if smoke_test_report:
            rows.append(
                {
                    "feedback_id": "memory_smoke_passed",
                    "feedback_type": "memory",
                    "metric_name": "smoke_memory_safety_proxy",
                    "value": smoke_test_report.passed,
                    "score": 1.0 if smoke_test_report.passed else 0.3,
                    "label": "memory_ready" if smoke_test_report.passed else "memory_not_ready",
                }
            )

        return rows

    def _export_feedback(
        self,
        *,
        export_package: StoryExportPackage | None,
        benchmark_pack: StoryBenchmarkPack | None,
        smoke_test_report: StorySmokeTestReport | None,
    ) -> List[Dict[str, Any]]:
        rows = []

        if export_package:
            rows.append(
                {
                    "feedback_id": "export_package_approved",
                    "feedback_type": "export",
                    "metric_name": "approved_for_export",
                    "value": export_package.approved_for_export,
                    "score": 1.0 if export_package.approved_for_export else 0.0,
                    "label": "export_ready" if export_package.approved_for_export else "export_blocked",
                }
            )

        if benchmark_pack:
            rows.append(
                {
                    "feedback_id": "export_benchmark_publish_ready",
                    "feedback_type": "export",
                    "metric_name": "ready_for_publish",
                    "value": benchmark_pack.readiness_summary.get("ready_for_publish", False),
                    "score": 1.0 if benchmark_pack.readiness_summary.get("ready_for_publish", False) else 0.0,
                    "label": "export_ready" if benchmark_pack.readiness_summary.get("ready_for_publish", False) else "export_blocked",
                }
            )

        if smoke_test_report:
            rows.append(
                {
                    "feedback_id": "export_smoke_export_ready",
                    "feedback_type": "export",
                    "metric_name": "smoke_export_ready",
                    "value": smoke_test_report.readiness_summary.get("export_ready", False),
                    "score": 1.0 if smoke_test_report.readiness_summary.get("export_ready", False) else 0.0,
                    "label": "export_ready" if smoke_test_report.readiness_summary.get("export_ready", False) else "export_blocked",
                }
            )

        return rows

    def _benchmark_feedback(self, *, benchmark_pack: StoryBenchmarkPack | None) -> List[Dict[str, Any]]:
        if not benchmark_pack:
            return []

        rows = []
        for result in benchmark_pack.benchmark_results:
            score = float(result.get("score", 0.0))
            rows.append(
                {
                    "feedback_id": f"benchmark_{result.get('case_id')}",
                    "feedback_type": "benchmark",
                    "metric_name": result.get("case_name"),
                    "value": result.get("status"),
                    "score": score,
                    "label": "positive" if result.get("status") == "passed" else "needs_improvement",
                    "message": result.get("message"),
                }
            )
        return rows

    def _smoke_feedback(self, *, smoke_test_report: StorySmokeTestReport | None) -> List[Dict[str, Any]]:
        if not smoke_test_report:
            return []

        rows = []
        for result in smoke_test_report.smoke_results:
            status = result.get("status")
            rows.append(
                {
                    "feedback_id": f"smoke_{result.get('case_id')}",
                    "feedback_type": "smoke",
                    "metric_name": result.get("case_name"),
                    "value": status,
                    "score": 1.0 if status == "passed" else 0.5 if status == "warning" else 0.0,
                    "label": "positive" if status == "passed" else "needs_improvement",
                    "message": result.get("message"),
                }
            )
        return rows

    def _feedback_rows(
        self,
        *,
        source_id: str,
        request_id: str,
        draft_id: str,
        quality_feedback: List[Dict[str, Any]],
        risk_feedback: List[Dict[str, Any]],
        memory_feedback: List[Dict[str, Any]],
        export_feedback: List[Dict[str, Any]],
        benchmark_feedback: List[Dict[str, Any]],
        smoke_feedback: List[Dict[str, Any]],
        human_feedback: Dict[str, Any],
        story_payload: Dict[str, Any],
        story_context: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        rows = (
            quality_feedback
            + risk_feedback
            + memory_feedback
            + export_feedback
            + benchmark_feedback
            + smoke_feedback
        )

        if human_feedback:
            rows.append(
                {
                    "feedback_id": "human_feedback_summary",
                    "feedback_type": "human",
                    "metric_name": "human_feedback",
                    "value": human_feedback,
                    "score": float(human_feedback.get("score", 0.5)) if isinstance(human_feedback.get("score", 0.5), (int, float)) else 0.5,
                    "label": human_feedback.get("label", "human_reviewed"),
                }
            )

        normalized = []
        for index, row in enumerate(rows, start=1):
            item = dict(row)
            item.setdefault("feedback_id", f"feedback_row_{index}")
            item["source_id"] = source_id
            item["request_id"] = request_id
            item["draft_id"] = draft_id
            item["story_payload_keys"] = sorted(story_payload.keys())
            item["story_context_keys"] = sorted(story_context.keys())
            item["created_at_utc"] = datetime.now(timezone.utc).isoformat()
            normalized.append(item)

        return self._unique_dicts(normalized, key="feedback_id")

    def _training_signal_candidates(
        self,
        *,
        feedback_rows: List[Dict[str, Any]],
        story_payload: Dict[str, Any],
        human_feedback: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        signals = []

        positive_rows = [row for row in feedback_rows if row.get("label") in {"positive", "safe", "export_ready", "memory_ready"}]
        negative_rows = [row for row in feedback_rows if row.get("label") in {"needs_improvement", "risky", "export_blocked", "memory_not_ready"}]

        if positive_rows:
            signals.append(
                {
                    "signal_id": "signal_positive_generation",
                    "signal_type": "preference_signal",
                    "label": "positive_generation",
                    "confidence": round(len(positive_rows) / max(len(feedback_rows), 1), 3),
                    "evidence_count": len(positive_rows),
                }
            )

        if negative_rows:
            signals.append(
                {
                    "signal_id": "signal_revision_needed",
                    "signal_type": "revision_signal",
                    "label": "revision_needed",
                    "confidence": round(len(negative_rows) / max(len(feedback_rows), 1), 3),
                    "evidence_count": len(negative_rows),
                }
            )

        if story_payload:
            signals.append(
                {
                    "signal_id": "signal_story_payload_available",
                    "signal_type": "supervised_example_candidate",
                    "label": "story_payload_available",
                    "confidence": 1.0,
                    "evidence_count": len(story_payload),
                }
            )

        if human_feedback:
            signals.append(
                {
                    "signal_id": "signal_human_feedback",
                    "signal_type": "human_feedback_signal",
                    "label": human_feedback.get("label", "human_reviewed"),
                    "confidence": float(human_feedback.get("confidence", 0.8)) if isinstance(human_feedback.get("confidence", 0.8), (int, float)) else 0.8,
                    "evidence_count": 1,
                }
            )

        return self._unique_dicts(signals, key="signal_id")

    def _feedback_summary(
        self,
        *,
        feedback_rows: List[Dict[str, Any]],
        training_signals: List[Dict[str, Any]],
        benchmark_pack: StoryBenchmarkPack | None,
        smoke_test_report: StorySmokeTestReport | None,
        human_feedback: Dict[str, Any],
    ) -> Dict[str, Any]:
        if not feedback_rows:
            average_score = 0.0
        else:
            average_score = sum(float(row.get("score", 0.0)) for row in feedback_rows) / len(feedback_rows)

        return {
            "feedback_row_count": len(feedback_rows),
            "training_signal_count": len(training_signals),
            "average_feedback_score": round(average_score, 3),
            "benchmark_status": getattr(benchmark_pack, "benchmark_status", None),
            "smoke_passed": getattr(smoke_test_report, "passed", None),
            "human_feedback_present": bool(human_feedback),
            "negative_feedback_count": len([row for row in feedback_rows if row.get("label") in {"needs_improvement", "risky", "export_blocked", "memory_not_ready"}]),
            "positive_feedback_count": len([row for row in feedback_rows if row.get("label") in {"positive", "safe", "export_ready", "memory_ready"}]),
        }

    def _approved_for_learning(
        self,
        *,
        feedback_summary: Dict[str, Any],
        smoke_test_report: StorySmokeTestReport | None,
        benchmark_pack: StoryBenchmarkPack | None,
        human_feedback: Dict[str, Any],
    ) -> bool:
        if human_feedback.get("exclude_from_learning") is True:
            return False

        if feedback_summary.get("training_signal_count", 0) == 0:
            return False

        if smoke_test_report and not smoke_test_report.passed:
            return False

        if benchmark_pack and benchmark_pack.score_summary.get("critical_failed_count", 0) > 0:
            return False

        return feedback_summary.get("average_feedback_score", 0.0) >= 0.65

    def _dataset_manifest(
        self,
        *,
        learning_feedback_id: str,
        source_id: str,
        request_id: str,
        draft_id: str,
        feedback_rows: List[Dict[str, Any]],
        training_signals: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        return {
            "learning_feedback_id": learning_feedback_id,
            "source_id": source_id,
            "request_id": request_id,
            "draft_id": draft_id,
            "feedback_version": "chunk_5_47_v1",
            "row_count": len(feedback_rows),
            "training_signal_count": len(training_signals),
            "created_at_utc": datetime.now(timezone.utc).isoformat(),
            "intended_future_use": [
                "preference dataset",
                "revision dataset",
                "quality scoring dataset",
                "risk gate dataset",
                "memory safety dataset",
            ],
        }

    def _recommended_actions(
        self,
        *,
        approved_for_learning: bool,
        feedback_summary: Dict[str, Any],
        benchmark_pack: StoryBenchmarkPack | None,
        smoke_test_report: StorySmokeTestReport | None,
        human_feedback: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        actions = []

        if not approved_for_learning:
            actions.append(
                {
                    "action_id": "stage_feedback_not_learning",
                    "action_type": "learning_gate",
                    "priority": "medium",
                    "instruction": "Keep feedback staged until smoke/benchmark/human gates are clean.",
                }
            )

        if feedback_summary.get("negative_feedback_count", 0) > 0:
            actions.append(
                {
                    "action_id": "review_negative_feedback",
                    "action_type": "feedback_review",
                    "priority": "medium",
                    "instruction": "Review negative feedback rows before using as positive training signals.",
                }
            )

        if smoke_test_report and not smoke_test_report.passed:
            actions.append(
                {
                    "action_id": "fix_smoke_before_learning",
                    "action_type": "smoke_gate",
                    "priority": "critical",
                    "instruction": "Fix smoke test failures before approving feedback for learning.",
                }
            )

        if benchmark_pack and benchmark_pack.score_summary.get("critical_failed_count", 0) > 0:
            actions.append(
                {
                    "action_id": "fix_benchmark_before_learning",
                    "action_type": "benchmark_gate",
                    "priority": "critical",
                    "instruction": "Fix critical benchmark failures before learning approval.",
                }
            )

        if human_feedback.get("exclude_from_learning") is True:
            actions.append(
                {
                    "action_id": "respect_human_exclusion",
                    "action_type": "human_feedback_gate",
                    "priority": "critical",
                    "instruction": "Human feedback excluded this item from learning.",
                }
            )

        return self._unique_dicts(actions, key="action_id")

    def _downstream_constraints(
        self,
        *,
        source_id: str,
        request_id: str,
        draft_id: str,
        approved_for_learning: bool,
        feedback_summary: Dict[str, Any],
    ) -> Dict[str, Any]:
        return {
            "source_id": source_id,
            "request_id": request_id,
            "draft_id": draft_id,
            "approved_for_learning": approved_for_learning,
            "feedback_summary": feedback_summary,
            "rules": [
                "Do not train models directly in Chunk 5.",
                "Do not use feedback for learning unless approved_for_learning is true.",
                "Preserve negative feedback rows as revision/risk examples, not positive labels.",
                "Chunk 8 may convert this package into datasets after governance checks.",
            ],
        }

    def _warnings(
        self,
        *,
        approved_for_learning: bool,
        feedback_summary: Dict[str, Any],
        benchmark_pack: StoryBenchmarkPack | None,
        smoke_test_report: StorySmokeTestReport | None,
    ) -> List[str]:
        warnings = []
        if not approved_for_learning:
            warnings.append("Learning feedback package is staged, not approved for learning.")
        if feedback_summary.get("negative_feedback_count", 0) > 0:
            warnings.append(f"{feedback_summary.get('negative_feedback_count')} negative feedback row(s) present.")
        if smoke_test_report and not smoke_test_report.passed:
            warnings.append("Smoke test did not pass.")
        if benchmark_pack and benchmark_pack.score_summary.get("critical_failed_count", 0) > 0:
            warnings.append("Benchmark pack has critical failures.")
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

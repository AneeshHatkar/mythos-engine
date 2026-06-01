from __future__ import annotations

from typing import Any, Dict, List

from backend.app.schemas.story_generation import (
    DraftComparisonReport,
    GeneratedStoryDeltaReport,
    GenerationContract,
    GenerationImprovementLoopDecision,
    OriginalityCopyRiskReport,
    StoryAntiGenericityReport,
    StoryContinuityValidationReport,
    StoryGenerationOrchestrationReport,
    StoryMemoryUpdateContract,
    StoryProvenanceRecord,
    StoryQualityScoreReport,
    StoryRevisionPlan,
)


class StoryGenerationOrchestrator:
    """Coordinates Chunk 5 story generation artifacts into one pipeline state.

    Locked Chunk 5.42. This orchestrator does not replace the individual engines.
    It verifies their outputs, decides whether the generated story can move
    forward, and builds a final handoff package for API/export/store layers.
    """

    engine_name = "story_generation.story_generation_orchestrator"

    REQUIRED_FINAL_ARTIFACTS = [
        "generation_contract",
        "quality_report",
        "anti_genericity_report",
        "continuity_report",
        "originality_report",
        "revision_plan",
        "comparison_report",
        "loop_decision",
        "provenance_record",
        "delta_report",
        "memory_update_contract",
    ]

    def orchestrate_generation_state(
        self,
        *,
        source_id: str,
        request_id: str = "",
        generation_contract: GenerationContract | None = None,
        quality_report: StoryQualityScoreReport | None = None,
        anti_genericity_report: StoryAntiGenericityReport | None = None,
        continuity_report: StoryContinuityValidationReport | None = None,
        originality_report: OriginalityCopyRiskReport | None = None,
        revision_plan: StoryRevisionPlan | None = None,
        comparison_report: DraftComparisonReport | None = None,
        loop_decision: GenerationImprovementLoopDecision | None = None,
        provenance_record: StoryProvenanceRecord | None = None,
        delta_report: GeneratedStoryDeltaReport | None = None,
        memory_update_contract: StoryMemoryUpdateContract | None = None,
        story_context: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        story_context = story_context or {}

        artifacts = {
            "generation_contract": generation_contract,
            "quality_report": quality_report,
            "anti_genericity_report": anti_genericity_report,
            "continuity_report": continuity_report,
            "originality_report": originality_report,
            "revision_plan": revision_plan,
            "comparison_report": comparison_report,
            "loop_decision": loop_decision,
            "provenance_record": provenance_record,
            "delta_report": delta_report,
            "memory_update_contract": memory_update_contract,
        }

        available_artifacts = self._available_artifacts(artifacts=artifacts)
        missing_inputs = self._missing_inputs(artifacts=artifacts)
        stage_results = self._pipeline_stage_results(artifacts=artifacts)
        quality_gate = self._quality_gate_summary(
            quality_report=quality_report,
            anti_genericity_report=anti_genericity_report,
            continuity_report=continuity_report,
        )
        risk_gate = self._risk_gate_summary(
            originality_report=originality_report,
            comparison_report=comparison_report,
            loop_decision=loop_decision,
            provenance_record=provenance_record,
        )
        memory_gate = self._memory_gate_summary(
            provenance_record=provenance_record,
            delta_report=delta_report,
            memory_update_contract=memory_update_contract,
        )

        blocked_reasons = self._blocked_reasons(
            missing_inputs=missing_inputs,
            quality_gate=quality_gate,
            risk_gate=risk_gate,
            memory_gate=memory_gate,
        )

        ready_for_export = self._ready_for_export(
            missing_inputs=missing_inputs,
            risk_gate=risk_gate,
            provenance_record=provenance_record,
        )
        ready_for_memory_apply = self._ready_for_memory_apply(
            memory_update_contract=memory_update_contract,
            provenance_record=provenance_record,
        )

        status = self._orchestration_status(
            missing_inputs=missing_inputs,
            blocked_reasons=blocked_reasons,
            ready_for_export=ready_for_export,
            ready_for_memory_apply=ready_for_memory_apply,
        )

        next_actions = self._next_actions(
            missing_inputs=missing_inputs,
            blocked_reasons=blocked_reasons,
            ready_for_export=ready_for_export,
            ready_for_memory_apply=ready_for_memory_apply,
            loop_decision=loop_decision,
            memory_update_contract=memory_update_contract,
        )

        report = StoryGenerationOrchestrationReport(
            orchestration_report_id=f"story_generation_orchestration_{source_id}_{request_id or 'default'}",
            source_id=source_id,
            request_id=request_id,
            orchestration_status=status,
            ready_for_export=ready_for_export,
            ready_for_memory_apply=ready_for_memory_apply,
            pipeline_stage_results=stage_results,
            required_inputs=list(self.REQUIRED_FINAL_ARTIFACTS),
            missing_inputs=missing_inputs,
            available_artifacts=available_artifacts,
            quality_gate_summary=quality_gate,
            risk_gate_summary=risk_gate,
            memory_gate_summary=memory_gate,
            final_handoff_package=self._final_handoff_package(
                source_id=source_id,
                request_id=request_id,
                available_artifacts=available_artifacts,
                ready_for_export=ready_for_export,
                ready_for_memory_apply=ready_for_memory_apply,
                story_context=story_context,
            ),
            next_actions=next_actions,
            blocked_reasons=blocked_reasons,
            downstream_constraints=self._downstream_constraints(
                source_id=source_id,
                request_id=request_id,
                ready_for_export=ready_for_export,
                ready_for_memory_apply=ready_for_memory_apply,
                missing_inputs=missing_inputs,
                blocked_reasons=blocked_reasons,
            ),
            warnings=self._warnings(
                missing_inputs=missing_inputs,
                blocked_reasons=blocked_reasons,
                ready_for_export=ready_for_export,
                ready_for_memory_apply=ready_for_memory_apply,
            ),
        )

        return {
            "success": True,
            "engine_name": self.engine_name,
            "story_generation_orchestration_report": report,
            "story_generation_orchestration_report_dict": report.model_dump(mode="json"),
            "handoff_to_next_engine": {
                "next_engine": "story_generation.story_generation_api_routes",
                "payload_keys": [
                    "story_generation_orchestration_report",
                    "final_handoff_package",
                    "story_context",
                ],
            },
        }

    def validate_orchestration_report(self, *, report: StoryGenerationOrchestrationReport) -> Dict[str, Any]:
        blockers: List[str] = []
        warnings: List[str] = []
        passed: List[str] = []

        if report.orchestration_report_id:
            passed.append("orchestration_report_id_present")
        else:
            blockers.append("orchestration_report_id missing")

        if report.source_id:
            passed.append("source_id_present")
        else:
            blockers.append("source_id missing")

        if report.pipeline_stage_results:
            passed.append("pipeline_stage_results_present")
        else:
            warnings.append("pipeline stage results missing")

        if report.final_handoff_package:
            passed.append("final_handoff_package_present")
        else:
            warnings.append("final handoff package missing")

        if report.downstream_constraints:
            passed.append("downstream_constraints_present")
        else:
            warnings.append("downstream constraints missing")

        if report.ready_for_export and report.blocked_reasons:
            blockers.append("cannot be ready for export while blocked reasons exist")

        if report.warnings:
            warnings.extend(report.warnings)

        return {
            "success": True,
            "engine_name": self.engine_name,
            "valid": not blockers,
            "blockers": blockers,
            "warnings": self._unique(warnings),
            "passed_checks": passed,
        }

    def summarize_orchestration_report(self, *, report: StoryGenerationOrchestrationReport) -> Dict[str, Any]:
        return {
            "success": True,
            "engine_name": self.engine_name,
            "summary": {
                "orchestration_report_id": report.orchestration_report_id,
                "source_id": report.source_id,
                "request_id": report.request_id,
                "orchestration_status": report.orchestration_status,
                "ready_for_export": report.ready_for_export,
                "ready_for_memory_apply": report.ready_for_memory_apply,
                "missing_input_count": len(report.missing_inputs),
                "stage_count": len(report.pipeline_stage_results),
                "blocked_reason_count": len(report.blocked_reasons),
                "next_action_count": len(report.next_actions),
                "warning_count": len(report.warnings),
            },
        }

    def build_orchestration_text(self, *, report: StoryGenerationOrchestrationReport) -> Dict[str, Any]:
        lines = [
            f"# Story Generation Orchestration Report: {report.source_id}",
            "",
            f"Request ID: {report.request_id}",
            f"Status: {report.orchestration_status}",
            f"Ready for export: {report.ready_for_export}",
            f"Ready for memory apply: {report.ready_for_memory_apply}",
            "",
            "## Pipeline Stages",
        ]

        for stage in report.pipeline_stage_results:
            lines.append(f"- {stage.get('stage_name')}: {stage.get('status')}")

        lines.append("")
        lines.append("## Missing Inputs")
        for item in report.missing_inputs:
            lines.append(f"- {item}")

        lines.append("")
        lines.append("## Blocked Reasons")
        for item in report.blocked_reasons:
            lines.append(f"- [{item.get('severity')}] {item.get('reason_type')}: {item.get('description')}")

        lines.append("")
        lines.append("## Next Actions")
        for item in report.next_actions:
            lines.append(f"- [{item.get('priority')}] {item.get('action_type')}: {item.get('instruction')}")

        return {
            "success": True,
            "engine_name": self.engine_name,
            "orchestration_text": "\n".join(lines),
        }

    def _available_artifacts(self, *, artifacts: Dict[str, Any]) -> Dict[str, Any]:
        available = {}
        for name, artifact in artifacts.items():
            if artifact is None:
                continue
            available[name] = {
                "available": True,
                "artifact_id": self._artifact_id(name=name, artifact=artifact),
                "artifact_type": name,
            }
        return available

    def _missing_inputs(self, *, artifacts: Dict[str, Any]) -> List[str]:
        return [name for name in self.REQUIRED_FINAL_ARTIFACTS if artifacts.get(name) is None]

    def _pipeline_stage_results(self, *, artifacts: Dict[str, Any]) -> List[Dict[str, Any]]:
        stages = []
        for index, name in enumerate(self.REQUIRED_FINAL_ARTIFACTS, start=1):
            artifact = artifacts.get(name)
            stages.append(
                {
                    "stage_number": index,
                    "stage_name": name,
                    "status": "available" if artifact is not None else "missing",
                    "artifact_id": self._artifact_id(name=name, artifact=artifact) if artifact is not None else None,
                }
            )
        return stages

    def _quality_gate_summary(
        self,
        *,
        quality_report: StoryQualityScoreReport | None,
        anti_genericity_report: StoryAntiGenericityReport | None,
        continuity_report: StoryContinuityValidationReport | None,
    ) -> Dict[str, Any]:
        return {
            "quality_available": quality_report is not None,
            "quality_score": getattr(quality_report, "overall_score", None),
            "quality_readiness": getattr(quality_report, "readiness_level", None),
            "anti_genericity_available": anti_genericity_report is not None,
            "anti_genericity_score": getattr(anti_genericity_report, "overall_anti_genericity_score", None),
            "genericity_risk_level": getattr(anti_genericity_report, "genericity_risk_level", None),
            "continuity_available": continuity_report is not None,
            "continuity_valid": getattr(continuity_report, "valid", None),
            "continuity_score": getattr(continuity_report, "continuity_score", None),
            "passed": self._quality_gate_passed(
                quality_report=quality_report,
                anti_genericity_report=anti_genericity_report,
                continuity_report=continuity_report,
            ),
        }

    def _risk_gate_summary(
        self,
        *,
        originality_report: OriginalityCopyRiskReport | None,
        comparison_report: DraftComparisonReport | None,
        loop_decision: GenerationImprovementLoopDecision | None,
        provenance_record: StoryProvenanceRecord | None,
    ) -> Dict[str, Any]:
        return {
            "originality_available": originality_report is not None,
            "safe_for_export": getattr(originality_report, "safe_for_export", None),
            "copy_risk_level": getattr(originality_report, "copy_risk_level", None),
            "comparison_available": comparison_report is not None,
            "comparison_approved": getattr(comparison_report, "approved", None),
            "regression_risk_score": getattr(comparison_report, "regression_risk_score", None),
            "loop_available": loop_decision is not None,
            "loop_action": getattr(loop_decision, "action", None),
            "loop_approved_for_handoff": getattr(loop_decision, "approved_for_handoff", None),
            "provenance_available": provenance_record is not None,
            "provenance_status": getattr(provenance_record, "provenance_status", None),
            "provenance_approved_for_export": getattr(provenance_record, "approved_for_export", None),
            "passed": self._risk_gate_passed(
                originality_report=originality_report,
                comparison_report=comparison_report,
                loop_decision=loop_decision,
                provenance_record=provenance_record,
            ),
        }

    def _memory_gate_summary(
        self,
        *,
        provenance_record: StoryProvenanceRecord | None,
        delta_report: GeneratedStoryDeltaReport | None,
        memory_update_contract: StoryMemoryUpdateContract | None,
    ) -> Dict[str, Any]:
        return {
            "provenance_available": provenance_record is not None,
            "provenance_approved_for_memory": getattr(provenance_record, "approved_for_memory_update", None),
            "delta_available": delta_report is not None,
            "memory_candidate_count": len(getattr(delta_report, "memory_update_candidates", []) or []),
            "memory_contract_available": memory_update_contract is not None,
            "memory_contract_approved": getattr(memory_update_contract, "approved_for_apply", None),
            "memory_contract_status": getattr(memory_update_contract, "contract_status", None),
            "passed": self._memory_gate_passed(
                provenance_record=provenance_record,
                delta_report=delta_report,
                memory_update_contract=memory_update_contract,
            ),
        }

    def _quality_gate_passed(
        self,
        *,
        quality_report: StoryQualityScoreReport | None,
        anti_genericity_report: StoryAntiGenericityReport | None,
        continuity_report: StoryContinuityValidationReport | None,
    ) -> bool:
        if quality_report and quality_report.readiness_level == "blocked":
            return False
        if anti_genericity_report and anti_genericity_report.genericity_risk_level == "critical":
            return False
        if continuity_report and not continuity_report.valid:
            return False
        return all(item is not None for item in [quality_report, anti_genericity_report, continuity_report])

    def _risk_gate_passed(
        self,
        *,
        originality_report: OriginalityCopyRiskReport | None,
        comparison_report: DraftComparisonReport | None,
        loop_decision: GenerationImprovementLoopDecision | None,
        provenance_record: StoryProvenanceRecord | None,
    ) -> bool:
        if not all(item is not None for item in [originality_report, comparison_report, loop_decision, provenance_record]):
            return False
        return bool(
            originality_report.safe_for_export
            and comparison_report.approved
            and loop_decision.approved_for_handoff
            and provenance_record.approved_for_export
        )

    def _memory_gate_passed(
        self,
        *,
        provenance_record: StoryProvenanceRecord | None,
        delta_report: GeneratedStoryDeltaReport | None,
        memory_update_contract: StoryMemoryUpdateContract | None,
    ) -> bool:
        if not all(item is not None for item in [provenance_record, delta_report, memory_update_contract]):
            return False
        return bool(
            provenance_record.approved_for_memory_update
            and memory_update_contract.approved_for_apply
        )

    def _blocked_reasons(
        self,
        *,
        missing_inputs: List[str],
        quality_gate: Dict[str, Any],
        risk_gate: Dict[str, Any],
        memory_gate: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        reasons = []

        if missing_inputs:
            reasons.append(
                {
                    "reason_id": "missing_required_inputs",
                    "reason_type": "missing_inputs",
                    "severity": "high",
                    "description": f"Missing required artifacts: {missing_inputs}",
                }
            )

        if not quality_gate.get("passed"):
            reasons.append(
                {
                    "reason_id": "quality_gate_not_passed",
                    "reason_type": "quality_gate",
                    "severity": "high",
                    "description": "Quality, anti-genericity, or continuity gate has not passed.",
                }
            )

        if not risk_gate.get("passed"):
            reasons.append(
                {
                    "reason_id": "risk_gate_not_passed",
                    "reason_type": "risk_gate",
                    "severity": "critical",
                    "description": "Originality, comparison, loop, or provenance export gate has not passed.",
                }
            )

        if not memory_gate.get("passed"):
            reasons.append(
                {
                    "reason_id": "memory_gate_not_passed",
                    "reason_type": "memory_gate",
                    "severity": "medium",
                    "description": "Memory update gate has not passed.",
                }
            )

        return reasons

    def _ready_for_export(
        self,
        *,
        missing_inputs: List[str],
        risk_gate: Dict[str, Any],
        provenance_record: StoryProvenanceRecord | None,
    ) -> bool:
        return bool(not missing_inputs and risk_gate.get("passed") and provenance_record and provenance_record.approved_for_export)

    def _ready_for_memory_apply(
        self,
        *,
        memory_update_contract: StoryMemoryUpdateContract | None,
        provenance_record: StoryProvenanceRecord | None,
    ) -> bool:
        return bool(
            memory_update_contract
            and memory_update_contract.approved_for_apply
            and provenance_record
            and provenance_record.approved_for_memory_update
        )

    def _orchestration_status(
        self,
        *,
        missing_inputs: List[str],
        blocked_reasons: List[Dict[str, Any]],
        ready_for_export: bool,
        ready_for_memory_apply: bool,
    ) -> str:
        if ready_for_export and ready_for_memory_apply:
            return "ready"
        if any(item.get("severity") == "critical" for item in blocked_reasons):
            return "blocked"
        if missing_inputs:
            return "incomplete"
        return "needs_review"

    def _next_actions(
        self,
        *,
        missing_inputs: List[str],
        blocked_reasons: List[Dict[str, Any]],
        ready_for_export: bool,
        ready_for_memory_apply: bool,
        loop_decision: GenerationImprovementLoopDecision | None,
        memory_update_contract: StoryMemoryUpdateContract | None,
    ) -> List[Dict[str, Any]]:
        actions = []

        for item in missing_inputs:
            actions.append(
                {
                    "action_id": f"create_missing_{item}",
                    "action_type": "create_missing_artifact",
                    "priority": "high",
                    "instruction": f"Run or supply artifact: {item}.",
                }
            )

        if loop_decision and not loop_decision.approved_for_handoff:
            actions.append(
                {
                    "action_id": "continue_improvement_loop",
                    "action_type": "improvement_loop",
                    "priority": loop_decision.next_priority,
                    "instruction": f"Continue loop action: {loop_decision.action}.",
                }
            )

        if memory_update_contract and not memory_update_contract.approved_for_apply:
            actions.append(
                {
                    "action_id": "resolve_memory_contract",
                    "action_type": "memory_contract",
                    "priority": "medium",
                    "instruction": f"Resolve memory contract status: {memory_update_contract.contract_status}.",
                }
            )

        if ready_for_export:
            actions.append(
                {
                    "action_id": "handoff_to_export_store",
                    "action_type": "export_store",
                    "priority": "low",
                    "instruction": "Create export artifact from approved story generation package.",
                }
            )

        if ready_for_memory_apply:
            actions.append(
                {
                    "action_id": "handoff_to_memory_apply",
                    "action_type": "memory_apply",
                    "priority": "low",
                    "instruction": "Apply approved memory update contract.",
                }
            )

        if not actions and blocked_reasons:
            actions.append(
                {
                    "action_id": "manual_review_blockers",
                    "action_type": "manual_review",
                    "priority": "critical",
                    "instruction": "Review blocked reasons before continuing.",
                }
            )

        return self._unique_dicts(actions, key="action_id")

    def _final_handoff_package(
        self,
        *,
        source_id: str,
        request_id: str,
        available_artifacts: Dict[str, Any],
        ready_for_export: bool,
        ready_for_memory_apply: bool,
        story_context: Dict[str, Any],
    ) -> Dict[str, Any]:
        return {
            "source_id": source_id,
            "request_id": request_id,
            "ready_for_export": ready_for_export,
            "ready_for_memory_apply": ready_for_memory_apply,
            "artifact_ids": {
                name: payload.get("artifact_id")
                for name, payload in available_artifacts.items()
            },
            "story_context_keys": sorted(story_context.keys()),
        }

    def _downstream_constraints(
        self,
        *,
        source_id: str,
        request_id: str,
        ready_for_export: bool,
        ready_for_memory_apply: bool,
        missing_inputs: List[str],
        blocked_reasons: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        return {
            "source_id": source_id,
            "request_id": request_id,
            "ready_for_export": ready_for_export,
            "ready_for_memory_apply": ready_for_memory_apply,
            "missing_inputs": missing_inputs,
            "blocked_reason_ids": [item.get("reason_id") for item in blocked_reasons],
            "rules": [
                "Do not export unless ready_for_export is true.",
                "Do not apply memory unless ready_for_memory_apply is true.",
                "Do not skip quality, risk, provenance, delta, or memory gates.",
                "API routes must return orchestration status and blocked reasons.",
            ],
        }

    def _warnings(
        self,
        *,
        missing_inputs: List[str],
        blocked_reasons: List[Dict[str, Any]],
        ready_for_export: bool,
        ready_for_memory_apply: bool,
    ) -> List[str]:
        warnings = []
        if missing_inputs:
            warnings.append(f"{len(missing_inputs)} required artifact(s) missing.")
        if blocked_reasons:
            warnings.append(f"{len(blocked_reasons)} blocked reason(s) present.")
        if not ready_for_export:
            warnings.append("Not ready for export.")
        if not ready_for_memory_apply:
            warnings.append("Not ready for automatic memory apply.")
        return warnings

    def _artifact_id(self, *, name: str, artifact: Any) -> str | None:
        id_fields = {
            "generation_contract": ["contract_id", "generation_contract_id"],
            "quality_report": ["quality_report_id"],
            "anti_genericity_report": ["anti_genericity_report_id", "report_id"],
            "continuity_report": ["continuity_report_id"],
            "originality_report": ["originality_report_id"],
            "revision_plan": ["revision_plan_id"],
            "comparison_report": ["comparison_report_id"],
            "loop_decision": ["loop_decision_id"],
            "provenance_record": ["provenance_record_id", "provenance_id"],
            "delta_report": ["delta_report_id"],
            "memory_update_contract": ["memory_contract_id", "memory_update_contract_id"],
        }
        for field in id_fields.get(name, []):
            value = getattr(artifact, field, None)
            if value:
                return str(value)
        return None

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

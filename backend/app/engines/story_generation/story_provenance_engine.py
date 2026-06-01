from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List

from backend.app.schemas.story_generation import (
    DraftComparisonReport,
    GenerationImprovementLoopDecision,
    OriginalityCopyRiskReport,
    StoryAntiGenericityReport,
    StoryContinuityValidationReport,
    StoryProvenanceRecord,
    StoryQualityScoreReport,
    StoryRevisionPlan,
)


class StoryProvenanceEngine:
    """Records generation provenance across story generation and revision.

    Locked Chunk 5.39. This engine creates an auditable trace of which engines,
    reports, decisions, risks, protected elements, and output artifacts produced
    the current draft.
    """

    engine_name = "story_generation.story_provenance_engine"

    def build_provenance_record(
        self,
        *,
        source_id: str,
        draft_id: str,
        generated_text: str | None = None,
        input_references: List[Dict[str, Any]] | None = None,
        output_references: List[Dict[str, Any]] | None = None,
        quality_report: StoryQualityScoreReport | None = None,
        anti_genericity_report: StoryAntiGenericityReport | None = None,
        continuity_report: StoryContinuityValidationReport | None = None,
        originality_report: OriginalityCopyRiskReport | None = None,
        revision_plan: StoryRevisionPlan | None = None,
        comparison_report: DraftComparisonReport | None = None,
        loop_decision: GenerationImprovementLoopDecision | None = None,
        story_context: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        input_references = input_references or []
        output_references = output_references or []
        story_context = story_context or {}

        engine_trace = self._engine_trace(
            quality_report=quality_report,
            anti_genericity_report=anti_genericity_report,
            continuity_report=continuity_report,
            originality_report=originality_report,
            revision_plan=revision_plan,
            comparison_report=comparison_report,
            loop_decision=loop_decision,
        )

        decision_trace = self._decision_trace(
            revision_plan=revision_plan,
            comparison_report=comparison_report,
            loop_decision=loop_decision,
        )

        risk_snapshot = self._risk_snapshot(
            anti_genericity_report=anti_genericity_report,
            continuity_report=continuity_report,
            originality_report=originality_report,
            comparison_report=comparison_report,
            loop_decision=loop_decision,
        )

        protected_snapshot = self._protected_elements_snapshot(
            revision_plan=revision_plan,
            continuity_report=continuity_report,
            originality_report=originality_report,
            comparison_report=comparison_report,
        )

        memory_candidates = self._memory_update_candidates(
            generated_text=generated_text,
            continuity_report=continuity_report,
            originality_report=originality_report,
            comparison_report=comparison_report,
            loop_decision=loop_decision,
            story_context=story_context,
        )

        approved_for_memory = self._approved_for_memory_update(
            loop_decision=loop_decision,
            continuity_report=continuity_report,
            originality_report=originality_report,
            comparison_report=comparison_report,
        )

        approved_for_export = self._approved_for_export(
            loop_decision=loop_decision,
            originality_report=originality_report,
            comparison_report=comparison_report,
        )

        provenance_id = f"story_provenance_{source_id}_{draft_id}"

        record = StoryProvenanceRecord(
            provenance_id=provenance_id,
            provenance_record_id=provenance_id,
            source_id=source_id,
            draft_id=draft_id,
            provenance_status=self._provenance_status(
                approved_for_memory_update=approved_for_memory,
                approved_for_export=approved_for_export,
                risk_snapshot=risk_snapshot,
            ),
            approved_for_memory_update=approved_for_memory,
            approved_for_export=approved_for_export,
            engine_trace=engine_trace,
            input_references=input_references,
            output_references=output_references,
            decision_trace=decision_trace,
            quality_trace=self._quality_trace(quality_report=quality_report),
            continuity_trace=self._continuity_trace(continuity_report=continuity_report),
            originality_trace=self._originality_trace(
                anti_genericity_report=anti_genericity_report,
                originality_report=originality_report,
            ),
            revision_trace=self._revision_trace(
                revision_plan=revision_plan,
                comparison_report=comparison_report,
                loop_decision=loop_decision,
            ),
            memory_update_candidates=memory_candidates,
            protected_elements_snapshot=protected_snapshot,
            risk_snapshot=risk_snapshot,
            audit_summary=self._audit_summary(
                engine_trace=engine_trace,
                decision_trace=decision_trace,
                risk_snapshot=risk_snapshot,
                memory_candidates=memory_candidates,
                approved_for_memory_update=approved_for_memory,
                approved_for_export=approved_for_export,
            ),
            downstream_constraints=self._downstream_constraints(
                source_id=source_id,
                draft_id=draft_id,
                approved_for_memory_update=approved_for_memory,
                approved_for_export=approved_for_export,
                memory_candidates=memory_candidates,
                protected_snapshot=protected_snapshot,
            ),
            warnings=self._warnings(
                generated_text=generated_text,
                engine_trace=engine_trace,
                risk_snapshot=risk_snapshot,
                loop_decision=loop_decision,
                originality_report=originality_report,
                continuity_report=continuity_report,
            ),
        )

        return {
            "success": True,
            "engine_name": self.engine_name,
            "story_provenance_record": record,
            "story_provenance_record_dict": record.model_dump(mode="json"),
            "handoff_to_next_engine": {
                "next_engine": "story_generation.generated_scene_delta_extractor",
                "payload_keys": [
                    "story_provenance_record",
                    "approved_draft",
                    "story_context",
                ],
            },
        }

    def validate_provenance_record(self, *, record: StoryProvenanceRecord) -> Dict[str, Any]:
        blockers: List[str] = []
        warnings: List[str] = []
        passed: List[str] = []

        if record.provenance_record_id:
            passed.append("provenance_record_id_present")
        else:
            blockers.append("provenance_record_id missing")

        if record.source_id and record.draft_id:
            passed.append("source_and_draft_ids_present")
        else:
            blockers.append("source_id or draft_id missing")

        if record.engine_trace:
            passed.append("engine_trace_present")
        else:
            warnings.append("engine trace missing")

        if record.audit_summary:
            passed.append("audit_summary_present")
        else:
            warnings.append("audit summary missing")

        if record.downstream_constraints:
            passed.append("downstream_constraints_present")
        else:
            warnings.append("downstream constraints missing")

        if record.risk_snapshot:
            warnings.append("risk snapshot contains active risk records")

        if record.warnings:
            warnings.extend(record.warnings)

        return {
            "success": True,
            "engine_name": self.engine_name,
            "valid": not blockers,
            "blockers": blockers,
            "warnings": self._unique(warnings),
            "passed_checks": passed,
        }

    def summarize_provenance_record(self, *, record: StoryProvenanceRecord) -> Dict[str, Any]:
        return {
            "success": True,
            "engine_name": self.engine_name,
            "summary": {
                "provenance_record_id": record.provenance_record_id,
                "source_id": record.source_id,
                "draft_id": record.draft_id,
                "provenance_status": record.provenance_status,
                "approved_for_memory_update": record.approved_for_memory_update,
                "approved_for_export": record.approved_for_export,
                "engine_trace_count": len(record.engine_trace),
                "decision_trace_count": len(record.decision_trace),
                "memory_candidate_count": len(record.memory_update_candidates),
                "protected_element_count": len(record.protected_elements_snapshot),
                "risk_count": len(record.risk_snapshot),
                "warning_count": len(record.warnings),
            },
        }

    def build_provenance_text(self, *, record: StoryProvenanceRecord) -> Dict[str, Any]:
        lines = [
            f"# Story Provenance Record: {record.source_id}",
            "",
            f"Draft ID: {record.draft_id}",
            f"Status: {record.provenance_status}",
            f"Approved for memory update: {record.approved_for_memory_update}",
            f"Approved for export: {record.approved_for_export}",
            "",
            "## Engine Trace",
        ]

        for item in record.engine_trace:
            lines.append(f"- {item.get('engine_name')}: {item.get('artifact_id')}")

        lines.append("")
        lines.append("## Decision Trace")
        for item in record.decision_trace:
            lines.append(f"- {item.get('decision_type')}: {item.get('decision')}")

        lines.append("")
        lines.append("## Memory Update Candidates")
        for item in record.memory_update_candidates:
            lines.append(f"- {item.get('candidate_type')}: {item.get('value')}")

        lines.append("")
        lines.append("## Risks")
        for item in record.risk_snapshot:
            lines.append(f"- [{item.get('severity')}] {item.get('risk_type')}: {item.get('description')}")

        return {
            "success": True,
            "engine_name": self.engine_name,
            "provenance_text": "\n".join(lines),
        }

    def _engine_trace(
        self,
        *,
        quality_report: StoryQualityScoreReport | None,
        anti_genericity_report: StoryAntiGenericityReport | None,
        continuity_report: StoryContinuityValidationReport | None,
        originality_report: OriginalityCopyRiskReport | None,
        revision_plan: StoryRevisionPlan | None,
        comparison_report: DraftComparisonReport | None,
        loop_decision: GenerationImprovementLoopDecision | None,
    ) -> List[Dict[str, Any]]:
        trace = []

        def add(engine: str, artifact_id: str | None, artifact_type: str, status: str = "available"):
            if artifact_id:
                trace.append(
                    {
                        "trace_id": f"trace_{self._safe_id(engine)}_{self._safe_id(artifact_id)}",
                        "engine_name": engine,
                        "artifact_id": artifact_id,
                        "artifact_type": artifact_type,
                        "status": status,
                        "timestamp_utc": self._now(),
                    }
                )

        add("story_generation.story_quality_scorer", getattr(quality_report, "quality_report_id", None), "quality_report")
        add("story_generation.story_anti_genericity_validator", getattr(anti_genericity_report, "anti_genericity_report_id", None), "anti_genericity_report")
        add("story_generation.story_continuity_validator", getattr(continuity_report, "continuity_report_id", None), "continuity_report")
        add("story_generation.originality_copy_risk_guard", getattr(originality_report, "originality_report_id", None), "originality_report")
        add("story_generation.story_revision_engine", getattr(revision_plan, "revision_plan_id", None), "revision_plan")
        add("story_generation.draft_comparison_engine", getattr(comparison_report, "comparison_report_id", None), "draft_comparison_report")
        add("story_generation.generation_improvement_loop", getattr(loop_decision, "loop_decision_id", None), "loop_decision")

        return trace

    def _decision_trace(
        self,
        *,
        revision_plan: StoryRevisionPlan | None,
        comparison_report: DraftComparisonReport | None,
        loop_decision: GenerationImprovementLoopDecision | None,
    ) -> List[Dict[str, Any]]:
        decisions = []

        if revision_plan:
            decisions.append(
                {
                    "decision_id": "revision_plan_decision",
                    "decision_type": "revision_plan",
                    "decision": revision_plan.revision_mode,
                    "priority": revision_plan.overall_revision_priority,
                    "description": "Revision plan selected revision mode and task priority.",
                }
            )

        if comparison_report:
            decisions.append(
                {
                    "decision_id": "draft_comparison_decision",
                    "decision_type": "draft_comparison",
                    "decision": "approved" if comparison_report.approved else "not_approved",
                    "priority": "high" if comparison_report.regression_risk_score > 0.35 else "medium",
                    "description": "Draft comparison evaluated revised draft approval readiness.",
                }
            )

        if loop_decision:
            decisions.append(
                {
                    "decision_id": "improvement_loop_decision",
                    "decision_type": "improvement_loop",
                    "decision": loop_decision.action,
                    "priority": loop_decision.next_priority,
                    "description": loop_decision.decision_reason,
                }
            )

        return decisions

    def _quality_trace(self, *, quality_report: StoryQualityScoreReport | None) -> Dict[str, Any]:
        if not quality_report:
            return {"available": False}

        return {
            "available": True,
            "quality_report_id": quality_report.quality_report_id,
            "overall_score": quality_report.overall_score,
            "readiness_level": quality_report.readiness_level,
            "anti_generic_score": quality_report.anti_generic_score,
            "revision_priority_count": len(quality_report.revision_priorities),
        }

    def _continuity_trace(self, *, continuity_report: StoryContinuityValidationReport | None) -> Dict[str, Any]:
        if not continuity_report:
            return {"available": False}

        return {
            "available": True,
            "continuity_report_id": continuity_report.continuity_report_id,
            "valid": continuity_report.valid,
            "continuity_score": continuity_report.continuity_score,
            "readiness_level": continuity_report.readiness_level,
            "checked_character_ids": continuity_report.checked_character_ids,
            "checked_secret_ids": continuity_report.checked_secret_ids,
            "checked_causal_ids": continuity_report.checked_causal_ids,
            "checked_world_details": continuity_report.checked_world_details,
        }

    def _originality_trace(
        self,
        *,
        anti_genericity_report: StoryAntiGenericityReport | None,
        originality_report: OriginalityCopyRiskReport | None,
    ) -> Dict[str, Any]:
        return {
            "anti_genericity": {
                "available": anti_genericity_report is not None,
                "report_id": getattr(anti_genericity_report, "anti_genericity_report_id", None),
                "score": getattr(anti_genericity_report, "overall_anti_genericity_score", None),
                "risk_level": getattr(anti_genericity_report, "genericity_risk_level", None),
            },
            "copy_risk": {
                "available": originality_report is not None,
                "report_id": getattr(originality_report, "originality_report_id", None),
                "safe_for_export": getattr(originality_report, "safe_for_export", None),
                "score": getattr(originality_report, "overall_originality_score", None),
                "risk_level": getattr(originality_report, "copy_risk_level", None),
            },
        }

    def _revision_trace(
        self,
        *,
        revision_plan: StoryRevisionPlan | None,
        comparison_report: DraftComparisonReport | None,
        loop_decision: GenerationImprovementLoopDecision | None,
    ) -> Dict[str, Any]:
        return {
            "revision_plan": {
                "available": revision_plan is not None,
                "revision_plan_id": getattr(revision_plan, "revision_plan_id", None),
                "mode": getattr(revision_plan, "revision_mode", None),
                "priority": getattr(revision_plan, "overall_revision_priority", None),
                "rewrite_step_count": len(getattr(revision_plan, "rewrite_order", []) or []),
            },
            "comparison": {
                "available": comparison_report is not None,
                "comparison_report_id": getattr(comparison_report, "comparison_report_id", None),
                "approved": getattr(comparison_report, "approved", None),
                "improvement_score": getattr(comparison_report, "improvement_score", None),
                "regression_risk_score": getattr(comparison_report, "regression_risk_score", None),
            },
            "loop": {
                "available": loop_decision is not None,
                "loop_decision_id": getattr(loop_decision, "loop_decision_id", None),
                "action": getattr(loop_decision, "action", None),
                "approved_for_handoff": getattr(loop_decision, "approved_for_handoff", None),
                "stop_loop": getattr(loop_decision, "stop_loop", None),
            },
        }

    def _risk_snapshot(
        self,
        *,
        anti_genericity_report: StoryAntiGenericityReport | None,
        continuity_report: StoryContinuityValidationReport | None,
        originality_report: OriginalityCopyRiskReport | None,
        comparison_report: DraftComparisonReport | None,
        loop_decision: GenerationImprovementLoopDecision | None,
    ) -> List[Dict[str, Any]]:
        risks = []

        if anti_genericity_report and anti_genericity_report.genericity_risk_level in {"high", "critical"}:
            risks.append(
                {
                    "risk_id": "risk_anti_genericity",
                    "risk_type": "genericity",
                    "severity": anti_genericity_report.genericity_risk_level,
                    "description": f"Anti-genericity risk is {anti_genericity_report.genericity_risk_level}.",
                }
            )

        if continuity_report and not continuity_report.valid:
            risks.append(
                {
                    "risk_id": "risk_continuity_invalid",
                    "risk_type": "continuity",
                    "severity": "critical",
                    "description": "Continuity report is invalid.",
                }
            )

        if originality_report and not originality_report.safe_for_export:
            risks.append(
                {
                    "risk_id": "risk_copy_export",
                    "risk_type": "copy_risk",
                    "severity": originality_report.copy_risk_level,
                    "description": "Originality/copy-risk report is not safe for export.",
                }
            )

        if comparison_report:
            for flag in getattr(comparison_report, "regression_flags", []) or []:
                risks.append(
                    {
                        "risk_id": f"risk_{flag.get('flag_id')}",
                        "risk_type": flag.get("flag_type"),
                        "severity": flag.get("severity", "medium"),
                        "description": flag.get("description", "Regression flag detected."),
                    }
                )

        if loop_decision and loop_decision.action in {"blocked_until_manual_review", "stop_max_iterations"}:
            risks.append(
                {
                    "risk_id": "risk_loop_not_approved",
                    "risk_type": "improvement_loop",
                    "severity": "high",
                    "description": f"Improvement loop ended with action {loop_decision.action}.",
                }
            )

        return self._unique_dicts(risks, key="risk_id")

    def _protected_elements_snapshot(
        self,
        *,
        revision_plan: StoryRevisionPlan | None,
        continuity_report: StoryContinuityValidationReport | None,
        originality_report: OriginalityCopyRiskReport | None,
        comparison_report: DraftComparisonReport | None,
    ) -> List[Dict[str, Any]]:
        protected = []

        if revision_plan:
            protected.extend(revision_plan.protected_elements)

        if continuity_report:
            for character_id in continuity_report.checked_character_ids:
                protected.append({"element_id": f"continuity_character_{character_id}", "element_type": "character", "value": character_id})
            for secret_id in continuity_report.checked_secret_ids:
                protected.append({"element_id": f"continuity_secret_{secret_id}", "element_type": "secret", "value": secret_id})
            for causal_id in continuity_report.checked_causal_ids:
                protected.append({"element_id": f"continuity_causal_{causal_id}", "element_type": "causal", "value": causal_id})
            for detail in continuity_report.checked_world_details:
                protected.append({"element_id": f"continuity_world_{self._safe_id(detail)}", "element_type": "world_detail", "value": detail})

        if originality_report:
            for index, item in enumerate(originality_report.approved_original_elements, start=1):
                protected.append({"element_id": f"originality_approved_{index}", "element_type": "approved_original_element", "value": item})

        if comparison_report:
            protected.extend(getattr(comparison_report, "preserved_elements", []) or [])

        return self._unique_dicts(protected, key="element_id")

    def _memory_update_candidates(
        self,
        *,
        generated_text: str | None,
        continuity_report: StoryContinuityValidationReport | None,
        originality_report: OriginalityCopyRiskReport | None,
        comparison_report: DraftComparisonReport | None,
        loop_decision: GenerationImprovementLoopDecision | None,
        story_context: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        candidates = []

        if continuity_report:
            for character_id in continuity_report.checked_character_ids:
                candidates.append({"candidate_id": f"memory_character_{character_id}", "candidate_type": "character_state", "value": character_id})
            for secret_id in continuity_report.checked_secret_ids:
                candidates.append({"candidate_id": f"memory_secret_{secret_id}", "candidate_type": "secret_state", "value": secret_id})
            for causal_id in continuity_report.checked_causal_ids:
                candidates.append({"candidate_id": f"memory_causal_{causal_id}", "candidate_type": "causal_state", "value": causal_id})
            for detail in continuity_report.checked_world_details:
                candidates.append({"candidate_id": f"memory_world_{self._safe_id(detail)}", "candidate_type": "world_state", "value": detail})

        if originality_report:
            for index, item in enumerate(originality_report.approved_original_elements, start=1):
                candidates.append({"candidate_id": f"memory_original_element_{index}", "candidate_type": "originality_evidence", "value": item})

        if comparison_report and comparison_report.approved:
            candidates.append({"candidate_id": "memory_revision_approved", "candidate_type": "revision_status", "value": "approved"})

        if loop_decision and loop_decision.approved_for_handoff:
            candidates.append({"candidate_id": "memory_loop_approved", "candidate_type": "loop_status", "value": loop_decision.action})

        if generated_text:
            candidates.append(
                {
                    "candidate_id": "memory_generated_text_summary",
                    "candidate_type": "draft_summary",
                    "value": generated_text[:500],
                }
            )

        for item in story_context.get("extra_memory_candidates", []):
            if isinstance(item, dict) and item.get("candidate_id"):
                candidates.append(item)

        return self._unique_dicts(candidates, key="candidate_id")

    def _approved_for_memory_update(
        self,
        *,
        loop_decision: GenerationImprovementLoopDecision | None,
        continuity_report: StoryContinuityValidationReport | None,
        originality_report: OriginalityCopyRiskReport | None,
        comparison_report: DraftComparisonReport | None,
    ) -> bool:
        if loop_decision and not loop_decision.approved_for_handoff:
            return False
        if comparison_report and not comparison_report.approved:
            return False
        if continuity_report and not continuity_report.valid:
            return False
        if originality_report and not originality_report.safe_for_export:
            return False
        return True

    def _approved_for_export(
        self,
        *,
        loop_decision: GenerationImprovementLoopDecision | None,
        originality_report: OriginalityCopyRiskReport | None,
        comparison_report: DraftComparisonReport | None,
    ) -> bool:
        if originality_report and not originality_report.safe_for_export:
            return False
        if comparison_report and not comparison_report.approved:
            return False
        if loop_decision and not loop_decision.approved_for_handoff:
            return False
        return True

    def _provenance_status(
        self,
        *,
        approved_for_memory_update: bool,
        approved_for_export: bool,
        risk_snapshot: List[Dict[str, Any]],
    ) -> str:
        if any(item.get("severity") in {"critical", "blocker"} for item in risk_snapshot):
            return "blocked"
        if approved_for_memory_update and approved_for_export:
            return "approved"
        if approved_for_memory_update:
            return "memory_only"
        return "recorded_needs_review"

    def _audit_summary(
        self,
        *,
        engine_trace: List[Dict[str, Any]],
        decision_trace: List[Dict[str, Any]],
        risk_snapshot: List[Dict[str, Any]],
        memory_candidates: List[Dict[str, Any]],
        approved_for_memory_update: bool,
        approved_for_export: bool,
    ) -> Dict[str, Any]:
        return {
            "engine_count": len(engine_trace),
            "decision_count": len(decision_trace),
            "risk_count": len(risk_snapshot),
            "memory_candidate_count": len(memory_candidates),
            "approved_for_memory_update": approved_for_memory_update,
            "approved_for_export": approved_for_export,
            "created_at_utc": self._now(),
        }

    def _downstream_constraints(
        self,
        *,
        source_id: str,
        draft_id: str,
        approved_for_memory_update: bool,
        approved_for_export: bool,
        memory_candidates: List[Dict[str, Any]],
        protected_snapshot: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        return {
            "source_id": source_id,
            "draft_id": draft_id,
            "approved_for_memory_update": approved_for_memory_update,
            "approved_for_export": approved_for_export,
            "memory_candidate_ids": [item.get("candidate_id") for item in memory_candidates],
            "protected_element_ids": [item.get("element_id") for item in protected_snapshot],
            "rules": [
                "Only approved provenance records may update long-form story memory.",
                "Do not export drafts whose provenance status is blocked.",
                "Preserve protected elements in delta extraction and memory update.",
                "Carry provenance record ID into export and benchmark artifacts.",
            ],
        }

    def _warnings(
        self,
        *,
        generated_text: str | None,
        engine_trace: List[Dict[str, Any]],
        risk_snapshot: List[Dict[str, Any]],
        loop_decision: GenerationImprovementLoopDecision | None,
        originality_report: OriginalityCopyRiskReport | None,
        continuity_report: StoryContinuityValidationReport | None,
    ) -> List[str]:
        warnings = []

        if not generated_text:
            warnings.append("No generated text supplied; provenance records structured artifacts only.")

        if not engine_trace:
            warnings.append("No engine trace artifacts supplied.")

        if risk_snapshot:
            warnings.append(f"{len(risk_snapshot)} provenance risk(s) recorded.")

        if loop_decision and not loop_decision.approved_for_handoff:
            warnings.append("Improvement loop has not approved handoff.")

        if originality_report and not originality_report.safe_for_export:
            warnings.append("Originality report is not safe for export.")

        if continuity_report and not continuity_report.valid:
            warnings.append("Continuity report is invalid.")

        return warnings

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _safe_id(self, value: Any) -> str:
        return "".join(ch.lower() if ch.isalnum() else "_" for ch in str(value)).strip("_")[:80] or "item"

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

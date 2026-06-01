from __future__ import annotations

from typing import Any, Dict, List

from backend.app.schemas.story_generation import (
    DraftComparisonReport,
    GenerationImprovementLoopDecision,
    StoryRevisionPlan,
)


class GenerationImprovementLoop:
    """Controls iterative story improvement after draft comparison.

    Locked Chunk 5.38. This engine decides whether a revised draft is approved,
    needs another targeted pass, needs deep revision, or must stop because
    copy-risk/continuity/export blockers remain.
    """

    engine_name = "story_generation.generation_improvement_loop"

    def decide_next_step(
        self,
        *,
        source_id: str,
        comparison_report: DraftComparisonReport,
        revision_plan: StoryRevisionPlan | None = None,
        current_iteration: int = 1,
        max_iterations: int = 3,
        story_context: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        story_context = story_context or {}

        required_actions = self._required_actions(
            comparison_report=comparison_report,
            revision_plan=revision_plan,
        )
        resolved_items = self._resolved_items(comparison_report=comparison_report)
        unresolved_items = self._unresolved_items(
            comparison_report=comparison_report,
            revision_plan=revision_plan,
        )

        loop_metrics = self._loop_metrics(
            comparison_report=comparison_report,
            current_iteration=current_iteration,
            max_iterations=max_iterations,
            resolved_items=resolved_items,
            unresolved_items=unresolved_items,
        )

        action = self._action(
            comparison_report=comparison_report,
            required_actions=required_actions,
            unresolved_items=unresolved_items,
            current_iteration=current_iteration,
            max_iterations=max_iterations,
        )

        stop_loop = action in {
            "approve_and_handoff",
            "stop_max_iterations",
            "blocked_until_manual_review",
        }

        approved_for_handoff = action == "approve_and_handoff"

        decision = GenerationImprovementLoopDecision(
            loop_decision_id=f"generation_improvement_loop_{source_id}_iter_{current_iteration}",
            source_id=source_id,
            current_iteration=current_iteration,
            max_iterations=max_iterations,
            action=action,
            approved_for_handoff=approved_for_handoff,
            stop_loop=stop_loop,
            improvement_status=self._improvement_status(action=action),
            decision_reason=self._decision_reason(
                action=action,
                comparison_report=comparison_report,
                current_iteration=current_iteration,
                max_iterations=max_iterations,
            ),
            next_revision_mode=self._next_revision_mode(
                action=action,
                comparison_report=comparison_report,
                revision_plan=revision_plan,
            ),
            next_priority=self._next_priority(
                comparison_report=comparison_report,
                required_actions=required_actions,
            ),
            required_actions=required_actions,
            resolved_items=resolved_items,
            unresolved_items=unresolved_items,
            loop_metrics=loop_metrics,
            next_engine_payload=self._next_engine_payload(
                action=action,
                comparison_report=comparison_report,
                revision_plan=revision_plan,
                story_context=story_context,
            ),
            handoff_constraints=self._handoff_constraints(
                action=action,
                comparison_report=comparison_report,
                revision_plan=revision_plan,
            ),
            warnings=self._warnings(
                action=action,
                comparison_report=comparison_report,
                current_iteration=current_iteration,
                max_iterations=max_iterations,
            ),
        )

        return {
            "success": True,
            "engine_name": self.engine_name,
            "generation_improvement_loop_decision": decision,
            "generation_improvement_loop_decision_dict": decision.model_dump(mode="json"),
            "handoff_to_next_engine": {
                "next_engine": self._next_engine_name(action=action),
                "payload_keys": [
                    "generation_improvement_loop_decision",
                    "draft_comparison_report",
                    "story_revision_plan",
                    "story_context",
                ],
            },
        }

    def validate_loop_decision(self, *, decision: GenerationImprovementLoopDecision) -> Dict[str, Any]:
        blockers: List[str] = []
        warnings: List[str] = []
        passed: List[str] = []

        if decision.loop_decision_id:
            passed.append("loop_decision_id_present")
        else:
            blockers.append("loop_decision_id missing")

        if decision.source_id:
            passed.append("source_id_present")
        else:
            blockers.append("source_id missing")

        allowed_actions = {
            "approve_and_handoff",
            "revise_again_targeted",
            "revise_again_deep",
            "blocked_until_manual_review",
            "stop_max_iterations",
        }

        if decision.action in allowed_actions:
            passed.append("action_valid")
        else:
            blockers.append("invalid loop action")

        if 0 <= decision.current_iteration <= decision.max_iterations:
            passed.append("iteration_bounds_valid")
        else:
            blockers.append("iteration bounds invalid")

        if decision.loop_metrics:
            passed.append("loop_metrics_present")
        else:
            warnings.append("loop metrics missing")

        if decision.handoff_constraints:
            passed.append("handoff_constraints_present")
        else:
            warnings.append("handoff constraints missing")

        if decision.warnings:
            warnings.extend(decision.warnings)

        return {
            "success": True,
            "engine_name": self.engine_name,
            "valid": not blockers,
            "blockers": blockers,
            "warnings": self._unique(warnings),
            "passed_checks": passed,
        }

    def summarize_loop_decision(self, *, decision: GenerationImprovementLoopDecision) -> Dict[str, Any]:
        return {
            "success": True,
            "engine_name": self.engine_name,
            "summary": {
                "loop_decision_id": decision.loop_decision_id,
                "source_id": decision.source_id,
                "current_iteration": decision.current_iteration,
                "max_iterations": decision.max_iterations,
                "action": decision.action,
                "approved_for_handoff": decision.approved_for_handoff,
                "stop_loop": decision.stop_loop,
                "improvement_status": decision.improvement_status,
                "next_revision_mode": decision.next_revision_mode,
                "next_priority": decision.next_priority,
                "required_action_count": len(decision.required_actions),
                "resolved_item_count": len(decision.resolved_items),
                "unresolved_item_count": len(decision.unresolved_items),
                "warning_count": len(decision.warnings),
            },
        }

    def build_loop_decision_text(self, *, decision: GenerationImprovementLoopDecision) -> Dict[str, Any]:
        lines = [
            f"# Generation Improvement Loop Decision: {decision.source_id}",
            "",
            f"Iteration: {decision.current_iteration}/{decision.max_iterations}",
            f"Action: {decision.action}",
            f"Status: {decision.improvement_status}",
            f"Approved for handoff: {decision.approved_for_handoff}",
            f"Stop loop: {decision.stop_loop}",
            "",
            f"Reason: {decision.decision_reason}",
            "",
            "## Required Actions",
        ]

        for item in decision.required_actions:
            lines.append(f"- [{item.get('priority')}] {item.get('action_type')}: {item.get('instruction')}")

        lines.append("")
        lines.append("## Unresolved Items")
        for item in decision.unresolved_items:
            lines.append(f"- {item.get('item_type')}: {item.get('description')}")

        lines.append("")
        lines.append("## Loop Metrics")
        for key, value in decision.loop_metrics.items():
            lines.append(f"- {key}: {value}")

        return {
            "success": True,
            "engine_name": self.engine_name,
            "loop_decision_text": "\n".join(lines),
        }

    def _required_actions(
        self,
        *,
        comparison_report: DraftComparisonReport,
        revision_plan: StoryRevisionPlan | None,
    ) -> List[Dict[str, Any]]:
        actions: List[Dict[str, Any]] = []

        for requirement in comparison_report.approval_requirements:
            actions.append(
                {
                    "required_action_id": f"required_{requirement.get('requirement_id')}",
                    "action_type": requirement.get("requirement_type", "approval_requirement"),
                    "priority": requirement.get("priority", "medium"),
                    "instruction": requirement.get("instruction", "Resolve approval requirement."),
                    "source": "draft_comparison_report",
                }
            )

        for flag in comparison_report.regression_flags:
            actions.append(
                {
                    "required_action_id": f"required_regression_{flag.get('flag_id')}",
                    "action_type": flag.get("flag_type", "regression"),
                    "priority": "high" if flag.get("severity") == "high" else "medium",
                    "instruction": flag.get("description", "Resolve regression flag."),
                    "source": "draft_comparison_report",
                }
            )

        if revision_plan:
            for issue in revision_plan.blocking_issues:
                actions.append(
                    {
                        "required_action_id": f"required_blocking_{issue.get('blocking_issue_id')}",
                        "action_type": issue.get("issue_type", "blocking_issue"),
                        "priority": "critical" if issue.get("severity") == "blocker" else "high",
                        "instruction": issue.get("description", "Resolve blocking issue."),
                        "source": "story_revision_plan",
                    }
                )

        return self._unique_dicts(actions, key="required_action_id")

    def _resolved_items(self, *, comparison_report: DraftComparisonReport) -> List[Dict[str, Any]]:
        resolved: List[Dict[str, Any]] = []

        for task in comparison_report.task_completion_results:
            if task.get("passed"):
                resolved.append(
                    {
                        "resolved_item_id": f"resolved_{task.get('task_result_id')}",
                        "item_type": task.get("task_type"),
                        "priority": task.get("priority", "medium"),
                        "description": task.get("reason", "Revision task passed."),
                    }
                )

        for item in comparison_report.preserved_elements:
            resolved.append(
                {
                    "resolved_item_id": f"resolved_preserved_{item.get('element_id')}",
                    "item_type": "protected_element_preserved",
                    "priority": "medium",
                    "description": f"Protected element preserved: {item.get('value')}",
                }
            )

        if comparison_report.quality_delta > 0:
            resolved.append(
                {
                    "resolved_item_id": "resolved_quality_improved",
                    "item_type": "quality_improvement",
                    "priority": "medium",
                    "description": f"Quality improved by {comparison_report.quality_delta}.",
                }
            )

        if comparison_report.anti_genericity_delta > 0:
            resolved.append(
                {
                    "resolved_item_id": "resolved_anti_genericity_improved",
                    "item_type": "anti_genericity_improvement",
                    "priority": "medium",
                    "description": f"Anti-genericity improved by {comparison_report.anti_genericity_delta}.",
                }
            )

        if comparison_report.continuity_delta >= 0:
            resolved.append(
                {
                    "resolved_item_id": "resolved_continuity_non_regression",
                    "item_type": "continuity_non_regression",
                    "priority": "medium",
                    "description": f"Continuity did not regress; delta {comparison_report.continuity_delta}.",
                }
            )

        if comparison_report.originality_delta >= 0:
            resolved.append(
                {
                    "resolved_item_id": "resolved_originality_non_regression",
                    "item_type": "originality_non_regression",
                    "priority": "medium",
                    "description": f"Originality did not regress; delta {comparison_report.originality_delta}.",
                }
            )

        return self._unique_dicts(resolved, key="resolved_item_id")

    def _unresolved_items(
        self,
        *,
        comparison_report: DraftComparisonReport,
        revision_plan: StoryRevisionPlan | None,
    ) -> List[Dict[str, Any]]:
        unresolved: List[Dict[str, Any]] = []

        for task in comparison_report.task_completion_results:
            if not task.get("passed"):
                unresolved.append(
                    {
                        "unresolved_item_id": f"unresolved_{task.get('task_result_id')}",
                        "item_type": task.get("task_type"),
                        "priority": task.get("priority", "medium"),
                        "description": task.get("reason", "Revision task not completed."),
                    }
                )

        for item in comparison_report.lost_protected_elements:
            unresolved.append(
                {
                    "unresolved_item_id": f"unresolved_lost_{item.get('element_id')}",
                    "item_type": "lost_protected_element",
                    "priority": "high",
                    "description": item.get("description", "Protected element was lost."),
                }
            )

        for requirement in comparison_report.approval_requirements:
            unresolved.append(
                {
                    "unresolved_item_id": f"unresolved_requirement_{requirement.get('requirement_id')}",
                    "item_type": requirement.get("requirement_type"),
                    "priority": requirement.get("priority", "medium"),
                    "description": requirement.get("instruction"),
                }
            )

        if revision_plan:
            for issue in revision_plan.blocking_issues:
                unresolved.append(
                    {
                        "unresolved_item_id": f"unresolved_blocking_{issue.get('blocking_issue_id')}",
                        "item_type": issue.get("issue_type"),
                        "priority": "critical",
                        "description": issue.get("description"),
                    }
                )

        return self._unique_dicts(unresolved, key="unresolved_item_id")

    def _loop_metrics(
        self,
        *,
        comparison_report: DraftComparisonReport,
        current_iteration: int,
        max_iterations: int,
        resolved_items: List[Dict[str, Any]],
        unresolved_items: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        total_items = len(resolved_items) + len(unresolved_items)
        completion_rate = len(resolved_items) / total_items if total_items else 1.0

        return {
            "current_iteration": current_iteration,
            "max_iterations": max_iterations,
            "iterations_remaining": max(0, max_iterations - current_iteration),
            "improvement_score": comparison_report.improvement_score,
            "regression_risk_score": comparison_report.regression_risk_score,
            "quality_delta": comparison_report.quality_delta,
            "anti_genericity_delta": comparison_report.anti_genericity_delta,
            "continuity_delta": comparison_report.continuity_delta,
            "originality_delta": comparison_report.originality_delta,
            "resolved_count": len(resolved_items),
            "unresolved_count": len(unresolved_items),
            "completion_rate": round(completion_rate, 3),
            "approved_by_comparison": comparison_report.approved,
        }

    def _action(
        self,
        *,
        comparison_report: DraftComparisonReport,
        required_actions: List[Dict[str, Any]],
        unresolved_items: List[Dict[str, Any]],
        current_iteration: int,
        max_iterations: int,
    ) -> str:
        critical_actions = [item for item in required_actions if item.get("priority") == "critical"]
        high_actions = [item for item in required_actions if item.get("priority") == "high"]

        if comparison_report.approved and not required_actions and not unresolved_items:
            return "approve_and_handoff"

        if critical_actions:
            return "blocked_until_manual_review"

        if current_iteration >= max_iterations:
            return "stop_max_iterations"

        if high_actions or comparison_report.regression_risk_score > 0.45:
            return "revise_again_deep"

        return "revise_again_targeted"

    def _improvement_status(self, *, action: str) -> str:
        mapping = {
            "approve_and_handoff": "approved",
            "revise_again_targeted": "needs_targeted_revision",
            "revise_again_deep": "needs_deep_revision",
            "blocked_until_manual_review": "blocked",
            "stop_max_iterations": "stopped_max_iterations",
        }
        return mapping.get(action, "in_progress")

    def _decision_reason(
        self,
        *,
        action: str,
        comparison_report: DraftComparisonReport,
        current_iteration: int,
        max_iterations: int,
    ) -> str:
        if action == "approve_and_handoff":
            return "Draft comparison approved the revision and no unresolved actions remain."
        if action == "blocked_until_manual_review":
            return "Critical blockers remain, usually copy-risk, continuity, or protected-element loss."
        if action == "stop_max_iterations":
            return f"Maximum iterations reached ({current_iteration}/{max_iterations}) before approval."
        if action == "revise_again_deep":
            return "High-priority issues or regression risk require a deeper revision pass."
        return "Revision has partial improvement but still needs a targeted pass."

    def _next_revision_mode(
        self,
        *,
        action: str,
        comparison_report: DraftComparisonReport,
        revision_plan: StoryRevisionPlan | None,
    ) -> str:
        if action == "approve_and_handoff":
            return "none"
        if action == "blocked_until_manual_review":
            return "blocked_until_risk_resolved"
        if action == "stop_max_iterations":
            return "none"
        if action == "revise_again_deep":
            return "deep"
        if revision_plan and revision_plan.revision_mode == "deep":
            return "deep"
        return "targeted"

    def _next_priority(
        self,
        *,
        comparison_report: DraftComparisonReport,
        required_actions: List[Dict[str, Any]],
    ) -> str:
        priorities = [item.get("priority", "medium") for item in required_actions]
        if "critical" in priorities:
            return "critical"
        if "high" in priorities or comparison_report.regression_risk_score > 0.35:
            return "high"
        if required_actions:
            return "medium"
        return "low"

    def _next_engine_payload(
        self,
        *,
        action: str,
        comparison_report: DraftComparisonReport,
        revision_plan: StoryRevisionPlan | None,
        story_context: Dict[str, Any],
    ) -> Dict[str, Any]:
        if action == "approve_and_handoff":
            return {
                "target_engine": "story_generation.story_provenance_engine",
                "approved_revised_draft_id": comparison_report.revised_draft_id,
                "story_context": story_context,
            }

        if action in {"revise_again_targeted", "revise_again_deep"}:
            return {
                "target_engine": "story_generation.story_revision_engine",
                "revision_mode": self._next_revision_mode(
                    action=action,
                    comparison_report=comparison_report,
                    revision_plan=revision_plan,
                ),
                "comparison_report_id": comparison_report.comparison_report_id,
                "story_context": story_context,
            }

        return {
            "target_engine": "manual_review",
            "comparison_report_id": comparison_report.comparison_report_id,
            "story_context": story_context,
        }

    def _handoff_constraints(
        self,
        *,
        action: str,
        comparison_report: DraftComparisonReport,
        revision_plan: StoryRevisionPlan | None,
    ) -> Dict[str, Any]:
        return {
            "action": action,
            "approved_for_handoff": action == "approve_and_handoff",
            "comparison_report_id": comparison_report.comparison_report_id,
            "must_restore_lost_element_ids": [
                item.get("element_id") for item in comparison_report.lost_protected_elements
            ],
            "must_resolve_regression_flag_ids": [
                item.get("flag_id") for item in comparison_report.regression_flags
            ],
            "must_resolve_approval_requirement_ids": [
                item.get("requirement_id") for item in comparison_report.approval_requirements
            ],
            "protected_element_ids": [
                item.get("element_id") for item in revision_plan.protected_elements
            ] if revision_plan else [],
            "rules": [
                "Only hand off approved drafts to provenance and memory update.",
                "Never export a draft with unresolved copy-risk or continuity blockers.",
                "Do not discard protected elements during additional revision passes.",
            ],
        }

    def _warnings(
        self,
        *,
        action: str,
        comparison_report: DraftComparisonReport,
        current_iteration: int,
        max_iterations: int,
    ) -> List[str]:
        warnings = []

        if action == "blocked_until_manual_review":
            warnings.append("Loop is blocked until critical risk issues are reviewed or repaired.")

        if action == "stop_max_iterations":
            warnings.append("Loop stopped because maximum iterations were reached.")

        if comparison_report.regression_flags:
            warnings.append(f"{len(comparison_report.regression_flags)} regression flag(s) remain.")

        if comparison_report.approval_requirements:
            warnings.append(f"{len(comparison_report.approval_requirements)} approval requirement(s) remain.")

        if current_iteration >= max_iterations and action != "approve_and_handoff":
            warnings.append("No more automatic revision iterations remain.")

        return warnings

    def _next_engine_name(self, *, action: str) -> str:
        if action == "approve_and_handoff":
            return "story_generation.story_provenance_engine"
        if action in {"revise_again_targeted", "revise_again_deep"}:
            return "story_generation.story_revision_engine"
        return "manual_review"

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

from __future__ import annotations

from typing import Any, Dict, List

from backend.app.schemas.story_generation import (
    AdaptiveStoryPatternPlan,
    GeneratedChapter,
    OriginalityCopyRiskReport,
    PlotOutline,
    StoryAntiGenericityReport,
    StoryContinuityValidationReport,
    StoryQualityScoreReport,
    StoryRevisionPlan,
)


class StoryRevisionEngine:
    """Builds controlled revision plans from quality/risk/continuity reports.

    Locked Chunk 5.36. This engine does not blindly rewrite prose. It converts
    quality, anti-genericity, continuity, and copy-risk reports into ordered,
    testable revision tasks that later engines can apply safely.
    """

    engine_name = "story_generation.story_revision_engine"

    def build_revision_plan(
        self,
        *,
        source_id: str,
        plot_outline: PlotOutline | None = None,
        chapter: GeneratedChapter | None = None,
        quality_report: StoryQualityScoreReport | None = None,
        anti_genericity_report: StoryAntiGenericityReport | None = None,
        continuity_report: StoryContinuityValidationReport | None = None,
        originality_report: OriginalityCopyRiskReport | None = None,
        adaptive_pattern_plan: AdaptiveStoryPatternPlan | None = None,
        story_context: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        story_context = story_context or {}

        quality_tasks = self._quality_revision_tasks(quality_report=quality_report)
        anti_genericity_tasks = self._anti_genericity_revision_tasks(anti_genericity_report=anti_genericity_report)
        continuity_tasks = self._continuity_repair_tasks(continuity_report=continuity_report)
        originality_tasks = self._originality_rewrite_tasks(originality_report=originality_report)

        blocking_issues = self._blocking_issues(
            continuity_report=continuity_report,
            originality_report=originality_report,
            quality_report=quality_report,
            anti_genericity_report=anti_genericity_report,
        )

        protected_elements = self._protected_elements(
            plot_outline=plot_outline,
            chapter=chapter,
            continuity_report=continuity_report,
            originality_report=originality_report,
            adaptive_pattern_plan=adaptive_pattern_plan,
        )

        all_tasks = quality_tasks + anti_genericity_tasks + continuity_tasks + originality_tasks
        rewrite_order = self._rewrite_order(all_tasks=all_tasks)
        revision_mode = self._revision_mode(all_tasks=all_tasks, blocking_issues=blocking_issues)
        priority = self._overall_revision_priority(all_tasks=all_tasks, blocking_issues=blocking_issues)

        plan = StoryRevisionPlan(
            revision_plan_id=f"story_revision_plan_{source_id}",
            source_id=source_id,
            ready_for_revision=True,
            revision_mode=revision_mode,
            overall_revision_priority=priority,
            revision_goals=self._revision_goals(
                quality_report=quality_report,
                anti_genericity_report=anti_genericity_report,
                continuity_report=continuity_report,
                originality_report=originality_report,
            ),
            quality_revision_tasks=quality_tasks,
            anti_genericity_revision_tasks=anti_genericity_tasks,
            continuity_repair_tasks=continuity_tasks,
            originality_rewrite_tasks=originality_tasks,
            protected_elements=protected_elements,
            rewrite_order=rewrite_order,
            revision_constraints=self._revision_constraints(
                continuity_report=continuity_report,
                originality_report=originality_report,
                adaptive_pattern_plan=adaptive_pattern_plan,
                protected_elements=protected_elements,
            ),
            expected_improvements=self._expected_improvements(all_tasks=all_tasks),
            blocking_issues=blocking_issues,
            warnings=self._warnings(
                all_tasks=all_tasks,
                blocking_issues=blocking_issues,
                quality_report=quality_report,
                anti_genericity_report=anti_genericity_report,
                continuity_report=continuity_report,
                originality_report=originality_report,
            ),
        )

        return {
            "success": True,
            "engine_name": self.engine_name,
            "story_revision_plan": plan,
            "story_revision_plan_dict": plan.model_dump(mode="json"),
            "handoff_to_next_engine": {
                "next_engine": "story_generation.draft_comparison_engine",
                "payload_keys": [
                    "story_revision_plan",
                    "plot_outline",
                    "generated_chapter",
                    "story_quality_score_report",
                    "story_anti_genericity_report",
                    "story_continuity_validation_report",
                    "originality_copy_risk_report",
                    "story_context",
                ],
            },
        }

    def validate_revision_plan(self, *, plan: StoryRevisionPlan) -> Dict[str, Any]:
        blockers: List[str] = []
        warnings: List[str] = []
        passed: List[str] = []

        if plan.revision_plan_id:
            passed.append("revision_plan_id_present")
        else:
            blockers.append("revision_plan_id missing")

        if plan.source_id:
            passed.append("source_id_present")
        else:
            blockers.append("source_id missing")

        if plan.revision_goals:
            passed.append("revision_goals_present")
        else:
            warnings.append("revision goals missing")

        if plan.rewrite_order:
            passed.append("rewrite_order_present")
        else:
            warnings.append("rewrite order missing")

        if plan.revision_constraints:
            passed.append("revision_constraints_present")
        else:
            warnings.append("revision constraints missing")

        if plan.overall_revision_priority in {"low", "medium", "high", "critical"}:
            passed.append("priority_valid")
        else:
            blockers.append("invalid revision priority")

        if plan.revision_mode in {"none", "targeted", "deep", "blocked_until_risk_resolved"}:
            passed.append("revision_mode_valid")
        else:
            blockers.append("invalid revision mode")

        if plan.blocking_issues:
            warnings.append("blocking issues present")

        if plan.warnings:
            warnings.extend(plan.warnings)

        return {
            "success": True,
            "engine_name": self.engine_name,
            "valid": not blockers,
            "blockers": blockers,
            "warnings": self._unique(warnings),
            "passed_checks": passed,
        }

    def summarize_revision_plan(self, *, plan: StoryRevisionPlan) -> Dict[str, Any]:
        return {
            "success": True,
            "engine_name": self.engine_name,
            "summary": {
                "revision_plan_id": plan.revision_plan_id,
                "source_id": plan.source_id,
                "ready_for_revision": plan.ready_for_revision,
                "revision_mode": plan.revision_mode,
                "overall_revision_priority": plan.overall_revision_priority,
                "quality_task_count": len(plan.quality_revision_tasks),
                "anti_genericity_task_count": len(plan.anti_genericity_revision_tasks),
                "continuity_task_count": len(plan.continuity_repair_tasks),
                "originality_task_count": len(plan.originality_rewrite_tasks),
                "protected_element_count": len(plan.protected_elements),
                "rewrite_step_count": len(plan.rewrite_order),
                "blocking_issue_count": len(plan.blocking_issues),
                "warning_count": len(plan.warnings),
            },
        }

    def build_revision_plan_text(self, *, plan: StoryRevisionPlan) -> Dict[str, Any]:
        lines = [
            f"# Story Revision Plan: {plan.source_id}",
            "",
            f"Mode: {plan.revision_mode}",
            f"Priority: {plan.overall_revision_priority}",
            f"Ready for revision: {plan.ready_for_revision}",
            "",
            "## Revision Goals",
        ]

        for goal in plan.revision_goals:
            lines.append(f"- {goal.get('goal_type')}: {goal.get('description')}")

        lines.append("")
        lines.append("## Rewrite Order")
        for step in plan.rewrite_order:
            lines.append(f"- Step {step.get('step_number')}: [{step.get('priority')}] {step.get('task_type')} — {step.get('instruction')}")

        lines.append("")
        lines.append("## Protected Elements")
        for item in plan.protected_elements:
            lines.append(f"- {item.get('element_type')}: {item.get('value')}")

        lines.append("")
        lines.append("## Blocking Issues")
        for item in plan.blocking_issues:
            lines.append(f"- [{item.get('severity')}] {item.get('issue_type')}: {item.get('description')}")

        return {
            "success": True,
            "engine_name": self.engine_name,
            "revision_plan_text": "\n".join(lines),
        }

    def _quality_revision_tasks(self, *, quality_report: StoryQualityScoreReport | None) -> List[Dict[str, Any]]:
        if not quality_report:
            return [
                {
                    "task_id": "quality_missing_report",
                    "task_type": "quality_context",
                    "priority": "medium",
                    "dimension": "quality",
                    "instruction": "Run story quality scoring before final revision.",
                    "source": "missing_quality_report",
                }
            ]

        tasks: List[Dict[str, Any]] = []

        for item in quality_report.revision_priorities:
            dimension = item.get("dimension", "quality")
            tasks.append(
                {
                    "task_id": f"quality_revision_{dimension}",
                    "task_type": "quality_revision",
                    "priority": item.get("priority", "medium"),
                    "dimension": dimension,
                    "instruction": item.get("instruction", f"Improve {dimension}."),
                    "source": "story_quality_score_report",
                    "current_score": item.get("score"),
                }
            )

        if quality_report.readiness_level == "blocked":
            tasks.append(
                {
                    "task_id": "quality_blocked_revision",
                    "task_type": "quality_blocker",
                    "priority": "critical",
                    "dimension": "overall",
                    "instruction": "Resolve blocked quality status before export or long-form continuation.",
                    "source": "story_quality_score_report",
                    "current_score": quality_report.overall_score,
                }
            )

        return self._unique_dicts(tasks, key="task_id")

    def _anti_genericity_revision_tasks(self, *, anti_genericity_report: StoryAntiGenericityReport | None) -> List[Dict[str, Any]]:
        if not anti_genericity_report:
            return [
                {
                    "task_id": "anti_genericity_missing_report",
                    "task_type": "anti_genericity_context",
                    "priority": "medium",
                    "dimension": "anti_genericity",
                    "instruction": "Run anti-genericity validation before final revision.",
                    "source": "missing_anti_genericity_report",
                }
            ]

        tasks: List[Dict[str, Any]] = []

        for target in anti_genericity_report.rewrite_targets:
            tasks.append(
                {
                    "task_id": f"anti_genericity_{target.get('rewrite_target_id')}",
                    "task_type": "anti_genericity_rewrite",
                    "priority": target.get("priority", "medium"),
                    "dimension": target.get("target_type", "anti_genericity"),
                    "instruction": target.get("instruction", "Increase story specificity."),
                    "source": "story_anti_genericity_report",
                }
            )

        if anti_genericity_report.genericity_risk_level in {"high", "critical"}:
            tasks.append(
                {
                    "task_id": "anti_genericity_high_risk",
                    "task_type": "anti_genericity_risk",
                    "priority": "critical" if anti_genericity_report.genericity_risk_level == "critical" else "high",
                    "dimension": "genericity_risk",
                    "instruction": "Rewrite generic/template-like material before continuation.",
                    "source": "story_anti_genericity_report",
                    "current_score": anti_genericity_report.overall_anti_genericity_score,
                }
            )

        return self._unique_dicts(tasks, key="task_id")

    def _continuity_repair_tasks(self, *, continuity_report: StoryContinuityValidationReport | None) -> List[Dict[str, Any]]:
        if not continuity_report:
            return [
                {
                    "task_id": "continuity_missing_report",
                    "task_type": "continuity_context",
                    "priority": "high",
                    "dimension": "continuity",
                    "instruction": "Run story continuity validation before revision.",
                    "source": "missing_continuity_report",
                }
            ]

        tasks: List[Dict[str, Any]] = []

        for target in continuity_report.repair_targets:
            tasks.append(
                {
                    "task_id": f"continuity_{target.get('repair_target_id')}",
                    "task_type": "continuity_repair",
                    "priority": target.get("priority", "medium"),
                    "dimension": target.get("target_type", "continuity"),
                    "instruction": target.get("instruction", "Repair continuity."),
                    "source": "story_continuity_validation_report",
                }
            )

        if not continuity_report.valid:
            tasks.append(
                {
                    "task_id": "continuity_invalid_story",
                    "task_type": "continuity_blocker",
                    "priority": "critical",
                    "dimension": "overall_continuity",
                    "instruction": "Repair blocker continuity issues before any export or continuation.",
                    "source": "story_continuity_validation_report",
                    "current_score": continuity_report.continuity_score,
                }
            )

        return self._unique_dicts(tasks, key="task_id")

    def _originality_rewrite_tasks(self, *, originality_report: OriginalityCopyRiskReport | None) -> List[Dict[str, Any]]:
        if not originality_report:
            return [
                {
                    "task_id": "originality_missing_report",
                    "task_type": "originality_context",
                    "priority": "high",
                    "dimension": "originality",
                    "instruction": "Run originality/copy-risk guard before final revision.",
                    "source": "missing_originality_report",
                }
            ]

        tasks: List[Dict[str, Any]] = []

        for requirement in originality_report.rewrite_requirements:
            tasks.append(
                {
                    "task_id": f"originality_{requirement.get('rewrite_requirement_id')}",
                    "task_type": "originality_rewrite",
                    "priority": "critical" if requirement.get("severity") == "blocker" else "high",
                    "dimension": requirement.get("requirement_type", "originality"),
                    "instruction": requirement.get("instruction", "Rewrite originality/copy-risk issue."),
                    "source": "originality_copy_risk_report",
                }
            )

        if not originality_report.safe_for_export:
            tasks.append(
                {
                    "task_id": "originality_not_safe_for_export",
                    "task_type": "originality_blocker",
                    "priority": "critical",
                    "dimension": "copy_risk",
                    "instruction": "Resolve copy-risk blockers before export.",
                    "source": "originality_copy_risk_report",
                    "current_score": originality_report.overall_originality_score,
                }
            )

        return self._unique_dicts(tasks, key="task_id")

    def _revision_goals(
        self,
        *,
        quality_report: StoryQualityScoreReport | None,
        anti_genericity_report: StoryAntiGenericityReport | None,
        continuity_report: StoryContinuityValidationReport | None,
        originality_report: OriginalityCopyRiskReport | None,
    ) -> List[Dict[str, Any]]:
        goals = []

        if quality_report:
            goals.append(
                {
                    "goal_id": "goal_quality",
                    "goal_type": "quality",
                    "description": f"Improve quality from readiness level {quality_report.readiness_level}.",
                    "current_score": quality_report.overall_score,
                }
            )

        if anti_genericity_report:
            goals.append(
                {
                    "goal_id": "goal_anti_genericity",
                    "goal_type": "anti_genericity",
                    "description": f"Reduce genericity risk from {anti_genericity_report.genericity_risk_level}.",
                    "current_score": anti_genericity_report.overall_anti_genericity_score,
                }
            )

        if continuity_report:
            goals.append(
                {
                    "goal_id": "goal_continuity",
                    "goal_type": "continuity",
                    "description": f"Preserve story threads and improve readiness from {continuity_report.readiness_level}.",
                    "current_score": continuity_report.continuity_score,
                }
            )

        if originality_report:
            goals.append(
                {
                    "goal_id": "goal_originality",
                    "goal_type": "originality",
                    "description": f"Reduce copy-risk from {originality_report.copy_risk_level}.",
                    "current_score": originality_report.overall_originality_score,
                }
            )

        if not goals:
            goals.append(
                {
                    "goal_id": "goal_baseline_revision",
                    "goal_type": "baseline",
                    "description": "Create a baseline revision pass after reports are available.",
                    "current_score": None,
                }
            )

        return goals

    def _protected_elements(
        self,
        *,
        plot_outline: PlotOutline | None,
        chapter: GeneratedChapter | None,
        continuity_report: StoryContinuityValidationReport | None,
        originality_report: OriginalityCopyRiskReport | None,
        adaptive_pattern_plan: AdaptiveStoryPatternPlan | None,
    ) -> List[Dict[str, Any]]:
        protected: List[Dict[str, Any]] = []

        if continuity_report:
            for character_id in continuity_report.checked_character_ids:
                protected.append({"element_id": f"protect_character_{character_id}", "element_type": "character", "value": character_id})
            for secret_id in continuity_report.checked_secret_ids:
                protected.append({"element_id": f"protect_secret_{secret_id}", "element_type": "secret", "value": secret_id})
            for causal_id in continuity_report.checked_causal_ids:
                protected.append({"element_id": f"protect_causal_{causal_id}", "element_type": "causal", "value": causal_id})
            for detail in continuity_report.checked_world_details:
                protected.append({"element_id": f"protect_world_{self._safe_id(detail)}", "element_type": "world_detail", "value": detail})

        if originality_report:
            for index, item in enumerate(originality_report.approved_original_elements, start=1):
                protected.append(
                    {
                        "element_id": f"protect_original_element_{index}",
                        "element_type": "approved_original_element",
                        "value": item,
                    }
                )

        if adaptive_pattern_plan:
            protected.append(
                {
                    "element_id": "protect_primary_pattern",
                    "element_type": "pattern",
                    "value": adaptive_pattern_plan.selected_primary_pattern,
                }
            )

        if plot_outline and plot_outline.premise:
            protected.append(
                {
                    "element_id": "protect_premise",
                    "element_type": "premise",
                    "value": plot_outline.premise,
                }
            )

        if chapter and chapter.title:
            protected.append(
                {
                    "element_id": "protect_chapter_title",
                    "element_type": "chapter_title",
                    "value": chapter.title,
                }
            )

        return self._unique_dicts(protected, key="element_id")

    def _rewrite_order(self, *, all_tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        priority_rank = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        source_rank = {
            "originality_copy_risk_report": 0,
            "story_continuity_validation_report": 1,
            "story_anti_genericity_report": 2,
            "story_quality_score_report": 3,
        }

        ordered = sorted(
            all_tasks,
            key=lambda task: (
                priority_rank.get(task.get("priority", "medium"), 2),
                source_rank.get(task.get("source", ""), 9),
                task.get("task_id", ""),
            ),
        )

        rewrite_order = []
        for index, task in enumerate(ordered, start=1):
            rewrite_order.append(
                {
                    "step_number": index,
                    "task_id": task.get("task_id"),
                    "task_type": task.get("task_type"),
                    "priority": task.get("priority"),
                    "dimension": task.get("dimension"),
                    "instruction": task.get("instruction"),
                    "source": task.get("source"),
                }
            )

        return rewrite_order

    def _revision_constraints(
        self,
        *,
        continuity_report: StoryContinuityValidationReport | None,
        originality_report: OriginalityCopyRiskReport | None,
        adaptive_pattern_plan: AdaptiveStoryPatternPlan | None,
        protected_elements: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        constraints: Dict[str, Any] = {
            "protected_element_ids": [item.get("element_id") for item in protected_elements],
            "must_preserve_character_voice": True,
            "must_preserve_world_state": True,
            "must_preserve_causal_logic": True,
            "must_reduce_genericity": True,
            "must_not_increase_copy_risk": True,
        }

        if continuity_report:
            constraints["continuity_constraints"] = continuity_report.downstream_constraints

        if originality_report:
            constraints["copy_risk_constraints"] = originality_report.downstream_constraints

        if adaptive_pattern_plan:
            constraints["pattern_constraints"] = adaptive_pattern_plan.downstream_generation_constraints
            constraints["anti_template_rules"] = adaptive_pattern_plan.anti_template_rules

        return constraints

    def _expected_improvements(self, *, all_tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
        dimensions = {}
        for task in all_tasks:
            dimension = task.get("dimension", "general")
            dimensions[dimension] = dimensions.get(dimension, 0) + 1

        return {
            "task_count": len(all_tasks),
            "targeted_dimensions": dimensions,
            "expected_result": "higher quality, lower genericity, stronger continuity, and lower copy-risk after revision",
        }

    def _blocking_issues(
        self,
        *,
        continuity_report: StoryContinuityValidationReport | None,
        originality_report: OriginalityCopyRiskReport | None,
        quality_report: StoryQualityScoreReport | None,
        anti_genericity_report: StoryAntiGenericityReport | None,
    ) -> List[Dict[str, Any]]:
        issues: List[Dict[str, Any]] = []

        if continuity_report and not continuity_report.valid:
            issues.append(
                {
                    "blocking_issue_id": "blocking_continuity_invalid",
                    "issue_type": "continuity",
                    "severity": "blocker",
                    "description": "Story continuity report is invalid.",
                }
            )

        if originality_report and not originality_report.safe_for_export:
            issues.append(
                {
                    "blocking_issue_id": "blocking_copy_risk_export",
                    "issue_type": "copy_risk",
                    "severity": "blocker",
                    "description": "Originality/copy-risk report is not safe for export.",
                }
            )

        if quality_report and quality_report.readiness_level == "blocked":
            issues.append(
                {
                    "blocking_issue_id": "blocking_quality",
                    "issue_type": "quality",
                    "severity": "blocker",
                    "description": "Story quality report is blocked.",
                }
            )

        if anti_genericity_report and anti_genericity_report.genericity_risk_level == "critical":
            issues.append(
                {
                    "blocking_issue_id": "blocking_genericity",
                    "issue_type": "genericity",
                    "severity": "blocker",
                    "description": "Anti-genericity report has critical genericity risk.",
                }
            )

        return issues

    def _revision_mode(self, *, all_tasks: List[Dict[str, Any]], blocking_issues: List[Dict[str, Any]]) -> str:
        if blocking_issues:
            if any(issue.get("issue_type") == "copy_risk" for issue in blocking_issues):
                return "blocked_until_risk_resolved"
            return "deep"

        critical_or_high = len([task for task in all_tasks if task.get("priority") in {"critical", "high"}])
        if not all_tasks:
            return "none"
        if critical_or_high >= 4 or len(all_tasks) >= 8:
            return "deep"
        return "targeted"

    def _overall_revision_priority(self, *, all_tasks: List[Dict[str, Any]], blocking_issues: List[Dict[str, Any]]) -> str:
        if blocking_issues:
            return "critical"
        priorities = [task.get("priority", "medium") for task in all_tasks]
        if "critical" in priorities:
            return "critical"
        if priorities.count("high") >= 2:
            return "high"
        if priorities:
            return "medium"
        return "low"

    def _warnings(
        self,
        *,
        all_tasks: List[Dict[str, Any]],
        blocking_issues: List[Dict[str, Any]],
        quality_report: StoryQualityScoreReport | None,
        anti_genericity_report: StoryAntiGenericityReport | None,
        continuity_report: StoryContinuityValidationReport | None,
        originality_report: OriginalityCopyRiskReport | None,
    ) -> List[str]:
        warnings: List[str] = []

        if not all_tasks:
            warnings.append("No revision tasks were generated.")

        if blocking_issues:
            warnings.append(f"{len(blocking_issues)} blocking issue(s) must be resolved.")

        if not quality_report:
            warnings.append("No quality report supplied.")
        if not anti_genericity_report:
            warnings.append("No anti-genericity report supplied.")
        if not continuity_report:
            warnings.append("No continuity report supplied.")
        if not originality_report:
            warnings.append("No originality/copy-risk report supplied.")

        return warnings

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

from __future__ import annotations

from typing import Any, Dict, List, Set

from backend.app.schemas.story_generation import (
    DraftComparisonReport,
    OriginalityCopyRiskReport,
    StoryAntiGenericityReport,
    StoryContinuityValidationReport,
    StoryQualityScoreReport,
    StoryRevisionPlan,
)


class DraftComparisonEngine:
    """Compares original and revised drafts against revision goals.

    Locked Chunk 5.37. This engine checks whether a revision improves the
    draft while preserving continuity, protected elements, originality, and
    story-specific threads.
    """

    engine_name = "story_generation.draft_comparison_engine"

    def compare_drafts(
        self,
        *,
        source_id: str,
        original_draft_id: str,
        revised_draft_id: str,
        original_text: str,
        revised_text: str,
        revision_plan: StoryRevisionPlan | None = None,
        original_quality_report: StoryQualityScoreReport | None = None,
        revised_quality_report: StoryQualityScoreReport | None = None,
        original_anti_genericity_report: StoryAntiGenericityReport | None = None,
        revised_anti_genericity_report: StoryAntiGenericityReport | None = None,
        original_continuity_report: StoryContinuityValidationReport | None = None,
        revised_continuity_report: StoryContinuityValidationReport | None = None,
        original_originality_report: OriginalityCopyRiskReport | None = None,
        revised_originality_report: OriginalityCopyRiskReport | None = None,
        story_context: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        story_context = story_context or {}

        text_summary = self._text_change_summary(original_text=original_text, revised_text=revised_text)
        original_elements = self._extract_elements(text=original_text, story_context=story_context)
        revised_elements = self._extract_elements(text=revised_text, story_context=story_context)

        protected_elements = revision_plan.protected_elements if revision_plan else []
        preserved_elements = self._preserved_protected_elements(
            protected_elements=protected_elements,
            revised_text=revised_text,
            revised_elements=revised_elements,
        )
        lost_protected_elements = self._lost_protected_elements(
            protected_elements=protected_elements,
            revised_text=revised_text,
            revised_elements=revised_elements,
        )

        added_elements = self._element_diff(
            from_elements=original_elements,
            to_elements=revised_elements,
            diff_type="added",
        )
        removed_elements = self._element_diff(
            from_elements=revised_elements,
            to_elements=original_elements,
            diff_type="removed",
        )

        quality_delta = self._quality_delta(original_quality_report, revised_quality_report)
        anti_genericity_delta = self._anti_genericity_delta(original_anti_genericity_report, revised_anti_genericity_report)
        continuity_delta = self._continuity_delta(original_continuity_report, revised_continuity_report)
        originality_delta = self._originality_delta(original_originality_report, revised_originality_report)

        task_results = self._task_completion_results(
            revision_plan=revision_plan,
            revised_text=revised_text,
            quality_delta=quality_delta,
            anti_genericity_delta=anti_genericity_delta,
            continuity_delta=continuity_delta,
            originality_delta=originality_delta,
        )

        regression_flags = self._regression_flags(
            quality_delta=quality_delta,
            anti_genericity_delta=anti_genericity_delta,
            continuity_delta=continuity_delta,
            originality_delta=originality_delta,
            lost_protected_elements=lost_protected_elements,
            removed_elements=removed_elements,
            revised_originality_report=revised_originality_report,
            revised_continuity_report=revised_continuity_report,
        )

        improvement_score = self._improvement_score(
            quality_delta=quality_delta,
            anti_genericity_delta=anti_genericity_delta,
            continuity_delta=continuity_delta,
            originality_delta=originality_delta,
            task_results=task_results,
            text_summary=text_summary,
        )
        regression_risk_score = self._regression_risk_score(regression_flags=regression_flags, lost_protected_elements=lost_protected_elements)

        approval_requirements = self._approval_requirements(
            regression_flags=regression_flags,
            lost_protected_elements=lost_protected_elements,
            revised_originality_report=revised_originality_report,
            revised_continuity_report=revised_continuity_report,
            improvement_score=improvement_score,
            regression_risk_score=regression_risk_score,
        )

        approved = not approval_requirements and improvement_score >= 0.45 and regression_risk_score <= 0.35

        report = DraftComparisonReport(
            comparison_report_id=f"draft_comparison_{source_id}",
            source_id=source_id,
            original_draft_id=original_draft_id,
            revised_draft_id=revised_draft_id,
            approved=approved,
            improvement_score=improvement_score,
            regression_risk_score=regression_risk_score,
            quality_delta=quality_delta,
            anti_genericity_delta=anti_genericity_delta,
            continuity_delta=continuity_delta,
            originality_delta=originality_delta,
            text_change_summary=text_summary,
            preserved_elements=preserved_elements,
            lost_protected_elements=lost_protected_elements,
            added_elements=added_elements,
            removed_elements=removed_elements,
            task_completion_results=task_results,
            regression_flags=regression_flags,
            approval_requirements=approval_requirements,
            downstream_constraints=self._downstream_constraints(
                approved=approved,
                lost_protected_elements=lost_protected_elements,
                regression_flags=regression_flags,
                revised_continuity_report=revised_continuity_report,
                revised_originality_report=revised_originality_report,
            ),
            warnings=self._warnings(
                revision_plan=revision_plan,
                regression_flags=regression_flags,
                approval_requirements=approval_requirements,
            ),
        )

        return {
            "success": True,
            "engine_name": self.engine_name,
            "draft_comparison_report": report,
            "draft_comparison_report_dict": report.model_dump(mode="json"),
            "handoff_to_next_engine": {
                "next_engine": "story_generation.generation_improvement_loop",
                "payload_keys": [
                    "draft_comparison_report",
                    "story_revision_plan",
                    "original_draft",
                    "revised_draft",
                    "story_context",
                ],
            },
        }

    def validate_comparison_report(self, *, report: DraftComparisonReport) -> Dict[str, Any]:
        blockers: List[str] = []
        warnings: List[str] = []
        passed: List[str] = []

        if report.comparison_report_id:
            passed.append("comparison_report_id_present")
        else:
            blockers.append("comparison_report_id missing")

        if report.source_id:
            passed.append("source_id_present")
        else:
            blockers.append("source_id missing")

        if report.original_draft_id and report.revised_draft_id:
            passed.append("draft_ids_present")
        else:
            blockers.append("draft ids missing")

        if 0.0 <= report.improvement_score <= 1.0 and 0.0 <= report.regression_risk_score <= 1.0:
            passed.append("scores_bounded")
        else:
            blockers.append("comparison scores out of bounds")

        if report.text_change_summary:
            passed.append("text_change_summary_present")
        else:
            warnings.append("text change summary missing")

        if report.downstream_constraints:
            passed.append("downstream_constraints_present")
        else:
            warnings.append("downstream constraints missing")

        if report.approval_requirements:
            warnings.append("approval requirements remain")

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

    def summarize_comparison_report(self, *, report: DraftComparisonReport) -> Dict[str, Any]:
        return {
            "success": True,
            "engine_name": self.engine_name,
            "summary": {
                "comparison_report_id": report.comparison_report_id,
                "source_id": report.source_id,
                "approved": report.approved,
                "improvement_score": report.improvement_score,
                "regression_risk_score": report.regression_risk_score,
                "quality_delta": report.quality_delta,
                "anti_genericity_delta": report.anti_genericity_delta,
                "continuity_delta": report.continuity_delta,
                "originality_delta": report.originality_delta,
                "preserved_element_count": len(report.preserved_elements),
                "lost_protected_element_count": len(report.lost_protected_elements),
                "task_completion_count": len(report.task_completion_results),
                "regression_flag_count": len(report.regression_flags),
                "approval_requirement_count": len(report.approval_requirements),
                "warning_count": len(report.warnings),
            },
        }

    def build_comparison_report_text(self, *, report: DraftComparisonReport) -> Dict[str, Any]:
        lines = [
            f"# Draft Comparison Report: {report.source_id}",
            "",
            f"Approved: {report.approved}",
            f"Improvement score: {report.improvement_score}",
            f"Regression risk score: {report.regression_risk_score}",
            "",
            "## Score Deltas",
            f"- Quality delta: {report.quality_delta}",
            f"- Anti-genericity delta: {report.anti_genericity_delta}",
            f"- Continuity delta: {report.continuity_delta}",
            f"- Originality delta: {report.originality_delta}",
            "",
            "## Lost Protected Elements",
        ]

        for item in report.lost_protected_elements:
            lines.append(f"- {item.get('element_type')}: {item.get('value')}")

        lines.append("")
        lines.append("## Regression Flags")
        for item in report.regression_flags:
            lines.append(f"- [{item.get('severity')}] {item.get('flag_type')}: {item.get('description')}")

        lines.append("")
        lines.append("## Approval Requirements")
        for item in report.approval_requirements:
            lines.append(f"- [{item.get('priority')}] {item.get('requirement_type')}: {item.get('instruction')}")

        return {
            "success": True,
            "engine_name": self.engine_name,
            "comparison_report_text": "\n".join(lines),
        }

    def _text_change_summary(self, *, original_text: str, revised_text: str) -> Dict[str, Any]:
        original_words = original_text.split()
        revised_words = revised_text.split()
        original_sentences = self._sentences(original_text)
        revised_sentences = self._sentences(revised_text)

        original_set = set(word.lower().strip(".,!?;:") for word in original_words)
        revised_set = set(word.lower().strip(".,!?;:") for word in revised_words)

        added_words = sorted([word for word in revised_set - original_set if word])
        removed_words = sorted([word for word in original_set - revised_set if word])

        return {
            "original_word_count": len(original_words),
            "revised_word_count": len(revised_words),
            "word_count_delta": len(revised_words) - len(original_words),
            "original_sentence_count": len(original_sentences),
            "revised_sentence_count": len(revised_sentences),
            "sentence_count_delta": len(revised_sentences) - len(original_sentences),
            "added_keyword_sample": added_words[:20],
            "removed_keyword_sample": removed_words[:20],
            "change_ratio": self._bounded(abs(len(revised_words) - len(original_words)) / max(1, len(original_words))),
        }

    def _extract_elements(self, *, text: str, story_context: Dict[str, Any]) -> Dict[str, Set[str]]:
        elements = {
            "characters": set(),
            "relationships": set(),
            "secrets": set(),
            "causal": set(),
            "world_details": set(),
            "open_loops": set(),
        }

        tokens = set(token.strip(".,!?;:()[]{}").lower() for token in text.split())

        for key, target_key in [
            ("known_character_ids", "characters"),
            ("known_relationship_ids", "relationships"),
            ("known_secret_ids", "secrets"),
            ("known_causal_ids", "causal"),
            ("known_world_details", "world_details"),
            ("known_open_loop_ids", "open_loops"),
        ]:
            for value in story_context.get(key, []):
                value_text = str(value)
                if self._appears_in_text(value_text, text, tokens):
                    elements[target_key].add(value_text)

        for token in tokens:
            if token.startswith("char_"):
                elements["characters"].add(token)
            if token.startswith("rel_"):
                elements["relationships"].add(token)
            if token.startswith("secret_"):
                elements["secrets"].add(token)
            if token.startswith("cause_"):
                elements["causal"].add(token)
            if token.startswith("open_loop_"):
                elements["open_loops"].add(token)

        for phrase in story_context.get("known_world_details", []):
            phrase_text = str(phrase)
            if phrase_text.lower() in text.lower():
                elements["world_details"].add(phrase_text)

        return elements

    def _preserved_protected_elements(
        self,
        *,
        protected_elements: List[Dict[str, Any]],
        revised_text: str,
        revised_elements: Dict[str, Set[str]],
    ) -> List[Dict[str, Any]]:
        preserved = []

        for item in protected_elements:
            value = str(item.get("value", ""))
            if self._protected_value_present(value=value, revised_text=revised_text, revised_elements=revised_elements):
                preserved.append(
                    {
                        "element_id": item.get("element_id"),
                        "element_type": item.get("element_type"),
                        "value": item.get("value"),
                        "status": "preserved",
                    }
                )

        return preserved

    def _lost_protected_elements(
        self,
        *,
        protected_elements: List[Dict[str, Any]],
        revised_text: str,
        revised_elements: Dict[str, Set[str]],
    ) -> List[Dict[str, Any]]:
        lost = []

        for item in protected_elements:
            value = str(item.get("value", ""))
            if value and not self._protected_value_present(value=value, revised_text=revised_text, revised_elements=revised_elements):
                lost.append(
                    {
                        "element_id": item.get("element_id"),
                        "element_type": item.get("element_type"),
                        "value": item.get("value"),
                        "severity": "high" if item.get("element_type") in {"character", "secret", "causal"} else "medium",
                        "description": f"Protected element was not found in revised draft: {item.get('value')}",
                    }
                )

        return lost

    def _protected_value_present(self, *, value: str, revised_text: str, revised_elements: Dict[str, Set[str]]) -> bool:
        if not value:
            return False
        if value.lower() in revised_text.lower():
            return True
        for values in revised_elements.values():
            if value in values or value.lower() in {str(item).lower() for item in values}:
                return True
        return False

    def _element_diff(
        self,
        *,
        from_elements: Dict[str, Set[str]],
        to_elements: Dict[str, Set[str]],
        diff_type: str,
    ) -> List[Dict[str, Any]]:
        results = []
        for element_type, values in to_elements.items():
            old_values = from_elements.get(element_type, set())
            for value in sorted(values - old_values):
                results.append(
                    {
                        "element_id": f"{diff_type}_{element_type}_{self._safe_id(value)}",
                        "element_type": element_type,
                        "value": value,
                        "diff_type": diff_type,
                    }
                )
        return results

    def _quality_delta(self, original: StoryQualityScoreReport | None, revised: StoryQualityScoreReport | None) -> float:
        if not original or not revised:
            return 0.0
        return self._rounded_delta(revised.overall_score - original.overall_score)

    def _anti_genericity_delta(self, original: StoryAntiGenericityReport | None, revised: StoryAntiGenericityReport | None) -> float:
        if not original or not revised:
            return 0.0
        return self._rounded_delta(revised.overall_anti_genericity_score - original.overall_anti_genericity_score)

    def _continuity_delta(self, original: StoryContinuityValidationReport | None, revised: StoryContinuityValidationReport | None) -> float:
        if not original or not revised:
            return 0.0
        return self._rounded_delta(revised.continuity_score - original.continuity_score)

    def _originality_delta(self, original: OriginalityCopyRiskReport | None, revised: OriginalityCopyRiskReport | None) -> float:
        if not original or not revised:
            return 0.0
        return self._rounded_delta(revised.overall_originality_score - original.overall_originality_score)

    def _task_completion_results(
        self,
        *,
        revision_plan: StoryRevisionPlan | None,
        revised_text: str,
        quality_delta: float,
        anti_genericity_delta: float,
        continuity_delta: float,
        originality_delta: float,
    ) -> List[Dict[str, Any]]:
        if not revision_plan:
            return []

        results = []
        lowered = revised_text.lower()

        for step in revision_plan.rewrite_order:
            dimension = str(step.get("dimension", "")).lower()
            task_type = str(step.get("task_type", "")).lower()
            passed = False
            reason = "No direct evidence of completion."

            if "quality" in task_type and quality_delta > 0:
                passed = True
                reason = f"Quality improved by {quality_delta}."
            elif "anti_genericity" in task_type and anti_genericity_delta > 0:
                passed = True
                reason = f"Anti-genericity improved by {anti_genericity_delta}."
            elif "continuity" in task_type and continuity_delta >= 0:
                passed = True
                reason = f"Continuity did not regress; delta {continuity_delta}."
            elif "originality" in task_type and originality_delta >= 0:
                passed = True
                reason = f"Originality did not regress; delta {originality_delta}."
            elif dimension and dimension in lowered:
                passed = True
                reason = "Revised draft contains dimension keyword."

            results.append(
                {
                    "task_result_id": f"task_result_{step.get('task_id')}",
                    "task_id": step.get("task_id"),
                    "task_type": step.get("task_type"),
                    "dimension": step.get("dimension"),
                    "priority": step.get("priority"),
                    "passed": passed,
                    "reason": reason,
                }
            )

        return results

    def _regression_flags(
        self,
        *,
        quality_delta: float,
        anti_genericity_delta: float,
        continuity_delta: float,
        originality_delta: float,
        lost_protected_elements: List[Dict[str, Any]],
        removed_elements: List[Dict[str, Any]],
        revised_originality_report: OriginalityCopyRiskReport | None,
        revised_continuity_report: StoryContinuityValidationReport | None,
    ) -> List[Dict[str, Any]]:
        flags = []

        for name, delta in [
            ("quality", quality_delta),
            ("anti_genericity", anti_genericity_delta),
            ("continuity", continuity_delta),
            ("originality", originality_delta),
        ]:
            if delta < -0.03:
                flags.append(
                    {
                        "flag_id": f"regression_{name}",
                        "flag_type": f"{name}_regression",
                        "severity": "high" if delta < -0.10 else "medium",
                        "description": f"{name} regressed by {delta}.",
                    }
                )

        for item in lost_protected_elements:
            flags.append(
                {
                    "flag_id": f"lost_protected_{item.get('element_id')}",
                    "flag_type": "lost_protected_element",
                    "severity": item.get("severity", "high"),
                    "description": item.get("description"),
                }
            )

        if len(removed_elements) >= 5:
            flags.append(
                {
                    "flag_id": "many_removed_elements",
                    "flag_type": "large_removal",
                    "severity": "medium",
                    "description": f"{len(removed_elements)} known elements were removed from the revised draft.",
                }
            )

        if revised_originality_report and not revised_originality_report.safe_for_export:
            flags.append(
                {
                    "flag_id": "revised_copy_risk_not_safe",
                    "flag_type": "copy_risk",
                    "severity": "high",
                    "description": "Revised draft is not safe for export according to copy-risk report.",
                }
            )

        if revised_continuity_report and not revised_continuity_report.valid:
            flags.append(
                {
                    "flag_id": "revised_continuity_invalid",
                    "flag_type": "continuity",
                    "severity": "high",
                    "description": "Revised draft has invalid continuity report.",
                }
            )

        return self._unique_dicts(flags, key="flag_id")

    def _improvement_score(
        self,
        *,
        quality_delta: float,
        anti_genericity_delta: float,
        continuity_delta: float,
        originality_delta: float,
        task_results: List[Dict[str, Any]],
        text_summary: Dict[str, Any],
    ) -> float:
        score = 0.30
        score += max(0.0, quality_delta) * 0.90
        score += max(0.0, anti_genericity_delta) * 0.75
        score += max(0.0, continuity_delta) * 0.90
        score += max(0.0, originality_delta) * 0.65

        if task_results:
            completed = len([item for item in task_results if item.get("passed")])
            score += (completed / len(task_results)) * 0.25

        if text_summary.get("change_ratio", 0.0) > 0.02:
            score += 0.05

        return self._bounded(score)

    def _regression_risk_score(
        self,
        *,
        regression_flags: List[Dict[str, Any]],
        lost_protected_elements: List[Dict[str, Any]],
    ) -> float:
        score = 0.0
        for flag in regression_flags:
            score += 0.25 if flag.get("severity") == "high" else 0.12
        score += len(lost_protected_elements) * 0.10
        return self._bounded(score)

    def _approval_requirements(
        self,
        *,
        regression_flags: List[Dict[str, Any]],
        lost_protected_elements: List[Dict[str, Any]],
        revised_originality_report: OriginalityCopyRiskReport | None,
        revised_continuity_report: StoryContinuityValidationReport | None,
        improvement_score: float,
        regression_risk_score: float,
    ) -> List[Dict[str, Any]]:
        requirements = []

        for flag in regression_flags:
            if flag.get("severity") == "high":
                requirements.append(
                    {
                        "requirement_id": f"approval_fix_{flag.get('flag_id')}",
                        "requirement_type": flag.get("flag_type"),
                        "priority": "high",
                        "instruction": flag.get("description"),
                    }
                )

        for item in lost_protected_elements:
            requirements.append(
                {
                    "requirement_id": f"approval_restore_{item.get('element_id')}",
                    "requirement_type": "restore_protected_element",
                    "priority": "high",
                    "instruction": f"Restore protected element: {item.get('value')}",
                }
            )

        if revised_originality_report and not revised_originality_report.safe_for_export:
            requirements.append(
                {
                    "requirement_id": "approval_copy_risk_safe_export",
                    "requirement_type": "copy_risk",
                    "priority": "critical",
                    "instruction": "Resolve copy-risk blockers before approving revision.",
                }
            )

        if revised_continuity_report and not revised_continuity_report.valid:
            requirements.append(
                {
                    "requirement_id": "approval_continuity_valid",
                    "requirement_type": "continuity",
                    "priority": "critical",
                    "instruction": "Repair continuity before approving revision.",
                }
            )

        if improvement_score < 0.45:
            requirements.append(
                {
                    "requirement_id": "approval_minimum_improvement",
                    "requirement_type": "improvement",
                    "priority": "medium",
                    "instruction": "Revision improvement is too small; apply another targeted pass.",
                }
            )

        if regression_risk_score > 0.35:
            requirements.append(
                {
                    "requirement_id": "approval_regression_risk",
                    "requirement_type": "regression_risk",
                    "priority": "high",
                    "instruction": "Regression risk is too high; inspect lost elements and score deltas.",
                }
            )

        return self._unique_dicts(requirements, key="requirement_id")

    def _downstream_constraints(
        self,
        *,
        approved: bool,
        lost_protected_elements: List[Dict[str, Any]],
        regression_flags: List[Dict[str, Any]],
        revised_continuity_report: StoryContinuityValidationReport | None,
        revised_originality_report: OriginalityCopyRiskReport | None,
    ) -> Dict[str, Any]:
        return {
            "approved_for_improvement_loop": approved,
            "must_restore_lost_element_ids": [item.get("element_id") for item in lost_protected_elements],
            "must_resolve_regression_flag_ids": [item.get("flag_id") for item in regression_flags],
            "revised_continuity_score": revised_continuity_report.continuity_score if revised_continuity_report else None,
            "revised_originality_score": revised_originality_report.overall_originality_score if revised_originality_report else None,
            "rules": [
                "Do not accept a revision that drops protected characters, secrets, causal IDs, or world details.",
                "Do not accept a revision that improves prose while worsening copy-risk or continuity.",
                "Use comparison output to guide the generation improvement loop.",
            ],
        }

    def _warnings(
        self,
        *,
        revision_plan: StoryRevisionPlan | None,
        regression_flags: List[Dict[str, Any]],
        approval_requirements: List[Dict[str, Any]],
    ) -> List[str]:
        warnings = []
        if not revision_plan:
            warnings.append("No revision plan supplied; task completion checks are limited.")
        if regression_flags:
            warnings.append(f"{len(regression_flags)} regression flag(s) detected.")
        if approval_requirements:
            warnings.append(f"{len(approval_requirements)} approval requirement(s) remain.")
        return warnings

    def _appears_in_text(self, value: str, text: str, tokens: Set[str]) -> bool:
        if not value:
            return False
        lowered = value.lower()
        return lowered in text.lower() or lowered in tokens

    def _sentences(self, text: str) -> List[str]:
        rough = text.replace("!", ".").replace("?", ".").split(".")
        return [item.strip() for item in rough if item.strip()]

    def _rounded_delta(self, value: float) -> float:
        return round(float(value), 3)

    def _safe_id(self, value: Any) -> str:
        return "".join(ch.lower() if ch.isalnum() else "_" for ch in str(value)).strip("_")[:80] or "item"

    def _bounded(self, value: float) -> float:
        return round(max(0.0, min(1.0, float(value))), 3)

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

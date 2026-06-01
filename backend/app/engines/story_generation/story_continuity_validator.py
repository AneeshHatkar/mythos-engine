from __future__ import annotations

from typing import Any, Dict, List

from backend.app.schemas.story_generation import (
    AdaptiveStoryPatternPlan,
    GameInteractiveScenePackage,
    GeneratedChapter,
    LongFormContinuationAnchor,
    PlotOutline,
    ScreenplayMovieFormatPackage,
    SeriesSeasonFormatPackage,
    StoryAntiGenericityReport,
    StoryContinuityValidationReport,
    StoryQualityScoreReport,
)


class StoryContinuityValidator:
    """Validates story-level continuity across generated narrative material.

    Locked Chunk 5.34. This validator checks that characters, relationships,
    secrets, causality, world details, open loops, formats, and interactive
    state remain consistent across plot outlines, chapters, anchors, and
    generated format packages.
    """

    engine_name = "story_generation.story_continuity_validator"

    def validate_story_continuity(
        self,
        *,
        source_id: str,
        plot_outline: PlotOutline | None = None,
        chapter: GeneratedChapter | None = None,
        continuation_anchor: LongFormContinuationAnchor | None = None,
        adaptive_pattern_plan: AdaptiveStoryPatternPlan | None = None,
        quality_report: StoryQualityScoreReport | None = None,
        anti_genericity_report: StoryAntiGenericityReport | None = None,
        screenplay_movie_package: ScreenplayMovieFormatPackage | None = None,
        series_package: SeriesSeasonFormatPackage | None = None,
        game_package: GameInteractiveScenePackage | None = None,
        story_context: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        story_context = story_context or {}

        expected = self._expected_threads(
            plot_outline=plot_outline,
            chapter=chapter,
            continuation_anchor=continuation_anchor,
            adaptive_pattern_plan=adaptive_pattern_plan,
            story_context=story_context,
        )
        observed = self._observed_threads(
            chapter=chapter,
            continuation_anchor=continuation_anchor,
            screenplay_movie_package=screenplay_movie_package,
            series_package=series_package,
            game_package=game_package,
            story_context=story_context,
        )

        continuity_breaks = self._continuity_breaks(expected=expected, observed=observed)
        continuity_warnings = self._continuity_warnings(
            expected=expected,
            observed=observed,
            plot_outline=plot_outline,
            chapter=chapter,
            continuation_anchor=continuation_anchor,
            screenplay_movie_package=screenplay_movie_package,
            series_package=series_package,
            game_package=game_package,
            quality_report=quality_report,
            anti_genericity_report=anti_genericity_report,
        )

        character_score = self._dimension_score(expected["character_ids"], observed["character_ids"])
        relationship_score = self._dimension_score(expected["relationship_ids"], observed["relationship_ids"])
        secret_score = self._dimension_score(expected["secret_ids"], observed["secret_ids"])
        causal_score = self._dimension_score(expected["causal_ids"], observed["causal_ids"])
        world_score = self._dimension_score(expected["world_details"], observed["world_details"])
        open_loop_score = self._dimension_score(expected["open_loop_ids"], observed["open_loop_ids"])
        format_score = self._format_continuity_score(
            screenplay_movie_package=screenplay_movie_package,
            series_package=series_package,
            game_package=game_package,
        )

        continuity_score = self._overall_score(
            character_score=character_score,
            relationship_score=relationship_score,
            secret_score=secret_score,
            causal_score=causal_score,
            world_score=world_score,
            open_loop_score=open_loop_score,
            format_score=format_score,
            continuity_breaks=continuity_breaks,
        )

        report = StoryContinuityValidationReport(
            continuity_report_id=f"story_continuity_{source_id}",
            source_id=source_id,
            valid=not any(item.get("severity") == "blocker" for item in continuity_breaks),
            continuity_score=continuity_score,
            readiness_level=self._readiness_level(score=continuity_score, continuity_breaks=continuity_breaks),
            character_continuity_score=character_score,
            relationship_continuity_score=relationship_score,
            secret_continuity_score=secret_score,
            causal_continuity_score=causal_score,
            world_continuity_score=world_score,
            open_loop_continuity_score=open_loop_score,
            format_continuity_score=format_score,
            checked_character_ids=expected["character_ids"],
            checked_relationship_ids=expected["relationship_ids"],
            checked_secret_ids=expected["secret_ids"],
            checked_causal_ids=expected["causal_ids"],
            checked_world_details=expected["world_details"],
            checked_open_loop_ids=expected["open_loop_ids"],
            continuity_breaks=continuity_breaks,
            continuity_warnings=continuity_warnings,
            repair_targets=self._repair_targets(continuity_breaks=continuity_breaks, continuity_warnings=continuity_warnings),
            preserved_threads=self._preserved_threads(expected=expected, observed=observed),
            downstream_constraints=self._downstream_constraints(expected=expected, continuity_score=continuity_score),
            warnings=self._warnings(
                plot_outline=plot_outline,
                chapter=chapter,
                continuation_anchor=continuation_anchor,
                continuity_breaks=continuity_breaks,
                continuity_warnings=continuity_warnings,
            ),
        )

        return {
            "success": True,
            "engine_name": self.engine_name,
            "story_continuity_validation_report": report,
            "story_continuity_validation_report_dict": report.model_dump(mode="json"),
            "handoff_to_next_engine": {
                "next_engine": "story_generation.originality_copy_risk_guard",
                "payload_keys": [
                    "story_continuity_validation_report",
                    "story_anti_genericity_report",
                    "story_quality_score_report",
                    "plot_outline",
                    "generated_chapter",
                    "format_packages",
                    "story_context",
                ],
            },
        }

    def validate_report(self, *, report: StoryContinuityValidationReport) -> Dict[str, Any]:
        blockers: List[str] = []
        warnings: List[str] = []
        passed: List[str] = []

        if report.continuity_report_id:
            passed.append("continuity_report_id_present")
        else:
            blockers.append("continuity_report_id missing")

        if report.source_id:
            passed.append("source_id_present")
        else:
            blockers.append("source_id missing")

        scores = [
            report.continuity_score,
            report.character_continuity_score,
            report.relationship_continuity_score,
            report.secret_continuity_score,
            report.causal_continuity_score,
            report.world_continuity_score,
            report.open_loop_continuity_score,
            report.format_continuity_score,
        ]

        if all(0.0 <= score <= 1.0 for score in scores):
            passed.append("scores_bounded")
        else:
            blockers.append("one or more continuity scores out of bounds")

        if report.readiness_level in {"ready", "needs_light_repair", "needs_repair", "blocked"}:
            passed.append("readiness_level_valid")
        else:
            blockers.append("invalid readiness level")

        if report.downstream_constraints:
            passed.append("downstream_constraints_present")
        else:
            warnings.append("downstream constraints missing")

        if report.continuity_breaks:
            warnings.append("continuity breaks present")

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

    def summarize_report(self, *, report: StoryContinuityValidationReport) -> Dict[str, Any]:
        weakest = self._weakest_dimension(report=report)

        return {
            "success": True,
            "engine_name": self.engine_name,
            "summary": {
                "continuity_report_id": report.continuity_report_id,
                "source_id": report.source_id,
                "valid": report.valid,
                "continuity_score": report.continuity_score,
                "readiness_level": report.readiness_level,
                "weakest_dimension": weakest["dimension"],
                "weakest_score": weakest["score"],
                "checked_character_count": len(report.checked_character_ids),
                "checked_relationship_count": len(report.checked_relationship_ids),
                "checked_secret_count": len(report.checked_secret_ids),
                "checked_causal_count": len(report.checked_causal_ids),
                "checked_world_detail_count": len(report.checked_world_details),
                "checked_open_loop_count": len(report.checked_open_loop_ids),
                "continuity_break_count": len(report.continuity_breaks),
                "repair_target_count": len(report.repair_targets),
                "warning_count": len(report.warnings),
            },
        }

    def build_continuity_report_text(self, *, report: StoryContinuityValidationReport) -> Dict[str, Any]:
        lines = [
            f"# Story Continuity Report: {report.source_id}",
            "",
            f"Valid: {report.valid}",
            f"Continuity score: {report.continuity_score}",
            f"Readiness: {report.readiness_level}",
            "",
            "## Checked Threads",
            f"- Characters: {', '.join(report.checked_character_ids)}",
            f"- Relationships: {', '.join(report.checked_relationship_ids)}",
            f"- Secrets: {', '.join(report.checked_secret_ids)}",
            f"- Causal IDs: {', '.join(report.checked_causal_ids)}",
            f"- World details: {', '.join(report.checked_world_details)}",
            f"- Open loops: {', '.join(report.checked_open_loop_ids)}",
            "",
            "## Continuity Breaks",
        ]

        for item in report.continuity_breaks:
            lines.append(f"- [{item.get('severity')}] {item.get('break_type')}: {item.get('description')}")

        lines.append("")
        lines.append("## Repair Targets")
        for item in report.repair_targets:
            lines.append(f"- [{item.get('priority')}] {item.get('target_type')}: {item.get('instruction')}")

        return {
            "success": True,
            "engine_name": self.engine_name,
            "continuity_report_text": "\n".join(lines),
        }

    def _expected_threads(
        self,
        *,
        plot_outline: PlotOutline | None,
        chapter: GeneratedChapter | None,
        continuation_anchor: LongFormContinuationAnchor | None,
        adaptive_pattern_plan: AdaptiveStoryPatternPlan | None,
        story_context: Dict[str, Any],
    ) -> Dict[str, List[str]]:
        expected = {
            "character_ids": [],
            "relationship_ids": [],
            "secret_ids": [],
            "causal_ids": [],
            "world_details": [],
            "open_loop_ids": [],
        }

        if plot_outline:
            expected["character_ids"].extend(plot_outline.continuity_requirements.get("required_character_ids", []))
            expected["character_ids"].extend([item.get("character_id") for item in plot_outline.character_arc_threads if item.get("character_id")])

            expected["relationship_ids"].extend(plot_outline.continuity_requirements.get("required_relationship_ids", []))
            expected["relationship_ids"].extend([item.get("relationship_id") for item in plot_outline.relationship_arc_threads if item.get("relationship_id")])

            expected["secret_ids"].extend(plot_outline.continuity_requirements.get("required_secret_ids", []))
            expected["secret_ids"].extend([item.get("secret_id") for item in plot_outline.secret_threads if item.get("secret_id")])

            expected["causal_ids"].extend(plot_outline.continuity_requirements.get("required_causal_ids", []))
            expected["causal_ids"].extend([item.get("causal_id") for item in plot_outline.causal_threads if item.get("causal_id")])

            expected["world_details"].extend(plot_outline.continuity_requirements.get("required_world_details", []))
            expected["world_details"].extend([item.get("world_detail") for item in plot_outline.world_state_threads if item.get("world_detail")])

            expected["open_loop_ids"].extend([item.get("loop_id") for item in plot_outline.open_loops if item.get("loop_id")])
            expected["open_loop_ids"].extend(plot_outline.continuity_requirements.get("open_loop_ids", []))

        if chapter:
            expected["character_ids"].extend(chapter.used_character_ids)
            expected["relationship_ids"].extend(chapter.used_relationship_ids)
            expected["secret_ids"].extend(chapter.used_secret_ids)
            expected["causal_ids"].extend(chapter.used_causal_ids)
            expected["world_details"].extend(chapter.used_world_details)
            expected["open_loop_ids"].extend([item.get("loop_id") for item in chapter.open_loops if item.get("loop_id")])

        if continuation_anchor:
            expected["character_ids"].extend(continuation_anchor.active_character_ids)
            expected["relationship_ids"].extend(continuation_anchor.active_relationship_ids)
            expected["secret_ids"].extend(continuation_anchor.active_secret_ids)
            expected["causal_ids"].extend(continuation_anchor.active_causal_ids)
            expected["world_details"].extend(continuation_anchor.active_world_details)
            expected["open_loop_ids"].extend([item.get("loop_id") for item in continuation_anchor.open_loops if item.get("loop_id")])

        if adaptive_pattern_plan:
            expected["character_ids"].extend([item.get("character_id") for item in adaptive_pattern_plan.character_pattern_assignments if item.get("character_id")])
            expected["relationship_ids"].extend([item.get("relationship_id") for item in adaptive_pattern_plan.relationship_pattern_assignments if item.get("relationship_id")])
            expected["secret_ids"].extend([item.get("secret_id") for item in adaptive_pattern_plan.secret_pattern_assignments if item.get("secret_id")])
            expected["causal_ids"].extend([item.get("causal_id") for item in adaptive_pattern_plan.causal_pattern_assignments if item.get("causal_id")])
            expected["world_details"].extend([item.get("world_detail") for item in adaptive_pattern_plan.world_pattern_assignments if item.get("world_detail")])

        continuity = story_context.get("continuity_requirements", {})
        if isinstance(continuity, dict):
            expected["character_ids"].extend(continuity.get("required_character_ids", []))
            expected["relationship_ids"].extend(continuity.get("required_relationship_ids", []))
            expected["secret_ids"].extend(continuity.get("required_secret_ids", []))
            expected["causal_ids"].extend(continuity.get("required_causal_ids", []))
            expected["world_details"].extend(continuity.get("required_world_details", []))
            expected["open_loop_ids"].extend(continuity.get("open_loop_ids", []))

        return {key: self._unique([value for value in values if value]) for key, values in expected.items()}

    def _observed_threads(
        self,
        *,
        chapter: GeneratedChapter | None,
        continuation_anchor: LongFormContinuationAnchor | None,
        screenplay_movie_package: ScreenplayMovieFormatPackage | None,
        series_package: SeriesSeasonFormatPackage | None,
        game_package: GameInteractiveScenePackage | None,
        story_context: Dict[str, Any],
    ) -> Dict[str, List[str]]:
        observed = {
            "character_ids": [],
            "relationship_ids": [],
            "secret_ids": [],
            "causal_ids": [],
            "world_details": [],
            "open_loop_ids": [],
        }

        if chapter:
            observed["character_ids"].extend(chapter.used_character_ids)
            observed["relationship_ids"].extend(chapter.used_relationship_ids)
            observed["secret_ids"].extend(chapter.used_secret_ids)
            observed["causal_ids"].extend(chapter.used_causal_ids)
            observed["world_details"].extend(chapter.used_world_details)
            observed["open_loop_ids"].extend([item.get("loop_id") for item in chapter.open_loops if item.get("loop_id")])

        if continuation_anchor:
            observed["character_ids"].extend(continuation_anchor.active_character_ids)
            observed["relationship_ids"].extend(continuation_anchor.active_relationship_ids)
            observed["secret_ids"].extend(continuation_anchor.active_secret_ids)
            observed["causal_ids"].extend(continuation_anchor.active_causal_ids)
            observed["world_details"].extend(continuation_anchor.active_world_details)
            observed["open_loop_ids"].extend([item.get("loop_id") for item in continuation_anchor.open_loops if item.get("loop_id")])

        if screenplay_movie_package:
            reqs = screenplay_movie_package.continuity_requirements
            observed["character_ids"].extend(reqs.get("used_character_ids", []))
            observed["secret_ids"].extend(reqs.get("used_secret_ids", []))
            observed["causal_ids"].extend(reqs.get("used_causal_ids", []))
            observed["world_details"].extend([item.get("source_detail") for item in screenplay_movie_package.visual_motifs if item.get("source_detail")])

        if series_package:
            for dynamic in series_package.recurring_character_dynamics:
                if dynamic.get("character_id"):
                    observed["character_ids"].append(dynamic["character_id"])
                if dynamic.get("relationship_id"):
                    observed["relationship_ids"].append(dynamic["relationship_id"])
            observed["open_loop_ids"].extend([item.get("source_id") for item in series_package.season_arc_carryover if item.get("source_id")])

        if game_package:
            observed["character_ids"].extend([item.get("npc_id") for item in game_package.npc_dialogue_blocks if item.get("npc_id")])
            observed["relationship_ids"].extend([item.get("relationship_id") for item in game_package.relationship_state_hooks if item.get("relationship_id")])
            observed["secret_ids"].extend([item.get("secret_id") for item in game_package.secret_state_hooks if item.get("secret_id")])
            observed["causal_ids"].extend([item.get("causal_id") for item in game_package.causal_state_hooks if item.get("causal_id")])
            observed["world_details"].extend([item.get("world_detail") for item in game_package.world_state_hooks if item.get("world_detail")])
            observed["open_loop_ids"].extend([item.get("source_thread_id") for item in game_package.quest_log_updates if item.get("source_thread_id")])

        observed_context = story_context.get("observed_threads", {})
        if isinstance(observed_context, dict):
            observed["character_ids"].extend(observed_context.get("character_ids", []))
            observed["relationship_ids"].extend(observed_context.get("relationship_ids", []))
            observed["secret_ids"].extend(observed_context.get("secret_ids", []))
            observed["causal_ids"].extend(observed_context.get("causal_ids", []))
            observed["world_details"].extend(observed_context.get("world_details", []))
            observed["open_loop_ids"].extend(observed_context.get("open_loop_ids", []))

        return {key: self._unique([value for value in values if value]) for key, values in observed.items()}

    def _continuity_breaks(self, *, expected: Dict[str, List[str]], observed: Dict[str, List[str]]) -> List[Dict[str, Any]]:
        breaks: List[Dict[str, Any]] = []

        severity_by_key = {
            "character_ids": "blocker",
            "relationship_ids": "major",
            "secret_ids": "blocker",
            "causal_ids": "blocker",
            "world_details": "major",
            "open_loop_ids": "major",
        }

        for key, expected_values in expected.items():
            observed_values = set(observed.get(key, []))
            for value in expected_values:
                if value not in observed_values:
                    breaks.append(
                        {
                            "break_id": f"missing_{key}_{self._safe_id(value)}",
                            "break_type": f"missing_{key}",
                            "missing_value": value,
                            "severity": severity_by_key.get(key, "major"),
                            "description": f"Expected {key} value {value} was not preserved in observed story material.",
                        }
                    )

        return breaks

    def _continuity_warnings(
        self,
        *,
        expected: Dict[str, List[str]],
        observed: Dict[str, List[str]],
        plot_outline: PlotOutline | None,
        chapter: GeneratedChapter | None,
        continuation_anchor: LongFormContinuationAnchor | None,
        screenplay_movie_package: ScreenplayMovieFormatPackage | None,
        series_package: SeriesSeasonFormatPackage | None,
        game_package: GameInteractiveScenePackage | None,
        quality_report: StoryQualityScoreReport | None,
        anti_genericity_report: StoryAntiGenericityReport | None,
    ) -> List[Dict[str, Any]]:
        warnings: List[Dict[str, Any]] = []

        for key, observed_values in observed.items():
            expected_values = set(expected.get(key, []))
            extra_values = [value for value in observed_values if value not in expected_values]
            if extra_values:
                warnings.append(
                    {
                        "warning_id": f"extra_{key}",
                        "warning_type": "unexpected_thread",
                        "severity": "minor",
                        "description": f"Observed extra {key}: {extra_values}",
                        "values": extra_values,
                    }
                )

        if plot_outline and plot_outline.open_loops and not continuation_anchor:
            warnings.append(
                {
                    "warning_id": "open_loops_without_anchor",
                    "warning_type": "missing_anchor",
                    "severity": "major",
                    "description": "Plot outline has open loops but no continuation anchor was supplied.",
                }
            )

        if quality_report and quality_report.readiness_level in {"blocked", "needs_revision"}:
            warnings.append(
                {
                    "warning_id": "quality_report_not_ready",
                    "warning_type": "quality_dependency",
                    "severity": "major",
                    "description": f"Quality report readiness is {quality_report.readiness_level}.",
                }
            )

        if anti_genericity_report and anti_genericity_report.genericity_risk_level in {"high", "critical"}:
            warnings.append(
                {
                    "warning_id": "anti_genericity_risk",
                    "warning_type": "anti_genericity_dependency",
                    "severity": "major",
                    "description": f"Anti-genericity risk is {anti_genericity_report.genericity_risk_level}.",
                }
            )

        if game_package and game_package.choice_menu and not game_package.state_deltas:
            warnings.append(
                {
                    "warning_id": "interactive_choices_without_state_deltas",
                    "warning_type": "interactive_state",
                    "severity": "major",
                    "description": "Game package has choices but no state deltas.",
                }
            )

        return warnings

    def _dimension_score(self, expected_values: List[str], observed_values: List[str]) -> float:
        if not expected_values:
            return 1.0
        observed_set = set(observed_values)
        preserved = len([value for value in expected_values if value in observed_set])
        return self._bounded(preserved / len(expected_values))

    def _format_continuity_score(
        self,
        *,
        screenplay_movie_package: ScreenplayMovieFormatPackage | None,
        series_package: SeriesSeasonFormatPackage | None,
        game_package: GameInteractiveScenePackage | None,
    ) -> float:
        score = 0.35
        if screenplay_movie_package:
            score += 0.20 if screenplay_movie_package.formatted_text else 0.0
            score += 0.10 if screenplay_movie_package.continuity_requirements else 0.0
        if series_package:
            score += 0.15 if series_package.episode_cards else 0.0
            score += 0.10 if series_package.season_arc_carryover else 0.0
        if game_package:
            score += 0.10 if game_package.choice_menu else 0.0
            score += 0.10 if game_package.state_deltas else 0.0
        return self._bounded(score)

    def _overall_score(
        self,
        *,
        character_score: float,
        relationship_score: float,
        secret_score: float,
        causal_score: float,
        world_score: float,
        open_loop_score: float,
        format_score: float,
        continuity_breaks: List[Dict[str, Any]],
    ) -> float:
        score = (
            character_score * 0.16
            + relationship_score * 0.12
            + secret_score * 0.16
            + causal_score * 0.18
            + world_score * 0.14
            + open_loop_score * 0.12
            + format_score * 0.12
        )

        blocker_count = len([item for item in continuity_breaks if item.get("severity") == "blocker"])
        major_count = len([item for item in continuity_breaks if item.get("severity") == "major"])

        score -= blocker_count * 0.07
        score -= major_count * 0.035

        return self._bounded(score)

    def _readiness_level(self, *, score: float, continuity_breaks: List[Dict[str, Any]]) -> str:
        blocker_count = len([item for item in continuity_breaks if item.get("severity") == "blocker"])
        major_count = len([item for item in continuity_breaks if item.get("severity") == "major"])

        if blocker_count > 0:
            return "blocked"
        if score >= 0.85 and major_count == 0:
            return "ready"
        if score >= 0.70 and major_count <= 2:
            return "needs_light_repair"
        return "needs_repair"

    def _repair_targets(
        self,
        *,
        continuity_breaks: List[Dict[str, Any]],
        continuity_warnings: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        targets: List[Dict[str, Any]] = []

        for item in continuity_breaks:
            targets.append(
                {
                    "repair_target_id": f"repair_{item.get('break_id')}",
                    "target_type": item.get("break_type"),
                    "priority": "high" if item.get("severity") == "blocker" else "medium",
                    "instruction": self._repair_instruction(item),
                }
            )

        for item in continuity_warnings:
            if item.get("severity") in {"major", "blocker"}:
                targets.append(
                    {
                        "repair_target_id": f"repair_{item.get('warning_id')}",
                        "target_type": item.get("warning_type"),
                        "priority": "medium",
                        "instruction": item.get("description"),
                    }
                )

        return self._unique_dicts(targets, key="repair_target_id")

    def _repair_instruction(self, continuity_break: Dict[str, Any]) -> str:
        break_type = continuity_break.get("break_type", "")
        value = continuity_break.get("missing_value", "")

        if "character" in break_type:
            return f"Restore character continuity for {value}; preserve voice, goal, knowledge, and emotional state."
        if "relationship" in break_type:
            return f"Restore relationship continuity for {value}; preserve trust, resentment, repair, and betrayal pressure."
        if "secret" in break_type:
            return f"Restore secret continuity for {value}; preserve reveal timing and who-knows-what."
        if "causal" in break_type:
            return f"Restore causal continuity for {value}; preserve setup, choice, consequence, and payoff."
        if "world" in break_type:
            return f"Restore world continuity for {value}; preserve rules, location, object, culture, or environment consequence."
        if "open_loop" in break_type:
            return f"Restore open loop continuity for {value}; resolve, escalate, or explicitly carry it forward."

        return f"Restore missing continuity value {value}."

    def _preserved_threads(self, *, expected: Dict[str, List[str]], observed: Dict[str, List[str]]) -> List[Dict[str, Any]]:
        preserved: List[Dict[str, Any]] = []

        for key, expected_values in expected.items():
            observed_set = set(observed.get(key, []))
            for value in expected_values:
                if value in observed_set:
                    preserved.append(
                        {
                            "thread_id": f"preserved_{key}_{self._safe_id(value)}",
                            "thread_type": key,
                            "value": value,
                            "description": f"{value} is preserved for {key}.",
                        }
                    )

        return preserved

    def _downstream_constraints(self, *, expected: Dict[str, List[str]], continuity_score: float) -> Dict[str, Any]:
        return {
            "continuity_score": continuity_score,
            "must_preserve_character_ids": expected["character_ids"],
            "must_preserve_relationship_ids": expected["relationship_ids"],
            "must_preserve_secret_ids": expected["secret_ids"],
            "must_preserve_causal_ids": expected["causal_ids"],
            "must_preserve_world_details": expected["world_details"],
            "must_preserve_open_loop_ids": expected["open_loop_ids"],
            "rules": [
                "Do not remove expected characters without explicit story reason.",
                "Do not reveal secrets unless reveal timing allows it.",
                "Do not orphan causal events without consequences.",
                "Do not treat world details as decoration; preserve their functional consequences.",
                "Do not drop open loops silently.",
            ],
        }

    def _warnings(
        self,
        *,
        plot_outline: PlotOutline | None,
        chapter: GeneratedChapter | None,
        continuation_anchor: LongFormContinuationAnchor | None,
        continuity_breaks: List[Dict[str, Any]],
        continuity_warnings: List[Dict[str, Any]],
    ) -> List[str]:
        warnings: List[str] = []

        if not plot_outline and not chapter:
            warnings.append("No plot outline or chapter supplied; continuity validation has limited context.")

        if plot_outline and plot_outline.open_loops and not continuation_anchor:
            warnings.append("Open loops exist but no continuation anchor was supplied.")

        if continuity_breaks:
            warnings.append(f"{len(continuity_breaks)} continuity break(s) detected.")

        if continuity_warnings:
            warnings.append(f"{len(continuity_warnings)} continuity warning(s) detected.")

        return warnings

    def _weakest_dimension(self, *, report: StoryContinuityValidationReport) -> Dict[str, Any]:
        dimensions = [
            {"dimension": "character", "score": report.character_continuity_score},
            {"dimension": "relationship", "score": report.relationship_continuity_score},
            {"dimension": "secret", "score": report.secret_continuity_score},
            {"dimension": "causal", "score": report.causal_continuity_score},
            {"dimension": "world", "score": report.world_continuity_score},
            {"dimension": "open_loop", "score": report.open_loop_continuity_score},
            {"dimension": "format", "score": report.format_continuity_score},
        ]
        return min(dimensions, key=lambda item: item["score"])

    def _safe_id(self, value: str) -> str:
        return "".join(ch.lower() if ch.isalnum() else "_" for ch in str(value)).strip("_")[:60] or "item"

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

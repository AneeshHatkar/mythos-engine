from __future__ import annotations

from typing import Any, Dict, List

from backend.app.schemas.story_generation import (
    AdaptiveStoryPatternPlan,
    CommercialAppealReport,
    FormatAdaptationPlan,
    GameInteractiveScenePackage,
    GeneratedChapter,
    MultiScenePacingReport,
    MultiWorldMultiCastScalingPlan,
    PlotOutline,
    ScreenplayMovieFormatPackage,
    SeriesSeasonFormatPackage,
    StoryQualityScoreReport,
)


class StoryQualityScorer:
    """Scores story quality across structure, continuity, patterning, and format.

    Locked Chunk 5.32. This is the official story-level quality scorer. It
    aggregates earlier support engines into one scorecard that tells the next
    systems what is strong, weak, generic, risky, or ready.
    """

    engine_name = "story_generation.story_quality_scorer"

    def score_story_quality(
        self,
        *,
        source_id: str,
        plot_outline: PlotOutline | None = None,
        chapter: GeneratedChapter | None = None,
        format_plan: FormatAdaptationPlan | None = None,
        adaptive_pattern_plan: AdaptiveStoryPatternPlan | None = None,
        pacing_report: MultiScenePacingReport | None = None,
        commercial_report: CommercialAppealReport | None = None,
        screenplay_movie_package: ScreenplayMovieFormatPackage | None = None,
        series_package: SeriesSeasonFormatPackage | None = None,
        game_package: GameInteractiveScenePackage | None = None,
        scaling_plan: MultiWorldMultiCastScalingPlan | None = None,
        story_context: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        story_context = story_context or {}

        structure_score = self._structure_score(plot_outline=plot_outline, chapter=chapter, series_package=series_package)
        character_score = self._character_score(plot_outline=plot_outline, chapter=chapter, adaptive_pattern_plan=adaptive_pattern_plan)
        relationship_score = self._relationship_score(plot_outline=plot_outline, chapter=chapter, adaptive_pattern_plan=adaptive_pattern_plan)
        secret_mystery_score = self._secret_mystery_score(plot_outline=plot_outline, chapter=chapter, adaptive_pattern_plan=adaptive_pattern_plan, game_package=game_package)
        causal_score = self._causal_score(plot_outline=plot_outline, chapter=chapter, adaptive_pattern_plan=adaptive_pattern_plan, pacing_report=pacing_report)
        world_score = self._world_score(plot_outline=plot_outline, chapter=chapter, scaling_plan=scaling_plan, game_package=game_package)
        pacing_score = self._pacing_score(pacing_report=pacing_report, plot_outline=plot_outline, chapter=chapter)
        format_score = self._format_score(format_plan=format_plan, screenplay_movie_package=screenplay_movie_package, series_package=series_package, game_package=game_package)
        anti_generic_score = self._anti_generic_score(adaptive_pattern_plan=adaptive_pattern_plan, plot_outline=plot_outline, story_context=story_context)
        commercial_potential_score = self._commercial_potential_score(commercial_report=commercial_report, plot_outline=plot_outline, story_context=story_context)

        overall = self._overall_score(
            structure_score=structure_score,
            character_score=character_score,
            relationship_score=relationship_score,
            secret_mystery_score=secret_mystery_score,
            causal_score=causal_score,
            world_score=world_score,
            pacing_score=pacing_score,
            format_score=format_score,
            anti_generic_score=anti_generic_score,
            commercial_potential_score=commercial_potential_score,
        )

        breakdown = self._dimension_breakdown(
            structure_score=structure_score,
            character_score=character_score,
            relationship_score=relationship_score,
            secret_mystery_score=secret_mystery_score,
            causal_score=causal_score,
            world_score=world_score,
            pacing_score=pacing_score,
            format_score=format_score,
            anti_generic_score=anti_generic_score,
            commercial_potential_score=commercial_potential_score,
        )

        quality_gates = self._quality_gates(breakdown=breakdown, overall=overall)
        revision_priorities = self._revision_priorities(breakdown=breakdown, quality_gates=quality_gates)

        report = StoryQualityScoreReport(
            quality_report_id=f"story_quality_score_{source_id}",
            source_id=source_id,
            overall_score=overall,
            readiness_level=self._readiness_level(overall=overall, quality_gates=quality_gates),
            structure_score=structure_score,
            character_score=character_score,
            relationship_score=relationship_score,
            secret_mystery_score=secret_mystery_score,
            causal_score=causal_score,
            world_score=world_score,
            pacing_score=pacing_score,
            format_score=format_score,
            anti_generic_score=anti_generic_score,
            commercial_potential_score=commercial_potential_score,
            dimension_breakdown=breakdown,
            quality_gates=quality_gates,
            revision_priorities=revision_priorities,
            strengths=self._strengths(breakdown=breakdown),
            risks=self._risks(
                breakdown=breakdown,
                adaptive_pattern_plan=adaptive_pattern_plan,
                pacing_report=pacing_report,
                scaling_plan=scaling_plan,
            ),
            warnings=self._warnings(
                plot_outline=plot_outline,
                chapter=chapter,
                adaptive_pattern_plan=adaptive_pattern_plan,
                pacing_report=pacing_report,
                format_plan=format_plan,
            ),
        )

        return {
            "success": True,
            "engine_name": self.engine_name,
            "story_quality_score_report": report,
            "story_quality_score_report_dict": report.model_dump(mode="json"),
            "handoff_to_next_engine": {
                "next_engine": "story_generation.story_anti_genericity_validator",
                "payload_keys": [
                    "story_quality_score_report",
                    "adaptive_story_pattern_plan",
                    "plot_outline",
                    "generated_chapter",
                    "format_packages",
                    "story_context",
                ],
            },
        }

    def validate_quality_report(self, *, report: StoryQualityScoreReport) -> Dict[str, Any]:
        blockers: List[str] = []
        warnings: List[str] = []
        passed: List[str] = []

        if not report.quality_report_id:
            blockers.append("quality_report_id missing")
        else:
            passed.append("quality_report_id_present")

        if report.source_id:
            passed.append("source_id_present")
        else:
            blockers.append("source_id missing")

        scores = [
            report.overall_score,
            report.structure_score,
            report.character_score,
            report.relationship_score,
            report.secret_mystery_score,
            report.causal_score,
            report.world_score,
            report.pacing_score,
            report.format_score,
            report.anti_generic_score,
            report.commercial_potential_score,
        ]

        if all(0.0 <= score <= 1.0 for score in scores):
            passed.append("scores_bounded")
        else:
            blockers.append("one or more scores out of bounds")

        if report.dimension_breakdown:
            passed.append("dimension_breakdown_present")
        else:
            blockers.append("dimension breakdown missing")

        if report.quality_gates:
            passed.append("quality_gates_present")
        else:
            warnings.append("quality gates missing")

        if report.revision_priorities:
            passed.append("revision_priorities_present")
        else:
            warnings.append("revision priorities missing")

        if report.readiness_level in {"ready", "needs_light_revision", "needs_revision", "blocked"}:
            passed.append("readiness_level_valid")
        else:
            blockers.append("invalid readiness level")

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

    def summarize_quality_report(self, *, report: StoryQualityScoreReport) -> Dict[str, Any]:
        weakest = min(report.dimension_breakdown, key=lambda item: item.get("score", 0.0)) if report.dimension_breakdown else {}

        return {
            "success": True,
            "engine_name": self.engine_name,
            "summary": {
                "quality_report_id": report.quality_report_id,
                "source_id": report.source_id,
                "overall_score": report.overall_score,
                "readiness_level": report.readiness_level,
                "weakest_dimension": weakest.get("dimension"),
                "weakest_score": weakest.get("score"),
                "quality_gate_count": len(report.quality_gates),
                "failed_gate_count": len([gate for gate in report.quality_gates if not gate.get("passed")]),
                "revision_priority_count": len(report.revision_priorities),
                "strength_count": len(report.strengths),
                "risk_count": len(report.risks),
                "warning_count": len(report.warnings),
            },
        }

    def build_quality_report_text(self, *, report: StoryQualityScoreReport) -> Dict[str, Any]:
        lines = [
            f"# Story Quality Report: {report.source_id}",
            "",
            f"Overall score: {report.overall_score}",
            f"Readiness: {report.readiness_level}",
            "",
            "## Dimension Breakdown",
        ]

        for item in report.dimension_breakdown:
            lines.append(f"- {item.get('dimension')}: {item.get('score')} — {item.get('status')}")

        lines.append("")
        lines.append("## Revision Priorities")
        for item in report.revision_priorities:
            lines.append(f"- [{item.get('priority')}] {item.get('dimension')}: {item.get('instruction')}")

        lines.append("")
        lines.append("## Strengths")
        for item in report.strengths:
            lines.append(f"- {item}")

        lines.append("")
        lines.append("## Risks")
        for item in report.risks:
            lines.append(f"- {item}")

        return {
            "success": True,
            "engine_name": self.engine_name,
            "quality_report_text": "\n".join(lines),
        }

    def _structure_score(
        self,
        *,
        plot_outline: PlotOutline | None,
        chapter: GeneratedChapter | None,
        series_package: SeriesSeasonFormatPackage | None,
    ) -> float:
        score = 0.25
        if plot_outline:
            if plot_outline.act_structure:
                score += 0.20
            if plot_outline.scene_sequence:
                score += 0.20
            if plot_outline.major_turning_points:
                score += 0.15
            if plot_outline.payoff_setups:
                score += 0.10
        if chapter and chapter.scene_ids:
            score += 0.05
        if series_package and series_package.episode_cards:
            score += 0.05
        return self._bounded(score)

    def _character_score(
        self,
        *,
        plot_outline: PlotOutline | None,
        chapter: GeneratedChapter | None,
        adaptive_pattern_plan: AdaptiveStoryPatternPlan | None,
    ) -> float:
        character_count = 0
        if plot_outline:
            character_count += len(plot_outline.character_arc_threads)
            character_count += len(plot_outline.continuity_requirements.get("required_character_ids", []))
        if chapter:
            character_count += len(chapter.used_character_ids)

        score = 0.20 + min(0.35, character_count * 0.06)
        if adaptive_pattern_plan and adaptive_pattern_plan.character_pattern_assignments:
            score += 0.25
        if adaptive_pattern_plan and "character_transformation" in [adaptive_pattern_plan.selected_primary_pattern] + adaptive_pattern_plan.selected_secondary_patterns:
            score += 0.10
        return self._bounded(score)

    def _relationship_score(
        self,
        *,
        plot_outline: PlotOutline | None,
        chapter: GeneratedChapter | None,
        adaptive_pattern_plan: AdaptiveStoryPatternPlan | None,
    ) -> float:
        relationship_count = 0
        if plot_outline:
            relationship_count += len(plot_outline.relationship_arc_threads)
            relationship_count += len(plot_outline.continuity_requirements.get("required_relationship_ids", []))
        if chapter:
            relationship_count += len(chapter.used_relationship_ids)

        score = 0.20 + min(0.35, relationship_count * 0.10)
        if adaptive_pattern_plan and adaptive_pattern_plan.relationship_pattern_assignments:
            score += 0.30
        if adaptive_pattern_plan and "relationship_fracture" in [adaptive_pattern_plan.selected_primary_pattern] + adaptive_pattern_plan.selected_secondary_patterns:
            score += 0.10
        return self._bounded(score)

    def _secret_mystery_score(
        self,
        *,
        plot_outline: PlotOutline | None,
        chapter: GeneratedChapter | None,
        adaptive_pattern_plan: AdaptiveStoryPatternPlan | None,
        game_package: GameInteractiveScenePackage | None,
    ) -> float:
        secret_count = 0
        open_loop_count = 0
        if plot_outline:
            secret_count += len(plot_outline.secret_threads)
            open_loop_count += len(plot_outline.open_loops)
        if chapter:
            secret_count += len(chapter.used_secret_ids)
            open_loop_count += len(chapter.open_loops)
        if game_package:
            secret_count += len(game_package.secret_state_hooks)

        score = 0.20 + min(0.30, secret_count * 0.08) + min(0.20, open_loop_count * 0.05)
        if adaptive_pattern_plan and adaptive_pattern_plan.secret_pattern_assignments:
            score += 0.20
        if adaptive_pattern_plan and "mystery_pressure" in [adaptive_pattern_plan.selected_primary_pattern] + adaptive_pattern_plan.selected_secondary_patterns:
            score += 0.10
        return self._bounded(score)

    def _causal_score(
        self,
        *,
        plot_outline: PlotOutline | None,
        chapter: GeneratedChapter | None,
        adaptive_pattern_plan: AdaptiveStoryPatternPlan | None,
        pacing_report: MultiScenePacingReport | None,
    ) -> float:
        causal_count = 0
        payoff_count = 0
        if plot_outline:
            causal_count += len(plot_outline.causal_threads)
            payoff_count += len(plot_outline.payoff_setups)
        if chapter:
            causal_count += len(chapter.used_causal_ids)

        score = 0.20 + min(0.30, causal_count * 0.07) + min(0.15, payoff_count * 0.04)
        if adaptive_pattern_plan and adaptive_pattern_plan.causal_pattern_assignments:
            score += 0.20
        if pacing_report:
            score += pacing_report.causal_spacing_score * 0.15
        return self._bounded(score)

    def _world_score(
        self,
        *,
        plot_outline: PlotOutline | None,
        chapter: GeneratedChapter | None,
        scaling_plan: MultiWorldMultiCastScalingPlan | None,
        game_package: GameInteractiveScenePackage | None,
    ) -> float:
        world_count = 0
        if plot_outline:
            world_count += len(plot_outline.world_state_threads)
            world_count += len(plot_outline.continuity_requirements.get("required_world_details", []))
        if chapter:
            world_count += len(chapter.used_world_details)
        if game_package:
            world_count += len(game_package.world_state_hooks)

        score = 0.20 + min(0.35, world_count * 0.06)
        if scaling_plan and scaling_plan.world_registry:
            score += 0.25
        if scaling_plan and scaling_plan.continuity_partition_rules:
            score += 0.10
        return self._bounded(score)

    def _pacing_score(
        self,
        *,
        pacing_report: MultiScenePacingReport | None,
        plot_outline: PlotOutline | None,
        chapter: GeneratedChapter | None,
    ) -> float:
        if pacing_report:
            return self._bounded(pacing_report.overall_pacing_score)

        score = 0.35
        if plot_outline and len(plot_outline.scene_sequence) >= 2:
            score += 0.20
        if plot_outline and plot_outline.major_turning_points:
            score += 0.20
        if chapter and len(chapter.scene_ids) >= 2:
            score += 0.10
        return self._bounded(score)

    def _format_score(
        self,
        *,
        format_plan: FormatAdaptationPlan | None,
        screenplay_movie_package: ScreenplayMovieFormatPackage | None,
        series_package: SeriesSeasonFormatPackage | None,
        game_package: GameInteractiveScenePackage | None,
    ) -> float:
        score = 0.30
        if format_plan:
            score += 0.20
            if format_plan.required_sections:
                score += 0.10
            if format_plan.forbidden_patterns is not None:
                score += 0.05
        if screenplay_movie_package and screenplay_movie_package.formatted_text:
            score += 0.15
        if series_package and series_package.formatted_text:
            score += 0.15
        if game_package and game_package.formatted_text:
            score += 0.15
        return self._bounded(score)

    def _anti_generic_score(
        self,
        *,
        adaptive_pattern_plan: AdaptiveStoryPatternPlan | None,
        plot_outline: PlotOutline | None,
        story_context: Dict[str, Any],
    ) -> float:
        score = 0.25
        if adaptive_pattern_plan:
            score += 0.25
            score += min(0.20, len(adaptive_pattern_plan.anti_template_rules) * 0.025)
            score += min(0.15, len(adaptive_pattern_plan.selected_secondary_patterns) * 0.04)
        if plot_outline and (plot_outline.secret_threads or plot_outline.relationship_arc_threads or plot_outline.world_state_threads):
            score += 0.10
        if story_context.get("genres"):
            score += 0.05
        return self._bounded(score)

    def _commercial_potential_score(
        self,
        *,
        commercial_report: CommercialAppealReport | None,
        plot_outline: PlotOutline | None,
        story_context: Dict[str, Any],
    ) -> float:
        if commercial_report:
            for field in ["overall_score", "commercial_score", "appeal_score"]:
                value = getattr(commercial_report, field, None)
                if isinstance(value, (int, float)):
                    return self._bounded(float(value))

        score = 0.35
        if plot_outline:
            if plot_outline.premise:
                score += 0.15
            if plot_outline.open_loops:
                score += 0.15
            if plot_outline.payoff_setups:
                score += 0.15
            if plot_outline.relationship_arc_threads:
                score += 0.10
        if story_context.get("target_audience"):
            score += 0.05
        return self._bounded(score)

    def _overall_score(self, **scores: float) -> float:
        weights = {
            "structure_score": 0.11,
            "character_score": 0.11,
            "relationship_score": 0.09,
            "secret_mystery_score": 0.10,
            "causal_score": 0.13,
            "world_score": 0.09,
            "pacing_score": 0.12,
            "format_score": 0.08,
            "anti_generic_score": 0.10,
            "commercial_potential_score": 0.07,
        }
        total = sum(float(scores[key]) * weight for key, weight in weights.items())
        return self._bounded(total)

    def _dimension_breakdown(self, **scores: float) -> List[Dict[str, Any]]:
        breakdown = []
        for key, score in scores.items():
            dimension = key.replace("_score", "")
            breakdown.append(
                {
                    "dimension": dimension,
                    "score": self._bounded(score),
                    "status": self._score_status(score),
                    "needs_revision": score < 0.70,
                }
            )
        return breakdown

    def _quality_gates(self, *, breakdown: List[Dict[str, Any]], overall: float) -> List[Dict[str, Any]]:
        gates = [
            {
                "gate_id": "overall_quality_gate",
                "dimension": "overall",
                "threshold": 0.70,
                "score": overall,
                "passed": overall >= 0.70,
            }
        ]

        for item in breakdown:
            threshold = 0.60
            if item["dimension"] in {"causal", "character", "anti_generic"}:
                threshold = 0.65
            gates.append(
                {
                    "gate_id": f"quality_gate_{item['dimension']}",
                    "dimension": item["dimension"],
                    "threshold": threshold,
                    "score": item["score"],
                    "passed": item["score"] >= threshold,
                }
            )
        return gates

    def _revision_priorities(self, *, breakdown: List[Dict[str, Any]], quality_gates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        failed_dimensions = {gate["dimension"] for gate in quality_gates if not gate.get("passed")}
        priorities = []

        for item in sorted(breakdown, key=lambda entry: entry["score"]):
            if item["dimension"] in failed_dimensions or item["score"] < 0.70:
                priorities.append(
                    {
                        "priority_id": f"revise_{item['dimension']}",
                        "dimension": item["dimension"],
                        "score": item["score"],
                        "priority": "high" if item["score"] < 0.55 else "medium",
                        "instruction": self._revision_instruction(item["dimension"]),
                    }
                )

        return priorities

    def _readiness_level(self, *, overall: float, quality_gates: List[Dict[str, Any]]) -> str:
        failed_count = len([gate for gate in quality_gates if not gate.get("passed")])
        if overall >= 0.82 and failed_count == 0:
            return "ready"
        if overall >= 0.70 and failed_count <= 2:
            return "needs_light_revision"
        if overall >= 0.50:
            return "needs_revision"
        return "blocked"

    def _strengths(self, *, breakdown: List[Dict[str, Any]]) -> List[str]:
        return [
            f"{item['dimension']} is strong at {item['score']}."
            for item in breakdown
            if item["score"] >= 0.75
        ]

    def _risks(
        self,
        *,
        breakdown: List[Dict[str, Any]],
        adaptive_pattern_plan: AdaptiveStoryPatternPlan | None,
        pacing_report: MultiScenePacingReport | None,
        scaling_plan: MultiWorldMultiCastScalingPlan | None,
    ) -> List[str]:
        risks = [
            f"{item['dimension']} is weak at {item['score']}."
            for item in breakdown
            if item["score"] < 0.60
        ]

        if adaptive_pattern_plan and adaptive_pattern_plan.warnings:
            risks.extend(adaptive_pattern_plan.warnings)

        if pacing_report and pacing_report.warnings:
            risks.extend(pacing_report.warnings)

        if scaling_plan and scaling_plan.collision_risk_flags:
            risks.extend(scaling_plan.collision_risk_flags)

        return self._unique(risks)

    def _warnings(
        self,
        *,
        plot_outline: PlotOutline | None,
        chapter: GeneratedChapter | None,
        adaptive_pattern_plan: AdaptiveStoryPatternPlan | None,
        pacing_report: MultiScenePacingReport | None,
        format_plan: FormatAdaptationPlan | None,
    ) -> List[str]:
        warnings = []
        if not plot_outline and not chapter:
            warnings.append("No plot outline or chapter supplied; story quality scoring has limited context.")
        if not adaptive_pattern_plan:
            warnings.append("No adaptive pattern plan supplied; anti-generic scoring is limited.")
        if not pacing_report:
            warnings.append("No multi-scene pacing report supplied; pacing score uses heuristic fallback.")
        if not format_plan:
            warnings.append("No format adaptation plan supplied; format score uses package fallback.")
        return warnings

    def _revision_instruction(self, dimension: str) -> str:
        instructions = {
            "structure": "Strengthen act structure, scene sequence, turning points, and payoff setup.",
            "character": "Add clearer character goals, voice consistency, emotional pressure, and transformation.",
            "relationship": "Clarify trust shifts, resentment, repair attempts, betrayal risks, and relationship consequences.",
            "secret_mystery": "Improve clue spacing, reveal timing, partial knowledge, and open-loop management.",
            "causal": "Strengthen setup, choice, consequence, and payoff chains.",
            "world": "Make world rules concrete and consequential instead of decorative.",
            "pacing": "Improve tension curve, rhythm variation, scene length balance, and turn placement.",
            "format": "Tighten format-specific rules for novel/screenplay/series/game output.",
            "anti_generic": "Increase specificity, pattern blending, world pressure, and non-template scene dynamics.",
            "commercial_potential": "Strengthen premise clarity, hook strength, emotional stakes, and audience pull.",
        }
        return instructions.get(dimension, f"Revise {dimension} quality.")

    def _score_status(self, score: float) -> str:
        if score >= 0.82:
            return "strong"
        if score >= 0.70:
            return "solid"
        if score >= 0.55:
            return "needs_revision"
        return "weak"

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

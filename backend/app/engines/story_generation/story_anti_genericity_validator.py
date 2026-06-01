from __future__ import annotations

from typing import Any, Dict, List

from backend.app.schemas.story_generation import (
    AdaptiveStoryPatternPlan,
    FormatAdaptationPlan,
    GameInteractiveScenePackage,
    GeneratedChapter,
    PlotOutline,
    ScreenplayMovieFormatPackage,
    SeriesSeasonFormatPackage,
    StoryAntiGenericityReport,
    StoryQualityScoreReport,
)


class StoryAntiGenericityValidator:
    """Validates whether generated story material avoids generic template output.

    Locked Chunk 5.33. This validator detects bland phrasing, template beats,
    shallow worldbuilding, interchangeable characters, cosmetic choices, weak
    causality, and non-specific genre output.
    """

    engine_name = "story_generation.story_anti_genericity_validator"

    GENERIC_PHRASES = [
        "something changed forever",
        "little did they know",
        "destiny awaited",
        "a secret would change everything",
        "only time would tell",
        "the journey had just begun",
        "nothing would ever be the same",
        "darkness loomed",
        "a mysterious force",
        "ancient evil",
        "chosen one",
        "against all odds",
        "heart raced",
        "could not believe his eyes",
        "more than meets the eye",
    ]

    TEMPLATE_BEATS = [
        "chosen_one_without_cost",
        "secret_revealed_without_setup",
        "betrayal_without_relationship_history",
        "world_detail_without_consequence",
        "villain_explains_everything",
        "choice_without_state_delta",
        "cliffhanger_without_causal_thread",
    ]

    def validate_anti_genericity(
        self,
        *,
        source_id: str,
        generated_text: str | None = None,
        plot_outline: PlotOutline | None = None,
        chapter: GeneratedChapter | None = None,
        adaptive_pattern_plan: AdaptiveStoryPatternPlan | None = None,
        quality_report: StoryQualityScoreReport | None = None,
        format_plan: FormatAdaptationPlan | None = None,
        screenplay_movie_package: ScreenplayMovieFormatPackage | None = None,
        series_package: SeriesSeasonFormatPackage | None = None,
        game_package: GameInteractiveScenePackage | None = None,
        story_context: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        story_context = story_context or {}
        text = self._combined_text(
            generated_text=generated_text,
            chapter=chapter,
            screenplay_movie_package=screenplay_movie_package,
            series_package=series_package,
            game_package=game_package,
        )

        detected_generic_patterns = self._detected_generic_patterns(text=text, plot_outline=plot_outline, game_package=game_package)
        anti_template_rule_results = self._anti_template_rule_results(
            adaptive_pattern_plan=adaptive_pattern_plan,
            text=text,
            plot_outline=plot_outline,
            game_package=game_package,
        )
        specificity_evidence = self._specificity_evidence(
            text=text,
            plot_outline=plot_outline,
            chapter=chapter,
            game_package=game_package,
            series_package=series_package,
            screenplay_movie_package=screenplay_movie_package,
        )

        specificity_score = self._specificity_score(specificity_evidence=specificity_evidence, text=text)
        template_resistance_score = self._template_resistance_score(
            detected_generic_patterns=detected_generic_patterns,
            anti_template_rule_results=anti_template_rule_results,
        )
        character_distinction_score = self._character_distinction_score(
            plot_outline=plot_outline,
            chapter=chapter,
            adaptive_pattern_plan=adaptive_pattern_plan,
        )
        relationship_specificity_score = self._relationship_specificity_score(
            plot_outline=plot_outline,
            chapter=chapter,
            adaptive_pattern_plan=adaptive_pattern_plan,
        )
        world_consequence_score = self._world_consequence_score(
            plot_outline=plot_outline,
            chapter=chapter,
            game_package=game_package,
        )
        secret_pressure_score = self._secret_pressure_score(
            plot_outline=plot_outline,
            chapter=chapter,
            adaptive_pattern_plan=adaptive_pattern_plan,
        )
        causal_uniqueness_score = self._causal_uniqueness_score(
            plot_outline=plot_outline,
            chapter=chapter,
            adaptive_pattern_plan=adaptive_pattern_plan,
        )
        format_distinctiveness_score = self._format_distinctiveness_score(
            format_plan=format_plan,
            screenplay_movie_package=screenplay_movie_package,
            series_package=series_package,
            game_package=game_package,
        )

        overall = self._overall_score(
            specificity_score=specificity_score,
            template_resistance_score=template_resistance_score,
            character_distinction_score=character_distinction_score,
            relationship_specificity_score=relationship_specificity_score,
            world_consequence_score=world_consequence_score,
            secret_pressure_score=secret_pressure_score,
            causal_uniqueness_score=causal_uniqueness_score,
            format_distinctiveness_score=format_distinctiveness_score,
            quality_report=quality_report,
        )

        report_id = f"story_anti_genericity_{source_id}"

        report = StoryAntiGenericityReport(
            report_id=report_id,
            draft_id=source_id,
            anti_genericity_report_id=report_id,
            source_id=source_id,
            overall_anti_genericity_score=overall,
            genericity_risk_level=self._risk_level(overall=overall, detected_generic_patterns=detected_generic_patterns),
            specificity_score=specificity_score,
            template_resistance_score=template_resistance_score,
            character_distinction_score=character_distinction_score,
            relationship_specificity_score=relationship_specificity_score,
            world_consequence_score=world_consequence_score,
            secret_pressure_score=secret_pressure_score,
            causal_uniqueness_score=causal_uniqueness_score,
            format_distinctiveness_score=format_distinctiveness_score,
            detected_generic_patterns=detected_generic_patterns,
            anti_template_rule_results=anti_template_rule_results,
            specificity_evidence=specificity_evidence,
            rewrite_targets=self._rewrite_targets(
                detected_generic_patterns=detected_generic_patterns,
                anti_template_rule_results=anti_template_rule_results,
                scores={
                    "specificity": specificity_score,
                    "template_resistance": template_resistance_score,
                    "character_distinction": character_distinction_score,
                    "relationship_specificity": relationship_specificity_score,
                    "world_consequence": world_consequence_score,
                    "secret_pressure": secret_pressure_score,
                    "causal_uniqueness": causal_uniqueness_score,
                    "format_distinctiveness": format_distinctiveness_score,
                },
            ),
            approved_strengths=self._approved_strengths(
                specificity_evidence=specificity_evidence,
                scores={
                    "specificity": specificity_score,
                    "template_resistance": template_resistance_score,
                    "character_distinction": character_distinction_score,
                    "relationship_specificity": relationship_specificity_score,
                    "world_consequence": world_consequence_score,
                    "secret_pressure": secret_pressure_score,
                    "causal_uniqueness": causal_uniqueness_score,
                    "format_distinctiveness": format_distinctiveness_score,
                },
            ),
            warnings=self._warnings(
                text=text,
                plot_outline=plot_outline,
                adaptive_pattern_plan=adaptive_pattern_plan,
                detected_generic_patterns=detected_generic_patterns,
            ),
        )

        return {
            "success": True,
            "engine_name": self.engine_name,
            "story_anti_genericity_report": report,
            "story_anti_genericity_report_dict": report.model_dump(mode="json"),
            "handoff_to_next_engine": {
                "next_engine": "story_generation.story_continuity_validator",
                "payload_keys": [
                    "story_anti_genericity_report",
                    "story_quality_score_report",
                    "adaptive_story_pattern_plan",
                    "plot_outline",
                    "generated_chapter",
                    "format_packages",
                    "story_context",
                ],
            },
        }

    def validate_report(self, *, report: StoryAntiGenericityReport) -> Dict[str, Any]:
        blockers: List[str] = []
        warnings: List[str] = []
        passed: List[str] = []

        if not report.anti_genericity_report_id:
            blockers.append("anti_genericity_report_id missing")
        else:
            passed.append("anti_genericity_report_id_present")

        if report.source_id:
            passed.append("source_id_present")
        else:
            blockers.append("source_id missing")

        scores = [
            report.overall_anti_genericity_score,
            report.specificity_score,
            report.template_resistance_score,
            report.character_distinction_score,
            report.relationship_specificity_score,
            report.world_consequence_score,
            report.secret_pressure_score,
            report.causal_uniqueness_score,
            report.format_distinctiveness_score,
        ]

        if all(0.0 <= score <= 1.0 for score in scores):
            passed.append("scores_bounded")
        else:
            blockers.append("one or more anti-genericity scores out of bounds")

        if report.genericity_risk_level in {"low", "medium", "high", "critical"}:
            passed.append("risk_level_valid")
        else:
            blockers.append("invalid genericity risk level")

        if report.rewrite_targets:
            passed.append("rewrite_targets_present")
        else:
            warnings.append("no rewrite targets generated")

        if report.specificity_evidence:
            passed.append("specificity_evidence_present")
        else:
            warnings.append("no specificity evidence found")

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

    def summarize_report(self, *, report: StoryAntiGenericityReport) -> Dict[str, Any]:
        weakest_dimension = self._weakest_dimension(report=report)

        return {
            "success": True,
            "engine_name": self.engine_name,
            "summary": {
                "anti_genericity_report_id": report.anti_genericity_report_id,
                "source_id": report.source_id,
                "overall_anti_genericity_score": report.overall_anti_genericity_score,
                "genericity_risk_level": report.genericity_risk_level,
                "weakest_dimension": weakest_dimension["dimension"],
                "weakest_score": weakest_dimension["score"],
                "detected_generic_pattern_count": len(report.detected_generic_patterns),
                "failed_anti_template_rule_count": len([item for item in report.anti_template_rule_results if not item.get("passed")]),
                "rewrite_target_count": len(report.rewrite_targets),
                "approved_strength_count": len(report.approved_strengths),
                "warning_count": len(report.warnings),
            },
        }

    def build_anti_genericity_report_text(self, *, report: StoryAntiGenericityReport) -> Dict[str, Any]:
        lines = [
            f"# Story Anti-Genericity Report: {report.source_id}",
            "",
            f"Overall anti-genericity score: {report.overall_anti_genericity_score}",
            f"Risk level: {report.genericity_risk_level}",
            "",
            "## Detected Generic Patterns",
        ]

        for item in report.detected_generic_patterns:
            lines.append(f"- {item.get('pattern_type')}: {item.get('description')}")

        lines.append("")
        lines.append("## Rewrite Targets")
        for item in report.rewrite_targets:
            lines.append(f"- [{item.get('priority')}] {item.get('target_type')}: {item.get('instruction')}")

        lines.append("")
        lines.append("## Approved Strengths")
        for item in report.approved_strengths:
            lines.append(f"- {item}")

        return {
            "success": True,
            "engine_name": self.engine_name,
            "anti_genericity_report_text": "\n".join(lines),
        }

    def _combined_text(
        self,
        *,
        generated_text: str | None,
        chapter: GeneratedChapter | None,
        screenplay_movie_package: ScreenplayMovieFormatPackage | None,
        series_package: SeriesSeasonFormatPackage | None,
        game_package: GameInteractiveScenePackage | None,
    ) -> str:
        parts: List[str] = []
        if generated_text:
            parts.append(generated_text)
        if chapter:
            parts.append(chapter.chapter_text)
        if screenplay_movie_package:
            parts.append(screenplay_movie_package.formatted_text)
        if series_package:
            parts.append(series_package.formatted_text)
        if game_package:
            parts.append(game_package.formatted_text)
        return "\n".join(part for part in parts if part).strip()

    def _detected_generic_patterns(
        self,
        *,
        text: str,
        plot_outline: PlotOutline | None,
        game_package: GameInteractiveScenePackage | None,
    ) -> List[Dict[str, Any]]:
        detected: List[Dict[str, Any]] = []
        lowered = text.lower()

        for phrase in self.GENERIC_PHRASES:
            if phrase in lowered:
                detected.append(
                    {
                        "pattern_type": "generic_phrase",
                        "pattern_id": self._safe_id(phrase),
                        "description": f"Generic phrase detected: {phrase}",
                        "severity": "medium",
                    }
                )

        if plot_outline:
            if plot_outline.secret_threads and not plot_outline.payoff_setups:
                detected.append(
                    {
                        "pattern_type": "unpaid_secret_pressure",
                        "pattern_id": "secret_without_payoff_setup",
                        "description": "Secrets exist but no payoff setup is attached.",
                        "severity": "high",
                    }
                )

            if plot_outline.world_state_threads and not plot_outline.causal_threads:
                detected.append(
                    {
                        "pattern_type": "decorative_worldbuilding",
                        "pattern_id": "world_without_causality",
                        "description": "World details exist without causal pressure.",
                        "severity": "medium",
                    }
                )

        if game_package and game_package.choice_menu and not game_package.state_deltas:
            detected.append(
                {
                    "pattern_type": "cosmetic_choice",
                    "pattern_id": "choices_without_state_delta",
                    "description": "Interactive choices exist without state deltas.",
                    "severity": "high",
                }
            )

        return detected

    def _anti_template_rule_results(
        self,
        *,
        adaptive_pattern_plan: AdaptiveStoryPatternPlan | None,
        text: str,
        plot_outline: PlotOutline | None,
        game_package: GameInteractiveScenePackage | None,
    ) -> List[Dict[str, Any]]:
        rules = adaptive_pattern_plan.anti_template_rules if adaptive_pattern_plan else []
        results: List[Dict[str, Any]] = []

        for index, rule in enumerate(rules, start=1):
            lowered = rule.lower()
            passed = True
            reason = "Rule has no detected violation."

            if "secrets" in lowered and plot_outline and plot_outline.secret_threads and not plot_outline.payoff_setups:
                passed = False
                reason = "Secrets exist without payoff setup."

            if "choices" in lowered and game_package and game_package.choice_menu and not game_package.state_deltas:
                passed = False
                reason = "Choices exist without state deltas."

            if "single universal" in lowered and text.lower().count("act") > 8 and not (plot_outline and plot_outline.secret_threads):
                passed = False
                reason = "Text appears structure-heavy without specific pressure threads."

            if "world details" in lowered and plot_outline and plot_outline.world_state_threads and not plot_outline.causal_threads:
                passed = False
                reason = "World details appear without causal consequence."

            results.append(
                {
                    "rule_result_id": f"anti_template_rule_{index}",
                    "rule": rule,
                    "passed": passed,
                    "reason": reason,
                }
            )

        if not results:
            results.append(
                {
                    "rule_result_id": "anti_template_rule_missing",
                    "rule": "No adaptive anti-template rules supplied.",
                    "passed": False,
                    "reason": "Missing adaptive pattern plan or anti-template rule list.",
                }
            )

        return results

    def _specificity_evidence(
        self,
        *,
        text: str,
        plot_outline: PlotOutline | None,
        chapter: GeneratedChapter | None,
        game_package: GameInteractiveScenePackage | None,
        series_package: SeriesSeasonFormatPackage | None,
        screenplay_movie_package: ScreenplayMovieFormatPackage | None,
    ) -> List[Dict[str, Any]]:
        evidence: List[Dict[str, Any]] = []

        if plot_outline:
            for detail in plot_outline.continuity_requirements.get("required_world_details", []):
                evidence.append(
                    {
                        "evidence_type": "world_detail",
                        "value": detail,
                        "description": f"Specific world detail exists: {detail}",
                    }
                )

            for secret in plot_outline.secret_threads:
                evidence.append(
                    {
                        "evidence_type": "secret_thread",
                        "value": secret.get("secret_id"),
                        "description": f"Specific secret thread exists: {secret.get('secret_id')}",
                    }
                )

            for causal in plot_outline.causal_threads:
                evidence.append(
                    {
                        "evidence_type": "causal_thread",
                        "value": causal.get("causal_id"),
                        "description": f"Specific causal thread exists: {causal.get('causal_id')}",
                    }
                )

        if chapter:
            for character_id in chapter.used_character_ids:
                evidence.append(
                    {
                        "evidence_type": "character_id",
                        "value": character_id,
                        "description": f"Specific character appears: {character_id}",
                    }
                )

        if game_package and game_package.state_deltas:
            evidence.append(
                {
                    "evidence_type": "interactive_state_delta",
                    "value": len(game_package.state_deltas),
                    "description": "Interactive choices produce concrete state deltas.",
                }
            )

        if series_package and series_package.cliffhanger_registry:
            evidence.append(
                {
                    "evidence_type": "series_cliffhanger_registry",
                    "value": len(series_package.cliffhanger_registry),
                    "description": "Series format has tracked cliffhangers.",
                }
            )

        if screenplay_movie_package and screenplay_movie_package.visual_motifs:
            evidence.append(
                {
                    "evidence_type": "visual_motif",
                    "value": len(screenplay_movie_package.visual_motifs),
                    "description": "Screen/movie format has visual motifs.",
                }
            )

        if text:
            specific_tokens = [token for token in text.split() if "_" in token or token.istitle()]
            if specific_tokens:
                evidence.append(
                    {
                        "evidence_type": "specific_text_markers",
                        "value": len(specific_tokens),
                        "description": "Text contains named/specific markers rather than only abstract phrasing.",
                    }
                )

        return evidence

    def _specificity_score(self, *, specificity_evidence: List[Dict[str, Any]], text: str) -> float:
        score = 0.20 + min(0.60, len(specificity_evidence) * 0.055)
        if text and len(text.split()) >= 120:
            score += 0.10
        if text and any("_" in token for token in text.split()):
            score += 0.05
        return self._bounded(score)

    def _template_resistance_score(
        self,
        *,
        detected_generic_patterns: List[Dict[str, Any]],
        anti_template_rule_results: List[Dict[str, Any]],
    ) -> float:
        score = 0.85
        score -= len(detected_generic_patterns) * 0.08
        failed_rules = len([item for item in anti_template_rule_results if not item.get("passed")])
        score -= failed_rules * 0.07
        return self._bounded(score)

    def _character_distinction_score(
        self,
        *,
        plot_outline: PlotOutline | None,
        chapter: GeneratedChapter | None,
        adaptive_pattern_plan: AdaptiveStoryPatternPlan | None,
    ) -> float:
        character_count = 0
        if plot_outline:
            character_count += len(plot_outline.character_arc_threads)
        if chapter:
            character_count += len(chapter.used_character_ids)

        score = 0.25 + min(0.35, character_count * 0.07)
        if adaptive_pattern_plan and adaptive_pattern_plan.character_pattern_assignments:
            score += 0.30
        return self._bounded(score)

    def _relationship_specificity_score(
        self,
        *,
        plot_outline: PlotOutline | None,
        chapter: GeneratedChapter | None,
        adaptive_pattern_plan: AdaptiveStoryPatternPlan | None,
    ) -> float:
        relationship_count = 0
        if plot_outline:
            relationship_count += len(plot_outline.relationship_arc_threads)
        if chapter:
            relationship_count += len(chapter.used_relationship_ids)

        score = 0.20 + min(0.35, relationship_count * 0.12)
        if adaptive_pattern_plan and adaptive_pattern_plan.relationship_pattern_assignments:
            score += 0.30
        return self._bounded(score)

    def _world_consequence_score(
        self,
        *,
        plot_outline: PlotOutline | None,
        chapter: GeneratedChapter | None,
        game_package: GameInteractiveScenePackage | None,
    ) -> float:
        world_count = 0
        causal_count = 0
        if plot_outline:
            world_count += len(plot_outline.world_state_threads)
            world_count += len(plot_outline.continuity_requirements.get("required_world_details", []))
            causal_count += len(plot_outline.causal_threads)
        if chapter:
            world_count += len(chapter.used_world_details)
            causal_count += len(chapter.used_causal_ids)
        if game_package:
            world_count += len(game_package.world_state_hooks)
            causal_count += len(game_package.causal_state_hooks)

        score = 0.20 + min(0.30, world_count * 0.05) + min(0.35, causal_count * 0.08)
        return self._bounded(score)

    def _secret_pressure_score(
        self,
        *,
        plot_outline: PlotOutline | None,
        chapter: GeneratedChapter | None,
        adaptive_pattern_plan: AdaptiveStoryPatternPlan | None,
    ) -> float:
        secret_count = 0
        payoff_count = 0
        open_loop_count = 0
        if plot_outline:
            secret_count += len(plot_outline.secret_threads)
            payoff_count += len(plot_outline.payoff_setups)
            open_loop_count += len(plot_outline.open_loops)
        if chapter:
            secret_count += len(chapter.used_secret_ids)
            open_loop_count += len(chapter.open_loops)

        score = 0.20 + min(0.25, secret_count * 0.08) + min(0.25, payoff_count * 0.08) + min(0.15, open_loop_count * 0.05)
        if adaptive_pattern_plan and adaptive_pattern_plan.secret_pattern_assignments:
            score += 0.15
        return self._bounded(score)

    def _causal_uniqueness_score(
        self,
        *,
        plot_outline: PlotOutline | None,
        chapter: GeneratedChapter | None,
        adaptive_pattern_plan: AdaptiveStoryPatternPlan | None,
    ) -> float:
        causal_count = 0
        if plot_outline:
            causal_count += len(plot_outline.causal_threads)
        if chapter:
            causal_count += len(chapter.used_causal_ids)

        score = 0.20 + min(0.40, causal_count * 0.10)
        if adaptive_pattern_plan and adaptive_pattern_plan.causal_pattern_assignments:
            score += 0.25
        if adaptive_pattern_plan and "causal_escalation" in [adaptive_pattern_plan.selected_primary_pattern] + adaptive_pattern_plan.selected_secondary_patterns:
            score += 0.10
        return self._bounded(score)

    def _format_distinctiveness_score(
        self,
        *,
        format_plan: FormatAdaptationPlan | None,
        screenplay_movie_package: ScreenplayMovieFormatPackage | None,
        series_package: SeriesSeasonFormatPackage | None,
        game_package: GameInteractiveScenePackage | None,
    ) -> float:
        score = 0.25
        if format_plan:
            score += 0.15
            if format_plan.required_sections:
                score += 0.10
            if format_plan.forbidden_patterns:
                score += 0.10
        if screenplay_movie_package and screenplay_movie_package.scene_headings:
            score += 0.12
        if series_package and series_package.episode_cards:
            score += 0.12
        if game_package and game_package.choice_menu and game_package.state_deltas:
            score += 0.16
        return self._bounded(score)

    def _overall_score(self, **kwargs: Any) -> float:
        quality_report = kwargs.pop("quality_report", None)
        weights = {
            "specificity_score": 0.16,
            "template_resistance_score": 0.16,
            "character_distinction_score": 0.13,
            "relationship_specificity_score": 0.11,
            "world_consequence_score": 0.12,
            "secret_pressure_score": 0.13,
            "causal_uniqueness_score": 0.12,
            "format_distinctiveness_score": 0.07,
        }
        score = sum(float(kwargs[key]) * weight for key, weight in weights.items())
        if quality_report:
            score = (score * 0.85) + (quality_report.anti_generic_score * 0.15)
        return self._bounded(score)

    def _risk_level(self, *, overall: float, detected_generic_patterns: List[Dict[str, Any]]) -> str:
        high_count = len([item for item in detected_generic_patterns if item.get("severity") == "high"])
        if overall < 0.40 or high_count >= 3:
            return "critical"
        if overall < 0.58 or high_count >= 1:
            return "high"
        if overall < 0.72:
            return "medium"
        return "low"

    def _rewrite_targets(
        self,
        *,
        detected_generic_patterns: List[Dict[str, Any]],
        anti_template_rule_results: List[Dict[str, Any]],
        scores: Dict[str, float],
    ) -> List[Dict[str, Any]]:
        targets: List[Dict[str, Any]] = []

        for pattern in detected_generic_patterns:
            targets.append(
                {
                    "rewrite_target_id": f"rewrite_{pattern.get('pattern_id')}",
                    "target_type": pattern.get("pattern_type"),
                    "priority": "high" if pattern.get("severity") == "high" else "medium",
                    "instruction": f"Replace generic pattern with specific character, world, causal, or secret pressure: {pattern.get('description')}",
                }
            )

        for result in anti_template_rule_results:
            if not result.get("passed"):
                targets.append(
                    {
                        "rewrite_target_id": f"rewrite_{result.get('rule_result_id')}",
                        "target_type": "anti_template_rule_failure",
                        "priority": "high",
                        "instruction": f"Fix anti-template rule failure: {result.get('reason')}",
                    }
                )

        for dimension, score in scores.items():
            if score < 0.62:
                targets.append(
                    {
                        "rewrite_target_id": f"rewrite_weak_{dimension}",
                        "target_type": dimension,
                        "priority": "high" if score < 0.50 else "medium",
                        "instruction": self._rewrite_instruction(dimension),
                    }
                )

        return self._unique_dicts(targets, key="rewrite_target_id")

    def _approved_strengths(self, *, specificity_evidence: List[Dict[str, Any]], scores: Dict[str, float]) -> List[str]:
        strengths = []

        for dimension, score in scores.items():
            if score >= 0.75:
                strengths.append(f"{dimension} is specific enough to preserve.")

        evidence_types = {item.get("evidence_type") for item in specificity_evidence}
        if "world_detail" in evidence_types:
            strengths.append("Specific world details are present.")
        if "secret_thread" in evidence_types:
            strengths.append("Specific secret threads are present.")
        if "causal_thread" in evidence_types:
            strengths.append("Specific causal threads are present.")

        return self._unique(strengths)

    def _warnings(
        self,
        *,
        text: str,
        plot_outline: PlotOutline | None,
        adaptive_pattern_plan: AdaptiveStoryPatternPlan | None,
        detected_generic_patterns: List[Dict[str, Any]],
    ) -> List[str]:
        warnings = []
        if not text:
            warnings.append("No generated text supplied; anti-genericity validation relies only on structured context.")
        if not plot_outline:
            warnings.append("No plot outline supplied; specificity validation is limited.")
        if not adaptive_pattern_plan:
            warnings.append("No adaptive pattern plan supplied; anti-template validation is limited.")
        if len(detected_generic_patterns) >= 5:
            warnings.append("Many generic patterns detected; rewrite before downstream generation.")
        return warnings

    def _weakest_dimension(self, *, report: StoryAntiGenericityReport) -> Dict[str, Any]:
        dimensions = [
            {"dimension": "specificity", "score": report.specificity_score},
            {"dimension": "template_resistance", "score": report.template_resistance_score},
            {"dimension": "character_distinction", "score": report.character_distinction_score},
            {"dimension": "relationship_specificity", "score": report.relationship_specificity_score},
            {"dimension": "world_consequence", "score": report.world_consequence_score},
            {"dimension": "secret_pressure", "score": report.secret_pressure_score},
            {"dimension": "causal_uniqueness", "score": report.causal_uniqueness_score},
            {"dimension": "format_distinctiveness", "score": report.format_distinctiveness_score},
        ]
        return min(dimensions, key=lambda item: item["score"])

    def _rewrite_instruction(self, dimension: str) -> str:
        instructions = {
            "specificity": "Add named world details, concrete actions, unique objects, and exact stakes.",
            "template_resistance": "Remove template phrases and replace them with story-specific reversals.",
            "character_distinction": "Give each character distinct goals, voice, knowledge, and pressure response.",
            "relationship_specificity": "Make relationship changes measurable through trust, resentment, repair, or betrayal risk.",
            "world_consequence": "Make world rules cause constraints, costs, or irreversible consequences.",
            "secret_pressure": "Add clue spacing, partial knowledge, reveal timing, and payoff setup.",
            "causal_uniqueness": "Clarify why this event causes this specific consequence.",
            "format_distinctiveness": "Use the format's unique strengths instead of generic prose structure.",
        }
        return instructions.get(dimension, f"Increase specificity for {dimension}.")

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

from __future__ import annotations

from typing import Any, Dict, List

from backend.app.schemas.story_generation import (
    AdaptiveStoryPatternPlan,
    GameInteractiveScenePackage,
    GeneratedChapter,
    OriginalityCopyRiskReport,
    PlotOutline,
    ScreenplayMovieFormatPackage,
    SeriesSeasonFormatPackage,
    StoryAntiGenericityReport,
    StoryContinuityValidationReport,
    StoryQualityScoreReport,
)


class OriginalityCopyRiskGuard:
    """Guards generated story material against copy-risk and unsafe imitation.

    Locked Chunk 5.35. This does not claim legal certainty. It is an engineering
    risk screen that detects obvious phrase overlap, protected-style prompts,
    derivative character/world/plot patterns, and export blockers.
    """

    engine_name = "story_generation.originality_copy_risk_guard"

    HIGH_RISK_STYLE_MARKERS = [
        "in the style of",
        "write like",
        "exactly like",
        "copy the style of",
        "same as",
        "make it like",
        "sound like",
        "voice of",
    ]

    GENERIC_PROTECTED_FRANCHISE_MARKERS = [
        "hogwarts",
        "jedi",
        "sith",
        "lightsaber",
        "middle-earth",
        "westeros",
        "pokemon",
        "marvel",
        "dc comics",
    ]

    HIGH_OVERLAP_PHRASES = [
        "the journey had just begun",
        "little did they know",
        "nothing would ever be the same",
        "chosen one",
        "ancient evil",
        "only time would tell",
    ]

    def evaluate_copy_risk(
        self,
        *,
        source_id: str,
        generated_text: str | None = None,
        reference_texts: List[Dict[str, Any]] | None = None,
        plot_outline: PlotOutline | None = None,
        chapter: GeneratedChapter | None = None,
        adaptive_pattern_plan: AdaptiveStoryPatternPlan | None = None,
        quality_report: StoryQualityScoreReport | None = None,
        anti_genericity_report: StoryAntiGenericityReport | None = None,
        continuity_report: StoryContinuityValidationReport | None = None,
        screenplay_movie_package: ScreenplayMovieFormatPackage | None = None,
        series_package: SeriesSeasonFormatPackage | None = None,
        game_package: GameInteractiveScenePackage | None = None,
        story_context: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        reference_texts = reference_texts or []
        story_context = story_context or {}

        text = self._combined_text(
            generated_text=generated_text,
            chapter=chapter,
            screenplay_movie_package=screenplay_movie_package,
            series_package=series_package,
            game_package=game_package,
        )

        phrase_risks = self._phrase_overlap_risks(text=text, reference_texts=reference_texts)
        protected_style_warnings = self._protected_style_warnings(text=text, story_context=story_context)
        source_policy_results = self._source_policy_results(reference_texts=reference_texts, story_context=story_context)
        similarity_risks = self._similarity_risks(
            text=text,
            plot_outline=plot_outline,
            chapter=chapter,
            story_context=story_context,
        )
        originality_evidence = self._originality_evidence(
            plot_outline=plot_outline,
            chapter=chapter,
            adaptive_pattern_plan=adaptive_pattern_plan,
            anti_genericity_report=anti_genericity_report,
            continuity_report=continuity_report,
            game_package=game_package,
            series_package=series_package,
            screenplay_movie_package=screenplay_movie_package,
        )

        detected_risks = phrase_risks + similarity_risks
        phrase_overlap_score = self._phrase_overlap_score(phrase_risks=phrase_risks, reference_texts=reference_texts)
        style_imitation_risk_score = self._style_imitation_risk_score(protected_style_warnings=protected_style_warnings)
        character_similarity_risk_score = self._risk_dimension_score(similarity_risks, "character_similarity")
        world_similarity_risk_score = self._risk_dimension_score(similarity_risks, "world_similarity")
        plot_similarity_risk_score = self._risk_dimension_score(similarity_risks, "plot_similarity")
        originality_strength_score = self._originality_strength_score(
            originality_evidence=originality_evidence,
            anti_genericity_report=anti_genericity_report,
            quality_report=quality_report,
        )

        overall_originality_score = self._overall_originality_score(
            phrase_overlap_score=phrase_overlap_score,
            style_imitation_risk_score=style_imitation_risk_score,
            character_similarity_risk_score=character_similarity_risk_score,
            world_similarity_risk_score=world_similarity_risk_score,
            plot_similarity_risk_score=plot_similarity_risk_score,
            originality_strength_score=originality_strength_score,
            source_policy_results=source_policy_results,
        )

        copy_risk_level = self._copy_risk_level(
            overall_originality_score=overall_originality_score,
            detected_risks=detected_risks,
            protected_style_warnings=protected_style_warnings,
            source_policy_results=source_policy_results,
        )

        rewrite_requirements = self._rewrite_requirements(
            detected_risks=detected_risks,
            protected_style_warnings=protected_style_warnings,
            source_policy_results=source_policy_results,
            copy_risk_level=copy_risk_level,
        )

        report = OriginalityCopyRiskReport(
            originality_report_id=f"originality_copy_risk_{source_id}",
            source_id=source_id,
            safe_for_export=copy_risk_level in {"low", "medium"} and not any(item.get("severity") == "blocker" for item in rewrite_requirements),
            overall_originality_score=overall_originality_score,
            copy_risk_level=copy_risk_level,
            phrase_overlap_score=phrase_overlap_score,
            style_imitation_risk_score=style_imitation_risk_score,
            character_similarity_risk_score=character_similarity_risk_score,
            world_similarity_risk_score=world_similarity_risk_score,
            plot_similarity_risk_score=plot_similarity_risk_score,
            originality_strength_score=originality_strength_score,
            detected_risks=detected_risks,
            protected_style_warnings=protected_style_warnings,
            source_policy_results=source_policy_results,
            originality_evidence=originality_evidence,
            rewrite_requirements=rewrite_requirements,
            approved_original_elements=self._approved_original_elements(originality_evidence=originality_evidence),
            downstream_constraints=self._downstream_constraints(
                copy_risk_level=copy_risk_level,
                rewrite_requirements=rewrite_requirements,
                originality_evidence=originality_evidence,
            ),
            warnings=self._warnings(
                text=text,
                reference_texts=reference_texts,
                protected_style_warnings=protected_style_warnings,
                source_policy_results=source_policy_results,
            ),
        )

        return {
            "success": True,
            "engine_name": self.engine_name,
            "originality_copy_risk_report": report,
            "originality_copy_risk_report_dict": report.model_dump(mode="json"),
            "handoff_to_next_engine": {
                "next_engine": "story_generation.story_revision_engine",
                "payload_keys": [
                    "originality_copy_risk_report",
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

    def validate_report(self, *, report: OriginalityCopyRiskReport) -> Dict[str, Any]:
        blockers: List[str] = []
        warnings: List[str] = []
        passed: List[str] = []

        if report.originality_report_id:
            passed.append("originality_report_id_present")
        else:
            blockers.append("originality_report_id missing")

        if report.source_id:
            passed.append("source_id_present")
        else:
            blockers.append("source_id missing")

        scores = [
            report.overall_originality_score,
            report.phrase_overlap_score,
            report.style_imitation_risk_score,
            report.character_similarity_risk_score,
            report.world_similarity_risk_score,
            report.plot_similarity_risk_score,
            report.originality_strength_score,
        ]

        if all(0.0 <= score <= 1.0 for score in scores):
            passed.append("scores_bounded")
        else:
            blockers.append("one or more originality/copy-risk scores out of bounds")

        if report.copy_risk_level in {"low", "medium", "high", "critical"}:
            passed.append("copy_risk_level_valid")
        else:
            blockers.append("invalid copy risk level")

        if report.downstream_constraints:
            passed.append("downstream_constraints_present")
        else:
            warnings.append("downstream constraints missing")

        if report.rewrite_requirements:
            warnings.append("rewrite requirements present")

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

    def summarize_report(self, *, report: OriginalityCopyRiskReport) -> Dict[str, Any]:
        return {
            "success": True,
            "engine_name": self.engine_name,
            "summary": {
                "originality_report_id": report.originality_report_id,
                "source_id": report.source_id,
                "safe_for_export": report.safe_for_export,
                "overall_originality_score": report.overall_originality_score,
                "copy_risk_level": report.copy_risk_level,
                "detected_risk_count": len(report.detected_risks),
                "protected_style_warning_count": len(report.protected_style_warnings),
                "source_policy_result_count": len(report.source_policy_results),
                "rewrite_requirement_count": len(report.rewrite_requirements),
                "approved_original_element_count": len(report.approved_original_elements),
                "warning_count": len(report.warnings),
            },
        }

    def build_copy_risk_report_text(self, *, report: OriginalityCopyRiskReport) -> Dict[str, Any]:
        lines = [
            f"# Originality / Copy-Risk Report: {report.source_id}",
            "",
            f"Safe for export: {report.safe_for_export}",
            f"Overall originality score: {report.overall_originality_score}",
            f"Copy-risk level: {report.copy_risk_level}",
            "",
            "## Detected Risks",
        ]

        for item in report.detected_risks:
            lines.append(f"- [{item.get('severity')}] {item.get('risk_type')}: {item.get('description')}")

        lines.append("")
        lines.append("## Protected Style Warnings")
        for item in report.protected_style_warnings:
            lines.append(f"- [{item.get('severity')}] {item.get('description')}")

        lines.append("")
        lines.append("## Rewrite Requirements")
        for item in report.rewrite_requirements:
            lines.append(f"- [{item.get('severity')}] {item.get('requirement_type')}: {item.get('instruction')}")

        lines.append("")
        lines.append("## Approved Original Elements")
        for item in report.approved_original_elements:
            lines.append(f"- {item}")

        return {
            "success": True,
            "engine_name": self.engine_name,
            "copy_risk_report_text": "\n".join(lines),
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
        if chapter and chapter.chapter_text:
            parts.append(chapter.chapter_text)
        if screenplay_movie_package and screenplay_movie_package.formatted_text:
            parts.append(screenplay_movie_package.formatted_text)
        if series_package and series_package.formatted_text:
            parts.append(series_package.formatted_text)
        if game_package and game_package.formatted_text:
            parts.append(game_package.formatted_text)
        return "\n".join(parts).strip()

    def _phrase_overlap_risks(self, *, text: str, reference_texts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        risks: List[Dict[str, Any]] = []
        lowered = text.lower()

        for phrase in self.HIGH_OVERLAP_PHRASES:
            if phrase in lowered:
                risks.append(
                    {
                        "risk_id": f"phrase_risk_{self._safe_id(phrase)}",
                        "risk_type": "generic_or_high_overlap_phrase",
                        "severity": "medium",
                        "description": f"High-overlap/generic phrase detected: {phrase}",
                    }
                )

        text_ngrams = self._ngrams(lowered, n=7)
        for ref in reference_texts:
            ref_text = str(ref.get("text", "")).lower()
            if not ref_text:
                continue
            ref_ngrams = self._ngrams(ref_text, n=7)
            overlap = sorted(text_ngrams.intersection(ref_ngrams))
            if overlap:
                severity = "high" if len(overlap) >= 3 else "medium"
                risks.append(
                    {
                        "risk_id": f"phrase_overlap_{self._safe_id(ref.get('source_id', 'reference'))}",
                        "risk_type": "reference_phrase_overlap",
                        "severity": severity,
                        "description": f"Detected {len(overlap)} overlapping 7-word phrase(s) with reference source.",
                        "source_id": ref.get("source_id"),
                        "source_policy": ref.get("policy", "unknown"),
                        "sample_overlap": overlap[:3],
                    }
                )

        return risks

    def _protected_style_warnings(self, *, text: str, story_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        warnings: List[Dict[str, Any]] = []
        lowered_text = text.lower()
        prompts = " ".join(str(item) for item in story_context.get("style_instructions", [])).lower()
        combined = f"{lowered_text}\n{prompts}"

        for marker in self.HIGH_RISK_STYLE_MARKERS:
            if marker in combined:
                warnings.append(
                    {
                        "warning_id": f"protected_style_marker_{self._safe_id(marker)}",
                        "warning_type": "protected_style_imitation",
                        "severity": "high",
                        "description": f"Potential protected-style imitation instruction detected: {marker}",
                    }
                )

        for marker in self.GENERIC_PROTECTED_FRANCHISE_MARKERS:
            if marker in combined:
                warnings.append(
                    {
                        "warning_id": f"protected_franchise_marker_{self._safe_id(marker)}",
                        "warning_type": "protected_franchise_marker",
                        "severity": "high",
                        "description": f"Potential protected franchise marker detected: {marker}",
                    }
                )

        for entity in story_context.get("avoid_style_targets", []):
            entity_text = str(entity).lower()
            if entity_text and entity_text in combined:
                warnings.append(
                    {
                        "warning_id": f"avoid_style_target_{self._safe_id(entity_text)}",
                        "warning_type": "avoid_style_target",
                        "severity": "high",
                        "description": f"Text or prompt references avoided style target: {entity}",
                    }
                )

        return self._unique_dicts(warnings, key="warning_id")

    def _source_policy_results(
        self,
        *,
        reference_texts: List[Dict[str, Any]],
        story_context: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        results: List[Dict[str, Any]] = []

        for ref in reference_texts:
            policy = str(ref.get("policy", "unknown")).lower()
            source_id = ref.get("source_id", "reference")
            allowed = policy in {"public_domain", "open_licensed", "synthetic", "user_provided_allowed"}
            severity = "none" if allowed else "blocker" if policy in {"restricted", "do_not_train", "unknown"} else "medium"

            results.append(
                {
                    "source_policy_result_id": f"source_policy_{self._safe_id(source_id)}",
                    "source_id": source_id,
                    "policy": policy,
                    "allowed_for_generation": allowed,
                    "severity": severity,
                    "description": "Reference source is allowed." if allowed else f"Reference source policy is risky or unknown: {policy}",
                }
            )

        declared_sources = story_context.get("declared_sources", [])
        for item in declared_sources:
            if isinstance(item, dict):
                source_id = item.get("source_id", "declared_source")
                policy = str(item.get("policy", "unknown")).lower()
                allowed = policy in {"public_domain", "open_licensed", "synthetic", "user_provided_allowed"}
                results.append(
                    {
                        "source_policy_result_id": f"declared_source_policy_{self._safe_id(source_id)}",
                        "source_id": source_id,
                        "policy": policy,
                        "allowed_for_generation": allowed,
                        "severity": "none" if allowed else "blocker",
                        "description": "Declared source policy checked.",
                    }
                )

        return self._unique_dicts(results, key="source_policy_result_id")

    def _similarity_risks(
        self,
        *,
        text: str,
        plot_outline: PlotOutline | None,
        chapter: GeneratedChapter | None,
        story_context: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        risks: List[Dict[str, Any]] = []
        lowered = text.lower()

        for marker in self.GENERIC_PROTECTED_FRANCHISE_MARKERS:
            if marker in lowered:
                risks.append(
                    {
                        "risk_id": f"world_similarity_{self._safe_id(marker)}",
                        "risk_type": "world_similarity",
                        "severity": "high",
                        "description": f"Protected or highly recognizable world marker appears: {marker}",
                    }
                )

        if plot_outline:
            if plot_outline.premise and any(marker in plot_outline.premise.lower() for marker in self.GENERIC_PROTECTED_FRANCHISE_MARKERS):
                risks.append(
                    {
                        "risk_id": "plot_similarity_premise_marker",
                        "risk_type": "plot_similarity",
                        "severity": "high",
                        "description": "Plot premise contains highly recognizable protected-world marker.",
                    }
                )

            if len(plot_outline.character_arc_threads) == 1 and "chosen one" in lowered:
                risks.append(
                    {
                        "risk_id": "character_similarity_chosen_one_single_protagonist",
                        "risk_type": "character_similarity",
                        "severity": "medium",
                        "description": "Single-protagonist chosen-one setup may be too template-like unless transformed.",
                    }
                )

        if story_context.get("known_inspiration_titles"):
            for title in story_context["known_inspiration_titles"]:
                title_text = str(title).lower()
                if title_text and title_text in lowered:
                    risks.append(
                        {
                            "risk_id": f"plot_similarity_title_{self._safe_id(title_text)}",
                            "risk_type": "plot_similarity",
                            "severity": "high",
                            "description": f"Generated text directly references known inspiration title: {title}",
                        }
                    )

        return self._unique_dicts(risks, key="risk_id")

    def _originality_evidence(
        self,
        *,
        plot_outline: PlotOutline | None,
        chapter: GeneratedChapter | None,
        adaptive_pattern_plan: AdaptiveStoryPatternPlan | None,
        anti_genericity_report: StoryAntiGenericityReport | None,
        continuity_report: StoryContinuityValidationReport | None,
        game_package: GameInteractiveScenePackage | None,
        series_package: SeriesSeasonFormatPackage | None,
        screenplay_movie_package: ScreenplayMovieFormatPackage | None,
    ) -> List[Dict[str, Any]]:
        evidence: List[Dict[str, Any]] = []

        if plot_outline:
            if plot_outline.world_state_threads:
                evidence.append(
                    {
                        "evidence_id": "original_world_threads",
                        "evidence_type": "world_specificity",
                        "description": f"{len(plot_outline.world_state_threads)} world-state thread(s) are story-specific.",
                    }
                )
            if plot_outline.secret_threads:
                evidence.append(
                    {
                        "evidence_id": "original_secret_threads",
                        "evidence_type": "secret_specificity",
                        "description": f"{len(plot_outline.secret_threads)} secret thread(s) are story-specific.",
                    }
                )
            if plot_outline.causal_threads:
                evidence.append(
                    {
                        "evidence_id": "original_causal_threads",
                        "evidence_type": "causal_specificity",
                        "description": f"{len(plot_outline.causal_threads)} causal thread(s) are story-specific.",
                    }
                )

        if chapter and chapter.used_world_details:
            evidence.append(
                {
                    "evidence_id": "chapter_world_specificity",
                    "evidence_type": "chapter_specificity",
                    "description": f"Chapter uses specific world details: {chapter.used_world_details[:5]}",
                }
            )

        if adaptive_pattern_plan and adaptive_pattern_plan.anti_template_rules:
            evidence.append(
                {
                    "evidence_id": "anti_template_rules_present",
                    "evidence_type": "anti_template_design",
                    "description": f"{len(adaptive_pattern_plan.anti_template_rules)} anti-template rule(s) guide generation.",
                }
            )

        if anti_genericity_report and anti_genericity_report.overall_anti_genericity_score >= 0.70:
            evidence.append(
                {
                    "evidence_id": "anti_genericity_score_strong",
                    "evidence_type": "anti_genericity",
                    "description": "Anti-genericity score is strong enough to support originality.",
                }
            )

        if continuity_report and continuity_report.continuity_score >= 0.70:
            evidence.append(
                {
                    "evidence_id": "continuity_score_strong",
                    "evidence_type": "continuity",
                    "description": "Continuity score supports internally original story identity.",
                }
            )

        if game_package and game_package.state_deltas:
            evidence.append(
                {
                    "evidence_id": "interactive_state_deltas",
                    "evidence_type": "interactive_originality",
                    "description": "Interactive choices produce state deltas instead of cosmetic branching.",
                }
            )

        if series_package and series_package.cliffhanger_registry:
            evidence.append(
                {
                    "evidence_id": "series_cliffhanger_registry",
                    "evidence_type": "series_originality",
                    "description": "Series cliffhangers are tracked as original continuity elements.",
                }
            )

        if screenplay_movie_package and screenplay_movie_package.visual_motifs:
            evidence.append(
                {
                    "evidence_id": "screen_visual_motifs",
                    "evidence_type": "visual_originality",
                    "description": "Screen/movie package uses story-specific visual motifs.",
                }
            )

        return self._unique_dicts(evidence, key="evidence_id")

    def _phrase_overlap_score(self, *, phrase_risks: List[Dict[str, Any]], reference_texts: List[Dict[str, Any]]) -> float:
        if not reference_texts and not phrase_risks:
            return 0.0
        score = 0.0
        for risk in phrase_risks:
            score += 0.15 if risk.get("severity") == "medium" else 0.30
        return self._bounded(score)

    def _style_imitation_risk_score(self, *, protected_style_warnings: List[Dict[str, Any]]) -> float:
        score = 0.0
        for warning in protected_style_warnings:
            score += 0.35 if warning.get("severity") == "high" else 0.15
        return self._bounded(score)

    def _risk_dimension_score(self, risks: List[Dict[str, Any]], risk_type: str) -> float:
        score = 0.0
        for risk in risks:
            if risk.get("risk_type") == risk_type:
                score += 0.30 if risk.get("severity") == "high" else 0.15
        return self._bounded(score)

    def _originality_strength_score(
        self,
        *,
        originality_evidence: List[Dict[str, Any]],
        anti_genericity_report: StoryAntiGenericityReport | None,
        quality_report: StoryQualityScoreReport | None,
    ) -> float:
        score = 0.25 + min(0.45, len(originality_evidence) * 0.075)
        if anti_genericity_report:
            score += anti_genericity_report.overall_anti_genericity_score * 0.15
        if quality_report:
            score += quality_report.anti_generic_score * 0.10
        return self._bounded(score)

    def _overall_originality_score(
        self,
        *,
        phrase_overlap_score: float,
        style_imitation_risk_score: float,
        character_similarity_risk_score: float,
        world_similarity_risk_score: float,
        plot_similarity_risk_score: float,
        originality_strength_score: float,
        source_policy_results: List[Dict[str, Any]],
    ) -> float:
        risk_penalty = (
            phrase_overlap_score * 0.22
            + style_imitation_risk_score * 0.24
            + character_similarity_risk_score * 0.12
            + world_similarity_risk_score * 0.17
            + plot_similarity_risk_score * 0.17
        )

        if any(item.get("severity") == "blocker" for item in source_policy_results):
            risk_penalty += 0.25

        return self._bounded(originality_strength_score - risk_penalty + 0.25)

    def _copy_risk_level(
        self,
        *,
        overall_originality_score: float,
        detected_risks: List[Dict[str, Any]],
        protected_style_warnings: List[Dict[str, Any]],
        source_policy_results: List[Dict[str, Any]],
    ) -> str:
        high_risks = len([item for item in detected_risks if item.get("severity") == "high"])
        style_high = len([item for item in protected_style_warnings if item.get("severity") == "high"])
        source_blockers = len([item for item in source_policy_results if item.get("severity") == "blocker"])

        if source_blockers > 0 or style_high >= 2 or high_risks >= 3 or overall_originality_score < 0.35:
            return "critical"
        if style_high >= 1 or high_risks >= 1 or overall_originality_score < 0.55:
            return "high"
        if overall_originality_score < 0.72 or detected_risks:
            return "medium"
        return "low"

    def _rewrite_requirements(
        self,
        *,
        detected_risks: List[Dict[str, Any]],
        protected_style_warnings: List[Dict[str, Any]],
        source_policy_results: List[Dict[str, Any]],
        copy_risk_level: str,
    ) -> List[Dict[str, Any]]:
        requirements: List[Dict[str, Any]] = []

        for risk in detected_risks:
            requirements.append(
                {
                    "rewrite_requirement_id": f"rewrite_{risk.get('risk_id')}",
                    "requirement_type": risk.get("risk_type"),
                    "severity": "blocker" if risk.get("severity") == "high" else "major",
                    "instruction": self._risk_rewrite_instruction(risk),
                }
            )

        for warning in protected_style_warnings:
            requirements.append(
                {
                    "rewrite_requirement_id": f"rewrite_{warning.get('warning_id')}",
                    "requirement_type": warning.get("warning_type"),
                    "severity": "blocker",
                    "instruction": "Remove protected-style/franchise reference and replace with original structural constraints.",
                }
            )

        for result in source_policy_results:
            if not result.get("allowed_for_generation"):
                requirements.append(
                    {
                        "rewrite_requirement_id": f"rewrite_{result.get('source_policy_result_id')}",
                        "requirement_type": "source_policy",
                        "severity": "blocker",
                        "instruction": f"Do not use source {result.get('source_id')} until license/policy is resolved.",
                    }
                )

        if copy_risk_level in {"high", "critical"} and not requirements:
            requirements.append(
                {
                    "rewrite_requirement_id": "rewrite_general_copy_risk",
                    "requirement_type": "general_copy_risk",
                    "severity": "major",
                    "instruction": "Increase original world, character, causal, and prose specificity before export.",
                }
            )

        return self._unique_dicts(requirements, key="rewrite_requirement_id")

    def _risk_rewrite_instruction(self, risk: Dict[str, Any]) -> str:
        risk_type = risk.get("risk_type")
        if risk_type == "reference_phrase_overlap":
            return "Rewrite overlapping phrases with new imagery, rhythm, structure, and story-specific details."
        if risk_type == "generic_or_high_overlap_phrase":
            return "Replace generic phrase with a specific character/world/cause consequence."
        if risk_type == "world_similarity":
            return "Replace recognizable world markers with original geography, institutions, culture, objects, and rules."
        if risk_type == "character_similarity":
            return "Change archetype, motivation, voice, cost, social context, and decision logic."
        if risk_type == "plot_similarity":
            return "Change premise mechanics, causal chain, stakes, world rules, and payoff structure."
        return "Rewrite risky material with original story-specific structure."

    def _approved_original_elements(self, *, originality_evidence: List[Dict[str, Any]]) -> List[str]:
        return [item.get("description") for item in originality_evidence if item.get("description")]

    def _downstream_constraints(
        self,
        *,
        copy_risk_level: str,
        rewrite_requirements: List[Dict[str, Any]],
        originality_evidence: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        return {
            "copy_risk_level": copy_risk_level,
            "safe_for_export_without_rewrite": copy_risk_level in {"low", "medium"} and not any(item.get("severity") == "blocker" for item in rewrite_requirements),
            "must_apply_rewrite_requirement_ids": [item.get("rewrite_requirement_id") for item in rewrite_requirements],
            "preserve_original_evidence_ids": [item.get("evidence_id") for item in originality_evidence],
            "rules": [
                "Do not imitate protected author style or franchise-specific markers.",
                "Do not use unknown/restricted sources for generation.",
                "Rewrite overlapping reference phrases.",
                "Preserve original world, character, causal, and interaction details.",
            ],
        }

    def _warnings(
        self,
        *,
        text: str,
        reference_texts: List[Dict[str, Any]],
        protected_style_warnings: List[Dict[str, Any]],
        source_policy_results: List[Dict[str, Any]],
    ) -> List[str]:
        warnings: List[str] = []
        if not text:
            warnings.append("No generated text supplied; copy-risk guard used structured context only.")
        if not reference_texts:
            warnings.append("No reference texts supplied; phrase-overlap check is limited.")
        if protected_style_warnings:
            warnings.append(f"{len(protected_style_warnings)} protected-style warning(s) detected.")
        if any(item.get("severity") == "blocker" for item in source_policy_results):
            warnings.append("One or more source policy blockers detected.")
        return warnings

    def _ngrams(self, text: str, *, n: int) -> set[str]:
        tokens = [token.strip(".,!?;:()[]{}\"'").lower() for token in text.split()]
        tokens = [token for token in tokens if token]
        if len(tokens) < n:
            return set()
        return {" ".join(tokens[i : i + n]) for i in range(len(tokens) - n + 1)}

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

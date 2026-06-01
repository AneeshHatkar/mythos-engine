from __future__ import annotations

from typing import Any, Dict, List

from backend.app.schemas.story_generation import (
    AdaptiveStoryPatternPlan,
    FormatAdaptationPlan,
    GameInteractiveScenePackage,
    MultiWorldMultiCastScalingPlan,
    PlotOutline,
    ScreenplayMovieFormatPackage,
    SeriesSeasonFormatPackage,
)


class AdaptiveStoryPatternEngine:
    """Selects and blends story patterns without hardcoding one formula.

    Locked Chunk 5.31. This engine makes the system adaptive: it chooses
    pattern families from the current story context, format, scale, genre,
    characters, relationships, secrets, and causality.
    """

    engine_name = "story_generation.adaptive_story_pattern_engine"

    BASE_PATTERNS = {
        "mystery_pressure": {
            "description": "Information asymmetry, clues, false leads, partial reveals, and controlled payoffs.",
            "best_for": ["secret", "mystery", "knowledge_boundary", "reveal"],
        },
        "relationship_fracture": {
            "description": "Trust shifts, resentment, betrayal risk, repair attempts, and emotional reversals.",
            "best_for": ["relationship", "romance", "betrayal", "ensemble"],
        },
        "causal_escalation": {
            "description": "Setup, choice, consequence, counter-consequence, and payoff.",
            "best_for": ["causal", "thriller", "political", "action"],
        },
        "world_pressure": {
            "description": "World rules, institutions, laws, factions, and environmental constraints shape the plot.",
            "best_for": ["world", "fantasy", "sci-fi", "political"],
        },
        "character_transformation": {
            "description": "A character is forced through identity, belief, goal, and cost changes.",
            "best_for": ["character", "drama", "coming_of_age", "tragedy"],
        },
        "ensemble_interlock": {
            "description": "Multiple character lanes create cross-pressure and intersecting payoffs.",
            "best_for": ["large_cast", "series", "multi_cast", "ensemble"],
        },
        "interactive_branching": {
            "description": "Choices create state deltas, branch consequences, quest updates, and replayable outcomes.",
            "best_for": ["game_scene", "interactive", "branching"],
        },
        "cinematic_sequence": {
            "description": "Visual set pieces, performable action, scene turns, and filmic payoff.",
            "best_for": ["screenplay", "movie", "cinematic"],
        },
        "season_arc_weave": {
            "description": "Episode-level problems connect to season-level mysteries, payoffs, and cliffhangers.",
            "best_for": ["series", "season", "episode"],
        },
        "multi_world_convergence": {
            "description": "Separate world/cast lanes converge through shared rules, objects, or consequences.",
            "best_for": ["multi_world", "multi_cast", "large_scale"],
        },
    }

    def build_adaptive_pattern_plan(
        self,
        *,
        source_id: str,
        plot_outline: PlotOutline | None = None,
        format_plan: FormatAdaptationPlan | None = None,
        screenplay_movie_package: ScreenplayMovieFormatPackage | None = None,
        series_package: SeriesSeasonFormatPackage | None = None,
        game_package: GameInteractiveScenePackage | None = None,
        scaling_plan: MultiWorldMultiCastScalingPlan | None = None,
        story_context: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        story_context = story_context or {}

        signals = self._collect_signals(
            plot_outline=plot_outline,
            format_plan=format_plan,
            screenplay_movie_package=screenplay_movie_package,
            series_package=series_package,
            game_package=game_package,
            scaling_plan=scaling_plan,
            story_context=story_context,
        )
        scored_patterns = self._score_patterns(signals=signals)
        primary = scored_patterns[0]["pattern_id"] if scored_patterns else "causal_escalation"
        secondary = [item["pattern_id"] for item in scored_patterns[1:5]]

        plan = AdaptiveStoryPatternPlan(
            pattern_plan_id=f"adaptive_story_pattern_{source_id}",
            source_id=source_id,
            selected_primary_pattern=primary,
            selected_secondary_patterns=secondary,
            pattern_blend_strategy=self._pattern_blend_strategy(
                primary=primary,
                secondary=secondary,
                scored_patterns=scored_patterns,
                signals=signals,
            ),
            genre_pattern_map=self._genre_pattern_map(story_context=story_context, scored_patterns=scored_patterns),
            format_pattern_rules=self._format_pattern_rules(
                format_plan=format_plan,
                screenplay_movie_package=screenplay_movie_package,
                series_package=series_package,
                game_package=game_package,
            ),
            character_pattern_assignments=self._character_pattern_assignments(
                plot_outline=plot_outline,
                scaling_plan=scaling_plan,
                primary=primary,
            ),
            relationship_pattern_assignments=self._relationship_pattern_assignments(
                plot_outline=plot_outline,
                game_package=game_package,
            ),
            secret_pattern_assignments=self._secret_pattern_assignments(
                plot_outline=plot_outline,
                game_package=game_package,
            ),
            causal_pattern_assignments=self._causal_pattern_assignments(
                plot_outline=plot_outline,
                game_package=game_package,
            ),
            world_pattern_assignments=self._world_pattern_assignments(
                plot_outline=plot_outline,
                scaling_plan=scaling_plan,
                game_package=game_package,
            ),
            anti_template_rules=self._anti_template_rules(primary=primary, secondary=secondary, signals=signals),
            adaptation_reasons=self._adaptation_reasons(scored_patterns=scored_patterns, signals=signals),
            downstream_generation_constraints=self._downstream_constraints(
                primary=primary,
                secondary=secondary,
                plot_outline=plot_outline,
                scaling_plan=scaling_plan,
            ),
            warnings=self._warnings(scored_patterns=scored_patterns, signals=signals),
        )

        return {
            "success": True,
            "engine_name": self.engine_name,
            "adaptive_story_pattern_plan": plan,
            "adaptive_story_pattern_plan_dict": plan.model_dump(mode="json"),
            "scored_patterns": scored_patterns,
            "handoff_to_next_engine": {
                "next_engine": "story_generation.story_quality_scorer",
                "payload_keys": [
                    "adaptive_story_pattern_plan",
                    "plot_outline",
                    "format_adaptation_plan",
                    "multi_world_multi_cast_scaling_plan",
                    "story_context",
                ],
            },
        }

    def validate_pattern_plan(self, *, plan: AdaptiveStoryPatternPlan) -> Dict[str, Any]:
        blockers: List[str] = []
        warnings: List[str] = []
        passed: List[str] = []

        if not plan.pattern_plan_id:
            blockers.append("pattern_plan_id missing")
        else:
            passed.append("pattern_plan_id_present")

        if not plan.source_id:
            blockers.append("source_id missing")
        else:
            passed.append("source_id_present")

        if plan.selected_primary_pattern:
            passed.append("primary_pattern_present")
        else:
            blockers.append("primary pattern missing")

        if plan.pattern_blend_strategy:
            passed.append("pattern_blend_strategy_present")
        else:
            blockers.append("pattern blend strategy missing")

        if plan.anti_template_rules:
            passed.append("anti_template_rules_present")
        else:
            warnings.append("anti-template rules missing")

        if plan.downstream_generation_constraints:
            passed.append("downstream_constraints_present")
        else:
            warnings.append("downstream generation constraints missing")

        if plan.adaptation_reasons:
            passed.append("adaptation_reasons_present")
        else:
            warnings.append("adaptation reasons missing")

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

    def summarize_pattern_plan(self, *, plan: AdaptiveStoryPatternPlan) -> Dict[str, Any]:
        return {
            "success": True,
            "engine_name": self.engine_name,
            "summary": {
                "pattern_plan_id": plan.pattern_plan_id,
                "source_id": plan.source_id,
                "selected_primary_pattern": plan.selected_primary_pattern,
                "secondary_pattern_count": len(plan.selected_secondary_patterns),
                "character_assignment_count": len(plan.character_pattern_assignments),
                "relationship_assignment_count": len(plan.relationship_pattern_assignments),
                "secret_assignment_count": len(plan.secret_pattern_assignments),
                "causal_assignment_count": len(plan.causal_pattern_assignments),
                "world_assignment_count": len(plan.world_pattern_assignments),
                "anti_template_rule_count": len(plan.anti_template_rules),
                "adaptation_reason_count": len(plan.adaptation_reasons),
                "warning_count": len(plan.warnings),
            },
        }

    def build_pattern_report_text(self, *, plan: AdaptiveStoryPatternPlan) -> Dict[str, Any]:
        lines = [
            f"# Adaptive Story Pattern Plan: {plan.source_id}",
            "",
            f"Primary pattern: {plan.selected_primary_pattern}",
            f"Secondary patterns: {', '.join(plan.selected_secondary_patterns)}",
            "",
            "## Blend Strategy",
            str(plan.pattern_blend_strategy),
            "",
            "## Anti-Template Rules",
        ]

        for rule in plan.anti_template_rules:
            lines.append(f"- {rule}")

        lines.append("")
        lines.append("## Adaptation Reasons")
        for reason in plan.adaptation_reasons:
            lines.append(f"- {reason}")

        lines.append("")
        lines.append("## Downstream Constraints")
        for key, value in plan.downstream_generation_constraints.items():
            lines.append(f"- {key}: {value}")

        return {
            "success": True,
            "engine_name": self.engine_name,
            "pattern_report_text": "\n".join(lines),
        }

    def _collect_signals(
        self,
        *,
        plot_outline: PlotOutline | None,
        format_plan: FormatAdaptationPlan | None,
        screenplay_movie_package: ScreenplayMovieFormatPackage | None,
        series_package: SeriesSeasonFormatPackage | None,
        game_package: GameInteractiveScenePackage | None,
        scaling_plan: MultiWorldMultiCastScalingPlan | None,
        story_context: Dict[str, Any],
    ) -> Dict[str, Any]:
        genres = [str(item).lower() for item in story_context.get("genres", [])]
        tone_tags = [str(item).lower() for item in story_context.get("tone_tags", [])]

        signals: Dict[str, Any] = {
            "genres": genres,
            "tone_tags": tone_tags,
            "target_format": format_plan.target_format if format_plan else story_context.get("target_format", ""),
            "secret_count": 0,
            "relationship_count": 0,
            "causal_count": 0,
            "world_count": 0,
            "character_count": 0,
            "episode_count": 0,
            "choice_count": 0,
            "branch_count": 0,
            "scaling_pressure_level": "low",
            "multi_world": False,
            "multi_cast": False,
            "has_screen_or_movie": False,
            "has_series": False,
            "has_game": False,
        }

        if plot_outline:
            signals["secret_count"] += len(plot_outline.secret_threads)
            signals["relationship_count"] += len(plot_outline.relationship_arc_threads)
            signals["causal_count"] += len(plot_outline.causal_threads)
            signals["world_count"] += len(plot_outline.world_state_threads)
            signals["character_count"] += len(plot_outline.character_arc_threads)

        if screenplay_movie_package:
            signals["has_screen_or_movie"] = True
            signals["target_format"] = screenplay_movie_package.target_format

        if series_package:
            signals["has_series"] = True
            signals["episode_count"] += series_package.episode_count

        if game_package:
            signals["has_game"] = True
            signals["choice_count"] += len(game_package.choice_menu)
            signals["branch_count"] += len(game_package.branching_outcomes)

        if scaling_plan:
            signals["world_count"] = max(signals["world_count"], scaling_plan.world_count)
            signals["character_count"] = max(signals["character_count"], scaling_plan.total_character_count)
            signals["scaling_pressure_level"] = scaling_plan.scaling_pressure_report.get("pressure_level", "low")
            signals["multi_world"] = scaling_plan.world_count > 1
            signals["multi_cast"] = scaling_plan.cast_count > 1 or scaling_plan.total_character_count > 12

        return signals

    def _score_patterns(self, *, signals: Dict[str, Any]) -> List[Dict[str, Any]]:
        scores: Dict[str, float] = {pattern_id: 0.10 for pattern_id in self.BASE_PATTERNS}

        genres = set(signals.get("genres", []))
        target_format = str(signals.get("target_format", "")).lower()

        if signals.get("secret_count", 0) > 0 or "mystery" in genres:
            scores["mystery_pressure"] += 0.35

        if signals.get("relationship_count", 0) > 0 or {"romance", "drama"} & genres:
            scores["relationship_fracture"] += 0.30

        if signals.get("causal_count", 0) > 0 or {"thriller", "political", "action"} & genres:
            scores["causal_escalation"] += 0.32

        if signals.get("world_count", 0) > 1 or {"fantasy", "sci-fi", "science fiction"} & genres:
            scores["world_pressure"] += 0.28

        if signals.get("character_count", 0) > 0:
            scores["character_transformation"] += 0.18

        if signals.get("character_count", 0) >= 8 or signals.get("multi_cast"):
            scores["ensemble_interlock"] += 0.35

        if signals.get("has_game") or target_format == "game_scene" or signals.get("choice_count", 0) > 0:
            scores["interactive_branching"] += 0.45

        if signals.get("has_screen_or_movie") or target_format in {"screenplay", "movie"}:
            scores["cinematic_sequence"] += 0.40

        if signals.get("has_series") or signals.get("episode_count", 0) > 0 or target_format in {"series", "series_episode"}:
            scores["season_arc_weave"] += 0.40

        if signals.get("multi_world") or signals.get("scaling_pressure_level") == "high":
            scores["multi_world_convergence"] += 0.45

        if "tragedy" in genres:
            scores["character_transformation"] += 0.15
            scores["relationship_fracture"] += 0.10

        if "comedy" in genres:
            scores["ensemble_interlock"] += 0.08
            scores["relationship_fracture"] += 0.05

        scored = [
            {
                "pattern_id": pattern_id,
                "score": round(min(1.0, score), 3),
                "description": self.BASE_PATTERNS[pattern_id]["description"],
            }
            for pattern_id, score in scores.items()
        ]
        scored.sort(key=lambda item: item["score"], reverse=True)
        return scored

    def _pattern_blend_strategy(
        self,
        *,
        primary: str,
        secondary: List[str],
        scored_patterns: List[Dict[str, Any]],
        signals: Dict[str, Any],
    ) -> Dict[str, Any]:
        return {
            "primary_pattern": primary,
            "secondary_patterns": secondary,
            "blend_mode": "weighted_interlock" if len(secondary) >= 2 else "single_pattern_with_support",
            "pattern_weights": {
                item["pattern_id"]: item["score"]
                for item in scored_patterns[:5]
            },
            "scaling_pressure_level": signals.get("scaling_pressure_level"),
            "rule": "Use the primary pattern for structure, secondary patterns for scene-level pressure and variation.",
        }

    def _genre_pattern_map(self, *, story_context: Dict[str, Any], scored_patterns: List[Dict[str, Any]]) -> Dict[str, Any]:
        genres = story_context.get("genres", [])
        return {
            "genres": genres,
            "top_patterns": [item["pattern_id"] for item in scored_patterns[:5]],
            "genre_rule": "Genre influences pattern weighting but does not hardcode the final story path.",
        }

    def _format_pattern_rules(
        self,
        *,
        format_plan: FormatAdaptationPlan | None,
        screenplay_movie_package: ScreenplayMovieFormatPackage | None,
        series_package: SeriesSeasonFormatPackage | None,
        game_package: GameInteractiveScenePackage | None,
    ) -> Dict[str, Any]:
        rules: Dict[str, Any] = {
            "format_sensitive": True,
            "must_preserve_format_constraints": True,
        }

        if format_plan:
            rules["format_plan_id"] = format_plan.adaptation_plan_id
            rules["target_format"] = format_plan.target_format
            rules["forbidden_patterns"] = format_plan.forbidden_patterns

        if screenplay_movie_package:
            rules["screen_or_movie_package_id"] = screenplay_movie_package.format_package_id
            rules["screen_rule"] = "Prefer visible action, performable turns, and cinematic sequence logic."

        if series_package:
            rules["series_package_id"] = series_package.series_package_id
            rules["series_rule"] = "Use episode cards, cliffhangers, and season carryover to distribute pattern payoffs."

        if game_package:
            rules["game_package_id"] = game_package.game_package_id
            rules["game_rule"] = "Pattern must create player choices, branch outcomes, and state deltas."

        return rules

    def _character_pattern_assignments(
        self,
        *,
        plot_outline: PlotOutline | None,
        scaling_plan: MultiWorldMultiCastScalingPlan | None,
        primary: str,
    ) -> List[Dict[str, Any]]:
        character_ids: List[str] = []
        if plot_outline:
            character_ids.extend([item.get("character_id") for item in plot_outline.character_arc_threads if item.get("character_id")])
            character_ids.extend(plot_outline.continuity_requirements.get("required_character_ids", []))
        if scaling_plan:
            for cast in scaling_plan.cast_registry:
                character_ids.extend(cast.get("character_ids", []))

        assignments = []
        for index, character_id in enumerate(self._unique(character_ids), start=1):
            assignments.append(
                {
                    "assignment_id": f"character_pattern_{character_id}",
                    "character_id": character_id,
                    "assigned_pattern": primary if index <= 3 else "ensemble_interlock",
                    "role": "primary_pressure_carrier" if index <= 3 else "supporting_lane_carrier",
                    "instruction": f"Use pattern logic to evolve {character_id} without flattening their voice or goals.",
                }
            )
        return assignments

    def _relationship_pattern_assignments(
        self,
        *,
        plot_outline: PlotOutline | None,
        game_package: GameInteractiveScenePackage | None,
    ) -> List[Dict[str, Any]]:
        relationship_ids: List[str] = []
        if plot_outline:
            relationship_ids.extend([item.get("relationship_id") for item in plot_outline.relationship_arc_threads if item.get("relationship_id")])
            relationship_ids.extend(plot_outline.continuity_requirements.get("required_relationship_ids", []))
        if game_package:
            relationship_ids.extend([item.get("relationship_id") for item in game_package.relationship_state_hooks if item.get("relationship_id")])

        return [
            {
                "assignment_id": f"relationship_pattern_{relationship_id}",
                "relationship_id": relationship_id,
                "assigned_pattern": "relationship_fracture",
                "instruction": f"Track trust, resentment, repair, and reversal pattern for {relationship_id}.",
            }
            for relationship_id in self._unique(relationship_ids)
        ]

    def _secret_pattern_assignments(
        self,
        *,
        plot_outline: PlotOutline | None,
        game_package: GameInteractiveScenePackage | None,
    ) -> List[Dict[str, Any]]:
        secret_ids: List[str] = []
        if plot_outline:
            secret_ids.extend([item.get("secret_id") for item in plot_outline.secret_threads if item.get("secret_id")])
            secret_ids.extend(plot_outline.continuity_requirements.get("required_secret_ids", []))
        if game_package:
            secret_ids.extend([item.get("secret_id") for item in game_package.secret_state_hooks if item.get("secret_id")])

        return [
            {
                "assignment_id": f"secret_pattern_{secret_id}",
                "secret_id": secret_id,
                "assigned_pattern": "mystery_pressure",
                "instruction": f"Use clue, withholding, partial reveal, and payoff timing for {secret_id}.",
            }
            for secret_id in self._unique(secret_ids)
        ]

    def _causal_pattern_assignments(
        self,
        *,
        plot_outline: PlotOutline | None,
        game_package: GameInteractiveScenePackage | None,
    ) -> List[Dict[str, Any]]:
        causal_ids: List[str] = []
        if plot_outline:
            causal_ids.extend([item.get("causal_id") for item in plot_outline.causal_threads if item.get("causal_id")])
            causal_ids.extend(plot_outline.continuity_requirements.get("required_causal_ids", []))
        if game_package:
            causal_ids.extend([item.get("causal_id") for item in game_package.causal_state_hooks if item.get("causal_id")])

        return [
            {
                "assignment_id": f"causal_pattern_{causal_id}",
                "causal_id": causal_id,
                "assigned_pattern": "causal_escalation",
                "instruction": f"Preserve setup, choice, consequence, and payoff for {causal_id}.",
            }
            for causal_id in self._unique(causal_ids)
        ]

    def _world_pattern_assignments(
        self,
        *,
        plot_outline: PlotOutline | None,
        scaling_plan: MultiWorldMultiCastScalingPlan | None,
        game_package: GameInteractiveScenePackage | None,
    ) -> List[Dict[str, Any]]:
        world_details: List[str] = []
        if plot_outline:
            world_details.extend([item.get("world_detail") for item in plot_outline.world_state_threads if item.get("world_detail")])
            world_details.extend(plot_outline.continuity_requirements.get("required_world_details", []))
        if scaling_plan:
            world_details.extend([item.get("world_name") for item in scaling_plan.world_registry if item.get("world_name")])
        if game_package:
            world_details.extend([item.get("world_detail") for item in game_package.world_state_hooks if item.get("world_detail")])

        return [
            {
                "assignment_id": f"world_pattern_{self._safe_id(detail)}",
                "world_detail": detail,
                "assigned_pattern": "world_pressure",
                "instruction": f"Use world rules/institutions/environment as pressure, not background decoration: {detail}.",
            }
            for detail in self._unique(world_details)
        ]

    def _anti_template_rules(self, *, primary: str, secondary: List[str], signals: Dict[str, Any]) -> List[str]:
        rules = [
            "Do not use a single universal three-act formula for every output.",
            "Do not resolve secrets immediately unless the reveal is explicitly required.",
            "Do not make every character react with the same emotional pattern.",
            "Do not treat world details as decorative lore; each repeated detail needs consequence or pressure.",
            "Do not repeat the same scene rhythm more than twice in a row.",
            "Do not flatten relationships into simple ally/enemy states.",
            "Do not let choices be cosmetic; interactive choices must produce state deltas.",
        ]

        if primary == "mystery_pressure":
            rules.append("Mystery pressure must include clue spacing, false certainty, and controlled payoff timing.")

        if primary == "ensemble_interlock" or signals.get("character_count", 0) >= 8:
            rules.append("Large casts must be split into distinct pressure lanes and voice clusters.")

        if signals.get("multi_world"):
            rules.append("Multi-world stories must define which rules transfer across worlds and which do not.")

        return self._unique(rules)

    def _adaptation_reasons(self, *, scored_patterns: List[Dict[str, Any]], signals: Dict[str, Any]) -> List[str]:
        reasons = []
        for item in scored_patterns[:5]:
            reasons.append(
                f"Selected {item['pattern_id']} with score {item['score']} because current story signals match: {self.BASE_PATTERNS[item['pattern_id']]['best_for']}."
            )

        if signals.get("has_game"):
            reasons.append("Interactive game output detected, so choices and state deltas affect pattern selection.")

        if signals.get("has_series"):
            reasons.append("Series output detected, so episode/season carryover affects pattern selection.")

        if signals.get("has_screen_or_movie"):
            reasons.append("Screen/movie output detected, so visual sequence logic affects pattern selection.")

        if signals.get("scaling_pressure_level") in {"medium", "high"}:
            reasons.append(f"Scaling pressure is {signals.get('scaling_pressure_level')}, so pattern lanes must be partitioned.")

        return self._unique(reasons)

    def _downstream_constraints(
        self,
        *,
        primary: str,
        secondary: List[str],
        plot_outline: PlotOutline | None,
        scaling_plan: MultiWorldMultiCastScalingPlan | None,
    ) -> Dict[str, Any]:
        constraints: Dict[str, Any] = {
            "primary_pattern": primary,
            "secondary_patterns": secondary,
            "must_use_pattern_blend": True,
            "must_preserve_open_loops": True,
            "must_preserve_causal_payoffs": True,
            "must_preserve_character_voice": True,
        }

        if plot_outline:
            constraints["required_payoff_ids"] = [item.get("payoff_id") for item in plot_outline.payoff_setups]
            constraints["required_open_loop_ids"] = [item.get("loop_id") for item in plot_outline.open_loops if item.get("loop_id")]

        if scaling_plan:
            constraints["generation_batch_ids"] = [item.get("batch_id") for item in scaling_plan.generation_batch_plan]
            constraints["continuity_partition_rule_ids"] = [item.get("rule_id") for item in scaling_plan.continuity_partition_rules]

        return constraints

    def _warnings(self, *, scored_patterns: List[Dict[str, Any]], signals: Dict[str, Any]) -> List[str]:
        warnings: List[str] = []

        if not scored_patterns:
            warnings.append("No story patterns were scored.")

        if signals.get("character_count", 0) == 0:
            warnings.append("No character signals found; pattern plan may become generic.")

        if signals.get("causal_count", 0) == 0:
            warnings.append("No causal signals found; pattern plan may lack consequence logic.")

        if signals.get("scaling_pressure_level") == "high":
            warnings.append("High scaling pressure requires strict continuity partitioning.")

        return self._unique(warnings)

    def _safe_id(self, value: str) -> str:
        return "".join(ch.lower() if ch.isalnum() else "_" for ch in str(value)).strip("_")[:60] or "item"

    def _unique(self, values: List[str]) -> List[str]:
        result = []
        seen = set()
        for value in values:
            if value and value not in seen:
                seen.add(value)
                result.append(value)
        return result

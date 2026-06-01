from __future__ import annotations

from typing import Any, Dict, List

from backend.app.schemas.story_generation import (
    GameInteractiveScenePackage,
    GeneratedChapter,
    LongFormContinuationAnchor,
    MultiWorldMultiCastScalingPlan,
    PlotOutline,
    SeriesSeasonFormatPackage,
)


class MultiWorldMultiCastScalingController:
    """Controls scaling across many worlds, casts, and story lanes.

    Locked Chunk 5.30. This controller prevents large-scale generation from
    becoming chaotic by partitioning worlds, casts, protagonists, storylines,
    continuity rules, and generation batches.
    """

    engine_name = "story_generation.multi_world_multi_cast_scaling_controller"

    def build_scaling_plan(
        self,
        *,
        source_id: str,
        plot_outline: PlotOutline | None = None,
        chapters: List[GeneratedChapter] | None = None,
        continuation_anchor: LongFormContinuationAnchor | None = None,
        series_package: SeriesSeasonFormatPackage | None = None,
        game_package: GameInteractiveScenePackage | None = None,
        story_context: Dict[str, Any] | None = None,
        max_characters_per_batch: int = 12,
        max_worlds_per_batch: int = 3,
    ) -> Dict[str, Any]:
        chapters = chapters or []
        story_context = story_context or {}

        world_registry = self._world_registry(
            plot_outline=plot_outline,
            chapters=chapters,
            continuation_anchor=continuation_anchor,
            game_package=game_package,
            story_context=story_context,
        )
        cast_registry = self._cast_registry(
            plot_outline=plot_outline,
            chapters=chapters,
            continuation_anchor=continuation_anchor,
            series_package=series_package,
            game_package=game_package,
            story_context=story_context,
        )
        protagonist_groups = self._protagonist_group_registry(
            cast_registry=cast_registry,
            story_context=story_context,
        )
        storyline_lanes = self._storyline_lanes(
            plot_outline=plot_outline,
            series_package=series_package,
            game_package=game_package,
            continuation_anchor=continuation_anchor,
        )
        cross_world_links = self._cross_world_links(
            world_registry=world_registry,
            plot_outline=plot_outline,
            story_context=story_context,
        )
        cross_cast_relationships = self._cross_cast_relationships(
            cast_registry=cast_registry,
            plot_outline=plot_outline,
            continuation_anchor=continuation_anchor,
        )
        continuity_rules = self._continuity_partition_rules(
            world_registry=world_registry,
            cast_registry=cast_registry,
            storyline_lanes=storyline_lanes,
        )
        pressure_report = self._scaling_pressure_report(
            world_registry=world_registry,
            cast_registry=cast_registry,
            storyline_lanes=storyline_lanes,
            cross_world_links=cross_world_links,
            cross_cast_relationships=cross_cast_relationships,
        )
        batch_plan = self._generation_batch_plan(
            world_registry=world_registry,
            cast_registry=cast_registry,
            storyline_lanes=storyline_lanes,
            max_characters_per_batch=max_characters_per_batch,
            max_worlds_per_batch=max_worlds_per_batch,
        )
        risk_flags = self._collision_risk_flags(
            world_registry=world_registry,
            cast_registry=cast_registry,
            storyline_lanes=storyline_lanes,
            pressure_report=pressure_report,
        )

        plan = MultiWorldMultiCastScalingPlan(
            scaling_plan_id=f"multi_world_multi_cast_scaling_{source_id}",
            source_id=source_id,
            world_count=len(world_registry),
            cast_count=len(cast_registry),
            total_character_count=sum(len(cast.get("character_ids", [])) for cast in cast_registry),
            world_registry=world_registry,
            cast_registry=cast_registry,
            protagonist_group_registry=protagonist_groups,
            storyline_lanes=storyline_lanes,
            cross_world_links=cross_world_links,
            cross_cast_relationships=cross_cast_relationships,
            continuity_partition_rules=continuity_rules,
            scaling_pressure_report=pressure_report,
            generation_batch_plan=batch_plan,
            collision_risk_flags=risk_flags,
            recommendations=self._recommendations(
                pressure_report=pressure_report,
                risk_flags=risk_flags,
                batch_plan=batch_plan,
            ),
            warnings=self._warnings(
                world_registry=world_registry,
                cast_registry=cast_registry,
                storyline_lanes=storyline_lanes,
            ),
        )

        return {
            "success": True,
            "engine_name": self.engine_name,
            "multi_world_multi_cast_scaling_plan": plan,
            "multi_world_multi_cast_scaling_plan_dict": plan.model_dump(mode="json"),
            "handoff_to_next_engine": {
                "next_engine": "story_generation.adaptive_story_pattern_engine",
                "payload_keys": [
                    "multi_world_multi_cast_scaling_plan",
                    "plot_outline",
                    "generated_chapters",
                    "series_season_format_package",
                    "game_interactive_scene_package",
                    "continuation_anchor",
                    "story_context",
                ],
            },
        }

    def validate_scaling_plan(self, *, plan: MultiWorldMultiCastScalingPlan) -> Dict[str, Any]:
        blockers: List[str] = []
        warnings: List[str] = []
        passed: List[str] = []

        if not plan.scaling_plan_id:
            blockers.append("scaling_plan_id missing")
        else:
            passed.append("scaling_plan_id_present")

        if not plan.source_id:
            blockers.append("source_id missing")
        else:
            passed.append("source_id_present")

        if plan.world_registry:
            passed.append("world_registry_present")
        else:
            blockers.append("world registry missing")

        if plan.cast_registry:
            passed.append("cast_registry_present")
        else:
            blockers.append("cast registry missing")

        if plan.storyline_lanes:
            passed.append("storyline_lanes_present")
        else:
            warnings.append("storyline lanes missing")

        if plan.continuity_partition_rules:
            passed.append("continuity_partition_rules_present")
        else:
            warnings.append("continuity partition rules missing")

        if plan.generation_batch_plan:
            passed.append("generation_batch_plan_present")
        else:
            warnings.append("generation batch plan missing")

        if plan.scaling_pressure_report:
            passed.append("scaling_pressure_report_present")
        else:
            warnings.append("scaling pressure report missing")

        if plan.collision_risk_flags:
            warnings.extend(plan.collision_risk_flags)

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

    def summarize_scaling_plan(self, *, plan: MultiWorldMultiCastScalingPlan) -> Dict[str, Any]:
        return {
            "success": True,
            "engine_name": self.engine_name,
            "summary": {
                "scaling_plan_id": plan.scaling_plan_id,
                "source_id": plan.source_id,
                "world_count": plan.world_count,
                "cast_count": plan.cast_count,
                "total_character_count": plan.total_character_count,
                "storyline_lane_count": len(plan.storyline_lanes),
                "cross_world_link_count": len(plan.cross_world_links),
                "cross_cast_relationship_count": len(plan.cross_cast_relationships),
                "continuity_rule_count": len(plan.continuity_partition_rules),
                "generation_batch_count": len(plan.generation_batch_plan),
                "collision_risk_count": len(plan.collision_risk_flags),
                "recommendation_count": len(plan.recommendations),
                "warning_count": len(plan.warnings),
            },
        }

    def build_scaling_report_text(self, *, plan: MultiWorldMultiCastScalingPlan) -> Dict[str, Any]:
        lines = [
            f"# Multi-World / Multi-Cast Scaling Plan: {plan.source_id}",
            "",
            f"- Worlds: {plan.world_count}",
            f"- Casts: {plan.cast_count}",
            f"- Total characters: {plan.total_character_count}",
            "",
            "## Worlds",
        ]

        for world in plan.world_registry:
            lines.append(f"- {world.get('world_id')}: {world.get('description')}")

        lines.append("")
        lines.append("## Casts")
        for cast in plan.cast_registry:
            lines.append(f"- {cast.get('cast_id')}: {len(cast.get('character_ids', []))} characters")

        lines.append("")
        lines.append("## Storyline Lanes")
        for lane in plan.storyline_lanes:
            lines.append(f"- {lane.get('lane_id')}: {lane.get('description')}")

        lines.append("")
        lines.append("## Batch Plan")
        for batch in plan.generation_batch_plan:
            lines.append(f"- {batch.get('batch_id')}: worlds={batch.get('world_ids')} cast={batch.get('cast_id')} lanes={batch.get('lane_ids')}")

        lines.append("")
        lines.append("## Recommendations")
        for item in plan.recommendations:
            lines.append(f"- {item}")

        return {
            "success": True,
            "engine_name": self.engine_name,
            "scaling_report_text": "\n".join(lines),
        }

    def _world_registry(
        self,
        *,
        plot_outline: PlotOutline | None,
        chapters: List[GeneratedChapter],
        continuation_anchor: LongFormContinuationAnchor | None,
        game_package: GameInteractiveScenePackage | None,
        story_context: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        worlds: List[Dict[str, Any]] = []

        for item in story_context.get("worlds", []):
            if isinstance(item, dict):
                worlds.append(dict(item))

        world_details: List[str] = []
        if plot_outline:
            world_details.extend(plot_outline.continuity_requirements.get("required_world_details", []))
            world_details.extend([item.get("world_detail") for item in plot_outline.world_state_threads if item.get("world_detail")])
        for chapter in chapters:
            world_details.extend(chapter.used_world_details)
        if continuation_anchor:
            world_details.extend(continuation_anchor.active_world_details)
        if game_package:
            world_details.extend([item.get("world_detail") for item in game_package.world_state_hooks if item.get("world_detail")])

        for index, detail in enumerate(self._unique(world_details), start=1):
            worlds.append(
                {
                    "world_id": f"world_{self._safe_id(detail)}",
                    "world_name": str(detail),
                    "description": f"World partition for detail/rule: {detail}.",
                    "source_detail": detail,
                    "continuity_scope": "local_world_rule",
                    "priority": "high" if index <= 5 else "medium",
                }
            )

        if not worlds:
            worlds.append(
                {
                    "world_id": "world_primary",
                    "world_name": "Primary World",
                    "description": "Default primary world partition.",
                    "source_detail": "default",
                    "continuity_scope": "primary",
                    "priority": "medium",
                }
            )

        return self._unique_dicts(worlds, key="world_id")

    def _cast_registry(
        self,
        *,
        plot_outline: PlotOutline | None,
        chapters: List[GeneratedChapter],
        continuation_anchor: LongFormContinuationAnchor | None,
        series_package: SeriesSeasonFormatPackage | None,
        game_package: GameInteractiveScenePackage | None,
        story_context: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        casts: List[Dict[str, Any]] = []

        for item in story_context.get("casts", []):
            if isinstance(item, dict):
                casts.append(dict(item))

        character_ids: List[str] = []
        relationship_ids: List[str] = []

        if plot_outline:
            character_ids.extend(plot_outline.continuity_requirements.get("required_character_ids", []))
            character_ids.extend([item.get("character_id") for item in plot_outline.character_arc_threads if item.get("character_id")])
            relationship_ids.extend(plot_outline.continuity_requirements.get("required_relationship_ids", []))
            relationship_ids.extend([item.get("relationship_id") for item in plot_outline.relationship_arc_threads if item.get("relationship_id")])

        for chapter in chapters:
            character_ids.extend(chapter.used_character_ids)
            relationship_ids.extend(chapter.used_relationship_ids)

        if continuation_anchor:
            character_ids.extend(continuation_anchor.active_character_ids)
            relationship_ids.extend(continuation_anchor.active_relationship_ids)

        if series_package:
            for dynamic in series_package.recurring_character_dynamics:
                if dynamic.get("character_id"):
                    character_ids.append(dynamic["character_id"])
                if dynamic.get("relationship_id"):
                    relationship_ids.append(dynamic["relationship_id"])

        if game_package:
            for dialogue in game_package.npc_dialogue_blocks:
                if dialogue.get("npc_id"):
                    character_ids.append(dialogue["npc_id"])
            for hook in game_package.relationship_state_hooks:
                if hook.get("relationship_id"):
                    relationship_ids.append(hook["relationship_id"])

        unique_chars = self._unique(character_ids)
        unique_relationships = self._unique(relationship_ids)

        if unique_chars:
            casts.append(
                {
                    "cast_id": "cast_primary",
                    "cast_type": "primary",
                    "character_ids": unique_chars[:20],
                    "relationship_ids": unique_relationships,
                    "description": "Primary active cast gathered from current story generation context.",
                    "priority": "high",
                }
            )

        if len(unique_chars) > 20:
            casts.append(
                {
                    "cast_id": "cast_secondary",
                    "cast_type": "secondary",
                    "character_ids": unique_chars[20:60],
                    "relationship_ids": [],
                    "description": "Secondary cast split to reduce generation overload.",
                    "priority": "medium",
                }
            )

        if not casts:
            casts.append(
                {
                    "cast_id": "cast_primary",
                    "cast_type": "primary",
                    "character_ids": ["char_placeholder"],
                    "relationship_ids": [],
                    "description": "Default placeholder cast for scaling plan.",
                    "priority": "low",
                }
            )

        return self._unique_dicts(casts, key="cast_id")

    def _protagonist_group_registry(
        self,
        *,
        cast_registry: List[Dict[str, Any]],
        story_context: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        groups: List[Dict[str, Any]] = []

        for item in story_context.get("protagonist_groups", []):
            if isinstance(item, dict):
                groups.append(dict(item))

        if not groups:
            for cast in cast_registry:
                character_ids = cast.get("character_ids", [])
                if character_ids:
                    groups.append(
                        {
                            "group_id": f"protagonist_group_{cast.get('cast_id')}",
                            "cast_id": cast.get("cast_id"),
                            "character_ids": character_ids[:5],
                            "group_type": "active_viewpoint_cluster",
                            "description": "Primary viewpoint cluster for scalable generation.",
                        }
                    )

        return self._unique_dicts(groups, key="group_id")

    def _storyline_lanes(
        self,
        *,
        plot_outline: PlotOutline | None,
        series_package: SeriesSeasonFormatPackage | None,
        game_package: GameInteractiveScenePackage | None,
        continuation_anchor: LongFormContinuationAnchor | None,
    ) -> List[Dict[str, Any]]:
        lanes: List[Dict[str, Any]] = []

        if plot_outline:
            for thread in plot_outline.causal_threads:
                lanes.append(
                    {
                        "lane_id": f"lane_causal_{thread.get('causal_id')}",
                        "lane_type": "causal",
                        "source_id": thread.get("causal_id"),
                        "description": thread.get("description"),
                        "priority": "high",
                    }
                )
            for thread in plot_outline.secret_threads:
                lanes.append(
                    {
                        "lane_id": f"lane_secret_{thread.get('secret_id')}",
                        "lane_type": "secret",
                        "source_id": thread.get("secret_id"),
                        "description": thread.get("description"),
                        "priority": "high",
                    }
                )

        if series_package:
            for lane_name, beats in series_package.plot_lanes.items():
                lanes.append(
                    {
                        "lane_id": f"lane_series_{lane_name}",
                        "lane_type": "series_plot_lane",
                        "source_id": lane_name,
                        "description": f"Series lane {lane_name} with {len(beats)} beat(s).",
                        "priority": "medium_high",
                    }
                )

        if game_package:
            for outcome in game_package.branching_outcomes:
                lanes.append(
                    {
                        "lane_id": f"lane_game_{outcome.get('outcome_id')}",
                        "lane_type": "interactive_branch",
                        "source_id": outcome.get("outcome_id"),
                        "description": outcome.get("description"),
                        "priority": "medium",
                    }
                )

        if continuation_anchor:
            for loop in continuation_anchor.open_loops:
                lanes.append(
                    {
                        "lane_id": f"lane_open_loop_{loop.get('loop_id')}",
                        "lane_type": "open_loop",
                        "source_id": loop.get("loop_id"),
                        "description": loop.get("description"),
                        "priority": "high",
                    }
                )

        if not lanes:
            lanes.append(
                {
                    "lane_id": "lane_main",
                    "lane_type": "main",
                    "source_id": "default",
                    "description": "Default main storyline lane.",
                    "priority": "medium",
                }
            )

        return self._unique_dicts(lanes, key="lane_id")

    def _cross_world_links(
        self,
        *,
        world_registry: List[Dict[str, Any]],
        plot_outline: PlotOutline | None,
        story_context: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        links: List[Dict[str, Any]] = []

        for item in story_context.get("cross_world_links", []):
            if isinstance(item, dict):
                links.append(dict(item))

        if len(world_registry) > 1:
            primary = world_registry[0]["world_id"]
            for world in world_registry[1:]:
                links.append(
                    {
                        "cross_world_link_id": f"cross_world_{primary}_to_{world['world_id']}",
                        "from_world_id": primary,
                        "to_world_id": world["world_id"],
                        "link_type": "shared_continuity_pressure",
                        "description": f"{primary} and {world['world_id']} share story continuity pressure.",
                    }
                )

        return self._unique_dicts(links, key="cross_world_link_id")

    def _cross_cast_relationships(
        self,
        *,
        cast_registry: List[Dict[str, Any]],
        plot_outline: PlotOutline | None,
        continuation_anchor: LongFormContinuationAnchor | None,
    ) -> List[Dict[str, Any]]:
        relationships: List[Dict[str, Any]] = []

        relationship_ids: List[str] = []
        if plot_outline:
            relationship_ids.extend(plot_outline.continuity_requirements.get("required_relationship_ids", []))
            relationship_ids.extend([item.get("relationship_id") for item in plot_outline.relationship_arc_threads if item.get("relationship_id")])
        if continuation_anchor:
            relationship_ids.extend(continuation_anchor.active_relationship_ids)

        for relationship_id in self._unique(relationship_ids):
            relationships.append(
                {
                    "cross_cast_relationship_id": f"cross_cast_{relationship_id}",
                    "relationship_id": relationship_id,
                    "related_cast_ids": [cast.get("cast_id") for cast in cast_registry],
                    "description": f"Relationship {relationship_id} must remain consistent across cast partitions.",
                }
            )

        return relationships

    def _continuity_partition_rules(
        self,
        *,
        world_registry: List[Dict[str, Any]],
        cast_registry: List[Dict[str, Any]],
        storyline_lanes: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        rules: List[Dict[str, Any]] = []

        for world in world_registry:
            rules.append(
                {
                    "rule_id": f"world_partition_rule_{world['world_id']}",
                    "rule_type": "world_partition",
                    "target_id": world["world_id"],
                    "description": f"Maintain world-specific rules and details for {world['world_id']} without contradiction.",
                }
            )

        for cast in cast_registry:
            rules.append(
                {
                    "rule_id": f"cast_partition_rule_{cast['cast_id']}",
                    "rule_type": "cast_partition",
                    "target_id": cast["cast_id"],
                    "description": f"Keep voice, relationship state, and memory stable for {cast['cast_id']}.",
                }
            )

        for lane in storyline_lanes:
            rules.append(
                {
                    "rule_id": f"lane_partition_rule_{lane['lane_id']}",
                    "rule_type": "storyline_lane",
                    "target_id": lane["lane_id"],
                    "description": f"Track setup, escalation, and payoff for storyline lane {lane['lane_id']}.",
                }
            )

        return rules

    def _scaling_pressure_report(
        self,
        *,
        world_registry: List[Dict[str, Any]],
        cast_registry: List[Dict[str, Any]],
        storyline_lanes: List[Dict[str, Any]],
        cross_world_links: List[Dict[str, Any]],
        cross_cast_relationships: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        total_characters = sum(len(cast.get("character_ids", [])) for cast in cast_registry)
        pressure_score = 0.0
        pressure_score += min(0.25, len(world_registry) * 0.04)
        pressure_score += min(0.30, total_characters * 0.01)
        pressure_score += min(0.25, len(storyline_lanes) * 0.025)
        pressure_score += min(0.10, len(cross_world_links) * 0.02)
        pressure_score += min(0.10, len(cross_cast_relationships) * 0.02)

        if pressure_score >= 0.75:
            level = "high"
        elif pressure_score >= 0.45:
            level = "medium"
        else:
            level = "low"

        return {
            "pressure_score": round(min(1.0, pressure_score), 3),
            "pressure_level": level,
            "world_count": len(world_registry),
            "cast_count": len(cast_registry),
            "total_character_count": total_characters,
            "storyline_lane_count": len(storyline_lanes),
            "cross_world_link_count": len(cross_world_links),
            "cross_cast_relationship_count": len(cross_cast_relationships),
        }

    def _generation_batch_plan(
        self,
        *,
        world_registry: List[Dict[str, Any]],
        cast_registry: List[Dict[str, Any]],
        storyline_lanes: List[Dict[str, Any]],
        max_characters_per_batch: int,
        max_worlds_per_batch: int,
    ) -> List[Dict[str, Any]]:
        batches: List[Dict[str, Any]] = []
        world_chunks = [
            world_registry[i : i + max(1, max_worlds_per_batch)]
            for i in range(0, len(world_registry), max(1, max_worlds_per_batch))
        ]

        for world_index, world_chunk in enumerate(world_chunks, start=1):
            for cast in cast_registry:
                characters = cast.get("character_ids", [])
                character_chunks = [
                    characters[i : i + max(1, max_characters_per_batch)]
                    for i in range(0, len(characters), max(1, max_characters_per_batch))
                ] or [[]]

                for char_index, char_chunk in enumerate(character_chunks, start=1):
                    lane_slice = storyline_lanes[:8]
                    batches.append(
                        {
                            "batch_id": f"generation_batch_w{world_index}_c{cast.get('cast_id')}_{char_index}",
                            "world_ids": [world["world_id"] for world in world_chunk],
                            "cast_id": cast.get("cast_id"),
                            "character_ids": char_chunk,
                            "lane_ids": [lane["lane_id"] for lane in lane_slice],
                            "batch_goal": "Generate or revise this partition while preserving continuity links.",
                        }
                    )

        return batches

    def _collision_risk_flags(
        self,
        *,
        world_registry: List[Dict[str, Any]],
        cast_registry: List[Dict[str, Any]],
        storyline_lanes: List[Dict[str, Any]],
        pressure_report: Dict[str, Any],
    ) -> List[str]:
        flags: List[str] = []

        if pressure_report.get("pressure_level") == "high":
            flags.append("high scaling pressure; use partitioned generation batches")

        if len(world_registry) > 6:
            flags.append("many worlds active; world-rule contradictions become more likely")

        total_characters = pressure_report.get("total_character_count", 0)
        if total_characters > 40:
            flags.append("large cast active; character voice and relationship memory must be batched")

        if len(storyline_lanes) > 20:
            flags.append("many storyline lanes active; payoff tracking must be strict")

        return flags

    def _recommendations(
        self,
        *,
        pressure_report: Dict[str, Any],
        risk_flags: List[str],
        batch_plan: List[Dict[str, Any]],
    ) -> List[str]:
        recommendations = [
            "Use generation batches instead of generating all worlds/casts at once.",
            "Keep world rules, cast state, and storyline lanes in separate continuity partitions.",
            "Merge outputs only after validating cross-world and cross-cast continuity.",
        ]

        if risk_flags:
            recommendations.append("Resolve collision risk flags before final long-form generation.")

        if len(batch_plan) > 1:
            recommendations.append("Run each batch independently, then reconcile shared hooks and payoffs.")

        if pressure_report.get("pressure_level") == "low":
            recommendations.append("Scaling pressure is low enough for a single-pass generation attempt.")

        return self._unique(recommendations)

    def _warnings(
        self,
        *,
        world_registry: List[Dict[str, Any]],
        cast_registry: List[Dict[str, Any]],
        storyline_lanes: List[Dict[str, Any]],
    ) -> List[str]:
        warnings: List[str] = []

        if not world_registry:
            warnings.append("No world registry entries created.")

        if not cast_registry:
            warnings.append("No cast registry entries created.")

        if not storyline_lanes:
            warnings.append("No storyline lanes created.")

        return warnings

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

    def _unique_dicts(self, values: List[Dict[str, Any]], *, key: str) -> List[Dict[str, Any]]:
        result = []
        seen = set()
        for value in values:
            marker = value.get(key) or str(value)
            if marker and marker not in seen:
                seen.add(marker)
                result.append(value)
        return result

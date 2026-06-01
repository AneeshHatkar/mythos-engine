from __future__ import annotations

from typing import Any, Dict, List

from backend.app.schemas.story_generation import (
    FormatAdaptationPlan,
    GeneratedChapter,
    LongFormContinuationAnchor,
    PlotOutline,
    SeriesEpisodeStructure,
    SeriesSeasonFormatPackage,
)


class SeriesSeasonFormatter:
    """Formats story material into series/season structure.

    Locked Chunk 5.28. This turns story material into a TV/streaming-season
    package with episode cards, cold opens, A/B/C plots, act breaks,
    season arc carryover, recurring dynamics, and cliffhangers.
    """

    engine_name = "story_generation.series_season_formatter"

    def format_series_or_season(
        self,
        *,
        source_id: str,
        series_title: str | None = None,
        season_number: int = 1,
        episode_structures: List[SeriesEpisodeStructure] | None = None,
        format_plan: FormatAdaptationPlan | None = None,
        plot_outline: PlotOutline | None = None,
        chapters: List[GeneratedChapter] | None = None,
        continuation_anchor: LongFormContinuationAnchor | None = None,
        story_context: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        episode_structures = episode_structures or []
        chapters = chapters or []
        story_context = story_context or {}

        title = self._series_title(
            series_title=series_title,
            plot_outline=plot_outline,
            story_context=story_context,
        )
        episode_cards = self._episode_cards(
            episode_structures=episode_structures,
            chapters=chapters,
            plot_outline=plot_outline,
            continuation_anchor=continuation_anchor,
        )
        plot_lanes = self._plot_lanes(
            episode_structures=episode_structures,
            plot_outline=plot_outline,
            continuation_anchor=continuation_anchor,
        )
        act_breaks = self._act_breaks(episode_structures=episode_structures, episode_cards=episode_cards)
        season_arc_carryover = self._season_arc_carryover(
            episode_structures=episode_structures,
            plot_outline=plot_outline,
            continuation_anchor=continuation_anchor,
        )
        recurring_character_dynamics = self._recurring_character_dynamics(
            episode_structures=episode_structures,
            plot_outline=plot_outline,
            chapters=chapters,
            continuation_anchor=continuation_anchor,
        )
        cliffhanger_registry = self._cliffhanger_registry(
            episode_structures=episode_structures,
            episode_cards=episode_cards,
            continuation_anchor=continuation_anchor,
        )
        season_arc_summary = self._season_arc_summary(
            plot_outline=plot_outline,
            episode_cards=episode_cards,
            season_arc_carryover=season_arc_carryover,
            cliffhanger_registry=cliffhanger_registry,
        )
        season_premise = self._season_premise(
            plot_outline=plot_outline,
            story_context=story_context,
            season_arc_summary=season_arc_summary,
        )

        formatted_text = self._formatted_text(
            series_title=title,
            season_number=season_number,
            season_premise=season_premise,
            season_arc_summary=season_arc_summary,
            episode_cards=episode_cards,
            plot_lanes=plot_lanes,
            act_breaks=act_breaks,
            recurring_character_dynamics=recurring_character_dynamics,
            cliffhanger_registry=cliffhanger_registry,
        )

        package = SeriesSeasonFormatPackage(
            series_package_id=f"series_season_format_{source_id}_s{season_number:02d}",
            source_id=source_id,
            target_format="series_season",
            series_title=title,
            season_number=season_number,
            episode_count=len(episode_cards),
            season_premise=season_premise,
            season_arc_summary=season_arc_summary,
            episode_cards=episode_cards,
            act_breaks=act_breaks,
            plot_lanes=plot_lanes,
            recurring_character_dynamics=recurring_character_dynamics,
            season_arc_carryover=season_arc_carryover,
            cliffhanger_registry=cliffhanger_registry,
            formatted_text=formatted_text,
            export_payload=self._export_payload(
                source_id=source_id,
                series_title=title,
                season_number=season_number,
                formatted_text=formatted_text,
                episode_cards=episode_cards,
            ),
            warnings=self._warnings(
                episode_cards=episode_cards,
                plot_lanes=plot_lanes,
                season_arc_carryover=season_arc_carryover,
                format_plan=format_plan,
            ),
        )

        return {
            "success": True,
            "engine_name": self.engine_name,
            "series_season_format_package": package,
            "series_season_format_package_dict": package.model_dump(mode="json"),
            "handoff_to_next_engine": {
                "next_engine": "story_generation.game_interactive_scene_formatter",
                "payload_keys": [
                    "series_season_format_package",
                    "format_adaptation_plan",
                    "plot_outline",
                    "generated_chapters",
                    "continuation_anchor",
                    "story_context",
                ],
            },
        }

    def validate_series_package(self, *, package: SeriesSeasonFormatPackage) -> Dict[str, Any]:
        blockers: List[str] = []
        warnings: List[str] = []
        passed: List[str] = []

        if not package.series_package_id:
            blockers.append("series_package_id missing")
        else:
            passed.append("series_package_id_present")

        if package.series_title:
            passed.append("series_title_present")
        else:
            blockers.append("series title missing")

        if package.episode_cards:
            passed.append("episode_cards_present")
        else:
            blockers.append("episode cards missing")

        if package.plot_lanes:
            passed.append("plot_lanes_present")
        else:
            warnings.append("plot lanes missing")

        if package.season_arc_carryover:
            passed.append("season_arc_carryover_present")
        else:
            warnings.append("season arc carryover missing")

        if package.cliffhanger_registry:
            passed.append("cliffhanger_registry_present")
        else:
            warnings.append("cliffhanger registry missing")

        if package.formatted_text and len(package.formatted_text.strip()) >= 150:
            passed.append("formatted_text_present")
        else:
            blockers.append("formatted text missing or too short")

        if package.export_payload:
            passed.append("export_payload_present")
        else:
            warnings.append("export payload missing")

        if package.warnings:
            warnings.extend(package.warnings)

        return {
            "success": True,
            "engine_name": self.engine_name,
            "valid": not blockers,
            "blockers": blockers,
            "warnings": self._unique(warnings),
            "passed_checks": passed,
        }

    def summarize_series_package(self, *, package: SeriesSeasonFormatPackage) -> Dict[str, Any]:
        return {
            "success": True,
            "engine_name": self.engine_name,
            "summary": {
                "series_package_id": package.series_package_id,
                "source_id": package.source_id,
                "series_title": package.series_title,
                "season_number": package.season_number,
                "episode_count": package.episode_count,
                "plot_lane_count": len(package.plot_lanes),
                "act_break_count": len(package.act_breaks),
                "recurring_dynamic_count": len(package.recurring_character_dynamics),
                "season_arc_carryover_count": len(package.season_arc_carryover),
                "cliffhanger_count": len(package.cliffhanger_registry),
                "formatted_word_count": len(package.formatted_text.split()),
                "warning_count": len(package.warnings),
            },
        }

    def build_export_text(self, *, package: SeriesSeasonFormatPackage) -> Dict[str, Any]:
        return {
            "success": True,
            "engine_name": self.engine_name,
            "export_text": package.formatted_text,
            "export_metadata": {
                "series_package_id": package.series_package_id,
                "target_format": package.target_format,
                "series_title": package.series_title,
                "season_number": package.season_number,
                "episode_count": package.episode_count,
                "suggested_extension": ".md",
            },
        }

    def _series_title(
        self,
        *,
        series_title: str | None,
        plot_outline: PlotOutline | None,
        story_context: Dict[str, Any],
    ) -> str:
        if series_title:
            return series_title
        if story_context.get("series_title"):
            return str(story_context["series_title"])
        if plot_outline and plot_outline.title:
            return plot_outline.title
        return "Untitled Series"

    def _episode_cards(
        self,
        *,
        episode_structures: List[SeriesEpisodeStructure],
        chapters: List[GeneratedChapter],
        plot_outline: PlotOutline | None,
        continuation_anchor: LongFormContinuationAnchor | None,
    ) -> List[Dict[str, Any]]:
        cards: List[Dict[str, Any]] = []

        for structure in episode_structures:
            cards.append(
                {
                    "episode_card_id": f"episode_card_s{structure.season_number:02d}e{structure.episode_number:02d}",
                    "season_number": structure.season_number,
                    "episode_number": structure.episode_number,
                    "episode_title": structure.episode_title or f"Episode {structure.episode_number}",
                    "cold_open": structure.cold_open,
                    "act_count": len(structure.act_structure),
                    "plot_lanes": list(structure.plot_lanes.keys()),
                    "episode_cliffhanger": structure.episode_cliffhanger,
                    "open_loop_count": len(structure.open_loop_carryover),
                    "source": "series_episode_structure",
                }
            )

        if not cards:
            for index, chapter in enumerate(chapters, start=1):
                cards.append(
                    {
                        "episode_card_id": f"episode_card_chapter_{chapter.chapter_id}",
                        "season_number": 1,
                        "episode_number": index,
                        "episode_title": chapter.title or f"Episode {index}",
                        "cold_open": {
                            "description": chapter.next_chapter_hooks[0] if chapter.next_chapter_hooks else "Open on unresolved chapter pressure."
                        },
                        "act_count": 4,
                        "plot_lanes": ["A_plot", "B_plot", "C_plot"],
                        "episode_cliffhanger": chapter.next_chapter_hooks[0] if chapter.next_chapter_hooks else None,
                        "open_loop_count": len(chapter.open_loops),
                        "source": "generated_chapter",
                    }
                )

        if not cards and plot_outline:
            for index, scene in enumerate(plot_outline.scene_sequence[:8], start=1):
                cards.append(
                    {
                        "episode_card_id": f"episode_card_outline_{index:02d}",
                        "season_number": 1,
                        "episode_number": index,
                        "episode_title": f"Episode {index}: {scene.get('scene_id', 'Outline Beat')}",
                        "cold_open": {"description": scene.get("purpose", "Open on outline pressure.")},
                        "act_count": 4,
                        "plot_lanes": ["A_plot", "B_plot", "C_plot"],
                        "episode_cliffhanger": plot_outline.next_outline_hooks[0] if plot_outline.next_outline_hooks else None,
                        "open_loop_count": len(plot_outline.open_loops),
                        "source": "plot_outline",
                    }
                )

        if not cards and continuation_anchor:
            cards.append(
                {
                    "episode_card_id": f"episode_card_anchor_{continuation_anchor.chapter_id}",
                    "season_number": continuation_anchor.chapter_number,
                    "episode_number": 1,
                    "episode_title": f"Continuation after {continuation_anchor.chapter_id}",
                    "cold_open": {
                        "description": continuation_anchor.next_chapter_hooks[0]
                        if continuation_anchor.next_chapter_hooks
                        else "Open on continuation pressure."
                    },
                    "act_count": 4,
                    "plot_lanes": ["A_plot", "B_plot", "C_plot"],
                    "episode_cliffhanger": continuation_anchor.next_chapter_hooks[0]
                    if continuation_anchor.next_chapter_hooks
                    else None,
                    "open_loop_count": len(continuation_anchor.open_loops),
                    "source": "continuation_anchor",
                }
            )

        return cards

    def _plot_lanes(
        self,
        *,
        episode_structures: List[SeriesEpisodeStructure],
        plot_outline: PlotOutline | None,
        continuation_anchor: LongFormContinuationAnchor | None,
    ) -> Dict[str, List[Dict[str, Any]]]:
        lanes: Dict[str, List[Dict[str, Any]]] = {
            "A_plot": [],
            "B_plot": [],
            "C_plot": [],
        }

        for structure in episode_structures:
            for lane_name, beats in structure.plot_lanes.items():
                lanes.setdefault(lane_name, []).extend(beats)

        if plot_outline:
            for causal in plot_outline.causal_threads:
                lanes["A_plot"].append(
                    {
                        "plot_beat_id": f"a_plot_{causal.get('causal_id')}",
                        "description": causal.get("description"),
                        "source_id": causal.get("causal_id"),
                    }
                )

            for relationship in plot_outline.relationship_arc_threads:
                lanes["B_plot"].append(
                    {
                        "plot_beat_id": f"b_plot_{relationship.get('relationship_id')}",
                        "description": relationship.get("description"),
                        "source_id": relationship.get("relationship_id"),
                    }
                )

            for secret in plot_outline.secret_threads:
                lanes["C_plot"].append(
                    {
                        "plot_beat_id": f"c_plot_{secret.get('secret_id')}",
                        "description": secret.get("description"),
                        "source_id": secret.get("secret_id"),
                    }
                )

        if continuation_anchor:
            for causal_id in continuation_anchor.active_causal_ids:
                lanes["A_plot"].append(
                    {
                        "plot_beat_id": f"a_plot_anchor_{causal_id}",
                        "description": f"Continue causal thread {causal_id}.",
                        "source_id": causal_id,
                    }
                )

            for relationship_id in continuation_anchor.active_relationship_ids:
                lanes["B_plot"].append(
                    {
                        "plot_beat_id": f"b_plot_anchor_{relationship_id}",
                        "description": f"Continue relationship pressure {relationship_id}.",
                        "source_id": relationship_id,
                    }
                )

            for secret_id in continuation_anchor.active_secret_ids:
                lanes["C_plot"].append(
                    {
                        "plot_beat_id": f"c_plot_anchor_{secret_id}",
                        "description": f"Continue secret pressure {secret_id}.",
                        "source_id": secret_id,
                    }
                )

        return {lane: self._unique_dicts(beats, key="plot_beat_id") for lane, beats in lanes.items()}

    def _act_breaks(
        self,
        *,
        episode_structures: List[SeriesEpisodeStructure],
        episode_cards: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        breaks: List[Dict[str, Any]] = []

        for structure in episode_structures:
            for act in structure.act_structure:
                breaks.append(
                    {
                        "act_break_id": f"act_break_s{structure.season_number:02d}e{structure.episode_number:02d}_{act.get('act_number')}",
                        "episode_number": structure.episode_number,
                        "act_number": act.get("act_number"),
                        "description": act.get("description"),
                        "break_hook": act.get("act_break_hook"),
                    }
                )

        if not breaks:
            for card in episode_cards:
                for act_number in range(1, int(card.get("act_count", 4)) + 1):
                    breaks.append(
                        {
                            "act_break_id": f"act_break_e{card.get('episode_number')}_{act_number}",
                            "episode_number": card.get("episode_number"),
                            "act_number": act_number,
                            "description": f"Episode {card.get('episode_number')} act {act_number} turn.",
                            "break_hook": card.get("episode_cliffhanger") if act_number == card.get("act_count", 4) else "Increase episode pressure.",
                        }
                    )

        return breaks

    def _season_arc_carryover(
        self,
        *,
        episode_structures: List[SeriesEpisodeStructure],
        plot_outline: PlotOutline | None,
        continuation_anchor: LongFormContinuationAnchor | None,
    ) -> List[Dict[str, Any]]:
        carryover: List[Dict[str, Any]] = []

        for structure in episode_structures:
            carryover.extend(structure.season_arc_links)

        if plot_outline:
            for payoff in plot_outline.payoff_setups:
                carryover.append(
                    {
                        "carryover_id": f"season_payoff_{payoff.get('payoff_id')}",
                        "carryover_type": payoff.get("payoff_type"),
                        "description": payoff.get("description"),
                        "source_id": payoff.get("payoff_id"),
                    }
                )

            for loop in plot_outline.open_loops:
                carryover.append(
                    {
                        "carryover_id": f"season_loop_{loop.get('loop_id')}",
                        "carryover_type": loop.get("loop_type", "open_loop"),
                        "description": loop.get("description"),
                        "source_id": loop.get("loop_id"),
                    }
                )

        if continuation_anchor:
            for loop in continuation_anchor.open_loops:
                carryover.append(
                    {
                        "carryover_id": f"season_anchor_loop_{loop.get('loop_id')}",
                        "carryover_type": loop.get("loop_type", "open_loop"),
                        "description": loop.get("description"),
                        "source_id": loop.get("loop_id"),
                    }
                )

        return self._unique_dicts(carryover, key="carryover_id")

    def _recurring_character_dynamics(
        self,
        *,
        episode_structures: List[SeriesEpisodeStructure],
        plot_outline: PlotOutline | None,
        chapters: List[GeneratedChapter],
        continuation_anchor: LongFormContinuationAnchor | None,
    ) -> List[Dict[str, Any]]:
        dynamics: List[Dict[str, Any]] = []

        for structure in episode_structures:
            for item in structure.character_continuity:
                character_id = item.get("character_id")
                if character_id:
                    dynamics.append(
                        {
                            "dynamic_id": f"recurring_character_{character_id}",
                            "character_id": character_id,
                            "dynamic_type": "character_continuity",
                            "description": item.get("continuity_rule"),
                        }
                    )

            for item in structure.relationship_continuity:
                relationship_id = item.get("relationship_id")
                if relationship_id:
                    dynamics.append(
                        {
                            "dynamic_id": f"recurring_relationship_{relationship_id}",
                            "relationship_id": relationship_id,
                            "dynamic_type": "relationship_continuity",
                            "description": item.get("continuity_rule"),
                        }
                    )

        if plot_outline:
            for thread in plot_outline.character_arc_threads:
                dynamics.append(
                    {
                        "dynamic_id": f"recurring_character_{thread.get('character_id')}",
                        "character_id": thread.get("character_id"),
                        "dynamic_type": "character_arc",
                        "description": thread.get("description"),
                    }
                )

            for thread in plot_outline.relationship_arc_threads:
                dynamics.append(
                    {
                        "dynamic_id": f"recurring_relationship_{thread.get('relationship_id')}",
                        "relationship_id": thread.get("relationship_id"),
                        "dynamic_type": "relationship_arc",
                        "description": thread.get("description"),
                    }
                )

        for chapter in chapters:
            for character_id in chapter.used_character_ids:
                dynamics.append(
                    {
                        "dynamic_id": f"recurring_character_{character_id}",
                        "character_id": character_id,
                        "dynamic_type": "chapter_character_usage",
                        "description": f"{character_id} carries chapter state into recurring series dynamics.",
                    }
                )

        if continuation_anchor:
            for character_id in continuation_anchor.active_character_ids:
                dynamics.append(
                    {
                        "dynamic_id": f"recurring_character_{character_id}",
                        "character_id": character_id,
                        "dynamic_type": "anchor_character_state",
                        "description": f"{character_id} remains active after {continuation_anchor.chapter_id}.",
                    }
                )

        return self._unique_dicts(dynamics, key="dynamic_id")

    def _cliffhanger_registry(
        self,
        *,
        episode_structures: List[SeriesEpisodeStructure],
        episode_cards: List[Dict[str, Any]],
        continuation_anchor: LongFormContinuationAnchor | None,
    ) -> List[Dict[str, Any]]:
        registry: List[Dict[str, Any]] = []

        for structure in episode_structures:
            if structure.episode_cliffhanger:
                registry.append(
                    {
                        "cliffhanger_id": f"cliffhanger_s{structure.season_number:02d}e{structure.episode_number:02d}",
                        "episode_number": structure.episode_number,
                        "description": structure.episode_cliffhanger,
                        "source": "episode_structure",
                    }
                )

        for card in episode_cards:
            if card.get("episode_cliffhanger"):
                registry.append(
                    {
                        "cliffhanger_id": f"cliffhanger_card_e{card.get('episode_number')}",
                        "episode_number": card.get("episode_number"),
                        "description": card.get("episode_cliffhanger"),
                        "source": card.get("source"),
                    }
                )

        if continuation_anchor:
            for index, hook in enumerate(continuation_anchor.next_chapter_hooks, start=1):
                registry.append(
                    {
                        "cliffhanger_id": f"cliffhanger_anchor_{index}",
                        "episode_number": None,
                        "description": hook,
                        "source": "continuation_anchor",
                    }
                )

        return self._unique_dicts(registry, key="cliffhanger_id")

    def _season_arc_summary(
        self,
        *,
        plot_outline: PlotOutline | None,
        episode_cards: List[Dict[str, Any]],
        season_arc_carryover: List[Dict[str, Any]],
        cliffhanger_registry: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        return {
            "episode_count": len(episode_cards),
            "central_premise": plot_outline.premise if plot_outline else None,
            "active_carryover_count": len(season_arc_carryover),
            "cliffhanger_count": len(cliffhanger_registry),
            "required_payoff_count": len(plot_outline.payoff_setups) if plot_outline else 0,
            "season_goal": "Escalate the core premise through episode-level turns while preserving long-form continuity.",
        }

    def _season_premise(
        self,
        *,
        plot_outline: PlotOutline | None,
        story_context: Dict[str, Any],
        season_arc_summary: Dict[str, Any],
    ) -> str:
        if story_context.get("season_premise"):
            return str(story_context["season_premise"])
        if plot_outline and plot_outline.premise:
            return plot_outline.premise
        return season_arc_summary.get("season_goal", "A season arc escalates through connected episodes.")

    def _formatted_text(
        self,
        *,
        series_title: str,
        season_number: int,
        season_premise: str,
        season_arc_summary: Dict[str, Any],
        episode_cards: List[Dict[str, Any]],
        plot_lanes: Dict[str, List[Dict[str, Any]]],
        act_breaks: List[Dict[str, Any]],
        recurring_character_dynamics: List[Dict[str, Any]],
        cliffhanger_registry: List[Dict[str, Any]],
    ) -> str:
        lines = [
            f"# {series_title}",
            "",
            f"## Season {season_number}",
            "",
            "### Season Premise",
            season_premise,
            "",
            "### Season Arc Summary",
            f"- Episode count: {season_arc_summary.get('episode_count')}",
            f"- Active carryovers: {season_arc_summary.get('active_carryover_count')}",
            f"- Cliffhangers: {season_arc_summary.get('cliffhanger_count')}",
            "",
            "## Episode Cards",
        ]

        for card in episode_cards:
            lines.extend(
                [
                    f"### S{card.get('season_number', season_number):02d}E{card.get('episode_number', 1):02d}: {card.get('episode_title')}",
                    f"- Cold open: {card.get('cold_open', {}).get('description')}",
                    f"- Act count: {card.get('act_count')}",
                    f"- Cliffhanger: {card.get('episode_cliffhanger')}",
                    "",
                ]
            )

        lines.append("## Plot Lanes")
        for lane_name, beats in plot_lanes.items():
            lines.append(f"### {lane_name}")
            for beat in beats:
                lines.append(f"- {beat.get('description')}")
            lines.append("")

        lines.append("## Act Breaks")
        for item in act_breaks[:20]:
            lines.append(f"- E{item.get('episode_number')} Act {item.get('act_number')}: {item.get('break_hook')}")

        lines.append("")
        lines.append("## Recurring Dynamics")
        for item in recurring_character_dynamics[:20]:
            lines.append(f"- {item.get('dynamic_type')}: {item.get('description')}")

        lines.append("")
        lines.append("## Cliffhanger Registry")
        for item in cliffhanger_registry:
            lines.append(f"- {item.get('cliffhanger_id')}: {item.get('description')}")

        return "\n".join(lines).strip()

    def _export_payload(
        self,
        *,
        source_id: str,
        series_title: str,
        season_number: int,
        formatted_text: str,
        episode_cards: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        return {
            "export_id": f"export_series_{source_id}_s{season_number:02d}",
            "source_id": source_id,
            "target_format": "series_season",
            "series_title": series_title,
            "season_number": season_number,
            "episode_count": len(episode_cards),
            "text": formatted_text,
            "suggested_extension": ".md",
        }

    def _warnings(
        self,
        *,
        episode_cards: List[Dict[str, Any]],
        plot_lanes: Dict[str, List[Dict[str, Any]]],
        season_arc_carryover: List[Dict[str, Any]],
        format_plan: FormatAdaptationPlan | None,
    ) -> List[str]:
        warnings: List[str] = []

        if not episode_cards:
            warnings.append("No episode cards were generated.")

        if not any(plot_lanes.values()):
            warnings.append("Plot lanes are empty; season may feel disconnected.")

        if not season_arc_carryover:
            warnings.append("No season arc carryover found.")

        if format_plan and format_plan.target_format not in {"series_episode", "chapter", "movie", "screenplay"}:
            warnings.append(f"Format plan target is {format_plan.target_format}; applying series formatter carefully.")

        return self._unique(warnings)

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

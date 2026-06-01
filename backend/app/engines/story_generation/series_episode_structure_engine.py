from __future__ import annotations

from typing import Any, Dict, List

from backend.app.schemas.story_generation import (
    FormatAdaptationPlan,
    GeneratedChapter,
    LongFormContinuationAnchor,
    SeriesEpisodeStructure,
)


class SeriesEpisodeStructureEngine:
    """Builds TV/streaming series episode structure.

    This engine adapts chapter/story material into episode logic:
    cold open, act breaks, A/B/C plot lanes, season arc links, open loops,
    cliffhanger, and continuity tracking.
    """

    engine_name = "story_generation.series_episode_structure_engine"

    def build_episode_structure(
        self,
        *,
        source_id: str,
        format_plan: FormatAdaptationPlan,
        chapter: GeneratedChapter | None = None,
        continuation_anchor: LongFormContinuationAnchor | None = None,
        episode_number: int = 1,
        season_number: int = 1,
        episode_title: str | None = None,
        story_context: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        story_context = story_context or {}

        title = episode_title or self._episode_title(
            episode_number=episode_number,
            chapter=chapter,
            continuation_anchor=continuation_anchor,
        )

        cold_open = self._cold_open(
            chapter=chapter,
            continuation_anchor=continuation_anchor,
            format_plan=format_plan,
        )
        act_structure = self._act_structure(
            chapter=chapter,
            continuation_anchor=continuation_anchor,
            format_plan=format_plan,
        )
        plot_lanes = self._plot_lanes(
            chapter=chapter,
            continuation_anchor=continuation_anchor,
            story_context=story_context,
        )
        season_arc_links = self._season_arc_links(
            chapter=chapter,
            continuation_anchor=continuation_anchor,
            story_context=story_context,
        )

        structure = SeriesEpisodeStructure(
            episode_structure_id=f"episode_structure_s{season_number:02d}e{episode_number:02d}_{source_id}",
            source_id=source_id,
            episode_number=episode_number,
            season_number=season_number,
            episode_title=title,
            cold_open=cold_open,
            act_structure=act_structure,
            plot_lanes=plot_lanes,
            season_arc_links=season_arc_links,
            character_continuity=self._character_continuity(chapter=chapter, continuation_anchor=continuation_anchor),
            relationship_continuity=self._relationship_continuity(chapter=chapter, continuation_anchor=continuation_anchor),
            open_loop_carryover=self._open_loop_carryover(chapter=chapter, continuation_anchor=continuation_anchor),
            episode_cliffhanger=self._episode_cliffhanger(chapter=chapter, continuation_anchor=continuation_anchor),
            pacing_notes=self._pacing_notes(format_plan=format_plan, act_structure=act_structure),
            warnings=self._warnings(format_plan=format_plan, chapter=chapter, continuation_anchor=continuation_anchor),
        )

        return {
            "success": True,
            "engine_name": self.engine_name,
            "series_episode_structure": structure,
            "series_episode_structure_dict": structure.model_dump(mode="json"),
            "handoff_to_next_engine": {
                "next_engine": "story_generation.chapter_expansion_engine",
                "payload_keys": [
                    "series_episode_structure",
                    "format_adaptation_plan",
                    "generated_chapter",
                    "continuation_anchor",
                    "story_context",
                ],
            },
        }

    def build_episode_outline_text(self, *, structure: SeriesEpisodeStructure) -> Dict[str, Any]:
        lines = [
            f"# S{structure.season_number:02d}E{structure.episode_number:02d}: {structure.episode_title}",
            "",
            "## Cold Open",
            structure.cold_open.get("description", "Open with immediate pressure."),
            "",
            "## Acts",
        ]

        for act in structure.act_structure:
            lines.append(f"### Act {act.get('act_number')}: {act.get('act_purpose')}")
            lines.append(act.get("description", ""))

        lines.append("")
        lines.append("## Plot Lanes")
        for lane, beats in structure.plot_lanes.items():
            lines.append(f"### {lane}")
            for beat in beats:
                lines.append(f"- {beat.get('description')}")

        if structure.episode_cliffhanger:
            lines.append("")
            lines.append("## Cliffhanger")
            lines.append(structure.episode_cliffhanger)

        return {
            "success": True,
            "engine_name": self.engine_name,
            "episode_outline_text": "\n".join(lines),
        }

    def validate_episode_structure(self, *, structure: SeriesEpisodeStructure) -> Dict[str, Any]:
        blockers: List[str] = []
        warnings: List[str] = []
        passed: List[str] = []

        if not structure.episode_structure_id:
            blockers.append("episode_structure_id missing")
        else:
            passed.append("episode_structure_id_present")

        if structure.cold_open:
            passed.append("cold_open_present")
        else:
            blockers.append("cold open missing")

        if len(structure.act_structure) >= 3:
            passed.append("act_structure_present")
        else:
            blockers.append("episode needs at least three acts")

        if structure.plot_lanes:
            passed.append("plot_lanes_present")
        else:
            warnings.append("plot lanes missing")

        if structure.episode_cliffhanger:
            passed.append("episode_cliffhanger_present")
        else:
            warnings.append("episode cliffhanger missing")

        if structure.character_continuity:
            passed.append("character_continuity_present")
        else:
            warnings.append("character continuity missing")

        if structure.open_loop_carryover:
            passed.append("open_loop_carryover_present")
        else:
            warnings.append("open loop carryover missing")

        if structure.warnings:
            warnings.extend(structure.warnings)

        return {
            "success": True,
            "engine_name": self.engine_name,
            "valid": not blockers,
            "blockers": blockers,
            "warnings": self._unique(warnings),
            "passed_checks": passed,
        }

    def summarize_episode_structure(self, *, structure: SeriesEpisodeStructure) -> Dict[str, Any]:
        return {
            "success": True,
            "engine_name": self.engine_name,
            "summary": {
                "episode_structure_id": structure.episode_structure_id,
                "episode_number": structure.episode_number,
                "season_number": structure.season_number,
                "episode_title": structure.episode_title,
                "act_count": len(structure.act_structure),
                "plot_lane_count": len(structure.plot_lanes),
                "season_arc_link_count": len(structure.season_arc_links),
                "character_continuity_count": len(structure.character_continuity),
                "relationship_continuity_count": len(structure.relationship_continuity),
                "open_loop_carryover_count": len(structure.open_loop_carryover),
                "has_cliffhanger": bool(structure.episode_cliffhanger),
                "warning_count": len(structure.warnings),
            },
        }

    def _episode_title(
        self,
        *,
        episode_number: int,
        chapter: GeneratedChapter | None,
        continuation_anchor: LongFormContinuationAnchor | None,
    ) -> str:
        if chapter and chapter.title:
            return chapter.title.replace("Chapter", "Episode")
        if continuation_anchor and continuation_anchor.next_chapter_hooks:
            return f"Episode {episode_number}: {continuation_anchor.next_chapter_hooks[0][:48]}"
        return f"Episode {episode_number}"

    def _cold_open(
        self,
        *,
        chapter: GeneratedChapter | None,
        continuation_anchor: LongFormContinuationAnchor | None,
        format_plan: FormatAdaptationPlan,
    ) -> Dict[str, Any]:
        hook = None
        if continuation_anchor and continuation_anchor.next_chapter_hooks:
            hook = continuation_anchor.next_chapter_hooks[0]
        elif chapter and chapter.next_chapter_hooks:
            hook = chapter.next_chapter_hooks[0]

        return {
            "cold_open_id": "cold_open_001",
            "description": hook or "Open on the most unstable unresolved pressure.",
            "purpose": "Create immediate question, mood, and continuation pull.",
            "uses_open_loop": bool(hook),
            "format_rule": format_plan.pacing_rules.get("shape"),
        }

    def _act_structure(
        self,
        *,
        chapter: GeneratedChapter | None,
        continuation_anchor: LongFormContinuationAnchor | None,
        format_plan: FormatAdaptationPlan,
    ) -> List[Dict[str, Any]]:
        act_count = format_plan.pacing_rules.get("act_breaks", 4)
        if not isinstance(act_count, int) or act_count < 3:
            act_count = 4

        hooks = []
        if continuation_anchor:
            hooks.extend(continuation_anchor.next_chapter_hooks)
        if chapter:
            hooks.extend(chapter.next_chapter_hooks)

        acts = []
        purposes = [
            "Re-establish conflict and character pressure.",
            "Complicate the main goal through secret or relationship pressure.",
            "Force a choice that changes the episode direction.",
            "Pay off a consequence and open the next problem.",
            "Escalate season-level stakes.",
        ]

        for index in range(1, act_count + 1):
            hook = hooks[(index - 1) % len(hooks)] if hooks else "unresolved pressure"
            acts.append(
                {
                    "act_number": index,
                    "act_purpose": purposes[min(index - 1, len(purposes) - 1)],
                    "description": f"Act {index} turns around {hook}.",
                    "required_turn": index > 1,
                    "act_break_hook": hook if index < act_count else "episode cliffhanger",
                }
            )

        return acts

    def _plot_lanes(
        self,
        *,
        chapter: GeneratedChapter | None,
        continuation_anchor: LongFormContinuationAnchor | None,
        story_context: Dict[str, Any],
    ) -> Dict[str, List[Dict[str, Any]]]:
        lanes = {
            "A_plot": [],
            "B_plot": [],
            "C_plot": [],
        }

        main_causal = []
        if continuation_anchor:
            main_causal = continuation_anchor.active_causal_ids
        elif chapter:
            main_causal = chapter.used_causal_ids

        for causal_id in main_causal[:3]:
            lanes["A_plot"].append(
                {
                    "plot_beat_id": f"a_plot_{causal_id}",
                    "description": f"Main causal thread continues through {causal_id}.",
                    "source_id": causal_id,
                }
            )

        relationships = continuation_anchor.active_relationship_ids if continuation_anchor else (chapter.used_relationship_ids if chapter else [])
        for relationship_id in relationships[:3]:
            lanes["B_plot"].append(
                {
                    "plot_beat_id": f"b_plot_{relationship_id}",
                    "description": f"Relationship pressure develops for {relationship_id}.",
                    "source_id": relationship_id,
                }
            )

        secrets = continuation_anchor.active_secret_ids if continuation_anchor else (chapter.used_secret_ids if chapter else [])
        for secret_id in secrets[:3]:
            lanes["C_plot"].append(
                {
                    "plot_beat_id": f"c_plot_{secret_id}",
                    "description": f"Secret pressure remains active around {secret_id}.",
                    "source_id": secret_id,
                }
            )

        if not lanes["A_plot"]:
            lanes["A_plot"].append(
                {
                    "plot_beat_id": "a_plot_default",
                    "description": "Main episode objective needs a causal engine thread.",
                    "source_id": None,
                }
            )

        return lanes

    def _season_arc_links(
        self,
        *,
        chapter: GeneratedChapter | None,
        continuation_anchor: LongFormContinuationAnchor | None,
        story_context: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        links: List[Dict[str, Any]] = []

        for item in story_context.get("season_arc_links", []):
            if isinstance(item, dict):
                links.append(dict(item))

        if continuation_anchor:
            for causal_id in continuation_anchor.active_causal_ids[:3]:
                links.append(
                    {
                        "season_arc_link_id": f"season_arc_{causal_id}",
                        "source_id": causal_id,
                        "arc_type": "causal_thread",
                        "description": f"Season arc must continue causal thread {causal_id}.",
                    }
                )

            for secret_id in continuation_anchor.active_secret_ids[:3]:
                links.append(
                    {
                        "season_arc_link_id": f"season_arc_{secret_id}",
                        "source_id": secret_id,
                        "arc_type": "mystery_or_secret",
                        "description": f"Season arc must manage reveal timing for {secret_id}.",
                    }
                )

        return self._unique_dicts(links, key="season_arc_link_id")

    def _character_continuity(
        self,
        *,
        chapter: GeneratedChapter | None,
        continuation_anchor: LongFormContinuationAnchor | None,
    ) -> List[Dict[str, Any]]:
        character_ids = continuation_anchor.active_character_ids if continuation_anchor else (chapter.used_character_ids if chapter else [])

        return [
            {
                "character_id": character_id,
                "continuity_rule": f"Carry forward {character_id}'s latest emotional, goal, and knowledge state.",
            }
            for character_id in character_ids
        ]

    def _relationship_continuity(
        self,
        *,
        chapter: GeneratedChapter | None,
        continuation_anchor: LongFormContinuationAnchor | None,
    ) -> List[Dict[str, Any]]:
        relationship_ids = continuation_anchor.active_relationship_ids if continuation_anchor else (chapter.used_relationship_ids if chapter else [])

        return [
            {
                "relationship_id": relationship_id,
                "continuity_rule": f"Carry forward trust, resentment, betrayal risk, and repair potential for {relationship_id}.",
            }
            for relationship_id in relationship_ids
        ]

    def _open_loop_carryover(
        self,
        *,
        chapter: GeneratedChapter | None,
        continuation_anchor: LongFormContinuationAnchor | None,
    ) -> List[Dict[str, Any]]:
        if continuation_anchor:
            return continuation_anchor.open_loops
        if chapter:
            return chapter.open_loops
        return []

    def _episode_cliffhanger(
        self,
        *,
        chapter: GeneratedChapter | None,
        continuation_anchor: LongFormContinuationAnchor | None,
    ) -> str | None:
        if continuation_anchor and continuation_anchor.next_chapter_hooks:
            return continuation_anchor.next_chapter_hooks[0]
        if chapter and chapter.next_chapter_hooks:
            return chapter.next_chapter_hooks[0]
        return None

    def _pacing_notes(self, *, format_plan: FormatAdaptationPlan, act_structure: List[Dict[str, Any]]) -> List[str]:
        return [
            f"Use pacing shape: {format_plan.pacing_rules.get('shape')}.",
            f"Episode contains {len(act_structure)} acts.",
            "Each act should end with a turn, discovery, reversal, or pressure increase.",
        ]

    def _warnings(
        self,
        *,
        format_plan: FormatAdaptationPlan,
        chapter: GeneratedChapter | None,
        continuation_anchor: LongFormContinuationAnchor | None,
    ) -> List[str]:
        warnings: List[str] = []

        if format_plan.target_format not in {"series_episode", "movie", "screenplay", "chapter", "scene"}:
            warnings.append(f"Target format {format_plan.target_format} is not specifically episodic; applying episode structure carefully.")

        if chapter and chapter.quality_summary.get("failed_scene_count", 0) > 0:
            warnings.append("Source chapter has failed scene quality reports.")

        if continuation_anchor and not continuation_anchor.open_loops:
            warnings.append("No open loops found; episode continuation may feel weak.")

        return warnings

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
            if marker not in seen:
                seen.add(marker)
                result.append(value)
        return result

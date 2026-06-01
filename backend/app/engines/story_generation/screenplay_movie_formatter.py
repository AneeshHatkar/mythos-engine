from __future__ import annotations

from typing import Any, Dict, List

from backend.app.schemas.story_generation import (
    AssembledScene,
    FormatAdaptationPlan,
    GeneratedChapter,
    PlotOutline,
    ScreenplayMovieFormatPackage,
)


class ScreenplayMovieFormatter:
    """Formats story material for screenplay/movie outputs.

    This is locked Chunk 5.27. It converts story/chapter/outline material into
    performable cinematic structure: scene headings, action blocks, dialogue
    blocks, visual sequence beats, motifs, and export-ready text.
    """

    engine_name = "story_generation.screenplay_movie_formatter"

    UNFILMABLE_MARKERS = [
        "felt like",
        "realized deep down",
        "knew in his heart",
        "thought about",
        "remembered internally",
        "in her soul",
        "understood everything",
    ]

    CAMERA_MARKERS = [
        "camera pans",
        "camera zooms",
        "we see",
        "close-up",
        "dolly shot",
    ]

    def format_for_screenplay_or_movie(
        self,
        *,
        source_id: str,
        target_format: str,
        format_plan: FormatAdaptationPlan | None = None,
        plot_outline: PlotOutline | None = None,
        chapter: GeneratedChapter | None = None,
        assembled_scenes: List[AssembledScene] | None = None,
        story_context: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        assembled_scenes = assembled_scenes or []
        story_context = story_context or {}

        normalized_format = self._normalize_format(target_format)
        title = self._title(
            plot_outline=plot_outline,
            chapter=chapter,
            story_context=story_context,
            normalized_format=normalized_format,
        )
        logline = self._logline(plot_outline=plot_outline, chapter=chapter, story_context=story_context)

        scene_units = self._scene_units(
            assembled_scenes=assembled_scenes,
            chapter=chapter,
            plot_outline=plot_outline,
        )

        scene_headings = self._scene_headings(scene_units=scene_units)
        action_blocks = self._action_blocks(scene_units=scene_units, normalized_format=normalized_format)
        dialogue_blocks = self._dialogue_blocks(scene_units=scene_units, chapter=chapter)
        movie_sequence_beats = self._movie_sequence_beats(
            scene_units=scene_units,
            plot_outline=plot_outline,
            normalized_format=normalized_format,
        )
        visual_motifs = self._visual_motifs(
            plot_outline=plot_outline,
            chapter=chapter,
            scene_units=scene_units,
        )
        continuity_requirements = self._continuity_requirements(
            format_plan=format_plan,
            plot_outline=plot_outline,
            chapter=chapter,
        )

        formatted_text = self._formatted_text(
            title=title,
            logline=logline,
            normalized_format=normalized_format,
            scene_headings=scene_headings,
            action_blocks=action_blocks,
            dialogue_blocks=dialogue_blocks,
            movie_sequence_beats=movie_sequence_beats,
        )

        package = ScreenplayMovieFormatPackage(
            format_package_id=f"screenplay_movie_format_{source_id}_{normalized_format}",
            source_id=source_id,
            target_format=normalized_format,
            title=title,
            logline=logline,
            scene_headings=scene_headings,
            action_blocks=action_blocks,
            dialogue_blocks=dialogue_blocks,
            movie_sequence_beats=movie_sequence_beats,
            visual_motifs=visual_motifs,
            continuity_requirements=continuity_requirements,
            formatted_text=formatted_text,
            export_payload=self._export_payload(
                source_id=source_id,
                normalized_format=normalized_format,
                title=title,
                formatted_text=formatted_text,
                scene_headings=scene_headings,
                movie_sequence_beats=movie_sequence_beats,
            ),
            warnings=self._warnings(
                formatted_text=formatted_text,
                scene_units=scene_units,
                normalized_format=normalized_format,
                format_plan=format_plan,
            ),
        )

        return {
            "success": True,
            "engine_name": self.engine_name,
            "screenplay_movie_format_package": package,
            "screenplay_movie_format_package_dict": package.model_dump(mode="json"),
            "handoff_to_next_engine": {
                "next_engine": "story_generation.series_season_formatter",
                "payload_keys": [
                    "screenplay_movie_format_package",
                    "format_adaptation_plan",
                    "plot_outline",
                    "generated_chapter",
                    "story_context",
                ],
            },
        }

    def validate_format_package(self, *, package: ScreenplayMovieFormatPackage) -> Dict[str, Any]:
        blockers: List[str] = []
        warnings: List[str] = []
        passed: List[str] = []

        if not package.format_package_id:
            blockers.append("format_package_id missing")
        else:
            passed.append("format_package_id_present")

        if package.target_format in {"screenplay", "movie"}:
            passed.append("target_format_supported")
        else:
            blockers.append("target format must be screenplay or movie")

        if package.scene_headings:
            passed.append("scene_headings_present")
        else:
            blockers.append("scene headings missing")

        if package.action_blocks:
            passed.append("action_blocks_present")
        else:
            blockers.append("action blocks missing")

        if package.formatted_text and len(package.formatted_text.strip()) >= 120:
            passed.append("formatted_text_present")
        else:
            blockers.append("formatted text missing or too short")

        if package.continuity_requirements:
            passed.append("continuity_requirements_present")
        else:
            warnings.append("continuity requirements missing")

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

    def summarize_format_package(self, *, package: ScreenplayMovieFormatPackage) -> Dict[str, Any]:
        return {
            "success": True,
            "engine_name": self.engine_name,
            "summary": {
                "format_package_id": package.format_package_id,
                "source_id": package.source_id,
                "target_format": package.target_format,
                "title": package.title,
                "scene_heading_count": len(package.scene_headings),
                "action_block_count": len(package.action_blocks),
                "dialogue_block_count": len(package.dialogue_blocks),
                "movie_sequence_beat_count": len(package.movie_sequence_beats),
                "visual_motif_count": len(package.visual_motifs),
                "formatted_word_count": len(package.formatted_text.split()),
                "warning_count": len(package.warnings),
            },
        }

    def build_export_text(self, *, package: ScreenplayMovieFormatPackage) -> Dict[str, Any]:
        return {
            "success": True,
            "engine_name": self.engine_name,
            "export_text": package.formatted_text,
            "export_metadata": {
                "format_package_id": package.format_package_id,
                "target_format": package.target_format,
                "title": package.title,
                "scene_count": len(package.scene_headings),
                "warning_count": len(package.warnings),
            },
        }

    def _normalize_format(self, target_format: str) -> str:
        lowered = str(target_format).lower().strip()
        if lowered in {"film", "movie_sequence", "cinematic"}:
            return "movie"
        if lowered in {"script", "screenplay_scene"}:
            return "screenplay"
        if lowered not in {"screenplay", "movie"}:
            return "screenplay"
        return lowered

    def _title(
        self,
        *,
        plot_outline: PlotOutline | None,
        chapter: GeneratedChapter | None,
        story_context: Dict[str, Any],
        normalized_format: str,
    ) -> str:
        if story_context.get("title"):
            return str(story_context["title"])
        if plot_outline and plot_outline.title:
            return plot_outline.title
        if chapter and chapter.title:
            return chapter.title
        return "Untitled Screenplay" if normalized_format == "screenplay" else "Untitled Film Sequence"

    def _logline(
        self,
        *,
        plot_outline: PlotOutline | None,
        chapter: GeneratedChapter | None,
        story_context: Dict[str, Any],
    ) -> str:
        if story_context.get("logline"):
            return str(story_context["logline"])
        if plot_outline and plot_outline.premise:
            return plot_outline.premise
        if chapter and chapter.next_chapter_hooks:
            return f"A chapter turns on this unresolved hook: {chapter.next_chapter_hooks[0]}"
        return "A conflict escalates through visible choices and consequences."

    def _scene_units(
        self,
        *,
        assembled_scenes: List[AssembledScene],
        chapter: GeneratedChapter | None,
        plot_outline: PlotOutline | None,
    ) -> List[Dict[str, Any]]:
        units: List[Dict[str, Any]] = []

        for index, scene in enumerate(assembled_scenes, start=1):
            units.append(
                {
                    "scene_id": scene.scene_id,
                    "index": index,
                    "title": scene.title or scene.scene_id,
                    "text": scene.assembled_text,
                    "location": scene.continuity_trace.get("location_id") or self._infer_location(scene.title or scene.scene_id),
                    "time": "DAY",
                    "used_character_ids": scene.used_character_ids,
                    "used_secret_ids": scene.used_secret_ids,
                    "used_causal_ids": scene.used_causal_ids,
                    "used_world_details": scene.used_world_details,
                    "objective": scene.continuity_trace.get("scene_objective") or "Make the conflict visible.",
                    "ending_hook": scene.continuity_trace.get("ending_hook"),
                }
            )

        if not units and chapter:
            for index, section in enumerate(chapter.sections, start=1):
                scene_id = section.get("scene_id") or f"{chapter.chapter_id}_section_{index}"
                units.append(
                    {
                        "scene_id": scene_id,
                        "index": index,
                        "title": section.get("title") or scene_id,
                        "text": section.get("text", chapter.chapter_text),
                        "location": self._infer_location(section.get("title") or scene_id),
                        "time": "DAY",
                        "used_character_ids": section.get("used_character_ids", chapter.used_character_ids),
                        "used_secret_ids": section.get("used_secret_ids", chapter.used_secret_ids),
                        "used_causal_ids": section.get("used_causal_ids", chapter.used_causal_ids),
                        "used_world_details": section.get("used_world_details", chapter.used_world_details),
                        "objective": section.get("purpose") or "Adapt chapter section into cinematic action.",
                        "ending_hook": None,
                    }
                )

            if not chapter.sections:
                units.append(
                    {
                        "scene_id": chapter.chapter_id,
                        "index": 1,
                        "title": chapter.title or chapter.chapter_id,
                        "text": chapter.chapter_text,
                        "location": self._infer_location(chapter.title or chapter.chapter_id),
                        "time": "DAY",
                        "used_character_ids": chapter.used_character_ids,
                        "used_secret_ids": chapter.used_secret_ids,
                        "used_causal_ids": chapter.used_causal_ids,
                        "used_world_details": chapter.used_world_details,
                        "objective": "Adapt chapter into cinematic sequence.",
                        "ending_hook": chapter.next_chapter_hooks[0] if chapter.next_chapter_hooks else None,
                    }
                )

        if not units and plot_outline:
            for index, item in enumerate(plot_outline.scene_sequence, start=1):
                units.append(
                    {
                        "scene_id": item.get("scene_id") or f"outline_scene_{index}",
                        "index": index,
                        "title": item.get("scene_id") or f"Outline Scene {index}",
                        "text": item.get("purpose") or "Outline scene becomes visible action.",
                        "location": self._infer_location(item.get("scene_id") or "outline"),
                        "time": "DAY",
                        "used_character_ids": item.get("used_character_ids", plot_outline.continuity_requirements.get("required_character_ids", [])),
                        "used_secret_ids": item.get("used_secret_ids", plot_outline.continuity_requirements.get("required_secret_ids", [])),
                        "used_causal_ids": item.get("used_causal_ids", plot_outline.continuity_requirements.get("required_causal_ids", [])),
                        "used_world_details": item.get("used_world_details", plot_outline.continuity_requirements.get("required_world_details", [])),
                        "objective": item.get("purpose") or "Turn outline beat into performable action.",
                        "ending_hook": None,
                    }
                )

        return units

    def _scene_headings(self, *, scene_units: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        headings = []
        for unit in scene_units:
            headings.append(
                {
                    "scene_id": unit["scene_id"],
                    "heading": f"INT. {str(unit.get('location', 'UNKNOWN')).upper()} - {unit.get('time', 'DAY')}",
                    "location": unit.get("location", "UNKNOWN"),
                    "time": unit.get("time", "DAY"),
                    "sequence_index": unit["index"],
                }
            )
        return headings

    def _action_blocks(self, *, scene_units: List[Dict[str, Any]], normalized_format: str) -> List[Dict[str, Any]]:
        blocks = []
        for unit in scene_units:
            world_detail = unit.get("used_world_details", ["the room"])
            world_phrase = world_detail[0] if world_detail else "the room"
            objective = unit.get("objective") or "The conflict turns visible."
            causal = ", ".join(unit.get("used_causal_ids", [])[:2]) or "the visible consequence"

            if normalized_format == "movie":
                text = f"{world_phrase} becomes the visual center of the sequence. {objective} Every action points toward {causal}."
            else:
                text = f"{world_phrase} holds the pressure of the scene. {objective} The consequence is visible before anyone explains it."

            blocks.append(
                {
                    "action_block_id": f"action_{unit['scene_id']}",
                    "scene_id": unit["scene_id"],
                    "text": text,
                    "performable": True,
                    "visual_focus": world_phrase,
                    "causal_focus": causal,
                }
            )
        return blocks

    def _dialogue_blocks(self, *, scene_units: List[Dict[str, Any]], chapter: GeneratedChapter | None) -> List[Dict[str, Any]]:
        blocks = []
        for unit in scene_units:
            characters = unit.get("used_character_ids", []) or (chapter.used_character_ids if chapter else [])
            if not characters:
                continue

            speaker = characters[0]
            listener = characters[1] if len(characters) > 1 else None
            line = "This does not leave the room unchanged."

            if unit.get("used_secret_ids"):
                line = "There are things I cannot say here."
            elif unit.get("ending_hook"):
                line = str(unit["ending_hook"])

            blocks.append(
                {
                    "dialogue_block_id": f"dialogue_{unit['scene_id']}_{speaker}",
                    "scene_id": unit["scene_id"],
                    "speaker_id": speaker,
                    "listener_id": listener,
                    "line": line,
                    "subtext": "The spoken line carries pressure without inner narration.",
                }
            )

        return blocks

    def _movie_sequence_beats(
        self,
        *,
        scene_units: List[Dict[str, Any]],
        plot_outline: PlotOutline | None,
        normalized_format: str,
    ) -> List[Dict[str, Any]]:
        beats = []
        for unit in scene_units:
            beats.append(
                {
                    "sequence_beat_id": f"movie_beat_{unit['scene_id']}",
                    "scene_id": unit["scene_id"],
                    "beat_type": self._beat_type(unit=unit),
                    "description": f"Visual beat for {unit['scene_id']}: {unit.get('objective')}",
                    "used_causal_ids": unit.get("used_causal_ids", []),
                    "used_secret_ids": unit.get("used_secret_ids", []),
                }
            )

        if plot_outline:
            for turn in plot_outline.major_turning_points[:4]:
                beats.append(
                    {
                        "sequence_beat_id": f"movie_turn_{turn.get('turning_point_id')}",
                        "scene_id": turn.get("source_id"),
                        "beat_type": "turning_point",
                        "description": turn.get("description"),
                        "used_causal_ids": [],
                        "used_secret_ids": [],
                    }
                )

        return beats

    def _visual_motifs(
        self,
        *,
        plot_outline: PlotOutline | None,
        chapter: GeneratedChapter | None,
        scene_units: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        motifs: List[Dict[str, Any]] = []

        details: List[str] = []
        if plot_outline:
            details.extend(plot_outline.continuity_requirements.get("required_world_details", []))
        if chapter:
            details.extend(chapter.used_world_details)
        for unit in scene_units:
            details.extend(unit.get("used_world_details", []))

        for detail in self._unique(details)[:10]:
            motifs.append(
                {
                    "motif_id": f"visual_motif_{self._safe_id(detail)}",
                    "source_detail": detail,
                    "description": f"Use {detail} as a recurring visual continuity marker.",
                }
            )

        return motifs

    def _continuity_requirements(
        self,
        *,
        format_plan: FormatAdaptationPlan | None,
        plot_outline: PlotOutline | None,
        chapter: GeneratedChapter | None,
    ) -> Dict[str, Any]:
        requirements: Dict[str, Any] = {
            "visual_only_rule": True,
            "avoid_unfilmable_interiority": True,
            "preserve_causal_visibility": True,
        }

        if format_plan:
            requirements["format_plan_id"] = format_plan.adaptation_plan_id
            requirements["format_continuity_rules"] = format_plan.continuity_rules

        if plot_outline:
            requirements["plot_outline_id"] = plot_outline.outline_id
            requirements["plot_continuity_requirements"] = plot_outline.continuity_requirements
            requirements["next_outline_hooks"] = plot_outline.next_outline_hooks

        if chapter:
            requirements["chapter_id"] = chapter.chapter_id
            requirements["used_character_ids"] = chapter.used_character_ids
            requirements["used_secret_ids"] = chapter.used_secret_ids
            requirements["used_causal_ids"] = chapter.used_causal_ids

        return requirements

    def _formatted_text(
        self,
        *,
        title: str,
        logline: str,
        normalized_format: str,
        scene_headings: List[Dict[str, Any]],
        action_blocks: List[Dict[str, Any]],
        dialogue_blocks: List[Dict[str, Any]],
        movie_sequence_beats: List[Dict[str, Any]],
    ) -> str:
        lines = [
            title.upper(),
            "",
            f"LOGLINE: {logline}",
            "",
        ]

        if normalized_format == "movie":
            lines.extend(["MOVIE SEQUENCE BEATS", ""])
            for beat in movie_sequence_beats:
                lines.append(f"- {beat.get('beat_type')}: {beat.get('description')}")
            lines.append("")

        dialogue_by_scene: Dict[str, List[Dict[str, Any]]] = {}
        for block in dialogue_blocks:
            dialogue_by_scene.setdefault(block["scene_id"], []).append(block)

        action_by_scene = {block["scene_id"]: block for block in action_blocks}

        for heading in scene_headings:
            scene_id = heading["scene_id"]
            lines.append(heading["heading"])
            lines.append("")
            action = action_by_scene.get(scene_id)
            if action:
                lines.append(action["text"])
                lines.append("")

            for dialogue in dialogue_by_scene.get(scene_id, []):
                lines.append(str(dialogue["speaker_id"]).upper())
                lines.append(dialogue["line"])
                lines.append("")

            lines.append("CUT TO:")
            lines.append("")

        return "\n".join(lines).strip()

    def _export_payload(
        self,
        *,
        source_id: str,
        normalized_format: str,
        title: str,
        formatted_text: str,
        scene_headings: List[Dict[str, Any]],
        movie_sequence_beats: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        return {
            "export_id": f"export_{source_id}_{normalized_format}",
            "source_id": source_id,
            "target_format": normalized_format,
            "title": title,
            "text": formatted_text,
            "scene_count": len(scene_headings),
            "movie_sequence_beat_count": len(movie_sequence_beats),
            "suggested_extension": ".fountain" if normalized_format == "screenplay" else ".md",
        }

    def _warnings(
        self,
        *,
        formatted_text: str,
        scene_units: List[Dict[str, Any]],
        normalized_format: str,
        format_plan: FormatAdaptationPlan | None,
    ) -> List[str]:
        warnings: List[str] = []
        lowered = formatted_text.lower()

        if not scene_units:
            warnings.append("No scene units were available for screenplay/movie formatting.")

        for marker in self.UNFILMABLE_MARKERS:
            if marker in lowered:
                warnings.append(f"Unfilmable interiority marker detected: {marker}")

        for marker in self.CAMERA_MARKERS:
            if marker in lowered:
                warnings.append(f"Camera direction marker detected; consider replacing with action: {marker}")

        if normalized_format == "screenplay" and "INT." not in formatted_text and "EXT." not in formatted_text:
            warnings.append("Screenplay output has no scene headings.")

        if format_plan and format_plan.target_format not in {"screenplay", "movie"}:
            warnings.append(f"Format plan target is {format_plan.target_format}; formatter output is {normalized_format}.")

        return self._unique(warnings)

    def _infer_location(self, value: str) -> str:
        clean = str(value).replace("_", " ").replace("-", " ").strip()
        if not clean:
            return "UNKNOWN"
        return clean.upper()

    def _beat_type(self, *, unit: Dict[str, Any]) -> str:
        if unit.get("used_secret_ids"):
            return "secret_pressure"
        if unit.get("used_causal_ids"):
            return "causal_turn"
        if unit.get("ending_hook"):
            return "hook"
        return "visual_setup"

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

from __future__ import annotations

from typing import Any, Dict, List

from backend.app.schemas.story_generation import (
    AssembledScene,
    GeneratedChapter,
    SceneQualityReport,
)


class ChapterGenerator:
    """Builds chapter-level output from assembled scenes.

    This engine is the bridge between scene generation and long-form generation.
    It preserves continuity trace, open loops, character usage, secrets, causal
    IDs, world details, and next-chapter hooks.
    """

    engine_name = "story_generation.chapter_generator"

    def generate_chapter(
        self,
        *,
        chapter_id: str,
        assembled_scenes: List[AssembledScene],
        quality_reports: List[SceneQualityReport] | None = None,
        chapter_number: int = 1,
        chapter_title: str | None = None,
        story_context: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        quality_reports = quality_reports or []
        story_context = story_context or {}

        sections = self._build_sections(assembled_scenes=assembled_scenes)
        chapter_text = self._render_chapter_text(
            title=chapter_title or self._chapter_title(chapter_number=chapter_number, assembled_scenes=assembled_scenes),
            sections=sections,
        )

        quality_summary = self._quality_summary(quality_reports=quality_reports)
        continuity_trace = self._continuity_trace(
            assembled_scenes=assembled_scenes,
            quality_reports=quality_reports,
            story_context=story_context,
        )

        open_loops = self._open_loops(
            assembled_scenes=assembled_scenes,
            story_context=story_context,
        )
        next_chapter_hooks = self._next_chapter_hooks(
            assembled_scenes=assembled_scenes,
            open_loops=open_loops,
        )

        chapter = GeneratedChapter(
            chapter_id=chapter_id,
            chapter_number=chapter_number,
            title=chapter_title or self._chapter_title(chapter_number=chapter_number, assembled_scenes=assembled_scenes),
            chapter_text=chapter_text,
            scene_ids=[scene.scene_id for scene in assembled_scenes],
            assembled_scene_ids=[scene.assembled_scene_id for scene in assembled_scenes],
            sections=sections,
            continuity_trace=continuity_trace,
            used_character_ids=self._unique([cid for scene in assembled_scenes for cid in scene.used_character_ids]),
            used_relationship_ids=self._unique([rid for scene in assembled_scenes for rid in scene.used_relationship_ids]),
            used_secret_ids=self._unique([sid for scene in assembled_scenes for sid in scene.used_secret_ids]),
            used_causal_ids=self._unique([cid for scene in assembled_scenes for cid in scene.used_causal_ids]),
            used_world_details=self._unique([detail for scene in assembled_scenes for detail in scene.used_world_details]),
            open_loops=open_loops,
            next_chapter_hooks=next_chapter_hooks,
            quality_summary=quality_summary,
            generation_notes=self._generation_notes(assembled_scenes=assembled_scenes, quality_reports=quality_reports),
            warnings=self._warnings(assembled_scenes=assembled_scenes, quality_reports=quality_reports, chapter_text=chapter_text),
        )

        return {
            "success": True,
            "engine_name": self.engine_name,
            "generated_chapter": chapter,
            "generated_chapter_dict": chapter.model_dump(mode="json"),
            "handoff_to_next_engine": {
                "next_engine": "story_generation.long_form_continuation_anchor",
                "payload_keys": [
                    "generated_chapter",
                    "assembled_scenes",
                    "scene_quality_reports",
                    "story_context",
                ],
            },
        }

    def validate_chapter(self, *, chapter: GeneratedChapter) -> Dict[str, Any]:
        blockers: List[str] = []
        warnings: List[str] = []
        passed: List[str] = []

        if not chapter.chapter_id:
            blockers.append("chapter_id missing")
        else:
            passed.append("chapter_id_present")

        if chapter.chapter_text and len(chapter.chapter_text.strip()) >= 250:
            passed.append("chapter_text_present")
        else:
            blockers.append("chapter text is missing or too short")

        if chapter.scene_ids:
            passed.append("scene_ids_present")
        else:
            blockers.append("no scenes included in chapter")

        if chapter.continuity_trace:
            passed.append("continuity_trace_present")
        else:
            warnings.append("chapter continuity trace missing")

        if chapter.used_character_ids:
            passed.append("characters_tracked")
        else:
            warnings.append("no characters tracked")

        if chapter.next_chapter_hooks:
            passed.append("next_chapter_hooks_present")
        else:
            warnings.append("no next chapter hooks generated")

        if chapter.quality_summary.get("failed_scene_count", 0) > 0:
            warnings.append("chapter contains scenes that failed quality gate")

        if chapter.warnings:
            warnings.extend(chapter.warnings)

        return {
            "success": True,
            "engine_name": self.engine_name,
            "valid": not blockers,
            "blockers": blockers,
            "warnings": self._unique(warnings),
            "passed_checks": passed,
        }

    def summarize_chapter(self, *, chapter: GeneratedChapter) -> Dict[str, Any]:
        return {
            "success": True,
            "engine_name": self.engine_name,
            "summary": {
                "chapter_id": chapter.chapter_id,
                "chapter_number": chapter.chapter_number,
                "title": chapter.title,
                "word_count": len(chapter.chapter_text.split()),
                "scene_count": len(chapter.scene_ids),
                "used_character_count": len(chapter.used_character_ids),
                "used_relationship_count": len(chapter.used_relationship_ids),
                "used_secret_count": len(chapter.used_secret_ids),
                "used_causal_count": len(chapter.used_causal_ids),
                "used_world_detail_count": len(chapter.used_world_details),
                "open_loop_count": len(chapter.open_loops),
                "next_chapter_hook_count": len(chapter.next_chapter_hooks),
                "warning_count": len(chapter.warnings),
            },
        }

    def build_long_form_handoff_payload(self, *, chapter: GeneratedChapter) -> Dict[str, Any]:
        payload = {
            "long_form_handoff_id": f"longform_handoff_{chapter.chapter_id}",
            "chapter_id": chapter.chapter_id,
            "chapter_number": chapter.chapter_number,
            "title": chapter.title,
            "chapter_text": chapter.chapter_text,
            "scene_ids": chapter.scene_ids,
            "continuity_trace": chapter.continuity_trace,
            "used_character_ids": chapter.used_character_ids,
            "used_relationship_ids": chapter.used_relationship_ids,
            "used_secret_ids": chapter.used_secret_ids,
            "used_causal_ids": chapter.used_causal_ids,
            "used_world_details": chapter.used_world_details,
            "open_loops": chapter.open_loops,
            "next_chapter_hooks": chapter.next_chapter_hooks,
            "quality_summary": chapter.quality_summary,
            "warnings": chapter.warnings,
        }

        return {
            "success": True,
            "engine_name": self.engine_name,
            "long_form_handoff_payload": payload,
        }

    def _build_sections(self, *, assembled_scenes: List[AssembledScene]) -> List[Dict[str, Any]]:
        sections: List[Dict[str, Any]] = []

        for index, scene in enumerate(assembled_scenes, start=1):
            sections.append(
                {
                    "chapter_section_id": f"chapter_section_{index:02d}_{scene.scene_id}",
                    "scene_id": scene.scene_id,
                    "assembled_scene_id": scene.assembled_scene_id,
                    "title": scene.title,
                    "text": scene.assembled_text,
                    "used_character_ids": scene.used_character_ids,
                    "used_secret_ids": scene.used_secret_ids,
                    "used_causal_ids": scene.used_causal_ids,
                    "used_world_details": scene.used_world_details,
                    "continuity_trace": scene.continuity_trace,
                    "warnings": scene.warnings,
                }
            )

        return sections

    def _render_chapter_text(self, *, title: str, sections: List[Dict[str, Any]]) -> str:
        body_parts = []

        for section in sections:
            scene_title = section.get("title") or section.get("scene_id")
            text = section.get("text", "")
            body_parts.append(f"## {scene_title}\n\n{text}")

        body = "\n\n".join(body_parts)
        return f"# {title}\n\n{body}"

    def _chapter_title(self, *, chapter_number: int, assembled_scenes: List[AssembledScene]) -> str:
        if assembled_scenes:
            first_title = assembled_scenes[0].title or assembled_scenes[0].scene_id
            return f"Chapter {chapter_number}: {first_title}"
        return f"Chapter {chapter_number}"

    def _quality_summary(self, *, quality_reports: List[SceneQualityReport]) -> Dict[str, Any]:
        if not quality_reports:
            return {
                "quality_report_count": 0,
                "average_overall_score": None,
                "passed_scene_count": 0,
                "failed_scene_count": 0,
                "weakest_scene_id": None,
            }

        average = round(sum(report.overall_score for report in quality_reports) / len(quality_reports), 3)
        weakest = min(quality_reports, key=lambda report: report.overall_score)

        return {
            "quality_report_count": len(quality_reports),
            "average_overall_score": average,
            "passed_scene_count": sum(1 for report in quality_reports if report.passed),
            "failed_scene_count": sum(1 for report in quality_reports if not report.passed),
            "weakest_scene_id": weakest.scene_id,
            "weakest_score": weakest.overall_score,
        }

    def _continuity_trace(
        self,
        *,
        assembled_scenes: List[AssembledScene],
        quality_reports: List[SceneQualityReport],
        story_context: Dict[str, Any],
    ) -> Dict[str, Any]:
        return {
            "story_context_id": story_context.get("story_context_id"),
            "scene_trace": [
                {
                    "scene_id": scene.scene_id,
                    "assembled_scene_id": scene.assembled_scene_id,
                    "continuity_trace": scene.continuity_trace,
                }
                for scene in assembled_scenes
            ],
            "quality_report_ids": [report.report_id for report in quality_reports],
            "ending_hooks": [
                scene.continuity_trace.get("ending_hook")
                for scene in assembled_scenes
                if scene.continuity_trace.get("ending_hook")
            ],
            "scene_objectives": [
                scene.continuity_trace.get("scene_objective")
                for scene in assembled_scenes
                if scene.continuity_trace.get("scene_objective")
            ],
        }

    def _open_loops(
        self,
        *,
        assembled_scenes: List[AssembledScene],
        story_context: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        loops: List[Dict[str, Any]] = []

        for item in story_context.get("open_loops", []):
            if isinstance(item, dict):
                loops.append(dict(item))

        for scene in assembled_scenes:
            hook = scene.continuity_trace.get("ending_hook")
            if hook:
                loops.append(
                    {
                        "loop_id": f"open_loop_{scene.scene_id}_ending_hook",
                        "source_scene_id": scene.scene_id,
                        "loop_type": "ending_hook",
                        "status": "open",
                        "description": hook,
                    }
                )

            for secret_id in scene.used_secret_ids:
                loops.append(
                    {
                        "loop_id": f"open_loop_{scene.scene_id}_{secret_id}",
                        "source_scene_id": scene.scene_id,
                        "loop_type": "secret_pressure",
                        "status": "open",
                        "secret_id": secret_id,
                        "description": f"Secret pressure remains active for {secret_id}.",
                    }
                )

        return self._unique_loops(loops)

    def _next_chapter_hooks(
        self,
        *,
        assembled_scenes: List[AssembledScene],
        open_loops: List[Dict[str, Any]],
    ) -> List[str]:
        hooks: List[str] = []

        for scene in assembled_scenes:
            hook = scene.continuity_trace.get("ending_hook")
            if hook:
                hooks.append(hook)

        for loop in open_loops:
            description = loop.get("description")
            if description:
                hooks.append(description)

        if not hooks and assembled_scenes:
            hooks.append(f"Continue from {assembled_scenes[-1].scene_id} with a new consequence.")

        return self._unique(hooks)

    def _generation_notes(
        self,
        *,
        assembled_scenes: List[AssembledScene],
        quality_reports: List[SceneQualityReport],
    ) -> List[str]:
        notes = [
            f"Chapter assembled from {len(assembled_scenes)} scene(s).",
            f"Quality reports included: {len(quality_reports)}.",
        ]

        failed = [report.scene_id for report in quality_reports if not report.passed]
        if failed:
            notes.append(f"Scenes needing revision before final export: {', '.join(failed)}.")

        return notes

    def _warnings(
        self,
        *,
        assembled_scenes: List[AssembledScene],
        quality_reports: List[SceneQualityReport],
        chapter_text: str,
    ) -> List[str]:
        warnings: List[str] = []

        if not assembled_scenes:
            warnings.append("No assembled scenes supplied.")

        if len(chapter_text.split()) < 250:
            warnings.append("Generated chapter is short and may need expansion.")

        for scene in assembled_scenes:
            warnings.extend(scene.warnings)

        for report in quality_reports:
            if not report.passed:
                warnings.append(f"Scene {report.scene_id} did not pass quality gate.")

        return self._unique(warnings)

    def _unique(self, values: List[str]) -> List[str]:
        result = []
        seen = set()
        for value in values:
            if value and value not in seen:
                seen.add(value)
                result.append(value)
        return result

    def _unique_loops(self, loops: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        result = []
        seen = set()
        for loop in loops:
            key = loop.get("loop_id") or str(loop)
            if key not in seen:
                seen.add(key)
                result.append(loop)
        return result

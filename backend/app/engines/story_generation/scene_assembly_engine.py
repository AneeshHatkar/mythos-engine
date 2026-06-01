from __future__ import annotations

from typing import Any, Dict, List

from backend.app.schemas.story_generation import (
    AssembledScene,
    GeneratedDialogueBlock,
    GeneratedSceneDraft,
    SceneBeat,
    SceneBlueprint,
)


class SceneAssemblyEngine:
    """Assembles draft prose and generated dialogue into a final scene package.

    This is the bridge from draft components to chapter-ready scene output.
    It also preserves trace data so later memory/provenance/revision systems
    know which characters, secrets, causes, relationships, and world details
    were used.
    """

    engine_name = "story_generation.scene_assembly_engine"

    def assemble_scene(
        self,
        *,
        blueprint: SceneBlueprint,
        scene_draft: GeneratedSceneDraft,
        dialogue_block: GeneratedDialogueBlock | None = None,
        scene_beats: List[SceneBeat] | None = None,
        prose_style_profile: Dict[str, Any] | None = None,
        story_context: Dict[str, Any] | None = None,
        world_detail_pack: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        scene_beats = scene_beats or []
        prose_style_profile = prose_style_profile or {}
        story_context = story_context or {}
        world_detail_pack = world_detail_pack or {}

        selected_format = (
            dialogue_block.selected_format
            if dialogue_block
            else scene_draft.selected_format
        )

        sections = self._assemble_sections(
            scene_draft=scene_draft,
            dialogue_block=dialogue_block,
            selected_format=selected_format,
        )

        assembled_text = self._render_assembled_text(
            title=scene_draft.title or self._title(blueprint),
            sections=sections,
            selected_format=selected_format,
        )

        continuity_trace = self._continuity_trace(
            blueprint=blueprint,
            scene_draft=scene_draft,
            dialogue_block=dialogue_block,
            scene_beats=scene_beats,
            prose_style_profile=prose_style_profile,
            story_context=story_context,
            world_detail_pack=world_detail_pack,
        )

        assembled = AssembledScene(
            assembled_scene_id=f"assembled_{blueprint.scene_id}",
            scene_id=blueprint.scene_id,
            draft_id=scene_draft.draft_id,
            dialogue_block_id=dialogue_block.dialogue_block_id if dialogue_block else None,
            selected_format=selected_format,
            title=scene_draft.title or self._title(blueprint),
            assembled_text=assembled_text,
            sections=sections,
            continuity_trace=continuity_trace,
            used_character_ids=self._used_character_ids(scene_draft=scene_draft, dialogue_block=dialogue_block),
            used_relationship_ids=scene_draft.used_relationship_ids,
            used_secret_ids=scene_draft.used_secret_ids,
            used_causal_ids=scene_draft.used_causal_ids,
            used_world_details=scene_draft.used_world_details,
            generation_notes=self._generation_notes(scene_draft=scene_draft, dialogue_block=dialogue_block),
            warnings=self._warnings(
                blueprint=blueprint,
                scene_draft=scene_draft,
                dialogue_block=dialogue_block,
                assembled_text=assembled_text,
            ),
        )

        return {
            "success": True,
            "engine_name": self.engine_name,
            "assembled_scene": assembled,
            "assembled_scene_dict": assembled.model_dump(mode="json"),
            "handoff_to_next_engine": {
                "next_engine": "story_generation.scene_quality_gate",
                "payload_keys": [
                    "assembled_scene",
                    "scene_blueprint",
                    "scene_beats",
                    "dialogue_block",
                    "prose_style_profile",
                    "story_context",
                    "world_detail_pack",
                ],
            },
        }

    def validate_assembled_scene(self, *, assembled_scene: AssembledScene) -> Dict[str, Any]:
        blockers: List[str] = []
        warnings: List[str] = []
        passed: List[str] = []

        if not assembled_scene.assembled_scene_id:
            blockers.append("assembled_scene_id missing")
        else:
            passed.append("assembled_scene_id_present")

        if not assembled_scene.scene_id:
            blockers.append("scene_id missing")
        else:
            passed.append("scene_id_present")

        if assembled_scene.assembled_text and len(assembled_scene.assembled_text.strip()) >= 150:
            passed.append("assembled_text_present")
        else:
            blockers.append("assembled text is missing or too short")

        if assembled_scene.sections:
            passed.append("sections_present")
        else:
            blockers.append("sections missing")

        if assembled_scene.continuity_trace:
            passed.append("continuity_trace_present")
        else:
            warnings.append("continuity trace missing")

        if assembled_scene.used_character_ids:
            passed.append("characters_tracked")
        else:
            warnings.append("used character ids missing")

        if assembled_scene.used_world_details:
            passed.append("world_details_tracked")
        else:
            warnings.append("used world details missing")

        if assembled_scene.warnings:
            warnings.extend(assembled_scene.warnings)

        return {
            "success": True,
            "engine_name": self.engine_name,
            "valid": not blockers,
            "blockers": blockers,
            "warnings": warnings,
            "passed_checks": passed,
        }

    def summarize_assembled_scene(self, *, assembled_scene: AssembledScene) -> Dict[str, Any]:
        return {
            "success": True,
            "engine_name": self.engine_name,
            "summary": {
                "assembled_scene_id": assembled_scene.assembled_scene_id,
                "scene_id": assembled_scene.scene_id,
                "selected_format": assembled_scene.selected_format,
                "word_count": len(assembled_scene.assembled_text.split()),
                "section_count": len(assembled_scene.sections),
                "used_character_count": len(assembled_scene.used_character_ids),
                "used_relationship_count": len(assembled_scene.used_relationship_ids),
                "used_secret_count": len(assembled_scene.used_secret_ids),
                "used_causal_count": len(assembled_scene.used_causal_ids),
                "used_world_detail_count": len(assembled_scene.used_world_details),
                "warning_count": len(assembled_scene.warnings),
            },
        }

    def build_chapter_handoff_payload(self, *, assembled_scene: AssembledScene) -> Dict[str, Any]:
        payload = {
            "chapter_scene_payload_id": f"chapter_payload_{assembled_scene.scene_id}",
            "scene_id": assembled_scene.scene_id,
            "assembled_scene_id": assembled_scene.assembled_scene_id,
            "title": assembled_scene.title,
            "text": assembled_scene.assembled_text,
            "continuity_trace": assembled_scene.continuity_trace,
            "used_character_ids": assembled_scene.used_character_ids,
            "used_relationship_ids": assembled_scene.used_relationship_ids,
            "used_secret_ids": assembled_scene.used_secret_ids,
            "used_causal_ids": assembled_scene.used_causal_ids,
            "used_world_details": assembled_scene.used_world_details,
            "warnings": assembled_scene.warnings,
        }

        return {
            "success": True,
            "engine_name": self.engine_name,
            "chapter_handoff_payload": payload,
        }

    def _assemble_sections(
        self,
        *,
        scene_draft: GeneratedSceneDraft,
        dialogue_block: GeneratedDialogueBlock | None,
        selected_format: str,
    ) -> List[Dict[str, Any]]:
        sections = list(scene_draft.sections)

        if dialogue_block and dialogue_block.rendered_text:
            dialogue_section = {
                "section_id": f"section_{dialogue_block.dialogue_block_id}",
                "beat_id": None,
                "beat_type": "dialogue_block",
                "tension_value": None,
                "text": dialogue_block.rendered_text,
                "causal_links": [],
                "knowledge_constraints": [],
            }

            if selected_format == "screenplay":
                sections.append(dialogue_section)
            else:
                insert_index = self._best_dialogue_insert_index(sections)
                sections.insert(insert_index, dialogue_section)

        return sections

    def _best_dialogue_insert_index(self, sections: List[Dict[str, Any]]) -> int:
        for idx, section in enumerate(sections):
            if section.get("beat_type") in {"secret_pressure", "relationship_pressure", "dialogue_pressure", "choice"}:
                return idx + 1
        return len(sections)

    def _render_assembled_text(
        self,
        *,
        title: str,
        sections: List[Dict[str, Any]],
        selected_format: str,
    ) -> str:
        if selected_format == "screenplay":
            body = "\n\n".join(section.get("text", "") for section in sections)
            return f"{title}\n\n{body}"

        body = "\n\n".join(section.get("text", "") for section in sections)
        if title.startswith("#"):
            return f"{title}\n\n{body}"
        return f"# {title}\n\n{body}"

    def _continuity_trace(
        self,
        *,
        blueprint: SceneBlueprint,
        scene_draft: GeneratedSceneDraft,
        dialogue_block: GeneratedDialogueBlock | None,
        scene_beats: List[SceneBeat],
        prose_style_profile: Dict[str, Any],
        story_context: Dict[str, Any],
        world_detail_pack: Dict[str, Any],
    ) -> Dict[str, Any]:
        return {
            "blueprint_id": blueprint.blueprint_id,
            "draft_id": scene_draft.draft_id,
            "dialogue_block_id": dialogue_block.dialogue_block_id if dialogue_block else None,
            "scene_beat_ids": [beat.beat_id for beat in scene_beats],
            "dialogue_line_ids": [line.line_id for line in dialogue_block.lines] if dialogue_block else [],
            "style_profile_id": prose_style_profile.get("prose_style_profile_id"),
            "story_context_id": story_context.get("story_context_id"),
            "world_detail_pack_id": world_detail_pack.get("world_detail_pack_id"),
            "ending_hook": blueprint.ending_hook,
            "scene_objective": blueprint.scene_objective,
            "secret_pressure_count": len(blueprint.secret_pressure),
            "relationship_pressure_count": len(blueprint.relationship_pressure),
        }

    def _used_character_ids(
        self,
        *,
        scene_draft: GeneratedSceneDraft,
        dialogue_block: GeneratedDialogueBlock | None,
    ) -> List[str]:
        values = list(scene_draft.used_character_ids)
        if dialogue_block:
            values.extend(dialogue_block.used_speaker_ids)
            for line in dialogue_block.lines:
                values.extend(line.listener_ids)
        return self._unique(values)

    def _generation_notes(
        self,
        *,
        scene_draft: GeneratedSceneDraft,
        dialogue_block: GeneratedDialogueBlock | None,
    ) -> List[str]:
        notes = list(scene_draft.generation_notes)
        if dialogue_block:
            notes.append(f"Assembled with dialogue block {dialogue_block.dialogue_block_id}.")
        else:
            notes.append("Assembled without a dialogue block.")
        return notes

    def _warnings(
        self,
        *,
        blueprint: SceneBlueprint,
        scene_draft: GeneratedSceneDraft,
        dialogue_block: GeneratedDialogueBlock | None,
        assembled_text: str,
    ) -> List[str]:
        warnings = list(scene_draft.warnings)

        if dialogue_block:
            warnings.extend(dialogue_block.warnings)
        else:
            warnings.append("No dialogue block supplied during scene assembly.")

        if blueprint.ending_hook and blueprint.ending_hook not in assembled_text:
            warnings.append("Ending hook not directly present in assembled text.")

        if blueprint.secret_pressure and "secret" not in assembled_text.lower():
            warnings.append("Secret pressure may be underrepresented in assembled text.")

        if len(assembled_text.split()) < 180:
            warnings.append("Assembled scene is short and may require expansion.")

        return self._unique(warnings)

    def _title(self, blueprint: SceneBlueprint) -> str:
        if blueprint.location_id:
            return f"Scene at {blueprint.location_id}"
        return f"Scene {blueprint.scene_id}"

    def _unique(self, values: List[str]) -> List[str]:
        result = []
        seen = set()
        for value in values:
            if value and value not in seen:
                seen.add(value)
                result.append(value)
        return result

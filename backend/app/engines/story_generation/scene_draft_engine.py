from __future__ import annotations

from typing import Any, Dict, List

from backend.app.schemas.story_generation import (
    CommercialAppealReport,
    DialogueBeat,
    GeneratedSceneDraft,
    RelationshipBeat,
    SceneBeat,
    SceneBlueprint,
)


class SceneDraftEngine:
    """Generates a structured scene draft from validated planning layers.

    This is deterministic/testable drafting. Later we can swap the paragraph
    composer with an LLM adapter while keeping the same contract, provenance,
    validation, and revision pipeline.
    """

    engine_name = "story_generation.scene_draft_engine"

    def generate_scene_draft(
        self,
        *,
        blueprint: SceneBlueprint,
        scene_beats: List[SceneBeat],
        dialogue_beats: List[DialogueBeat] | None = None,
        relationship_beats: List[RelationshipBeat] | None = None,
        prose_style_profile: Dict[str, Any] | None = None,
        commercial_report: CommercialAppealReport | None = None,
        story_context: Dict[str, Any] | None = None,
        world_detail_pack: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        dialogue_beats = dialogue_beats or []
        relationship_beats = relationship_beats or []
        prose_style_profile = prose_style_profile or {}
        story_context = story_context or {}
        world_detail_pack = world_detail_pack or {}

        selected_format = prose_style_profile.get("selected_format", "scene")
        sections = self._build_sections(
            blueprint=blueprint,
            scene_beats=scene_beats,
            dialogue_beats=dialogue_beats,
            relationship_beats=relationship_beats,
            prose_style_profile=prose_style_profile,
            story_context=story_context,
            world_detail_pack=world_detail_pack,
        )

        draft_text = self._render_text(
            title=self._title(blueprint),
            selected_format=selected_format,
            sections=sections,
            prose_style_profile=prose_style_profile,
        )

        draft = GeneratedSceneDraft(
            draft_id=f"draft_{blueprint.scene_id}",
            scene_id=blueprint.scene_id,
            blueprint_id=blueprint.blueprint_id,
            selected_format=selected_format,
            title=self._title(blueprint),
            draft_text=draft_text,
            sections=sections,
            used_world_details=self._used_world_details(blueprint=blueprint, world_detail_pack=world_detail_pack),
            used_character_ids=blueprint.active_character_ids,
            used_relationship_ids=[item.relationship_id for item in relationship_beats],
            used_secret_ids=self._used_secret_ids(blueprint=blueprint, story_context=story_context),
            used_causal_ids=self._used_causal_ids(scene_beats=scene_beats, story_context=story_context),
            style_profile_id=prose_style_profile.get("prose_style_profile_id"),
            commercial_report_id=commercial_report.report_id if commercial_report else None,
            generation_notes=self._generation_notes(prose_style_profile=prose_style_profile, commercial_report=commercial_report),
            warnings=self._warnings(blueprint=blueprint, sections=sections, draft_text=draft_text),
        )

        return {
            "success": True,
            "engine_name": self.engine_name,
            "scene_draft": draft,
            "scene_draft_dict": draft.model_dump(mode="json"),
            "handoff_to_next_engine": {
                "next_engine": "story_generation.dialogue_line_generator",
                "payload_keys": [
                    "scene_draft",
                    "scene_blueprint",
                    "scene_beats",
                    "dialogue_beats",
                    "relationship_beats",
                    "prose_style_profile",
                    "story_context",
                    "world_detail_pack",
                ],
            },
        }

    def validate_scene_draft(self, *, draft: GeneratedSceneDraft) -> Dict[str, Any]:
        blockers: List[str] = []
        warnings: List[str] = []
        passed: List[str] = []

        if not draft.draft_id:
            blockers.append("draft_id missing")
        else:
            passed.append("draft_id_present")

        if not draft.scene_id:
            blockers.append("scene_id missing")
        else:
            passed.append("scene_id_present")

        if draft.draft_text and len(draft.draft_text.strip()) >= 100:
            passed.append("draft_text_present")
        else:
            blockers.append("draft text is missing or too short")

        if draft.sections:
            passed.append("sections_present")
        else:
            blockers.append("sections missing")

        if draft.used_character_ids:
            passed.append("characters_used")
        else:
            warnings.append("no used characters recorded")

        if draft.used_world_details:
            passed.append("world_details_used")
        else:
            warnings.append("no world details recorded")

        if draft.warnings:
            warnings.extend(draft.warnings)

        return {
            "success": True,
            "engine_name": self.engine_name,
            "valid": not blockers,
            "blockers": blockers,
            "warnings": warnings,
            "passed_checks": passed,
        }

    def summarize_scene_draft(self, *, draft: GeneratedSceneDraft) -> Dict[str, Any]:
        return {
            "success": True,
            "engine_name": self.engine_name,
            "summary": {
                "draft_id": draft.draft_id,
                "scene_id": draft.scene_id,
                "selected_format": draft.selected_format,
                "section_count": len(draft.sections),
                "word_count": len(draft.draft_text.split()),
                "used_character_count": len(draft.used_character_ids),
                "used_world_detail_count": len(draft.used_world_details),
                "used_relationship_count": len(draft.used_relationship_ids),
                "used_secret_count": len(draft.used_secret_ids),
                "used_causal_count": len(draft.used_causal_ids),
                "warning_count": len(draft.warnings),
            },
        }

    def build_revision_targets(self, *, draft: GeneratedSceneDraft) -> Dict[str, Any]:
        targets: List[str] = []

        if len(draft.draft_text.split()) < 250:
            targets.append("expand scene length and sensory development")

        if not draft.used_world_details:
            targets.append("add concrete world details")

        if not draft.used_relationship_ids:
            targets.append("increase relationship-specific tension")

        if not draft.used_secret_ids:
            targets.append("make secret pressure more visible")

        if not draft.used_causal_ids:
            targets.append("connect draft more clearly to causal chain")

        if not targets:
            targets.append("polish rhythm, subtext, and specificity")

        return {
            "success": True,
            "engine_name": self.engine_name,
            "revision_targets": targets,
            "needs_revision": bool(targets),
        }

    def _build_sections(
        self,
        *,
        blueprint: SceneBlueprint,
        scene_beats: List[SceneBeat],
        dialogue_beats: List[DialogueBeat],
        relationship_beats: List[RelationshipBeat],
        prose_style_profile: Dict[str, Any],
        story_context: Dict[str, Any],
        world_detail_pack: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        sections: List[Dict[str, Any]] = []

        dialogue_by_type = self._dialogue_by_beat_type(dialogue_beats)
        world_details = self._used_world_details(blueprint=blueprint, world_detail_pack=world_detail_pack)
        relationship_note = self._relationship_note(relationship_beats)
        style_notes = prose_style_profile.get("drafting_instructions", [])

        for beat in scene_beats:
            paragraph = self._compose_beat_paragraph(
                beat=beat,
                blueprint=blueprint,
                dialogue_candidates=dialogue_by_type.get(beat.beat_type, []),
                world_details=world_details,
                relationship_note=relationship_note,
                style_notes=style_notes,
                story_context=story_context,
            )
            sections.append(
                {
                    "section_id": f"section_{beat.beat_id}",
                    "beat_id": beat.beat_id,
                    "beat_type": beat.beat_type,
                    "tension_value": beat.tension_value,
                    "text": paragraph,
                    "causal_links": beat.causal_links,
                    "knowledge_constraints": beat.knowledge_constraints,
                }
            )

        if not sections:
            sections.append(
                {
                    "section_id": f"section_{blueprint.scene_id}_fallback",
                    "beat_id": None,
                    "beat_type": "fallback_scene",
                    "tension_value": max(blueprint.tension_curve or [0.5]),
                    "text": self._fallback_scene_text(blueprint=blueprint, world_details=world_details),
                    "causal_links": [],
                    "knowledge_constraints": blueprint.secret_pressure,
                }
            )

        return sections

    def _compose_beat_paragraph(
        self,
        *,
        beat: SceneBeat,
        blueprint: SceneBlueprint,
        dialogue_candidates: List[DialogueBeat],
        world_details: List[str],
        relationship_note: str,
        style_notes: List[str],
        story_context: Dict[str, Any],
    ) -> str:
        location = blueprint.location_id or "the scene"
        world_detail = world_details[(beat.beat_index - 1) % len(world_details)] if world_details else "the pressure of the world"
        characters = ", ".join(beat.character_ids or blueprint.active_character_ids)

        base = (
            f"In {location}, {world_detail} presses against {characters}. "
            f"The beat purpose is clear: {beat.purpose}"
        )

        if beat.emotional_state:
            base += f" Emotion sits under the action through {beat.emotional_state}."

        if beat.knowledge_constraints:
            base += f" Knowledge boundaries shape the moment: {'; '.join(beat.knowledge_constraints)}."

        if beat.causal_links:
            base += f" This beat stays tied to {'; '.join(beat.causal_links)}."

        if relationship_note:
            base += f" The relationship layer matters here: {relationship_note}"

        if dialogue_candidates:
            rendered_dialogue = " ".join(self._render_dialogue_hint(item) for item in dialogue_candidates[:2])
            base += f" Dialogue pressure: {rendered_dialogue}"

        if beat.beat_type == "ending_hook" and blueprint.ending_hook:
            base += f" The scene turns toward the hook: {blueprint.ending_hook}"

        if style_notes:
            base += f" Drafting constraint: {style_notes[0]}"

        return base

    def _render_dialogue_hint(self, beat: DialogueBeat) -> str:
        speaker = beat.speaker_id
        surface = beat.surface_meaning or "speaks under pressure"
        subtext = beat.subtext or beat.hidden_meaning or "subtext remains active"
        return f"{speaker} says something that means '{surface}' while carrying '{subtext}'."

    def _render_text(self, *, title: str, selected_format: str, sections: List[Dict[str, Any]], prose_style_profile: Dict[str, Any]) -> str:
        if selected_format == "screenplay":
            body = "\n\n".join(f"ACTION: {section['text']}" for section in sections)
            return f"{title}\n\n{body}"

        body = "\n\n".join(section["text"] for section in sections)
        return f"# {title}\n\n{body}"

    def _fallback_scene_text(self, *, blueprint: SceneBlueprint, world_details: List[str]) -> str:
        detail = world_details[0] if world_details else "a concrete detail"
        return (
            f"The scene begins with {detail}. {blueprint.scene_objective or blueprint.scene_purpose} "
            f"pushes the characters into a choice, and the ending pressure remains unresolved."
        )

    def _title(self, blueprint: SceneBlueprint) -> str:
        if blueprint.location_id:
            return f"Scene at {blueprint.location_id}"
        return f"Scene {blueprint.scene_id}"

    def _dialogue_by_beat_type(self, dialogue_beats: List[DialogueBeat]) -> Dict[str, List[DialogueBeat]]:
        grouped: Dict[str, List[DialogueBeat]] = {}
        for beat in dialogue_beats:
            # dialogue beat IDs end with the originating beat type in this project.
            beat_type = beat.dialogue_beat_id.split("_")[-1]
            grouped.setdefault(beat_type, []).append(beat)

            if "secret" in beat.dialogue_beat_id:
                grouped.setdefault("secret_pressure", []).append(beat)
            if "relationship" in beat.dialogue_beat_id:
                grouped.setdefault("relationship_pressure", []).append(beat)
            if "choice" in beat.dialogue_beat_id:
                grouped.setdefault("choice", []).append(beat)
            if "consequence" in beat.dialogue_beat_id:
                grouped.setdefault("consequence", []).append(beat)
            if "ending" in beat.dialogue_beat_id:
                grouped.setdefault("ending_hook", []).append(beat)

        return grouped

    def _relationship_note(self, relationship_beats: List[RelationshipBeat]) -> str:
        if not relationship_beats:
            return ""

        beat = relationship_beats[0]
        return (
            f"{beat.relationship_id} should shift through {beat.turning_point}; "
            f"expected shift: {beat.expected_end_state_shift}."
        )

    def _used_world_details(self, *, blueprint: SceneBlueprint, world_detail_pack: Dict[str, Any]) -> List[str]:
        details = list(blueprint.required_world_details)

        for key in ["law_and_rule_anchors", "location_anchors", "ritual_anchors", "faction_anchors"]:
            for item in world_detail_pack.get(key, []):
                detail = item.get("detail") if isinstance(item, dict) else None
                if detail:
                    details.append(str(detail))

        return self._unique(details)

    def _used_secret_ids(self, *, blueprint: SceneBlueprint, story_context: Dict[str, Any]) -> List[str]:
        values: List[str] = []

        for pressure in blueprint.secret_pressure:
            values.extend(self._extract_ids(pressure, prefixes=["secret_", "major_mystery"]))

        for boundary in story_context.get("knowledge_boundaries", []):
            values.extend(boundary.get("known_secret_ids", []))
            values.extend(boundary.get("missing_required_secret_ids", []))
            values.extend(boundary.get("forbidden_secret_reveals", []))

        return self._unique(values)

    def _used_causal_ids(self, *, scene_beats: List[SceneBeat], story_context: Dict[str, Any]) -> List[str]:
        values: List[str] = []

        for beat in scene_beats:
            values.extend(beat.causal_links)

        for obligation in story_context.get("causal_obligations", []):
            if obligation.get("id"):
                values.append(obligation["id"])

        return self._unique(values)

    def _generation_notes(self, *, prose_style_profile: Dict[str, Any], commercial_report: CommercialAppealReport | None) -> List[str]:
        notes = []
        if prose_style_profile.get("prose_style_profile_id"):
            notes.append(f"Used prose style profile {prose_style_profile['prose_style_profile_id']}.")

        if commercial_report:
            notes.append(f"Commercial appeal score before drafting: {commercial_report.overall_score}.")

        for warning in prose_style_profile.get("warnings", []):
            notes.append(f"Style warning: {warning}")

        return notes

    def _warnings(self, *, blueprint: SceneBlueprint, sections: List[Dict[str, Any]], draft_text: str) -> List[str]:
        warnings = []

        if not sections:
            warnings.append("No sections generated.")

        if len(draft_text.split()) < 120:
            warnings.append("Draft is short and may need expansion.")

        if blueprint.secret_pressure and "secret" not in draft_text.lower():
            warnings.append("Blueprint has secret pressure, but draft barely references it.")

        if blueprint.relationship_pressure and "relationship" not in draft_text.lower() and "trust" not in draft_text.lower():
            warnings.append("Blueprint has relationship pressure, but draft may underuse it.")

        return warnings

    def _extract_ids(self, text: str, prefixes: List[str]) -> List[str]:
        values = []
        for raw in str(text).split():
            token = raw.strip(".,:;()[]{}")
            if any(token.startswith(prefix) for prefix in prefixes):
                values.append(token)
        return values

    def _unique(self, values: List[str]) -> List[str]:
        result = []
        seen = set()
        for value in values:
            if value and value not in seen:
                seen.add(value)
                result.append(value)
        return result

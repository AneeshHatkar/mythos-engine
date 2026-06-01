from __future__ import annotations

from typing import Any, Dict, List

from backend.app.schemas.story_generation import (
    DialogueBeat,
    GeneratedDialogueBlock,
    GeneratedDialogueLine,
    GeneratedSceneDraft,
    RelationshipBeat,
    SceneBlueprint,
)


class DialogueLineGenerator:
    """Generates dialogue lines from dialogue beats and voice rules.

    This layer turns dialogue planning into line-level text. It remains
    deterministic for testing, but its inputs are already shaped for future
    LLM-based dialogue generation.
    """

    engine_name = "story_generation.dialogue_line_generator"

    def generate_dialogue_block(
        self,
        *,
        blueprint: SceneBlueprint,
        scene_draft: GeneratedSceneDraft | None = None,
        dialogue_beats: List[DialogueBeat] | None = None,
        relationship_beats: List[RelationshipBeat] | None = None,
        prose_style_profile: Dict[str, Any] | None = None,
        story_context: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        dialogue_beats = dialogue_beats or []
        relationship_beats = relationship_beats or []
        prose_style_profile = prose_style_profile or {}
        story_context = story_context or {}

        selected_format = (
            prose_style_profile.get("selected_format")
            or (scene_draft.selected_format if scene_draft else "scene")
            or "scene"
        )

        lines: List[GeneratedDialogueLine] = []

        for index, beat in enumerate(dialogue_beats, start=1):
            line = self._generate_line(
                index=index,
                beat=beat,
                blueprint=blueprint,
                relationship_beats=relationship_beats,
                story_context=story_context,
            )
            lines.append(line)

        if not lines and blueprint.active_character_ids:
            lines.append(self._fallback_line(blueprint=blueprint))

        rendered_text = self._render_dialogue(lines=lines, selected_format=selected_format)

        block = GeneratedDialogueBlock(
            dialogue_block_id=f"dialogue_block_{blueprint.scene_id}",
            scene_id=blueprint.scene_id,
            selected_format=selected_format,
            lines=lines,
            rendered_text=rendered_text,
            used_speaker_ids=self._unique([line.speaker_id for line in lines]),
            used_dialogue_beat_ids=self._unique([line.dialogue_beat_id for line in lines]),
            warnings=self._warnings(lines=lines, dialogue_beats=dialogue_beats, blueprint=blueprint),
        )

        return {
            "success": True,
            "engine_name": self.engine_name,
            "dialogue_block": block,
            "dialogue_block_dict": block.model_dump(mode="json"),
            "handoff_to_next_engine": {
                "next_engine": "story_generation.scene_assembly_engine",
                "payload_keys": [
                    "scene_draft",
                    "dialogue_block",
                    "scene_blueprint",
                    "scene_beats",
                    "prose_style_profile",
                    "story_context",
                    "world_detail_pack",
                ],
            },
        }

    def merge_dialogue_into_draft(
        self,
        *,
        scene_draft: GeneratedSceneDraft,
        dialogue_block: GeneratedDialogueBlock,
    ) -> Dict[str, Any]:
        sections = list(scene_draft.sections)
        if dialogue_block.rendered_text:
            sections.append(
                {
                    "section_id": f"section_{dialogue_block.dialogue_block_id}",
                    "beat_id": None,
                    "beat_type": "generated_dialogue_block",
                    "tension_value": None,
                    "text": dialogue_block.rendered_text,
                    "causal_links": [],
                    "knowledge_constraints": [],
                }
            )

        draft_data = scene_draft.model_dump(mode="python")
        draft_data["sections"] = sections
        draft_data["draft_text"] = scene_draft.draft_text.rstrip() + "\n\n" + dialogue_block.rendered_text
        draft_data["used_character_ids"] = self._unique(scene_draft.used_character_ids + dialogue_block.used_speaker_ids)
        draft_data["generation_notes"] = scene_draft.generation_notes + [
            f"Merged dialogue block {dialogue_block.dialogue_block_id}."
        ]

        updated = GeneratedSceneDraft(**draft_data)

        return {
            "success": True,
            "engine_name": self.engine_name,
            "scene_draft": updated,
            "scene_draft_dict": updated.model_dump(mode="json"),
        }

    def validate_dialogue_block(self, *, dialogue_block: GeneratedDialogueBlock) -> Dict[str, Any]:
        blockers: List[str] = []
        warnings: List[str] = []
        passed: List[str] = []

        if not dialogue_block.dialogue_block_id:
            blockers.append("dialogue_block_id missing")
        else:
            passed.append("dialogue_block_id_present")

        if dialogue_block.lines:
            passed.append("dialogue_lines_present")
        else:
            blockers.append("dialogue lines missing")

        if dialogue_block.rendered_text and len(dialogue_block.rendered_text.strip()) >= 20:
            passed.append("rendered_text_present")
        else:
            blockers.append("rendered dialogue text missing or too short")

        if dialogue_block.used_speaker_ids:
            passed.append("speakers_used")
        else:
            warnings.append("no speakers recorded")

        if any(line.subtext for line in dialogue_block.lines):
            passed.append("subtext_preserved")
        else:
            warnings.append("no subtext preserved in generated lines")

        if any(line.secret_risk > 0 for line in dialogue_block.lines):
            passed.append("secret_risk_preserved")

        if dialogue_block.warnings:
            warnings.extend(dialogue_block.warnings)

        return {
            "success": True,
            "engine_name": self.engine_name,
            "valid": not blockers,
            "blockers": blockers,
            "warnings": warnings,
            "passed_checks": passed,
        }

    def summarize_dialogue_block(self, *, dialogue_block: GeneratedDialogueBlock) -> Dict[str, Any]:
        return {
            "success": True,
            "engine_name": self.engine_name,
            "summary": {
                "dialogue_block_id": dialogue_block.dialogue_block_id,
                "scene_id": dialogue_block.scene_id,
                "selected_format": dialogue_block.selected_format,
                "line_count": len(dialogue_block.lines),
                "speaker_count": len(dialogue_block.used_speaker_ids),
                "dialogue_beat_count": len(dialogue_block.used_dialogue_beat_ids),
                "average_secret_risk": self._average([line.secret_risk for line in dialogue_block.lines]),
                "relationship_effect_count": sum(1 for line in dialogue_block.lines if line.relationship_effect),
                "warning_count": len(dialogue_block.warnings),
            },
        }

    def _generate_line(
        self,
        *,
        index: int,
        beat: DialogueBeat,
        blueprint: SceneBlueprint,
        relationship_beats: List[RelationshipBeat],
        story_context: Dict[str, Any],
    ) -> GeneratedDialogueLine:
        voice_rules = beat.voice_rules or {}
        vocabulary_style = voice_rules.get("vocabulary_style") or voice_rules.get("voice_profile", {}).get("style") or "specific"
        emotion = beat.emotion or self._fallback_emotion(beat=beat, story_context=story_context)
        relationship_effect = beat.relationship_effect or self._relationship_effect(beat=beat, relationship_beats=relationship_beats)

        line_text = self._line_text(
            beat=beat,
            blueprint=blueprint,
            vocabulary_style=vocabulary_style,
            emotion=emotion,
        )

        warnings = []
        if beat.secret_risk >= 0.75 and self._looks_like_direct_secret_reveal(line_text):
            warnings.append("high secret risk line may reveal too much")

        if not beat.subtext and not beat.hidden_meaning:
            warnings.append("dialogue beat has weak subtext signal")

        return GeneratedDialogueLine(
            line_id=f"line_{blueprint.scene_id}_{index:02d}",
            scene_id=blueprint.scene_id,
            dialogue_beat_id=beat.dialogue_beat_id,
            speaker_id=beat.speaker_id,
            listener_ids=beat.listener_ids,
            line_text=line_text,
            subtext=beat.subtext,
            hidden_meaning=beat.hidden_meaning,
            emotion=emotion,
            secret_risk=beat.secret_risk,
            relationship_effect=relationship_effect,
            voice_rules_used=voice_rules,
            warnings=warnings,
        )

    def _line_text(
        self,
        *,
        beat: DialogueBeat,
        blueprint: SceneBlueprint,
        vocabulary_style: str,
        emotion: str | None,
    ) -> str:
        speaker = beat.speaker_id
        objective = blueprint.scene_objective or "this choice"
        surface = beat.surface_meaning or "the pressure in the room"
        subtext = beat.subtext or beat.hidden_meaning or "what remains unsaid"

        if vocabulary_style in {"precise", "controlled"}:
            return f'"Do not mistake silence for surrender," {speaker} says. "I heard {surface.lower()}, and I know what it costs."'

        if vocabulary_style in {"plain_defensive", "guarded"}:
            return f'"Then say it plainly," {speaker} says. "Because {objective.lower()} is not going to wait for your silence."'

        if emotion == "guilt":
            return f'"I am not denying it," {speaker} says, each word measured around {subtext}.'

        if beat.secret_risk >= 0.7:
            return f'"There are things I cannot name here," {speaker} says. "Not without making this worse."'

        return f'"This is not over," {speaker} says. "Not while {surface.lower()} still matters."'

    def _fallback_line(self, *, blueprint: SceneBlueprint) -> GeneratedDialogueLine:
        speaker_id = blueprint.pov_character_id or blueprint.active_character_ids[0]
        listeners = [cid for cid in blueprint.active_character_ids if cid != speaker_id]

        return GeneratedDialogueLine(
            line_id=f"line_{blueprint.scene_id}_fallback",
            scene_id=blueprint.scene_id,
            dialogue_beat_id="fallback_dialogue_beat",
            speaker_id=speaker_id,
            listener_ids=listeners,
            line_text=f'"This choice has a cost," {speaker_id} says.',
            subtext="the scene needs dialogue pressure",
            hidden_meaning="fallback line generated because no dialogue beats were supplied",
            emotion=None,
            secret_risk=0.0,
            relationship_effect=None,
            voice_rules_used={},
            warnings=["fallback dialogue generated"],
        )

    def _render_dialogue(self, *, lines: List[GeneratedDialogueLine], selected_format: str) -> str:
        if selected_format == "screenplay":
            rendered = []
            for line in lines:
                rendered.append(f"{line.speaker_id.upper()}\n{line.line_text.strip(chr(34))}")
            return "\n\n".join(rendered)

        return "\n".join(f"{line.speaker_id}: {line.line_text}" for line in lines)

    def _fallback_emotion(self, *, beat: DialogueBeat, story_context: Dict[str, Any]) -> str | None:
        for item in story_context.get("emotional_pressure", []):
            if item.get("character_id") == beat.speaker_id:
                return item.get("dominant_emotion")
        return None

    def _relationship_effect(self, *, beat: DialogueBeat, relationship_beats: List[RelationshipBeat]) -> str | None:
        participants = {beat.speaker_id, *beat.listener_ids}
        for relationship in relationship_beats:
            if relationship.character_a_id in participants and relationship.character_b_id in participants:
                return f"{relationship.relationship_id}: {relationship.expected_end_state_shift}"
        return None

    def _looks_like_direct_secret_reveal(self, line_text: str) -> bool:
        lowered = line_text.lower()
        return "secret_" in lowered or "major_mystery" in lowered

    def _warnings(
        self,
        *,
        lines: List[GeneratedDialogueLine],
        dialogue_beats: List[DialogueBeat],
        blueprint: SceneBlueprint,
    ) -> List[str]:
        warnings = []

        if len(lines) < len(dialogue_beats):
            warnings.append("some dialogue beats did not produce lines")

        if blueprint.secret_pressure and not any(line.secret_risk > 0 for line in lines):
            warnings.append("blueprint has secret pressure but generated lines have no secret risk")

        if blueprint.relationship_pressure and not any(line.relationship_effect for line in lines):
            warnings.append("blueprint has relationship pressure but generated lines have no relationship effect")

        warnings.extend([warning for line in lines for warning in line.warnings])

        return self._unique(warnings)

    def _average(self, values: List[float]) -> float:
        if not values:
            return 0.0
        return round(sum(values) / len(values), 3)

    def _unique(self, values: List[str]) -> List[str]:
        result = []
        seen = set()
        for value in values:
            if value and value not in seen:
                seen.add(value)
                result.append(value)
        return result

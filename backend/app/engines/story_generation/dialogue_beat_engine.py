from __future__ import annotations

from typing import Any, Dict, List

from backend.app.schemas.story_generation import DialogueBeat, SceneBeat, SceneBlueprint


class DialogueBeatEngine:
    """Creates subtext-aware dialogue beats from scene beats.

    This engine does not write final dialogue lines yet. It plans who speaks,
    who listens, what the line seems to mean, what it secretly means, how much
    secret risk it carries, and how the relationship shifts.
    """

    engine_name = "story_generation.dialogue_beat_engine"

    DIALOGUE_RELEVANT_BEATS = {
        "relationship_pressure",
        "secret_pressure",
        "dialogue_pressure",
        "choice",
        "consequence",
        "ending_hook",
    }

    def build_dialogue_beats(
        self,
        *,
        blueprint: SceneBlueprint,
        scene_beats: List[SceneBeat],
        story_context: Dict[str, Any],
    ) -> Dict[str, Any]:
        active_cast = story_context.get("active_cast", [])
        speaker_order = self._speaker_order(blueprint=blueprint, active_cast=active_cast)

        dialogue_beats: List[DialogueBeat] = []

        for beat in scene_beats:
            if beat.beat_type not in self.DIALOGUE_RELEVANT_BEATS:
                continue

            speaker_id = self._select_speaker(
                beat=beat,
                blueprint=blueprint,
                speaker_order=speaker_order,
                index=len(dialogue_beats),
            )
            listener_ids = self._listeners(
                speaker_id=speaker_id,
                active_character_ids=blueprint.active_character_ids,
            )

            dialogue_beats.append(
                DialogueBeat(
                    dialogue_beat_id=f"dialogue_{blueprint.scene_id}_{len(dialogue_beats) + 1:02d}_{beat.beat_type}",
                    scene_id=blueprint.scene_id,
                    speaker_id=speaker_id,
                    listener_ids=listener_ids,
                    surface_meaning=self._surface_meaning(beat=beat, speaker_id=speaker_id),
                    hidden_meaning=self._hidden_meaning(beat=beat, story_context=story_context),
                    subtext=self._subtext(beat=beat, story_context=story_context),
                    emotion=self._speaker_emotion(speaker_id=speaker_id, story_context=story_context),
                    secret_risk=self._secret_risk(beat=beat),
                    power_shift=self._power_shift(beat=beat),
                    relationship_effect=self._relationship_effect(beat=beat, story_context=story_context),
                    voice_rules=self._voice_rules_placeholder(speaker_id=speaker_id, active_cast=active_cast),
                )
            )

        warnings = self._warnings(dialogue_beats=dialogue_beats, blueprint=blueprint)

        return {
            "success": True,
            "engine_name": self.engine_name,
            "dialogue_beats": dialogue_beats,
            "dialogue_beats_dict": [beat.model_dump(mode="json") for beat in dialogue_beats],
            "dialogue_beat_count": len(dialogue_beats),
            "warnings": warnings,
            "handoff_to_next_engine": {
                "next_engine": "story_generation.character_voice_engine",
                "payload_keys": [
                    "dialogue_beats",
                    "active_cast",
                    "story_context",
                    "scene_blueprint",
                ],
            },
        }

    def validate_dialogue_beats(
        self,
        *,
        dialogue_beats: List[DialogueBeat],
        blueprint: SceneBlueprint,
    ) -> Dict[str, Any]:
        blockers: List[str] = []
        warnings: List[str] = []
        passed: List[str] = []

        if not dialogue_beats:
            blockers.append("no dialogue beats generated")
        else:
            passed.append("dialogue_beats_present")

        if all(beat.speaker_id for beat in dialogue_beats):
            passed.append("speakers_present")
        else:
            blockers.append("one or more dialogue beats missing speaker_id")

        if all(beat.surface_meaning for beat in dialogue_beats):
            passed.append("surface_meaning_present")
        else:
            blockers.append("one or more dialogue beats missing surface meaning")

        if any(beat.subtext for beat in dialogue_beats):
            passed.append("subtext_present")
        else:
            warnings.append("no subtext found in dialogue beats")

        if any(beat.secret_risk > 0 for beat in dialogue_beats):
            passed.append("secret_risk_tracked")
        elif blueprint.secret_pressure:
            warnings.append("blueprint has secret pressure but no dialogue beat tracks secret risk")

        if any(beat.relationship_effect for beat in dialogue_beats):
            passed.append("relationship_effect_tracked")
        elif blueprint.relationship_pressure:
            warnings.append("blueprint has relationship pressure but no dialogue beat tracks relationship effect")

        invalid_speakers = [
            beat.speaker_id
            for beat in dialogue_beats
            if beat.speaker_id not in blueprint.active_character_ids
        ]

        if invalid_speakers:
            blockers.append(f"dialogue speakers outside active cast: {sorted(set(invalid_speakers))}")
        else:
            passed.append("speakers_are_active_characters")

        return {
            "success": True,
            "engine_name": self.engine_name,
            "valid": not blockers,
            "blockers": blockers,
            "warnings": warnings,
            "passed_checks": passed,
        }

    def summarize_dialogue_beats(self, *, dialogue_beats: List[DialogueBeat]) -> Dict[str, Any]:
        speaker_counts: Dict[str, int] = {}
        for beat in dialogue_beats:
            speaker_counts[beat.speaker_id] = speaker_counts.get(beat.speaker_id, 0) + 1

        return {
            "success": True,
            "engine_name": self.engine_name,
            "summary": {
                "dialogue_beat_count": len(dialogue_beats),
                "speaker_counts": speaker_counts,
                "average_secret_risk": self._average([beat.secret_risk for beat in dialogue_beats]),
                "subtext_count": sum(1 for beat in dialogue_beats if beat.subtext),
                "relationship_effect_count": sum(1 for beat in dialogue_beats if beat.relationship_effect),
                "power_shift_count": sum(1 for beat in dialogue_beats if beat.power_shift),
            },
        }

    def _speaker_order(
        self,
        *,
        blueprint: SceneBlueprint,
        active_cast: List[Dict[str, Any]],
    ) -> List[str]:
        order = []

        if blueprint.pov_character_id:
            order.append(blueprint.pov_character_id)

        # Add emotionally pressured / required characters early.
        required = [
            item.get("character_id")
            for item in active_cast
            if item.get("required") and item.get("character_id")
        ]
        for cid in required:
            if cid not in order:
                order.append(cid)

        for cid in blueprint.active_character_ids:
            if cid not in order:
                order.append(cid)

        return order or blueprint.active_character_ids

    def _select_speaker(
        self,
        *,
        beat: SceneBeat,
        blueprint: SceneBlueprint,
        speaker_order: List[str],
        index: int,
    ) -> str:
        if beat.beat_type in {"choice", "ending_hook"} and blueprint.pov_character_id:
            return blueprint.pov_character_id

        if speaker_order:
            return speaker_order[index % len(speaker_order)]

        if blueprint.active_character_ids:
            return blueprint.active_character_ids[0]

        return "unknown_speaker"

    def _listeners(self, *, speaker_id: str, active_character_ids: List[str]) -> List[str]:
        return [cid for cid in active_character_ids if cid != speaker_id]

    def _surface_meaning(self, *, beat: SceneBeat, speaker_id: str) -> str:
        mapping = {
            "relationship_pressure": f"{speaker_id} responds to relationship pressure.",
            "secret_pressure": f"{speaker_id} speaks around dangerous information.",
            "dialogue_pressure": f"{speaker_id} pushes the conversation under pressure.",
            "choice": f"{speaker_id} states or avoids a choice.",
            "consequence": f"{speaker_id} reacts to the consequence.",
            "ending_hook": f"{speaker_id} leaves the scene with unresolved pressure.",
        }

        return mapping.get(beat.beat_type, beat.purpose)

    def _hidden_meaning(self, *, beat: SceneBeat, story_context: Dict[str, Any]) -> str | None:
        if beat.beat_type == "secret_pressure":
            return "The speaker is protecting, hiding, or testing access to secret knowledge."

        if beat.beat_type == "relationship_pressure":
            return "The speaker is saying one thing while measuring trust, resentment, or betrayal."

        if beat.beat_type == "choice":
            return "The choice reveals what the speaker values more than what they claim."

        if beat.beat_type == "ending_hook":
            return "The unresolved pressure points toward the next scene."

        if beat.knowledge_constraints:
            return "The speaker is constrained by what they know or cannot reveal."

        return None

    def _subtext(self, *, beat: SceneBeat, story_context: Dict[str, Any]) -> str | None:
        if beat.beat_type == "secret_pressure":
            return "avoidance, misdirection, and fear of exposure"

        if beat.beat_type == "relationship_pressure":
            return "hurt disguised as control"

        if beat.beat_type == "dialogue_pressure":
            return "the real conflict sits underneath the spoken topic"

        if beat.beat_type == "choice":
            return "agency under emotional cost"

        if beat.beat_type == "consequence":
            return "the result matters more than the explanation"

        if beat.beat_type == "ending_hook":
            return "something important remains unsaid"

        return None

    def _speaker_emotion(self, *, speaker_id: str, story_context: Dict[str, Any]) -> str | None:
        for item in story_context.get("emotional_pressure", []):
            if item.get("character_id") == speaker_id:
                return item.get("dominant_emotion")

        # fallback: if no specific emotion, use highest pressure emotion
        pressures = story_context.get("emotional_pressure", [])
        if pressures:
            return pressures[0].get("dominant_emotion")

        return None

    def _secret_risk(self, *, beat: SceneBeat) -> float:
        if beat.beat_type == "secret_pressure":
            return 0.85
        if beat.knowledge_constraints:
            return 0.55
        if beat.beat_type in {"choice", "ending_hook"}:
            return 0.35
        return 0.0

    def _power_shift(self, *, beat: SceneBeat) -> str | None:
        if beat.beat_type == "relationship_pressure":
            return "power shifts toward whoever controls the emotional truth"

        if beat.beat_type == "secret_pressure":
            return "power shifts toward whoever knows more than they reveal"

        if beat.beat_type == "choice":
            return "power shifts through the chosen action"

        if beat.beat_type == "consequence":
            return "power shifts because the story state changes"

        return None

    def _relationship_effect(self, *, beat: SceneBeat, story_context: Dict[str, Any]) -> str | None:
        if beat.relationship_change_hint:
            return beat.relationship_change_hint

        if beat.beat_type in {"relationship_pressure", "secret_pressure", "choice", "consequence", "ending_hook"}:
            pressure = story_context.get("relationship_pressure", [])
            if pressure:
                return f"Dialogue should affect {pressure[0].get('relationship_id')}."

        return None

    def _voice_rules_placeholder(
        self,
        *,
        speaker_id: str,
        active_cast: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        for character in active_cast:
            if character.get("character_id") == speaker_id:
                voice = character.get("voice_profile", {})
                if isinstance(voice, dict) and voice:
                    return {
                        "source": "character_voice_profile",
                        "voice_profile": voice,
                    }

        return {
            "source": "pending_character_voice_engine",
            "note": "CharacterVoiceEngine will expand this into detailed voice instructions.",
        }

    def _warnings(self, *, dialogue_beats: List[DialogueBeat], blueprint: SceneBlueprint) -> List[str]:
        warnings = []

        if not dialogue_beats:
            warnings.append("No dialogue beats generated.")

        if len(blueprint.active_character_ids) < 2:
            warnings.append("Only one active character; dialogue may require internal monologue or off-page pressure.")

        if blueprint.secret_pressure and not any(beat.secret_risk > 0 for beat in dialogue_beats):
            warnings.append("Secret pressure exists but no dialogue beat carries secret risk.")

        if blueprint.relationship_pressure and not any(beat.relationship_effect for beat in dialogue_beats):
            warnings.append("Relationship pressure exists but no dialogue beat carries relationship effect.")

        return warnings

    def _average(self, values: List[float]) -> float:
        if not values:
            return 0.0
        return round(sum(values) / len(values), 3)

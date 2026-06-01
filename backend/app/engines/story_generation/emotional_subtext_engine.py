from __future__ import annotations

from typing import Any, Dict, List

from backend.app.schemas.story_generation import (
    CharacterVoiceInstruction,
    DialogueBeat,
    EmotionalSubtextInstruction,
)


class EmotionalSubtextEngine:
    """Turns character emotions into usable writing behavior.

    This engine makes emotion actionable for later prose/dialogue generation.
    Instead of saying "Seren feels guilty", it creates rules like:
    - avoids direct answers
    - pauses before truthful words
    - speaks precisely to hide panic
    - lets emotion leak through silence
    """

    engine_name = "story_generation.emotional_subtext_engine"

    EMOTION_BEHAVIOR_MAP = {
        "guilt": {
            "body": ["still hands", "eyes lowered after hard questions", "delayed eye contact"],
            "dialogue": ["answers one step beside the truth", "over-explains harmless facts", "avoids naming the victim"],
            "internal": ["measures every word against what it might cost someone else"],
            "leakage": ["truth leaks through pauses, not confessions"],
        },
        "shame": {
            "body": ["tight jaw", "chin lowered before defiance", "shoulders held too still"],
            "dialogue": ["turns accusation into factual correction", "rejects pity quickly"],
            "internal": ["notices who is watching before noticing what is said"],
            "leakage": ["anger appears where hurt should be"],
        },
        "resolve": {
            "body": ["steady posture", "direct attention", "controlled breathing"],
            "dialogue": ["names facts plainly", "refuses rhetorical escape routes"],
            "internal": ["narrows the world to the next necessary action"],
            "leakage": ["fear shows only after the decision is made"],
        },
        "fear": {
            "body": ["checks exits", "flinches at sudden silence", "keeps distance from authority"],
            "dialogue": ["asks indirect questions", "keeps sentences short", "tests safety before honesty"],
            "internal": ["calculates danger before desire"],
            "leakage": ["control becomes brittle"],
        },
        "rage": {
            "body": ["sharp movement", "stillness before impact", "hands closing around objects"],
            "dialogue": ["clips sentences", "uses names like weapons", "refuses softeners"],
            "internal": ["turns pain into a target"],
            "leakage": ["precision fails when the wound is touched"],
        },
        "longing": {
            "body": ["almost reaches out", "stays close after the conversation ends", "watches when unseen"],
            "dialogue": ["asks practical questions with emotional weight", "says less than the feeling requires"],
            "internal": ["notices small details that should not matter"],
            "leakage": ["care appears as restraint"],
        },
        "grief": {
            "body": ["delayed reactions", "touches old objects", "moves as if sound is too loud"],
            "dialogue": ["speaks in fragments", "uses past tense by accident"],
            "internal": ["returns to the missing person or lost possibility"],
            "leakage": ["ordinary details become unbearable"],
        },
        "jealousy": {
            "body": ["watches comparisons", "smiles too late", "turns away at intimacy"],
            "dialogue": ["asks questions that sound neutral but are not", "minimizes what hurts"],
            "internal": ["tracks who receives attention and why"],
            "leakage": ["sarcasm covers fear of replacement"],
        },
        "hope": {
            "body": ["leans forward", "voice warms before logic catches up", "breath releases"],
            "dialogue": ["allows one honest future-tense sentence", "risks a softer word"],
            "internal": ["imagines the impossible before rejecting it"],
            "leakage": ["guard drops for a moment"],
        },
    }

    def build_emotional_subtext(
        self,
        *,
        active_cast: List[Dict[str, Any]],
        voice_instructions: List[CharacterVoiceInstruction] | None = None,
        dialogue_beats: List[DialogueBeat] | None = None,
        story_context: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        voice_instructions = voice_instructions or []
        dialogue_beats = dialogue_beats or []
        story_context = story_context or {}

        voice_by_character = {item.character_id: item for item in voice_instructions}
        instructions: List[EmotionalSubtextInstruction] = []

        for character in active_cast:
            character_id = character.get("character_id")
            if not character_id:
                continue

            emotional_state = self._emotional_state_for_character(
                character_id=character_id,
                character=character,
                story_context=story_context,
            )
            dominant_emotion, intensity = self._dominant_emotion(emotional_state)

            beat_pressure = self._beat_pressure(character_id=character_id, dialogue_beats=dialogue_beats)
            voice = voice_by_character.get(character_id)

            instruction = EmotionalSubtextInstruction(
                character_id=character_id,
                dominant_emotion=dominant_emotion,
                intensity=intensity,
                body_language_hints=self._body_language(
                    dominant_emotion=dominant_emotion,
                    intensity=intensity,
                    beat_pressure=beat_pressure,
                ),
                dialogue_pressure_hints=self._dialogue_pressure(
                    dominant_emotion=dominant_emotion,
                    intensity=intensity,
                    beat_pressure=beat_pressure,
                    voice=voice,
                ),
                internal_narration_hints=self._internal_narration(
                    dominant_emotion=dominant_emotion,
                    intensity=intensity,
                    character=character,
                ),
                emotional_leakage_rules=self._leakage_rules(
                    dominant_emotion=dominant_emotion,
                    intensity=intensity,
                    beat_pressure=beat_pressure,
                    voice=voice,
                ),
            )

            instructions.append(instruction)

        warnings = self._warnings(instructions=instructions, active_cast=active_cast)

        return {
            "success": True,
            "engine_name": self.engine_name,
            "emotional_subtext_instructions": instructions,
            "emotional_subtext_dict": [item.model_dump(mode="json") for item in instructions],
            "warnings": warnings,
            "handoff_to_next_engine": {
                "next_engine": "story_generation.relationship_beat_engine",
                "payload_keys": [
                    "emotional_subtext_instructions",
                    "voice_instructions",
                    "dialogue_beats",
                    "story_context",
                ],
            },
        }

    def apply_subtext_to_dialogue_beats(
        self,
        *,
        dialogue_beats: List[DialogueBeat],
        emotional_subtext: List[EmotionalSubtextInstruction],
    ) -> Dict[str, Any]:
        subtext_by_character = {item.character_id: item for item in emotional_subtext}
        updated: List[DialogueBeat] = []

        for beat in dialogue_beats:
            instruction = subtext_by_character.get(beat.speaker_id)
            if not instruction:
                updated.append(beat)
                continue

            data = beat.model_dump(mode="python")
            existing = data.get("voice_rules", {}) or {}
            existing["emotional_subtext"] = {
                "dominant_emotion": instruction.dominant_emotion,
                "intensity": instruction.intensity,
                "body_language_hints": instruction.body_language_hints,
                "dialogue_pressure_hints": instruction.dialogue_pressure_hints,
                "emotional_leakage_rules": instruction.emotional_leakage_rules,
            }
            data["voice_rules"] = existing

            if not data.get("emotion"):
                data["emotion"] = instruction.dominant_emotion

            if not data.get("subtext"):
                data["subtext"] = self._fallback_subtext(instruction)

            updated.append(DialogueBeat(**data))

        return {
            "success": True,
            "engine_name": self.engine_name,
            "dialogue_beats": updated,
            "dialogue_beats_dict": [beat.model_dump(mode="json") for beat in updated],
        }

    def validate_emotional_subtext(
        self,
        *,
        emotional_subtext: List[EmotionalSubtextInstruction],
    ) -> Dict[str, Any]:
        blockers: List[str] = []
        warnings: List[str] = []
        passed: List[str] = []

        if not emotional_subtext:
            blockers.append("no emotional subtext instructions generated")
        else:
            passed.append("emotional_subtext_present")

        if all(item.character_id for item in emotional_subtext):
            passed.append("character_ids_present")
        else:
            blockers.append("one or more emotional subtext instructions missing character_id")

        if all(item.dominant_emotion for item in emotional_subtext):
            passed.append("dominant_emotions_present")
        else:
            warnings.append("one or more characters missing dominant emotion")

        if all(item.body_language_hints for item in emotional_subtext):
            passed.append("body_language_hints_present")
        else:
            warnings.append("one or more characters missing body language hints")

        if all(item.dialogue_pressure_hints for item in emotional_subtext):
            passed.append("dialogue_pressure_hints_present")
        else:
            warnings.append("one or more characters missing dialogue pressure hints")

        if all(0.0 <= item.intensity <= 1.0 for item in emotional_subtext):
            passed.append("emotion_intensities_bounded")
        else:
            blockers.append("one or more emotion intensities out of bounds")

        return {
            "success": True,
            "engine_name": self.engine_name,
            "valid": not blockers,
            "blockers": blockers,
            "warnings": warnings,
            "passed_checks": passed,
        }

    def summarize_emotional_subtext(
        self,
        *,
        emotional_subtext: List[EmotionalSubtextInstruction],
    ) -> Dict[str, Any]:
        emotion_counts: Dict[str, int] = {}
        for item in emotional_subtext:
            emotion_counts[item.dominant_emotion] = emotion_counts.get(item.dominant_emotion, 0) + 1

        return {
            "success": True,
            "engine_name": self.engine_name,
            "summary": {
                "instruction_count": len(emotional_subtext),
                "emotion_counts": emotion_counts,
                "average_intensity": self._average([item.intensity for item in emotional_subtext]),
                "body_language_hint_count": sum(len(item.body_language_hints) for item in emotional_subtext),
                "dialogue_pressure_hint_count": sum(len(item.dialogue_pressure_hints) for item in emotional_subtext),
                "leakage_rule_count": sum(len(item.emotional_leakage_rules) for item in emotional_subtext),
            },
        }

    def _emotional_state_for_character(
        self,
        *,
        character_id: str,
        character: Dict[str, Any],
        story_context: Dict[str, Any],
    ) -> Dict[str, Any]:
        if isinstance(character.get("emotional_state"), dict) and character["emotional_state"]:
            return character["emotional_state"]

        for item in story_context.get("emotional_pressure", []):
            if item.get("character_id") == character_id:
                emotion = item.get("dominant_emotion")
                intensity = item.get("dominant_intensity", 0.5)
                if emotion:
                    return {emotion: intensity}

        return {"controlled_pressure": 0.5}

    def _dominant_emotion(self, emotional_state: Dict[str, Any]) -> tuple[str, float]:
        if not emotional_state:
            return "controlled_pressure", 0.5

        try:
            emotion, value = max(emotional_state.items(), key=lambda item: float(item[1]))
            return str(emotion), max(0.0, min(1.0, float(value)))
        except Exception:
            emotion = next(iter(emotional_state.keys()), "controlled_pressure")
            return str(emotion), 0.5

    def _beat_pressure(
        self,
        *,
        character_id: str,
        dialogue_beats: List[DialogueBeat],
    ) -> Dict[str, Any]:
        relevant = [beat for beat in dialogue_beats if beat.speaker_id == character_id]

        return {
            "beat_count": len(relevant),
            "secret_risk": self._average([beat.secret_risk for beat in relevant]),
            "has_power_shift": any(bool(beat.power_shift) for beat in relevant),
            "has_relationship_effect": any(bool(beat.relationship_effect) for beat in relevant),
            "has_hidden_meaning": any(bool(beat.hidden_meaning) for beat in relevant),
        }

    def _body_language(
        self,
        *,
        dominant_emotion: str,
        intensity: float,
        beat_pressure: Dict[str, Any],
    ) -> List[str]:
        base = list(self.EMOTION_BEHAVIOR_MAP.get(dominant_emotion, {}).get("body", []))

        if not base:
            base = ["emotion appears through posture before words"]

        if intensity >= 0.75:
            base.append("the body betrays what the voice tries to control")

        if beat_pressure.get("secret_risk", 0.0) > 0.5:
            base.append("small physical hesitation before dangerous information")

        return base[:5]

    def _dialogue_pressure(
        self,
        *,
        dominant_emotion: str,
        intensity: float,
        beat_pressure: Dict[str, Any],
        voice: CharacterVoiceInstruction | None,
    ) -> List[str]:
        base = list(self.EMOTION_BEHAVIOR_MAP.get(dominant_emotion, {}).get("dialogue", []))

        if not base:
            base = ["speech should reveal pressure indirectly"]

        if voice and voice.subtext_style:
            base.append(f"use voice subtext style: {voice.subtext_style}")

        if beat_pressure.get("secret_risk", 0.0) > 0.5:
            base.append("avoid direct naming of the secret unless the scene requires a reveal")

        if beat_pressure.get("has_relationship_effect"):
            base.append("let the relationship shift underneath the spoken topic")

        if intensity >= 0.85:
            base.append("allow one controlled break in the character's normal speech pattern")

        return base[:6]

    def _internal_narration(
        self,
        *,
        dominant_emotion: str,
        intensity: float,
        character: Dict[str, Any],
    ) -> List[str]:
        base = list(self.EMOTION_BEHAVIOR_MAP.get(dominant_emotion, {}).get("internal", []))

        if not base:
            base = ["internal narration should reveal what dialogue hides"]

        display_name = character.get("display_name", character.get("character_id", "the character"))
        if intensity >= 0.7:
            base.append(f"{display_name}'s inner focus should narrow around the emotional threat")

        return base[:5]

    def _leakage_rules(
        self,
        *,
        dominant_emotion: str,
        intensity: float,
        beat_pressure: Dict[str, Any],
        voice: CharacterVoiceInstruction | None,
    ) -> List[str]:
        base = list(self.EMOTION_BEHAVIOR_MAP.get(dominant_emotion, {}).get("leakage", []))

        if not base:
            base = ["emotion leaks through hesitation, over-control, or redirected attention"]

        if voice and voice.silence_behavior:
            base.append(f"silence behavior: {voice.silence_behavior}")

        if beat_pressure.get("has_power_shift"):
            base.append("emotional leakage should alter who controls the exchange")

        if intensity >= 0.8:
            base.append("subtext should briefly become visible before being controlled again")

        return base[:6]

    def _fallback_subtext(self, instruction: EmotionalSubtextInstruction) -> str:
        return f"{instruction.dominant_emotion} shapes what the character cannot say directly"

    def _average(self, values: List[float]) -> float:
        if not values:
            return 0.0
        return round(sum(values) / len(values), 3)

    def _warnings(
        self,
        *,
        instructions: List[EmotionalSubtextInstruction],
        active_cast: List[Dict[str, Any]],
    ) -> List[str]:
        warnings = []

        if not instructions:
            warnings.append("No emotional subtext instructions generated.")

        if len(instructions) < len([item for item in active_cast if item.get("character_id")]):
            warnings.append("Some active cast members did not receive emotional subtext instructions.")

        weak = [
            item.character_id
            for item in instructions
            if item.dominant_emotion == "controlled_pressure" and item.intensity <= 0.5
        ]
        if weak:
            warnings.append(f"Weak emotional signal for: {', '.join(weak)}")

        return warnings

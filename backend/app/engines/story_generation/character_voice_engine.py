from __future__ import annotations

from typing import Any, Dict, List

from backend.app.schemas.story_generation import CharacterVoiceInstruction, DialogueBeat


class CharacterVoiceEngine:
    """Builds character-specific voice instructions for dialogue and prose.

    This prevents interchangeable characters by translating character metadata,
    emotional pressure, role tags, and existing voice profile hints into
    structured voice rules.
    """

    engine_name = "story_generation.character_voice_engine"

    def build_voice_instructions(
        self,
        *,
        active_cast: List[Dict[str, Any]],
        dialogue_beats: List[DialogueBeat] | None = None,
        story_context: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        dialogue_beats = dialogue_beats or []
        story_context = story_context or {}

        instructions: List[CharacterVoiceInstruction] = []

        for character in active_cast:
            character_id = character.get("character_id")
            if not character_id:
                continue

            voice_profile = character.get("voice_profile", {}) if isinstance(character.get("voice_profile", {}), dict) else {}
            emotional_state = character.get("emotional_state", {}) if isinstance(character.get("emotional_state", {}), dict) else {}
            role_tags = character.get("role_tags", []) or []
            story_function_tags = character.get("story_function_tags", []) or []

            beat_pressure = self._dialogue_pressure_for_character(
                character_id=character_id,
                dialogue_beats=dialogue_beats,
            )

            instruction = CharacterVoiceInstruction(
                character_id=character_id,
                formality=self._formality(voice_profile=voice_profile, role_tags=role_tags),
                sentence_length=self._sentence_length(voice_profile=voice_profile, emotional_state=emotional_state),
                vocabulary_style=self._vocabulary_style(voice_profile=voice_profile, role_tags=role_tags),
                rhythm=self._rhythm(voice_profile=voice_profile, emotional_state=emotional_state),
                humor_style=self._humor_style(voice_profile=voice_profile, role_tags=role_tags),
                anger_behavior=self._anger_behavior(voice_profile=voice_profile, emotional_state=emotional_state),
                fear_behavior=self._fear_behavior(voice_profile=voice_profile, emotional_state=emotional_state),
                romance_behavior=self._romance_behavior(
                    voice_profile=voice_profile,
                    role_tags=role_tags,
                    story_function_tags=story_function_tags,
                    beat_pressure=beat_pressure,
                ),
                silence_behavior=self._silence_behavior(voice_profile=voice_profile, emotional_state=emotional_state),
                subtext_style=self._subtext_style(voice_profile=voice_profile, beat_pressure=beat_pressure),
                power_behavior=self._power_behavior(voice_profile=voice_profile, role_tags=role_tags),
                forbidden_phrases=self._forbidden_phrases(voice_profile=voice_profile),
                signature_phrases=self._signature_phrases(voice_profile=voice_profile),
                metadata={
                    "display_name": character.get("display_name", character_id),
                    "source_voice_profile": voice_profile,
                    "role_tags": role_tags,
                    "story_function_tags": story_function_tags,
                    "dominant_emotion": self._dominant_emotion(emotional_state),
                    "dialogue_pressure": beat_pressure,
                    "voice_distinctiveness_score": self._distinctiveness_score(
                        voice_profile=voice_profile,
                        emotional_state=emotional_state,
                        role_tags=role_tags,
                        beat_pressure=beat_pressure,
                    ),
                },
            )

            instructions.append(instruction)

        warnings = self._warnings(instructions=instructions, active_cast=active_cast)

        return {
            "success": True,
            "engine_name": self.engine_name,
            "voice_instructions": instructions,
            "voice_instructions_dict": [item.model_dump(mode="json") for item in instructions],
            "warnings": warnings,
            "handoff_to_next_engine": {
                "next_engine": "story_generation.emotional_subtext_engine",
                "payload_keys": [
                    "voice_instructions",
                    "dialogue_beats",
                    "story_context",
                    "active_cast",
                ],
            },
        }

    def apply_voice_to_dialogue_beats(
        self,
        *,
        dialogue_beats: List[DialogueBeat],
        voice_instructions: List[CharacterVoiceInstruction],
    ) -> Dict[str, Any]:
        voice_by_character = {item.character_id: item for item in voice_instructions}
        updated: List[DialogueBeat] = []

        for beat in dialogue_beats:
            instruction = voice_by_character.get(beat.speaker_id)
            if instruction:
                data = beat.model_dump(mode="python")
                data["voice_rules"] = {
                    "source": "character_voice_engine",
                    "formality": instruction.formality,
                    "sentence_length": instruction.sentence_length,
                    "vocabulary_style": instruction.vocabulary_style,
                    "rhythm": instruction.rhythm,
                    "humor_style": instruction.humor_style,
                    "anger_behavior": instruction.anger_behavior,
                    "fear_behavior": instruction.fear_behavior,
                    "romance_behavior": instruction.romance_behavior,
                    "silence_behavior": instruction.silence_behavior,
                    "subtext_style": instruction.subtext_style,
                    "power_behavior": instruction.power_behavior,
                    "forbidden_phrases": instruction.forbidden_phrases,
                    "signature_phrases": instruction.signature_phrases,
                }
                updated.append(DialogueBeat(**data))
            else:
                updated.append(beat)

        return {
            "success": True,
            "engine_name": self.engine_name,
            "dialogue_beats": updated,
            "dialogue_beats_dict": [beat.model_dump(mode="json") for beat in updated],
        }

    def validate_voice_instructions(
        self,
        *,
        voice_instructions: List[CharacterVoiceInstruction],
    ) -> Dict[str, Any]:
        blockers: List[str] = []
        warnings: List[str] = []
        passed: List[str] = []

        if not voice_instructions:
            blockers.append("no voice instructions generated")
        else:
            passed.append("voice_instructions_present")

        if all(item.character_id for item in voice_instructions):
            passed.append("character_ids_present")
        else:
            blockers.append("one or more voice instructions missing character_id")

        if all(item.vocabulary_style for item in voice_instructions):
            passed.append("vocabulary_styles_present")
        else:
            warnings.append("one or more characters missing vocabulary style")

        if all(item.rhythm for item in voice_instructions):
            passed.append("rhythms_present")
        else:
            warnings.append("one or more characters missing rhythm")

        distinctiveness_scores = [
            item.metadata.get("voice_distinctiveness_score", 0.0)
            for item in voice_instructions
        ]

        if distinctiveness_scores and max(distinctiveness_scores) >= 0.5:
            passed.append("voice_distinctiveness_usable")
        else:
            warnings.append("voice distinctiveness is weak; characters may sound similar")

        return {
            "success": True,
            "engine_name": self.engine_name,
            "valid": not blockers,
            "blockers": blockers,
            "warnings": warnings,
            "passed_checks": passed,
        }

    def summarize_voice_instructions(
        self,
        *,
        voice_instructions: List[CharacterVoiceInstruction],
    ) -> Dict[str, Any]:
        return {
            "success": True,
            "engine_name": self.engine_name,
            "summary": {
                "voice_instruction_count": len(voice_instructions),
                "character_ids": [item.character_id for item in voice_instructions],
                "average_formality": self._average([item.formality for item in voice_instructions]),
                "vocabulary_styles": sorted({item.vocabulary_style for item in voice_instructions}),
                "rhythms": sorted({item.rhythm for item in voice_instructions}),
                "average_distinctiveness": self._average(
                    [item.metadata.get("voice_distinctiveness_score", 0.0) for item in voice_instructions]
                ),
            },
        }

    def _dialogue_pressure_for_character(
        self,
        *,
        character_id: str,
        dialogue_beats: List[DialogueBeat],
    ) -> Dict[str, Any]:
        relevant = [beat for beat in dialogue_beats if beat.speaker_id == character_id]
        if not relevant:
            return {
                "beat_count": 0,
                "average_secret_risk": 0.0,
                "has_power_shift": False,
                "has_relationship_effect": False,
            }

        return {
            "beat_count": len(relevant),
            "average_secret_risk": self._average([beat.secret_risk for beat in relevant]),
            "has_power_shift": any(bool(beat.power_shift) for beat in relevant),
            "has_relationship_effect": any(bool(beat.relationship_effect) for beat in relevant),
        }

    def _formality(self, *, voice_profile: Dict[str, Any], role_tags: List[str]) -> float:
        if "formality" in voice_profile:
            return self._bounded(voice_profile["formality"])

        style = str(voice_profile.get("style", "")).lower()
        if "controlled" in style or "formal" in style or "court" in role_tags:
            return 0.75
        if "guarded" in style:
            return 0.60
        if "comic" in role_tags:
            return 0.25
        return 0.50

    def _sentence_length(self, *, voice_profile: Dict[str, Any], emotional_state: Dict[str, Any]) -> str:
        if voice_profile.get("sentence_length"):
            return str(voice_profile["sentence_length"])

        dominant = self._dominant_emotion(emotional_state)
        if dominant in {"fear", "guilt", "rage"}:
            return "short"
        if dominant in {"grief", "longing"}:
            return "fragmented"
        return "medium"

    def _vocabulary_style(self, *, voice_profile: Dict[str, Any], role_tags: List[str]) -> str:
        if voice_profile.get("vocabulary_style"):
            return str(voice_profile["vocabulary_style"])

        style = str(voice_profile.get("style", "")).lower()
        if "controlled" in style:
            return "precise"
        if "guarded" in style:
            return "plain_defensive"
        if "scholar" in role_tags:
            return "analytical"
        if "royal" in role_tags or "court" in role_tags:
            return "formal_political"
        return "neutral_specific"

    def _rhythm(self, *, voice_profile: Dict[str, Any], emotional_state: Dict[str, Any]) -> str:
        if voice_profile.get("rhythm"):
            return str(voice_profile["rhythm"])

        dominant = self._dominant_emotion(emotional_state)
        if dominant == "guilt":
            return "controlled_with_breaks"
        if dominant == "rage":
            return "sharp"
        if dominant == "fear":
            return "interrupted"
        if dominant == "resolve":
            return "steady"
        return "balanced"

    def _humor_style(self, *, voice_profile: Dict[str, Any], role_tags: List[str]) -> str | None:
        if voice_profile.get("humor_style"):
            return str(voice_profile["humor_style"])
        if "comic_relief" in role_tags or "comic" in role_tags:
            return "deflective"
        return None

    def _anger_behavior(self, *, voice_profile: Dict[str, Any], emotional_state: Dict[str, Any]) -> str | None:
        if voice_profile.get("anger_behavior"):
            return str(voice_profile["anger_behavior"])
        if "rage" in emotional_state or "anger" in emotional_state:
            return "clips sentences and avoids explanation"
        return "tightens language before raising volume"

    def _fear_behavior(self, *, voice_profile: Dict[str, Any], emotional_state: Dict[str, Any]) -> str | None:
        if voice_profile.get("fear_behavior"):
            return str(voice_profile["fear_behavior"])
        if "fear" in emotional_state:
            return "asks indirect questions and checks exits"
        return "hides fear through control"

    def _romance_behavior(
        self,
        *,
        voice_profile: Dict[str, Any],
        role_tags: List[str],
        story_function_tags: List[str],
        beat_pressure: Dict[str, Any],
    ) -> str | None:
        if voice_profile.get("romance_behavior"):
            return str(voice_profile["romance_behavior"])
        if "love_interest" in role_tags or "anchor_romance" in story_function_tags:
            return "shows care through restraint, silence, and almost-confessions"
        if beat_pressure.get("has_relationship_effect"):
            return "lets emotion appear through what is not said"
        return None

    def _silence_behavior(self, *, voice_profile: Dict[str, Any], emotional_state: Dict[str, Any]) -> str | None:
        if voice_profile.get("silence_behavior"):
            return str(voice_profile["silence_behavior"])
        dominant = self._dominant_emotion(emotional_state)
        if dominant == "guilt":
            return "pauses before truthful words and redirects blame"
        if dominant == "fear":
            return "silence becomes self-protection"
        return "silence signals withheld information"

    def _subtext_style(self, *, voice_profile: Dict[str, Any], beat_pressure: Dict[str, Any]) -> str | None:
        if voice_profile.get("subtext_style"):
            return str(voice_profile["subtext_style"])
        if beat_pressure.get("average_secret_risk", 0.0) > 0.5:
            return "misdirection under emotional strain"
        if beat_pressure.get("has_relationship_effect"):
            return "relationship truth hidden beneath practical words"
        return "controlled implication"

    def _power_behavior(self, *, voice_profile: Dict[str, Any], role_tags: List[str]) -> str | None:
        if voice_profile.get("power_behavior"):
            return str(voice_profile["power_behavior"])
        if "protagonist" in role_tags:
            return "claims power by naming facts"
        if "love_interest" in role_tags:
            return "keeps power by withholding emotional truth"
        if "antagonist" in role_tags:
            return "uses precision and public pressure"
        return "power shifts through information control"

    def _forbidden_phrases(self, *, voice_profile: Dict[str, Any]) -> List[str]:
        values = voice_profile.get("forbidden_phrases", [])
        return list(values) if isinstance(values, list) else []

    def _signature_phrases(self, *, voice_profile: Dict[str, Any]) -> List[str]:
        values = voice_profile.get("signature_phrases", [])
        return list(values) if isinstance(values, list) else []

    def _dominant_emotion(self, emotional_state: Dict[str, Any]) -> str | None:
        if not emotional_state:
            return None
        try:
            return max(emotional_state.items(), key=lambda item: float(item[1]))[0]
        except Exception:
            return next(iter(emotional_state.keys()), None)

    def _distinctiveness_score(
        self,
        *,
        voice_profile: Dict[str, Any],
        emotional_state: Dict[str, Any],
        role_tags: List[str],
        beat_pressure: Dict[str, Any],
    ) -> float:
        score = 0.20
        if voice_profile:
            score += 0.25
        if emotional_state:
            score += 0.20
        if role_tags:
            score += 0.15
        if beat_pressure.get("beat_count", 0) > 0:
            score += 0.10
        if beat_pressure.get("average_secret_risk", 0.0) > 0.4:
            score += 0.10
        return round(max(0.0, min(1.0, score)), 3)

    def _bounded(self, value: Any) -> float:
        try:
            return max(0.0, min(1.0, float(value)))
        except (TypeError, ValueError):
            return 0.5

    def _average(self, values: List[float]) -> float:
        if not values:
            return 0.0
        return round(sum(values) / len(values), 3)

    def _warnings(
        self,
        *,
        instructions: List[CharacterVoiceInstruction],
        active_cast: List[Dict[str, Any]],
    ) -> List[str]:
        warnings = []

        if not instructions:
            warnings.append("No voice instructions generated.")

        if len(instructions) < len([item for item in active_cast if item.get("character_id")]):
            warnings.append("Some active cast members did not receive voice instructions.")

        low_distinctiveness = [
            item.character_id
            for item in instructions
            if item.metadata.get("voice_distinctiveness_score", 0.0) < 0.45
        ]
        if low_distinctiveness:
            warnings.append(f"Low voice distinctiveness for: {', '.join(low_distinctiveness)}")

        return warnings

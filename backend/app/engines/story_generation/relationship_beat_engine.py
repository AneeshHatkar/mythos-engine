from __future__ import annotations

from typing import Any, Dict, List

from backend.app.schemas.story_generation import (
    DialogueBeat,
    EmotionalSubtextInstruction,
    RelationshipBeat,
    SceneBlueprint,
)


class RelationshipBeatEngine:
    """Turns relationship state into scene-level relationship beats.

    This makes scenes relationally specific instead of generic. It uses
    relationship pressure, dialogue beats, emotional subtext, secrets, and
    character pair data to decide what should change between characters.
    """

    engine_name = "story_generation.relationship_beat_engine"

    def build_relationship_beats(
        self,
        *,
        blueprint: SceneBlueprint,
        story_context: Dict[str, Any],
        dialogue_beats: List[DialogueBeat] | None = None,
        emotional_subtext: List[EmotionalSubtextInstruction] | None = None,
    ) -> Dict[str, Any]:
        dialogue_beats = dialogue_beats or []
        emotional_subtext = emotional_subtext or []

        relationship_pressure = story_context.get("relationship_pressure", [])
        relationship_beats: List[RelationshipBeat] = []

        for item in relationship_pressure:
            relationship_id = item.get("relationship_id")
            if not relationship_id:
                continue

            character_a_id = item.get("character_a_id") or self._infer_character_a(blueprint)
            character_b_id = item.get("character_b_id") or self._infer_character_b(blueprint, character_a_id)

            dialogue_pressure = self._dialogue_pressure_for_relationship(
                character_a_id=character_a_id,
                character_b_id=character_b_id,
                dialogue_beats=dialogue_beats,
            )
            emotion_pressure = self._emotion_pressure_for_pair(
                character_a_id=character_a_id,
                character_b_id=character_b_id,
                emotional_subtext=emotional_subtext,
            )

            relationship_beats.append(
                RelationshipBeat(
                    relationship_id=relationship_id,
                    character_a_id=character_a_id,
                    character_b_id=character_b_id,
                    starting_trust=self._float(item.get("trust", 0.0)),
                    starting_resentment=self._float(item.get("resentment", 0.0)),
                    starting_affection=self._float(item.get("affection", item.get("romantic_tension", 0.0))),
                    starting_rivalry=self._float(item.get("rivalry", 0.0)),
                    romantic_tension=self._float(item.get("romantic_tension", item.get("affection", 0.0))),
                    betrayal_risk=self._float(item.get("betrayal_risk", 0.0)),
                    repair_potential=self._repair_potential(item=item, emotion_pressure=emotion_pressure),
                    power_imbalance=self._power_imbalance(item=item, dialogue_pressure=dialogue_pressure),
                    knowledge_asymmetry=self._knowledge_asymmetry(
                        story_context=story_context,
                        character_a_id=character_a_id,
                        character_b_id=character_b_id,
                    ),
                    turning_point=self._turning_point(
                        item=item,
                        blueprint=blueprint,
                        dialogue_pressure=dialogue_pressure,
                        emotion_pressure=emotion_pressure,
                    ),
                    expected_end_state_shift=self._expected_shift(
                        item=item,
                        blueprint=blueprint,
                        dialogue_pressure=dialogue_pressure,
                        emotion_pressure=emotion_pressure,
                    ),
                )
            )

        if not relationship_beats and len(blueprint.active_character_ids) >= 2:
            relationship_beats.append(self._fallback_relationship_beat(blueprint=blueprint, story_context=story_context))

        warnings = self._warnings(relationship_beats=relationship_beats, blueprint=blueprint)

        return {
            "success": True,
            "engine_name": self.engine_name,
            "relationship_beats": relationship_beats,
            "relationship_beats_dict": [item.model_dump(mode="json") for item in relationship_beats],
            "warnings": warnings,
            "handoff_to_next_engine": {
                "next_engine": "story_generation.knowledge_boundary_validator",
                "payload_keys": [
                    "relationship_beats",
                    "dialogue_beats",
                    "emotional_subtext_instructions",
                    "story_context",
                    "scene_blueprint",
                ],
            },
        }

    def apply_relationship_beats_to_dialogue(
        self,
        *,
        dialogue_beats: List[DialogueBeat],
        relationship_beats: List[RelationshipBeat],
    ) -> Dict[str, Any]:
        updated: List[DialogueBeat] = []

        for beat in dialogue_beats:
            relevant = self._find_relevant_relationship(beat=beat, relationship_beats=relationship_beats)
            if not relevant:
                updated.append(beat)
                continue

            data = beat.model_dump(mode="python")
            voice_rules = data.get("voice_rules", {}) or {}
            voice_rules["relationship_beat"] = {
                "relationship_id": relevant.relationship_id,
                "turning_point": relevant.turning_point,
                "expected_end_state_shift": relevant.expected_end_state_shift,
                "power_imbalance": relevant.power_imbalance,
                "knowledge_asymmetry": relevant.knowledge_asymmetry,
            }
            data["voice_rules"] = voice_rules

            if not data.get("relationship_effect"):
                data["relationship_effect"] = (
                    f"Dialogue should move {relevant.relationship_id}: {relevant.expected_end_state_shift}"
                )

            updated.append(DialogueBeat(**data))

        return {
            "success": True,
            "engine_name": self.engine_name,
            "dialogue_beats": updated,
            "dialogue_beats_dict": [beat.model_dump(mode="json") for beat in updated],
        }

    def validate_relationship_beats(
        self,
        *,
        relationship_beats: List[RelationshipBeat],
    ) -> Dict[str, Any]:
        blockers: List[str] = []
        warnings: List[str] = []
        passed: List[str] = []

        if not relationship_beats:
            blockers.append("no relationship beats generated")
        else:
            passed.append("relationship_beats_present")

        if all(item.relationship_id for item in relationship_beats):
            passed.append("relationship_ids_present")
        else:
            blockers.append("one or more relationship beats missing relationship_id")

        if all(item.character_a_id and item.character_b_id for item in relationship_beats):
            passed.append("relationship_characters_present")
        else:
            blockers.append("one or more relationship beats missing character ids")

        if any(item.turning_point for item in relationship_beats):
            passed.append("turning_points_present")
        else:
            warnings.append("no relationship turning points found")

        if any(item.expected_end_state_shift for item in relationship_beats):
            passed.append("expected_end_state_shift_present")
        else:
            warnings.append("no expected relationship state shifts found")

        if any(item.knowledge_asymmetry for item in relationship_beats):
            passed.append("knowledge_asymmetry_tracked")
        else:
            warnings.append("no knowledge asymmetry found")

        return {
            "success": True,
            "engine_name": self.engine_name,
            "valid": not blockers,
            "blockers": blockers,
            "warnings": warnings,
            "passed_checks": passed,
        }

    def summarize_relationship_beats(
        self,
        *,
        relationship_beats: List[RelationshipBeat],
    ) -> Dict[str, Any]:
        return {
            "success": True,
            "engine_name": self.engine_name,
            "summary": {
                "relationship_beat_count": len(relationship_beats),
                "relationship_ids": [item.relationship_id for item in relationship_beats],
                "average_betrayal_risk": self._average([item.betrayal_risk for item in relationship_beats]),
                "average_romantic_tension": self._average([item.romantic_tension for item in relationship_beats]),
                "average_repair_potential": self._average([item.repair_potential for item in relationship_beats]),
                "average_power_imbalance": self._average([item.power_imbalance for item in relationship_beats]),
                "turning_point_count": sum(1 for item in relationship_beats if item.turning_point),
            },
        }

    def _dialogue_pressure_for_relationship(
        self,
        *,
        character_a_id: str,
        character_b_id: str,
        dialogue_beats: List[DialogueBeat],
    ) -> Dict[str, Any]:
        relevant = [
            beat
            for beat in dialogue_beats
            if beat.speaker_id in {character_a_id, character_b_id}
            or any(listener in {character_a_id, character_b_id} for listener in beat.listener_ids)
        ]

        return {
            "beat_count": len(relevant),
            "secret_risk": self._average([beat.secret_risk for beat in relevant]),
            "has_power_shift": any(bool(beat.power_shift) for beat in relevant),
            "has_relationship_effect": any(bool(beat.relationship_effect) for beat in relevant),
            "subtext_count": sum(1 for beat in relevant if beat.subtext),
        }

    def _emotion_pressure_for_pair(
        self,
        *,
        character_a_id: str,
        character_b_id: str,
        emotional_subtext: List[EmotionalSubtextInstruction],
    ) -> Dict[str, Any]:
        relevant = [
            item
            for item in emotional_subtext
            if item.character_id in {character_a_id, character_b_id}
        ]

        emotions = {item.character_id: item.dominant_emotion for item in relevant}
        intensities = [item.intensity for item in relevant]

        return {
            "emotions": emotions,
            "average_intensity": self._average(intensities),
            "has_guilt": any(item.dominant_emotion == "guilt" for item in relevant),
            "has_shame": any(item.dominant_emotion == "shame" for item in relevant),
            "has_longing": any(item.dominant_emotion == "longing" for item in relevant),
            "has_rage": any(item.dominant_emotion == "rage" for item in relevant),
        }

    def _repair_potential(self, *, item: Dict[str, Any], emotion_pressure: Dict[str, Any]) -> float:
        base = self._float(item.get("repair_potential", 0.0))
        if emotion_pressure.get("has_guilt"):
            base += 0.20
        if emotion_pressure.get("has_longing"):
            base += 0.15
        if self._float(item.get("trust", 0.0)) > 0.4:
            base += 0.10
        return round(max(0.0, min(1.0, base)), 3)

    def _power_imbalance(self, *, item: Dict[str, Any], dialogue_pressure: Dict[str, Any]) -> float:
        base = self._float(item.get("power_imbalance", 0.0))
        if dialogue_pressure.get("secret_risk", 0.0) > 0.5:
            base += 0.25
        if dialogue_pressure.get("has_power_shift"):
            base += 0.20
        if self._float(item.get("betrayal_risk", 0.0)) > 0.6:
            base += 0.10
        return round(max(0.0, min(1.0, base)), 3)

    def _knowledge_asymmetry(
        self,
        *,
        story_context: Dict[str, Any],
        character_a_id: str,
        character_b_id: str,
    ) -> List[str]:
        asymmetry = []

        for boundary in story_context.get("knowledge_boundaries", []):
            holder = boundary.get("holder_id")
            if holder not in {character_a_id, character_b_id}:
                continue

            missing = boundary.get("missing_required_secret_ids", [])
            forbidden = boundary.get("forbidden_secret_reveals", [])

            for secret_id in missing:
                asymmetry.append(f"{holder} does not know {secret_id}")
            for secret_id in forbidden:
                asymmetry.append(f"{holder} must not reveal {secret_id}")

        return asymmetry

    def _turning_point(
        self,
        *,
        item: Dict[str, Any],
        blueprint: SceneBlueprint,
        dialogue_pressure: Dict[str, Any],
        emotion_pressure: Dict[str, Any],
    ) -> str:
        if self._float(item.get("betrayal_risk", 0.0)) >= 0.65:
            return "Betrayal risk becomes visible through what is said or withheld."

        if dialogue_pressure.get("secret_risk", 0.0) >= 0.55:
            return "A secret changes the emotional balance of the relationship."

        if emotion_pressure.get("has_guilt"):
            return "Guilt creates a chance for repair but also raises suspicion."

        if self._float(item.get("romantic_tension", 0.0)) >= 0.5:
            return "Romantic tension becomes harder to deny."

        return "The relationship must leave the scene in a different state."

    def _expected_shift(
        self,
        *,
        item: Dict[str, Any],
        blueprint: SceneBlueprint,
        dialogue_pressure: Dict[str, Any],
        emotion_pressure: Dict[str, Any],
    ) -> Dict[str, float]:
        shift = {
            "trust_delta": 0.0,
            "resentment_delta": 0.0,
            "romantic_tension_delta": 0.0,
            "repair_potential_delta": 0.0,
            "betrayal_risk_delta": 0.0,
        }

        if dialogue_pressure.get("secret_risk", 0.0) >= 0.5:
            shift["trust_delta"] -= 0.08
            shift["resentment_delta"] += 0.08
            shift["betrayal_risk_delta"] += 0.05

        if emotion_pressure.get("has_guilt"):
            shift["repair_potential_delta"] += 0.10
            shift["trust_delta"] += 0.03

        if self._float(item.get("romantic_tension", 0.0)) >= 0.4:
            shift["romantic_tension_delta"] += 0.06

        if blueprint.ending_hook:
            shift["resentment_delta"] += 0.02

        return {key: round(value, 3) for key, value in shift.items()}

    def _fallback_relationship_beat(
        self,
        *,
        blueprint: SceneBlueprint,
        story_context: Dict[str, Any],
    ) -> RelationshipBeat:
        a = self._infer_character_a(blueprint)
        b = self._infer_character_b(blueprint, a)

        return RelationshipBeat(
            relationship_id=f"rel_{a}_{b}",
            character_a_id=a,
            character_b_id=b,
            starting_trust=0.0,
            starting_resentment=0.0,
            starting_affection=0.0,
            starting_rivalry=0.0,
            romantic_tension=0.0,
            betrayal_risk=0.0,
            repair_potential=0.0,
            power_imbalance=0.0,
            knowledge_asymmetry=self._knowledge_asymmetry(
                story_context=story_context,
                character_a_id=a,
                character_b_id=b,
            ),
            turning_point="The scene must define how these characters currently affect each other.",
            expected_end_state_shift={"trust_delta": 0.0, "resentment_delta": 0.0},
        )

    def _find_relevant_relationship(
        self,
        *,
        beat: DialogueBeat,
        relationship_beats: List[RelationshipBeat],
    ) -> RelationshipBeat | None:
        participants = {beat.speaker_id, *beat.listener_ids}
        for relationship in relationship_beats:
            if relationship.character_a_id in participants and relationship.character_b_id in participants:
                return relationship
        return relationship_beats[0] if relationship_beats else None

    def _infer_character_a(self, blueprint: SceneBlueprint) -> str:
        if blueprint.pov_character_id:
            return blueprint.pov_character_id
        if blueprint.active_character_ids:
            return blueprint.active_character_ids[0]
        return "unknown_a"

    def _infer_character_b(self, blueprint: SceneBlueprint, character_a_id: str) -> str:
        for cid in blueprint.active_character_ids:
            if cid != character_a_id:
                return cid
        return "unknown_b"

    def _warnings(
        self,
        *,
        relationship_beats: List[RelationshipBeat],
        blueprint: SceneBlueprint,
    ) -> List[str]:
        warnings = []

        if not relationship_beats:
            warnings.append("No relationship beats generated.")

        if blueprint.relationship_pressure and not relationship_beats:
            warnings.append("Blueprint had relationship pressure but no relationship beat was created.")

        weak = [
            item.relationship_id
            for item in relationship_beats
            if not item.turning_point or not item.expected_end_state_shift
        ]
        if weak:
            warnings.append(f"Weak relationship beat structure for: {', '.join(weak)}")

        return warnings

    def _float(self, value: Any) -> float:
        try:
            return max(0.0, min(1.0, float(value)))
        except (TypeError, ValueError):
            return 0.0

    def _average(self, values: List[float]) -> float:
        if not values:
            return 0.0
        return round(sum(values) / len(values), 3)

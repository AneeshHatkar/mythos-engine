from typing import Any, Dict, List

from backend.app.schemas.story_dna import EmotionalResonanceSeed


class EmotionalResonanceSeedService:
    """Creates structured reader-emotion targets for later simulation/scene engines."""

    def build_resonance_seed(
        self,
        *,
        project_id: str = "default_project",
        universe_id: str = "default_universe",
        story_dna: Dict[str, Any] | None = None,
        relationship_mode: str = "rivalry_with_hidden_care",
        target_intensity: float = 0.75,
    ) -> Dict[str, Any]:
        dna = story_dna or {}
        intensity = max(0.0, min(1.0, float(target_intensity)))

        desired = self._desired_emotion(dna, relationship_mode)
        contrast = self._contrast(relationship_mode)
        aftertaste = self._aftertaste(desired, dna)

        seed = EmotionalResonanceSeed(
            project_id=project_id,
            universe_id=universe_id,
            desired_reader_emotion=desired,
            emotional_contrast=contrast,
            scene_aftertaste=aftertaste,
            heartbreak_vector=round(intensity * self._weight(relationship_mode, "heartbreak"), 3),
            awe_vector=round(intensity * self._weight(relationship_mode, "awe"), 3),
            dread_vector=round(intensity * self._weight(relationship_mode, "dread"), 3),
            hope_vector=round(intensity * self._weight(relationship_mode, "hope"), 3),
            intimacy_vector=round(intensity * self._weight(relationship_mode, "intimacy"), 3),
            betrayal_vector=round(intensity * self._weight(relationship_mode, "betrayal"), 3),
            catharsis_condition=self._catharsis_condition(relationship_mode),
            resonance_tags=[relationship_mode, desired, "structured_emotion_target"],
        )

        return {
            "success": True,
            "emotional_resonance_seed": seed.model_dump(),
            "chunk4_usage": [
                "tension curve targets",
                "relationship rupture/repair intensity",
                "event consequence emotional aftertaste",
                "scene seed emotional direction",
            ],
        }

    def _desired_emotion(self, dna: Dict[str, Any], relationship_mode: str) -> str:
        if "romance" in relationship_mode or "hidden_care" in relationship_mode:
            return "aching intimacy under pressure"
        if "betrayal" in relationship_mode:
            return "dreadful inevitability"
        if "rivalry" in relationship_mode:
            return "admiration sharpened by threat"
        return dna.get("emotional_promise") or "earned emotional weight"

    def _contrast(self, relationship_mode: str) -> str:
        if "rivalry" in relationship_mode:
            return "respect versus resentment"
        if "romance" in relationship_mode:
            return "desire versus danger"
        if "betrayal" in relationship_mode:
            return "love versus self-preservation"
        return "hope versus cost"

    def _aftertaste(self, desired: str, dna: Dict[str, Any]) -> str:
        core = dna.get("core_question", "truth costs something")
        return f"{desired}; the reader should feel that {core}"

    def _weight(self, mode: str, vector: str) -> float:
        table = {
            "heartbreak": 0.75 if "romance" in mode or "betrayal" in mode else 0.45,
            "awe": 0.35 if "rivalry" in mode else 0.25,
            "dread": 0.75 if "betrayal" in mode else 0.45,
            "hope": 0.55 if "hidden_care" in mode or "repair" in mode else 0.35,
            "intimacy": 0.80 if "romance" in mode or "hidden_care" in mode else 0.3,
            "betrayal": 0.85 if "betrayal" in mode else 0.25,
        }
        return table.get(vector, 0.4)

    def _catharsis_condition(self, relationship_mode: str) -> str:
        if "hidden_care" in relationship_mode:
            return "one character protects the other without demanding public recognition"
        if "betrayal" in relationship_mode:
            return "truth is finally spoken with consequence, not excuse"
        if "rivalry" in relationship_mode:
            return "respect becomes undeniable under shared pressure"
        return "the emotional cost is acknowledged rather than erased"

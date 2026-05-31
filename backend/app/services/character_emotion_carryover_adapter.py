from typing import Any, Dict, List


class CharacterEmotionCarryoverAdapter:
    """Carries emotional state across events instead of resetting characters each scene."""

    EMOTION_DECAY_DEFAULTS = {
        "shame": 0.08,
        "anger": 0.10,
        "fear": 0.07,
        "grief": 0.04,
        "hope": 0.06,
        "trust": 0.05,
        "dread": 0.03,
    }

    def build_emotion_update(
        self,
        *,
        character_id: str,
        event_payload: Dict[str, Any],
        current_emotion_state: Dict[str, Any] | None = None,
        intensity: float = 0.5,
    ) -> Dict[str, Any]:
        current = current_emotion_state or {}
        event_type = event_payload.get("event_type", "unknown_event")
        event_emotions = self._event_emotion_deltas(event_type, intensity)

        updated_emotions = dict(current.get("emotion_vector", {}))
        for emotion, delta in event_emotions.items():
            updated_emotions[emotion] = round(max(0.0, min(1.0, updated_emotions.get(emotion, 0.0) + delta)), 3)

        dominant = max(updated_emotions, key=updated_emotions.get) if updated_emotions else "controlled_pressure"
        suppressed = self._infer_suppressed_emotion(event_type, updated_emotions)

        state = {
            "character_id": character_id,
            "dominant_emotion": dominant,
            "suppressed_emotion": suppressed,
            "emotion_vector": updated_emotions,
            "triggered_wound": self._infer_triggered_wound(event_type),
            "emotion_intensity": round(max(updated_emotions.values()) if updated_emotions else intensity, 3),
            "emotional_mask": self._infer_mask(dominant),
            "relationship_specific_emotional_leak": {},
            "decay_rates": {
                emotion: self.EMOTION_DECAY_DEFAULTS.get(emotion, 0.06)
                for emotion in updated_emotions
            },
        }

        return {
            "success": True,
            "character_id": character_id,
            "emotion_update": state,
            "event_emotion_deltas": event_emotions,
        }

    def decay_emotions(self, emotion_state: Dict[str, Any], *, ticks: int = 1) -> Dict[str, Any]:
        updated = dict(emotion_state)
        vector = dict(updated.get("emotion_vector", {}))
        rates = updated.get("decay_rates", {})

        for _ in range(ticks):
            for emotion, value in list(vector.items()):
                vector[emotion] = round(max(0.0, value - float(rates.get(emotion, 0.06))), 3)

        updated["emotion_vector"] = vector
        updated["dominant_emotion"] = max(vector, key=vector.get) if vector else "controlled_pressure"
        updated["emotion_intensity"] = round(max(vector.values()) if vector else 0.0, 3)

        return {
            "success": True,
            "decayed_emotion_state": updated,
        }

    def _event_emotion_deltas(self, event_type: str, intensity: float) -> Dict[str, float]:
        val = round(min(1.0, max(0.0, intensity)), 3)
        if event_type == "public_humiliation":
            return {"shame": val, "anger": val * 0.7, "fear": val * 0.3}
        if event_type == "betrayal":
            return {"anger": val, "grief": val * 0.7, "dread": val * 0.4}
        if event_type == "secret_discovery":
            return {"fear": val * 0.5, "dread": val * 0.6, "hope": val * 0.2}
        if event_type == "rescue":
            return {"hope": val, "trust": val * 0.5, "fear": val * 0.2}
        return {"dread": val * 0.3, "hope": val * 0.2}

    def _infer_suppressed_emotion(self, event_type: str, vector: Dict[str, float]) -> str:
        if event_type == "public_humiliation":
            return "shame"
        if event_type == "betrayal":
            return "grief"
        if "fear" in vector:
            return "fear"
        return "vulnerability"

    def _infer_triggered_wound(self, event_type: str) -> str | None:
        if event_type == "public_humiliation":
            return "belonging can be revoked publicly"
        if event_type == "betrayal":
            return "trust becomes a weapon"
        if event_type == "secret_discovery":
            return "truth was hidden by people with power"
        return None

    def _infer_mask(self, dominant: str) -> str:
        if dominant in ["shame", "grief"]:
            return "controlled_precision"
        if dominant == "anger":
            return "cold_specificity"
        if dominant == "fear":
            return "strategic_silence"
        return "measured_composure"

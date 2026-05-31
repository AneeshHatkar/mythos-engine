from typing import Any, Dict, List


class CharacterConsistencyInvariantChecker:
    """Checks that updates do not break character psychology, voice, power costs, or destiny rules."""

    def check_update(
        self,
        *,
        character_profile: Dict[str, Any],
        proposed_update: Dict[str, Any],
        event_context: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        event = event_context or {}
        violations = []
        warnings = []

        flat = self._flatten(character_profile)
        update_flat = self._flatten(proposed_update)

        if self._dialogue_voice_violation(flat, update_flat, event):
            violations.append("dialogue contradicts established voice without pressure or transformation reason")

        if self._betrayal_without_trigger(flat, update_flat, event):
            violations.append("betrayal proposed without sufficient trigger, leverage, fear, or moral pressure")

        if self._romance_without_pressure(flat, update_flat, event):
            warnings.append("romance escalation lacks trust, pressure, vulnerability, or repair condition")

        if self._skill_cost_violation(flat, update_flat):
            violations.append("skill/power use ignores established cost model")

        if self._destiny_condition_violation(flat, update_flat, event):
            warnings.append("destiny escalation appears without condition, sacrifice, threshold, or consequence")

        consistency_score = round(max(0.0, 1.0 - 0.25 * len(violations) - 0.1 * len(warnings)), 3)

        return {
            "success": True,
            "character_id": flat.get("character_id") or character_profile.get("character_id", "unknown_character"),
            "consistent": len(violations) == 0 and consistency_score >= 0.7,
            "consistency_score": consistency_score,
            "violations": violations,
            "warnings": warnings,
            "checked_axes": [
                "dialogue_voice",
                "betrayal_trigger",
                "romance_escalation",
                "skill_cost",
                "destiny_condition",
            ],
        }

    def _dialogue_voice_violation(self, flat: Dict[str, Any], update: Dict[str, Any], event: Dict[str, Any]) -> bool:
        voice = str(flat.get("voice_family") or flat.get("dialogue_voice_family") or "").lower()
        dialogue = str(update.get("dialogue") or update.get("line") or "").lower()
        pressure = float(event.get("intensity", 0.0) or 0.0)

        if "controlled" in voice and any(token in dialogue for token in ["omg", "lol", "whateverrr"]):
            return pressure < 0.8
        return False

    def _betrayal_without_trigger(self, flat: Dict[str, Any], update: Dict[str, Any], event: Dict[str, Any]) -> bool:
        action = str(update.get("action") or update.get("choice") or "").lower()
        if "betray" not in action:
            return False

        triggers = [
            event.get("leverage_exists"),
            event.get("blackmail_active"),
            event.get("fear_pressure", 0) >= 0.7,
            event.get("moral_pressure", 0) >= 0.7,
            event.get("survival_pressure", 0) >= 0.7,
        ]
        return not any(triggers)

    def _romance_without_pressure(self, flat: Dict[str, Any], update: Dict[str, Any], event: Dict[str, Any]) -> bool:
        relation_delta = update.get("relationship_delta", {})
        if not isinstance(relation_delta, dict):
            return False

        romance_delta = float(relation_delta.get("romantic_tension", 0.0) or 0.0)
        trust_delta = float(relation_delta.get("trust", 0.0) or 0.0)
        has_pressure = event.get("shared_danger") or event.get("truth_disclosure") or event.get("sacrifice") or event.get("repair_attempt")

        return romance_delta > 0.25 and trust_delta < 0.05 and not has_pressure

    def _skill_cost_violation(self, flat: Dict[str, Any], update: Dict[str, Any]) -> bool:
        uses_skill = bool(update.get("uses_skill") or update.get("skill_used"))
        if not uses_skill:
            return False

        has_cost_model = bool(flat.get("cost_model") or flat.get("skill_cost") or flat.get("adaptation_cost"))
        pays_cost = bool(update.get("skill_cost_paid") or update.get("cost_applied") or update.get("consequence_applied"))

        return has_cost_model and not pays_cost

    def _destiny_condition_violation(self, flat: Dict[str, Any], update: Dict[str, Any], event: Dict[str, Any]) -> bool:
        destiny_update = bool(update.get("destiny_escalation") or update.get("prophecy_triggered"))
        if not destiny_update:
            return False

        return not any(
            [
                event.get("threshold_crossed"),
                event.get("sacrifice"),
                event.get("moral_choice"),
                event.get("severe_consequence"),
            ]
        )

    def _flatten(self, value: Any) -> Dict[str, Any]:
        flat: Dict[str, Any] = {}

        def walk(item: Any) -> None:
            if isinstance(item, dict):
                for key, val in item.items():
                    if key not in flat and not isinstance(val, (dict, list)):
                        flat[key] = val
                    walk(val)
            elif isinstance(item, list):
                for val in item:
                    walk(val)

        walk(value)
        return flat

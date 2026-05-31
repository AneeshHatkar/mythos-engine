from typing import Any, Dict, List
from uuid import uuid4


class CharacterMemoryUpdateAdapter:
    """Turns simulation events into durable memory updates."""

    def build_memory_update(
        self,
        *,
        character_id: str,
        event_payload: Dict[str, Any],
        intensity: float = 0.5,
    ) -> Dict[str, Any]:
        event_type = event_payload.get("event_type", "unknown_event")
        event_id = event_payload.get("event_id", f"evt_{uuid4().hex[:12]}")
        description = event_payload.get("description") or event_payload.get("summary") or event_type

        emotional_tags = self._infer_emotional_tags(event_type, intensity)
        future_modifiers = self._infer_future_modifiers(event_type, intensity)

        memory_record = {
            "memory_id": f"mem_{uuid4().hex[:12]}",
            "character_id": character_id,
            "source_event_id": event_id,
            "memory_type": self._infer_memory_type(event_type),
            "content": description,
            "emotional_intensity": round(float(intensity), 3),
            "emotional_tags": emotional_tags,
            "trigger_conditions": self._infer_trigger_conditions(event_type),
            "dialogue_constraints": self._infer_dialogue_constraints(event_type),
            "future_agency_modifiers": future_modifiers,
            "created_by_adapter": "character_memory_update_adapter",
        }

        return {
            "success": True,
            "character_id": character_id,
            "source_event_id": event_id,
            "memory_record": memory_record,
            "should_persist": intensity >= 0.35,
            "memory_update_summary": {
                "memory_type": memory_record["memory_type"],
                "emotional_tags": emotional_tags,
                "future_agency_modifiers": future_modifiers,
            },
        }

    def apply_memory_update(
        self,
        *,
        character_state: Dict[str, Any],
        memory_update: Dict[str, Any],
    ) -> Dict[str, Any]:
        updated = dict(character_state)
        memories = list(updated.get("memory_records", []))
        active_ids = list(updated.get("active_memory_ids", []))

        memory_record = memory_update.get("memory_record", {})
        if memory_record:
            memories.append(memory_record)
            active_ids.append(memory_record.get("memory_id"))

        updated["memory_records"] = memories
        updated["active_memory_ids"] = [item for item in active_ids if item]
        updated.setdefault("state_update_log", []).append(
            {
                "update_type": "memory_update",
                "memory_id": memory_record.get("memory_id"),
                "source_event_id": memory_record.get("source_event_id"),
            }
        )

        return {
            "success": True,
            "updated_character_state": updated,
            "added_memory_id": memory_record.get("memory_id"),
        }

    def _infer_memory_type(self, event_type: str) -> str:
        mapping = {
            "public_humiliation": "wound_activation_memory",
            "secret_discovery": "knowledge_turning_point_memory",
            "betrayal": "trust_rupture_memory",
            "rescue": "debt_or_attachment_memory",
            "promise_broken": "promise_rupture_memory",
            "romantic_boundary_crossing": "intimacy_boundary_memory",
        }
        return mapping.get(event_type, "event_memory")

    def _infer_emotional_tags(self, event_type: str, intensity: float) -> List[str]:
        tags = []
        if event_type == "public_humiliation":
            tags.extend(["shame", "anger", "exposure"])
        elif event_type == "secret_discovery":
            tags.extend(["shock", "suspicion", "clarity"])
        elif event_type == "betrayal":
            tags.extend(["hurt", "distrust", "coldness"])
        elif event_type == "rescue":
            tags.extend(["relief", "debt", "conflicted_gratitude"])
        else:
            tags.append("pressure")

        if intensity >= 0.75:
            tags.append("high_intensity")
        return tags

    def _infer_trigger_conditions(self, event_type: str) -> List[str]:
        if event_type == "public_humiliation":
            return ["public ranking pressure", "laughter", "status threat"]
        if event_type == "betrayal":
            return ["broken trust", "withheld truth", "similar wording"]
        if event_type == "secret_discovery":
            return ["hidden evidence", "contradictory testimony"]
        return ["similar emotional pressure"]

    def _infer_dialogue_constraints(self, event_type: str) -> List[str]:
        if event_type == "public_humiliation":
            return ["avoids admitting shame directly", "uses controlled precision under pressure"]
        if event_type == "betrayal":
            return ["trust language becomes colder", "asks exact questions instead of pleading"]
        return ["emotion leaks through subtext"]

    def _infer_future_modifiers(self, event_type: str, intensity: float) -> Dict[str, float]:
        base = round(min(1.0, max(0.0, intensity)), 3)
        if event_type == "public_humiliation":
            return {"risk_avoidance": base, "status_sensitivity": base, "anger_pressure": base * 0.8}
        if event_type == "betrayal":
            return {"trust_resistance": base, "truth_demand": base, "attachment_guard": base}
        if event_type == "rescue":
            return {"debt_pressure": base, "attachment_opening": base * 0.6}
        return {"emotional_carryover": base}

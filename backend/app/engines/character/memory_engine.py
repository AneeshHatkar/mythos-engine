from typing import Any, Dict, List
from uuid import uuid4

from backend.app.engines.base import BaseEngine
from backend.app.schemas.character import MemoryRecord
from backend.app.schemas.foundation import EngineRunResult


class MemoryEngine(BaseEngine):
    """Builds emotionally weighted memory records for a character.

    Memories are not lore notes. They influence behavior, emotional triggers,
    trust, betrayal, scene reactions, relationship simulation, and future plot.
    """

    engine_name = "character.memory_engine"

    def run(self, payload: Dict[str, Any]) -> EngineRunResult:
        character_seed = payload.get("character_seed", {})
        psychology_profile = payload.get("psychology_profile") or character_seed.get("psychology", {})
        trauma_records = payload.get("trauma_records") or character_seed.get("trauma_records", [])
        healing_profile = payload.get("healing_profile") or character_seed.get("healing_profile", {})
        emotional_state_profile = payload.get("emotional_state_profile") or character_seed.get("emotional_state", {})
        emotional_arc_profile = payload.get("emotional_arc_profile") or character_seed.get("emotional_arc", {})
        arc_beats = payload.get("arc_beats") or character_seed.get("arc_beats", [])

        warnings: List[str] = []

        if not character_seed:
            warnings.append("No character_seed provided; memory engine used draft defaults.")

        character_id = (
            character_seed.get("character_id")
            or psychology_profile.get("character_id")
            or emotional_state_profile.get("character_id")
            or self._first_character_id(trauma_records)
            or f"char_{uuid4().hex[:12]}"
        )

        memory_records = self._build_memory_records(
            character_id=character_id,
            character_seed=character_seed,
            psychology_profile=psychology_profile,
            trauma_records=trauma_records,
            healing_profile=healing_profile,
            emotional_state_profile=emotional_state_profile,
            emotional_arc_profile=emotional_arc_profile,
            arc_beats=arc_beats,
        )

        memory_network = self._build_memory_network(memory_records, character_seed)
        memory_diagnostics = self._build_memory_diagnostics(memory_records, memory_network)
        next_engine_payload = self._build_next_engine_payload(
            character_seed=character_seed,
            psychology_profile=psychology_profile,
            trauma_records=trauma_records,
            emotional_state_profile=emotional_state_profile,
            emotional_arc_profile=emotional_arc_profile,
            memory_records=memory_records,
            memory_network=memory_network,
        )

        return self.build_result(
            success=True,
            data={
                "memory_records": [record.model_dump() for record in memory_records],
                "memory_network": memory_network,
                "memory_diagnostics": memory_diagnostics,
                "next_engine_payload": next_engine_payload,
                "memory_summary": {
                    "character_id": character_id,
                    "memory_count": len(memory_records),
                    "highest_emotional_weight": max([record.emotional_weight for record in memory_records], default=0.0),
                    "average_reliability": self._average([record.reliability for record in memory_records]),
                    "has_behavioral_influence": all(len(record.behavioral_influence) > 0 for record in memory_records),
                    "ready_for_reputation_engine": True,
                    "ready_for_goal_engine": True,
                    "ready_for_relationship_simulation_later": True,
                },
                "training_notes": [
                    "Memory records make characters stateful across scenes and relationships.",
                    "Memories should trigger emotion and behavior, not merely summarize backstory.",
                    "Reliability allows false, distorted, or incomplete memories without breaking logic.",
                    "Future Chunk 8 can train retrieval-augmented character memory from curated event-memory pairs.",
                ],
            },
            warnings=warnings,
            errors=[],
            generated_object_ids=[record.memory_id for record in memory_records],
        )

    def _first_character_id(self, trauma_records: List[Dict[str, Any]]) -> str | None:
        if trauma_records and isinstance(trauma_records[0], dict):
            return trauma_records[0].get("character_id")
        return None

    def _build_memory_records(
        self,
        *,
        character_id: str,
        character_seed: Dict[str, Any],
        psychology_profile: Dict[str, Any],
        trauma_records: List[Dict[str, Any]],
        healing_profile: Dict[str, Any],
        emotional_state_profile: Dict[str, Any],
        emotional_arc_profile: Dict[str, Any],
        arc_beats: List[Dict[str, Any]],
    ) -> List[MemoryRecord]:
        records: List[MemoryRecord] = []

        core_wound = psychology_profile.get("core_wound") or character_seed.get("core_wound")
        shame_trigger = psychology_profile.get("shame_trigger")
        healing_condition = psychology_profile.get("healing_condition") or healing_profile.get("primary_healing_condition")
        betrayal_response = psychology_profile.get("betrayal_response")
        breakthrough_condition = character_seed.get("breakthrough_condition")

        if core_wound:
            records.append(
                MemoryRecord(
                    memory_id=f"mem_{uuid4().hex[:12]}",
                    character_id=character_id,
                    event_id="evt core wound origin",
                    content=f"The character remembers the first time this wound became true to them: {core_wound}.",
                    emotional_weight=self._weight_from_text(core_wound, 0.82),
                    reliability=0.78,
                    trigger_terms=self._trigger_terms(core_wound, shame_trigger),
                    related_people=self._related_people(character_seed, "core_wound"),
                    related_objects=self._related_objects(character_seed, "core_wound"),
                    related_locations=self._related_locations(character_seed, "core_wound"),
                    behavioral_influence=[
                        "reacts strongly when the old wound is repeated",
                        "tries to prevent others from experiencing the same humiliation",
                    ],
                    decay_or_reinforcement="reinforces when public judgment repeats",
                )
            )

        for index, trauma in enumerate(trauma_records[:3]):
            source = trauma.get("trauma_source", "unresolved trauma")
            record = MemoryRecord(
                memory_id=f"mem_{uuid4().hex[:12]}",
                character_id=character_id,
                event_id=trauma.get("trauma_id") or f"evt_trauma_{index}",
                content=f"Trauma-linked memory: {source}.",
                emotional_weight=float(trauma.get("trauma_intensity", 0.55)),
                reliability=self._trauma_memory_reliability(trauma),
                trigger_terms=trauma.get("trigger_events", [])[:5],
                related_people=self._related_people(character_seed, "trauma"),
                related_objects=self._related_objects(character_seed, "trauma"),
                related_locations=self._related_locations(character_seed, "trauma"),
                behavioral_influence=[
                    trauma.get("avoidance_behavior", "avoids similar situations"),
                    trauma.get("coping_behavior", "uses old coping behavior under stress"),
                ],
                decay_or_reinforcement="reinforces under similar trigger; softens through healing milestone",
            )
            records.append(record)

        if healing_condition:
            records.append(
                MemoryRecord(
                    memory_id=f"mem_{uuid4().hex[:12]}",
                    character_id=character_id,
                    event_id="evt_possible_healing",
                    content=f"The character carries a possible healing memory/need: {healing_condition}.",
                    emotional_weight=0.68,
                    reliability=0.86,
                    trigger_terms=["protection", "truth", "repair", "trust", "choice"],
                    related_people=["trusted confidant", "future relationship anchor"],
                    related_objects=self._related_objects(character_seed, "healing"),
                    related_locations=["private safe place", "threshold location"],
                    behavioral_influence=[
                        "softens when someone protects truth without demanding ownership",
                        "moves toward vulnerability after repeated proof",
                    ],
                    decay_or_reinforcement="reinforces when safe relationships repeat",
                )
            )

        if betrayal_response:
            records.append(
                MemoryRecord(
                    memory_id=f"mem_{uuid4().hex[:12]}",
                    character_id=character_id,
                    event_id="evt_betrayal_pattern",
                    content=f"The character has a betrayal pattern memory: {betrayal_response}.",
                    emotional_weight=0.74,
                    reliability=0.82,
                    trigger_terms=["betrayal", "secret", "public abandonment", "used as tool"],
                    related_people=["past betrayer", "future rival", "intimate ally"],
                    related_objects=self._related_objects(character_seed, "betrayal"),
                    related_locations=["public hall", "private archive"],
                    behavioral_influence=[
                        "withdraws trust when words echo the old betrayal",
                        "remembers exact phrasing during conflict",
                    ],
                    decay_or_reinforcement="reinforces when trust is weaponized",
                )
            )

        if breakthrough_condition:
            records.append(
                MemoryRecord(
                    memory_id=f"mem_{uuid4().hex[:12]}",
                    character_id=character_id,
                    event_id="evt_limit_break_trigger_memory",
                    content=f"The character stores a pressure memory tied to future adaptability: {breakthrough_condition}.",
                    emotional_weight=0.79,
                    reliability=0.9,
                    trigger_terms=["weaker person", "punishment", "threshold", "choice", "cost"],
                    related_people=["vulnerable person", "authority figure", "witness"],
                    related_objects=self._related_objects(character_seed, "limit_break"),
                    related_locations=["public punishment site", "academy hall"],
                    behavioral_influence=[
                        "may override avoidance when someone weaker is threatened",
                        "connects justice pressure to adaptability activation",
                    ],
                    decay_or_reinforcement="reinforces when moral threshold is crossed",
                )
            )

        if arc_beats:
            records.append(
                MemoryRecord(
                    memory_id=f"mem_{uuid4().hex[:12]}",
                    character_id=character_id,
                    event_id="evt_arc_memory_scaffold",
                    content="The character carries a structural emotional memory scaffold for future arc beats.",
                    emotional_weight=0.52,
                    reliability=0.92,
                    trigger_terms=[beat.get("beat", "") for beat in arc_beats if beat.get("beat")],
                    related_people=["relationship pressure character", "rival", "mentor"],
                    related_objects=["symbolic object from emotional arc"],
                    related_locations=["recurring emotional threshold location"],
                    behavioral_influence=[
                        "future scenes should echo earlier emotional beats",
                        "major choices should reference remembered triggers",
                    ],
                    decay_or_reinforcement="reinforces through recurring motifs",
                )
            )

        if not records:
            records.append(
                MemoryRecord(
                    memory_id=f"mem_{uuid4().hex[:12]}",
                    character_id=character_id,
                    event_id="evt_identity_seed",
                    content="The character remembers being misunderstood before being known.",
                    emotional_weight=0.35,
                    reliability=0.88,
                    trigger_terms=["misread", "role", "name"],
                    related_people=["early authority figure"],
                    related_objects=["ordinary personal item"],
                    related_locations=["first public setting"],
                    behavioral_influence=[
                        "resists being reduced to a role",
                        "listens for whether others remember details",
                    ],
                    decay_or_reinforcement="stable",
                )
            )

        return records

    def _weight_from_text(self, text: str, default: float) -> float:
        lowered = text.lower()

        if any(term in lowered for term in ["erased", "death", "betrayal", "abandonment"]):
            return 0.9

        if any(term in lowered for term in ["failure", "humiliation", "revoked", "disposable"]):
            return 0.82

        if any(term in lowered for term in ["shame", "worth", "class"]):
            return 0.74

        return default

    def _trigger_terms(self, core_wound: str, shame_trigger: str | None) -> List[str]:
        terms = []

        for raw in core_wound.replace("-", " ").replace(",", " ").split():
            word = raw.strip().lower()
            if len(word) >= 5:
                terms.append(word)

        if shame_trigger:
            terms.extend([
                word.strip().lower()
                for word in shame_trigger.replace("-", " ").replace(",", " ").split()
                if len(word.strip()) >= 5
            ])

        if not terms:
            terms.extend(["judgment", "misread", "truth"])

        return sorted(set(terms))[:8]

    def _related_people(self, seed: Dict[str, Any], memory_type: str) -> List[str]:
        if seed.get("related_people"):
            return seed["related_people"]

        if memory_type == "core_wound":
            return ["authority figure", "watching peers"]

        if memory_type == "trauma":
            return ["past witness", "source of pressure"]

        if memory_type == "healing":
            return ["trusted confidant"]

        if memory_type == "limit_break":
            return ["vulnerable person", "punishing authority"]

        return ["unknown remembered person"]

    def _related_objects(self, seed: Dict[str, Any], memory_type: str) -> List[str]:
        objects = []

        if seed.get("family_name_status") in {"distrusted", "erased", "unknown"}:
            objects.append("family-name badge")

        if seed.get("skill_rarity") in {"rare", "anomaly", "S", "SS", "SSS"}:
            objects.append("training mark")

        if seed.get("destiny_type"):
            objects.append("destiny token")

        if memory_type == "healing":
            objects.append("kept proof of trust")

        if memory_type == "limit_break":
            objects.append("threshold symbol")

        if not objects:
            objects.append("ordinary personal object")

        return sorted(set(objects))

    def _related_locations(self, seed: Dict[str, Any], memory_type: str) -> List[str]:
        if seed.get("origin_location"):
            return [seed["origin_location"]]

        if memory_type == "core_wound":
            return ["academy hall", "public ranking site"]

        if memory_type == "trauma":
            return ["place of old pressure"]

        if memory_type == "healing":
            return ["private threshold space"]

        if memory_type == "limit_break":
            return ["public punishment site"]

        return ["first remembered setting"]

    def _trauma_memory_reliability(self, trauma: Dict[str, Any]) -> float:
        intensity = float(trauma.get("trauma_intensity", 0.5))

        if intensity >= 0.8:
            return 0.68

        if intensity >= 0.6:
            return 0.76

        return 0.86

    def _build_memory_network(self, records: List[MemoryRecord], seed: Dict[str, Any]) -> Dict[str, Any]:
        trigger_index: Dict[str, List[str]] = {}
        people_index: Dict[str, List[str]] = {}
        object_index: Dict[str, List[str]] = {}
        location_index: Dict[str, List[str]] = {}

        for record in records:
            for trigger in record.trigger_terms:
                trigger_index.setdefault(trigger, []).append(record.memory_id)

            for person in record.related_people:
                people_index.setdefault(person, []).append(record.memory_id)

            for obj in record.related_objects:
                object_index.setdefault(obj, []).append(record.memory_id)

            for location in record.related_locations:
                location_index.setdefault(location, []).append(record.memory_id)

        strongest = max(records, key=lambda record: record.emotional_weight)

        return {
            "character_id": records[0].character_id if records else seed.get("character_id"),
            "trigger_index": trigger_index,
            "people_index": people_index,
            "object_index": object_index,
            "location_index": location_index,
            "strongest_memory_id": strongest.memory_id if records else None,
            "strongest_memory_weight": strongest.emotional_weight if records else 0.0,
            "recurring_objects": [
                obj for obj, ids in object_index.items()
                if len(ids) >= 2
            ],
            "recurring_people": [
                person for person, ids in people_index.items()
                if len(ids) >= 2
            ],
            "memory_count": len(records),
        }

    def _build_memory_diagnostics(self, records: List[MemoryRecord], network: Dict[str, Any]) -> Dict[str, Any]:
        has_triggers = all(len(record.trigger_terms) > 0 for record in records)
        has_behavior = all(len(record.behavioral_influence) > 0 for record in records)
        has_links = all(
            len(record.related_people) > 0 or len(record.related_objects) > 0 or len(record.related_locations) > 0
            for record in records
        )
        has_reliability = all(0.0 <= record.reliability <= 1.0 for record in records)

        return {
            "memory_count": len(records),
            "has_trigger_logic": has_triggers,
            "has_behavioral_influence": has_behavior,
            "has_related_links": has_links,
            "has_reliability_scores": has_reliability,
            "strongest_memory_weight": network.get("strongest_memory_weight", 0.0),
            "recurring_object_count": len(network.get("recurring_objects", [])),
            "recurring_people_count": len(network.get("recurring_people", [])),
            "memory_network_ready": bool(network.get("trigger_index")),
            "relationship_simulation_ready": has_triggers and has_behavior and has_links,
            "rag_memory_ready_later": has_reliability and bool(network.get("trigger_index")),
        }

    def _build_next_engine_payload(
        self,
        *,
        character_seed: Dict[str, Any],
        psychology_profile: Dict[str, Any],
        trauma_records: List[Dict[str, Any]],
        emotional_state_profile: Dict[str, Any],
        emotional_arc_profile: Dict[str, Any],
        memory_records: List[MemoryRecord],
        memory_network: Dict[str, Any],
    ) -> Dict[str, Any]:
        merged_seed = dict(character_seed)
        merged_seed["memories"] = [record.model_dump() for record in memory_records]
        merged_seed["memory_network"] = memory_network

        return {
            "character_seed": merged_seed,
            "reputation_engine_payload": {
                "character_seed": merged_seed,
                "memory_records": [record.model_dump() for record in memory_records],
                "memory_network": memory_network,
            },
            "goal_engine_payload": {
                "character_seed": merged_seed,
                "psychology_profile": psychology_profile,
                "memory_records": [record.model_dump() for record in memory_records],
                "emotional_arc_profile": emotional_arc_profile,
            },
            "relationship_simulation_payload_later": {
                "character_id": memory_network.get("character_id"),
                "memory_records": [record.model_dump() for record in memory_records],
                "memory_network": memory_network,
                "emotional_state_profile": emotional_state_profile,
            },
        }

    def _average(self, values: List[float]) -> float:
        if not values:
            return 0.0
        return round(sum(values) / len(values), 3)

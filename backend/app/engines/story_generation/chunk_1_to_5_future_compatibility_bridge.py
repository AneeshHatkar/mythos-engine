from __future__ import annotations

from typing import Any, Dict, Iterable, List, Type

from backend.app.schemas.story_generation import (
    ChunkFutureCompatibilityContract,
    CivilizationReferencePacket,
    CultureReferencePacket,
    DailyLifeReferencePacket,
    DeepWorldReferencePacket,
    EcologyReferencePacket,
    FutureWorldReferencePacket,
    GeographyReferencePacket,
    ObjectArtifactReferencePacket,
    SecretLocationReferencePacket,
    SettlementReferencePacket,
    SpeciesReferencePacket,
    StoryWorldExpansionBridge,
    TravelConstraintReferencePacket,
    WeatherReferencePacket,
    WorldStateMemoryReference,
)


class ChunkOneToFiveFutureCompatibilityBridge:
    PACKET_CLASSES: Dict[str, Type[FutureWorldReferencePacket]] = {
        "deep_world": DeepWorldReferencePacket,
        "geography": GeographyReferencePacket,
        "ecology": EcologyReferencePacket,
        "civilization": CivilizationReferencePacket,
        "species": SpeciesReferencePacket,
        "culture": CultureReferencePacket,
        "settlement": SettlementReferencePacket,
        "object_artifact": ObjectArtifactReferencePacket,
        "weather": WeatherReferencePacket,
        "travel_constraint": TravelConstraintReferencePacket,
        "daily_life": DailyLifeReferencePacket,
        "secret_location": SecretLocationReferencePacket,
    }

    STORY_CONTEXT_KEYS = {
        "deep_world": "deep_world_packets",
        "geography": "geography_packets",
        "ecology": "ecology_packets",
        "civilization": "civilization_packets",
        "species": "species_packets",
        "culture": "culture_packets",
        "settlement": "settlement_packets",
        "object_artifact": "object_artifact_packets",
        "weather": "weather_packets",
        "travel_constraint": "travel_constraint_packets",
        "daily_life": "daily_life_packets",
        "secret_location": "secret_location_packets",
    }

    MEMORY_TYPES = {
        "deep_world": "world_state",
        "geography": "region_state",
        "ecology": "ecology_state",
        "civilization": "civilization_state",
        "species": "species_state",
        "culture": "culture_state",
        "settlement": "settlement_state",
        "object_artifact": "object_artifact_state",
        "weather": "weather_state",
        "travel_constraint": "road_path_state",
        "daily_life": "daily_life_state",
        "secret_location": "secret_location_state",
    }

    REQUIRED_HOOKS = [
        "chunk_1_project_registration",
        "chunk_2_character_reaction_hooks",
        "chunk_3_world_society_extension_hooks",
        "chunk_4_memory_state_update_hooks",
        "chunk_5_story_context_injection_hooks",
        "chunk_5_generation_hint_hooks",
        "chunk_5_benchmark_smoke_feedback_hooks",
    ]

    def build_reference_packet(self, *, packet_type: str, packet_id: str, title: str, summary: str, priority: str = "medium", tags: List[str] | None = None, references: List[str] | None = None, metadata: Dict[str, Any] | None = None) -> FutureWorldReferencePacket:
        packet_key = packet_type.strip().lower()
        packet_class = self.PACKET_CLASSES.get(packet_key, FutureWorldReferencePacket)
        payload = {"packet_id": packet_id, "packet_type": packet_key, "title": title, "summary": summary, "priority": priority, "tags": tags or [], "references": references or [], "metadata": metadata or {}}
        if packet_class is FutureWorldReferencePacket:
            return packet_class(**payload)
        payload.pop("packet_type", None)
        return packet_class(**payload)

    def build_bridge(self, *, source_id: str, packets: Iterable[FutureWorldReferencePacket | Dict[str, Any]], story_context: Dict[str, Any] | None = None) -> Dict[str, StoryWorldExpansionBridge]:
        normalized_packets = [self._coerce_packet(packet) for packet in packets]
        story_context = story_context or {}
        bridge = StoryWorldExpansionBridge(
            bridge_id=f"world_expansion_bridge_{source_id}",
            source_id=source_id,
            packets=normalized_packets,
            story_context_injections={**story_context.get("world_expansion", {}), **self._story_context_injections(normalized_packets)},
            generation_injection_hints=self._generation_hints(normalized_packets),
            memory_update_candidates=self._memory_candidates(source_id=source_id, packets=normalized_packets),
            benchmark_expectations=self._benchmark_expectations(normalized_packets),
            smoke_test_expectations=self._smoke_test_expectations(normalized_packets),
            learning_feedback_tags=self._learning_feedback_tags(normalized_packets),
            warnings=self._warnings(normalized_packets),
        )
        return {"story_world_expansion_bridge": bridge}

    def build_compatibility_contract(self, *, source_id: str, packets: Iterable[FutureWorldReferencePacket | Dict[str, Any]], story_context: Dict[str, Any] | None = None) -> Dict[str, ChunkFutureCompatibilityContract]:
        bridge = self.build_bridge(source_id=source_id, packets=packets, story_context=story_context)["story_world_expansion_bridge"]
        validation_results = self.validate_bridge(bridge=bridge)["validation_results"]
        approved = all(item.get("passed", False) for item in validation_results)
        contract = ChunkFutureCompatibilityContract(
            compatibility_contract_id=f"chunk_1_to_5_future_compatibility_{source_id}",
            source_id=source_id,
            target_future_chunk="chunk_6",
            supported_packet_types=sorted(self.PACKET_CLASSES.keys()),
            required_chunk_1_to_5_hooks=list(self.REQUIRED_HOOKS),
            bridge=bridge,
            approved_for_chunk6_start=approved,
            validation_results=validation_results,
            downstream_constraints={"additive_only": True, "do_not_rename_existing_fields": True, "do_not_replace_existing_engines": True, "chunk_6_must_use_bridge_packets": True},
            warnings=bridge.warnings,
        )
        return {"chunk_future_compatibility_contract": contract}

    def build_story_context_patch(self, *, bridge: StoryWorldExpansionBridge) -> Dict[str, Any]:
        return {
            "world_expansion": bridge.story_context_injections,
            "generation_injection_hints": bridge.generation_injection_hints,
            "world_memory_update_candidates": [candidate.model_dump() for candidate in bridge.memory_update_candidates],
            "world_benchmark_expectations": bridge.benchmark_expectations,
            "world_smoke_test_expectations": bridge.smoke_test_expectations,
            "learning_feedback_tags": bridge.learning_feedback_tags,
        }

    def validate_bridge(self, *, bridge: StoryWorldExpansionBridge) -> Dict[str, Any]:
        packet_types = {packet.packet_type for packet in bridge.packets}
        validation_results = [
            {"check": "has_packets", "passed": bool(bridge.packets), "detail": f"{len(bridge.packets)} packets present."},
            {"check": "has_story_context_injections", "passed": bool(bridge.story_context_injections), "detail": f"{len(bridge.story_context_injections)} story context groups present."},
           {"check": "has_generation_hints", "passed": bool(bridge.generation_injection_hints), "detail": f"{len(bridge.generation_injection_hints)} generation hints present."},
            {"check": "has_memory_candidates", "passed": bool(bridge.memory_update_candidates), "detail": f"{len(bridge.memory_update_candidates)} memory candidates present."},
            {"check": "supported_packet_types", "passed": all(packet_type in self.PACKET_CLASSES for packet_type in packet_types), "detail": f"packet types: {sorted(packet_types)}"},
        ]
        return {"passed": all(item["passed"] for item in validation_results), "validation_results": validation_results}

    def summarize_contract(self, *, contract: ChunkFutureCompatibilityContract) -> Dict[str, Any]:
        bridge = contract.bridge
        return {"success": True, "summary": {"source_id": contract.source_id, "approved_for_chunk6_start": contract.approved_for_chunk6_start, "supported_packet_type_count": len(contract.supported_packet_types), "packet_count": len(bridge.packets) if bridge else 0, "memory_candidate_count": len(bridge.memory_update_candidates) if bridge else 0, "generation_hint_count": len(bridge.generation_injection_hints) if bridge else 0}}

    def _coerce_packet(self, packet: FutureWorldReferencePacket | Dict[str, Any]) -> FutureWorldReferencePacket:
        if isinstance(packet, FutureWorldReferencePacket):
            return packet
        packet_type = str(packet.get("packet_type", "deep_world")).strip().lower()
        packet_class = self.PACKET_CLASSES.get(packet_type, FutureWorldReferencePacket)
        payload = dict(packet)
        if packet_class is FutureWorldReferencePacket:
            payload.setdefault("packet_type", packet_type)
            return packet_class(**payload)
        payload.pop("packet_type", None)
        return packet_class(**payload)

    def _story_context_injections(self, packets: List[FutureWorldReferencePacket]) -> Dict[str, List[Dict[str, Any]]]:
        grouped: Dict[str, List[Dict[str, Any]]] = {}
        for packet in packets:
            key = self.STORY_CONTEXT_KEYS.get(packet.packet_type, "future_world_packets")
            grouped.setdefault(key, []).append({"packet_id": packet.packet_id, "title": packet.title, "summary": packet.summary, "priority": packet.priority, "tags": list(packet.tags), "metadata": dict(packet.metadata)})
        return grouped

    def _memory_candidates(self, *, source_id: str, packets: List[FutureWorldReferencePacket]) -> List[WorldStateMemoryReference]:
        candidates: List[WorldStateMemoryReference] = []
        for packet in packets:
            memory_type = self.MEMORY_TYPES.get(packet.packet_type, "world_state")
            entity = packet.metadata.get("entity_id") or packet.metadata.get("location_id") or packet.title or packet.packet_id
            candidates.append(WorldStateMemoryReference(memory_reference_id=f"memory_{source_id}_{packet.packet_id}", memory_type=memory_type, source_packet_id=packet.packet_id, affected_entity_id=str(entity), state_summary=packet.summary, persistence_level=str(packet.metadata.get("persistence_level", "story")), causal_importance=str(packet.metadata.get("causal_importance", packet.priority)), tags=list(packet.tags), metadata=dict(packet.metadata)))
        return candidates

    def _generation_hints(self, packets: List[FutureWorldReferencePacket]) -> List[Dict[str, Any]]:
        return [{"hint_id": f"generation_hint_{packet.packet_id}", "packet_type": packet.packet_type, "priority": packet.priority, "instruction": f"Use {packet.title or packet.packet_id} as concrete world context: {packet.summary}", "tags": list(packet.tags)} for packet in packets]

    def _benchmark_expectations(self, packets: List[FutureWorldReferencePacket]) -> List[Dict[str, Any]]:
        return [{"expectation_id": f"benchmark_expectation_{packet.packet_id}", "packet_id": packet.packet_id, "must_reference_packet_type": packet.packet_type, "minimum_specificity": "medium"} for packet in packets]

    def _smoke_test_expectations(self, packets: List[FutureWorldReferencePacket]) -> List[Dict[str, Any]]:
        return [{"smoke_expectation_id": f"smoke_expectation_{packet.packet_id}", "packet_id": packet.packet_id, "check": "packet_visible_in_story_context", "required": True} for packet in packets]

    def _learning_feedback_tags(self, packets: List[FutureWorldReferencePacket]) -> List[str]:
        tags = {"chunk6_ready", "deep_world_bridge"}
        for packet in packets:
            tags.add(f"packet:{packet.packet_type}")
            for tag in packet.tags:
                tags.add(f"world_tag:{tag}")
        return sorted(tags)

    def _warnings(self, packets: List[FutureWorldReferencePacket]) -> List[str]:
        warnings = []
        if not packets:
            warnings.append("No future world packets were provided.")
        for packet in packets:
            if not packet.summary:
                warnings.append(f"Packet {packet.packet_id} has no summary.")
        return warnings

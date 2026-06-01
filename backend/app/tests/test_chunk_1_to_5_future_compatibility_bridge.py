from backend.app.engines.story_generation.chunk_1_to_5_future_compatibility_bridge import (
    ChunkOneToFiveFutureCompatibilityBridge,
)
from backend.app.schemas.story_generation import (
    ChunkFutureCompatibilityContract,
    DeepWorldReferencePacket,
    StoryWorldExpansionBridge,
)


def sample_packets():
    bridge = ChunkOneToFiveFutureCompatibilityBridge()
    return [
        bridge.build_reference_packet(packet_type="geography", packet_id="geo_oath_mountains", title="Oath Mountains", summary="A storm-cut mountain chain that isolates the Oath Court from the lowland villages.", priority="high", tags=["mountain", "travel", "isolation"], metadata={"location_id": "loc_oath_mountains", "causal_importance": "high"}),
        bridge.build_reference_packet(packet_type="weather", packet_id="weather_ash_monsoon", title="Ash Monsoon", summary="A seasonal ash rain that changes visibility, travel speed, and ritual timing.", priority="high", tags=["weather", "ritual", "travel"], metadata={"entity_id": "weather_ash_monsoon", "persistence_level": "arc"}),
        {"packet_type": "culture", "packet_id": "culture_bell_oath", "title": "Bell Oath Custom", "summary": "Villagers ring cracked bronze bells before naming a secret in public.", "priority": "medium", "tags": ["culture", "ritual", "secret"], "metadata": {"entity_id": "culture_bell_oath"}},
    ]


def test_future_compatibility_bridge_builds_packets():
    bridge = ChunkOneToFiveFutureCompatibilityBridge()
    packet = bridge.build_reference_packet(packet_type="deep_world", packet_id="deep_world_oath_region", title="Oath Region", summary="A region shaped by old trials, ash storms, and hidden roads.")
    assert isinstance(packet, DeepWorldReferencePacket)
    assert packet.packet_type == "deep_world"
    assert packet.packet_id == "deep_world_oath_region"



def test_future_compatibility_bridge_builds_context_and_memory():
    bridge = ChunkOneToFiveFutureCompatibilityBridge()
    payload = bridge.build_bridge(source_id="future_bridge_source", packets=sample_packets())["story_world_expansion_bridge"]
    assert isinstance(payload, StoryWorldExpansionBridge)
    assert "geography_packets" in payload.story_context_injections
    assert "weather_packets" in payload.story_context_injections
    assert "culture_packets" in payload.story_context_injections
    assert len(payload.memory_update_candidates) == 3
    assert any(candidate.memory_type == "weather_state" for candidate in payload.memory_update_candidates)
    assert payload.generation_injection_hints
    assert payload.benchmark_expectations
    assert payload.smoke_test_expectations
    assert "chunk6_ready" in payload.learning_feedback_tags


def test_future_compatibility_bridge_builds_story_context_patch():
    bridge = ChunkOneToFiveFutureCompatibilityBridge()
    payload = bridge.build_bridge(source_id="future_bridge_source", packets=sample_packets())["story_world_expansion_bridge"]
    patch = bridge.build_story_context_patch(bridge=payload)
    assert "world_expansion" in patch
    assert "world_memory_update_candidates" in patch
    assert "generation_injection_hints" in patch
    assert len(patch["world_memory_update_candidates"]) == 3


def test_future_compatibility_bridge_builds_contract():
    bridge = ChunkOneToFiveFutureCompatibilityBridge()
    contract = bridge.build_compatibility_contract(source_id="future_bridge_source", packets=sample_packets())["chunk_future_compatibility_contract"]
    assert isinstance(contract, ChunkFutureCompatibilityContract)
    assert contract.approved_for_chunk6_start is True
    assert "geography" in contract.supported_packet_types
    assert "chunk_5_story_context_injection_hooks" in contract.required_chunk_1_to_5_hooks
    assert contract.downstream_constraints["additive_only"] is True



def test_future_compatibility_bridge_validates_and_summarizes():
    bridge = ChunkOneToFiveFutureCompatibilityBridge()
    contract = bridge.build_compatibility_contract(source_id="future_bridge_source", packets=sample_packets())["chunk_future_compatibility_contract"]
    validation = bridge.validate_bridge(bridge=contract.bridge)
    summary = bridge.summarize_contract(contract=contract)
    assert validation["passed"] is True
    assert summary["success"] is True
    assert summary["summary"]["approved_for_chunk6_start"] is True
    assert summary["summary"]["packet_count"] == 3

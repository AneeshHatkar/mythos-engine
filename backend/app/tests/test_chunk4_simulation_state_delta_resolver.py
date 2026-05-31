from backend.app.engines.simulation.simulation_state_delta_resolver import SimulationStateDeltaResolver
from backend.app.schemas.simulation import (
    BackstoryDelta,
    BackstoryStatus,
    CastScalingDelta,
    CastScalingPolicy,
    CharacterBackstoryPolicy,
    CharacterImportanceLevel,
    CharacterSourceType,
    DeltaBatch,
    DeltaOperation,
    EmotionDelta,
    KnowledgeDelta,
    MemoryDelta,
    RelationshipDelta,
    ReputationDelta,
    SimulationCharacterState,
    SimulationState,
    SimulationWorldState,
)


def build_state():
    return SimulationState(
        simulation_id="sim_test_001",
        world_state=SimulationWorldState(
            world_id="world_velmora",
            world_simulation_constraints={
                "legal_constraints": ["distrusted family names need sponsor"],
                "power_cost_rules": ["relic power requires cost"],
            },
        ),
        character_states={
            "char_kael": SimulationCharacterState(
                character_id="char_kael",
                current_emotion_state={"emotion_vector": {"hope": 0.2}, "dominant_emotion": "hope"},
                current_memory_state={"active_memory_ids": []},
                current_agency_state={"agency_capacity": 0.7},
            ),
            "char_seren": SimulationCharacterState(
                character_id="char_seren",
                current_emotion_state={"emotion_vector": {"trust": 0.3}, "dominant_emotion": "trust"},
                current_memory_state={"active_memory_ids": []},
            ),
        },
    )


def test_delta_resolver_applies_relationship_delta_and_creates_relationship():
    state = build_state()
    resolver = SimulationStateDeltaResolver()

    delta = RelationshipDelta(
        simulation_id=state.simulation_id,
        source_engine="simulation.relationship_graph_engine",
        operation=DeltaOperation.INCREMENT,
        target_entity_id="rel_kael_seren",
        target_path="relationship_states",
        character_a_id="char_kael",
        character_b_id="char_seren",
        trust_delta=-0.1,
        respect_delta=0.2,
        romantic_tension_delta=0.15,
        rivalry_delta=0.1,
        relationship_event_label="public defense with cost",
    )

    batch = DeltaBatch(
        simulation_id=state.simulation_id,
        source_engine="test",
        relationship_deltas=[delta],
    )

    result = resolver.resolve_delta_batch(state=state, delta_batch=batch)

    updated = result["updated_state"]
    rel = list(updated.relationship_states.values())[0]

    assert result["success"] is True
    assert delta.delta_id in result["applied_delta_ids"]
    assert rel.character_a_id == "char_kael"
    assert rel.character_b_id == "char_seren"
    assert rel.trust == 0.0
    assert rel.respect == 0.2
    assert rel.romantic_tension == 0.15


def test_delta_resolver_rejects_magic_knowledge_without_path():
    state = build_state()
    resolver = SimulationStateDeltaResolver()

    delta = KnowledgeDelta(
        simulation_id=state.simulation_id,
        source_engine="simulation.knowledge_secret_engine",
        operation=DeltaOperation.APPEND,
        target_entity_id="char_kael",
        target_path="knowledge_states.char_kael",
        knowledge_holder_id="char_kael",
        secret_ids_added=["secret_rank_system_edited"],
        no_magic_knowledge_checked=False,
    )

    batch = DeltaBatch(
        simulation_id=state.simulation_id,
        source_engine="test",
        knowledge_deltas=[delta],
    )

    result = resolver.resolve_delta_batch(state=state, delta_batch=batch)

    assert result["success"] is False
    assert delta.delta_id in result["rejected_delta_ids"]
    assert any("no_magic_knowledge_checked" in err for err in result["errors"])


def test_delta_resolver_applies_valid_knowledge_delta():
    state = build_state()
    resolver = SimulationStateDeltaResolver()

    delta = KnowledgeDelta(
        simulation_id=state.simulation_id,
        source_engine="simulation.knowledge_secret_engine",
        operation=DeltaOperation.APPEND,
        target_entity_id="char_kael",
        target_path="knowledge_states.char_kael",
        knowledge_holder_id="char_kael",
        secret_ids_added=["secret_rank_system_edited"],
        evidence_ids_seen=["evidence_cracked_badge"],
        knowledge_path=["found_document", "verified_signature"],
        witness_ids=["char_seren"],
        knowledge_confidence_updates={"secret_rank_system_edited": 0.82},
        no_magic_knowledge_checked=True,
    )

    batch = DeltaBatch(
        simulation_id=state.simulation_id,
        source_engine="test",
        knowledge_deltas=[delta],
    )

    result = resolver.resolve_delta_batch(state=state, delta_batch=batch)

    knowledge = result["updated_state"].knowledge_states["char_kael"]

    assert result["success"] is True
    assert "secret_rank_system_edited" in knowledge.known_secret_ids
    assert "evidence_cracked_badge" in knowledge.evidence_seen_ids
    assert knowledge.knowledge_confidence["secret_rank_system_edited"] == 0.82


def test_delta_resolver_applies_emotion_and_memory_deltas():
    state = build_state()
    resolver = SimulationStateDeltaResolver()

    emotion = EmotionDelta(
        simulation_id=state.simulation_id,
        source_engine="simulation.emotional_carryover_engine",
        operation=DeltaOperation.MERGE,
        target_entity_id="char_kael",
        target_path="character_states.char_kael.current_emotion_state",
        character_id="char_kael",
        emotion_vector_delta={"shame": 0.4, "anger": 0.2},
        dominant_emotion_after="shame",
        triggered_wound="belonging can be revoked publicly",
    )

    memory = MemoryDelta(
        simulation_id=state.simulation_id,
        source_engine="simulation.emotional_carryover_engine",
        operation=DeltaOperation.APPEND,
        target_entity_id="char_kael",
        target_path="character_states.char_kael.current_memory_state",
        character_id="char_kael",
        memory_ids_added=["mem_public_humiliation"],
        trigger_tags_added=["ranking ceremony"],
        dialogue_constraints_added=["avoids admitting shame directly"],
        future_agency_modifiers={"status_sensitivity": 0.7},
    )

    batch = DeltaBatch(
        simulation_id=state.simulation_id,
        source_engine="test",
        emotion_deltas=[emotion],
        memory_deltas=[memory],
    )

    result = resolver.resolve_delta_batch(state=state, delta_batch=batch)
    char = result["updated_state"].character_states["char_kael"]

    assert result["success"] is True
    assert char.current_emotion_state["dominant_emotion"] == "shame"
    assert char.current_emotion_state["emotion_vector"]["shame"] == 0.4
    assert "mem_public_humiliation" in char.current_memory_state["active_memory_ids"]
    assert "ranking ceremony" in char.current_memory_state["trigger_tags"]
    assert char.current_memory_state["future_agency_modifiers"]["status_sensitivity"] == 0.7


def test_delta_resolver_applies_reputation_delta_by_audience():
    state = build_state()
    resolver = SimulationStateDeltaResolver()

    delta = ReputationDelta(
        simulation_id=state.simulation_id,
        source_engine="simulation.reputation_engine",
        operation=DeltaOperation.INCREMENT,
        target_entity_id="char_kael",
        target_path="character_states.char_kael.metadata.reputation_state.public",
        character_id="char_kael",
        audience_type="public",
        reputation_score_delta=-0.2,
        respect_score_delta=0.1,
        rumor_ids_created=["rumor_ranking_failure"],
    )

    batch = DeltaBatch(
        simulation_id=state.simulation_id,
        source_engine="test",
        reputation_deltas=[delta],
    )

    result = resolver.resolve_delta_batch(state=state, delta_batch=batch)
    reputation = result["updated_state"].character_states["char_kael"].metadata["reputation_state"]["public"]

    assert result["success"] is True
    assert reputation["reputation_score"] == 0.3
    assert reputation["respect_score"] == 0.6
    assert "rumor_ranking_failure" in reputation["rumor_ids"]


def test_delta_resolver_applies_cast_scaling_and_backstory_policies():
    state = build_state()
    resolver = SimulationStateDeltaResolver()

    cast_policy = CastScalingPolicy(
        generated_character_count=100,
        manual_character_count=2,
        total_active_character_count=102,
        main_cast_count=9,
        destined_character_count=17,
        scale_warnings=["main_cast_focus_needed"],
    )

    cast_delta = CastScalingDelta(
        simulation_id=state.simulation_id,
        source_engine="simulation.cast_scaling_policy_engine",
        operation=DeltaOperation.MERGE,
        target_entity_id=state.simulation_id,
        target_path="metadata.cast_scaling_policy",
        cast_scaling_policy_after=cast_policy,
    )

    backstory_policy = CharacterBackstoryPolicy(
        character_id="char_kael",
        source_type=CharacterSourceType.USER_CREATED,
        importance_level=CharacterImportanceLevel.CORE_CHARACTER,
        backstory_status=BackstoryStatus.DEEP,
        expandable_character=True,
        required_backstory_fields=["origin", "family_pressure", "formative_memories"],
    )

    backstory_delta = BackstoryDelta(
        simulation_id=state.simulation_id,
        source_engine="simulation.backstory_expansion_engine",
        operation=DeltaOperation.MERGE,
        target_entity_id="char_kael",
        target_path="character_states.char_kael.metadata.backstory_policy",
        character_id="char_kael",
        backstory_policy_after=backstory_policy,
        backstory_fields_added={"origin": "Scholarship student with distrusted family records."},
        formative_memory_ids_added=["mem_first_public_failure"],
        expansion_triggered=True,
    )

    batch = DeltaBatch(
        simulation_id=state.simulation_id,
        source_engine="test",
        cast_scaling_deltas=[cast_delta],
        backstory_deltas=[backstory_delta],
    )

    result = resolver.resolve_delta_batch(state=state, delta_batch=batch)
    updated = result["updated_state"]

    assert result["success"] is True
    assert updated.metadata["cast_scaling_policy"]["no_fixed_cast_limit"] is True
    assert updated.metadata["cast_scaling_policy"]["total_active_character_count"] == 102
    assert updated.character_states["char_kael"].metadata["backstory_policy"]["backstory_status"] == "deep"
    assert updated.character_states["char_kael"].metadata["backstory_state"]["origin"]


def test_delta_resolver_preserves_original_state_immutability():
    state = build_state()
    resolver = SimulationStateDeltaResolver()

    delta = EmotionDelta(
        simulation_id=state.simulation_id,
        source_engine="simulation.emotional_carryover_engine",
        operation=DeltaOperation.MERGE,
        target_entity_id="char_kael",
        target_path="character_states.char_kael.current_emotion_state",
        character_id="char_kael",
        emotion_vector_delta={"shame": 0.4},
    )

    batch = DeltaBatch(
        simulation_id=state.simulation_id,
        source_engine="test",
        emotion_deltas=[delta],
    )

    result = resolver.resolve_delta_batch(state=state, delta_batch=batch)

    assert "shame" not in state.character_states["char_kael"].current_emotion_state["emotion_vector"]
    assert "shame" in result["updated_state"].character_states["char_kael"].current_emotion_state["emotion_vector"]


def test_delta_resolver_rejects_wrong_simulation_id():
    state = build_state()
    resolver = SimulationStateDeltaResolver()

    delta = EmotionDelta(
        simulation_id="sim_wrong",
        source_engine="simulation.emotional_carryover_engine",
        operation=DeltaOperation.MERGE,
        target_entity_id="char_kael",
        target_path="character_states.char_kael.current_emotion_state",
        character_id="char_kael",
        emotion_vector_delta={"shame": 0.4},
    )

    batch = DeltaBatch(
        simulation_id=state.simulation_id,
        source_engine="test",
        emotion_deltas=[delta],
    )

    result = resolver.resolve_delta_batch(state=state, delta_batch=batch)

    assert result["success"] is False
    assert delta.delta_id in result["rejected_delta_ids"]
    assert any("simulation_id does not match" in err for err in result["errors"])

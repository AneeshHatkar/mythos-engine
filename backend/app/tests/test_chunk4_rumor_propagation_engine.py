from backend.app.engines.simulation.rumor_propagation_engine import RumorPropagationEngine
from backend.app.schemas.simulation import (
    SimulationCharacterState,
    SimulationEventPayload,
    SimulationEventType,
    SimulationEventVisibility,
    SimulationRelationshipState,
    SimulationState,
    SimulationWorldState,
)


def build_state():
    return SimulationState(
        simulation_id="sim_rumor_001",
        world_state=SimulationWorldState(
            world_id="world_velmora",
            metadata={
                "rumor_edges": [
                    {
                        "from_location_id": "location_court",
                        "to_location_id": "location_outer",
                        "bidirectional": True,
                    }
                ]
            },
        ),
        character_states={
            "char_kael": SimulationCharacterState(character_id="char_kael", current_location_id="location_court"),
            "char_seren": SimulationCharacterState(character_id="char_seren", current_location_id="location_court"),
            "char_vask": SimulationCharacterState(character_id="char_vask", current_location_id="location_outer"),
            "char_mira": SimulationCharacterState(character_id="char_mira", current_location_id="location_outer"),
        },
        relationship_states={
            "rel_seren_kael": SimulationRelationshipState(
                relationship_id="rel_seren_kael",
                character_a_id="char_seren",
                character_b_id="char_kael",
                trust=0.65,
                respect=0.5,
                resentment=0.1,
            )
        },
    )


def test_rumor_engine_creates_and_registers_rumor():
    state = build_state()
    engine = RumorPropagationEngine()

    rumor = engine.create_rumor_record(
        rumor_id="rumor_rank_edit",
        source_event_id="evt_trial",
        originator_id="char_seren",
        claim="The academy ranking was edited.",
        linked_secret_ids=["secret_rank_system_edited"],
        linked_evidence_ids=["evidence_cracked_badge"],
        truth_status="partially_true",
        credibility=0.72,
        audience_ids=["char_kael"],
    )

    result = engine.register_rumor_on_state(state=state, rumor_record=rumor)

    assert result["success"] is True
    assert "rumor_rank_edit" in state.metadata["rumor_registry"]
    assert "rumor_rank_edit" in state.knowledge_states["char_kael"].rumors_heard_ids
    assert "secret_rank_system_edited" in state.knowledge_states["char_kael"].suspected_secret_ids


def test_rumor_engine_creates_rumor_from_public_event():
    state = build_state()
    engine = RumorPropagationEngine()

    event = SimulationEventPayload(
        event_id="evt_public_humiliation",
        event_type=SimulationEventType.PUBLIC_HUMILIATION,
        actor_ids=["char_seren"],
        target_ids=["char_kael"],
        witness_ids=["char_vask"],
        location_id="location_court",
        visibility=SimulationEventVisibility.PUBLIC,
        intensity=0.8,
    )

    result = engine.create_rumor_from_event(
        state=state,
        event_payload=event,
        originator_id="char_vask",
        claim="Kael was exposed during the ranking ceremony.",
        target_character_ids=["char_kael"],
    )

    rumor = result["rumor_record"]

    assert result["success"] is True
    assert rumor["source_event_id"] == "evt_public_humiliation"
    assert "char_vask" in result["initial_audience_ids"]
    assert "char_kael" in rumor["target_character_ids"]
    assert rumor["credibility"] > 0.4


def test_rumor_engine_propagates_to_reachable_audience():
    state = build_state()
    engine = RumorPropagationEngine()

    rumor = engine.create_rumor_record(
        rumor_id="rumor_rank_edit",
        source_event_id="evt_trial",
        originator_id="char_seren",
        claim="The academy ranking was edited.",
        linked_secret_ids=["secret_rank_system_edited"],
        truth_status="partially_true",
        credibility=0.78,
        emotional_charge=0.8,
        origin_location_id="location_court",
        audience_ids=["char_seren"],
    )
    engine.register_rumor_on_state(state=state, rumor_record=rumor)

    result = engine.propagate_rumor(
        state=state,
        rumor_id="rumor_rank_edit",
        spreader_id="char_seren",
        max_depth=1,
    )

    assert result["success"] is True
    assert "char_kael" in result["new_listeners"]
    assert "char_vask" in result["new_listeners"] or "char_mira" in result["new_listeners"]
    assert state.metadata["rumor_registry"]["rumor_rank_edit"]["mutation_history"]


def test_rumor_engine_blocks_spreader_who_has_not_heard_rumor():
    state = build_state()
    engine = RumorPropagationEngine()

    rumor = engine.create_rumor_record(
        rumor_id="rumor_rank_edit",
        source_event_id="evt_trial",
        originator_id="char_seren",
        claim="The academy ranking was edited.",
        audience_ids=["char_seren"],
    )
    engine.register_rumor_on_state(state=state, rumor_record=rumor)

    result = engine.propagate_rumor(
        state=state,
        rumor_id="rumor_rank_edit",
        spreader_id="char_vask",
    )

    assert result["success"] is False
    assert any("has not heard rumor" in blocker for blocker in result["blockers"])


def test_rumor_engine_builds_knowledge_delta_from_rumor():
    state = build_state()
    engine = RumorPropagationEngine()

    rumor = engine.create_rumor_record(
        rumor_id="rumor_rank_edit",
        source_event_id="evt_trial",
        originator_id="char_seren",
        claim="The academy ranking was edited.",
        linked_secret_ids=["secret_rank_system_edited"],
        truth_status="partially_true",
        credibility=0.8,
        emotional_charge=0.7,
        audience_ids=["char_seren"],
    )
    engine.register_rumor_on_state(state=state, rumor_record=rumor)

    delta = engine.build_knowledge_delta_from_rumor(
        state=state,
        rumor_id="rumor_rank_edit",
        listener_id="char_kael",
    )

    assert delta.no_magic_knowledge_checked is True
    assert "rumor_rank_edit" in delta.rumor_ids_heard
    assert "secret_rank_system_edited" in delta.suspected_secret_ids_added
    assert delta.knowledge_path == ["rumor_heard"]


def test_rumor_engine_builds_reputation_delta_from_rumor():
    state = build_state()
    engine = RumorPropagationEngine()

    rumor = engine.create_rumor_record(
        rumor_id="rumor_kael_exposed",
        source_event_id="evt_humiliation",
        originator_id="char_vask",
        claim="Kael failed publicly.",
        target_character_ids=["char_kael"],
        credibility=0.75,
        emotional_charge=0.85,
        distortion_level=0.2,
    )
    engine.register_rumor_on_state(state=state, rumor_record=rumor)

    delta = engine.build_reputation_delta_from_rumor(
        state=state,
        rumor_id="rumor_kael_exposed",
        target_character_id="char_kael",
    )

    assert delta.character_id == "char_kael"
    assert delta.reputation_score_delta < 0
    assert delta.trust_score_delta < 0
    assert "rumor_kael_exposed" in delta.rumor_ids_amplified


def test_rumor_engine_suppresses_rumor():
    state = build_state()
    engine = RumorPropagationEngine()

    rumor = engine.create_rumor_record(
        rumor_id="rumor_rank_edit",
        source_event_id="evt_trial",
        originator_id="char_seren",
        claim="The academy ranking was edited.",
        credibility=0.8,
        distortion_level=0.2,
    )
    engine.register_rumor_on_state(state=state, rumor_record=rumor)

    result = engine.suppress_rumor(
        state=state,
        rumor_id="rumor_rank_edit",
        suppressor_id="faction_oath_court",
        suppression_power=0.6,
        reason="Court censorship.",
    )

    updated = result["updated_rumor"]

    assert result["success"] is True
    assert "faction_oath_court" in updated["suppressed_by_ids"]
    assert updated["credibility"] < 0.8
    assert updated["distortion_level"] > 0.2


def test_rumor_engine_builds_rumor_map():
    state = build_state()
    engine = RumorPropagationEngine()

    rumor = engine.create_rumor_record(
        rumor_id="rumor_rank_edit",
        source_event_id="evt_trial",
        originator_id="char_seren",
        claim="The academy ranking was edited.",
        linked_secret_ids=["secret_rank_system_edited"],
        target_character_ids=["char_kael"],
        credibility=0.8,
        distortion_level=0.2,
        emotional_charge=0.9,
        audience_ids=["char_kael", "char_vask"],
    )
    engine.register_rumor_on_state(state=state, rumor_record=rumor)

    rumor_map = engine.build_rumor_map(state=state)

    record = rumor_map["rumor_records"]["rumor_rank_edit"]

    assert rumor_map["success"] is True
    assert rumor_map["rumor_count"] == 1
    assert record["heard_by_count"] == 2
    assert record["spread_risk"] > 0.5
    assert record["reputation_risk"] > 0.4


def test_rumor_engine_builds_delta_batch_for_rumor_spread():
    state = build_state()
    engine = RumorPropagationEngine()

    rumor = engine.create_rumor_record(
        rumor_id="rumor_rank_edit",
        source_event_id="evt_trial",
        originator_id="char_seren",
        claim="The academy ranking was edited.",
        linked_secret_ids=["secret_rank_system_edited"],
        target_character_ids=["char_kael"],
        truth_status="partially_true",
        credibility=0.8,
        audience_ids=["char_seren"],
    )
    engine.register_rumor_on_state(state=state, rumor_record=rumor)

    batch = engine.build_delta_batch_for_rumor_spread(
        state=state,
        rumor_id="rumor_rank_edit",
        listener_ids=["char_kael", "char_vask"],
        target_character_ids=["char_kael"],
    )

    assert batch.source_engine == engine.engine_name
    assert len(batch.knowledge_deltas) == 2
    assert len(batch.reputation_deltas) == 1
    assert batch.application_order == [delta.delta_id for delta in batch.knowledge_deltas + batch.reputation_deltas]

from backend.app.engines.simulation.knowledge_secret_state_engine import KnowledgeSecretStateEngine
from backend.app.schemas.simulation import (
    SimulationCharacterState,
    SimulationEventPayload,
    SimulationEventType,
    SimulationEventVisibility,
    SimulationState,
    SimulationWorldState,
)


def build_state():
    return SimulationState(
        simulation_id="sim_knowledge_001",
        world_state=SimulationWorldState(world_id="world_velmora"),
        character_states={
            "char_kael": SimulationCharacterState(character_id="char_kael"),
            "char_seren": SimulationCharacterState(character_id="char_seren"),
            "char_vask": SimulationCharacterState(character_id="char_vask"),
        },
    )


def test_knowledge_engine_registers_secret_and_updates_knowers():
    state = build_state()
    engine = KnowledgeSecretStateEngine()

    secret = engine.create_secret_record(
        secret_id="secret_rank_system_edited",
        truth_statement="The academy ranking system was edited by the court.",
        owner_ids=["faction_oath_court"],
        knower_ids=["char_seren"],
        suspect_ids=["char_kael"],
        false_believer_ids=["char_vask"],
        evidence_ids=["evidence_cracked_badge"],
        public_if_revealed=True,
    )

    result = engine.register_secret_on_state(state=state, secret_record=secret)

    assert result["success"] is True
    assert "secret_rank_system_edited" in state.metadata["secret_registry"]
    assert "secret_rank_system_edited" in state.knowledge_states["char_seren"].known_secret_ids
    assert "secret_rank_system_edited" in state.knowledge_states["char_kael"].suspected_secret_ids
    assert "falsehood_about_secret_rank_system_edited" in state.knowledge_states["char_vask"].believed_falsehood_ids


def test_knowledge_engine_initializes_knowledge_state():
    state = build_state()
    engine = KnowledgeSecretStateEngine()

    result = engine.initialize_knowledge_state(
        state=state,
        entity_id="char_kael",
        known_secret_ids=["secret_a"],
        suspected_secret_ids=["secret_b"],
        evidence_seen_ids=["evidence_1"],
    )

    assert result["success"] is True
    assert state.knowledge_states["char_kael"].known_secret_ids == ["secret_a"]
    assert state.knowledge_states["char_kael"].suspected_secret_ids == ["secret_b"]
    assert state.knowledge_states["char_kael"].evidence_seen_ids == ["evidence_1"]


def test_knowledge_engine_infers_direct_witness_path():
    state = build_state()
    engine = KnowledgeSecretStateEngine()

    event = SimulationEventPayload(
        event_type=SimulationEventType.SECRET_DISCOVERY,
        actor_ids=["char_seren"],
        witness_ids=["char_kael"],
        location_id="location_court",
        visibility=SimulationEventVisibility.WITNESSED,
    )

    path = engine.infer_knowledge_path(
        state=state,
        event_payload=event,
        knowledge_holder_id="char_kael",
        evidence_ids=["evidence_cracked_badge"],
    )

    assert path["valid"] is True
    assert "direct_witness" in path["knowledge_path"]
    assert "evidence_seen" in path["knowledge_path"]
    assert path["witness_ids"] == ["char_kael"]


def test_knowledge_engine_blocks_reader_only_magic_knowledge():
    state = build_state()
    engine = KnowledgeSecretStateEngine()

    event = SimulationEventPayload(
        event_type=SimulationEventType.SECRET_DISCOVERY,
        actor_ids=["char_seren"],
        witness_ids=[],
        visibility=SimulationEventVisibility.READER_ONLY,
    )

    path = engine.infer_knowledge_path(
        state=state,
        event_payload=event,
        knowledge_holder_id="char_kael",
    )

    assert path["valid"] is False
    assert any("reader-only" in blocker for blocker in path["blockers"])


def test_knowledge_engine_builds_valid_knowledge_delta_from_event():
    state = build_state()
    engine = KnowledgeSecretStateEngine()

    event = SimulationEventPayload(
        event_id="evt_secret_reveal",
        event_type=SimulationEventType.SECRET_DISCOVERY,
        actor_ids=["char_seren"],
        target_ids=["char_kael"],
        witness_ids=["char_kael"],
        visibility=SimulationEventVisibility.WITNESSED,
    )

    delta = engine.build_knowledge_delta_from_event(
        state=state,
        event_payload=event,
        knowledge_holder_id="char_kael",
        secret_ids_added=["secret_rank_system_edited"],
        evidence_ids_seen=["evidence_cracked_badge"],
        confidence=0.88,
    )

    assert delta.no_magic_knowledge_checked is True
    assert "secret_rank_system_edited" in delta.secret_ids_added
    assert "evidence_cracked_badge" in delta.evidence_ids_seen
    assert delta.knowledge_confidence_updates["secret_rank_system_edited"] == 0.88
    assert delta.source_event_id == "evt_secret_reveal"


def test_knowledge_engine_evaluates_secret_exposure():
    state = build_state()
    engine = KnowledgeSecretStateEngine()

    secret = engine.create_secret_record(
        secret_id="secret_rank_system_edited",
        truth_statement="The academy ranking system was edited.",
        knower_ids=["char_seren"],
        evidence_ids=["evidence_cracked_badge"],
        public_if_revealed=True,
        exposure_difficulty=0.3,
    )
    engine.register_secret_on_state(state=state, secret_record=secret)
    state.knowledge_states["char_seren"].evidence_seen_ids.append("evidence_cracked_badge")

    exposure = engine.evaluate_secret_exposure(
        state=state,
        secret_id="secret_rank_system_edited",
        exposer_id="char_seren",
        audience_ids=["char_kael", "char_vask"],
        evidence_ids_used=["evidence_cracked_badge"],
    )

    assert exposure["success"] is True
    assert exposure["can_expose"] is True
    assert exposure["exposure_strength"] > 0.5
    assert "exposer_knows_secret" in exposure["passed_checks"]


def test_knowledge_engine_blocks_exposure_by_non_knower():
    state = build_state()
    engine = KnowledgeSecretStateEngine()

    secret = engine.create_secret_record(
        secret_id="secret_rank_system_edited",
        truth_statement="The academy ranking system was edited.",
        knower_ids=["char_seren"],
        evidence_ids=["evidence_cracked_badge"],
    )
    engine.register_secret_on_state(state=state, secret_record=secret)

    exposure = engine.evaluate_secret_exposure(
        state=state,
        secret_id="secret_rank_system_edited",
        exposer_id="char_kael",
        audience_ids=["char_vask"],
        evidence_ids_used=["evidence_cracked_badge"],
    )

    assert exposure["can_expose"] is False
    assert any("does not know" in blocker for blocker in exposure["blockers"])


def test_knowledge_engine_exposes_secret_to_audience():
    state = build_state()
    engine = KnowledgeSecretStateEngine()

    secret = engine.create_secret_record(
        secret_id="secret_rank_system_edited",
        truth_statement="The academy ranking system was edited.",
        knower_ids=["char_seren"],
        evidence_ids=["evidence_cracked_badge"],
        public_if_revealed=True,
    )
    engine.register_secret_on_state(state=state, secret_record=secret)
    state.knowledge_states["char_seren"].evidence_seen_ids.append("evidence_cracked_badge")

    result = engine.expose_secret(
        state=state,
        secret_id="secret_rank_system_edited",
        exposer_id="char_seren",
        audience_ids=["char_kael", "char_vask"],
        source_event_id="evt_trial",
        evidence_ids_used=["evidence_cracked_badge"],
    )

    assert result["success"] is True
    assert state.metadata["secret_registry"]["secret_rank_system_edited"]["exposed"] is True
    assert "secret_rank_system_edited" in state.knowledge_states["char_kael"].known_secret_ids
    assert "secret_rank_system_edited" in state.knowledge_states["char_vask"].known_secret_ids
    assert "secret_rank_system_edited" in state.metadata["public_knowledge_ids"]


def test_knowledge_engine_builds_secret_map_and_dramatic_irony():
    state = build_state()
    engine = KnowledgeSecretStateEngine()

    secret = engine.create_secret_record(
        secret_id="secret_rank_system_edited",
        truth_statement="The academy ranking system was edited.",
        knower_ids=["char_seren"],
        suspect_ids=["char_kael"],
        false_believer_ids=["char_vask"],
        evidence_ids=["evidence_cracked_badge"],
    )
    engine.register_secret_on_state(state=state, secret_record=secret)
    state.knowledge_states["char_seren"].evidence_seen_ids.append("evidence_cracked_badge")

    secret_map = engine.build_secret_map(state=state)

    record = secret_map["secret_records"]["secret_rank_system_edited"]

    assert secret_map["success"] is True
    assert secret_map["secret_count"] == 1
    assert "char_seren" in record["known_by"]
    assert "char_kael" in record["suspected_by"]
    assert "char_vask" in record["false_believed_by"]
    assert secret_map["dramatic_irony_records"]


def test_knowledge_engine_builds_delta_batch_for_secret_reveal():
    state = build_state()
    engine = KnowledgeSecretStateEngine()

    event = SimulationEventPayload(
        event_id="evt_trial_reveal",
        event_type=SimulationEventType.TRIAL,
        actor_ids=["char_seren"],
        witness_ids=["char_kael", "char_vask"],
        visibility=SimulationEventVisibility.PUBLIC,
    )

    batch = engine.build_delta_batch_for_secret_reveal(
        state=state,
        event_payload=event,
        secret_id="secret_rank_system_edited",
        reveal_to_ids=["char_kael", "char_vask"],
        evidence_ids_seen=["evidence_cracked_badge"],
    )

    assert batch.source_engine == engine.engine_name
    assert len(batch.knowledge_deltas) == 2
    assert batch.knowledge_deltas[0].no_magic_knowledge_checked is True
    assert batch.application_order == [delta.delta_id for delta in batch.knowledge_deltas]

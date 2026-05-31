from backend.app.engines.simulation.negotiation_bargain_engine import NegotiationBargainEngine
from backend.app.schemas.simulation import (
    SimulationCharacterState,
    SimulationEventPayload,
    SimulationEventType,
    SimulationEventVisibility,
    SimulationKnowledgeState,
    SimulationRelationshipState,
    SimulationState,
    SimulationWorldState,
)


def build_state():
    return SimulationState(
        simulation_id="sim_bargain_001",
        world_state=SimulationWorldState(world_id="world_velmora"),
        character_states={
            "char_kael": SimulationCharacterState(character_id="char_kael"),
            "char_seren": SimulationCharacterState(character_id="char_seren"),
            "char_vask": SimulationCharacterState(character_id="char_vask"),
        },
        knowledge_states={
            "char_seren": SimulationKnowledgeState(
                entity_id="char_seren",
                known_secret_ids=["secret_rank_system_edited"],
                evidence_seen_ids=["evidence_cracked_badge"],
            )
        },
        relationship_states={
            "rel_char_kael_char_seren": SimulationRelationshipState(
                relationship_id="rel_char_kael_char_seren",
                character_a_id="char_kael",
                character_b_id="char_seren",
                trust=0.55,
                respect=0.6,
                loyalty=0.25,
                betrayal_risk=0.2,
                resentment=0.1,
            )
        },
    )


def add_supporting_state(state):
    state.metadata.setdefault("obligation_registry", {})["obl_trial_testimony"] = {
        "obligation_id": "obl_trial_testimony",
        "status": "active",
    }


def test_negotiation_engine_creates_and_registers_bargain():
    state = build_state()
    engine = NegotiationBargainEngine()

    bargain = engine.create_bargain_record(
        bargain_id="bar_seren_kael_trial_deal",
        negotiation_type="trial_deal",
        proposer_id="char_seren",
        receiver_id="char_kael",
        offer_summary="Seren offers evidence if Kael protects her source.",
        requested_terms=["protect source"],
        offered_terms=["share evidence"],
        linked_secret_ids=["secret_rank_system_edited"],
        linked_evidence_ids=["evidence_cracked_badge"],
        fairness_score=0.7,
    )

    result = engine.register_bargain_on_state(state=state, bargain_record=bargain)

    assert result["success"] is True
    assert "bar_seren_kael_trial_deal" in state.metadata["bargain_registry"]
    assert "bar_seren_kael_trial_deal" in state.character_states["char_seren"].metadata["bargain_ids"]
    assert "bar_seren_kael_trial_deal" in state.character_states["char_kael"].metadata["bargain_ids"]


def test_negotiation_engine_creates_bargain_from_event():
    state = build_state()
    engine = NegotiationBargainEngine()

    event = SimulationEventPayload(
        event_id="evt_trial_negotiation",
        event_type=SimulationEventType.NEGOTIATION_OFFER,
        actor_ids=["char_seren"],
        target_ids=["char_kael"],
        visibility=SimulationEventVisibility.PRIVATE,
        intensity=0.65,
        involved_faction_ids=["faction_oath_court"],
        metadata={
            "requested_terms": ["protect source"],
            "offered_terms": ["share evidence"],
            "linked_secret_ids": ["secret_rank_system_edited"],
            "linked_evidence_ids": ["evidence_cracked_badge"],
            "fairness_score": 0.72,
            "trust_requirement": 0.5,
        },
    )

    result = engine.create_bargain_from_event(
        state=state,
        event_payload=event,
        proposer_id="char_seren",
        receiver_id="char_kael",
        offer_summary="Evidence in exchange for source protection.",
        negotiation_type="trial_deal",
    )

    bargain = result["bargain_record"]

    assert result["success"] is True
    assert bargain["bargain_id"] == "bar_evt_trial_negotiation_char_seren_char_kael"
    assert bargain["linked_faction_ids"] == ["faction_oath_court"]
    assert bargain["fairness_score"] == 0.72


def test_negotiation_engine_evaluates_viable_bargain():
    state = build_state()
    add_supporting_state(state)
    engine = NegotiationBargainEngine()

    bargain = engine.create_bargain_record(
        bargain_id="bar_seren_kael_trial_deal",
        negotiation_type="trial_deal",
        proposer_id="char_seren",
        receiver_id="char_kael",
        offer_summary="Seren offers evidence if Kael protects her source.",
        requested_terms=["protect source"],
        offered_terms=["share evidence"],
        linked_secret_ids=["secret_rank_system_edited"],
        linked_evidence_ids=["evidence_cracked_badge"],
        linked_obligation_ids=["obl_trial_testimony"],
        fairness_score=0.7,
    )
    engine.register_bargain_on_state(state=state, bargain_record=bargain)

    report = engine.evaluate_bargain_viability(
        state=state,
        bargain_id="bar_seren_kael_trial_deal",
    )

    assert report["success"] is True
    assert report["viable"] is True
    assert report["acceptance_probability"] > 0.3
    assert "proposer_knows_secret_rank_system_edited" in report["passed_checks"]
    assert "obligation_obl_trial_testimony_usable" in report["passed_checks"]


def test_negotiation_engine_blocks_secret_bargain_without_knowledge():
    state = build_state()
    engine = NegotiationBargainEngine()

    bargain = engine.create_bargain_record(
        bargain_id="bar_kael_invalid",
        negotiation_type="secret_exchange",
        proposer_id="char_kael",
        receiver_id="char_seren",
        offer_summary="Kael offers a secret he does not know.",
        linked_secret_ids=["secret_rank_system_edited"],
    )
    engine.register_bargain_on_state(state=state, bargain_record=bargain)

    report = engine.evaluate_bargain_viability(state=state, bargain_id="bar_kael_invalid")

    assert report["viable"] is False
    assert any("does not know/suspect" in blocker for blocker in report["blockers"])


def test_negotiation_engine_creates_counteroffer():
    state = build_state()
    engine = NegotiationBargainEngine()

    bargain = engine.create_bargain_record(
        bargain_id="bar_initial",
        negotiation_type="trial_deal",
        proposer_id="char_seren",
        receiver_id="char_kael",
        offer_summary="Initial deal.",
    )
    engine.register_bargain_on_state(state=state, bargain_record=bargain)

    result = engine.create_counteroffer(
        state=state,
        parent_bargain_id="bar_initial",
        counteroffer_id="bar_counter",
        proposer_id="char_kael",
        receiver_id="char_seren",
        offer_summary="Counter terms.",
        requested_terms=["public testimony"],
        offered_terms=["source protection"],
    )

    assert result["success"] is True
    assert state.metadata["bargain_registry"]["bar_initial"]["status"] == "countered"
    assert "bar_counter" in state.metadata["bargain_registry"]["bar_initial"]["counteroffer_ids"]
    assert "bar_counter" in state.metadata["bargain_registry"]


def test_negotiation_engine_resolves_bargain_outcome():
    state = build_state()
    engine = NegotiationBargainEngine()

    bargain = engine.create_bargain_record(
        bargain_id="bar_initial",
        negotiation_type="trial_deal",
        proposer_id="char_seren",
        receiver_id="char_kael",
        offer_summary="Initial deal.",
    )
    engine.register_bargain_on_state(state=state, bargain_record=bargain)

    result = engine.resolve_bargain_outcome(
        state=state,
        bargain_id="bar_initial",
        outcome="accepted",
        outcome_event_id="evt_accept",
        notes="Kael accepts the terms.",
    )

    updated = result["updated_bargain"]

    assert result["success"] is True
    assert updated["status"] == "accepted"
    assert "evt_accept" in updated["acceptance_event_ids"]
    assert "Kael accepts the terms." in updated["resolution_notes"]


def test_negotiation_engine_builds_relationship_delta_for_fulfilled_bargain():
    state = build_state()
    engine = NegotiationBargainEngine()

    bargain = engine.create_bargain_record(
        bargain_id="bar_seren_kael",
        negotiation_type="trial_deal",
        proposer_id="char_seren",
        receiver_id="char_kael",
        offer_summary="Trial bargain.",
        requested_terms=["protect source"],
        offered_terms=["evidence"],
        fairness_score=0.8,
    )
    engine.register_bargain_on_state(state=state, bargain_record=bargain)

    delta = engine.build_relationship_delta_from_bargain(
        state=state,
        bargain_id="bar_seren_kael",
        outcome="fulfilled",
    )

    assert delta.relationship_id == "rel_char_kael_char_seren"
    assert delta.trust_delta > 0
    assert delta.respect_delta > 0
    assert delta.loyalty_delta > 0


def test_negotiation_engine_builds_knowledge_delta_from_bargain():
    state = build_state()
    engine = NegotiationBargainEngine()

    bargain = engine.create_bargain_record(
        bargain_id="bar_secret_exchange",
        negotiation_type="secret_exchange",
        proposer_id="char_seren",
        receiver_id="char_kael",
        offer_summary="Secret exchange.",
        linked_secret_ids=["secret_rank_system_edited"],
        linked_evidence_ids=["evidence_cracked_badge"],
    )
    engine.register_bargain_on_state(state=state, bargain_record=bargain)

    delta = engine.build_knowledge_delta_from_bargain(
        state=state,
        bargain_id="bar_secret_exchange",
        receiver_id="char_kael",
    )

    assert delta.no_magic_knowledge_checked is True
    assert "secret_rank_system_edited" in delta.suspected_secret_ids_added
    assert "evidence_cracked_badge" in delta.evidence_ids_seen
    assert delta.knowledge_path == ["bargain_exchange"]


def test_negotiation_engine_builds_delta_batch_for_bargain_outcome():
    state = build_state()
    engine = NegotiationBargainEngine()

    bargain = engine.create_bargain_record(
        bargain_id="bar_full",
        negotiation_type="faction_treaty",
        proposer_id="char_seren",
        receiver_id="char_kael",
        offer_summary="Faction-backed deal.",
        linked_secret_ids=["secret_rank_system_edited"],
        linked_evidence_ids=["evidence_cracked_badge"],
        linked_resource_ids=["resource_archive_access"],
        linked_faction_ids=["faction_oath_court"],
    )
    engine.register_bargain_on_state(state=state, bargain_record=bargain)

    batch = engine.build_delta_batch_for_bargain_outcome(
        state=state,
        bargain_id="bar_full",
        outcome="accepted",
    )

    assert batch.source_engine == engine.engine_name
    assert len(batch.relationship_deltas) == 1
    assert len(batch.knowledge_deltas) == 1
    assert len(batch.resource_deltas) == 1
    assert len(batch.faction_deltas) == 1
    assert batch.application_order == [
        batch.relationship_deltas[0].delta_id,
        batch.knowledge_deltas[0].delta_id,
        batch.resource_deltas[0].delta_id,
        batch.faction_deltas[0].delta_id,
    ]


def test_negotiation_engine_builds_bargain_map():
    state = build_state()
    engine = NegotiationBargainEngine()

    bargain = engine.create_bargain_record(
        bargain_id="bar_low_acceptance",
        negotiation_type="trial_deal",
        proposer_id="char_seren",
        receiver_id="char_kael",
        offer_summary="Unfair bargain.",
        fairness_score=0.1,
        trust_requirement=0.9,
        betrayal_risk=0.8,
        pressure_level=0.1,
    )
    engine.register_bargain_on_state(state=state, bargain_record=bargain)

    bargain_map = engine.build_bargain_map(state=state)

    record = bargain_map["bargain_records"]["bar_low_acceptance"]

    assert bargain_map["success"] is True
    assert bargain_map["bargain_count"] == 1
    assert record["acceptance_probability"] < 0.5
    assert "trust_fit" in record

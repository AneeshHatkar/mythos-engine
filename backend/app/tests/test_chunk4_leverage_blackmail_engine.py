from backend.app.engines.simulation.leverage_blackmail_engine import LeverageBlackmailEngine
from backend.app.schemas.simulation import (
    SimulationCharacterState,
    SimulationEventPayload,
    SimulationEventType,
    SimulationEventVisibility,
    SimulationKnowledgeState,
    SimulationState,
    SimulationWorldState,
)


def build_state():
    return SimulationState(
        simulation_id="sim_leverage_001",
        world_state=SimulationWorldState(world_id="world_velmora"),
        character_states={
            "char_kael": SimulationCharacterState(character_id="char_kael"),
            "char_seren": SimulationCharacterState(character_id="char_seren"),
            "char_vask": SimulationCharacterState(character_id="char_vask"),
        },
        knowledge_states={
            "char_vask": SimulationKnowledgeState(
                entity_id="char_vask",
                known_secret_ids=["secret_rank_system_edited"],
                evidence_seen_ids=["evidence_cracked_badge"],
            )
        },
    )


def add_evidence_and_obligation(state):
    state.metadata.setdefault("evidence_registry", {})["evidence_cracked_badge"] = {
        "evidence_id": "evidence_cracked_badge",
        "owner_id": "char_vask",
        "seen_by_ids": ["char_vask"],
        "reliability": 0.88,
        "legal_validity": 0.75,
        "destroyed": False,
    }
    state.metadata.setdefault("obligation_registry", {})["obl_seren_protect_kael"] = {
        "obligation_id": "obl_seren_protect_kael",
        "promiser_id": "char_seren",
        "promisee_id": "char_kael",
        "status": "active",
    }


def test_leverage_engine_creates_and_registers_leverage():
    state = build_state()
    add_evidence_and_obligation(state)
    engine = LeverageBlackmailEngine()

    leverage = engine.create_leverage_record(
        leverage_id="lev_vask_blackmail_seren",
        leverage_type="secret_exposure",
        holder_id="char_vask",
        target_id="char_seren",
        demand="Stay silent at trial.",
        threat="I will expose the rank edit evidence.",
        linked_secret_ids=["secret_rank_system_edited"],
        linked_evidence_ids=["evidence_cracked_badge"],
        pressure_level=0.8,
        exposure_risk=0.75,
    )

    result = engine.register_leverage_on_state(state=state, leverage_record=leverage)

    assert result["success"] is True
    assert "lev_vask_blackmail_seren" in state.metadata["leverage_registry"]
    assert "lev_vask_blackmail_seren" in state.character_states["char_vask"].metadata["leverage_ids"]
    assert "lev_vask_blackmail_seren" in state.character_states["char_seren"].metadata["leverage_ids"]


def test_leverage_engine_creates_leverage_from_event():
    state = build_state()
    engine = LeverageBlackmailEngine()

    event = SimulationEventPayload(
        event_id="evt_blackmail_attempt",
        event_type=SimulationEventType.BLACKMAIL_ATTEMPT,
        actor_ids=["char_vask"],
        target_ids=["char_seren"],
        witness_ids=[],
        visibility=SimulationEventVisibility.PRIVATE,
        intensity=0.85,
        metadata={
            "linked_secret_ids": ["secret_rank_system_edited"],
            "linked_evidence_ids": ["evidence_cracked_badge"],
            "pressure_level": 0.85,
            "exposure_risk": 0.8,
            "moral_cost": 0.7,
        },
    )

    result = engine.create_leverage_from_event(
        state=state,
        event_payload=event,
        holder_id="char_vask",
        target_id="char_seren",
        demand="Stay silent at trial.",
        threat="I expose the evidence.",
    )

    leverage = result["leverage_record"]

    assert result["success"] is True
    assert leverage["leverage_id"] == "lev_evt_blackmail_attempt_char_vask_char_seren"
    assert leverage["linked_secret_ids"] == ["secret_rank_system_edited"]
    assert leverage["linked_evidence_ids"] == ["evidence_cracked_badge"]
    assert leverage["pressure_level"] == 0.85


def test_leverage_engine_validates_secret_and_evidence_access():
    state = build_state()
    add_evidence_and_obligation(state)
    engine = LeverageBlackmailEngine()

    leverage = engine.create_leverage_record(
        leverage_id="lev_vask_blackmail_seren",
        leverage_type="secret_exposure",
        holder_id="char_vask",
        target_id="char_seren",
        demand="Stay silent.",
        threat="Expose evidence.",
        linked_secret_ids=["secret_rank_system_edited"],
        linked_evidence_ids=["evidence_cracked_badge"],
        linked_obligation_ids=["obl_seren_protect_kael"],
        pressure_level=0.8,
        exposure_risk=0.8,
    )
    engine.register_leverage_on_state(state=state, leverage_record=leverage)

    report = engine.evaluate_leverage_validity(
        state=state,
        leverage_id="lev_vask_blackmail_seren",
    )

    assert report["success"] is True
    assert report["valid"] is True
    assert report["pressure_score"] > 0.5
    assert report["exposure_power"] > 0.4
    assert "holder_knows_secret_rank_system_edited" in report["passed_checks"]
    assert "holder_has_evidence_evidence_cracked_badge" in report["passed_checks"]


def test_leverage_engine_blocks_leverage_when_holder_does_not_know_secret():
    state = build_state()
    add_evidence_and_obligation(state)
    engine = LeverageBlackmailEngine()

    leverage = engine.create_leverage_record(
        leverage_id="lev_kael_invalid",
        leverage_type="secret_exposure",
        holder_id="char_kael",
        target_id="char_seren",
        demand="Stay silent.",
        threat="Expose secret.",
        linked_secret_ids=["secret_rank_system_edited"],
    )
    engine.register_leverage_on_state(state=state, leverage_record=leverage)

    report = engine.evaluate_leverage_validity(state=state, leverage_id="lev_kael_invalid")

    assert report["valid"] is False
    assert any("does not know/suspect" in blocker for blocker in report["blockers"])


def test_leverage_engine_attempts_valid_leverage():
    state = build_state()
    add_evidence_and_obligation(state)
    engine = LeverageBlackmailEngine()

    leverage = engine.create_leverage_record(
        leverage_id="lev_vask_blackmail_seren",
        leverage_type="secret_exposure",
        holder_id="char_vask",
        target_id="char_seren",
        demand="Stay silent.",
        threat="Expose evidence.",
        linked_secret_ids=["secret_rank_system_edited"],
        linked_evidence_ids=["evidence_cracked_badge"],
        pressure_level=0.75,
        exposure_risk=0.8,
        target_resistance=0.25,
    )
    engine.register_leverage_on_state(state=state, leverage_record=leverage)

    result = engine.attempt_leverage(
        state=state,
        leverage_id="lev_vask_blackmail_seren",
        attempt_event_id="evt_blackmail",
        attempt_intensity=0.8,
    )

    assert result["success"] is True
    assert "evt_blackmail" in result["updated_leverage"]["attempt_event_ids"]
    assert result["compliance_probability"] > 0.4


def test_leverage_engine_resolves_refused_outcome():
    state = build_state()
    add_evidence_and_obligation(state)
    engine = LeverageBlackmailEngine()

    leverage = engine.create_leverage_record(
        leverage_id="lev_vask_blackmail_seren",
        leverage_type="secret_exposure",
        holder_id="char_vask",
        target_id="char_seren",
        demand="Stay silent.",
        threat="Expose evidence.",
    )
    engine.register_leverage_on_state(state=state, leverage_record=leverage)

    result = engine.resolve_leverage_outcome(
        state=state,
        leverage_id="lev_vask_blackmail_seren",
        outcome="refused",
        outcome_event_id="evt_refusal",
        notes="Seren refuses to be controlled.",
    )

    updated = result["updated_leverage"]

    assert result["success"] is True
    assert updated["status"] == "refused"
    assert "evt_refusal" in updated["refusal_event_ids"]
    assert updated["exposure_risk"] > leverage["exposure_risk"]


def test_leverage_engine_builds_relationship_delta_for_accepted_blackmail():
    state = build_state()
    add_evidence_and_obligation(state)
    engine = LeverageBlackmailEngine()

    leverage = engine.create_leverage_record(
        leverage_id="lev_vask_blackmail_seren",
        leverage_type="secret_exposure",
        holder_id="char_vask",
        target_id="char_seren",
        demand="Stay silent.",
        threat="Expose evidence.",
        pressure_level=0.8,
        exposure_risk=0.8,
        moral_cost=0.7,
    )
    engine.register_leverage_on_state(state=state, leverage_record=leverage)

    delta = engine.build_relationship_delta_from_leverage(
        state=state,
        leverage_id="lev_vask_blackmail_seren",
        outcome="accepted",
    )

    assert delta.relationship_id == "rel_char_seren_char_vask"
    assert delta.trust_delta < 0
    assert delta.fear_delta > 0
    assert delta.power_imbalance_delta > 0
    assert delta.betrayal_risk_delta > 0


def test_leverage_engine_builds_reputation_delta_for_exposure():
    state = build_state()
    add_evidence_and_obligation(state)
    engine = LeverageBlackmailEngine()

    leverage = engine.create_leverage_record(
        leverage_id="lev_vask_blackmail_seren",
        leverage_type="secret_exposure",
        holder_id="char_vask",
        target_id="char_seren",
        demand="Stay silent.",
        threat="Expose evidence.",
        linked_secret_ids=["secret_rank_system_edited"],
        linked_evidence_ids=["evidence_cracked_badge"],
        pressure_level=0.8,
        exposure_risk=0.8,
    )
    engine.register_leverage_on_state(state=state, leverage_record=leverage)

    delta = engine.build_reputation_delta_from_leverage(
        state=state,
        leverage_id="lev_vask_blackmail_seren",
        affected_character_id="char_seren",
        outcome="exposed",
    )

    assert delta.character_id == "char_seren"
    assert delta.reputation_score_delta < 0
    assert delta.trust_score_delta < 0


def test_leverage_engine_builds_knowledge_delta_from_exposure():
    state = build_state()
    add_evidence_and_obligation(state)
    engine = LeverageBlackmailEngine()

    leverage = engine.create_leverage_record(
        leverage_id="lev_vask_blackmail_seren",
        leverage_type="secret_exposure",
        holder_id="char_vask",
        target_id="char_seren",
        demand="Stay silent.",
        threat="Expose evidence.",
        linked_secret_ids=["secret_rank_system_edited"],
        linked_evidence_ids=["evidence_cracked_badge"],
        exposure_risk=0.8,
    )
    engine.register_leverage_on_state(state=state, leverage_record=leverage)

    delta = engine.build_knowledge_delta_from_leverage_exposure(
        state=state,
        leverage_id="lev_vask_blackmail_seren",
        listener_id="char_kael",
        source_event_id="evt_exposure",
    )

    assert delta.no_magic_knowledge_checked is True
    assert "secret_rank_system_edited" in delta.suspected_secret_ids_added
    assert "evidence_cracked_badge" in delta.evidence_ids_seen
    assert delta.knowledge_path == ["leverage_exposure"]


def test_leverage_engine_builds_delta_batch_for_exposed_outcome():
    state = build_state()
    add_evidence_and_obligation(state)
    engine = LeverageBlackmailEngine()

    leverage = engine.create_leverage_record(
        leverage_id="lev_vask_blackmail_seren",
        leverage_type="secret_exposure",
        holder_id="char_vask",
        target_id="char_seren",
        demand="Stay silent.",
        threat="Expose evidence.",
        linked_secret_ids=["secret_rank_system_edited"],
        linked_evidence_ids=["evidence_cracked_badge"],
    )
    engine.register_leverage_on_state(state=state, leverage_record=leverage)

    batch = engine.build_delta_batch_for_leverage_outcome(
        state=state,
        leverage_id="lev_vask_blackmail_seren",
        outcome="exposed",
        exposed_to_ids=["char_kael", "char_seren"],
    )

    assert batch.source_engine == engine.engine_name
    assert len(batch.relationship_deltas) == 1
    assert len(batch.reputation_deltas) == 1
    assert len(batch.knowledge_deltas) == 2
    assert batch.application_order == [
        batch.relationship_deltas[0].delta_id,
        batch.reputation_deltas[0].delta_id,
        batch.knowledge_deltas[0].delta_id,
        batch.knowledge_deltas[1].delta_id,
    ]


def test_leverage_engine_builds_leverage_map_with_counter_leverage_warning():
    state = build_state()
    add_evidence_and_obligation(state)
    engine = LeverageBlackmailEngine()

    first = engine.create_leverage_record(
        leverage_id="lev_vask_blackmail_seren",
        leverage_type="secret_exposure",
        holder_id="char_vask",
        target_id="char_seren",
        demand="Stay silent.",
        threat="Expose evidence.",
        pressure_level=0.9,
        exposure_risk=0.9,
        linked_secret_ids=["secret_rank_system_edited"],
    )
    counter = engine.create_leverage_record(
        leverage_id="lev_seren_counter_vask",
        leverage_type="counter_leverage",
        holder_id="char_seren",
        target_id="char_vask",
        demand="Back down.",
        threat="Expose your forgery.",
        pressure_level=0.7,
        exposure_risk=0.8,
    )

    engine.register_leverage_on_state(state=state, leverage_record=first)
    engine.register_leverage_on_state(state=state, leverage_record=counter)

    leverage_map = engine.build_leverage_map(state=state)

    record = leverage_map["leverage_records"]["lev_vask_blackmail_seren"]

    assert leverage_map["success"] is True
    assert leverage_map["leverage_count"] == 2
    assert record["has_counter_leverage"] is True
    assert any("counter-leverage" in warning for warning in leverage_map["warnings"])

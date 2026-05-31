from backend.app.engines.simulation.promise_oath_debt_engine import PromiseOathDebtEngine
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
        simulation_id="sim_obligation_001",
        world_state=SimulationWorldState(world_id="world_velmora"),
        character_states={
            "char_kael": SimulationCharacterState(character_id="char_kael"),
            "char_seren": SimulationCharacterState(character_id="char_seren"),
            "char_vask": SimulationCharacterState(character_id="char_vask"),
        },
    )


def test_promise_engine_creates_and_registers_obligation():
    state = build_state()
    engine = PromiseOathDebtEngine()

    obligation = engine.create_obligation_record(
        obligation_id="obl_seren_protect_kael",
        obligation_type="oath",
        promiser_id="char_seren",
        promisee_id="char_kael",
        summary="Seren swears to protect Kael's testimony.",
        terms=["protect testimony", "do not reveal source"],
        witness_ids=["char_vask"],
        emotional_weight=0.8,
        legal_weight=0.6,
        magical_weight=0.5,
        social_weight=0.7,
    )

    result = engine.register_obligation_on_state(state=state, obligation_record=obligation)

    assert result["success"] is True
    assert "obl_seren_protect_kael" in state.metadata["obligation_registry"]
    assert "obl_seren_protect_kael" in state.character_states["char_seren"].metadata["obligation_ids"]
    assert state.metadata["obligation_registry"]["obl_seren_protect_kael"]["pressure_score"] > 0.5


def test_promise_engine_creates_obligation_from_event():
    state = build_state()
    engine = PromiseOathDebtEngine()

    event = SimulationEventPayload(
        event_id="evt_private_oath",
        event_type=SimulationEventType.PROMISE_MADE,
        actor_ids=["char_seren"],
        target_ids=["char_kael"],
        witness_ids=["char_vask"],
        visibility=SimulationEventVisibility.WITNESSED,
        intensity=0.75,
        metadata={
            "emotional_weight": 0.8,
            "legal_weight": 0.4,
            "magical_weight": 0.3,
            "linked_secret_ids": ["secret_rank_system_edited"],
        },
    )

    result = engine.create_obligation_from_event(
        state=state,
        event_payload=event,
        promiser_id="char_seren",
        promisee_id="char_kael",
        obligation_type="romantic_promise",
        summary="Seren promises not to abandon Kael at trial.",
        due_condition="trial testimony",
        breach_condition="abandon trial",
    )

    obligation = result["obligation_record"]

    assert result["success"] is True
    assert obligation["source_event_id"] == "evt_private_oath"
    assert obligation["promiser_id"] == "char_seren"
    assert obligation["promisee_id"] == "char_kael"
    assert obligation["linked_secret_ids"] == ["secret_rank_system_edited"]


def test_promise_engine_fulfills_obligation():
    state = build_state()
    engine = PromiseOathDebtEngine()

    obligation = engine.create_obligation_record(
        obligation_id="obl_seren_protect_kael",
        obligation_type="promise",
        promiser_id="char_seren",
        promisee_id="char_kael",
        summary="Seren promises to protect Kael.",
        emotional_weight=0.7,
    )
    engine.register_obligation_on_state(state=state, obligation_record=obligation)

    result = engine.fulfill_obligation(
        state=state,
        obligation_id="obl_seren_protect_kael",
        fulfillment_event_id="evt_trial_defense",
        fulfillment_strength=0.95,
    )

    updated = result["updated_obligation"]

    assert result["success"] is True
    assert updated["status"] == "fulfilled"
    assert updated["debt_balance"] == 0.0
    assert "evt_trial_defense" in updated["fulfillment_event_ids"]


def test_promise_engine_partially_fulfills_obligation():
    state = build_state()
    engine = PromiseOathDebtEngine()

    obligation = engine.create_obligation_record(
        obligation_id="obl_seren_protect_kael",
        obligation_type="promise",
        promiser_id="char_seren",
        promisee_id="char_kael",
        summary="Seren promises to protect Kael.",
        emotional_weight=0.8,
    )
    engine.register_obligation_on_state(state=state, obligation_record=obligation)

    before = state.metadata["obligation_registry"]["obl_seren_protect_kael"]["debt_balance"]

    result = engine.fulfill_obligation(
        state=state,
        obligation_id="obl_seren_protect_kael",
        fulfillment_event_id="evt_partial_defense",
        fulfillment_strength=0.4,
    )

    updated = result["updated_obligation"]

    assert updated["status"] == "partially_fulfilled"
    assert updated["debt_balance"] < before
    assert updated["debt_balance"] > 0.0


def test_promise_engine_breaks_obligation():
    state = build_state()
    engine = PromiseOathDebtEngine()

    obligation = engine.create_obligation_record(
        obligation_id="obl_seren_protect_kael",
        obligation_type="oath",
        promiser_id="char_seren",
        promisee_id="char_kael",
        summary="Seren swears to protect Kael.",
        emotional_weight=0.8,
        magical_weight=0.6,
    )
    engine.register_obligation_on_state(state=state, obligation_record=obligation)

    result = engine.break_obligation(
        state=state,
        obligation_id="obl_seren_protect_kael",
        breach_event_id="evt_abandon_trial",
        breach_severity=0.9,
        reason="Seren stays silent at court.",
    )

    updated = result["updated_obligation"]

    assert result["success"] is True
    assert updated["status"] == "broken"
    assert "evt_abandon_trial" in updated["breach_event_ids"]
    assert updated["pressure_score"] > obligation["pressure_score"]


def test_promise_engine_forgives_obligation():
    state = build_state()
    engine = PromiseOathDebtEngine()

    obligation = engine.create_obligation_record(
        obligation_id="obl_broken",
        obligation_type="promise",
        promiser_id="char_seren",
        promisee_id="char_kael",
        summary="A broken promise.",
        emotional_weight=0.8,
    )
    engine.register_obligation_on_state(state=state, obligation_record=obligation)
    engine.break_obligation(
        state=state,
        obligation_id="obl_broken",
        breach_event_id="evt_breach",
        breach_severity=0.8,
    )

    result = engine.forgive_obligation(
        state=state,
        obligation_id="obl_broken",
        forgiveness_event_id="evt_forgiveness",
        forgiveness_strength=0.95,
        forgiven_by_id="char_kael",
    )

    updated = result["updated_obligation"]

    assert result["success"] is True
    assert updated["status"] == "forgiven"
    assert updated["debt_balance"] <= 0.15
    assert "evt_forgiveness" in updated["forgiveness_event_ids"]


def test_promise_engine_builds_relationship_delta_for_broken_obligation():
    state = build_state()
    engine = PromiseOathDebtEngine()

    obligation = engine.create_obligation_record(
        obligation_id="obl_seren_protect_kael",
        obligation_type="oath",
        promiser_id="char_seren",
        promisee_id="char_kael",
        summary="Seren swears to protect Kael.",
        emotional_weight=0.8,
        social_weight=0.8,
    )
    engine.register_obligation_on_state(state=state, obligation_record=obligation)

    delta = engine.build_relationship_delta_from_obligation(
        state=state,
        obligation_id="obl_seren_protect_kael",
        event_outcome="broken",
    )

    assert delta.relationship_id == "rel_char_kael_char_seren"
    assert delta.trust_delta < 0
    assert delta.resentment_delta > 0
    assert delta.betrayal_risk_delta > 0


def test_promise_engine_builds_reputation_delta_for_fulfilled_obligation():
    state = build_state()
    engine = PromiseOathDebtEngine()

    obligation = engine.create_obligation_record(
        obligation_id="obl_seren_protect_kael",
        obligation_type="oath",
        promiser_id="char_seren",
        promisee_id="char_kael",
        summary="Seren swears to protect Kael.",
        witness_ids=["char_vask"],
        emotional_weight=0.8,
        social_weight=0.8,
    )
    engine.register_obligation_on_state(state=state, obligation_record=obligation)

    delta = engine.build_reputation_delta_from_obligation(
        state=state,
        obligation_id="obl_seren_protect_kael",
        event_outcome="fulfilled",
    )

    assert delta.character_id == "char_seren"
    assert delta.reputation_score_delta > 0
    assert delta.respect_score_delta > 0
    assert delta.trust_score_delta > 0


def test_promise_engine_builds_delta_batch_for_obligation_outcome():
    state = build_state()
    engine = PromiseOathDebtEngine()

    obligation = engine.create_obligation_record(
        obligation_id="obl_seren_protect_kael",
        obligation_type="oath",
        promiser_id="char_seren",
        promisee_id="char_kael",
        summary="Seren swears to protect Kael.",
    )
    engine.register_obligation_on_state(state=state, obligation_record=obligation)

    batch = engine.build_delta_batch_for_obligation_outcome(
        state=state,
        obligation_id="obl_seren_protect_kael",
        event_outcome="broken",
    )

    assert batch.source_engine == engine.engine_name
    assert len(batch.relationship_deltas) == 1
    assert len(batch.reputation_deltas) == 1
    assert batch.application_order == [
        batch.relationship_deltas[0].delta_id,
        batch.reputation_deltas[0].delta_id,
    ]


def test_promise_engine_builds_obligation_map_and_warnings():
    state = build_state()
    engine = PromiseOathDebtEngine()

    obligation = engine.create_obligation_record(
        obligation_id="obl_high_pressure_private",
        obligation_type="life_debt",
        promiser_id="char_seren",
        promisee_id="char_kael",
        summary="A private life debt.",
        emotional_weight=1.0,
        legal_weight=0.7,
        magical_weight=0.8,
        social_weight=0.7,
    )
    engine.register_obligation_on_state(state=state, obligation_record=obligation)

    obligation_map = engine.build_obligation_map(state=state)

    record = obligation_map["obligation_records"]["obl_high_pressure_private"]

    assert obligation_map["success"] is True
    assert obligation_map["obligation_count"] == 1
    assert record["breach_risk"] > 0.5
    assert any("high pressure" in warning for warning in obligation_map["warnings"])


def test_promise_engine_evaluates_status_with_current_event():
    state = build_state()
    engine = PromiseOathDebtEngine()

    obligation = engine.create_obligation_record(
        obligation_id="obl_trial_testimony",
        obligation_type="promise",
        promiser_id="char_seren",
        promisee_id="char_kael",
        summary="Seren promises testimony.",
        due_condition="trial testimony",
        breach_condition="abandon trial",
    )
    engine.register_obligation_on_state(state=state, obligation_record=obligation)

    event = SimulationEventPayload(
        event_id="evt_trial",
        event_type=SimulationEventType.TRIAL,
        event_name="Trial testimony",
        actor_ids=["char_seren"],
    )

    report = engine.evaluate_obligation_status(
        state=state,
        obligation_id="obl_trial_testimony",
        current_event=event,
    )

    assert report["success"] is True
    assert "current_event_matches_fulfillment" in report["passed_checks"]

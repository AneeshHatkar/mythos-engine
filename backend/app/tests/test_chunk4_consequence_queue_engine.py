from backend.app.engines.simulation.consequence_queue_engine import ConsequenceQueueEngine
from backend.app.schemas.simulation import (
    SimulationCharacterState,
    SimulationRelationshipState,
    SimulationState,
    SimulationWorldState,
)


def build_state():
    return SimulationState(
        simulation_id="sim_consequence_001",
        world_state=SimulationWorldState(world_id="world_velmora"),
        character_states={
            "char_kael": SimulationCharacterState(character_id="char_kael", current_location_id="location_court"),
            "char_seren": SimulationCharacterState(character_id="char_seren", current_location_id="location_archive"),
        },
        relationship_states={
            "rel_char_kael_char_seren": SimulationRelationshipState(
                relationship_id="rel_char_kael_char_seren",
                character_a_id="char_kael",
                character_b_id="char_seren",
                trust=0.4,
                resentment=0.2,
            )
        },
        metadata={"current_tick": 3},
    )


def sample_choice_report():
    return {
        "choice_id": "choice_expose_truth",
        "actor_id": "char_kael",
        "target_id": "char_seren",
        "action_type": "expose_secret",
        "risk_profile": {
            "social_risk": 0.8,
            "moral_cost": 0.2,
            "emotional_cost": 0.7,
            "overall_risk": 0.7,
        },
        "consequence_preview": {
            "relationship_consequence": True,
            "reputation_consequence": True,
            "knowledge_consequence": True,
            "branch_consequence": False,
        },
    }


def test_consequence_queue_creates_and_registers_immediate_consequence():
    state = build_state()
    engine = ConsequenceQueueEngine()

    consequence = engine.create_consequence_record(
        consequence_id="cons_relationship_fallout",
        consequence_type="relationship",
        source_event_id="evt_truth",
        source_choice_id="choice_truth",
        summary="Seren feels betrayed by public exposure.",
        affected_entity_ids=["char_kael", "char_seren"],
        trigger_type="immediate",
        severity=0.7,
    )

    result = engine.register_consequence_on_state(
        state=state,
        consequence_record=consequence,
        current_tick=3,
    )

    registered = state.metadata["consequence_queue"]["cons_relationship_fallout"]

    assert result["success"] is True
    assert registered["status"] == "ready"
    assert registered["created_tick"] == 3
    assert registered["ready_tick"] == 3


def test_consequence_queue_registers_delayed_consequence():
    state = build_state()
    engine = ConsequenceQueueEngine()

    consequence = engine.create_consequence_record(
        consequence_id="cons_reputation_fallout",
        consequence_type="reputation",
        source_event_id="evt_truth",
        source_choice_id="choice_truth",
        summary="Court rumor spreads after the reveal.",
        affected_entity_ids=["char_kael"],
        trigger_type="after_event_count",
        trigger_condition={"event_count": 2},
        delay_ticks=2,
        severity=0.6,
    )

    engine.register_consequence_on_state(
        state=state,
        consequence_record=consequence,
        current_tick=3,
    )

    registered = state.metadata["consequence_queue"]["cons_reputation_fallout"]

    assert registered["status"] == "queued"
    assert registered["ready_tick"] == 5


def test_consequence_queue_queues_from_choice_report():
    state = build_state()
    engine = ConsequenceQueueEngine()

    result = engine.queue_consequences_from_choice_report(
        state=state,
        choice_report=sample_choice_report(),
        current_tick=3,
    )

    assert result["success"] is True
    assert result["consequence_count"] == 3
    assert "cons_choice_expose_truth_relationship" in result["registered_consequence_ids"]
    assert "cons_choice_expose_truth_reputation" in result["registered_consequence_ids"]
    assert "cons_choice_expose_truth_knowledge" in result["registered_consequence_ids"]


def test_consequence_queue_advances_ready_after_delay():
    state = build_state()
    engine = ConsequenceQueueEngine()

    consequence = engine.create_consequence_record(
        consequence_id="cons_reputation_fallout",
        consequence_type="reputation",
        source_event_id="evt_truth",
        source_choice_id="choice_truth",
        summary="Court rumor spreads.",
        trigger_type="after_event_count",
        trigger_condition={"event_count": 1},
        delay_ticks=1,
        severity=0.6,
    )
    engine.register_consequence_on_state(state=state, consequence_record=consequence, current_tick=3)

    result = engine.advance_consequence_queue(
        state=state,
        current_tick=4,
        event_context={"event_count_since_source": 1},
    )

    assert result["success"] is True
    assert "cons_reputation_fallout" in result["ready_consequence_ids"]
    assert state.metadata["consequence_queue"]["cons_reputation_fallout"]["status"] == "ready"


def test_consequence_queue_triggers_secret_exposed_condition():
    state = build_state()
    state.metadata["secret_registry"] = {
        "secret_rank_system_edited": {"exposed": True}
    }
    engine = ConsequenceQueueEngine()

    consequence = engine.create_consequence_record(
        consequence_id="cons_secret_fallout",
        consequence_type="knowledge",
        source_event_id="evt_secret",
        source_choice_id="choice_truth",
        summary="Secret exposure triggers knowledge fallout.",
        trigger_type="when_secret_exposed",
        trigger_condition={"secret_id": "secret_rank_system_edited"},
        delay_ticks=0,
        severity=0.8,
    )
    engine.register_consequence_on_state(state=state, consequence_record=consequence, current_tick=3)

    result = engine.advance_consequence_queue(state=state, current_tick=3)

    assert "cons_secret_fallout" in result["ready_consequence_ids"]


def test_consequence_queue_triggers_relationship_threshold_condition():
    state = build_state()
    engine = ConsequenceQueueEngine()

    consequence = engine.create_consequence_record(
        consequence_id="cons_relationship_low_trust",
        consequence_type="relationship",
        source_event_id="evt_betrayal",
        source_choice_id="choice_betray",
        summary="Low trust creates rupture scene.",
        trigger_type="when_relationship_threshold_crossed",
        trigger_condition={
            "relationship_id": "rel_char_kael_char_seren",
            "metric": "trust",
            "threshold": 0.5,
            "direction": "lte",
        },
        severity=0.7,
    )
    engine.register_consequence_on_state(state=state, consequence_record=consequence, current_tick=3)

    result = engine.advance_consequence_queue(state=state, current_tick=3)

    assert "cons_relationship_low_trust" in result["ready_consequence_ids"]


def test_consequence_queue_mark_triggered_and_resolve_with_followup():
    state = build_state()
    engine = ConsequenceQueueEngine()

    consequence = engine.create_consequence_record(
        consequence_id="cons_relationship_fallout",
        consequence_type="relationship",
        source_event_id="evt_truth",
        source_choice_id="choice_truth",
        summary="Relationship fallout.",
        trigger_type="immediate",
        severity=0.7,
    )
    engine.register_consequence_on_state(state=state, consequence_record=consequence, current_tick=3)

    triggered = engine.mark_consequence_triggered(
        state=state,
        consequence_id="cons_relationship_fallout",
        triggered_tick=4,
    )

    followup = engine.create_consequence_record(
        consequence_id="cons_repair_hook",
        consequence_type="plot_hook",
        source_event_id=None,
        source_choice_id="choice_truth",
        summary="Future repair scene needed.",
        trigger_type="manual",
        severity=0.5,
    )

    resolved = engine.resolve_consequence(
        state=state,
        consequence_id="cons_relationship_fallout",
        resolution_summary="Seren leaves the court.",
        resolved_tick=5,
        created_followup_consequences=[followup],
    )

    assert triggered["updated_consequence"]["status"] == "resolved" or state.metadata["consequence_queue"]["cons_relationship_fallout"]["status"] == "resolved"
    assert resolved["success"] is True
    assert "cons_repair_hook" in resolved["followup_consequence_ids"]
    assert state.metadata["consequence_queue"]["cons_relationship_fallout"]["resolved_tick"] == 5


def test_consequence_queue_cancels_consequence():
    state = build_state()
    engine = ConsequenceQueueEngine()

    consequence = engine.create_consequence_record(
        consequence_id="cons_cancel_me",
        consequence_type="plot_hook",
        source_event_id=None,
        source_choice_id=None,
        summary="Cancel this hook.",
    )
    engine.register_consequence_on_state(state=state, consequence_record=consequence)

    result = engine.cancel_consequence(
        state=state,
        consequence_id="cons_cancel_me",
        reason="Branch changed.",
    )

    assert result["success"] is True
    assert result["updated_consequence"]["status"] == "cancelled"
    assert result["updated_consequence"]["metadata"]["cancel_reason"] == "Branch changed."


def test_consequence_queue_builds_map_and_ready_list():
    state = build_state()
    engine = ConsequenceQueueEngine()

    ready = engine.create_consequence_record(
        consequence_id="cons_ready",
        consequence_type="relationship",
        source_event_id=None,
        source_choice_id=None,
        summary="Ready consequence.",
        trigger_type="immediate",
        severity=0.4,
    )
    queued = engine.create_consequence_record(
        consequence_id="cons_queued",
        consequence_type="reputation",
        source_event_id=None,
        source_choice_id=None,
        summary="Queued consequence.",
        trigger_type="manual",
        severity=0.9,
    )
    engine.register_consequence_on_state(state=state, consequence_record=ready)
    engine.register_consequence_on_state(state=state, consequence_record=queued)

    consequence_map = engine.build_consequence_map(state=state)
    ready_result = engine.get_ready_consequences(state=state)

    assert consequence_map["success"] is True
    assert consequence_map["consequence_count"] == 2
    assert consequence_map["summary"]["ready_count"] == 1
    assert ready_result["ready_count"] == 1
    assert "cons_ready" in ready_result["ready_consequences"]

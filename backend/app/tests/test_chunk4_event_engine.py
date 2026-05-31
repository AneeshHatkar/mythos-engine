from backend.app.engines.simulation.event_engine import EventEngine
from backend.app.schemas.simulation import (
    SimulationCharacterState,
    SimulationState,
    SimulationWorldState,
)


def build_state():
    return SimulationState(
        simulation_id="sim_event_001",
        world_state=SimulationWorldState(world_id="world_velmora"),
        character_states={
            "char_kael": SimulationCharacterState(character_id="char_kael", current_location_id="location_court"),
            "char_seren": SimulationCharacterState(character_id="char_seren", current_location_id="location_court"),
            "char_vask": SimulationCharacterState(character_id="char_vask", current_location_id="location_court"),
        },
        metadata={
            "secret_registry": {
                "secret_rank_system_edited": {"secret_id": "secret_rank_system_edited"}
            },
            "evidence_registry": {
                "evidence_cracked_badge": {"evidence_id": "evidence_cracked_badge"}
            },
            "obligation_registry": {
                "obl_trial_testimony": {"obligation_id": "obl_trial_testimony"}
            },
        },
    )


def test_event_engine_creates_event_record():
    engine = EventEngine()

    event = engine.create_event_record(
        event_id="evt_truth_reveal",
        event_type="evidence_reveal",
        event_name="Kael reveals the cracked badge.",
        actor_ids=["char_kael"],
        target_ids=["char_seren"],
        witness_ids=["char_vask"],
        location_id="location_court",
        visibility="public",
        intensity=0.85,
        linked_secret_ids=["secret_rank_system_edited"],
        linked_evidence_ids=["evidence_cracked_badge"],
    )

    assert event["event_id"] == "evt_truth_reveal"
    assert event["event_family"] == "knowledge"
    assert event["severity_label"] == "critical"
    assert event["visibility"] == "public"


def test_event_engine_classifies_known_and_unknown_event_types():
    engine = EventEngine()

    known = engine.classify_event_type("blackmail_attempt")
    unknown = engine.classify_event_type("mysterious_secret_trial_event")

    assert known["known_event_type"] is True
    assert known["event_family"] == "leverage"
    assert unknown["known_event_type"] is False
    assert unknown["event_family"] in {"knowledge", "world"}


def test_event_engine_validates_event_record():
    state = build_state()
    engine = EventEngine()

    event = engine.create_event_record(
        event_id="evt_truth_reveal",
        event_type="evidence_reveal",
        event_name="Kael reveals the cracked badge.",
        actor_ids=["char_kael"],
        target_ids=["char_seren"],
        witness_ids=["char_vask"],
        location_id="location_court",
        visibility="public",
        intensity=0.85,
        linked_secret_ids=["secret_rank_system_edited"],
        linked_evidence_ids=["evidence_cracked_badge"],
    )

    report = engine.validate_event_record(state=state, event_record=event)

    assert report["success"] is True
    assert report["valid"] is True
    assert "actor_char_kael_exists" in report["passed_checks"]
    assert "target_char_seren_exists" in report["passed_checks"]
    assert "secret_secret_rank_system_edited_linked" in report["passed_checks"]
    assert "evidence_evidence_cracked_badge_linked" in report["passed_checks"]


def test_event_engine_blocks_missing_actor():
    state = build_state()
    engine = EventEngine()

    event = engine.create_event_record(
        event_id="evt_invalid",
        event_type="trial",
        event_name="Invalid trial event.",
        actor_ids=["char_missing"],
        location_id="location_court",
        visibility="public",
    )

    report = engine.validate_event_record(state=state, event_record=event)

    assert report["valid"] is False
    assert any("actor char_missing missing" in blocker for blocker in report["blockers"])


def test_event_engine_registers_event_on_state():
    state = build_state()
    engine = EventEngine()

    event = engine.create_event_record(
        event_id="evt_trial",
        event_type="trial",
        event_name="The academy court trial begins.",
        actor_ids=["char_kael"],
        target_ids=["char_seren"],
        witness_ids=["char_vask"],
        location_id="location_court",
        visibility="public",
        intensity=0.75,
    )

    result = engine.register_event_on_state(state=state, event_record=event)

    assert result["success"] is True
    assert "evt_trial" in state.metadata["event_registry"]
    assert state.metadata["last_event_id"] == "evt_trial"
    assert state.metadata["event_count"] == 1


def test_event_engine_routes_event_to_engines():
    engine = EventEngine()

    event = engine.create_event_record(
        event_id="evt_blackmail",
        event_type="blackmail_attempt",
        event_name="Vask blackmails Seren.",
        actor_ids=["char_vask"],
        target_ids=["char_seren"],
        linked_secret_ids=["secret_rank_system_edited"],
        linked_evidence_ids=["evidence_cracked_badge"],
        linked_leverage_ids=["lev_vask_seren"],
    )

    routing = engine.route_event_to_engines(event_record=event)

    assert routing["success"] is True
    assert "leverage_blackmail_engine" in routing["routes"]
    assert "knowledge_secret_state_engine" in routing["routes"]
    assert "evidence_engine" in routing["routes"]
    assert "causal_chain_explanation_engine" in routing["routes"]


def test_event_engine_builds_processing_plan():
    state = build_state()
    engine = EventEngine()

    event = engine.create_event_record(
        event_id="evt_promise",
        event_type="promise_made",
        event_name="Seren promises to protect Kael.",
        actor_ids=["char_seren"],
        target_ids=["char_kael"],
        witness_ids=["char_vask"],
        location_id="location_court",
        visibility="witnessed",
        intensity=0.65,
        linked_obligation_ids=["obl_trial_testimony"],
    )

    plan = engine.build_event_processing_plan(state=state, event_record=event)

    assert plan["success"] is True
    assert plan["valid"] is True
    assert "register_event" in plan["plan_steps"]
    assert "run_promise_oath_debt_engine" in plan["plan_steps"]
    assert "update_causal_graph" in plan["plan_steps"]
    assert plan["estimated_impact_score"] > 0.3
    assert plan["chunk5_handoff"]["scene_type"] == "promise_oath_debt_scene"


def test_event_engine_builds_event_card():
    engine = EventEngine()

    event = engine.create_event_record(
        event_id="evt_confession",
        event_type="private_confession",
        event_name="Seren confesses the truth.",
        actor_ids=["char_seren"],
        target_ids=["char_kael"],
        visibility="private",
        intensity=0.7,
        linked_secret_ids=["secret_rank_system_edited"],
    )

    card = engine.build_event_card(event_record=event)

    assert card["event_id"] == "evt_confession"
    assert card["event_family"] == "relationship"
    assert card["story_function"] == "vulnerability_turning_point"
    assert card["linked_record_counts"]["secrets"] == 1


def test_event_engine_builds_event_map():
    state = build_state()
    engine = EventEngine()

    event_one = engine.create_event_record(
        event_id="evt_trial",
        event_type="trial",
        event_name="Trial begins.",
        actor_ids=["char_kael"],
        location_id="location_court",
        visibility="public",
    )
    event_two = engine.create_event_record(
        event_id="evt_confession",
        event_type="private_confession",
        event_name="Confession.",
        actor_ids=["char_seren"],
        target_ids=["char_kael"],
        location_id="location_court",
        visibility="private",
    )

    engine.register_event_on_state(state=state, event_record=event_one)
    engine.register_event_on_state(state=state, event_record=event_two)

    event_map = engine.build_event_map(state=state)

    assert event_map["success"] is True
    assert event_map["event_count"] == 2
    assert event_map["family_counts"]["world"] == 1
    assert event_map["family_counts"]["relationship"] == 1
    assert event_map["last_event_id"] == "evt_confession"


def test_event_engine_builds_chunk5_handoff():
    engine = EventEngine()

    event = engine.create_event_record(
        event_id="evt_betrayal",
        event_type="betrayal",
        event_name="Kael betrays Seren publicly.",
        actor_ids=["char_kael"],
        target_ids=["char_seren"],
        visibility="public",
        intensity=0.9,
        linked_secret_ids=["secret_rank_system_edited"],
        source_choice_id="choice_truth",
    )

    handoff = engine.build_event_chunk5_handoff(event_record=event)

    assert handoff["scene_type"] == "betrayal_scene"
    assert handoff["priority"] == "high"
    assert handoff["must_show_information_path"] is True
    assert handoff["must_show_consequence_seed"] is True
    assert "choice_consequence" in handoff["plot_tags"]

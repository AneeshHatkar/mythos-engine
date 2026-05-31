from backend.app.engines.simulation.stakes_engine import StakesEngine
from backend.app.schemas.simulation import SimulationCharacterState, SimulationState, SimulationWorldState


def build_state():
    return SimulationState(
        simulation_id="sim_stakes_001",
        world_state=SimulationWorldState(world_id="world_velmora"),
        character_states={
            "char_kael": SimulationCharacterState(character_id="char_kael"),
            "char_seren": SimulationCharacterState(character_id="char_seren"),
        },
    )


def test_stakes_engine_creates_and_registers_stakes_record():
    state = build_state()
    engine = StakesEngine()

    record = engine.create_stakes_record(
        stakes_id="stakes_truth",
        source_type="choice",
        source_id="choice_truth",
        affected_entity_ids=["char_kael", "char_seren"],
        stake_values={
            "truth": 0.8,
            "relationship": 0.7,
            "reputation": 0.6,
        },
        summary="Truth reveal risks love and reputation.",
    )

    result = engine.register_stakes_on_state(state=state, stakes_record=record)

    assert result["success"] is True
    assert "stakes_truth" in state.metadata["stakes_registry"]
    assert record["overall_stakes_score"] > 0.6
    assert record["dominant_stake_type"] == "truth"
    assert record["stakes_label"] in {"high", "catastrophic"}


def test_stakes_engine_evaluates_event_stakes():
    state = build_state()
    engine = StakesEngine()

    event = {
        "event_id": "evt_trial_reveal",
        "event_type": "trial",
        "event_family": "world",
        "actor_ids": ["char_kael"],
        "target_ids": ["char_seren"],
        "witness_ids": [],
        "involved_faction_ids": ["faction_oath_court"],
        "visibility": "public",
        "intensity": 0.85,
        "linked_secret_ids": ["secret_rank_system_edited"],
        "linked_evidence_ids": ["evidence_cracked_badge"],
    }

    result = engine.evaluate_event_stakes(state=state, event_record=event)
    record = result["stakes_record"]

    assert result["success"] is True
    assert record["source_type"] == "event"
    assert record["stake_values"]["truth"] > 0.7
    assert record["stake_values"]["reputation"] > 0.6
    assert record["overall_stakes_score"] > 0.6
    assert result["chunk5_handoff"]["must_show_aftermath"] is True


def test_stakes_engine_evaluates_choice_stakes():
    state = build_state()
    engine = StakesEngine()

    choice_report = {
        "choice_id": "choice_expose_truth",
        "actor_id": "char_kael",
        "target_id": "char_seren",
        "action_type": "expose_secret",
        "risk_profile": {
            "social_risk": 0.8,
            "moral_cost": 0.2,
            "emotional_cost": 0.7,
            "coercion_pressure": 0.1,
            "overall_risk": 0.7,
        },
        "consequence_preview": {
            "relationship_consequence": True,
            "reputation_consequence": True,
            "knowledge_consequence": True,
            "branch_consequence": True,
        },
    }

    result = engine.evaluate_choice_stakes(state=state, choice_report=choice_report)
    record = result["stakes_record"]

    assert result["success"] is True
    assert record["source_type"] == "choice"
    assert record["stake_values"]["truth"] >= 0.6
    assert record["stake_values"]["relationship"] >= 0.55
    assert record["stake_values"]["branch"] >= 0.65
    assert record["overall_stakes_score"] > 0.6


def test_stakes_engine_evaluates_consequence_stakes():
    state = build_state()
    engine = StakesEngine()

    consequence = {
        "consequence_id": "cons_relationship",
        "consequence_type": "relationship",
        "severity": 0.8,
        "affected_entity_ids": ["char_kael", "char_seren"],
    }

    result = engine.evaluate_consequence_stakes(state=state, consequence_record=consequence)
    record = result["stakes_record"]

    assert result["success"] is True
    assert record["source_type"] == "consequence"
    assert record["stake_values"]["relationship"] > 0.7
    assert record["dominant_stake_type"] == "relationship"


def test_stakes_engine_combines_scene_stakes():
    state = build_state()
    engine = StakesEngine()

    event = {
        "event_id": "evt_trial",
        "event_type": "trial",
        "event_family": "world",
        "actor_ids": ["char_kael"],
        "target_ids": ["char_seren"],
        "witness_ids": [],
        "visibility": "public",
        "intensity": 0.7,
        "linked_secret_ids": ["secret_rank_system_edited"],
    }

    choice = {
        "choice_id": "choice_truth",
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
            "knowledge_consequence": True,
        },
    }

    result = engine.evaluate_scene_stakes(
        state=state,
        scene_id="scene_trial_truth",
        event_records=[event],
        choice_reports=[choice],
    )

    record = result["stakes_record"]

    assert result["success"] is True
    assert result["child_stakes_count"] == 2
    assert record["source_type"] == "scene"
    assert record["overall_stakes_score"] > 0.6
    assert "char_kael" in record["affected_entity_ids"]


def test_stakes_engine_compares_stakes_records():
    engine = StakesEngine()

    low = engine.create_stakes_record(
        stakes_id="low",
        source_type="event",
        source_id="evt_low",
        stake_values={"emotional": 0.2},
    )
    high = engine.create_stakes_record(
        stakes_id="high",
        source_type="event",
        source_id="evt_high",
        stake_values={"truth": 0.9, "relationship": 0.8},
    )

    result = engine.compare_stakes(records=[low, high])

    assert result["success"] is True
    assert result["ranked_stakes"][0]["stakes_id"] == "high"
    assert result["highest_stakes_record"]["stakes_id"] == "high"
    assert result["average_stakes_score"] > 0


def test_stakes_engine_builds_stakes_map():
    state = build_state()
    engine = StakesEngine()

    record = engine.create_stakes_record(
        stakes_id="stakes_truth",
        source_type="choice",
        source_id="choice_truth",
        stake_values={"truth": 0.8, "relationship": 0.7},
    )
    engine.register_stakes_on_state(state=state, stakes_record=record)

    result = engine.build_stakes_map(state=state)

    assert result["success"] is True
    assert result["stakes_count"] == 1
    assert result["highest_stakes_record"]["stakes_id"] == "stakes_truth"
    assert "average_stakes_score" in result

from backend.app.engines.simulation.tension_curve_engine import TensionCurveEngine
from backend.app.schemas.simulation import SimulationState, SimulationWorldState


def build_state():
    return SimulationState(
        simulation_id="sim_tension_001",
        world_state=SimulationWorldState(world_id="world_velmora"),
    )


def test_tension_engine_creates_tension_point():
    engine = TensionCurveEngine()

    point = engine.create_tension_point(
        point_id="point_1",
        source_type="event",
        source_id="evt_trial",
        sequence_index=0,
        tension_value=0.7,
        emotional_pressure=0.6,
        stakes_pressure=0.8,
        social_pressure=0.5,
        knowledge_pressure=0.7,
        consequence_pressure=0.6,
        release_value=0.1,
    )

    assert point["point_id"] == "point_1"
    assert point["source_type"] == "event"
    assert point["net_pressure"] > 0.5
    assert point["sequence_index"] == 0


def test_tension_engine_builds_point_from_stakes():
    engine = TensionCurveEngine()

    stakes = {
        "stakes_id": "stakes_truth",
        "overall_stakes_score": 0.75,
        "dominant_stake_type": "truth",
        "stakes_label": "high",
        "stake_values": {
            "truth": 0.8,
            "relationship": 0.7,
            "reputation": 0.6,
            "emotional": 0.7,
            "branch": 0.65,
        },
        "summary": "Truth reveal stakes.",
    }

    point = engine.build_tension_point_from_stakes(
        stakes_record=stakes,
        sequence_index=2,
    )

    assert point["source_type"] == "stakes"
    assert point["source_id"] == "stakes_truth"
    assert point["knowledge_pressure"] == 0.8
    assert point["net_pressure"] > 0.6


def test_tension_engine_builds_point_from_event():
    engine = TensionCurveEngine()

    event = {
        "event_id": "evt_trial_reveal",
        "event_type": "trial",
        "event_family": "world",
        "event_name": "The truth is revealed in court.",
        "visibility": "public",
        "intensity": 0.85,
        "linked_secret_ids": ["secret_rank_system_edited"],
        "linked_evidence_ids": ["evidence_cracked_badge"],
        "metadata": {},
    }

    point = engine.build_tension_point_from_event(
        event_record=event,
        sequence_index=1,
    )

    assert point["source_type"] == "event"
    assert point["source_id"] == "evt_trial_reveal"
    assert point["knowledge_pressure"] > 0.7
    assert point["social_pressure"] > 0


def test_tension_engine_builds_point_from_choice():
    engine = TensionCurveEngine()

    choice = {
        "choice_id": "choice_truth",
        "action_type": "expose_secret",
        "summary": "Expose the truth.",
        "agency_score": 0.6,
        "feasibility_score": 0.7,
        "risk_profile": {
            "overall_risk": 0.75,
            "coercion_pressure": 0.2,
            "moral_cost": 0.3,
            "emotional_cost": 0.8,
            "social_risk": 0.8,
        },
        "consequence_preview": {
            "branch_consequence": True,
        },
    }

    point = engine.build_tension_point_from_choice(
        choice_report=choice,
        sequence_index=2,
    )

    assert point["source_type"] == "choice"
    assert point["source_id"] == "choice_truth"
    assert point["knowledge_pressure"] == 0.55
    assert point["consequence_pressure"] == 0.65


def test_tension_engine_builds_tension_curve():
    engine = TensionCurveEngine()

    points = [
        engine.create_tension_point(
            point_id="p1",
            source_type="event",
            source_id="evt_1",
            sequence_index=0,
            tension_value=0.25,
        ),
        engine.create_tension_point(
            point_id="p2",
            source_type="event",
            source_id="evt_2",
            sequence_index=1,
            tension_value=0.55,
        ),
        engine.create_tension_point(
            point_id="p3",
            source_type="event",
            source_id="evt_3",
            sequence_index=2,
            tension_value=0.85,
        ),
    ]

    result = engine.build_tension_curve(
        curve_id="curve_trial",
        points=points,
        source_type="scene",
        source_id="scene_trial",
    )

    curve = result["tension_curve"]

    assert result["success"] is True
    assert curve["curve_id"] == "curve_trial"
    assert curve["point_count"] == 3
    assert curve["peak_tension"] > curve["lowest_tension"]
    assert curve["curve_label"] in engine.CURVE_LABELS
    assert "chunk5_handoff" in curve


def test_tension_engine_detects_flat_curve_warning():
    engine = TensionCurveEngine()

    points = [
        engine.create_tension_point(point_id="p1", source_type="event", source_id="a", sequence_index=0, tension_value=0.4),
        engine.create_tension_point(point_id="p2", source_type="event", source_id="b", sequence_index=1, tension_value=0.41),
        engine.create_tension_point(point_id="p3", source_type="event", source_id="c", sequence_index=2, tension_value=0.39),
    ]

    curve = engine.build_tension_curve(
        curve_id="curve_flat",
        points=points,
    )["tension_curve"]

    assert curve["curve_label"] == "flat"
    assert any("flat" in warning for warning in curve["warnings"])
    assert curve["chunk5_handoff"]["needs_escalation"] is True


def test_tension_engine_evaluates_scene_tension():
    engine = TensionCurveEngine()

    event = {
        "event_id": "evt_trial",
        "event_type": "trial",
        "event_family": "world",
        "event_name": "Trial begins.",
        "visibility": "public",
        "intensity": 0.7,
        "metadata": {},
    }

    choice = {
        "choice_id": "choice_truth",
        "action_type": "expose_secret",
        "summary": "Expose truth.",
        "agency_score": 0.6,
        "feasibility_score": 0.7,
        "risk_profile": {
            "overall_risk": 0.7,
            "emotional_cost": 0.7,
            "social_risk": 0.8,
            "moral_cost": 0.3,
        },
        "consequence_preview": {"branch_consequence": True},
    }

    consequence = {
        "consequence_id": "cons_reputation",
        "consequence_type": "reputation",
        "severity": 0.65,
        "status": "queued",
        "summary": "Court reacts.",
    }

    result = engine.evaluate_scene_tension(
        scene_id="scene_trial",
        event_records=[event],
        choice_reports=[choice],
        consequence_records=[consequence],
    )

    curve = result["tension_curve"]

    assert result["success"] is True
    assert curve["source_type"] == "scene"
    assert curve["source_id"] == "scene_trial"
    assert curve["point_count"] == 3
    assert curve["average_tension"] > 0


def test_tension_engine_registers_and_builds_map():
    state = build_state()
    engine = TensionCurveEngine()

    points = [
        engine.create_tension_point(point_id="p1", source_type="event", source_id="evt_1", sequence_index=0, tension_value=0.3),
        engine.create_tension_point(point_id="p2", source_type="event", source_id="evt_2", sequence_index=1, tension_value=0.7),
    ]

    curve = engine.build_tension_curve(
        curve_id="curve_scene",
        points=points,
        source_type="scene",
        source_id="scene_1",
    )["tension_curve"]

    registered = engine.register_tension_curve_on_state(state=state, curve=curve)
    tension_map = engine.build_tension_map(state=state)

    assert registered["success"] is True
    assert "curve_scene" in state.metadata["tension_curves"]
    assert tension_map["success"] is True
    assert tension_map["curve_count"] == 1
    assert "curve_scene" in tension_map["tension_curve_records"]


def test_tension_engine_compares_curves():
    engine = TensionCurveEngine()

    curve_a = engine.build_tension_curve(
        curve_id="curve_a",
        points=[
            engine.create_tension_point(point_id="a1", source_type="event", source_id="a1", sequence_index=0, tension_value=0.2),
            engine.create_tension_point(point_id="a2", source_type="event", source_id="a2", sequence_index=1, tension_value=0.8),
        ],
    )["tension_curve"]

    curve_b = engine.build_tension_curve(
        curve_id="curve_b",
        points=[
            engine.create_tension_point(point_id="b1", source_type="event", source_id="b1", sequence_index=0, tension_value=0.3),
            engine.create_tension_point(point_id="b2", source_type="event", source_id="b2", sequence_index=1, tension_value=0.4),
        ],
    )["tension_curve"]

    result = engine.compare_tension_curves(curves=[curve_a, curve_b])

    assert result["success"] is True
    assert result["curve_count"] == 2
    assert result["highest_peak_curve"]["curve_id"] in {"curve_a", "curve_b"}
    assert "average_pacing_score" in result

from backend.app.engines.simulation.conflict_resolution_engine import ConflictResolutionEngine
from backend.app.schemas.simulation import (
    SimulationCharacterState,
    SimulationRelationshipState,
    SimulationState,
    SimulationWorldState,
)


def build_state():
    return SimulationState(
        simulation_id="sim_conflict_001",
        world_state=SimulationWorldState(world_id="world_velmora"),
        character_states={
            "char_kael": SimulationCharacterState(
                character_id="char_kael",
                metadata={"reputation_state": {"public": 0.45}},
            ),
            "char_seren": SimulationCharacterState(
                character_id="char_seren",
                metadata={"reputation_state": {"public": 0.35}},
            ),
            "char_vask": SimulationCharacterState(
                character_id="char_vask",
                metadata={"reputation_state": {"public": 0.30}},
            ),
        },
        relationship_states={
            "rel_kael_seren": SimulationRelationshipState(
                relationship_id="rel_kael_seren",
                character_a_id="char_kael",
                character_b_id="char_seren",
                trust=0.45,
                resentment=0.35,
                rivalry=0.25,
                betrayal_risk=0.30,
                fear=0.10,
            )
        },
        metadata={
            "leverage_registry": {
                "lev_vask_seren": {
                    "holder_id": "char_vask",
                    "target_id": "char_seren",
                    "status": "active",
                    "pressure_level": 0.8,
                }
            },
            "obligation_registry": {
                "obl_seren_kael": {
                    "promiser_id": "char_seren",
                    "promisee_id": "char_kael",
                    "status": "active",
                    "pressure_score": 0.7,
                }
            },
        },
    )


def make_conflict(engine):
    return engine.create_conflict_record(
        conflict_id="conflict_truth_vs_protection",
        conflict_type="truth",
        title="Truth vs Protection",
        participant_ids=["char_kael", "char_seren"],
        source_event_id="evt_trial",
        source_choice_id="choice_truth",
        core_issue="Kael wants truth revealed; Seren wants the source protected.",
        opposing_goals={
            "char_kael": "reveal the edited ranking system",
            "char_seren": "protect family and source",
        },
        linked_secret_ids=["secret_rank_system_edited"],
        linked_evidence_ids=["evidence_cracked_badge"],
        linked_obligation_ids=["obl_seren_kael"],
        intensity=0.75,
        stakes_score=0.8,
        tension_score=0.78,
        moral_complexity=0.85,
    )


def test_conflict_engine_creates_and_registers_conflict():
    state = build_state()
    engine = ConflictResolutionEngine()

    conflict = make_conflict(engine)
    result = engine.register_conflict_on_state(state=state, conflict_record=conflict)

    assert result["success"] is True
    assert "conflict_truth_vs_protection" in state.metadata["conflict_registry"]
    assert conflict["conflict_pressure"] > 0.7
    assert "conflict_truth_vs_protection" in state.character_states["char_kael"].metadata["conflict_ids"]


def test_conflict_engine_evaluates_conflict():
    state = build_state()
    engine = ConflictResolutionEngine()

    conflict = make_conflict(engine)
    engine.register_conflict_on_state(state=state, conflict_record=conflict)

    report = engine.evaluate_conflict(
        state=state,
        conflict_id="conflict_truth_vs_protection",
    )

    assert report["success"] is True
    assert report["conflict_id"] == "conflict_truth_vs_protection"
    assert report["escalation_risk"] > 0.3
    assert report["compromise_potential"] >= 0
    assert len(report["participant_reports"]) == 2
    assert report["recommended_next_state"] in {"escalate", "resolve", "compromise", "leave_unresolved"}


def test_conflict_engine_escalates_conflict():
    state = build_state()
    engine = ConflictResolutionEngine()

    conflict = make_conflict(engine)
    engine.register_conflict_on_state(state=state, conflict_record=conflict)

    before = state.metadata["conflict_registry"]["conflict_truth_vs_protection"]["conflict_pressure"]

    result = engine.escalate_conflict(
        state=state,
        conflict_id="conflict_truth_vs_protection",
        escalation_event_id="evt_blackmail",
        escalation_reason="Vask threatens exposure.",
        escalation_amount=0.12,
    )

    updated = result["updated_conflict"]

    assert result["success"] is True
    assert updated["status"] == "escalated"
    assert updated["conflict_pressure"] >= before
    assert updated["escalation_history"]


def test_conflict_engine_deescalates_conflict():
    state = build_state()
    engine = ConflictResolutionEngine()

    conflict = make_conflict(engine)
    engine.register_conflict_on_state(state=state, conflict_record=conflict)

    before = state.metadata["conflict_registry"]["conflict_truth_vs_protection"]["conflict_pressure"]

    result = engine.deescalate_conflict(
        state=state,
        conflict_id="conflict_truth_vs_protection",
        deescalation_event_id="evt_confession",
        deescalation_reason="Seren privately admits the truth.",
        deescalation_amount=0.18,
    )

    updated = result["updated_conflict"]

    assert result["success"] is True
    assert updated["status"] == "deescalated"
    assert updated["conflict_pressure"] < before
    assert updated["deescalation_history"]


def test_conflict_engine_resolves_conflict_with_compromise():
    state = build_state()
    engine = ConflictResolutionEngine()

    conflict = make_conflict(engine)
    engine.register_conflict_on_state(state=state, conflict_record=conflict)

    result = engine.resolve_conflict(
        state=state,
        conflict_id="conflict_truth_vs_protection",
        outcome_type="compromise",
        resolution_event_id="evt_compromise",
        winner_ids=[],
        loser_ids=[],
        compromise_terms=["reveal the evidence without naming the source"],
        unresolved_threads=["Seren still fears family retaliation"],
        resolution_summary="They agree to reveal proof carefully.",
    )

    updated = result["updated_conflict"]

    assert result["success"] is True
    assert updated["status"] == "compromised"
    assert updated["resolution_history"][0]["outcome_type"] == "compromise"
    assert "Seren still fears family retaliation" in updated["unresolved_threads"]
    assert result["chunk5_handoff"]["must_leave_thread"] is False


def test_conflict_engine_resolves_conflict_as_open_wound():
    state = build_state()
    engine = ConflictResolutionEngine()

    conflict = make_conflict(engine)
    engine.register_conflict_on_state(state=state, conflict_record=conflict)

    result = engine.resolve_conflict(
        state=state,
        conflict_id="conflict_truth_vs_protection",
        outcome_type="open_wound",
        resolution_event_id="evt_avoidance",
        unresolved_threads=["Kael no longer trusts Seren"],
        resolution_summary="They avoid the real issue.",
    )

    updated = result["updated_conflict"]

    assert result["success"] is True
    assert updated["status"] == "unresolved"
    assert result["chunk5_handoff"]["must_leave_thread"] is True
    assert result["resolution_consequences"]


def test_conflict_engine_generates_resolution_options():
    state = build_state()
    engine = ConflictResolutionEngine()

    conflict = make_conflict(engine)
    engine.register_conflict_on_state(state=state, conflict_record=conflict)

    result = engine.generate_resolution_options(
        state=state,
        conflict_id="conflict_truth_vs_protection",
    )

    assert result["success"] is True
    assert result["options"]
    assert result["recommended_option"]["outcome_type"] in engine.OUTCOME_TYPES


def test_conflict_engine_builds_conflict_map():
    state = build_state()
    engine = ConflictResolutionEngine()

    conflict = make_conflict(engine)
    engine.register_conflict_on_state(state=state, conflict_record=conflict)

    result = engine.build_conflict_map(state=state)

    assert result["success"] is True
    assert result["conflict_count"] == 1
    assert result["highest_pressure_conflict"]["conflict_id"] == "conflict_truth_vs_protection"
    assert "conflict_truth_vs_protection" in result["conflict_records"]

from backend.app.engines.simulation.simulation_constraint_solver import SimulationConstraintSolver
from backend.app.schemas.global_refs import EntityRef, EntityType
from backend.app.schemas.simulation import (
    DeltaBatch,
    DeltaOperation,
    KnowledgeDelta,
    RelationshipDelta,
    SimulationCharacterState,
    SimulationEntityKind,
    SimulationEntityState,
    SimulationEventPayload,
    SimulationEventType,
    SimulationEventVisibility,
    SimulationKnowledgeState,
    SimulationState,
    SimulationWorldState,
)


def build_state():
    return SimulationState(
        simulation_id="sim_constraint_001",
        world_state=SimulationWorldState(
            world_id="world_velmora",
            active_locations=[
                {"location_id": "location_academy", "name": "Academy"},
                {"location_id": "location_court", "name": "Court"},
            ],
            location_access_rules=[
                {"location_id": "location_court", "requires_sponsor": True},
            ],
            world_simulation_constraints={
                "legal_constraints": ["distrusted family names require sponsor"],
                "power_cost_rules": ["relic power requires cost"],
                "character_permission_boundaries": ["court access requires sponsor"],
            },
            metadata={
                "travel_edges": [
                    {"from_location_id": "location_academy", "to_location_id": "location_court"}
                ]
            },
        ),
        character_states={
            "char_kael": SimulationCharacterState(
                character_id="char_kael",
                current_location_id="location_academy",
                current_agency_state={
                    "agency_capacity": 0.7,
                    "unthinkable_actions": [],
                },
                character_to_simulation_contract={"chunk4_ready": True, "access_route": "sponsor route"},
                metadata={"has_sponsor": True},
            ),
            "char_seren": SimulationCharacterState(
                character_id="char_seren",
                current_location_id="location_court",
                current_agency_state={"agency_capacity": 0.8},
            ),
        },
        knowledge_states={
            "char_kael": SimulationKnowledgeState(
                entity_id="char_kael",
                known_secret_ids=["secret_rank_system_edited"],
                evidence_seen_ids=["evidence_cracked_badge"],
            )
        },
    )


def test_constraint_solver_allows_feasible_public_event():
    state = build_state()
    solver = SimulationConstraintSolver()

    event = SimulationEventPayload(
        event_type=SimulationEventType.PUBLIC_HUMILIATION,
        event_name="Ranking Humiliation",
        actor_ids=["char_seren"],
        target_ids=["char_kael"],
        location_id="location_court",
        visibility=SimulationEventVisibility.PUBLIC,
        witness_ids=["char_seren"],
        intensity=0.8,
        stakes_tags=["status", "identity"],
        theme_tags=["public_worth"],
    )

    report = solver.evaluate_event_feasibility(state=state, event_payload=event)

    assert report["success"] is True
    assert report["feasible"] is True
    assert report["feasibility_score"] > 0.8
    assert "event_intensity_bounded" in report["passed_checks"]


def test_constraint_solver_blocks_missing_participant():
    state = build_state()
    solver = SimulationConstraintSolver()

    event = SimulationEventPayload(
        event_type=SimulationEventType.PRIVATE_CONFESSION,
        actor_ids=["char_missing"],
        target_ids=["char_kael"],
        location_id="location_academy",
        intensity=0.4,
    )

    report = solver.evaluate_event_feasibility(state=state, event_payload=event)

    assert report["feasible"] is False
    assert any("participant char_missing" in blocker for blocker in report["blockers"])


def test_constraint_solver_blocks_impossible_location():
    state = build_state()
    solver = SimulationConstraintSolver()

    event = SimulationEventPayload(
        event_type=SimulationEventType.SECRET_DISCOVERY,
        actor_ids=["char_kael"],
        target_ids=[],
        location_id="location_unknown_vault",
        visibility=SimulationEventVisibility.PRIVATE,
        intensity=0.5,
    )

    report = solver.evaluate_event_feasibility(state=state, event_payload=event)

    assert report["feasible"] is False
    assert any("not in active world locations" in blocker for blocker in report["blockers"])


def test_constraint_solver_blocks_secret_event_without_evidence_or_witness():
    state = build_state()
    solver = SimulationConstraintSolver()

    event = SimulationEventPayload(
        event_type=SimulationEventType.SECRET_DISCOVERY,
        actor_ids=["char_kael"],
        location_id="location_academy",
        visibility=SimulationEventVisibility.PRIVATE,
        intensity=0.5,
        metadata={
            "secret_ids_revealed": ["secret_trial_record"],
        },
    )

    report = solver.evaluate_event_feasibility(state=state, event_payload=event)

    assert report["feasible"] is False
    assert any("secret-moving event lacks evidence" in blocker for blocker in report["blockers"])


def test_constraint_solver_warns_trial_without_sponsor_metadata():
    state = build_state()
    solver = SimulationConstraintSolver()

    event = SimulationEventPayload(
        event_type=SimulationEventType.TRIAL,
        actor_ids=["char_kael"],
        target_ids=["char_seren"],
        location_id="location_court",
        visibility=SimulationEventVisibility.PUBLIC,
        witness_ids=["char_seren"],
        intensity=0.9,
        stakes_tags=["legal", "identity"],
        theme_tags=["truth"],
        metadata={
            "secret_ids_revealed": ["secret_rank_system_edited"],
            "evidence_ids_used": ["evidence_cracked_badge"],
        },
    )

    report = solver.evaluate_event_feasibility(state=state, event_payload=event)

    assert report["feasible"] is True
    assert any("sponsor_id" in warning for warning in report["warnings"])


def test_constraint_solver_blocks_power_event_without_cost():
    state = build_state()
    solver = SimulationConstraintSolver()

    event = SimulationEventPayload(
        event_type=SimulationEventType.RESCUE,
        actor_ids=["char_kael"],
        target_ids=["char_seren"],
        location_id="location_court",
        visibility=SimulationEventVisibility.WITNESSED,
        witness_ids=["char_seren"],
        intensity=0.95,
        stakes_tags=["life_death", "relationship"],
        theme_tags=["sacrifice"],
        metadata={
            "uses_power": True,
            "cost_paid": False,
        },
    )

    report = solver.evaluate_event_feasibility(state=state, event_payload=event)

    assert report["feasible"] is False
    assert any("violates power cost rule" in blocker for blocker in report["blockers"])


def test_constraint_solver_allows_valid_knowledge_delta():
    state = build_state()
    solver = SimulationConstraintSolver()

    delta = KnowledgeDelta(
        simulation_id=state.simulation_id,
        source_engine="simulation.knowledge_secret_engine",
        operation=DeltaOperation.APPEND,
        target_entity_id="char_kael",
        target_path="knowledge_states.char_kael",
        knowledge_holder_id="char_kael",
        secret_ids_added=["secret_court_record"],
        evidence_ids_seen=["evidence_court_record"],
        knowledge_path=["found_document"],
        no_magic_knowledge_checked=True,
    )

    report = solver.evaluate_delta_feasibility(state=state, delta=delta)

    assert report["feasible"] is True
    assert "knowledge_path_exists" in report["passed_checks"]


def test_constraint_solver_blocks_invalid_knowledge_delta():
    state = build_state()
    solver = SimulationConstraintSolver()

    delta = KnowledgeDelta(
        simulation_id=state.simulation_id,
        source_engine="simulation.knowledge_secret_engine",
        operation=DeltaOperation.APPEND,
        target_entity_id="char_kael",
        target_path="knowledge_states.char_kael",
        knowledge_holder_id="char_kael",
        secret_ids_added=["secret_court_record"],
        no_magic_knowledge_checked=False,
    )

    report = solver.evaluate_delta_feasibility(state=state, delta=delta)

    assert report["feasible"] is False
    assert any("no_magic_knowledge" in blocker for blocker in report["blockers"])


def test_constraint_solver_warns_large_relationship_jump_without_trigger():
    state = build_state()
    solver = SimulationConstraintSolver()

    delta = RelationshipDelta(
        simulation_id=state.simulation_id,
        source_engine="simulation.relationship_graph_engine",
        operation=DeltaOperation.INCREMENT,
        target_entity_id="rel_kael_seren",
        target_path="relationship_states.rel_kael_seren",
        character_a_id="char_kael",
        character_b_id="char_seren",
        trust_delta=-0.4,
        romantic_tension_delta=0.3,
        reason="they talked",
        relationship_event_label="small conversation",
    )

    report = solver.evaluate_delta_feasibility(state=state, delta=delta)

    assert report["feasible"] is True
    assert any("trust" in warning for warning in report["warnings"])
    assert any("romantic tension" in warning for warning in report["warnings"])


def test_constraint_solver_blocks_delta_batch_with_invalid_knowledge_delta():
    state = build_state()
    solver = SimulationConstraintSolver()

    good_relationship = RelationshipDelta(
        simulation_id=state.simulation_id,
        source_engine="simulation.relationship_graph_engine",
        operation=DeltaOperation.INCREMENT,
        target_entity_id="rel_kael_seren",
        target_path="relationship_states.rel_kael_seren",
        character_a_id="char_kael",
        character_b_id="char_seren",
        respect_delta=0.1,
        reason="truth under pressure",
        relationship_event_label="truth disclosure",
    )

    bad_knowledge = KnowledgeDelta(
        simulation_id=state.simulation_id,
        source_engine="simulation.knowledge_secret_engine",
        operation=DeltaOperation.APPEND,
        target_entity_id="char_kael",
        target_path="knowledge_states.char_kael",
        knowledge_holder_id="char_kael",
        secret_ids_added=["secret_without_path"],
        no_magic_knowledge_checked=False,
    )

    batch = DeltaBatch(
        simulation_id=state.simulation_id,
        source_engine="test",
        relationship_deltas=[good_relationship],
        knowledge_deltas=[bad_knowledge],
    )

    report = solver.evaluate_delta_batch_feasibility(state=state, delta_batch=batch)

    assert report["feasible"] is False
    assert any("secret knowledge added" in blocker for blocker in report["blockers"])


def test_constraint_solver_blocks_canon_sensitive_locked_field_delta():
    state = build_state()

    ref = EntityRef(
        entity_type=EntityType.CHARACTER,
        entity_id="char_kael",
    )
    state.entity_states["char_kael"] = SimulationEntityState(
        entity_ref=ref,
        entity_kind=SimulationEntityKind.CHARACTER,
        locked_fields=["alive"],
    )

    solver = SimulationConstraintSolver()

    delta = KnowledgeDelta(
        simulation_id=state.simulation_id,
        source_engine="simulation.test",
        operation=DeltaOperation.SET,
        target_entity_id="char_kael",
        target_path="alive",
        knowledge_holder_id="char_kael",
        canon_sensitive=True,
        no_magic_knowledge_checked=True,
    )

    report = solver.evaluate_delta_feasibility(state=state, delta=delta)

    assert report["feasible"] is False
    assert any("locked field alive" in blocker for blocker in report["blockers"])

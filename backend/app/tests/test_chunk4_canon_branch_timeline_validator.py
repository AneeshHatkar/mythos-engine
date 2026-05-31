from backend.app.engines.simulation.canon_branch_timeline_validator import CanonBranchTimelineValidator
from backend.app.schemas.global_refs import CanonStatus, EntityRef, EntityType
from backend.app.schemas.simulation import (
    CanonDelta,
    DeltaBatch,
    DeltaOperation,
    SimulationBranch,
    SimulationCharacterState,
    SimulationEntityKind,
    SimulationEntityState,
    SimulationEventPayload,
    SimulationEventType,
    SimulationState,
    SimulationStatus,
    SimulationTimeline,
    SimulationWorldState,
    TimelineDelta,
)


def build_state():
    ref = EntityRef(entity_type=EntityType.CHARACTER, entity_id="char_kael")

    return SimulationState(
        simulation_id="sim_canon_001",
        status=SimulationStatus.READY,
        world_state=SimulationWorldState(world_id="world_velmora"),
        character_states={
            "char_kael": SimulationCharacterState(character_id="char_kael"),
            "char_seren": SimulationCharacterState(character_id="char_seren"),
        },
        entity_states={
            "char_kael": SimulationEntityState(
                entity_ref=ref,
                entity_kind=SimulationEntityKind.CHARACTER,
                locked_fields=["alive"],
                state_values={"alive": True},
            )
        },
        timeline=SimulationTimeline(
            tick_order=["tick_001"],
            event_order=["evt_intro", "evt_rank_ceremony"],
            current_tick_number=2,
            current_event_id="evt_rank_ceremony",
        ),
    )


def test_validator_allows_valid_event_with_prerequisites():
    state = build_state()
    validator = CanonBranchTimelineValidator()

    event = SimulationEventPayload(
        event_id="evt_trial_reveal",
        event_type=SimulationEventType.TRIAL,
        actor_ids=["char_kael"],
        target_ids=["char_seren"],
        witness_ids=["char_seren"],
        prerequisite_event_ids=["evt_intro", "evt_rank_ceremony"],
        metadata={"target_tick_number": 3},
    )

    report = validator.validate_event(state=state, event_payload=event)

    assert report["success"] is True
    assert report["valid"] is True
    assert "event_prerequisites_satisfied" in report["passed_checks"]
    assert "event_id_not_duplicate" in report["passed_checks"]


def test_validator_blocks_duplicate_event_id():
    state = build_state()
    validator = CanonBranchTimelineValidator()

    event = SimulationEventPayload(
        event_id="evt_intro",
        event_type=SimulationEventType.PRIVATE_CONFESSION,
        actor_ids=["char_kael"],
    )

    report = validator.validate_event(state=state, event_payload=event)

    assert report["valid"] is False
    assert any("already exists" in blocker for blocker in report["blockers"])


def test_validator_blocks_missing_prerequisite():
    state = build_state()
    validator = CanonBranchTimelineValidator()

    event = SimulationEventPayload(
        event_id="evt_trial_reveal",
        event_type=SimulationEventType.TRIAL,
        actor_ids=["char_kael"],
        prerequisite_event_ids=["evt_missing"],
    )

    report = validator.validate_event(state=state, event_payload=event)

    assert report["valid"] is False
    assert any("prerequisites missing" in blocker for blocker in report["blockers"])


def test_validator_blocks_past_timeline_insert_without_branch():
    state = build_state()
    validator = CanonBranchTimelineValidator()

    event = SimulationEventPayload(
        event_id="evt_backfill",
        event_type=SimulationEventType.SECRET_DISCOVERY,
        actor_ids=["char_kael"],
        metadata={"target_tick_number": 1},
    )

    report = validator.validate_event(state=state, event_payload=event)

    assert report["valid"] is False
    assert any("insert into past timeline" in blocker for blocker in report["blockers"])


def test_validator_blocks_dead_character_participation():
    state = build_state()
    state.character_states["char_kael"].metadata["dead"] = True
    validator = CanonBranchTimelineValidator()

    event = SimulationEventPayload(
        event_id="evt_after_death",
        event_type=SimulationEventType.PRIVATE_CONFESSION,
        actor_ids=["char_kael"],
    )

    report = validator.validate_event(state=state, event_payload=event)

    assert report["valid"] is False
    assert any("dead" in blocker for blocker in report["blockers"])


def test_validator_blocks_unknown_branch_reference():
    state = build_state()
    validator = CanonBranchTimelineValidator()

    event = SimulationEventPayload(
        event_id="evt_branch_event",
        event_type=SimulationEventType.SECRET_DISCOVERY,
        actor_ids=["char_kael"],
        metadata={"branch_id": "branch_missing"},
    )

    report = validator.validate_event(state=state, event_payload=event)

    assert report["valid"] is False
    assert any("unknown branch_id" in blocker for blocker in report["blockers"])


def test_validator_allows_known_branch_reference():
    state = build_state()
    branch = SimulationBranch(
        branch_id="branch_truth_path",
        source_event_id="evt_rank_ceremony",
        branch_reason="Kael tells the truth publicly.",
        canon_status=CanonStatus.ALTERNATE_BRANCH,
    )
    state.branches[branch.branch_id] = branch

    validator = CanonBranchTimelineValidator()

    event = SimulationEventPayload(
        event_id="evt_branch_event",
        event_type=SimulationEventType.SECRET_DISCOVERY,
        actor_ids=["char_kael"],
        metadata={"branch_id": "branch_truth_path"},
    )

    report = validator.validate_event(state=state, event_payload=event)

    assert report["valid"] is True
    assert "event_branch_id_exists" in report["passed_checks"]


def test_validator_blocks_canon_sensitive_locked_field_delta():
    state = build_state()
    validator = CanonBranchTimelineValidator()

    delta = CanonDelta(
        simulation_id=state.simulation_id,
        source_engine="simulation.test",
        operation=DeltaOperation.SET,
        target_entity_id="char_kael",
        target_path="alive",
        canon_sensitive=True,
        canon_status_before=CanonStatus.CANON,
        canon_status_after=CanonStatus.CANON,
        canon_change_summary="Trying to change locked alive field.",
    )

    report = validator.validate_delta(state=state, delta=delta)

    assert report["valid"] is False
    assert any("locked field alive" in blocker for blocker in report["blockers"])


def test_validator_blocks_retcon_without_alternate_branch():
    state = build_state()
    validator = CanonBranchTimelineValidator()

    delta = CanonDelta(
        simulation_id=state.simulation_id,
        source_engine="simulation.test",
        operation=DeltaOperation.SET,
        target_entity_id="evt_intro",
        target_path="canon_status",
        canon_status_before=CanonStatus.CANON,
        canon_status_after=CanonStatus.DRAFT,
        retcon_required=True,
        alternate_branch_recommended=False,
        canon_change_summary="Unsafe retcon.",
    )

    report = validator.validate_delta(state=state, delta=delta)

    assert report["valid"] is False
    assert any("retcon_required" in blocker for blocker in report["blockers"])


def test_validator_blocks_timeline_delta_missing_prerequisite():
    state = build_state()
    validator = CanonBranchTimelineValidator()

    delta = TimelineDelta(
        simulation_id=state.simulation_id,
        source_engine="simulation.timeline_engine",
        operation=DeltaOperation.APPEND,
        target_entity_id=state.simulation_id,
        target_path="timeline.event_order",
        event_ids_added=["evt_new"],
        prerequisite_event_ids=["evt_missing"],
    )

    report = validator.validate_delta(state=state, delta=delta)

    assert report["valid"] is False
    assert any("missing prerequisite" in blocker for blocker in report["blockers"])


def test_validator_validates_delta_batch():
    state = build_state()
    validator = CanonBranchTimelineValidator()

    good = TimelineDelta(
        simulation_id=state.simulation_id,
        source_engine="simulation.timeline_engine",
        operation=DeltaOperation.APPEND,
        target_entity_id=state.simulation_id,
        target_path="timeline.event_order",
        event_ids_added=["evt_new"],
        prerequisite_event_ids=["evt_rank_ceremony"],
    )

    bad = CanonDelta(
        simulation_id=state.simulation_id,
        source_engine="simulation.test",
        operation=DeltaOperation.SET,
        target_entity_id="evt_intro",
        target_path="canon_status",
        retcon_required=True,
        alternate_branch_recommended=False,
    )

    batch = DeltaBatch(
        simulation_id=state.simulation_id,
        source_engine="test",
        timeline_deltas=[good],
        canon_deltas=[bad],
    )

    report = validator.validate_delta_batch(state=state, delta_batch=batch)

    assert report["valid"] is False
    assert any("retcon_required" in blocker for blocker in report["blockers"])


def test_validator_branch_creation_requires_source():
    state = build_state()
    validator = CanonBranchTimelineValidator()

    branch = SimulationBranch(
        branch_reason="",
        canon_status=CanonStatus.ALTERNATE_BRANCH,
    )

    report = validator.validate_branch_creation(state=state, branch=branch)

    assert report["valid"] is False
    assert any("requires source_event_id or source_tick_id" in blocker for blocker in report["blockers"])


def test_validator_allows_valid_branch_creation():
    state = build_state()
    validator = CanonBranchTimelineValidator()

    branch = SimulationBranch(
        source_event_id="evt_rank_ceremony",
        branch_reason="Kael tells the truth instead of staying silent.",
        chosen_choice_id="choice_truth",
        rejected_choice_ids=["choice_silence"],
        canon_status=CanonStatus.ALTERNATE_BRANCH,
    )

    report = validator.validate_branch_creation(state=state, branch=branch)

    assert report["valid"] is True
    assert "branch_has_source" in report["passed_checks"]
    assert "branch_reason_present" in report["passed_checks"]

from backend.app.engines.simulation.evidence_engine import EvidenceEngine
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
        simulation_id="sim_evidence_001",
        world_state=SimulationWorldState(world_id="world_velmora"),
        character_states={
            "char_kael": SimulationCharacterState(character_id="char_kael", current_location_id="location_court"),
            "char_seren": SimulationCharacterState(character_id="char_seren", current_location_id="location_court"),
            "char_vask": SimulationCharacterState(character_id="char_vask", current_location_id="location_outer"),
        },
    )


def test_evidence_engine_creates_and_registers_evidence():
    state = build_state()
    engine = EvidenceEngine()

    evidence = engine.create_evidence_record(
        evidence_id="evidence_cracked_badge",
        evidence_type="physical",
        summary="A cracked academy badge with edited rank seal residue.",
        linked_secret_ids=["secret_rank_system_edited"],
        truth_value="true",
        reliability=0.86,
        legal_validity=0.74,
        owner_id="char_seren",
        current_location_id="location_court",
        seen_by_ids=["char_seren"],
    )

    result = engine.register_evidence_on_state(state=state, evidence_record=evidence)

    assert result["success"] is True
    assert "evidence_cracked_badge" in state.metadata["evidence_registry"]
    assert "evidence_cracked_badge" in state.knowledge_states["char_seren"].evidence_seen_ids
    assert "secret_rank_system_edited" in state.knowledge_states["char_seren"].suspected_secret_ids


def test_evidence_engine_evaluates_owner_access():
    state = build_state()
    engine = EvidenceEngine()

    evidence = engine.create_evidence_record(
        evidence_id="evidence_cracked_badge",
        evidence_type="physical",
        summary="A cracked academy badge.",
        owner_id="char_seren",
        current_location_id="location_court",
    )
    engine.register_evidence_on_state(state=state, evidence_record=evidence)

    access = engine.evaluate_evidence_access(
        state=state,
        evidence_id="evidence_cracked_badge",
        actor_id="char_seren",
    )

    assert access["can_access"] is True
    assert "actor_owns_evidence" in access["passed_checks"]


def test_evidence_engine_blocks_no_access_path():
    state = build_state()
    engine = EvidenceEngine()

    evidence = engine.create_evidence_record(
        evidence_id="evidence_hidden_record",
        evidence_type="document",
        summary="A hidden court record.",
        current_location_id="location_court",
    )
    engine.register_evidence_on_state(state=state, evidence_record=evidence)

    access = engine.evaluate_evidence_access(
        state=state,
        evidence_id="evidence_hidden_record",
        actor_id="char_vask",
    )

    assert access["can_access"] is False
    assert any("no valid access path" in blocker for blocker in access["blockers"])


def test_evidence_engine_reveals_true_evidence_to_character_as_known_secret():
    state = build_state()
    engine = EvidenceEngine()

    evidence = engine.create_evidence_record(
        evidence_id="evidence_cracked_badge",
        evidence_type="legal_record",
        summary="Court-certified rank edit residue report.",
        linked_secret_ids=["secret_rank_system_edited"],
        truth_value="true",
        reliability=0.9,
        legal_validity=0.88,
        current_location_id="location_court",
    )
    engine.register_evidence_on_state(state=state, evidence_record=evidence)

    event = SimulationEventPayload(
        event_id="evt_trial_reveal",
        event_type=SimulationEventType.TRIAL,
        actor_ids=["char_seren"],
        target_ids=["char_kael"],
        witness_ids=["char_kael"],
        location_id="location_court",
        visibility=SimulationEventVisibility.PUBLIC,
    )

    result = engine.reveal_evidence_to_character(
        state=state,
        evidence_id="evidence_cracked_badge",
        viewer_id="char_kael",
        event_payload=event,
    )

    assert result["success"] is True
    assert "evidence_cracked_badge" in state.knowledge_states["char_kael"].evidence_seen_ids
    assert "secret_rank_system_edited" in state.knowledge_states["char_kael"].known_secret_ids
    assert state.knowledge_states["char_kael"].knowledge_confidence["secret_rank_system_edited"] > 0.7


def test_evidence_engine_reveals_low_reliability_evidence_as_suspicion():
    state = build_state()
    engine = EvidenceEngine()

    evidence = engine.create_evidence_record(
        evidence_id="evidence_partial_rumor_note",
        evidence_type="document",
        summary="An unsigned note implying rank edits.",
        linked_secret_ids=["secret_rank_system_edited"],
        truth_value="true",
        reliability=0.55,
        legal_validity=0.3,
        current_location_id="location_court",
    )
    engine.register_evidence_on_state(state=state, evidence_record=evidence)

    event = SimulationEventPayload(
        event_id="evt_note_found",
        event_type=SimulationEventType.SECRET_DISCOVERY,
        actor_ids=["char_kael"],
        location_id="location_court",
    )

    result = engine.reveal_evidence_to_character(
        state=state,
        evidence_id="evidence_partial_rumor_note",
        viewer_id="char_kael",
        event_payload=event,
    )

    assert result["success"] is True
    assert "secret_rank_system_edited" in state.knowledge_states["char_kael"].suspected_secret_ids
    assert "secret_rank_system_edited" not in state.knowledge_states["char_kael"].known_secret_ids


def test_evidence_engine_builds_knowledge_delta_from_evidence():
    state = build_state()
    engine = EvidenceEngine()

    evidence = engine.create_evidence_record(
        evidence_id="evidence_cracked_badge",
        evidence_type="legal_record",
        summary="Court-certified record.",
        linked_secret_ids=["secret_rank_system_edited"],
        truth_value="true",
        reliability=0.9,
        legal_validity=0.88,
    )
    engine.register_evidence_on_state(state=state, evidence_record=evidence)

    event = SimulationEventPayload(
        event_id="evt_trial",
        event_type=SimulationEventType.TRIAL,
        witness_ids=["char_kael"],
    )

    delta = engine.build_knowledge_delta_from_evidence(
        state=state,
        evidence_id="evidence_cracked_badge",
        viewer_id="char_kael",
        event_payload=event,
    )

    assert delta.no_magic_knowledge_checked is True
    assert "evidence_cracked_badge" in delta.evidence_ids_seen
    assert "secret_rank_system_edited" in delta.secret_ids_added
    assert delta.knowledge_confidence_updates["secret_rank_system_edited"] > 0.7


def test_evidence_engine_evaluates_trial_claim_strength():
    state = build_state()
    engine = EvidenceEngine()

    strong = engine.create_evidence_record(
        evidence_id="evidence_court_record",
        evidence_type="legal_record",
        summary="Court record proving rank edit.",
        linked_secret_ids=["secret_rank_system_edited"],
        truth_value="true",
        reliability=0.91,
        legal_validity=0.9,
    )
    engine.register_evidence_on_state(state=state, evidence_record=strong)

    report = engine.evaluate_evidence_for_trial_or_public_claim(
        state=state,
        evidence_ids=["evidence_court_record"],
        claim_secret_id="secret_rank_system_edited",
        audience_type="court",
    )

    assert report["success"] is True
    assert report["claim_supported"] is True
    assert report["total_argument_strength"] >= 0.75


def test_evidence_engine_marks_evidence_forged_or_disputed():
    state = build_state()
    engine = EvidenceEngine()

    evidence = engine.create_evidence_record(
        evidence_id="evidence_fake_letter",
        evidence_type="document",
        summary="A suspicious letter.",
        linked_secret_ids=["secret_rank_system_edited"],
        truth_value="unknown",
        reliability=0.6,
        legal_validity=0.4,
    )
    engine.register_evidence_on_state(state=state, evidence_record=evidence)

    result = engine.mark_evidence_forged_or_disputed(
        state=state,
        evidence_id="evidence_fake_letter",
        disputed_by_id="char_kael",
        forged_by_id="char_vask",
        reason="Ink signature mismatch.",
    )

    updated = result["updated_evidence"]

    assert result["success"] is True
    assert updated["evidence_type"] == "forged"
    assert updated["truth_value"] == "false"
    assert updated["forged_by_id"] == "char_vask"
    assert "char_kael" in updated["disputed_by_ids"]
    assert updated["reliability"] < 0.6


def test_evidence_engine_builds_evidence_map():
    state = build_state()
    engine = EvidenceEngine()

    evidence = engine.create_evidence_record(
        evidence_id="evidence_cracked_badge",
        evidence_type="physical",
        summary="A cracked badge.",
        linked_secret_ids=["secret_rank_system_edited"],
        truth_value="true",
        reliability=0.8,
        legal_validity=0.7,
        seen_by_ids=["char_seren"],
    )
    engine.register_evidence_on_state(state=state, evidence_record=evidence)

    evidence_map = engine.build_evidence_map(state=state)

    assert evidence_map["success"] is True
    assert evidence_map["evidence_count"] == 1
    record = evidence_map["evidence_records"]["evidence_cracked_badge"]
    assert record["truth_value"] == "true"
    assert "char_seren" in record["seen_by"]
    assert record["argument_strength"] > 0.5


def test_evidence_engine_builds_delta_batch_for_evidence_reveal():
    state = build_state()
    engine = EvidenceEngine()

    evidence = engine.create_evidence_record(
        evidence_id="evidence_cracked_badge",
        evidence_type="legal_record",
        summary="Court-certified record.",
        linked_secret_ids=["secret_rank_system_edited"],
        truth_value="true",
        reliability=0.9,
        legal_validity=0.88,
    )
    engine.register_evidence_on_state(state=state, evidence_record=evidence)

    event = SimulationEventPayload(
        event_id="evt_trial",
        event_type=SimulationEventType.TRIAL,
        witness_ids=["char_kael", "char_vask"],
    )

    batch = engine.build_delta_batch_for_evidence_reveal(
        state=state,
        event_payload=event,
        evidence_id="evidence_cracked_badge",
        reveal_to_ids=["char_kael", "char_vask"],
    )

    assert batch.source_engine == engine.engine_name
    assert len(batch.knowledge_deltas) == 2
    assert batch.knowledge_deltas[0].no_magic_knowledge_checked is True
    assert batch.application_order == [delta.delta_id for delta in batch.knowledge_deltas]

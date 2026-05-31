from backend.app.engines.simulation.location_presence_witness_validator import LocationPresenceWitnessValidator
from backend.app.schemas.simulation import (
    DeltaOperation,
    KnowledgeDelta,
    SimulationCharacterState,
    SimulationEventPayload,
    SimulationEventType,
    SimulationEventVisibility,
    SimulationState,
    SimulationWorldState,
)


def build_state():
    return SimulationState(
        simulation_id="sim_presence_001",
        world_state=SimulationWorldState(
            world_id="world_velmora",
            active_locations=[
                {"location_id": "location_academy", "name": "Academy"},
                {"location_id": "location_court", "name": "Court"},
                {"location_id": "location_outer_district", "name": "Outer District"},
            ],
            location_access_rules=[
                {
                    "location_id": "location_court",
                    "requires_sponsor": True,
                    "restricted_classes": ["erased"],
                }
            ],
            metadata={
                "travel_edges": [
                    {
                        "from_location_id": "location_academy",
                        "to_location_id": "location_court",
                        "bidirectional": True,
                    }
                ],
                "rumor_edges": [
                    {
                        "from_location_id": "location_court",
                        "to_location_id": "location_outer_district",
                        "bidirectional": True,
                    }
                ],
                "evidence_locations": {
                    "evidence_cracked_badge": "location_court",
                },
            },
        ),
        character_states={
            "char_kael": SimulationCharacterState(
                character_id="char_kael",
                current_location_id="location_academy",
                character_to_simulation_contract={"access_route": "sponsor route"},
                metadata={"has_sponsor": True},
            ),
            "char_seren": SimulationCharacterState(
                character_id="char_seren",
                current_location_id="location_court",
            ),
            "char_vask": SimulationCharacterState(
                character_id="char_vask",
                current_location_id="location_outer_district",
            ),
        },
    )


def test_presence_validator_allows_event_when_travel_path_exists():
    state = build_state()
    validator = LocationPresenceWitnessValidator()

    event = SimulationEventPayload(
        event_type=SimulationEventType.TRIAL,
        actor_ids=["char_kael"],
        target_ids=["char_seren"],
        witness_ids=["char_seren"],
        location_id="location_court",
        visibility=SimulationEventVisibility.PUBLIC,
    )

    report = validator.validate_event_presence(state=state, event_payload=event)

    assert report["success"] is True
    assert report["valid"] is True
    assert any("char_kael_travel_path_exists" in item for item in report["passed_checks"])
    assert any("char_kael_has_required_sponsor" in item for item in report["passed_checks"])


def test_presence_validator_blocks_unknown_location():
    state = build_state()
    validator = LocationPresenceWitnessValidator()

    event = SimulationEventPayload(
        event_type=SimulationEventType.SECRET_DISCOVERY,
        actor_ids=["char_kael"],
        location_id="location_unknown",
    )

    report = validator.validate_event_presence(state=state, event_payload=event)

    assert report["valid"] is False
    assert any("not an active world location" in blocker for blocker in report["blockers"])


def test_presence_validator_blocks_impossible_presence_without_travel():
    state = build_state()
    validator = LocationPresenceWitnessValidator()

    event = SimulationEventPayload(
        event_type=SimulationEventType.PRIVATE_CONFESSION,
        actor_ids=["char_vask"],
        target_ids=["char_kael"],
        location_id="location_academy",
        visibility=SimulationEventVisibility.PRIVATE,
    )

    report = validator.validate_event_presence(state=state, event_payload=event)

    assert report["valid"] is False
    assert any("cannot be present" in blocker for blocker in report["blockers"])


def test_presence_validator_allows_remote_participant_metadata():
    state = build_state()
    validator = LocationPresenceWitnessValidator()

    event = SimulationEventPayload(
        event_type=SimulationEventType.FACTION_ORDER,
        actor_ids=["char_vask"],
        target_ids=["char_kael"],
        location_id="location_academy",
        visibility=SimulationEventVisibility.PRIVATE,
        metadata={"remote_participant_ids": ["char_vask"]},
    )

    report = validator.validate_event_presence(state=state, event_payload=event)

    assert report["valid"] is True
    assert any("remote_participation_possible" in item for item in report["passed_checks"])


def test_presence_validator_blocks_invalid_private_witness_location():
    state = build_state()
    validator = LocationPresenceWitnessValidator()

    event = SimulationEventPayload(
        event_type=SimulationEventType.PRIVATE_CONFESSION,
        actor_ids=["char_kael"],
        target_ids=["char_seren"],
        witness_ids=["char_vask"],
        location_id="location_academy",
        visibility=SimulationEventVisibility.PRIVATE,
    )

    report = validator.validate_event_presence(state=state, event_payload=event)

    assert report["valid"] is False
    assert any("cannot witness" in blocker for blocker in report["blockers"])


def test_presence_validator_allows_rumor_channel_witness():
    state = build_state()
    validator = LocationPresenceWitnessValidator()

    event = SimulationEventPayload(
        event_type=SimulationEventType.RUMOR_SPREAD,
        actor_ids=["char_seren"],
        witness_ids=["char_vask"],
        location_id="location_court",
        visibility=SimulationEventVisibility.WITNESSED,
    )

    report = validator.validate_event_presence(state=state, event_payload=event)

    assert report["valid"] is True
    assert any("rumor_channel_possible" in item for item in report["passed_checks"])


def test_witness_path_report_classifies_direct_remote_and_impossible_witnesses():
    state = build_state()
    validator = LocationPresenceWitnessValidator()

    event = SimulationEventPayload(
        event_type=SimulationEventType.PUBLIC_HUMILIATION,
        actor_ids=["char_seren"],
        witness_ids=["char_seren", "char_vask", "char_missing"],
        location_id="location_court",
        visibility=SimulationEventVisibility.PUBLIC,
    )

    report = validator.build_witness_path_report(state=state, event_payload=event)

    assert report["success"] is True
    assert "char_seren" in report["direct_witnesses"]
    assert "char_vask" in report["hidden_or_remote_witnesses"]
    assert report["impossible_witnesses"][0]["witness_id"] == "char_missing"
    assert report["witness_path_valid"] is False


def test_knowledge_witness_path_accepts_evidence_and_source_event_presence():
    state = build_state()
    validator = LocationPresenceWitnessValidator()

    event = SimulationEventPayload(
        event_type=SimulationEventType.SECRET_DISCOVERY,
        actor_ids=["char_seren"],
        target_ids=["char_kael"],
        witness_ids=["char_kael"],
        location_id="location_court",
        visibility=SimulationEventVisibility.WITNESSED,
    )

    delta = KnowledgeDelta(
        simulation_id=state.simulation_id,
        source_engine="simulation.knowledge_secret_engine",
        operation=DeltaOperation.APPEND,
        target_entity_id="char_kael",
        target_path="knowledge_states.char_kael",
        knowledge_holder_id="char_kael",
        secret_ids_added=["secret_rank_system_edited"],
        evidence_ids_seen=["evidence_cracked_badge"],
        knowledge_path=["witnessed_evidence"],
        witness_ids=["char_seren"],
        no_magic_knowledge_checked=True,
    )

    report = validator.validate_knowledge_witness_path(
        state=state,
        knowledge_delta=delta,
        source_event=event,
    )

    assert report["valid"] is True
    assert report["knowledge_path_type"] == "evidence+explicit+witness"
    assert "knowledge_holder_present_or_witnessed_source_event" in report["passed_checks"]


def test_knowledge_witness_path_blocks_secret_without_path():
    state = build_state()
    validator = LocationPresenceWitnessValidator()

    delta = KnowledgeDelta(
        simulation_id=state.simulation_id,
        source_engine="simulation.knowledge_secret_engine",
        operation=DeltaOperation.APPEND,
        target_entity_id="char_kael",
        target_path="knowledge_states.char_kael",
        knowledge_holder_id="char_kael",
        secret_ids_added=["secret_rank_system_edited"],
        no_magic_knowledge_checked=True,
    )

    report = validator.validate_knowledge_witness_path(state=state, knowledge_delta=delta)

    assert report["valid"] is False
    assert any("no evidence, witness, or explicit path" in blocker for blocker in report["blockers"])


def test_knowledge_witness_path_blocks_holder_not_in_source_event_private_visibility():
    state = build_state()
    validator = LocationPresenceWitnessValidator()

    event = SimulationEventPayload(
        event_type=SimulationEventType.SECRET_DISCOVERY,
        actor_ids=["char_seren"],
        target_ids=[],
        witness_ids=[],
        location_id="location_court",
        visibility=SimulationEventVisibility.PRIVATE,
    )

    delta = KnowledgeDelta(
        simulation_id=state.simulation_id,
        source_engine="simulation.knowledge_secret_engine",
        operation=DeltaOperation.APPEND,
        target_entity_id="char_kael",
        target_path="knowledge_states.char_kael",
        knowledge_holder_id="char_kael",
        secret_ids_added=["secret_trial_record"],
        evidence_ids_seen=["evidence_cracked_badge"],
        knowledge_path=["somehow_knows"],
        no_magic_knowledge_checked=True,
    )

    report = validator.validate_knowledge_witness_path(
        state=state,
        knowledge_delta=delta,
        source_event=event,
    )

    assert report["valid"] is False
    assert any("not actor, target, witness" in blocker for blocker in report["blockers"])


def test_private_event_warns_for_outside_witness():
    state = build_state()
    validator = LocationPresenceWitnessValidator()

    event = SimulationEventPayload(
        event_type=SimulationEventType.PRIVATE_CONFESSION,
        actor_ids=["char_seren"],
        target_ids=["char_kael"],
        witness_ids=["char_seren", "char_kael"],
        location_id="location_court",
        visibility=SimulationEventVisibility.PRIVATE,
    )

    report = validator.validate_event_presence(state=state, event_payload=event)

    assert report["valid"] is True
    assert "private_event_has_no_outside_witnesses" in report["passed_checks"]

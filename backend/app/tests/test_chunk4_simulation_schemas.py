from backend.app.schemas.global_refs import CanonStatus, EntityRef, EntityType, ProjectUniverseRef
from backend.app.schemas.simulation import (
    SimulationAuditTrace,
    SimulationBranch,
    SimulationCharacterState,
    SimulationDependencyContract,
    SimulationEntityKind,
    SimulationEntityState,
    SimulationEventPayload,
    SimulationEventType,
    SimulationEventVisibility,
    SimulationKnowledgeState,
    SimulationReadinessLevel,
    SimulationRelationshipState,
    SimulationRunResult,
    SimulationState,
    SimulationStatus,
    SimulationTick,
    SimulationTimeline,
    SimulationWorldState,
)


def sample_project_ref():
    return ProjectUniverseRef(
        project_id="proj_ashen",
        universe_id="velmora",
        branch_id="main",
        timeline_id="main",
    )


def sample_world_state():
    return SimulationWorldState(
        world_id="world_velmora",
        world_name="Velmora",
        world_contract={
            "legal_constraints": ["distrusted family names need sponsor to testify"],
            "power_laws": ["relic power requires cost"],
        },
        world_simulation_constraints={
            "legal_constraints": ["distrusted family names need sponsor to testify"],
            "power_cost_rules": ["relic power requires cost"],
            "character_permission_boundaries": ["academy access requires route"],
        },
        active_laws=[{"law_id": "law_testimony", "name": "Witness Sponsor Law"}],
        active_factions=[{"faction_id": "faction_oath_court", "name": "Oath Court"}],
        active_locations=[{"location_id": "location_academy", "name": "Academy"}],
        location_access_rules=[{"location_id": "location_court", "requires_sponsor": True}],
        canon_status=CanonStatus.DRAFT,
    )


def sample_character_state(character_id="char_kael"):
    return SimulationCharacterState(
        character_id=character_id,
        current_location_id="location_academy",
        current_emotion_state={
            "dominant_emotion": "controlled_pressure",
            "emotion_vector": {"shame": 0.2, "hope": 0.3},
        },
        current_memory_state={
            "active_memory_ids": ["mem_public_failure"],
            "new_memory_queue": [],
        },
        current_agency_state={
            "agency_capacity": 0.72,
            "available_actions": ["stay_silent", "ask_for_time"],
        },
        current_relationship_state={
            "known_relationship_edges": [],
            "pending_relationship_deltas": [],
        },
        current_knowledge_state={
            "known_secret_ids": [],
            "suspected_secret_ids": [],
            "evidence_seen_ids": [],
        },
        current_goal_pressure={
            "surface_goal": "survive academy ranking",
            "hidden_goal": "prove the ranking system is edited",
        },
        dialogue_constraint_seed={"base_voice_family": "controlled_subtext_voice"},
        relationship_state_seed={"relationship_readiness_family": "high_loyalty_power_broker_readiness"},
        character_to_simulation_contract={"chunk4_ready": True},
    )


def test_simulation_world_state_validates():
    world = sample_world_state()

    assert world.world_id == "world_velmora"
    assert world.world_simulation_constraints["power_cost_rules"]
    assert world.active_laws[0]["law_id"] == "law_testimony"
    assert world.canon_status == CanonStatus.DRAFT


def test_simulation_character_state_separates_mutable_state_from_profile():
    character = sample_character_state()

    assert character.character_id == "char_kael"
    assert character.current_emotion_state["dominant_emotion"] == "controlled_pressure"
    assert character.current_memory_state["active_memory_ids"] == ["mem_public_failure"]
    assert character.current_agency_state["agency_capacity"] == 0.72
    assert character.character_to_simulation_contract["chunk4_ready"] is True


def test_simulation_entity_state_validates_with_entity_ref():
    ref = EntityRef(
        entity_type=EntityType.CHARACTER,
        entity_id="char_kael",
        project_id="proj_ashen",
        universe_id="velmora",
    )

    entity_state = SimulationEntityState(
        entity_ref=ref,
        entity_kind=SimulationEntityKind.CHARACTER,
        current_location_id="location_academy",
        state_values={"alive": True, "public_status": "scholarship student"},
        locked_fields=["alive"],
    )

    assert entity_state.entity_ref.entity_id == "char_kael"
    assert entity_state.entity_kind == SimulationEntityKind.CHARACTER
    assert entity_state.locked_fields == ["alive"]


def test_relationship_and_knowledge_states_validate():
    relationship = SimulationRelationshipState(
        character_a_id="char_kael",
        character_b_id="char_seren",
        relationship_type="rivalry_with_hidden_care",
        trust=0.25,
        respect=0.55,
        romantic_tension=0.35,
        rivalry=0.7,
        knowledge_asymmetry=0.4,
        repair_potential=0.6,
        betrayal_risk=0.2,
    )

    knowledge = SimulationKnowledgeState(
        entity_id="char_kael",
        known_secret_ids=["secret_rank_system_edited"],
        evidence_seen_ids=["evidence_cracked_badge"],
        rumors_heard_ids=["rumor_seren_family"],
        knowledge_confidence={"secret_rank_system_edited": 0.82},
    )

    assert relationship.relationship_id.startswith("rel_")
    assert relationship.romantic_tension == 0.35
    assert knowledge.knowledge_id.startswith("knowledge_")
    assert knowledge.knowledge_confidence["secret_rank_system_edited"] == 0.82


def test_simulation_event_payload_validates_core_event_types():
    event = SimulationEventPayload(
        event_type=SimulationEventType.PUBLIC_HUMILIATION,
        event_name="Ranking Ceremony Humiliation",
        description="Kael is humiliated during a public ranking ceremony.",
        actor_ids=["char_rival"],
        target_ids=["char_kael"],
        location_id="location_academy_hall",
        visibility=SimulationEventVisibility.PUBLIC,
        witness_ids=["char_seren", "char_vask"],
        intensity=0.86,
        stakes_tags=["status", "identity", "romance_pressure"],
        theme_tags=["public_worth", "erased_truth"],
    )

    assert event.event_id.startswith("evt_")
    assert event.event_type == SimulationEventType.PUBLIC_HUMILIATION
    assert event.visibility == SimulationEventVisibility.PUBLIC
    assert event.intensity == 0.86


def test_simulation_dependency_contract_validates_pass_e_inputs():
    contract = SimulationDependencyContract(
        project_ref=sample_project_ref(),
        world_contract={"legal_constraints": ["sponsor required"]},
        world_simulation_constraints={"power_cost_rules": ["cost required"]},
        character_simulation_contracts={
            "char_kael": {"chunk4_ready": True},
            "char_seren": {"chunk4_ready": True},
        },
        story_dna_seed={"core_question": "Can truth survive institutional permission?"},
        emotional_resonance_seed={"desired_reader_emotion": "aching intimacy under pressure"},
        character_contrast_matrix={"ensemble_ready": True},
        world_character_pressure_matrix={"simulation_ready": True},
        required_invariants=[
            "no_magic_knowledge",
            "no_consequence_free_major_choice",
            "no_relationship_jump_without_cause",
        ],
        readiness_level=SimulationReadinessLevel.VERIFIED,
        readiness_score=0.96,
    )

    assert contract.contract_id.startswith("simcontract_")
    assert contract.readiness_level == SimulationReadinessLevel.VERIFIED
    assert contract.character_simulation_contracts["char_kael"]["chunk4_ready"] is True
    assert contract.story_dna_seed["core_question"]


def test_simulation_timeline_branch_tick_and_audit_validate():
    timeline = SimulationTimeline(
        project_ref=sample_project_ref(),
        tick_order=["tick_1"],
        event_order=["evt_1"],
        current_tick_number=1,
        current_event_id="evt_1",
    )

    branch = SimulationBranch(
        branch_reason="Kael chooses public truth instead of silence.",
        source_event_id="evt_1",
        chosen_choice_id="choice_truth",
        rejected_choice_ids=["choice_silence"],
        canon_status=CanonStatus.ALTERNATE_BRANCH,
    )

    event = SimulationEventPayload(event_type=SimulationEventType.SECRET_DISCOVERY)
    tick = SimulationTick(
        simulation_id="sim_001",
        tick_number=1,
        event_payload=event,
        produced_delta_ids=["delta_1"],
        quality_scores={"causal_coherence": 0.91},
    )

    audit = SimulationAuditTrace(
        simulation_id="sim_001",
        tick_id=tick.tick_id,
        engine_name="simulation.test_engine",
        decisions=["validated event feasibility"],
        metrics={"runtime_ms": 2.4},
    )

    assert timeline.timeline_id.startswith("simtimeline_")
    assert branch.branch_id.startswith("simbranch_")
    assert tick.tick_id.startswith("tick_")
    assert audit.audit_id.startswith("simaudit_")


def test_simulation_state_validates_complete_master_state():
    kael = sample_character_state("char_kael")
    seren = sample_character_state("char_seren")

    relationship = SimulationRelationshipState(
        character_a_id="char_kael",
        character_b_id="char_seren",
        relationship_type="rivalry_with_hidden_care",
        trust=0.2,
        respect=0.6,
    )

    dependency_contract = SimulationDependencyContract(
        project_ref=sample_project_ref(),
        world_contract={"legal_constraints": ["sponsor required"]},
        world_simulation_constraints={"power_cost_rules": ["cost required"]},
        character_simulation_contracts={
            "char_kael": {"chunk4_ready": True},
            "char_seren": {"chunk4_ready": True},
        },
        story_dna_seed={"core_question": "Can truth survive institutional permission?"},
        emotional_resonance_seed={"desired_reader_emotion": "aching intimacy"},
        character_contrast_matrix={"ensemble_ready": True},
        world_character_pressure_matrix={"simulation_ready": True},
        readiness_level=SimulationReadinessLevel.VERIFIED,
        readiness_score=0.96,
    )

    state = SimulationState(
        project_ref=sample_project_ref(),
        status=SimulationStatus.READY,
        world_state=sample_world_state(),
        character_states={
            "char_kael": kael,
            "char_seren": seren,
        },
        relationship_states={
            relationship.relationship_id: relationship,
        },
        knowledge_states={
            "char_kael": SimulationKnowledgeState(entity_id="char_kael"),
            "char_seren": SimulationKnowledgeState(entity_id="char_seren"),
        },
        dependency_contract=dependency_contract,
        quality_scores={"deep_story_readiness": 0.96},
    )

    assert state.simulation_id.startswith("sim_")
    assert state.status == SimulationStatus.READY
    assert len(state.character_states) == 2
    assert len(state.relationship_states) == 1
    assert state.dependency_contract.readiness_level == SimulationReadinessLevel.VERIFIED
    assert state.quality_scores["deep_story_readiness"] == 0.96


def test_simulation_run_result_validates():
    event = SimulationEventPayload(event_type=SimulationEventType.BLACKMAIL_ATTEMPT)
    tick = SimulationTick(
        simulation_id="sim_001",
        tick_number=1,
        event_payload=event,
        produced_delta_ids=["delta_blackmail_pressure"],
        anti_genericity_flags=[],
        quality_scores={"agency_validity": 0.9},
    )

    result = SimulationRunResult(
        simulation_id="sim_001",
        success=True,
        status=SimulationStatus.COMPLETED,
        tick_results=[tick],
        quality_scores={"overall": 0.9},
        warnings=[],
        errors=[],
    )

    assert result.run_result_id.startswith("simrun_")
    assert result.success is True
    assert result.status == SimulationStatus.COMPLETED
    assert result.tick_results[0].event_payload.event_type == SimulationEventType.BLACKMAIL_ATTEMPT

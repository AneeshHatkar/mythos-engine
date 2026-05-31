from backend.app.schemas.global_refs import CanonStatus
from backend.app.schemas.simulation import (
    BackstoryDelta,
    BackstoryStatus,
    CanonDelta,
    CastScalingDelta,
    CastScalingPolicy,
    CharacterBackstoryPolicy,
    CharacterDestinyStatus,
    CharacterImportanceLevel,
    CharacterSourceType,
    ConsequenceDelta,
    DeltaBatch,
    DeltaOperation,
    DeltaScope,
    DeltaStatus,
    EmotionDelta,
    KnowledgeDelta,
    MemoryDelta,
    RelationshipDelta,
    SimulationEventVisibility,
    StateDelta,
    TensionDelta,
)


def test_base_state_delta_validates():
    delta = StateDelta(
        simulation_id="sim_001",
        source_engine="simulation.test_engine",
        delta_scope=DeltaScope.CHARACTER,
        operation=DeltaOperation.SET,
        target_entity_id="char_kael",
        target_path="current_agency_state.agency_capacity",
        before_value=0.72,
        after_value=0.61,
        reason="Public humiliation reduces agency capacity temporarily.",
        required_validator_names=["character_consistency", "canon_lock"],
        status=DeltaStatus.PROPOSED,
        canon_sensitive=False,
    )

    assert delta.delta_id.startswith("delta_")
    assert delta.delta_scope == DeltaScope.CHARACTER
    assert delta.operation == DeltaOperation.SET
    assert delta.status == DeltaStatus.PROPOSED
    assert delta.after_value == 0.61


def test_relationship_delta_tracks_multidimensional_edge_changes():
    delta = RelationshipDelta(
        simulation_id="sim_001",
        source_engine="simulation.relationship_graph_engine",
        operation=DeltaOperation.INCREMENT,
        target_entity_id="rel_kael_seren",
        target_path="relationship_states.rel_kael_seren",
        character_a_id="char_kael",
        character_b_id="char_seren",
        trust_delta=-0.12,
        respect_delta=0.08,
        romantic_tension_delta=0.04,
        rivalry_delta=0.1,
        betrayal_risk_delta=0.05,
        relationship_event_label="public defense with hidden cost",
    )

    assert delta.delta_scope == DeltaScope.RELATIONSHIP
    assert delta.trust_delta == -0.12
    assert delta.respect_delta == 0.08
    assert delta.relationship_event_label


def test_knowledge_delta_requires_no_magic_knowledge_tracking():
    delta = KnowledgeDelta(
        simulation_id="sim_001",
        source_engine="simulation.knowledge_secret_engine",
        operation=DeltaOperation.APPEND,
        target_entity_id="char_kael",
        target_path="knowledge_states.char_kael",
        knowledge_holder_id="char_kael",
        secret_ids_added=["secret_rank_system_edited"],
        evidence_ids_seen=["evidence_cracked_badge"],
        knowledge_path=["witnessed_evidence", "read_document"],
        witness_ids=["char_seren"],
        no_magic_knowledge_checked=True,
    )

    assert delta.delta_scope == DeltaScope.KNOWLEDGE
    assert delta.secret_ids_added == ["secret_rank_system_edited"]
    assert delta.evidence_ids_seen == ["evidence_cracked_badge"]
    assert delta.no_magic_knowledge_checked is True


def test_emotion_and_memory_deltas_support_backstory_and_carryover():
    emotion = EmotionDelta(
        simulation_id="sim_001",
        source_engine="simulation.emotional_carryover_engine",
        operation=DeltaOperation.MERGE,
        target_entity_id="char_kael",
        target_path="character_states.char_kael.current_emotion_state",
        character_id="char_kael",
        emotion_vector_delta={"shame": 0.34, "anger": 0.18},
        dominant_emotion_after="shame",
        triggered_wound="belonging can be revoked publicly",
    )

    memory = MemoryDelta(
        simulation_id="sim_001",
        source_engine="simulation.emotional_carryover_engine",
        operation=DeltaOperation.APPEND,
        target_entity_id="char_kael",
        target_path="character_states.char_kael.current_memory_state",
        character_id="char_kael",
        memory_ids_added=["mem_public_ranking_humiliation"],
        trigger_tags_added=["public ranking", "laughter", "status threat"],
        dialogue_constraints_added=["avoids admitting shame directly"],
        future_agency_modifiers={"status_sensitivity": 0.7},
    )

    assert emotion.delta_scope == DeltaScope.EMOTION
    assert emotion.emotion_vector_delta["shame"] == 0.34
    assert memory.delta_scope == DeltaScope.MEMORY
    assert memory.memory_ids_added == ["mem_public_ranking_humiliation"]
    assert memory.future_agency_modifiers["status_sensitivity"] == 0.7


def test_consequence_delta_models_delayed_consequence_payload():
    delta = ConsequenceDelta(
        simulation_id="sim_001",
        source_engine="simulation.consequence_queue_engine",
        operation=DeltaOperation.SCHEDULE,
        target_entity_id="char_kael",
        target_path="active_consequence_ids",
        consequence_type="delayed_reputation_collapse",
        target_entity_ids=["char_kael", "faction_oath_court"],
        trigger_event_id="evt_public_humiliation",
        delay_type="activation_condition",
        activation_condition="rumor reaches court audience",
        severity_level=0.8,
        visibility=SimulationEventVisibility.PUBLIC,
        state_delta_payload={"reputation_delta": -0.25, "legal_risk_delta": 0.15},
    )

    assert delta.delta_scope == DeltaScope.CONSEQUENCE
    assert delta.operation == DeltaOperation.SCHEDULE
    assert delta.activation_condition == "rumor reaches court audience"
    assert delta.state_delta_payload["reputation_delta"] == -0.25


def test_cast_scaling_policy_has_no_fixed_character_or_destiny_limit():
    policy = CastScalingPolicy(
        user_requested_character_count=117,
        generated_character_count=100,
        manual_character_count=17,
        imported_character_count=0,
        total_active_character_count=117,
        main_cast_count=13,
        recurring_side_character_count=34,
        background_character_count=70,
        destined_character_count=27,
        false_destined_character_count=8,
        hidden_destined_character_count=5,
        character_type_counts={
            "user_created": 17,
            "project_generated": 100,
            "destined": 27,
            "normal": 90,
        },
        scale_warnings=["relationship_graph_too_dense_without_depth_filtering"],
    )

    assert policy.no_fixed_cast_limit is True
    assert policy.no_fixed_destiny_limit is True
    assert policy.total_active_character_count == 117
    assert policy.destined_character_count == 27
    assert "relationship_graph_too_dense_without_depth_filtering" in policy.scale_warnings


def test_character_backstory_policy_supports_scalable_depth():
    policy = CharacterBackstoryPolicy(
        character_id="char_kael",
        source_type=CharacterSourceType.USER_CREATED,
        importance_level=CharacterImportanceLevel.CORE_CHARACTER,
        destiny_status=CharacterDestinyStatus.HIDDEN_DESTINED,
        backstory_status=BackstoryStatus.DEEP,
        expandable_character=True,
        required_backstory_fields=[
            "origin",
            "family_pressure",
            "core_wound",
            "formative_memories",
            "world_pressure",
        ],
        formative_memory_ids=["mem_public_failure"],
        origin_summary="Lower-class academy-sponsored student with distrusted family-name status.",
    )

    assert policy.source_type == CharacterSourceType.USER_CREATED
    assert policy.importance_level == CharacterImportanceLevel.CORE_CHARACTER
    assert policy.destiny_status == CharacterDestinyStatus.HIDDEN_DESTINED
    assert policy.backstory_status == BackstoryStatus.DEEP
    assert policy.expandable_character is True


def test_cast_scaling_delta_and_backstory_delta_validate_project_wide_rule():
    cast_policy = CastScalingPolicy(
        generated_character_count=300,
        manual_character_count=2,
        total_active_character_count=302,
        main_cast_count=11,
        background_character_count=291,
        destined_character_count=19,
        scale_warnings=["main_cast_focus_needed"],
    )

    cast_delta = CastScalingDelta(
        simulation_id="sim_001",
        source_engine="simulation.cast_scaling_policy_engine",
        operation=DeltaOperation.MERGE,
        target_entity_id="sim_001",
        target_path="metadata.cast_scaling_policy",
        cast_scaling_policy_after=cast_policy,
        character_ids_added=["char_user_001", "char_generated_001"],
        main_cast_ids_added=["char_user_001"],
        destiny_count_changes={"destined": 19},
        scale_warning_flags=["main_cast_focus_needed"],
    )

    backstory_policy = CharacterBackstoryPolicy(
        character_id="char_generated_001",
        source_type=CharacterSourceType.PROJECT_GENERATED,
        importance_level=CharacterImportanceLevel.SIDE_CHARACTER,
        destiny_status=CharacterDestinyStatus.NONE,
        backstory_status=BackstoryStatus.PARTIAL,
        expandable_character=True,
    )

    backstory_delta = BackstoryDelta(
        simulation_id="sim_001",
        source_engine="simulation.backstory_expansion_engine",
        operation=DeltaOperation.MERGE,
        target_entity_id="char_generated_001",
        target_path="character_states.char_generated_001.metadata.backstory_policy",
        character_id="char_generated_001",
        backstory_policy_after=backstory_policy,
        backstory_fields_added={"origin": "Outer district courier with academy access debt."},
        formative_memory_ids_added=["mem_first_failed_delivery"],
        expansion_triggered=True,
    )

    assert cast_delta.delta_scope == DeltaScope.CAST_SCALING
    assert cast_delta.cast_scaling_policy_after.total_active_character_count == 302
    assert cast_delta.cast_scaling_policy_after.no_fixed_cast_limit is True
    assert backstory_delta.delta_scope == DeltaScope.BACKSTORY
    assert backstory_delta.backstory_policy_after.expandable_character is True
    assert backstory_delta.expansion_triggered is True


def test_canon_tension_and_delta_batch_validate():
    canon = CanonDelta(
        simulation_id="sim_001",
        source_engine="simulation.canon_branch_timeline_validator",
        operation=DeltaOperation.SET,
        target_entity_id="secret_rank_system_edited",
        target_path="canon_status",
        canon_status_before=CanonStatus.DRAFT,
        canon_status_after=CanonStatus.CANON,
        lock_ids_affected=["lock_secret_rank"],
        canon_change_summary="Secret promoted to canon after trial reveal.",
    )

    tension = TensionDelta(
        simulation_id="sim_001",
        source_engine="simulation.tension_curve_engine",
        operation=DeltaOperation.INCREMENT,
        target_entity_id="sim_001",
        target_path="quality_scores.tension",
        romantic_tension_delta=0.12,
        mystery_tension_delta=0.22,
        dread_delta=0.16,
        hope_delta=0.08,
    )

    batch = DeltaBatch(
        simulation_id="sim_001",
        tick_id="tick_001",
        source_event_id="evt_trial_reveal",
        source_engine="simulation.test_pipeline",
        canon_deltas=[canon],
        tension_deltas=[tension],
        application_order=[canon.delta_id, tension.delta_id],
    )

    assert canon.delta_scope == DeltaScope.CANON
    assert canon.canon_status_after == CanonStatus.CANON
    assert tension.delta_scope == DeltaScope.TENSION
    assert batch.batch_id.startswith("deltabatch_")
    assert batch.validation_required is True
    assert batch.application_order == [canon.delta_id, tension.delta_id]

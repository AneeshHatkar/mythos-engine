from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import uuid4

from pydantic import BaseModel, Field

from backend.app.schemas.global_refs import (
    ArtifactRef,
    BranchRef,
    CanonStatus,
    EntityRef,
    ProjectUniverseRef,
    StateSnapshotRef,
    TimelineRef,
)
from backend.app.schemas.handoffs import CrossChunkHandoffContract


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class SimulationStatus(str, Enum):
    CREATED = "created"
    READY = "ready"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"


class SimulationEntityKind(str, Enum):
    WORLD = "world"
    CHARACTER = "character"
    FACTION = "faction"
    LOCATION = "location"
    OBJECT = "object"
    RELATIONSHIP = "relationship"
    SECRET = "secret"
    EVIDENCE = "evidence"
    PROMISE = "promise"
    OATH = "oath"
    DEBT = "debt"
    EVENT = "event"


class SimulationEventVisibility(str, Enum):
    PRIVATE = "private"
    WITNESSED = "witnessed"
    PUBLIC = "public"
    FACTION_KNOWN = "faction_known"
    READER_ONLY = "reader_only"
    HIDDEN = "hidden"


class SimulationEventType(str, Enum):
    PRIVATE_CONFESSION = "private_confession"
    PUBLIC_HUMILIATION = "public_humiliation"
    SECRET_DISCOVERY = "secret_discovery"
    RUMOR_SPREAD = "rumor_spread"
    PROMISE_MADE = "promise_made"
    PROMISE_BROKEN = "promise_broken"
    BETRAYAL = "betrayal"
    NEGOTIATION_OFFER = "negotiation_offer"
    SOCIAL_DUEL = "social_duel"
    PHYSICAL_DUEL = "physical_duel"
    TRIAL = "trial"
    RESCUE = "rescue"
    SACRIFICE = "sacrifice"
    BLACKMAIL_ATTEMPT = "blackmail_attempt"
    FACTION_ORDER = "faction_order"
    ROMANTIC_BOUNDARY_CROSSING = "romantic_boundary_crossing"
    CUSTOM = "custom"


class SimulationReadinessLevel(str, Enum):
    NOT_READY = "not_ready"
    PARTIAL = "partial"
    READY = "ready"
    VERIFIED = "verified"


class SimulationEntityState(BaseModel):
    entity_ref: EntityRef
    entity_kind: SimulationEntityKind
    active: bool = True
    current_location_id: Optional[str] = None
    public_visibility: SimulationEventVisibility = SimulationEventVisibility.PRIVATE
    state_values: Dict[str, Any] = Field(default_factory=dict)
    locked_fields: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    updated_at: str = Field(default_factory=utc_now)


class SimulationWorldState(BaseModel):
    world_id: str
    world_name: Optional[str] = None
    world_ref: Optional[EntityRef] = None
    world_contract: Dict[str, Any] = Field(default_factory=dict)
    world_simulation_constraints: Dict[str, Any] = Field(default_factory=dict)
    active_laws: List[Dict[str, Any]] = Field(default_factory=list)
    active_factions: List[Dict[str, Any]] = Field(default_factory=list)
    active_locations: List[Dict[str, Any]] = Field(default_factory=list)
    active_resources: List[Dict[str, Any]] = Field(default_factory=list)
    location_access_rules: List[Dict[str, Any]] = Field(default_factory=list)
    faction_resource_rules: List[Dict[str, Any]] = Field(default_factory=list)
    world_pressure_matrix: Dict[str, Any] = Field(default_factory=dict)
    canon_status: CanonStatus = CanonStatus.DRAFT
    metadata: Dict[str, Any] = Field(default_factory=dict)


class SimulationCharacterState(BaseModel):
    character_id: str
    character_ref: Optional[EntityRef] = None
    stable_profile_ref: Optional[ArtifactRef] = None
    current_location_id: Optional[str] = None
    current_emotion_state: Dict[str, Any] = Field(default_factory=dict)
    current_memory_state: Dict[str, Any] = Field(default_factory=dict)
    current_agency_state: Dict[str, Any] = Field(default_factory=dict)
    current_relationship_state: Dict[str, Any] = Field(default_factory=dict)
    current_knowledge_state: Dict[str, Any] = Field(default_factory=dict)
    current_goal_pressure: Dict[str, Any] = Field(default_factory=dict)
    dialogue_constraint_seed: Dict[str, Any] = Field(default_factory=dict)
    relationship_state_seed: Dict[str, Any] = Field(default_factory=dict)
    character_to_simulation_contract: Dict[str, Any] = Field(default_factory=dict)
    mutable_state_snapshot_ids: List[str] = Field(default_factory=list)
    canon_status: CanonStatus = CanonStatus.DRAFT
    metadata: Dict[str, Any] = Field(default_factory=dict)


class SimulationRelationshipState(BaseModel):
    relationship_id: str = Field(default_factory=lambda: f"rel_{uuid4().hex[:12]}")
    character_a_id: str
    character_b_id: str
    relationship_type: str = "undefined"
    trust: float = 0.0
    affection: float = 0.0
    respect: float = 0.0
    fear: float = 0.0
    envy: float = 0.0
    loyalty: float = 0.0
    debt: float = 0.0
    resentment: float = 0.0
    romantic_tension: float = 0.0
    rivalry: float = 0.0
    dependency: float = 0.0
    power_imbalance: float = 0.0
    knowledge_asymmetry: float = 0.0
    public_alignment: float = 0.0
    private_alignment: float = 0.0
    repair_potential: float = 0.0
    betrayal_risk: float = 0.0
    active_oath_ids: List[str] = Field(default_factory=list)
    active_debt_ids: List[str] = Field(default_factory=list)
    active_promise_ids: List[str] = Field(default_factory=list)
    relationship_memory_ids: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class SimulationKnowledgeState(BaseModel):
    knowledge_id: str = Field(default_factory=lambda: f"knowledge_{uuid4().hex[:12]}")
    entity_id: str
    known_secret_ids: List[str] = Field(default_factory=list)
    suspected_secret_ids: List[str] = Field(default_factory=list)
    believed_falsehood_ids: List[str] = Field(default_factory=list)
    evidence_seen_ids: List[str] = Field(default_factory=list)
    rumors_heard_ids: List[str] = Field(default_factory=list)
    reader_only_knowledge_ids: List[str] = Field(default_factory=list)
    public_knowledge_ids: List[str] = Field(default_factory=list)
    faction_knowledge_ids: List[str] = Field(default_factory=list)
    knowledge_confidence: Dict[str, float] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class SimulationEventPayload(BaseModel):
    event_id: str = Field(default_factory=lambda: f"evt_{uuid4().hex[:12]}")
    event_type: SimulationEventType = SimulationEventType.CUSTOM
    event_name: str = "untitled_event"
    description: str = ""
    actor_ids: List[str] = Field(default_factory=list)
    target_ids: List[str] = Field(default_factory=list)
    location_id: Optional[str] = None
    visibility: SimulationEventVisibility = SimulationEventVisibility.PRIVATE
    witness_ids: List[str] = Field(default_factory=list)
    involved_faction_ids: List[str] = Field(default_factory=list)
    involved_object_ids: List[str] = Field(default_factory=list)
    prerequisite_event_ids: List[str] = Field(default_factory=list)
    intensity: float = 0.5
    stakes_tags: List[str] = Field(default_factory=list)
    theme_tags: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: str = Field(default_factory=utc_now)


class SimulationAuditTrace(BaseModel):
    audit_id: str = Field(default_factory=lambda: f"simaudit_{uuid4().hex[:12]}")
    simulation_id: str
    tick_id: Optional[str] = None
    engine_name: str
    input_refs: List[str] = Field(default_factory=list)
    output_refs: List[str] = Field(default_factory=list)
    decisions: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)
    metrics: Dict[str, Any] = Field(default_factory=dict)
    created_at: str = Field(default_factory=utc_now)


class SimulationTick(BaseModel):
    tick_id: str = Field(default_factory=lambda: f"tick_{uuid4().hex[:12]}")
    simulation_id: str
    tick_number: int = 0
    event_payload: Optional[SimulationEventPayload] = None
    produced_delta_ids: List[str] = Field(default_factory=list)
    applied_delta_ids: List[str] = Field(default_factory=list)
    scheduled_consequence_ids: List[str] = Field(default_factory=list)
    triggered_consequence_ids: List[str] = Field(default_factory=list)
    causal_chain_ids: List[str] = Field(default_factory=list)
    quality_scores: Dict[str, float] = Field(default_factory=dict)
    anti_genericity_flags: List[str] = Field(default_factory=list)
    audit_trace_ids: List[str] = Field(default_factory=list)
    state_snapshot_id_before: Optional[str] = None
    state_snapshot_id_after: Optional[str] = None
    created_at: str = Field(default_factory=utc_now)


class SimulationTimeline(BaseModel):
    timeline_id: str = Field(default_factory=lambda: f"simtimeline_{uuid4().hex[:12]}")
    project_ref: ProjectUniverseRef = Field(default_factory=ProjectUniverseRef)
    base_timeline_ref: TimelineRef = Field(default_factory=TimelineRef)
    tick_order: List[str] = Field(default_factory=list)
    event_order: List[str] = Field(default_factory=list)
    branch_ids: List[str] = Field(default_factory=list)
    current_tick_number: int = 0
    current_event_id: Optional[str] = None
    timeline_hash: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class SimulationBranch(BaseModel):
    branch_id: str = Field(default_factory=lambda: f"simbranch_{uuid4().hex[:12]}")
    branch_ref: BranchRef = Field(default_factory=BranchRef)
    source_tick_id: Optional[str] = None
    source_event_id: Optional[str] = None
    branch_reason: str = ""
    chosen_choice_id: Optional[str] = None
    rejected_choice_ids: List[str] = Field(default_factory=list)
    canon_status: CanonStatus = CanonStatus.DRAFT
    state_snapshot_id: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class SimulationDependencyContract(BaseModel):
    contract_id: str = Field(default_factory=lambda: f"simcontract_{uuid4().hex[:12]}")
    project_ref: ProjectUniverseRef = Field(default_factory=ProjectUniverseRef)
    source_handoff_contracts: List[CrossChunkHandoffContract] = Field(default_factory=list)
    world_contract: Dict[str, Any] = Field(default_factory=dict)
    world_simulation_constraints: Dict[str, Any] = Field(default_factory=dict)
    character_simulation_contracts: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    story_dna_seed: Dict[str, Any] = Field(default_factory=dict)
    emotional_resonance_seed: Dict[str, Any] = Field(default_factory=dict)
    character_contrast_matrix: Dict[str, Any] = Field(default_factory=dict)
    world_character_pressure_matrix: Dict[str, Any] = Field(default_factory=dict)
    required_invariants: List[str] = Field(default_factory=list)
    readiness_level: SimulationReadinessLevel = SimulationReadinessLevel.NOT_READY
    readiness_score: float = 0.0
    blockers: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    created_at: str = Field(default_factory=utc_now)


class SimulationState(BaseModel):
    simulation_id: str = Field(default_factory=lambda: f"sim_{uuid4().hex[:12]}")
    project_ref: ProjectUniverseRef = Field(default_factory=ProjectUniverseRef)
    status: SimulationStatus = SimulationStatus.CREATED
    world_state: SimulationWorldState
    character_states: Dict[str, SimulationCharacterState] = Field(default_factory=dict)
    entity_states: Dict[str, SimulationEntityState] = Field(default_factory=dict)
    relationship_states: Dict[str, SimulationRelationshipState] = Field(default_factory=dict)
    knowledge_states: Dict[str, SimulationKnowledgeState] = Field(default_factory=dict)
    dependency_contract: Optional[SimulationDependencyContract] = None
    timeline: SimulationTimeline = Field(default_factory=SimulationTimeline)
    branches: Dict[str, SimulationBranch] = Field(default_factory=dict)
    ticks: List[SimulationTick] = Field(default_factory=list)
    active_consequence_ids: List[str] = Field(default_factory=list)
    causal_chain_ids: List[str] = Field(default_factory=list)
    artifact_refs: List[ArtifactRef] = Field(default_factory=list)
    provenance_ids: List[str] = Field(default_factory=list)
    learning_metadata_ids: List[str] = Field(default_factory=list)
    embedding_ids: List[str] = Field(default_factory=list)
    training_queue_ids: List[str] = Field(default_factory=list)
    snapshot_refs: List[StateSnapshotRef] = Field(default_factory=list)
    audit_trace_ids: List[str] = Field(default_factory=list)
    quality_scores: Dict[str, float] = Field(default_factory=dict)
    anti_genericity_flags: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: str = Field(default_factory=utc_now)
    updated_at: str = Field(default_factory=utc_now)


class SimulationRunResult(BaseModel):
    run_result_id: str = Field(default_factory=lambda: f"simrun_{uuid4().hex[:12]}")
    simulation_id: str
    success: bool
    status: SimulationStatus
    tick_results: List[SimulationTick] = Field(default_factory=list)
    final_state_snapshot_id: Optional[str] = None
    produced_artifact_refs: List[ArtifactRef] = Field(default_factory=list)
    audit_traces: List[SimulationAuditTrace] = Field(default_factory=list)
    quality_scores: Dict[str, float] = Field(default_factory=dict)
    anti_genericity_flags: List[str] = Field(default_factory=list)
    learning_metadata_ids: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)
    created_at: str = Field(default_factory=utc_now)



# ---------------------------------------------------------------------------
# Chunk 4.2 — State Delta Models
# ---------------------------------------------------------------------------

class DeltaStatus(str, Enum):
    PROPOSED = "proposed"
    VALIDATED = "validated"
    APPLIED = "applied"
    REJECTED = "rejected"
    SUPERSEDED = "superseded"


class DeltaScope(str, Enum):
    WORLD = "world"
    CHARACTER = "character"
    RELATIONSHIP = "relationship"
    KNOWLEDGE = "knowledge"
    EMOTION = "emotion"
    MEMORY = "memory"
    REPUTATION = "reputation"
    FACTION = "faction"
    RESOURCE = "resource"
    LEGAL = "legal"
    TENSION = "tension"
    STAKES = "stakes"
    CANON = "canon"
    TIMELINE = "timeline"
    CONSEQUENCE = "consequence"
    CAST_SCALING = "cast_scaling"
    BACKSTORY = "backstory"


class DeltaOperation(str, Enum):
    SET = "set"
    INCREMENT = "increment"
    DECREMENT = "decrement"
    APPEND = "append"
    REMOVE = "remove"
    MERGE = "merge"
    LOCK = "lock"
    UNLOCK = "unlock"
    CREATE = "create"
    DELETE = "delete"
    SCHEDULE = "schedule"
    CANCEL = "cancel"


class CharacterSourceType(str, Enum):
    USER_CREATED = "user_created"
    PROJECT_GENERATED = "project_generated"
    IMPORTED = "imported"
    MIXED = "mixed"
    UNKNOWN = "unknown"


class CharacterImportanceLevel(str, Enum):
    STATISTICAL_BACKGROUND = "statistical_background"
    NAMED_BACKGROUND = "named_background"
    SIDE_CHARACTER = "side_character"
    MAJOR_CHARACTER = "major_character"
    CORE_CHARACTER = "core_character"
    FRANCHISE_PILLAR = "franchise_pillar"


class CharacterDestinyStatus(str, Enum):
    NONE = "none"
    DESTINED = "destined"
    HIDDEN_DESTINED = "hidden_destined"
    FALSE_DESTINED = "false_destined"
    FAILED_DESTINED = "failed_destined"
    CORRUPTED_DESTINED = "corrupted_destined"
    SHARED_DESTINED = "shared_destined"
    USER_DEFINED = "user_defined"


class BackstoryStatus(str, Enum):
    NONE = "none"
    COMPACT = "compact"
    PARTIAL = "partial"
    FULL = "full"
    DEEP = "deep"
    FRANCHISE_LEVEL = "franchise_level"
    NEEDS_EXPANSION = "needs_expansion"


class CastScalingPolicy(BaseModel):
    """Project-wide cast scaling policy.

    MythOS must not hardcode fixed character counts or fixed destiny splits.
    These values are descriptive and validator-guided, not hard limits.
    """

    policy_id: str = Field(default_factory=lambda: f"castpolicy_{uuid4().hex[:12]}")
    user_requested_character_count: Optional[int] = None
    generated_character_count: int = 0
    manual_character_count: int = 0
    imported_character_count: int = 0
    total_active_character_count: int = 0
    main_cast_count: int = 0
    recurring_side_character_count: int = 0
    background_character_count: int = 0
    destined_character_count: int = 0
    false_destined_character_count: int = 0
    hidden_destined_character_count: int = 0
    failed_destined_character_count: int = 0
    character_type_counts: Dict[str, int] = Field(default_factory=dict)
    max_depth_level_by_group: Dict[str, CharacterImportanceLevel] = Field(default_factory=dict)
    scale_warnings: List[str] = Field(default_factory=list)
    hard_constraints: List[str] = Field(default_factory=list)
    user_can_override_warnings: bool = True
    no_fixed_cast_limit: bool = True
    no_fixed_destiny_limit: bool = True
    created_at: str = Field(default_factory=utc_now)


class CharacterBackstoryPolicy(BaseModel):
    character_id: str
    source_type: CharacterSourceType = CharacterSourceType.UNKNOWN
    importance_level: CharacterImportanceLevel = CharacterImportanceLevel.NAMED_BACKGROUND
    destiny_status: CharacterDestinyStatus = CharacterDestinyStatus.NONE
    backstory_status: BackstoryStatus = BackstoryStatus.COMPACT
    expandable_character: bool = True
    user_locked_backstory: bool = False
    required_backstory_fields: List[str] = Field(default_factory=list)
    missing_backstory_fields: List[str] = Field(default_factory=list)
    backstory_artifact_ids: List[str] = Field(default_factory=list)
    origin_summary: Optional[str] = None
    formative_memory_ids: List[str] = Field(default_factory=list)
    family_pressure_refs: List[str] = Field(default_factory=list)
    world_pressure_refs: List[str] = Field(default_factory=list)
    expansion_recommendations: List[str] = Field(default_factory=list)


class StateDelta(BaseModel):
    delta_id: str = Field(default_factory=lambda: f"delta_{uuid4().hex[:12]}")
    simulation_id: str
    tick_id: Optional[str] = None
    source_event_id: Optional[str] = None
    source_engine: str
    delta_scope: DeltaScope
    operation: DeltaOperation
    target_entity_id: str
    target_path: str
    before_value: Any = None
    after_value: Any = None
    delta_value: Any = None
    reason: str = ""
    causal_parent_ids: List[str] = Field(default_factory=list)
    consequence_child_ids: List[str] = Field(default_factory=list)
    required_validator_names: List[str] = Field(default_factory=list)
    status: DeltaStatus = DeltaStatus.PROPOSED
    confidence: float = 1.0
    severity: float = 0.0
    reversible: bool = True
    canon_sensitive: bool = False
    requires_human_review: bool = False
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: str = Field(default_factory=utc_now)


class RelationshipDelta(StateDelta):
    delta_scope: DeltaScope = DeltaScope.RELATIONSHIP
    character_a_id: str
    character_b_id: str
    relationship_id: Optional[str] = None
    trust_delta: float = 0.0
    affection_delta: float = 0.0
    respect_delta: float = 0.0
    fear_delta: float = 0.0
    envy_delta: float = 0.0
    loyalty_delta: float = 0.0
    debt_delta: float = 0.0
    resentment_delta: float = 0.0
    romantic_tension_delta: float = 0.0
    rivalry_delta: float = 0.0
    dependency_delta: float = 0.0
    power_imbalance_delta: float = 0.0
    knowledge_asymmetry_delta: float = 0.0
    repair_potential_delta: float = 0.0
    betrayal_risk_delta: float = 0.0
    relationship_event_label: str = ""


class KnowledgeDelta(StateDelta):
    delta_scope: DeltaScope = DeltaScope.KNOWLEDGE
    knowledge_holder_id: str
    secret_ids_added: List[str] = Field(default_factory=list)
    secret_ids_removed: List[str] = Field(default_factory=list)
    suspected_secret_ids_added: List[str] = Field(default_factory=list)
    evidence_ids_seen: List[str] = Field(default_factory=list)
    rumor_ids_heard: List[str] = Field(default_factory=list)
    falsehood_ids_believed: List[str] = Field(default_factory=list)
    knowledge_confidence_updates: Dict[str, float] = Field(default_factory=dict)
    knowledge_path: List[str] = Field(default_factory=list)
    witness_ids: List[str] = Field(default_factory=list)
    no_magic_knowledge_checked: bool = False


class EmotionDelta(StateDelta):
    delta_scope: DeltaScope = DeltaScope.EMOTION
    character_id: str
    emotion_vector_delta: Dict[str, float] = Field(default_factory=dict)
    dominant_emotion_after: Optional[str] = None
    suppressed_emotion_after: Optional[str] = None
    triggered_wound: Optional[str] = None
    emotional_mask_after: Optional[str] = None
    decay_rate_updates: Dict[str, float] = Field(default_factory=dict)
    relationship_specific_leaks: Dict[str, Any] = Field(default_factory=dict)


class MemoryDelta(StateDelta):
    delta_scope: DeltaScope = DeltaScope.MEMORY
    character_id: str
    memory_ids_added: List[str] = Field(default_factory=list)
    memory_ids_activated: List[str] = Field(default_factory=list)
    memory_ids_suppressed: List[str] = Field(default_factory=list)
    memory_records_added: List[Dict[str, Any]] = Field(default_factory=list)
    trigger_tags_added: List[str] = Field(default_factory=list)
    dialogue_constraints_added: List[str] = Field(default_factory=list)
    future_agency_modifiers: Dict[str, float] = Field(default_factory=dict)


class ReputationDelta(StateDelta):
    delta_scope: DeltaScope = DeltaScope.REPUTATION
    character_id: str
    audience_id: Optional[str] = None
    audience_type: str = "public"
    reputation_score_delta: float = 0.0
    fear_score_delta: float = 0.0
    respect_score_delta: float = 0.0
    trust_score_delta: float = 0.0
    rumor_ids_created: List[str] = Field(default_factory=list)
    rumor_ids_amplified: List[str] = Field(default_factory=list)
    public_visibility_required: bool = True


class FactionDelta(StateDelta):
    delta_scope: DeltaScope = DeltaScope.FACTION
    faction_id: str
    influence_delta: float = 0.0
    legitimacy_delta: float = 0.0
    hostility_delta: float = 0.0
    alliance_updates: Dict[str, Any] = Field(default_factory=dict)
    enforcement_action_ids: List[str] = Field(default_factory=list)


class ResourceDelta(StateDelta):
    delta_scope: DeltaScope = DeltaScope.RESOURCE
    resource_id: str
    quantity_delta: float = 0.0
    scarcity_delta: float = 0.0
    controller_before: Optional[str] = None
    controller_after: Optional[str] = None
    market_status_after: Optional[str] = None
    black_market_pressure_delta: float = 0.0


class LegalDelta(StateDelta):
    delta_scope: DeltaScope = DeltaScope.LEGAL
    law_id: Optional[str] = None
    target_character_id: Optional[str] = None
    legal_risk_delta: float = 0.0
    public_charge_ids_added: List[str] = Field(default_factory=list)
    evidence_required_ids: List[str] = Field(default_factory=list)
    sponsor_required: bool = False
    trial_triggered: bool = False


class TensionDelta(StateDelta):
    delta_scope: DeltaScope = DeltaScope.TENSION
    romantic_tension_delta: float = 0.0
    mystery_tension_delta: float = 0.0
    social_tension_delta: float = 0.0
    conflict_tension_delta: float = 0.0
    dread_delta: float = 0.0
    hope_delta: float = 0.0
    relief_delta: float = 0.0
    escalation_rate_delta: float = 0.0


class StakesDelta(StateDelta):
    delta_scope: DeltaScope = DeltaScope.STAKES
    identity_stakes_delta: float = 0.0
    relationship_stakes_delta: float = 0.0
    romantic_stakes_delta: float = 0.0
    legal_stakes_delta: float = 0.0
    life_death_stakes_delta: float = 0.0
    family_stakes_delta: float = 0.0
    class_status_stakes_delta: float = 0.0
    destiny_stakes_delta: float = 0.0
    resource_stakes_delta: float = 0.0
    faction_stakes_delta: float = 0.0
    world_order_stakes_delta: float = 0.0


class CanonDelta(StateDelta):
    delta_scope: DeltaScope = DeltaScope.CANON
    canon_status_before: Optional[CanonStatus] = None
    canon_status_after: Optional[CanonStatus] = None
    lock_ids_affected: List[str] = Field(default_factory=list)
    retcon_required: bool = False
    alternate_branch_recommended: bool = False
    canon_change_summary: str = ""


class TimelineDelta(StateDelta):
    delta_scope: DeltaScope = DeltaScope.TIMELINE
    timeline_id: Optional[str] = None
    branch_id: Optional[str] = None
    event_ids_added: List[str] = Field(default_factory=list)
    event_ids_reordered: List[str] = Field(default_factory=list)
    prerequisite_event_ids: List[str] = Field(default_factory=list)
    timeline_warning_flags: List[str] = Field(default_factory=list)


class ConsequenceDelta(StateDelta):
    delta_scope: DeltaScope = DeltaScope.CONSEQUENCE
    consequence_id: str = Field(default_factory=lambda: f"conseq_{uuid4().hex[:12]}")
    consequence_type: str = "generic_consequence"
    target_entity_ids: List[str] = Field(default_factory=list)
    trigger_event_id: Optional[str] = None
    delay_type: str = "immediate"
    activation_condition: Optional[str] = None
    severity_level: float = 0.5
    visibility: SimulationEventVisibility = SimulationEventVisibility.PRIVATE
    cancellation_conditions: List[str] = Field(default_factory=list)
    state_delta_payload: Dict[str, Any] = Field(default_factory=dict)


class CastScalingDelta(StateDelta):
    delta_scope: DeltaScope = DeltaScope.CAST_SCALING
    cast_scaling_policy_before: Optional[Dict[str, Any]] = None
    cast_scaling_policy_after: Optional[CastScalingPolicy] = None
    character_ids_added: List[str] = Field(default_factory=list)
    character_ids_removed: List[str] = Field(default_factory=list)
    main_cast_ids_added: List[str] = Field(default_factory=list)
    main_cast_ids_removed: List[str] = Field(default_factory=list)
    character_type_count_changes: Dict[str, int] = Field(default_factory=dict)
    destiny_count_changes: Dict[str, int] = Field(default_factory=dict)
    scale_warning_flags: List[str] = Field(default_factory=list)


class BackstoryDelta(StateDelta):
    delta_scope: DeltaScope = DeltaScope.BACKSTORY
    character_id: str
    backstory_policy_before: Optional[Dict[str, Any]] = None
    backstory_policy_after: Optional[CharacterBackstoryPolicy] = None
    backstory_fields_added: Dict[str, Any] = Field(default_factory=dict)
    formative_memory_ids_added: List[str] = Field(default_factory=list)
    origin_updated: bool = False
    family_pressure_updated: bool = False
    world_pressure_updated: bool = False
    expansion_triggered: bool = False


class DeltaBatch(BaseModel):
    batch_id: str = Field(default_factory=lambda: f"deltabatch_{uuid4().hex[:12]}")
    simulation_id: str
    tick_id: Optional[str] = None
    source_event_id: Optional[str] = None
    source_engine: str
    deltas: List[StateDelta] = Field(default_factory=list)
    relationship_deltas: List[RelationshipDelta] = Field(default_factory=list)
    knowledge_deltas: List[KnowledgeDelta] = Field(default_factory=list)
    emotion_deltas: List[EmotionDelta] = Field(default_factory=list)
    memory_deltas: List[MemoryDelta] = Field(default_factory=list)
    reputation_deltas: List[ReputationDelta] = Field(default_factory=list)
    faction_deltas: List[FactionDelta] = Field(default_factory=list)
    resource_deltas: List[ResourceDelta] = Field(default_factory=list)
    legal_deltas: List[LegalDelta] = Field(default_factory=list)
    tension_deltas: List[TensionDelta] = Field(default_factory=list)
    stakes_deltas: List[StakesDelta] = Field(default_factory=list)
    canon_deltas: List[CanonDelta] = Field(default_factory=list)
    timeline_deltas: List[TimelineDelta] = Field(default_factory=list)
    consequence_deltas: List[ConsequenceDelta] = Field(default_factory=list)
    cast_scaling_deltas: List[CastScalingDelta] = Field(default_factory=list)
    backstory_deltas: List[BackstoryDelta] = Field(default_factory=list)
    validation_required: bool = True
    application_order: List[str] = Field(default_factory=list)
    blockers: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    created_at: str = Field(default_factory=utc_now)


from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, field_validator


class PopulationGroup(BaseModel):
    group_id: str = Field(..., min_length=1)
    world_id: str = Field(..., min_length=1)
    group_name: str = Field(..., min_length=1)
    region: Optional[str] = None
    social_class: Optional[str] = None
    occupation_roles: List[str] = Field(default_factory=list)
    faction_affiliations: List[str] = Field(default_factory=list)
    estimated_count: int = Field(default=0, ge=0)
    percentage_of_population: float = Field(default=0.0, ge=0.0, le=100.0)
    education_access: float = Field(default=0.0, ge=0.0, le=1.0)
    wealth_access: float = Field(default=0.0, ge=0.0, le=1.0)
    legal_trust_level: float = Field(default=0.0, ge=0.0, le=1.0)
    danger_exposure: float = Field(default=0.0, ge=0.0, le=1.0)
    destiny_density: float = Field(default=0.0, ge=0.0, le=1.0)
    rare_skill_density: float = Field(default=0.0, ge=0.0, le=1.0)
    narrative_function: List[str] = Field(default_factory=list)


class PeopleTypeProfile(BaseModel):
    people_type_id: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1)
    category: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1)
    rarity: str = "common"
    compatible_roles: List[str] = Field(default_factory=list)
    compatible_classes: List[str] = Field(default_factory=list)
    compatible_destinies: List[str] = Field(default_factory=list)
    pressure_responses: List[str] = Field(default_factory=list)
    likely_wounds: List[str] = Field(default_factory=list)
    likely_goals: List[str] = Field(default_factory=list)
    relationship_tendencies: List[str] = Field(default_factory=list)
    corruption_risks: List[str] = Field(default_factory=list)
    growth_paths: List[str] = Field(default_factory=list)
    anti_cliche_notes: List[str] = Field(default_factory=list)


class CharacterIdentity(BaseModel):
    character_id: str = Field(..., min_length=1)
    project_id: str = Field(..., min_length=1)
    universe_id: str = Field(..., min_length=1)
    world_id: Optional[str] = None
    name: str = Field(..., min_length=1)
    aliases: List[str] = Field(default_factory=list)
    age: Optional[int] = Field(default=None, ge=0)
    role: str = Field(..., min_length=1)
    importance_level: int = Field(default=1, ge=0, le=5)
    character_depth_level: int = Field(default=1, ge=0, le=5)
    culture: Optional[str] = None
    language: Optional[str] = None
    faction: Optional[str] = None
    occupation: Optional[str] = None
    public_status: Optional[str] = None
    private_truth: Optional[str] = None
    legal_status: Optional[str] = None
    canon_status: str = "draft"
    tags: List[str] = Field(default_factory=list)


class OriginProfile(BaseModel):
    origin_id: str = Field(..., min_length=1)
    character_id: str = Field(..., min_length=1)
    birth_status: str = Field(..., min_length=1)
    social_class: str = Field(..., min_length=1)
    origin_location: Optional[str] = None
    family_name_trust: float = Field(default=0.0, ge=0.0, le=1.0)
    wealth_rank: float = Field(default=0.0, ge=0.0, le=1.0)
    education_access: float = Field(default=0.0, ge=0.0, le=1.0)
    institution_access: List[str] = Field(default_factory=list)
    forbidden_access: List[str] = Field(default_factory=list)
    resource_access: List[str] = Field(default_factory=list)
    inherited_privileges: List[str] = Field(default_factory=list)
    inherited_disadvantages: List[str] = Field(default_factory=list)
    class_wound: Optional[str] = None
    mobility_score: float = Field(default=0.0, ge=0.0, le=1.0)
    public_assumptions: List[str] = Field(default_factory=list)
    world_constraint_notes: List[str] = Field(default_factory=list)


class FamilyMember(BaseModel):
    name: str
    relation: str
    status: str = "unknown"
    emotional_closeness: float = Field(default=0.0, ge=-1.0, le=1.0)
    conflict_level: float = Field(default=0.0, ge=0.0, le=1.0)
    secret_link: Optional[str] = None


class FamilyProfile(BaseModel):
    family_id: str = Field(..., min_length=1)
    character_id: str = Field(..., min_length=1)
    family_name: Optional[str] = None
    family_status: str = "unknown"
    family_reputation: Optional[str] = None
    family_ideology: Optional[str] = None
    family_debt: List[str] = Field(default_factory=list)
    family_secrets: List[str] = Field(default_factory=list)
    inherited_trauma: List[str] = Field(default_factory=list)
    inherited_privilege: List[str] = Field(default_factory=list)
    inherited_obligations: List[str] = Field(default_factory=list)
    guardians: List[FamilyMember] = Field(default_factory=list)
    parents: List[FamilyMember] = Field(default_factory=list)
    siblings: List[FamilyMember] = Field(default_factory=list)
    other_relatives: List[FamilyMember] = Field(default_factory=list)
    family_allies: List[str] = Field(default_factory=list)
    family_enemies: List[str] = Field(default_factory=list)
    family_artifact_links: List[str] = Field(default_factory=list)


class PsychologyProfile(BaseModel):
    psychology_id: str = Field(..., min_length=1)
    character_id: str = Field(..., min_length=1)
    core_wound: str = Field(..., min_length=1)
    core_desire: str = Field(..., min_length=1)
    core_fear: str = Field(..., min_length=1)
    core_lie: str = Field(..., min_length=1)
    core_truth: str = Field(..., min_length=1)
    defense_mechanism: str = Field(..., min_length=1)
    attachment_tendency: Optional[str] = None
    shame_trigger: Optional[str] = None
    stress_response: Optional[str] = None
    love_response: Optional[str] = None
    betrayal_response: Optional[str] = None
    power_response: Optional[str] = None
    healing_condition: Optional[str] = None
    corruption_condition: Optional[str] = None
    contradiction_notes: List[str] = Field(default_factory=list)
    behavior_rules: List[str] = Field(default_factory=list)

    @field_validator("behavior_rules")
    @classmethod
    def major_psychology_needs_behavior_rules(cls, value: List[str]) -> List[str]:
        if len(value) == 0:
            raise ValueError("PsychologyProfile requires at least one behavior rule.")
        return value


class TraumaRecord(BaseModel):
    trauma_id: str = Field(..., min_length=1)
    character_id: str = Field(..., min_length=1)
    trauma_source: str = Field(..., min_length=1)
    trauma_intensity: float = Field(default=0.0, ge=0.0, le=1.0)
    trigger_events: List[str] = Field(default_factory=list)
    avoidance_behavior: Optional[str] = None
    coping_behavior: Optional[str] = None
    relapse_risk: float = Field(default=0.0, ge=0.0, le=1.0)
    healing_condition: Optional[str] = None
    healing_relationship: Optional[str] = None
    recovery_milestones: List[str] = Field(default_factory=list)
    setback_conditions: List[str] = Field(default_factory=list)
    content_safety_notes: List[str] = Field(default_factory=list)


class EmotionVector(BaseModel):
    anger: float = Field(default=0.0, ge=0.0, le=1.0)
    fear: float = Field(default=0.0, ge=0.0, le=1.0)
    hope: float = Field(default=0.0, ge=0.0, le=1.0)
    love: float = Field(default=0.0, ge=0.0, le=1.0)
    shame: float = Field(default=0.0, ge=0.0, le=1.0)
    grief: float = Field(default=0.0, ge=0.0, le=1.0)
    envy: float = Field(default=0.0, ge=0.0, le=1.0)
    pride: float = Field(default=0.0, ge=0.0, le=1.0)
    trust: float = Field(default=0.0, ge=0.0, le=1.0)
    loneliness: float = Field(default=0.0, ge=0.0, le=1.0)
    guilt: float = Field(default=0.0, ge=0.0, le=1.0)
    revenge: float = Field(default=0.0, ge=0.0, le=1.0)
    despair: float = Field(default=0.0, ge=0.0, le=1.0)
    purpose: float = Field(default=0.0, ge=0.0, le=1.0)
    obsession: float = Field(default=0.0, ge=0.0, le=1.0)
    peace: float = Field(default=0.0, ge=0.0, le=1.0)


class EmotionalStateProfile(BaseModel):
    emotional_state_id: str = Field(..., min_length=1)
    character_id: str = Field(..., min_length=1)
    baseline: EmotionVector = Field(default_factory=EmotionVector)
    current: EmotionVector = Field(default_factory=EmotionVector)
    volatility: float = Field(default=0.0, ge=0.0, le=1.0)
    recovery_rate: float = Field(default=0.0, ge=0.0, le=1.0)
    dominant_state: Optional[str] = None
    suppressed_emotions: List[str] = Field(default_factory=list)
    recent_emotion_deltas: List[Dict[str, Any]] = Field(default_factory=list)


class EmotionalArcProfile(BaseModel):
    emotional_arc_id: str = Field(..., min_length=1)
    character_id: str = Field(..., min_length=1)
    arc_type: str = Field(..., min_length=1)
    hope_curve: List[float] = Field(default_factory=list)
    despair_cycle: List[float] = Field(default_factory=list)
    romantic_tension_curve: List[float] = Field(default_factory=list)
    healing_milestones: List[str] = Field(default_factory=list)
    rage_escalation: List[float] = Field(default_factory=list)
    corruption_curve: List[float] = Field(default_factory=list)
    redemption_curve: List[float] = Field(default_factory=list)
    emotional_climax: Optional[str] = None
    emotional_resolution: Optional[str] = None
    open_wounds: List[str] = Field(default_factory=list)


class MemoryRecord(BaseModel):
    memory_id: str = Field(..., min_length=1)
    character_id: str = Field(..., min_length=1)
    event_id: Optional[str] = None
    content: str = Field(..., min_length=1)
    emotional_weight: float = Field(default=0.0, ge=0.0, le=1.0)
    reliability: float = Field(default=1.0, ge=0.0, le=1.0)
    trigger_terms: List[str] = Field(default_factory=list)
    related_people: List[str] = Field(default_factory=list)
    related_objects: List[str] = Field(default_factory=list)
    related_locations: List[str] = Field(default_factory=list)
    behavioral_influence: List[str] = Field(default_factory=list)
    decay_or_reinforcement: str = "stable"


class ReputationProfile(BaseModel):
    reputation_id: str = Field(..., min_length=1)
    character_id: str = Field(..., min_length=1)
    public_reputation: Optional[str] = None
    private_truth: Optional[str] = None
    family_reputation: Optional[str] = None
    faction_reputations: Dict[str, str] = Field(default_factory=dict)
    institution_reputations: Dict[str, str] = Field(default_factory=dict)
    romantic_interest_reputation: Optional[str] = None
    enemy_reputation: Optional[str] = None
    underground_reputation: Optional[str] = None
    rumors: List[str] = Field(default_factory=list)
    false_accusations: List[str] = Field(default_factory=list)
    witness_paths: List[str] = Field(default_factory=list)
    reputation_scores: Dict[str, float] = Field(default_factory=dict)


class GoalRecord(BaseModel):
    goal_id: str = Field(..., min_length=1)
    character_id: str = Field(..., min_length=1)
    goal_type: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1)
    priority: float = Field(default=0.5, ge=0.0, le=1.0)
    urgency: float = Field(default=0.5, ge=0.0, le=1.0)
    blocker: Optional[str] = None
    target: Optional[str] = None
    moral_cost: Optional[str] = None
    progress: float = Field(default=0.0, ge=0.0, le=1.0)
    failure_consequence: Optional[str] = None
    conflicts_with: List[str] = Field(default_factory=list)


class MoralProfile(BaseModel):
    moral_profile_id: str = Field(..., min_length=1)
    character_id: str = Field(..., min_length=1)
    compassion: float = Field(default=0.5, ge=0.0, le=1.0)
    justice: float = Field(default=0.5, ge=0.0, le=1.0)
    loyalty: float = Field(default=0.5, ge=0.0, le=1.0)
    honesty: float = Field(default=0.5, ge=0.0, le=1.0)
    mercy: float = Field(default=0.5, ge=0.0, le=1.0)
    ambition: float = Field(default=0.5, ge=0.0, le=1.0)
    revenge: float = Field(default=0.0, ge=0.0, le=1.0)
    cruelty: float = Field(default=0.0, ge=0.0, le=1.0)
    self_sacrifice: float = Field(default=0.5, ge=0.0, le=1.0)
    manipulation_tolerance: float = Field(default=0.0, ge=0.0, le=1.0)
    violence_tolerance: float = Field(default=0.0, ge=0.0, le=1.0)
    corruption_risk: float = Field(default=0.0, ge=0.0, le=1.0)
    redemption_potential: float = Field(default=0.5, ge=0.0, le=1.0)
    forbidden_lines: List[str] = Field(default_factory=list)
    broken_lines: List[str] = Field(default_factory=list)
    guilt_burden: List[str] = Field(default_factory=list)


class SkillProfile(BaseModel):
    skill_id: str = Field(..., min_length=1)
    character_id: str = Field(..., min_length=1)
    domain: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1)
    rank: str = Field(default="F")
    rarity: str = Field(default="common")
    mastery: float = Field(default=0.0, ge=0.0, le=1.0)
    cost: Optional[str] = None
    limitation: Optional[str] = None
    counter: Optional[str] = None
    training_needed: Optional[str] = None
    social_consequence: Optional[str] = None
    known_by_public: bool = False

    @field_validator("rank")
    @classmethod
    def rank_must_be_valid(cls, value: str) -> str:
        valid = {"F", "E", "D", "C", "B", "A", "S", "SS", "SSS", "Mythic", "Anomaly"}
        if value not in valid:
            raise ValueError(f"rank must be one of {sorted(valid)}")
        return value


class GrowthTrack(BaseModel):
    growth_id: str = Field(..., min_length=1)
    character_id: str = Field(..., min_length=1)
    domain: str = Field(..., min_length=1)
    current_level: float = Field(default=0.0, ge=0.0, le=1.0)
    target_level: float = Field(default=1.0, ge=0.0, le=1.0)
    milestones: List[str] = Field(default_factory=list)
    practice_time_required: Optional[str] = None
    mentor_access: Optional[str] = None
    plateaus: List[str] = Field(default_factory=list)
    breakthrough_conditions: List[str] = Field(default_factory=list)
    regression_conditions: List[str] = Field(default_factory=list)
    failure_records: List[str] = Field(default_factory=list)
    emotional_blockers: List[str] = Field(default_factory=list)


class AdaptabilityProfile(BaseModel):
    adaptability_id: str = Field(..., min_length=1)
    character_id: str = Field(..., min_length=1)
    adaptability_score: float = Field(default=0.0, ge=0.0, le=1.0)
    limit_break_potential: float = Field(default=0.0, ge=0.0, le=1.0)
    pressure_thresholds: Dict[str, float] = Field(default_factory=dict)
    breakthrough_conditions: List[str] = Field(default_factory=list)
    failure_conditions: List[str] = Field(default_factory=list)
    adaptation_domains: List[str] = Field(default_factory=list)
    cost_of_adaptation: List[str] = Field(default_factory=list)
    risk_of_instability: float = Field(default=0.0, ge=0.0, le=1.0)
    post_break_change: List[str] = Field(default_factory=list)
    regression_risk: float = Field(default=0.0, ge=0.0, le=1.0)
    world_rule_exception_tags: List[str] = Field(default_factory=list)
    destiny_amplifier: float = Field(default=0.0, ge=0.0, le=1.0)
    training_amplifier: float = Field(default=0.0, ge=0.0, le=1.0)
    trauma_amplifier: float = Field(default=0.0, ge=0.0, le=1.0)
    relationship_amplifier: float = Field(default=0.0, ge=0.0, le=1.0)
    limit_break_types: List[str] = Field(default_factory=list)

    @field_validator("breakthrough_conditions")
    @classmethod
    def limit_break_needs_condition(cls, value: List[str]) -> List[str]:
        if len(value) == 0:
            raise ValueError("AdaptabilityProfile requires at least one breakthrough condition.")
        return value


class DestinyProfile(BaseModel):
    destiny_id: str = Field(..., min_length=1)
    character_id: str = Field(..., min_length=1)
    destiny_type: str = Field(..., min_length=1)
    destiny_score: float = Field(default=0.0, ge=0.0, le=1.0)
    visibility: str = "hidden"
    trigger: Optional[str] = None
    burden: Optional[str] = None
    cost: Optional[str] = None
    rival: Optional[str] = None
    failure_condition: Optional[str] = None
    corruption_path: Optional[str] = None
    fulfillment_path: Optional[str] = None
    world_impact_potential: float = Field(default=0.0, ge=0.0, le=1.0)
    activation_status: str = "dormant"
    failed_destiny_outcomes: List[str] = Field(default_factory=list)


class ProphecyLink(BaseModel):
    prophecy_link_id: str = Field(..., min_length=1)
    character_id: str = Field(..., min_length=1)
    prophecy_id: str = Field(..., min_length=1)
    prophecy_text: Optional[str] = None
    role_in_prophecy: Optional[str] = None
    interpretation_variants: List[str] = Field(default_factory=list)
    truth_status: str = "unknown"
    political_usage: List[str] = Field(default_factory=list)
    false_readings: List[str] = Field(default_factory=list)
    payoff_scenes: List[str] = Field(default_factory=list)


class GenerationalLegacyProfile(BaseModel):
    legacy_id: str = Field(..., min_length=1)
    character_id: str = Field(..., min_length=1)
    family_history: List[str] = Field(default_factory=list)
    world_history_links: List[str] = Field(default_factory=list)
    old_wars: List[str] = Field(default_factory=list)
    inherited_guilt: List[str] = Field(default_factory=list)
    inherited_privilege: List[str] = Field(default_factory=list)
    ancestral_promises: List[str] = Field(default_factory=list)
    bloodline_myths: List[str] = Field(default_factory=list)
    family_curses: List[str] = Field(default_factory=list)
    old_debts: List[str] = Field(default_factory=list)
    legacy_artifacts: List[str] = Field(default_factory=list)
    future_generation_hooks: List[str] = Field(default_factory=list)


class CharacterMirrorProfile(BaseModel):
    mirror_id: str = Field(..., min_length=1)
    character_id: str = Field(..., min_length=1)
    mirrored_character_id: str = Field(..., min_length=1)
    mirror_type: str = Field(..., min_length=1)
    shared_wound: Optional[str] = None
    key_difference: Optional[str] = None
    thematic_function: Optional[str] = None
    possible_confrontations: List[str] = Field(default_factory=list)
    payoff_scenes: List[str] = Field(default_factory=list)
    resolution: Optional[str] = None


class CharacterScoreProfile(BaseModel):
    score_id: str = Field(..., min_length=1)
    character_id: str = Field(..., min_length=1)
    reader_attachment_score: float = Field(default=0.0, ge=0.0, le=1.0)
    commercial_memorability_score: float = Field(default=0.0, ge=0.0, le=1.0)
    psychological_depth_score: float = Field(default=0.0, ge=0.0, le=1.0)
    agency_score: float = Field(default=0.0, ge=0.0, le=1.0)
    arc_potential_score: float = Field(default=0.0, ge=0.0, le=1.0)
    relationship_potential_score: float = Field(default=0.0, ge=0.0, le=1.0)
    villain_strength_score: float = Field(default=0.0, ge=0.0, le=1.0)
    romance_independence_score: float = Field(default=0.0, ge=0.0, le=1.0)
    adaptation_strength_score: float = Field(default=0.0, ge=0.0, le=1.0)
    fan_discussion_potential: float = Field(default=0.0, ge=0.0, le=1.0)
    cliche_risk_score: float = Field(default=0.0, ge=0.0, le=1.0)
    overpowered_risk_score: float = Field(default=0.0, ge=0.0, le=1.0)
    simulation_readiness_score: float = Field(default=0.0, ge=0.0, le=1.0)
    explanation: List[str] = Field(default_factory=list)
    improvement_suggestions: List[str] = Field(default_factory=list)


class CharacterDatasetMetadata(BaseModel):
    metadata_id: str = Field(..., min_length=1)
    character_id: str = Field(..., min_length=1)
    training_eligible: bool = False
    human_review_required: bool = True
    do_not_train: bool = True
    source_mode: str = "synthetic_engine_generated"
    provenance_notes: List[str] = Field(default_factory=list)
    quality_tier: str = "unreviewed"
    duplicate_risk: str = "unknown"
    cliche_risk: str = "unknown"
    sensitive_content_flags: List[str] = Field(default_factory=list)
    recommended_dataset_split: str = "human_review_queue"
    character_type_tags: List[str] = Field(default_factory=list)
    arc_tags: List[str] = Field(default_factory=list)
    destiny_tags: List[str] = Field(default_factory=list)
    psychology_tags: List[str] = Field(default_factory=list)
    world_dependency_tags: List[str] = Field(default_factory=list)
    adaptability_tags: List[str] = Field(default_factory=list)


class CharacterSnapshotMetadata(BaseModel):
    snapshot_id: str = Field(..., min_length=1)
    character_id: str = Field(..., min_length=1)
    snapshot_type: str = Field(..., min_length=1)
    snapshot_label: Optional[str] = None
    parent_snapshot_id: Optional[str] = None
    change_summary: Optional[str] = None
    rollback_ready: bool = True
    created_by: str = "character.snapshot_engine"
    tags: List[str] = Field(default_factory=list)


class CharacterBibleExport(BaseModel):
    export_id: str = Field(..., min_length=1)
    character_id: str = Field(..., min_length=1)
    export_format: str = "markdown_and_json"
    export_title: Optional[str] = None
    character_bible_markdown: Optional[str] = None
    character_bible_json: Dict[str, Any] = Field(default_factory=dict)
    export_readiness_score: float = Field(default=0.0, ge=0.0, le=1.0)
    missing_sections: List[str] = Field(default_factory=list)
    includes_dataset_metadata: bool = True
    includes_snapshot_metadata: bool = True


class CharacterAgentState(BaseModel):
    agent_state_id: str = Field(..., min_length=1)
    character_id: str = Field(..., min_length=1)
    internal_state: Dict[str, Any] = Field(default_factory=dict)
    external_state: Dict[str, Any] = Field(default_factory=dict)
    social_state: Dict[str, Any] = Field(default_factory=dict)
    emotional_state: Dict[str, Any] = Field(default_factory=dict)
    memory_state: Dict[str, Any] = Field(default_factory=dict)
    goal_state: Dict[str, Any] = Field(default_factory=dict)
    moral_state: Dict[str, Any] = Field(default_factory=dict)
    skill_state: Dict[str, Any] = Field(default_factory=dict)
    destiny_state: Dict[str, Any] = Field(default_factory=dict)
    adaptability_state: Dict[str, Any] = Field(default_factory=dict)
    agency_state: Dict[str, Any] = Field(default_factory=dict)
    simulation_readiness: float = Field(default=0.0, ge=0.0, le=1.0)


class CompleteCharacterProfile(BaseModel):
    identity: CharacterIdentity
    people_type: Optional[PeopleTypeProfile] = None
    origin: Optional[OriginProfile] = None
    family: Optional[FamilyProfile] = None
    psychology: Optional[PsychologyProfile] = None
    trauma_records: List[TraumaRecord] = Field(default_factory=list)
    emotional_state: Optional[EmotionalStateProfile] = None
    emotional_arc: Optional[EmotionalArcProfile] = None
    memories: List[MemoryRecord] = Field(default_factory=list)
    reputation: Optional[ReputationProfile] = None
    goals: List[GoalRecord] = Field(default_factory=list)
    morality: Optional[MoralProfile] = None
    skills: List[SkillProfile] = Field(default_factory=list)
    growth_tracks: List[GrowthTrack] = Field(default_factory=list)
    adaptability: Optional[AdaptabilityProfile] = None
    destiny: Optional[DestinyProfile] = None
    prophecy_links: List[ProphecyLink] = Field(default_factory=list)
    legacy: Optional[GenerationalLegacyProfile] = None
    mirrors: List[CharacterMirrorProfile] = Field(default_factory=list)
    scores: Optional[CharacterScoreProfile] = None
    dataset_metadata: Optional[CharacterDatasetMetadata] = None
    snapshot_metadata: Optional[CharacterSnapshotMetadata] = None
    bible_export: Optional[CharacterBibleExport] = None
    agent_state: Optional[CharacterAgentState] = None

    def completion_ratio(self) -> float:
        sections = [
            self.origin,
            self.family,
            self.psychology,
            self.emotional_state,
            self.reputation,
            self.morality,
            self.adaptability,
            self.destiny,
            self.scores,
            self.dataset_metadata,
            self.snapshot_metadata,
            self.bible_export,
            self.agent_state,
        ]

        list_sections = [
            self.trauma_records,
            self.memories,
            self.goals,
            self.skills,
            self.growth_tracks,
            self.prophecy_links,
            self.mirrors,
        ]

        completed = sum(1 for section in sections if section is not None)
        completed += sum(1 for section in list_sections if len(section) > 0)

        total = len(sections) + len(list_sections)

        return round(completed / total, 3)

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import uuid4

from pydantic import BaseModel, Field


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def new_world_id(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex[:12]}"


# ---------------------------------------------------------------------
# Shared / common world schema components
# ---------------------------------------------------------------------


class ScoreDetail(BaseModel):
    score_name: str
    score: float = Field(ge=0.0, le=1.0)
    rationale: str = ""
    evidence: List[str] = Field(default_factory=list)


class SourceReference(BaseModel):
    source_id: str = ""
    source_type: str = "system_generated"
    title: str = ""
    license: str = ""
    provenance_notes: str = ""
    usable_for_training: bool = False


class TrainingReadinessMetadata(BaseModel):
    generation_method: str = "rule_based_v0"
    model_version: str = "none"
    dataset_tags: List[str] = Field(default_factory=list)
    source_references: List[SourceReference] = Field(default_factory=list)
    human_feedback_score: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    consistency_score: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    originality_score: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    story_potential_score: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    training_eligible: bool = False
    do_not_train: bool = True
    training_notes: List[str] = Field(default_factory=list)


# ---------------------------------------------------------------------
# 1. World Identity Engine
# ---------------------------------------------------------------------


class WorldIdentity(BaseModel):
    world_name: str = Field(min_length=1, max_length=180)
    alternate_names: List[str] = Field(default_factory=list)
    mythic_names: List[str] = Field(default_factory=list)
    forbidden_names: List[str] = Field(default_factory=list)
    public_identity: str = ""
    hidden_identity: str = ""
    emotional_promise: str = ""
    genre_promise: str = ""
    reader_promise: str = ""
    world_thesis: str = ""
    symbolic_core: str = ""
    central_world_question: str = ""
    world_wound: str = ""
    world_desire: str = ""
    world_fear: str = ""
    world_contradiction: str = ""
    world_myth: str = ""


# ---------------------------------------------------------------------
# 2. World Rule Engine
# ---------------------------------------------------------------------


class WorldRule(BaseModel):
    rule_id: str = Field(default_factory=lambda: new_world_id("wrule"))
    rule_name: str
    rule_category: str = "general"
    description: str
    applies_to: List[str] = Field(default_factory=list)
    cost_or_limit: str = ""
    enforcement_mechanism: str = ""
    loopholes: List[str] = Field(default_factory=list)
    forbidden_exceptions: List[str] = Field(default_factory=list)
    contradiction_risks: List[str] = Field(default_factory=list)
    story_uses: List[str] = Field(default_factory=list)


class WorldRuleSet(BaseModel):
    magic_rules: List[WorldRule] = Field(default_factory=list)
    technology_rules: List[WorldRule] = Field(default_factory=list)
    destiny_rules: List[WorldRule] = Field(default_factory=list)
    memory_rules: List[WorldRule] = Field(default_factory=list)
    death_rules: List[WorldRule] = Field(default_factory=list)
    healing_rules: List[WorldRule] = Field(default_factory=list)
    prophecy_rules: List[WorldRule] = Field(default_factory=list)
    artifact_rules: List[WorldRule] = Field(default_factory=list)
    knowledge_rules: List[WorldRule] = Field(default_factory=list)
    social_mobility_rules: List[WorldRule] = Field(default_factory=list)
    global_constraints: List[str] = Field(default_factory=list)


# ---------------------------------------------------------------------
# 3. Chronology and Historical Wound Engine
# ---------------------------------------------------------------------


class HistoricalEvent(BaseModel):
    event_id: str = Field(default_factory=lambda: new_world_id("event"))
    name: str
    era_name: str = ""
    year_label: str = ""
    public_version: str = ""
    true_version: str = ""
    causes: List[str] = Field(default_factory=list)
    consequences: List[str] = Field(default_factory=list)
    affected_groups: List[str] = Field(default_factory=list)
    unresolved_tensions: List[str] = Field(default_factory=list)
    story_hooks: List[str] = Field(default_factory=list)


class HistoricalEra(BaseModel):
    era_id: str = Field(default_factory=lambda: new_world_id("era"))
    name: str
    description: str = ""
    dominant_power: str = ""
    dominant_belief: str = ""
    major_events: List[HistoricalEvent] = Field(default_factory=list)
    legacy: str = ""


class HistoricalWound(BaseModel):
    wound_id: str = Field(default_factory=lambda: new_world_id("wound"))
    name: str
    origin_event: str = ""
    who_remembers_it: List[str] = Field(default_factory=list)
    who_denies_it: List[str] = Field(default_factory=list)
    current_effects: List[str] = Field(default_factory=list)
    emotional_charge: str = ""
    plot_potential: List[str] = Field(default_factory=list)


class ChronologyProfile(BaseModel):
    creation_myth: str = ""
    official_history_summary: str = ""
    true_history_summary: str = ""
    current_era: str = ""
    current_year_label: str = ""
    eras: List[HistoricalEra] = Field(default_factory=list)
    erased_history: List[str] = Field(default_factory=list)
    historical_lies: List[str] = Field(default_factory=list)
    historical_wounds: List[HistoricalWound] = Field(default_factory=list)


# ---------------------------------------------------------------------
# 4–5. Geography, Location, Environment, Climate, Disaster
# ---------------------------------------------------------------------


class LocationProfile(BaseModel):
    location_id: str = Field(default_factory=lambda: new_world_id("loc"))
    name: str
    location_type: str = "general"
    description: str = ""
    owner_or_controller: str = ""
    danger_level: float = Field(default=0.0, ge=0.0, le=1.0)
    symbolic_meaning: str = ""
    economic_role: str = ""
    political_role: str = ""
    religious_role: str = ""
    secrets: List[str] = Field(default_factory=list)
    story_potential: List[str] = Field(default_factory=list)
    connected_location_ids: List[str] = Field(default_factory=list)


class TravelRoute(BaseModel):
    route_id: str = Field(default_factory=lambda: new_world_id("route"))
    from_location: str
    to_location: str
    travel_time: str = ""
    cost: str = ""
    danger_level: float = Field(default=0.0, ge=0.0, le=1.0)
    controlled_by: str = ""
    route_notes: str = ""


class GeographyProfile(BaseModel):
    world_map_summary: str = ""
    regions: List[str] = Field(default_factory=list)
    locations: List[LocationProfile] = Field(default_factory=list)
    travel_routes: List[TravelRoute] = Field(default_factory=list)
    unknown_regions: List[str] = Field(default_factory=list)


class EnvironmentProfile(BaseModel):
    climate_zones: List[str] = Field(default_factory=list)
    season_patterns: List[str] = Field(default_factory=list)
    natural_disasters: List[str] = Field(default_factory=list)
    magical_or_environmental_anomalies: List[str] = Field(default_factory=list)
    famine_risks: List[str] = Field(default_factory=list)
    disease_risks: List[str] = Field(default_factory=list)
    dangerous_terrain: List[str] = Field(default_factory=list)
    environmental_pressures: List[str] = Field(default_factory=list)
    weather_symbolism: List[str] = Field(default_factory=list)


# ---------------------------------------------------------------------
# 6–8. Demographics, Society, Hierarchy, Power, Factions
# ---------------------------------------------------------------------


class DemographicsProfile(BaseModel):
    estimated_population: Optional[int] = Field(default=None, ge=0)
    urban_rural_split: Dict[str, float] = Field(default_factory=dict)
    class_distribution: Dict[str, float] = Field(default_factory=dict)
    age_distribution: Dict[str, float] = Field(default_factory=dict)
    migration_patterns: List[str] = Field(default_factory=list)
    minority_groups: List[str] = Field(default_factory=list)
    destined_person_rarity: str = ""
    literacy_distribution: Dict[str, float] = Field(default_factory=dict)
    academy_eligible_population: Optional[int] = Field(default=None, ge=0)


class ClassTier(BaseModel):
    tier_id: str = Field(default_factory=lambda: new_world_id("class"))
    name: str
    rank: int = Field(ge=0)
    privileges: List[str] = Field(default_factory=list)
    restrictions: List[str] = Field(default_factory=list)
    status_symbols: List[str] = Field(default_factory=list)
    mobility_paths: List[str] = Field(default_factory=list)
    common_conflicts: List[str] = Field(default_factory=list)


class SocietyProfile(BaseModel):
    society_summary: str = ""
    class_tiers: List[ClassTier] = Field(default_factory=list)
    birth_privilege_rules: List[str] = Field(default_factory=list)
    marriage_rules: List[str] = Field(default_factory=list)
    inheritance_rules: List[str] = Field(default_factory=list)
    reputation_rules: List[str] = Field(default_factory=list)
    shame_systems: List[str] = Field(default_factory=list)
    honor_systems: List[str] = Field(default_factory=list)
    discrimination_systems: List[str] = Field(default_factory=list)
    destined_person_social_impact: str = ""


class FactionSeed(BaseModel):
    faction_id: str = Field(default_factory=lambda: new_world_id("faction"))
    name: str
    faction_type: str = "general"
    public_goal: str = ""
    hidden_goal: str = ""
    resources: List[str] = Field(default_factory=list)
    allies: List[str] = Field(default_factory=list)
    enemies: List[str] = Field(default_factory=list)
    recruitment_method: str = ""
    betrayal_probability: float = Field(default=0.0, ge=0.0, le=1.0)
    story_uses: List[str] = Field(default_factory=list)


class PowerStructureProfile(BaseModel):
    public_authority: str = ""
    real_authority: str = ""
    ruling_groups: List[str] = Field(default_factory=list)
    hidden_rulers: List[str] = Field(default_factory=list)
    kingmakers: List[str] = Field(default_factory=list)
    factions: List[FactionSeed] = Field(default_factory=list)
    alliance_map: Dict[str, List[str]] = Field(default_factory=dict)
    power_instability_notes: List[str] = Field(default_factory=list)


# ---------------------------------------------------------------------
# 9–11. Economy, Law, Military
# ---------------------------------------------------------------------


class ResourceProfile(BaseModel):
    resource_id: str = Field(default_factory=lambda: new_world_id("res"))
    name: str
    resource_type: str = "general"
    scarcity_level: float = Field(default=0.0, ge=0.0, le=1.0)
    controlled_by: List[str] = Field(default_factory=list)
    economic_value: str = ""
    story_conflicts: List[str] = Field(default_factory=list)


class EconomyProfile(BaseModel):
    currency_system: str = ""
    main_resources: List[ResourceProfile] = Field(default_factory=list)
    trade_routes: List[str] = Field(default_factory=list)
    taxation_system: str = ""
    debt_system: str = ""
    labor_system: str = ""
    black_markets: List[str] = Field(default_factory=list)
    wealth_concentration: str = ""
    academy_or_institution_funding: str = ""
    collapse_triggers: List[str] = Field(default_factory=list)


class LawSystem(BaseModel):
    legal_summary: str = ""
    legal_classes: List[str] = Field(default_factory=list)
    rights_by_birth: Dict[str, List[str]] = Field(default_factory=dict)
    forbidden_acts: List[str] = Field(default_factory=list)
    punishments: List[str] = Field(default_factory=list)
    courts: List[str] = Field(default_factory=list)
    law_enforcement_groups: List[str] = Field(default_factory=list)
    legal_loopholes: List[str] = Field(default_factory=list)
    corruption_level: float = Field(default=0.0, ge=0.0, le=1.0)


class MilitarySecurityProfile(BaseModel):
    armies: List[str] = Field(default_factory=list)
    elite_units: List[str] = Field(default_factory=list)
    police_or_security_forces: List[str] = Field(default_factory=list)
    spy_networks: List[str] = Field(default_factory=list)
    assassin_or_special_orders: List[str] = Field(default_factory=list)
    military_ranks: List[str] = Field(default_factory=list)
    war_readiness_score: float = Field(default=0.0, ge=0.0, le=1.0)
    current_war_risks: List[str] = Field(default_factory=list)
    military_corruption: str = ""


# ---------------------------------------------------------------------
# 12–18. Religion, Culture, Knowledge, Institutions, Tech, Species, Infrastructure
# ---------------------------------------------------------------------


class BeliefSystem(BaseModel):
    belief_summary: str = ""
    gods_or_forces: List[str] = Field(default_factory=list)
    dead_or_forgotten_gods: List[str] = Field(default_factory=list)
    holy_texts: List[str] = Field(default_factory=list)
    rituals: List[str] = Field(default_factory=list)
    taboos: List[str] = Field(default_factory=list)
    afterlife_beliefs: str = ""
    heresies: List[str] = Field(default_factory=list)
    prophecy_system: str = ""
    destiny_philosophy: str = ""
    free_will_philosophy: str = ""


class CultureProfile(BaseModel):
    culture_summary: str = ""
    naming_rules: List[str] = Field(default_factory=list)
    family_name_logic: str = ""
    honorifics: List[str] = Field(default_factory=list)
    class_speech_differences: List[str] = Field(default_factory=list)
    slang_and_insults: List[str] = Field(default_factory=list)
    greetings: List[str] = Field(default_factory=list)
    food_culture: List[str] = Field(default_factory=list)
    clothing_culture: List[str] = Field(default_factory=list)
    marriage_customs: List[str] = Field(default_factory=list)
    funeral_customs: List[str] = Field(default_factory=list)
    festivals: List[str] = Field(default_factory=list)
    taboo_gestures: List[str] = Field(default_factory=list)


class KnowledgeEducationProfile(BaseModel):
    literacy_rate_notes: str = ""
    education_access_rules: List[str] = Field(default_factory=list)
    academy_entrance_rules: List[str] = Field(default_factory=list)
    forbidden_books: List[str] = Field(default_factory=list)
    public_archives: List[str] = Field(default_factory=list)
    secret_archives: List[str] = Field(default_factory=list)
    propaganda_systems: List[str] = Field(default_factory=list)
    censorship_methods: List[str] = Field(default_factory=list)
    information_punishments: List[str] = Field(default_factory=list)


class InstitutionProfile(BaseModel):
    institution_id: str = Field(default_factory=lambda: new_world_id("inst"))
    name: str
    institution_type: str
    public_purpose: str = ""
    hidden_purpose: str = ""
    entrance_rules: List[str] = Field(default_factory=list)
    rank_system: List[str] = Field(default_factory=list)
    corruption_level: float = Field(default=0.0, ge=0.0, le=1.0)
    internal_factions: List[str] = Field(default_factory=list)
    story_uses: List[str] = Field(default_factory=list)


class TechnologyMagicScienceProfile(BaseModel):
    technology_level: str = ""
    magic_development_level: str = ""
    scientific_understanding: str = ""
    lost_technology: List[str] = Field(default_factory=list)
    forbidden_research: List[str] = Field(default_factory=list)
    medicine_or_healing_level: str = ""
    transportation_level: str = ""
    communication_level: str = ""
    innovation_bottlenecks: List[str] = Field(default_factory=list)
    military_technology: List[str] = Field(default_factory=list)


class SpeciesCreatureProfile(BaseModel):
    sentient_species: List[str] = Field(default_factory=list)
    non_sentient_creatures: List[str] = Field(default_factory=list)
    monster_ecology: List[str] = Field(default_factory=list)
    sacred_animals: List[str] = Field(default_factory=list)
    domesticated_creatures: List[str] = Field(default_factory=list)
    species_relations: List[str] = Field(default_factory=list)
    species_laws: List[str] = Field(default_factory=list)
    dangerous_habitats: List[str] = Field(default_factory=list)


class InfrastructureProfile(BaseModel):
    roads: List[str] = Field(default_factory=list)
    ports: List[str] = Field(default_factory=list)
    bridges: List[str] = Field(default_factory=list)
    transit_systems: List[str] = Field(default_factory=list)
    postal_or_messenger_systems: List[str] = Field(default_factory=list)
    communication_delays: List[str] = Field(default_factory=list)
    trade_chokepoints: List[str] = Field(default_factory=list)
    border_controls: List[str] = Field(default_factory=list)
    infrastructure_decay: List[str] = Field(default_factory=list)


# ---------------------------------------------------------------------
# 19–21. Artifacts, Aesthetic, Civilization Pressure
# ---------------------------------------------------------------------


class ArtifactProfile(BaseModel):
    artifact_id: str = Field(default_factory=lambda: new_world_id("artifact"))
    name: str
    artifact_type: str = "general"
    origin: str = ""
    ownership_history: List[str] = Field(default_factory=list)
    symbolism: str = ""
    legal_status: str = ""
    religious_status: str = ""
    emotional_status: str = ""
    power_or_function: str = ""
    plot_potential: List[str] = Field(default_factory=list)


class AestheticTextureProfile(BaseModel):
    visual_palette: List[str] = Field(default_factory=list)
    architecture_style: str = ""
    soundscape: List[str] = Field(default_factory=list)
    smellscape: List[str] = Field(default_factory=list)
    food_textures: List[str] = Field(default_factory=list)
    clothing_silhouettes: List[str] = Field(default_factory=list)
    symbolic_colors: List[str] = Field(default_factory=list)
    elite_visual_style: str = ""
    poor_visual_style: str = ""
    cinematic_identity: str = ""


class CivilizationPressureProfile(BaseModel):
    current_crisis: str = ""
    hidden_crisis: str = ""
    social_pressure: str = ""
    economic_pressure: str = ""
    spiritual_pressure: str = ""
    war_pressure: str = ""
    mystery_pressure: str = ""
    villain_pressure: str = ""
    destiny_pressure: str = ""
    collapse_timeline: str = ""
    if_nobody_acts: str = ""
    if_villain_wins: str = ""
    system_breaking_points: List[str] = Field(default_factory=list)


# ---------------------------------------------------------------------
# 22–32. Checkers, DNA, Causality, Memory, Training, Boundaries
# ---------------------------------------------------------------------


class WorldConsistencyIssue(BaseModel):
    issue_id: str = Field(default_factory=lambda: new_world_id("issue"))
    severity: str = "medium"
    category: str
    description: str
    suggested_fix: str = ""


class WorldConsistencyReport(BaseModel):
    consistency_score: float = Field(default=0.0, ge=0.0, le=1.0)
    issues: List[WorldConsistencyIssue] = Field(default_factory=list)
    passed_checks: List[str] = Field(default_factory=list)
    failed_checks: List[str] = Field(default_factory=list)


class OriginalityReport(BaseModel):
    originality_score: float = Field(default=0.0, ge=0.0, le=1.0)
    genericness_risk: float = Field(default=0.0, ge=0.0, le=1.0)
    unique_rule_density: float = Field(default=0.0, ge=0.0, le=1.0)
    memorable_location_score: float = Field(default=0.0, ge=0.0, le=1.0)
    cultural_specificity_score: float = Field(default=0.0, ge=0.0, le=1.0)
    notes: List[str] = Field(default_factory=list)


class StoryPotentialReport(BaseModel):
    overall_story_potential: float = Field(default=0.0, ge=0.0, le=1.0)
    character_opportunity: float = Field(default=0.0, ge=0.0, le=1.0)
    romance_opportunity: float = Field(default=0.0, ge=0.0, le=1.0)
    villain_opportunity: float = Field(default=0.0, ge=0.0, le=1.0)
    mystery_opportunity: float = Field(default=0.0, ge=0.0, le=1.0)
    war_opportunity: float = Field(default=0.0, ge=0.0, le=1.0)
    political_intrigue_opportunity: float = Field(default=0.0, ge=0.0, le=1.0)
    sequel_potential: float = Field(default=0.0, ge=0.0, le=1.0)
    commercial_hook_strength: float = Field(default=0.0, ge=0.0, le=1.0)


class WorldDNAProfile(BaseModel):
    world_dna_id: str = Field(default_factory=lambda: new_world_id("wdna"))
    dominant_conflict_type: str = ""
    dominant_social_structure: str = ""
    dominant_power_source: str = ""
    dominant_emotional_atmosphere: str = ""
    dominant_aesthetic_pattern: str = ""
    dominant_historical_wound: str = ""
    dominant_law_pattern: str = ""
    dominant_belief_pattern: str = ""
    rarity_profile: str = ""
    similarity_warnings: List[str] = Field(default_factory=list)
    uniqueness_axes: Dict[str, float] = Field(default_factory=dict)


class CausalityLink(BaseModel):
    link_id: str = Field(default_factory=lambda: new_world_id("cause"))
    cause: str
    effect: str
    strength: float = Field(default=0.5, ge=0.0, le=1.0)
    affected_systems: List[str] = Field(default_factory=list)
    story_use: str = ""


class WorldCausalityGraph(BaseModel):
    links: List[CausalityLink] = Field(default_factory=list)
    root_causes: List[str] = Field(default_factory=list)
    likely_future_effects: List[str] = Field(default_factory=list)


class WorldScaleGranularityProfile(BaseModel):
    target_format: str = "novel_series"
    scale_label: str = "large"
    expected_story_length: str = ""
    recommended_region_count: int = Field(default=3, ge=0)
    recommended_faction_count: int = Field(default=5, ge=0)
    recommended_institution_count: int = Field(default=5, ge=0)
    recommended_artifact_count: int = Field(default=5, ge=0)
    history_depth: str = "medium"
    location_density: str = "medium"


class WorldContradictionIntent(BaseModel):
    intentional_hypocrisies: List[str] = Field(default_factory=list)
    social_contradictions: List[str] = Field(default_factory=list)
    legal_contradictions: List[str] = Field(default_factory=list)
    religious_contradictions: List[str] = Field(default_factory=list)
    economic_contradictions: List[str] = Field(default_factory=list)
    bad_contradiction_risks: List[str] = Field(default_factory=list)


class WorldMemoryArchive(BaseModel):
    archived_events: List[str] = Field(default_factory=list)
    law_changes: List[str] = Field(default_factory=list)
    faction_changes: List[str] = Field(default_factory=list)
    destroyed_locations: List[str] = Field(default_factory=list)
    lost_artifacts: List[str] = Field(default_factory=list)
    fulfilled_prophecies: List[str] = Field(default_factory=list)
    broken_promises: List[str] = Field(default_factory=list)
    world_state_snapshots: List[str] = Field(default_factory=list)


class WorldBoundaryConstraintProfile(BaseModel):
    known_world_boundaries: List[str] = Field(default_factory=list)
    believed_outside_world: List[str] = Field(default_factory=list)
    actual_outside_world: List[str] = Field(default_factory=list)
    physical_boundaries: List[str] = Field(default_factory=list)
    political_boundaries: List[str] = Field(default_factory=list)
    magical_boundaries: List[str] = Field(default_factory=list)
    knowledge_boundaries: List[str] = Field(default_factory=list)
    exploration_limits: List[str] = Field(default_factory=list)
    sequel_expansion_potential: List[str] = Field(default_factory=list)


# ---------------------------------------------------------------------
# Master world objects
# ---------------------------------------------------------------------


class WorldCreate(BaseModel):
    universe_id: str
    name: str = Field(min_length=1, max_length=180)
    seed_premise: str = Field(default="", max_length=10000)
    target_format: str = "novel_series"
    scale_label: str = "large"
    genre_tags: List[str] = Field(default_factory=list)
    tone_tags: List[str] = Field(default_factory=list)
    desired_complexity: str = "high"


class WorldRead(WorldCreate):
    world_id: str
    status: str = "draft"
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)


class WorldGenerationRequest(BaseModel):
    project_id: str
    universe_id: str
    seed_premise: str = ""
    target_format: str = "novel_series"
    genre_tags: List[str] = Field(default_factory=list)
    tone_tags: List[str] = Field(default_factory=list)
    desired_complexity: str = "high"
    world_count: int = Field(default=1, ge=1, le=100)


class WorldBible(BaseModel):
    world_id: str
    universe_id: str
    identity: Optional[WorldIdentity] = None
    scale_granularity: WorldScaleGranularityProfile = Field(default_factory=WorldScaleGranularityProfile)
    rules: WorldRuleSet = Field(default_factory=WorldRuleSet)
    chronology: ChronologyProfile = Field(default_factory=ChronologyProfile)
    geography: GeographyProfile = Field(default_factory=GeographyProfile)
    environment: EnvironmentProfile = Field(default_factory=EnvironmentProfile)
    demographics: DemographicsProfile = Field(default_factory=DemographicsProfile)
    society: SocietyProfile = Field(default_factory=SocietyProfile)
    power_structure: PowerStructureProfile = Field(default_factory=PowerStructureProfile)
    economy: EconomyProfile = Field(default_factory=EconomyProfile)
    law: LawSystem = Field(default_factory=LawSystem)
    military_security: MilitarySecurityProfile = Field(default_factory=MilitarySecurityProfile)
    belief: BeliefSystem = Field(default_factory=BeliefSystem)
    culture: CultureProfile = Field(default_factory=CultureProfile)
    knowledge_education: KnowledgeEducationProfile = Field(default_factory=KnowledgeEducationProfile)
    institutions: List[InstitutionProfile] = Field(default_factory=list)
    technology_magic_science: TechnologyMagicScienceProfile = Field(default_factory=TechnologyMagicScienceProfile)
    species_creatures: SpeciesCreatureProfile = Field(default_factory=SpeciesCreatureProfile)
    infrastructure: InfrastructureProfile = Field(default_factory=InfrastructureProfile)
    artifacts: List[ArtifactProfile] = Field(default_factory=list)
    aesthetic_texture: AestheticTextureProfile = Field(default_factory=AestheticTextureProfile)
    civilization_pressure: CivilizationPressureProfile = Field(default_factory=CivilizationPressureProfile)
    consistency_report: WorldConsistencyReport = Field(default_factory=WorldConsistencyReport)
    originality_report: OriginalityReport = Field(default_factory=OriginalityReport)
    story_potential_report: StoryPotentialReport = Field(default_factory=StoryPotentialReport)
    world_dna: WorldDNAProfile = Field(default_factory=WorldDNAProfile)
    causality_graph: WorldCausalityGraph = Field(default_factory=WorldCausalityGraph)
    contradiction_intent: WorldContradictionIntent = Field(default_factory=WorldContradictionIntent)
    memory_archive: WorldMemoryArchive = Field(default_factory=WorldMemoryArchive)
    boundary_constraints: WorldBoundaryConstraintProfile = Field(default_factory=WorldBoundaryConstraintProfile)
    training_metadata: TrainingReadinessMetadata = Field(default_factory=TrainingReadinessMetadata)


class WorldGenerationResult(BaseModel):
    success: bool
    world: Optional[WorldRead] = None
    world_bible: Optional[WorldBible] = None
    warnings: List[str] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)

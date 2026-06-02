
from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator


class DeepWorldPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class DeepWorldElementType(str, Enum):
    WORLD = "world"
    REGION = "region"
    BIOME = "biome"
    TERRAIN = "terrain"
    CLIMATE = "climate"
    WEATHER = "weather"
    FLORA = "flora"
    FAUNA = "fauna"
    CREATURE = "creature"
    SPECIES = "species"
    CIVILIZATION = "civilization"
    CULTURE = "culture"
    SETTLEMENT = "settlement"
    ROUTE = "route"
    SECRET_LOCATION = "secret_location"
    OBJECT_ARTIFACT = "object_artifact"
    DAILY_LIFE = "daily_life"
    DISASTER = "disaster"
    MIGRATION = "migration"
    MEMORY = "memory"
    VALIDATION = "validation"


class DeepWorldValidationStatus(str, Enum):
    DRAFT = "draft"
    NEEDS_REVIEW = "needs_review"
    VALIDATED = "validated"
    BLOCKED = "blocked"


class DeepWorldBaseElement(BaseModel):
    element_id: str = Field(..., min_length=1)
    source_id: str = Field(..., min_length=1)
    element_type: DeepWorldElementType
    name: str = Field(..., min_length=1)
    summary: str = Field(..., min_length=1)
    priority: DeepWorldPriority = DeepWorldPriority.MEDIUM
    tags: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    story_use: str = Field(..., min_length=1)
    character_effect: str = Field(..., min_length=1)
    plot_effect: str = Field(..., min_length=1)
    memory_effect: str = Field(..., min_length=1)
    validation_status: DeepWorldValidationStatus = DeepWorldValidationStatus.DRAFT
    provenance: Dict[str, Any] = Field(default_factory=dict)
    compression_summary: str = Field(..., min_length=1)

    @field_validator("tags")
    @classmethod
    def normalize_tags(cls, value: List[str]) -> List[str]:
        return sorted({tag.strip().lower() for tag in value if tag and tag.strip()})


class DeepWorldRegion(DeepWorldBaseElement):
    element_type: DeepWorldElementType = DeepWorldElementType.REGION
    terrain_signature: List[str] = Field(default_factory=list)
    climate_signature: List[str] = Field(default_factory=list)
    visual_signature: List[str] = Field(default_factory=list)
    emotional_signature: List[str] = Field(default_factory=list)
    danger_signature: List[str] = Field(default_factory=list)
    secret_signature: List[str] = Field(default_factory=list)
    connected_settlement_ids: List[str] = Field(default_factory=list)
    connected_route_ids: List[str] = Field(default_factory=list)


class DeepWorldClimateSystem(DeepWorldBaseElement):
    element_type: DeepWorldElementType = DeepWorldElementType.CLIMATE
    seasons: List[str] = Field(default_factory=list)
    weather_patterns: List[str] = Field(default_factory=list)
    travel_effects: List[str] = Field(default_factory=list)
    crop_effects: List[str] = Field(default_factory=list)
    ritual_effects: List[str] = Field(default_factory=list)
    scene_atmosphere_effects: List[str] = Field(default_factory=list)


class DeepWorldEcologySystem(DeepWorldBaseElement):
    element_type: DeepWorldElementType = DeepWorldElementType.BIOME
    food_chain_notes: List[str] = Field(default_factory=list)
    predator_prey_links: List[Dict[str, Any]] = Field(default_factory=list)
    keystone_species: List[str] = Field(default_factory=list)
    invasive_species_risks: List[str] = Field(default_factory=list)
    collapse_risks: List[str] = Field(default_factory=list)
    civilization_dependencies: List[str] = Field(default_factory=list)


class DeepWorldFlora(DeepWorldBaseElement):
    element_type: DeepWorldElementType = DeepWorldElementType.FLORA
    lifecycle: Dict[str, Any] = Field(default_factory=dict)
    uses: List[str] = Field(default_factory=list)
    toxicity: Optional[str] = None
    medicinal_effects: List[str] = Field(default_factory=list)
    ritual_uses: List[str] = Field(default_factory=list)
    trade_value: Optional[str] = None
    ecological_dependencies: List[str] = Field(default_factory=list)


class DeepWorldFauna(DeepWorldBaseElement):
    element_type: DeepWorldElementType = DeepWorldElementType.FAUNA
    behavior_patterns: List[str] = Field(default_factory=list)
    habitat_rules: List[str] = Field(default_factory=list)
    domestication_notes: Optional[str] = None
    danger_profile: List[str] = Field(default_factory=list)
    cultural_meaning: List[str] = Field(default_factory=list)
    economic_uses: List[str] = Field(default_factory=list)


class DeepWorldSpecies(DeepWorldBaseElement):
    element_type: DeepWorldElementType = DeepWorldElementType.SPECIES
    biology: Dict[str, Any] = Field(default_factory=dict)
    culture: Dict[str, Any] = Field(default_factory=dict)
    environmental_adaptations: List[str] = Field(default_factory=list)
    social_position: Optional[str] = None
    language_traits: List[str] = Field(default_factory=list)
    conflict_hooks: List[str] = Field(default_factory=list)
    character_generation_hooks: List[str] = Field(default_factory=list)


class DeepWorldSettlement(DeepWorldBaseElement):
    element_type: DeepWorldElementType = DeepWorldElementType.SETTLEMENT
    settlement_type: str = Field(..., min_length=1)
    reason_for_location: str = Field(..., min_length=1)
    sustaining_resources: List[str] = Field(default_factory=list)
    controlling_powers: List[str] = Field(default_factory=list)
    suffering_groups: List[str] = Field(default_factory=list)
    hidden_secrets: List[str] = Field(default_factory=list)
    threats: List[str] = Field(default_factory=list)
    connected_routes: List[str] = Field(default_factory=list)
    settlement_soul: Dict[str, Any] = Field(default_factory=dict)


class DeepWorldRoute(DeepWorldBaseElement):
    element_type: DeepWorldElementType = DeepWorldElementType.ROUTE
    route_type: str = Field(..., min_length=1)
    start_location_id: str = Field(..., min_length=1)
    end_location_id: str = Field(..., min_length=1)
    travel_time: str = Field(..., min_length=1)
    travel_cost: str = Field(..., min_length=1)
    travel_risks: List[str] = Field(default_factory=list)
    seasonal_constraints: List[str] = Field(default_factory=list)
    witness_exposure: Optional[str] = None


class DeepWorldSecretLocation(DeepWorldBaseElement):
    element_type: DeepWorldElementType = DeepWorldElementType.SECRET_LOCATION
    discovery_conditions: List[str] = Field(default_factory=list)
    access_requirements: List[str] = Field(default_factory=list)
    linked_histories: List[str] = Field(default_factory=list)
    linked_artifacts: List[str] = Field(default_factory=list)
    reveal_risks: List[str] = Field(default_factory=list)


class DeepWorldObjectArtifact(DeepWorldBaseElement):
    element_type: DeepWorldElementType = DeepWorldElementType.OBJECT_ARTIFACT
    material: str = Field(..., min_length=1)
    origin: str = Field(..., min_length=1)
    maker: Optional[str] = None
    owner: Optional[str] = None
    use: str = Field(..., min_length=1)
    symbolic_meaning: str = Field(..., min_length=1)
    economic_value: Optional[str] = None
    rarity: Optional[str] = None
    durability: Optional[str] = None


class DeepWorldMemoryUpdate(BaseModel):
    memory_update_id: str = Field(..., min_length=1)
    source_id: str = Field(..., min_length=1)
    update_type: str = Field(..., min_length=1)
    target_element_id: str = Field(..., min_length=1)
    before_state: Dict[str, Any] = Field(default_factory=dict)
    after_state: Dict[str, Any] = Field(default_factory=dict)
    causal_reason: str = Field(..., min_length=1)
    downstream_effects: List[str] = Field(default_factory=list)
    approved_for_story_memory: bool = False


class DeepWorldProvenanceRecord(BaseModel):
    provenance_id: str = Field(..., min_length=1)
    source_id: str = Field(..., min_length=1)
    element_id: str = Field(..., min_length=1)
    origin_type: str = Field(..., min_length=1)
    generated_by_engine: str = Field(..., min_length=1)
    input_references: List[Dict[str, Any]] = Field(default_factory=list)
    dataset_references: List[Dict[str, Any]] = Field(default_factory=list)
    human_review_status: str = "not_reviewed"
    training_eligibility: bool = False
    embedding_eligibility: bool = False
    bias_notes: List[str] = Field(default_factory=list)


class DeepWorldValidationReport(BaseModel):
    validation_report_id: str = Field(..., min_length=1)
    source_id: str = Field(..., min_length=1)
    passed: bool
    specificity_score: float = Field(..., ge=0.0, le=1.0)
    consistency_score: float = Field(..., ge=0.0, le=1.0)
    novelty_score: float = Field(..., ge=0.0, le=1.0)
    story_usefulness_score: float = Field(..., ge=0.0, le=1.0)
    emotional_resonance_score: float = Field(..., ge=0.0, le=1.0)
    warnings: List[str] = Field(default_factory=list)
    blockers: List[str] = Field(default_factory=list)
    recommended_repairs: List[str] = Field(default_factory=list)


class DeepWorldExpansionBundle(BaseModel):
    bundle_id: str = Field(..., min_length=1)
    source_id: str = Field(..., min_length=1)
    regions: List[DeepWorldRegion] = Field(default_factory=list)
    climate_systems: List[DeepWorldClimateSystem] = Field(default_factory=list)
    ecology_systems: List[DeepWorldEcologySystem] = Field(default_factory=list)
    flora: List[DeepWorldFlora] = Field(default_factory=list)
    fauna: List[DeepWorldFauna] = Field(default_factory=list)
    species: List[DeepWorldSpecies] = Field(default_factory=list)
    settlements: List[DeepWorldSettlement] = Field(default_factory=list)
    routes: List[DeepWorldRoute] = Field(default_factory=list)
    secret_locations: List[DeepWorldSecretLocation] = Field(default_factory=list)
    objects_artifacts: List[DeepWorldObjectArtifact] = Field(default_factory=list)
    memory_updates: List[DeepWorldMemoryUpdate] = Field(default_factory=list)
    provenance_records: List[DeepWorldProvenanceRecord] = Field(default_factory=list)
    validation_report: Optional[DeepWorldValidationReport] = None
    story_context_patch: Dict[str, Any] = Field(default_factory=dict)
    generation_hints: List[str] = Field(default_factory=list)
    compression_summary: str = Field(..., min_length=1)


class Chunk6DeepWorldDesignContract(BaseModel):
    contract_id: str = Field(..., min_length=1)
    source_id: str = Field(..., min_length=1)
    chunk_number: int = 6
    chunk_name: str = "Deep Living World Simulation + World-to-Story Intelligence Layer"
    total_locked_steps: int = 55
    required_output_fields: List[str] = Field(default_factory=lambda: [
        "story_use",
        "character_effect",
        "plot_effect",
        "memory_effect",
        "validation_status",
        "provenance",
        "compression_summary",
    ])
    backward_connections: List[str] = Field(default_factory=lambda: [
        "chunk_1_foundation_contracts",
        "chunk_2_world_society_foundation",
        "chunk_3_character_psychology",
        "chunk_4_simulation_memory_causality",
        "chunk_5_story_generation_pipeline",
        "pre_chunk6_future_compatibility_bridge",
    ])
    forward_connections: List[str] = Field(default_factory=lambda: [
        "chunk_7_genre_engines",
        "chunk_8_adaptation_product_legal_ip",
        "chunk_9_ml_data_research_deployment",
    ])
    bridge_contracts: List[str] = Field(default_factory=lambda: [
        "FutureWorldReferencePacket",
        "DeepWorldReferencePacket",
        "StoryWorldExpansionBridge",
        "ChunkFutureCompatibilityContract",
    ])
    non_negotiable_rules: List[str] = Field(default_factory=list)
    approved_for_implementation: bool = False
    warnings: List[str] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Chunk 6.3B — Global Generated Identity + Naming Depth Contract
# ---------------------------------------------------------------------------

class GeneratedNameProfile(BaseModel):
    name_profile_id: str = Field(..., min_length=1)
    source_id: str = Field(..., min_length=1)
    generated_for_type: str = Field(..., min_length=1)
    unique_name: str = Field(..., min_length=1)
    name_origin: str = Field(..., min_length=1)
    name_meaning: str = Field(..., min_length=1)
    name_language_logic: str = Field(..., min_length=1)
    cultural_context: str = Field(..., min_length=1)
    world_context: str = Field(..., min_length=1)
    pronunciation_hint: str | None = None
    nickname_rules: List[str] = Field(default_factory=list)
    title_rules: List[str] = Field(default_factory=list)
    taboo_name_rules: List[str] = Field(default_factory=list)
    alias_rules: List[str] = Field(default_factory=list)
    related_place_or_family: str | None = None
    anti_genericity_signal: str = Field(..., min_length=1)
    detail_depth_score: float = Field(..., ge=0.0, le=1.0)
    provenance: Dict[str, Any] = Field(default_factory=dict)
    compression_summary: str = Field(..., min_length=1)


class DetailDepthContract(BaseModel):
    detail_depth_contract_id: str = Field(..., min_length=1)
    source_id: str = Field(..., min_length=1)
    applies_to_types: List[str] = Field(default_factory=lambda: [
        "people", "characters", "families", "countries", "cities", "villages",
        "regions", "species", "flora", "fauna", "creatures", "objects",
        "artifacts", "roads", "rivers", "mountains", "forests", "seas",
        "religions", "languages", "laws", "rituals", "foods", "clothing",
        "weapons", "tools", "schools", "markets", "factions", "wars",
        "historical_eras", "secret_places", "myths", "legends",
    ])
    required_identity_fields: List[str] = Field(default_factory=lambda: [
        "unique_name",
        "name_origin",
        "name_meaning",
        "name_language_logic",
        "cultural_context",
        "world_context",
        "visual_identity",
        "sensory_identity",
        "social_function",
        "economic_function",
        "belief_function",
        "story_use",
        "character_effect",
        "plot_effect",
        "memory_effect",
        "validation_status",
        "provenance",
        "anti_genericity_signal",
        "detail_depth_score",
        "compression_summary",
    ])
    minimum_detail_depth_score: float = Field(default=0.75, ge=0.0, le=1.0)
    no_one_liner_rule: bool = True
    require_story_function: bool = True
    require_memory_function: bool = True
    require_lore_connection: bool = True
    require_provenance: bool = True
    warnings: List[str] = Field(default_factory=list)


class GeneratedElementDepthReport(BaseModel):
    depth_report_id: str = Field(..., min_length=1)
    source_id: str = Field(..., min_length=1)
    target_element_id: str = Field(..., min_length=1)
    target_element_type: str = Field(..., min_length=1)
    passed: bool
    detail_depth_score: float = Field(..., ge=0.0, le=1.0)
    naming_depth_score: float = Field(..., ge=0.0, le=1.0)
    lore_depth_score: float = Field(..., ge=0.0, le=1.0)
    story_usefulness_score: float = Field(..., ge=0.0, le=1.0)
    missing_fields: List[str] = Field(default_factory=list)
    shallow_output_warnings: List[str] = Field(default_factory=list)
    repair_actions: List[str] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Chunk 6.3C — Deep Lore, Historical Memory, and Past Event Contract
# ---------------------------------------------------------------------------

class HistoricalMemoryRecord(BaseModel):
    historical_record_id: str = Field(..., min_length=1)
    source_id: str = Field(..., min_length=1)
    event_name: str = Field(..., min_length=1)
    event_type: str = Field(..., min_length=1)
    era_name: str = Field(..., min_length=1)
    public_version: str = Field(..., min_length=1)
    secret_version: str | None = None
    false_version: str | None = None
    who_remembers: List[str] = Field(default_factory=list)
    who_lies_about_it: List[str] = Field(default_factory=list)
    who_benefits_from_forgetting: List[str] = Field(default_factory=list)
    physical_evidence: List[str] = Field(default_factory=list)
    cultural_aftereffects: List[str] = Field(default_factory=list)
    character_trauma_hooks: List[str] = Field(default_factory=list)
    plot_conflict_hooks: List[str] = Field(default_factory=list)
    memory_state_updates: List[Dict[str, Any]] = Field(default_factory=list)
    story_use: str = Field(..., min_length=1)
    character_effect: str = Field(..., min_length=1)
    plot_effect: str = Field(..., min_length=1)
    memory_effect: str = Field(..., min_length=1)
    provenance: Dict[str, Any] = Field(default_factory=dict)
    compression_summary: str = Field(..., min_length=1)


class DeepLoreContract(BaseModel):
    lore_contract_id: str = Field(..., min_length=1)
    source_id: str = Field(..., min_length=1)
    required_lore_categories: List[str] = Field(default_factory=lambda: [
        "historical_eras", "founding_events", "ancient_wars", "lost_civilizations",
        "disasters", "migrations", "religious_schisms", "political_betrayals",
        "old_treaties", "broken_borders", "erased_families", "dead_languages",
        "renamed_cities", "fallen_capitals", "forgotten_roads", "extinct_species",
        "legendary_artifacts", "public_history", "secret_history", "false_history",
        "oral_tradition", "archival_records", "forbidden_knowledge",
    ])
    required_questions: List[str] = Field(default_factory=lambda: [
        "what_happened_here_before",
        "who_remembers_it",
        "who_lies_about_it",
        "who_benefits_from_forgetting_it",
        "what_physical_evidence_remains",
        "what_cultural_behavior_came_from_it",
        "what_character_trauma_came_from_it",
        "what_plot_conflict_can_it_trigger_now",
        "what_memory_state_should_preserve_it",
    ])
    require_public_secret_false_history: bool = True
    require_physical_evidence: bool = True
    require_character_trauma_hooks: bool = True
    require_plot_conflict_hooks: bool = True
    require_memory_state_updates: bool = True
    warnings: List[str] = Field(default_factory=list)


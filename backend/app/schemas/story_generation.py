from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, ConfigDict, field_validator


class GenerationMode(str, Enum):
    quick_scene = "quick_scene"
    full_scene = "full_scene"
    dialogue_only = "dialogue_only"
    chapter = "chapter"
    novel_outline = "novel_outline"
    movie_scene = "movie_scene"
    screenplay_scene = "screenplay_scene"
    series_episode = "series_episode"
    season_outline = "season_outline"
    multi_book_arc = "multi_book_arc"
    interactive_game_scene = "interactive_game_scene"
    rewrite_existing = "rewrite_existing"
    continue_story = "continue_story"
    compare_drafts = "compare_drafts"
    export_bundle = "export_bundle"


class StoryFormat(str, Enum):
    novel = "novel"
    chapter = "chapter"
    short_story = "short_story"
    scene = "scene"
    movie = "movie"
    screenplay = "screenplay"
    series_episode = "series_episode"
    season_outline = "season_outline"
    multi_book_arc = "multi_book_arc"
    comic_scene = "comic_scene"
    game_scene = "game_scene"
    treatment = "treatment"


class DraftStatus(str, Enum):
    planned = "planned"
    drafted = "drafted"
    revised = "revised"
    validated = "validated"
    exported = "exported"
    rejected = "rejected"


class StoryIntent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    intent_id: str
    user_prompt: str
    desired_format: StoryFormat = StoryFormat.scene
    generation_mode: GenerationMode = GenerationMode.full_scene
    genres: List[str] = Field(default_factory=list)
    tone_tags: List[str] = Field(default_factory=list)
    pov_preference: Optional[str] = None
    target_length: Optional[str] = None
    required_character_ids: List[str] = Field(default_factory=list)
    preferred_character_count: Optional[int] = None
    forbidden_elements: List[str] = Field(default_factory=list)
    required_emotional_beats: List[str] = Field(default_factory=list)
    required_plot_beats: List[str] = Field(default_factory=list)
    ending_preference: Optional[str] = None
    dialogue_density: float = 0.5
    worldbuilding_density: float = 0.5
    romance_intensity: float = 0.0
    action_intensity: float = 0.0
    tragedy_intensity: float = 0.0
    comedy_intensity: float = 0.0
    commercial_target: Optional[str] = None
    audience_type: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

    @field_validator(
        "dialogue_density",
        "worldbuilding_density",
        "romance_intensity",
        "action_intensity",
        "tragedy_intensity",
        "comedy_intensity",
    )
    @classmethod
    def bounded_score(cls, value: float) -> float:
        return max(0.0, min(1.0, float(value)))


class HandoffReference(BaseModel):
    model_config = ConfigDict(extra="allow")

    simulation_id: str
    run_id: Optional[str] = None
    handoff_package_id: Optional[str] = None
    scene_payload_id: Optional[str] = None
    plot_payload_id: Optional[str] = None
    dialogue_payload_id: Optional[str] = None
    generation_control_payload_id: Optional[str] = None
    quality_report_id: Optional[str] = None
    anti_genericity_report_id: Optional[str] = None
    benchmark_report_id: Optional[str] = None


class Chunk5DesignContract(BaseModel):
    model_config = ConfigDict(extra="forbid")

    contract_id: str = "chunk5_design_contract_v1"
    must_preserve_user_intent: bool = True
    must_preserve_world_rules: bool = True
    must_preserve_character_backstories: bool = True
    must_preserve_relationship_state: bool = True
    must_preserve_hidden_knowledge_boundaries: bool = True
    must_preserve_causal_continuity: bool = True
    must_use_character_voice_when_available: bool = True
    must_validate_before_export: bool = True
    must_produce_provenance: bool = True
    must_create_story_memory_update_candidates: bool = True
    must_support_deterministic_tests: bool = True
    must_be_provider_agnostic: bool = True
    must_support_future_llm_provider: bool = True
    must_support_future_corpus_learning_without_source_copying: bool = True
    must_support_large_entity_pools: bool = True
    must_support_long_form_generation: bool = True
    notes: List[str] = Field(
        default_factory=lambda: [
            "Chunk 5 generates from structured context, not empty prompts.",
            "Future LLM providers must plug into the same schemas.",
            "Long-form stories must be generated through tracked scene/chapter units.",
            "Raw source text from future corpus learning must not be copied into learning metadata.",
        ]
    )


class GenerationContract(BaseModel):
    model_config = ConfigDict(extra="allow")

    generation_contract_id: str
    story_intent_id: str
    handoff_reference: HandoffReference
    allowed_formats: List[StoryFormat] = Field(default_factory=list)
    selected_format: StoryFormat = StoryFormat.scene
    required_character_ids: List[str] = Field(default_factory=list)
    allowed_character_ids: List[str] = Field(default_factory=list)
    forbidden_character_ids: List[str] = Field(default_factory=list)
    required_world_rule_ids: List[str] = Field(default_factory=list)
    required_secret_ids: List[str] = Field(default_factory=list)
    forbidden_secret_reveals: List[str] = Field(default_factory=list)
    required_causal_node_ids: List[str] = Field(default_factory=list)
    required_consequence_ids: List[str] = Field(default_factory=list)
    required_relationship_ids: List[str] = Field(default_factory=list)
    tone_contract: Dict[str, Any] = Field(default_factory=dict)
    format_contract: Dict[str, Any] = Field(default_factory=dict)
    quality_thresholds: Dict[str, float] = Field(default_factory=dict)
    originality_rules: Dict[str, Any] = Field(default_factory=dict)
    validation_required: bool = True
    provenance_required: bool = True


class StoryContextPackage(BaseModel):
    model_config = ConfigDict(extra="allow")

    context_package_id: str
    project_id: Optional[str] = None
    universe_id: Optional[str] = None
    world_context: Dict[str, Any] = Field(default_factory=dict)
    location_context: Dict[str, Any] = Field(default_factory=dict)
    faction_context: Dict[str, Any] = Field(default_factory=dict)
    culture_context: Dict[str, Any] = Field(default_factory=dict)
    character_context: Dict[str, Any] = Field(default_factory=dict)
    relationship_context: Dict[str, Any] = Field(default_factory=dict)
    knowledge_context: Dict[str, Any] = Field(default_factory=dict)
    emotional_context: Dict[str, Any] = Field(default_factory=dict)
    causal_context: Dict[str, Any] = Field(default_factory=dict)
    format_context: Dict[str, Any] = Field(default_factory=dict)
    user_intent_context: Dict[str, Any] = Field(default_factory=dict)
    large_pool_context: Dict[str, Any] = Field(default_factory=dict)


class SceneBlueprint(BaseModel):
    model_config = ConfigDict(extra="allow")

    blueprint_id: str
    scene_id: str
    scene_purpose: str
    opening_image: Optional[str] = None
    pov_character_id: Optional[str] = None
    active_character_ids: List[str] = Field(default_factory=list)
    location_id: Optional[str] = None
    scene_objective: str
    opposition: Optional[str] = None
    stakes: List[str] = Field(default_factory=list)
    secret_pressure: List[str] = Field(default_factory=list)
    relationship_pressure: List[str] = Field(default_factory=list)
    emotional_turn: Optional[str] = None
    tension_curve: List[float] = Field(default_factory=list)
    ending_hook: Optional[str] = None
    required_world_details: List[str] = Field(default_factory=list)


class SceneBeat(BaseModel):
    model_config = ConfigDict(extra="allow")

    beat_id: str
    scene_id: str
    beat_index: int
    beat_type: str
    purpose: str
    character_ids: List[str] = Field(default_factory=list)
    emotional_state: Dict[str, float] = Field(default_factory=dict)
    knowledge_constraints: List[str] = Field(default_factory=list)
    causal_links: List[str] = Field(default_factory=list)
    relationship_change_hint: Optional[str] = None
    tension_value: float = 0.0

    @field_validator("tension_value")
    @classmethod
    def tension_bounded(cls, value: float) -> float:
        return max(0.0, min(1.0, float(value)))


class DialogueBeat(BaseModel):
    model_config = ConfigDict(extra="allow")

    dialogue_beat_id: str
    scene_id: str
    speaker_id: str
    listener_ids: List[str] = Field(default_factory=list)
    surface_meaning: str
    hidden_meaning: Optional[str] = None
    subtext: Optional[str] = None
    emotion: Optional[str] = None
    secret_risk: float = 0.0
    power_shift: Optional[str] = None
    relationship_effect: Optional[str] = None
    voice_rules: Dict[str, Any] = Field(default_factory=dict)

    @field_validator("secret_risk")
    @classmethod
    def secret_risk_bounded(cls, value: float) -> float:
        return max(0.0, min(1.0, float(value)))


class CharacterVoiceInstruction(BaseModel):
    model_config = ConfigDict(extra="allow")

    character_id: str
    formality: float = 0.5
    sentence_length: str = "medium"
    vocabulary_style: str = "neutral"
    rhythm: str = "balanced"
    humor_style: Optional[str] = None
    anger_behavior: Optional[str] = None
    fear_behavior: Optional[str] = None
    romance_behavior: Optional[str] = None
    silence_behavior: Optional[str] = None
    subtext_style: Optional[str] = None
    power_behavior: Optional[str] = None
    forbidden_phrases: List[str] = Field(default_factory=list)
    signature_phrases: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class EmotionalSubtextInstruction(BaseModel):
    model_config = ConfigDict(extra="allow")

    character_id: str
    dominant_emotion: str
    intensity: float = 0.5
    body_language_hints: List[str] = Field(default_factory=list)
    dialogue_pressure_hints: List[str] = Field(default_factory=list)
    internal_narration_hints: List[str] = Field(default_factory=list)
    emotional_leakage_rules: List[str] = Field(default_factory=list)

    @field_validator("intensity")
    @classmethod
    def intensity_bounded(cls, value: float) -> float:
        return max(0.0, min(1.0, float(value)))


class RelationshipBeat(BaseModel):
    model_config = ConfigDict(extra="allow")

    relationship_id: str
    character_a_id: str
    character_b_id: str
    starting_trust: float = 0.0
    starting_resentment: float = 0.0
    starting_affection: float = 0.0
    starting_rivalry: float = 0.0
    romantic_tension: float = 0.0
    betrayal_risk: float = 0.0
    repair_potential: float = 0.0
    power_imbalance: float = 0.0
    knowledge_asymmetry: List[str] = Field(default_factory=list)
    turning_point: Optional[str] = None
    expected_end_state_shift: Dict[str, float] = Field(default_factory=dict)


class KnowledgeBoundaryReport(BaseModel):
    model_config = ConfigDict(extra="allow")

    report_id: str
    valid: bool = True
    character_id: Optional[str] = None
    checked_secret_ids: List[str] = Field(default_factory=list)
    checked_evidence_ids: List[str] = Field(default_factory=list)
    impossible_knowledge_violations: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)


class CausalContinuityReport(BaseModel):
    model_config = ConfigDict(extra="allow")

    report_id: str
    valid: bool = True
    checked_causal_node_ids: List[str] = Field(default_factory=list)
    missing_causes: List[str] = Field(default_factory=list)
    missing_consequences: List[str] = Field(default_factory=list)
    orphan_events: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)


class ConsequencePayoffPlan(BaseModel):
    model_config = ConfigDict(extra="allow")

    payoff_plan_id: str
    source_consequence_ids: List[str] = Field(default_factory=list)
    payoff_obligations: List[str] = Field(default_factory=list)
    required_scene_beats: List[str] = Field(default_factory=list)
    delayed_payoff_candidates: List[str] = Field(default_factory=list)


class ConstraintSatisfactionReport(BaseModel):
    model_config = ConfigDict(extra="allow")

    report_id: str
    satisfied: bool = True
    required_characters_present: bool = True
    forbidden_elements_avoided: bool = True
    requested_format_followed: bool = True
    requested_tone_followed: bool = True
    emotional_beats_included: bool = True
    relationship_beats_included: bool = True
    ending_hook_included: bool = True
    knowledge_rules_obeyed: bool = True
    failed_constraints: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)



class CommercialAppealReport(BaseModel):
    """Audience-pull and market-positioning score for a planned story unit."""

    report_id: str
    overall_score: float = Field(default=0.0, ge=0.0, le=1.0)
    hook_strength: float = Field(default=0.0, ge=0.0, le=1.0)
    emotional_investment: float = Field(default=0.0, ge=0.0, le=1.0)
    character_appeal: float = Field(default=0.0, ge=0.0, le=1.0)
    relationship_appeal: float = Field(default=0.0, ge=0.0, le=1.0)
    stakes_clarity: float = Field(default=0.0, ge=0.0, le=1.0)
    world_uniqueness: float = Field(default=0.0, ge=0.0, le=1.0)
    scene_momentum: float = Field(default=0.0, ge=0.0, le=1.0)
    continuation_pull: float = Field(default=0.0, ge=0.0, le=1.0)
    adaptation_potential: float = Field(default=0.0, ge=0.0, le=1.0)
    improvement_suggestions: List[str] = Field(default_factory=list)


class ProseStyleProfile(BaseModel):
    model_config = ConfigDict(extra="allow")

    style_profile_id: str
    literary_density: float = 0.5
    sentence_rhythm: str = "balanced"
    sensory_detail: float = 0.5
    internality: float = 0.5
    visuality: float = 0.5
    dialogue_density: float = 0.5
    worldbuilding_density: float = 0.5
    pacing: str = "balanced"
    metaphor_intensity: float = 0.3
    darkness_level: float = 0.0
    humor_level: float = 0.0
    romance_subtlety: float = 0.5
    commercial_readability: float = 0.5


class SceneDraft(BaseModel):
    model_config = ConfigDict(extra="allow")

    draft_id: str
    scene_id: str
    title: Optional[str] = None
    format: StoryFormat = StoryFormat.scene
    status: DraftStatus = DraftStatus.drafted
    text: str
    word_count: int = 0
    source_blueprint_id: Optional[str] = None
    source_contract_id: Optional[str] = None
    revision_number: int = 0
    metadata: Dict[str, Any] = Field(default_factory=dict)


class DialogueDraft(BaseModel):
    model_config = ConfigDict(extra="allow")

    draft_id: str
    scene_id: str
    lines: List[Dict[str, Any]] = Field(default_factory=list)
    status: DraftStatus = DraftStatus.drafted
    source_dialogue_beat_ids: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ChapterDraft(BaseModel):
    model_config = ConfigDict(extra="allow")

    chapter_id: str
    title: str
    scene_draft_ids: List[str] = Field(default_factory=list)
    text: str = ""
    chapter_objective: Optional[str] = None
    ending_hook: Optional[str] = None
    continuity_anchors: List[str] = Field(default_factory=list)
    status: DraftStatus = DraftStatus.drafted


class ScriptDraft(BaseModel):
    model_config = ConfigDict(extra="allow")

    script_id: str
    title: str
    scenes: List[Dict[str, Any]] = Field(default_factory=list)
    format: StoryFormat = StoryFormat.screenplay
    status: DraftStatus = DraftStatus.drafted


class SeriesEpisodeDraft(BaseModel):
    model_config = ConfigDict(extra="allow")

    episode_id: str
    season_id: Optional[str] = None
    title: str
    cold_open: Optional[str] = None
    act_breaks: List[str] = Field(default_factory=list)
    a_plot: List[str] = Field(default_factory=list)
    b_plot: List[str] = Field(default_factory=list)
    episode_hook: Optional[str] = None
    status: DraftStatus = DraftStatus.drafted


class SeasonArcDraft(BaseModel):
    model_config = ConfigDict(extra="allow")

    season_arc_id: str
    title: str
    episode_ids: List[str] = Field(default_factory=list)
    midseason_turn: Optional[str] = None
    finale_payoff: Optional[str] = None
    character_arc_progression: Dict[str, Any] = Field(default_factory=dict)


class MultiBookArcDraft(BaseModel):
    model_config = ConfigDict(extra="allow")

    multi_book_arc_id: str
    title: str
    book_count: int = 1
    book_summaries: List[Dict[str, Any]] = Field(default_factory=list)
    saga_open_loops: List[str] = Field(default_factory=list)
    final_payoffs: List[str] = Field(default_factory=list)


class InteractiveSceneDraft(BaseModel):
    model_config = ConfigDict(extra="allow")

    interactive_scene_id: str
    scene_id: str
    setup_text: str
    choice_points: List[Dict[str, Any]] = Field(default_factory=list)
    branch_outcomes: Dict[str, Any] = Field(default_factory=dict)
    simulation_delta_candidates: List[Dict[str, Any]] = Field(default_factory=list)


class StoryQualityReport(BaseModel):
    model_config = ConfigDict(extra="allow")

    report_id: str
    draft_id: str
    overall_score: float = 0.0
    user_intent_match: float = 0.0
    character_specificity: float = 0.0
    voice_consistency: float = 0.0
    emotional_depth: float = 0.0
    causal_coherence: float = 0.0
    knowledge_correctness: float = 0.0
    relationship_progression: float = 0.0
    world_specificity: float = 0.0
    format_adherence: float = 0.0
    scene_momentum: float = 0.0
    dialogue_quality: float = 0.0
    commercial_potential: float = 0.0
    recommendations: List[str] = Field(default_factory=list)


class StoryAntiGenericityReport(BaseModel):
    model_config = ConfigDict(extra="allow")

    report_id: str
    draft_id: str
    anti_genericity_score: float = 0.0
    cliche_flags: List[str] = Field(default_factory=list)
    vague_emotion_flags: List[str] = Field(default_factory=list)
    generic_dialogue_flags: List[str] = Field(default_factory=list)
    weak_world_specificity_flags: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)


class StoryContinuityReport(BaseModel):
    model_config = ConfigDict(extra="allow")

    report_id: str
    draft_id: str
    valid: bool = True
    world_rule_violations: List[str] = Field(default_factory=list)
    character_state_violations: List[str] = Field(default_factory=list)
    relationship_state_violations: List[str] = Field(default_factory=list)
    knowledge_state_violations: List[str] = Field(default_factory=list)
    causal_violations: List[str] = Field(default_factory=list)
    format_violations: List[str] = Field(default_factory=list)


class OriginalityGuardReport(BaseModel):
    model_config = ConfigDict(extra="allow")

    report_id: str
    draft_id: str
    safe: bool = True
    copy_risk_score: float = 0.0
    raw_source_text_detected: bool = False
    excessive_imitation_flags: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)


class RewriteInstruction(BaseModel):
    model_config = ConfigDict(extra="allow")

    instruction_id: str
    target_draft_id: str
    issue_type: str
    instruction: str
    priority: int = 1
    source_report_id: Optional[str] = None


class RewritePlan(BaseModel):
    model_config = ConfigDict(extra="allow")

    rewrite_plan_id: str
    target_draft_id: str
    instructions: List[RewriteInstruction] = Field(default_factory=list)
    expected_improvements: List[str] = Field(default_factory=list)
    requires_regeneration: bool = False


class DraftComparisonReport(BaseModel):
    model_config = ConfigDict(extra="allow")

    comparison_report_id: str
    draft_ids: List[str] = Field(default_factory=list)
    best_draft_id: Optional[str] = None
    ranking: List[Dict[str, Any]] = Field(default_factory=list)
    selection_reason: Optional[str] = None


class StoryProvenanceRecord(BaseModel):
    model_config = ConfigDict(extra="allow")

    provenance_id: str
    draft_id: str
    simulation_id: Optional[str] = None
    run_id: Optional[str] = None
    handoff_package_id: Optional[str] = None
    generation_contract_id: Optional[str] = None
    character_ids_used: List[str] = Field(default_factory=list)
    relationship_ids_used: List[str] = Field(default_factory=list)
    secret_ids_referenced: List[str] = Field(default_factory=list)
    evidence_ids_referenced: List[str] = Field(default_factory=list)
    causal_node_ids_used: List[str] = Field(default_factory=list)
    validators_run: List[str] = Field(default_factory=list)
    rewrite_passes: int = 0
    quality_report_ids: List[str] = Field(default_factory=list)


class GeneratedSceneDelta(BaseModel):
    model_config = ConfigDict(extra="allow")

    generated_delta_id: str
    draft_id: str
    scene_id: str
    delta_type: str
    target_entity_id: str
    proposed_change: Dict[str, Any] = Field(default_factory=dict)
    confidence: float = 0.5
    requires_user_approval: bool = True


class StoryMemoryUpdateContract(BaseModel):
    model_config = ConfigDict(extra="allow")

    memory_update_contract_id: str
    draft_id: str
    confirmed_changes: List[GeneratedSceneDelta] = Field(default_factory=list)
    possible_changes: List[GeneratedSceneDelta] = Field(default_factory=list)
    requires_user_approval: bool = True
    simulation_delta_candidates: List[Dict[str, Any]] = Field(default_factory=list)
    memory_summary: str = ""
    continuation_anchors: List[str] = Field(default_factory=list)
    open_loops: List[str] = Field(default_factory=list)


class AdaptiveLearningSignal(BaseModel):
    model_config = ConfigDict(extra="allow")

    signal_id: str
    source_draft_id: Optional[str] = None
    signal_type: str
    target_area: str
    value: float = 0.0
    label: str = ""
    features: Dict[str, Any] = Field(default_factory=dict)
    abstract_learning_only: bool = True
    contains_source_text: bool = False
    requires_human_review: bool = False

    @field_validator("value")
    @classmethod
    def learning_value_bounded(cls, value: float) -> float:
        return max(0.0, min(1.0, float(value)))


class StoryGenerationRun(BaseModel):
    model_config = ConfigDict(extra="allow")

    run_id: str
    story_intent: StoryIntent
    generation_contract: Optional[GenerationContract] = None
    context_package_id: Optional[str] = None
    generated_draft_ids: List[str] = Field(default_factory=list)
    selected_draft_id: Optional[str] = None
    quality_report_ids: List[str] = Field(default_factory=list)
    continuity_report_ids: List[str] = Field(default_factory=list)
    anti_genericity_report_ids: List[str] = Field(default_factory=list)
    provenance_ids: List[str] = Field(default_factory=list)
    memory_update_contract_ids: List[str] = Field(default_factory=list)
    status: DraftStatus = DraftStatus.planned
    warnings: List[str] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)


class StoryExportBundle(BaseModel):
    model_config = ConfigDict(extra="allow")

    export_bundle_id: str
    run_id: str
    draft_ids: List[str] = Field(default_factory=list)
    export_format: str = "markdown"
    export_paths: List[str] = Field(default_factory=list)
    included_report_ids: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

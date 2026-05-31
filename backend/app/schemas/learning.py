from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import uuid4

from pydantic import BaseModel, Field


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class DatasetProvenanceRecord(BaseModel):
    """Tracks where a learned/generated pattern came from.

    This is required so future training never becomes an untraceable black box.
    Every learned type, ontology label, and generated training candidate should
    keep source, license, review, and eligibility metadata.
    """

    provenance_id: str = Field(default_factory=lambda: f"prov_{uuid4().hex[:12]}")
    source_name: str = "unknown"
    source_type: str = "unknown"
    source_uri: Optional[str] = None
    dataset_family: str = "general"
    license_status: str = "unknown"
    usage_allowed: bool = False
    human_review_required: bool = True
    sensitive_content_flags: List[str] = Field(default_factory=list)
    genre_tags: List[str] = Field(default_factory=list)
    culture_tags: List[str] = Field(default_factory=list)
    language: str = "unknown"
    created_at: str = Field(default_factory=utc_now_iso)


class EmbeddingMetadata(BaseModel):
    """Metadata for embedding-indexed ontology or training items."""

    embedding_id: str = Field(default_factory=lambda: f"emb_{uuid4().hex[:12]}")
    vector_store: str = "local_or_future_vector_store"
    embedding_model: str = "not_computed_yet"
    embedding_dimension: Optional[int] = None
    similarity_tags: List[str] = Field(default_factory=list)
    nearest_neighbor_ids: List[str] = Field(default_factory=list)
    novelty_score: float = 0.0
    originality_score: float = 0.0
    similarity_threshold_used: float = 0.8
    created_at: str = Field(default_factory=utc_now_iso)


class TrainingEligibility(BaseModel):
    """Controls whether something can be used for future training."""

    eligibility_id: str = Field(default_factory=lambda: f"elig_{uuid4().hex[:12]}")
    training_eligible: bool = False
    human_review_required: bool = True
    do_not_train: bool = True
    recommended_split: str = "human_review_queue"
    quality_score: float = 0.0
    consistency_score: float = 0.0
    originality_score: float = 0.0
    safety_score: float = 0.0
    minimum_quality_threshold: float = 0.75
    rejection_reasons: List[str] = Field(default_factory=list)
    approval_notes: List[str] = Field(default_factory=list)
    created_at: str = Field(default_factory=utc_now_iso)


class HumanFeedbackRecord(BaseModel):
    """Stores user/human feedback for continuous learning."""

    feedback_id: str = Field(default_factory=lambda: f"fb_{uuid4().hex[:12]}")
    target_id: str
    target_type: str
    rating: Optional[float] = None
    feedback_text: Optional[str] = None
    accepted: Optional[bool] = None
    edited_by_human: bool = False
    edit_summary: Optional[str] = None
    improvement_tags: List[str] = Field(default_factory=list)
    created_at: str = Field(default_factory=utc_now_iso)


class LearnedOntologyRecord(BaseModel):
    """A scalable learned ontology item.

    This record is intentionally generic so the same structure can represent
    people types, skills, powers, cultures, worlds, emotions, relationship
    patterns, plot beats, dialogue voices, moral dilemmas, and more.
    """

    ontology_id: str = Field(default_factory=lambda: f"onto_{uuid4().hex[:12]}")
    ontology_type: str
    name: str
    family: str
    subtype: str = "general"
    description: str = ""
    axes: Dict[str, Any] = Field(default_factory=dict)
    tags: List[str] = Field(default_factory=list)
    examples: List[str] = Field(default_factory=list)
    counterexamples: List[str] = Field(default_factory=list)
    source_provenance_ids: List[str] = Field(default_factory=list)
    embedding_id: Optional[str] = None
    confidence_score: float = 0.0
    novelty_score: float = 0.0
    quality_score: float = 0.0
    usage_count: int = 0
    learned_from_data: bool = False
    generated_by_engine: Optional[str] = None
    created_at: str = Field(default_factory=utc_now_iso)
    updated_at: str = Field(default_factory=utc_now_iso)


class LearnedTypeRegistryRecord(BaseModel):
    """Registry entry for a reusable learned/generated type."""

    registry_id: str = Field(default_factory=lambda: f"ltype_{uuid4().hex[:12]}")
    type_name: str
    type_family: str
    type_subfamily: str = "general"
    type_scope: str = "character"
    ontology_ids: List[str] = Field(default_factory=list)
    embedding_metadata: Optional[EmbeddingMetadata] = None
    provenance_records: List[DatasetProvenanceRecord] = Field(default_factory=list)
    training_eligibility: TrainingEligibility = Field(default_factory=TrainingEligibility)
    human_feedback: List[HumanFeedbackRecord] = Field(default_factory=list)
    reusable_prompt_tags: List[str] = Field(default_factory=list)
    generation_constraints: List[str] = Field(default_factory=list)
    counter_patterns: List[str] = Field(default_factory=list)
    learned_axes: Dict[str, Any] = Field(default_factory=dict)
    active: bool = True
    created_at: str = Field(default_factory=utc_now_iso)
    updated_at: str = Field(default_factory=utc_now_iso)


class EngineLearningMetadata(BaseModel):
    """Learning metadata attached to any engine result.

    Future orchestrators should attach this to world, character, relationship,
    plot, dialogue, and training outputs.
    """

    learning_metadata_id: str = Field(default_factory=lambda: f"learn_{uuid4().hex[:12]}")
    engine_name: str
    target_object_id: str
    target_object_type: str
    ontology_records: List[LearnedOntologyRecord] = Field(default_factory=list)
    learned_type_candidates: List[LearnedTypeRegistryRecord] = Field(default_factory=list)
    provenance_records: List[DatasetProvenanceRecord] = Field(default_factory=list)
    embedding_metadata: Optional[EmbeddingMetadata] = None
    training_eligibility: TrainingEligibility = Field(default_factory=TrainingEligibility)
    feedback_records: List[HumanFeedbackRecord] = Field(default_factory=list)
    retrieval_context_used: List[str] = Field(default_factory=list)
    generated_training_labels: Dict[str, Any] = Field(default_factory=dict)
    learning_notes: List[str] = Field(default_factory=list)
    created_at: str = Field(default_factory=utc_now_iso)


class ContinuousLearningEvent(BaseModel):
    """A future event for updating ontology, embeddings, and training queues."""

    event_id: str = Field(default_factory=lambda: f"clearn_{uuid4().hex[:12]}")
    event_type: str
    target_id: str
    target_type: str
    source_engine: str
    action: str
    payload: Dict[str, Any] = Field(default_factory=dict)
    should_update_registry: bool = False
    should_update_embedding_index: bool = False
    should_enter_training_queue: bool = False
    human_review_required: bool = True
    created_at: str = Field(default_factory=utc_now_iso)

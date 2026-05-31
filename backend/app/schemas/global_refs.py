from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import uuid4

from pydantic import BaseModel, Field


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class EntityType(str, Enum):
    PROJECT = "project"
    UNIVERSE = "universe"
    WORLD = "world"
    CHARACTER = "character"
    FACTION = "faction"
    LOCATION = "location"
    INSTITUTION = "institution"
    FAMILY = "family"
    OBJECT = "object"
    RESOURCE = "resource"
    LAW = "law"
    POWER_RULE = "power_rule"
    RELATIONSHIP = "relationship"
    SECRET = "secret"
    EVIDENCE = "evidence"
    RUMOR = "rumor"
    PROMISE = "promise"
    DEBT = "debt"
    OATH = "oath"
    EVENT = "event"
    CHOICE = "choice"
    CONSEQUENCE = "consequence"
    CAUSAL_NODE = "causal_node"
    SCENE = "scene"
    PLOT_BEAT = "plot_beat"
    GENRE_MODE = "genre_mode"
    ADAPTATION_ASSET = "adaptation_asset"
    DATASET = "dataset"
    MODEL = "model"
    EMBEDDING = "embedding"
    TRAINING_RECORD = "training_record"
    ARTIFACT = "artifact"


class CanonStatus(str, Enum):
    DRAFT = "draft"
    CANDIDATE = "candidate"
    CANON = "canon"
    ALTERNATE_BRANCH = "alternate_branch"
    REJECTED = "rejected"
    RETCONNED = "retconned"
    DEPRECATED = "deprecated"


class ReviewStatus(str, Enum):
    NOT_REQUIRED = "not_required"
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    NEEDS_REVISION = "needs_revision"


class EntityRef(BaseModel):
    entity_type: EntityType
    entity_id: str
    display_name: Optional[str] = None
    project_id: Optional[str] = None
    universe_id: Optional[str] = None
    canon_status: CanonStatus = CanonStatus.DRAFT
    branch_id: Optional[str] = None
    timeline_id: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ProjectUniverseRef(BaseModel):
    project_id: str = "default_project"
    universe_id: str = "default_universe"
    branch_id: str = "main"
    timeline_id: str = "main"
    canon_status: CanonStatus = CanonStatus.DRAFT


class ArtifactRef(BaseModel):
    artifact_id: str = Field(default_factory=lambda: f"artifact_{uuid4().hex[:12]}")
    artifact_type: str
    project_id: str = "default_project"
    universe_id: str = "default_universe"
    source_engine: str
    storage_path: Optional[str] = None
    canon_status: CanonStatus = CanonStatus.DRAFT
    branch_id: Optional[str] = None
    timeline_id: Optional[str] = None
    provenance_ids: List[str] = Field(default_factory=list)
    learning_metadata_ids: List[str] = Field(default_factory=list)
    created_at: str = Field(default_factory=utc_now)


class BranchRef(BaseModel):
    branch_id: str = "main"
    parent_branch_id: Optional[str] = None
    branch_reason: Optional[str] = None
    divergence_event_id: Optional[str] = None
    chosen_choice_id: Optional[str] = None
    rejected_choice_ids: List[str] = Field(default_factory=list)
    canon_status: CanonStatus = CanonStatus.DRAFT


class TimelineRef(BaseModel):
    timeline_id: str = "main"
    tick_number: int = 0
    event_order: List[str] = Field(default_factory=list)
    current_event_id: Optional[str] = None
    branch_id: str = "main"


class StateSnapshotRef(BaseModel):
    snapshot_id: str = Field(default_factory=lambda: f"snapshot_{uuid4().hex[:12]}")
    simulation_id: Optional[str] = None
    tick_number: int = 0
    state_hash: Optional[str] = None
    created_after_event_id: Optional[str] = None
    rollback_allowed: bool = True
    created_at: str = Field(default_factory=utc_now)

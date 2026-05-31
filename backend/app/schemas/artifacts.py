from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import uuid4

from pydantic import BaseModel, Field

from backend.app.schemas.global_refs import ArtifactRef, CanonStatus, EntityRef


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class ArtifactRecord(BaseModel):
    artifact_id: str = Field(default_factory=lambda: f"artifact_{uuid4().hex[:12]}")
    artifact_type: str
    project_id: str = "default_project"
    universe_id: str = "default_universe"
    source_engine: str
    source_entity_refs: List[EntityRef] = Field(default_factory=list)
    storage_path: Optional[str] = None
    artifact_ref: Optional[ArtifactRef] = None
    version: str = "0.1.0"
    canon_status: CanonStatus = CanonStatus.DRAFT
    branch_id: str = "main"
    timeline_id: str = "main"
    provenance_ids: List[str] = Field(default_factory=list)
    learning_metadata_ids: List[str] = Field(default_factory=list)
    quality_scores: Dict[str, float] = Field(default_factory=dict)
    tags: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: str = Field(default_factory=utc_now)


class ArtifactRegistrySummary(BaseModel):
    project_id: str = "default_project"
    universe_id: str = "default_universe"
    artifact_count: int = 0
    artifact_types: Dict[str, int] = Field(default_factory=dict)
    canon_count: int = 0
    draft_count: int = 0
    branch_count: int = 0
    latest_artifact_ids: List[str] = Field(default_factory=list)

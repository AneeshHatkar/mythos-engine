from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import uuid4

from pydantic import BaseModel, Field


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def new_id(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex[:12]}"


class HealthResponse(BaseModel):
    app_name: str
    app_version: str
    environment: str
    status: str


class RootResponse(BaseModel):
    name: str
    version: str
    message: str
    route_groups: List[str]


class EngineRunResult(BaseModel):
    success: bool
    engine_name: str
    data: Dict[str, Any] = Field(default_factory=dict)
    warnings: List[str] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)
    audit_id: Optional[str] = None
    version_id: Optional[str] = None
    generated_object_ids: List[str] = Field(default_factory=list)


class ProjectCreate(BaseModel):
    name: str = Field(min_length=1, max_length=160)
    description: str = Field(default="", max_length=2000)
    project_mode: str = Field(default="story_universe_and_adaptation")
    target_use: str = Field(default="personal_research_and_ip_development")
    default_content_profile: str = Field(default="teen_to_mature")


class ProjectRead(BaseModel):
    project_id: str
    name: str
    description: str
    project_mode: str
    target_use: str
    default_content_profile: str
    status: str = "active"
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)


class UniverseCreate(BaseModel):
    project_id: str
    name: str = Field(min_length=1, max_length=160)
    seed_premise: str = Field(default="", max_length=5000)
    genres: List[str] = Field(default_factory=list)
    tone: str = Field(default="epic, emotional, intelligent")
    scale_preference: str = Field(default="large")
    target_formats: List[str] = Field(default_factory=lambda: ["novel_series"])


class UniverseRead(BaseModel):
    universe_id: str
    project_id: str
    name: str
    seed_premise: str
    genres: List[str]
    tone: str
    scale_preference: str
    target_formats: List[str]
    status: str = "draft"
    canon_status: str = "draft"
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)


class RegistryTypeCreate(BaseModel):
    type_id: str = Field(min_length=3, max_length=180)
    category: str = Field(min_length=1, max_length=120)
    name: str = Field(min_length=1, max_length=180)
    description: str = Field(default="", max_length=5000)
    tags: List[str] = Field(default_factory=list)
    compatible_with: List[str] = Field(default_factory=list)
    conflicts_with: List[str] = Field(default_factory=list)
    risk_notes: List[str] = Field(default_factory=list)
    example_output: str = Field(default="", max_length=3000)
    created_by: str = "system"


class RegistryTypeRead(RegistryTypeCreate):
    registry_id: str
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)


class VersionRecordCreate(BaseModel):
    project_id: str
    universe_id: Optional[str] = None
    object_type: str
    object_id: str
    version_label: str = "v0.1"
    summary: str = ""
    parent_version_id: Optional[str] = None
    canon_status: str = "draft"
    snapshot: Dict[str, Any] = Field(default_factory=dict)


class VersionRecordRead(VersionRecordCreate):
    version_id: str
    created_at: datetime = Field(default_factory=utc_now)


class AuditRecordCreate(BaseModel):
    project_id: str
    universe_id: Optional[str] = None
    engine_name: str
    event_type: str = "engine_run"
    input_summary: str = ""
    output_summary: str = ""
    model_provider: str = "none"
    model_name: str = "rule_based_v0"
    parameters: Dict[str, Any] = Field(default_factory=dict)
    warnings: List[str] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)
    quality_score: Optional[float] = None


class AuditRecordRead(AuditRecordCreate):
    audit_id: str
    created_at: datetime = Field(default_factory=utc_now)


class FeedbackRecordCreate(BaseModel):
    project_id: str
    universe_id: Optional[str] = None
    object_type: str
    object_id: str
    feedback_type: str
    rating: Optional[int] = Field(default=None, ge=1, le=10)
    comment: str = ""
    future_use: str = "preference_learning_later"


class FeedbackRecordRead(FeedbackRecordCreate):
    feedback_id: str
    created_at: datetime = Field(default_factory=utc_now)


class ExportRecordCreate(BaseModel):
    project_id: str
    universe_id: Optional[str] = None
    export_type: str = "json_state"
    object_scope: str = "project"
    file_path: str = ""
    summary: str = ""


class ExportRecordRead(ExportRecordCreate):
    export_id: str
    created_at: datetime = Field(default_factory=utc_now)

class CanonLockCreate(BaseModel):
    project_id: str
    universe_id: Optional[str] = None
    object_type: str
    object_id: str
    field_path: str = Field(
        default="*",
        description="Specific field to lock, or * to lock the whole object.",
    )
    locked_value: Dict[str, Any] = Field(default_factory=dict)
    reason: str = ""
    locked_by: str = "user"


class CanonLockRead(CanonLockCreate):
    canon_lock_id: str
    status: str = "locked"
    created_at: datetime = Field(default_factory=utc_now)


class BranchCreate(BaseModel):
    project_id: str
    universe_id: str
    branch_name: str = Field(min_length=1, max_length=180)
    branch_type: str = Field(default="alternate_timeline")
    parent_branch_id: Optional[str] = None
    reason: str = ""
    canon_status: str = "alternate_timeline"


class BranchRead(BranchCreate):
    branch_id: str
    status: str = "active"
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import uuid4

from pydantic import BaseModel, Field

from backend.app.schemas.global_refs import BranchRef, CanonStatus, StateSnapshotRef, TimelineRef


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class BranchRecord(BaseModel):
    branch_id: str = Field(default_factory=lambda: f"branch_{uuid4().hex[:12]}")
    parent_branch_id: Optional[str] = None
    branch_name: str = "untitled_branch"
    branch_reason: str = ""
    divergence_event_id: Optional[str] = None
    chosen_choice_id: Optional[str] = None
    rejected_choice_ids: List[str] = Field(default_factory=list)
    canon_status: CanonStatus = CanonStatus.DRAFT
    created_by_engine: str = "unknown_engine"
    created_at: str = Field(default_factory=utc_now)


class TimelineRecord(BaseModel):
    timeline_id: str = Field(default_factory=lambda: f"timeline_{uuid4().hex[:12]}")
    branch_id: str = "main"
    project_id: str = "default_project"
    universe_id: str = "default_universe"
    event_order: List[str] = Field(default_factory=list)
    current_tick: int = 0
    current_event_id: Optional[str] = None
    snapshot_refs: List[StateSnapshotRef] = Field(default_factory=list)
    timeline_hash: Optional[str] = None
    created_at: str = Field(default_factory=utc_now)


class TimelineBranchBundle(BaseModel):
    branch_ref: BranchRef
    timeline_ref: TimelineRef
    branch_record: Optional[BranchRecord] = None
    timeline_record: Optional[TimelineRecord] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

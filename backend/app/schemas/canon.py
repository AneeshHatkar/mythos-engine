from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import uuid4

from pydantic import BaseModel, Field

from backend.app.schemas.global_refs import CanonStatus, EntityRef


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class CanonLockType(str, Enum):
    ENTITY_EXISTENCE = "entity_existence"
    CHARACTER_DEATH = "character_death"
    RELATIONSHIP_STATE = "relationship_state"
    SECRET_STATUS = "secret_status"
    PROMISE_OUTCOME = "promise_outcome"
    EVENT_OUTCOME = "event_outcome"
    LOCATION_ACCESS = "location_access"
    POWER_RULE = "power_rule"
    TIMELINE_ORDER = "timeline_order"
    ROMANCE_BOUNDARY = "romance_boundary"


class CanonLock(BaseModel):
    lock_id: str = Field(default_factory=lambda: f"canonlock_{uuid4().hex[:12]}")
    lock_type: CanonLockType
    target_ref: EntityRef
    locked_value: Dict[str, Any] = Field(default_factory=dict)
    reason: str = ""
    created_by_engine: str = "unknown_engine"
    branch_id: str = "main"
    timeline_id: str = "main"
    can_override_with_retcon: bool = False
    created_at: str = Field(default_factory=utc_now)


class CanonStatusRecord(BaseModel):
    record_id: str = Field(default_factory=lambda: f"canonstatus_{uuid4().hex[:12]}")
    target_ref: EntityRef
    canon_status: CanonStatus = CanonStatus.DRAFT
    branch_id: str = "main"
    timeline_id: str = "main"
    promoted_by_engine: Optional[str] = None
    human_review_required: bool = False
    reason: str = ""
    related_lock_ids: List[str] = Field(default_factory=list)
    created_at: str = Field(default_factory=utc_now)


class CanonValidationResult(BaseModel):
    validation_id: str = Field(default_factory=lambda: f"canonval_{uuid4().hex[:12]}")
    valid: bool = True
    violations: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    blocked_by_lock_ids: List[str] = Field(default_factory=list)
    retcon_required: bool = False
    alternate_branch_recommended: bool = False

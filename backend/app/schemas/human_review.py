from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import uuid4

from pydantic import BaseModel, Field

from backend.app.schemas.global_refs import EntityRef, ReviewStatus


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class ReviewQueueType(str, Enum):
    TRAINING_APPROVAL = "training_approval"
    CANON_PROMOTION = "canon_promotion"
    COMMERCIAL_EXPORT = "commercial_export"
    DATASET_INGESTION = "dataset_ingestion"
    QUALITY_REVIEW = "quality_review"
    SAFETY_REVIEW = "safety_review"
    LEGAL_REVIEW = "legal_review"


class HumanReviewRecord(BaseModel):
    review_id: str = Field(default_factory=lambda: f"review_{uuid4().hex[:12]}")
    target_ref: EntityRef
    review_queue_type: ReviewQueueType
    review_status: ReviewStatus = ReviewStatus.PENDING
    review_reason: str
    review_priority: str = "medium"
    requested_by_engine: str = "unknown_engine"
    approved_by_human: Optional[str] = None
    rejected_by_human: Optional[str] = None
    notes: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: str = Field(default_factory=utc_now)
    reviewed_at: Optional[str] = None

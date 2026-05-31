from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import uuid4

from pydantic import BaseModel, Field


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class EngineErrorType(str, Enum):
    SCHEMA_VALIDATION_ERROR = "schema_validation_error"
    WORLD_CONTRACT_VIOLATION = "world_contract_violation"
    CHARACTER_CONSISTENCY_ERROR = "character_consistency_error"
    KNOWLEDGE_LEAK_ERROR = "knowledge_leak_error"
    CANON_LOCK_VIOLATION = "canon_lock_violation"
    STATE_DELTA_CONFLICT = "state_delta_conflict"
    PROVENANCE_BLOCKED = "provenance_blocked"
    TRAINING_NOT_ALLOWED = "training_not_allowed"
    LOW_QUALITY_OUTPUT = "low_quality_output"
    GENERICITY_FAILURE = "genericity_failure"
    UNKNOWN_ERROR = "unknown_error"


class EngineRunMetrics(BaseModel):
    metrics_id: str = Field(default_factory=lambda: f"metrics_{uuid4().hex[:12]}")
    engine_name: str
    runtime_ms: float = 0.0
    input_count: int = 0
    output_count: int = 0
    warnings_count: int = 0
    errors_count: int = 0
    quality_score: Optional[float] = None
    registered_to_learning: bool = False
    artifact_ids: List[str] = Field(default_factory=list)
    created_at: str = Field(default_factory=utc_now)


class EngineErrorRecord(BaseModel):
    error_id: str = Field(default_factory=lambda: f"error_{uuid4().hex[:12]}")
    engine_name: str = "unknown_engine"
    error_type: EngineErrorType = EngineErrorType.UNKNOWN_ERROR
    message: str
    target_object_id: Optional[str] = None
    recoverable: bool = True
    suggested_fix: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: str = Field(default_factory=utc_now)


class EngineWarningRecord(BaseModel):
    warning_id: str = Field(default_factory=lambda: f"warning_{uuid4().hex[:12]}")
    engine_name: str = "unknown_engine"
    message: str
    target_object_id: Optional[str] = None
    severity: str = "medium"
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: str = Field(default_factory=utc_now)


class EngineThresholdConfig(BaseModel):
    threshold_name: str
    value: float
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    description: str = ""


class EngineConfigRecord(BaseModel):
    config_id: str = Field(default_factory=lambda: f"engineconfig_{uuid4().hex[:12]}")
    engine_name: str
    config_version: str = "0.1.0"
    thresholds: Dict[str, EngineThresholdConfig] = Field(default_factory=dict)
    weights: Dict[str, float] = Field(default_factory=dict)
    flags: Dict[str, bool] = Field(default_factory=dict)
    notes: List[str] = Field(default_factory=list)
    created_at: str = Field(default_factory=utc_now)

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import uuid4

from pydantic import BaseModel, Field


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class InvariantType(str, Enum):
    NO_MAGIC_KNOWLEDGE = "no_magic_knowledge"
    NO_CONSEQUENCE_FREE_MAJOR_CHOICE = "no_consequence_free_major_choice"
    NO_RELATIONSHIP_JUMP_WITHOUT_CAUSE = "no_relationship_jump_without_cause"
    NO_CANON_VIOLATION = "no_canon_violation"
    NO_WORLD_CONTRACT_VIOLATION = "no_world_contract_violation"
    NO_TRAINING_WITHOUT_PROVENANCE = "no_training_without_provenance"


class BenchmarkLabel(str, Enum):
    KNOWLEDGE_CONSISTENCY = "knowledge_consistency"
    RELATIONSHIP_BELIEVABILITY = "relationship_believability"
    AGENCY_VALIDITY = "agency_validity"
    CAUSAL_COHERENCE = "causal_coherence"
    CONSEQUENCE_STRENGTH = "consequence_strength"
    TENSION_CURVE = "tension_curve"
    WORLD_CONTRACT_COMPLIANCE = "world_contract_compliance"
    CHARACTER_CONSISTENCY = "character_consistency"
    NON_GENERICITY = "non_genericity"
    TRAINING_ELIGIBILITY = "training_eligibility"


class ExpectedBehavior(BaseModel):
    expected_deltas: List[Dict[str, Any]] = Field(default_factory=list)
    expected_blockers: List[str] = Field(default_factory=list)
    expected_quality_labels: List[BenchmarkLabel] = Field(default_factory=list)
    expected_causal_explanation_contains: List[str] = Field(default_factory=list)
    expected_invariant_results: Dict[InvariantType, bool] = Field(default_factory=dict)


class EvaluationCase(BaseModel):
    case_id: str = Field(default_factory=lambda: f"evalcase_{uuid4().hex[:12]}")
    case_name: str
    dataset_family: str = "simulation"
    input_state: Dict[str, Any] = Field(default_factory=dict)
    event_payload: Dict[str, Any] = Field(default_factory=dict)
    expected_behavior: ExpectedBehavior = Field(default_factory=ExpectedBehavior)
    benchmark_labels: List[BenchmarkLabel] = Field(default_factory=list)
    difficulty: str = "medium"
    created_at: str = Field(default_factory=utc_now)


class InvariantCheckResult(BaseModel):
    invariant_id: str = Field(default_factory=lambda: f"invariant_{uuid4().hex[:12]}")
    invariant_type: InvariantType
    passed: bool
    severity: str = "medium"
    message: str = ""
    evidence: Dict[str, Any] = Field(default_factory=dict)
    suggested_fix: Optional[str] = None
    created_at: str = Field(default_factory=utc_now)


class QualityGateResult(BaseModel):
    gate_id: str = Field(default_factory=lambda: f"qualitygate_{uuid4().hex[:12]}")
    gate_name: str
    passed: bool
    score: Optional[float] = None
    threshold: Optional[float] = None
    blockers: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    created_at: str = Field(default_factory=utc_now)

from pydantic import BaseModel, Field
from datetime import datetime, timezone
from typing import Any, Dict
from uuid import uuid4

from fastapi import APIRouter

from backend.app.services.world_learning_adapter import WorldLearningAdapter
from backend.app.engines.world.embedding_originality_engine import EmbeddingOriginalityEngine
from backend.app.engines.world.world_orchestrator_engine import WorldOrchestratorEngine
from backend.app.engines.world.world_quality_engine import WorldQualityEngine
from backend.app.engines.world.world_template_engine import WorldTemplateEngine
from backend.app.services.world_run_store import world_run_store


router = APIRouter(prefix="/world/engines", tags=["World Engines"])

template_engine = WorldTemplateEngine()
quality_engine = WorldQualityEngine()
orchestrator_engine = WorldOrchestratorEngine()
embedding_originality_engine = EmbeddingOriginalityEngine()


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _input_summary(payload: Dict[str, Any]) -> str:
    seed = payload.get("seed_premise", "")
    template_id = payload.get("template_id")
    world_name = payload.get("world_name") or payload.get("name")

    parts = []

    if world_name:
        parts.append(f"world_name={world_name}")

    if template_id:
        parts.append(f"template_id={template_id}")

    if seed:
        compact_seed = seed[:180].replace("\n", " ")
        parts.append(f"seed_premise={compact_seed}")

    if not parts:
        return "No explicit seed/template/world name provided."

    return "; ".join(parts)


def _output_summary(result_data: Dict[str, Any]) -> str:
    orchestration_summary = result_data.get("orchestration_summary", {})
    world_state = result_data.get("world_state", {})
    quality_summary = world_state.get("quality_summary", {})
    export_package = world_state.get("world_bible_export", {})

    engine_count = orchestration_summary.get("engine_count")
    quality_tier = quality_summary.get("quality_tier")
    export_id = export_package.get("export_id")

    return (
        f"engine_count={engine_count}; "
        f"quality_tier={quality_tier}; "
        f"export_id={export_id}"
    )


def _quality_score(result_data: Dict[str, Any]) -> float:
    world_state = result_data.get("world_state", {})
    quality_summary = world_state.get("quality_summary", {})

    scores = [
        quality_summary.get("consistency_score"),
        quality_summary.get("originality_score"),
        quality_summary.get("story_potential_score"),
        quality_summary.get("training_readiness_score"),
    ]

    numeric_scores = [
        float(score)
        for score in scores
        if isinstance(score, (int, float))
    ]

    if not numeric_scores:
        return 0.0

    return round(sum(numeric_scores) / len(numeric_scores), 3)


def _build_audit_integration(
    *,
    engine_name: str,
    event_type: str,
    payload: Dict[str, Any],
    result_success: bool,
    result_data: Dict[str, Any],
    warning_count: int,
    error_count: int,
) -> Dict[str, Any]:
    quality_score = _quality_score(result_data)

    return {
        "audit_id": f"aud_api_{uuid4().hex[:12]}",
        "created_at": _utc_now(),
        "engine_name": engine_name,
        "event_type": event_type,
        "status": "success" if result_success else "failed",
        "input_summary": _input_summary(payload),
        "output_summary": _output_summary(result_data),
        "quality_score": quality_score,
        "warning_count": warning_count,
        "error_count": error_count,
        "store_recommendation": {
            "store_in_audit_table": True,
            "store_in_version_table": event_type == "world_orchestration_run",
            "notes": [
                "This is audit-ready metadata returned by the API layer.",
                "Future persistence can write this into Chunk 1 audit/version storage.",
                "No model training occurs during this API call.",
            ],
        },
    }


@router.get("/health")
def world_engine_health() -> Dict[str, Any]:
    return {
        "status": "ok",
        "service": "world_engine_api",
        "available_endpoints": [
            "GET /world/engines/health",
            "GET /world/engines/templates",
            "POST /world/engines/orchestrate",
            "POST /world/engines/quality",
            "POST /world/engines/originality",
        ],
    }


@router.get("/templates")
def list_world_templates() -> Dict[str, Any]:
    result = template_engine.run({})

    return {
        "success": result.success,
        "data": result.data,
        "warnings": result.warnings,
        "errors": result.errors,
    }


@router.post("/quality")
def score_world_quality(payload: Dict[str, Any]) -> Dict[str, Any]:
    result = quality_engine.run(payload)

    audit_integration = _build_audit_integration(
        engine_name=result.engine_name,
        event_type="world_quality_scoring_run",
        payload=payload,
        result_success=result.success,
        result_data=result.data,
        warning_count=len(result.warnings),
        error_count=len(result.errors),
    )

    return {
        "success": result.success,
        "engine_name": result.engine_name,
        "data": result.data,
        "warnings": result.warnings,
        "errors": result.errors,
        "audit_integration": audit_integration,
    }




@router.post("/originality")
def score_world_originality(payload: Dict[str, Any]) -> Dict[str, Any]:
    result = embedding_originality_engine.run(payload)

    audit_integration = _build_audit_integration(
        engine_name=result.engine_name,
        event_type="world_embedding_originality_run",
        payload=payload,
        result_success=result.success,
        result_data=result.data,
        warning_count=len(result.warnings),
        error_count=len(result.errors),
    )

    return {
        "success": result.success,
        "engine_name": result.engine_name,
        "data": result.data,
        "warnings": result.warnings,
        "errors": result.errors,
        "audit_integration": audit_integration,
    }

@router.post("/orchestrate")
def orchestrate_world(payload: Dict[str, Any]) -> Dict[str, Any]:
    result = orchestrator_engine.run(payload)

    audit_integration = _build_audit_integration(
        engine_name=result.engine_name,
        event_type="world_orchestration_run",
        payload=payload,
        result_success=result.success,
        result_data=result.data,
        warning_count=len(result.warnings),
        error_count=len(result.errors),
    )

    response_data = dict(result.data)
    response_data["audit_integration"] = audit_integration

    persisted_run = world_run_store.save_orchestration_run(
        payload=payload,
        result_data=response_data,
        audit_metadata=audit_integration,
        status="success" if result.success else "failed",
    )

    persistence = {
        "persisted": True,
        "run_id": persisted_run["run_id"],
        "created_at": persisted_run["created_at"],
        "snapshot_id": persisted_run.get("snapshot_id"),
        "export_id": persisted_run.get("export_id"),
    }

    response_data["persistence"] = persistence

    return {
        "success": result.success,
        "engine_name": result.engine_name,
        "data": response_data,
        "warnings": result.warnings,
        "errors": result.errors,
        "generated_object_ids": result.generated_object_ids,
        "audit_integration": audit_integration,
        "persistence": persistence,
    }


@router.get("/runs")
def list_world_generation_runs(
    project_id: str | None = None,
    universe_id: str | None = None,
    template_id: str | None = None,
    limit: int = 20,
) -> Dict[str, Any]:
    runs = world_run_store.list_runs(
        project_id=project_id,
        universe_id=universe_id,
        template_id=template_id,
        limit=limit,
    )

    return {
        "success": True,
        "count": len(runs),
        "runs": runs,
    }


@router.get("/runs/{run_id}")
def get_world_generation_run(run_id: str) -> Dict[str, Any]:
    run = world_run_store.get_run(run_id)

    if run is None:
        return {
            "success": False,
            "error": f"World generation run not found: {run_id}",
        }

    return {
        "success": True,
        "run": run,
    }

# ---------------------------------------------------------------------------
# Upgrade Pass B: World global learning registration routes
# ---------------------------------------------------------------------------

class WorldLearningRegistrationRequest(BaseModel):
    result_payload: Dict[str, Any] = Field(default_factory=dict)
    project_id: str = "default_project"
    universe_id: str = "default_universe"
    source_payload: Dict[str, Any] = Field(default_factory=dict)
    enforce_quality_gates: bool = True


class WorldProfileLearningRegistrationRequest(BaseModel):
    world_profile: Dict[str, Any] = Field(default_factory=dict)
    project_id: str = "default_project"
    universe_id: str = "default_universe"
    enforce_quality_gates: bool = True


def _world_learning_adapter() -> WorldLearningAdapter:
    return WorldLearningAdapter()


@router.post("/learning/register-result")
def register_world_engine_result_to_learning(request: WorldLearningRegistrationRequest) -> Dict[str, Any]:
    """Register an existing world engine result into the global learning foundation.

    This endpoint is intentionally separate from the existing world engine routes so
    older Chunk 2 routes stay backward-compatible. Pass B/C can later call this
    internally from orchestration routes.
    """

    result = _world_learning_adapter().register_world_engine_result(
        result_payload=request.result_payload,
        project_id=request.project_id,
        universe_id=request.universe_id,
        source_payload=request.source_payload or None,
        enforce_quality_gates=request.enforce_quality_gates,
    )

    return {
        "success": True,
        "data": result,
    }


@router.post("/learning/register-profile")
def register_world_profile_to_learning(request: WorldProfileLearningRegistrationRequest) -> Dict[str, Any]:
    """Register learning metadata found inside a world profile/bible."""

    result = _world_learning_adapter().register_world_profile(
        world_profile=request.world_profile,
        project_id=request.project_id,
        universe_id=request.universe_id,
        enforce_quality_gates=request.enforce_quality_gates,
    )

    return {
        "success": True,
        "data": result,
    }


@router.post("/learning/contract")
def build_world_to_character_contract(request: WorldProfileLearningRegistrationRequest) -> Dict[str, Any]:
    """Build the dependency contract that Chunk 3/4 consume from a world profile."""

    contract = _world_learning_adapter().build_world_to_character_contract(request.world_profile)

    return {
        "success": True,
        "data": {
            "world_to_character_contract": contract,
        },
    }

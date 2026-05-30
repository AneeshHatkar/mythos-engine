from datetime import datetime, timezone
from typing import Any, Dict
from uuid import uuid4

from fastapi import APIRouter

from backend.app.engines.world.world_orchestrator_engine import WorldOrchestratorEngine
from backend.app.engines.world.world_quality_engine import WorldQualityEngine
from backend.app.engines.world.world_template_engine import WorldTemplateEngine


router = APIRouter(prefix="/world/engines", tags=["World Engines"])

template_engine = WorldTemplateEngine()
quality_engine = WorldQualityEngine()
orchestrator_engine = WorldOrchestratorEngine()


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

    return {
        "success": result.success,
        "engine_name": result.engine_name,
        "data": response_data,
        "warnings": result.warnings,
        "errors": result.errors,
        "generated_object_ids": result.generated_object_ids,
        "audit_integration": audit_integration,
    }

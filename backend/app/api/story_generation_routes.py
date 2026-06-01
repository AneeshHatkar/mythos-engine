from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter
from pydantic import BaseModel, Field

from backend.app.engines.story_generation.story_generation_orchestrator import StoryGenerationOrchestrator
from backend.app.schemas.story_generation import (
    DraftComparisonReport,
    GeneratedStoryDeltaReport,
    GenerationContract,
    GenerationImprovementLoopDecision,
    OriginalityCopyRiskReport,
    StoryAntiGenericityReport,
    StoryContinuityValidationReport,
    StoryGenerationOrchestrationReport,
    StoryMemoryUpdateContract,
    StoryProvenanceRecord,
    StoryQualityScoreReport,
    StoryRevisionPlan,
)

router = APIRouter(prefix="/story-generation", tags=["story-generation"])


class StoryGenerationOrchestrateRequest(BaseModel):
    """API request for orchestration state checks.

    This route intentionally accepts already-built artifacts. It does not run
    every generation engine yet; it verifies and packages the Chunk 5 state.
    """

    source_id: str = Field(default="api_story_source")
    request_id: str = Field(default="api_request")
    generation_contract: GenerationContract | None = None
    quality_report: StoryQualityScoreReport | None = None
    anti_genericity_report: StoryAntiGenericityReport | None = None
    continuity_report: StoryContinuityValidationReport | None = None
    originality_report: OriginalityCopyRiskReport | None = None
    revision_plan: StoryRevisionPlan | None = None
    comparison_report: DraftComparisonReport | None = None
    loop_decision: GenerationImprovementLoopDecision | None = None
    provenance_record: StoryProvenanceRecord | None = None
    delta_report: GeneratedStoryDeltaReport | None = None
    memory_update_contract: StoryMemoryUpdateContract | None = None
    story_context: Dict[str, Any] = Field(default_factory=dict)


class StoryGenerationValidateRequest(BaseModel):
    report: StoryGenerationOrchestrationReport


@router.get("/health")
def story_generation_health() -> Dict[str, Any]:
    return {
        "success": True,
        "service": "story-generation",
        "chunk": "5",
        "status": "available",
        "routes": [
            "GET /story-generation/health",
            "POST /story-generation/orchestrate",
            "POST /story-generation/validate-orchestration",
            "POST /story-generation/summarize-orchestration",
        ],
    }


@router.post("/orchestrate")
def orchestrate_story_generation(request: StoryGenerationOrchestrateRequest) -> Dict[str, Any]:
    orchestrator = StoryGenerationOrchestrator()

    result = orchestrator.orchestrate_generation_state(
        source_id=request.source_id,
        request_id=request.request_id,
        generation_contract=request.generation_contract,
        quality_report=request.quality_report,
        anti_genericity_report=request.anti_genericity_report,
        continuity_report=request.continuity_report,
        originality_report=request.originality_report,
        revision_plan=request.revision_plan,
        comparison_report=request.comparison_report,
        loop_decision=request.loop_decision,
        provenance_record=request.provenance_record,
        delta_report=request.delta_report,
        memory_update_contract=request.memory_update_contract,
        story_context=request.story_context,
    )

    report = result["story_generation_orchestration_report"]

    return {
        "success": True,
        "engine_name": result["engine_name"],
        "orchestration_report": report.model_dump(mode="json"),
        "handoff_to_next_engine": result["handoff_to_next_engine"],
    }


@router.post("/validate-orchestration")
def validate_story_generation_orchestration(request: StoryGenerationValidateRequest) -> Dict[str, Any]:
    orchestrator = StoryGenerationOrchestrator()
    return orchestrator.validate_orchestration_report(report=request.report)


@router.post("/summarize-orchestration")
def summarize_story_generation_orchestration(request: StoryGenerationValidateRequest) -> Dict[str, Any]:
    orchestrator = StoryGenerationOrchestrator()
    return orchestrator.summarize_orchestration_report(report=request.report)

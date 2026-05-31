from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.app.engines.simulation.interaction_simulation_orchestrator import InteractionSimulationOrchestrator
from backend.app.engines.simulation.simulation_anti_genericity_validator import SimulationAntiGenericityValidator
from backend.app.engines.simulation.simulation_quality_scorer import SimulationQualityScorer
from backend.app.engines.simulation.simulation_run_store import SimulationRunStore
from backend.app.schemas.simulation import (
    SimulationCharacterState,
    SimulationKnowledgeState,
    SimulationRelationshipState,
    SimulationState,
    SimulationWorldState,
)


router = APIRouter(prefix="/simulation", tags=["simulation"])


class SimulationRunRequest(BaseModel):
    run_id: str = Field(..., min_length=1)
    story_request: Dict[str, Any] = Field(default_factory=dict)
    event_specs: List[Dict[str, Any]] = Field(default_factory=list)
    candidate_ids: Optional[List[str]] = None
    target_cast_size: Optional[int] = None
    initial_state: Optional[Dict[str, Any]] = None


def _default_state() -> SimulationState:
    return SimulationState(
        simulation_id="sim_api_default",
        world_state=SimulationWorldState(
            world_id="world_velmora",
            metadata={
                "world_rules": {"oath_court": "public proof changes status"},
                "locations": ["location_court"],
                "factions": ["faction_oath_court"],
                "culture": {"law": "truth has cost"},
            },
        ),
        character_states={
            "char_kael": SimulationCharacterState(
                character_id="char_kael",
                current_location_id="location_court",
                metadata={
                    "display_name": "Kael",
                    "role_tags": ["protagonist", "destined_person"],
                    "story_function_tags": ["drive_plot", "reveal_truth"],
                    "source_type": "user_supplied_character",
                    "user_requested": True,
                    "destined_weight": 0.9,
                    "backstory": "Kael was disgraced by a corrupted ranking ritual.",
                    "goals": {"main": "prove the truth without losing his last ally"},
                    "psychology": {"core_wound": "public institutions can erase belonging"},
                    "voice_profile": {"style": "guarded, sharp, precise"},
                    "backstory_depth": 0.9,
                    "agency_score": 0.8,
                    "uniqueness_score": 0.85,
                    "reputation_state": {"public": 0.4},
                },
            ),
            "char_seren": SimulationCharacterState(
                character_id="char_seren",
                current_location_id="location_court",
                metadata={
                    "display_name": "Seren",
                    "role_tags": ["love_interest", "traitor"],
                    "story_function_tags": ["anchor_romance", "cause_betrayal", "test_loyalty"],
                    "source_type": "created_character",
                    "destined_weight": 0.7,
                    "backstory": "Seren serves the oath court to protect her younger brother.",
                    "goals": {"main": "protect the source and survive the court"},
                    "psychology": {"core_wound": "love becomes dangerous when duty watches"},
                    "voice_profile": {"style": "controlled, restrained, formal under stress"},
                    "backstory_depth": 0.85,
                    "agency_score": 0.7,
                    "uniqueness_score": 0.8,
                    "reputation_state": {"public": 0.35},
                },
            ),
            "char_vask": SimulationCharacterState(
                character_id="char_vask",
                current_location_id="location_court",
                metadata={
                    "display_name": "Vask",
                    "role_tags": ["antagonist", "faction_leader"],
                    "story_function_tags": ["create_conflict", "force_choice", "hold_secret"],
                    "source_type": "created_character",
                    "backstory": "Vask weaponizes public proof rituals.",
                    "goals": {"main": "keep the oath court ranking system untouched"},
                    "voice_profile": {"style": "polite institutional threat"},
                    "backstory_depth": 0.75,
                    "agency_score": 0.75,
                    "uniqueness_score": 0.7,
                    "reputation_state": {"public": 0.3},
                },
            ),
        },
        knowledge_states={
            "char_kael": SimulationKnowledgeState(
                entity_id="char_kael",
                known_secret_ids=["secret_rank_system_edited"],
                evidence_seen_ids=["evidence_cracked_badge"],
            ),
            "char_seren": SimulationKnowledgeState(
                entity_id="char_seren",
                suspected_secret_ids=["secret_rank_system_edited"],
            ),
        },
        relationship_states={
            "rel_char_kael_char_seren": SimulationRelationshipState(
                relationship_id="rel_char_kael_char_seren",
                character_a_id="char_kael",
                character_b_id="char_seren",
                trust=0.28,
                respect=0.55,
                affection=0.5,
                resentment=0.55,
                betrayal_risk=0.65,
                repair_potential=0.7,
                romantic_tension=0.5,
                power_imbalance=0.3,
                knowledge_asymmetry=0.6,
            )
        },
        metadata={
            "secret_registry": {
                "secret_rank_system_edited": {"secret_id": "secret_rank_system_edited"}
            },
            "evidence_registry": {
                "evidence_cracked_badge": {"evidence_id": "evidence_cracked_badge"}
            },
        },
    )


def _state_from_payload(payload: Optional[Dict[str, Any]]) -> SimulationState:
    if not payload:
        return _default_state()
    return SimulationState.model_validate(payload)


def _state_to_dict(state: SimulationState) -> Dict[str, Any]:
    return state.model_dump(mode="json")


@router.get("/health")
def simulation_health() -> Dict[str, Any]:
    return {
        "status": "ok",
        "service": "mythos-simulation",
        "chunk": "4",
        "routes": [
            "POST /simulation/run",
            "GET /simulation/runs",
            "GET /simulation/runs/{run_id}",
            "GET /simulation/runs/{run_id}/summary",
            "POST /simulation/runs/{run_id}/quality",
            "POST /simulation/runs/{run_id}/anti-genericity",
            "POST /simulation/runs/{run_id}/bundle",
        ],
    }


@router.post("/run")
def run_simulation(request: SimulationRunRequest) -> Dict[str, Any]:
    state = _state_from_payload(request.initial_state)
    orchestrator = InteractionSimulationOrchestrator()

    result = orchestrator.run_interaction_simulation(
        state=state,
        run_id=request.run_id,
        story_request=request.story_request,
        event_specs=request.event_specs,
        candidate_ids=request.candidate_ids,
        target_cast_size=request.target_cast_size,
    )

    return {
        "success": result["success"],
        "run_id": request.run_id,
        "run_record": result["run_record"],
        "state": _state_to_dict(state),
    }


@router.get("/runs")
def list_runs() -> Dict[str, Any]:
    store = SimulationRunStore()
    return store.list_runs()


@router.get("/runs/{run_id}")
def get_run(run_id: str) -> Dict[str, Any]:
    store = SimulationRunStore()
    result = store.load_run(run_id=run_id)
    if not result["success"]:
        raise HTTPException(status_code=404, detail=result["errors"][0])
    return result


@router.get("/runs/{run_id}/summary")
def get_run_summary(run_id: str) -> Dict[str, Any]:
    store = SimulationRunStore()
    loaded = store.load_run(run_id=run_id)
    if not loaded["success"]:
        raise HTTPException(status_code=404, detail=loaded["errors"][0])

    run = loaded["run_record"]
    return {
        "success": True,
        "run_id": run_id,
        "status": run.get("status"),
        "step_count": len(run.get("steps", [])),
        "selected_character_ids": run.get("selected_character_ids", []),
        "event_ids": run.get("event_ids", []),
        "handoff_package_id": run.get("outputs", {}).get("handoff_package_id"),
        "generation_control_payload_id": run.get("outputs", {}).get("generation_control_payload_id"),
        "warning_count": len(run.get("warnings", [])),
        "error_count": len(run.get("errors", [])),
    }


@router.post("/runs/{run_id}/quality")
def score_run_quality(run_id: str, request: SimulationRunRequest) -> Dict[str, Any]:
    state = _state_from_payload(request.initial_state)

    if run_id not in state.metadata.get("simulation_runs", {}):
        orchestrator = InteractionSimulationOrchestrator()
        run_result = orchestrator.run_interaction_simulation(
            state=state,
            run_id=run_id,
            story_request=request.story_request,
            event_specs=request.event_specs,
            candidate_ids=request.candidate_ids,
            target_cast_size=request.target_cast_size,
        )
        if not run_result["success"]:
            return {
                "success": False,
                "run_id": run_id,
                "errors": run_result["run_record"].get("errors", []),
                "state": _state_to_dict(state),
            }

    scorer = SimulationQualityScorer()
    result = scorer.score_simulation_run(state=state, run_id=run_id)

    return {
        "success": result["success"],
        "quality_report": result["quality_report"],
        "state": _state_to_dict(state),
    }


@router.post("/runs/{run_id}/anti-genericity")
def validate_run_anti_genericity(run_id: str, request: SimulationRunRequest) -> Dict[str, Any]:
    state = _state_from_payload(request.initial_state)

    if run_id not in state.metadata.get("simulation_runs", {}):
        orchestrator = InteractionSimulationOrchestrator()
        run_result = orchestrator.run_interaction_simulation(
            state=state,
            run_id=run_id,
            story_request=request.story_request,
            event_specs=request.event_specs,
            candidate_ids=request.candidate_ids,
            target_cast_size=request.target_cast_size,
        )
        if not run_result["success"]:
            return {
                "success": False,
                "run_id": run_id,
                "errors": run_result["run_record"].get("errors", []),
                "state": _state_to_dict(state),
            }

    validator = SimulationAntiGenericityValidator()
    result = validator.validate_simulation_run(state=state, run_id=run_id)

    return {
        "success": result["success"],
        "anti_genericity_report": result["anti_genericity_report"],
        "state": _state_to_dict(state),
    }


@router.post("/runs/{run_id}/bundle")
def export_run_bundle(run_id: str, request: SimulationRunRequest) -> Dict[str, Any]:
    state = _state_from_payload(request.initial_state)

    if run_id not in state.metadata.get("simulation_runs", {}):
        orchestrator = InteractionSimulationOrchestrator()
        run_result = orchestrator.run_interaction_simulation(
            state=state,
            run_id=run_id,
            story_request=request.story_request,
            event_specs=request.event_specs,
            candidate_ids=request.candidate_ids,
            target_cast_size=request.target_cast_size,
        )
        if not run_result["success"]:
            return {
                "success": False,
                "run_id": run_id,
                "errors": run_result["run_record"].get("errors", []),
                "state": _state_to_dict(state),
            }

    scorer = SimulationQualityScorer()
    scorer.score_simulation_run(state=state, run_id=run_id)

    validator = SimulationAntiGenericityValidator()
    validator.validate_simulation_run(state=state, run_id=run_id)

    store = SimulationRunStore()
    result = store.export_run_bundle(state=state, run_id=run_id)

    return {
        "success": result["success"],
        "run_id": run_id,
        "bundle_id": result.get("bundle_id"),
        "path": result.get("path"),
        "bundle": result.get("bundle"),
        "state": _state_to_dict(state),
    }

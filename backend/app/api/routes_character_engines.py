from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.app.services.character_learning_adapter import CharacterLearningAdapter
from backend.app.services.character_learning_metadata_verifier import CharacterLearningMetadataVerifier
from backend.app.engines.character.adaptability_engine import AdaptabilityEngine
from backend.app.engines.character.character_consistency_validator import CharacterConsistencyValidator
from backend.app.engines.character.character_full_profile_orchestrator import CharacterFullProfileOrchestrator
from backend.app.engines.character.character_originality_engine import CharacterOriginalityEngine
from backend.app.engines.character.character_quality_scorer import CharacterQualityScorer
from backend.app.engines.character.destiny_legacy_engine import DestinyLegacyEngine
from backend.app.engines.character.dialogue_voice_engine import DialogueVoiceEngine
from backend.app.engines.character.relationship_readiness_engine import RelationshipReadinessEngine
from backend.app.services.character_run_store import CharacterRunStore


router = APIRouter(prefix="/character/engines", tags=["character-engines"])


class CharacterEngineRequest(BaseModel):
    payload: Dict[str, Any] = Field(default_factory=dict)
    persist: bool = False
    project_id: str = "default_project"
    universe_id: str = "default_universe"
    run_label: Optional[str] = None


class CharacterProfileSaveRequest(BaseModel):
    character_id: str
    profile: Dict[str, Any]
    orchestration_report: Dict[str, Any] = Field(default_factory=dict)
    quality_report: Dict[str, Any] = Field(default_factory=dict)
    learning_metadata: Dict[str, Any] = Field(default_factory=dict)
    project_id: str = "default_project"
    universe_id: str = "default_universe"


def _store() -> CharacterRunStore:
    return CharacterRunStore()


def _result_to_dict(result: Any) -> Dict[str, Any]:
    if hasattr(result, "model_dump"):
        return result.model_dump()
    if isinstance(result, dict):
        return result
    raise TypeError("Unsupported engine result type")


def _character_id_from_payload(payload: Dict[str, Any], result_data: Dict[str, Any]) -> str:
    seed = payload.get("character_seed", {})
    return (
        seed.get("character_id")
        or payload.get("character_id")
        or result_data.get("character_id")
        or result_data.get("character_full_profile", {}).get("character_id")
        or result_data.get("quality_report", {}).get("character_id")
        or result_data.get("originality_report", {}).get("character_id")
        or result_data.get("consistency_report", {}).get("character_id")
        or result_data.get("dialogue_voice_profile", {}).get("character_id")
        or result_data.get("relationship_readiness_profile", {}).get("character_id")
        or result_data.get("destiny_profile", {}).get("character_id")
        or result_data.get("adaptability_profile", {}).get("character_id")
        or "unknown_character"
    )


def _run_engine(engine: Any, request: CharacterEngineRequest) -> Dict[str, Any]:
    result = engine.run(request.payload)
    result_dict = _result_to_dict(result)

    persistence = {
        "persisted": False,
        "run_id": None,
        "run_path": None,
    }

    if request.persist:
        result_data = result_dict.get("data", {})
        character_id = _character_id_from_payload(request.payload, result_data)
        save_result = _store().save_engine_run(
            engine_name=result_dict.get("engine_name", getattr(engine, "engine_name", "unknown_engine")),
            character_id=character_id,
            input_payload=request.payload,
            result_payload=result_dict,
            project_id=request.project_id,
            universe_id=request.universe_id,
            run_label=request.run_label,
        )
        persistence = {
            "persisted": True,
            "run_id": save_result["run_id"],
            "run_path": save_result["run_path"],
        }

    return {
        "success": result_dict.get("success", True),
        "engine_name": result_dict.get("engine_name", getattr(engine, "engine_name", "unknown_engine")),
        "data": result_dict.get("data", {}),
        "warnings": result_dict.get("warnings", []),
        "errors": result_dict.get("errors", []),
        "generated_object_ids": result_dict.get("generated_object_ids", []),
        "persistence": persistence,
    }


@router.get("/health")
def character_engines_health() -> Dict[str, Any]:
    return {
        "success": True,
        "service": "character-engines",
        "chunk": "chunk_3_character_intelligence",
        "available_engines": [
            "adaptability",
            "destiny",
            "relationship-readiness",
            "dialogue-voice",
            "consistency-validator",
            "originality",
            "quality-scorer",
            "full-profile-orchestrator",
        ],
        "available_store_routes": [
            "save-profile",
            "get-profile",
            "list-profiles",
            "list-runs",
            "store-summary",
        ],
    }


@router.post("/adaptability")
def run_adaptability_engine(request: CharacterEngineRequest) -> Dict[str, Any]:
    return _run_engine(AdaptabilityEngine(), request)


@router.post("/destiny")
def run_destiny_engine(request: CharacterEngineRequest) -> Dict[str, Any]:
    return _run_engine(DestinyLegacyEngine(), request)


@router.post("/relationship-readiness")
def run_relationship_readiness_engine(request: CharacterEngineRequest) -> Dict[str, Any]:
    return _run_engine(RelationshipReadinessEngine(), request)


@router.post("/dialogue-voice")
def run_dialogue_voice_engine(request: CharacterEngineRequest) -> Dict[str, Any]:
    return _run_engine(DialogueVoiceEngine(), request)


@router.post("/consistency-validator")
def run_consistency_validator(request: CharacterEngineRequest) -> Dict[str, Any]:
    return _run_engine(CharacterConsistencyValidator(), request)


@router.post("/originality")
def run_originality_engine(request: CharacterEngineRequest) -> Dict[str, Any]:
    return _run_engine(CharacterOriginalityEngine(), request)


@router.post("/quality-scorer")
def run_quality_scorer(request: CharacterEngineRequest) -> Dict[str, Any]:
    return _run_engine(CharacterQualityScorer(), request)


@router.post("/full-profile-orchestrator")
def run_full_profile_orchestrator(request: CharacterEngineRequest) -> Dict[str, Any]:
    response = _run_engine(CharacterFullProfileOrchestrator(), request)

    if request.persist and response["success"]:
        data = response.get("data", {})
        full_profile = data.get("character_full_profile", {})
        if full_profile:
            character_id = full_profile.get("character_id", "unknown_character")
            profile_save = _store().save_character_profile(
                character_id=character_id,
                profile=full_profile,
                orchestration_report=data.get("orchestration_report", {}),
                quality_report=full_profile.get("validation", {}).get("quality_report", {}),
                learning_metadata=data.get("learning_metadata", {}),
                project_id=request.project_id,
                universe_id=request.universe_id,
            )
            response["profile_persistence"] = {
                "persisted": True,
                "record_id": profile_save["record_id"],
                "profile_path": profile_save["profile_path"],
            }

    return response


@router.post("/save-profile")
def save_character_profile(request: CharacterProfileSaveRequest) -> Dict[str, Any]:
    try:
        result = _store().save_character_profile(
            character_id=request.character_id,
            profile=request.profile,
            orchestration_report=request.orchestration_report,
            quality_report=request.quality_report,
            learning_metadata=request.learning_metadata,
            project_id=request.project_id,
            universe_id=request.universe_id,
        )
        return {
            "success": True,
            "data": result,
        }
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/profiles/{character_id}")
def get_character_profile(character_id: str) -> Dict[str, Any]:
    try:
        profile = _store().load_character_profile(character_id)
        return {
            "success": True,
            "data": profile,
        }
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/profiles")
def list_character_profiles(
    project_id: Optional[str] = None,
    universe_id: Optional[str] = None,
    min_quality_score: Optional[float] = None,
) -> Dict[str, Any]:
    profiles = _store().list_character_profiles(
        project_id=project_id,
        universe_id=universe_id,
        min_quality_score=min_quality_score,
    )
    return {
        "success": True,
        "data": {
            "profiles": profiles,
            "count": len(profiles),
        },
    }


@router.get("/runs")
def list_character_runs(
    character_id: Optional[str] = None,
    engine_name: Optional[str] = None,
    project_id: Optional[str] = None,
) -> Dict[str, Any]:
    runs = _store().list_engine_runs(
        character_id=character_id,
        engine_name=engine_name,
        project_id=project_id,
    )
    return {
        "success": True,
        "data": {
            "runs": runs,
            "count": len(runs),
        },
    }


@router.get("/store-summary")
def get_character_store_summary() -> Dict[str, Any]:
    return {
        "success": True,
        "data": _store().get_store_summary(),
    }

# ---------------------------------------------------------------------------
# Upgrade Pass C: Character global learning registration routes
# ---------------------------------------------------------------------------

class CharacterLearningRegistrationRequest(BaseModel):
    result_payload: Dict[str, Any] = Field(default_factory=dict)
    project_id: str = "default_project"
    universe_id: str = "default_universe"
    source_payload: Dict[str, Any] = Field(default_factory=dict)
    world_contract: Dict[str, Any] = Field(default_factory=dict)
    enforce_quality_gates: bool = True


class CharacterProfileLearningRegistrationRequest(BaseModel):
    character_profile: Dict[str, Any] = Field(default_factory=dict)
    project_id: str = "default_project"
    universe_id: str = "default_universe"
    world_contract: Dict[str, Any] = Field(default_factory=dict)
    enforce_quality_gates: bool = True


class CharacterLearningVerifyRequest(BaseModel):
    result_payload: Dict[str, Any] = Field(default_factory=dict)
    project_id: str = "default_project"
    universe_id: str = "default_universe"
    world_contract: Dict[str, Any] = Field(default_factory=dict)
    allow_synthesis: bool = True


class CharacterWorldContractCheckRequest(BaseModel):
    character_profile: Dict[str, Any] = Field(default_factory=dict)
    world_contract: Dict[str, Any] = Field(default_factory=dict)


class CharacterChunk4HandoffRequest(BaseModel):
    character_id: str = "unknown_character"
    character_profile: Dict[str, Any] = Field(default_factory=dict)


def _character_learning_adapter() -> CharacterLearningAdapter:
    return CharacterLearningAdapter()


def _character_learning_verifier() -> CharacterLearningMetadataVerifier:
    return CharacterLearningMetadataVerifier()


@router.post("/learning/register-result")
def register_character_engine_result_to_learning(request: CharacterLearningRegistrationRequest) -> Dict[str, Any]:
    """Register an existing character engine result into the global learning foundation."""

    result = _character_learning_adapter().register_character_engine_result(
        result_payload=request.result_payload,
        project_id=request.project_id,
        universe_id=request.universe_id,
        source_payload=request.source_payload or None,
        world_contract=request.world_contract or None,
        enforce_quality_gates=request.enforce_quality_gates,
    )

    return {
        "success": True,
        "data": result,
    }


@router.post("/learning/register-profile")
def register_character_profile_to_learning(request: CharacterProfileLearningRegistrationRequest) -> Dict[str, Any]:
    """Register learning metadata found inside a character profile or Character Bible."""

    result = _character_learning_adapter().register_character_profile(
        character_profile=request.character_profile,
        project_id=request.project_id,
        universe_id=request.universe_id,
        world_contract=request.world_contract or None,
        enforce_quality_gates=request.enforce_quality_gates,
    )

    return {
        "success": True,
        "data": result,
    }


@router.post("/learning/verify")
def verify_character_learning_metadata(request: CharacterLearningVerifyRequest) -> Dict[str, Any]:
    """Verify whether a character result is global-learning-ready and Chunk-4-ready."""

    result = _character_learning_verifier().verify_character_result(
        result_payload=request.result_payload,
        project_id=request.project_id,
        universe_id=request.universe_id,
        world_contract=request.world_contract or None,
        allow_synthesis=request.allow_synthesis,
    )

    return {
        "success": True,
        "data": result,
    }


@router.post("/learning/world-contract-check")
def check_character_world_contract(request: CharacterWorldContractCheckRequest) -> Dict[str, Any]:
    """Validate that a character obeys the world-to-character dependency contract."""

    result = _character_learning_adapter().validate_character_against_world_contract(
        character_profile=request.character_profile,
        world_contract=request.world_contract,
    )

    return {
        "success": True,
        "data": result,
    }


@router.post("/learning/chunk4-handoff")
def build_character_chunk4_handoff(request: CharacterChunk4HandoffRequest) -> Dict[str, Any]:
    """Build the character handoff payload needed for Chunk 4 relationship simulation."""

    result = _character_learning_adapter().build_chunk4_handoff_contract(
        character_id=request.character_id,
        character_profile=request.character_profile,
    )

    return {
        "success": True,
        "data": result,
    }

from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.app.services.embedding_registry_store import EmbeddingRegistryStore
from backend.app.services.learning_integration import LearningIntegrationService
from backend.app.services.learning_registry_store import LearningRegistryStore
from backend.app.services.provenance_store import ProvenanceStore
from backend.app.services.training_queue_store import TrainingQueueStore


router = APIRouter(prefix="/learning", tags=["learning"])


class LearningMetadataRegisterRequest(BaseModel):
    learning_metadata: Dict[str, Any]
    project_id: str = "default_project"
    universe_id: str = "default_universe"
    source_payload: Dict[str, Any] = Field(default_factory=dict)
    enqueue_training: bool = True
    register_embeddings: bool = True
    register_provenance: bool = True


class EngineResultRegisterRequest(BaseModel):
    result_payload: Dict[str, Any]
    project_id: str = "default_project"
    universe_id: str = "default_universe"
    source_payload: Dict[str, Any] = Field(default_factory=dict)


class ProvenanceRegisterRequest(BaseModel):
    source_name: str
    source_type: str
    dataset_family: str
    usage_allowed: bool
    human_review_required: bool = True
    do_not_train: bool = False
    license_name: Optional[str] = None
    license_url: Optional[str] = None
    source_url: Optional[str] = None
    notes: Optional[str] = None
    project_id: str = "default_project"
    universe_id: str = "default_universe"
    tags: list[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class TrainingQueueRequest(BaseModel):
    target_object_id: str
    target_object_type: str
    engine_name: str
    payload: Dict[str, Any]
    training_eligibility: Dict[str, Any]
    project_id: str = "default_project"
    universe_id: str = "default_universe"
    provenance_id: Optional[str] = None
    learning_metadata_id: Optional[str] = None
    tags: list[str] = Field(default_factory=list)


class EmbeddingMetadataRequest(BaseModel):
    target_object_id: str
    target_object_type: str
    embedding_metadata: Dict[str, Any]
    engine_name: str = "unknown_engine"
    project_id: str = "default_project"
    universe_id: str = "default_universe"
    source_payload: Dict[str, Any] = Field(default_factory=dict)
    queue_for_vectorization: bool = True


class TrainingStatusUpdateRequest(BaseModel):
    status: str
    notes: Optional[str] = None


def _learning_registry() -> LearningRegistryStore:
    return LearningRegistryStore()


def _provenance_store() -> ProvenanceStore:
    return ProvenanceStore()


def _training_queue() -> TrainingQueueStore:
    return TrainingQueueStore()


def _embedding_registry() -> EmbeddingRegistryStore:
    return EmbeddingRegistryStore()


def _integration_service() -> LearningIntegrationService:
    return LearningIntegrationService()


@router.get("/health")
def learning_health() -> Dict[str, Any]:
    return {
        "success": True,
        "service": "learning",
        "upgrade_pass": "A",
        "description": "Global learning, provenance, training queue, and embedding registry foundation.",
        "available_routes": [
            "GET /learning/health",
            "GET /learning/summary",
            "POST /learning/metadata",
            "POST /learning/engine-result",
            "GET /learning/records/{category}",
            "GET /learning/records/{category}/{record_id}",
            "POST /learning/provenance",
            "GET /learning/provenance",
            "POST /learning/training-queue",
            "GET /learning/training-queue",
            "PATCH /learning/training-queue/{training_queue_id}/status",
            "POST /learning/embeddings",
            "GET /learning/embeddings",
            "GET /learning/embeddings/vectorization-queue",
        ],
    }


@router.get("/summary")
def learning_summary() -> Dict[str, Any]:
    return {
        "success": True,
        "data": _integration_service().get_global_learning_summary(),
    }


@router.post("/metadata")
def register_learning_metadata(request: LearningMetadataRegisterRequest) -> Dict[str, Any]:
    try:
        result = _integration_service().register_learning_metadata(
            learning_metadata=request.learning_metadata,
            project_id=request.project_id,
            universe_id=request.universe_id,
            source_payload=request.source_payload or request.learning_metadata,
            enqueue_training=request.enqueue_training,
            register_embeddings=request.register_embeddings,
            register_provenance=request.register_provenance,
        )
        return {
            "success": True,
            "data": result,
        }
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/engine-result")
def register_engine_result(request: EngineResultRegisterRequest) -> Dict[str, Any]:
    result = _integration_service().register_engine_result(
        result_payload=request.result_payload,
        project_id=request.project_id,
        universe_id=request.universe_id,
        source_payload=request.source_payload or request.result_payload,
    )
    return {
        "success": True,
        "data": result,
    }


@router.get("/records/{category}")
def list_learning_records(
    category: str,
    project_id: Optional[str] = None,
    universe_id: Optional[str] = None,
    engine_name: Optional[str] = None,
    target_object_type: Optional[str] = None,
    type_family: Optional[str] = None,
    min_quality_score: Optional[float] = None,
) -> Dict[str, Any]:
    try:
        records = _learning_registry().list_records(
            category=category,
            project_id=project_id,
            universe_id=universe_id,
            engine_name=engine_name,
            target_object_type=target_object_type,
            type_family=type_family,
            min_quality_score=min_quality_score,
        )
        return {
            "success": True,
            "data": {
                "category": category,
                "count": len(records),
                "records": records,
            },
        }
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/records/{category}/{record_id}")
def get_learning_record(category: str, record_id: str) -> Dict[str, Any]:
    try:
        record = _learning_registry().load_record(category=category, record_id=record_id)
        return {
            "success": True,
            "data": record,
        }
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/provenance")
def register_provenance(request: ProvenanceRegisterRequest) -> Dict[str, Any]:
    try:
        result = _provenance_store().register_source(
            source_name=request.source_name,
            source_type=request.source_type,
            dataset_family=request.dataset_family,
            usage_allowed=request.usage_allowed,
            human_review_required=request.human_review_required,
            do_not_train=request.do_not_train,
            license_name=request.license_name,
            license_url=request.license_url,
            source_url=request.source_url,
            notes=request.notes,
            project_id=request.project_id,
            universe_id=request.universe_id,
            tags=request.tags,
            metadata=request.metadata,
        )
        return {
            "success": True,
            "data": result,
        }
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/provenance")
def list_provenance(
    dataset_family: Optional[str] = None,
    source_type: Optional[str] = None,
    project_id: Optional[str] = None,
    universe_id: Optional[str] = None,
    allowed_for_training: Optional[bool] = None,
    usage_allowed: Optional[bool] = None,
) -> Dict[str, Any]:
    records = _provenance_store().list_records(
        dataset_family=dataset_family,
        source_type=source_type,
        project_id=project_id,
        universe_id=universe_id,
        allowed_for_training=allowed_for_training,
        usage_allowed=usage_allowed,
    )
    return {
        "success": True,
        "data": {
            "count": len(records),
            "records": records,
        },
    }


@router.get("/provenance/{provenance_id}")
def get_provenance(provenance_id: str) -> Dict[str, Any]:
    try:
        return {
            "success": True,
            "data": _provenance_store().load_record(provenance_id),
        }
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/training-queue")
def enqueue_training_record(request: TrainingQueueRequest) -> Dict[str, Any]:
    try:
        result = _training_queue().enqueue(
            target_object_id=request.target_object_id,
            target_object_type=request.target_object_type,
            engine_name=request.engine_name,
            payload=request.payload,
            training_eligibility=request.training_eligibility,
            project_id=request.project_id,
            universe_id=request.universe_id,
            provenance_id=request.provenance_id,
            learning_metadata_id=request.learning_metadata_id,
            tags=request.tags,
        )
        return {
            "success": True,
            "data": result,
        }
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/training-queue")
def list_training_queue(
    status: Optional[str] = None,
    recommended_split: Optional[str] = None,
    target_object_type: Optional[str] = None,
    engine_name: Optional[str] = None,
    project_id: Optional[str] = None,
    universe_id: Optional[str] = None,
    min_quality_score: Optional[float] = None,
    future_chunk8_ready: Optional[bool] = None,
) -> Dict[str, Any]:
    records = _training_queue().list_records(
        status=status,
        recommended_split=recommended_split,
        target_object_type=target_object_type,
        engine_name=engine_name,
        project_id=project_id,
        universe_id=universe_id,
        min_quality_score=min_quality_score,
        future_chunk8_ready=future_chunk8_ready,
    )
    return {
        "success": True,
        "data": {
            "count": len(records),
            "records": records,
        },
    }


@router.get("/training-queue/{training_queue_id}")
def get_training_queue_record(training_queue_id: str) -> Dict[str, Any]:
    try:
        return {
            "success": True,
            "data": _training_queue().load_record(training_queue_id),
        }
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.patch("/training-queue/{training_queue_id}/status")
def update_training_status(training_queue_id: str, request: TrainingStatusUpdateRequest) -> Dict[str, Any]:
    try:
        result = _training_queue().update_status(
            training_queue_id=training_queue_id,
            status=request.status,
            notes=request.notes,
        )
        return {
            "success": True,
            "data": result,
        }
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/embeddings")
def register_embedding_metadata(request: EmbeddingMetadataRequest) -> Dict[str, Any]:
    try:
        result = _embedding_registry().register_embedding_metadata(
            target_object_id=request.target_object_id,
            target_object_type=request.target_object_type,
            embedding_metadata=request.embedding_metadata,
            engine_name=request.engine_name,
            project_id=request.project_id,
            universe_id=request.universe_id,
            source_payload=request.source_payload,
            queue_for_vectorization=request.queue_for_vectorization,
        )
        return {
            "success": True,
            "data": result,
        }
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/embeddings")
def list_embeddings(
    target_object_type: Optional[str] = None,
    engine_name: Optional[str] = None,
    project_id: Optional[str] = None,
    universe_id: Optional[str] = None,
    tag: Optional[str] = None,
    min_originality_score: Optional[float] = None,
    vector_computed: Optional[bool] = None,
) -> Dict[str, Any]:
    records = _embedding_registry().list_records(
        target_object_type=target_object_type,
        engine_name=engine_name,
        project_id=project_id,
        universe_id=universe_id,
        tag=tag,
        min_originality_score=min_originality_score,
        vector_computed=vector_computed,
    )
    return {
        "success": True,
        "data": {
            "count": len(records),
            "records": records,
        },
    }


@router.get("/embeddings/vectorization-queue")
def list_vectorization_queue(
    status: Optional[str] = None,
    target_object_type: Optional[str] = None,
    engine_name: Optional[str] = None,
) -> Dict[str, Any]:
    records = _embedding_registry().list_vectorization_queue(
        status=status,
        target_object_type=target_object_type,
        engine_name=engine_name,
    )
    return {
        "success": True,
        "data": {
            "count": len(records),
            "records": records,
        },
    }


@router.get("/embeddings/{embedding_id}")
def get_embedding_record(embedding_id: str) -> Dict[str, Any]:
    try:
        return {
            "success": True,
            "data": _embedding_registry().load_record(embedding_id),
        }
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc



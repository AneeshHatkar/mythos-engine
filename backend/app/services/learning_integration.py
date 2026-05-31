from pathlib import Path
from typing import Any, Dict, List, Optional

from backend.app.services.embedding_registry_store import EmbeddingRegistryStore
from backend.app.services.learning_registry_store import LearningRegistryStore
from backend.app.services.provenance_store import ProvenanceStore
from backend.app.services.training_queue_store import TrainingQueueStore


class LearningIntegrationService:
    """Coordinates global learning registration across MythOS Engine.

    Individual engines should not manually know how to write every learning
    store. This service takes engine outputs and registers:

    - learning metadata
    - ontology records
    - learned type candidates
    - provenance records
    - embedding metadata
    - training queue records

    It is the bridge between deterministic engine scaffolding and the future
    Chunk 8 learning/RAG/training system.
    """

    def __init__(
        self,
        *,
        learning_root: str | Path = "reports/learning",
        provenance_root: str | Path = "reports/provenance",
        training_queue_root: str | Path = "reports/training_queue",
        embedding_root: str | Path = "reports/embeddings",
    ) -> None:
        self.learning_registry = LearningRegistryStore(learning_root)
        self.provenance_store = ProvenanceStore(provenance_root)
        self.training_queue = TrainingQueueStore(training_queue_root)
        self.embedding_registry = EmbeddingRegistryStore(embedding_root)

    def register_engine_result(
        self,
        *,
        result_payload: Dict[str, Any],
        project_id: str = "default_project",
        universe_id: str = "default_universe",
        source_payload: Optional[Dict[str, Any]] = None,
        enqueue_training: bool = True,
        register_embeddings: bool = True,
        register_provenance: bool = True,
    ) -> Dict[str, Any]:
        """Register learning metadata from a standard EngineRunResult payload."""

        data = result_payload.get("data", {}) if isinstance(result_payload, dict) else {}
        learning_metadata = data.get("learning_metadata")

        if not learning_metadata:
            return {
                "success": True,
                "registered": False,
                "reason": "no_learning_metadata_found",
                "engine_name": result_payload.get("engine_name", "unknown_engine"),
            }

        return self.register_learning_metadata(
            learning_metadata=learning_metadata,
            project_id=project_id,
            universe_id=universe_id,
            source_payload=source_payload or data,
            enqueue_training=enqueue_training,
            register_embeddings=register_embeddings,
            register_provenance=register_provenance,
        )

    def register_learning_metadata(
        self,
        *,
        learning_metadata: Dict[str, Any],
        project_id: str = "default_project",
        universe_id: str = "default_universe",
        source_payload: Optional[Dict[str, Any]] = None,
        enqueue_training: bool = True,
        register_embeddings: bool = True,
        register_provenance: bool = True,
    ) -> Dict[str, Any]:
        engine_name = learning_metadata.get("engine_name", "unknown_engine")
        target_object_id = learning_metadata.get("target_object_id", "unknown_target")
        target_object_type = learning_metadata.get("target_object_type", "unknown_target_type")

        learning_result = self.learning_registry.register_learning_metadata(
            engine_name=engine_name,
            target_object_id=target_object_id,
            target_object_type=target_object_type,
            learning_metadata=learning_metadata,
            project_id=project_id,
            universe_id=universe_id,
        )

        provenance_results: List[Dict[str, Any]] = []
        if register_provenance:
            for provenance_record in learning_metadata.get("provenance_records", []) or []:
                provenance_results.append(
                    self.provenance_store.register_from_engine_provenance(
                        provenance_record,
                        project_id=project_id,
                        universe_id=universe_id,
                    )
                )

        embedding_result = None
        if register_embeddings and learning_metadata.get("embedding_metadata"):
            embedding_result = self.embedding_registry.register_from_learning_metadata(
                learning_metadata,
                project_id=project_id,
                universe_id=universe_id,
                source_payload=source_payload or learning_metadata,
            )

        training_result = None
        training_eligibility = learning_metadata.get("training_eligibility", {}) or {}
        if enqueue_training and training_eligibility.get("training_eligible") is True:
            training_result = self.training_queue.enqueue_from_learning_metadata(
                learning_metadata,
                payload=source_payload or learning_metadata,
                project_id=project_id,
                universe_id=universe_id,
                provenance_id=provenance_results[0]["provenance_id"] if provenance_results else None,
            )

        return {
            "success": True,
            "registered": True,
            "engine_name": engine_name,
            "target_object_id": target_object_id,
            "target_object_type": target_object_type,
            "learning_registry": learning_result,
            "provenance_registered": len(provenance_results),
            "provenance_results": provenance_results,
            "embedding_registered": embedding_result is not None,
            "embedding_result": embedding_result,
            "training_enqueued": training_result is not None,
            "training_result": training_result,
        }

    def register_many_engine_results(
        self,
        *,
        result_payloads: List[Dict[str, Any]],
        project_id: str = "default_project",
        universe_id: str = "default_universe",
        source_payloads: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        results = []

        for index, result_payload in enumerate(result_payloads):
            source_payload = None
            if source_payloads and index < len(source_payloads):
                source_payload = source_payloads[index]

            results.append(
                self.register_engine_result(
                    result_payload=result_payload,
                    project_id=project_id,
                    universe_id=universe_id,
                    source_payload=source_payload,
                )
            )

        return {
            "success": True,
            "attempted": len(result_payloads),
            "registered_count": sum(1 for item in results if item.get("registered") is True),
            "skipped_count": sum(1 for item in results if item.get("registered") is False),
            "training_enqueued_count": sum(1 for item in results if item.get("training_enqueued") is True),
            "embedding_registered_count": sum(1 for item in results if item.get("embedding_registered") is True),
            "results": results,
        }

    def extract_learning_metadata_from_profile(self, profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract nested learning metadata records from full world/character profiles."""

        found: List[Dict[str, Any]] = []

        def walk(value: Any) -> None:
            if isinstance(value, dict):
                if (
                    "engine_name" in value
                    and "target_object_id" in value
                    and "target_object_type" in value
                    and "training_eligibility" in value
                ):
                    found.append(value)

                for child in value.values():
                    walk(child)

            elif isinstance(value, list):
                for child in value:
                    walk(child)

        walk(profile)

        # Deduplicate by learning_metadata_id if present, otherwise object id.
        deduped = []
        seen = set()

        for item in found:
            key = item.get("learning_metadata_id") or f"{item.get('engine_name')}:{item.get('target_object_id')}:{item.get('target_object_type')}"
            if key not in seen:
                seen.add(key)
                deduped.append(item)

        return deduped

    def register_profile_learning_metadata(
        self,
        *,
        profile: Dict[str, Any],
        project_id: str = "default_project",
        universe_id: str = "default_universe",
    ) -> Dict[str, Any]:
        metadata_records = self.extract_learning_metadata_from_profile(profile)

        results = []
        for metadata in metadata_records:
            results.append(
                self.register_learning_metadata(
                    learning_metadata=metadata,
                    project_id=project_id,
                    universe_id=universe_id,
                    source_payload=profile,
                )
            )

        return {
            "success": True,
            "metadata_found": len(metadata_records),
            "registered_count": sum(1 for item in results if item.get("registered") is True),
            "training_enqueued_count": sum(1 for item in results if item.get("training_enqueued") is True),
            "embedding_registered_count": sum(1 for item in results if item.get("embedding_registered") is True),
            "results": results,
        }

    def get_global_learning_summary(self) -> Dict[str, Any]:
        return {
            "learning_registry": self.learning_registry.get_summary(),
            "provenance": self.provenance_store.get_summary(),
            "training_queue": self.training_queue.get_summary(),
            "embedding_registry": self.embedding_registry.get_summary(),
        }


def register_engine_learning_output(
    *,
    result_payload: Dict[str, Any],
    project_id: str = "default_project",
    universe_id: str = "default_universe",
    root_dir: str | Path = "reports",
) -> Dict[str, Any]:
    """Convenience wrapper for one-off registration from APIs/orchestrators."""

    root = Path(root_dir)

    service = LearningIntegrationService(
        learning_root=root / "learning",
        provenance_root=root / "provenance",
        training_queue_root=root / "training_queue",
        embedding_root=root / "embeddings",
    )

    return service.register_engine_result(
        result_payload=result_payload,
        project_id=project_id,
        universe_id=universe_id,
    )

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import uuid4


class EmbeddingRegistryStore:
    """Global embedding metadata and future similarity registry.

    This store does not compute embeddings yet. It stores embedding metadata,
    similarity tags, future vector IDs, nearest-neighbor placeholders, and
    originality/deduplication signals so Chunk 8 can later add real vector
    search, RAG, and semantic originality scoring.

    Current use:
    - persist embedding metadata emitted by engines
    - track similarity/originality scores
    - support lexical/tag-based retrieval filtering
    - queue records for future vectorization

    Later upgrade path:
    - sentence-transformer/OpenAI embedding integration
    - vector DB / FAISS / pgvector
    - semantic nearest-neighbor search
    - duplicate detection
    - originality scoring against licensed datasets
    """

    def __init__(self, root_dir: str | Path = "reports/embeddings") -> None:
        self.root_dir = Path(root_dir)
        self.records_dir = self.root_dir / "records"
        self.vector_queue_dir = self.root_dir / "vectorization_queue"
        self.similarity_events_dir = self.root_dir / "similarity_events"
        self.index_path = self.root_dir / "embedding_registry_index.json"
        self._ensure_dirs()

    def _ensure_dirs(self) -> None:
        self.records_dir.mkdir(parents=True, exist_ok=True)
        self.vector_queue_dir.mkdir(parents=True, exist_ok=True)
        self.similarity_events_dir.mkdir(parents=True, exist_ok=True)

        if not self.index_path.exists():
            self._write_json(
                self.index_path,
                {
                    "store_type": "embedding_registry_store",
                    "schema_version": "embedding_registry_v0.1.0",
                    "created_at": self._now(),
                    "updated_at": self._now(),
                    "records": {},
                    "vectorization_queue": {},
                    "similarity_events": {},
                },
            )

    def register_embedding_metadata(
        self,
        *,
        target_object_id: str,
        target_object_type: str,
        embedding_metadata: Dict[str, Any],
        engine_name: str = "unknown_engine",
        project_id: str = "default_project",
        universe_id: str = "default_universe",
        source_payload: Optional[Dict[str, Any]] = None,
        queue_for_vectorization: bool = True,
    ) -> Dict[str, Any]:
        if not target_object_id:
            raise ValueError("target_object_id is required")
        if not target_object_type:
            raise ValueError("target_object_type is required")

        embedding_id = (
            embedding_metadata.get("embedding_id")
            or embedding_metadata.get("vector_id")
            or f"embreg_{uuid4().hex[:12]}"
        )

        created_at = self._now()

        similarity_tags = embedding_metadata.get("similarity_tags", []) or []
        retrieval_queries = embedding_metadata.get("retrieval_queries", []) or embedding_metadata.get("future_retrieval_queries", []) or []

        record = {
            "embedding_id": embedding_id,
            "target_object_id": target_object_id,
            "target_object_type": target_object_type,
            "engine_name": engine_name,
            "project_id": project_id,
            "universe_id": universe_id,
            "embedding_metadata": embedding_metadata,
            "source_payload": source_payload or {},
            "embedding_model": embedding_metadata.get("embedding_model", "future_embedding_model_not_computed_yet"),
            "vector_id": embedding_metadata.get("vector_id"),
            "vector_computed": bool(embedding_metadata.get("vector_computed", False)),
            "similarity_tags": similarity_tags,
            "retrieval_queries": retrieval_queries,
            "nearest_neighbor_placeholders": embedding_metadata.get("nearest_neighbor_placeholders", []) or embedding_metadata.get("nearest_neighbors", []) or [],
            "novelty_score": float(embedding_metadata.get("novelty_score", 0.0)),
            "originality_score": float(embedding_metadata.get("originality_score", 0.0)),
            "similarity_threshold_used": float(embedding_metadata.get("similarity_threshold_used", 0.0)),
            "deduplication_status": self._deduplication_status(embedding_metadata),
            "created_at": created_at,
            "updated_at": created_at,
            "registry_metadata": {
                "schema_version": "embedding_registry_record_v0.1.0",
                "ready_for_vectorization": queue_for_vectorization,
                "ready_for_similarity_search": bool(similarity_tags or retrieval_queries),
                "requires_real_embedding_later": not bool(embedding_metadata.get("vector_computed", False)),
            },
        }

        path = self.records_dir / f"{self._safe_name(embedding_id)}.json"
        self._write_json(path, record)
        self._upsert_index_record(record, path)

        queue_result = None
        if queue_for_vectorization:
            queue_result = self.queue_for_vectorization(
                target_object_id=target_object_id,
                target_object_type=target_object_type,
                embedding_id=embedding_id,
                engine_name=engine_name,
                project_id=project_id,
                universe_id=universe_id,
                source_payload=source_payload or embedding_metadata,
            )

        return {
            "success": True,
            "embedding_id": embedding_id,
            "record_path": str(path),
            "queued_for_vectorization": queue_result is not None,
            "vectorization_queue_id": queue_result["vectorization_queue_id"] if queue_result else None,
            "deduplication_status": record["deduplication_status"],
        }

    def register_from_learning_metadata(
        self,
        learning_metadata: Dict[str, Any],
        *,
        project_id: str = "default_project",
        universe_id: str = "default_universe",
        source_payload: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        embedding_metadata = learning_metadata.get("embedding_metadata")
        if not embedding_metadata:
            raise ValueError("learning_metadata does not include embedding_metadata")

        return self.register_embedding_metadata(
            target_object_id=learning_metadata.get("target_object_id", "unknown_target"),
            target_object_type=learning_metadata.get("target_object_type", "unknown_target_type"),
            embedding_metadata=embedding_metadata,
            engine_name=learning_metadata.get("engine_name", "unknown_engine"),
            project_id=project_id,
            universe_id=universe_id,
            source_payload=source_payload or learning_metadata,
            queue_for_vectorization=True,
        )

    def queue_for_vectorization(
        self,
        *,
        target_object_id: str,
        target_object_type: str,
        embedding_id: str,
        engine_name: str,
        project_id: str,
        universe_id: str,
        source_payload: Dict[str, Any],
    ) -> Dict[str, Any]:
        queue_id = f"vecq_{uuid4().hex[:12]}"
        created_at = self._now()

        record = {
            "vectorization_queue_id": queue_id,
            "embedding_id": embedding_id,
            "target_object_id": target_object_id,
            "target_object_type": target_object_type,
            "engine_name": engine_name,
            "project_id": project_id,
            "universe_id": universe_id,
            "status": "queued",
            "source_payload": source_payload,
            "created_at": created_at,
            "updated_at": created_at,
            "queue_metadata": {
                "future_chunk8_task": "compute_real_embedding",
                "recommended_embedding_family": self._recommended_embedding_family(target_object_type),
            },
        }

        path = self.vector_queue_dir / f"{self._safe_name(queue_id)}.json"
        self._write_json(path, record)

        index = self._read_index()
        index.setdefault("vectorization_queue", {})[queue_id] = {
            "vectorization_queue_id": queue_id,
            "embedding_id": embedding_id,
            "target_object_id": target_object_id,
            "target_object_type": target_object_type,
            "engine_name": engine_name,
            "project_id": project_id,
            "universe_id": universe_id,
            "status": "queued",
            "path": str(path),
            "created_at": created_at,
            "updated_at": created_at,
        }
        index["updated_at"] = self._now()
        self._write_json(self.index_path, index)

        return {
            "success": True,
            "vectorization_queue_id": queue_id,
            "path": str(path),
        }

    def register_similarity_event(
        self,
        *,
        source_embedding_id: str,
        compared_embedding_id: Optional[str],
        target_object_id: str,
        similarity_score: float,
        similarity_type: str,
        decision: str,
        details: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        if not source_embedding_id:
            raise ValueError("source_embedding_id is required")
        if not target_object_id:
            raise ValueError("target_object_id is required")

        event_id = f"simevent_{uuid4().hex[:12]}"
        created_at = self._now()

        event = {
            "similarity_event_id": event_id,
            "source_embedding_id": source_embedding_id,
            "compared_embedding_id": compared_embedding_id,
            "target_object_id": target_object_id,
            "similarity_score": float(similarity_score),
            "similarity_type": similarity_type,
            "decision": decision,
            "details": details or {},
            "created_at": created_at,
        }

        path = self.similarity_events_dir / f"{self._safe_name(event_id)}.json"
        self._write_json(path, event)

        index = self._read_index()
        index.setdefault("similarity_events", {})[event_id] = {
            "similarity_event_id": event_id,
            "source_embedding_id": source_embedding_id,
            "compared_embedding_id": compared_embedding_id,
            "target_object_id": target_object_id,
            "similarity_score": float(similarity_score),
            "similarity_type": similarity_type,
            "decision": decision,
            "path": str(path),
            "created_at": created_at,
        }
        index["updated_at"] = self._now()
        self._write_json(self.index_path, index)

        return {
            "success": True,
            "similarity_event_id": event_id,
            "path": str(path),
        }

    def load_record(self, embedding_id: str) -> Dict[str, Any]:
        index = self._read_index()
        summary = index.get("records", {}).get(embedding_id)

        if not summary:
            raise FileNotFoundError(f"No embedding registry record found for {embedding_id}")

        path = Path(summary["record_path"])
        if not path.exists():
            raise FileNotFoundError(f"Indexed embedding record path missing: {path}")

        return self._read_json(path)

    def list_records(
        self,
        *,
        target_object_type: Optional[str] = None,
        engine_name: Optional[str] = None,
        project_id: Optional[str] = None,
        universe_id: Optional[str] = None,
        tag: Optional[str] = None,
        min_originality_score: Optional[float] = None,
        vector_computed: Optional[bool] = None,
    ) -> List[Dict[str, Any]]:
        records = list(self._read_index().get("records", {}).values())

        if target_object_type is not None:
            records = [item for item in records if item.get("target_object_type") == target_object_type]

        if engine_name is not None:
            records = [item for item in records if item.get("engine_name") == engine_name]

        if project_id is not None:
            records = [item for item in records if item.get("project_id") == project_id]

        if universe_id is not None:
            records = [item for item in records if item.get("universe_id") == universe_id]

        if tag is not None:
            records = [item for item in records if tag in item.get("similarity_tags", [])]

        if min_originality_score is not None:
            records = [item for item in records if float(item.get("originality_score", 0.0)) >= min_originality_score]

        if vector_computed is not None:
            records = [item for item in records if item.get("vector_computed") is vector_computed]

        return sorted(records, key=lambda item: item.get("created_at", ""), reverse=True)

    def list_vectorization_queue(
        self,
        *,
        status: Optional[str] = None,
        target_object_type: Optional[str] = None,
        engine_name: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        records = list(self._read_index().get("vectorization_queue", {}).values())

        if status is not None:
            records = [item for item in records if item.get("status") == status]

        if target_object_type is not None:
            records = [item for item in records if item.get("target_object_type") == target_object_type]

        if engine_name is not None:
            records = [item for item in records if item.get("engine_name") == engine_name]

        return sorted(records, key=lambda item: item.get("created_at", ""), reverse=True)

    def update_vectorization_status(
        self,
        *,
        vectorization_queue_id: str,
        status: str,
        vector_id: Optional[str] = None,
        embedding_model: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> Dict[str, Any]:
        index = self._read_index()
        summary = index.get("vectorization_queue", {}).get(vectorization_queue_id)

        if not summary:
            raise FileNotFoundError(f"No vectorization queue record found for {vectorization_queue_id}")

        path = Path(summary["path"])
        record = self._read_json(path)
        record["status"] = status
        record["updated_at"] = self._now()

        if vector_id:
            record["vector_id"] = vector_id

        if embedding_model:
            record["embedding_model"] = embedding_model

        if notes:
            record.setdefault("notes", []).append({"note": notes, "created_at": self._now()})

        self._write_json(path, record)

        summary["status"] = status
        summary["updated_at"] = record["updated_at"]
        if vector_id:
            summary["vector_id"] = vector_id
        if embedding_model:
            summary["embedding_model"] = embedding_model

        index["updated_at"] = self._now()
        self._write_json(self.index_path, index)

        return {
            "success": True,
            "vectorization_queue_id": vectorization_queue_id,
            "status": status,
        }

    def get_summary(self) -> Dict[str, Any]:
        index = self._read_index()
        records = list(index.get("records", {}).values())
        queue = list(index.get("vectorization_queue", {}).values())

        avg_originality = (
            sum(float(item.get("originality_score", 0.0)) for item in records) / len(records)
            if records else 0.0
        )
        avg_novelty = (
            sum(float(item.get("novelty_score", 0.0)) for item in records) / len(records)
            if records else 0.0
        )

        return {
            "store_type": "embedding_registry_store",
            "schema_version": index.get("schema_version"),
            "root_dir": str(self.root_dir),
            "record_count": len(records),
            "vectorization_queue_count": len(queue),
            "similarity_event_count": len(index.get("similarity_events", {})),
            "vector_computed_count": sum(1 for item in records if item.get("vector_computed") is True),
            "pending_vectorization_count": sum(1 for item in queue if item.get("status") == "queued"),
            "average_originality_score": round(avg_originality, 3),
            "average_novelty_score": round(avg_novelty, 3),
            "target_object_types": sorted({item.get("target_object_type") for item in records if item.get("target_object_type")}),
            "updated_at": index.get("updated_at"),
        }

    def _deduplication_status(self, embedding_metadata: Dict[str, Any]) -> str:
        originality = float(embedding_metadata.get("originality_score", 0.0))
        threshold = float(embedding_metadata.get("similarity_threshold_used", 0.82))

        if originality >= 0.8:
            return "likely_original"
        if originality >= 0.6:
            return "review_recommended"
        if threshold >= 0.8:
            return "possible_duplicate_or_generic"
        return "unknown"

    def _recommended_embedding_family(self, target_object_type: str) -> str:
        if "dialogue" in target_object_type:
            return "dialogue_style_embedding"
        if "character" in target_object_type:
            return "character_profile_embedding"
        if "world" in target_object_type:
            return "world_lore_embedding"
        if "relationship" in target_object_type:
            return "relationship_dynamics_embedding"
        return "general_story_embedding"

    def _upsert_index_record(self, record: Dict[str, Any], path: Path) -> None:
        index = self._read_index()
        embedding_id = record["embedding_id"]

        index.setdefault("records", {})[embedding_id] = {
            "embedding_id": embedding_id,
            "target_object_id": record["target_object_id"],
            "target_object_type": record["target_object_type"],
            "engine_name": record["engine_name"],
            "project_id": record["project_id"],
            "universe_id": record["universe_id"],
            "embedding_model": record["embedding_model"],
            "vector_id": record["vector_id"],
            "vector_computed": record["vector_computed"],
            "similarity_tags": record["similarity_tags"],
            "retrieval_queries": record["retrieval_queries"],
            "novelty_score": record["novelty_score"],
            "originality_score": record["originality_score"],
            "similarity_threshold_used": record["similarity_threshold_used"],
            "deduplication_status": record["deduplication_status"],
            "record_path": str(path),
            "created_at": record["created_at"],
            "updated_at": record["updated_at"],
        }

        index["updated_at"] = self._now()
        self._write_json(self.index_path, index)

    def _read_index(self) -> Dict[str, Any]:
        self._ensure_dirs()
        return self._read_json(self.index_path)

    def _read_json(self, path: Path) -> Dict[str, Any]:
        return json.loads(path.read_text(encoding="utf-8"))

    def _write_json(self, path: Path, data: Dict[str, Any]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False),
            encoding="utf-8",
        )

    def _safe_name(self, value: str) -> str:
        allowed = []
        for char in str(value):
            if char.isalnum() or char in {"_", "-"}:
                allowed.append(char)
            else:
                allowed.append("_")
        return "".join(allowed).strip("_") or "unnamed"

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

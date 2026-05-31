import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import uuid4


class LearningRegistryStore:
    """Global learning registry for MythOS Engine.

    This is the central persistence layer for learned ontology records, learned
    type candidates, engine learning metadata, provenance records, embedding
    metadata, and training-eligible objects.

    It does not train models yet. It makes the project learning-aware and gives
    later Chunk 8 systems a durable registry to retrieve from, deduplicate,
    evaluate, and train on.

    Current backend:
    - JSON filesystem store

    Later upgrade path:
    - SQLite/Postgres
    - vector DB / FAISS / pgvector
    - learned ontology graph
    - human feedback review queue
    - actual dataset ingestion and training pipelines
    """

    def __init__(self, root_dir: str | Path = "reports/learning") -> None:
        self.root_dir = Path(root_dir)
        self.ontology_dir = self.root_dir / "ontology_records"
        self.type_candidates_dir = self.root_dir / "type_candidates"
        self.metadata_dir = self.root_dir / "engine_learning_metadata"
        self.provenance_dir = self.root_dir / "provenance_records"
        self.embedding_dir = self.root_dir / "embedding_metadata"
        self.training_dir = self.root_dir / "training_eligible_records"
        self.index_path = self.root_dir / "learning_index.json"
        self._ensure_dirs()

    def _ensure_dirs(self) -> None:
        for path in [
            self.ontology_dir,
            self.type_candidates_dir,
            self.metadata_dir,
            self.provenance_dir,
            self.embedding_dir,
            self.training_dir,
        ]:
            path.mkdir(parents=True, exist_ok=True)

        if not self.index_path.exists():
            self._write_json(
                self.index_path,
                {
                    "store_type": "learning_registry_store",
                    "schema_version": "learning_registry_v0.1.0",
                    "created_at": self._now(),
                    "updated_at": self._now(),
                    "ontology_records": {},
                    "type_candidates": {},
                    "engine_learning_metadata": {},
                    "provenance_records": {},
                    "embedding_metadata": {},
                    "training_eligible_records": {},
                },
            )

    def register_learning_metadata(
        self,
        *,
        engine_name: str,
        target_object_id: str,
        target_object_type: str,
        learning_metadata: Dict[str, Any],
        project_id: str = "default_project",
        universe_id: str = "default_universe",
    ) -> Dict[str, Any]:
        """Register a full engine learning metadata payload.

        This method extracts nested ontology records, type candidates,
        provenance records, embedding metadata, and training eligibility.
        """

        if not engine_name:
            raise ValueError("engine_name is required")
        if not target_object_id:
            raise ValueError("target_object_id is required")
        if not target_object_type:
            raise ValueError("target_object_type is required")

        metadata_id = (
            learning_metadata.get("learning_metadata_id")
            or learning_metadata.get("metadata_id")
            or f"learn_{uuid4().hex[:12]}"
        )

        record = {
            "metadata_id": metadata_id,
            "engine_name": engine_name,
            "target_object_id": target_object_id,
            "target_object_type": target_object_type,
            "project_id": project_id,
            "universe_id": universe_id,
            "registered_at": self._now(),
            "learning_metadata": learning_metadata,
            "registry_metadata": {
                "schema_version": "engine_learning_metadata_registry_v0.1.0",
                "source": "engine_output",
                "ready_for_chunk8": True,
            },
        }

        metadata_path = self.metadata_dir / f"{self._safe_name(metadata_id)}.json"
        self._write_json(metadata_path, record)

        ontology_results = []
        for ontology_record in learning_metadata.get("ontology_records", []) or []:
            ontology_results.append(
                self.register_ontology_record(
                    ontology_record=ontology_record,
                    project_id=project_id,
                    universe_id=universe_id,
                    parent_metadata_id=metadata_id,
                )
            )

        type_candidate_results = []
        for type_candidate in learning_metadata.get("learned_type_candidates", []) or []:
            type_candidate_results.append(
                self.register_type_candidate(
                    type_candidate=type_candidate,
                    project_id=project_id,
                    universe_id=universe_id,
                    parent_metadata_id=metadata_id,
                )
            )

        provenance_results = []
        for provenance_record in learning_metadata.get("provenance_records", []) or []:
            provenance_results.append(
                self.register_provenance_record(
                    provenance_record=provenance_record,
                    project_id=project_id,
                    universe_id=universe_id,
                    parent_metadata_id=metadata_id,
                )
            )

        embedding_result = None
        embedding_metadata = learning_metadata.get("embedding_metadata")
        if embedding_metadata:
            embedding_result = self.register_embedding_metadata(
                embedding_metadata=embedding_metadata,
                target_object_id=target_object_id,
                target_object_type=target_object_type,
                project_id=project_id,
                universe_id=universe_id,
                parent_metadata_id=metadata_id,
            )

        training_result = None
        training_eligibility = learning_metadata.get("training_eligibility")
        if training_eligibility and training_eligibility.get("training_eligible") is True:
            training_result = self.register_training_eligible_record(
                target_object_id=target_object_id,
                target_object_type=target_object_type,
                engine_name=engine_name,
                learning_metadata=learning_metadata,
                training_eligibility=training_eligibility,
                project_id=project_id,
                universe_id=universe_id,
                parent_metadata_id=metadata_id,
            )

        self._upsert_index(
            category="engine_learning_metadata",
            record_id=metadata_id,
            summary={
                "metadata_id": metadata_id,
                "engine_name": engine_name,
                "target_object_id": target_object_id,
                "target_object_type": target_object_type,
                "project_id": project_id,
                "universe_id": universe_id,
                "path": str(metadata_path),
                "registered_at": record["registered_at"],
                "ontology_count": len(ontology_results),
                "type_candidate_count": len(type_candidate_results),
                "provenance_count": len(provenance_results),
                "has_embedding_metadata": embedding_result is not None,
                "training_eligible": training_result is not None,
            },
        )

        return {
            "success": True,
            "metadata_id": metadata_id,
            "engine_name": engine_name,
            "target_object_id": target_object_id,
            "target_object_type": target_object_type,
            "metadata_path": str(metadata_path),
            "ontology_registered": len(ontology_results),
            "type_candidates_registered": len(type_candidate_results),
            "provenance_registered": len(provenance_results),
            "embedding_registered": embedding_result is not None,
            "training_record_registered": training_result is not None,
        }

    def register_ontology_record(
        self,
        *,
        ontology_record: Dict[str, Any],
        project_id: str = "default_project",
        universe_id: str = "default_universe",
        parent_metadata_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        ontology_id = (
            ontology_record.get("ontology_id")
            or ontology_record.get("id")
            or f"ont_{uuid4().hex[:12]}"
        )

        record = {
            "ontology_id": ontology_id,
            "project_id": project_id,
            "universe_id": universe_id,
            "parent_metadata_id": parent_metadata_id,
            "registered_at": self._now(),
            "ontology_record": ontology_record,
            "registry_metadata": {
                "ontology_type": ontology_record.get("ontology_type", "unknown"),
                "family": ontology_record.get("family", "unknown"),
                "subtype": ontology_record.get("subtype", "unknown"),
                "generated_by_engine": ontology_record.get("generated_by_engine", "unknown_engine"),
                "learned_from_data": bool(ontology_record.get("learned_from_data", False)),
            },
        }

        path = self.ontology_dir / f"{self._safe_name(ontology_id)}.json"
        self._write_json(path, record)

        self._upsert_index(
            category="ontology_records",
            record_id=ontology_id,
            summary={
                "ontology_id": ontology_id,
                "ontology_type": record["registry_metadata"]["ontology_type"],
                "family": record["registry_metadata"]["family"],
                "subtype": record["registry_metadata"]["subtype"],
                "generated_by_engine": record["registry_metadata"]["generated_by_engine"],
                "project_id": project_id,
                "universe_id": universe_id,
                "path": str(path),
                "registered_at": record["registered_at"],
            },
        )

        return {
            "success": True,
            "ontology_id": ontology_id,
            "path": str(path),
        }

    def register_type_candidate(
        self,
        *,
        type_candidate: Dict[str, Any],
        project_id: str = "default_project",
        universe_id: str = "default_universe",
        parent_metadata_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        registry_id = (
            type_candidate.get("registry_id")
            or type_candidate.get("type_id")
            or f"type_{uuid4().hex[:12]}"
        )

        record = {
            "registry_id": registry_id,
            "project_id": project_id,
            "universe_id": universe_id,
            "parent_metadata_id": parent_metadata_id,
            "registered_at": self._now(),
            "type_candidate": type_candidate,
            "registry_metadata": {
                "type_name": type_candidate.get("type_name", "unknown_type"),
                "type_family": type_candidate.get("type_family", "unknown_family"),
                "type_subfamily": type_candidate.get("type_subfamily", "unknown_subfamily"),
                "type_scope": type_candidate.get("type_scope", "unknown_scope"),
            },
        }

        path = self.type_candidates_dir / f"{self._safe_name(registry_id)}.json"
        self._write_json(path, record)

        self._upsert_index(
            category="type_candidates",
            record_id=registry_id,
            summary={
                "registry_id": registry_id,
                "type_name": record["registry_metadata"]["type_name"],
                "type_family": record["registry_metadata"]["type_family"],
                "type_subfamily": record["registry_metadata"]["type_subfamily"],
                "type_scope": record["registry_metadata"]["type_scope"],
                "project_id": project_id,
                "universe_id": universe_id,
                "path": str(path),
                "registered_at": record["registered_at"],
            },
        )

        return {
            "success": True,
            "registry_id": registry_id,
            "path": str(path),
        }

    def register_provenance_record(
        self,
        *,
        provenance_record: Dict[str, Any],
        project_id: str = "default_project",
        universe_id: str = "default_universe",
        parent_metadata_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        provenance_id = (
            provenance_record.get("provenance_id")
            or provenance_record.get("source_id")
            or f"prov_{uuid4().hex[:12]}"
        )

        record = {
            "provenance_id": provenance_id,
            "project_id": project_id,
            "universe_id": universe_id,
            "parent_metadata_id": parent_metadata_id,
            "registered_at": self._now(),
            "provenance_record": provenance_record,
            "registry_metadata": {
                "source_name": provenance_record.get("source_name", "unknown_source"),
                "source_type": provenance_record.get("source_type", "unknown_type"),
                "dataset_family": provenance_record.get("dataset_family", "unknown_family"),
                "usage_allowed": bool(provenance_record.get("usage_allowed", False)),
                "human_review_required": bool(provenance_record.get("human_review_required", True)),
            },
        }

        path = self.provenance_dir / f"{self._safe_name(provenance_id)}.json"
        self._write_json(path, record)

        self._upsert_index(
            category="provenance_records",
            record_id=provenance_id,
            summary={
                "provenance_id": provenance_id,
                "source_name": record["registry_metadata"]["source_name"],
                "source_type": record["registry_metadata"]["source_type"],
                "dataset_family": record["registry_metadata"]["dataset_family"],
                "usage_allowed": record["registry_metadata"]["usage_allowed"],
                "human_review_required": record["registry_metadata"]["human_review_required"],
                "project_id": project_id,
                "universe_id": universe_id,
                "path": str(path),
                "registered_at": record["registered_at"],
            },
        )

        return {
            "success": True,
            "provenance_id": provenance_id,
            "path": str(path),
        }

    def register_embedding_metadata(
        self,
        *,
        embedding_metadata: Dict[str, Any],
        target_object_id: str,
        target_object_type: str,
        project_id: str = "default_project",
        universe_id: str = "default_universe",
        parent_metadata_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        embedding_id = (
            embedding_metadata.get("embedding_id")
            or embedding_metadata.get("vector_id")
            or f"emb_{uuid4().hex[:12]}"
        )

        record = {
            "embedding_id": embedding_id,
            "target_object_id": target_object_id,
            "target_object_type": target_object_type,
            "project_id": project_id,
            "universe_id": universe_id,
            "parent_metadata_id": parent_metadata_id,
            "registered_at": self._now(),
            "embedding_metadata": embedding_metadata,
            "registry_metadata": {
                "embedding_model": embedding_metadata.get("embedding_model", "future_embedding_model_not_computed_yet"),
                "novelty_score": float(embedding_metadata.get("novelty_score", 0.0)),
                "originality_score": float(embedding_metadata.get("originality_score", 0.0)),
                "similarity_threshold_used": float(embedding_metadata.get("similarity_threshold_used", 0.0)),
                "similarity_tag_count": len(embedding_metadata.get("similarity_tags", []) or []),
            },
        }

        path = self.embedding_dir / f"{self._safe_name(embedding_id)}.json"
        self._write_json(path, record)

        self._upsert_index(
            category="embedding_metadata",
            record_id=embedding_id,
            summary={
                "embedding_id": embedding_id,
                "target_object_id": target_object_id,
                "target_object_type": target_object_type,
                "embedding_model": record["registry_metadata"]["embedding_model"],
                "novelty_score": record["registry_metadata"]["novelty_score"],
                "originality_score": record["registry_metadata"]["originality_score"],
                "project_id": project_id,
                "universe_id": universe_id,
                "path": str(path),
                "registered_at": record["registered_at"],
            },
        )

        return {
            "success": True,
            "embedding_id": embedding_id,
            "path": str(path),
        }

    def register_training_eligible_record(
        self,
        *,
        target_object_id: str,
        target_object_type: str,
        engine_name: str,
        learning_metadata: Dict[str, Any],
        training_eligibility: Dict[str, Any],
        project_id: str = "default_project",
        universe_id: str = "default_universe",
        parent_metadata_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        training_record_id = f"trainable_{uuid4().hex[:12]}"

        record = {
            "training_record_id": training_record_id,
            "target_object_id": target_object_id,
            "target_object_type": target_object_type,
            "engine_name": engine_name,
            "project_id": project_id,
            "universe_id": universe_id,
            "parent_metadata_id": parent_metadata_id,
            "registered_at": self._now(),
            "learning_metadata": learning_metadata,
            "training_eligibility": training_eligibility,
            "registry_metadata": {
                "recommended_split": training_eligibility.get("recommended_split", "human_review_queue"),
                "quality_score": float(training_eligibility.get("quality_score", 0.0)),
                "consistency_score": float(training_eligibility.get("consistency_score", 0.0)),
                "originality_score": float(training_eligibility.get("originality_score", 0.0)),
                "safety_score": float(training_eligibility.get("safety_score", 0.0)),
                "human_review_required": bool(training_eligibility.get("human_review_required", True)),
            },
        }

        path = self.training_dir / f"{self._safe_name(training_record_id)}.json"
        self._write_json(path, record)

        self._upsert_index(
            category="training_eligible_records",
            record_id=training_record_id,
            summary={
                "training_record_id": training_record_id,
                "target_object_id": target_object_id,
                "target_object_type": target_object_type,
                "engine_name": engine_name,
                "recommended_split": record["registry_metadata"]["recommended_split"],
                "quality_score": record["registry_metadata"]["quality_score"],
                "consistency_score": record["registry_metadata"]["consistency_score"],
                "originality_score": record["registry_metadata"]["originality_score"],
                "safety_score": record["registry_metadata"]["safety_score"],
                "project_id": project_id,
                "universe_id": universe_id,
                "path": str(path),
                "registered_at": record["registered_at"],
            },
        )

        return {
            "success": True,
            "training_record_id": training_record_id,
            "path": str(path),
        }

    def list_records(
        self,
        *,
        category: str,
        project_id: Optional[str] = None,
        universe_id: Optional[str] = None,
        engine_name: Optional[str] = None,
        target_object_type: Optional[str] = None,
        type_family: Optional[str] = None,
        min_quality_score: Optional[float] = None,
    ) -> List[Dict[str, Any]]:
        index = self._read_index()

        if category not in index:
            raise ValueError(f"Unknown learning registry category: {category}")

        records = list(index.get(category, {}).values())

        if project_id is not None:
            records = [item for item in records if item.get("project_id") == project_id]

        if universe_id is not None:
            records = [item for item in records if item.get("universe_id") == universe_id]

        if engine_name is not None:
            records = [item for item in records if item.get("engine_name") == engine_name or item.get("generated_by_engine") == engine_name]

        if target_object_type is not None:
            records = [item for item in records if item.get("target_object_type") == target_object_type]

        if type_family is not None:
            records = [item for item in records if item.get("type_family") == type_family or item.get("family") == type_family]

        if min_quality_score is not None:
            records = [
                item for item in records
                if float(item.get("quality_score", item.get("originality_score", 0.0))) >= min_quality_score
            ]

        return sorted(records, key=lambda item: item.get("registered_at", ""), reverse=True)

    def load_record(self, *, category: str, record_id: str) -> Dict[str, Any]:
        index = self._read_index()

        if category not in index:
            raise ValueError(f"Unknown learning registry category: {category}")

        summary = index.get(category, {}).get(record_id)
        if not summary:
            raise FileNotFoundError(f"No record found in {category} for {record_id}")

        path = Path(summary["path"])
        if not path.exists():
            raise FileNotFoundError(f"Indexed record path does not exist: {path}")

        return self._read_json(path)

    def get_summary(self) -> Dict[str, Any]:
        index = self._read_index()

        categories = [
            "ontology_records",
            "type_candidates",
            "engine_learning_metadata",
            "provenance_records",
            "embedding_metadata",
            "training_eligible_records",
        ]

        counts = {category: len(index.get(category, {})) for category in categories}

        return {
            "store_type": "learning_registry_store",
            "schema_version": index.get("schema_version", "learning_registry_v0.1.0"),
            "root_dir": str(self.root_dir),
            "counts": counts,
            "total_records": sum(counts.values()),
            "index_path": str(self.index_path),
            "updated_at": index.get("updated_at"),
        }

    def _upsert_index(self, *, category: str, record_id: str, summary: Dict[str, Any]) -> None:
        index = self._read_index()
        index.setdefault(category, {})[record_id] = summary
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

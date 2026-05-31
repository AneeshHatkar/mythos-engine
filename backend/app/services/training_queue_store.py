import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import uuid4


class TrainingQueueStore:
    """Global training queue store for future Chunk 8 learning.

    This store does not train models. It queues approved, high-quality,
    provenance-safe records for later training/RAG/evaluation pipelines.

    The queue separates:
    - train
    - eval
    - human_review_queue
    - rejected
    """

    VALID_STATUSES = {"queued", "approved", "rejected", "trained_later", "human_review"}
    VALID_SPLITS = {"train", "eval", "human_review_queue", "rejected"}

    def __init__(self, root_dir: str | Path = "reports/training_queue") -> None:
        self.root_dir = Path(root_dir)
        self.records_dir = self.root_dir / "records"
        self.payloads_dir = self.root_dir / "payloads"
        self.index_path = self.root_dir / "training_queue_index.json"
        self._ensure_dirs()

    def _ensure_dirs(self) -> None:
        self.records_dir.mkdir(parents=True, exist_ok=True)
        self.payloads_dir.mkdir(parents=True, exist_ok=True)

        if not self.index_path.exists():
            self._write_json(
                self.index_path,
                {
                    "store_type": "training_queue_store",
                    "schema_version": "training_queue_v0.1.0",
                    "created_at": self._now(),
                    "updated_at": self._now(),
                    "records": {},
                },
            )

    def enqueue(
        self,
        *,
        target_object_id: str,
        target_object_type: str,
        engine_name: str,
        payload: Dict[str, Any],
        training_eligibility: Dict[str, Any],
        project_id: str = "default_project",
        universe_id: str = "default_universe",
        provenance_id: Optional[str] = None,
        learning_metadata_id: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        if not target_object_id:
            raise ValueError("target_object_id is required")
        if not target_object_type:
            raise ValueError("target_object_type is required")
        if not engine_name:
            raise ValueError("engine_name is required")

        training_eligible = bool(training_eligibility.get("training_eligible", False))
        do_not_train = bool(training_eligibility.get("do_not_train", not training_eligible))
        human_review_required = bool(training_eligibility.get("human_review_required", not training_eligible))

        recommended_split = training_eligibility.get("recommended_split") or (
            "train" if training_eligible else "human_review_queue"
        )

        if do_not_train:
            recommended_split = "human_review_queue" if human_review_required else "rejected"

        if recommended_split not in self.VALID_SPLITS:
            recommended_split = "human_review_queue"

        status = "queued" if training_eligible and not do_not_train else "human_review"
        if recommended_split == "rejected":
            status = "rejected"

        record_id = f"trainq_{uuid4().hex[:12]}"
        created_at = self._now()

        payload_path = self.payloads_dir / f"{self._safe_name(record_id)}_payload.json"
        self._write_json(payload_path, payload)

        record = {
            "training_queue_id": record_id,
            "target_object_id": target_object_id,
            "target_object_type": target_object_type,
            "engine_name": engine_name,
            "project_id": project_id,
            "universe_id": universe_id,
            "provenance_id": provenance_id,
            "learning_metadata_id": learning_metadata_id,
            "status": status,
            "recommended_split": recommended_split,
            "training_eligible": training_eligible,
            "do_not_train": do_not_train,
            "human_review_required": human_review_required,
            "quality_score": float(training_eligibility.get("quality_score", 0.0)),
            "consistency_score": float(training_eligibility.get("consistency_score", 0.0)),
            "originality_score": float(training_eligibility.get("originality_score", 0.0)),
            "safety_score": float(training_eligibility.get("safety_score", 0.0)),
            "rejection_reasons": training_eligibility.get("rejection_reasons", []) or [],
            "tags": tags or [],
            "payload_path": str(payload_path),
            "created_at": created_at,
            "updated_at": created_at,
            "queue_metadata": {
                "schema_version": "training_queue_record_v0.1.0",
                "future_chunk8_ready": training_eligible and not do_not_train,
                "requires_human_review_before_training": human_review_required,
            },
        }

        record_path = self.records_dir / f"{self._safe_name(record_id)}.json"
        self._write_json(record_path, record)
        self._upsert_index_record(record, record_path)

        return {
            "success": True,
            "training_queue_id": record_id,
            "status": status,
            "recommended_split": recommended_split,
            "record_path": str(record_path),
            "payload_path": str(payload_path),
            "future_chunk8_ready": record["queue_metadata"]["future_chunk8_ready"],
        }

    def enqueue_from_learning_metadata(
        self,
        learning_metadata: Dict[str, Any],
        *,
        payload: Dict[str, Any],
        project_id: str = "default_project",
        universe_id: str = "default_universe",
        provenance_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        return self.enqueue(
            target_object_id=learning_metadata.get("target_object_id", "unknown_target"),
            target_object_type=learning_metadata.get("target_object_type", "unknown_target_type"),
            engine_name=learning_metadata.get("engine_name", "unknown_engine"),
            payload=payload,
            training_eligibility=learning_metadata.get("training_eligibility", {}),
            project_id=project_id,
            universe_id=universe_id,
            provenance_id=provenance_id,
            learning_metadata_id=learning_metadata.get("learning_metadata_id"),
            tags=list(learning_metadata.get("generated_training_labels", {}).keys()),
        )

    def update_status(
        self,
        *,
        training_queue_id: str,
        status: str,
        notes: Optional[str] = None,
    ) -> Dict[str, Any]:
        if status not in self.VALID_STATUSES:
            raise ValueError(f"Invalid training queue status: {status}")

        record = self.load_record(training_queue_id)
        record["status"] = status
        record["updated_at"] = self._now()

        if notes:
            record.setdefault("status_notes", []).append(
                {
                    "note": notes,
                    "created_at": self._now(),
                }
            )

        record_path = self.records_dir / f"{self._safe_name(training_queue_id)}.json"
        self._write_json(record_path, record)
        self._upsert_index_record(record, record_path)

        return {
            "success": True,
            "training_queue_id": training_queue_id,
            "status": status,
        }

    def load_record(self, training_queue_id: str) -> Dict[str, Any]:
        index = self._read_index()
        summary = index.get("records", {}).get(training_queue_id)

        if not summary:
            raise FileNotFoundError(f"No training queue record found for {training_queue_id}")

        path = Path(summary["record_path"])
        if not path.exists():
            raise FileNotFoundError(f"Indexed training queue path missing: {path}")

        return self._read_json(path)

    def load_payload(self, training_queue_id: str) -> Dict[str, Any]:
        record = self.load_record(training_queue_id)
        path = Path(record["payload_path"])

        if not path.exists():
            raise FileNotFoundError(f"Training queue payload path missing: {path}")

        return self._read_json(path)

    def list_records(
        self,
        *,
        status: Optional[str] = None,
        recommended_split: Optional[str] = None,
        target_object_type: Optional[str] = None,
        engine_name: Optional[str] = None,
        project_id: Optional[str] = None,
        universe_id: Optional[str] = None,
        min_quality_score: Optional[float] = None,
        future_chunk8_ready: Optional[bool] = None,
    ) -> List[Dict[str, Any]]:
        records = list(self._read_index().get("records", {}).values())

        if status is not None:
            records = [item for item in records if item.get("status") == status]

        if recommended_split is not None:
            records = [item for item in records if item.get("recommended_split") == recommended_split]

        if target_object_type is not None:
            records = [item for item in records if item.get("target_object_type") == target_object_type]

        if engine_name is not None:
            records = [item for item in records if item.get("engine_name") == engine_name]

        if project_id is not None:
            records = [item for item in records if item.get("project_id") == project_id]

        if universe_id is not None:
            records = [item for item in records if item.get("universe_id") == universe_id]

        if min_quality_score is not None:
            records = [item for item in records if float(item.get("quality_score", 0.0)) >= min_quality_score]

        if future_chunk8_ready is not None:
            records = [item for item in records if item.get("future_chunk8_ready") is future_chunk8_ready]

        return sorted(records, key=lambda item: item.get("created_at", ""), reverse=True)

    def get_summary(self) -> Dict[str, Any]:
        records = list(self._read_index().get("records", {}).values())

        return {
            "store_type": "training_queue_store",
            "root_dir": str(self.root_dir),
            "record_count": len(records),
            "queued_count": sum(1 for item in records if item.get("status") == "queued"),
            "human_review_count": sum(1 for item in records if item.get("status") == "human_review"),
            "rejected_count": sum(1 for item in records if item.get("status") == "rejected"),
            "future_chunk8_ready_count": sum(1 for item in records if item.get("future_chunk8_ready") is True),
            "train_split_count": sum(1 for item in records if item.get("recommended_split") == "train"),
            "eval_split_count": sum(1 for item in records if item.get("recommended_split") == "eval"),
            "target_object_types": sorted({item.get("target_object_type") for item in records if item.get("target_object_type")}),
            "updated_at": self._read_index().get("updated_at"),
        }

    def _upsert_index_record(self, record: Dict[str, Any], record_path: Path) -> None:
        index = self._read_index()
        queue_id = record["training_queue_id"]

        index.setdefault("records", {})[queue_id] = {
            "training_queue_id": queue_id,
            "target_object_id": record["target_object_id"],
            "target_object_type": record["target_object_type"],
            "engine_name": record["engine_name"],
            "project_id": record["project_id"],
            "universe_id": record["universe_id"],
            "status": record["status"],
            "recommended_split": record["recommended_split"],
            "training_eligible": record["training_eligible"],
            "do_not_train": record["do_not_train"],
            "human_review_required": record["human_review_required"],
            "quality_score": record["quality_score"],
            "consistency_score": record["consistency_score"],
            "originality_score": record["originality_score"],
            "safety_score": record["safety_score"],
            "future_chunk8_ready": record["queue_metadata"]["future_chunk8_ready"],
            "record_path": str(record_path),
            "payload_path": record["payload_path"],
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

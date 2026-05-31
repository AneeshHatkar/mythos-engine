import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import uuid4


class ProvenanceStore:
    """Global dataset/source provenance governance store.

    This store answers one critical research-grade question:

    Can this data/output be used for retrieval, evaluation, training, export,
    or human review?

    It does not train anything. It governs data/source permissions so MythOS
    can safely scale across world datasets, people datasets, dialogue datasets,
    emotion datasets, novels, scripts, reviews, and human-approved synthetic
    examples later.
    """

    def __init__(self, root_dir: str | Path = "reports/provenance") -> None:
        self.root_dir = Path(root_dir)
        self.records_dir = self.root_dir / "records"
        self.audit_dir = self.root_dir / "audit"
        self.index_path = self.root_dir / "provenance_index.json"
        self._ensure_dirs()

    def _ensure_dirs(self) -> None:
        self.records_dir.mkdir(parents=True, exist_ok=True)
        self.audit_dir.mkdir(parents=True, exist_ok=True)

        if not self.index_path.exists():
            self._write_json(
                self.index_path,
                {
                    "store_type": "provenance_store",
                    "schema_version": "provenance_store_v0.1.0",
                    "created_at": self._now(),
                    "updated_at": self._now(),
                    "records": {},
                    "audit_events": {},
                },
            )

    def register_source(
        self,
        *,
        source_name: str,
        source_type: str,
        dataset_family: str,
        usage_allowed: bool,
        human_review_required: bool = True,
        do_not_train: bool = False,
        license_name: Optional[str] = None,
        license_url: Optional[str] = None,
        source_url: Optional[str] = None,
        notes: Optional[str] = None,
        project_id: str = "default_project",
        universe_id: str = "default_universe",
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        if not source_name:
            raise ValueError("source_name is required")
        if not source_type:
            raise ValueError("source_type is required")
        if not dataset_family:
            raise ValueError("dataset_family is required")

        provenance_id = f"prov_{uuid4().hex[:12]}"
        created_at = self._now()

        allowed_for_training = bool(usage_allowed) and not bool(do_not_train) and not bool(human_review_required)

        record = {
            "provenance_id": provenance_id,
            "source_name": source_name,
            "source_type": source_type,
            "dataset_family": dataset_family,
            "usage_allowed": bool(usage_allowed),
            "human_review_required": bool(human_review_required),
            "do_not_train": bool(do_not_train),
            "allowed_for_training": allowed_for_training,
            "allowed_for_retrieval": bool(usage_allowed),
            "allowed_for_evaluation": bool(usage_allowed),
            "license_name": license_name,
            "license_url": license_url,
            "source_url": source_url,
            "notes": notes,
            "project_id": project_id,
            "universe_id": universe_id,
            "tags": tags or [],
            "metadata": metadata or {},
            "created_at": created_at,
            "updated_at": created_at,
            "governance_flags": self._governance_flags(
                usage_allowed=usage_allowed,
                human_review_required=human_review_required,
                do_not_train=do_not_train,
                license_name=license_name,
            ),
        }

        path = self.records_dir / f"{self._safe_name(provenance_id)}.json"
        self._write_json(path, record)

        self._upsert_index_record(record, path)
        self.add_audit_event(
            event_type="provenance_record_created",
            provenance_id=provenance_id,
            details={
                "source_name": source_name,
                "dataset_family": dataset_family,
                "allowed_for_training": allowed_for_training,
            },
        )

        return {
            "success": True,
            "provenance_id": provenance_id,
            "path": str(path),
            "allowed_for_training": allowed_for_training,
            "allowed_for_retrieval": record["allowed_for_retrieval"],
            "governance_flags": record["governance_flags"],
        }

    def register_from_engine_provenance(
        self,
        provenance_record: Dict[str, Any],
        *,
        project_id: str = "default_project",
        universe_id: str = "default_universe",
    ) -> Dict[str, Any]:
        return self.register_source(
            source_name=provenance_record.get("source_name", "unknown_source"),
            source_type=provenance_record.get("source_type", "unknown_source_type"),
            dataset_family=provenance_record.get("dataset_family", "unknown_dataset_family"),
            usage_allowed=bool(provenance_record.get("usage_allowed", False)),
            human_review_required=bool(provenance_record.get("human_review_required", True)),
            do_not_train=bool(provenance_record.get("do_not_train", False)),
            license_name=provenance_record.get("license_name"),
            license_url=provenance_record.get("license_url"),
            source_url=provenance_record.get("source_url"),
            notes=provenance_record.get("notes"),
            project_id=project_id,
            universe_id=universe_id,
            tags=(provenance_record.get("genre_tags") or []) + (provenance_record.get("culture_tags") or []),
            metadata=provenance_record,
        )

    def load_record(self, provenance_id: str) -> Dict[str, Any]:
        index = self._read_index()
        summary = index.get("records", {}).get(provenance_id)

        if not summary:
            raise FileNotFoundError(f"No provenance record found for {provenance_id}")

        path = Path(summary["path"])
        if not path.exists():
            raise FileNotFoundError(f"Indexed provenance path missing: {path}")

        return self._read_json(path)

    def list_records(
        self,
        *,
        dataset_family: Optional[str] = None,
        source_type: Optional[str] = None,
        project_id: Optional[str] = None,
        universe_id: Optional[str] = None,
        allowed_for_training: Optional[bool] = None,
        usage_allowed: Optional[bool] = None,
    ) -> List[Dict[str, Any]]:
        records = list(self._read_index().get("records", {}).values())

        if dataset_family is not None:
            records = [item for item in records if item.get("dataset_family") == dataset_family]

        if source_type is not None:
            records = [item for item in records if item.get("source_type") == source_type]

        if project_id is not None:
            records = [item for item in records if item.get("project_id") == project_id]

        if universe_id is not None:
            records = [item for item in records if item.get("universe_id") == universe_id]

        if allowed_for_training is not None:
            records = [item for item in records if item.get("allowed_for_training") is allowed_for_training]

        if usage_allowed is not None:
            records = [item for item in records if item.get("usage_allowed") is usage_allowed]

        return sorted(records, key=lambda item: item.get("created_at", ""), reverse=True)

    def add_audit_event(
        self,
        *,
        event_type: str,
        provenance_id: Optional[str],
        details: Dict[str, Any],
    ) -> Dict[str, Any]:
        if not event_type:
            raise ValueError("event_type is required")

        audit_id = f"provaudit_{uuid4().hex[:12]}"
        created_at = self._now()

        event = {
            "audit_id": audit_id,
            "event_type": event_type,
            "provenance_id": provenance_id,
            "details": details,
            "created_at": created_at,
        }

        path = self.audit_dir / f"{self._safe_name(audit_id)}.json"
        self._write_json(path, event)

        index = self._read_index()
        index.setdefault("audit_events", {})[audit_id] = {
            "audit_id": audit_id,
            "event_type": event_type,
            "provenance_id": provenance_id,
            "path": str(path),
            "created_at": created_at,
        }
        index["updated_at"] = self._now()
        self._write_json(self.index_path, index)

        return {
            "success": True,
            "audit_id": audit_id,
            "path": str(path),
        }

    def get_summary(self) -> Dict[str, Any]:
        index = self._read_index()
        records = list(index.get("records", {}).values())

        return {
            "store_type": "provenance_store",
            "schema_version": index.get("schema_version"),
            "root_dir": str(self.root_dir),
            "record_count": len(records),
            "audit_event_count": len(index.get("audit_events", {})),
            "training_allowed_count": sum(1 for item in records if item.get("allowed_for_training") is True),
            "retrieval_allowed_count": sum(1 for item in records if item.get("allowed_for_retrieval") is True),
            "human_review_required_count": sum(1 for item in records if item.get("human_review_required") is True),
            "do_not_train_count": sum(1 for item in records if item.get("do_not_train") is True),
            "dataset_families": sorted({item.get("dataset_family") for item in records if item.get("dataset_family")}),
            "updated_at": index.get("updated_at"),
        }

    def _governance_flags(
        self,
        *,
        usage_allowed: bool,
        human_review_required: bool,
        do_not_train: bool,
        license_name: Optional[str],
    ) -> List[str]:
        flags = []

        if not usage_allowed:
            flags.append("usage_not_allowed")

        if human_review_required:
            flags.append("human_review_required")

        if do_not_train:
            flags.append("do_not_train")

        if not license_name:
            flags.append("license_not_recorded")

        if usage_allowed and not human_review_required and not do_not_train:
            flags.append("training_candidate_source")

        return flags

    def _upsert_index_record(self, record: Dict[str, Any], path: Path) -> None:
        index = self._read_index()
        provenance_id = record["provenance_id"]
        index.setdefault("records", {})[provenance_id] = {
            "provenance_id": provenance_id,
            "source_name": record["source_name"],
            "source_type": record["source_type"],
            "dataset_family": record["dataset_family"],
            "usage_allowed": record["usage_allowed"],
            "human_review_required": record["human_review_required"],
            "do_not_train": record["do_not_train"],
            "allowed_for_training": record["allowed_for_training"],
            "allowed_for_retrieval": record["allowed_for_retrieval"],
            "project_id": record["project_id"],
            "universe_id": record["universe_id"],
            "governance_flags": record["governance_flags"],
            "path": str(path),
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

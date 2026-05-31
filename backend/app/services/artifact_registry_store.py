import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from backend.app.schemas.artifacts import ArtifactRecord, ArtifactRegistrySummary
from backend.app.schemas.global_refs import CanonStatus


class ArtifactRegistryStore:
    """Persistent registry for generated MythOS artifacts.

    This keeps generated outputs auditable instead of letting them disappear
    after one run.
    """

    def __init__(self, root: str | Path = "reports/artifact_registry") -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self.records_path = self.root / "artifact_records.jsonl"

    def save_artifact(self, artifact: ArtifactRecord | Dict[str, Any]) -> Dict[str, Any]:
        record = artifact if isinstance(artifact, ArtifactRecord) else ArtifactRecord.model_validate(artifact)
        payload = record.model_dump()

        with self.records_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(payload, sort_keys=True, ensure_ascii=False) + "\n")

        return {
            "success": True,
            "artifact_id": record.artifact_id,
            "artifact_type": record.artifact_type,
            "project_id": record.project_id,
            "universe_id": record.universe_id,
            "canon_status": record.canon_status,
        }

    def list_artifacts(
        self,
        *,
        project_id: Optional[str] = None,
        universe_id: Optional[str] = None,
        artifact_type: Optional[str] = None,
        canon_status: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        records = self._read_all()

        if project_id:
            records = [item for item in records if item.get("project_id") == project_id]
        if universe_id:
            records = [item for item in records if item.get("universe_id") == universe_id]
        if artifact_type:
            records = [item for item in records if item.get("artifact_type") == artifact_type]
        if canon_status:
            records = [item for item in records if str(item.get("canon_status")) == canon_status]

        return records

    def get_artifact(self, artifact_id: str) -> Optional[Dict[str, Any]]:
        for record in reversed(self._read_all()):
            if record.get("artifact_id") == artifact_id:
                return record
        return None

    def summarize(self, *, project_id: str = "default_project", universe_id: str = "default_universe") -> Dict[str, Any]:
        records = self.list_artifacts(project_id=project_id, universe_id=universe_id)

        artifact_types: Dict[str, int] = {}
        canon_count = 0
        draft_count = 0
        branch_count = 0

        for item in records:
            artifact_types[item.get("artifact_type", "unknown")] = artifact_types.get(item.get("artifact_type", "unknown"), 0) + 1
            status = str(item.get("canon_status", "draft"))
            if status == CanonStatus.CANON.value:
                canon_count += 1
            if status == CanonStatus.DRAFT.value:
                draft_count += 1
            if status == CanonStatus.ALTERNATE_BRANCH.value:
                branch_count += 1

        summary = ArtifactRegistrySummary(
            project_id=project_id,
            universe_id=universe_id,
            artifact_count=len(records),
            artifact_types=artifact_types,
            canon_count=canon_count,
            draft_count=draft_count,
            branch_count=branch_count,
            latest_artifact_ids=[item["artifact_id"] for item in records[-10:] if item.get("artifact_id")],
        )

        return summary.model_dump()

    def _read_all(self) -> List[Dict[str, Any]]:
        if not self.records_path.exists():
            return []

        records = []
        with self.records_path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    records.append(json.loads(line))
        return records

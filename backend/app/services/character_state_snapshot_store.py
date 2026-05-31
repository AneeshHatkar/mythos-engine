import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from backend.app.schemas.global_refs import StateSnapshotRef


class CharacterStateSnapshotStore:
    """Stores mutable character state snapshots separate from the stable character bible."""

    def __init__(self, root: str | Path = "reports/character_state_snapshots") -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self.records_path = self.root / "character_state_snapshots.jsonl"

    def create_snapshot(
        self,
        *,
        character_id: str,
        character_state: Dict[str, Any],
        project_id: str = "default_project",
        universe_id: str = "default_universe",
        branch_id: str = "main",
        timeline_id: str = "main",
        tick_number: int = 0,
        created_after_event_id: Optional[str] = None,
        rollback_allowed: bool = True,
    ) -> Dict[str, Any]:
        state_hash = self.compute_state_hash(character_state)

        snapshot_ref = StateSnapshotRef(
            simulation_id=character_id,
            tick_number=tick_number,
            state_hash=state_hash,
            created_after_event_id=created_after_event_id,
            rollback_allowed=rollback_allowed,
        )

        record = {
            "snapshot_id": snapshot_ref.snapshot_id,
            "character_id": character_id,
            "project_id": project_id,
            "universe_id": universe_id,
            "branch_id": branch_id,
            "timeline_id": timeline_id,
            "tick_number": tick_number,
            "state_hash": state_hash,
            "snapshot_ref": snapshot_ref.model_dump(),
            "character_state": character_state,
        }

        with self.records_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, sort_keys=True, ensure_ascii=False) + "\n")

        return {
            "success": True,
            "snapshot_id": snapshot_ref.snapshot_id,
            "character_id": character_id,
            "state_hash": state_hash,
            "snapshot_ref": snapshot_ref.model_dump(),
        }

    def get_snapshot(self, snapshot_id: str) -> Optional[Dict[str, Any]]:
        for record in reversed(self._read_all()):
            if record.get("snapshot_id") == snapshot_id:
                return record
        return None

    def list_snapshots(self, *, character_id: Optional[str] = None) -> List[Dict[str, Any]]:
        records = self._read_all()
        if character_id:
            records = [item for item in records if item.get("character_id") == character_id]
        return records

    def latest_snapshot(self, character_id: str) -> Optional[Dict[str, Any]]:
        records = self.list_snapshots(character_id=character_id)
        return records[-1] if records else None

    def compute_state_hash(self, character_state: Dict[str, Any]) -> str:
        raw = json.dumps(character_state, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

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

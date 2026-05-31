import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import uuid4


class CharacterRunStore:
    """JSON-backed persistence for Chunk 3 character profiles and run outputs.

    This is intentionally lightweight for now. It gives the project durable
    storage without forcing a database dependency before the API/orchestrator
    layer is stable.

    Later upgrade path:
    - SQLite/Postgres run table
    - vector indexes for profiles/voice/originality
    - artifact storage for exported bibles
    - training queue table for Chunk 8
    """

    def __init__(self, root_dir: str | Path = "reports/characters") -> None:
        self.root_dir = Path(root_dir)
        self.profiles_dir = self.root_dir / "profiles"
        self.runs_dir = self.root_dir / "runs"
        self.index_path = self.root_dir / "character_index.json"
        self._ensure_dirs()

    def _ensure_dirs(self) -> None:
        self.profiles_dir.mkdir(parents=True, exist_ok=True)
        self.runs_dir.mkdir(parents=True, exist_ok=True)
        if not self.index_path.exists():
            self._write_json(
                self.index_path,
                {
                    "store_type": "character_run_store",
                    "created_at": self._now(),
                    "updated_at": self._now(),
                    "characters": {},
                    "runs": {},
                },
            )

    def save_character_profile(
        self,
        *,
        character_id: str,
        profile: Dict[str, Any],
        orchestration_report: Optional[Dict[str, Any]] = None,
        quality_report: Optional[Dict[str, Any]] = None,
        learning_metadata: Optional[Dict[str, Any]] = None,
        project_id: str = "default_project",
        universe_id: str = "default_universe",
    ) -> Dict[str, Any]:
        if not character_id:
            raise ValueError("character_id is required to save a character profile")

        record_id = f"charrec_{uuid4().hex[:12]}"
        created_at = self._now()

        record = {
            "record_id": record_id,
            "character_id": character_id,
            "project_id": project_id,
            "universe_id": universe_id,
            "created_at": created_at,
            "updated_at": created_at,
            "profile": profile,
            "orchestration_report": orchestration_report or {},
            "quality_report": quality_report or self._extract_quality_report(profile),
            "learning_metadata": learning_metadata or {},
            "store_metadata": {
                "schema_version": "character_store_v0.3.0",
                "storage_backend": "json_filesystem",
                "ready_for_api": True,
                "ready_for_export": bool(orchestration_report or profile),
                "ready_for_chunk8_training_later": bool(learning_metadata),
            },
        }

        profile_path = self._profile_path(character_id)
        self._write_json(profile_path, record)
        self._upsert_index_character(record, profile_path)

        return {
            "success": True,
            "record_id": record_id,
            "character_id": character_id,
            "profile_path": str(profile_path),
            "stored_at": created_at,
        }

    def save_engine_run(
        self,
        *,
        engine_name: str,
        character_id: str,
        input_payload: Dict[str, Any],
        result_payload: Dict[str, Any],
        project_id: str = "default_project",
        universe_id: str = "default_universe",
        run_label: Optional[str] = None,
    ) -> Dict[str, Any]:
        if not engine_name:
            raise ValueError("engine_name is required")
        if not character_id:
            raise ValueError("character_id is required")

        run_id = f"charrun_{uuid4().hex[:12]}"
        created_at = self._now()

        record = {
            "run_id": run_id,
            "run_label": run_label or engine_name,
            "engine_name": engine_name,
            "character_id": character_id,
            "project_id": project_id,
            "universe_id": universe_id,
            "created_at": created_at,
            "input_payload": input_payload,
            "result_payload": result_payload,
            "run_metadata": {
                "schema_version": "character_run_v0.3.0",
                "storage_backend": "json_filesystem",
                "success": bool(result_payload.get("success", True)),
                "generated_object_ids": result_payload.get("generated_object_ids", []),
            },
        }

        run_path = self._run_path(run_id)
        self._write_json(run_path, record)
        self._upsert_index_run(record, run_path)

        return {
            "success": True,
            "run_id": run_id,
            "character_id": character_id,
            "engine_name": engine_name,
            "run_path": str(run_path),
            "stored_at": created_at,
        }

    def load_character_profile(self, character_id: str) -> Dict[str, Any]:
        path = self._profile_path(character_id)
        if not path.exists():
            raise FileNotFoundError(f"No saved character profile found for {character_id}")
        return self._read_json(path)

    def load_engine_run(self, run_id: str) -> Dict[str, Any]:
        path = self._run_path(run_id)
        if not path.exists():
            raise FileNotFoundError(f"No saved character run found for {run_id}")
        return self._read_json(path)

    def list_character_profiles(
        self,
        *,
        project_id: Optional[str] = None,
        universe_id: Optional[str] = None,
        min_quality_score: Optional[float] = None,
    ) -> List[Dict[str, Any]]:
        index = self._read_index()
        records = list(index.get("characters", {}).values())

        if project_id is not None:
            records = [item for item in records if item.get("project_id") == project_id]

        if universe_id is not None:
            records = [item for item in records if item.get("universe_id") == universe_id]

        if min_quality_score is not None:
            records = [
                item for item in records
                if float(item.get("quality_score", 0.0)) >= min_quality_score
            ]

        return sorted(records, key=lambda item: item.get("updated_at", ""), reverse=True)

    def list_engine_runs(
        self,
        *,
        character_id: Optional[str] = None,
        engine_name: Optional[str] = None,
        project_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        index = self._read_index()
        records = list(index.get("runs", {}).values())

        if character_id is not None:
            records = [item for item in records if item.get("character_id") == character_id]

        if engine_name is not None:
            records = [item for item in records if item.get("engine_name") == engine_name]

        if project_id is not None:
            records = [item for item in records if item.get("project_id") == project_id]

        return sorted(records, key=lambda item: item.get("created_at", ""), reverse=True)

    def delete_character_profile(self, character_id: str) -> Dict[str, Any]:
        path = self._profile_path(character_id)
        existed = path.exists()

        if existed:
            path.unlink()

        index = self._read_index()
        index.get("characters", {}).pop(character_id, None)
        index["updated_at"] = self._now()
        self._write_json(self.index_path, index)

        return {
            "success": True,
            "character_id": character_id,
            "deleted": existed,
        }

    def get_store_summary(self) -> Dict[str, Any]:
        index = self._read_index()
        characters = list(index.get("characters", {}).values())
        runs = list(index.get("runs", {}).values())

        quality_scores = [float(item.get("quality_score", 0.0)) for item in characters]
        avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0.0

        return {
            "store_type": "character_run_store",
            "root_dir": str(self.root_dir),
            "profile_count": len(characters),
            "run_count": len(runs),
            "average_quality_score": round(avg_quality, 3),
            "latest_character_updated_at": max([item.get("updated_at", "") for item in characters], default=None),
            "latest_run_created_at": max([item.get("created_at", "") for item in runs], default=None),
            "index_path": str(self.index_path),
        }

    def _profile_path(self, character_id: str) -> Path:
        safe_id = self._safe_name(character_id)
        return self.profiles_dir / f"{safe_id}.json"

    def _run_path(self, run_id: str) -> Path:
        safe_id = self._safe_name(run_id)
        return self.runs_dir / f"{safe_id}.json"

    def _upsert_index_character(self, record: Dict[str, Any], profile_path: Path) -> None:
        index = self._read_index()
        character_id = record["character_id"]
        identity = record.get("profile", {}).get("identity", {})
        quality_report = record.get("quality_report", {}) or record.get("profile", {}).get("validation", {}).get("quality_report", {})

        index.setdefault("characters", {})[character_id] = {
            "character_id": character_id,
            "record_id": record["record_id"],
            "name": identity.get("name", record.get("profile", {}).get("identity", {}).get("name", "Unnamed Character")),
            "role": identity.get("role", "unknown"),
            "project_id": record.get("project_id", "default_project"),
            "universe_id": record.get("universe_id", "default_universe"),
            "quality_score": float(quality_report.get("overall_quality_score", 0.0)),
            "quality_tier": quality_report.get("quality_tier", "unknown"),
            "profile_path": str(profile_path),
            "created_at": record["created_at"],
            "updated_at": record["updated_at"],
        }

        index["updated_at"] = self._now()
        self._write_json(self.index_path, index)

    def _upsert_index_run(self, record: Dict[str, Any], run_path: Path) -> None:
        index = self._read_index()
        run_id = record["run_id"]

        index.setdefault("runs", {})[run_id] = {
            "run_id": run_id,
            "run_label": record.get("run_label"),
            "engine_name": record["engine_name"],
            "character_id": record["character_id"],
            "project_id": record.get("project_id", "default_project"),
            "universe_id": record.get("universe_id", "default_universe"),
            "success": record.get("run_metadata", {}).get("success", True),
            "run_path": str(run_path),
            "created_at": record["created_at"],
        }

        index["updated_at"] = self._now()
        self._write_json(self.index_path, index)

    def _extract_quality_report(self, profile: Dict[str, Any]) -> Dict[str, Any]:
        return profile.get("validation", {}).get("quality_report", {})

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

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import uuid4


class WorldRunStore:
    """SQLite-backed persistence for orchestrated world generation runs.

    This stores full Chunk 2 orchestrator results so generated worlds are not
    only returned from the API, but saved for later review, comparison,
    exports, embeddings, training metadata, and audit workflows.
    """

    def __init__(self, db_path: str = "data/mythos_engine.db") -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS world_generation_runs (
                    run_id TEXT PRIMARY KEY,
                    project_id TEXT,
                    universe_id TEXT,
                    world_name TEXT,
                    template_id TEXT,
                    seed_premise TEXT,
                    status TEXT NOT NULL,
                    quality_tier TEXT,
                    training_eligible INTEGER,
                    do_not_train INTEGER,
                    snapshot_id TEXT,
                    export_id TEXT,
                    world_state_json TEXT NOT NULL,
                    orchestration_summary_json TEXT NOT NULL,
                    quality_summary_json TEXT NOT NULL,
                    dataset_metadata_json TEXT NOT NULL,
                    snapshot_json TEXT NOT NULL,
                    world_bible_export_json TEXT NOT NULL,
                    audit_metadata_json TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )

            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_world_generation_runs_project_id ON world_generation_runs(project_id)"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_world_generation_runs_universe_id ON world_generation_runs(universe_id)"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_world_generation_runs_world_name ON world_generation_runs(world_name)"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_world_generation_runs_template_id ON world_generation_runs(template_id)"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_world_generation_runs_created_at ON world_generation_runs(created_at)"
            )

    def _new_run_id(self) -> str:
        return f"wrun_{uuid4().hex[:12]}"

    def _utc_now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _json(self, value: Any) -> str:
        return json.dumps(value, ensure_ascii=False, sort_keys=True)

    def _loads(self, value: str) -> Any:
        return json.loads(value) if value else None

    def save_orchestration_run(
        self,
        *,
        payload: Dict[str, Any],
        result_data: Dict[str, Any],
        audit_metadata: Optional[Dict[str, Any]] = None,
        status: str = "success",
    ) -> Dict[str, Any]:
        world_state = result_data.get("world_state", {})
        orchestration_summary = result_data.get("orchestration_summary", {})
        quality_summary = world_state.get("quality_summary", {})
        dataset_metadata = world_state.get("dataset_metadata", {})
        snapshot = world_state.get("snapshot", {})
        world_bible_export = world_state.get("world_bible_export", {})

        run_id = self._new_run_id()
        created_at = self._utc_now()

        world_name = (
            payload.get("world_name")
            or payload.get("name")
            or world_state.get("identity", {}).get("world_name")
            or world_state.get("identity", {}).get("name")
        )

        template_id = payload.get("template_id")
        seed_premise = payload.get("seed_premise")
        project_id = payload.get("project_id")
        universe_id = payload.get("universe_id")

        snapshot_id = snapshot.get("snapshot_id")
        export_id = world_bible_export.get("export_id")
        quality_tier = quality_summary.get("quality_tier")
        training_eligible = bool(dataset_metadata.get("training_eligible"))
        do_not_train = bool(dataset_metadata.get("do_not_train"))

        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO world_generation_runs (
                    run_id,
                    project_id,
                    universe_id,
                    world_name,
                    template_id,
                    seed_premise,
                    status,
                    quality_tier,
                    training_eligible,
                    do_not_train,
                    snapshot_id,
                    export_id,
                    world_state_json,
                    orchestration_summary_json,
                    quality_summary_json,
                    dataset_metadata_json,
                    snapshot_json,
                    world_bible_export_json,
                    audit_metadata_json,
                    created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    run_id,
                    project_id,
                    universe_id,
                    world_name,
                    template_id,
                    seed_premise,
                    status,
                    quality_tier,
                    int(training_eligible),
                    int(do_not_train),
                    snapshot_id,
                    export_id,
                    self._json(world_state),
                    self._json(orchestration_summary),
                    self._json(quality_summary),
                    self._json(dataset_metadata),
                    self._json(snapshot),
                    self._json(world_bible_export),
                    self._json(audit_metadata or {}),
                    created_at,
                ),
            )

        return self.get_run(run_id) or {
            "run_id": run_id,
            "created_at": created_at,
        }

    def get_run(self, run_id: str) -> Optional[Dict[str, Any]]:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM world_generation_runs WHERE run_id = ?",
                (run_id,),
            ).fetchone()

        if row is None:
            return None

        return self._row_to_dict(row)

    def list_runs(
        self,
        *,
        project_id: Optional[str] = None,
        universe_id: Optional[str] = None,
        template_id: Optional[str] = None,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        clauses = []
        params: List[Any] = []

        if project_id:
            clauses.append("project_id = ?")
            params.append(project_id)

        if universe_id:
            clauses.append("universe_id = ?")
            params.append(universe_id)

        if template_id:
            clauses.append("template_id = ?")
            params.append(template_id)

        where_sql = f"WHERE {' AND '.join(clauses)}" if clauses else ""

        params.append(limit)

        with self._connect() as conn:
            rows = conn.execute(
                f"""
                SELECT * FROM world_generation_runs
                {where_sql}
                ORDER BY created_at DESC
                LIMIT ?
                """,
                params,
            ).fetchall()

        return [self._row_to_dict(row, include_large_fields=False) for row in rows]

    def _row_to_dict(self, row: sqlite3.Row, *, include_large_fields: bool = True) -> Dict[str, Any]:
        base = {
            "run_id": row["run_id"],
            "project_id": row["project_id"],
            "universe_id": row["universe_id"],
            "world_name": row["world_name"],
            "template_id": row["template_id"],
            "seed_premise": row["seed_premise"],
            "status": row["status"],
            "quality_tier": row["quality_tier"],
            "training_eligible": bool(row["training_eligible"]),
            "do_not_train": bool(row["do_not_train"]),
            "snapshot_id": row["snapshot_id"],
            "export_id": row["export_id"],
            "created_at": row["created_at"],
        }

        base["orchestration_summary"] = self._loads(row["orchestration_summary_json"])
        base["quality_summary"] = self._loads(row["quality_summary_json"])
        base["dataset_metadata"] = self._loads(row["dataset_metadata_json"])
        base["snapshot"] = self._loads(row["snapshot_json"])
        base["world_bible_export"] = self._loads(row["world_bible_export_json"])
        base["audit_metadata"] = self._loads(row["audit_metadata_json"])

        if include_large_fields:
            base["world_state"] = self._loads(row["world_state_json"])

        return base


world_run_store = WorldRunStore()

# ---------------------------------------------------------------------------
# Upgrade Pass B: World learning registration tracking helpers
# ---------------------------------------------------------------------------

def _extract_world_learning_registration_summary(learning_registration):
    if not isinstance(learning_registration, dict):
        return {
            "registered_to_global_learning": False,
            "learning_metadata_ids": [],
            "provenance_ids": [],
            "embedding_ids": [],
            "training_queue_ids": [],
        }

    learning = learning_registration.get("learning_registration", learning_registration)

    learning_metadata_ids = []
    provenance_ids = []
    embedding_ids = []
    training_queue_ids = []

    registry = learning.get("learning_registry", {})
    if registry.get("metadata_id"):
        learning_metadata_ids.append(registry["metadata_id"])

    for item in learning.get("provenance_results", []) or []:
        if item.get("provenance_id"):
            provenance_ids.append(item["provenance_id"])

    embedding_result = learning.get("embedding_result")
    if isinstance(embedding_result, dict) and embedding_result.get("embedding_id"):
        embedding_ids.append(embedding_result["embedding_id"])

    training_result = learning.get("training_result")
    if isinstance(training_result, dict) and training_result.get("training_queue_id"):
        training_queue_ids.append(training_result["training_queue_id"])

    return {
        "registered_to_global_learning": bool(learning.get("registered", False)),
        "learning_metadata_ids": learning_metadata_ids,
        "provenance_ids": provenance_ids,
        "embedding_ids": embedding_ids,
        "training_queue_ids": training_queue_ids,
    }


def attach_learning_registration_to_world_record(record, learning_registration=None, world_to_character_contract=None):
    """Attach global learning traceability to a world run/store record.

    This function is intentionally standalone so it can be used by existing
    world storage code without forcing a breaking refactor of WorldRunStore.
    """

    if not isinstance(record, dict):
        raise ValueError("record must be a dictionary")

    summary = _extract_world_learning_registration_summary(learning_registration or {})

    record["global_learning_trace"] = {
        **summary,
        "learning_registration_summary": learning_registration or {},
        "world_to_character_contract": world_to_character_contract or {},
        "trace_schema_version": "world_learning_trace_v0.1.0",
    }

    return record


def extract_world_learning_trace(record):
    """Return learning trace block from a stored world record."""

    if not isinstance(record, dict):
        raise ValueError("record must be a dictionary")

    return record.get(
        "global_learning_trace",
        {
            "registered_to_global_learning": False,
            "learning_metadata_ids": [],
            "provenance_ids": [],
            "embedding_ids": [],
            "training_queue_ids": [],
            "learning_registration_summary": {},
            "world_to_character_contract": {},
            "trace_schema_version": "world_learning_trace_v0.1.0",
        },
    )

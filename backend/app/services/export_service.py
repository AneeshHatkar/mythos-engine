import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from pydantic import BaseModel

from backend.app.schemas.foundation import ExportRecordCreate, ExportRecordRead
from backend.app.services.foundation_store import SQLiteFoundationStore, store


def utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def model_to_dict(model: BaseModel) -> Dict[str, Any]:
    return model.model_dump(mode="json")


class FoundationExportService:
    """Creates real export files for Chunk 1 foundation data.

    Supported export formats:
    - JSON: machine-readable full project state
    - CSV: spreadsheet-friendly collection files
    - Markdown: human-readable foundation summary
    - DB snapshot metadata: records local DB state and record counts
    """

    def __init__(
        self,
        foundation_store: SQLiteFoundationStore,
        export_root: str = "exports",
    ) -> None:
        self.store = foundation_store
        self.export_root = Path(export_root)

    # ------------------------------------------------------------------
    # State collection
    # ------------------------------------------------------------------

    def collect_project_state(self, project_id: str) -> Optional[Dict[str, Any]]:
        project = self.store.get_project(project_id)
        if project is None:
            return None

        universes = self.store.list_universes_for_project(project_id)

        universe_ids = {universe.universe_id for universe in universes}

        versions = self.store.list_versions(project_id=project_id)
        audit_records = self.store.list_audit_records(project_id=project_id)
        feedback_records = self.store.list_feedback(project_id=project_id)
        export_records = self.store.list_exports(project_id=project_id)
        canon_locks = self.store.list_canon_locks(project_id=project_id)
        branches = self.store.list_branches(project_id=project_id)

        # Registry types are global in Chunk 1. We include all registry types
        # because they define the foundation vocabulary used by all projects.
        registry_types = self.store.list_registry_types()

        return {
            "export_metadata": {
                "project_id": project_id,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "schema_version": "foundation_export_v0.1",
                "included_collections": [
                    "project",
                    "universes",
                    "registry_types",
                    "versions",
                    "audit_records",
                    "feedback_records",
                    "exports",
                    "canon_locks",
                    "branches",
                ],
                "universe_ids": sorted(universe_ids),
            },
            "project": model_to_dict(project),
            "universes": [model_to_dict(item) for item in universes],
            "registry_types": [model_to_dict(item) for item in registry_types],
            "versions": [model_to_dict(item) for item in versions],
            "audit_records": [model_to_dict(item) for item in audit_records],
            "feedback_records": [model_to_dict(item) for item in feedback_records],
            "exports": [model_to_dict(item) for item in export_records],
            "canon_locks": [model_to_dict(item) for item in canon_locks],
            "branches": [model_to_dict(item) for item in branches],
        }

    # ------------------------------------------------------------------
    # Export formats
    # ------------------------------------------------------------------

    def export_json(self, project_id: str) -> Optional[ExportRecordRead]:
        state = self.collect_project_state(project_id)
        if state is None:
            return None

        output_dir = self.export_root / "json"
        output_dir.mkdir(parents=True, exist_ok=True)

        path = output_dir / f"{project_id}_foundation_state_{utc_stamp()}.json"
        path.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")

        return self._record_export(
            project_id=project_id,
            export_type="json_state",
            object_scope="project",
            file_path=str(path),
            summary="Foundation project state exported as JSON.",
        )

    def export_csv(self, project_id: str) -> Optional[ExportRecordRead]:
        state = self.collect_project_state(project_id)
        if state is None:
            return None

        output_dir = self.export_root / "csv" / f"{project_id}_{utc_stamp()}"
        output_dir.mkdir(parents=True, exist_ok=True)

        collections = {
            "projects": [state["project"]],
            "universes": state["universes"],
            "registry_types": state["registry_types"],
            "versions": state["versions"],
            "audit_records": state["audit_records"],
            "feedback_records": state["feedback_records"],
            "exports": state["exports"],
            "canon_locks": state["canon_locks"],
            "branches": state["branches"],
        }

        for name, rows in collections.items():
            self._write_csv(output_dir / f"{name}.csv", rows)

        manifest = {
            "project_id": project_id,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "format": "csv_folder",
            "files": sorted(path.name for path in output_dir.glob("*.csv")),
        }
        (output_dir / "manifest.json").write_text(
            json.dumps(manifest, indent=2),
            encoding="utf-8",
        )

        return self._record_export(
            project_id=project_id,
            export_type="csv_folder",
            object_scope="project",
            file_path=str(output_dir),
            summary="Foundation project state exported as CSV collection folder.",
        )

    def export_markdown(self, project_id: str) -> Optional[ExportRecordRead]:
        state = self.collect_project_state(project_id)
        if state is None:
            return None

        output_dir = self.export_root / "markdown"
        output_dir.mkdir(parents=True, exist_ok=True)

        project = state["project"]
        path = output_dir / f"{project_id}_foundation_summary_{utc_stamp()}.md"

        markdown = self._build_markdown_summary(state)
        path.write_text(markdown, encoding="utf-8")

        return self._record_export(
            project_id=project_id,
            export_type="markdown_summary",
            object_scope="project",
            file_path=str(path),
            summary=f"Foundation summary exported for {project['name']}.",
        )

    def export_db_snapshot_metadata(self, project_id: str) -> Optional[ExportRecordRead]:
        state = self.collect_project_state(project_id)
        if state is None:
            return None

        output_dir = self.export_root / "db_snapshot"
        output_dir.mkdir(parents=True, exist_ok=True)

        record_counts = {
            "universes": len(state["universes"]),
            "registry_types": len(state["registry_types"]),
            "versions": len(state["versions"]),
            "audit_records": len(state["audit_records"]),
            "feedback_records": len(state["feedback_records"]),
            "exports": len(state["exports"]),
            "canon_locks": len(state["canon_locks"]),
            "branches": len(state["branches"]),
        }

        snapshot = {
            "project_id": project_id,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "database_note": (
                "This is metadata for the local SQLite database snapshot. "
                "The actual local database file is not committed to GitHub."
            ),
            "default_database_path": "data/mythos.db",
            "record_counts": record_counts,
        }

        path = output_dir / f"{project_id}_db_snapshot_metadata_{utc_stamp()}.json"
        path.write_text(json.dumps(snapshot, indent=2), encoding="utf-8")

        return self._record_export(
            project_id=project_id,
            export_type="db_snapshot_metadata",
            object_scope="project",
            file_path=str(path),
            summary="Foundation database snapshot metadata exported.",
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _record_export(
        self,
        *,
        project_id: str,
        export_type: str,
        object_scope: str,
        file_path: str,
        summary: str,
    ) -> Optional[ExportRecordRead]:
        return self.store.create_export_record(
            ExportRecordCreate(
                project_id=project_id,
                export_type=export_type,
                object_scope=object_scope,
                file_path=file_path,
                summary=summary,
            )
        )

    def _write_csv(self, path: Path, rows: List[Dict[str, Any]]) -> None:
        if not rows:
            path.write_text("", encoding="utf-8")
            return

        fieldnames = sorted({key for row in rows for key in row.keys()})

        with path.open("w", newline="", encoding="utf-8") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()

            for row in rows:
                flattened = {
                    key: self._csv_safe_value(row.get(key))
                    for key in fieldnames
                }
                writer.writerow(flattened)

    def _csv_safe_value(self, value: Any) -> Any:
        if isinstance(value, (list, dict)):
            return json.dumps(value, ensure_ascii=False)
        return value

    def _build_markdown_summary(self, state: Dict[str, Any]) -> str:
        project = state["project"]
        metadata = state["export_metadata"]

        lines = [
            f"# MythOS Foundation Export: {project['name']}",
            "",
            "## Export Metadata",
            "",
            f"- Project ID: `{metadata['project_id']}`",
            f"- Created At: `{metadata['created_at']}`",
            f"- Schema Version: `{metadata['schema_version']}`",
            "",
            "## Project",
            "",
            f"- Name: {project['name']}",
            f"- Description: {project.get('description', '')}",
            f"- Mode: `{project.get('project_mode')}`",
            f"- Target Use: `{project.get('target_use')}`",
            f"- Status: `{project.get('status')}`",
            "",
            "## Record Counts",
            "",
            f"- Universes: {len(state['universes'])}",
            f"- Registry Types: {len(state['registry_types'])}",
            f"- Versions: {len(state['versions'])}",
            f"- Audit Records: {len(state['audit_records'])}",
            f"- Feedback Records: {len(state['feedback_records'])}",
            f"- Export Records: {len(state['exports'])}",
            f"- Canon Locks: {len(state['canon_locks'])}",
            f"- Branches: {len(state['branches'])}",
            "",
            "## Universes",
            "",
        ]

        if state["universes"]:
            for universe in state["universes"]:
                lines.extend(
                    [
                        f"### {universe['name']}",
                        "",
                        f"- Universe ID: `{universe['universe_id']}`",
                        f"- Genres: {', '.join(universe.get('genres', []))}",
                        f"- Tone: {universe.get('tone', '')}",
                        f"- Scale Preference: `{universe.get('scale_preference')}`",
                        "",
                    ]
                )
        else:
            lines.append("No universes have been created yet.")
            lines.append("")

        lines.extend(
            [
                "## Canon Locks",
                "",
            ]
        )

        if state["canon_locks"]:
            for lock in state["canon_locks"]:
                lines.extend(
                    [
                        f"- `{lock['object_type']}` / `{lock['object_id']}` / `{lock['field_path']}`",
                    ]
                )
        else:
            lines.append("No canon locks have been created yet.")

        lines.append("")
        lines.append("## Branches")
        lines.append("")

        if state["branches"]:
            for branch in state["branches"]:
                lines.extend(
                    [
                        f"- {branch['branch_name']} (`{branch['branch_type']}`)",
                    ]
                )
        else:
            lines.append("No branches have been created yet.")

        lines.append("")
        return "\n".join(lines)


export_service = FoundationExportService(store)

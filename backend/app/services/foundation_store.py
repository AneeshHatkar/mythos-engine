import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Type, TypeVar

from pydantic import BaseModel

from backend.app.db.database import create_connection, initialize_object_store
from backend.app.schemas.foundation import (
    AuditRecordCreate,
    AuditRecordRead,
    BranchCreate,
    BranchRead,
    CanonLockCreate,
    CanonLockRead,
    ExportRecordCreate,
    ExportRecordRead,
    FeedbackRecordCreate,
    FeedbackRecordRead,
    ProjectCreate,
    ProjectRead,
    RegistryTypeCreate,
    RegistryTypeRead,
    UniverseCreate,
    UniverseRead,
    VersionRecordCreate,
    VersionRecordRead,
    new_id,
)

ModelT = TypeVar("ModelT", bound=BaseModel)


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class SQLiteFoundationStore:
    """SQLite-backed foundation store for MythOS Engine.

    This replaces the temporary in-memory store while keeping the same public
    method names used by the API routes.

    The design uses one generic persisted-object table for Chunk 1. Each object
    is stored as validated Pydantic JSON. This keeps the foundation flexible and
    lets us persist all early object types without writing a large migration
    system too early.

    Later chunks can add specialized SQL tables for high-volume systems such as
    world events, character memories, relationship graphs, model evaluations,
    and generated scenes.
    """

    def __init__(self, db_path: Optional[str] = None) -> None:
        self.connection = create_connection(db_path)
        initialize_object_store(self.connection)

    # ------------------------------------------------------------------
    # Generic helpers
    # ------------------------------------------------------------------

    def _model_to_json(self, model: BaseModel) -> str:
        return json.dumps(model.model_dump(mode="json"), ensure_ascii=False)

    def _row_to_model(self, row: Any, model_cls: Type[ModelT]) -> ModelT:
        payload = json.loads(row["payload_json"])
        return model_cls.model_validate(payload)

    def _insert_model(
        self,
        *,
        collection: str,
        object_id: str,
        model: BaseModel,
        type_key: Optional[str] = None,
        project_id: Optional[str] = None,
        universe_id: Optional[str] = None,
        object_type: Optional[str] = None,
    ) -> None:
        timestamp = now_iso()
        self.connection.execute(
            """
            INSERT INTO mythos_objects (
                collection,
                object_id,
                type_key,
                project_id,
                universe_id,
                object_type,
                payload_json,
                created_at,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                collection,
                object_id,
                type_key,
                project_id,
                universe_id,
                object_type,
                self._model_to_json(model),
                timestamp,
                timestamp,
            ),
        )
        self.connection.commit()

    def _get_model(
        self,
        *,
        collection: str,
        object_id: str,
        model_cls: Type[ModelT],
    ) -> Optional[ModelT]:
        row = self.connection.execute(
            """
            SELECT payload_json
            FROM mythos_objects
            WHERE collection = ? AND object_id = ?
            """,
            (collection, object_id),
        ).fetchone()

        if row is None:
            return None

        return self._row_to_model(row, model_cls)

    def _list_models(
        self,
        *,
        collection: str,
        model_cls: Type[ModelT],
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[ModelT]:
        query = "SELECT payload_json FROM mythos_objects WHERE collection = ?"
        params: List[Any] = [collection]

        filters = filters or {}

        for column, value in filters.items():
            if value is None:
                continue

            query += f" AND {column} = ?"
            params.append(value)

        rows = self.connection.execute(query, params).fetchall()
        return [self._row_to_model(row, model_cls) for row in rows]

    # ------------------------------------------------------------------
    # Projects
    # ------------------------------------------------------------------

    def create_project(self, payload: ProjectCreate) -> ProjectRead:
        project = ProjectRead(
            project_id=new_id("proj"),
            name=payload.name,
            description=payload.description,
            project_mode=payload.project_mode,
            target_use=payload.target_use,
            default_content_profile=payload.default_content_profile,
        )

        self._insert_model(
            collection="projects",
            object_id=project.project_id,
            model=project,
            project_id=project.project_id,
            object_type="project",
        )
        return project

    def list_projects(self) -> List[ProjectRead]:
        return self._list_models(collection="projects", model_cls=ProjectRead)

    def get_project(self, project_id: str) -> Optional[ProjectRead]:
        return self._get_model(
            collection="projects",
            object_id=project_id,
            model_cls=ProjectRead,
        )

    # ------------------------------------------------------------------
    # Universes
    # ------------------------------------------------------------------

    def create_universe(self, payload: UniverseCreate) -> Optional[UniverseRead]:
        if self.get_project(payload.project_id) is None:
            return None

        universe = UniverseRead(
            universe_id=new_id("uni"),
            project_id=payload.project_id,
            name=payload.name,
            seed_premise=payload.seed_premise,
            genres=payload.genres,
            tone=payload.tone,
            scale_preference=payload.scale_preference,
            target_formats=payload.target_formats,
        )

        self._insert_model(
            collection="universes",
            object_id=universe.universe_id,
            model=universe,
            project_id=universe.project_id,
            universe_id=universe.universe_id,
            object_type="universe",
        )
        return universe

    def list_universes_for_project(self, project_id: str) -> List[UniverseRead]:
        return self._list_models(
            collection="universes",
            model_cls=UniverseRead,
            filters={"project_id": project_id},
        )

    def get_universe(self, universe_id: str) -> Optional[UniverseRead]:
        return self._get_model(
            collection="universes",
            object_id=universe_id,
            model_cls=UniverseRead,
        )

    # ------------------------------------------------------------------
    # Registry
    # ------------------------------------------------------------------

    def create_registry_type(
        self, payload: RegistryTypeCreate
    ) -> Optional[RegistryTypeRead]:
        if self.get_registry_type(payload.type_id) is not None:
            return None

        registry_type = RegistryTypeRead(
            registry_id=new_id("reg"),
            type_id=payload.type_id,
            category=payload.category,
            name=payload.name,
            description=payload.description,
            tags=payload.tags,
            compatible_with=payload.compatible_with,
            conflicts_with=payload.conflicts_with,
            risk_notes=payload.risk_notes,
            example_output=payload.example_output,
            created_by=payload.created_by,
        )

        self._insert_model(
            collection="registry_types",
            object_id=registry_type.type_id,
            model=registry_type,
            type_key=registry_type.type_id,
            object_type=registry_type.category,
        )
        return registry_type

    def list_registry_types(
        self,
        category: Optional[str] = None,
        tag: Optional[str] = None,
    ) -> List[RegistryTypeRead]:
        results = self._list_models(
            collection="registry_types",
            model_cls=RegistryTypeRead,
            filters={"object_type": category},
        )

        if tag:
            results = [item for item in results if tag in item.tags]

        return results

    def get_registry_type(self, type_id: str) -> Optional[RegistryTypeRead]:
        return self._get_model(
            collection="registry_types",
            object_id=type_id,
            model_cls=RegistryTypeRead,
        )

    # ------------------------------------------------------------------
    # Versions
    # ------------------------------------------------------------------

    def create_version(self, payload: VersionRecordCreate) -> Optional[VersionRecordRead]:
        if self.get_project(payload.project_id) is None:
            return None

        if payload.universe_id and self.get_universe(payload.universe_id) is None:
            return None

        version = VersionRecordRead(
            version_id=new_id("ver"),
            project_id=payload.project_id,
            universe_id=payload.universe_id,
            object_type=payload.object_type,
            object_id=payload.object_id,
            version_label=payload.version_label,
            summary=payload.summary,
            parent_version_id=payload.parent_version_id,
            canon_status=payload.canon_status,
            snapshot=payload.snapshot,
        )

        self._insert_model(
            collection="versions",
            object_id=version.version_id,
            model=version,
            project_id=version.project_id,
            universe_id=version.universe_id,
            object_type=version.object_type,
        )
        return version

    def list_versions(
        self,
        project_id: Optional[str] = None,
        universe_id: Optional[str] = None,
        object_type: Optional[str] = None,
        object_id: Optional[str] = None,
    ) -> List[VersionRecordRead]:
        results = self._list_models(
            collection="versions",
            model_cls=VersionRecordRead,
            filters={
                "project_id": project_id,
                "universe_id": universe_id,
                "object_type": object_type,
            },
        )

        if object_id:
            results = [item for item in results if item.object_id == object_id]

        return results

    # ------------------------------------------------------------------
    # Audit
    # ------------------------------------------------------------------

    def create_audit_record(
        self, payload: AuditRecordCreate
    ) -> Optional[AuditRecordRead]:
        if self.get_project(payload.project_id) is None:
            return None

        if payload.universe_id and self.get_universe(payload.universe_id) is None:
            return None

        audit_record = AuditRecordRead(
            audit_id=new_id("aud"),
            project_id=payload.project_id,
            universe_id=payload.universe_id,
            engine_name=payload.engine_name,
            event_type=payload.event_type,
            input_summary=payload.input_summary,
            output_summary=payload.output_summary,
            model_provider=payload.model_provider,
            model_name=payload.model_name,
            parameters=payload.parameters,
            warnings=payload.warnings,
            errors=payload.errors,
            quality_score=payload.quality_score,
        )

        self._insert_model(
            collection="audit_records",
            object_id=audit_record.audit_id,
            model=audit_record,
            project_id=audit_record.project_id,
            universe_id=audit_record.universe_id,
            object_type=audit_record.engine_name,
        )
        return audit_record

    def list_audit_records(
        self,
        project_id: Optional[str] = None,
        universe_id: Optional[str] = None,
        engine_name: Optional[str] = None,
    ) -> List[AuditRecordRead]:
        return self._list_models(
            collection="audit_records",
            model_cls=AuditRecordRead,
            filters={
                "project_id": project_id,
                "universe_id": universe_id,
                "object_type": engine_name,
            },
        )

    # ------------------------------------------------------------------
    # Feedback
    # ------------------------------------------------------------------

    def create_feedback(
        self, payload: FeedbackRecordCreate
    ) -> Optional[FeedbackRecordRead]:
        if self.get_project(payload.project_id) is None:
            return None

        if payload.universe_id and self.get_universe(payload.universe_id) is None:
            return None

        feedback = FeedbackRecordRead(
            feedback_id=new_id("fb"),
            project_id=payload.project_id,
            universe_id=payload.universe_id,
            object_type=payload.object_type,
            object_id=payload.object_id,
            feedback_type=payload.feedback_type,
            rating=payload.rating,
            comment=payload.comment,
            future_use=payload.future_use,
        )

        self._insert_model(
            collection="feedback_records",
            object_id=feedback.feedback_id,
            model=feedback,
            project_id=feedback.project_id,
            universe_id=feedback.universe_id,
            object_type=feedback.object_type,
        )
        return feedback

    def list_feedback(
        self,
        project_id: Optional[str] = None,
        universe_id: Optional[str] = None,
        object_type: Optional[str] = None,
        object_id: Optional[str] = None,
    ) -> List[FeedbackRecordRead]:
        results = self._list_models(
            collection="feedback_records",
            model_cls=FeedbackRecordRead,
            filters={
                "project_id": project_id,
                "universe_id": universe_id,
                "object_type": object_type,
            },
        )

        if object_id:
            results = [item for item in results if item.object_id == object_id]

        return results

    # ------------------------------------------------------------------
    # Exports
    # ------------------------------------------------------------------

    def create_export_record(
        self, payload: ExportRecordCreate
    ) -> Optional[ExportRecordRead]:
        if self.get_project(payload.project_id) is None:
            return None

        if payload.universe_id and self.get_universe(payload.universe_id) is None:
            return None

        export_record = ExportRecordRead(
            export_id=new_id("exp"),
            project_id=payload.project_id,
            universe_id=payload.universe_id,
            export_type=payload.export_type,
            object_scope=payload.object_scope,
            file_path=payload.file_path,
            summary=payload.summary,
        )

        self._insert_model(
            collection="exports",
            object_id=export_record.export_id,
            model=export_record,
            project_id=export_record.project_id,
            universe_id=export_record.universe_id,
            object_type=export_record.export_type,
        )
        return export_record

    def list_exports(
        self,
        project_id: Optional[str] = None,
        universe_id: Optional[str] = None,
        export_type: Optional[str] = None,
    ) -> List[ExportRecordRead]:
        return self._list_models(
            collection="exports",
            model_cls=ExportRecordRead,
            filters={
                "project_id": project_id,
                "universe_id": universe_id,
                "object_type": export_type,
            },
        )

    # ------------------------------------------------------------------
    # Canon Locks
    # ------------------------------------------------------------------

    def create_canon_lock(
        self, payload: CanonLockCreate
    ) -> Optional[CanonLockRead]:
        if self.get_project(payload.project_id) is None:
            return None

        if payload.universe_id and self.get_universe(payload.universe_id) is None:
            return None

        canon_lock = CanonLockRead(
            canon_lock_id=new_id("lock"),
            project_id=payload.project_id,
            universe_id=payload.universe_id,
            object_type=payload.object_type,
            object_id=payload.object_id,
            field_path=payload.field_path,
            locked_value=payload.locked_value,
            reason=payload.reason,
            locked_by=payload.locked_by,
        )

        self._insert_model(
            collection="canon_locks",
            object_id=canon_lock.canon_lock_id,
            model=canon_lock,
            project_id=canon_lock.project_id,
            universe_id=canon_lock.universe_id,
            object_type=canon_lock.object_type,
        )
        return canon_lock

    def list_canon_locks(
        self,
        project_id: Optional[str] = None,
        universe_id: Optional[str] = None,
        object_type: Optional[str] = None,
        object_id: Optional[str] = None,
    ) -> List[CanonLockRead]:
        results = self._list_models(
            collection="canon_locks",
            model_cls=CanonLockRead,
            filters={
                "project_id": project_id,
                "universe_id": universe_id,
                "object_type": object_type,
            },
        )

        if object_id:
            results = [item for item in results if item.object_id == object_id]

        return results

    # ------------------------------------------------------------------
    # Branches
    # ------------------------------------------------------------------

    def create_branch(self, payload: BranchCreate) -> Optional[BranchRead]:
        if self.get_project(payload.project_id) is None:
            return None

        if self.get_universe(payload.universe_id) is None:
            return None

        if payload.parent_branch_id and self.get_branch(payload.parent_branch_id) is None:
            return None

        branch = BranchRead(
            branch_id=new_id("branch"),
            project_id=payload.project_id,
            universe_id=payload.universe_id,
            branch_name=payload.branch_name,
            branch_type=payload.branch_type,
            parent_branch_id=payload.parent_branch_id,
            reason=payload.reason,
            canon_status=payload.canon_status,
        )

        self._insert_model(
            collection="branches",
            object_id=branch.branch_id,
            model=branch,
            project_id=branch.project_id,
            universe_id=branch.universe_id,
            object_type=branch.branch_type,
        )
        return branch

    def list_branches(
        self,
        project_id: Optional[str] = None,
        universe_id: Optional[str] = None,
        branch_type: Optional[str] = None,
    ) -> List[BranchRead]:
        return self._list_models(
            collection="branches",
            model_cls=BranchRead,
            filters={
                "project_id": project_id,
                "universe_id": universe_id,
                "object_type": branch_type,
            },
        )

    def get_branch(self, branch_id: str) -> Optional[BranchRead]:
        return self._get_model(
            collection="branches",
            object_id=branch_id,
            model_cls=BranchRead,
        )


# The app imports this singleton.
store = SQLiteFoundationStore()

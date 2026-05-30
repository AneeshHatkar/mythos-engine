from typing import Dict, List, Optional

from backend.app.schemas.foundation import (
    AuditRecordCreate,
    AuditRecordRead,
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


class FoundationStore:
    """In-memory foundation store for MythOS Engine v0.1.

    This gives us working API behavior before we move to SQLite/SQLAlchemy.
    """

    def __init__(self) -> None:
        self.projects: Dict[str, ProjectRead] = {}
        self.universes: Dict[str, UniverseRead] = {}
        self.registry_types: Dict[str, RegistryTypeRead] = {}
        self.versions: Dict[str, VersionRecordRead] = {}
        self.audit_records: Dict[str, AuditRecordRead] = {}
        self.feedback_records: Dict[str, FeedbackRecordRead] = {}
        self.exports: Dict[str, ExportRecordRead] = {}

    # -------------------------------------------------------------------------
    # Projects
    # -------------------------------------------------------------------------

    def create_project(self, payload: ProjectCreate) -> ProjectRead:
        project = ProjectRead(
            project_id=new_id("proj"),
            name=payload.name,
            description=payload.description,
            project_mode=payload.project_mode,
            target_use=payload.target_use,
            default_content_profile=payload.default_content_profile,
        )
        self.projects[project.project_id] = project
        return project

    def list_projects(self) -> List[ProjectRead]:
        return list(self.projects.values())

    def get_project(self, project_id: str) -> Optional[ProjectRead]:
        return self.projects.get(project_id)

    # -------------------------------------------------------------------------
    # Universes
    # -------------------------------------------------------------------------

    def create_universe(self, payload: UniverseCreate) -> Optional[UniverseRead]:
        if payload.project_id not in self.projects:
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
        self.universes[universe.universe_id] = universe
        return universe

    def list_universes_for_project(self, project_id: str) -> List[UniverseRead]:
        return [
            universe
            for universe in self.universes.values()
            if universe.project_id == project_id
        ]

    def get_universe(self, universe_id: str) -> Optional[UniverseRead]:
        return self.universes.get(universe_id)

    # -------------------------------------------------------------------------
    # Registry
    # -------------------------------------------------------------------------

    def create_registry_type(
        self, payload: RegistryTypeCreate
    ) -> Optional[RegistryTypeRead]:
        if payload.type_id in self.registry_types:
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
        self.registry_types[payload.type_id] = registry_type
        return registry_type

    def list_registry_types(
        self,
        category: Optional[str] = None,
        tag: Optional[str] = None,
    ) -> List[RegistryTypeRead]:
        results = list(self.registry_types.values())

        if category:
            results = [item for item in results if item.category == category]

        if tag:
            results = [item for item in results if tag in item.tags]

        return results

    def get_registry_type(self, type_id: str) -> Optional[RegistryTypeRead]:
        return self.registry_types.get(type_id)

    # -------------------------------------------------------------------------
    # Versions
    # -------------------------------------------------------------------------

    def create_version(self, payload: VersionRecordCreate) -> Optional[VersionRecordRead]:
        if payload.project_id not in self.projects:
            return None

        if payload.universe_id and payload.universe_id not in self.universes:
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
        self.versions[version.version_id] = version
        return version

    def list_versions(
        self,
        project_id: Optional[str] = None,
        universe_id: Optional[str] = None,
        object_type: Optional[str] = None,
        object_id: Optional[str] = None,
    ) -> List[VersionRecordRead]:
        results = list(self.versions.values())

        if project_id:
            results = [item for item in results if item.project_id == project_id]

        if universe_id:
            results = [item for item in results if item.universe_id == universe_id]

        if object_type:
            results = [item for item in results if item.object_type == object_type]

        if object_id:
            results = [item for item in results if item.object_id == object_id]

        return results

    # -------------------------------------------------------------------------
    # Audit
    # -------------------------------------------------------------------------

    def create_audit_record(
        self, payload: AuditRecordCreate
    ) -> Optional[AuditRecordRead]:
        if payload.project_id not in self.projects:
            return None

        if payload.universe_id and payload.universe_id not in self.universes:
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
        self.audit_records[audit_record.audit_id] = audit_record
        return audit_record

    def list_audit_records(
        self,
        project_id: Optional[str] = None,
        universe_id: Optional[str] = None,
        engine_name: Optional[str] = None,
    ) -> List[AuditRecordRead]:
        results = list(self.audit_records.values())

        if project_id:
            results = [item for item in results if item.project_id == project_id]

        if universe_id:
            results = [item for item in results if item.universe_id == universe_id]

        if engine_name:
            results = [item for item in results if item.engine_name == engine_name]

        return results

    # -------------------------------------------------------------------------
    # Feedback
    # -------------------------------------------------------------------------

    def create_feedback(
        self, payload: FeedbackRecordCreate
    ) -> Optional[FeedbackRecordRead]:
        if payload.project_id not in self.projects:
            return None

        if payload.universe_id and payload.universe_id not in self.universes:
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
        self.feedback_records[feedback.feedback_id] = feedback
        return feedback

    def list_feedback(
        self,
        project_id: Optional[str] = None,
        universe_id: Optional[str] = None,
        object_type: Optional[str] = None,
        object_id: Optional[str] = None,
    ) -> List[FeedbackRecordRead]:
        results = list(self.feedback_records.values())

        if project_id:
            results = [item for item in results if item.project_id == project_id]

        if universe_id:
            results = [item for item in results if item.universe_id == universe_id]

        if object_type:
            results = [item for item in results if item.object_type == object_type]

        if object_id:
            results = [item for item in results if item.object_id == object_id]

        return results

    # -------------------------------------------------------------------------
    # Exports
    # -------------------------------------------------------------------------

    def create_export_record(
        self, payload: ExportRecordCreate
    ) -> Optional[ExportRecordRead]:
        if payload.project_id not in self.projects:
            return None

        if payload.universe_id and payload.universe_id not in self.universes:
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
        self.exports[export_record.export_id] = export_record
        return export_record

    def list_exports(
        self,
        project_id: Optional[str] = None,
        universe_id: Optional[str] = None,
        export_type: Optional[str] = None,
    ) -> List[ExportRecordRead]:
        results = list(self.exports.values())

        if project_id:
            results = [item for item in results if item.project_id == project_id]

        if universe_id:
            results = [item for item in results if item.universe_id == universe_id]

        if export_type:
            results = [item for item in results if item.export_type == export_type]

        return results


store = FoundationStore()
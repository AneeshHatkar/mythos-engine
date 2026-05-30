from typing import Dict, List, Optional

from backend.app.schemas.foundation import (
    ProjectCreate,
    ProjectRead,
    RegistryTypeCreate,
    RegistryTypeRead,
    UniverseCreate,
    UniverseRead,
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


store = FoundationStore()
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query

from backend.app.schemas.foundation import (
    ProjectCreate,
    ProjectRead,
    RegistryTypeCreate,
    RegistryTypeRead,
    UniverseCreate,
    UniverseRead,
)
from backend.app.services.foundation_store import store


router = APIRouter(tags=["Foundation"])


@router.post("/projects", response_model=ProjectRead, status_code=201)
def create_project(payload: ProjectCreate) -> ProjectRead:
    return store.create_project(payload)


@router.get("/projects", response_model=List[ProjectRead])
def list_projects() -> List[ProjectRead]:
    return store.list_projects()


@router.get("/projects/{project_id}", response_model=ProjectRead)
def get_project(project_id: str) -> ProjectRead:
    project = store.get_project(project_id)

    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    return project


@router.post(
    "/projects/{project_id}/universes",
    response_model=UniverseRead,
    status_code=201,
)
def create_universe(project_id: str, payload: UniverseCreate) -> UniverseRead:
    if payload.project_id != project_id:
        raise HTTPException(
            status_code=400,
            detail="Project ID in path must match project_id in request body",
        )

    universe = store.create_universe(payload)

    if universe is None:
        raise HTTPException(status_code=404, detail="Project not found")

    return universe


@router.get(
    "/projects/{project_id}/universes",
    response_model=List[UniverseRead],
)
def list_universes_for_project(project_id: str) -> List[UniverseRead]:
    if store.get_project(project_id) is None:
        raise HTTPException(status_code=404, detail="Project not found")

    return store.list_universes_for_project(project_id)


@router.get("/universes/{universe_id}", response_model=UniverseRead)
def get_universe(universe_id: str) -> UniverseRead:
    universe = store.get_universe(universe_id)

    if universe is None:
        raise HTTPException(status_code=404, detail="Universe not found")

    return universe


@router.post(
    "/registry/types",
    response_model=RegistryTypeRead,
    status_code=201,
)
def create_registry_type(payload: RegistryTypeCreate) -> RegistryTypeRead:
    registry_type = store.create_registry_type(payload)

    if registry_type is None:
        raise HTTPException(
            status_code=409,
            detail="Registry type_id already exists",
        )

    return registry_type


@router.get("/registry/types", response_model=List[RegistryTypeRead])
def list_registry_types(
    category: Optional[str] = Query(default=None),
    tag: Optional[str] = Query(default=None),
) -> List[RegistryTypeRead]:
    return store.list_registry_types(category=category, tag=tag)


@router.get("/registry/types/{type_id}", response_model=RegistryTypeRead)
def get_registry_type(type_id: str) -> RegistryTypeRead:
    registry_type = store.get_registry_type(type_id)

    if registry_type is None:
        raise HTTPException(status_code=404, detail="Registry type not found")

    return registry_type
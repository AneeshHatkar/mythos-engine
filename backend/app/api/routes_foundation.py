from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query

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
    BranchCreate,
    BranchRead,
    CanonLockCreate,
    CanonLockRead,
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


@router.post("/versions", response_model=VersionRecordRead, status_code=201)
def create_version(payload: VersionRecordCreate) -> VersionRecordRead:
    version = store.create_version(payload)

    if version is None:
        raise HTTPException(
            status_code=404,
            detail="Project or universe not found for version record",
        )

    return version


@router.get("/versions", response_model=List[VersionRecordRead])
def list_versions(
    project_id: Optional[str] = Query(default=None),
    universe_id: Optional[str] = Query(default=None),
    object_type: Optional[str] = Query(default=None),
    object_id: Optional[str] = Query(default=None),
) -> List[VersionRecordRead]:
    return store.list_versions(
        project_id=project_id,
        universe_id=universe_id,
        object_type=object_type,
        object_id=object_id,
    )


@router.post("/audit/records", response_model=AuditRecordRead, status_code=201)
def create_audit_record(payload: AuditRecordCreate) -> AuditRecordRead:
    audit_record = store.create_audit_record(payload)

    if audit_record is None:
        raise HTTPException(
            status_code=404,
            detail="Project or universe not found for audit record",
        )

    return audit_record


@router.get("/audit/records", response_model=List[AuditRecordRead])
def list_audit_records(
    project_id: Optional[str] = Query(default=None),
    universe_id: Optional[str] = Query(default=None),
    engine_name: Optional[str] = Query(default=None),
) -> List[AuditRecordRead]:
    return store.list_audit_records(
        project_id=project_id,
        universe_id=universe_id,
        engine_name=engine_name,
    )


@router.post("/feedback", response_model=FeedbackRecordRead, status_code=201)
def create_feedback(payload: FeedbackRecordCreate) -> FeedbackRecordRead:
    feedback = store.create_feedback(payload)

    if feedback is None:
        raise HTTPException(
            status_code=404,
            detail="Project or universe not found for feedback record",
        )

    return feedback


@router.get("/feedback", response_model=List[FeedbackRecordRead])
def list_feedback(
    project_id: Optional[str] = Query(default=None),
    universe_id: Optional[str] = Query(default=None),
    object_type: Optional[str] = Query(default=None),
    object_id: Optional[str] = Query(default=None),
) -> List[FeedbackRecordRead]:
    return store.list_feedback(
        project_id=project_id,
        universe_id=universe_id,
        object_type=object_type,
        object_id=object_id,
    )


@router.post("/exports/json", response_model=ExportRecordRead, status_code=201)
def create_json_export_record(payload: ExportRecordCreate) -> ExportRecordRead:
    export_record = store.create_export_record(payload)

    if export_record is None:
        raise HTTPException(
            status_code=404,
            detail="Project or universe not found for export record",
        )

    return export_record


@router.get("/exports", response_model=List[ExportRecordRead])
def list_exports(
    project_id: Optional[str] = Query(default=None),
    universe_id: Optional[str] = Query(default=None),
    export_type: Optional[str] = Query(default=None),
) -> List[ExportRecordRead]:
    return store.list_exports(
        project_id=project_id,
        universe_id=universe_id,
        export_type=export_type,
    )

@router.post("/canon/locks", response_model=CanonLockRead, status_code=201)
def create_canon_lock(payload: CanonLockCreate) -> CanonLockRead:
    canon_lock = store.create_canon_lock(payload)

    if canon_lock is None:
        raise HTTPException(
            status_code=404,
            detail="Project or universe not found for canon lock",
        )

    return canon_lock


@router.get("/canon/locks", response_model=List[CanonLockRead])
def list_canon_locks(
    project_id: Optional[str] = Query(default=None),
    universe_id: Optional[str] = Query(default=None),
    object_type: Optional[str] = Query(default=None),
    object_id: Optional[str] = Query(default=None),
) -> List[CanonLockRead]:
    return store.list_canon_locks(
        project_id=project_id,
        universe_id=universe_id,
        object_type=object_type,
        object_id=object_id,
    )


@router.post("/branches", response_model=BranchRead, status_code=201)
def create_branch(payload: BranchCreate) -> BranchRead:
    branch = store.create_branch(payload)

    if branch is None:
        raise HTTPException(
            status_code=404,
            detail="Project, universe, or parent branch not found",
        )

    return branch


@router.get("/branches", response_model=List[BranchRead])
def list_branches(
    project_id: Optional[str] = Query(default=None),
    universe_id: Optional[str] = Query(default=None),
    branch_type: Optional[str] = Query(default=None),
) -> List[BranchRead]:
    return store.list_branches(
        project_id=project_id,
        universe_id=universe_id,
        branch_type=branch_type,
    )


@router.get("/branches/{branch_id}", response_model=BranchRead)
def get_branch(branch_id: str) -> BranchRead:
    branch = store.get_branch(branch_id)

    if branch is None:
        raise HTTPException(status_code=404, detail="Branch not found")

    return branch


@router.post(
    "/registry/seed/foundation",
    response_model=List[RegistryTypeRead],
    status_code=201,
)
def seed_foundation_registry() -> List[RegistryTypeRead]:
    """Load the official Chunk 1 foundation registry seed pack.

    The endpoint is idempotent: existing type_id values are returned instead of duplicated.
    """
    from backend.app.registry_seed.foundation_seed import FOUNDATION_REGISTRY_SEED

    seeded_types: List[RegistryTypeRead] = []

    for seed_item in FOUNDATION_REGISTRY_SEED:
        existing = store.get_registry_type(seed_item["type_id"])
        if existing is not None:
            seeded_types.append(existing)
            continue

        created = store.create_registry_type(RegistryTypeCreate(**seed_item))
        if created is not None:
            seeded_types.append(created)

    return seeded_types

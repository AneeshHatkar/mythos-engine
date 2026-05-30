from pathlib import Path

from backend.app.schemas.foundation import (
    AuditRecordCreate,
    BranchCreate,
    CanonLockCreate,
    ExportRecordCreate,
    FeedbackRecordCreate,
    ProjectCreate,
    RegistryTypeCreate,
    UniverseCreate,
    VersionRecordCreate,
)
from backend.app.services.foundation_store import SQLiteFoundationStore


def test_sqlite_store_persists_project_across_instances(tmp_path: Path):
    db_path = tmp_path / "mythos_test.db"

    first_store = SQLiteFoundationStore(db_path=str(db_path))
    project = first_store.create_project(
        ProjectCreate(name="Persistent Project")
    )

    second_store = SQLiteFoundationStore(db_path=str(db_path))
    loaded_project = second_store.get_project(project.project_id)

    assert loaded_project is not None
    assert loaded_project.project_id == project.project_id
    assert loaded_project.name == "Persistent Project"


def test_sqlite_store_persists_universe_and_registry_type(tmp_path: Path):
    db_path = tmp_path / "mythos_test.db"

    first_store = SQLiteFoundationStore(db_path=str(db_path))
    project = first_store.create_project(ProjectCreate(name="Persistent Universe Project"))

    universe = first_store.create_universe(
        UniverseCreate(
            project_id=project.project_id,
            name="Persistent Universe",
            genres=["dark_academy"],
        )
    )

    registry_type = first_store.create_registry_type(
        RegistryTypeCreate(
            type_id="test.persistent.registry_type",
            category="test_category",
            name="Persistent Registry Type",
            description="A persisted registry type.",
            tags=["persistent"],
        )
    )

    second_store = SQLiteFoundationStore(db_path=str(db_path))

    loaded_universes = second_store.list_universes_for_project(project.project_id)
    loaded_registry_type = second_store.get_registry_type(
        "test.persistent.registry_type"
    )

    assert universe is not None
    assert registry_type is not None
    assert len(loaded_universes) == 1
    assert loaded_universes[0].name == "Persistent Universe"
    assert loaded_registry_type is not None
    assert loaded_registry_type.name == "Persistent Registry Type"


def test_sqlite_store_persists_tracking_and_branch_records(tmp_path: Path):
    db_path = tmp_path / "mythos_test.db"

    first_store = SQLiteFoundationStore(db_path=str(db_path))
    project = first_store.create_project(ProjectCreate(name="Persistent Tracking Project"))
    universe = first_store.create_universe(
        UniverseCreate(
            project_id=project.project_id,
            name="Persistent Tracking Universe",
        )
    )

    assert universe is not None

    version = first_store.create_version(
        VersionRecordCreate(
            project_id=project.project_id,
            universe_id=universe.universe_id,
            object_type="universe",
            object_id=universe.universe_id,
            summary="Persistent version.",
            snapshot={"name": universe.name},
        )
    )

    audit = first_store.create_audit_record(
        AuditRecordCreate(
            project_id=project.project_id,
            universe_id=universe.universe_id,
            engine_name="foundation.persistence_test",
        )
    )

    feedback = first_store.create_feedback(
        FeedbackRecordCreate(
            project_id=project.project_id,
            universe_id=universe.universe_id,
            object_type="universe",
            object_id=universe.universe_id,
            feedback_type="test_feedback",
            rating=8,
        )
    )

    export = first_store.create_export_record(
        ExportRecordCreate(
            project_id=project.project_id,
            universe_id=universe.universe_id,
            export_type="json_state",
            object_scope="universe",
            file_path="exports/json/test.json",
        )
    )

    canon_lock = first_store.create_canon_lock(
        CanonLockCreate(
            project_id=project.project_id,
            universe_id=universe.universe_id,
            object_type="world_rule",
            object_id="rule_test",
            locked_value={"value": "locked"},
        )
    )

    branch = first_store.create_branch(
        BranchCreate(
            project_id=project.project_id,
            universe_id=universe.universe_id,
            branch_name="Persistent Branch",
        )
    )

    second_store = SQLiteFoundationStore(db_path=str(db_path))

    assert version is not None
    assert audit is not None
    assert feedback is not None
    assert export is not None
    assert canon_lock is not None
    assert branch is not None

    assert len(second_store.list_versions(project_id=project.project_id)) == 1
    assert len(second_store.list_audit_records(project_id=project.project_id)) == 1
    assert len(second_store.list_feedback(project_id=project.project_id)) == 1
    assert len(second_store.list_exports(project_id=project.project_id)) == 1
    assert len(second_store.list_canon_locks(project_id=project.project_id)) == 1
    assert len(second_store.list_branches(project_id=project.project_id)) == 1
    assert second_store.get_branch(branch.branch_id) is not None

import sqlite3
import sys
from pathlib import Path
from typing import Optional


DEFAULT_DB_PATH = Path("data/mythos.db")


def is_pytest_runtime() -> bool:
    """Return True when the app is being imported during pytest.

    Tests should not use the user's real local database because that would make
    tests order-dependent and would pollute local development data.
    """
    return "pytest" in sys.modules


def resolve_database_path(db_path: Optional[str] = None) -> str:
    if db_path:
        return db_path

    if is_pytest_runtime():
        return ":memory:"

    DEFAULT_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return str(DEFAULT_DB_PATH)


def create_connection(db_path: Optional[str] = None) -> sqlite3.Connection:
    resolved_path = resolve_database_path(db_path)
    connection = sqlite3.connect(resolved_path, check_same_thread=False)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_object_store(connection: sqlite3.Connection) -> None:
    """Create the generic persisted object table.

    Chunk 1 stores foundation objects as typed JSON payloads. This is deliberate:
    it keeps the early foundation flexible while still giving us real persistence.
    Later chunks can add specialized relational tables for heavy world, character,
    simulation, and ML data.
    """
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS mythos_objects (
            collection TEXT NOT NULL,
            object_id TEXT NOT NULL,
            type_key TEXT,
            project_id TEXT,
            universe_id TEXT,
            object_type TEXT,
            payload_json TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            PRIMARY KEY (collection, object_id)
        )
        """
    )

    connection.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_mythos_objects_collection
        ON mythos_objects(collection)
        """
    )

    connection.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_mythos_objects_project
        ON mythos_objects(project_id)
        """
    )

    connection.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_mythos_objects_universe
        ON mythos_objects(universe_id)
        """
    )

    connection.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_mythos_objects_type_key
        ON mythos_objects(type_key)
        """
    )

    connection.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_mythos_objects_object_type
        ON mythos_objects(object_type)
        """
    )

    connection.commit()

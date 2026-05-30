import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Type, TypeVar

from pydantic import BaseModel

from backend.app.db.database import create_connection, initialize_object_store
from backend.app.schemas.world import (
    WorldBible,
    WorldCreate,
    WorldRead,
    new_world_id,
)
from backend.app.services.foundation_store import store as foundation_store

ModelT = TypeVar("ModelT", bound=BaseModel)


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class WorldStore:
    """SQLite-backed store for Chunk 2 world objects.

    This store persists:
    - WorldRead objects
    - WorldBible objects

    It uses the same generic mythos_objects table created in Chunk 1.
    """

    def __init__(self, db_path: Optional[str] = None) -> None:
        self.connection = create_connection(db_path)
        initialize_object_store(self.connection)

    def _model_to_json(self, model: BaseModel) -> str:
        return json.dumps(model.model_dump(mode="json"), ensure_ascii=False)

    def _row_to_model(self, row: Any, model_cls: Type[ModelT]) -> ModelT:
        payload = json.loads(row["payload_json"])
        return model_cls.model_validate(payload)

    def _insert_or_replace_model(
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

        existing = self.connection.execute(
            """
            SELECT created_at
            FROM mythos_objects
            WHERE collection = ? AND object_id = ?
            """,
            (collection, object_id),
        ).fetchone()

        created_at = existing["created_at"] if existing else timestamp

        self.connection.execute(
            """
            INSERT OR REPLACE INTO mythos_objects (
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
                universe_id,
                universe_id,
                object_type,
                self._model_to_json(model),
                created_at,
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

    def create_world(self, payload: WorldCreate) -> Optional[WorldRead]:
        if foundation_store.get_universe(payload.universe_id) is None:
            return None

        world = WorldRead(
            world_id=new_world_id("world"),
            universe_id=payload.universe_id,
            name=payload.name,
            seed_premise=payload.seed_premise,
            target_format=payload.target_format,
            scale_label=payload.scale_label,
            genre_tags=payload.genre_tags,
            tone_tags=payload.tone_tags,
            desired_complexity=payload.desired_complexity,
        )

        self._insert_or_replace_model(
            collection="worlds",
            object_id=world.world_id,
            model=world,
            type_key=world.world_id,
            universe_id=world.universe_id,
            object_type="world",
        )
        return world

    def list_worlds(self) -> List[WorldRead]:
        return self._list_models(collection="worlds", model_cls=WorldRead)

    def list_worlds_for_universe(self, universe_id: str) -> List[WorldRead]:
        return self._list_models(
            collection="worlds",
            model_cls=WorldRead,
            filters={"universe_id": universe_id},
        )

    def get_world(self, world_id: str) -> Optional[WorldRead]:
        return self._get_model(
            collection="worlds",
            object_id=world_id,
            model_cls=WorldRead,
        )

    def save_world_bible(self, world_id: str, bible: WorldBible) -> Optional[WorldBible]:
        world = self.get_world(world_id)
        if world is None:
            return None

        if bible.world_id != world_id:
            return None

        if bible.universe_id != world.universe_id:
            return None

        self._insert_or_replace_model(
            collection="world_bibles",
            object_id=world_id,
            model=bible,
            type_key=world_id,
            universe_id=bible.universe_id,
            object_type="world_bible",
        )
        return bible

    def get_world_bible(self, world_id: str) -> Optional[WorldBible]:
        return self._get_model(
            collection="world_bibles",
            object_id=world_id,
            model_cls=WorldBible,
        )


world_store = WorldStore()

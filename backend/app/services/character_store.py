from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import uuid4

from backend.app.schemas.character import CompleteCharacterProfile


class CharacterStore:
    """In-memory character store for early Chunk 3.

    This is the basic character object store used before the deeper
    Character Run Persistence system arrives later in Chunk 3.

    It gives the API a real place to create, retrieve, list, and delete
    character objects while engines are still being built.
    """

    def __init__(self) -> None:
        self._characters: Dict[str, Dict[str, Any]] = {}

    def _utc_now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _new_character_id(self) -> str:
        return f"char_{uuid4().hex[:12]}"

    def create_character(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        character_id = (
            payload.get("character_id")
            or payload.get("identity", {}).get("character_id")
            or self._new_character_id()
        )

        character = dict(payload)
        character["character_id"] = character_id
        character.setdefault("project_id", payload.get("project_id", "default_project"))
        character.setdefault("universe_id", payload.get("universe_id", "default_universe"))
        character.setdefault("world_id", payload.get("world_id"))
        character.setdefault("name", payload.get("name", "Unnamed Character"))
        character.setdefault("role", payload.get("role", "draft_character"))
        character.setdefault("status", "draft")
        character.setdefault("created_at", self._utc_now())
        character["updated_at"] = self._utc_now()

        # Preserve a complete profile if supplied, but keep API flexible
        # during early Chunk 3 while engines are being added.
        if "profile" in character and isinstance(character["profile"], dict):
            try:
                CompleteCharacterProfile.model_validate(character["profile"])
                character["profile_validated"] = True
            except Exception as exc:
                character["profile_validated"] = False
                character["profile_validation_error"] = str(exc)

        self._characters[character_id] = character

        return character

    def get_character(self, character_id: str) -> Optional[Dict[str, Any]]:
        return self._characters.get(character_id)

    def list_characters(
        self,
        *,
        project_id: Optional[str] = None,
        universe_id: Optional[str] = None,
        world_id: Optional[str] = None,
        role: Optional[str] = None,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        characters = list(self._characters.values())

        if project_id:
            characters = [
                character for character in characters
                if character.get("project_id") == project_id
            ]

        if universe_id:
            characters = [
                character for character in characters
                if character.get("universe_id") == universe_id
            ]

        if world_id:
            characters = [
                character for character in characters
                if character.get("world_id") == world_id
            ]

        if role:
            characters = [
                character for character in characters
                if character.get("role") == role
            ]

        characters.sort(key=lambda item: item.get("created_at", ""), reverse=True)

        return characters[:limit]

    def delete_character(self, character_id: str) -> bool:
        if character_id not in self._characters:
            return False

        del self._characters[character_id]
        return True

    def clear(self) -> None:
        self._characters.clear()


character_store = CharacterStore()

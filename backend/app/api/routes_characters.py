from typing import Any, Dict

from fastapi import APIRouter

from backend.app.services.character_store import character_store


router = APIRouter(prefix="/characters", tags=["Characters"])


@router.get("/health")
def character_health() -> Dict[str, Any]:
    return {
        "status": "ok",
        "service": "character_api",
        "chunk": "3",
        "layer": "Character Intelligence Layer",
        "available_endpoints": [
            "GET /characters/health",
            "POST /characters",
            "GET /characters",
            "GET /characters/{character_id}",
            "DELETE /characters/{character_id}",
        ],
    }


@router.post("")
def create_character(payload: Dict[str, Any]) -> Dict[str, Any]:
    character = character_store.create_character(payload)

    return {
        "success": True,
        "character": character,
    }


@router.get("")
def list_characters(
    project_id: str | None = None,
    universe_id: str | None = None,
    world_id: str | None = None,
    role: str | None = None,
    limit: int = 50,
) -> Dict[str, Any]:
    characters = character_store.list_characters(
        project_id=project_id,
        universe_id=universe_id,
        world_id=world_id,
        role=role,
        limit=limit,
    )

    return {
        "success": True,
        "count": len(characters),
        "characters": characters,
    }


@router.get("/{character_id}")
def get_character(character_id: str) -> Dict[str, Any]:
    character = character_store.get_character(character_id)

    if character is None:
        return {
            "success": False,
            "error": f"Character not found: {character_id}",
        }

    return {
        "success": True,
        "character": character,
    }


@router.delete("/{character_id}")
def delete_character(character_id: str) -> Dict[str, Any]:
    deleted = character_store.delete_character(character_id)

    if not deleted:
        return {
            "success": False,
            "error": f"Character not found: {character_id}",
        }

    return {
        "success": True,
        "deleted_character_id": character_id,
    }

from typing import List

from fastapi import APIRouter, HTTPException

from backend.app.schemas.world import WorldBible, WorldCreate, WorldRead
from backend.app.services.foundation_store import store as foundation_store
from backend.app.services.world_store import world_store

router = APIRouter(tags=["Worlds"])


@router.post("/worlds", response_model=WorldRead, status_code=201)
def create_world(payload: WorldCreate) -> WorldRead:
    world = world_store.create_world(payload)

    if world is None:
        raise HTTPException(
            status_code=404,
            detail="Universe not found for world creation",
        )

    return world


@router.get("/worlds", response_model=List[WorldRead])
def list_worlds() -> List[WorldRead]:
    return world_store.list_worlds()


@router.get("/worlds/{world_id}", response_model=WorldRead)
def get_world(world_id: str) -> WorldRead:
    world = world_store.get_world(world_id)

    if world is None:
        raise HTTPException(status_code=404, detail="World not found")

    return world


@router.get("/universes/{universe_id}/worlds", response_model=List[WorldRead])
def list_worlds_for_universe(universe_id: str) -> List[WorldRead]:
    if foundation_store.get_universe(universe_id) is None:
        raise HTTPException(status_code=404, detail="Universe not found")

    return world_store.list_worlds_for_universe(universe_id)


@router.post("/worlds/{world_id}/bible", response_model=WorldBible, status_code=201)
def save_world_bible(world_id: str, bible: WorldBible) -> WorldBible:
    saved_bible = world_store.save_world_bible(world_id, bible)

    if saved_bible is None:
        raise HTTPException(
            status_code=400,
            detail="World not found or world bible IDs do not match",
        )

    return saved_bible


@router.get("/worlds/{world_id}/bible", response_model=WorldBible)
def get_world_bible(world_id: str) -> WorldBible:
    bible = world_store.get_world_bible(world_id)

    if bible is None:
        raise HTTPException(status_code=404, detail="World bible not found")

    return bible

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import uuid4

from pydantic import BaseModel, Field

from backend.app.schemas.global_refs import ArtifactRef, EntityRef, ProjectUniverseRef


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class CrossChunkHandoffContract(BaseModel):
    handoff_id: str = Field(default_factory=lambda: f"handoff_{uuid4().hex[:12]}")
    handoff_type: str
    from_chunk: str
    to_chunk: str
    project_ref: ProjectUniverseRef = Field(default_factory=ProjectUniverseRef)
    required_entity_refs: List[EntityRef] = Field(default_factory=list)
    artifact_refs: List[ArtifactRef] = Field(default_factory=list)
    payload: Dict[str, Any] = Field(default_factory=dict)
    readiness_score: float = 0.0
    ready: bool = False
    missing_fields: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    created_at: str = Field(default_factory=utc_now)


class WorldToCharacterContract(CrossChunkHandoffContract):
    handoff_type: str = "world_to_character"
    from_chunk: str = "world_intelligence"
    to_chunk: str = "character_intelligence"


class CharacterToSimulationContract(CrossChunkHandoffContract):
    handoff_type: str = "character_to_simulation"
    from_chunk: str = "character_intelligence"
    to_chunk: str = "relationship_simulation"


class SimulationToSceneContract(CrossChunkHandoffContract):
    handoff_type: str = "simulation_to_scene"
    from_chunk: str = "relationship_simulation"
    to_chunk: str = "narrative_scene_generation"


class SceneToGenreContract(CrossChunkHandoffContract):
    handoff_type: str = "scene_to_genre"
    from_chunk: str = "narrative_scene_generation"
    to_chunk: str = "genre_specialization"


class GenreToAdaptationContract(CrossChunkHandoffContract):
    handoff_type: str = "genre_to_adaptation"
    from_chunk: str = "genre_specialization"
    to_chunk: str = "adaptation_ip_intelligence"


class SystemToMLTrainingContract(CrossChunkHandoffContract):
    handoff_type: str = "system_to_ml_training"
    from_chunk: str = "full_system"
    to_chunk: str = "ml_data_research"

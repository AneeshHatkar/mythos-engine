from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import uuid4

from pydantic import BaseModel, Field


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class StoryDNASeed(BaseModel):
    story_dna_id: str = Field(default_factory=lambda: f"storydna_{uuid4().hex[:12]}")
    project_id: str = "default_project"
    universe_id: str = "default_universe"
    core_question: str
    central_wound: str
    moral_argument: str
    recurring_symbol_set: List[str] = Field(default_factory=list)
    image_system: List[str] = Field(default_factory=list)
    emotional_promise: str
    philosophical_pressure: str
    tragic_flaw_pattern: str
    redemption_path: str
    corruption_path: str
    meaning_of_power: str
    meaning_of_love: str
    meaning_of_loss: str
    theme_tags: List[str] = Field(default_factory=list)
    generated_by: str = "story_dna_seed_service"
    created_at: str = Field(default_factory=utc_now)


class EmotionalResonanceSeed(BaseModel):
    resonance_id: str = Field(default_factory=lambda: f"resonance_{uuid4().hex[:12]}")
    project_id: str = "default_project"
    universe_id: str = "default_universe"
    desired_reader_emotion: str
    emotional_contrast: str
    scene_aftertaste: str
    heartbreak_vector: float = 0.0
    awe_vector: float = 0.0
    dread_vector: float = 0.0
    hope_vector: float = 0.0
    intimacy_vector: float = 0.0
    betrayal_vector: float = 0.0
    catharsis_condition: str
    resonance_tags: List[str] = Field(default_factory=list)
    created_at: str = Field(default_factory=utc_now)


class CharacterContrastRecord(BaseModel):
    contrast_id: str = Field(default_factory=lambda: f"contrast_{uuid4().hex[:12]}")
    character_a_id: str
    character_b_id: str
    contrast_score: float
    mirror_score: float
    foil_score: float
    chemistry_score: float
    conflict_score: float
    redundancy_warning: bool = False
    contrast_axes: Dict[str, Any] = Field(default_factory=dict)
    story_uses: List[str] = Field(default_factory=list)


class WorldCharacterPressureRecord(BaseModel):
    pressure_id: str = Field(default_factory=lambda: f"pressure_{uuid4().hex[:12]}")
    character_id: str
    world_id: str
    law_pressure: List[str] = Field(default_factory=list)
    class_pressure: List[str] = Field(default_factory=list)
    economic_pressure: List[str] = Field(default_factory=list)
    faction_pressure: List[str] = Field(default_factory=list)
    religious_or_cultural_pressure: List[str] = Field(default_factory=list)
    romance_pressure: List[str] = Field(default_factory=list)
    power_pressure: List[str] = Field(default_factory=list)
    pressure_score: float = 0.0
    simulation_event_fuel: List[str] = Field(default_factory=list)

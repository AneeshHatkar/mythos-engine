from fastapi import FastAPI

from backend.app.api.routes_foundation import router as foundation_router
from backend.app.api.routes_world import router as world_router
from backend.app.api.routes_world_engines import router as world_engines_router
from backend.app.api.routes_characters import router as characters_router
from backend.app.api.routes_character_engines import router as character_engines_router
from backend.app.api.routes_learning import router as learning_router
from backend.app.core.config import settings
from backend.app.schemas.foundation import HealthResponse, RootResponse

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "MythOS Engine is a simulation-driven AI/ML story-universe, "
        "character, adaptation, franchise, and IP intelligence platform."
    ),
)

app.include_router(foundation_router)
app.include_router(world_router)
app.include_router(world_engines_router)
app.include_router(characters_router)
app.include_router(character_engines_router)
app.include_router(learning_router)


@app.get("/", response_model=RootResponse)
def root() -> RootResponse:
    return RootResponse(
        name=settings.app_name,
        version=settings.app_version,
        message="MythOS Engine backend is running.",
        route_groups=[
            "foundation",
            "projects",
            "universes",
            "registry",
            "versioning",
            "audit",
            "feedback",
            "exports",
            "canon",
            "branches",
            "world",
            "world_engines",
            "worlds",
            "world_bibles",
            "world_identity",
            "world_rules",
            "chronology",
            "geography",
            "environment",
            "demographics",
            "society",
            "power_factions",
            "economy",
            "law",
            "military_security",
            "belief_religion",
            "culture_language",
            "knowledge_education",
            "institutions",
            "technology_magic_science",
            "species_creatures",
            "infrastructure",
            "artifacts",
            "aesthetic_texture",
            "civilization_pressure",
            "consistency",
            "originality",
            "story_potential",
            "world_dna",
            "causality_graph",
            "training_readiness",
            "characters",
            "simulation",
            "narrative",
            "genre",
            "adaptation",
            "ml_research",
        ],
    )


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(
        app_name=settings.app_name,
        app_version=settings.app_version,
        environment=settings.environment,
        status="ok",
    )

from backend.app.api.simulation_routes import router as simulation_router
app.include_router(simulation_router)

from fastapi import FastAPI

from backend.app.api.routes_foundation import router as foundation_router
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
            "world",
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
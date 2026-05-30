from backend.app.engines.world.geography_environment_engine import (
    GeographyEnvironmentEngine,
)
from backend.app.schemas.foundation import EngineRunResult
from backend.app.schemas.world import (
    EnvironmentProfile,
    GeographyProfile,
    InfrastructureProfile,
)


def test_geography_environment_engine_returns_engine_result():
    engine = GeographyEnvironmentEngine()

    result = engine.run(
        {
            "world_name": "Velmora",
            "seed_premise": (
                "A late imperial collapse academy empire where relic mines, sealed archives, "
                "and borderlands shape power."
            ),
            "genre_tags": ["dark_academy", "political_fantasy"],
            "tone_tags": ["tragic"],
            "desired_complexity": "extreme",
            "target_format": "seven_novel_series",
        }
    )

    assert isinstance(result, EngineRunResult)
    assert result.success is True
    assert result.engine_name == "world.geography_environment_engine"
    assert "geography" in result.data
    assert "environment" in result.data
    assert "infrastructure" in result.data
    assert "training_notes" in result.data


def test_geography_environment_engine_generates_locations_and_routes():
    engine = GeographyEnvironmentEngine()

    result = engine.run(
        {
            "world_name": "Velmora",
            "seed_premise": (
                "A dark academy empire where relic mines fund institutions and forbidden archives hide history."
            ),
            "genre_tags": ["dark_academy", "political_fantasy"],
            "desired_complexity": "god_level",
        }
    )

    geography = GeographyProfile.model_validate(result.data["geography"])

    assert geography.world_map_summary != ""
    assert len(geography.regions) >= 6
    assert len(geography.locations) >= 6
    assert len(geography.travel_routes) >= 4
    assert len(geography.unknown_regions) >= 1

    location_types = {location.location_type for location in geography.locations}
    assert "capital" in location_types
    assert "academy" in location_types
    assert "forbidden_archive" in location_types
    assert "underground_market" in location_types

    assert any(route.danger_level >= 0.7 for route in geography.travel_routes)


def test_geography_environment_engine_generates_destiny_location_when_needed():
    engine = GeographyEnvironmentEngine()

    result = engine.run(
        {
            "world_name": "Velmora",
            "seed_premise": "A world where 27 destined people are classified by academy law.",
            "genre_tags": ["dark_academy"],
            "desired_complexity": "extreme",
        }
    )

    geography = GeographyProfile.model_validate(result.data["geography"])
    names = [location.name for location in geography.locations]

    assert "The Hall of Unclaimed Fates" in names


def test_geography_environment_engine_generates_environment_pressure():
    engine = GeographyEnvironmentEngine()

    result = engine.run(
        {
            "world_name": "Velmora",
            "seed_premise": "A tragic relic-mining academy empire.",
            "genre_tags": ["dark_academy"],
            "tone_tags": ["tragic"],
            "desired_complexity": "god_level",
        }
    )

    environment = EnvironmentProfile.model_validate(result.data["environment"])

    assert len(environment.climate_zones) >= 4
    assert len(environment.season_patterns) >= 4
    assert len(environment.natural_disasters) >= 2
    assert len(environment.magical_or_environmental_anomalies) >= 2
    assert len(environment.famine_risks) >= 2
    assert len(environment.disease_risks) >= 2
    assert len(environment.environmental_pressures) >= 3
    assert any("Fog" in item or "fog" in item for item in environment.weather_symbolism)


def test_geography_environment_engine_generates_infrastructure_logic():
    engine = GeographyEnvironmentEngine()

    result = engine.run(
        {
            "world_name": "Velmora",
            "seed_premise": "A political academy empire with relic convoys and border checkpoints.",
            "genre_tags": ["dark_academy", "political_fantasy"],
            "desired_complexity": "god_level",
        }
    )

    infrastructure = InfrastructureProfile.model_validate(result.data["infrastructure"])

    assert len(infrastructure.roads) >= 4
    assert len(infrastructure.ports) >= 2
    assert len(infrastructure.bridges) >= 2
    assert len(infrastructure.transit_systems) >= 3
    assert len(infrastructure.postal_or_messenger_systems) >= 3
    assert len(infrastructure.communication_delays) >= 4
    assert len(infrastructure.trade_chokepoints) >= 4
    assert len(infrastructure.border_controls) >= 4
    assert len(infrastructure.infrastructure_decay) >= 4
    assert any("checkpoint" in item.lower() for item in infrastructure.border_controls)


def test_geography_environment_engine_warns_when_seed_missing():
    engine = GeographyEnvironmentEngine()

    result = engine.run({})

    assert result.success is True
    assert len(result.warnings) == 1
    assert "seed_premise" in result.warnings[0]

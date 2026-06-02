from backend.app.engines.deep_world.country_political_unit_system import CountryPoliticalUnitSystem
from backend.app.engines.deep_world.disaster_environmental_pressure_engine import DisasterEnvironmentalPressureEngine
from backend.app.engines.deep_world.economy_resource_ecology_engine import EconomyResourceEcologyEngine
from backend.app.engines.deep_world.ecology_engine import EcologyEngine
from backend.app.engines.deep_world.migration_demographic_movement_engine import MigrationDemographicMovementEngine
from backend.app.engines.deep_world.population_diversity_engine import PopulationDiversityEngine
from backend.app.engines.deep_world.roads_routes_travel_distance_engine import RoadsRoutesTravelDistanceEngine
from backend.app.engines.deep_world.settlement_engine import SettlementEngine


def build_context():
    population_engine = PopulationDiversityEngine()
    political_system = CountryPoliticalUnitSystem()
    settlement_engine = SettlementEngine()
    route_engine = RoadsRoutesTravelDistanceEngine()
    ecology_engine = EcologyEngine()
    economy_engine = EconomyResourceEcologyEngine()
    disaster_engine = DisasterEnvironmentalPressureEngine()

    population = population_engine.build_population_diversity_profile(source_id="migration_context")[
        "population_diversity_profile"
    ]
    unit = political_system.build_political_unit(source_id="migration_context")["political_unit"]
    settlement = settlement_engine.build_settlement(source_id="migration_context", political_unit=unit)["settlement"]
    route_network = route_engine.build_route_network(
        source_id="migration_context",
        settlements=[settlement],
        political_unit=unit,
    )["route_network"]
    ecology = ecology_engine.build_ecology_system(source_id="migration_context")["deep_world_ecology_system"]
    economy = economy_engine.build_resource_economy_profile(
        source_id="migration_context",
        ecology_profile=ecology.model_dump(),
        political_unit=unit,
        settlement=settlement,
        route_network=route_network,
    )["resource_economy_profile"]
    disaster = disaster_engine.build_disaster_pressure_profile(
        source_id="migration_context",
        ecology_profile=ecology.model_dump(),
        settlement=settlement,
        route_network=route_network,
        economy_profile=economy,
    )["disaster_pressure_profile"]

    return population, unit, settlement, route_network, disaster, economy


def test_migration_engine_builds_migration_system():
    population, unit, settlement, route_network, disaster, economy = build_context()
    engine = MigrationDemographicMovementEngine()

    system = engine.build_migration_system(
        source_id="migration_test",
        population_profile=population,
        political_unit=unit,
        settlement=settlement,
        route_network=route_network,
        disaster_profile=disaster,
        economy_profile=economy,
        migration_seed={
            "system_name": "Ashglass Tide Refuge Movement",
            "region_name": "Ashglass Coast",
        },
    )["migration_system"]

    assert system["system_name"] == "Ashglass Tide Refuge Movement"
    assert system["region_name"] == "Ashglass Coast"
    assert system["population_diversity_profile_id"] == population["population_diversity_profile_id"]
    assert system["political_unit_id"] == unit["political_unit_id"]
    assert system["settlement_id"] == settlement["settlement_id"]
    assert system["route_network_id"] == route_network["route_network_id"]
    assert system["disaster_pressure_profile_id"] == disaster["disaster_pressure_profile_id"]
    assert system["resource_economy_profile_id"] == economy["resource_economy_profile_id"]
    assert system["migration_types"]
    assert system["demographic_groups"]
    assert system["identity_changes"]
    assert system["detail_depth_score"] >= 0.75


def test_migration_engine_builds_migration_event():
    population, unit, settlement, route_network, disaster, economy = build_context()
    engine = MigrationDemographicMovementEngine()
    system = engine.build_migration_system(
        source_id="event_test",
        population_profile=population,
        political_unit=unit,
        settlement=settlement,
        route_network=route_network,
        disaster_profile=disaster,
        economy_profile=economy,
    )["migration_system"]

    event = engine.build_migration_event(
        source_id="event_test",
        migration_system=system,
        event_seed={
            "event_name": "Archive Exile Road Flight",
            "origin": "Saltbark Archive Row",
            "destination": "border ravines",
            "route_taken": "Red Fog Underway",
        },
    )["migration_event"]

    assert event["migration_system_id"] == system["migration_system_id"]
    assert event["event_name"] == "Archive Exile Road Flight"
    assert event["origin"] == "Saltbark Archive Row"
    assert event["destination"] == "border ravines"
    assert event["route_taken"] == "Red Fog Underway"
    assert event["moving_groups"]
    assert event["legal_status"]
    assert event["memory_effect"]


def test_migration_engine_builds_story_context_patch():
    population, unit, settlement, route_network, disaster, economy = build_context()
    engine = MigrationDemographicMovementEngine()
    system = engine.build_migration_system(
        source_id="patch_test",
        population_profile=population,
        political_unit=unit,
        settlement=settlement,
        route_network=route_network,
        disaster_profile=disaster,
        economy_profile=economy,
    )["migration_system"]
    event = engine.build_migration_event(source_id="patch_test", migration_system=system)["migration_event"]

    patch = engine.build_story_context_patch(migration_system=system, migration_event=event)["story_context_patch"]

    assert patch["migration_system_id"] == system["migration_system_id"]
    assert patch["active_migration_event"]["migration_event_id"] == event["migration_event_id"]
    assert "generation_hints" in patch
    assert "memory_update_candidates" in patch
    assert len(patch["memory_update_candidates"]) == 2


def test_migration_engine_validates_system_and_event():
    population, unit, settlement, route_network, disaster, economy = build_context()
    engine = MigrationDemographicMovementEngine()
    system = engine.build_migration_system(
        source_id="validate_test",
        population_profile=population,
        political_unit=unit,
        settlement=settlement,
        route_network=route_network,
        disaster_profile=disaster,
        economy_profile=economy,
    )["migration_system"]
    event = engine.build_migration_event(source_id="validate_test", migration_system=system)["migration_event"]

    system_validation = engine.validate_migration_system(migration_system=system)
    event_validation = engine.validate_migration_event(migration_event=event)

    assert system_validation["passed"] is True
    assert system_validation["missing_fields"] == []
    assert event_validation["passed"] is True
    assert event_validation["missing_fields"] == []


def test_migration_engine_detects_bad_records():
    engine = MigrationDemographicMovementEngine()

    system_validation = engine.validate_migration_system(
        migration_system={
            "migration_system_id": "bad_migration",
            "system_name": "Generic Migration",
            "story_use": "Bad.",
        }
    )

    event_validation = engine.validate_migration_event(
        migration_event={
            "migration_event_id": "bad_event",
            "event_name": "People moved",
            "plot_effect": "Bad.",
        }
    )

    assert system_validation["passed"] is False
    assert system_validation["missing_fields"]
    assert "story_use" in system_validation["shallow_fields"]

    assert event_validation["passed"] is False
    assert event_validation["missing_fields"]
    assert "plot_effect" in event_validation["shallow_fields"]


def test_migration_engine_summarizes_and_textualizes():
    population, unit, settlement, route_network, disaster, economy = build_context()
    engine = MigrationDemographicMovementEngine()
    system = engine.build_migration_system(
        source_id="text_test",
        population_profile=population,
        political_unit=unit,
        settlement=settlement,
        route_network=route_network,
        disaster_profile=disaster,
        economy_profile=economy,
    )["migration_system"]
    event = engine.build_migration_event(source_id="text_test", migration_system=system)["migration_event"]

    summary = engine.summarize_migration_system(migration_system=system, migration_event=event)
    text = engine.build_migration_text(migration_system=system, migration_event=event)["migration_text"]

    assert summary["success"] is True
    assert summary["summary"]["migration_system_id"] == system["migration_system_id"]
    assert "Migration + Demographic Movement Profile" in text
    assert "Identity Changes" in text
    assert "Memory Effect" in text

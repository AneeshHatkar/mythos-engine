from backend.app.engines.deep_world.climate_weather_engine import ClimateWeatherSimulationEngine
from backend.app.engines.deep_world.country_political_unit_system import CountryPoliticalUnitSystem
from backend.app.engines.deep_world.disaster_environmental_pressure_engine import DisasterEnvironmentalPressureEngine
from backend.app.engines.deep_world.economy_resource_ecology_engine import EconomyResourceEcologyEngine
from backend.app.engines.deep_world.ecology_engine import EcologyEngine
from backend.app.engines.deep_world.roads_routes_travel_distance_engine import RoadsRoutesTravelDistanceEngine
from backend.app.engines.deep_world.settlement_engine import SettlementEngine


def build_context():
    climate_engine = ClimateWeatherSimulationEngine()
    ecology_engine = EcologyEngine()
    political_system = CountryPoliticalUnitSystem()
    settlement_engine = SettlementEngine()
    route_engine = RoadsRoutesTravelDistanceEngine()
    economy_engine = EconomyResourceEcologyEngine()

    climate = climate_engine.build_climate_system(source_id="disaster_context")["deep_world_climate_system"]
    ecology = ecology_engine.build_ecology_system(source_id="disaster_context")["deep_world_ecology_system"]
    unit = political_system.build_political_unit(source_id="disaster_context")["political_unit"]
    settlement = settlement_engine.build_settlement(source_id="disaster_context", political_unit=unit)["settlement"]
    route_network = route_engine.build_route_network(
        source_id="disaster_context",
        settlements=[settlement],
        political_unit=unit,
    )["route_network"]
    economy = economy_engine.build_resource_economy_profile(
        source_id="disaster_context",
        ecology_profile=ecology.model_dump(),
        political_unit=unit,
        settlement=settlement,
        route_network=route_network,
    )["resource_economy_profile"]

    return climate.model_dump(), ecology.model_dump(), settlement, route_network, economy


def test_disaster_engine_builds_pressure_profile():
    climate, ecology, settlement, route_network, economy = build_context()
    engine = DisasterEnvironmentalPressureEngine()

    profile = engine.build_disaster_pressure_profile(
        source_id="disaster_test",
        climate_profile=climate,
        ecology_profile=ecology,
        settlement=settlement,
        route_network=route_network,
        economy_profile=economy,
        disaster_seed={
            "pressure_name": "Ashglass Red Tide Disaster Cycle",
            "region_name": "Ashglass Coast",
        },
    )["disaster_pressure_profile"]

    assert profile["pressure_name"] == "Ashglass Red Tide Disaster Cycle"
    assert profile["region_name"] == "Ashglass Coast"
    assert profile["settlement_id"] == settlement["settlement_id"]
    assert profile["route_network_id"] == route_network["route_network_id"]
    assert profile["resource_economy_profile_id"] == economy["resource_economy_profile_id"]
    assert profile["disaster_types"]
    assert profile["pressure_chains"]
    assert profile["settlement_impacts"]
    assert profile["route_impacts"]
    assert profile["economy_impacts"]
    assert profile["detail_depth_score"] >= 0.75


def test_disaster_engine_builds_disaster_event():
    climate, ecology, settlement, route_network, economy = build_context()
    engine = DisasterEnvironmentalPressureEngine()
    profile = engine.build_disaster_pressure_profile(
        source_id="event_test",
        climate_profile=climate,
        ecology_profile=ecology,
        settlement=settlement,
        route_network=route_network,
        economy_profile=economy,
    )["disaster_pressure_profile"]

    event = engine.build_disaster_event(
        source_id="event_test",
        disaster_pressure_profile=profile,
        event_seed={
            "event_name": "Bell Rain Flood Closure",
            "trigger": "bell rain flooded old tower underways",
            "severity": "critical",
        },
    )["disaster_event"]

    assert event["disaster_pressure_profile_id"] == profile["disaster_pressure_profile_id"]
    assert event["event_name"] == "Bell Rain Flood Closure"
    assert event["trigger"] == "bell rain flooded old tower underways"
    assert event["severity"] == "critical"
    assert event["affected_locations"]
    assert event["affected_groups"]
    assert event["immediate_consequences"]
    assert event["memory_effect"]


def test_disaster_engine_builds_story_context_patch():
    climate, ecology, settlement, route_network, economy = build_context()
    engine = DisasterEnvironmentalPressureEngine()
    profile = engine.build_disaster_pressure_profile(
        source_id="patch_test",
        climate_profile=climate,
        ecology_profile=ecology,
        settlement=settlement,
        route_network=route_network,
        economy_profile=economy,
    )["disaster_pressure_profile"]
    event = engine.build_disaster_event(source_id="patch_test", disaster_pressure_profile=profile)["disaster_event"]

    patch = engine.build_story_context_patch(
        disaster_pressure_profile=profile,
        disaster_event=event,
    )["story_context_patch"]

    assert patch["disaster_pressure_profile_id"] == profile["disaster_pressure_profile_id"]
    assert patch["active_disaster_event"]["disaster_event_id"] == event["disaster_event_id"]
    assert "generation_hints" in patch
    assert "memory_update_candidates" in patch
    assert len(patch["memory_update_candidates"]) == 2


def test_disaster_engine_validates_profile_and_event():
    climate, ecology, settlement, route_network, economy = build_context()
    engine = DisasterEnvironmentalPressureEngine()
    profile = engine.build_disaster_pressure_profile(
        source_id="validate_test",
        climate_profile=climate,
        ecology_profile=ecology,
        settlement=settlement,
        route_network=route_network,
        economy_profile=economy,
    )["disaster_pressure_profile"]
    event = engine.build_disaster_event(source_id="validate_test", disaster_pressure_profile=profile)["disaster_event"]

    profile_validation = engine.validate_disaster_pressure_profile(disaster_pressure_profile=profile)
    event_validation = engine.validate_disaster_event(disaster_event=event)

    assert profile_validation["passed"] is True
    assert profile_validation["missing_fields"] == []
    assert event_validation["passed"] is True
    assert event_validation["missing_fields"] == []


def test_disaster_engine_detects_bad_records():
    engine = DisasterEnvironmentalPressureEngine()

    profile_validation = engine.validate_disaster_pressure_profile(
        disaster_pressure_profile={
            "disaster_pressure_profile_id": "bad_pressure",
            "pressure_name": "Generic Disaster",
            "story_use": "Bad.",
        }
    )

    event_validation = engine.validate_disaster_event(
        disaster_event={
            "disaster_event_id": "bad_event",
            "event_name": "Storm",
            "plot_effect": "Bad.",
        }
    )

    assert profile_validation["passed"] is False
    assert profile_validation["missing_fields"]
    assert "story_use" in profile_validation["shallow_fields"]

    assert event_validation["passed"] is False
    assert event_validation["missing_fields"]
    assert "plot_effect" in event_validation["shallow_fields"]


def test_disaster_engine_summarizes_and_textualizes():
    climate, ecology, settlement, route_network, economy = build_context()
    engine = DisasterEnvironmentalPressureEngine()
    profile = engine.build_disaster_pressure_profile(
        source_id="text_test",
        climate_profile=climate,
        ecology_profile=ecology,
        settlement=settlement,
        route_network=route_network,
        economy_profile=economy,
    )["disaster_pressure_profile"]
    event = engine.build_disaster_event(source_id="text_test", disaster_pressure_profile=profile)["disaster_event"]

    summary = engine.summarize_disaster_pressure(disaster_pressure_profile=profile, disaster_event=event)
    text = engine.build_disaster_pressure_text(
        disaster_pressure_profile=profile,
        disaster_event=event,
    )["disaster_pressure_text"]

    assert summary["success"] is True
    assert summary["summary"]["disaster_pressure_profile_id"] == profile["disaster_pressure_profile_id"]
    assert "Disaster + Environmental Pressure Profile" in text
    assert "Pressure Chains" in text
    assert "Memory Effect" in text

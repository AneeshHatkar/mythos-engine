from backend.app.engines.deep_world.country_political_unit_system import CountryPoliticalUnitSystem
from backend.app.engines.deep_world.economy_resource_ecology_engine import EconomyResourceEcologyEngine
from backend.app.engines.deep_world.ecology_engine import EcologyEngine
from backend.app.engines.deep_world.roads_routes_travel_distance_engine import RoadsRoutesTravelDistanceEngine
from backend.app.engines.deep_world.settlement_engine import SettlementEngine


def build_context():
    ecology_engine = EcologyEngine()
    political_system = CountryPoliticalUnitSystem()
    settlement_engine = SettlementEngine()
    route_engine = RoadsRoutesTravelDistanceEngine()

    ecology = ecology_engine.build_ecology_system(source_id="economy_context")["deep_world_ecology_system"]
    unit = political_system.build_political_unit(source_id="economy_context")["political_unit"]
    settlement = settlement_engine.build_settlement(source_id="economy_context", political_unit=unit)["settlement"]
    route_network = route_engine.build_route_network(
        source_id="economy_context",
        settlements=[settlement],
        political_unit=unit,
    )["route_network"]

    return ecology.model_dump(), unit, settlement, route_network


def test_economy_resource_engine_builds_profile():
    ecology, unit, settlement, route_network = build_context()
    engine = EconomyResourceEcologyEngine()

    profile = engine.build_resource_economy_profile(
        source_id="economy_test",
        ecology_profile=ecology,
        political_unit=unit,
        settlement=settlement,
        route_network=route_network,
        economy_seed={
            "economy_name": "Ashglass Tide-Medicine Economy",
            "region_name": "Ashglass Coast",
        },
    )["resource_economy_profile"]

    assert profile["economy_name"] == "Ashglass Tide-Medicine Economy"
    assert profile["region_name"] == "Ashglass Coast"
    assert profile["political_unit_id"] == unit["political_unit_id"]
    assert profile["settlement_id"] == settlement["settlement_id"]
    assert profile["route_network_id"] == route_network["route_network_id"]
    assert profile["core_resources"]
    assert profile["production_chains"]
    assert profile["trade_routes"]
    assert profile["scarcity_rules"]
    assert profile["black_market_system"]
    assert profile["detail_depth_score"] >= 0.75


def test_economy_resource_engine_builds_shock_event():
    ecology, unit, settlement, route_network = build_context()
    engine = EconomyResourceEcologyEngine()
    profile = engine.build_resource_economy_profile(
        source_id="shock_test",
        ecology_profile=ecology,
        political_unit=unit,
        settlement=settlement,
        route_network=route_network,
    )["resource_economy_profile"]

    shock = engine.build_economic_shock_event(
        source_id="shock_test",
        resource_economy_profile=profile,
        shock_seed={
            "shock_name": "Foglamp Oil Panic",
            "trigger": "poor district lamps went dark during red fog",
        },
    )["economic_shock_event"]

    assert shock["resource_economy_profile_id"] == profile["resource_economy_profile_id"]
    assert shock["shock_name"] == "Foglamp Oil Panic"
    assert shock["trigger"] == "poor district lamps went dark during red fog"
    assert shock["affected_resources"]
    assert shock["affected_groups"]
    assert shock["price_effect"]
    assert shock["black_market_effect"]
    assert shock["memory_effect"]


def test_economy_resource_engine_builds_story_context_patch():
    ecology, unit, settlement, route_network = build_context()
    engine = EconomyResourceEcologyEngine()
    profile = engine.build_resource_economy_profile(
        source_id="patch_test",
        ecology_profile=ecology,
        political_unit=unit,
        settlement=settlement,
        route_network=route_network,
    )["resource_economy_profile"]
    shock = engine.build_economic_shock_event(
        source_id="patch_test",
        resource_economy_profile=profile,
    )["economic_shock_event"]

    patch = engine.build_story_context_patch(
        resource_economy_profile=profile,
        economic_shock_event=shock,
    )["story_context_patch"]

    assert patch["resource_economy_profile_id"] == profile["resource_economy_profile_id"]
    assert patch["active_economic_shock_event"]["economic_shock_event_id"] == shock["economic_shock_event_id"]
    assert "generation_hints" in patch
    assert "memory_update_candidates" in patch
    assert len(patch["memory_update_candidates"]) == 2


def test_economy_resource_engine_validates_profile_and_shock():
    ecology, unit, settlement, route_network = build_context()
    engine = EconomyResourceEcologyEngine()
    profile = engine.build_resource_economy_profile(
        source_id="validate_test",
        ecology_profile=ecology,
        political_unit=unit,
        settlement=settlement,
        route_network=route_network,
    )["resource_economy_profile"]
    shock = engine.build_economic_shock_event(
        source_id="validate_test",
        resource_economy_profile=profile,
    )["economic_shock_event"]

    profile_validation = engine.validate_resource_economy_profile(resource_economy_profile=profile)
    shock_validation = engine.validate_economic_shock_event(economic_shock_event=shock)

    assert profile_validation["passed"] is True
    assert profile_validation["missing_fields"] == []
    assert shock_validation["passed"] is True
    assert shock_validation["missing_fields"] == []


def test_economy_resource_engine_detects_bad_records():
    engine = EconomyResourceEcologyEngine()

    profile_validation = engine.validate_resource_economy_profile(
        resource_economy_profile={
            "resource_economy_profile_id": "bad_economy",
            "economy_name": "Generic Economy",
            "story_use": "Bad.",
        }
    )

    shock_validation = engine.validate_economic_shock_event(
        economic_shock_event={
            "economic_shock_event_id": "bad_shock",
            "shock_name": "Shortage",
            "plot_effect": "Bad.",
        }
    )

    assert profile_validation["passed"] is False
    assert profile_validation["missing_fields"]
    assert "story_use" in profile_validation["shallow_fields"]

    assert shock_validation["passed"] is False
    assert shock_validation["missing_fields"]
    assert "plot_effect" in shock_validation["shallow_fields"]


def test_economy_resource_engine_summarizes_and_textualizes():
    ecology, unit, settlement, route_network = build_context()
    engine = EconomyResourceEcologyEngine()
    profile = engine.build_resource_economy_profile(
        source_id="text_test",
        ecology_profile=ecology,
        political_unit=unit,
        settlement=settlement,
        route_network=route_network,
    )["resource_economy_profile"]
    shock = engine.build_economic_shock_event(
        source_id="text_test",
        resource_economy_profile=profile,
    )["economic_shock_event"]

    summary = engine.summarize_resource_economy(
        resource_economy_profile=profile,
        economic_shock_event=shock,
    )
    text = engine.build_resource_economy_text(
        resource_economy_profile=profile,
        economic_shock_event=shock,
    )["resource_economy_text"]

    assert summary["success"] is True
    assert summary["summary"]["resource_economy_profile_id"] == profile["resource_economy_profile_id"]
    assert "Economy + Resource Ecology Profile" in text
    assert "Core Resources" in text
    assert "Memory Effect" in text

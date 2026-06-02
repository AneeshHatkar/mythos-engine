from backend.app.engines.deep_world.country_political_unit_system import CountryPoliticalUnitSystem
from backend.app.engines.deep_world.roads_routes_travel_distance_engine import RoadsRoutesTravelDistanceEngine
from backend.app.engines.deep_world.settlement_engine import SettlementEngine


def build_context():
    political_system = CountryPoliticalUnitSystem()
    settlement_engine = SettlementEngine()

    unit = political_system.build_political_unit(source_id="route_context")["political_unit"]
    settlement = settlement_engine.build_settlement(source_id="route_context", political_unit=unit)["settlement"]

    return unit, settlement


def test_roads_routes_engine_builds_route_network():
    unit, settlement = build_context()
    engine = RoadsRoutesTravelDistanceEngine()

    network = engine.build_route_network(
        source_id="route_test",
        settlements=[settlement],
        political_unit=unit,
        route_seed={
            "network_name": "Ashglass Tide Roads",
            "region_name": "Ashglass Coast",
        },
    )["route_network"]

    assert network["network_name"] == "Ashglass Tide Roads"
    assert network["region_name"] == "Ashglass Coast"
    assert network["political_unit_id"] == unit["political_unit_id"]
    assert settlement["settlement_id"] in network["settlement_refs"]
    assert network["route_types"]
    assert network["major_routes"]
    assert network["distance_rules"]
    assert network["weather_effects"]
    assert network["hidden_routes"]
    assert network["blocked_routes"]
    assert network["detail_depth_score"] >= 0.75


def test_roads_routes_engine_builds_travel_plan():
    unit, settlement = build_context()
    engine = RoadsRoutesTravelDistanceEngine()
    network = engine.build_route_network(source_id="travel_test", settlements=[settlement], political_unit=unit)[
        "route_network"
    ]

    travel = engine.build_travel_plan(
        source_id="travel_test",
        route_network=network,
        travel_seed={
            "route_name": "Nine-Bell Road",
            "traveler_group": "accused witness and hired fog guide",
            "estimated_distance_days": 4,
        },
    )["travel_plan"]

    assert travel["route_network_id"] == network["route_network_id"]
    assert travel["route_name"] == "Nine-Bell Road"
    assert travel["traveler_group"] == "accused witness and hired fog guide"
    assert travel["estimated_distance_days"] == 4
    assert travel["required_supplies"]
    assert travel["danger_points"]
    assert travel["social_risks"]
    assert travel["memory_effect"]


def test_roads_routes_engine_builds_story_context_patch():
    unit, settlement = build_context()
    engine = RoadsRoutesTravelDistanceEngine()
    network = engine.build_route_network(source_id="patch_test", settlements=[settlement], political_unit=unit)[
        "route_network"
    ]
    travel = engine.build_travel_plan(source_id="patch_test", route_network=network)["travel_plan"]

    patch = engine.build_story_context_patch(route_network=network, travel_plan=travel)["story_context_patch"]

    assert patch["route_network_id"] == network["route_network_id"]
    assert patch["active_travel_plan"]["travel_plan_id"] == travel["travel_plan_id"]
    assert "generation_hints" in patch
    assert "memory_update_candidates" in patch
    assert len(patch["memory_update_candidates"]) == 2


def test_roads_routes_engine_validates_network_and_travel_plan():
    unit, settlement = build_context()
    engine = RoadsRoutesTravelDistanceEngine()
    network = engine.build_route_network(source_id="validate_test", settlements=[settlement], political_unit=unit)[
        "route_network"
    ]
    travel = engine.build_travel_plan(source_id="validate_test", route_network=network)["travel_plan"]

    network_validation = engine.validate_route_network(route_network=network)
    travel_validation = engine.validate_travel_plan(travel_plan=travel)

    assert network_validation["passed"] is True
    assert network_validation["missing_fields"] == []
    assert travel_validation["passed"] is True
    assert travel_validation["missing_fields"] == []


def test_roads_routes_engine_detects_bad_records():
    engine = RoadsRoutesTravelDistanceEngine()

    network_validation = engine.validate_route_network(
        route_network={
            "route_network_id": "bad_network",
            "network_name": "Generic Roads",
            "story_use": "Bad.",
        }
    )

    travel_validation = engine.validate_travel_plan(
        travel_plan={
            "travel_plan_id": "bad_travel",
            "route_name": "Road",
            "plot_effect": "Bad.",
        }
    )

    assert network_validation["passed"] is False
    assert network_validation["missing_fields"]
    assert "story_use" in network_validation["shallow_fields"]

    assert travel_validation["passed"] is False
    assert travel_validation["missing_fields"]
    assert "plot_effect" in travel_validation["shallow_fields"]


def test_roads_routes_engine_summarizes_and_textualizes():
    unit, settlement = build_context()
    engine = RoadsRoutesTravelDistanceEngine()
    network = engine.build_route_network(source_id="text_test", settlements=[settlement], political_unit=unit)[
        "route_network"
    ]
    travel = engine.build_travel_plan(source_id="text_test", route_network=network)["travel_plan"]

    summary = engine.summarize_route_network(route_network=network, travel_plan=travel)
    text = engine.build_route_text(route_network=network, travel_plan=travel)["route_text"]

    assert summary["success"] is True
    assert summary["summary"]["route_network_id"] == network["route_network_id"]
    assert "Roads, Routes, Travel, and Distance Profile" in text
    assert "Hidden Routes" in text
    assert "Memory Effect" in text

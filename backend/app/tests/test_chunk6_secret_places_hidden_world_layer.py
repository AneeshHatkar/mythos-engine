from backend.app.engines.deep_world.country_political_unit_system import CountryPoliticalUnitSystem
from backend.app.engines.deep_world.roads_routes_travel_distance_engine import RoadsRoutesTravelDistanceEngine
from backend.app.engines.deep_world.secret_places_hidden_world_layer import SecretPlacesHiddenWorldLayer
from backend.app.engines.deep_world.settlement_engine import SettlementEngine


def build_context():
    political_system = CountryPoliticalUnitSystem()
    settlement_engine = SettlementEngine()
    route_engine = RoadsRoutesTravelDistanceEngine()

    unit = political_system.build_political_unit(source_id="secret_context")["political_unit"]
    settlement = settlement_engine.build_settlement(source_id="secret_context", political_unit=unit)["settlement"]
    route_network = route_engine.build_route_network(
        source_id="secret_context",
        settlements=[settlement],
        political_unit=unit,
    )["route_network"]

    return unit, settlement, route_network


def test_secret_places_layer_builds_secret_place():
    unit, settlement, route_network = build_context()
    layer = SecretPlacesHiddenWorldLayer()

    secret_place = layer.build_secret_place(
        source_id="secret_test",
        settlement=settlement,
        route_network=route_network,
        political_unit=unit,
        secret_seed={
            "base_name": "Mirel",
            "unique_name": "The Tideglass Underarchive of Mirel",
            "secret_place_type": "submerged temple archive",
            "region_name": "Ashglass Coast",
        },
    )["secret_place"]

    assert secret_place["unique_name"] == "The Tideglass Underarchive of Mirel"
    assert secret_place["secret_place_type"] == "submerged temple archive"
    assert secret_place["settlement_id"] == settlement["settlement_id"]
    assert secret_place["route_network_id"] == route_network["route_network_id"]
    assert secret_place["political_unit_id"] == unit["political_unit_id"]
    assert secret_place["discovery_conditions"]
    assert secret_place["access_rules"]
    assert secret_place["hidden_contents"]
    assert secret_place["who_knows"]
    assert secret_place["detail_depth_score"] >= 0.75


def test_secret_places_layer_builds_reveal_event():
    _, settlement, route_network = build_context()
    layer = SecretPlacesHiddenWorldLayer()
    secret_place = layer.build_secret_place(
        source_id="reveal_test",
        settlement=settlement,
        route_network=route_network,
    )["secret_place"]

    reveal = layer.build_secret_reveal_event(
        source_id="reveal_test",
        secret_place=secret_place,
        reveal_seed={
            "reveal_name": "Underarchive Tide Witness",
            "trigger": "blue tide exposed the old temple stairs",
        },
    )["secret_reveal_event"]

    assert reveal["secret_place_id"] == secret_place["secret_place_id"]
    assert reveal["reveal_name"] == "Underarchive Tide Witness"
    assert reveal["trigger"] == "blue tide exposed the old temple stairs"
    assert reveal["revealed_truth"]
    assert reveal["evidence_revealed"]
    assert reveal["public_consequence"]
    assert reveal["memory_effect"]


def test_secret_places_layer_builds_story_context_patch():
    _, settlement, route_network = build_context()
    layer = SecretPlacesHiddenWorldLayer()
    secret_place = layer.build_secret_place(
        source_id="patch_test",
        settlement=settlement,
        route_network=route_network,
    )["secret_place"]
    reveal = layer.build_secret_reveal_event(source_id="patch_test", secret_place=secret_place)["secret_reveal_event"]

    patch = layer.build_story_context_patch(
        secret_place=secret_place,
        reveal_event=reveal,
    )["story_context_patch"]

    assert patch["secret_place_id"] == secret_place["secret_place_id"]
    assert patch["active_secret_reveal_event"]["secret_reveal_event_id"] == reveal["secret_reveal_event_id"]
    assert "generation_hints" in patch
    assert "memory_update_candidates" in patch
    assert len(patch["memory_update_candidates"]) == 2


def test_secret_places_layer_validates_place_and_reveal():
    _, settlement, route_network = build_context()
    layer = SecretPlacesHiddenWorldLayer()
    secret_place = layer.build_secret_place(
        source_id="validate_test",
        settlement=settlement,
        route_network=route_network,
    )["secret_place"]
    reveal = layer.build_secret_reveal_event(source_id="validate_test", secret_place=secret_place)["secret_reveal_event"]

    place_validation = layer.validate_secret_place(secret_place=secret_place)
    reveal_validation = layer.validate_reveal_event(reveal_event=reveal)

    assert place_validation["passed"] is True
    assert place_validation["missing_fields"] == []
    assert reveal_validation["passed"] is True
    assert reveal_validation["missing_fields"] == []


def test_secret_places_layer_detects_bad_records():
    layer = SecretPlacesHiddenWorldLayer()

    place_validation = layer.validate_secret_place(
        secret_place={
            "secret_place_id": "bad_secret",
            "unique_name": "Generic Cave",
            "story_use": "Bad.",
        }
    )

    reveal_validation = layer.validate_reveal_event(
        reveal_event={
            "secret_reveal_event_id": "bad_reveal",
            "reveal_name": "Secret",
            "plot_effect": "Bad.",
        }
    )

    assert place_validation["passed"] is False
    assert place_validation["missing_fields"]
    assert "story_use" in place_validation["shallow_fields"]

    assert reveal_validation["passed"] is False
    assert reveal_validation["missing_fields"]
    assert "plot_effect" in reveal_validation["shallow_fields"]


def test_secret_places_layer_summarizes_and_textualizes():
    _, settlement, route_network = build_context()
    layer = SecretPlacesHiddenWorldLayer()
    secret_place = layer.build_secret_place(
        source_id="text_test",
        settlement=settlement,
        route_network=route_network,
    )["secret_place"]
    reveal = layer.build_secret_reveal_event(source_id="text_test", secret_place=secret_place)["secret_reveal_event"]

    summary = layer.summarize_secret_place(secret_place=secret_place, reveal_event=reveal)
    text = layer.build_secret_place_text(secret_place=secret_place, reveal_event=reveal)["secret_place_text"]

    assert summary["success"] is True
    assert summary["summary"]["secret_place_id"] == secret_place["secret_place_id"]
    assert "Secret Places + Hidden World Profile" in text
    assert "Secret Truth" in text
    assert "Memory Effect" in text

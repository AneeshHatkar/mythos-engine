from backend.app.engines.world.faction_institution_resource_engine import FactionInstitutionResourceEngine
from backend.app.engines.world.world_location_access_engine import WorldLocationAccessEngine
from backend.app.engines.world.world_rule_conflict_detector import WorldRuleConflictDetector
from backend.app.services.world_state_snapshot_service import WorldStateSnapshotService


def sample_world():
    return {
        "world_id": "world_velmora",
        "world_name": "Velmora",
        "social_classes": ["erased", "academy_sponsored", "old_nobility"],
        "magic_rules": ["relic power requires cost and counterplay"],
        "legal_constraints": ["distrusted family names require sponsor to testify"],
        "factions": ["Oath Court", "Relic Guild"],
        "institutions": ["Academy", "Court"],
        "academy_access": ["sponsor seat", "exam route", "debt contract"],
        "economy": ["relic labor", "sponsor seats"],
        "culture": ["public names carry legal trust"],
        "geography": ["capital court district", "outer academy district", "relic mines"],
        "travel_rules": ["outer district requires academy pass"],
    }


def test_world_state_snapshot_service_creates_and_fetches_snapshot(tmp_path):
    service = WorldStateSnapshotService(root=tmp_path / "world_snapshots")

    result = service.create_snapshot(
        world_id="world_velmora",
        world_state=sample_world(),
        project_id="proj_ashen",
        universe_id="velmora",
    )

    fetched = service.get_snapshot(result["snapshot_id"])
    listed = service.list_snapshots(world_id="world_velmora")

    assert result["success"] is True
    assert result["state_hash"]
    assert fetched["world_id"] == "world_velmora"
    assert len(listed) == 1


def test_world_rule_conflict_detector_passes_consistent_world():
    engine = WorldRuleConflictDetector()

    result = engine.run({"world_profile": sample_world()})

    assert result.success is True
    assert result.data["world_id"] == "world_velmora"
    assert result.data["simulation_safe"] is True
    assert result.data["world_rule_consistency_score"] >= 0.7
    assert result.data["conflicts"] == []


def test_world_rule_conflict_detector_catches_cost_contradiction():
    engine = WorldRuleConflictDetector()

    world = sample_world()
    world["magic_rules"] = [
        "relic power requires cost",
        "relic power has no cost for academy elites",
    ]

    result = engine.run({"world_profile": world})

    assert result.success is True
    assert result.data["simulation_safe"] is False
    assert result.data["conflicts"]


def test_world_location_access_engine_exports_locations_access_and_witness_rules():
    engine = WorldLocationAccessEngine()

    result = engine.run(
        {
            "world_profile": sample_world(),
            "project_id": "proj_ashen",
            "universe_id": "velmora",
        }
    )

    data = result.data

    assert result.success is True
    assert data["world_id"] == "world_velmora"
    assert data["simulation_ready"] is True
    assert len(data["location_refs"]) == 3
    assert data["access_rules"]
    assert data["witness_possible_rules"]
    assert any(rule["requires_sponsor"] for rule in data["access_rules"])


def test_faction_institution_resource_engine_exports_political_constraints():
    engine = FactionInstitutionResourceEngine()

    result = engine.run(
        {
            "world_profile": sample_world(),
            "project_id": "proj_ashen",
            "universe_id": "velmora",
        }
    )

    data = result.data

    assert result.success is True
    assert data["world_id"] == "world_velmora"
    assert data["simulation_ready"] is True
    assert len(data["faction_refs"]) == 2
    assert len(data["institution_refs"]) == 2
    assert len(data["resource_refs"]) >= 2
    assert data["faction_power_sources"][0]["power_sources"]
    assert data["resource_dependencies"][0]["simulation_pressure"]

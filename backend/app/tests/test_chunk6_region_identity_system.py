from backend.app.engines.deep_world.geography_terrain_engine import GeographyTerrainEngine
from backend.app.engines.deep_world.region_identity_system import RegionIdentitySystem


def build_region():
    geo = GeographyTerrainEngine()
    return geo.build_region(
        source_id="identity_geo_source",
        region_seed={
            "name": "Saltroot Forest",
            "dominant_terrain": "memory-preserving salt forest",
            "climate": "silver fog season and dry salt wind",
            "danger": "memory sickness during dense fog",
            "secret": "a buried oath road under the oldest roots",
        },
    )["deep_world_region"]


def test_region_identity_system_builds_identity():
    system = RegionIdentitySystem()
    region = build_region()

    identity = system.build_region_identity(
        source_id="identity_test",
        region=region,
        identity_seed={
            "food_signature": ["salt-bark tea", "fog root stew"],
            "belief_signature": ["fog remembers broken oaths"],
            "architecture_signature": ["bell towers facing old roads"],
        },
    )["region_identity"]

    assert identity["region_name"] == "Saltroot Forest"
    assert "food_signature" in identity
    assert "salt-bark tea" in identity["food_signature"]
    assert "fog remembers broken oaths" in identity["belief_signature"]
    assert identity["story_use"]
    assert identity["character_effect"]
    assert identity["plot_effect"]
    assert identity["memory_effect"]
    assert identity["compression_summary"]


def test_region_identity_system_builds_context_patch():
    system = RegionIdentitySystem()
    region = build_region()
    identity = system.build_region_identity(source_id="identity_patch", region=region)["region_identity"]

    patch = system.build_story_context_patch(identity=identity)["story_context_patch"]

    assert patch["region_id"] == region.element_id
    assert "identity_fingerprint" in patch
    assert "food" in patch["identity_fingerprint"]
    assert "generation_hints" in patch
    assert "memory_update_candidates" in patch


def test_region_identity_system_validates_identity():
    system = RegionIdentitySystem()
    region = build_region()
    identity = system.build_region_identity(source_id="identity_validate", region=region)["region_identity"]

    validation = system.validate_identity(identity=identity)

    assert validation["passed"] is True
    assert validation["blockers"] == []


def test_region_identity_system_detects_missing_identity_fields():
    system = RegionIdentitySystem()
    region = build_region()
    identity = system.build_region_identity(source_id="identity_bad", region=region)["region_identity"]
    identity["food_signature"] = []

    validation = system.validate_identity(identity=identity)

    assert validation["passed"] is False
    assert any("food_signature" in blocker for blocker in validation["blockers"])


def test_region_identity_system_summarizes_and_textualizes():
    system = RegionIdentitySystem()
    region = build_region()
    identity = system.build_region_identity(source_id="identity_text", region=region)["region_identity"]

    summary = system.summarize_identity(identity=identity)
    text = system.build_identity_text(identity=identity)["identity_text"]

    assert summary["success"] is True
    assert summary["summary"]["identity_id"] == identity["identity_id"]
    assert "Deep World Region Identity" in text
    assert "Character Effect" in text
    assert "Memory Effect" in text

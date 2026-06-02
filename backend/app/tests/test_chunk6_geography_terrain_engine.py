from backend.app.engines.deep_world.geography_terrain_engine import GeographyTerrainEngine
from backend.app.schemas.deep_world import DeepWorldRegion, DeepWorldValidationStatus


def test_geography_engine_builds_region():
    engine = GeographyTerrainEngine()

    region = engine.build_region(
        source_id="geo_test",
        region_seed={
            "name": "Ashglass Coast",
            "dominant_terrain": "black glass cliffs and ash beaches",
            "climate": "salt storms and red dawn fog",
            "danger": "glass cuts carried by storm wind",
            "secret": "a drowned stairway visible only at red tide",
            "settlement_logic": "ports survive behind glass windbreak walls",
            "plot_pressure": "red tide decides whether the hidden stairway can be reached",
            "tags": ["coast", "secret_route"],
        },
        story_context={"genre": "fantasy", "tone": "mythic"},
    )["deep_world_region"]

    assert isinstance(region, DeepWorldRegion)
    assert region.name == "Ashglass Coast"
    assert region.validation_status == DeepWorldValidationStatus.VALIDATED
    assert "black glass cliffs" in region.terrain_signature[0]
    assert "red tide" in region.secret_signature[0]
    assert "story_useful_region" in region.tags
    assert "fantasy" in region.tags


def test_geography_region_has_required_story_contract_fields():
    engine = GeographyTerrainEngine()
    region = engine.build_region(source_id="geo_contract_test")["deep_world_region"]

    assert region.story_use
    assert region.character_effect
    assert region.plot_effect
    assert region.memory_effect
    assert region.provenance["generated_by_engine"] == "GeographyTerrainEngine"
    assert region.compression_summary


def test_geography_engine_builds_story_context_patch():
    engine = GeographyTerrainEngine()
    region = engine.build_region(source_id="geo_patch_test")["deep_world_region"]

    patch = engine.build_region_context_patch(region=region)["story_context_patch"]

    assert patch["deep_world_region_id"] == region.element_id
    assert "generation_hints" in patch
    assert "memory_update_candidates" in patch
    assert any("terrain" in hint.lower() for hint in patch["generation_hints"])


def test_geography_engine_validates_region():
    engine = GeographyTerrainEngine()
    region = engine.build_region(source_id="geo_validate_test")["deep_world_region"]

    validation = engine.validate_region(region=region)

    assert validation["passed"] is True
    assert validation["blockers"] == []


def test_geography_engine_summarizes_and_textualizes_region():
    engine = GeographyTerrainEngine()
    region = engine.build_region(source_id="geo_text_test")["deep_world_region"]

    summary = engine.summarize_region(region=region)
    text = engine.build_region_text(region=region)["region_text"]

    assert summary["success"] is True
    assert summary["summary"]["region_id"] == region.element_id
    assert "Deep World Geography Region" in text
    assert "Terrain Signature" in text
    assert "Memory Effect" in text

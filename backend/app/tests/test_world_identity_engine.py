from backend.app.engines.world.world_identity_engine import WorldIdentityEngine
from backend.app.schemas.foundation import EngineRunResult
from backend.app.schemas.world import (
    WorldDNAProfile,
    WorldIdentity,
    WorldScaleGranularityProfile,
)


def test_world_identity_engine_returns_engine_result():
    engine = WorldIdentityEngine()

    result = engine.run(
        {
            "world_name": "Velmora",
            "seed_premise": (
                "A late imperial collapse world where noble academies control "
                "royal magic and 27 destined people awaken too quickly."
            ),
            "target_format": "seven_novel_series",
            "genre_tags": ["dark_academy", "political_fantasy"],
            "tone_tags": ["epic", "tragic", "intelligent"],
            "desired_complexity": "extreme",
        }
    )

    assert isinstance(result, EngineRunResult)
    assert result.success is True
    assert result.engine_name == "world.identity_engine"
    assert "identity" in result.data
    assert "world_dna" in result.data
    assert "scale_granularity" in result.data


def test_world_identity_engine_builds_deep_identity():
    engine = WorldIdentityEngine()

    result = engine.run(
        {
            "world_name": "Velmora",
            "seed_premise": (
                "An academy empire ruled by noble bloodlines where destined people "
                "threaten the old order."
            ),
            "target_format": "seven_novel_series",
            "genre_tags": ["dark_academy", "political_fantasy"],
            "tone_tags": ["tragic"],
            "desired_complexity": "extreme",
        }
    )

    identity = WorldIdentity.model_validate(result.data["identity"])

    assert identity.world_name == "Velmora"
    assert "Academy" in " ".join(identity.alternate_names)
    assert "destiny" in identity.central_world_question.lower()
    assert identity.world_wound != ""
    assert identity.world_contradiction != ""
    assert identity.reader_promise.startswith("A world where")


def test_world_identity_engine_builds_world_dna():
    engine = WorldIdentityEngine()

    result = engine.run(
        {
            "seed_premise": (
                "A relic-funded empire where 27 destined people destabilize noble academies."
            ),
            "genre_tags": ["dark_academy", "political_fantasy"],
            "tone_tags": ["tragic"],
            "desired_complexity": "god_level",
        }
    )

    dna = WorldDNAProfile.model_validate(result.data["world_dna"])

    assert dna.dominant_conflict_type == "class_vs_destiny"
    assert dna.dominant_social_structure == "noble_academy_hierarchy"
    assert dna.dominant_power_source == "relic_mines_and_oath_artifacts"
    assert dna.uniqueness_axes["world_scale_complexity"] == 0.95
    assert dna.uniqueness_axes["future_training_structure_quality"] == 0.9
    assert dna.rarity_profile.startswith("high-rarity")


def test_world_identity_engine_builds_scale_for_seven_novel_series():
    engine = WorldIdentityEngine()

    result = engine.run(
        {
            "target_format": "seven_novel_series",
            "seed_premise": "A huge academy empire.",
            "genre_tags": ["dark_academy"],
            "desired_complexity": "extreme",
        }
    )

    scale = WorldScaleGranularityProfile.model_validate(result.data["scale_granularity"])

    assert scale.scale_label == "epic_series_scale"
    assert scale.recommended_region_count >= 8
    assert scale.recommended_faction_count >= 12
    assert scale.history_depth == "deep"


def test_world_identity_engine_builds_civilization_simulation_scale():
    engine = WorldIdentityEngine()

    result = engine.run(
        {
            "target_format": "civilization_simulation",
            "seed_premise": "A 1500-player civilization simulation world.",
            "genre_tags": ["civilization"],
            "desired_complexity": "god_level",
        }
    )

    scale = WorldScaleGranularityProfile.model_validate(result.data["scale_granularity"])

    assert scale.scale_label == "civilization_simulation_scale"
    assert scale.recommended_faction_count >= 30
    assert scale.recommended_artifact_count >= 40


def test_world_identity_engine_warns_when_seed_missing():
    engine = WorldIdentityEngine()

    result = engine.run({})

    assert result.success is True
    assert len(result.warnings) == 1
    assert "seed_premise" in result.warnings[0]

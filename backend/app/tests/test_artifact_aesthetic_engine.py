from backend.app.engines.world.artifact_aesthetic_engine import ArtifactAestheticEngine
from backend.app.schemas.foundation import EngineRunResult
from backend.app.schemas.world import AestheticTextureProfile, ArtifactProfile


def test_artifact_aesthetic_engine_returns_engine_result():
    engine = ArtifactAestheticEngine()

    result = engine.run(
        {
            "seed_premise": (
                "A tragic dark academy empire where relics, oath law, destiny seals, "
                "and forbidden exam scrolls shape the world."
            ),
            "genre_tags": ["dark_academy", "political_fantasy"],
            "tone_tags": ["tragic"],
            "desired_complexity": "extreme",
        }
    )

    assert isinstance(result, EngineRunResult)
    assert result.success is True
    assert result.engine_name == "world.artifact_aesthetic_engine"
    assert "artifacts" in result.data
    assert "aesthetic_texture" in result.data
    assert "training_notes" in result.data


def test_artifact_aesthetic_engine_generates_symbolic_artifacts():
    engine = ArtifactAestheticEngine()

    result = engine.run(
        {
            "seed_premise": (
                "A relic academy empire where oath objects, destiny classification, "
                "and forbidden books drive politics."
            ),
            "genre_tags": ["dark_academy", "political_fantasy"],
            "tone_tags": ["tragic"],
            "desired_complexity": "god_level",
        }
    )

    artifacts = [ArtifactProfile.model_validate(item) for item in result.data["artifacts"]]

    assert len(artifacts) >= 10

    names = [artifact.name for artifact in artifacts]

    assert "The Ashen Crown Shard" in names
    assert "The Oath Bell" in names
    assert "The Forbidden Exam Scroll" in names
    assert "The Memory-Stone Core" in names
    assert "The Unclaimed Fate Seal" in names
    assert "The Corrected Future Lens" in names

    for artifact in artifacts:
        assert artifact.name != ""
        assert artifact.artifact_type != ""
        assert artifact.origin != ""
        assert len(artifact.ownership_history) >= 2
        assert artifact.symbolism != ""
        assert artifact.legal_status != ""
        assert artifact.emotional_status != ""
        assert len(artifact.plot_potential) >= 3


def test_artifact_aesthetic_engine_generates_aesthetic_texture():
    engine = ArtifactAestheticEngine()

    result = engine.run(
        {
            "seed_premise": (
                "A tragic relic academy empire built on oath law, sealed archives, and class hierarchy."
            ),
            "genre_tags": ["dark_academy", "political_fantasy"],
            "tone_tags": ["tragic"],
            "desired_complexity": "god_level",
        }
    )

    aesthetic = AestheticTextureProfile.model_validate(result.data["aesthetic_texture"])

    assert len(aesthetic.visual_palette) >= 7
    assert aesthetic.architecture_style != ""
    assert len(aesthetic.soundscape) >= 5
    assert len(aesthetic.smellscape) >= 5
    assert len(aesthetic.food_textures) >= 5
    assert len(aesthetic.clothing_silhouettes) >= 5
    assert len(aesthetic.symbolic_colors) >= 6
    assert aesthetic.elite_visual_style != ""
    assert aesthetic.poor_visual_style != ""
    assert aesthetic.cinematic_identity != ""

    assert "ash white" in aesthetic.visual_palette
    assert any("bell" in item.lower() for item in aesthetic.soundscape)
    assert "class" in aesthetic.cinematic_identity.lower()


def test_artifact_aesthetic_engine_adds_relic_and_destiny_objects_conditionally():
    engine = ArtifactAestheticEngine()

    result = engine.run(
        {
            "seed_premise": "A world where relic debt and destiny classification shape academy politics.",
            "genre_tags": ["dark_academy"],
            "desired_complexity": "extreme",
        }
    )

    artifacts = [ArtifactProfile.model_validate(item) for item in result.data["artifacts"]]
    names = [artifact.name for artifact in artifacts]

    assert "The Memory-Stone Core" in names
    assert "The Unclaimed Fate Seal" in names


def test_artifact_aesthetic_engine_warns_when_seed_missing():
    engine = ArtifactAestheticEngine()

    result = engine.run({})

    assert result.success is True
    assert len(result.warnings) == 1
    assert "seed_premise" in result.warnings[0]

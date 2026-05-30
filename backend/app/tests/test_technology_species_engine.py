from backend.app.engines.world.technology_species_engine import TechnologySpeciesEngine
from backend.app.schemas.foundation import EngineRunResult
from backend.app.schemas.world import SpeciesCreatureProfile, TechnologyMagicScienceProfile


def test_technology_species_engine_returns_engine_result():
    engine = TechnologySpeciesEngine()

    result = engine.run(
        {
            "seed_premise": (
                "A late imperial academy empire where magic, relics, oath law, "
                "destiny research, and dangerous border creatures shape civilization."
            ),
            "genre_tags": ["dark_academy", "political_fantasy"],
            "tone_tags": ["tragic"],
            "desired_complexity": "extreme",
        }
    )

    assert isinstance(result, EngineRunResult)
    assert result.success is True
    assert result.engine_name == "world.technology_species_engine"
    assert "technology_magic_science" in result.data
    assert "species_creatures" in result.data
    assert "training_notes" in result.data


def test_technology_species_engine_generates_technology_magic_science():
    engine = TechnologySpeciesEngine()

    result = engine.run(
        {
            "seed_premise": (
                "A relic magic academy empire where oath systems, forbidden destiny research, "
                "healing, and military technology are controlled by institutions."
            ),
            "genre_tags": ["dark_academy", "political_fantasy"],
            "desired_complexity": "god_level",
        }
    )

    tech = TechnologyMagicScienceProfile.model_validate(
        result.data["technology_magic_science"]
    )

    assert tech.technology_level != ""
    assert tech.magic_development_level != ""
    assert tech.scientific_understanding != ""
    assert len(tech.lost_technology) >= 5
    assert len(tech.forbidden_research) >= 6
    assert tech.medicine_or_healing_level != ""
    assert tech.transportation_level != ""
    assert tech.communication_level != ""
    assert len(tech.innovation_bottlenecks) >= 6
    assert len(tech.military_technology) >= 6

    assert any("destiny" in item.lower() for item in tech.forbidden_research)
    assert any("relic" in item.lower() for item in tech.lost_technology)
    assert any("communication" in item.lower() or "Messages" in tech.communication_level for item in tech.innovation_bottlenecks)


def test_technology_species_engine_generates_species_and_creature_ecology():
    engine = TechnologySpeciesEngine()

    result = engine.run(
        {
            "seed_premise": (
                "A relic fantasy academy empire where oathmarked people, archive-born identities, "
                "sacred animals, and dangerous habitats influence law."
            ),
            "genre_tags": ["dark_academy", "political_fantasy"],
            "tone_tags": ["tragic"],
            "desired_complexity": "god_level",
        }
    )

    species = SpeciesCreatureProfile.model_validate(result.data["species_creatures"])

    assert len(species.sentient_species) >= 2
    assert len(species.non_sentient_creatures) >= 5
    assert len(species.monster_ecology) >= 3
    assert len(species.sacred_animals) >= 3
    assert len(species.domesticated_creatures) >= 4
    assert len(species.species_relations) >= 3
    assert len(species.species_laws) >= 4
    assert len(species.dangerous_habitats) >= 5

    assert any("Oathmarked" in item for item in species.sentient_species)
    assert any("relic" in item.lower() for item in species.monster_ecology)
    assert any("law" in item.lower() or "legal" in item.lower() for item in species.species_relations)


def test_technology_species_engine_handles_non_magic_world():
    engine = TechnologySpeciesEngine()

    result = engine.run(
        {
            "seed_premise": "A political empire with bureaucracy, law, and military roads.",
            "genre_tags": ["political_fantasy"],
            "desired_complexity": "high",
        }
    )

    species = SpeciesCreatureProfile.model_validate(result.data["species_creatures"])
    tech = TechnologyMagicScienceProfile.model_validate(
        result.data["technology_magic_science"]
    )

    assert "No openly dominant magic system" not in tech.magic_development_level
    assert len(species.sentient_species) >= 1
    assert "Humans" in species.sentient_species[0]


def test_technology_species_engine_warns_when_seed_missing():
    engine = TechnologySpeciesEngine()

    result = engine.run({})

    assert result.success is True
    assert len(result.warnings) == 1
    assert "seed_premise" in result.warnings[0]

from backend.app.engines.world.demographics_society_engine import (
    DemographicsSocietyEngine,
)
from backend.app.schemas.foundation import EngineRunResult
from backend.app.schemas.world import DemographicsProfile, SocietyProfile


def test_demographics_society_engine_returns_engine_result():
    engine = DemographicsSocietyEngine()

    result = engine.run(
        {
            "seed_premise": (
                "A late imperial academy empire where noble birth controls education "
                "and 27 destined people destabilize class hierarchy."
            ),
            "genre_tags": ["dark_academy", "political_fantasy"],
            "tone_tags": ["tragic"],
            "desired_complexity": "extreme",
            "target_format": "seven_novel_series",
        }
    )

    assert isinstance(result, EngineRunResult)
    assert result.success is True
    assert result.engine_name == "world.demographics_society_engine"
    assert "demographics" in result.data
    assert "society" in result.data
    assert "training_notes" in result.data


def test_demographics_society_engine_generates_population_logic():
    engine = DemographicsSocietyEngine()

    result = engine.run(
        {
            "seed_premise": (
                "A political academy empire with relic mines, class hierarchy, and destiny classification."
            ),
            "genre_tags": ["dark_academy", "political_fantasy"],
            "desired_complexity": "god_level",
            "target_format": "seven_novel_series",
        }
    )

    demographics = DemographicsProfile.model_validate(result.data["demographics"])

    assert demographics.estimated_population is not None
    assert demographics.estimated_population > 1_000_000
    assert demographics.academy_eligible_population is not None
    assert demographics.academy_eligible_population > 0
    assert len(demographics.urban_rural_split) >= 5
    assert len(demographics.class_distribution) >= 6
    assert len(demographics.age_distribution) >= 4
    assert len(demographics.migration_patterns) >= 4
    assert len(demographics.minority_groups) >= 4
    assert "27" in demographics.destined_person_rarity


def test_demographics_society_engine_generates_class_pyramid():
    engine = DemographicsSocietyEngine()

    result = engine.run(
        {
            "seed_premise": (
                "An academy empire where noble bloodlines control education and commoners seek illegal tutoring."
            ),
            "genre_tags": ["dark_academy", "political_fantasy"],
            "desired_complexity": "extreme",
        }
    )

    society = SocietyProfile.model_validate(result.data["society"])

    assert society.society_summary != ""
    assert len(society.class_tiers) == 6

    tier_names = [tier.name for tier in society.class_tiers]

    assert "S-Class Founder Bloodlines" in tier_names
    assert "E-Class Unregistered, Exiled, Debt-Bound, and Erased People" in tier_names

    s_tier = society.class_tiers[0]
    e_tier = society.class_tiers[-1]

    assert s_tier.rank == 1
    assert e_tier.rank == 6
    assert len(s_tier.privileges) >= 3
    assert len(e_tier.restrictions) >= 3
    assert len(e_tier.mobility_paths) >= 2


def test_demographics_society_engine_generates_social_rules():
    engine = DemographicsSocietyEngine()

    result = engine.run(
        {
            "seed_premise": (
                "A dark academy empire built on oath law, relic mines, noble rank, and destined people."
            ),
            "genre_tags": ["dark_academy", "political_fantasy"],
            "desired_complexity": "god_level",
        }
    )

    society = SocietyProfile.model_validate(result.data["society"])

    assert len(society.birth_privilege_rules) >= 4
    assert len(society.marriage_rules) >= 4
    assert len(society.inheritance_rules) >= 4
    assert len(society.reputation_rules) >= 4
    assert len(society.shame_systems) >= 4
    assert len(society.honor_systems) >= 4
    assert len(society.discrimination_systems) >= 5
    assert "Destined people" in society.destined_person_social_impact


def test_demographics_society_engine_warns_when_seed_missing():
    engine = DemographicsSocietyEngine()

    result = engine.run({})

    assert result.success is True
    assert len(result.warnings) == 1
    assert "seed_premise" in result.warnings[0]

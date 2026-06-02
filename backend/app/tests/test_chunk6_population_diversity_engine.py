from backend.app.engines.deep_world.population_diversity_engine import PopulationDiversityEngine
from backend.app.engines.deep_world.species_people_type_expansion_engine import SpeciesPeopleTypeExpansionEngine


def build_species_and_people_type():
    species_engine = SpeciesPeopleTypeExpansionEngine()
    species = species_engine.build_species_profile(source_id="population_species_source")["species_profile"]
    people_type = species_engine.build_people_type_profile(
        source_id="population_people_type_source",
        species_profile=species,
    )["people_type_profile"]
    return species, people_type


def test_population_diversity_engine_builds_profile():
    species, people_type = build_species_and_people_type()
    engine = PopulationDiversityEngine()

    profile = engine.build_population_diversity_profile(
        source_id="population_test",
        species_profiles=[species],
        people_type_profiles=[people_type],
        population_seed={
            "region_name": "Ashglass Coast",
            "culture": "drowned temple tide culture",
        },
    )["population_diversity_profile"]

    assert profile["region_name"] == "Ashglass Coast"
    assert profile["population_groups"]
    assert profile["class_distribution"]
    assert profile["belief_diversity"]
    assert profile["migration_patterns"]
    assert profile["underrepresented_groups"]
    assert profile["naming_variation_rules"]
    assert profile["species_profile_refs"] == [species["species_profile_id"]]
    assert profile["people_type_profile_refs"] == [people_type["people_type_profile_id"]]
    assert profile["detail_depth_score"] >= 0.75


def test_population_diversity_engine_builds_population_sample():
    species, people_type = build_species_and_people_type()
    engine = PopulationDiversityEngine()
    profile = engine.build_population_diversity_profile(
        source_id="sample_test",
        species_profiles=[species],
        people_type_profiles=[people_type],
    )["population_diversity_profile"]

    sample = engine.build_population_sample(
        source_id="sample_test",
        diversity_profile=profile,
        sample_seed={"sample_size": 6},
    )["population_sample"]

    assert sample["population_diversity_profile_id"] == profile["population_diversity_profile_id"]
    assert sample["sample_size"] == 6
    assert len(sample["generated_population"]) == 6
    assert sample["generated_population"][0]["public_name_pattern"]
    assert sample["story_use"]
    assert sample["character_effect"]
    assert sample["plot_effect"]
    assert sample["memory_effect"]


def test_population_diversity_engine_builds_story_context_patch():
    species, people_type = build_species_and_people_type()
    engine = PopulationDiversityEngine()
    profile = engine.build_population_diversity_profile(
        source_id="patch_test",
        species_profiles=[species],
        people_type_profiles=[people_type],
    )["population_diversity_profile"]
    sample = engine.build_population_sample(source_id="patch_test", diversity_profile=profile)["population_sample"]

    patch = engine.build_story_context_patch(
        diversity_profile=profile,
        population_sample=sample,
    )["story_context_patch"]

    assert patch["population_diversity_profile_id"] == profile["population_diversity_profile_id"]
    assert patch["population_sample"]["population_sample_id"] == sample["population_sample_id"]
    assert "generation_hints" in patch
    assert "memory_update_candidates" in patch
    assert len(patch["memory_update_candidates"]) == 2


def test_population_diversity_engine_validates_profile_and_sample():
    species, people_type = build_species_and_people_type()
    engine = PopulationDiversityEngine()
    profile = engine.build_population_diversity_profile(
        source_id="validate_test",
        species_profiles=[species],
        people_type_profiles=[people_type],
    )["population_diversity_profile"]
    sample = engine.build_population_sample(
        source_id="validate_test",
        diversity_profile=profile,
        sample_seed={"sample_size": 5},
    )["population_sample"]

    profile_validation = engine.validate_population_diversity_profile(diversity_profile=profile)
    sample_validation = engine.validate_population_sample(population_sample=sample)

    assert profile_validation["passed"] is True
    assert profile_validation["missing_fields"] == []
    assert sample_validation["passed"] is True
    assert sample_validation["missing_fields"] == []


def test_population_diversity_engine_detects_bad_records():
    engine = PopulationDiversityEngine()

    profile_validation = engine.validate_population_diversity_profile(
        diversity_profile={
            "population_diversity_profile_id": "bad_population",
            "profile_name": "Generic Population",
            "story_use": "Bad.",
        }
    )

    sample_validation = engine.validate_population_sample(
        population_sample={
            "population_sample_id": "bad_sample",
            "population_diversity_profile_id": "bad_population",
            "sample_size": 3,
            "generated_population": [{"name": "one"}],
            "plot_effect": "Bad.",
        }
    )

    assert profile_validation["passed"] is False
    assert profile_validation["missing_fields"]
    assert "story_use" in profile_validation["shallow_fields"]

    assert sample_validation["passed"] is False
    assert sample_validation["missing_fields"]
    assert sample_validation["count_mismatch"] is True
    assert "plot_effect" in sample_validation["shallow_fields"]


def test_population_diversity_engine_summarizes_and_textualizes():
    species, people_type = build_species_and_people_type()
    engine = PopulationDiversityEngine()
    profile = engine.build_population_diversity_profile(
        source_id="text_test",
        species_profiles=[species],
        people_type_profiles=[people_type],
    )["population_diversity_profile"]
    sample = engine.build_population_sample(source_id="text_test", diversity_profile=profile)["population_sample"]

    summary = engine.summarize_population_diversity(
        diversity_profile=profile,
        population_sample=sample,
    )
    text = engine.build_population_text(
        diversity_profile=profile,
        population_sample=sample,
    )["population_text"]

    assert summary["success"] is True
    assert summary["summary"]["population_diversity_profile_id"] == profile["population_diversity_profile_id"]
    assert "Population Diversity Profile" in text
    assert "Naming Variation Rules" in text
    assert "Memory Effect" in text

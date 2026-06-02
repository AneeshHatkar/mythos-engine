from backend.app.engines.deep_world.species_people_type_expansion_engine import SpeciesPeopleTypeExpansionEngine


def test_species_people_engine_builds_species_profile():
    engine = SpeciesPeopleTypeExpansionEngine()

    species = engine.build_species_profile(
        source_id="species_test",
        species_seed={
            "base_name": "Mirel",
            "unique_name": "Mirel Tideborn Kin",
            "classification": "coastal humanoid people type",
            "region_name": "Ashglass Coast",
            "culture": "drowned temple tide culture",
            "name_meaning": "people named by tide memory",
        },
        story_context={"genre": "fantasy", "tone": "mythic"},
    )["species_profile"]

    assert species["unique_name"] == "Mirel Tideborn Kin"
    assert species["classification"] == "coastal humanoid people type"
    assert species["name_origin"]
    assert species["name_language_logic"]
    assert species["biological_traits"]
    assert species["social_traits"]
    assert species["naming_rules"]
    assert species["taboo_rules"]
    assert species["story_use"]
    assert species["character_effect"]
    assert species["plot_effect"]
    assert species["memory_effect"]
    assert species["detail_depth_score"] >= 0.75


def test_species_people_engine_builds_people_type_profile():
    engine = SpeciesPeopleTypeExpansionEngine()
    species = engine.build_species_profile(source_id="people_type_test")["species_profile"]

    people_type = engine.build_people_type_profile(
        source_id="people_type_test",
        species_profile=species,
        people_type_seed={
            "role_name": "Bell-Road Witness",
            "name_meaning": "one who remembers legal truth on the road",
        },
    )["people_type_profile"]

    assert people_type["species_profile_id"] == species["species_profile_id"]
    assert people_type["species_name"] == species["unique_name"]
    assert people_type["role_name"] == "Bell-Road Witness"
    assert people_type["name_meaning"] == "one who remembers legal truth on the road"
    assert people_type["skill_profile"]
    assert people_type["failure_modes"]
    assert people_type["story_use"]
    assert people_type["character_effect"]
    assert people_type["plot_effect"]
    assert people_type["memory_effect"]


def test_species_people_engine_builds_story_context_patch():
    engine = SpeciesPeopleTypeExpansionEngine()
    species = engine.build_species_profile(source_id="patch_test")["species_profile"]
    people_type = engine.build_people_type_profile(
        source_id="patch_test",
        species_profile=species,
    )["people_type_profile"]

    patch = engine.build_story_context_patch(
        species_profile=species,
        people_type_profile=people_type,
    )["story_context_patch"]

    assert patch["species_profile_id"] == species["species_profile_id"]
    assert patch["people_type_profile"]["people_type_profile_id"] == people_type["people_type_profile_id"]
    assert "generation_hints" in patch
    assert "memory_update_candidates" in patch
    assert len(patch["memory_update_candidates"]) == 2


def test_species_people_engine_validates_species_and_people_type():
    engine = SpeciesPeopleTypeExpansionEngine()
    species = engine.build_species_profile(source_id="validate_test")["species_profile"]
    people_type = engine.build_people_type_profile(
        source_id="validate_test",
        species_profile=species,
    )["people_type_profile"]

    species_validation = engine.validate_species_profile(species_profile=species)
    people_validation = engine.validate_people_type_profile(people_type_profile=people_type)

    assert species_validation["passed"] is True
    assert species_validation["missing_fields"] == []
    assert people_validation["passed"] is True
    assert people_validation["missing_fields"] == []


def test_species_people_engine_detects_bad_profiles():
    engine = SpeciesPeopleTypeExpansionEngine()

    species_validation = engine.validate_species_profile(
        species_profile={
            "species_profile_id": "bad_species",
            "unique_name": "Generic People",
            "story_use": "Bad.",
        }
    )

    people_validation = engine.validate_people_type_profile(
        people_type_profile={
            "people_type_profile_id": "bad_people_type",
            "unique_name": "Generic Role",
            "plot_effect": "Bad.",
        }
    )

    assert species_validation["passed"] is False
    assert species_validation["missing_fields"]
    assert "story_use" in species_validation["shallow_fields"]

    assert people_validation["passed"] is False
    assert people_validation["missing_fields"]
    assert "plot_effect" in people_validation["shallow_fields"]


def test_species_people_engine_summarizes_and_textualizes():
    engine = SpeciesPeopleTypeExpansionEngine()
    species = engine.build_species_profile(source_id="text_test")["species_profile"]
    people_type = engine.build_people_type_profile(
        source_id="text_test",
        species_profile=species,
    )["people_type_profile"]

    summary = engine.summarize_species_and_people_type(
        species_profile=species,
        people_type_profile=people_type,
    )

    text = engine.build_species_people_text(
        species_profile=species,
        people_type_profile=people_type,
    )["species_people_text"]

    assert summary["success"] is True
    assert summary["summary"]["species_profile_id"] == species["species_profile_id"]
    assert summary["summary"]["people_type_profile_id"] == people_type["people_type_profile_id"]
    assert "Species + People Type Expansion Profile" in text
    assert "Naming Rules" in text
    assert "Memory Effect" in text

from backend.app.schemas.story_dna import EmotionalResonanceSeed, StoryDNASeed
from backend.app.services.character_contrast_matrix_service import CharacterContrastMatrixService
from backend.app.services.emotional_resonance_seed_service import EmotionalResonanceSeedService
from backend.app.services.story_dna_seed_service import StoryDNASeedService
from backend.app.services.world_character_pressure_matrix_service import WorldCharacterPressureMatrixService


def sample_world():
    return {
        "world_id": "world_velmora",
        "world_name": "Velmora",
        "genre_tags": ["academy", "romance", "political_intrigue"],
        "legal_constraints": ["distrusted family names require sponsor to testify"],
        "factions": ["Oath Court", "Relic Guild"],
        "economy": ["relic labor", "debt contracts"],
        "culture": ["public names carry legal trust"],
        "magic_rules": ["relic power requires cost and counterplay"],
    }


def char_kael():
    return {
        "character_id": "char_kael",
        "identity": {"character_id": "char_kael", "name": "Kael"},
        "origin": {"social_class": "academy_sponsored", "family_name_status": "distrusted"},
        "psychology": {
            "psychology_profile": {"core_wound": "believes belonging can be revoked after public failure"},
            "goal_profile": {
                "surface_goal": "survive academy ranking",
                "hidden_goal": "prove the ranking system is edited",
            },
        },
        "power": {"skill_ontology": {"skill_family": "cognitive_inference"}},
        "dialogue": {"dialogue_voice_profile": {"voice_family": "controlled_subtext_voice"}},
        "relationships": {"relationship_readiness_profile": {"relationship_readiness_family": "high_loyalty_power_broker_readiness"}},
        "symbolic_role": "erased truth seeker",
        "public_mask": "precise and composed",
        "private_truth": "terrified of being unreal",
    }


def char_seren():
    return {
        "character_id": "char_seren",
        "identity": {"character_id": "char_seren", "name": "Seren"},
        "origin": {"social_class": "old_nobility", "family_name_status": "trusted"},
        "psychology": {
            "psychology_profile": {"core_wound": "believes love becomes dangerous when witnessed"},
            "goal_profile": {
                "surface_goal": "protect family position",
                "hidden_goal": "free herself from inherited loyalty",
            },
        },
        "power": {"skill_ontology": {"skill_family": "oath_magic"}},
        "dialogue": {"dialogue_voice_profile": {"voice_family": "ceremonial_restraint_voice"}},
        "relationships": {"relationship_readiness_profile": {"relationship_readiness_family": "guarded_loyalty_readiness"}},
        "symbolic_role": "witness with divided loyalty",
        "public_mask": "obedient noble composure",
        "private_truth": "wants truth more than safety",
    }


def test_story_dna_seed_service_builds_deep_theme_seed():
    service = StoryDNASeedService()

    result = service.build_story_dna(
        project_id="proj_ashen",
        universe_id="velmora",
        world_profile=sample_world(),
        character_profiles=[char_kael(), char_seren()],
    )

    dna = StoryDNASeed.model_validate(result["story_dna"])

    assert result["success"] is True
    assert dna.project_id == "proj_ashen"
    assert "institutions control" in dna.core_question or "institutional" in dna.moral_argument
    assert dna.recurring_symbol_set
    assert dna.image_system
    assert "identity" in dna.theme_tags
    assert "event thematic pressure" in result["chunk4_usage"]


def test_emotional_resonance_seed_service_builds_reader_emotion_targets():
    story_result = StoryDNASeedService().build_story_dna(
        world_profile=sample_world(),
        character_profiles=[char_kael(), char_seren()],
    )

    result = EmotionalResonanceSeedService().build_resonance_seed(
        story_dna=story_result["story_dna"],
        relationship_mode="rivalry_with_hidden_care",
        target_intensity=0.8,
    )

    seed = EmotionalResonanceSeed.model_validate(result["emotional_resonance_seed"])

    assert result["success"] is True
    assert "intimacy" in seed.desired_reader_emotion
    assert seed.intimacy_vector > 0.0
    assert seed.hope_vector > 0.0
    assert seed.catharsis_condition
    assert "tension curve targets" in result["chunk4_usage"]


def test_character_contrast_matrix_service_detects_non_redundant_ensemble():
    service = CharacterContrastMatrixService()

    result = service.build_contrast_matrix(character_profiles=[char_kael(), char_seren()])

    record = result["contrast_records"][0]

    assert result["success"] is True
    assert result["character_count"] == 2
    assert result["pair_count"] == 1
    assert record["character_a_id"] == "char_kael"
    assert record["character_b_id"] == "char_seren"
    assert record["contrast_score"] > 0.4
    assert record["redundancy_warning"] is False
    assert result["ensemble_ready"] is True


def test_world_character_pressure_matrix_service_builds_pressure_records():
    service = WorldCharacterPressureMatrixService()

    result = service.build_pressure_matrix(
        world_profile=sample_world(),
        character_profiles=[char_kael(), char_seren()],
    )

    kael_record = result["pressure_records"][0]

    assert result["success"] is True
    assert result["world_id"] == "world_velmora"
    assert result["character_count"] == 2
    assert result["simulation_ready"] is True
    assert kael_record["character_id"] == "char_kael"
    assert kael_record["law_pressure"]
    assert kael_record["class_pressure"]
    assert kael_record["power_pressure"]
    assert "public humiliation" in kael_record["simulation_event_fuel"]


def test_story_depth_layers_interconnect_for_chunk4():
    dna = StoryDNASeedService().build_story_dna(
        world_profile=sample_world(),
        character_profiles=[char_kael(), char_seren()],
    )
    resonance = EmotionalResonanceSeedService().build_resonance_seed(
        story_dna=dna["story_dna"],
        relationship_mode="rivalry_with_hidden_care",
    )
    contrast = CharacterContrastMatrixService().build_contrast_matrix(
        character_profiles=[char_kael(), char_seren()]
    )
    pressure = WorldCharacterPressureMatrixService().build_pressure_matrix(
        world_profile=sample_world(),
        character_profiles=[char_kael(), char_seren()],
    )

    assert dna["success"] is True
    assert resonance["success"] is True
    assert contrast["ensemble_ready"] is True
    assert pressure["simulation_ready"] is True

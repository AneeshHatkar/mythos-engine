from backend.app.engines.character.character_type_ontology_engine import CharacterTypeOntologyEngine
from backend.app.schemas.foundation import EngineRunResult
from backend.app.schemas.learning import EngineLearningMetadata, LearnedOntologyRecord


def sample_seed():
    return {
        "character_id": "char_kael",
        "name": "Kael Veyran",
        "role": "protagonist",
        "people_type": "Hidden Kingmaker",
        "type_description": "A low-visible academy student with hidden influence who redirects power flow through strategy and pattern recognition.",
        "social_class": "academy_sponsored",
        "family_name_status": "distrusted",
        "destiny_type": "hidden_kingmaker",
        "adaptability_type": "earned_breakthrough",
        "breakthrough_condition": "protects someone weaker from public punishment",
    }


def sample_people_type():
    return {
        "people_type_id": "ptype_hidden_kingmaker",
        "name": "Hidden Kingmaker",
        "description": "A low visible figure whose choices redirect who can gain power.",
        "compatible_roles": ["protagonist", "catalyst"],
    }


def sample_skill_ontology():
    return {
        "skill_family": "cognitive_inference",
        "skill_subtype": "pattern_detection",
        "power_scale": "rare_human_plus",
        "adaptability_compatibility": 0.72,
        "destiny_compatibility": 0.68,
    }


def sample_goal():
    return {
        "character_id": "char_kael",
        "surface_goal": "understand why destiny has marked them",
        "agency_score": 0.74,
    }


def sample_reputation():
    return {
        "character_id": "char_kael",
        "exposure_risk": 0.72,
        "enemy_threat_reputation": 0.58,
    }


def test_character_type_ontology_engine_returns_engine_result():
    engine = CharacterTypeOntologyEngine()

    result = engine.run(
        {
            "character_seed": sample_seed(),
            "people_type": sample_people_type(),
            "skill_ontology": sample_skill_ontology(),
            "goal_profile": sample_goal(),
            "reputation_profile": sample_reputation(),
            "source_mode": "human_approved_synthetic",
            "user_rating": 9,
        }
    )

    assert isinstance(result, EngineRunResult)
    assert result.success is True
    assert result.engine_name == "character.character_type_ontology_engine"
    assert "character_type_ontology" in result.data
    assert "ontology_record" in result.data
    assert "learned_type_candidate" in result.data
    assert "learning_metadata" in result.data
    assert "next_engine_payload" in result.data


def test_character_type_ontology_classifies_hidden_kingmaker():
    engine = CharacterTypeOntologyEngine()

    result = engine.run(
        {
            "character_seed": sample_seed(),
            "people_type": sample_people_type(),
            "skill_ontology": sample_skill_ontology(),
            "goal_profile": sample_goal(),
            "reputation_profile": sample_reputation(),
            "source_mode": "human_approved_synthetic",
            "user_rating": 9,
        }
    )

    ontology = result.data["character_type_ontology"]

    assert ontology["type_name"] == "Hidden Kingmaker"
    assert ontology["type_family"] == "power_redirector"
    assert ontology["type_subtype"] == "hidden_kingmaker"
    assert "power_redirector" in ontology["role_function"]
    assert ontology["social_position"] == "low_visible_status_high_hidden_influence"
    assert ontology["power_access"] == "indirect_systemic_influence"
    assert ontology["psychological_pattern"] == "unseen_worth_and_controlled_visibility"
    assert ontology["plot_function"] == "redirects_power_flow_and_changes_who_can_win"
    assert ontology["adaptability_potential"] >= 0.7
    assert ontology["destiny_relevance"] >= 0.6


def test_character_type_ontology_outputs_learning_schema_records():
    engine = CharacterTypeOntologyEngine()

    result = engine.run(
        {
            "character_seed": sample_seed(),
            "people_type": sample_people_type(),
            "skill_ontology": sample_skill_ontology(),
            "goal_profile": sample_goal(),
            "source_mode": "human_approved_synthetic",
            "user_rating": 9,
        }
    )

    ontology_record = LearnedOntologyRecord.model_validate(result.data["ontology_record"])
    learning_metadata = EngineLearningMetadata.model_validate(result.data["learning_metadata"])

    assert ontology_record.ontology_type == "people_type"
    assert ontology_record.family == "power_redirector"
    assert ontology_record.subtype == "hidden_kingmaker"
    assert ontology_record.generated_by_engine == "character.character_type_ontology_engine"

    assert learning_metadata.engine_name == "character.character_type_ontology_engine"
    assert learning_metadata.target_object_id == "char_kael"
    assert learning_metadata.generated_training_labels["type_family"] == "power_redirector"
    assert learning_metadata.training_eligibility.training_eligible is True
    assert learning_metadata.training_eligibility.do_not_train is False


def test_character_type_ontology_classifies_failed_prodigy_rival():
    engine = CharacterTypeOntologyEngine()

    result = engine.run(
        {
            "character_seed": {
                "character_id": "char_riven",
                "name": "Riven Sol",
                "role": "rival",
                "people_type": "Failed Prodigy Rival",
                "type_description": "A failed prodigy rival whose rank collapse creates comparison pressure and respect hunger.",
                "social_class": "academy_sponsored",
            },
            "source_mode": "human_approved_synthetic",
            "user_rating": 9,
        }
    )

    ontology = result.data["character_type_ontology"]

    assert ontology["type_family"] == "status_fall_character"
    assert ontology["type_subtype"] == "failed_prodigy"
    assert ontology["psychological_pattern"] == "worth_bound_to_performance"
    assert ontology["relationship_function"] == "rivalry_to_respect_or_obsession"
    assert ontology["compatibility_axes"]["rivalry_compatibility"] >= 0.7


def test_character_type_ontology_classifies_villain_as_oppositional_force():
    engine = CharacterTypeOntologyEngine()

    result = engine.run(
        {
            "character_seed": {
                "character_id": "char_oren",
                "name": "Magister Oren Vaul",
                "role": "villain",
                "people_type": "Institutional Villain",
                "type_description": "An ideological antagonist who embodies oath courts, legal hierarchy, and fear of chaos.",
                "social_class": "old_nobility",
            },
            "moral_profile": {
                "dominant_moral_value": "order",
                "corruption_risk": 0.72,
            },
            "source_mode": "human_approved_synthetic",
            "user_rating": 9,
        }
    )

    ontology = result.data["character_type_ontology"]

    assert ontology["type_family"] == "oppositional_force"
    assert ontology["type_subtype"] == "ideological_antagonist"
    assert "opposer" in ontology["role_function"]
    assert ontology["moral_tendency"] == "order_control_or_corruption_prone"
    assert ontology["relationship_function"] == "moral_pressure_and_antagonistic_mirror"
    assert ontology["threat_level"] in {"meaningful_threat", "severe_threat"}


def test_character_type_ontology_classifies_false_saint_and_memory_eating_type():
    engine = CharacterTypeOntologyEngine()

    false_saint = engine.run(
        {
            "character_seed": {
                "character_id": "char_saint",
                "people_type": "False Saint",
                "type_description": "A false saint whose public purity hides private contradiction.",
            },
            "source_mode": "human_approved_synthetic",
            "user_rating": 9,
        }
    )

    memory_eater = engine.run(
        {
            "character_seed": {
                "character_id": "char_mem",
                "people_type": "Memory-Eating Saint",
                "type_description": "A sacred figure who heals by eating memory and risks identity erasure.",
            },
            "source_mode": "human_approved_synthetic",
            "user_rating": 9,
        }
    )

    assert false_saint.data["character_type_ontology"]["type_family"] == "sacred_status_contradiction"
    assert false_saint.data["character_type_ontology"]["type_subtype"] == "false_saint"

    assert memory_eater.data["character_type_ontology"]["type_family"] == "identity_erasure_character"
    assert memory_eater.data["character_type_ontology"]["type_subtype"] == "memory_consuming_figure"


def test_character_type_ontology_has_anti_cliche_and_generation_constraints():
    engine = CharacterTypeOntologyEngine()

    result = engine.run(
        {
            "character_seed": sample_seed(),
            "people_type": sample_people_type(),
            "skill_ontology": sample_skill_ontology(),
            "source_mode": "human_approved_synthetic",
            "user_rating": 9,
        }
    )

    ontology = result.data["character_type_ontology"]

    assert "must include agency beyond trope label" in ontology["anti_cliche_patterns"]
    assert "kingmaker influence must create consequence and vulnerability" in ontology["anti_cliche_patterns"]
    assert any("must respect type family" in item for item in ontology["generation_constraints"])
    assert any("must support role function" in item for item in ontology["generation_constraints"])


def test_character_type_ontology_is_conservative_when_source_not_approved():
    engine = CharacterTypeOntologyEngine()

    result = engine.run(
        {
            "character_seed": sample_seed(),
            "people_type": sample_people_type(),
            "source_mode": "unknown_web_text",
            "user_rating": 9,
        }
    )

    metadata = result.data["learning_metadata"]

    assert metadata["training_eligibility"]["training_eligible"] is False
    assert metadata["training_eligibility"]["do_not_train"] is True
    assert "source mode is not approved for training" in metadata["training_eligibility"]["rejection_reasons"]


def test_character_type_ontology_builds_next_payloads_for_future_engines():
    engine = CharacterTypeOntologyEngine()

    result = engine.run(
        {
            "character_seed": sample_seed(),
            "people_type": sample_people_type(),
            "skill_ontology": sample_skill_ontology(),
            "source_mode": "human_approved_synthetic",
            "user_rating": 9,
        }
    )

    payload = result.data["next_engine_payload"]

    assert "character_seed" in payload
    assert "adaptability_engine_payload" in payload
    assert "destiny_engine_payload" in payload
    assert "relationship_readiness_payload" in payload
    assert "chunk8_training_payload_later" in payload
    assert payload["character_seed"]["character_type_ontology"]["type_family"] == "power_redirector"


def test_character_type_ontology_warns_without_context():
    engine = CharacterTypeOntologyEngine()

    result = engine.run({})

    assert result.success is True
    assert len(result.warnings) == 1
    assert "character_seed or people_type" in result.warnings[0]
    assert result.data["character_type_ontology"]["type_name"] == "Unresolved Character Type"

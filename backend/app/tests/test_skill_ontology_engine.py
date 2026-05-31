from backend.app.engines.character.skill_ontology_engine import SkillOntologyEngine
from backend.app.schemas.foundation import EngineRunResult
from backend.app.schemas.learning import EngineLearningMetadata, LearnedOntologyRecord


def sample_seed():
    return {
        "character_id": "char_kael",
        "name": "Kael Veyran",
        "role": "protagonist",
        "primary_skill": "Pattern Reading",
        "skill_description": "Reads hidden institutional, social, and behavioral patterns before others can prove them.",
        "skill_rank": "S",
        "skill_rarity": "rare",
        "skill_cost": "mental fatigue and emotional exposure",
        "destiny_type": "hidden_kingmaker",
        "adaptability_type": "earned_breakthrough",
        "breakthrough_condition": "protects someone weaker from public punishment",
        "adaptation_cost": "burns safe anonymity",
    }


def sample_skill_profile():
    return {
        "character_id": "char_kael",
        "primary_skill": "Pattern Reading",
        "skill_domain": "cognitive",
        "skill_rank": "S",
        "skill_rarity": "rare",
        "narrative_function": "lets the character see hidden systems before others believe them",
        "world_legality": "legal_but_suspicious",
        "social_visibility": "visible_if_demonstrated",
    }


def sample_power_limits():
    return {
        "costs": ["emotional exhaustion", "decision fatigue and social isolation"],
        "limitations": ["fails when emotionally attached or deliberately misinformed"],
        "cannot_do": ["cannot read completely hidden information without evidence"],
    }


def test_skill_ontology_engine_returns_engine_result():
    engine = SkillOntologyEngine()

    result = engine.run(
        {
            "character_seed": sample_seed(),
            "skill_profile": sample_skill_profile(),
            "power_limits": sample_power_limits(),
            "source_mode": "human_approved_synthetic",
            "user_rating": 9,
        }
    )

    assert isinstance(result, EngineRunResult)
    assert result.success is True
    assert result.engine_name == "character.skill_ontology_engine"
    assert "skill_ontology" in result.data
    assert "ontology_record" in result.data
    assert "learned_type_candidate" in result.data
    assert "learning_metadata" in result.data
    assert "next_engine_payload" in result.data


def test_skill_ontology_engine_classifies_pattern_reading_as_cognitive_inference():
    engine = SkillOntologyEngine()

    result = engine.run(
        {
            "character_seed": sample_seed(),
            "skill_profile": sample_skill_profile(),
            "power_limits": sample_power_limits(),
            "source_mode": "human_approved_synthetic",
            "user_rating": 9,
        }
    )

    ontology = result.data["skill_ontology"]

    assert ontology["skill_name"] == "Pattern Reading"
    assert ontology["skill_family"] == "cognitive_inference"
    assert ontology["skill_subtype"] == "pattern_detection"
    assert ontology["activation_model"] == "passive_focus"
    assert ontology["growth_model"] == "precision_refinement"
    assert "mental_fatigue" in ontology["cost_family"]
    assert "false_signal" in ontology["counter_family"]
    assert ontology["adaptability_compatibility"] >= 0.6
    assert ontology["destiny_compatibility"] >= 0.6


def test_skill_ontology_engine_outputs_learning_schema_records():
    engine = SkillOntologyEngine()

    result = engine.run(
        {
            "character_seed": sample_seed(),
            "skill_profile": sample_skill_profile(),
            "power_limits": sample_power_limits(),
            "source_mode": "human_approved_synthetic",
            "user_rating": 9,
        }
    )

    ontology_record = LearnedOntologyRecord.model_validate(result.data["ontology_record"])
    learning_metadata = EngineLearningMetadata.model_validate(result.data["learning_metadata"])

    assert ontology_record.ontology_type == "skill"
    assert ontology_record.family == "cognitive_inference"
    assert ontology_record.subtype == "pattern_detection"
    assert ontology_record.generated_by_engine == "character.skill_ontology_engine"
    assert ontology_record.learned_from_data is False

    assert learning_metadata.engine_name == "character.skill_ontology_engine"
    assert learning_metadata.target_object_id == "char_kael"
    assert learning_metadata.generated_training_labels["skill_family"] == "cognitive_inference"
    assert learning_metadata.training_eligibility.training_eligible is True
    assert learning_metadata.training_eligibility.do_not_train is False


def test_skill_ontology_engine_classifies_adaptive_anomaly_skill():
    engine = SkillOntologyEngine()

    result = engine.run(
        {
            "character_seed": {
                "character_id": "char_ilyen",
                "primary_skill": "Pressure Adaptation",
                "skill_description": "Exceeds limits only when someone weaker will be erased unless the character breaks through.",
                "skill_rank": "SS",
                "skill_rarity": "anomaly",
                "adaptability_type": "limit_break_anomaly",
                "breakthrough_condition": "someone weaker will be erased unless they exceed a limit",
                "adaptation_cost": "identity instability after breakthrough",
            },
            "skill_profile": {
                "character_id": "char_ilyen",
                "primary_skill": "Pressure Adaptation",
                "skill_domain": "adaptive",
                "skill_rank": "SS",
                "skill_rarity": "anomaly",
            },
            "source_mode": "human_approved_synthetic",
            "user_rating": 9,
        }
    )

    ontology = result.data["skill_ontology"]

    assert ontology["skill_family"] == "adaptive_limit_system"
    assert ontology["skill_subtype"] == "pressure_evolution"
    assert ontology["activation_model"] == "pressure_triggered"
    assert ontology["power_scale"] == "mythic_or_anomalous"
    assert ontology["world_legality_family"] == "unclassified_by_current_law"
    assert ontology["adaptability_compatibility"] >= 0.8
    assert "recovery_window_attack" in ontology["counter_family"]


def test_skill_ontology_engine_classifies_elemental_authority_skill():
    engine = SkillOntologyEngine()

    result = engine.run(
        {
            "character_seed": {
                "character_id": "char_flame",
                "primary_skill": "Flame Monarch Authority",
                "skill_description": "Commands flame as area control and command aura with stamina and visibility cost.",
                "skill_rank": "SS",
                "skill_rarity": "mythic",
            },
            "source_mode": "human_approved_synthetic",
            "user_rating": 9,
        }
    )

    ontology = result.data["skill_ontology"]

    assert ontology["skill_family"] == "elemental_authority"
    assert ontology["skill_subtype"] == "element_control"
    assert ontology["power_scale"] == "mythic_or_anomalous"
    assert "opposing_element" in ontology["counter_family"]
    assert "stamina_drain" in ontology["cost_family"]
    assert ontology["visibility_model"] == "impossible_to_hide_after_major_use"


def test_skill_ontology_engine_classifies_dream_thread_cartography_as_psychic_mapping():
    engine = SkillOntologyEngine()

    result = engine.run(
        {
            "character_seed": {
                "character_id": "char_dream",
                "primary_skill": "Dream Thread Cartography",
                "skill_description": "Maps dreams, memory symbols, and hidden routes through sleeping minds.",
                "skill_rank": "A",
                "skill_rarity": "rare",
            },
            "source_mode": "human_approved_synthetic",
            "user_rating": 9,
        }
    )

    ontology = result.data["skill_ontology"]

    assert ontology["skill_family"] == "psychic_cognitive_mapping"
    assert ontology["skill_subtype"] == "symbolic_navigation"
    assert "symbol_corruption" in ontology["counter_family"]
    assert ontology["growth_model"] == "symbolic_accuracy_and_backlash_control"
    assert "psychic_cognitive_mapping" in ontology["similarity_tags"]


def test_skill_ontology_engine_is_conservative_when_source_not_approved():
    engine = SkillOntologyEngine()

    result = engine.run(
        {
            "character_seed": sample_seed(),
            "skill_profile": sample_skill_profile(),
            "power_limits": sample_power_limits(),
            "source_mode": "unknown_web_text",
            "user_rating": 9,
        }
    )

    metadata = result.data["learning_metadata"]

    assert metadata["training_eligibility"]["training_eligible"] is False
    assert metadata["training_eligibility"]["do_not_train"] is True
    assert "source mode is not approved for training" in metadata["training_eligibility"]["rejection_reasons"]


def test_skill_ontology_engine_builds_next_payloads_for_future_engines():
    engine = SkillOntologyEngine()

    result = engine.run(
        {
            "character_seed": sample_seed(),
            "skill_profile": sample_skill_profile(),
            "power_limits": sample_power_limits(),
            "source_mode": "human_approved_synthetic",
            "user_rating": 9,
        }
    )

    payload = result.data["next_engine_payload"]

    assert "character_seed" in payload
    assert "adaptability_engine_payload" in payload
    assert "destiny_engine_payload" in payload
    assert "character_type_ontology_payload" in payload
    assert "chunk8_training_payload_later" in payload
    assert payload["character_seed"]["skill_ontology"]["skill_family"] == "cognitive_inference"


def test_skill_ontology_engine_warns_without_context():
    engine = SkillOntologyEngine()

    result = engine.run({})

    assert result.success is True
    assert len(result.warnings) == 1
    assert "character_seed or skill_profile" in result.warnings[0]
    assert result.data["skill_ontology"]["skill_name"] == "Adaptive Observation"

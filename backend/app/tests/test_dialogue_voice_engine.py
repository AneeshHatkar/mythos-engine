from backend.app.engines.character.dialogue_voice_engine import DialogueVoiceEngine
from backend.app.schemas.foundation import EngineRunResult
from backend.app.schemas.learning import EngineLearningMetadata, LearnedOntologyRecord


def sample_seed():
    return {
        "character_id": "char_kael",
        "name": "Kael Veyran",
        "role": "protagonist",
        "social_class": "academy_sponsored",
        "family_name_status": "distrusted",
        "destiny_type": "hidden_kingmaker",
    }


def sample_psychology():
    return {
        "character_id": "char_kael",
        "core_wound": "believes belonging can be revoked at any public failure",
        "core_fear": "belonging being revoked after one visible failure",
        "shame_trigger": "being treated as useful but replaceable",
        "healing_condition": "someone learns the family truth and protects them without using it",
        "betrayal_response": "goes cold, protects family secrets, and remembers exact words",
        "love_response": "tests intimacy through duty, truth, and public pressure",
    }


def sample_origin():
    return {
        "character_id": "char_kael",
        "social_class": "academy_sponsored",
        "family_name_status": "distrusted",
    }


def sample_memory_records():
    return [
        {"memory_id": "mem_core", "content": "public failure memory", "emotional_weight": 0.82},
        {"memory_id": "mem_secret", "content": "family secret memory", "emotional_weight": 0.74},
    ]


def sample_goal():
    return {
        "character_id": "char_kael",
        "hidden_goal": "find proof that the ranking system is edited",
        "true_need": "belonging is not the same as permission",
        "false_need": "worth can be revoked by public failure",
    }


def sample_skill_ontology():
    return {
        "skill_family": "cognitive_inference",
        "skill_subtype": "pattern_detection",
    }


def sample_type_ontology():
    return {
        "type_family": "power_redirector",
        "type_subtype": "hidden_kingmaker",
    }


def sample_destiny():
    return {
        "destiny_family": "power_flow_destiny",
        "destiny_burdens": ["others may treat the character as a means to power"],
    }


def sample_relationship_readiness():
    return {
        "character_id": "char_kael",
        "relationship_readiness_family": "high_loyalty_power_broker_readiness",
        "attachment_pattern": "guarded_attachment_with_secret_testing",
        "trust_model": "trust_requires_truth_protection_without_weaponization",
        "intimacy_risk": 0.72,
    }


def sample_attachment_conflict():
    return {
        "betrayal_sensitivity": 0.74,
    }


def sample_boundary():
    return {
        "boundary_strength": 0.72,
        "relationship_generation_constraints": ["preserve independent goals"],
    }


def test_dialogue_voice_engine_returns_engine_result():
    engine = DialogueVoiceEngine()

    result = engine.run(
        {
            "character_seed": sample_seed(),
            "psychology_profile": sample_psychology(),
            "origin_profile": sample_origin(),
            "memory_records": sample_memory_records(),
            "goal_profile": sample_goal(),
            "skill_ontology": sample_skill_ontology(),
            "character_type_ontology": sample_type_ontology(),
            "destiny_profile": sample_destiny(),
            "relationship_readiness_profile": sample_relationship_readiness(),
            "attachment_and_conflict_model": sample_attachment_conflict(),
            "boundary_model": sample_boundary(),
            "source_mode": "human_approved_synthetic",
            "user_rating": 9,
        }
    )

    assert isinstance(result, EngineRunResult)
    assert result.success is True
    assert result.engine_name == "character.dialogue_voice_engine"
    assert "dialogue_voice_profile" in result.data
    assert "speech_pattern_model" in result.data
    assert "emotional_dialogue_rules" in result.data
    assert "relationship_dialogue_variants" in result.data
    assert "forbidden_dialogue_patterns" in result.data
    assert "learning_metadata" in result.data


def test_dialogue_voice_engine_builds_controlled_subtext_voice():
    engine = DialogueVoiceEngine()

    result = engine.run(
        {
            "character_seed": sample_seed(),
            "psychology_profile": sample_psychology(),
            "origin_profile": sample_origin(),
            "memory_records": sample_memory_records(),
            "goal_profile": sample_goal(),
            "skill_ontology": sample_skill_ontology(),
            "character_type_ontology": sample_type_ontology(),
            "destiny_profile": sample_destiny(),
            "relationship_readiness_profile": sample_relationship_readiness(),
        }
    )

    profile = result.data["dialogue_voice_profile"]

    assert profile["character_id"] == "char_kael"
    assert profile["dialogue_voice_id"].startswith("dvoice_")
    assert profile["voice_family"] == "controlled_subtext_voice"
    assert profile["voice_subtype"] == "strategic_understatement"
    assert "says less than they know" in profile["core_voice_principle"]
    assert "educated but conditional" in profile["voice_social_root"]
    assert "shame trigger" in profile["voice_wound_root"]
    assert profile["voice_strength"] >= 0.7


def test_dialogue_voice_engine_builds_speech_pattern_model():
    engine = DialogueVoiceEngine()

    result = engine.run(
        {
            "character_seed": sample_seed(),
            "psychology_profile": sample_psychology(),
            "origin_profile": sample_origin(),
            "memory_records": sample_memory_records(),
            "goal_profile": sample_goal(),
            "skill_ontology": sample_skill_ontology(),
            "character_type_ontology": sample_type_ontology(),
            "destiny_profile": sample_destiny(),
            "relationship_readiness_profile": sample_relationship_readiness(),
        }
    )

    speech = result.data["speech_pattern_model"]

    assert speech["speech_pattern_id"].startswith("speech_")
    assert speech["formality_level"] == "educated_controlled"
    assert speech["sentence_rhythm"] == "short_precise_lines_with_held_back_explanations"
    assert speech["subtext_density"] == "high_subtext"
    assert speech["directness_level"] == "indirect_until_moral_threshold"
    assert "archives" in speech["metaphor_source"]
    assert "asks questions that reveal what others missed" == speech["question_style"]


def test_dialogue_voice_engine_builds_emotional_and_relationship_variants():
    engine = DialogueVoiceEngine()

    result = engine.run(
        {
            "character_seed": sample_seed(),
            "psychology_profile": sample_psychology(),
            "origin_profile": sample_origin(),
            "memory_records": sample_memory_records(),
            "goal_profile": sample_goal(),
            "skill_ontology": sample_skill_ontology(),
            "character_type_ontology": sample_type_ontology(),
            "destiny_profile": sample_destiny(),
            "relationship_readiness_profile": sample_relationship_readiness(),
            "attachment_and_conflict_model": sample_attachment_conflict(),
            "boundary_model": sample_boundary(),
        }
    )

    emotional = result.data["emotional_dialogue_rules"]
    relationship = result.data["relationship_dialogue_variants"]

    assert "emotion leaks through precision" in emotional["emotional_leakage_model"]
    assert emotional["anger_voice"] == "cold specificity; fewer words; exact memory of harm"
    assert emotional["betrayal_voice"] == "goes cold, protects family secrets, and remembers exact words"
    assert "practical protection" in emotional["love_voice"]

    assert relationship["friend_voice"] == "practical warmth; more context but still careful"
    assert relationship["romance_voice"] == "softens through specific trust, not generic confession"
    assert relationship["boundary_voice_variant"] == "states boundary directly without overexplaining"


def test_dialogue_voice_engine_builds_destiny_layer_and_forbidden_patterns():
    engine = DialogueVoiceEngine()

    result = engine.run(
        {
            "character_seed": sample_seed(),
            "psychology_profile": sample_psychology(),
            "origin_profile": sample_origin(),
            "memory_records": sample_memory_records(),
            "goal_profile": sample_goal(),
            "skill_ontology": sample_skill_ontology(),
            "character_type_ontology": sample_type_ontology(),
            "destiny_profile": sample_destiny(),
            "relationship_readiness_profile": sample_relationship_readiness(),
            "boundary_model": sample_boundary(),
        }
    )

    destiny_layer = result.data["destiny_dialogue_layer"]
    forbidden = result.data["forbidden_dialogue_patterns"]

    assert "who wants the prophecy to mean power transfer" in destiny_layer["prophecy_response_voice"]
    assert destiny_layer["destiny_forbidden_voice"] == "must not speak as if destiny guarantees victory or ownership of others"
    assert "generic witty banter disconnected from wound" in forbidden["generic_voice_failure_modes"]
    assert "preserve character-specific subtext" in forbidden["dialogue_generation_constraints"]
    assert "preserve independent goals" in forbidden["dialogue_generation_constraints"]


def test_dialogue_voice_engine_outputs_learning_metadata():
    engine = DialogueVoiceEngine()

    result = engine.run(
        {
            "character_seed": sample_seed(),
            "psychology_profile": sample_psychology(),
            "origin_profile": sample_origin(),
            "memory_records": sample_memory_records(),
            "goal_profile": sample_goal(),
            "skill_ontology": sample_skill_ontology(),
            "character_type_ontology": sample_type_ontology(),
            "destiny_profile": sample_destiny(),
            "relationship_readiness_profile": sample_relationship_readiness(),
            "attachment_and_conflict_model": sample_attachment_conflict(),
            "boundary_model": sample_boundary(),
            "source_mode": "human_approved_synthetic",
            "user_rating": 9,
        }
    )

    ontology_record = LearnedOntologyRecord.model_validate(result.data["ontology_record"])
    learning_metadata = EngineLearningMetadata.model_validate(result.data["learning_metadata"])

    assert ontology_record.ontology_type == "dialogue_voice"
    assert ontology_record.family == "controlled_subtext_voice"
    assert ontology_record.generated_by_engine == "character.dialogue_voice_engine"

    assert learning_metadata.engine_name == "character.dialogue_voice_engine"
    assert learning_metadata.target_object_id == "char_kael"
    assert learning_metadata.generated_training_labels["voice_family"] == "controlled_subtext_voice"
    assert learning_metadata.generated_training_labels["dialogue_training_ready"] is True
    assert learning_metadata.training_eligibility.training_eligible is True


def test_dialogue_voice_engine_handles_villain_institutional_voice():
    engine = DialogueVoiceEngine()

    result = engine.run(
        {
            "character_seed": {
                "character_id": "char_oren",
                "name": "Magister Oren Vaul",
                "role": "villain",
                "social_class": "old_nobility",
            },
            "character_type_ontology": {
                "type_family": "oppositional_force",
            },
            "skill_ontology": {
                "skill_family": "institutional_authority",
            },
            "source_mode": "human_approved_synthetic",
            "user_rating": 9,
        }
    )

    profile = result.data["dialogue_voice_profile"]
    speech = result.data["speech_pattern_model"]

    assert profile["voice_family"] == "institutional_authority_voice"
    assert profile["voice_subtype"] == "procedural_threat"
    assert "procedure" in profile["core_voice_principle"]
    assert speech["formality_level"] == "high_formality"
    assert speech["question_style"] == "asks questions as procedural traps"


def test_dialogue_voice_engine_diagnostics_confirm_bible_ready():
    engine = DialogueVoiceEngine()

    result = engine.run(
        {
            "character_seed": sample_seed(),
            "psychology_profile": sample_psychology(),
            "origin_profile": sample_origin(),
            "memory_records": sample_memory_records(),
            "goal_profile": sample_goal(),
            "skill_ontology": sample_skill_ontology(),
            "character_type_ontology": sample_type_ontology(),
            "destiny_profile": sample_destiny(),
            "relationship_readiness_profile": sample_relationship_readiness(),
            "attachment_and_conflict_model": sample_attachment_conflict(),
            "boundary_model": sample_boundary(),
        }
    )

    diagnostics = result.data["dialogue_diagnostics"]

    assert diagnostics["dialogue_voice_completeness_score"] >= 0.9
    assert diagnostics["has_voice_family"] is True
    assert diagnostics["has_speech_pattern"] is True
    assert diagnostics["has_emotional_rules"] is True
    assert diagnostics["has_relationship_variants"] is True
    assert diagnostics["has_destiny_layer"] is True
    assert diagnostics["has_forbidden_patterns"] is True
    assert diagnostics["relationship_voice_ready"] is True
    assert diagnostics["character_bible_ready"] is True
    assert diagnostics["training_ready_schema"] is True


def test_dialogue_voice_engine_builds_next_payloads():
    engine = DialogueVoiceEngine()

    result = engine.run(
        {
            "character_seed": sample_seed(),
            "psychology_profile": sample_psychology(),
            "origin_profile": sample_origin(),
            "memory_records": sample_memory_records(),
            "goal_profile": sample_goal(),
            "skill_ontology": sample_skill_ontology(),
            "character_type_ontology": sample_type_ontology(),
            "destiny_profile": sample_destiny(),
            "relationship_readiness_profile": sample_relationship_readiness(),
            "attachment_and_conflict_model": sample_attachment_conflict(),
            "boundary_model": sample_boundary(),
        }
    )

    payload = result.data["next_engine_payload"]

    assert "character_seed" in payload
    assert "character_validator_payload" in payload
    assert "character_bible_export_payload" in payload
    assert "chunk4_dialogue_simulation_payload_later" in payload
    assert "chunk8_training_payload_later" in payload
    assert payload["character_seed"]["dialogue_voice_profile"]["character_id"] == "char_kael"


def test_dialogue_voice_engine_warns_without_character_seed():
    engine = DialogueVoiceEngine()

    result = engine.run({})

    assert result.success is True
    assert len(result.warnings) == 1
    assert "character_seed" in result.warnings[0]
    assert result.data["dialogue_voice_profile"]["character_id"].startswith("char_")

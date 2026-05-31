from backend.app.engines.character.character_consistency_validator import CharacterConsistencyValidator
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


def sample_origin():
    return {
        "character_id": "char_kael",
        "social_class": "academy_sponsored",
        "family_name_status": "distrusted",
        "education_access": 0.82,
    }


def sample_family():
    return {
        "character_id": "char_kael",
        "family_name_status": "distrusted",
    }


def sample_psychology():
    return {
        "character_id": "char_kael",
        "core_wound": "believes belonging can be revoked after public failure",
        "betrayal_response": "goes cold, protects family secrets, and remembers exact words",
    }


def sample_goal():
    return {
        "character_id": "char_kael",
        "hidden_goal": "find proof that the ranking system is edited",
        "true_need": "belonging is not the same as permission",
        "false_need": "worth can be revoked by public failure",
    }


def sample_moral():
    return {
        "character_id": "char_kael",
        "corruption_risk": 0.43,
        "forbidden_lines": ["will not knowingly sacrifice someone powerless for personal advancement"],
    }


def sample_memories():
    return [
        {
            "memory_id": "mem_public_failure",
            "content": "public failure and family secret memory",
            "emotional_weight": 0.82,
        }
    ]


def sample_skill_ontology():
    return {
        "skill_name": "Pattern Reading",
        "skill_family": "cognitive_inference",
        "cost_family": ["mental_fatigue", "emotional_exposure"],
        "counter_family": ["false_signal", "missing_evidence", "emotional_bias"],
    }


def sample_character_type_ontology():
    return {
        "type_family": "power_redirector",
        "type_subtype": "hidden_kingmaker",
    }


def sample_adaptability():
    return {
        "adaptability_family": "earned_moral_breakthrough",
        "trigger_model": "moral_threshold: protects someone weaker from public punishment",
        "cost_model": {"cost_families": ["mental_fatigue", "burns safe anonymity"]},
    }


def sample_limit_break_rules():
    return {
        "limit_break_allowed": True,
        "hard_prohibitions": ["cannot activate for convenience", "cannot erase prior consequences"],
    }


def sample_destiny():
    return {
        "destiny_family": "power_flow_destiny",
        "destiny_is_absolute": False,
        "destiny_burdens": ["others may treat the character as a means to power"],
    }


def sample_prophecy():
    return {
        "prophecy_requires_choice": True,
    }


def sample_boundary():
    return {
        "relationship_boundaries": [
            "relationship cannot erase independent agency",
            "destiny cannot force love, loyalty, or forgiveness",
        ],
    }


def sample_voice():
    return {
        "character_id": "char_kael",
        "voice_family": "controlled_subtext_voice",
    }


def sample_speech():
    return {
        "sentence_rhythm": "short_precise_lines_with_held_back_explanations",
        "subtext_density": "high_subtext",
    }


def sample_forbidden_dialogue():
    return {
        "generic_voice_failure_modes": ["generic witty banter disconnected from wound"],
    }


def full_payload():
    return {
        "character_seed": sample_seed(),
        "origin_profile": sample_origin(),
        "family_profile": sample_family(),
        "psychology_profile": sample_psychology(),
        "goal_profile": sample_goal(),
        "moral_profile": sample_moral(),
        "memory_records": sample_memories(),
        "skill_ontology": sample_skill_ontology(),
        "character_type_ontology": sample_character_type_ontology(),
        "adaptability_profile": sample_adaptability(),
        "limit_break_rules": sample_limit_break_rules(),
        "destiny_profile": sample_destiny(),
        "prophecy_model": sample_prophecy(),
        "boundary_model": sample_boundary(),
        "dialogue_voice_profile": sample_voice(),
        "speech_pattern_model": sample_speech(),
        "forbidden_dialogue_patterns": sample_forbidden_dialogue(),
        "source_mode": "human_approved_synthetic",
        "user_rating": 9,
    }


def test_consistency_validator_returns_engine_result():
    engine = CharacterConsistencyValidator()

    result = engine.run(full_payload())

    assert isinstance(result, EngineRunResult)
    assert result.success is True
    assert result.engine_name == "character.consistency_validator"
    assert "consistency_report" in result.data
    assert "validation_checks" in result.data
    assert "repair_plan" in result.data
    assert "validator_diagnostics" in result.data
    assert "learning_metadata" in result.data


def test_consistency_validator_passes_strong_complete_profile():
    engine = CharacterConsistencyValidator()

    result = engine.run(full_payload())

    report = result.data["consistency_report"]
    diagnostics = result.data["validator_diagnostics"]

    assert report["character_id"] == "char_kael"
    assert report["overall_consistency_score"] >= 0.9
    assert report["consistency_tier"] == "excellent_consistency"
    assert report["critical_issue_count"] == 0
    assert report["violation_count"] == 0
    assert diagnostics["character_bible_ready"] is True
    assert diagnostics["orchestrator_ready"] is True


def test_consistency_validator_detects_skill_without_cost_or_counterplay():
    engine = CharacterConsistencyValidator()

    payload = full_payload()
    payload["skill_ontology"] = {
        "skill_name": "Unlimited Fate Fire",
        "skill_family": "elemental_authority",
        "cost_family": [],
        "counter_family": [],
    }

    result = engine.run(payload)

    report = result.data["consistency_report"]
    checks = result.data["validation_checks"]
    skill_check = next(check for check in checks if check["check_id"] == "skill_limit_consistency")

    assert skill_check["status"] == "violation"
    assert "skill ontology has no cost family" in skill_check["issues"]
    assert "skill ontology has no counter family" in skill_check["issues"]
    assert report["violation_count"] >= 1
    assert result.data["validator_diagnostics"]["character_bible_ready"] is False


def test_consistency_validator_detects_limit_break_without_prohibitions():
    engine = CharacterConsistencyValidator()

    payload = full_payload()
    payload["limit_break_rules"] = {
        "limit_break_allowed": True,
        "hard_prohibitions": [],
    }

    result = engine.run(payload)

    checks = result.data["validation_checks"]
    adaptation_check = next(check for check in checks if check["check_id"] == "adaptability_consistency")

    assert adaptation_check["status"] == "violation"
    assert "limit-break allowed without hard prohibitions" in adaptation_check["issues"]
    assert "add hard_prohibitions so power is not unlimited" in adaptation_check["recommended_fixes"]


def test_consistency_validator_detects_destiny_that_removes_choice():
    engine = CharacterConsistencyValidator()

    payload = full_payload()
    payload["prophecy_model"] = {
        "prophecy_requires_choice": False,
    }

    result = engine.run(payload)

    checks = result.data["validation_checks"]
    destiny_check = next(check for check in checks if check["check_id"] == "destiny_agency_consistency")

    assert destiny_check["status"] == "violation"
    assert "prophecy removes choice" in destiny_check["issues"]
    assert "make prophecy pressure-based or add multiple valid interpretations" in destiny_check["recommended_fixes"]


def test_consistency_validator_detects_missing_relationship_boundary():
    engine = CharacterConsistencyValidator()

    payload = full_payload()
    payload["boundary_model"] = {
        "relationship_boundaries": []
    }

    result = engine.run(payload)

    checks = result.data["validation_checks"]
    boundary_check = next(check for check in checks if check["check_id"] == "relationship_boundary_consistency")

    assert boundary_check["status"] == "violation"
    assert "relationship boundary model has no boundaries" in boundary_check["issues"]


def test_consistency_validator_detects_dialogue_missing_speech_pattern():
    engine = CharacterConsistencyValidator()

    payload = full_payload()
    payload["speech_pattern_model"] = {}

    result = engine.run(payload)

    checks = result.data["validation_checks"]
    dialogue_check = next(check for check in checks if check["check_id"] == "dialogue_voice_consistency")

    assert dialogue_check["status"] == "warning"
    assert "dialogue voice lacks speech pattern model" in dialogue_check["issues"]


def test_consistency_validator_builds_repair_plan_for_failures():
    engine = CharacterConsistencyValidator()

    payload = full_payload()
    payload["skill_ontology"] = {
        "skill_name": "Unlimited Fate Fire",
        "skill_family": "elemental_authority",
        "cost_family": [],
        "counter_family": [],
    }

    result = engine.run(payload)

    repair = result.data["repair_plan"]

    assert repair["requires_repair"] is True
    assert repair["repair_count"] >= 1
    assert any(item["check_id"] == "skill_limit_consistency" for item in repair["ordered_repairs"])
    assert "repair contradictions before export" in repair["global_repair_constraints"]


def test_consistency_validator_outputs_learning_metadata():
    engine = CharacterConsistencyValidator()

    result = engine.run(full_payload())

    ontology_record = LearnedOntologyRecord.model_validate(result.data["ontology_record"])
    learning_metadata = EngineLearningMetadata.model_validate(result.data["learning_metadata"])

    assert ontology_record.ontology_type == "character_consistency_validation"
    assert ontology_record.family == "character_validation"
    assert ontology_record.generated_by_engine == "character.consistency_validator"

    assert learning_metadata.engine_name == "character.consistency_validator"
    assert learning_metadata.target_object_id == "char_kael"
    assert learning_metadata.generated_training_labels["character_bible_ready"] is True
    assert learning_metadata.training_eligibility.training_eligible is True


def test_consistency_validator_builds_next_payloads():
    engine = CharacterConsistencyValidator()

    result = engine.run(full_payload())

    payload = result.data["next_engine_payload"]

    assert "character_seed" in payload
    assert "originality_engine_payload" in payload
    assert "quality_scorer_payload" in payload
    assert "character_bible_export_payload" in payload
    assert "chunk8_training_payload_later" in payload
    assert payload["character_seed"]["consistency_report"]["character_id"] == "char_kael"


def test_consistency_validator_warns_without_character_seed():
    engine = CharacterConsistencyValidator()

    result = engine.run({})

    assert result.success is True
    assert len(result.warnings) == 1
    assert "character_seed" in result.warnings[0]
    assert result.data["consistency_report"]["character_id"].startswith("char_")

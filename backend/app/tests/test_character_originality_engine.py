from backend.app.engines.character.character_originality_engine import CharacterOriginalityEngine
from backend.app.schemas.foundation import EngineRunResult
from backend.app.schemas.learning import EngineLearningMetadata, LearnedOntologyRecord


def strong_payload():
    return {
        "character_seed": {
            "character_id": "char_kael",
            "name": "Kael Veyran",
            "role": "protagonist",
            "social_class": "academy_sponsored",
            "family_name_status": "distrusted",
            "destiny_type": "hidden_kingmaker",
        },
        "psychology_profile": {
            "character_id": "char_kael",
            "core_wound": "believes belonging can be revoked after public failure",
        },
        "goal_profile": {
            "character_id": "char_kael",
            "true_need": "belonging is not the same as permission",
            "false_need": "worth can be revoked by public failure",
        },
        "moral_profile": {
            "character_id": "char_kael",
            "dominant_moral_value": "justice",
            "corruption_risk": 0.43,
        },
        "skill_ontology": {
            "skill_family": "cognitive_inference",
            "skill_subtype": "pattern_detection",
        },
        "character_type_ontology": {
            "type_family": "power_redirector",
            "type_subtype": "hidden_kingmaker",
        },
        "adaptability_profile": {
            "adaptability_family": "earned_moral_breakthrough",
        },
        "destiny_profile": {
            "destiny_family": "power_flow_destiny",
            "destiny_burdens": ["others may treat the character as a means to power"],
        },
        "relationship_readiness_profile": {
            "relationship_readiness_family": "high_loyalty_power_broker_readiness",
            "intimacy_risk": 0.72,
        },
        "dialogue_voice_profile": {
            "voice_family": "controlled_subtext_voice",
        },
        "consistency_report": {
            "overall_consistency_score": 0.94,
        },
        "source_mode": "human_approved_synthetic",
        "user_rating": 9,
    }


def generic_payload():
    return {
        "character_seed": {
            "character_id": "char_generic",
            "name": "Arin",
            "role": "protagonist",
        },
        "skill_ontology": {
            "skill_family": "elemental_authority",
        },
        "character_type_ontology": {
            "type_family": "general_ensemble_character",
        },
        "destiny_profile": {
            "destiny_family": "prophetic_selection_destiny",
        },
        "source_mode": "human_approved_synthetic",
        "user_rating": 9,
    }


def test_originality_engine_returns_engine_result():
    engine = CharacterOriginalityEngine()

    result = engine.run(strong_payload())

    assert isinstance(result, EngineRunResult)
    assert result.success is True
    assert result.engine_name == "character.originality_engine"
    assert "character_originality_feature_vector" in result.data
    assert "similarity_report" in result.data
    assert "originality_report" in result.data
    assert "anti_genericity_report" in result.data
    assert "originality_improvement_plan" in result.data
    assert "learning_metadata" in result.data


def test_originality_engine_scores_strong_character_as_original():
    engine = CharacterOriginalityEngine()

    result = engine.run(strong_payload())

    report = result.data["originality_report"]
    feature = result.data["character_originality_feature_vector"]

    assert feature["people_type_family"] == "power_redirector"
    assert feature["skill_family"] == "cognitive_inference"
    assert feature["destiny_family"] == "power_flow_destiny"
    assert feature["voice_family"] == "controlled_subtext_voice"
    assert feature["unusual_combination_count"] >= 4
    assert report["overall_originality_score"] >= 0.7
    assert report["originality_tier"] in {"strong_originality", "high_originality"}
    assert "power_redirector_plus_cognitive_inference" in report["strong_originality_sources"]


def test_originality_engine_detects_generic_trope_risks():
    engine = CharacterOriginalityEngine()

    result = engine.run(generic_payload())

    similarity = result.data["similarity_report"]
    anti_generic = result.data["anti_genericity_report"]

    assert "generic_chosen_protagonist_risk" in similarity["trope_matches"]
    assert "generic_elemental_power_risk" in similarity["trope_matches"]
    assert "generic_character_type_risk" in similarity["trope_matches"]
    assert "missing_wound_genericity_risk" in similarity["trope_matches"]
    assert anti_generic["genericity_risk_score"] > 0.4
    assert len(anti_generic["required_inversions"]) >= 3


def test_originality_engine_builds_improvement_plan_for_generic_character():
    engine = CharacterOriginalityEngine()

    result = engine.run(generic_payload())

    plan = result.data["originality_improvement_plan"]

    assert plan["requires_originality_improvement"] is True
    assert "increase cross-engine grounding" in plan["priority_repairs"]
    assert "do not add random uniqueness without causal grounding" in plan["originality_constraints"]
    assert "embed full character bible" in plan["future_embedding_upgrade_tasks"]


def test_originality_engine_outputs_learning_metadata():
    engine = CharacterOriginalityEngine()

    result = engine.run(strong_payload())

    ontology_record = LearnedOntologyRecord.model_validate(result.data["ontology_record"])
    learning_metadata = EngineLearningMetadata.model_validate(result.data["learning_metadata"])

    assert ontology_record.ontology_type == "character_originality"
    assert ontology_record.family == "character_originality"
    assert ontology_record.generated_by_engine == "character.originality_engine"

    assert learning_metadata.engine_name == "character.originality_engine"
    assert learning_metadata.target_object_id == "char_kael"
    assert learning_metadata.generated_training_labels["ready_for_quality_scorer"] is True
    assert learning_metadata.training_eligibility.training_eligible is True


def test_originality_engine_is_conservative_when_source_not_approved():
    engine = CharacterOriginalityEngine()

    payload = strong_payload()
    payload["source_mode"] = "unknown_web_text"

    result = engine.run(payload)

    metadata = result.data["learning_metadata"]

    assert metadata["training_eligibility"]["training_eligible"] is False
    assert metadata["training_eligibility"]["do_not_train"] is True
    assert "source mode is not approved for training" in metadata["training_eligibility"]["rejection_reasons"]


def test_originality_engine_builds_next_payloads():
    engine = CharacterOriginalityEngine()

    result = engine.run(strong_payload())

    payload = result.data["next_engine_payload"]

    assert "character_seed" in payload
    assert "quality_scorer_payload" in payload
    assert "character_bible_export_payload" in payload
    assert "chunk8_embedding_payload_later" in payload
    assert payload["character_seed"]["originality_report"]["character_id"] == "char_kael"


def test_originality_engine_warns_without_character_seed():
    engine = CharacterOriginalityEngine()

    result = engine.run({})

    assert result.success is True
    assert len(result.warnings) == 1
    assert "character_seed" in result.warnings[0]
    assert result.data["originality_report"]["character_id"].startswith("char_")

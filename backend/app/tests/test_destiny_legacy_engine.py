from backend.app.engines.character.destiny_legacy_engine import DestinyLegacyEngine
from backend.app.schemas.foundation import EngineRunResult
from backend.app.schemas.learning import EngineLearningMetadata, LearnedOntologyRecord


def sample_seed():
    return {
        "character_id": "char_kael",
        "name": "Kael Veyran",
        "role": "protagonist",
        "family_name_status": "distrusted",
        "destiny_type": "hidden_kingmaker",
        "adaptability_type": "earned_breakthrough",
        "breakthrough_condition": "protects someone weaker from public punishment",
        "adaptation_cost": "burns safe anonymity",
    }


def sample_skill_ontology():
    return {
        "skill_family": "cognitive_inference",
        "skill_subtype": "pattern_detection",
        "power_scale": "rare_human_plus",
        "destiny_compatibility": 0.68,
    }


def sample_character_type_ontology():
    return {
        "type_family": "power_redirector",
        "type_subtype": "hidden_kingmaker",
        "social_position": "low_visible_status_high_hidden_influence",
        "destiny_relevance": 0.78,
    }


def sample_adaptability():
    return {
        "character_id": "char_kael",
        "adaptability_family": "earned_moral_breakthrough",
        "adaptability_subtype": "protection_triggered_exceedance",
    }


def sample_goal():
    return {
        "character_id": "char_kael",
        "true_need": "belonging is not the same as permission",
        "false_need": "worth can be revoked by public failure",
    }


def sample_moral():
    return {
        "character_id": "char_kael",
        "dominant_moral_value": "justice",
        "corruption_risk": 0.43,
    }


def test_destiny_engine_returns_engine_result():
    engine = DestinyLegacyEngine()

    result = engine.run(
        {
            "character_seed": sample_seed(),
            "skill_ontology": sample_skill_ontology(),
            "character_type_ontology": sample_character_type_ontology(),
            "adaptability_profile": sample_adaptability(),
            "goal_profile": sample_goal(),
            "moral_profile": sample_moral(),
            "source_mode": "human_approved_synthetic",
            "user_rating": 9,
        }
    )

    assert isinstance(result, EngineRunResult)
    assert result.success is True
    assert result.engine_name == "character.destiny_legacy_engine"
    assert "destiny_profile" in result.data
    assert "prophecy_model" in result.data
    assert "legacy_model" in result.data
    assert "agency_conflict_model" in result.data
    assert "learning_metadata" in result.data
    assert "next_engine_payload" in result.data


def test_destiny_engine_builds_hidden_kingmaker_destiny():
    engine = DestinyLegacyEngine()

    result = engine.run(
        {
            "character_seed": sample_seed(),
            "skill_ontology": sample_skill_ontology(),
            "character_type_ontology": sample_character_type_ontology(),
            "adaptability_profile": sample_adaptability(),
            "goal_profile": sample_goal(),
            "moral_profile": sample_moral(),
            "source_mode": "human_approved_synthetic",
            "user_rating": 9,
        }
    )

    profile = result.data["destiny_profile"]

    assert profile["character_id"] == "char_kael"
    assert profile["destiny_family"] == "power_flow_destiny"
    assert profile["destiny_subtype"] == "hidden_kingmaker_fate"
    assert profile["destiny_name"] == "hidden_kingmaker"
    assert profile["destiny_is_absolute"] is False
    assert "others may treat the character as a means to power" in profile["destiny_burdens"]
    assert "can identify who should hold power before others see it" in profile["destiny_benefits"]


def test_destiny_engine_builds_ambiguous_prophecy_with_agency_reading():
    engine = DestinyLegacyEngine()

    result = engine.run(
        {
            "character_seed": sample_seed(),
            "skill_ontology": sample_skill_ontology(),
            "character_type_ontology": sample_character_type_ontology(),
            "adaptability_profile": sample_adaptability(),
            "goal_profile": sample_goal(),
            "moral_profile": sample_moral(),
        }
    )

    prophecy = result.data["prophecy_model"]

    assert prophecy["prophecy_id"].startswith("prop_")
    assert prophecy["prophecy_structure"] == "causal_pattern_prophecy"
    assert "one unseen at the table" in prophecy["prophecy_text"]
    assert prophecy["prophecy_is_complete"] is False
    assert prophecy["prophecy_requires_choice"] is True
    assert "chosen-one simplification" in prophecy["misinterpretation_vectors"]
    assert "treating influence as control" in prophecy["misinterpretation_vectors"]


def test_destiny_engine_builds_legacy_and_agency_conflict():
    engine = DestinyLegacyEngine()

    result = engine.run(
        {
            "character_seed": sample_seed(),
            "skill_ontology": sample_skill_ontology(),
            "character_type_ontology": sample_character_type_ontology(),
            "adaptability_profile": sample_adaptability(),
            "goal_profile": sample_goal(),
            "moral_profile": sample_moral(),
        }
    )

    legacy = result.data["legacy_model"]
    conflict = result.data["agency_conflict_model"]

    assert legacy["legacy_id"].startswith("leg_")
    assert legacy["legacy_pressure_type"] == "contested_name_legacy"
    assert legacy["legacy_lie"] == "worth can be revoked by public failure"
    assert legacy["legacy_truth"] == "belonging is not the same as permission"

    assert conflict["agency_conflict_id"].startswith("dconf_")
    assert conflict["agency_conflict_type"] == "agency_vs_being_used_as_power_tool"
    assert "destiny must not decide without character choice" in conflict["agency_protection_rules"]
    assert "do not write destiny as guaranteed victory" in conflict["destiny_generation_constraints"]
    assert len(conflict["refusal_path"]) >= 3
    assert len(conflict["reinterpretation_path"]) >= 3


def test_destiny_engine_outputs_learning_metadata():
    engine = DestinyLegacyEngine()

    result = engine.run(
        {
            "character_seed": sample_seed(),
            "skill_ontology": sample_skill_ontology(),
            "character_type_ontology": sample_character_type_ontology(),
            "adaptability_profile": sample_adaptability(),
            "goal_profile": sample_goal(),
            "moral_profile": sample_moral(),
            "source_mode": "human_approved_synthetic",
            "user_rating": 9,
        }
    )

    ontology_record = LearnedOntologyRecord.model_validate(result.data["ontology_record"])
    learning_metadata = EngineLearningMetadata.model_validate(result.data["learning_metadata"])

    assert ontology_record.ontology_type == "destiny"
    assert ontology_record.family == "power_flow_destiny"
    assert ontology_record.generated_by_engine == "character.destiny_legacy_engine"

    assert learning_metadata.engine_name == "character.destiny_legacy_engine"
    assert learning_metadata.target_object_id == "char_kael"
    assert learning_metadata.generated_training_labels["destiny_family"] == "power_flow_destiny"
    assert learning_metadata.training_eligibility.training_eligible is True


def test_destiny_engine_classifies_adaptive_threshold_destiny():
    engine = DestinyLegacyEngine()

    result = engine.run(
        {
            "character_seed": {
                "character_id": "char_ilyen",
                "destiny_type": "threshold_marked",
                "adaptability_type": "limit_break_anomaly",
                "breakthrough_condition": "someone weaker will be erased unless they exceed a limit",
                "adaptation_cost": "identity instability after breakthrough",
            },
            "skill_ontology": {
                "skill_family": "adaptive_limit_system",
                "power_scale": "mythic_or_anomalous",
                "destiny_compatibility": 0.75,
            },
            "adaptability_profile": {
                "adaptability_family": "limit_break_anomaly",
            },
            "source_mode": "human_approved_synthetic",
            "user_rating": 9,
        }
    )

    profile = result.data["destiny_profile"]
    prophecy = result.data["prophecy_model"]

    assert profile["destiny_family"] == "adaptive_threshold_destiny"
    assert profile["destiny_subtype"] == "rule_breaking_pressure"
    assert prophecy["prophecy_structure"] == "threshold_event_prophecy"
    assert "rule fails the powerless" in prophecy["prophecy_text"]


def test_destiny_engine_diagnostics_confirm_non_generic_destiny():
    engine = DestinyLegacyEngine()

    result = engine.run(
        {
            "character_seed": sample_seed(),
            "skill_ontology": sample_skill_ontology(),
            "character_type_ontology": sample_character_type_ontology(),
            "adaptability_profile": sample_adaptability(),
            "goal_profile": sample_goal(),
            "moral_profile": sample_moral(),
        }
    )

    diagnostics = result.data["destiny_diagnostics"]

    assert diagnostics["destiny_completeness_score"] >= 0.9
    assert diagnostics["has_prophecy"] is True
    assert diagnostics["has_misinterpretation"] is True
    assert diagnostics["has_legacy_burden"] is True
    assert diagnostics["has_agency_protection"] is True
    assert diagnostics["has_refusal_path"] is True
    assert diagnostics["has_reinterpretation_path"] is True
    assert diagnostics["destiny_is_not_generic_chosen_one"] is True
    assert diagnostics["plot_ready"] is True
    assert diagnostics["training_ready_schema"] is True


def test_destiny_engine_is_conservative_when_source_not_approved():
    engine = DestinyLegacyEngine()

    result = engine.run(
        {
            "character_seed": sample_seed(),
            "skill_ontology": sample_skill_ontology(),
            "character_type_ontology": sample_character_type_ontology(),
            "adaptability_profile": sample_adaptability(),
            "goal_profile": sample_goal(),
            "moral_profile": sample_moral(),
            "source_mode": "unknown_web_text",
            "user_rating": 9,
        }
    )

    metadata = result.data["learning_metadata"]

    assert metadata["training_eligibility"]["training_eligible"] is False
    assert metadata["training_eligibility"]["do_not_train"] is True
    assert "source mode is not approved for training" in metadata["training_eligibility"]["rejection_reasons"]


def test_destiny_engine_builds_next_payloads():
    engine = DestinyLegacyEngine()

    result = engine.run(
        {
            "character_seed": sample_seed(),
            "skill_ontology": sample_skill_ontology(),
            "character_type_ontology": sample_character_type_ontology(),
            "adaptability_profile": sample_adaptability(),
            "goal_profile": sample_goal(),
            "moral_profile": sample_moral(),
        }
    )

    payload = result.data["next_engine_payload"]

    assert "character_seed" in payload
    assert "relationship_readiness_payload" in payload
    assert "dialogue_voice_payload" in payload
    assert "plot_engine_payload_later" in payload
    assert "chunk8_training_payload_later" in payload
    assert payload["character_seed"]["destiny_profile"]["character_id"] == "char_kael"


def test_destiny_engine_warns_without_character_seed():
    engine = DestinyLegacyEngine()

    result = engine.run({})

    assert result.success is True
    assert len(result.warnings) == 1
    assert "character_seed" in result.warnings[0]
    assert result.data["destiny_profile"]["character_id"].startswith("char_")

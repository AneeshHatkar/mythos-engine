from backend.app.engines.character.adaptability_engine import AdaptabilityEngine
from backend.app.schemas.foundation import EngineRunResult
from backend.app.schemas.learning import EngineLearningMetadata, LearnedOntologyRecord


def sample_seed():
    return {
        "character_id": "char_kael",
        "name": "Kael Veyran",
        "role": "protagonist",
        "adaptability_type": "earned_breakthrough",
        "breakthrough_condition": "protects someone weaker from public punishment",
        "adaptation_cost": "burns safe anonymity",
        "destiny_type": "hidden_kingmaker",
    }


def sample_skill_profile():
    return {
        "character_id": "char_kael",
        "primary_skill": "Pattern Reading",
        "skill_rank": "S",
        "skill_rarity": "rare",
    }


def sample_skill_ontology():
    return {
        "skill_name": "Pattern Reading",
        "skill_family": "cognitive_inference",
        "skill_subtype": "pattern_detection",
        "activation_model": "passive_focus",
        "growth_model": "precision_refinement",
        "cost_family": ["mental_fatigue", "emotional_exposure"],
        "counter_family": ["false_signal", "missing_evidence", "emotional_bias"],
        "power_scale": "rare_human_plus",
        "world_legality_family": "legal_but_context_dependent",
        "adaptability_compatibility": 0.72,
        "destiny_compatibility": 0.68,
    }


def sample_character_type_ontology():
    return {
        "type_family": "power_redirector",
        "type_subtype": "hidden_kingmaker",
        "relationship_function": "slow_trust_high_loyalty_power_broker",
        "plot_function": "redirects_power_flow_and_changes_who_can_win",
        "adaptability_potential": 0.82,
        "destiny_relevance": 0.78,
    }


def sample_power_limits():
    return {
        "costs": ["emotional exhaustion", "decision fatigue and social isolation"],
        "limitations": ["fails when emotionally attached or deliberately misinformed"],
        "cannot_do": ["cannot read completely hidden information without evidence"],
    }


def sample_goal():
    return {
        "character_id": "char_kael",
        "choice_pressure": "must choose between safety and protecting someone weaker",
        "true_need": "belonging is not the same as permission",
    }


def sample_moral():
    return {
        "character_id": "char_kael",
        "moral_flexibility": 0.57,
        "corruption_risk": 0.43,
        "mercy_triggers": ["protects someone weaker from public punishment"],
    }


def test_adaptability_engine_returns_engine_result():
    engine = AdaptabilityEngine()

    result = engine.run(
        {
            "character_seed": sample_seed(),
            "skill_profile": sample_skill_profile(),
            "skill_ontology": sample_skill_ontology(),
            "character_type_ontology": sample_character_type_ontology(),
            "power_limits": sample_power_limits(),
            "goal_profile": sample_goal(),
            "moral_profile": sample_moral(),
            "source_mode": "human_approved_synthetic",
            "user_rating": 9,
        }
    )

    assert isinstance(result, EngineRunResult)
    assert result.success is True
    assert result.engine_name == "character.adaptability_engine"
    assert "adaptability_profile" in result.data
    assert "limit_break_rules" in result.data
    assert "adaptation_pathways" in result.data
    assert "failure_and_cost_model" in result.data
    assert "learning_metadata" in result.data
    assert "next_engine_payload" in result.data


def test_adaptability_engine_builds_earned_moral_breakthrough():
    engine = AdaptabilityEngine()

    result = engine.run(
        {
            "character_seed": sample_seed(),
            "skill_profile": sample_skill_profile(),
            "skill_ontology": sample_skill_ontology(),
            "character_type_ontology": sample_character_type_ontology(),
            "power_limits": sample_power_limits(),
            "goal_profile": sample_goal(),
            "moral_profile": sample_moral(),
            "source_mode": "human_approved_synthetic",
            "user_rating": 9,
        }
    )

    profile = result.data["adaptability_profile"]

    assert profile["character_id"] == "char_kael"
    assert profile["adaptability_family"] == "earned_moral_breakthrough"
    assert profile["adaptability_subtype"] == "protection_triggered_exceedance"
    assert "protects someone weaker" in profile["trigger_model"]
    assert profile["world_rule_exception_type"] in {"destiny_pressure_exception", "localized_rule_stress_exception"}
    assert profile["adaptation_ceiling"] >= 0.7
    assert profile["story_function"] == "turns moral pressure into costly growth and consequence"


def test_adaptability_engine_limit_break_rules_are_not_unlimited_power():
    engine = AdaptabilityEngine()

    result = engine.run(
        {
            "character_seed": sample_seed(),
            "skill_profile": sample_skill_profile(),
            "skill_ontology": sample_skill_ontology(),
            "character_type_ontology": sample_character_type_ontology(),
            "power_limits": sample_power_limits(),
            "goal_profile": sample_goal(),
            "moral_profile": sample_moral(),
        }
    )

    rules = result.data["limit_break_rules"]

    assert rules["limit_break_allowed"] is True
    assert "cannot activate for convenience" in rules["hard_prohibitions"]
    assert "cannot erase prior consequences" in rules["hard_prohibitions"]
    assert "limit-break requires cost" in rules["generation_constraints"]
    assert "limit-break requires counterplay" in rules["generation_constraints"]
    assert "mental_fatigue" in rules["required_costs"]


def test_adaptability_engine_builds_adaptation_pathways_and_failure_model():
    engine = AdaptabilityEngine()

    result = engine.run(
        {
            "character_seed": sample_seed(),
            "skill_profile": sample_skill_profile(),
            "skill_ontology": sample_skill_ontology(),
            "character_type_ontology": sample_character_type_ontology(),
            "power_limits": sample_power_limits(),
            "goal_profile": sample_goal(),
            "moral_profile": sample_moral(),
        }
    )

    pathways = result.data["adaptation_pathways"]
    failures = result.data["failure_and_cost_model"]

    assert pathways["counter_adaptation_needed"] is True
    assert "enemy develops counter-adaptation" in pathways["medium_term_pathway"]
    assert "adaptation succeeds but creates worse social consequence" in failures["failure_modes"]
    assert "enemy learns the activation pattern" in failures["failure_modes"]
    assert "weaponize public visibility" in failures["counter_adaptation_patterns"] or len(failures["counter_adaptation_patterns"]) > 0


def test_adaptability_engine_outputs_learning_metadata():
    engine = AdaptabilityEngine()

    result = engine.run(
        {
            "character_seed": sample_seed(),
            "skill_profile": sample_skill_profile(),
            "skill_ontology": sample_skill_ontology(),
            "character_type_ontology": sample_character_type_ontology(),
            "power_limits": sample_power_limits(),
            "goal_profile": sample_goal(),
            "moral_profile": sample_moral(),
            "source_mode": "human_approved_synthetic",
            "user_rating": 9,
        }
    )

    ontology_record = LearnedOntologyRecord.model_validate(result.data["ontology_record"])
    learning_metadata = EngineLearningMetadata.model_validate(result.data["learning_metadata"])

    assert ontology_record.ontology_type == "adaptability"
    assert ontology_record.family == "earned_moral_breakthrough"
    assert ontology_record.generated_by_engine == "character.adaptability_engine"

    assert learning_metadata.engine_name == "character.adaptability_engine"
    assert learning_metadata.target_object_id == "char_kael"
    assert learning_metadata.generated_training_labels["adaptability_family"] == "earned_moral_breakthrough"
    assert learning_metadata.training_eligibility.training_eligible is True


def test_adaptability_engine_handles_limit_break_anomaly_with_review_needed():
    engine = AdaptabilityEngine()

    result = engine.run(
        {
            "character_seed": {
                "character_id": "char_ilyen",
                "adaptability_type": "limit_break_anomaly",
                "breakthrough_condition": "someone weaker will be erased unless they exceed a limit",
                "adaptation_cost": "identity instability after breakthrough",
            },
            "skill_ontology": {
                "skill_family": "adaptive_limit_system",
                "skill_subtype": "pressure_evolution",
                "activation_model": "pressure_triggered",
                "power_scale": "mythic_or_anomalous",
                "cost_family": ["instability", "post_break_recovery", "identity_strain"],
                "counter_family": ["pressure_denial", "recovery_window_attack"],
                "adaptability_compatibility": 0.9,
            },
            "character_type_ontology": {
                "adaptability_potential": 0.9,
            },
            "source_mode": "human_approved_synthetic",
            "user_rating": 9,
        }
    )

    profile = result.data["adaptability_profile"]
    diagnostics = result.data["adaptation_diagnostics"]
    metadata = result.data["learning_metadata"]

    assert profile["adaptability_family"] == "limit_break_anomaly"
    assert profile["instability_score"] >= 0.7
    assert diagnostics["adaptation_safety_tier"] == "high_review_needed"
    assert metadata["training_eligibility"]["training_eligible"] is False
    assert "high instability requires human review before training" in metadata["training_eligibility"]["rejection_reasons"]


def test_adaptability_engine_diagnostics_confirm_plot_ready_and_not_unlimited():
    engine = AdaptabilityEngine()

    result = engine.run(
        {
            "character_seed": sample_seed(),
            "skill_profile": sample_skill_profile(),
            "skill_ontology": sample_skill_ontology(),
            "character_type_ontology": sample_character_type_ontology(),
            "power_limits": sample_power_limits(),
            "goal_profile": sample_goal(),
            "moral_profile": sample_moral(),
        }
    )

    diagnostics = result.data["adaptation_diagnostics"]

    assert diagnostics["adaptability_completeness_score"] >= 0.9
    assert diagnostics["has_trigger"] is True
    assert diagnostics["has_cost"] is True
    assert diagnostics["has_recovery"] is True
    assert diagnostics["has_counterplay"] is True
    assert diagnostics["has_hard_prohibitions"] is True
    assert diagnostics["is_not_unlimited_power"] is True
    assert diagnostics["plot_ready"] is True
    assert diagnostics["training_ready_schema"] is True


def test_adaptability_engine_builds_next_payloads():
    engine = AdaptabilityEngine()

    result = engine.run(
        {
            "character_seed": sample_seed(),
            "skill_profile": sample_skill_profile(),
            "skill_ontology": sample_skill_ontology(),
            "character_type_ontology": sample_character_type_ontology(),
            "power_limits": sample_power_limits(),
            "goal_profile": sample_goal(),
            "moral_profile": sample_moral(),
        }
    )

    payload = result.data["next_engine_payload"]

    assert "character_seed" in payload
    assert "destiny_engine_payload" in payload
    assert "relationship_readiness_payload" in payload
    assert "plot_engine_payload_later" in payload
    assert "chunk8_training_payload_later" in payload
    assert payload["character_seed"]["adaptability_profile"]["character_id"] == "char_kael"


def test_adaptability_engine_warns_without_character_seed():
    engine = AdaptabilityEngine()

    result = engine.run({})

    assert result.success is True
    assert len(result.warnings) == 1
    assert "character_seed" in result.warnings[0]
    assert result.data["adaptability_profile"]["character_id"].startswith("char_")

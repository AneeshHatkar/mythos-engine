from backend.app.engines.character.relationship_readiness_engine import RelationshipReadinessEngine
from backend.app.schemas.foundation import EngineRunResult
from backend.app.schemas.learning import EngineLearningMetadata, LearnedOntologyRecord


def sample_seed():
    return {
        "character_id": "char_kael",
        "name": "Kael Veyran",
        "role": "protagonist",
        "family_name_status": "distrusted",
        "destiny_type": "hidden_kingmaker",
    }


def sample_psychology():
    return {
        "character_id": "char_kael",
        "core_wound": "believes belonging can be revoked at any public failure",
        "shame_trigger": "being treated as useful but replaceable",
        "healing_condition": "someone learns the family truth and protects them without using it",
        "betrayal_response": "goes cold, protects family secrets, and remembers exact words",
    }


def sample_memories():
    return [
        {
            "memory_id": "mem_core",
            "content": "public failure memory",
            "emotional_weight": 0.82,
        },
        {
            "memory_id": "mem_secret",
            "content": "family secret memory",
            "emotional_weight": 0.74,
        },
    ]


def sample_reputation():
    return {
        "character_id": "char_kael",
        "exposure_risk": 0.72,
        "enemy_threat_reputation": 0.58,
    }


def sample_moral():
    return {
        "character_id": "char_kael",
        "moral_flexibility": 0.57,
        "forbidden_lines": ["will not knowingly sacrifice someone powerless for personal advancement"],
    }


def sample_goal():
    return {
        "character_id": "char_kael",
        "hidden_goal": "find proof that the ranking system is edited",
        "true_need": "belonging is not the same as permission",
        "false_need": "worth can be revoked by public failure",
        "agency_score": 0.74,
    }


def sample_skill_ontology():
    return {
        "skill_family": "cognitive_inference",
        "visibility_model": "visible_when_demonstrated",
    }


def sample_type_ontology():
    return {
        "type_family": "power_redirector",
        "relationship_function": "slow_trust_high_loyalty_power_broker",
        "plot_function": "redirects_power_flow_and_changes_who_can_win",
        "compatibility_axes": {
            "romance_compatibility": 0.53,
            "rivalry_compatibility": 0.62,
            "mentor_compatibility": 0.4,
            "villain_pressure_compatibility": 0.58,
            "ensemble_utility": 0.74,
        },
    }


def sample_adaptability():
    return {
        "relationship_risk": 0.52,
    }


def sample_destiny():
    return {
        "destiny_family": "power_flow_destiny",
        "destiny_burdens": ["others may treat the character as a means to power"],
    }


def sample_legacy():
    return {
        "legacy_pressure_type": "contested_name_legacy",
    }


def sample_agency_conflict():
    return {
        "agency_conflict_type": "agency_vs_being_used_as_power_tool",
    }


def test_relationship_readiness_engine_returns_engine_result():
    engine = RelationshipReadinessEngine()

    result = engine.run(
        {
            "character_seed": sample_seed(),
            "psychology_profile": sample_psychology(),
            "memory_records": sample_memories(),
            "reputation_profile": sample_reputation(),
            "moral_profile": sample_moral(),
            "goal_profile": sample_goal(),
            "skill_ontology": sample_skill_ontology(),
            "character_type_ontology": sample_type_ontology(),
            "adaptability_profile": sample_adaptability(),
            "destiny_profile": sample_destiny(),
            "legacy_model": sample_legacy(),
            "agency_conflict_model": sample_agency_conflict(),
            "source_mode": "human_approved_synthetic",
            "user_rating": 9,
        }
    )

    assert isinstance(result, EngineRunResult)
    assert result.success is True
    assert result.engine_name == "character.relationship_readiness_engine"
    assert "relationship_readiness_profile" in result.data
    assert "relationship_hooks" in result.data
    assert "compatibility_vectors" in result.data
    assert "attachment_and_conflict_model" in result.data
    assert "boundary_model" in result.data
    assert "learning_metadata" in result.data


def test_relationship_readiness_engine_builds_core_profile():
    engine = RelationshipReadinessEngine()

    result = engine.run(
        {
            "character_seed": sample_seed(),
            "psychology_profile": sample_psychology(),
            "memory_records": sample_memories(),
            "reputation_profile": sample_reputation(),
            "moral_profile": sample_moral(),
            "goal_profile": sample_goal(),
            "skill_ontology": sample_skill_ontology(),
            "character_type_ontology": sample_type_ontology(),
            "adaptability_profile": sample_adaptability(),
            "destiny_profile": sample_destiny(),
        }
    )

    profile = result.data["relationship_readiness_profile"]

    assert profile["character_id"] == "char_kael"
    assert profile["relationship_readiness_id"].startswith("relready_")
    assert profile["relationship_readiness_family"] == "high_loyalty_power_broker_readiness"
    assert profile["attachment_pattern"] == "guarded_attachment_with_secret_testing"
    assert profile["trust_model"] == "trust_requires_truth_protection_without_weaponization"
    assert "someone learns the family truth" in profile["vulnerability_model"]
    assert profile["intimacy_risk"] >= 0.6
    assert profile["relationship_agency_level"] == "high_relationship_agency"


def test_relationship_readiness_engine_builds_relationship_hooks():
    engine = RelationshipReadinessEngine()

    result = engine.run(
        {
            "character_seed": sample_seed(),
            "psychology_profile": sample_psychology(),
            "memory_records": sample_memories(),
            "reputation_profile": sample_reputation(),
            "moral_profile": sample_moral(),
            "goal_profile": sample_goal(),
            "skill_ontology": sample_skill_ontology(),
            "character_type_ontology": sample_type_ontology(),
            "adaptability_profile": sample_adaptability(),
            "destiny_profile": sample_destiny(),
            "legacy_model": sample_legacy(),
        }
    )

    hooks = result.data["relationship_hooks"]

    assert "friendship_hooks" in hooks
    assert "romance_hooks" in hooks
    assert "rivalry_hooks" in hooks
    assert "family_hooks" in hooks
    assert "enemy_hooks" in hooks
    assert "betrayal_hooks" in hooks
    assert any("legacy pressure" in hook for hook in hooks["family_hooks"])
    assert any("destiny interpretation" in hook for hook in hooks["enemy_hooks"])


def test_relationship_readiness_engine_builds_compatibility_vectors():
    engine = RelationshipReadinessEngine()

    result = engine.run(
        {
            "character_seed": sample_seed(),
            "psychology_profile": sample_psychology(),
            "memory_records": sample_memories(),
            "reputation_profile": sample_reputation(),
            "moral_profile": sample_moral(),
            "goal_profile": sample_goal(),
            "skill_ontology": sample_skill_ontology(),
            "character_type_ontology": sample_type_ontology(),
            "adaptability_profile": sample_adaptability(),
            "destiny_profile": sample_destiny(),
        }
    )

    vectors = result.data["compatibility_vectors"]

    assert vectors["friendship_vector"]["readiness_score"] >= 0.6
    assert vectors["romance_vector"]["relationship_type"] == "romance"
    assert vectors["rivalry_vector"]["readiness_score"] >= 0.6
    assert vectors["enemy_vector"]["readiness_score"] >= 0.5
    assert vectors["ensemble_vector"]["readiness_score"] >= 0.7


def test_relationship_readiness_engine_builds_attachment_conflict_and_boundaries():
    engine = RelationshipReadinessEngine()

    result = engine.run(
        {
            "character_seed": sample_seed(),
            "psychology_profile": sample_psychology(),
            "memory_records": sample_memories(),
            "reputation_profile": sample_reputation(),
            "moral_profile": sample_moral(),
            "goal_profile": sample_goal(),
            "skill_ontology": sample_skill_ontology(),
            "character_type_ontology": sample_type_ontology(),
            "adaptability_profile": sample_adaptability(),
            "destiny_profile": sample_destiny(),
            "agency_conflict_model": sample_agency_conflict(),
        }
    )

    attachment = result.data["attachment_and_conflict_model"]
    boundary = result.data["boundary_model"]

    assert attachment["attachment_pattern"] == "guarded_attachment_with_secret_testing"
    assert attachment["betrayal_sensitivity"] >= 0.6
    assert any("destiny/agency conflict" in trigger for trigger in attachment["conflict_triggers"])
    assert "specific truth repair" in attachment["repair_requirements"]

    assert boundary["boundary_strength"] >= 0.6
    assert "relationship cannot erase independent agency" in boundary["relationship_boundaries"]
    assert "destiny cannot force love, loyalty, or forgiveness" in boundary["relationship_boundaries"]
    assert "preserve independent goals" in boundary["relationship_generation_constraints"]


def test_relationship_readiness_engine_outputs_learning_metadata():
    engine = RelationshipReadinessEngine()

    result = engine.run(
        {
            "character_seed": sample_seed(),
            "psychology_profile": sample_psychology(),
            "memory_records": sample_memories(),
            "reputation_profile": sample_reputation(),
            "moral_profile": sample_moral(),
            "goal_profile": sample_goal(),
            "skill_ontology": sample_skill_ontology(),
            "character_type_ontology": sample_type_ontology(),
            "adaptability_profile": sample_adaptability(),
            "destiny_profile": sample_destiny(),
            "source_mode": "human_approved_synthetic",
            "user_rating": 9,
        }
    )

    ontology_record = LearnedOntologyRecord.model_validate(result.data["ontology_record"])
    learning_metadata = EngineLearningMetadata.model_validate(result.data["learning_metadata"])

    assert ontology_record.ontology_type == "relationship_readiness"
    assert ontology_record.family == "high_loyalty_power_broker_readiness"
    assert ontology_record.generated_by_engine == "character.relationship_readiness_engine"

    assert learning_metadata.engine_name == "character.relationship_readiness_engine"
    assert learning_metadata.target_object_id == "char_kael"
    assert learning_metadata.generated_training_labels["chunk4_ready"] is True
    assert learning_metadata.training_eligibility.training_eligible is True


def test_relationship_readiness_engine_love_interest_preserves_independent_goal():
    engine = RelationshipReadinessEngine()

    result = engine.run(
        {
            "character_seed": {
                "character_id": "char_mira",
                "name": "Mira Vaul",
                "role": "love_interest",
            },
            "psychology_profile": {
                "healing_condition": "trust without ownership",
            },
            "goal_profile": {
                "hidden_goal": "protect her own investigation",
                "agency_score": 0.72,
            },
            "character_type_ontology": {
                "type_family": "intimacy_axis_character",
                "relationship_function": "romantic_axis_with_independent_agency",
                "compatibility_axes": {"romance_compatibility": 0.82},
            },
            "source_mode": "human_approved_synthetic",
            "user_rating": 9,
        }
    )

    profile = result.data["relationship_readiness_profile"]
    vectors = result.data["compatibility_vectors"]
    boundary = result.data["boundary_model"]

    assert profile["relationship_readiness_family"] == "romantic_agency_readiness"
    assert "independent of romance" in profile["independent_goal_requirement"]
    assert vectors["romance_vector"]["readiness_score"] >= 0.8
    assert "romance cannot replace personal goal" in boundary["relationship_boundaries"]


def test_relationship_readiness_engine_diagnostics_confirm_chunk4_ready():
    engine = RelationshipReadinessEngine()

    result = engine.run(
        {
            "character_seed": sample_seed(),
            "psychology_profile": sample_psychology(),
            "memory_records": sample_memories(),
            "reputation_profile": sample_reputation(),
            "moral_profile": sample_moral(),
            "goal_profile": sample_goal(),
            "skill_ontology": sample_skill_ontology(),
            "character_type_ontology": sample_type_ontology(),
            "adaptability_profile": sample_adaptability(),
            "destiny_profile": sample_destiny(),
        }
    )

    diagnostics = result.data["relationship_readiness_diagnostics"]

    assert diagnostics["relationship_readiness_completeness_score"] >= 0.9
    assert diagnostics["has_attachment_model"] is True
    assert diagnostics["has_trust_model"] is True
    assert diagnostics["has_compatibility_vectors"] is True
    assert diagnostics["has_conflict_triggers"] is True
    assert diagnostics["has_repair_requirements"] is True
    assert diagnostics["has_boundaries"] is True
    assert diagnostics["chunk4_relationship_ready"] is True
    assert diagnostics["training_ready_schema"] is True


def test_relationship_readiness_engine_builds_next_payloads():
    engine = RelationshipReadinessEngine()

    result = engine.run(
        {
            "character_seed": sample_seed(),
            "psychology_profile": sample_psychology(),
            "memory_records": sample_memories(),
            "reputation_profile": sample_reputation(),
            "moral_profile": sample_moral(),
            "goal_profile": sample_goal(),
            "skill_ontology": sample_skill_ontology(),
            "character_type_ontology": sample_type_ontology(),
            "adaptability_profile": sample_adaptability(),
            "destiny_profile": sample_destiny(),
        }
    )

    payload = result.data["next_engine_payload"]

    assert "character_seed" in payload
    assert "dialogue_voice_payload" in payload
    assert "chunk4_relationship_simulation_payload_later" in payload
    assert "character_validator_payload" in payload
    assert "chunk8_training_payload_later" in payload
    assert payload["character_seed"]["relationship_readiness_profile"]["character_id"] == "char_kael"


def test_relationship_readiness_engine_warns_without_character_seed():
    engine = RelationshipReadinessEngine()

    result = engine.run({})

    assert result.success is True
    assert len(result.warnings) == 1
    assert "character_seed" in result.warnings[0]
    assert result.data["relationship_readiness_profile"]["character_id"].startswith("char_")

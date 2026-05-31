from backend.app.engines.character.character_full_profile_orchestrator import CharacterFullProfileOrchestrator
from backend.app.schemas.foundation import EngineRunResult
from backend.app.schemas.learning import EngineLearningMetadata, LearnedOntologyRecord


def strong_payload():
    return {
        "character_seed": {
            "character_id": "char_kael",
            "name": "Kael Veyran",
            "role": "protagonist",
            "people_type": "Hidden Kingmaker",
            "project_id": "proj_ashen",
            "universe_id": "velmora",
            "social_class": "academy_sponsored",
            "family_name_status": "distrusted",
            "destiny_type": "hidden_kingmaker",
        },
        "origin_profile": {"social_class": "academy_sponsored", "family_name_status": "distrusted"},
        "family_profile": {"family_name_status": "distrusted"},
        "psychology_profile": {"core_wound": "believes belonging can be revoked after public failure"},
        "goal_profile": {"true_need": "belonging is not the same as permission"},
        "moral_profile": {"dominant_moral_value": "justice"},
        "memory_records": [{"memory_id": "mem_core", "content": "public failure and family secret memory"}],
        "emotional_arc_profile": {"arc_type": "adaptive_breakthrough_arc"},
        "skill_ontology": {"skill_family": "cognitive_inference", "skill_subtype": "pattern_detection"},
        "character_type_ontology": {"type_family": "power_redirector", "type_subtype": "hidden_kingmaker"},
        "adaptability_profile": {"adaptability_family": "earned_moral_breakthrough"},
        "limit_break_rules": {"hard_prohibitions": ["cannot activate for convenience"]},
        "destiny_profile": {"destiny_family": "power_flow_destiny", "destiny_burdens": ["means to power"]},
        "prophecy_model": {"prophecy_requires_choice": True},
        "legacy_model": {"legacy_pressure_type": "contested_name_legacy"},
        "relationship_readiness_profile": {"relationship_readiness_family": "high_loyalty_power_broker_readiness"},
        "relationship_hooks": {"friendship_hooks": ["friend notices controlled distance"]},
        "compatibility_vectors": {"friendship_vector": {"readiness_score": 0.72}},
        "attachment_and_conflict_model": {"betrayal_sensitivity": 0.72},
        "boundary_model": {"relationship_boundaries": ["relationship cannot erase independent agency"]},
        "dialogue_voice_profile": {"voice_family": "controlled_subtext_voice"},
        "speech_pattern_model": {"sentence_rhythm": "short_precise_lines_with_held_back_explanations"},
        "emotional_dialogue_rules": {"emotional_leakage_model": "emotion leaks through precision"},
        "relationship_dialogue_variants": {"friend_voice": "practical warmth"},
        "destiny_dialogue_layer": {"destiny_denial_voice": "rejects simplistic labels"},
        "forbidden_dialogue_patterns": {"generic_voice_failure_modes": ["generic witty banter disconnected from wound"]},
        "consistency_report": {
            "overall_consistency_score": 0.94,
            "critical_issue_count": 0,
            "violation_count": 0,
        },
        "validation_checks": [{"check_id": "identity_consistency", "status": "pass"}],
        "repair_plan": {"requires_repair": False, "repair_count": 0},
        "originality_report": {"overall_originality_score": 0.78, "novelty_score": 0.82},
        "similarity_report": {"similarity_risk_score": 0.12},
        "anti_genericity_report": {"genericity_risk_score": 0.12},
        "quality_report": {
            "overall_quality_score": 0.84,
            "quality_tier": "strong_character_ready",
            "weak_axes": [],
        },
        "readiness_report": {
            "character_bible_ready": True,
            "orchestrator_ready": True,
            "training_queue_ready": True,
            "chunk4_relationship_ready": True,
        },
        "quality_recommendation_report": {"recommended_next_steps": ["preserve current structure"]},
        "source_mode": "human_approved_synthetic",
        "user_rating": 9,
    }


def partial_payload():
    return {
        "character_seed": {
            "character_id": "char_partial",
            "name": "Arin",
            "role": "protagonist",
        },
        "quality_report": {
            "overall_quality_score": 0.52,
            "quality_tier": "repair_needed",
            "weak_axes": ["psychological_depth", "dialogue_voice"],
        },
        "readiness_report": {
            "character_bible_ready": False,
            "orchestrator_ready": False,
            "training_queue_ready": False,
        },
        "source_mode": "human_approved_synthetic",
        "user_rating": 9,
    }


def test_full_profile_orchestrator_returns_engine_result():
    engine = CharacterFullProfileOrchestrator()

    result = engine.run(strong_payload())

    assert isinstance(result, EngineRunResult)
    assert result.success is True
    assert result.engine_name == "character.full_profile_orchestrator"
    assert "character_full_profile" in result.data
    assert "orchestration_report" in result.data
    assert "export_manifest" in result.data
    assert "missing_component_report" in result.data
    assert "learning_metadata" in result.data


def test_full_profile_orchestrator_builds_complete_profile_blocks():
    engine = CharacterFullProfileOrchestrator()

    result = engine.run(strong_payload())

    profile = result.data["character_full_profile"]

    assert profile["character_id"] == "char_kael"
    assert profile["profile_id"].startswith("charprofile_")
    assert profile["identity"]["name"] == "Kael Veyran"
    assert profile["identity"]["project_id"] == "proj_ashen"
    assert profile["identity"]["universe_id"] == "velmora"
    assert profile["origin"]["social_class"] == "academy_sponsored"
    assert profile["psychology"]["goal_profile"]["true_need"] == "belonging is not the same as permission"
    assert profile["power"]["skill_ontology"]["skill_family"] == "cognitive_inference"
    assert profile["destiny"]["destiny_profile"]["destiny_family"] == "power_flow_destiny"
    assert profile["relationships"]["relationship_readiness_profile"]["relationship_readiness_family"] == "high_loyalty_power_broker_readiness"
    assert profile["dialogue"]["dialogue_voice_profile"]["voice_family"] == "controlled_subtext_voice"
    assert profile["validation"]["quality_report"]["overall_quality_score"] == 0.84


def test_full_profile_orchestrator_reports_complete_ready_profile():
    engine = CharacterFullProfileOrchestrator()

    result = engine.run(strong_payload())

    report = result.data["orchestration_report"]
    diagnostics = result.data["orchestrator_diagnostics"]
    manifest = result.data["export_manifest"]

    assert report["profile_completeness_score"] >= 0.9
    assert report["profile_tier"] in {"complete_profile_ready", "complete_high_quality_profile"}
    assert diagnostics["character_bible_ready"] is True
    assert diagnostics["api_ready"] is True
    assert diagnostics["persistence_ready"] is True
    assert diagnostics["benchmark_ready"] is True
    assert diagnostics["chunk4_ready"] is True
    assert diagnostics["training_queue_ready"] is True
    assert manifest["safe_to_export"] is True
    assert "character_bible_markdown" in manifest["recommended_exports"]


def test_full_profile_orchestrator_detects_missing_and_weak_components():
    engine = CharacterFullProfileOrchestrator()

    result = engine.run(partial_payload())

    report = result.data["orchestration_report"]
    missing = result.data["missing_component_report"]
    diagnostics = result.data["orchestrator_diagnostics"]

    assert report["profile_tier"] in {"incomplete_profile", "partial_profile_needs_completion"}
    assert "psychology" in missing["missing_components"]
    assert "skill" in missing["missing_components"]
    assert "dialogue" in missing["missing_components"]
    assert "psychological_depth" in missing["weak_components"]
    assert diagnostics["character_bible_ready"] is False
    assert diagnostics["training_queue_ready"] is False


def test_full_profile_orchestrator_outputs_learning_metadata():
    engine = CharacterFullProfileOrchestrator()

    result = engine.run(strong_payload())

    ontology_record = LearnedOntologyRecord.model_validate(result.data["ontology_record"])
    learning_metadata = EngineLearningMetadata.model_validate(result.data["learning_metadata"])

    assert ontology_record.ontology_type == "character_full_profile"
    assert ontology_record.family == "character_full_profile"
    assert ontology_record.generated_by_engine == "character.full_profile_orchestrator"

    assert learning_metadata.engine_name == "character.full_profile_orchestrator"
    assert learning_metadata.target_object_id == "char_kael"
    assert learning_metadata.generated_training_labels["character_bible_ready"] is True
    assert learning_metadata.generated_training_labels["api_ready"] is True
    assert learning_metadata.generated_training_labels["training_queue_ready"] is True
    assert learning_metadata.training_eligibility.training_eligible is True


def test_full_profile_orchestrator_is_conservative_when_source_not_approved():
    engine = CharacterFullProfileOrchestrator()

    payload = strong_payload()
    payload["source_mode"] = "unknown_web_text"

    result = engine.run(payload)

    metadata = result.data["learning_metadata"]

    assert metadata["training_eligibility"]["training_eligible"] is False
    assert metadata["training_eligibility"]["do_not_train"] is True
    assert "source mode is not approved for training" in metadata["training_eligibility"]["rejection_reasons"]


def test_full_profile_orchestrator_builds_next_payloads():
    engine = CharacterFullProfileOrchestrator()

    result = engine.run(strong_payload())

    payload = result.data["next_engine_payload"]

    assert "character_store_payload" in payload
    assert "character_api_payload" in payload
    assert "character_bible_export_payload" in payload
    assert "benchmark_payload" in payload
    assert "chunk4_relationship_payload_later" in payload
    assert "chunk8_training_payload_later" in payload
    assert payload["character_store_payload"]["character_id"] == "char_kael"
    assert payload["chunk4_relationship_payload_later"]["character_id"] == "char_kael"


def test_full_profile_orchestrator_warns_without_character_seed():
    engine = CharacterFullProfileOrchestrator()

    result = engine.run({})

    assert result.success is True
    assert len(result.warnings) == 1
    assert "character_seed" in result.warnings[0]
    assert result.data["character_full_profile"]["character_id"].startswith("char_")

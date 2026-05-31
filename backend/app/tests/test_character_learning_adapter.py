from backend.app.services.character_learning_adapter import CharacterLearningAdapter
from backend.app.services.learning_integration import LearningIntegrationService


def sample_character_profile():
    return {
        "character_id": "char_kael",
        "identity": {
            "character_id": "char_kael",
            "name": "Kael Veyran",
            "role": "protagonist",
            "archetype_label": "Hidden Kingmaker",
        },
        "origin": {
            "social_class": "academy_sponsored",
            "family_name_status": "distrusted",
            "origin_profile": {
                "education_access": "conditional sponsor seat",
                "family_name_status": "distrusted",
            },
        },
        "psychology": {
            "psychology_profile": {
                "core_wound": "believes belonging can be revoked after public failure",
            },
            "goal_profile": {
                "surface_goal": "survive academy ranking",
                "hidden_goal": "prove the ranking system is edited",
                "true_need": "belonging is not permission",
                "false_need": "worth can be revoked by public failure",
            },
            "memory_records": [
                {"memory_id": "mem_core", "content": "public failure and family secret memory"}
            ],
        },
        "power": {
            "skill_ontology": {
                "skill_family": "cognitive_inference",
                "skill_subtype": "pattern_detection",
                "cost_family": ["mental_fatigue"],
            },
            "adaptability_profile": {
                "adaptability_family": "earned_moral_breakthrough",
                "cost_model": "identity instability after breakthrough",
            },
        },
        "destiny": {
            "destiny_profile": {
                "destiny_family": "power_flow_destiny",
            }
        },
        "relationships": {
            "relationship_readiness_profile": {
                "relationship_readiness_family": "high_loyalty_power_broker_readiness",
                "trust_model": "trust requires truth protection without weaponization",
            }
        },
        "dialogue": {
            "dialogue_voice_profile": {
                "voice_family": "controlled_subtext_voice",
            }
        },
        "validation": {
            "quality_report": {
                "overall_quality_score": 0.84,
                "quality_tier": "strong_character_ready",
            },
            "originality_report": {
                "overall_originality_score": 0.78,
                "novelty_score": 0.82,
            },
            "consistency_report": {
                "overall_consistency_score": 0.9,
            },
            "anti_genericity_report": {
                "genericity_risk_score": 0.18,
            },
        },
    }


def sample_world_contract():
    return {
        "contract_id": "worldchar_velmora",
        "world_id": "world_velmora",
        "social_classes": ["erased", "academy_sponsored", "old_nobility"],
        "power_laws": ["relic power requires cost and counterplay"],
        "legal_constraints": ["distrusted family names require sponsor to testify"],
        "faction_constraints": ["Oath Court", "Relic Guild"],
        "education_access_constraints": ["sponsor seat", "exam route", "debt contract"],
        "character_permission_boundaries": [
            "characters must obey class/status access constraints unless an explicit exception route exists",
            "skills and limit-breaks must obey world power laws, costs, counters, and exceptions",
        ],
    }


def sample_character_result_without_metadata():
    return {
        "success": True,
        "engine_name": "character.full_profile_orchestrator",
        "data": {
            "character_full_profile": sample_character_profile(),
        },
        "warnings": [],
        "errors": [],
    }


def sample_character_learning_metadata():
    return {
        "learning_metadata_id": "learn_character_api_001",
        "engine_name": "character.bible_export_engine",
        "target_object_id": "char_kael",
        "target_object_type": "character_bible",
        "ontology_records": [
            {
                "ontology_id": "ont_character_bible_001",
                "ontology_type": "character_bible",
                "name": "Kael Veyran character bible",
                "family": "character_intelligence",
                "subtype": "character_bible",
                "generated_by_engine": "character.bible_export_engine",
                "learned_from_data": False,
            }
        ],
        "learned_type_candidates": [
            {
                "registry_id": "type_character_bible_001",
                "type_name": "character_intelligence:character_bible",
                "type_family": "character_intelligence",
                "type_subfamily": "character_bible",
                "type_scope": "character_generation",
            }
        ],
        "provenance_records": [
            {
                "provenance_id": "prov_character_bible_001",
                "source_name": "human_approved_synthetic",
                "source_type": "synthetic_or_user_generated",
                "dataset_family": "character_bible",
                "usage_allowed": True,
                "human_review_required": False,
                "license_name": "user_owned",
            }
        ],
        "embedding_metadata": {
            "embedding_id": "emb_character_bible_001",
            "embedding_model": "future_embedding_model_not_computed_yet",
            "similarity_tags": ["character_bible", "kael", "velmora"],
            "retrieval_queries": ["Kael Veyran character bible"],
            "novelty_score": 0.8,
            "originality_score": 0.78,
            "similarity_threshold_used": 0.82,
            "vector_computed": False,
        },
        "training_eligibility": {
            "training_eligible": True,
            "human_review_required": False,
            "do_not_train": False,
            "recommended_split": "train",
            "quality_score": 0.84,
            "consistency_score": 0.9,
            "originality_score": 0.78,
            "safety_score": 0.88,
            "rejection_reasons": [],
        },
        "generated_training_labels": {
            "character_bible_ready": True,
            "chunk4_ready": True,
            "quality_score": 0.84,
        },
    }


def sample_character_result_with_metadata():
    return {
        "success": True,
        "engine_name": "character.bible_export_engine",
        "data": {
            "character_bible": sample_character_profile(),
            "learning_metadata": sample_character_learning_metadata(),
        },
        "warnings": [],
        "errors": [],
    }


def build_adapter(tmp_path):
    integration = LearningIntegrationService(
        learning_root=tmp_path / "learning",
        provenance_root=tmp_path / "provenance",
        training_queue_root=tmp_path / "training_queue",
        embedding_root=tmp_path / "embeddings",
    )
    return CharacterLearningAdapter(integration_service=integration)


def test_character_learning_adapter_normalizes_result_without_metadata(tmp_path):
    adapter = build_adapter(tmp_path)

    normalized = adapter.normalize_character_result(
        result_payload=sample_character_result_without_metadata(),
        project_id="proj_ashen",
        universe_id="velmora",
        world_contract=sample_world_contract(),
    )

    assert normalized["character_id"] == "char_kael"
    assert normalized["project_id"] == "proj_ashen"
    assert normalized["universe_id"] == "velmora"
    assert normalized["learning_metadata"]["target_object_id"] == "char_kael"
    assert normalized["learning_metadata"]["target_object_type"] == "character_full_profile"
    assert normalized["learning_metadata"]["training_eligibility"]["training_eligible"] is True
    assert normalized["world_contract_validation"]["world_contract_valid"] is True
    assert normalized["chunk4_handoff_contract"]["handoff_ready"] is True


def test_character_learning_adapter_world_contract_validation_passes(tmp_path):
    adapter = build_adapter(tmp_path)

    report = adapter.validate_character_against_world_contract(
        character_profile=sample_character_profile(),
        world_contract=sample_world_contract(),
    )

    assert report["world_contract_checked"] is True
    assert report["world_contract_valid"] is True
    assert report["compatibility_score"] >= 0.8
    assert "social_class" in report["validated_axes"]
    assert "family_name_status" in report["validated_axes"]
    assert "skill_power" in report["validated_axes"]


def test_character_learning_adapter_world_contract_validation_catches_erased_without_route(tmp_path):
    adapter = build_adapter(tmp_path)

    profile = sample_character_profile()
    profile["origin"]["family_name_status"] = "erased"
    profile["origin"]["origin_profile"]["family_name_status"] = "erased"
    profile["origin"]["origin_profile"]["education_access"] = ""

    report = adapter.validate_character_against_world_contract(
        character_profile=profile,
        world_contract=sample_world_contract(),
    )

    assert report["world_contract_checked"] is True
    assert report["world_contract_valid"] is False
    assert report["violations"]


def test_character_learning_adapter_chunk4_handoff(tmp_path):
    adapter = build_adapter(tmp_path)

    handoff = adapter.build_chunk4_handoff_contract(
        character_id="char_kael",
        character_profile=sample_character_profile(),
    )

    assert handoff["character_id"] == "char_kael"
    assert handoff["handoff_ready"] is True
    assert "friendship simulation" in handoff["chunk4_usage"]
    assert handoff["relationship_readiness"]
    assert handoff["dialogue_voice"]
    assert handoff["psychology"]
    assert handoff["memory_records"]


def test_character_learning_adapter_quality_gates_pass_for_good_character(tmp_path):
    adapter = build_adapter(tmp_path)

    normalized = adapter.normalize_character_result(
        result_payload=sample_character_result_with_metadata(),
        project_id="proj_ashen",
        universe_id="velmora",
        world_contract=sample_world_contract(),
    )

    gate = adapter.evaluate_character_learning_quality_gates(normalized)

    assert gate["can_register_learning"] is True
    assert gate["can_enqueue_training"] is True
    assert gate["quality_score"] == 0.84
    assert gate["originality_score"] == 0.78
    assert gate["consistency_score"] == 0.9
    assert gate["source_allowed"] is True
    assert gate["world_contract_valid"] is True
    assert gate["chunk4_handoff_ready"] is True


def test_character_learning_adapter_quality_gates_block_bad_source(tmp_path):
    adapter = build_adapter(tmp_path)

    result = sample_character_result_with_metadata()
    result["data"]["learning_metadata"]["provenance_records"][0]["usage_allowed"] = False
    result["data"]["learning_metadata"]["provenance_records"][0]["human_review_required"] = True

    normalized = adapter.normalize_character_result(
        result_payload=result,
        project_id="proj_ashen",
        universe_id="velmora",
        world_contract=sample_world_contract(),
    )

    gate = adapter.evaluate_character_learning_quality_gates(normalized)

    assert gate["can_register_learning"] is False
    assert "source provenance is not approved for learning registration" in gate["blockers"]


def test_character_learning_adapter_registers_character_result_with_synthesized_metadata(tmp_path):
    adapter = build_adapter(tmp_path)

    result = adapter.register_character_engine_result(
        result_payload=sample_character_result_without_metadata(),
        project_id="proj_ashen",
        universe_id="velmora",
        world_contract=sample_world_contract(),
    )

    assert result["success"] is True
    assert result["registered"] is True
    assert result["character_id"] == "char_kael"
    assert result["quality_gate_report"]["can_register_learning"] is True
    assert result["learning_registration"]["registered"] is True
    assert result["learning_registration"]["embedding_registered"] is True
    assert result["learning_registration"]["training_enqueued"] is True


def test_character_learning_adapter_registers_character_result_with_existing_metadata(tmp_path):
    adapter = build_adapter(tmp_path)

    result = adapter.register_character_engine_result(
        result_payload=sample_character_result_with_metadata(),
        project_id="proj_ashen",
        universe_id="velmora",
        world_contract=sample_world_contract(),
    )

    assert result["success"] is True
    assert result["registered"] is True
    assert result["learning_registration"]["learning_registry"]["metadata_id"] == "learn_character_api_001"
    assert result["learning_registration"]["provenance_registered"] == 1
    assert result["learning_registration"]["embedding_registered"] is True
    assert result["learning_registration"]["training_enqueued"] is True


def test_character_learning_adapter_rejects_registration_when_gate_fails(tmp_path):
    adapter = build_adapter(tmp_path)

    bad = sample_character_result_without_metadata()
    bad["data"]["character_full_profile"]["validation"]["quality_report"]["overall_quality_score"] = 0.2
    bad["data"]["character_full_profile"]["validation"]["originality_report"]["overall_originality_score"] = 0.2
    bad["data"]["character_full_profile"]["validation"]["consistency_report"]["overall_consistency_score"] = 0.2

    result = adapter.register_character_engine_result(
        result_payload=bad,
        project_id="proj_ashen",
        universe_id="velmora",
        world_contract=sample_world_contract(),
        enforce_quality_gates=True,
    )

    assert result["success"] is True
    assert result["registered"] is False
    assert result["reason"] == "character_learning_quality_gate_failed"
    assert result["quality_gate_report"]["blockers"]


def test_character_learning_adapter_registers_character_profile_learning_metadata(tmp_path):
    adapter = build_adapter(tmp_path)

    profile = {
        "character_id": "char_kael",
        "character_full_profile": sample_character_profile(),
        "learning": {
            "character_bible_learning_metadata": sample_character_learning_metadata(),
        },
    }

    result = adapter.register_character_profile(
        character_profile=profile,
        project_id="proj_ashen",
        universe_id="velmora",
        world_contract=sample_world_contract(),
    )

    assert result["success"] is True
    assert result["registered"] is True
    assert result["learning_registration"]["metadata_found"] == 1
    assert result["learning_registration"]["registered_count"] == 1


def test_character_learning_adapter_partial_world_contract_is_allowed_with_warning(tmp_path):
    adapter = build_adapter(tmp_path)

    report = adapter.validate_character_against_world_contract(
        character_profile=sample_character_profile(),
        world_contract={},
    )

    assert report["world_contract_checked"] is False
    assert report["world_contract_valid"] is True
    assert report["warnings"]

from backend.app.services.character_learning_metadata_verifier import CharacterLearningMetadataVerifier


def sample_world_contract():
    return {
        "contract_id": "worldchar_velmora",
        "world_id": "world_velmora",
        "social_classes": ["erased", "academy_sponsored", "old_nobility"],
        "power_laws": ["relic power requires cost and counterplay"],
        "legal_constraints": ["distrusted family names require sponsor to testify"],
        "education_access_constraints": ["sponsor seat", "exam route", "debt contract"],
        "character_permission_boundaries": [
            "characters must obey class/status access constraints unless an explicit exception route exists",
            "skills and limit-breaks must obey world power laws, costs, counters, and exceptions",
        ],
    }


def sample_character_profile():
    return {
        "character_id": "char_kael",
        "identity": {
            "character_id": "char_kael",
            "name": "Kael Veyran",
            "role": "protagonist",
        },
        "origin": {
            "social_class": "academy_sponsored",
            "family_name_status": "distrusted",
            "origin_profile": {
                "education_access": "conditional sponsor seat",
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
            },
            "memory_records": [
                {"memory_id": "mem_core", "content": "public failure and family secret memory"}
            ],
        },
        "power": {
            "skill_ontology": {
                "skill_family": "cognitive_inference",
            },
            "adaptability_profile": {
                "cost_model": "identity instability after breakthrough",
            },
        },
        "relationships": {
            "relationship_readiness_profile": {
                "relationship_readiness_family": "high_loyalty_power_broker_readiness",
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
            },
            "originality_report": {
                "overall_originality_score": 0.78,
            },
            "consistency_report": {
                "overall_consistency_score": 0.9,
            },
            "anti_genericity_report": {
                "genericity_risk_score": 0.18,
            },
        },
    }


def complete_learning_metadata():
    return {
        "learning_metadata_id": "learn_character_verify_001",
        "engine_name": "character.bible_export_engine",
        "target_object_id": "char_kael",
        "target_object_type": "character_bible",
        "ontology_records": [
            {
                "ontology_id": "ont_character_verify_001",
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
                "registry_id": "type_character_verify_001",
                "type_name": "character_intelligence:character_bible",
                "type_family": "character_intelligence",
                "type_subfamily": "character_bible",
                "type_scope": "character_generation",
            }
        ],
        "provenance_records": [
            {
                "provenance_id": "prov_character_verify_001",
                "source_name": "human_approved_synthetic",
                "source_type": "synthetic_or_user_generated",
                "dataset_family": "character_bible",
                "usage_allowed": True,
                "human_review_required": False,
                "license_name": "user_owned",
            }
        ],
        "embedding_metadata": {
            "embedding_id": "emb_character_verify_001",
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


def test_verifier_accepts_complete_character_metadata():
    verifier = CharacterLearningMetadataVerifier()

    result = verifier.verify_character_result(
        result_payload={
            "success": True,
            "engine_name": "character.bible_export_engine",
            "data": {
                "character_bible": sample_character_profile(),
                "learning_metadata": complete_learning_metadata(),
            },
        },
        project_id="proj_ashen",
        universe_id="velmora",
        world_contract=sample_world_contract(),
    )

    assert result["success"] is True
    assert result["metadata_present"] is True
    assert result["metadata_synthesized"] is False
    assert result["metadata_completeness_report"]["complete"] is True
    assert result["ontology_report"]["character_ontology_ready"] is True
    assert result["provenance_report"]["provenance_ready"] is True
    assert result["embedding_report"]["future_vectorization_ready"] is True
    assert result["training_report"]["training_eligible"] is True
    assert result["character_depth_report"]["character_depth_ready"] is True
    assert result["world_contract_report"]["world_contract_valid"] is True
    assert result["chunk4_handoff_report"]["chunk4_ready"] is True
    assert result["readiness_report"]["global_learning_ready"] is True
    assert result["readiness_report"]["training_queue_ready"] is True


def test_verifier_synthesizes_missing_metadata_when_allowed():
    verifier = CharacterLearningMetadataVerifier()

    result = verifier.verify_character_result(
        result_payload={
            "success": True,
            "engine_name": "character.full_profile_orchestrator",
            "data": {
                "character_full_profile": sample_character_profile(),
            },
        },
        project_id="proj_ashen",
        universe_id="velmora",
        world_contract=sample_world_contract(),
        allow_synthesis=True,
    )

    assert result["metadata_present"] is False
    assert result["metadata_synthesized"] is True
    assert result["metadata_completeness_report"]["complete"] is True
    assert result["readiness_report"]["global_learning_ready"] is True
    assert result["readiness_report"]["training_queue_ready"] is True
    assert result["normalized_result_payload"]["data"]["learning_metadata"]["target_object_id"] == "char_kael"


def test_verifier_blocks_when_synthesis_disabled_and_metadata_missing():
    verifier = CharacterLearningMetadataVerifier()

    result = verifier.verify_character_result(
        result_payload={
            "success": True,
            "engine_name": "character.full_profile_orchestrator",
            "data": {
                "character_full_profile": sample_character_profile(),
            },
        },
        world_contract=sample_world_contract(),
        allow_synthesis=False,
    )

    assert result["metadata_present"] is False
    assert result["metadata_synthesized"] is False
    assert result["metadata_completeness_report"]["complete"] is False
    assert result["readiness_report"]["global_learning_ready"] is False
    assert "metadata incomplete" in result["readiness_report"]["blockers"]


def test_verifier_detects_bad_provenance():
    verifier = CharacterLearningMetadataVerifier()

    metadata = complete_learning_metadata()
    metadata["provenance_records"][0]["usage_allowed"] = False
    metadata["provenance_records"][0]["human_review_required"] = True

    result = verifier.verify_character_result(
        result_payload={
            "success": True,
            "engine_name": "character.bible_export_engine",
            "data": {
                "character_bible": sample_character_profile(),
                "learning_metadata": metadata,
            },
        },
        world_contract=sample_world_contract(),
    )

    assert result["provenance_report"]["provenance_ready"] is False
    assert result["readiness_report"]["global_learning_ready"] is False
    assert "approved provenance missing" in result["readiness_report"]["blockers"]


def test_verifier_detects_world_contract_violation():
    verifier = CharacterLearningMetadataVerifier()

    profile = sample_character_profile()
    profile["origin"]["family_name_status"] = "erased"
    profile["origin"]["origin_profile"]["family_name_status"] = "erased"
    profile["origin"]["origin_profile"]["education_access"] = ""

    result = verifier.verify_character_result(
        result_payload={
            "success": True,
            "engine_name": "character.bible_export_engine",
            "data": {
                "character_bible": profile,
                "learning_metadata": complete_learning_metadata(),
            },
        },
        world_contract=sample_world_contract(),
    )

    assert result["world_contract_report"]["world_contract_valid"] is False
    assert result["readiness_report"]["global_learning_ready"] is False
    assert "character violates world contract" in result["readiness_report"]["blockers"]


def test_verifier_detects_low_training_scores():
    verifier = CharacterLearningMetadataVerifier()

    metadata = complete_learning_metadata()
    metadata["training_eligibility"]["quality_score"] = 0.2
    metadata["training_eligibility"]["consistency_score"] = 0.2
    metadata["training_eligibility"]["originality_score"] = 0.2

    result = verifier.verify_character_result(
        result_payload={
            "success": True,
            "engine_name": "character.bible_export_engine",
            "data": {
                "character_bible": sample_character_profile(),
                "learning_metadata": metadata,
            },
        },
        world_contract=sample_world_contract(),
    )

    assert result["readiness_report"]["training_queue_ready"] is False
    assert "quality below training threshold" in result["readiness_report"]["blockers"]
    assert "consistency below training threshold" in result["readiness_report"]["blockers"]
    assert "originality below training threshold" in result["readiness_report"]["blockers"]


def test_verifier_profile_metadata_extraction():
    verifier = CharacterLearningMetadataVerifier()

    result = verifier.verify_character_profile(
        character_profile={
            "character_id": "char_kael",
            "character_full_profile": sample_character_profile(),
            "learning": {
                "character_bible_learning_metadata": complete_learning_metadata(),
            },
        },
        project_id="proj_ashen",
        universe_id="velmora",
        world_contract=sample_world_contract(),
    )

    assert result["success"] is True
    assert result["metadata_found"] == 1
    assert result["profile_learning_ready"] is True
    assert result["character_depth_report"]["character_depth_ready"] is True
    assert result["chunk4_handoff_report"]["chunk4_ready"] is True


def test_verifier_many_character_results():
    verifier = CharacterLearningMetadataVerifier()

    report = verifier.verify_many_character_results(
        result_payloads=[
            {
                "success": True,
                "engine_name": "character.bible_export_engine",
                "data": {
                    "character_bible": sample_character_profile(),
                    "learning_metadata": complete_learning_metadata(),
                },
            },
            {
                "success": True,
                "engine_name": "character.full_profile_orchestrator",
                "data": {
                    "character_full_profile": sample_character_profile(),
                },
            },
        ],
        project_id="proj_ashen",
        universe_id="velmora",
        world_contract=sample_world_contract(),
    )

    assert report["success"] is True
    assert report["checked_count"] == 2
    assert report["global_learning_ready_count"] == 2
    assert report["training_ready_count"] == 2
    assert report["chunk4_ready_count"] == 2
    assert report["synthesized_count"] == 1

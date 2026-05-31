from backend.app.services.world_learning_metadata_verifier import WorldLearningMetadataVerifier


def sample_world_profile():
    return {
        "world_id": "world_velmora",
        "world_name": "Velmora",
        "quality_score": 0.82,
        "originality_score": 0.76,
        "consistency_score": 0.84,
        "social_classes": ["erased", "academy_sponsored", "old_nobility"],
        "magic_rules": ["relic power requires contract cost"],
        "legal_constraints": ["erased names require sponsor to testify"],
        "factions": ["Oath Court", "Relic Guild"],
        "academy_access": ["sponsor seat", "exam route"],
    }


def complete_learning_metadata():
    return {
        "learning_metadata_id": "learn_world_verify_001",
        "engine_name": "world.world_bible_export_engine",
        "target_object_id": "world_velmora",
        "target_object_type": "world_bible",
        "ontology_records": [
            {
                "ontology_id": "ont_world_verify_001",
                "ontology_type": "world_bible",
                "name": "Velmora world bible",
                "family": "world_intelligence",
                "subtype": "world_bible",
                "generated_by_engine": "world.world_bible_export_engine",
                "learned_from_data": False,
            }
        ],
        "learned_type_candidates": [
            {
                "registry_id": "type_world_verify_001",
                "type_name": "world_intelligence:world_bible",
                "type_family": "world_intelligence",
                "type_subfamily": "world_bible",
                "type_scope": "world_generation",
            }
        ],
        "provenance_records": [
            {
                "provenance_id": "prov_world_verify_001",
                "source_name": "human_approved_synthetic",
                "source_type": "synthetic_or_user_generated",
                "dataset_family": "world_bible",
                "usage_allowed": True,
                "human_review_required": False,
                "license_name": "user_owned",
            }
        ],
        "embedding_metadata": {
            "embedding_id": "emb_world_verify_001",
            "embedding_model": "future_embedding_model_not_computed_yet",
            "similarity_tags": ["world_bible", "velmora"],
            "retrieval_queries": ["Velmora world bible"],
            "novelty_score": 0.78,
            "originality_score": 0.76,
            "similarity_threshold_used": 0.82,
            "vector_computed": False,
        },
        "training_eligibility": {
            "training_eligible": True,
            "human_review_required": False,
            "do_not_train": False,
            "recommended_split": "train",
            "quality_score": 0.82,
            "consistency_score": 0.84,
            "originality_score": 0.76,
            "safety_score": 0.88,
            "rejection_reasons": [],
        },
        "generated_training_labels": {
            "world_bible_ready": True,
            "chunk3_ready": True,
            "chunk4_ready": True,
            "quality_score": 0.82,
        },
    }


def test_verifier_accepts_complete_world_metadata():
    verifier = WorldLearningMetadataVerifier()

    result = verifier.verify_world_result(
        result_payload={
            "success": True,
            "engine_name": "world.world_bible_export_engine",
            "data": {
                "world_bible": sample_world_profile(),
                "learning_metadata": complete_learning_metadata(),
            },
        },
        project_id="proj_ashen",
        universe_id="velmora",
    )

    assert result["success"] is True
    assert result["metadata_present"] is True
    assert result["metadata_synthesized"] is False
    assert result["metadata_completeness_report"]["complete"] is True
    assert result["ontology_report"]["world_ontology_ready"] is True
    assert result["provenance_report"]["provenance_ready"] is True
    assert result["embedding_report"]["future_vectorization_ready"] is True
    assert result["training_report"]["training_eligible"] is True
    assert result["world_to_character_contract_report"]["contract_usable"] is True
    assert result["readiness_report"]["global_learning_ready"] is True
    assert result["readiness_report"]["training_queue_ready"] is True


def test_verifier_synthesizes_missing_metadata_when_allowed():
    verifier = WorldLearningMetadataVerifier()

    result = verifier.verify_world_result(
        result_payload={
            "success": True,
            "engine_name": "world.world_orchestrator_engine",
            "data": {
                "world_profile": sample_world_profile(),
            },
        },
        project_id="proj_ashen",
        universe_id="velmora",
        allow_synthesis=True,
    )

    assert result["metadata_present"] is False
    assert result["metadata_synthesized"] is True
    assert result["metadata_completeness_report"]["complete"] is True
    assert result["readiness_report"]["global_learning_ready"] is True
    assert result["readiness_report"]["training_queue_ready"] is True
    assert result["normalized_result_payload"]["data"]["learning_metadata"]["target_object_id"] == "world_velmora"


def test_verifier_blocks_when_synthesis_disabled_and_metadata_missing():
    verifier = WorldLearningMetadataVerifier()

    result = verifier.verify_world_result(
        result_payload={
            "success": True,
            "engine_name": "world.world_orchestrator_engine",
            "data": {
                "world_profile": sample_world_profile(),
            },
        },
        allow_synthesis=False,
    )

    assert result["metadata_present"] is False
    assert result["metadata_synthesized"] is False
    assert result["metadata_completeness_report"]["complete"] is False
    assert result["readiness_report"]["global_learning_ready"] is False
    assert "metadata incomplete" in result["readiness_report"]["blockers"]


def test_verifier_detects_bad_provenance():
    verifier = WorldLearningMetadataVerifier()

    metadata = complete_learning_metadata()
    metadata["provenance_records"][0]["usage_allowed"] = False
    metadata["provenance_records"][0]["human_review_required"] = True

    result = verifier.verify_world_result(
        result_payload={
            "success": True,
            "engine_name": "world.world_bible_export_engine",
            "data": {
                "world_bible": sample_world_profile(),
                "learning_metadata": metadata,
            },
        }
    )

    assert result["provenance_report"]["provenance_ready"] is False
    assert result["readiness_report"]["global_learning_ready"] is False
    assert "approved provenance missing" in result["readiness_report"]["blockers"]


def test_verifier_detects_low_training_scores():
    verifier = WorldLearningMetadataVerifier()

    metadata = complete_learning_metadata()
    metadata["training_eligibility"]["quality_score"] = 0.2
    metadata["training_eligibility"]["consistency_score"] = 0.2
    metadata["training_eligibility"]["originality_score"] = 0.2

    result = verifier.verify_world_result(
        result_payload={
            "success": True,
            "engine_name": "world.world_bible_export_engine",
            "data": {
                "world_bible": sample_world_profile(),
                "learning_metadata": metadata,
            },
        }
    )

    assert result["readiness_report"]["training_queue_ready"] is False
    assert "quality below training threshold" in result["readiness_report"]["blockers"]
    assert "consistency below training threshold" in result["readiness_report"]["blockers"]
    assert "originality below training threshold" in result["readiness_report"]["blockers"]


def test_verifier_many_world_results():
    verifier = WorldLearningMetadataVerifier()

    report = verifier.verify_many_world_results(
        result_payloads=[
            {
                "success": True,
                "engine_name": "world.world_bible_export_engine",
                "data": {
                    "world_bible": sample_world_profile(),
                    "learning_metadata": complete_learning_metadata(),
                },
            },
            {
                "success": True,
                "engine_name": "world.world_orchestrator_engine",
                "data": {
                    "world_profile": sample_world_profile(),
                },
            },
        ],
        project_id="proj_ashen",
        universe_id="velmora",
    )

    assert report["success"] is True
    assert report["checked_count"] == 2
    assert report["global_learning_ready_count"] == 2
    assert report["training_ready_count"] == 2
    assert report["synthesized_count"] == 1

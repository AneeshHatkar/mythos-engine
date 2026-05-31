from backend.app.services.learning_integration import (
    LearningIntegrationService,
    register_engine_learning_output,
)


def sample_learning_metadata(training_eligible=True):
    return {
        "learning_metadata_id": "learn_integration_001",
        "engine_name": "character.quality_scorer",
        "target_object_id": "char_kael",
        "target_object_type": "character_quality",
        "ontology_records": [
            {
                "ontology_id": "ont_quality_001",
                "ontology_type": "character_quality",
                "name": "strong_character_ready",
                "family": "character_quality",
                "subtype": "strong_character_ready",
                "generated_by_engine": "character.quality_scorer",
                "learned_from_data": False,
            }
        ],
        "learned_type_candidates": [
            {
                "registry_id": "type_quality_001",
                "type_name": "character_quality:strong_character_ready",
                "type_family": "character_quality",
                "type_subfamily": "strong_character_ready",
                "type_scope": "character_quality_control",
            }
        ],
        "provenance_records": [
            {
                "provenance_id": "prov_quality_001",
                "source_name": "human_approved_synthetic",
                "source_type": "synthetic_or_user_generated",
                "dataset_family": "character_quality",
                "usage_allowed": True,
                "human_review_required": False,
                "license_name": "user_owned",
            }
        ],
        "embedding_metadata": {
            "embedding_id": "emb_quality_001",
            "embedding_model": "future_embedding_model_not_computed_yet",
            "similarity_tags": ["character_quality", "strong_character_ready"],
            "retrieval_queries": ["strong character quality"],
            "novelty_score": 0.76,
            "originality_score": 0.82,
            "similarity_threshold_used": 0.82,
            "vector_computed": False,
        },
        "training_eligibility": {
            "training_eligible": training_eligible,
            "human_review_required": not training_eligible,
            "do_not_train": not training_eligible,
            "recommended_split": "train" if training_eligible else "human_review_queue",
            "quality_score": 0.84 if training_eligible else 0.42,
            "consistency_score": 0.86,
            "originality_score": 0.82,
            "safety_score": 0.88,
            "rejection_reasons": [] if training_eligible else ["quality below threshold"],
        },
        "generated_training_labels": {
            "quality_tier": "strong_character_ready",
            "training_queue_ready": training_eligible,
        },
    }


def sample_engine_result(training_eligible=True):
    return {
        "success": True,
        "engine_name": "character.quality_scorer",
        "data": {
            "quality_report": {
                "overall_quality_score": 0.84,
            },
            "learning_metadata": sample_learning_metadata(training_eligible=training_eligible),
        },
        "warnings": [],
        "errors": [],
        "generated_object_ids": ["qual_001"],
    }


def test_learning_integration_registers_engine_result(tmp_path):
    service = LearningIntegrationService(
        learning_root=tmp_path / "learning",
        provenance_root=tmp_path / "provenance",
        training_queue_root=tmp_path / "training_queue",
        embedding_root=tmp_path / "embeddings",
    )

    result = service.register_engine_result(
        result_payload=sample_engine_result(training_eligible=True),
        project_id="proj_ashen",
        universe_id="velmora",
    )

    assert result["success"] is True
    assert result["registered"] is True
    assert result["engine_name"] == "character.quality_scorer"
    assert result["provenance_registered"] == 1
    assert result["embedding_registered"] is True
    assert result["training_enqueued"] is True

    summary = service.get_global_learning_summary()

    assert summary["learning_registry"]["counts"]["engine_learning_metadata"] == 1
    assert summary["provenance"]["record_count"] == 1
    assert summary["embedding_registry"]["record_count"] == 1
    assert summary["training_queue"]["record_count"] == 1


def test_learning_integration_skips_result_without_metadata(tmp_path):
    service = LearningIntegrationService(
        learning_root=tmp_path / "learning",
        provenance_root=tmp_path / "provenance",
        training_queue_root=tmp_path / "training_queue",
        embedding_root=tmp_path / "embeddings",
    )

    result = service.register_engine_result(
        result_payload={
            "success": True,
            "engine_name": "character.no_learning_engine",
            "data": {},
        }
    )

    assert result["success"] is True
    assert result["registered"] is False
    assert result["reason"] == "no_learning_metadata_found"


def test_learning_integration_does_not_enqueue_ineligible_training(tmp_path):
    service = LearningIntegrationService(
        learning_root=tmp_path / "learning",
        provenance_root=tmp_path / "provenance",
        training_queue_root=tmp_path / "training_queue",
        embedding_root=tmp_path / "embeddings",
    )

    result = service.register_engine_result(
        result_payload=sample_engine_result(training_eligible=False),
        project_id="proj_ashen",
        universe_id="velmora",
    )

    assert result["registered"] is True
    assert result["training_enqueued"] is False
    assert result["embedding_registered"] is True

    summary = service.get_global_learning_summary()

    assert summary["training_queue"]["record_count"] == 0
    assert summary["learning_registry"]["counts"]["engine_learning_metadata"] == 1


def test_learning_integration_registers_many_engine_results(tmp_path):
    service = LearningIntegrationService(
        learning_root=tmp_path / "learning",
        provenance_root=tmp_path / "provenance",
        training_queue_root=tmp_path / "training_queue",
        embedding_root=tmp_path / "embeddings",
    )

    result = service.register_many_engine_results(
        result_payloads=[
            sample_engine_result(training_eligible=True),
            {
                "success": True,
                "engine_name": "character.no_learning_engine",
                "data": {},
            },
        ],
        project_id="proj_ashen",
        universe_id="velmora",
    )

    assert result["success"] is True
    assert result["attempted"] == 2
    assert result["registered_count"] == 1
    assert result["skipped_count"] == 1
    assert result["training_enqueued_count"] == 1
    assert result["embedding_registered_count"] == 1


def test_learning_integration_extracts_learning_metadata_from_profile(tmp_path):
    service = LearningIntegrationService(
        learning_root=tmp_path / "learning",
        provenance_root=tmp_path / "provenance",
        training_queue_root=tmp_path / "training_queue",
        embedding_root=tmp_path / "embeddings",
    )

    profile = {
        "character_id": "char_kael",
        "validation": {
            "quality_learning_metadata": sample_learning_metadata(training_eligible=True),
        },
        "learning": {
            "learning_metadata_records": {
                "duplicate_quality": sample_learning_metadata(training_eligible=True),
            }
        },
    }

    extracted = service.extract_learning_metadata_from_profile(profile)

    assert len(extracted) == 1
    assert extracted[0]["learning_metadata_id"] == "learn_integration_001"


def test_learning_integration_registers_profile_learning_metadata(tmp_path):
    service = LearningIntegrationService(
        learning_root=tmp_path / "learning",
        provenance_root=tmp_path / "provenance",
        training_queue_root=tmp_path / "training_queue",
        embedding_root=tmp_path / "embeddings",
    )

    profile = {
        "character_id": "char_kael",
        "validation": {
            "quality_learning_metadata": sample_learning_metadata(training_eligible=True),
        },
    }

    result = service.register_profile_learning_metadata(
        profile=profile,
        project_id="proj_ashen",
        universe_id="velmora",
    )

    assert result["success"] is True
    assert result["metadata_found"] == 1
    assert result["registered_count"] == 1
    assert result["training_enqueued_count"] == 1
    assert result["embedding_registered_count"] == 1


def test_register_engine_learning_output_convenience_wrapper(tmp_path):
    result = register_engine_learning_output(
        result_payload=sample_engine_result(training_eligible=True),
        project_id="proj_ashen",
        universe_id="velmora",
        root_dir=tmp_path,
    )

    assert result["success"] is True
    assert result["registered"] is True
    assert result["training_enqueued"] is True

from backend.app.services.learning_integration import LearningIntegrationService
from backend.app.services.world_learning_adapter import WorldLearningAdapter


def sample_world_profile():
    return {
        "world_id": "world_velmora",
        "world_name": "Velmora",
        "quality_score": 0.82,
        "originality_score": 0.76,
        "consistency_score": 0.84,
        "social_classes": ["erased", "academy_sponsored", "old_nobility"],
        "magic_rules": ["relic power requires contract cost", "memory magic leaves social trace"],
        "legal_constraints": ["erased family names cannot testify without sponsor"],
        "factions": ["Oath Court", "Relic Guild", "Archive Church"],
        "academy_access": ["sponsor seat", "exam route", "debt contract"],
        "economy": ["relic labor economy", "memory-tax bureaucracy"],
        "culture": ["public names carry legal trust"],
        "geography": ["capital rings", "outer academy district"],
    }


def sample_world_result_without_learning_metadata():
    return {
        "success": True,
        "engine_name": "world.world_orchestrator_engine",
        "data": {
            "world_profile": sample_world_profile(),
        },
        "warnings": [],
        "errors": [],
    }


def sample_world_learning_metadata():
    return {
        "learning_metadata_id": "learn_world_api_001",
        "engine_name": "world.world_bible_export_engine",
        "target_object_id": "world_velmora",
        "target_object_type": "world_bible",
        "ontology_records": [
            {
                "ontology_id": "ont_world_bible_001",
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
                "registry_id": "type_world_bible_001",
                "type_name": "world_intelligence:world_bible",
                "type_family": "world_intelligence",
                "type_subfamily": "world_bible",
                "type_scope": "world_generation",
            }
        ],
        "provenance_records": [
            {
                "provenance_id": "prov_world_bible_001",
                "source_name": "human_approved_synthetic",
                "source_type": "synthetic_or_user_generated",
                "dataset_family": "world_bible",
                "usage_allowed": True,
                "human_review_required": False,
                "license_name": "user_owned",
            }
        ],
        "embedding_metadata": {
            "embedding_id": "emb_world_bible_001",
            "embedding_model": "future_embedding_model_not_computed_yet",
            "similarity_tags": ["world_bible", "velmora"],
            "retrieval_queries": ["Velmora world bible rules factions social classes"],
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
        },
    }


def sample_world_result_with_learning_metadata():
    return {
        "success": True,
        "engine_name": "world.world_bible_export_engine",
        "data": {
            "world_bible": sample_world_profile(),
            "learning_metadata": sample_world_learning_metadata(),
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
    return WorldLearningAdapter(integration_service=integration)


def test_world_learning_adapter_normalizes_result_without_metadata(tmp_path):
    adapter = build_adapter(tmp_path)

    normalized = adapter.normalize_world_result(
        result_payload=sample_world_result_without_learning_metadata(),
        project_id="proj_ashen",
        universe_id="velmora",
    )

    assert normalized["world_id"] == "world_velmora"
    assert normalized["project_id"] == "proj_ashen"
    assert normalized["universe_id"] == "velmora"
    assert normalized["learning_metadata"]["target_object_id"] == "world_velmora"
    assert normalized["learning_metadata"]["target_object_type"] == "world_rule_system"
    assert normalized["learning_metadata"]["training_eligibility"]["training_eligible"] is True
    assert normalized["world_to_character_contract"]["world_id"] == "world_velmora"


def test_world_learning_adapter_builds_world_to_character_contract(tmp_path):
    adapter = build_adapter(tmp_path)

    contract = adapter.build_world_to_character_contract(sample_world_profile())

    assert contract["world_id"] == "world_velmora"
    assert "erased" in contract["social_classes"]
    assert "relic power requires contract cost" in contract["power_laws"]
    assert "erased family names cannot testify without sponsor" in contract["legal_constraints"]
    assert "Oath Court" in contract["faction_constraints"]
    assert "sponsor seat" in contract["education_access_constraints"]
    assert contract["character_permission_boundaries"]
    assert contract["contract_complete"] is True


def test_world_learning_adapter_quality_gates_pass_for_good_world(tmp_path):
    adapter = build_adapter(tmp_path)

    normalized = adapter.normalize_world_result(
        result_payload=sample_world_result_with_learning_metadata(),
        project_id="proj_ashen",
        universe_id="velmora",
    )

    gate = adapter.evaluate_world_learning_quality_gates(normalized)

    assert gate["can_register_learning"] is True
    assert gate["can_enqueue_training"] is True
    assert gate["quality_score"] == 0.82
    assert gate["originality_score"] == 0.76
    assert gate["consistency_score"] == 0.84
    assert gate["source_allowed"] is True
    assert gate["contract_quality_report"]["contract_usable"] is True


def test_world_learning_adapter_quality_gates_block_bad_source(tmp_path):
    adapter = build_adapter(tmp_path)

    result = sample_world_result_with_learning_metadata()
    result["data"]["learning_metadata"]["provenance_records"][0]["usage_allowed"] = False
    result["data"]["learning_metadata"]["provenance_records"][0]["human_review_required"] = True

    normalized = adapter.normalize_world_result(
        result_payload=result,
        project_id="proj_ashen",
        universe_id="velmora",
    )

    gate = adapter.evaluate_world_learning_quality_gates(normalized)

    assert gate["can_register_learning"] is False
    assert "source provenance is not approved for learning registration" in gate["blockers"]


def test_world_learning_adapter_registers_world_result_with_synthesized_metadata(tmp_path):
    adapter = build_adapter(tmp_path)

    result = adapter.register_world_engine_result(
        result_payload=sample_world_result_without_learning_metadata(),
        project_id="proj_ashen",
        universe_id="velmora",
    )

    assert result["success"] is True
    assert result["registered"] is True
    assert result["world_id"] == "world_velmora"
    assert result["quality_gate_report"]["can_register_learning"] is True
    assert result["learning_registration"]["registered"] is True
    assert result["learning_registration"]["embedding_registered"] is True
    assert result["learning_registration"]["training_enqueued"] is True


def test_world_learning_adapter_registers_world_result_with_existing_metadata(tmp_path):
    adapter = build_adapter(tmp_path)

    result = adapter.register_world_engine_result(
        result_payload=sample_world_result_with_learning_metadata(),
        project_id="proj_ashen",
        universe_id="velmora",
    )

    assert result["success"] is True
    assert result["registered"] is True
    assert result["learning_registration"]["learning_registry"]["metadata_id"] == "learn_world_api_001"
    assert result["learning_registration"]["provenance_registered"] == 1
    assert result["learning_registration"]["embedding_registered"] is True
    assert result["learning_registration"]["training_enqueued"] is True


def test_world_learning_adapter_rejects_registration_when_gate_fails(tmp_path):
    adapter = build_adapter(tmp_path)

    bad = sample_world_result_without_learning_metadata()
    bad["data"]["world_profile"]["quality_score"] = 0.2
    bad["data"]["world_profile"]["originality_score"] = 0.2
    bad["data"]["world_profile"]["consistency_score"] = 0.2

    result = adapter.register_world_engine_result(
        result_payload=bad,
        project_id="proj_ashen",
        universe_id="velmora",
        enforce_quality_gates=True,
    )

    assert result["success"] is True
    assert result["registered"] is False
    assert result["reason"] == "world_learning_quality_gate_failed"
    assert result["quality_gate_report"]["blockers"]


def test_world_learning_adapter_registers_world_profile_learning_metadata(tmp_path):
    adapter = build_adapter(tmp_path)

    profile = {
        "world_id": "world_velmora",
        "world_profile": sample_world_profile(),
        "learning": {
            "world_bible_learning_metadata": sample_world_learning_metadata(),
        },
    }

    result = adapter.register_world_profile(
        world_profile=profile,
        project_id="proj_ashen",
        universe_id="velmora",
    )

    assert result["success"] is True
    assert result["registered"] is True
    assert result["learning_registration"]["metadata_found"] == 1
    assert result["learning_registration"]["registered_count"] == 1


def test_world_learning_adapter_contract_reports_missing_sections(tmp_path):
    adapter = build_adapter(tmp_path)

    contract = adapter.build_world_to_character_contract(
        {
            "world_id": "world_empty",
            "world_name": "Empty World",
        }
    )

    report = adapter._contract_quality_report(contract)

    assert report["contract_usable"] is False
    assert "social_classes" in report["missing_sections"]
    assert "power_laws" in report["missing_sections"]

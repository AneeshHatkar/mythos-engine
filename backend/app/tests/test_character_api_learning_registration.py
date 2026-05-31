from fastapi.testclient import TestClient

from backend.app.main import app


client = TestClient(app)


def sample_world_contract():
    return {
        "contract_id": "worldchar_api_velmora",
        "world_id": "world_api_velmora",
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
        "character_id": "char_api_kael",
        "identity": {
            "character_id": "char_api_kael",
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


def sample_character_result():
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
        "learning_metadata_id": "learn_character_api_route_001",
        "engine_name": "character.bible_export_engine",
        "target_object_id": "char_api_kael",
        "target_object_type": "character_bible",
        "ontology_records": [
            {
                "ontology_id": "ont_character_api_route_001",
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
                "registry_id": "type_character_api_route_001",
                "type_name": "character_intelligence:character_bible",
                "type_family": "character_intelligence",
                "type_subfamily": "character_bible",
                "type_scope": "character_generation",
            }
        ],
        "provenance_records": [
            {
                "provenance_id": "prov_character_api_route_001",
                "source_name": "human_approved_synthetic",
                "source_type": "synthetic_or_user_generated",
                "dataset_family": "character_bible",
                "usage_allowed": True,
                "human_review_required": False,
                "license_name": "user_owned",
            }
        ],
        "embedding_metadata": {
            "embedding_id": "emb_character_api_route_001",
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


def test_character_learning_world_contract_check_route():
    response = client.post(
        "/character/engines/learning/world-contract-check",
        json={
            "character_profile": sample_character_profile(),
            "world_contract": sample_world_contract(),
        },
    )

    assert response.status_code == 200

    data = response.json()["data"]

    assert data["world_contract_checked"] is True
    assert data["world_contract_valid"] is True
    assert data["compatibility_score"] >= 0.8


def test_character_learning_chunk4_handoff_route():
    response = client.post(
        "/character/engines/learning/chunk4-handoff",
        json={
            "character_id": "char_api_kael",
            "character_profile": sample_character_profile(),
        },
    )

    assert response.status_code == 200

    data = response.json()["data"]

    assert data["character_id"] == "char_api_kael"
    assert data["handoff_ready"] is True
    assert data["relationship_readiness"]
    assert data["dialogue_voice"]
    assert data["psychology"]
    assert data["memory_records"]


def test_character_learning_verify_route_with_synthesized_metadata():
    response = client.post(
        "/character/engines/learning/verify",
        json={
            "result_payload": sample_character_result(),
            "project_id": "proj_api_character_learning",
            "universe_id": "velmora_api",
            "world_contract": sample_world_contract(),
            "allow_synthesis": True,
        },
    )

    assert response.status_code == 200

    data = response.json()["data"]

    assert data["metadata_synthesized"] is True
    assert data["readiness_report"]["global_learning_ready"] is True
    assert data["readiness_report"]["training_queue_ready"] is True
    assert data["readiness_report"]["chunk4_ready"] is True


def test_character_learning_register_result_route_with_synthesized_metadata():
    response = client.post(
        "/character/engines/learning/register-result",
        json={
            "result_payload": sample_character_result(),
            "project_id": "proj_api_character_learning",
            "universe_id": "velmora_api",
            "world_contract": sample_world_contract(),
            "enforce_quality_gates": True,
        },
    )

    assert response.status_code == 200

    data = response.json()["data"]

    assert data["success"] is True
    assert data["registered"] is True
    assert data["character_id"] == "char_api_kael"
    assert data["quality_gate_report"]["can_register_learning"] is True
    assert data["learning_registration"]["registered"] is True
    assert data["learning_registration"]["embedding_registered"] is True
    assert data["learning_registration"]["training_enqueued"] is True


def test_character_learning_register_result_route_with_existing_metadata():
    result = sample_character_result()
    result["engine_name"] = "character.bible_export_engine"
    result["data"]["learning_metadata"] = sample_character_learning_metadata()

    response = client.post(
        "/character/engines/learning/register-result",
        json={
            "result_payload": result,
            "project_id": "proj_api_character_learning",
            "universe_id": "velmora_api",
            "world_contract": sample_world_contract(),
            "enforce_quality_gates": True,
        },
    )

    assert response.status_code == 200

    data = response.json()["data"]

    assert data["registered"] is True
    assert data["learning_registration"]["learning_registry"]["metadata_id"] == "learn_character_api_route_001"


def test_character_learning_register_profile_route():
    response = client.post(
        "/character/engines/learning/register-profile",
        json={
            "character_profile": {
                "character_id": "char_api_kael_profile",
                "character_full_profile": sample_character_profile(),
                "learning": {
                    "character_bible_learning_metadata": {
                        **sample_character_learning_metadata(),
                        "learning_metadata_id": "learn_character_profile_api_001",
                        "target_object_id": "char_api_kael_profile",
                        "ontology_records": [],
                        "learned_type_candidates": [],
                        "provenance_records": [],
                        "embedding_metadata": {
                            **sample_character_learning_metadata()["embedding_metadata"],
                            "embedding_id": "emb_character_profile_api_001",
                        },
                    },
                },
            },
            "project_id": "proj_api_character_learning",
            "universe_id": "velmora_api",
            "world_contract": sample_world_contract(),
            "enforce_quality_gates": True,
        },
    )

    assert response.status_code == 200

    data = response.json()["data"]

    assert data["success"] is True
    assert data["registered"] is True
    assert data["learning_registration"]["metadata_found"] == 1


def test_character_learning_register_result_blocks_low_quality_character():
    bad = sample_character_result()
    bad["data"]["character_full_profile"]["validation"]["quality_report"]["overall_quality_score"] = 0.2
    bad["data"]["character_full_profile"]["validation"]["originality_report"]["overall_originality_score"] = 0.2
    bad["data"]["character_full_profile"]["validation"]["consistency_report"]["overall_consistency_score"] = 0.2

    response = client.post(
        "/character/engines/learning/register-result",
        json={
            "result_payload": bad,
            "project_id": "proj_api_character_learning",
            "universe_id": "velmora_api",
            "world_contract": sample_world_contract(),
            "enforce_quality_gates": True,
        },
    )

    assert response.status_code == 200

    data = response.json()["data"]

    assert data["registered"] is False
    assert data["reason"] == "character_learning_quality_gate_failed"
    assert data["quality_gate_report"]["blockers"]


def test_learning_summary_sees_character_registration():
    response = client.get("/learning/summary")

    assert response.status_code == 200

    data = response.json()["data"]

    assert data["learning_registry"]["counts"]["engine_learning_metadata"] >= 1
    assert data["embedding_registry"]["record_count"] >= 1

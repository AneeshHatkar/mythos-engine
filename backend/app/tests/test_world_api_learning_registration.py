from fastapi.testclient import TestClient

from backend.app.main import app


client = TestClient(app)


def sample_world_profile():
    return {
        "world_id": "world_api_velmora",
        "world_name": "Velmora API",
        "quality_score": 0.82,
        "originality_score": 0.76,
        "consistency_score": 0.84,
        "social_classes": ["erased", "academy_sponsored", "old_nobility"],
        "magic_rules": ["relic power requires contract cost"],
        "legal_constraints": ["erased names require sponsor to testify"],
        "factions": ["Oath Court", "Relic Guild"],
        "academy_access": ["sponsor seat", "exam route"],
        "economy": ["relic labor economy"],
        "culture": ["public names carry legal trust"],
        "geography": ["capital rings"],
    }


def sample_world_result():
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
        "learning_metadata_id": "learn_world_api_route_001",
        "engine_name": "world.world_bible_export_engine",
        "target_object_id": "world_api_velmora",
        "target_object_type": "world_bible",
        "ontology_records": [
            {
                "ontology_id": "ont_world_api_route_001",
                "ontology_type": "world_bible",
                "name": "Velmora API world bible",
                "family": "world_intelligence",
                "subtype": "world_bible",
                "generated_by_engine": "world.world_bible_export_engine",
                "learned_from_data": False,
            }
        ],
        "learned_type_candidates": [
            {
                "registry_id": "type_world_api_route_001",
                "type_name": "world_intelligence:world_bible",
                "type_family": "world_intelligence",
                "type_subfamily": "world_bible",
                "type_scope": "world_generation",
            }
        ],
        "provenance_records": [
            {
                "provenance_id": "prov_world_api_route_001",
                "source_name": "human_approved_synthetic",
                "source_type": "synthetic_or_user_generated",
                "dataset_family": "world_bible",
                "usage_allowed": True,
                "human_review_required": False,
                "license_name": "user_owned",
            }
        ],
        "embedding_metadata": {
            "embedding_id": "emb_world_api_route_001",
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
        },
    }


def test_world_learning_contract_route():
    response = client.post(
        "/world/engines/learning/contract",
        json={
            "world_profile": sample_world_profile(),
            "project_id": "proj_api_world_learning",
            "universe_id": "velmora_api",
        },
    )

    assert response.status_code == 200

    data = response.json()["data"]["world_to_character_contract"]

    assert data["world_id"] == "world_api_velmora"
    assert "erased" in data["social_classes"]
    assert "relic power requires contract cost" in data["power_laws"]
    assert data["character_permission_boundaries"]


def test_world_learning_register_result_route_with_synthesized_metadata():
    response = client.post(
        "/world/engines/learning/register-result",
        json={
            "result_payload": sample_world_result(),
            "project_id": "proj_api_world_learning",
            "universe_id": "velmora_api",
            "enforce_quality_gates": True,
        },
    )

    assert response.status_code == 200

    data = response.json()["data"]

    assert data["success"] is True
    assert data["registered"] is True
    assert data["world_id"] == "world_api_velmora"
    assert data["quality_gate_report"]["can_register_learning"] is True
    assert data["learning_registration"]["registered"] is True
    assert data["learning_registration"]["embedding_registered"] is True
    assert data["learning_registration"]["training_enqueued"] is True


def test_world_learning_register_result_route_with_existing_metadata():
    result = sample_world_result()
    result["engine_name"] = "world.world_bible_export_engine"
    result["data"]["learning_metadata"] = sample_world_learning_metadata()

    response = client.post(
        "/world/engines/learning/register-result",
        json={
            "result_payload": result,
            "project_id": "proj_api_world_learning",
            "universe_id": "velmora_api",
            "enforce_quality_gates": True,
        },
    )

    assert response.status_code == 200

    data = response.json()["data"]

    assert data["registered"] is True
    assert data["learning_registration"]["learning_registry"]["metadata_id"] == "learn_world_api_route_001"


def test_world_learning_register_profile_route():
    response = client.post(
        "/world/engines/learning/register-profile",
        json={
            "world_profile": {
                "world_id": "world_api_velmora_profile",
                "world_profile": sample_world_profile(),
                "learning": {
                    "world_bible_learning_metadata": {
                        **sample_world_learning_metadata(),
                        "learning_metadata_id": "learn_world_profile_api_001",
                        "target_object_id": "world_api_velmora_profile",
                        "ontology_records": [],
                        "learned_type_candidates": [],
                        "provenance_records": [],
                        "embedding_metadata": {
                            **sample_world_learning_metadata()["embedding_metadata"],
                            "embedding_id": "emb_world_profile_api_001",
                        },
                    },
                },
            },
            "project_id": "proj_api_world_learning",
            "universe_id": "velmora_api",
            "enforce_quality_gates": True,
        },
    )

    assert response.status_code == 200

    data = response.json()["data"]

    assert data["success"] is True
    assert data["registered"] is True
    assert data["learning_registration"]["metadata_found"] == 1


def test_world_learning_register_result_blocks_low_quality_world():
    bad = sample_world_result()
    bad["data"]["world_profile"]["quality_score"] = 0.2
    bad["data"]["world_profile"]["originality_score"] = 0.2
    bad["data"]["world_profile"]["consistency_score"] = 0.2

    response = client.post(
        "/world/engines/learning/register-result",
        json={
            "result_payload": bad,
            "project_id": "proj_api_world_learning",
            "universe_id": "velmora_api",
            "enforce_quality_gates": True,
        },
    )

    assert response.status_code == 200

    data = response.json()["data"]

    assert data["registered"] is False
    assert data["reason"] == "world_learning_quality_gate_failed"
    assert data["quality_gate_report"]["blockers"]


def test_learning_summary_sees_world_registration():
    response = client.get("/learning/summary")

    assert response.status_code == 200

    data = response.json()["data"]

    assert data["learning_registry"]["counts"]["engine_learning_metadata"] >= 1
    assert data["embedding_registry"]["record_count"] >= 1

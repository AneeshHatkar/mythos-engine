from fastapi.testclient import TestClient

from backend.app.main import app


client = TestClient(app)


def sample_training_eligibility():
    return {
        "training_eligible": True,
        "human_review_required": False,
        "do_not_train": False,
        "recommended_split": "train",
        "quality_score": 0.84,
        "consistency_score": 0.86,
        "originality_score": 0.82,
        "safety_score": 0.88,
        "rejection_reasons": [],
    }


def sample_learning_metadata():
    return {
        "learning_metadata_id": "learn_api_001",
        "engine_name": "character.quality_scorer",
        "target_object_id": "char_api_kael",
        "target_object_type": "character_quality",
        "ontology_records": [
            {
                "ontology_id": "ont_api_quality_001",
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
                "registry_id": "type_api_quality_001",
                "type_name": "character_quality:strong_character_ready",
                "type_family": "character_quality",
                "type_subfamily": "strong_character_ready",
                "type_scope": "character_quality_control",
            }
        ],
        "provenance_records": [
            {
                "provenance_id": "prov_api_quality_001",
                "source_name": "human_approved_synthetic",
                "source_type": "synthetic_or_user_generated",
                "dataset_family": "character_quality",
                "usage_allowed": True,
                "human_review_required": False,
                "license_name": "user_owned",
            }
        ],
        "embedding_metadata": {
            "embedding_id": "emb_api_quality_001",
            "embedding_model": "future_embedding_model_not_computed_yet",
            "similarity_tags": ["character_quality", "strong_character_ready"],
            "retrieval_queries": ["strong character quality"],
            "novelty_score": 0.76,
            "originality_score": 0.82,
            "similarity_threshold_used": 0.82,
            "vector_computed": False,
        },
        "training_eligibility": sample_training_eligibility(),
        "generated_training_labels": {
            "quality_tier": "strong_character_ready",
            "training_queue_ready": True,
        },
    }


def test_learning_health_route():
    response = client.get("/learning/health")

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True
    assert data["service"] == "learning"
    assert data["upgrade_pass"] == "A"
    assert "GET /learning/summary" in data["available_routes"]


def test_learning_summary_route():
    response = client.get("/learning/summary")

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True
    assert "learning_registry" in data["data"]
    assert "provenance" in data["data"]
    assert "training_queue" in data["data"]
    assert "embedding_registry" in data["data"]


def test_learning_metadata_registration_route():
    response = client.post(
        "/learning/metadata",
        json={
            "learning_metadata": sample_learning_metadata(),
            "project_id": "proj_api_learning",
            "universe_id": "velmora_api",
            "source_payload": {"quality_report": {"overall_quality_score": 0.84}},
        },
    )

    assert response.status_code == 200

    data = response.json()["data"]

    assert data["registered"] is True
    assert data["learning_registry"]["metadata_id"] == "learn_api_001"
    assert data["provenance_registered"] == 1
    assert data["embedding_registered"] is True
    assert data["training_enqueued"] is True


def test_learning_engine_result_registration_route():
    response = client.post(
        "/learning/engine-result",
        json={
            "project_id": "proj_api_learning",
            "universe_id": "velmora_api",
            "result_payload": {
                "success": True,
                "engine_name": "character.quality_scorer",
                "data": {
                    "learning_metadata": {
                        **sample_learning_metadata(),
                        "learning_metadata_id": "learn_api_engine_result_001",
                        "target_object_id": "char_api_engine_result",
                        "ontology_records": [],
                        "learned_type_candidates": [],
                        "provenance_records": [],
                        "embedding_metadata": {
                            **sample_learning_metadata()["embedding_metadata"],
                            "embedding_id": "emb_api_engine_result_001",
                        },
                    }
                },
            },
        },
    )

    assert response.status_code == 200

    data = response.json()["data"]

    assert data["registered"] is True
    assert data["target_object_id"] == "char_api_engine_result"


def test_learning_records_routes_after_registration():
    list_response = client.get(
        "/learning/records/engine_learning_metadata",
        params={"project_id": "proj_api_learning"},
    )

    assert list_response.status_code == 200

    list_data = list_response.json()["data"]

    assert list_data["count"] >= 1

    record_id = list_data["records"][0]["metadata_id"]

    get_response = client.get(f"/learning/records/engine_learning_metadata/{record_id}")

    assert get_response.status_code == 200
    assert get_response.json()["data"]["metadata_id"] == record_id


def test_learning_provenance_routes():
    response = client.post(
        "/learning/provenance",
        json={
            "source_name": "licensed_dialogue_dataset_api",
            "source_type": "licensed_dataset",
            "dataset_family": "dialogue_dataset",
            "usage_allowed": True,
            "human_review_required": False,
            "do_not_train": False,
            "license_name": "licensed_internal",
            "project_id": "proj_api_learning",
            "universe_id": "velmora_api",
            "tags": ["dialogue", "fantasy"],
        },
    )

    assert response.status_code == 200

    provenance_id = response.json()["data"]["provenance_id"]

    list_response = client.get(
        "/learning/provenance",
        params={"dataset_family": "dialogue_dataset", "allowed_for_training": True},
    )
    get_response = client.get(f"/learning/provenance/{provenance_id}")

    assert list_response.status_code == 200
    assert get_response.status_code == 200
    assert get_response.json()["data"]["source_name"] == "licensed_dialogue_dataset_api"


def test_learning_training_queue_routes():
    response = client.post(
        "/learning/training-queue",
        json={
            "target_object_id": "char_api_queue",
            "target_object_type": "character_full_profile",
            "engine_name": "character.full_profile_orchestrator",
            "payload": {"character_id": "char_api_queue"},
            "training_eligibility": sample_training_eligibility(),
            "project_id": "proj_api_learning",
            "universe_id": "velmora_api",
            "tags": ["character", "quality"],
        },
    )

    assert response.status_code == 200

    queue_id = response.json()["data"]["training_queue_id"]

    list_response = client.get(
        "/learning/training-queue",
        params={"project_id": "proj_api_learning", "future_chunk8_ready": True},
    )
    get_response = client.get(f"/learning/training-queue/{queue_id}")
    patch_response = client.patch(
        f"/learning/training-queue/{queue_id}/status",
        json={"status": "approved", "notes": "approved in API test"},
    )

    assert list_response.status_code == 200
    assert get_response.status_code == 200
    assert patch_response.status_code == 200
    assert patch_response.json()["data"]["status"] == "approved"


def test_learning_embedding_routes():
    response = client.post(
        "/learning/embeddings",
        json={
            "target_object_id": "char_api_embedding",
            "target_object_type": "character_dialogue_voice",
            "engine_name": "character.dialogue_voice_engine",
            "project_id": "proj_api_learning",
            "universe_id": "velmora_api",
            "embedding_metadata": {
                "embedding_id": "emb_api_direct_001",
                "embedding_model": "future_embedding_model_not_computed_yet",
                "similarity_tags": ["dialogue_voice", "controlled_subtext_voice"],
                "retrieval_queries": ["controlled subtext voice"],
                "novelty_score": 0.76,
                "originality_score": 0.84,
                "similarity_threshold_used": 0.82,
                "vector_computed": False,
            },
            "source_payload": {"voice": "controlled subtext"},
            "queue_for_vectorization": True,
        },
    )

    assert response.status_code == 200

    embedding_id = response.json()["data"]["embedding_id"]

    list_response = client.get(
        "/learning/embeddings",
        params={"tag": "controlled_subtext_voice", "min_originality_score": 0.8},
    )
    get_response = client.get(f"/learning/embeddings/{embedding_id}")
    queue_response = client.get("/learning/embeddings/vectorization-queue", params={"status": "queued"})

    assert list_response.status_code == 200
    assert get_response.status_code == 200
    assert queue_response.status_code == 200
    assert get_response.json()["data"]["embedding_id"] == embedding_id


def test_learning_api_handles_bad_requests():
    bad_metadata = client.post(
        "/learning/metadata",
        json={
            "learning_metadata": {
                "engine_name": "",
                "target_object_id": "x",
                "target_object_type": "y",
            }
        },
    )

    bad_provenance = client.post(
        "/learning/provenance",
        json={
            "source_name": "",
            "source_type": "licensed_dataset",
            "dataset_family": "dialogue",
            "usage_allowed": True,
        },
    )

    bad_training = client.post(
        "/learning/training-queue",
        json={
            "target_object_id": "",
            "target_object_type": "character",
            "engine_name": "engine",
            "payload": {},
            "training_eligibility": {},
        },
    )

    bad_embedding = client.post(
        "/learning/embeddings",
        json={
            "target_object_id": "",
            "target_object_type": "character",
            "embedding_metadata": {},
        },
    )

    assert bad_metadata.status_code == 400
    assert bad_provenance.status_code == 400
    assert bad_training.status_code == 400
    assert bad_embedding.status_code == 400

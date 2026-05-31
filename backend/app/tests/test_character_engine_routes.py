from fastapi.testclient import TestClient

from backend.app.main import app


client = TestClient(app)


def sample_seed():
    return {
        "character_id": "char_api_kael",
        "name": "Kael Veyran",
        "role": "protagonist",
        "social_class": "academy_sponsored",
        "family_name_status": "distrusted",
        "destiny_type": "hidden_kingmaker",
    }


def test_character_engines_health_route():
    response = client.get("/character/engines/health")

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True
    assert data["service"] == "character-engines"
    assert "full-profile-orchestrator" in data["available_engines"]
    assert "save-profile" in data["available_store_routes"]


def test_character_adaptability_route():
    response = client.post(
        "/character/engines/adaptability",
        json={
            "payload": {
                "character_seed": {
                    **sample_seed(),
                    "adaptability_type": "earned_breakthrough",
                    "breakthrough_condition": "protects someone weaker",
                },
                "skill_ontology": {
                    "skill_family": "cognitive_inference",
                    "adaptability_compatibility": 0.8,
                    "cost_family": ["mental_fatigue"],
                    "counter_family": ["false_signal"],
                },
                "source_mode": "human_approved_synthetic",
                "user_rating": 9,
            }
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True
    assert data["engine_name"] == "character.adaptability_engine"
    assert "adaptability_profile" in data["data"]


def test_character_destiny_route():
    response = client.post(
        "/character/engines/destiny",
        json={
            "payload": {
                "character_seed": sample_seed(),
                "character_type_ontology": {
                    "type_family": "power_redirector",
                    "type_subtype": "hidden_kingmaker",
                },
                "source_mode": "human_approved_synthetic",
                "user_rating": 9,
            }
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True
    assert data["engine_name"] == "character.destiny_legacy_engine"
    assert "destiny_profile" in data["data"]


def test_character_relationship_readiness_route():
    response = client.post(
        "/character/engines/relationship-readiness",
        json={
            "payload": {
                "character_seed": sample_seed(),
                "psychology_profile": {
                    "core_wound": "believes belonging can be revoked",
                    "healing_condition": "someone protects truth without using it",
                },
                "character_type_ontology": {
                    "type_family": "power_redirector",
                },
                "source_mode": "human_approved_synthetic",
                "user_rating": 9,
            }
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True
    assert data["engine_name"] == "character.relationship_readiness_engine"
    assert "relationship_readiness_profile" in data["data"]


def test_character_dialogue_voice_route():
    response = client.post(
        "/character/engines/dialogue-voice",
        json={
            "payload": {
                "character_seed": sample_seed(),
                "psychology_profile": {
                    "core_wound": "believes belonging can be revoked",
                    "shame_trigger": "being treated as useful but replaceable",
                },
                "character_type_ontology": {
                    "type_family": "power_redirector",
                },
                "relationship_readiness_profile": {
                    "relationship_readiness_family": "high_loyalty_power_broker_readiness",
                    "trust_model": "trust_requires_truth_protection_without_weaponization",
                },
                "source_mode": "human_approved_synthetic",
                "user_rating": 9,
            }
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True
    assert data["engine_name"] == "character.dialogue_voice_engine"
    assert "dialogue_voice_profile" in data["data"]


def test_character_consistency_validator_route():
    response = client.post(
        "/character/engines/consistency-validator",
        json={
            "payload": {
                "character_seed": sample_seed(),
                "skill_ontology": {
                    "skill_family": "cognitive_inference",
                    "cost_family": ["mental_fatigue"],
                    "counter_family": ["false_signal"],
                },
                "source_mode": "human_approved_synthetic",
                "user_rating": 9,
            }
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True
    assert data["engine_name"] == "character.consistency_validator"
    assert "consistency_report" in data["data"]


def test_character_originality_route():
    response = client.post(
        "/character/engines/originality",
        json={
            "payload": {
                "character_seed": sample_seed(),
                "psychology_profile": {
                    "core_wound": "believes belonging can be revoked after public failure",
                },
                "goal_profile": {
                    "true_need": "belonging is not the same as permission",
                    "false_need": "worth can be revoked by public failure",
                },
                "skill_ontology": {
                    "skill_family": "cognitive_inference",
                },
                "character_type_ontology": {
                    "type_family": "power_redirector",
                },
                "destiny_profile": {
                    "destiny_family": "power_flow_destiny",
                },
                "source_mode": "human_approved_synthetic",
                "user_rating": 9,
            }
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True
    assert data["engine_name"] == "character.originality_engine"
    assert "originality_report" in data["data"]


def test_character_quality_scorer_route():
    response = client.post(
        "/character/engines/quality-scorer",
        json={
            "payload": {
                "character_seed": sample_seed(),
                "consistency_report": {
                    "overall_consistency_score": 0.9,
                    "critical_issue_count": 0,
                    "violation_count": 0,
                },
                "originality_report": {
                    "overall_originality_score": 0.78,
                    "novelty_score": 0.8,
                    "strong_originality_sources": ["power_redirector_plus_cognitive_inference"],
                },
                "anti_genericity_report": {
                    "genericity_risk_score": 0.12,
                    "genericity_risks": [],
                },
                "repair_plan": {
                    "requires_repair": False,
                    "repair_count": 0,
                },
                "source_mode": "human_approved_synthetic",
                "user_rating": 9,
            }
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True
    assert data["engine_name"] == "character.quality_scorer"
    assert "quality_report" in data["data"]


def test_character_full_profile_orchestrator_route_with_persistence():
    response = client.post(
        "/character/engines/full-profile-orchestrator",
        json={
            "persist": True,
            "project_id": "proj_api",
            "universe_id": "velmora_api",
            "payload": {
                "character_seed": sample_seed(),
                "origin_profile": {
                    "social_class": "academy_sponsored",
                    "family_name_status": "distrusted",
                },
                "psychology_profile": {
                    "core_wound": "believes belonging can be revoked after public failure",
                },
                "goal_profile": {
                    "true_need": "belonging is not the same as permission",
                },
                "skill_ontology": {
                    "skill_family": "cognitive_inference",
                },
                "character_type_ontology": {
                    "type_family": "power_redirector",
                },
                "relationship_readiness_profile": {
                    "relationship_readiness_family": "high_loyalty_power_broker_readiness",
                },
                "dialogue_voice_profile": {
                    "voice_family": "controlled_subtext_voice",
                },
                "quality_report": {
                    "overall_quality_score": 0.82,
                    "quality_tier": "strong_character_ready",
                    "weak_axes": [],
                },
                "readiness_report": {
                    "character_bible_ready": True,
                    "orchestrator_ready": True,
                    "training_queue_ready": True,
                },
                "source_mode": "human_approved_synthetic",
                "user_rating": 9,
            },
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True
    assert data["engine_name"] == "character.full_profile_orchestrator"
    assert "character_full_profile" in data["data"]
    assert data["persistence"]["persisted"] is True
    assert data["profile_persistence"]["persisted"] is True


def test_character_profile_store_routes_after_persistence():
    save_response = client.post(
        "/character/engines/save-profile",
        json={
            "character_id": "char_manual_api",
            "project_id": "proj_api",
            "universe_id": "velmora_api",
            "profile": {
                "profile_id": "manual_profile",
                "character_id": "char_manual_api",
                "identity": {
                    "character_id": "char_manual_api",
                    "name": "Manual API Character",
                    "role": "supporting",
                },
                "validation": {
                    "quality_report": {
                        "overall_quality_score": 0.81,
                        "quality_tier": "strong_character_ready",
                    }
                },
            },
            "orchestration_report": {
                "profile_tier": "complete_profile_ready",
            },
        },
    )

    assert save_response.status_code == 200

    get_response = client.get("/character/engines/profiles/char_manual_api")
    list_response = client.get("/character/engines/profiles", params={"project_id": "proj_api"})
    summary_response = client.get("/character/engines/store-summary")

    assert get_response.status_code == 200
    assert list_response.status_code == 200
    assert summary_response.status_code == 200

    assert get_response.json()["data"]["character_id"] == "char_manual_api"
    assert list_response.json()["data"]["count"] >= 1
    assert summary_response.json()["data"]["profile_count"] >= 1


def test_character_runs_list_route():
    response = client.get("/character/engines/runs", params={"project_id": "proj_api"})

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True
    assert "runs" in data["data"]
    assert data["data"]["count"] >= 1

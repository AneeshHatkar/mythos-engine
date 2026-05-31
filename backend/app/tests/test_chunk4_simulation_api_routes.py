from fastapi.testclient import TestClient

from backend.app.main import app


client = TestClient(app)


def test_simulation_health_route():
    response = client.get("/simulation/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "mythos-simulation"


def test_simulation_run_route():
    response = client.post(
        "/simulation/run",
        json={
            "run_id": "api_run_001",
            "story_request": {
                "story_request_id": "api_story_001",
                "cast_id": "cast_api_001",
                "scene_id": "scene_api_001",
                "plot_arc_id": "arc_api_001",
                "format": "novel",
                "primary_genres": ["dark_academy", "romance"],
                "tone_tags": ["tense", "mythic"],
                "distinctive_elements": ["oath court proof ritual", "cracked badge evidence"],
                "allow_any_character_count": True,
                "allow_project_created_characters": True,
                "required_roles": ["protagonist", "love_interest", "antagonist"],
                "required_story_functions": ["drive_plot", "anchor_romance", "create_conflict"],
                "scene_goal": "Kael reveals the truth in court.",
                "conflicts": [
                    {
                        "conflict_id": "conflict_api_truth",
                        "conflict_type": "truth",
                        "title": "Truth vs Protection",
                        "participant_ids": ["char_kael", "char_seren"],
                        "core_issue": "Reveal truth or protect source.",
                        "opposing_goals": {
                            "char_kael": "reveal truth",
                            "char_seren": "protect source"
                        },
                        "intensity": 0.8,
                        "stakes_score": 0.85,
                        "tension_score": 0.8,
                        "moral_complexity": 0.85
                    }
                ]
            },
            "event_specs": [
                {
                    "event_id": "evt_api_trial",
                    "event_type": "trial",
                    "event_name": "Kael reveals the cracked badge in court.",
                    "actor_ids": ["char_kael"],
                    "target_ids": ["char_seren"],
                    "witness_ids": ["char_vask"],
                    "location_id": "location_court",
                    "visibility": "public",
                    "intensity": 0.85,
                    "linked_secret_ids": ["secret_rank_system_edited"],
                    "linked_evidence_ids": ["evidence_cracked_badge"]
                }
            ],
            "target_cast_size": 3
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["run_id"] == "api_run_001"
    assert data["run_record"]["status"] == "completed"
    assert data["run_record"]["outputs"]["handoff_package_id"] == "handoff_api_run_001"
    assert "state" in data


def test_simulation_quality_route():
    response = client.post(
        "/simulation/runs/api_quality/quality",
        json={
            "run_id": "api_quality",
            "story_request": {
                "cast_id": "cast_api_quality",
                "scene_id": "scene_api_quality",
                "format": "novel",
                "primary_genres": ["dark_academy"],
                "required_roles": ["protagonist", "love_interest"],
                "required_story_functions": ["drive_plot", "anchor_romance"],
                "allow_any_character_count": True,
                "allow_project_created_characters": True
            },
            "event_specs": [
                {
                    "event_id": "evt_api_quality",
                    "event_type": "private_confession",
                    "event_name": "Seren confesses a truth.",
                    "actor_ids": ["char_seren"],
                    "target_ids": ["char_kael"],
                    "location_id": "location_court",
                    "visibility": "private",
                    "intensity": 0.7
                }
            ],
            "target_cast_size": 2
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["quality_report"]["run_id"] == "api_quality"
    assert "overall_quality_score" in data["quality_report"]


def test_simulation_anti_genericity_route():
    response = client.post(
        "/simulation/runs/api_antigeneric/anti-genericity",
        json={
            "run_id": "api_antigeneric",
            "story_request": {
                "cast_id": "cast_api_antigeneric",
                "scene_id": "scene_api_antigeneric",
                "format": "novel",
                "primary_genres": ["dark_academy", "romance"],
                "tone_tags": ["tense", "courtly"],
                "distinctive_elements": ["oath court proof ritual", "cracked badge evidence"],
                "required_roles": ["protagonist", "love_interest"],
                "required_story_functions": ["drive_plot", "anchor_romance"],
                "allow_any_character_count": True,
                "allow_project_created_characters": True
            },
            "event_specs": [
                {
                    "event_id": "evt_api_antigeneric",
                    "event_type": "trial",
                    "event_name": "Kael reveals oath-court evidence.",
                    "actor_ids": ["char_kael"],
                    "target_ids": ["char_seren"],
                    "location_id": "location_court",
                    "visibility": "public",
                    "intensity": 0.8,
                    "linked_secret_ids": ["secret_rank_system_edited"],
                    "linked_evidence_ids": ["evidence_cracked_badge"]
                }
            ],
            "target_cast_size": 2
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["anti_genericity_report"]["run_id"] == "api_antigeneric"
    assert "anti_genericity_score" in data["anti_genericity_report"]


def test_simulation_bundle_route():
    response = client.post(
        "/simulation/runs/api_bundle/bundle",
        json={
            "run_id": "api_bundle",
            "story_request": {
                "cast_id": "cast_api_bundle",
                "scene_id": "scene_api_bundle",
                "format": "novel",
                "primary_genres": ["dark_academy"],
                "required_roles": ["protagonist"],
                "required_story_functions": ["drive_plot"],
                "allow_any_character_count": True,
                "allow_project_created_characters": True
            },
            "event_specs": [],
            "target_cast_size": 2
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["run_id"] == "api_bundle"
    assert data["bundle_id"] == "bundle_api_bundle"
    assert data["bundle"]["run_record"]["run_id"] == "api_bundle"

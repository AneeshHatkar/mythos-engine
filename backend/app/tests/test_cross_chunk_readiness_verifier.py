from backend.app.services.cross_chunk_readiness_verifier import CrossChunkReadinessVerifier


def sample_world_profile():
    return {
        "world_id": "world_velmora",
        "world_name": "Velmora",
        "social_classes": ["erased", "academy_sponsored", "old_nobility"],
        "magic_rules": ["relic power requires cost and counterplay"],
        "legal_constraints": ["distrusted family names require sponsor to testify"],
        "factions": ["Oath Court", "Relic Guild"],
        "academy_access": ["sponsor seat", "exam route", "debt contract"],
        "economy": ["relic labor economy"],
        "culture": ["public names carry legal trust"],
        "geography": ["capital rings", "outer academy district"],
    }


def sample_character_profile(character_id="char_kael"):
    return {
        "character_id": character_id,
        "identity": {
            "character_id": character_id,
            "name": "Kael Veyran",
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
                "false_need": "worth is public permission",
            },
            "memory_records": [
                {"memory_id": "mem_public_failure", "content": "public failure"}
            ],
        },
        "relationships": {
            "relationship_readiness_profile": {
                "relationship_readiness_family": "high_loyalty_power_broker_readiness",
                "trust_model": "trust requires truth protection",
            }
        },
        "dialogue": {
            "dialogue_voice_profile": {
                "voice_family": "controlled_subtext_voice",
            }
        },
    }


def test_cross_chunk_readiness_foundation_layer():
    verifier = CrossChunkReadinessVerifier()

    report = verifier.verify_foundation_layer()

    assert report["ready"] is True
    assert report["readiness_score"] == 1.0
    assert report["checks"]["EntityRef"] is True
    assert report["checks"]["ArtifactRecord"] is True
    assert report["checks"]["WorldToCharacterContract"] is True
    assert report["checks"]["CharacterToSimulationContract"] is True


def test_cross_chunk_readiness_world_layer():
    verifier = CrossChunkReadinessVerifier()

    report = verifier.verify_world_layer(
        world_payload=sample_world_profile(),
        project_id="proj_ashen",
        universe_id="velmora",
    )

    assert report["ready"] is True
    assert report["world_id"] == "world_velmora"
    assert report["constraint_checks"]["legal_constraints"] is True
    assert report["constraint_checks"]["power_cost_rules"] is True
    assert report["constraint_checks"]["permission_boundaries"] is True
    assert report["handoff_valid"] is True


def test_cross_chunk_readiness_character_layer():
    verifier = CrossChunkReadinessVerifier()

    world_report = verifier.verify_world_layer(
        world_payload=sample_world_profile(),
        project_id="proj_ashen",
        universe_id="velmora",
    )

    report = verifier.verify_character_layer(
        character_payloads=[sample_character_profile()],
        world_contract=world_report["world_to_character_contract"],
        project_id="proj_ashen",
        universe_id="velmora",
    )

    assert report["ready"] is True
    assert report["character_count"] == 1
    assert report["ready_character_count"] == 1
    assert report["character_reports"][0]["character_id"] == "char_kael"
    assert report["character_reports"][0]["handoff_valid"] is True


def test_cross_chunk_readiness_invariants_available():
    verifier = CrossChunkReadinessVerifier()

    report = verifier.verify_required_invariants_available()

    assert report["ready"] is True
    assert "no_magic_knowledge" in report["required_invariants"]
    assert "no_consequence_free_major_choice" in report["required_invariants"]
    assert "no_relationship_jump_without_cause" in report["required_invariants"]


def test_cross_chunk_readiness_full_report_ready_for_chunk4():
    verifier = CrossChunkReadinessVerifier()

    report = verifier.verify_cross_chunk_readiness(
        world_payload=sample_world_profile(),
        character_payloads=[
            sample_character_profile("char_kael"),
            sample_character_profile("char_seren"),
        ],
        project_id="proj_ashen",
        universe_id="velmora",
    )

    assert report["success"] is True
    assert report["cross_chunk_ready_for_chunk4"] is True
    assert report["readiness_score"] >= 0.9
    assert report["recommendation"] == "start_chunk4"
    assert report["blockers"] == []
    assert report["character_report"]["ready_character_count"] == 2


def test_cross_chunk_readiness_detects_bad_world_contract():
    verifier = CrossChunkReadinessVerifier()

    bad_world = {
        "world_id": "world_bad",
        "world_name": "Bad World",
    }

    report = verifier.verify_cross_chunk_readiness(
        world_payload=bad_world,
        character_payloads=[sample_character_profile()],
        project_id="proj_ashen",
        universe_id="velmora",
    )

    assert report["success"] is True
    assert report["cross_chunk_ready_for_chunk4"] is False
    assert report["blockers"]


def test_error_taxonomy_available():
    verifier = CrossChunkReadinessVerifier()

    taxonomy = verifier.error_taxonomy_available()

    assert "knowledge_leak_error" in taxonomy
    assert "canon_lock_violation" in taxonomy
    assert "state_delta_conflict" in taxonomy
    assert "provenance_blocked" in taxonomy

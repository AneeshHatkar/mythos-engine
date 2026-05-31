from backend.app.services.artifact_registry_store import ArtifactRegistryStore
from backend.app.services.character_state_snapshot_store import CharacterStateSnapshotStore
from backend.app.services.deep_story_readiness_verifier import DeepStoryReadinessVerifier
from backend.app.services.human_review_store import HumanReviewStore
from backend.app.services.world_state_snapshot_service import WorldStateSnapshotService


def sample_world():
    return {
        "world_id": "world_velmora",
        "world_name": "Velmora",
        "genre_tags": ["academy", "romance", "political_intrigue"],
        "social_classes": ["erased", "academy_sponsored", "old_nobility"],
        "magic_rules": ["relic power requires cost and counterplay"],
        "legal_constraints": ["distrusted family names require sponsor to testify"],
        "factions": ["Oath Court", "Relic Guild"],
        "institutions": ["Academy", "Court"],
        "academy_access": ["sponsor seat", "exam route", "debt contract"],
        "economy": ["relic labor", "debt contracts"],
        "culture": ["public names carry legal trust"],
        "geography": ["capital court district", "outer academy district", "relic mines"],
    }


def char_kael():
    return {
        "character_id": "char_kael",
        "identity": {"character_id": "char_kael", "name": "Kael"},
        "origin": {"social_class": "academy_sponsored", "family_name_status": "distrusted"},
        "psychology": {
            "psychology_profile": {"core_wound": "believes belonging can be revoked after public failure"},
            "goal_profile": {
                "surface_goal": "survive academy ranking",
                "hidden_goal": "prove the ranking system is edited",
                "true_need": "belonging is not permission",
            },
            "memory_records": [{"memory_id": "mem_kael_core", "content": "public failure"}],
        },
        "power": {
            "skill_ontology": {"skill_family": "cognitive_inference"},
            "adaptability_profile": {"cost_model": "identity instability after breakthrough"},
        },
        "dialogue": {"dialogue_voice_profile": {"voice_family": "controlled_subtext_voice"}},
        "relationships": {"relationship_readiness_profile": {"relationship_readiness_family": "high_loyalty_power_broker_readiness"}},
        "symbolic_role": "erased truth seeker",
        "public_mask": "precise and composed",
        "private_truth": "terrified of being unreal",
    }


def char_seren():
    return {
        "character_id": "char_seren",
        "identity": {"character_id": "char_seren", "name": "Seren"},
        "origin": {"social_class": "old_nobility", "family_name_status": "trusted"},
        "psychology": {
            "psychology_profile": {"core_wound": "believes love becomes dangerous when witnessed"},
            "goal_profile": {
                "surface_goal": "protect family position",
                "hidden_goal": "free herself from inherited loyalty",
                "true_need": "truth without permission",
            },
            "memory_records": [{"memory_id": "mem_seren_core", "content": "family oath"}],
        },
        "power": {
            "skill_ontology": {"skill_family": "oath_magic"},
            "adaptability_profile": {"cost_model": "oath backlash after false testimony"},
        },
        "dialogue": {"dialogue_voice_profile": {"voice_family": "ceremonial_restraint_voice"}},
        "relationships": {"relationship_readiness_profile": {"relationship_readiness_family": "guarded_loyalty_readiness"}},
        "symbolic_role": "witness with divided loyalty",
        "public_mask": "obedient noble composure",
        "private_truth": "wants truth more than safety",
    }


def build_verifier(tmp_path):
    return DeepStoryReadinessVerifier(
        artifact_store=ArtifactRegistryStore(root=tmp_path / "artifacts"),
        review_store=HumanReviewStore(root=tmp_path / "review"),
        world_snapshot_store=WorldStateSnapshotService(root=tmp_path / "world_snapshots"),
        character_snapshot_store=CharacterStateSnapshotStore(root=tmp_path / "character_snapshots"),
    )


def test_deep_story_readiness_foundation_hardening(tmp_path):
    verifier = build_verifier(tmp_path)

    report = verifier.verify_foundation_hardening(
        world_profile=sample_world(),
        character_profiles=[char_kael(), char_seren()],
        project_id="proj_ashen",
        universe_id="velmora",
    )

    assert report["ready"] is True
    assert report["checks"]["artifact_registry_store"] is True
    assert report["checks"]["canon_lock_service_blocks_invalid_change"] is True
    assert report["checks"]["engine_config_store"] is True
    assert report["checks"]["human_review_store"] is True


def test_deep_story_readiness_world_hardening(tmp_path):
    verifier = build_verifier(tmp_path)

    report = verifier.verify_world_hardening(
        world_profile=sample_world(),
        project_id="proj_ashen",
        universe_id="velmora",
    )

    assert report["ready"] is True
    assert report["checks"]["world_snapshot_created"] is True
    assert report["checks"]["world_rule_conflict_detector"] is True
    assert report["checks"]["world_location_access_engine"] is True
    assert report["checks"]["faction_institution_resource_engine"] is True


def test_deep_story_readiness_character_hardening(tmp_path):
    verifier = build_verifier(tmp_path)

    report = verifier.verify_character_hardening(
        character_profiles=[char_kael(), char_seren()],
        project_id="proj_ashen",
        universe_id="velmora",
    )

    assert report["ready"] is True
    assert report["character_count"] == 2
    assert report["ready_character_count"] == 2
    assert report["character_reports"][0]["checks"]["memory_update_ready"] is True
    assert report["character_reports"][0]["checks"]["emotion_carryover_ready"] is True
    assert report["character_reports"][0]["checks"]["agency_state_ready"] is True


def test_deep_story_readiness_deep_story_layers(tmp_path):
    verifier = build_verifier(tmp_path)

    report = verifier.verify_deep_story_layers(
        world_profile=sample_world(),
        character_profiles=[char_kael(), char_seren()],
        project_id="proj_ashen",
        universe_id="velmora",
    )

    assert report["ready"] is True
    assert report["checks"]["story_dna_ready"] is True
    assert report["checks"]["emotional_resonance_ready"] is True
    assert report["checks"]["character_contrast_ready"] is True
    assert report["checks"]["world_character_pressure_ready"] is True


def test_deep_story_readiness_full_report_ready_for_chunk4(tmp_path):
    verifier = build_verifier(tmp_path)

    report = verifier.verify_deep_story_readiness(
        world_profile=sample_world(),
        character_profiles=[char_kael(), char_seren()],
        project_id="proj_ashen",
        universe_id="velmora",
    )

    assert report["success"] is True
    assert report["deep_story_ready_for_chunk4"] is True
    assert report["readiness_score"] >= 0.9
    assert report["recommendation"] == "start_chunk4"
    assert report["blockers"] == []
    assert report["foundation_hardening_report"]["ready"] is True
    assert report["world_hardening_report"]["ready"] is True
    assert report["character_hardening_report"]["ready"] is True
    assert report["deep_story_layer_report"]["ready"] is True
    assert report["cross_chunk_readiness_report"]["ready"] is True

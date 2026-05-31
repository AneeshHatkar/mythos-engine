from backend.app.services.character_learning_adapter import CharacterLearningAdapter
from backend.app.services.world_learning_adapter import WorldLearningAdapter
from backend.app.schemas.handoffs import CharacterToSimulationContract, WorldToCharacterContract


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


def sample_character_profile():
    return {
        "character_id": "char_kael",
        "identity": {
            "character_id": "char_kael",
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


def test_world_adapter_exports_simulation_ready_constraints():
    adapter = WorldLearningAdapter()

    export = adapter.build_world_simulation_constraint_export(
        sample_world_profile(),
        project_id="proj_ashen",
        universe_id="velmora",
    )

    assert export["world_id"] == "world_velmora"
    assert export["chunk4_ready"] is True
    assert export["world_simulation_constraints"]["legal_constraints"]
    assert export["world_simulation_constraints"]["power_cost_rules"]
    assert export["world_simulation_constraints"]["character_permission_boundaries"]

    handoff = WorldToCharacterContract.model_validate(export["cross_chunk_handoff"])
    assert handoff.handoff_type == "world_to_character"
    assert handoff.ready is True
    assert handoff.payload["world_simulation_constraints"]["power_cost_rules"]


def test_world_normalization_includes_simulation_constraint_export():
    adapter = WorldLearningAdapter()

    normalized = adapter.normalize_world_result(
        result_payload={
            "success": True,
            "engine_name": "world.world_orchestrator_engine",
            "data": {"world_profile": sample_world_profile()},
        },
        project_id="proj_ashen",
        universe_id="velmora",
    )

    assert "world_simulation_constraint_export" in normalized
    assert normalized["world_simulation_constraint_export"]["chunk4_ready"] is True


def test_character_adapter_builds_character_to_simulation_contract():
    adapter = CharacterLearningAdapter()

    world_adapter = WorldLearningAdapter()
    world_export = world_adapter.build_world_simulation_constraint_export(
        sample_world_profile(),
        project_id="proj_ashen",
        universe_id="velmora",
    )

    world_validation = adapter.validate_character_against_world_contract(
        character_profile=sample_character_profile(),
        world_contract=world_export["world_to_character_contract"],
    )
    chunk4_handoff = adapter.build_chunk4_handoff_contract(
        character_id="char_kael",
        character_profile=sample_character_profile(),
    )

    contract = adapter.build_character_to_simulation_contract(
        character_id="char_kael",
        character_profile=sample_character_profile(),
        project_id="proj_ashen",
        universe_id="velmora",
        world_contract_validation=world_validation,
        chunk4_handoff_contract=chunk4_handoff,
    )

    assert contract["character_id"] == "char_kael"
    assert contract["chunk4_ready"] is True
    assert contract["simulation_state_seed"]["current_memory_state"]["active_memory_ids"] == ["mem_public_failure"]
    assert contract["dialogue_constraint_seed"]["base_voice_family"] == "controlled_subtext_voice"
    assert contract["relationship_state_seed"]["relationship_readiness_family"] == "high_loyalty_power_broker_readiness"

    handoff = CharacterToSimulationContract.model_validate(contract["cross_chunk_handoff"])
    assert handoff.handoff_type == "character_to_simulation"
    assert handoff.ready is True


def test_character_normalization_includes_character_to_simulation_contract():
    adapter = CharacterLearningAdapter()

    normalized = adapter.normalize_character_result(
        result_payload={
            "success": True,
            "engine_name": "character.full_profile_orchestrator",
            "data": {"character_full_profile": sample_character_profile()},
        },
        project_id="proj_ashen",
        universe_id="velmora",
        world_contract=sample_world_profile(),
    )

    assert "character_to_simulation_contract" in normalized
    assert normalized["character_to_simulation_contract"]["character_id"] == "char_kael"
    assert normalized["character_to_simulation_contract"]["chunk4_ready"] is True


def test_character_contract_separates_base_profile_from_mutable_simulation_state():
    adapter = CharacterLearningAdapter()

    contract = adapter.build_character_to_simulation_contract(
        character_id="char_kael",
        character_profile=sample_character_profile(),
        project_id="proj_ashen",
        universe_id="velmora",
    )

    seed = contract["simulation_state_seed"]

    assert "current_emotion_state" in seed
    assert "current_memory_state" in seed
    assert "current_agency_state" in seed
    assert "current_relationship_state" in seed
    assert "current_knowledge_state" in seed
    assert seed["current_relationship_state"]["pending_relationship_deltas"] == []

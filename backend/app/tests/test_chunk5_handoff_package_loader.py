from backend.app.engines.story_generation.generation_contract_resolver import GenerationContractResolver
from backend.app.engines.story_generation.generation_mode_controller import GenerationModeController
from backend.app.engines.story_generation.handoff_package_loader import HandoffPackageLoader
from backend.app.schemas.simulation import (
    SimulationCharacterState,
    SimulationKnowledgeState,
    SimulationRelationshipState,
    SimulationState,
    SimulationWorldState,
)
from backend.app.schemas.story_generation import GenerationMode, StoryFormat, StoryIntent


def build_state():
    return SimulationState(
        simulation_id="sim_loader_001",
        world_state=SimulationWorldState(
            world_id="world_oath",
            metadata={
                "world_rules": {"rule_oath_court_proof": "public evidence changes legal rank"},
                "locations": {"location_court": {"name": "Oath Court"}},
                "factions": {"faction_oath_court": {"name": "Oath Court"}},
                "cultures": {"culture_ranked": {"name": "Ranked Houses"}},
            },
        ),
        character_states={
            "char_kael": SimulationCharacterState(
                character_id="char_kael",
                current_location_id="location_court",
                metadata={
                    "display_name": "Kael",
                    "voice_profile": {"style": "guarded"},
                    "emotional_state": {"shame": 0.7, "resolve": 0.8},
                },
            ),
            "char_seren": SimulationCharacterState(
                character_id="char_seren",
                current_location_id="location_court",
                metadata={
                    "display_name": "Seren",
                    "voice_profile": {"style": "controlled"},
                    "emotional_state": {"guilt": 0.8},
                },
            ),
        },
        relationship_states={
            "rel_kael_seren": SimulationRelationshipState(
                relationship_id="rel_kael_seren",
                character_a_id="char_kael",
                character_b_id="char_seren",
                trust=0.3,
                resentment=0.5,
                romantic_tension=0.4,
            )
        },
        knowledge_states={
            "char_kael": SimulationKnowledgeState(
                entity_id="char_kael",
                known_secret_ids=["secret_rank_system"],
                evidence_seen_ids=["evidence_cracked_badge"],
            )
        },
        metadata={
            "project_id": "project_mythos",
            "universe_id": "universe_oath",
            "handoff_packages": {
                "handoff_001": {
                    "handoff_package_id": "handoff_001",
                    "simulation_id": "sim_loader_001",
                    "run_id": "run_loader_001",
                    "selected_character_ids": ["char_kael", "char_seren"],
                    "linked_secret_ids": ["secret_rank_system"],
                    "causal_node_ids": ["cause_trial_reveal"],
                    "consequence_ids": ["cons_reputation_shift"],
                    "relationship_ids": ["rel_kael_seren"],
                }
            },
            "generation_control_payloads": {
                "gen_control_001": {
                    "generation_control_payload_id": "gen_control_001",
                    "simulation_id": "sim_loader_001",
                    "tone_tags": ["tense"],
                    "genres": ["dark_academy"],
                }
            },
            "skill_registry": {f"skill_{i}": {} for i in range(105)},
            "power_registry": {f"power_{i}": {} for i in range(3)},
            "artifact_registry": {"artifact_badge": {}},
            "causal_chains": {"cause_trial_reveal": {"why": "Kael reveals evidence"}},
        },
    )


def build_contract(state):
    intent = StoryIntent(
        intent_id="intent_loader",
        user_prompt="Write a tense dark academy scene.",
        desired_format=StoryFormat.scene,
        generation_mode=GenerationMode.full_scene,
        required_character_ids=["char_kael"],
        genres=["dark_academy"],
        tone_tags=["tense"],
    )
    mode = GenerationModeController().choose_mode(intent=intent)
    return GenerationContractResolver().resolve_contract(
        intent=intent,
        mode_decision=mode,
        handoff_payload=state.metadata["handoff_packages"]["handoff_001"],
        generation_control_payload=state.metadata["generation_control_payloads"]["gen_control_001"],
    )["generation_contract"]


def test_handoff_loader_loads_context_from_state():
    state = build_state()
    contract = build_contract(state)
    loader = HandoffPackageLoader()

    result = loader.load_from_state(state=state, contract=contract)

    context = result["context_package"]

    assert result["success"] is True
    assert context.context_package_id == f"context_{contract.generation_contract_id}"
    assert context.world_context["world_id"] == "world_oath"
    assert "char_kael" in context.character_context
    assert "rel_kael_seren" in context.relationship_context
    assert "char_kael" in context.knowledge_context
    assert context.format_context["selected_format"] == "scene"
    assert context.large_pool_context["large_skill_pool"] is True


def test_handoff_loader_context_contains_emotional_state():
    state = build_state()
    contract = build_contract(state)
    loader = HandoffPackageLoader()

    result = loader.load_from_state(state=state, contract=contract)
    emotional = result["context_package"].emotional_context

    assert emotional["char_kael"]["shame"] == 0.7
    assert emotional["char_seren"]["guilt"] == 0.8


def test_handoff_loader_validates_context_package():
    state = build_state()
    contract = build_contract(state)
    loader = HandoffPackageLoader()

    context = loader.load_from_state(state=state, contract=contract)["context_package"]
    validation = loader.validate_context_package(context=context)

    assert validation["success"] is True
    assert validation["valid"] is True
    assert "character_context_present" in validation["passed_checks"]
    assert "world_context_present" in validation["passed_checks"]
    assert "format_context_present" in validation["passed_checks"]


def test_handoff_loader_summarizes_context_package():
    state = build_state()
    contract = build_contract(state)
    loader = HandoffPackageLoader()

    context = loader.load_from_state(state=state, contract=contract)["context_package"]
    summary = loader.summarize_context(context=context)

    assert summary["success"] is True
    assert summary["summary"]["character_count"] >= 1
    assert summary["summary"]["relationship_count"] >= 1
    assert summary["summary"]["selected_format"] == "scene"
    assert summary["summary"]["large_pool_context"]["skill_count"] == 105


def test_handoff_loader_builds_from_payload_dicts():
    state = build_state()
    contract = build_contract(state)
    loader = HandoffPackageLoader()

    result = loader.load_from_payloads(
        contract=contract,
        handoff_payload={
            "character_context": {"char_test": {"display_name": "Test"}},
            "relationship_context": {"rel_test": {"trust": 0.2}},
            "knowledge_context": {"char_test": {"known_secret_ids": ["secret_x"]}},
            "causal_node_ids": ["cause_x"],
            "consequence_ids": ["cons_x"],
        },
        state_payload={
            "project_id": "project_payload",
            "universe_id": "universe_payload",
            "world_context": {
                "world_id": "world_payload",
                "locations": ["tower"],
                "factions": ["court"],
            },
        },
    )

    context = result["context_package"]

    assert result["success"] is True
    assert context.project_id == "project_payload"
    assert context.world_context["world_id"] == "world_payload"
    assert "char_test" in context.character_context
    assert context.causal_context["causal_node_ids"] == ["cause_x"]


def test_handoff_loader_warns_without_explicit_handoff():
    state = build_state()
    contract = build_contract(state)
    contract.handoff_reference.handoff_package_id = "missing_handoff"
    loader = HandoffPackageLoader()

    result = loader.load_from_state(state=state, contract=contract)

    assert result["success"] is True
    assert result["raw_handoff_found"] is False
    assert any("No explicit Chunk 4 handoff package" in warning for warning in result["warnings"])

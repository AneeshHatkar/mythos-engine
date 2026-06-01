from backend.app.engines.story_generation.generation_contract_resolver import GenerationContractResolver
from backend.app.engines.story_generation.generation_mode_controller import GenerationModeController
from backend.app.engines.story_generation.handoff_package_loader import HandoffPackageLoader
from backend.app.engines.story_generation.story_context_builder import StoryContextBuilder
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
        simulation_id="sim_story_context_001",
        world_state=SimulationWorldState(
            world_id="world_oath",
            metadata={
                "world_rules": {"rule_oath_court_proof": "public evidence changes legal rank"},
                "locations": {"location_court": {"name": "Oath Court"}},
                "factions": {"faction_oath_court": {"name": "Oath Court"}},
            },
        ),
        character_states={
            "char_kael": SimulationCharacterState(
                character_id="char_kael",
                current_location_id="location_court",
                metadata={
                    "display_name": "Kael",
                    "voice_profile": {"style": "guarded"},
                    "goals": {"main": "prove the truth"},
                    "psychology": {"wound": "public exile"},
                    "emotional_state": {"shame": 0.7, "resolve": 0.8},
                    "role_tags": ["protagonist"],
                    "story_function_tags": ["drive_plot"],
                },
            ),
            "char_seren": SimulationCharacterState(
                character_id="char_seren",
                current_location_id="location_court",
                metadata={
                    "display_name": "Seren",
                    "voice_profile": {"style": "controlled"},
                    "emotional_state": {"guilt": 0.8},
                    "role_tags": ["love_interest"],
                    "story_function_tags": ["anchor_romance"],
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
                betrayal_risk=0.7,
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
                    "simulation_id": "sim_story_context_001",
                    "run_id": "run_story_context_001",
                    "selected_character_ids": ["char_kael", "char_seren"],
                    "linked_secret_ids": ["secret_rank_system"],
                    "causal_node_ids": ["cause_trial_reveal"],
                    "consequence_ids": ["cons_reputation_shift"],
                    "relationship_ids": ["rel_kael_seren"],
                }
            },
        },
    )


def build_context_and_contract():
    state = build_state()
    intent = StoryIntent(
        intent_id="intent_story_context",
        user_prompt="Write a tense dark academy scene.",
        desired_format=StoryFormat.scene,
        generation_mode=GenerationMode.full_scene,
        required_character_ids=["char_kael"],
        genres=["dark_academy"],
        tone_tags=["tense"],
    )
    mode = GenerationModeController().choose_mode(intent=intent)
    contract = GenerationContractResolver().resolve_contract(
        intent=intent,
        mode_decision=mode,
        handoff_payload=state.metadata["handoff_packages"]["handoff_001"],
    )["generation_contract"]
    context_package = HandoffPackageLoader().load_from_state(
        state=state,
        contract=contract,
    )["context_package"]
    return context_package, contract


def test_story_context_builder_builds_story_ready_context():
    context_package, contract = build_context_and_contract()
    builder = StoryContextBuilder()

    result = builder.build_story_context(
        context_package=context_package,
        contract=contract,
    )

    story_context = result["story_context"]

    assert result["success"] is True
    assert story_context["story_context_id"].startswith("storyctx_")
    assert story_context["active_cast"]
    assert story_context["world_rules"]
    assert story_context["relationship_pressure"]
    assert story_context["knowledge_boundaries"]
    assert story_context["causal_obligations"]
    assert story_context["readiness"]["ready_for_blueprint"] is True


def test_story_context_builder_active_cast_preserves_voice_and_emotion():
    context_package, contract = build_context_and_contract()
    builder = StoryContextBuilder()

    story_context = builder.build_story_context(
        context_package=context_package,
        contract=contract,
    )["story_context"]

    kael = next(item for item in story_context["active_cast"] if item["character_id"] == "char_kael")

    assert kael["display_name"] == "Kael"
    assert kael["voice_profile"]["style"] == "guarded"
    assert kael["emotional_state"]["resolve"] == 0.8
    assert kael["required"] is True


def test_story_context_builder_relationship_pressure_sorted():
    context_package, contract = build_context_and_contract()
    builder = StoryContextBuilder()

    story_context = builder.build_story_context(
        context_package=context_package,
        contract=contract,
    )["story_context"]

    pressure = story_context["relationship_pressure"][0]

    assert pressure["relationship_id"] == "rel_kael_seren"
    assert pressure["betrayal_risk"] == 0.7
    assert pressure["pressure_score"] >= 0.7


def test_story_context_builder_knowledge_boundaries_include_missing_required():
    context_package, contract = build_context_and_contract()
    contract.required_secret_ids.append("secret_seren_source")
    builder = StoryContextBuilder()

    story_context = builder.build_story_context(
        context_package=context_package,
        contract=contract,
    )["story_context"]

    kael_boundary = next(item for item in story_context["knowledge_boundaries"] if item["holder_id"] == "char_kael")

    assert "secret_rank_system" in kael_boundary["known_secret_ids"]
    assert "secret_seren_source" in kael_boundary["missing_required_secret_ids"]


def test_story_context_builder_validates_story_context():
    context_package, contract = build_context_and_contract()
    builder = StoryContextBuilder()

    story_context = builder.build_story_context(
        context_package=context_package,
        contract=contract,
    )["story_context"]

    validation = builder.validate_story_context(story_context=story_context)

    assert validation["success"] is True
    assert validation["valid"] is True
    assert "active_cast_present" in validation["passed_checks"]
    assert "ready_for_blueprint" in validation["passed_checks"]


def test_story_context_builder_summarizes_story_context():
    context_package, contract = build_context_and_contract()
    builder = StoryContextBuilder()

    story_context = builder.build_story_context(
        context_package=context_package,
        contract=contract,
    )["story_context"]

    summary = builder.summarize_story_context(story_context=story_context)

    assert summary["success"] is True
    assert summary["summary"]["cast_count"] >= 1
    assert summary["summary"]["world_rule_count"] >= 1
    assert summary["summary"]["selected_format"] == "scene"
    assert summary["summary"]["ready_for_blueprint"] is True


def test_story_context_builder_warns_on_weak_context():
    context_package, contract = build_context_and_contract()
    context_package.world_context = {}
    context_package.relationship_context = {}
    context_package.knowledge_context = {}
    context_package.causal_context = {}

    builder = StoryContextBuilder()

    story_context = builder.build_story_context(
        context_package=context_package,
        contract=contract,
    )["story_context"]

    assert any("No world rules" in warning for warning in story_context["warnings"])
    assert any("No relationship pressure" in warning for warning in story_context["warnings"])

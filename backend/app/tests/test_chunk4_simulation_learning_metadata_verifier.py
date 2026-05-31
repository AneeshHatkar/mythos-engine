from backend.app.engines.simulation.interaction_simulation_orchestrator import InteractionSimulationOrchestrator
from backend.app.engines.simulation.simulation_anti_genericity_validator import SimulationAntiGenericityValidator
from backend.app.engines.simulation.simulation_benchmark_pack import SimulationBenchmarkPack
from backend.app.engines.simulation.simulation_learning_adapter import SimulationLearningAdapter
from backend.app.engines.simulation.simulation_learning_metadata_verifier import SimulationLearningMetadataVerifier
from backend.app.engines.simulation.simulation_quality_scorer import SimulationQualityScorer
from backend.app.schemas.simulation import (
    SimulationCharacterState,
    SimulationKnowledgeState,
    SimulationRelationshipState,
    SimulationState,
    SimulationWorldState,
)


def build_state():
    return SimulationState(
        simulation_id="sim_learning_verify_001",
        world_state=SimulationWorldState(
            world_id="world_velmora",
            metadata={
                "world_rules": {"oath_court": "public proof changes status"},
                "locations": ["location_court"],
                "factions": ["faction_oath_court"],
            },
        ),
        character_states={
            "char_kael": SimulationCharacterState(
                character_id="char_kael",
                current_location_id="location_court",
                metadata={
                    "display_name": "Kael",
                    "role_tags": ["protagonist"],
                    "story_function_tags": ["drive_plot", "reveal_truth"],
                    "source_type": "user_supplied_character",
                    "user_requested": True,
                    "backstory": "Kael was disgraced by a corrupted ranking ritual.",
                    "goals": {"main": "prove the truth"},
                    "psychology": {"core_wound": "public exile"},
                    "voice_profile": {"style": "guarded"},
                    "backstory_depth": 0.9,
                    "agency_score": 0.8,
                    "uniqueness_score": 0.85,
                    "reputation_state": {"public": 0.4},
                },
            ),
            "char_seren": SimulationCharacterState(
                character_id="char_seren",
                current_location_id="location_court",
                metadata={
                    "display_name": "Seren",
                    "role_tags": ["love_interest", "traitor"],
                    "story_function_tags": ["anchor_romance", "cause_betrayal"],
                    "source_type": "created_character",
                    "backstory": "Seren protects her brother through the oath court.",
                    "goals": {"main": "protect the source"},
                    "psychology": {"core_wound": "duty over love"},
                    "voice_profile": {"style": "restrained"},
                    "backstory_depth": 0.85,
                    "agency_score": 0.7,
                    "uniqueness_score": 0.8,
                    "reputation_state": {"public": 0.35},
                },
            ),
            "char_vask": SimulationCharacterState(
                character_id="char_vask",
                current_location_id="location_court",
                metadata={
                    "display_name": "Vask",
                    "role_tags": ["antagonist"],
                    "story_function_tags": ["create_conflict", "force_choice"],
                    "source_type": "created_character",
                    "backstory": "Vask weaponizes institutional proof.",
                    "goals": {"main": "preserve hierarchy"},
                    "voice_profile": {"style": "polite threat"},
                    "backstory_depth": 0.75,
                    "agency_score": 0.75,
                    "uniqueness_score": 0.7,
                    "reputation_state": {"public": 0.3},
                },
            ),
        },
        knowledge_states={
            "char_kael": SimulationKnowledgeState(
                entity_id="char_kael",
                known_secret_ids=["secret_rank_system_edited"],
                evidence_seen_ids=["evidence_cracked_badge"],
            )
        },
        relationship_states={
            "rel_char_kael_char_seren": SimulationRelationshipState(
                relationship_id="rel_char_kael_char_seren",
                character_a_id="char_kael",
                character_b_id="char_seren",
                trust=0.28,
                affection=0.5,
                resentment=0.55,
                betrayal_risk=0.65,
                repair_potential=0.7,
                romantic_tension=0.5,
            )
        },
        metadata={
            "secret_registry": {"secret_rank_system_edited": {"secret_id": "secret_rank_system_edited"}},
            "evidence_registry": {"evidence_cracked_badge": {"evidence_id": "evidence_cracked_badge"}},
        },
    )


def create_learning_dataset_state():
    state = build_state()
    orchestrator = InteractionSimulationOrchestrator()

    orchestrator.run_interaction_simulation(
        state=state,
        run_id="run_verify_learning",
        story_request={
            "story_request_id": "story_verify_learning",
            "cast_id": "cast_verify_learning",
            "scene_id": "scene_verify_learning",
            "plot_arc_id": "arc_verify_learning",
            "format": "novel",
            "primary_genres": ["dark_academy", "romance"],
            "tone_tags": ["tense"],
            "distinctive_elements": ["oath court ritual", "cracked badge evidence"],
            "allow_any_character_count": True,
            "allow_project_created_characters": True,
            "required_roles": ["protagonist", "love_interest", "antagonist"],
            "required_story_functions": ["drive_plot", "anchor_romance", "create_conflict"],
            "scene_goal": "Kael reveals evidence in court.",
            "conflicts": [
                {
                    "conflict_id": "conflict_verify_learning",
                    "conflict_type": "truth",
                    "title": "Truth vs Protection",
                    "participant_ids": ["char_kael", "char_seren"],
                    "core_issue": "Truth saves Kael but exposes Seren's source.",
                    "opposing_goals": {"char_kael": "reveal truth", "char_seren": "protect source"},
                    "intensity": 0.8,
                    "stakes_score": 0.85,
                    "tension_score": 0.8,
                    "moral_complexity": 0.85,
                }
            ],
        },
        event_specs=[
            {
                "event_id": "evt_verify_learning",
                "event_type": "trial",
                "event_name": "Kael reveals the cracked badge.",
                "actor_ids": ["char_kael"],
                "target_ids": ["char_seren"],
                "witness_ids": ["char_vask"],
                "location_id": "location_court",
                "visibility": "public",
                "intensity": 0.85,
                "linked_secret_ids": ["secret_rank_system_edited"],
                "linked_evidence_ids": ["evidence_cracked_badge"],
            }
        ],
        target_cast_size=3,
    )

    SimulationQualityScorer().score_simulation_run(state=state, run_id="run_verify_learning")
    SimulationAntiGenericityValidator().validate_simulation_run(state=state, run_id="run_verify_learning")
    SimulationBenchmarkPack().run_benchmark(
        state=state,
        benchmark_id="minimal_scene",
        run_id="benchmark_verify_learning",
    )

    adapter = SimulationLearningAdapter()
    adapter.build_learning_dataset_from_state(
        state=state,
        dataset_id="dataset_verify_learning",
    )

    return state


def test_metadata_verifier_validates_learning_dataset():
    state = create_learning_dataset_state()
    verifier = SimulationLearningMetadataVerifier()
    dataset = state.metadata["simulation_learning_datasets"]["dataset_verify_learning"]

    result = verifier.verify_learning_dataset(dataset=dataset)

    assert result["success"] is True
    assert result["valid"] is True
    assert result["verification_score"] > 0.5
    assert "contains_source_text_false" in result["passed_checks"]
    assert "abstract_learning_only_true" in result["passed_checks"]


def test_metadata_verifier_detects_bad_dataset():
    verifier = SimulationLearningMetadataVerifier()

    bad_dataset = {
        "dataset_id": "bad_dataset",
        "signal_count": 1,
        "signals": [
            {
                "signal_id": "sig_bad",
                "signal_type": "quality_signal",
                "source_type": "test",
                "source_id": "source",
                "target_area": "quality",
                "value": 2.0,
                "label": "bad",
                "features": {"source_text": "unsafe"},
                "recommendations": [],
                "requires_human_review": False,
                "metadata": {},
            }
        ],
        "summary": {},
        "safety_contract": {
            "contains_source_text": True,
            "abstract_learning_only": False,
        },
    }

    result = verifier.verify_learning_dataset(dataset=bad_dataset)

    assert result["success"] is True
    assert result["valid"] is False
    assert any("out of bounds" in blocker for blocker in result["blockers"])
    assert any("contains_source_text" in blocker for blocker in result["blockers"])


def test_metadata_verifier_verifies_dataset_from_state_and_builds_map():
    state = create_learning_dataset_state()
    verifier = SimulationLearningMetadataVerifier()

    result = verifier.verify_dataset_from_state(
        state=state,
        dataset_id="dataset_verify_learning",
    )
    verification_map = verifier.build_verification_map(state=state)

    assert result["success"] is True
    assert result["verification_report"]["valid"] is True
    assert "learning_metadata_verification_dataset_verify_learning" in state.metadata["simulation_learning_metadata_verifications"]
    assert verification_map["success"] is True
    assert verification_map["verification_count"] == 1
    assert verification_map["valid_count"] == 1


def test_metadata_verifier_missing_dataset_from_state():
    state = build_state()
    verifier = SimulationLearningMetadataVerifier()

    result = verifier.verify_dataset_from_state(
        state=state,
        dataset_id="missing_dataset",
    )

    assert result["success"] is False
    assert "not found" in result["errors"][0]


def test_metadata_verifier_signal_coverage():
    state = create_learning_dataset_state()
    verifier = SimulationLearningMetadataVerifier()
    dataset = state.metadata["simulation_learning_datasets"]["dataset_verify_learning"]

    result = verifier.verify_signal_coverage(signals=dataset["signals"])

    assert "quality_signal" in result["signal_types"]
    assert "anti_genericity_signal" in result["signal_types"]
    assert "benchmark_signal" in result["signal_types"]
    assert "overall_quality_target_present" in result["passed_checks"]

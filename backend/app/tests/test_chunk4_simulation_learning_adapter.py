from backend.app.engines.simulation.interaction_simulation_orchestrator import InteractionSimulationOrchestrator
from backend.app.engines.simulation.simulation_anti_genericity_validator import SimulationAntiGenericityValidator
from backend.app.engines.simulation.simulation_benchmark_pack import SimulationBenchmarkPack
from backend.app.engines.simulation.simulation_learning_adapter import SimulationLearningAdapter
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
        simulation_id="sim_learning_001",
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


def create_scored_state():
    state = build_state()
    orchestrator = InteractionSimulationOrchestrator()

    orchestrator.run_interaction_simulation(
        state=state,
        run_id="run_learning",
        story_request={
            "story_request_id": "story_learning",
            "cast_id": "cast_learning",
            "scene_id": "scene_learning",
            "plot_arc_id": "arc_learning",
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
                    "conflict_id": "conflict_learning",
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
                "event_id": "evt_learning",
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

    scorer = SimulationQualityScorer()
    scorer.score_simulation_run(state=state, run_id="run_learning")

    anti = SimulationAntiGenericityValidator()
    anti.validate_simulation_run(state=state, run_id="run_learning")

    benchmark = SimulationBenchmarkPack()
    benchmark.run_benchmark(state=state, benchmark_id="minimal_scene", run_id="benchmark_learning_minimal")

    return state


def test_learning_adapter_creates_signal():
    adapter = SimulationLearningAdapter()

    signal = adapter.create_learning_signal(
        signal_id="signal_test",
        signal_type="quality_signal",
        source_type="simulation_run",
        source_id="run_1",
        target_area="causal_coherence",
        value=0.8,
        label="strong",
    )

    assert signal["signal_id"] == "signal_test"
    assert signal["signal_type"] == "quality_signal"
    assert signal["value"] == 0.8


def test_learning_adapter_builds_signals_from_run():
    state = create_scored_state()
    adapter = SimulationLearningAdapter()

    result = adapter.build_learning_signals_from_run(state=state, run_id="run_learning")

    assert result["success"] is True
    assert result["signal_count"] >= 2
    ids = {signal["signal_id"] for signal in result["learning_signals"]}
    assert "signal_run_learning_run_completion" in ids
    assert "signal_run_learning_handoff_readiness" in ids


def test_learning_adapter_builds_signals_from_quality_report():
    state = create_scored_state()
    adapter = SimulationLearningAdapter()
    report = state.metadata["simulation_quality_reports"]["quality_run_learning"]

    result = adapter.build_learning_signals_from_quality_report(quality_report=report)

    assert result["success"] is True
    assert result["signal_count"] >= 2
    assert any(signal["target_area"] == "overall_quality" for signal in result["learning_signals"])
    assert any(signal["signal_type"] == "quality_signal" for signal in result["learning_signals"])


def test_learning_adapter_builds_signals_from_anti_genericity_report():
    state = create_scored_state()
    adapter = SimulationLearningAdapter()
    report = state.metadata["simulation_anti_genericity_reports"]["anti_genericity_run_learning"]

    result = adapter.build_learning_signals_from_anti_genericity_report(
        anti_genericity_report=report
    )

    assert result["success"] is True
    assert result["signal_count"] >= 2
    assert any(signal["target_area"] == "anti_genericity" for signal in result["learning_signals"])
    assert any(signal["signal_type"] == "anti_genericity_signal" for signal in result["learning_signals"])


def test_learning_adapter_builds_signals_from_benchmark_report():
    state = create_scored_state()
    adapter = SimulationLearningAdapter()
    report = state.metadata["simulation_benchmark_reports"]["benchmark_report_minimal_scene"]

    result = adapter.build_learning_signals_from_benchmark_report(benchmark_report=report)

    assert result["success"] is True
    assert result["signal_count"] == 3
    assert any(signal["target_area"] == "benchmark_pass" for signal in result["learning_signals"])


def test_learning_adapter_builds_learning_dataset_from_state():
    state = create_scored_state()
    adapter = SimulationLearningAdapter()

    result = adapter.build_learning_dataset_from_state(
        state=state,
        dataset_id="dataset_learning_test",
    )

    dataset = result["dataset"]

    assert result["success"] is True
    assert dataset["dataset_id"] == "dataset_learning_test"
    assert dataset["signal_count"] > 0
    assert dataset["safety_contract"]["abstract_learning_only"] is True
    assert dataset["safety_contract"]["contains_source_text"] is False
    assert "dataset_learning_test" in state.metadata["simulation_learning_datasets"]


def test_learning_adapter_builds_feedback_learning_record():
    adapter = SimulationLearningAdapter()

    result = adapter.build_feedback_learning_record(
        feedback_id="feedback_001",
        run_id="run_learning",
        user_rating=0.9,
        user_notes="This was strong and specific.",
        accepted=True,
        target_area="scene_generation",
    )

    signal = result["learning_signal"]

    assert result["success"] is True
    assert signal["signal_type"] == "feedback_signal"
    assert signal["value"] == 0.9
    assert signal["label"] == "accepted"
    assert signal["requires_human_review"] is True


def test_learning_adapter_builds_learning_map():
    state = create_scored_state()
    adapter = SimulationLearningAdapter()

    dataset = adapter.build_learning_dataset_from_state(
        state=state,
        dataset_id="dataset_learning_map",
    )["dataset"]

    registered = adapter.register_learning_dataset_on_state(state=state, dataset=dataset)
    learning_map = adapter.build_learning_map(state=state)

    assert registered["success"] is True
    assert learning_map["success"] is True
    assert learning_map["dataset_count"] == 1
    assert "dataset_learning_map" in learning_map["learning_datasets"]

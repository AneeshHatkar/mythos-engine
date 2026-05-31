from backend.app.engines.simulation.interaction_simulation_orchestrator import InteractionSimulationOrchestrator
from backend.app.schemas.simulation import (
    SimulationCharacterState,
    SimulationKnowledgeState,
    SimulationRelationshipState,
    SimulationState,
    SimulationWorldState,
)


def build_state():
    return SimulationState(
        simulation_id="sim_orchestrator_001",
        world_state=SimulationWorldState(world_id="world_velmora"),
        character_states={
            "char_kael": SimulationCharacterState(
                character_id="char_kael",
                current_location_id="location_court",
                metadata={
                    "display_name": "Kael",
                    "role_tags": ["protagonist", "destined_person"],
                    "story_function_tags": ["drive_plot", "reveal_truth"],
                    "source_type": "user_supplied_character",
                    "user_requested": True,
                    "destined_weight": 0.9,
                    "backstory_depth": 0.85,
                    "agency_score": 0.8,
                    "uniqueness_score": 0.8,
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
                    "destined_weight": 0.7,
                    "backstory_depth": 0.8,
                    "agency_score": 0.7,
                    "uniqueness_score": 0.75,
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
            ),
            "char_seren": SimulationKnowledgeState(
                entity_id="char_seren",
                suspected_secret_ids=["secret_rank_system_edited"],
            ),
        },
        relationship_states={
            "rel_char_kael_char_seren": SimulationRelationshipState(
                relationship_id="rel_char_kael_char_seren",
                character_a_id="char_kael",
                character_b_id="char_seren",
                trust=0.28,
                respect=0.55,
                affection=0.5,
                resentment=0.55,
                betrayal_risk=0.65,
                repair_potential=0.7,
                romantic_tension=0.5,
                knowledge_asymmetry=0.6,
            )
        },
        metadata={
            "secret_registry": {
                "secret_rank_system_edited": {"secret_id": "secret_rank_system_edited"}
            },
            "evidence_registry": {
                "evidence_cracked_badge": {"evidence_id": "evidence_cracked_badge"}
            },
        },
    )


def test_orchestrator_creates_and_registers_run():
    state = build_state()
    orchestrator = InteractionSimulationOrchestrator()

    run = orchestrator.create_simulation_run_record(
        run_id="run_001",
        story_request={"format": "novel"},
        selected_character_ids=["char_kael"],
    )

    result = orchestrator.register_run_on_state(state=state, run_record=run)

    assert result["success"] is True
    assert "run_001" in state.metadata["simulation_runs"]
    assert state.metadata["simulation_runs"]["run_001"]["status"] == "created"


def test_orchestrator_runs_interaction_simulation():
    state = build_state()
    orchestrator = InteractionSimulationOrchestrator()

    result = orchestrator.run_interaction_simulation(
        state=state,
        run_id="run_trial_truth",
        story_request={
            "story_request_id": "story_trial_truth",
            "cast_id": "cast_trial_truth",
            "scene_id": "scene_trial_truth",
            "plot_arc_id": "arc_trial_truth",
            "format": "novel",
            "primary_genres": ["dark_academy", "romance"],
            "tone_tags": ["tense", "mythic"],
            "allow_any_character_count": True,
            "allow_project_created_characters": True,
            "required_roles": ["protagonist", "love_interest", "antagonist"],
            "required_story_functions": ["drive_plot", "anchor_romance", "create_conflict"],
            "scene_goal": "Kael reveals the truth in court and forces Seren to choose.",
            "plot_goal": "Create a causally coherent trial reveal arc.",
            "location_id": "location_court",
            "conflicts": [
                {
                    "conflict_id": "conflict_truth_vs_protection",
                    "conflict_type": "truth",
                    "title": "Truth vs Protection",
                    "participant_ids": ["char_kael", "char_seren"],
                    "core_issue": "Reveal truth or protect the source.",
                    "opposing_goals": {
                        "char_kael": "reveal the truth",
                        "char_seren": "protect the source",
                    },
                    "linked_secret_ids": ["secret_rank_system_edited"],
                    "linked_evidence_ids": ["evidence_cracked_badge"],
                    "intensity": 0.8,
                    "stakes_score": 0.85,
                    "tension_score": 0.8,
                    "moral_complexity": 0.85,
                }
            ],
        },
        event_specs=[
            {
                "event_id": "evt_trial_reveal",
                "event_type": "trial",
                "event_name": "Kael reveals the cracked badge in court.",
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

    run = result["run_record"]
    outputs = run["outputs"]

    assert result["success"] is True
    assert run["status"] == "completed"
    assert "cast_selected" in run["steps"]
    assert "events_registered" in run["steps"]
    assert "handoff_payloads_built" in run["steps"]
    assert outputs["registered_event_ids"] == ["evt_trial_reveal"]
    assert outputs["handoff_package_id"] == "handoff_run_trial_truth"
    assert outputs["generation_control_payload_id"] == "generation_control_run_trial_truth"
    assert "cast_trial_truth" in state.metadata["cast_registry"]
    assert "evt_trial_reveal" in state.metadata["event_registry"]
    assert "stakes_event_evt_trial_reveal" in state.metadata["stakes_registry"]
    assert "handoff_run_trial_truth" in state.metadata["handoff_packages"]
    assert "generation_control_run_trial_truth" in state.metadata["generation_control_payloads"]


def test_orchestrator_builds_summary():
    state = build_state()
    orchestrator = InteractionSimulationOrchestrator()

    orchestrator.run_interaction_simulation(
        state=state,
        run_id="run_summary",
        story_request={
            "cast_id": "cast_summary",
            "scene_id": "scene_summary",
            "format": "scene",
            "required_roles": ["protagonist"],
            "required_story_functions": ["drive_plot"],
        },
        event_specs=[
            {
                "event_id": "evt_summary",
                "event_type": "private_confession",
                "event_name": "Seren confesses something.",
                "actor_ids": ["char_seren"],
                "target_ids": ["char_kael"],
                "location_id": "location_court",
                "visibility": "private",
                "intensity": 0.7,
            }
        ],
        target_cast_size=2,
    )

    summary = orchestrator.build_orchestrator_summary(state=state, run_id="run_summary")

    assert summary["success"] is True
    assert summary["run_id"] == "run_summary"
    assert summary["ready_for_chunk5_generation"] is True
    assert summary["handoff_package_id"] == "handoff_run_summary"
    assert summary["generation_control_payload_id"] == "generation_control_run_summary"


def test_orchestrator_builds_map():
    state = build_state()
    orchestrator = InteractionSimulationOrchestrator()

    orchestrator.run_interaction_simulation(
        state=state,
        run_id="run_map",
        story_request={
            "cast_id": "cast_map",
            "scene_id": "scene_map",
            "format": "scene",
            "required_roles": ["protagonist"],
            "required_story_functions": ["drive_plot"],
        },
        event_specs=[],
        target_cast_size=2,
    )

    result = orchestrator.build_orchestrator_map(state=state)

    assert result["success"] is True
    assert result["run_count"] == 1
    assert "run_map" in result["run_records"]
    assert result["ready_run_count"] == 1

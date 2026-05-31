from backend.app.engines.simulation.interaction_simulation_orchestrator import InteractionSimulationOrchestrator
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
        simulation_id="sim_quality_001",
        world_state=SimulationWorldState(world_id="world_velmora"),
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
                    "backstory": "Kael was disgraced before.",
                    "goals": {"main": "prove the truth"},
                    "psychology": {"core_wound": "exile"},
                    "voice_profile": {"style": "guarded"},
                    "backstory_depth": 0.9,
                    "agency_score": 0.8,
                    "uniqueness_score": 0.85,
                },
            ),
            "char_seren": SimulationCharacterState(
                character_id="char_seren",
                current_location_id="location_court",
                metadata={
                    "display_name": "Seren",
                    "role_tags": ["love_interest", "traitor"],
                    "story_function_tags": ["anchor_romance", "cause_betrayal"],
                    "backstory": "Seren serves a dangerous oath court.",
                    "goals": {"main": "protect the source"},
                    "psychology": {"core_wound": "duty over love"},
                    "voice_profile": {"style": "controlled"},
                    "backstory_depth": 0.85,
                    "agency_score": 0.7,
                    "uniqueness_score": 0.8,
                },
            ),
            "char_vask": SimulationCharacterState(
                character_id="char_vask",
                current_location_id="location_court",
                metadata={
                    "display_name": "Vask",
                    "role_tags": ["antagonist"],
                    "story_function_tags": ["create_conflict", "force_choice"],
                    "backstory": "Vask weaponizes institutions.",
                    "goals": {"main": "control the court"},
                    "voice_profile": {"style": "formal threat"},
                    "backstory_depth": 0.75,
                    "agency_score": 0.75,
                    "uniqueness_score": 0.7,
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


def create_completed_run_state():
    state = build_state()
    orchestrator = InteractionSimulationOrchestrator()

    orchestrator.run_interaction_simulation(
        state=state,
        run_id="run_quality",
        story_request={
            "story_request_id": "story_quality",
            "cast_id": "cast_quality",
            "scene_id": "scene_quality",
            "plot_arc_id": "arc_quality",
            "format": "novel",
            "primary_genres": ["dark_academy", "romance"],
            "tone_tags": ["tense"],
            "allow_any_character_count": True,
            "allow_project_created_characters": True,
            "required_roles": ["protagonist", "love_interest", "antagonist"],
            "required_story_functions": ["drive_plot", "anchor_romance", "create_conflict"],
            "scene_goal": "Kael reveals the truth.",
            "conflicts": [
                {
                    "conflict_id": "conflict_truth",
                    "conflict_type": "truth",
                    "title": "Truth vs Protection",
                    "participant_ids": ["char_kael", "char_seren"],
                    "core_issue": "Reveal truth or protect source.",
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
                "event_id": "evt_quality",
                "event_type": "trial",
                "event_name": "Kael reveals the evidence in court.",
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
    return state


def test_quality_scorer_scores_completed_run():
    state = create_completed_run_state()
    scorer = SimulationQualityScorer()

    result = scorer.score_simulation_run(state=state, run_id="run_quality")
    report = result["quality_report"]

    assert result["success"] is True
    assert report["run_id"] == "run_quality"
    assert report["overall_quality_score"] > 0.5
    assert report["quality_label"] in {"usable", "strong", "excellent", "needs_revision"}
    assert "causal_coherence" in report["dimension_scores"]
    assert "handoff_readiness" in report["dimension_scores"]
    assert "generation_control_readiness" in report["dimension_scores"]
    assert "quality_run_quality" in state.metadata["simulation_quality_reports"]


def test_quality_scorer_dimension_scores_are_available():
    state = create_completed_run_state()
    scorer = SimulationQualityScorer()
    run = state.metadata["simulation_runs"]["run_quality"]

    assert scorer.score_causal_coherence(state=state, run=run) > 0
    assert scorer.score_character_readiness(state=state, selected_character_ids=run["selected_character_ids"]) > 0.5
    assert scorer.score_relationship_continuity(state=state, selected_character_ids=run["selected_character_ids"]) > 0
    assert scorer.score_emotional_continuity(state=state, selected_character_ids=run["selected_character_ids"]) > 0
    assert scorer.score_stakes_clarity(state=state, stakes_ids=run["outputs"]["stakes_ids"]) > 0
    assert scorer.score_tension_pacing(state=state, tension_curve_id=run["outputs"]["tension_curve_id"]) > 0
    assert scorer.score_conflict_usefulness(state=state, conflict_ids=run["outputs"]["conflict_ids"]) > 0
    assert scorer.score_consequence_traceability(state=state, consequence_ids=run["outputs"]["consequence_ids"]) > 0
    assert scorer.score_cast_balance(state=state, cast_id="cast_quality") > 0
    assert scorer.score_handoff_readiness(state=state, handoff_package_id=run["outputs"]["handoff_package_id"]) > 0
    assert scorer.score_generation_control_readiness(state=state, generation_control_payload_id=run["outputs"]["generation_control_payload_id"]) > 0


def test_quality_scorer_blocks_missing_run():
    state = build_state()
    scorer = SimulationQualityScorer()

    result = scorer.score_simulation_run(state=state, run_id="missing_run")

    assert result["success"] is False
    assert "not found" in result["errors"][0]


def test_quality_scorer_builds_quality_map():
    state = create_completed_run_state()
    scorer = SimulationQualityScorer()

    scorer.score_simulation_run(state=state, run_id="run_quality")
    result = scorer.build_quality_map(state=state)

    assert result["success"] is True
    assert result["quality_report_count"] == 1
    assert result["best_quality_report"]["quality_report_id"] == "quality_run_quality"
    assert "quality_run_quality" in result["quality_reports"]

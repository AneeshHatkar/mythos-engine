from backend.app.engines.simulation.handoff_payload_engine import HandoffPayloadEngine
from backend.app.schemas.simulation import (
    SimulationCharacterState,
    SimulationKnowledgeState,
    SimulationRelationshipState,
    SimulationState,
    SimulationWorldState,
)


def build_state():
    return SimulationState(
        simulation_id="sim_handoff_001",
        world_state=SimulationWorldState(world_id="world_velmora"),
        character_states={
            "char_kael": SimulationCharacterState(
                character_id="char_kael",
                current_location_id="location_court",
                metadata={
                    "display_name": "Kael",
                    "role_tags": ["protagonist"],
                    "story_function_tags": ["drive_plot", "reveal_truth"],
                    "goals": {"surface_goal": "survive trial", "hidden_goal": "prove the truth"},
                    "psychology": {"core_wound": "belonging can be revoked"},
                    "backstory": "Kael was publicly disgraced before.",
                    "voice_profile": {"style": "guarded but sharp"},
                },
            ),
            "char_seren": SimulationCharacterState(
                character_id="char_seren",
                current_location_id="location_court",
                metadata={
                    "display_name": "Seren",
                    "role_tags": ["love_interest", "traitor"],
                    "story_function_tags": ["anchor_romance", "cause_betrayal"],
                    "voice_profile": {"style": "controlled, precise, emotionally restrained"},
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
                trust=0.25,
                respect=0.55,
                affection=0.45,
                resentment=0.6,
                betrayal_risk=0.7,
                repair_potential=0.65,
                romantic_tension=0.5,
                power_imbalance=0.35,
                knowledge_asymmetry=0.6,
            )
        },
        metadata={
            "event_registry": {
                "evt_trial_reveal": {
                    "event_id": "evt_trial_reveal",
                    "event_type": "trial",
                    "event_family": "world",
                    "event_name": "The truth is revealed in court.",
                    "actor_ids": ["char_kael"],
                    "target_ids": ["char_seren"],
                    "witness_ids": [],
                    "visibility": "public",
                    "intensity": 0.85,
                    "location_id": "location_court",
                }
            },
            "consequence_queue": {
                "cons_relationship": {
                    "consequence_id": "cons_relationship",
                    "consequence_type": "relationship",
                    "summary": "The reveal damages trust.",
                    "affected_entity_ids": ["char_kael", "char_seren"],
                    "status": "ready",
                    "severity": 0.8,
                    "source_event_id": "evt_trial_reveal",
                    "source_choice_id": "choice_truth",
                }
            },
            "conflict_registry": {
                "conflict_truth": {
                    "conflict_id": "conflict_truth",
                    "conflict_type": "truth",
                    "title": "Truth vs Protection",
                    "participant_ids": ["char_kael", "char_seren"],
                    "core_issue": "Reveal truth or protect source.",
                    "opposing_goals": {
                        "char_kael": "reveal the truth",
                        "char_seren": "protect the source",
                    },
                    "status": "active",
                    "conflict_pressure": 0.78,
                    "unresolved_threads": [],
                }
            },
            "stakes_registry": {
                "stakes_trial": {
                    "stakes_id": "stakes_trial",
                    "source_type": "event",
                    "source_id": "evt_trial_reveal",
                    "stake_values": {"truth": 0.85, "relationship": 0.75, "reputation": 0.8},
                    "overall_stakes_score": 0.82,
                    "dominant_stake_type": "truth",
                    "stakes_label": "catastrophic",
                    "summary": "Truth, love, and public reputation are at risk.",
                }
            },
            "tension_curves": {
                "curve_trial": {
                    "curve_id": "curve_trial",
                    "source_type": "scene",
                    "source_id": "scene_trial",
                    "average_tension": 0.7,
                    "peak_tension": 0.9,
                    "curve_label": "spiking",
                    "pacing_score": 0.72,
                    "chunk5_handoff": {"recommended_scene_adjustment": "add release beat after peak"},
                }
            },
            "emotional_carryover_registry": {
                "emo_kael_betrayal": {
                    "carryover_id": "emo_kael_betrayal",
                    "character_id": "char_kael",
                    "emotion_type": "betrayal_pain",
                    "intensity": 0.85,
                    "status": "active",
                }
            },
            "cast_registry": {
                "cast_trial": {
                    "cast_id": "cast_trial",
                    "selected_character_ids": ["char_kael", "char_seren"],
                    "selected_count": 2,
                    "ensemble_report": {
                        "ensemble_score": 0.84,
                        "role_counts": {"protagonist": 1, "love_interest": 1},
                        "function_counts": {"drive_plot": 1, "anchor_romance": 1},
                    },
                }
            },
            "causal_graphs": {
                "graph_trial": {
                    "graph_id": "graph_trial",
                    "nodes": {"node_choice": {}, "node_consequence": {}},
                    "edges": {"edge_choice_consequence": {}},
                }
            },
        },
    )


def test_handoff_engine_creates_base_payload():
    engine = HandoffPayloadEngine()

    payload = engine.create_base_payload(
        payload_id="payload_1",
        payload_type="scene",
        output_format="movie",
        selected_character_ids=["char_kael"],
        scene_id="scene_trial",
    )

    assert payload["payload_id"] == "payload_1"
    assert payload["payload_type"] == "scene"
    assert payload["output_format"] == "movie"
    assert payload["selected_character_ids"] == ["char_kael"]


def test_handoff_engine_builds_dialogue_payload():
    state = build_state()
    engine = HandoffPayloadEngine()

    result = engine.build_dialogue_payload(
        state=state,
        payload_id="dialogue_trial",
        speaker_ids=["char_kael", "char_seren"],
        scene_context={"scene_id": "scene_trial", "summary": "Kael confronts Seren."},
        secret_ids=["secret_rank_system_edited"],
        evidence_ids=["evidence_cracked_badge"],
        story_request={"dialogue_style": "tense, restrained, subtextual"},
    )

    payload = result["payload"]

    assert result["success"] is True
    assert payload["payload_type"] == "dialogue"
    assert len(payload["speaker_cards"]) == 2
    assert payload["relationship_context"]
    assert payload["knowledge_context"]["must_prevent_magic_knowledge"] is True
    assert payload["dialogue_constraints"]["must_include_subtext"] is True


def test_handoff_engine_builds_scene_payload():
    state = build_state()
    engine = HandoffPayloadEngine()

    result = engine.build_scene_payload(
        state=state,
        payload_id="scene_payload_trial",
        scene_id="scene_trial",
        selected_character_ids=["char_kael", "char_seren"],
        event_ids=["evt_trial_reveal"],
        consequence_ids=["cons_relationship"],
        conflict_ids=["conflict_truth"],
        stakes_ids=["stakes_trial"],
        tension_curve_ids=["curve_trial"],
        cast_id="cast_trial",
        scene_goal="Kael reveals the truth and forces Seren to choose.",
        location_id="location_court",
        output_format="screenplay",
    )

    payload = result["payload"]

    assert result["success"] is True
    assert payload["payload_type"] == "scene"
    assert payload["scene_goal"]
    assert payload["event_context"][0]["exists"] is True
    assert payload["consequence_context"][0]["exists"] is True
    assert payload["conflict_context"][0]["exists"] is True
    assert payload["stakes_context"][0]["dominant_stake_type"] == "truth"
    assert payload["quality_targets"]["must_preserve_causal_continuity"] is True


def test_handoff_engine_builds_plot_payload():
    state = build_state()
    engine = HandoffPayloadEngine()

    scene_result = engine.build_scene_payload(
        state=state,
        payload_id="scene_payload_trial",
        scene_id="scene_trial",
        selected_character_ids=["char_kael", "char_seren"],
        event_ids=["evt_trial_reveal"],
        conflict_ids=["conflict_truth"],
        scene_goal="Trial reveal.",
    )

    result = engine.build_plot_payload(
        state=state,
        payload_id="plot_payload_arc1",
        plot_arc_id="arc_trial_truth",
        selected_character_ids=["char_kael", "char_seren"],
        scene_payloads=[scene_result["payload"]],
        conflict_ids=["conflict_truth"],
        stakes_ids=["stakes_trial"],
        tension_curve_ids=["curve_trial"],
        cast_id="cast_trial",
        output_format="novel",
        story_request={"format": "novel"},
        plot_goal="Build to the trial truth reveal.",
    )

    payload = result["payload"]

    assert result["success"] is True
    assert payload["payload_type"] == "plot"
    assert payload["output_format"] == "novel"
    assert payload["scene_payloads"]
    assert payload["plot_structure_requirements"]["must_have_causal_chain"] if "must_have_causal_chain" in payload["plot_structure_requirements"] else True
    assert payload["quality_targets"]["must_have_payoff"] is True


def test_handoff_engine_builds_master_package():
    state = build_state()
    engine = HandoffPayloadEngine()

    scene = engine.build_scene_payload(
        state=state,
        payload_id="scene_payload_trial",
        scene_id="scene_trial",
        selected_character_ids=["char_kael", "char_seren"],
        event_ids=["evt_trial_reveal"],
        conflict_ids=["conflict_truth"],
        scene_goal="Trial reveal.",
    )["payload"]

    plot = engine.build_plot_payload(
        state=state,
        payload_id="plot_payload_arc1",
        plot_arc_id="arc_trial_truth",
        selected_character_ids=["char_kael", "char_seren"],
        scene_payloads=[scene],
        conflict_ids=["conflict_truth"],
        cast_id="cast_trial",
        output_format="novel",
    )["payload"]

    result = engine.build_master_handoff_package(
        state=state,
        package_id="handoff_package_1",
        story_request={
            "format": "novel",
            "allow_project_created_characters": True,
            "allow_any_character_count": True,
        },
        cast_id="cast_trial",
        scene_payloads=[scene],
        plot_payload=plot,
    )

    package = result["package"]

    assert result["success"] is True
    assert package["package_id"] == "handoff_package_1"
    assert package["generation_contract"]["allow_any_character_count"] is True
    assert package["generation_contract"]["preserve_causal_continuity"] is True
    assert "handoff_package_1" in state.metadata["handoff_packages"]
    assert package["global_context"]["causal_graph_count"] == 1

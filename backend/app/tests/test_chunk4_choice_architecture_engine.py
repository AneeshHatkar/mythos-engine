from backend.app.engines.simulation.choice_architecture_engine import ChoiceArchitectureEngine
from backend.app.engines.simulation.choice_feasibility_engine import ChoiceFeasibilityEngine
from backend.app.schemas.simulation import (
    SimulationCharacterState,
    SimulationKnowledgeState,
    SimulationRelationshipState,
    SimulationState,
    SimulationWorldState,
)


def build_state():
    return SimulationState(
        simulation_id="sim_choice_arch_001",
        world_state=SimulationWorldState(
            world_id="world_velmora",
            metadata={
                "travel_edges": [
                    {
                        "from_location_id": "location_archive",
                        "to_location_id": "location_court",
                        "bidirectional": True,
                    }
                ]
            },
        ),
        character_states={
            "char_kael": SimulationCharacterState(
                character_id="char_kael",
                current_location_id="location_archive",
                metadata={
                    "goals": {
                        "surface_goal": "survive academy ranking",
                        "hidden_goal": "prove the ranking system is edited",
                        "true_need": "belonging without permission",
                    },
                    "psychology": {
                        "core_wound": "belonging can be revoked after public failure",
                        "dominant_moral_value": "truth and protection",
                    },
                    "resource_ids": ["resource_archive_access"],
                },
            ),
            "char_seren": SimulationCharacterState(
                character_id="char_seren",
                current_location_id="location_court",
                metadata={
                    "goals": {
                        "surface_goal": "protect family position",
                        "hidden_goal": "free herself from inherited loyalty",
                    }
                },
            ),
            "char_vask": SimulationCharacterState(character_id="char_vask"),
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
                trust=0.58,
                respect=0.62,
                affection=0.22,
                resentment=0.12,
                betrayal_risk=0.2,
                repair_potential=0.52,
            )
        },
    )


def sample_choices():
    feasibility = ChoiceFeasibilityEngine()
    return [
        feasibility.create_choice_record(
            choice_id="choice_truth",
            actor_id="char_kael",
            action_type="expose_secret",
            summary="Expose the rank edit truth at trial.",
            target_id="char_seren",
            required_secret_ids=["secret_rank_system_edited"],
            required_evidence_ids=["evidence_cracked_badge"],
            required_resource_ids=["resource_archive_access"],
            required_location_id="location_court",
            moral_cost=0.2,
            social_risk=0.8,
            emotional_cost=0.7,
        ),
        feasibility.create_choice_record(
            choice_id="choice_silence",
            actor_id="char_kael",
            action_type="hide_truth",
            summary="Stay silent to protect Seren.",
            target_id="char_seren",
            moral_cost=0.7,
            social_risk=0.4,
            emotional_cost=0.6,
        ),
        feasibility.create_choice_record(
            choice_id="choice_missing_resource",
            actor_id="char_kael",
            action_type="seek_evidence",
            summary="Use a missing forbidden key.",
            required_resource_ids=["resource_forbidden_key"],
            moral_cost=0.3,
            social_risk=0.5,
            emotional_cost=0.4,
        ),
    ]


def test_choice_architecture_builds_choice_set():
    state = build_state()
    engine = ChoiceArchitectureEngine()

    result = engine.build_choice_set(
        state=state,
        choice_set_id="choice_set_trial",
        actor_id="char_kael",
        candidate_choices=sample_choices(),
        choice_set_type="trial_choice",
        user_intent={"must_have": ["trial truth reveal"]},
    )

    choice_set = result["choice_set"]

    assert result["success"] is True
    assert choice_set["choice_set_id"] == "choice_set_trial"
    assert choice_set["choice_set_type"] == "trial_choice"
    assert len(choice_set["visible_choices"]) >= 1
    assert "recommended_choice_id" in choice_set
    assert "stakes_profile" in choice_set
    assert result["chunk5_handoff"]["scene_type"] == "trial_decision_scene"


def test_choice_architecture_choice_cards_include_consequence_preview():
    state = build_state()
    engine = ChoiceArchitectureEngine()

    result = engine.build_choice_set(
        state=state,
        choice_set_id="choice_set_trial",
        actor_id="char_kael",
        candidate_choices=sample_choices(),
        choice_set_type="trial_choice",
    )

    card = result["choice_set"]["visible_choices"][0]

    assert "pressure_label" in card
    assert "story_function" in card
    assert "choice_visibility" in card
    assert "consequence_preview" in card
    assert "required_setup" in card


def test_choice_architecture_builds_moral_dilemma():
    state = build_state()
    engine = ChoiceArchitectureEngine()
    choices = sample_choices()

    result = engine.build_moral_dilemma(
        state=state,
        choice_set_id="choice_set_dilemma",
        actor_id="char_kael",
        good_choice=choices[0],
        costly_choice=choices[1],
        dangerous_choice=choices[2],
        user_intent={"genre": "dark academy moral dilemma"},
    )

    choice_set = result["choice_set"]

    assert result["success"] is True
    assert choice_set["choice_set_type"] == "moral_dilemma"
    assert "dilemma_axes" in choice_set
    assert "dilemma_quality" in choice_set
    assert result["chunk5_handoff"]["scene_type"] == "moral_dilemma_scene"


def test_choice_architecture_builds_blackmail_response_choices():
    state = build_state()
    state.metadata.setdefault("leverage_registry", {})["lev_vask_kael"] = {
        "leverage_id": "lev_vask_kael",
        "holder_id": "char_vask",
        "target_id": "char_kael",
        "status": "active",
        "pressure_level": 0.8,
    }

    engine = ChoiceArchitectureEngine()

    result = engine.build_response_choices_from_pressure(
        state=state,
        choice_set_id="choice_set_blackmail",
        actor_id="char_kael",
        pressure_source_type="blackmail",
        pressure_source_id="lev_vask_kael",
        target_id="char_vask",
    )

    choice_set = result["choice_set"]

    assert result["success"] is True
    assert choice_set["choice_set_type"] == "blackmail_response"
    assert len(choice_set["visible_choices"]) == 3
    assert choice_set["pressure_source"]["pressure_source_id"] == "lev_vask_kael"
    assert result["chunk5_handoff"]["scene_type"] == "coercion_response_scene"


def test_choice_architecture_marks_locked_choices_visible():
    state = build_state()
    engine = ChoiceArchitectureEngine()

    result = engine.build_choice_set(
        state=state,
        choice_set_id="choice_set_trial",
        actor_id="char_kael",
        candidate_choices=sample_choices(),
        choice_set_type="trial_choice",
        include_blocked_choices=True,
    )

    visible = result["choice_set"]["visible_choices"]

    assert any(choice["choice_visibility"] == "locked_visible" for choice in visible)


def test_choice_architecture_compares_choice_sets():
    state = build_state()
    engine = ChoiceArchitectureEngine()

    first = engine.build_choice_set(
        state=state,
        choice_set_id="choice_set_trial",
        actor_id="char_kael",
        candidate_choices=sample_choices(),
        choice_set_type="trial_choice",
    )["choice_set"]

    second = engine.build_moral_dilemma(
        state=state,
        choice_set_id="choice_set_dilemma",
        actor_id="char_kael",
        good_choice=sample_choices()[0],
        costly_choice=sample_choices()[1],
        dangerous_choice=sample_choices()[2],
    )["choice_set"]

    result = engine.compare_choice_sets(
        state=state,
        choice_sets=[first, second],
    )

    assert result["success"] is True
    assert result["choice_set_count"] == 2
    assert len(result["ranked_choice_sets"]) == 2
    assert result["best_choice_set"]["quality_score"] >= result["ranked_choice_sets"][-1]["quality_score"]


def test_choice_architecture_chunk5_handoff_has_plot_branch_tags():
    state = build_state()
    engine = ChoiceArchitectureEngine()

    result = engine.build_choice_set(
        state=state,
        choice_set_id="choice_set_trial",
        actor_id="char_kael",
        candidate_choices=sample_choices(),
        choice_set_type="trial_choice",
    )

    handoff = result["chunk5_handoff"]

    assert "scene_requirements" in handoff
    assert "plot_branch_tags" in handoff
    assert "trial_choice" in handoff["plot_branch_tags"]

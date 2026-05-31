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
        simulation_id="sim_choice_001",
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
                loyalty=0.18,
                resentment=0.12,
                betrayal_risk=0.2,
                knowledge_asymmetry=0.35,
                repair_potential=0.52,
            )
        },
    )


def add_pressure_state(state):
    state.metadata.setdefault("obligation_registry", {})["obl_trial_testimony"] = {
        "obligation_id": "obl_trial_testimony",
        "status": "active",
    }
    state.metadata.setdefault("leverage_registry", {})["lev_vask_seren"] = {
        "leverage_id": "lev_vask_seren",
        "status": "active",
    }


def test_choice_feasibility_engine_creates_choice_record():
    engine = ChoiceFeasibilityEngine()

    choice = engine.create_choice_record(
        choice_id="choice_expose_secret",
        actor_id="char_kael",
        action_type="expose_secret",
        summary="Expose the rank edit at trial.",
        target_id="char_seren",
        required_secret_ids=["secret_rank_system_edited"],
        required_evidence_ids=["evidence_cracked_badge"],
        required_resource_ids=["resource_archive_access"],
        required_location_id="location_court",
    )

    assert choice["choice_id"] == "choice_expose_secret"
    assert choice["actor_id"] == "char_kael"
    assert choice["required_location_id"] == "location_court"
    assert choice["required_secret_ids"] == ["secret_rank_system_edited"]


def test_choice_feasibility_allows_choice_with_travel_warning():
    state = build_state()
    engine = ChoiceFeasibilityEngine()

    choice = engine.create_choice_record(
        choice_id="choice_expose_secret",
        actor_id="char_kael",
        action_type="expose_secret",
        summary="Expose the rank edit at trial using evidence.",
        target_id="char_seren",
        required_secret_ids=["secret_rank_system_edited"],
        required_evidence_ids=["evidence_cracked_badge"],
        required_resource_ids=["resource_archive_access"],
        required_location_id="location_court",
        required_relationship_thresholds={"trust": 0.4},
        moral_cost=0.2,
        emotional_cost=0.5,
    )

    report = engine.evaluate_choice_feasibility(
        state=state,
        choice=choice,
        user_intent={"must_have": ["trial truth reveal"]},
    )

    assert report["success"] is True
    assert report["feasible"] is True
    assert report["feasibility_label"] in {"feasible", "risky", "strongly_feasible"}
    assert "travel_path_exists" in report["passed_checks"]
    assert any("must travel" in warning for warning in report["warnings"])
    assert report["chunk5_handoff"]["choice_can_be_plotted"] is True


def test_choice_feasibility_blocks_missing_knowledge():
    state = build_state()
    engine = ChoiceFeasibilityEngine()

    choice = engine.create_choice_record(
        choice_id="choice_seren_expose",
        actor_id="char_seren",
        action_type="expose_secret",
        summary="Seren exposes evidence she has not seen.",
        required_secret_ids=["secret_rank_system_edited"],
        required_evidence_ids=["evidence_cracked_badge"],
    )

    report = engine.evaluate_choice_feasibility(state=state, choice=choice)

    assert report["feasible"] is False
    assert report["feasibility_label"] == "blocked"
    assert any("knowledge state" in blocker or "evidence" in blocker for blocker in report["blockers"])
    assert "add evidence discovery/access scene" in report["chunk5_handoff"]["required_setup"]


def test_choice_feasibility_blocks_missing_resource():
    state = build_state()
    engine = ChoiceFeasibilityEngine()

    choice = engine.create_choice_record(
        choice_id="choice_use_missing_resource",
        actor_id="char_kael",
        action_type="seek_evidence",
        summary="Use a forbidden key.",
        required_resource_ids=["resource_forbidden_key"],
    )

    report = engine.evaluate_choice_feasibility(state=state, choice=choice)

    assert report["feasible"] is False
    assert any("missing required resource" in blocker for blocker in report["blockers"])


def test_choice_feasibility_blocks_relationship_threshold():
    state = build_state()
    engine = ChoiceFeasibilityEngine()

    choice = engine.create_choice_record(
        choice_id="choice_repair_relationship",
        actor_id="char_kael",
        action_type="repair_relationship",
        summary="Ask Seren for forgiveness.",
        target_id="char_seren",
        required_relationship_thresholds={"trust": 0.9},
    )

    report = engine.evaluate_choice_feasibility(state=state, choice=choice)

    assert report["feasible"] is False
    assert any("below required threshold" in blocker for blocker in report["blockers"])


def test_choice_feasibility_checks_required_obligation_and_leverage():
    state = build_state()
    add_pressure_state(state)
    engine = ChoiceFeasibilityEngine()

    choice = engine.create_choice_record(
        choice_id="choice_resist_blackmail",
        actor_id="char_seren",
        action_type="resist_blackmail",
        summary="Seren resists Vask's blackmail because of her oath.",
        required_obligation_ids=["obl_trial_testimony"],
        required_leverage_ids=["lev_vask_seren"],
        external_pressure=0.8,
    )

    report = engine.evaluate_choice_feasibility(state=state, choice=choice)

    assert report["success"] is True
    assert "obligation_obl_trial_testimony_usable" in report["passed_checks"]
    assert "leverage_lev_vask_seren_active" in report["passed_checks"]


def test_choice_feasibility_blocks_canon_lock():
    state = build_state()
    state.metadata["canon_locks"] = [
        {
            "tag": "kael_cannot_die_before_trial",
            "locked": True,
            "mode": "block",
        }
    ]
    engine = ChoiceFeasibilityEngine()

    choice = engine.create_choice_record(
        choice_id="choice_break_canon",
        actor_id="char_kael",
        action_type="sacrifice",
        summary="Kael dies before the trial.",
        metadata={"canon_tags": ["kael_cannot_die_before_trial"]},
    )

    report = engine.evaluate_choice_feasibility(state=state, choice=choice)

    assert report["feasible"] is False
    assert any("canon lock" in blocker for blocker in report["blockers"])
    assert "branch timeline or revise canon lock" in report["chunk5_handoff"]["required_setup"]


def test_choice_feasibility_ranks_choices():
    state = build_state()
    engine = ChoiceFeasibilityEngine()

    good = engine.create_choice_record(
        choice_id="choice_good",
        actor_id="char_kael",
        action_type="expose_secret",
        summary="Expose the truth with evidence.",
        required_secret_ids=["secret_rank_system_edited"],
        required_evidence_ids=["evidence_cracked_badge"],
        required_resource_ids=["resource_archive_access"],
    )
    bad = engine.create_choice_record(
        choice_id="choice_bad",
        actor_id="char_seren",
        action_type="expose_secret",
        summary="Expose evidence without knowing it.",
        required_secret_ids=["secret_rank_system_edited"],
        required_evidence_ids=["evidence_cracked_badge"],
    )

    ranked = engine.rank_feasible_choices(
        state=state,
        choices=[bad, good],
    )

    assert ranked["success"] is True
    assert ranked["choice_count"] == 2
    assert ranked["feasible_count"] >= 1
    assert ranked["ranked_choices"][0]["feasibility_score"] >= ranked["ranked_choices"][1]["feasibility_score"]


def test_choice_feasibility_builds_map():
    state = build_state()
    engine = ChoiceFeasibilityEngine()

    choice = engine.create_choice_record(
        choice_id="choice_good",
        actor_id="char_kael",
        action_type="expose_secret",
        summary="Expose the truth with evidence.",
        required_secret_ids=["secret_rank_system_edited"],
        required_evidence_ids=["evidence_cracked_badge"],
    )

    result = engine.build_choice_feasibility_map(
        state=state,
        choices_by_character={"char_kael": [choice]},
    )

    assert result["success"] is True
    assert result["character_count"] == 1
    assert result["total_choice_count"] == 1
    assert "char_kael" in result["choice_feasibility_records"]

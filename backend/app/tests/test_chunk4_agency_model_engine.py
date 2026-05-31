from backend.app.engines.simulation.agency_model_engine import AgencyModelEngine
from backend.app.schemas.simulation import (
    SimulationCharacterState,
    SimulationKnowledgeState,
    SimulationRelationshipState,
    SimulationState,
    SimulationWorldState,
)


def build_state():
    return SimulationState(
        simulation_id="sim_agency_001",
        world_state=SimulationWorldState(world_id="world_velmora"),
        character_states={
            "char_kael": SimulationCharacterState(
                character_id="char_kael",
                current_location_id="location_court",
                metadata={
                    "goals": {
                        "surface_goal": "survive academy ranking",
                        "hidden_goal": "prove the ranking system is edited",
                        "true_need": "belonging without permission",
                    },
                    "psychology": {
                        "core_wound": "belonging can be revoked after public failure",
                        "dominant_moral_value": "truth and protection",
                        "fear_profile": {"primary": "being made unreal"},
                        "public_mask": "controlled precision",
                        "private_truth": "terrified of being erased",
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
                        "true_need": "truth without permission",
                    },
                    "psychology": {
                        "core_wound": "love becomes dangerous when witnessed",
                        "dominant_moral_value": "loyalty and family survival",
                    },
                },
            ),
            "char_vask": SimulationCharacterState(character_id="char_vask"),
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
                trust=0.52,
                affection=0.28,
                respect=0.62,
                loyalty=0.25,
                resentment=0.18,
                betrayal_risk=0.22,
                knowledge_asymmetry=0.35,
                rivalry=0.28,
                repair_potential=0.55,
            )
        },
    )


def add_pressure_state(state):
    state.metadata.setdefault("obligation_registry", {})["obl_seren_trial"] = {
        "obligation_id": "obl_seren_trial",
        "promiser_id": "char_seren",
        "promisee_id": "char_kael",
        "status": "active",
        "pressure_score": 0.7,
    }
    state.metadata.setdefault("leverage_registry", {})["lev_vask_seren"] = {
        "leverage_id": "lev_vask_seren",
        "holder_id": "char_vask",
        "target_id": "char_seren",
        "status": "active",
        "pressure_level": 0.8,
    }


def test_agency_engine_builds_agency_profile():
    state = build_state()
    add_pressure_state(state)
    engine = AgencyModelEngine()

    result = engine.build_agency_profile(state=state, character_id="char_seren")

    profile = result["agency_profile"]

    assert result["success"] is True
    assert profile["character_id"] == "char_seren"
    assert profile["active_obligation_count"] == 1
    assert profile["active_leverage_against_count"] == 1
    assert profile["agency_freedom_score"] < 1.0
    assert profile["coercion_pressure"] > 0


def test_agency_engine_allows_motivated_secret_exposure():
    state = build_state()
    engine = AgencyModelEngine()

    result = engine.evaluate_action_agency(
        state=state,
        character_id="char_kael",
        action_type="expose_secret",
        action_summary="Kael exposes the ranking edit truth during trial.",
        target_id="char_seren",
        required_secret_ids=["secret_rank_system_edited"],
        required_evidence_ids=["evidence_cracked_badge"],
        required_resource_ids=["resource_archive_access"],
        moral_cost=0.2,
        social_risk=0.7,
        emotional_cost=0.5,
        user_intent={"genre": "dark academy trial reveal", "must_have": ["truth", "trial", "secret reveal"]},
    )

    assert result["success"] is True
    assert result["viable"] is True
    assert result["agency_score"] >= 0.35
    assert "knows_secret_rank_system_edited" in result["passed_checks"]
    assert "saw_evidence_cracked_badge" in result["passed_checks"]
    assert result["recommendation"] in {"allow_action", "allow_only_if_scene_shows_motive_and_pressure"}


def test_agency_engine_blocks_action_without_required_knowledge():
    state = build_state()
    engine = AgencyModelEngine()

    result = engine.evaluate_action_agency(
        state=state,
        character_id="char_seren",
        action_type="expose_secret",
        action_summary="Seren exposes proof she has not seen.",
        required_secret_ids=["secret_rank_system_edited"],
        required_evidence_ids=["evidence_cracked_badge"],
    )

    assert result["viable"] is False
    assert any("has not seen required evidence" in blocker for blocker in result["blockers"])


def test_agency_engine_warns_for_betrayal_without_trigger():
    state = build_state()
    engine = AgencyModelEngine()

    result = engine.evaluate_action_agency(
        state=state,
        character_id="char_kael",
        action_type="betray",
        action_summary="Kael betrays Seren without any clear pressure.",
        target_id="char_seren",
        moral_cost=0.8,
        emotional_cost=0.7,
    )

    assert result["success"] is True
    assert any("clear trigger" in warning for warning in result["warnings"])


def test_agency_engine_ranks_candidate_actions():
    state = build_state()
    add_pressure_state(state)
    engine = AgencyModelEngine()

    result = engine.rank_actions_for_character(
        state=state,
        character_id="char_kael",
        candidate_actions=[
            {
                "action_type": "expose_secret",
                "action_summary": "Expose the rank edit using evidence.",
                "target_id": "char_seren",
                "required_secret_ids": ["secret_rank_system_edited"],
                "required_evidence_ids": ["evidence_cracked_badge"],
                "required_resource_ids": ["resource_archive_access"],
                "moral_cost": 0.2,
                "emotional_cost": 0.5,
            },
            {
                "action_type": "betray",
                "action_summary": "Betray Seren randomly.",
                "target_id": "char_seren",
                "moral_cost": 0.9,
                "emotional_cost": 0.8,
            },
        ],
        user_intent={"must_have": ["trial truth reveal"]},
    )

    assert result["success"] is True
    assert result["action_count"] == 2
    assert result["best_action"]["action_type"] in {"expose_secret", "betray"}
    assert result["ranked_actions"][0]["agency_score"] >= result["ranked_actions"][1]["agency_score"]


def test_agency_engine_builds_agency_map():
    state = build_state()
    add_pressure_state(state)
    engine = AgencyModelEngine()

    result = engine.build_agency_map(state=state)

    assert result["success"] is True
    assert result["character_count"] == 3
    assert "char_kael" in result["agency_profiles"]
    assert "average_agency_freedom" in result
    assert "average_coercion_pressure" in result


def test_agency_engine_chunk5_handoff_flags_plot_forcing():
    state = build_state()
    engine = AgencyModelEngine()

    result = engine.evaluate_action_agency(
        state=state,
        character_id="char_kael",
        action_type="attempt_blackmail",
        action_summary="Kael suddenly blackmails Seren without setup.",
        target_id="char_seren",
        moral_cost=0.9,
        emotional_cost=0.8,
    )

    handoff = result["chunk5_handoff"]

    assert "agency_scene_requirement" in handoff
    assert isinstance(handoff["avoid_plot_forcing"], bool)

from backend.app.engines.simulation.cast_selection_engine import CastSelectionEngine
from backend.app.schemas.simulation import (
    SimulationCharacterState,
    SimulationRelationshipState,
    SimulationState,
    SimulationWorldState,
)


def build_state():
    return SimulationState(
        simulation_id="sim_cast_001",
        world_state=SimulationWorldState(world_id="world_velmora"),
        character_states={
            "char_kael": SimulationCharacterState(
                character_id="char_kael",
                metadata={
                    "display_name": "Kael",
                    "role_tags": ["protagonist", "destined_person"],
                    "story_function_tags": ["drive_plot", "reveal_truth", "carry_emotional_core"],
                    "source_type": "user_supplied_character",
                    "user_requested": True,
                    "destined_weight": 0.9,
                    "normal_person_weight": 0.2,
                    "faction_ids": ["faction_students"],
                    "backstory_depth": 0.9,
                    "agency_score": 0.8,
                    "uniqueness_score": 0.85,
                    "tone_tags": ["dark_academy"],
                },
            ),
            "char_seren": SimulationCharacterState(
                character_id="char_seren",
                metadata={
                    "display_name": "Seren",
                    "role_tags": ["love_interest", "traitor", "destined_person"],
                    "story_function_tags": ["anchor_romance", "cause_betrayal", "test_loyalty"],
                    "source_type": "created_character",
                    "destined_weight": 0.8,
                    "faction_ids": ["faction_oath_court"],
                    "romance_tags": ["slow_burn", "forbidden"],
                    "conflict_tags": ["betrayal"],
                    "backstory_depth": 0.85,
                    "agency_score": 0.7,
                    "uniqueness_score": 0.8,
                    "tone_tags": ["dark_academy", "romance"],
                },
            ),
            "char_vask": SimulationCharacterState(
                character_id="char_vask",
                metadata={
                    "display_name": "Vask",
                    "role_tags": ["antagonist", "faction_leader"],
                    "story_function_tags": ["create_conflict", "force_choice", "hold_secret"],
                    "source_type": "created_character",
                    "destined_weight": 0.4,
                    "normal_person_weight": 0.2,
                    "faction_ids": ["faction_oath_court"],
                    "conflict_tags": ["blackmail", "political"],
                    "mystery_tags": ["hidden_agenda"],
                    "backstory_depth": 0.75,
                    "agency_score": 0.75,
                    "uniqueness_score": 0.7,
                },
            ),
            "char_mira": SimulationCharacterState(
                character_id="char_mira",
                metadata={
                    "display_name": "Mira",
                    "role_tags": ["ordinary_person", "friend"],
                    "story_function_tags": ["provide_contrast", "offer_wisdom"],
                    "source_type": "created_character",
                    "destined_weight": 0.1,
                    "normal_person_weight": 0.9,
                    "backstory_depth": 0.55,
                    "agency_score": 0.65,
                    "uniqueness_score": 0.6,
                },
            ),
        },
        relationship_states={
            "rel_kael_seren": SimulationRelationshipState(
                relationship_id="rel_kael_seren",
                character_a_id="char_kael",
                character_b_id="char_seren",
                trust=0.45,
                affection=0.55,
                betrayal_risk=0.65,
                repair_potential=0.7,
            ),
            "rel_seren_vask": SimulationRelationshipState(
                relationship_id="rel_seren_vask",
                character_a_id="char_seren",
                character_b_id="char_vask",
                trust=0.2,
                rivalry=0.5,
                resentment=0.45,
                betrayal_risk=0.6,
            ),
        },
        metadata={
            "emotional_carryover_registry": {
                "emo_kael_betrayal": {
                    "character_id": "char_kael",
                    "intensity": 0.8,
                    "status": "active",
                },
                "emo_seren_guilt": {
                    "character_id": "char_seren",
                    "intensity": 0.75,
                    "status": "active",
                },
            }
        },
    )


def test_cast_engine_creates_candidate():
    engine = CastSelectionEngine()

    candidate = engine.create_cast_candidate(
        character_id="char_test",
        display_name="Test",
        role_tags=["protagonist", "unknown_role"],
        story_function_tags=["drive_plot", "unknown_function"],
        source_type="user_supplied_character",
        user_requested=True,
        destined_weight=0.8,
        backstory_depth=0.9,
    )

    assert candidate["character_id"] == "char_test"
    assert "protagonist" in candidate["role_tags"]
    assert "created_character" in candidate["role_tags"]
    assert "drive_plot" in candidate["story_function_tags"]
    assert candidate["user_requested"] is True


def test_cast_engine_builds_candidate_from_state():
    state = build_state()
    engine = CastSelectionEngine()

    candidate = engine.build_candidate_from_state(state=state, character_id="char_kael")

    assert candidate["character_id"] == "char_kael"
    assert candidate["display_name"] == "Kael"
    assert candidate["user_requested"] is True
    assert candidate["source_type"] == "user_supplied_character"
    assert candidate["relationship_density"] > 0
    assert candidate["emotional_pressure"] > 0


def test_cast_engine_scores_candidate_for_story():
    state = build_state()
    engine = CastSelectionEngine()
    candidate = engine.build_candidate_from_state(state=state, character_id="char_kael")

    score = engine.score_candidate_for_story(
        candidate=candidate,
        story_request={
            "required_roles": ["protagonist"],
            "required_story_functions": ["drive_plot", "reveal_truth"],
            "preferred_faction_ids": ["faction_students"],
            "tone_tags": ["dark_academy"],
            "character_mode": "mixed",
        },
    )

    assert score["success"] is True
    assert score["character_id"] == "char_kael"
    assert score["cast_fit_score"] > 0.6
    assert score["score_components"]["role_fit"] == 1.0
    assert score["score_components"]["function_fit"] == 1.0


def test_cast_engine_selects_cast_and_preserves_user_requested_character():
    state = build_state()
    engine = CastSelectionEngine()

    result = engine.select_cast(
        state=state,
        story_request={
            "story_request_id": "story_dark_academy_trial",
            "cast_id": "cast_trial",
            "format": "movie",
            "character_mode": "mixed",
            "required_roles": ["protagonist", "antagonist", "love_interest"],
            "required_story_functions": ["drive_plot", "create_conflict", "anchor_romance"],
            "tone_tags": ["dark_academy"],
        },
        target_cast_size=3,
        allow_any_size=True,
    )

    cast = result["cast_record"]

    assert result["success"] is True
    assert cast["selected_count"] == 3
    assert "char_kael" in cast["selected_character_ids"]
    assert "char_vask" in cast["selected_character_ids"]
    assert "char_seren" in cast["selected_character_ids"]
    assert result["chunk5_handoff"]["must_preserve_user_requested_characters"] is True


def test_cast_engine_evaluates_ensemble_balance():
    state = build_state()
    engine = CastSelectionEngine()

    candidates = [
        engine.build_candidate_from_state(state=state, character_id="char_kael"),
        engine.build_candidate_from_state(state=state, character_id="char_seren"),
        engine.build_candidate_from_state(state=state, character_id="char_vask"),
    ]

    report = engine.evaluate_ensemble_balance(
        selected_candidates=candidates,
        story_request={
            "required_roles": ["protagonist", "love_interest", "antagonist"],
            "required_story_functions": ["drive_plot", "anchor_romance", "create_conflict"],
        },
    )

    assert report["success"] is True
    assert report["selected_count"] == 3
    assert report["role_coverage"] == 1.0
    assert report["function_coverage"] == 1.0
    assert report["ensemble_score"] > 0.5


def test_cast_engine_optimizes_cast_for_scene():
    state = build_state()
    engine = CastSelectionEngine()

    result = engine.optimize_cast_for_scene(
        state=state,
        scene_request={
            "scene_id": "scene_trial_reveal",
            "format": "scene",
            "required_roles": ["protagonist", "antagonist"],
            "required_story_functions": ["reveal_truth", "force_choice"],
            "target_cast_size": 2,
            "tone_tags": ["dark_academy"],
        },
    )

    cast = result["cast_record"]

    assert result["success"] is True
    assert cast["selected_count"] == 2
    assert "char_kael" in cast["selected_character_ids"]
    assert result["chunk5_handoff"]["scene_grouping_needed"] is False


def test_cast_engine_registers_cast_and_builds_map():
    state = build_state()
    engine = CastSelectionEngine()

    result = engine.select_cast(
        state=state,
        story_request={
            "story_request_id": "story_1",
            "cast_id": "cast_1",
            "format": "movie",
            "required_roles": ["protagonist", "antagonist"],
            "required_story_functions": ["drive_plot", "create_conflict"],
        },
        target_cast_size=3,
    )

    registered = engine.register_cast_on_state(state=state, cast_record=result["cast_record"])
    cast_map = engine.build_cast_map(state=state)

    assert registered["success"] is True
    assert "cast_1" in state.metadata["cast_registry"]
    assert cast_map["success"] is True
    assert cast_map["cast_count"] == 1
    assert cast_map["best_cast"]["cast_id"] == "cast_1"

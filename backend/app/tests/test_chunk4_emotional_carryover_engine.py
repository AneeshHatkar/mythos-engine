from backend.app.engines.simulation.emotional_carryover_engine import EmotionalCarryoverEngine
from backend.app.schemas.simulation import SimulationCharacterState, SimulationState, SimulationWorldState


def build_state():
    return SimulationState(
        simulation_id="sim_emotional_001",
        world_state=SimulationWorldState(world_id="world_velmora"),
        character_states={
            "char_kael": SimulationCharacterState(character_id="char_kael"),
            "char_seren": SimulationCharacterState(character_id="char_seren"),
            "char_vask": SimulationCharacterState(character_id="char_vask"),
        },
    )


def test_emotional_engine_creates_and_registers_carryover():
    state = build_state()
    engine = EmotionalCarryoverEngine()

    record = engine.create_emotional_carryover_record(
        carryover_id="emo_kael_betrayal_pain",
        character_id="char_kael",
        emotion_type="betrayal_pain",
        source_event_id="evt_betrayal",
        intensity=0.8,
        persistence=0.75,
        trigger_tags=["betrayal", "trial"],
        linked_character_ids=["char_seren"],
        summary="Kael cannot shake the betrayal.",
    )

    result = engine.register_carryover_on_state(state=state, carryover_record=record)

    assert result["success"] is True
    assert "emo_kael_betrayal_pain" in state.metadata["emotional_carryover_registry"]
    assert "emo_kael_betrayal_pain" in state.character_states["char_kael"].metadata["emotional_carryover_ids"]


def test_emotional_engine_generates_carryover_from_event():
    state = build_state()
    engine = EmotionalCarryoverEngine()

    event = {
        "event_id": "evt_betrayal",
        "event_type": "betrayal",
        "event_family": "relationship",
        "actor_ids": ["char_seren"],
        "target_ids": ["char_kael"],
        "visibility": "public",
        "intensity": 0.85,
        "linked_secret_ids": ["secret_rank_system_edited"],
        "linked_obligation_ids": ["obl_seren_kael"],
    }

    result = engine.generate_carryover_from_event(state=state, event_record=event)

    assert result["success"] is True
    assert result["carryover_count"] == 2
    emotions = {record["character_id"]: record["emotion_type"] for record in result["carryover_records"]}
    assert emotions["char_seren"] == "guilt"
    assert emotions["char_kael"] == "betrayal_pain"


def test_emotional_engine_generates_carryover_from_conflict_resolution():
    state = build_state()
    engine = EmotionalCarryoverEngine()

    conflict = {
        "conflict_id": "conflict_truth",
        "conflict_type": "truth",
        "participant_ids": ["char_kael", "char_seren"],
        "conflict_pressure": 0.8,
        "linked_secret_ids": ["secret_rank_system_edited"],
        "linked_obligation_ids": ["obl_seren_kael"],
    }

    result = engine.generate_carryover_from_conflict_resolution(
        state=state,
        conflict_record=conflict,
        outcome_type="open_wound",
    )

    assert result["success"] is True
    assert result["carryover_count"] == 2
    assert all(record["emotion_type"] == "resentment" for record in result["carryover_records"])
    assert all(record["persistence"] >= 0.7 for record in result["carryover_records"])


def test_emotional_engine_activates_carryovers_for_scene():
    state = build_state()
    engine = EmotionalCarryoverEngine()

    record = engine.create_emotional_carryover_record(
        carryover_id="emo_kael_betrayal_pain",
        character_id="char_kael",
        emotion_type="betrayal_pain",
        intensity=0.75,
        persistence=0.8,
        trigger_tags=["trial", "betrayal"],
        linked_character_ids=["char_seren"],
        linked_secret_ids=["secret_rank_system_edited"],
    )
    engine.register_carryover_on_state(state=state, carryover_record=record)

    result = engine.activate_carryovers_for_scene(
        state=state,
        character_id="char_kael",
        scene_tags=["trial", "truth"],
        present_character_ids=["char_seren"],
        linked_secret_ids=["secret_rank_system_edited"],
    )

    assert result["success"] is True
    assert result["activated_count"] == 1
    assert result["activated_carryovers"][0]["carryover_id"] == "emo_kael_betrayal_pain"
    assert result["scene_emotional_pressure"] > 0


def test_emotional_engine_decays_carryovers():
    state = build_state()
    engine = EmotionalCarryoverEngine()

    record = engine.create_emotional_carryover_record(
        carryover_id="emo_seren_guilt",
        character_id="char_seren",
        emotion_type="guilt",
        intensity=0.6,
        decay_rate=0.2,
        persistence=0.2,
    )
    engine.register_carryover_on_state(state=state, carryover_record=record)

    result = engine.decay_carryovers(state=state, character_id="char_seren", ticks=1)

    updated = state.metadata["emotional_carryover_registry"]["emo_seren_guilt"]

    assert result["success"] is True
    assert result["updated_count"] == 1
    assert updated["intensity"] < 0.6
    assert updated["history"]


def test_emotional_engine_resolves_and_transforms_carryover():
    state = build_state()
    engine = EmotionalCarryoverEngine()

    record = engine.create_emotional_carryover_record(
        carryover_id="emo_kael_distrust",
        character_id="char_kael",
        emotion_type="distrust",
        intensity=0.7,
    )
    engine.register_carryover_on_state(state=state, carryover_record=record)

    result = engine.resolve_carryover(
        state=state,
        carryover_id="emo_kael_distrust",
        resolution_reason="Seren proves her loyalty.",
        transformed_emotion_type="trust",
    )

    updated = result["updated_carryover"]

    assert result["success"] is True
    assert updated["status"] == "transformed"
    assert updated["emotion_type"] == "trust"
    assert updated["intensity"] < 0.7


def test_emotional_engine_builds_character_emotional_state():
    state = build_state()
    engine = EmotionalCarryoverEngine()

    records = [
        engine.create_emotional_carryover_record(
            carryover_id="emo_kael_betrayal",
            character_id="char_kael",
            emotion_type="betrayal_pain",
            intensity=0.8,
            persistence=0.8,
        ),
        engine.create_emotional_carryover_record(
            carryover_id="emo_kael_hope",
            character_id="char_kael",
            emotion_type="hope",
            intensity=0.4,
            persistence=0.4,
        ),
    ]
    for record in records:
        engine.register_carryover_on_state(state=state, carryover_record=record)

    report = engine.build_character_emotional_state(state=state, character_id="char_kael")

    assert report["success"] is True
    assert report["active_carryover_count"] == 2
    assert report["dominant_emotion"] == "betrayal_pain"
    assert report["emotional_pressure"] > 0
    assert report["scene_guidance"]["must_acknowledge_emotion"] is True


def test_emotional_engine_builds_carryover_map():
    state = build_state()
    engine = EmotionalCarryoverEngine()

    record = engine.create_emotional_carryover_record(
        carryover_id="emo_seren_guilt",
        character_id="char_seren",
        emotion_type="guilt",
        intensity=0.75,
        persistence=0.7,
    )
    engine.register_carryover_on_state(state=state, carryover_record=record)

    result = engine.build_emotional_carryover_map(state=state)

    assert result["success"] is True
    assert result["carryover_count"] == 1
    assert result["active_carryover_count"] == 1
    assert result["highest_pressure_character"] == "char_seren"
    assert "chunk5_handoff" in result
    assert result["chunk5_handoff"]["emotional_scene_requirements"]

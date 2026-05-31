from backend.app.engines.simulation.relationship_repair_engine import RelationshipRepairEngine
from backend.app.schemas.simulation import (
    SimulationCharacterState,
    SimulationKnowledgeState,
    SimulationRelationshipState,
    SimulationState,
    SimulationWorldState,
)


def build_state():
    return SimulationState(
        simulation_id="sim_repair_001",
        world_state=SimulationWorldState(world_id="world_velmora"),
        character_states={
            "char_kael": SimulationCharacterState(character_id="char_kael"),
            "char_seren": SimulationCharacterState(character_id="char_seren"),
        },
        knowledge_states={
            "char_seren": SimulationKnowledgeState(
                entity_id="char_seren",
                known_secret_ids=["secret_rank_system_edited"],
                evidence_seen_ids=["evidence_cracked_badge"],
            )
        },
        relationship_states={
            "rel_char_kael_char_seren": SimulationRelationshipState(
                relationship_id="rel_char_kael_char_seren",
                character_a_id="char_kael",
                character_b_id="char_seren",
                trust=0.25,
                resentment=0.55,
                betrayal_risk=0.65,
                repair_potential=0.7,
                affection=0.32,
                romantic_tension=0.35,
            )
        },
        metadata={
            "obligation_registry": {
                "obl_seren_truth": {
                    "obligation_id": "obl_seren_truth",
                    "status": "active",
                }
            },
            "emotional_carryover_registry": {
                "emo_kael_betrayal": {
                    "carryover_id": "emo_kael_betrayal",
                    "character_id": "char_kael",
                    "emotion_type": "betrayal_pain",
                    "intensity": 0.8,
                    "status": "active",
                    "linked_character_ids": ["char_seren"],
                    "history": [],
                }
            },
        },
    )


def make_repair(engine):
    return engine.create_repair_attempt_record(
        repair_id="repair_seren_kael_truth",
        relationship_id="rel_char_kael_char_seren",
        initiator_id="char_seren",
        receiver_id="char_kael",
        repair_type="truth_confession",
        summary="Seren confesses what she hid and accepts the cost.",
        required_truth_ids=["secret_rank_system_edited"],
        required_evidence_ids=["evidence_cracked_badge"],
        required_obligation_ids=["obl_seren_truth"],
        source_carryover_ids=["emo_kael_betrayal"],
        apology_quality=0.75,
        accountability=0.85,
        sincerity=0.8,
        emotional_risk=0.7,
        timing_fit=0.65,
    )


def test_relationship_repair_engine_creates_and_registers_repair():
    state = build_state()
    engine = RelationshipRepairEngine()

    repair = make_repair(engine)
    result = engine.register_repair_attempt_on_state(state=state, repair_record=repair)

    assert result["success"] is True
    assert "repair_seren_kael_truth" in state.metadata["relationship_repair_registry"]
    assert "repair_seren_kael_truth" in state.character_states["char_seren"].metadata["relationship_repair_ids"]


def test_relationship_repair_engine_evaluates_feasible_repair():
    state = build_state()
    engine = RelationshipRepairEngine()

    repair = make_repair(engine)
    engine.register_repair_attempt_on_state(state=state, repair_record=repair)

    report = engine.evaluate_repair_feasibility(state=state, repair_id="repair_seren_kael_truth")

    assert report["success"] is True
    assert report["feasible"] is True
    assert report["repair_score"] >= 0.5
    assert "relationship_exists" in report["passed_checks"]
    assert "knows_truth_secret_rank_system_edited" in report["passed_checks"]
    assert "saw_evidence_evidence_cracked_badge" in report["passed_checks"]
    assert report["chunk5_handoff"]["scene_type"] == "truth_confession_repair_scene"


def test_relationship_repair_engine_blocks_missing_knowledge():
    state = build_state()
    engine = RelationshipRepairEngine()

    repair = engine.create_repair_attempt_record(
        repair_id="repair_kael_missing_truth",
        relationship_id="rel_char_kael_char_seren",
        initiator_id="char_kael",
        receiver_id="char_seren",
        repair_type="truth_confession",
        summary="Kael confesses a truth he does not know.",
        required_truth_ids=["secret_rank_system_edited"],
    )
    engine.register_repair_attempt_on_state(state=state, repair_record=repair)

    report = engine.evaluate_repair_feasibility(state=state, repair_id="repair_kael_missing_truth")

    assert report["feasible"] is False
    assert report["repair_label"] == "blocked"
    assert any("knowledge state" in blocker or "does not know" in blocker for blocker in report["blockers"])


def test_relationship_repair_engine_applies_successful_outcome():
    state = build_state()
    engine = RelationshipRepairEngine()

    repair = make_repair(engine)
    engine.register_repair_attempt_on_state(state=state, repair_record=repair)

    result = engine.apply_repair_outcome(
        state=state,
        repair_id="repair_seren_kael_truth",
        outcome="successful",
        outcome_event_id="evt_confession",
        notes="Kael does not fully forgive her, but the wall cracks.",
    )

    assert result["success"] is True
    assert result["updated_repair"]["status"] == "successful"
    assert result["relationship_update"]["trust_delta"] > 0
    assert result["relationship_update"]["resentment_delta"] < 0
    assert result["carryover_updates"][0]["new_intensity"] < 0.8
    assert result["chunk5_handoff"]["next_scene_need"] == "show changed behavior later"


def test_relationship_repair_engine_applies_failed_outcome():
    state = build_state()
    engine = RelationshipRepairEngine()

    repair = make_repair(engine)
    engine.register_repair_attempt_on_state(state=state, repair_record=repair)

    result = engine.apply_repair_outcome(
        state=state,
        repair_id="repair_seren_kael_truth",
        outcome="failed",
        outcome_event_id="evt_failed_apology",
        notes="Seren explains too late and Kael shuts down.",
    )

    assert result["success"] is True
    assert result["updated_repair"]["status"] == "failed"
    assert result["relationship_update"]["trust_delta"] < 0
    assert result["relationship_update"]["resentment_delta"] > 0
    assert result["carryover_updates"][0]["new_intensity"] >= 0.8


def test_relationship_repair_engine_suggests_repair_paths():
    state = build_state()
    engine = RelationshipRepairEngine()

    result = engine.suggest_repair_paths(
        state=state,
        relationship_id="rel_char_kael_char_seren",
        initiator_id="char_seren",
        receiver_id="char_kael",
    )

    assert result["success"] is True
    assert result["options"]
    assert result["recommended_repair_type"] in {
        "atonement",
        "truth_confession",
        "proof_of_loyalty",
        "wound_validation",
        "romantic_repair",
    }


def test_relationship_repair_engine_builds_repair_map():
    state = build_state()
    engine = RelationshipRepairEngine()

    repair = make_repair(engine)
    engine.register_repair_attempt_on_state(state=state, repair_record=repair)

    result = engine.build_relationship_repair_map(state=state)

    assert result["success"] is True
    assert result["repair_attempt_count"] == 1
    assert "repair_seren_kael_truth" in result["repair_records"]
    assert result["best_repair_attempt"]["repair_id"] == "repair_seren_kael_truth"

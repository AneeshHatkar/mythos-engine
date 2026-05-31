from backend.app.engines.simulation.relationship_arc_engine import RelationshipArcEngine
from backend.app.schemas.simulation import (
    DeltaOperation,
    RelationshipDelta,
    SimulationRelationshipState,
    SimulationState,
    SimulationWorldState,
)


def rivalry_rel():
    return SimulationRelationshipState(
        relationship_id="rel_char_kael_char_seren",
        character_a_id="char_kael",
        character_b_id="char_seren",
        relationship_type="rivalry_with_hidden_respect:respect_hidden_inside_competition",
        trust=0.22,
        respect=0.52,
        rivalry=0.65,
        resentment=0.18,
        repair_potential=0.45,
    )


def romance_rel():
    return SimulationRelationshipState(
        relationship_id="rel_char_kael_char_seren",
        character_a_id="char_kael",
        character_b_id="char_seren",
        relationship_type="romance_blocked_by_public_status:slow_burn_under_visibility_threat",
        trust=0.28,
        respect=0.45,
        romantic_tension=0.48,
        fear=0.28,
        power_imbalance=0.45,
        knowledge_asymmetry=0.38,
        repair_potential=0.52,
    )


def betrayal_rel():
    return SimulationRelationshipState(
        relationship_id="rel_char_kael_char_vask",
        character_a_id="char_kael",
        character_b_id="char_vask",
        relationship_type="loyalty_under_betrayal_pressure:trust_tested_by_secret_leverage",
        trust=0.08,
        resentment=0.55,
        betrayal_risk=0.72,
        knowledge_asymmetry=0.5,
        repair_potential=0.33,
    )


def test_relationship_arc_engine_detects_rivals_to_allies_stage():
    engine = RelationshipArcEngine()

    report = engine.build_arc_record(
        relationship_state=rivalry_rel(),
        delta_history=[
            {"relationship_event_label": "social_duel", "reason": "competition with visible skill"},
            {"relationship_event_label": "forced_teamwork", "reason": "shared danger"},
        ],
        user_intent={"genre": "rivals to allies"},
    )

    assert report["success"] is True
    assert report["arc_family"] == "rivals_to_allies"
    assert report["current_stage"] in {"hidden_respect", "forced_cooperation", "earned_trust"}
    assert report["arc_progress"] > 0
    assert report["next_recommended_beats"]
    assert report["chunk5_handoff"]["recommended_plot_beats"]


def test_relationship_arc_engine_detects_status_blocked_romance():
    engine = RelationshipArcEngine()

    report = engine.build_arc_record(
        relationship_state=romance_rel(),
        story_dna={"core_question": "Can truth survive public worth?"},
        user_intent={"genre": "dark academy romance"},
    )

    assert report["arc_family"] == "status_blocked_romance"
    assert report["current_stage"] in {"public_constraint", "private_vulnerability", "status_risk"}
    assert report["stakes"]["romantic_stakes"] is True
    assert "secret_pressure" in report["chunk5_handoff"]["scene_pressure_tags"]
    assert report["chunk5_handoff"]["dialogue_pressure"]["subtext_required"] is True


def test_relationship_arc_engine_detects_betrayal_rupture_repair():
    engine = RelationshipArcEngine()

    report = engine.build_arc_record(
        relationship_state=betrayal_rel(),
        delta_history=[
            {"relationship_event_label": "betrayal", "reason": "blackmail pressure"},
            {"relationship_event_label": "promise_broken", "reason": "protective lie exposed"},
        ],
    )

    assert report["arc_family"] == "betrayal_rupture_repair"
    assert report["rupture_status"]["rupture_active"] is True
    assert report["rupture_status"]["needs_accountability"] is True
    assert "betrayal_or_secret_leverage" in report["rupture_status"]["likely_causes"]
    assert report["repair_status"]["repair_requires_cost"] is True


def test_relationship_arc_engine_update_from_delta_changes_stage():
    engine = RelationshipArcEngine()
    rel = rivalry_rel()

    delta = RelationshipDelta(
        simulation_id="sim_001",
        source_engine="simulation.relationship_graph_engine",
        operation=DeltaOperation.INCREMENT,
        target_entity_id=rel.relationship_id,
        target_path=f"relationship_states.{rel.relationship_id}",
        relationship_id=rel.relationship_id,
        character_a_id=rel.character_a_id,
        character_b_id=rel.character_b_id,
        trust_delta=0.35,
        rivalry_delta=-0.35,
        respect_delta=0.12,
        repair_potential_delta=0.1,
        relationship_event_label="rescue",
        reason="shared danger forces cooperation and earned trust",
    )

    report = engine.update_arc_from_delta(relationship_state=rel, delta=delta)

    assert report["success"] is True
    assert report["updated_relationship_state"]["trust"] > rel.trust
    assert report["updated_relationship_state"]["rivalry"] < rel.rivalry
    assert report["updated_arc"]["arc_family"] == "rivals_to_allies"


def test_relationship_arc_map_builds_records_for_state():
    engine = RelationshipArcEngine()

    state = SimulationState(
        simulation_id="sim_arc_001",
        world_state=SimulationWorldState(world_id="world_velmora"),
        relationship_states={
            "rel_1": rivalry_rel(),
            "rel_2": betrayal_rel(),
        },
    )

    report = engine.build_arc_map(
        state=state,
        delta_history_by_relationship={
            "rel_2": [{"relationship_event_label": "betrayal", "reason": "blackmail"}],
        },
        user_intent={"target_format": "series"},
    )

    assert report["success"] is True
    assert report["relationship_count"] == 2
    assert len(report["arc_records"]) == 2
    assert report["summary"]["arc_family_counts"]
    assert report["simulation_ready"] is True


def test_relationship_arc_quality_flags_detect_flat_edge():
    engine = RelationshipArcEngine()

    rel = SimulationRelationshipState(
        relationship_id="rel_flat",
        character_a_id="char_a",
        character_b_id="char_b",
        relationship_type="emergent_story_bond:undefined",
        trust=0.0,
        respect=0.0,
        rivalry=0.0,
        romantic_tension=0.0,
        repair_potential=0.0,
    )

    report = engine.build_arc_record(relationship_state=rel)

    assert "relationship_edge_too_flat" in report["quality_flags"]


def test_relationship_arc_handoff_contains_scene_and_dialogue_pressure():
    engine = RelationshipArcEngine()

    report = engine.build_arc_record(relationship_state=romance_rel())

    handoff = report["chunk5_handoff"]

    assert handoff["relationship_id"] == "rel_char_kael_char_seren"
    assert "romantic_tension" in handoff["scene_pressure_tags"]
    assert handoff["dialogue_pressure"]["subtext_required"] is True
    assert handoff["dialogue_pressure"]["avoid_easy_confession"] is True

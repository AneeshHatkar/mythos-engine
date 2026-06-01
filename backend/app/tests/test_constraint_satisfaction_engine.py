from backend.app.engines.story_generation.constraint_satisfaction_engine import ConstraintSatisfactionEngine
from backend.app.schemas.story_generation import (
    CausalContinuityReport,
    ConsequencePayoffPlan,
    DialogueBeat,
    GenerationContract,
    HandoffReference,
    KnowledgeBoundaryReport,
    RelationshipBeat,
    SceneBeat,
    SceneBlueprint,
    StoryFormat,
)


def build_contract():
    return GenerationContract(
        generation_contract_id="contract_constraints",
        story_intent_id="intent_constraints",
        handoff_reference=HandoffReference(simulation_id="sim_001"),
        allowed_formats=[StoryFormat.scene],
        selected_format=StoryFormat.scene,
        required_character_ids=["char_kael", "char_seren"],
        allowed_character_ids=["char_kael", "char_seren"],
        required_secret_ids=["secret_rank_system"],
        forbidden_secret_reveals=["major_mystery_solution_until_planned_reveal"],
        required_causal_node_ids=["cause_trial_reveal"],
        required_consequence_ids=["cons_reputation_shift"],
        required_relationship_ids=["rel_kael_seren"],
        tone_contract={"tone_tags": ["tense"], "genres": ["dark_academy"]},
        format_contract={"selected_format": "scene", "requires_ending_hook": True},
        quality_thresholds={"overall_score": 0.7},
        originality_rules={"forbidden_elements": ["cheesy"], "no_raw_source_text": True},
        validation_required=True,
        provenance_required=True,
    )


def build_blueprint():
    return SceneBlueprint(
        blueprint_id="blueprint_constraints",
        scene_id="scene_constraints",
        scene_purpose="Force public pressure around the badge evidence.",
        pov_character_id="char_kael",
        active_character_ids=["char_kael", "char_seren"],
        location_id="location_court",
        scene_objective="Kael must confront the court with proof.",
        stakes=["Consequence cons_reputation_shift must be paid off."],
        secret_pressure=["char_kael lacks required secret knowledge: secret_seren_source."],
        relationship_pressure=["rel_kael_seren pressure"],
        emotional_turn="Seren's guilt must leak.",
        tension_curve=[0.3, 0.5, 0.8, 0.9],
        ending_hook="The pressure becomes harder to hide.",
        required_world_details=["Oath Court", "public proof changes legal rank"],
    )


def build_scene_beats():
    return [
        SceneBeat(
            beat_id="beat_setup",
            scene_id="scene_constraints",
            beat_index=1,
            beat_type="setup",
            purpose="Set public pressure.",
            character_ids=["char_kael", "char_seren"],
            emotional_state={"char_seren:guilt": 0.8},
            causal_links=["cause_trial_reveal"],
            tension_value=0.3,
        ),
        SceneBeat(
            beat_id="beat_consequence",
            scene_id="scene_constraints",
            beat_index=2,
            beat_type="consequence",
            purpose="Show consequence cons_reputation_shift.",
            character_ids=["char_kael", "char_seren"],
            causal_links=["cause_trial_reveal", "cons_reputation_shift"],
            tension_value=0.9,
        ),
        SceneBeat(
            beat_id="beat_ending",
            scene_id="scene_constraints",
            beat_index=3,
            beat_type="ending_hook",
            purpose="End with pressure unresolved.",
            character_ids=["char_kael", "char_seren"],
            causal_links=["cause_trial_reveal"],
            tension_value=0.9,
        ),
    ]


def build_dialogue_beats():
    return [
        DialogueBeat(
            dialogue_beat_id="dialogue_constraints",
            scene_id="scene_constraints",
            speaker_id="char_seren",
            listener_ids=["char_kael"],
            surface_meaning="Seren avoids the direct answer.",
            hidden_meaning="She protects her source.",
            subtext="guilt under control",
            emotion="guilt",
            secret_risk=0.5,
            relationship_effect="trust shifts",
        )
    ]


def build_relationship_beats():
    return [
        RelationshipBeat(
            relationship_id="rel_kael_seren",
            character_a_id="char_kael",
            character_b_id="char_seren",
            starting_trust=0.3,
            starting_resentment=0.5,
            betrayal_risk=0.7,
            turning_point="Evidence changes trust.",
            expected_end_state_shift={"trust_delta": -0.05, "resentment_delta": 0.08},
        )
    ]


def build_reports():
    knowledge = KnowledgeBoundaryReport(
        report_id="knowledge_report",
        valid=True,
        checked_secret_ids=["secret_rank_system"],
        checked_evidence_ids=["evidence_cracked_badge"],
        impossible_knowledge_violations=[],
        warnings=[],
    )
    causal = CausalContinuityReport(
        report_id="causal_report",
        valid=True,
        checked_causal_node_ids=["cause_trial_reveal"],
        missing_causes=[],
        missing_consequences=[],
        orphan_events=[],
        warnings=[],
    )
    payoff = ConsequencePayoffPlan(
        payoff_plan_id="payoff_plan",
        source_consequence_ids=["cons_reputation_shift"],
        payoff_obligations=["Acknowledge consequence cons_reputation_shift."],
        required_scene_beats=[],
        delayed_payoff_candidates=[],
    )
    return knowledge, causal, payoff


def test_constraint_engine_satisfies_valid_plan():
    engine = ConstraintSatisfactionEngine()
    knowledge, causal, payoff = build_reports()

    result = engine.evaluate_constraints(
        contract=build_contract(),
        blueprint=build_blueprint(),
        scene_beats=build_scene_beats(),
        dialogue_beats=build_dialogue_beats(),
        relationship_beats=build_relationship_beats(),
        knowledge_report=knowledge,
        causal_report=causal,
        payoff_plan=payoff,
        story_context={"emotional_pressure": [{"character_id": "char_seren", "dominant_emotion": "guilt"}]},
        world_detail_pack={"law_and_rule_anchors": [{"detail": "public proof changes legal rank"}]},
    )

    report = result["constraint_report"]

    assert result["success"] is True
    assert report.satisfied is True
    assert report.required_characters_present is True
    assert report.forbidden_elements_avoided is True
    assert report.requested_format_followed is True
    assert report.knowledge_rules_obeyed is True
    assert result["extra_checks"]["causal_rules_obeyed"] is True
    assert result["extra_checks"]["consequence_payoff_included"] is True


def test_constraint_engine_blocks_missing_required_character():
    engine = ConstraintSatisfactionEngine()
    knowledge, causal, payoff = build_reports()
    blueprint = build_blueprint()
    blueprint.active_character_ids = ["char_kael"]

    result = engine.evaluate_constraints(
        contract=build_contract(),
        blueprint=blueprint,
        scene_beats=build_scene_beats(),
        dialogue_beats=build_dialogue_beats(),
        relationship_beats=build_relationship_beats(),
        knowledge_report=knowledge,
        causal_report=causal,
        payoff_plan=payoff,
    )

    report = result["constraint_report"]

    assert report.satisfied is False
    assert "required characters missing from blueprint" in report.failed_constraints


def test_constraint_engine_blocks_forbidden_elements():
    engine = ConstraintSatisfactionEngine()
    knowledge, causal, payoff = build_reports()
    blueprint = build_blueprint()
    blueprint.scene_objective = "Kael must make a cheesy speech."

    result = engine.evaluate_constraints(
        contract=build_contract(),
        blueprint=blueprint,
        scene_beats=build_scene_beats(),
        dialogue_beats=build_dialogue_beats(),
        relationship_beats=build_relationship_beats(),
        knowledge_report=knowledge,
        causal_report=causal,
        payoff_plan=payoff,
    )

    report = result["constraint_report"]

    assert report.satisfied is False
    assert "forbidden elements appear in planned scene" in report.failed_constraints


def test_constraint_engine_blocks_invalid_knowledge_and_causality():
    engine = ConstraintSatisfactionEngine()
    knowledge, causal, payoff = build_reports()
    knowledge.valid = False
    causal.valid = False

    result = engine.evaluate_constraints(
        contract=build_contract(),
        blueprint=build_blueprint(),
        scene_beats=build_scene_beats(),
        dialogue_beats=build_dialogue_beats(),
        relationship_beats=build_relationship_beats(),
        knowledge_report=knowledge,
        causal_report=causal,
        payoff_plan=payoff,
    )

    report = result["constraint_report"]

    assert report.satisfied is False
    assert "knowledge boundary report is invalid" in report.failed_constraints
    assert "causal continuity report is invalid" in report.failed_constraints


def test_constraint_engine_builds_repair_plan():
    engine = ConstraintSatisfactionEngine()
    knowledge, causal, payoff = build_reports()
    knowledge.valid = False

    evaluated = engine.evaluate_constraints(
        contract=build_contract(),
        blueprint=build_blueprint(),
        scene_beats=[],
        dialogue_beats=[],
        relationship_beats=[],
        knowledge_report=knowledge,
        causal_report=causal,
        payoff_plan=payoff,
        story_context={},
        world_detail_pack={},
    )

    result = engine.build_constraint_repair_plan(
        report=evaluated["constraint_report"],
        extra_checks=evaluated["extra_checks"],
    )

    assert result["success"] is True
    assert result["ready_for_generation"] is False
    assert result["repair_count"] >= 1
    assert any("safe reveal" in repair.lower() or "knowledge" in repair.lower() for repair in result["repairs"])


def test_constraint_engine_validates_report():
    engine = ConstraintSatisfactionEngine()
    knowledge, causal, payoff = build_reports()

    report = engine.evaluate_constraints(
        contract=build_contract(),
        blueprint=build_blueprint(),
        scene_beats=build_scene_beats(),
        dialogue_beats=build_dialogue_beats(),
        relationship_beats=build_relationship_beats(),
        knowledge_report=knowledge,
        causal_report=causal,
        payoff_plan=payoff,
    )["constraint_report"]

    validation = engine.validate_constraint_report(report=report)

    assert validation["success"] is True
    assert validation["valid"] is True
    assert "constraints_satisfied" in validation["passed_checks"]
    assert "required_characters_present" in validation["passed_checks"]


def test_constraint_engine_summarizes_report():
    engine = ConstraintSatisfactionEngine()
    knowledge, causal, payoff = build_reports()

    evaluated = engine.evaluate_constraints(
        contract=build_contract(),
        blueprint=build_blueprint(),
        scene_beats=build_scene_beats(),
        dialogue_beats=build_dialogue_beats(),
        relationship_beats=build_relationship_beats(),
        knowledge_report=knowledge,
        causal_report=causal,
        payoff_plan=payoff,
    )

    summary = engine.summarize_constraint_report(
        report=evaluated["constraint_report"],
        extra_checks=evaluated["extra_checks"],
    )

    assert summary["success"] is True
    assert summary["summary"]["satisfied"] is True
    assert summary["summary"]["failed_constraint_count"] == 0
    assert summary["summary"]["causal_rules_obeyed"] is True

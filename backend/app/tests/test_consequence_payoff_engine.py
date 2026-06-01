from backend.app.engines.story_generation.consequence_payoff_engine import ConsequencePayoffEngine
from backend.app.schemas.story_generation import (
    CausalContinuityReport,
    RelationshipBeat,
    SceneBeat,
    SceneBlueprint,
)


def build_blueprint():
    return SceneBlueprint(
        blueprint_id="blueprint_payoff",
        scene_id="scene_payoff",
        scene_purpose="Pay off evidence reveal consequence.",
        pov_character_id="char_kael",
        active_character_ids=["char_kael", "char_seren"],
        scene_objective="Kael exposes the badge and the court must respond.",
        stakes=[
            "Consequence cons_reputation_shift must be acknowledged or paid off.",
        ],
        relationship_pressure=["rel_kael_seren pressure"],
        ending_hook="Seren's silence delays the full cost.",
    )


def build_scene_beats():
    return [
        SceneBeat(
            beat_id="beat_setup",
            scene_id="scene_payoff",
            beat_index=1,
            beat_type="setup",
            purpose="Set up cause_trial_reveal.",
            character_ids=["char_kael"],
            causal_links=["cause_trial_reveal"],
            tension_value=0.3,
        ),
        SceneBeat(
            beat_id="beat_consequence",
            scene_id="scene_payoff",
            beat_index=2,
            beat_type="consequence",
            purpose="Show or trigger consequence cons_reputation_shift.",
            character_ids=["char_kael", "char_seren"],
            causal_links=["cause_trial_reveal", "cons_reputation_shift"],
            tension_value=0.9,
        ),
    ]


def build_relationship_beats():
    return [
        RelationshipBeat(
            relationship_id="rel_kael_seren",
            character_a_id="char_kael",
            character_b_id="char_seren",
            starting_trust=0.3,
            starting_resentment=0.5,
            romantic_tension=0.4,
            betrayal_risk=0.7,
            knowledge_asymmetry=["char_kael does not know secret_seren_source"],
            turning_point="Evidence changes the emotional balance.",
            expected_end_state_shift={"trust_delta": -0.05, "resentment_delta": 0.08},
        )
    ]


def build_story_context():
    return {
        "causal_context": {
            "required_consequence_ids": ["cons_reputation_shift"],
            "handoff_consequence_ids": ["cons_reputation_shift"],
        },
        "causal_obligations": [
            {"obligation_type": "consequence", "id": "cons_reputation_shift", "required": True},
        ],
        "knowledge_boundaries": [
            {
                "holder_id": "char_kael",
                "missing_required_secret_ids": ["secret_seren_source"],
            }
        ],
    }


def build_causal_report(valid=True):
    return CausalContinuityReport(
        report_id="causal_report_scene_payoff",
        valid=valid,
        checked_causal_node_ids=["cause_trial_reveal"],
        missing_causes=[],
        missing_consequences=[] if valid else ["cons_missing"],
        orphan_events=[],
        warnings=[],
    )


def test_consequence_payoff_engine_builds_payoff_plan():
    engine = ConsequencePayoffEngine()

    result = engine.build_payoff_plan(
        blueprint=build_blueprint(),
        scene_beats=build_scene_beats(),
        relationship_beats=build_relationship_beats(),
        causal_report=build_causal_report(),
        story_context=build_story_context(),
    )

    plan = result["consequence_payoff_plan"]

    assert result["success"] is True
    assert plan.payoff_plan_id == "payoff_plan_scene_payoff"
    assert "cons_reputation_shift" in plan.source_consequence_ids
    assert plan.payoff_obligations
    assert any("rel_kael_seren" in item for item in plan.payoff_obligations)


def test_consequence_payoff_engine_tracks_required_scene_beats():
    engine = ConsequencePayoffEngine()

    plan = engine.build_payoff_plan(
        blueprint=build_blueprint(),
        scene_beats=[],
        relationship_beats=build_relationship_beats(),
        story_context=build_story_context(),
    )["consequence_payoff_plan"]

    assert "add consequence beat" in plan.required_scene_beats
    assert any("cons_reputation_shift" in item for item in plan.required_scene_beats)


def test_consequence_payoff_engine_tracks_delayed_payoffs():
    engine = ConsequencePayoffEngine()

    plan = engine.build_payoff_plan(
        blueprint=build_blueprint(),
        scene_beats=build_scene_beats(),
        relationship_beats=build_relationship_beats(),
        causal_report=build_causal_report(valid=False),
        story_context=build_story_context(),
    )["consequence_payoff_plan"]

    assert "cons_missing" in plan.delayed_payoff_candidates


def test_consequence_payoff_engine_validates_payoff_plan():
    engine = ConsequencePayoffEngine()

    plan = engine.build_payoff_plan(
        blueprint=build_blueprint(),
        scene_beats=build_scene_beats(),
        relationship_beats=build_relationship_beats(),
        causal_report=build_causal_report(),
        story_context=build_story_context(),
    )["consequence_payoff_plan"]

    validation = engine.validate_payoff_plan(plan=plan)

    assert validation["success"] is True
    assert validation["valid"] is True
    assert "payoff_plan_id_present" in validation["passed_checks"]
    assert "source_consequences_present" in validation["passed_checks"]
    assert "payoff_obligations_present" in validation["passed_checks"]


def test_consequence_payoff_engine_builds_open_loop_registry_update():
    engine = ConsequencePayoffEngine()

    plan = engine.build_payoff_plan(
        blueprint=build_blueprint(),
        scene_beats=build_scene_beats(),
        relationship_beats=build_relationship_beats(),
        causal_report=build_causal_report(valid=False),
        story_context=build_story_context(),
    )["consequence_payoff_plan"]

    result = engine.build_open_loop_registry_update(plan=plan)

    assert result["success"] is True
    assert result["open_loop_count"] >= 1
    assert any(item["source_consequence_id"] == "cons_missing" for item in result["open_loop_registry"])


def test_consequence_payoff_engine_summarizes_plan():
    engine = ConsequencePayoffEngine()

    plan = engine.build_payoff_plan(
        blueprint=build_blueprint(),
        scene_beats=build_scene_beats(),
        relationship_beats=build_relationship_beats(),
        causal_report=build_causal_report(),
        story_context=build_story_context(),
    )["consequence_payoff_plan"]

    summary = engine.summarize_payoff_plan(plan=plan)

    assert summary["success"] is True
    assert summary["summary"]["source_consequence_count"] >= 1
    assert summary["summary"]["payoff_obligation_count"] >= 1


def test_consequence_payoff_engine_warns_without_consequences():
    engine = ConsequencePayoffEngine()

    empty_blueprint = SceneBlueprint(
        blueprint_id="blueprint_empty",
        scene_id="scene_empty",
        scene_purpose="No payoff.",
        active_character_ids=["char_a"],
        scene_objective="Move forward.",
    )

    result = engine.build_payoff_plan(
        blueprint=empty_blueprint,
        scene_beats=[],
        relationship_beats=[],
        story_context={},
    )

    assert any("No source consequences" in warning for warning in result["warnings"])

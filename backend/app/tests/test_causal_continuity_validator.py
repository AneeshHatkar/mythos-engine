from backend.app.engines.story_generation.causal_continuity_validator import CausalContinuityValidator
from backend.app.schemas.story_generation import (
    DialogueBeat,
    KnowledgeBoundaryReport,
    RelationshipBeat,
    SceneBeat,
    SceneBlueprint,
)


def build_blueprint():
    return SceneBlueprint(
        blueprint_id="blueprint_causal",
        scene_id="scene_causal",
        scene_purpose="Reveal evidence and force a consequence.",
        pov_character_id="char_kael",
        active_character_ids=["char_kael", "char_seren"],
        scene_objective="Kael exposes the cracked badge.",
        stakes=[
            "Causal thread cause_trial_reveal must remain coherent.",
            "Consequence cons_reputation_shift must be acknowledged or paid off.",
        ],
        secret_pressure=["char_kael lacks required secret knowledge: secret_seren_source."],
        relationship_pressure=["rel_kael_seren pressure"],
        tension_curve=[0.3, 0.5, 0.8, 0.9],
        ending_hook="End by making cause_trial_reveal impossible to ignore.",
    )


def build_scene_beats():
    return [
        SceneBeat(
            beat_id="beat_setup",
            scene_id="scene_causal",
            beat_index=1,
            beat_type="setup",
            purpose="Set up cause_trial_reveal.",
            character_ids=["char_kael", "char_seren"],
            causal_links=["cause_trial_reveal"],
            tension_value=0.3,
        ),
        SceneBeat(
            beat_id="beat_choice",
            scene_id="scene_causal",
            beat_index=2,
            beat_type="choice",
            purpose="Kael chooses to expose the cracked badge.",
            character_ids=["char_kael"],
            causal_links=["cause_trial_reveal"],
            tension_value=0.8,
        ),
        SceneBeat(
            beat_id="beat_consequence",
            scene_id="scene_causal",
            beat_index=3,
            beat_type="consequence",
            purpose="Show or trigger consequence cons_reputation_shift.",
            character_ids=["char_kael", "char_seren"],
            causal_links=["cause_trial_reveal", "cons_reputation_shift"],
            tension_value=0.9,
        ),
        SceneBeat(
            beat_id="beat_ending",
            scene_id="scene_causal",
            beat_index=4,
            beat_type="ending_hook",
            purpose="End by making cause_trial_reveal impossible to ignore.",
            character_ids=["char_kael", "char_seren"],
            causal_links=["cause_trial_reveal"],
            tension_value=0.9,
        ),
    ]


def build_dialogue_beats():
    return [
        DialogueBeat(
            dialogue_beat_id="dialogue_causal",
            scene_id="scene_causal",
            speaker_id="char_kael",
            listener_ids=["char_seren"],
            surface_meaning="Kael exposes the badge.",
            hidden_meaning="He forces the court to respond.",
            subtext="truth becomes public pressure",
            secret_risk=0.3,
            relationship_effect="trust changes after evidence",
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
            knowledge_asymmetry=["char_kael does not know secret_seren_source"],
            turning_point="Evidence changes the emotional balance.",
            expected_end_state_shift={"trust_delta": -0.05, "resentment_delta": 0.08},
        )
    ]


def build_story_context():
    return {
        "causal_context": {
            "required_causal_node_ids": ["cause_trial_reveal"],
            "required_consequence_ids": ["cons_reputation_shift"],
            "handoff_causal_node_ids": ["cause_trial_reveal"],
            "handoff_consequence_ids": ["cons_reputation_shift"],
            "causal_chains": {"cause_trial_reveal": {"effect": "cons_reputation_shift"}},
        },
        "causal_obligations": [
            {"obligation_type": "causal_node", "id": "cause_trial_reveal", "required": True},
            {"obligation_type": "consequence", "id": "cons_reputation_shift", "required": True},
        ],
    }


def build_knowledge_report(valid=True):
    return KnowledgeBoundaryReport(
        report_id="knowledge_report_scene_causal",
        valid=valid,
        checked_secret_ids=["secret_seren_source"],
        checked_evidence_ids=["evidence_cracked_badge"],
        impossible_knowledge_violations=[] if valid else ["char_kael knows impossible secret"],
        warnings=[],
    )


def test_causal_continuity_validator_passes_valid_scene_plan():
    validator = CausalContinuityValidator()

    result = validator.validate_causal_continuity(
        blueprint=build_blueprint(),
        scene_beats=build_scene_beats(),
        dialogue_beats=build_dialogue_beats(),
        relationship_beats=build_relationship_beats(),
        knowledge_report=build_knowledge_report(),
        story_context=build_story_context(),
    )

    report = result["causal_continuity_report"]

    assert result["success"] is True
    assert report.valid is True
    assert "cause_trial_reveal" in report.checked_causal_node_ids
    assert report.missing_causes == []
    assert report.missing_consequences == []
    assert report.orphan_events == []


def test_causal_continuity_validator_detects_missing_cause():
    validator = CausalContinuityValidator()

    story_context = build_story_context()
    story_context["causal_context"]["required_causal_node_ids"] = ["cause_trial_reveal", "cause_missing_setup"]

    result = validator.validate_causal_continuity(
        blueprint=build_blueprint(),
        scene_beats=build_scene_beats(),
        dialogue_beats=build_dialogue_beats(),
        relationship_beats=build_relationship_beats(),
        knowledge_report=build_knowledge_report(),
        story_context=story_context,
    )

    report = result["causal_continuity_report"]

    assert report.valid is False
    assert "cause_missing_setup" in report.missing_causes


def test_causal_continuity_validator_detects_orphan_choice_without_causal_context():
    validator = CausalContinuityValidator()

    orphan_beats = [
        SceneBeat(
            beat_id="beat_orphan_choice",
            scene_id="scene_causal",
            beat_index=1,
            beat_type="choice",
            purpose="Kael makes an unsupported major choice.",
            character_ids=["char_kael"],
            causal_links=[],
            tension_value=0.7,
        )
    ]

    result = validator.validate_causal_continuity(
        blueprint=build_blueprint(),
        scene_beats=orphan_beats,
        dialogue_beats=[],
        relationship_beats=[],
        story_context={},
    )

    report = result["causal_continuity_report"]

    assert report.valid is False
    assert "beat_orphan_choice" in report.orphan_events


def test_causal_continuity_validator_builds_repair_plan():
    validator = CausalContinuityValidator()

    story_context = build_story_context()
    story_context["causal_context"]["required_causal_node_ids"] = ["cause_missing_setup"]

    report = validator.validate_causal_continuity(
        blueprint=build_blueprint(),
        scene_beats=build_scene_beats(),
        dialogue_beats=build_dialogue_beats(),
        relationship_beats=build_relationship_beats(),
        story_context=story_context,
    )["causal_continuity_report"]

    plan = validator.build_causal_repair_plan(report=report)

    assert plan["success"] is True
    assert plan["ready_for_generation"] is False
    assert plan["repair_priority"] == "high"
    assert any("cause_missing_setup" in item for item in plan["required_fixes"])


def test_causal_continuity_validator_validates_report():
    validator = CausalContinuityValidator()

    report = validator.validate_causal_continuity(
        blueprint=build_blueprint(),
        scene_beats=build_scene_beats(),
        dialogue_beats=build_dialogue_beats(),
        relationship_beats=build_relationship_beats(),
        knowledge_report=build_knowledge_report(),
        story_context=build_story_context(),
    )["causal_continuity_report"]

    validation = validator.validate_report(report=report)

    assert validation["success"] is True
    assert validation["valid"] is True
    assert "causal_continuity_valid" in validation["passed_checks"]
    assert "causal_nodes_checked" in validation["passed_checks"]


def test_causal_continuity_validator_summarizes_report():
    validator = CausalContinuityValidator()

    report = validator.validate_causal_continuity(
        blueprint=build_blueprint(),
        scene_beats=build_scene_beats(),
        dialogue_beats=build_dialogue_beats(),
        relationship_beats=build_relationship_beats(),
        knowledge_report=build_knowledge_report(),
        story_context=build_story_context(),
    )["causal_continuity_report"]

    summary = validator.summarize_report(report=report)

    assert summary["success"] is True
    assert summary["summary"]["valid"] is True
    assert summary["summary"]["checked_causal_node_count"] >= 1
    assert summary["summary"]["missing_cause_count"] == 0


def test_causal_continuity_validator_warns_when_knowledge_invalid():
    validator = CausalContinuityValidator()

    result = validator.validate_causal_continuity(
        blueprint=build_blueprint(),
        scene_beats=build_scene_beats(),
        dialogue_beats=build_dialogue_beats(),
        relationship_beats=build_relationship_beats(),
        knowledge_report=build_knowledge_report(valid=False),
        story_context=build_story_context(),
    )

    report = result["causal_continuity_report"]

    assert any("Knowledge boundary report is invalid" in warning for warning in report.warnings)

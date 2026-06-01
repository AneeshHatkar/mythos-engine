from backend.app.engines.story_generation.scene_quality_gate import SceneQualityGate
from backend.app.schemas.story_generation import AssembledScene, CommercialAppealReport


def build_assembled_scene():
    text = """
# Scene at location_court

In location_court, Oath Court presses against char_kael and char_seren. The cracked badge is not just an object; it is public proof changes legal rank made visible in the room. The secret_seren_source remains hidden, and char_kael does not know why Seren refuses to name it.

char_seren: "Do not mistake silence for surrender," char_seren says.

The relationship layer matters because rel_kael_seren has trust shifting under pressure. The silence does not soften the betrayal risk; it sharpens it. cause_trial_reveal remains tied to the choice, and cons_reputation_shift waits in the court's reaction.

Seren refuses to deny the badge.
""".strip()

    return AssembledScene(
        assembled_scene_id="assembled_scene_quality",
        scene_id="scene_quality",
        draft_id="draft_scene_quality",
        dialogue_block_id="dialogue_block_scene_quality",
        selected_format="scene",
        title="Scene at location_court",
        assembled_text=text,
        sections=[
            {"section_id": "section_setup", "beat_type": "setup", "text": "Oath Court setup"},
            {"section_id": "section_dialogue", "beat_type": "dialogue_block", "text": "char_seren speaks"},
            {"section_id": "section_ending", "beat_type": "ending_hook", "text": "Seren refuses to deny the badge."},
        ],
        continuity_trace={
            "blueprint_id": "blueprint_quality",
            "scene_beat_ids": ["beat_setup", "beat_choice", "beat_consequence"],
            "dialogue_line_ids": ["line_001"],
            "ending_hook": "Seren refuses to deny the badge.",
            "scene_objective": "Kael must expose the cracked badge.",
        },
        used_character_ids=["char_kael", "char_seren"],
        used_relationship_ids=["rel_kael_seren"],
        used_secret_ids=["secret_seren_source"],
        used_causal_ids=["cause_trial_reveal", "cons_reputation_shift"],
        used_world_details=["Oath Court", "cracked badge", "public proof changes legal rank"],
        generation_notes=[],
        warnings=[],
    )


def build_commercial_report():
    return CommercialAppealReport(
        report_id="commercial_report_scene_quality",
        overall_score=0.82,
        hook_strength=0.8,
        emotional_investment=0.8,
        character_appeal=0.8,
        relationship_appeal=0.8,
        stakes_clarity=0.8,
        world_uniqueness=0.9,
        scene_momentum=0.8,
        continuation_pull=0.8,
        adaptation_potential=0.7,
        improvement_suggestions=[],
    )


def test_scene_quality_gate_evaluates_scene():
    gate = SceneQualityGate()

    result = gate.evaluate_scene_quality(
        assembled_scene=build_assembled_scene(),
        commercial_report=build_commercial_report(),
        prose_style_profile={"generic_phrase_bans": ["cheesy"]},
        min_word_count=80,
    )

    report = result["scene_quality_report"]

    assert result["success"] is True
    assert report.report_id == "scene_quality_scene_quality"
    assert report.scene_id == "scene_quality"
    assert report.overall_score >= 0.65
    assert report.passed is True


def test_scene_quality_gate_scores_core_dimensions():
    gate = SceneQualityGate()

    report = gate.evaluate_scene_quality(
        assembled_scene=build_assembled_scene(),
        commercial_report=build_commercial_report(),
        min_word_count=80,
    )["scene_quality_report"]

    assert report.world_specificity_score >= 0.65
    assert report.character_presence_score >= 0.65
    assert report.relationship_pressure_score >= 0.65
    assert report.secret_pressure_score >= 0.65
    assert report.causal_trace_score >= 0.65
    assert report.dialogue_presence_score >= 0.65


def test_scene_quality_gate_detects_generic_phrase_risk():
    gate = SceneQualityGate()
    scene = build_assembled_scene()
    scene.assembled_text += "\nIn that moment, everything changed."

    report = gate.evaluate_scene_quality(
        assembled_scene=scene,
        commercial_report=build_commercial_report(),
        min_word_count=80,
    )["scene_quality_report"]

    assert report.generic_phrase_risk > 0.0
    assert any("generic phrase risk" in warning.lower() for warning in report.warnings)


def test_scene_quality_gate_builds_repair_plan_for_weak_scene():
    gate = SceneQualityGate()

    weak = AssembledScene(
        assembled_scene_id="assembled_weak",
        scene_id="scene_weak",
        assembled_text="Short scene.",
        sections=[],
        continuity_trace={},
        used_character_ids=[],
        used_world_details=[],
        used_causal_ids=[],
    )

    report = gate.evaluate_scene_quality(
        assembled_scene=weak,
        commercial_report=None,
        min_word_count=100,
    )["scene_quality_report"]

    plan = gate.build_quality_repair_plan(report=report)

    assert plan["success"] is True
    assert plan["ready_for_chapter_handoff"] is False
    assert plan["repair_count"] >= 1
    assert any("Expand scene" in repair or "causal" in repair for repair in plan["repairs"])


def test_scene_quality_gate_validates_report():
    gate = SceneQualityGate()

    report = gate.evaluate_scene_quality(
        assembled_scene=build_assembled_scene(),
        commercial_report=build_commercial_report(),
        min_word_count=80,
    )["scene_quality_report"]

    validation = gate.validate_quality_report(report=report)

    assert validation["success"] is True
    assert validation["valid"] is True
    assert "report_id_present" in validation["passed_checks"]
    assert "scores_bounded" in validation["passed_checks"]
    assert "quality_gate_passed" in validation["passed_checks"]


def test_scene_quality_gate_summarizes_report():
    gate = SceneQualityGate()

    report = gate.evaluate_scene_quality(
        assembled_scene=build_assembled_scene(),
        commercial_report=build_commercial_report(),
        min_word_count=80,
    )["scene_quality_report"]

    summary = gate.summarize_quality_report(report=report)

    assert summary["success"] is True
    assert summary["summary"]["scene_id"] == "scene_quality"
    assert summary["summary"]["overall_score"] >= 0.65
    assert "weakest_dimension" in summary["summary"]


def test_scene_quality_gate_blocks_very_weak_scene():
    gate = SceneQualityGate()

    weak = AssembledScene(
        assembled_scene_id="assembled_weak",
        scene_id="scene_weak",
        assembled_text="Short scene.",
        sections=[],
        continuity_trace={},
        used_character_ids=[],
        used_world_details=[],
        used_causal_ids=[],
    )

    report = gate.evaluate_scene_quality(
        assembled_scene=weak,
        commercial_report=None,
        min_word_count=100,
    )["scene_quality_report"]

    assert report.passed is False
    assert report.blockers
    assert "assembled scene is too short" in report.blockers

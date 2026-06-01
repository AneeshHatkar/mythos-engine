from backend.app.engines.story_generation.multi_scene_pacing_engine import MultiScenePacingEngine
from backend.app.schemas.story_generation import (
    AssembledScene,
    ChapterExpansionPlan,
    GeneratedChapter,
    SeriesEpisodeStructure,
)


def build_scene(scene_id, index, text, tension_ids=None):
    return AssembledScene(
        assembled_scene_id=f"assembled_{scene_id}",
        scene_id=scene_id,
        draft_id=f"draft_{scene_id}",
        dialogue_block_id=f"dialogue_block_{scene_id}" if ":" in text or '"' in text else None,
        selected_format="scene",
        title=f"Scene {index}",
        assembled_text=text,
        sections=[{"section_id": f"section_{scene_id}", "beat_type": "assembled", "text": text}],
        continuity_trace={
            "scene_beat_ids": [f"beat_{scene_id}"],
            "ending_hook": "The next pressure remains." if index == 3 else None,
            "scene_objective": "Move the court conflict forward.",
        },
        used_character_ids=["char_kael", "char_seren"],
        used_relationship_ids=["rel_kael_seren"] if index >= 2 else [],
        used_secret_ids=["secret_seren_source"] if index >= 2 else [],
        used_causal_ids=tension_ids or ["cause_trial_reveal"],
        used_world_details=["Oath Court", "cracked badge"],
    )


def build_scenes():
    return [
        build_scene(
            "scene_pace_1",
            1,
            "Kael enters the quiet Oath Court and studies the cracked badge. The world rule is visible.",
            ["cause_trial_reveal"],
        ),
        build_scene(
            "scene_pace_2",
            2,
            'Seren says: "Do not ask what I cannot name." The secret remains hidden, and trust becomes harder.',
            ["cause_trial_reveal"],
        ),
        build_scene(
            "scene_pace_3",
            3,
            "The reveal becomes a consequence. cons_reputation_shift hits the court, betrayal risk rises, and Seren refuses to deny the badge.",
            ["cause_trial_reveal", "cons_reputation_shift"],
        ),
    ]


def build_chapter():
    return GeneratedChapter(
        chapter_id="chapter_pacing",
        chapter_number=1,
        title="The Court Pressure",
        chapter_text="\n\n".join(scene.assembled_text for scene in build_scenes()),
        scene_ids=["scene_pace_1", "scene_pace_2", "scene_pace_3"],
        assembled_scene_ids=["assembled_scene_pace_1", "assembled_scene_pace_2", "assembled_scene_pace_3"],
        sections=[
            {
                "scene_id": scene.scene_id,
                "text": scene.assembled_text,
                "used_character_ids": scene.used_character_ids,
                "used_secret_ids": scene.used_secret_ids,
                "used_causal_ids": scene.used_causal_ids,
                "used_world_details": scene.used_world_details,
            }
            for scene in build_scenes()
        ],
        used_character_ids=["char_kael", "char_seren"],
        used_relationship_ids=["rel_kael_seren"],
        used_secret_ids=["secret_seren_source"],
        used_causal_ids=["cause_trial_reveal", "cons_reputation_shift"],
        used_world_details=["Oath Court", "cracked badge"],
        open_loops=[{"loop_id": "open_loop_secret", "description": "Secret remains hidden."}],
        next_chapter_hooks=["Seren refuses to deny the badge."],
        quality_summary={"failed_scene_count": 0},
    )


def build_expansion_plan():
    return ChapterExpansionPlan(
        expansion_plan_id="chapter_expansion_pacing",
        chapter_id="chapter_pacing",
        source_word_count=100,
        target_word_count=1500,
        expansion_ratio=15.0,
        expansion_targets=[
            {"target_type": "scene_expansion", "target_id": "scene_pace_1"},
            {"target_type": "relationship_expansion", "target_id": "rel_kael_seren"},
        ],
    )


def build_episode_structure():
    return SeriesEpisodeStructure(
        episode_structure_id="episode_structure_pacing",
        source_id="chapter_pacing",
        episode_number=1,
        season_number=1,
        episode_title="The Court Pressure",
        cold_open={"description": "Open on the cracked badge."},
        act_structure=[
            {"act_number": 1, "description": "Setup", "act_break_hook": "Secret remains hidden."},
            {"act_number": 2, "description": "Complication", "act_break_hook": "Trust becomes harder."},
            {"act_number": 3, "description": "Choice", "act_break_hook": "Reputation shifts."},
            {"act_number": 4, "description": "Cliffhanger", "act_break_hook": "Seren refuses to deny the badge."},
        ],
        plot_lanes={"A_plot": [], "B_plot": [], "C_plot": []},
        episode_cliffhanger="Seren refuses to deny the badge.",
    )


def test_multi_scene_pacing_engine_evaluates_pacing():
    engine = MultiScenePacingEngine()

    result = engine.evaluate_pacing(
        source_id="chapter_pacing",
        assembled_scenes=build_scenes(),
        chapter=build_chapter(),
        expansion_plan=build_expansion_plan(),
        episode_structure=build_episode_structure(),
        story_context={"emotional_pressure": [{"dominant_emotion": "guilt"}]},
    )

    report = result["multi_scene_pacing_report"]

    assert result["success"] is True
    assert report.pacing_report_id == "multi_scene_pacing_chapter_pacing"
    assert report.scene_count == 3
    assert report.overall_pacing_score > 0.0
    assert report.scene_pacing_map


def test_multi_scene_pacing_engine_scores_core_dimensions():
    engine = MultiScenePacingEngine()

    report = engine.evaluate_pacing(
        source_id="chapter_pacing",
        assembled_scenes=build_scenes(),
        chapter=build_chapter(),
        story_context={"emotional_pressure": [{"dominant_emotion": "guilt"}]},
    )["multi_scene_pacing_report"]

    assert report.tension_curve_score >= 0.5
    assert report.emotional_variety_score >= 0.35
    assert report.relationship_rhythm_score >= 0.35
    assert report.secret_pressure_spacing_score >= 0.35
    assert report.causal_spacing_score >= 0.35
    assert report.world_detail_spacing_score >= 0.35
    assert report.dialogue_action_balance_score >= 0.35


def test_multi_scene_pacing_engine_uses_episode_act_breaks():
    engine = MultiScenePacingEngine()

    report = engine.evaluate_pacing(
        source_id="chapter_pacing",
        assembled_scenes=build_scenes(),
        chapter=build_chapter(),
        episode_structure=build_episode_structure(),
    )["multi_scene_pacing_report"]

    assert len(report.act_break_recommendations) == 4
    assert report.act_break_recommendations[0]["act_number"] == 1


def test_multi_scene_pacing_engine_builds_repair_plan():
    engine = MultiScenePacingEngine()

    weak_scene = build_scene(
        "scene_weak",
        1,
        "Quiet. Quiet. Quiet.",
        [],
    )
    weak_scene.used_relationship_ids = []
    weak_scene.used_secret_ids = []
    weak_scene.used_causal_ids = []
    weak_scene.used_world_details = []

    report = engine.evaluate_pacing(
        source_id="weak_source",
        assembled_scenes=[weak_scene],
        chapter=None,
    )["multi_scene_pacing_report"]

    plan = engine.build_pacing_repair_plan(report=report)

    assert plan["success"] is True
    assert plan["repairs"]
    assert plan["repair_count"] >= 1


def test_multi_scene_pacing_engine_validates_report():
    engine = MultiScenePacingEngine()

    report = engine.evaluate_pacing(
        source_id="chapter_pacing",
        assembled_scenes=build_scenes(),
        chapter=build_chapter(),
        episode_structure=build_episode_structure(),
    )["multi_scene_pacing_report"]

    validation = engine.validate_pacing_report(report=report)

    assert validation["success"] is True
    assert validation["valid"] is True
    assert "pacing_report_id_present" in validation["passed_checks"]
    assert "scene_units_present" in validation["passed_checks"]
    assert "scores_bounded" in validation["passed_checks"]


def test_multi_scene_pacing_engine_summarizes_report():
    engine = MultiScenePacingEngine()

    report = engine.evaluate_pacing(
        source_id="chapter_pacing",
        assembled_scenes=build_scenes(),
        chapter=build_chapter(),
    )["multi_scene_pacing_report"]

    summary = engine.summarize_pacing_report(report=report)

    assert summary["success"] is True
    assert summary["summary"]["source_id"] == "chapter_pacing"
    assert summary["summary"]["scene_count"] == 3
    assert "weakest_dimension" in summary["summary"]


def test_multi_scene_pacing_engine_can_use_chapter_sections_when_no_assembled_scenes():
    engine = MultiScenePacingEngine()

    report = engine.evaluate_pacing(
        source_id="chapter_pacing",
        assembled_scenes=[],
        chapter=build_chapter(),
    )["multi_scene_pacing_report"]

    assert report.scene_count == 3
    assert report.scene_pacing_map


def test_multi_scene_pacing_engine_warns_when_no_scene_units():
    engine = MultiScenePacingEngine()

    report = engine.evaluate_pacing(
        source_id="empty_source",
        assembled_scenes=[],
        chapter=None,
        episode_structure=None,
    )["multi_scene_pacing_report"]

    assert report.scene_count == 0
    assert any("No scene units" in warning for warning in report.warnings)

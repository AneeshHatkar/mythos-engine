from backend.app.engines.story_generation.chapter_generator import ChapterGenerator
from backend.app.schemas.story_generation import AssembledScene, SceneQualityReport


def build_scene(scene_id="scene_chapter_1"):
    text = """
# Scene at location_court

In the Oath Court, char_kael and char_seren stand beneath public witness tiers. The cracked badge proves that public proof changes legal rank. The secret_seren_source remains hidden, and cause_trial_reveal pushes the court toward cons_reputation_shift.

char_seren: "Do not mistake silence for surrender," char_seren says.

The relationship pressure around rel_kael_seren does not vanish. Trust shifts, resentment rises, and Seren refuses to deny the badge.
""".strip()

    return AssembledScene(
        assembled_scene_id=f"assembled_{scene_id}",
        scene_id=scene_id,
        draft_id=f"draft_{scene_id}",
        dialogue_block_id=f"dialogue_block_{scene_id}",
        selected_format="scene",
        title="Scene at location_court",
        assembled_text=text,
        sections=[{"section_id": f"section_{scene_id}", "beat_type": "assembled", "text": text}],
        continuity_trace={
            "blueprint_id": f"blueprint_{scene_id}",
            "scene_beat_ids": ["beat_setup", "beat_consequence"],
            "dialogue_line_ids": ["line_001"],
            "ending_hook": "Seren refuses to deny the badge.",
            "scene_objective": "Kael must expose the cracked badge.",
        },
        used_character_ids=["char_kael", "char_seren"],
        used_relationship_ids=["rel_kael_seren"],
        used_secret_ids=["secret_seren_source"],
        used_causal_ids=["cause_trial_reveal", "cons_reputation_shift"],
        used_world_details=["Oath Court", "cracked badge", "public proof changes legal rank"],
        generation_notes=["assembled scene"],
        warnings=[],
    )


def build_quality_report(scene_id="scene_chapter_1", passed=True):
    return SceneQualityReport(
        report_id=f"scene_quality_{scene_id}",
        scene_id=scene_id,
        passed=passed,
        overall_score=0.82 if passed else 0.42,
        length_score=0.8,
        world_specificity_score=0.8,
        character_presence_score=0.8,
        relationship_pressure_score=0.8,
        secret_pressure_score=0.8,
        causal_trace_score=0.8,
        dialogue_presence_score=0.8,
        generic_phrase_risk=0.0,
        blockers=[] if passed else ["overall quality score too low"],
        warnings=[],
        improvement_targets=[] if passed else ["length"],
    )


def test_chapter_generator_builds_chapter():
    engine = ChapterGenerator()

    result = engine.generate_chapter(
        chapter_id="chapter_001",
        chapter_number=1,
        chapter_title="The Badge in the Court",
        assembled_scenes=[build_scene()],
        quality_reports=[build_quality_report()],
        story_context={"story_context_id": "storyctx_chapter"},
    )

    chapter = result["generated_chapter"]

    assert result["success"] is True
    assert chapter.chapter_id == "chapter_001"
    assert chapter.chapter_number == 1
    assert chapter.title == "The Badge in the Court"
    assert chapter.chapter_text
    assert chapter.scene_ids == ["scene_chapter_1"]
    assert chapter.assembled_scene_ids == ["assembled_scene_chapter_1"]


def test_chapter_generator_tracks_used_context():
    engine = ChapterGenerator()

    chapter = engine.generate_chapter(
        chapter_id="chapter_001",
        assembled_scenes=[build_scene()],
        quality_reports=[build_quality_report()],
    )["generated_chapter"]

    assert "char_kael" in chapter.used_character_ids
    assert "rel_kael_seren" in chapter.used_relationship_ids
    assert "secret_seren_source" in chapter.used_secret_ids
    assert "cause_trial_reveal" in chapter.used_causal_ids
    assert "Oath Court" in chapter.used_world_details


def test_chapter_generator_builds_open_loops_and_hooks():
    engine = ChapterGenerator()

    chapter = engine.generate_chapter(
        chapter_id="chapter_001",
        assembled_scenes=[build_scene()],
        quality_reports=[build_quality_report()],
    )["generated_chapter"]

    assert chapter.open_loops
    assert any(loop["loop_type"] == "ending_hook" for loop in chapter.open_loops)
    assert any(loop.get("secret_id") == "secret_seren_source" for loop in chapter.open_loops)
    assert "Seren refuses to deny the badge." in chapter.next_chapter_hooks


def test_chapter_generator_quality_summary_tracks_failed_scenes():
    engine = ChapterGenerator()

    chapter = engine.generate_chapter(
        chapter_id="chapter_001",
        assembled_scenes=[build_scene()],
        quality_reports=[build_quality_report(passed=False)],
    )["generated_chapter"]

    assert chapter.quality_summary["failed_scene_count"] == 1
    assert any("did not pass quality gate" in warning for warning in chapter.warnings)


def test_chapter_generator_validates_chapter():
    engine = ChapterGenerator()

    chapter = engine.generate_chapter(
        chapter_id="chapter_001",
        assembled_scenes=[build_scene()],
        quality_reports=[build_quality_report()],
    )["generated_chapter"]

    validation = engine.validate_chapter(chapter=chapter)

    assert validation["success"] is True
    assert validation["valid"] is True
    assert "chapter_id_present" in validation["passed_checks"]
    assert "chapter_text_present" in validation["passed_checks"]
    assert "continuity_trace_present" in validation["passed_checks"]


def test_chapter_generator_summarizes_chapter():
    engine = ChapterGenerator()

    chapter = engine.generate_chapter(
        chapter_id="chapter_001",
        assembled_scenes=[build_scene()],
        quality_reports=[build_quality_report()],
    )["generated_chapter"]

    summary = engine.summarize_chapter(chapter=chapter)

    assert summary["success"] is True
    assert summary["summary"]["chapter_id"] == "chapter_001"
    assert summary["summary"]["scene_count"] == 1
    assert summary["summary"]["used_secret_count"] == 1
    assert summary["summary"]["open_loop_count"] >= 1


def test_chapter_generator_builds_long_form_handoff_payload():
    engine = ChapterGenerator()

    chapter = engine.generate_chapter(
        chapter_id="chapter_001",
        assembled_scenes=[build_scene()],
        quality_reports=[build_quality_report()],
    )["generated_chapter"]

    result = engine.build_long_form_handoff_payload(chapter=chapter)
    payload = result["long_form_handoff_payload"]

    assert result["success"] is True
    assert payload["chapter_id"] == "chapter_001"
    assert payload["chapter_text"] == chapter.chapter_text
    assert payload["open_loops"] == chapter.open_loops
    assert payload["next_chapter_hooks"] == chapter.next_chapter_hooks


def test_chapter_generator_handles_multiple_scenes():
    engine = ChapterGenerator()

    chapter = engine.generate_chapter(
        chapter_id="chapter_002",
        chapter_number=2,
        assembled_scenes=[build_scene("scene_a"), build_scene("scene_b")],
        quality_reports=[build_quality_report("scene_a"), build_quality_report("scene_b")],
    )["generated_chapter"]

    assert len(chapter.scene_ids) == 2
    assert "scene_a" in chapter.scene_ids
    assert "scene_b" in chapter.scene_ids
    assert len(chapter.sections) == 2

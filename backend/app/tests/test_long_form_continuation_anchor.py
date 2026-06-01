from backend.app.engines.story_generation.long_form_continuation_anchor import LongFormContinuationAnchorEngine
from backend.app.schemas.story_generation import GeneratedChapter, LongFormContinuationAnchor


def build_chapter():
    return GeneratedChapter(
        chapter_id="chapter_001",
        chapter_number=1,
        title="The Badge in the Court",
        chapter_text=(
            "# The Badge in the Court\n\n"
            "Kael exposes the cracked badge in the Oath Court. Seren refuses to deny it. "
            "The secret_seren_source remains unresolved, and cause_trial_reveal pushes toward "
            "cons_reputation_shift. The chapter ends with the court waiting for the next answer."
        ),
        scene_ids=["scene_001"],
        assembled_scene_ids=["assembled_scene_001"],
        used_character_ids=["char_kael", "char_seren"],
        used_relationship_ids=["rel_kael_seren"],
        used_secret_ids=["secret_seren_source"],
        used_causal_ids=["cause_trial_reveal", "cons_reputation_shift"],
        used_world_details=["Oath Court", "cracked badge", "public proof changes legal rank"],
        open_loops=[
            {
                "loop_id": "open_loop_scene_001_ending_hook",
                "source_scene_id": "scene_001",
                "loop_type": "ending_hook",
                "status": "open",
                "description": "Seren refuses to deny the badge.",
            }
        ],
        next_chapter_hooks=["Seren refuses to deny the badge."],
        quality_summary={"failed_scene_count": 0, "average_overall_score": 0.82},
        warnings=[],
    )


def test_continuation_anchor_engine_builds_anchor():
    engine = LongFormContinuationAnchorEngine()

    result = engine.build_continuation_anchor(
        chapter=build_chapter(),
        story_context={"story_context_id": "storyctx_001"},
    )

    anchor = result["continuation_anchor"]

    assert result["success"] is True
    assert anchor.anchor_id == "continuation_anchor_chapter_001"
    assert anchor.chapter_id == "chapter_001"
    assert anchor.chapter_number == 1
    assert "char_kael" in anchor.active_character_ids
    assert "rel_kael_seren" in anchor.active_relationship_ids
    assert "secret_seren_source" in anchor.active_secret_ids
    assert "cause_trial_reveal" in anchor.active_causal_ids


def test_continuation_anchor_tracks_open_loops_and_hooks():
    engine = LongFormContinuationAnchorEngine()

    anchor = engine.build_continuation_anchor(
        chapter=build_chapter(),
    )["continuation_anchor"]

    assert anchor.open_loops
    assert anchor.next_chapter_hooks
    assert any(loop["loop_id"] == "open_loop_scene_001_ending_hook" for loop in anchor.open_loops)
    assert "Seren refuses to deny the badge." in anchor.next_chapter_hooks


def test_continuation_anchor_builds_memory_update_candidates():
    engine = LongFormContinuationAnchorEngine()

    anchor = engine.build_continuation_anchor(
        chapter=build_chapter(),
    )["continuation_anchor"]

    update_types = {item["update_type"] for item in anchor.memory_update_candidates}

    assert "character_progress" in update_types
    assert "relationship_progress" in update_types
    assert "knowledge_or_secret_progress" in update_types
    assert "causal_progress" in update_types


def test_continuation_anchor_merges_previous_anchor():
    engine = LongFormContinuationAnchorEngine()

    previous = LongFormContinuationAnchor(
        anchor_id="continuation_anchor_previous",
        chapter_id="chapter_000",
        chapter_number=0,
        active_character_ids=["char_old"],
        active_relationship_ids=["rel_old"],
        active_secret_ids=["secret_old"],
        active_causal_ids=["cause_old"],
        active_world_details=["Old Tower"],
        open_loops=[
            {
                "loop_id": "open_loop_old",
                "loop_type": "old_loop",
                "status": "open",
                "description": "Old promise remains unpaid.",
            }
        ],
        next_chapter_hooks=["Old promise remains unpaid."],
    )

    anchor = engine.build_continuation_anchor(
        chapter=build_chapter(),
        previous_anchor=previous,
    )["continuation_anchor"]

    assert "char_old" in anchor.active_character_ids
    assert "rel_old" in anchor.active_relationship_ids
    assert "secret_old" in anchor.active_secret_ids
    assert "cause_old" in anchor.active_causal_ids
    assert any(loop["loop_id"] == "open_loop_old" for loop in anchor.open_loops)


def test_continuation_anchor_validates_anchor():
    engine = LongFormContinuationAnchorEngine()

    anchor = engine.build_continuation_anchor(
        chapter=build_chapter(),
    )["continuation_anchor"]

    validation = engine.validate_continuation_anchor(anchor=anchor)

    assert validation["success"] is True
    assert validation["valid"] is True
    assert "anchor_id_present" in validation["passed_checks"]
    assert "active_characters_present" in validation["passed_checks"]
    assert "open_loops_tracked" in validation["passed_checks"]


def test_continuation_anchor_summarizes_anchor():
    engine = LongFormContinuationAnchorEngine()

    anchor = engine.build_continuation_anchor(
        chapter=build_chapter(),
    )["continuation_anchor"]

    summary = engine.summarize_anchor(anchor=anchor)

    assert summary["success"] is True
    assert summary["summary"]["chapter_id"] == "chapter_001"
    assert summary["summary"]["active_character_count"] == 2
    assert summary["summary"]["active_secret_count"] == 1
    assert summary["summary"]["open_loop_count"] >= 1


def test_continuation_anchor_builds_next_chapter_seed():
    engine = LongFormContinuationAnchorEngine()

    anchor = engine.build_continuation_anchor(
        chapter=build_chapter(),
    )["continuation_anchor"]

    result = engine.build_next_chapter_seed(anchor=anchor)
    seed = result["next_chapter_seed"]

    assert result["success"] is True
    assert seed["source_anchor_id"] == "continuation_anchor_chapter_001"
    assert "char_kael" in seed["required_character_ids"]
    assert "secret_seren_source" in seed["required_secret_ids"]
    assert seed["open_loops_to_address"]


def test_continuation_anchor_flags_failed_quality():
    engine = LongFormContinuationAnchorEngine()
    chapter = build_chapter()
    chapter.quality_summary = {"failed_scene_count": 1}

    anchor = engine.build_continuation_anchor(
        chapter=chapter,
    )["continuation_anchor"]

    assert any("failed quality gate" in flag for flag in anchor.risk_flags)

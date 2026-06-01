from backend.app.engines.story_generation.long_form_memory_bridge import LongFormMemoryBridge
from backend.app.schemas.story_generation import (
    GeneratedChapter,
    LongFormContinuationAnchor,
    MultiScenePacingReport,
)


def build_chapter():
    return GeneratedChapter(
        chapter_id="chapter_memory",
        chapter_number=1,
        title="The Memory Chapter",
        chapter_text=(
            "Kael exposes the cracked badge in the Oath Court. Seren refuses to deny it. "
            "The secret_seren_source remains active. cause_trial_reveal creates cons_reputation_shift. "
            "The relationship between Kael and Seren changes under pressure."
        ),
        scene_ids=["scene_001"],
        assembled_scene_ids=["assembled_scene_001"],
        used_character_ids=["char_kael", "char_seren"],
        used_relationship_ids=["rel_kael_seren"],
        used_secret_ids=["secret_seren_source"],
        used_causal_ids=["cause_trial_reveal", "cons_reputation_shift"],
        used_world_details=["Oath Court", "cracked badge"],
        open_loops=[
            {
                "loop_id": "open_loop_secret",
                "loop_type": "secret_pressure",
                "status": "open",
                "description": "Secret remains hidden.",
            }
        ],
        next_chapter_hooks=["Seren refuses to deny the badge."],
        quality_summary={"failed_scene_count": 0},
    )


def build_anchor():
    return LongFormContinuationAnchor(
        anchor_id="continuation_anchor_memory",
        chapter_id="chapter_memory",
        chapter_number=1,
        active_character_ids=["char_kael", "char_seren"],
        active_relationship_ids=["rel_kael_seren"],
        active_secret_ids=["secret_seren_source"],
        active_causal_ids=["cause_trial_reveal", "cons_reputation_shift"],
        active_world_details=["Oath Court", "cracked badge"],
        open_loops=[
            {
                "loop_id": "open_loop_secret",
                "loop_type": "secret_pressure",
                "status": "open",
                "description": "Secret remains hidden.",
            }
        ],
        next_chapter_hooks=["Seren refuses to deny the badge."],
        continuity_reminders=["Do not reveal secret_seren_source too early."],
        risk_flags=[],
    )


def build_pacing_report(score=0.74):
    return MultiScenePacingReport(
        pacing_report_id="multi_scene_pacing_memory",
        source_id="chapter_memory",
        scene_count=1,
        overall_pacing_score=score,
        tension_curve_score=0.7,
        emotional_variety_score=0.7,
        relationship_rhythm_score=0.7,
        secret_pressure_spacing_score=0.7,
        causal_spacing_score=0.7,
        world_detail_spacing_score=0.7,
        dialogue_action_balance_score=0.7,
        scene_pacing_map=[],
        pacing_repair_targets=[],
        warnings=[],
    )


def test_long_form_memory_bridge_builds_report():
    bridge = LongFormMemoryBridge()

    result = bridge.build_memory_bridge_report(
        source_id="chapter_memory",
        chapter=build_chapter(),
        continuation_anchor=build_anchor(),
        pacing_report=build_pacing_report(),
    )

    report = result["memory_bridge_report"]

    assert result["success"] is True
    assert report.memory_bridge_id == "memory_bridge_chapter_memory"
    assert report.chapter_id == "chapter_memory"
    assert report.character_memory_updates
    assert report.relationship_memory_updates
    assert report.secret_memory_updates
    assert report.causal_memory_updates
    assert report.world_memory_updates
    assert report.open_loop_updates


def test_long_form_memory_bridge_creates_character_and_relationship_updates():
    bridge = LongFormMemoryBridge()

    report = bridge.build_memory_bridge_report(
        source_id="chapter_memory",
        chapter=build_chapter(),
        continuation_anchor=build_anchor(),
        pacing_report=build_pacing_report(),
    )["memory_bridge_report"]

    character_targets = {item["target_id"] for item in report.character_memory_updates}
    relationship_targets = {item["target_id"] for item in report.relationship_memory_updates}

    assert "char_kael" in character_targets
    assert "char_seren" in character_targets
    assert "rel_kael_seren" in relationship_targets


def test_long_form_memory_bridge_tracks_secret_and_causal_memory():
    bridge = LongFormMemoryBridge()

    report = bridge.build_memory_bridge_report(
        source_id="chapter_memory",
        chapter=build_chapter(),
        continuation_anchor=build_anchor(),
        pacing_report=build_pacing_report(),
    )["memory_bridge_report"]

    secret_targets = {item["target_id"] for item in report.secret_memory_updates}
    causal_targets = {item["target_id"] for item in report.causal_memory_updates}

    assert "secret_seren_source" in secret_targets
    assert "cause_trial_reveal" in causal_targets
    assert "cons_reputation_shift" in causal_targets


def test_long_form_memory_bridge_builds_continuity_ledger():
    bridge = LongFormMemoryBridge()

    report = bridge.build_memory_bridge_report(
        source_id="chapter_memory",
        chapter=build_chapter(),
        continuation_anchor=build_anchor(),
        pacing_report=build_pacing_report(),
    )["memory_bridge_report"]

    assert report.continuity_ledger_entries
    categories = {entry["category"] for entry in report.continuity_ledger_entries}
    assert "character" in categories
    assert "relationship" in categories
    assert "secret" in categories
    assert "causal" in categories
    assert "world" in categories
    assert "open_loop" in categories


def test_long_form_memory_bridge_builds_next_generation_payload():
    bridge = LongFormMemoryBridge()

    report = bridge.build_memory_bridge_report(
        source_id="chapter_memory",
        chapter=build_chapter(),
        continuation_anchor=build_anchor(),
        pacing_report=build_pacing_report(),
    )["memory_bridge_report"]

    payload = report.next_generation_memory_payload

    assert payload["source_chapter_id"] == "chapter_memory"
    assert "char_kael" in payload["required_character_ids"]
    assert "secret_seren_source" in payload["required_secret_ids"]
    assert "cause_trial_reveal" in payload["required_causal_ids"]
    assert payload["open_loops_to_carry"]


def test_long_form_memory_bridge_builds_persistence_payload():
    bridge = LongFormMemoryBridge()

    report = bridge.build_memory_bridge_report(
        source_id="chapter_memory",
        chapter=build_chapter(),
        continuation_anchor=build_anchor(),
        pacing_report=build_pacing_report(),
    )["memory_bridge_report"]

    result = bridge.build_persistence_payload(report=report)
    payload = result["persistence_payload"]

    assert result["success"] is True
    assert payload["chapter_id"] == "chapter_memory"
    assert payload["updates"]["characters"]
    assert payload["updates"]["continuity_ledger"]
    assert payload["next_generation_memory_payload"]


def test_long_form_memory_bridge_validates_report():
    bridge = LongFormMemoryBridge()

    report = bridge.build_memory_bridge_report(
        source_id="chapter_memory",
        chapter=build_chapter(),
        continuation_anchor=build_anchor(),
        pacing_report=build_pacing_report(),
    )["memory_bridge_report"]

    validation = bridge.validate_memory_bridge_report(report=report)

    assert validation["success"] is True
    assert validation["valid"] is True
    assert "memory_bridge_id_present" in validation["passed_checks"]
    assert "continuity_ledger_entries_present" in validation["passed_checks"]
    assert "next_generation_memory_payload_present" in validation["passed_checks"]


def test_long_form_memory_bridge_summarizes_report():
    bridge = LongFormMemoryBridge()

    report = bridge.build_memory_bridge_report(
        source_id="chapter_memory",
        chapter=build_chapter(),
        continuation_anchor=build_anchor(),
        pacing_report=build_pacing_report(),
    )["memory_bridge_report"]

    summary = bridge.summarize_memory_bridge_report(report=report)

    assert summary["success"] is True
    assert summary["summary"]["chapter_id"] == "chapter_memory"
    assert summary["summary"]["character_update_count"] == 2
    assert summary["summary"]["secret_update_count"] == 1
    assert summary["summary"]["causal_update_count"] == 2


def test_long_form_memory_bridge_flags_weak_pacing():
    bridge = LongFormMemoryBridge()

    report = bridge.build_memory_bridge_report(
        source_id="chapter_memory",
        chapter=build_chapter(),
        continuation_anchor=build_anchor(),
        pacing_report=build_pacing_report(score=0.40),
    )["memory_bridge_report"]

    assert any("pacing score is weak" in flag for flag in report.memory_risk_flags)

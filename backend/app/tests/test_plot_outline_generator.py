from backend.app.engines.story_generation.plot_outline_generator import PlotOutlineGenerator
from backend.app.schemas.story_generation import AssembledScene, GeneratedChapter, LongFormContinuationAnchor


def build_chapter():
    return GeneratedChapter(
        chapter_id="chapter_outline",
        chapter_number=1,
        title="The Badge in the Court",
        chapter_text="Kael exposes the badge. Seren refuses to deny it.",
        scene_ids=["scene_001", "scene_002"],
        assembled_scene_ids=["assembled_scene_001", "assembled_scene_002"],
        sections=[
            {
                "scene_id": "scene_001",
                "title": "The Oath Court",
                "text": "Kael enters the court.",
                "used_character_ids": ["char_kael"],
                "used_secret_ids": ["secret_seren_source"],
                "used_causal_ids": ["cause_trial_reveal"],
                "used_world_details": ["Oath Court"],
            },
            {
                "scene_id": "scene_002",
                "title": "The Refusal",
                "text": "Seren refuses to deny the badge.",
                "used_character_ids": ["char_kael", "char_seren"],
                "used_secret_ids": ["secret_seren_source"],
                "used_causal_ids": ["cons_reputation_shift"],
                "used_world_details": ["cracked badge"],
            },
        ],
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


def build_scene():
    return AssembledScene(
        assembled_scene_id="assembled_scene_extra",
        scene_id="scene_extra",
        title="The Witness Tier",
        assembled_text="A witness notices the cracked badge.",
        continuity_trace={
            "scene_objective": "Show public attention rising.",
            "ending_hook": "The witness remembers another badge.",
        },
        used_character_ids=["char_witness"],
        used_relationship_ids=[],
        used_secret_ids=["secret_old_badge"],
        used_causal_ids=["cause_witness_memory"],
        used_world_details=["witness tiers"],
    )


def build_anchor():
    return LongFormContinuationAnchor(
        anchor_id="continuation_anchor_outline",
        chapter_id="chapter_outline",
        chapter_number=1,
        active_character_ids=["char_kael", "char_seren"],
        active_relationship_ids=["rel_kael_seren"],
        active_secret_ids=["secret_seren_source"],
        active_causal_ids=["cause_trial_reveal", "cons_reputation_shift"],
        active_world_details=["Oath Court", "cracked badge"],
        open_loops=[
            {
                "loop_id": "open_loop_anchor",
                "loop_type": "ending_hook",
                "status": "open",
                "description": "The court waits for Seren's answer.",
            }
        ],
        next_chapter_hooks=["The court waits for Seren's answer."],
        continuity_reminders=["Do not reveal secret_seren_source too early."],
    )


def test_plot_outline_generator_builds_outline():
    engine = PlotOutlineGenerator()

    result = engine.generate_plot_outline(
        source_id="outline_source",
        title="Court Secrets",
        chapters=[build_chapter()],
        assembled_scenes=[build_scene()],
        continuation_anchor=build_anchor(),
        story_context={"premise": "A public proof system threatens private loyalties."},
    )

    outline = result["plot_outline"]

    assert result["success"] is True
    assert outline.outline_id == "plot_outline_outline_source"
    assert outline.title == "Court Secrets"
    assert outline.premise == "A public proof system threatens private loyalties."
    assert outline.act_structure
    assert outline.scene_sequence


def test_plot_outline_generator_tracks_threads():
    engine = PlotOutlineGenerator()

    outline = engine.generate_plot_outline(
        source_id="outline_source",
        chapters=[build_chapter()],
        assembled_scenes=[build_scene()],
        continuation_anchor=build_anchor(),
    )["plot_outline"]

    character_ids = {item["character_id"] for item in outline.character_arc_threads}
    relationship_ids = {item["relationship_id"] for item in outline.relationship_arc_threads}
    secret_ids = {item["secret_id"] for item in outline.secret_threads}
    causal_ids = {item["causal_id"] for item in outline.causal_threads}

    assert "char_kael" in character_ids
    assert "char_seren" in character_ids
    assert "char_witness" in character_ids
    assert "rel_kael_seren" in relationship_ids
    assert "secret_seren_source" in secret_ids
    assert "secret_old_badge" in secret_ids
    assert "cause_trial_reveal" in causal_ids


def test_plot_outline_generator_builds_payoff_setups():
    engine = PlotOutlineGenerator()

    outline = engine.generate_plot_outline(
        source_id="outline_source",
        chapters=[build_chapter()],
        assembled_scenes=[build_scene()],
        continuation_anchor=build_anchor(),
    )["plot_outline"]

    payoff_ids = {item["payoff_id"] for item in outline.payoff_setups}

    assert "payoff_secret_secret_seren_source" in payoff_ids
    assert "payoff_causal_cause_trial_reveal" in payoff_ids
    assert "payoff_relationship_rel_kael_seren" in payoff_ids
    assert "payoff_open_loop_open_loop_secret" in payoff_ids


def test_plot_outline_generator_builds_continuity_requirements():
    engine = PlotOutlineGenerator()

    outline = engine.generate_plot_outline(
        source_id="outline_source",
        chapters=[build_chapter()],
        continuation_anchor=build_anchor(),
    )["plot_outline"]

    requirements = outline.continuity_requirements

    assert "char_kael" in requirements["required_character_ids"]
    assert "rel_kael_seren" in requirements["required_relationship_ids"]
    assert "secret_seren_source" in requirements["required_secret_ids"]
    assert "cause_trial_reveal" in requirements["required_causal_ids"]
    assert "Oath Court" in requirements["required_world_details"]
    assert "Do not reveal secrets without planned reveal timing." in requirements["rules"]


def test_plot_outline_generator_builds_outline_text():
    engine = PlotOutlineGenerator()

    outline = engine.generate_plot_outline(
        source_id="outline_source",
        title="Court Secrets",
        chapters=[build_chapter()],
        continuation_anchor=build_anchor(),
    )["plot_outline"]

    result = engine.build_outline_text(outline=outline)
    text = result["outline_text"]

    assert result["success"] is True
    assert "Premise" in text
    assert "Act Structure" in text
    assert "Scene Sequence" in text
    assert "Open Loops" in text
    assert "Payoff Setups" in text


def test_plot_outline_generator_validates_outline():
    engine = PlotOutlineGenerator()

    outline = engine.generate_plot_outline(
        source_id="outline_source",
        chapters=[build_chapter()],
        continuation_anchor=build_anchor(),
    )["plot_outline"]

    validation = engine.validate_plot_outline(outline=outline)

    assert validation["success"] is True
    assert validation["valid"] is True
    assert "outline_id_present" in validation["passed_checks"]
    assert "act_structure_present" in validation["passed_checks"]
    assert "scene_sequence_present" in validation["passed_checks"]
    assert "continuity_requirements_present" in validation["passed_checks"]


def test_plot_outline_generator_summarizes_outline():
    engine = PlotOutlineGenerator()

    outline = engine.generate_plot_outline(
        source_id="outline_source",
        chapters=[build_chapter()],
        assembled_scenes=[build_scene()],
        continuation_anchor=build_anchor(),
    )["plot_outline"]

    summary = engine.summarize_plot_outline(outline=outline)

    assert summary["success"] is True
    assert summary["summary"]["source_id"] == "outline_source"
    assert summary["summary"]["scene_count"] >= 2
    assert summary["summary"]["character_thread_count"] >= 2
    assert summary["summary"]["payoff_setup_count"] >= 3


def test_plot_outline_generator_warns_without_sources():
    engine = PlotOutlineGenerator()

    outline = engine.generate_plot_outline(
        source_id="empty_outline",
        chapters=[],
        assembled_scenes=[],
        continuation_anchor=None,
    )["plot_outline"]

    assert any("No chapters or assembled scenes supplied" in warning for warning in outline.warnings)

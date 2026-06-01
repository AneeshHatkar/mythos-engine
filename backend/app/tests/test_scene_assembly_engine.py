from backend.app.engines.story_generation.scene_assembly_engine import SceneAssemblyEngine
from backend.app.schemas.story_generation import (
    GeneratedDialogueBlock,
    GeneratedDialogueLine,
    GeneratedSceneDraft,
    SceneBeat,
    SceneBlueprint,
)


def build_blueprint():
    return SceneBlueprint(
        blueprint_id="blueprint_assembly",
        scene_id="scene_assembly",
        scene_purpose="Assemble a court scene.",
        pov_character_id="char_kael",
        active_character_ids=["char_kael", "char_seren"],
        location_id="location_court",
        scene_objective="Kael must expose the cracked badge.",
        secret_pressure=["char_kael lacks required secret knowledge: secret_seren_source."],
        relationship_pressure=["rel_kael_seren pressure"],
        ending_hook="Seren refuses to deny the badge.",
        required_world_details=["Oath Court", "cracked badge"],
    )


def build_scene_draft():
    return GeneratedSceneDraft(
        draft_id="draft_scene_assembly",
        scene_id="scene_assembly",
        blueprint_id="blueprint_assembly",
        selected_format="scene",
        title="Scene at location_court",
        draft_text="# Scene at location_court\n\nIn location_court, Oath Court presses against char_kael and char_seren. The secret remains dangerous. The relationship layer matters here because trust shifts.",
        sections=[
            {
                "section_id": "section_setup",
                "beat_id": "beat_setup",
                "beat_type": "setup",
                "tension_value": 0.3,
                "text": "In location_court, Oath Court presses against char_kael and char_seren. The secret remains dangerous.",
                "causal_links": ["cause_trial_reveal"],
                "knowledge_constraints": [],
            },
            {
                "section_id": "section_secret",
                "beat_id": "beat_secret",
                "beat_type": "secret_pressure",
                "tension_value": 0.7,
                "text": "The secret_seren_source remains hidden while the cracked badge is raised.",
                "causal_links": ["cause_trial_reveal"],
                "knowledge_constraints": ["char_kael does not know secret_seren_source"],
            },
            {
                "section_id": "section_ending",
                "beat_id": "beat_ending",
                "beat_type": "ending_hook",
                "tension_value": 0.9,
                "text": "Seren refuses to deny the badge.",
                "causal_links": ["cause_trial_reveal"],
                "knowledge_constraints": [],
            },
        ],
        used_world_details=["Oath Court", "cracked badge"],
        used_character_ids=["char_kael", "char_seren"],
        used_relationship_ids=["rel_kael_seren"],
        used_secret_ids=["secret_seren_source"],
        used_causal_ids=["cause_trial_reveal"],
        generation_notes=["draft generated"],
        warnings=[],
    )


def build_dialogue_block():
    return GeneratedDialogueBlock(
        dialogue_block_id="dialogue_block_scene_assembly",
        scene_id="scene_assembly",
        selected_format="scene",
        lines=[
            GeneratedDialogueLine(
                line_id="line_scene_assembly_01",
                scene_id="scene_assembly",
                dialogue_beat_id="dialogue_001",
                speaker_id="char_seren",
                listener_ids=["char_kael"],
                line_text='"Do not mistake silence for surrender," char_seren says.',
                subtext="guilt under control",
                hidden_meaning="She protects the source.",
                emotion="guilt",
                secret_risk=0.8,
                relationship_effect="trust shifts",
            )
        ],
        rendered_text='char_seren: "Do not mistake silence for surrender," char_seren says.',
        used_speaker_ids=["char_seren"],
        used_dialogue_beat_ids=["dialogue_001"],
        warnings=[],
    )


def build_scene_beats():
    return [
        SceneBeat(
            beat_id="beat_setup",
            scene_id="scene_assembly",
            beat_index=1,
            beat_type="setup",
            purpose="Set court pressure.",
            character_ids=["char_kael", "char_seren"],
            causal_links=["cause_trial_reveal"],
            tension_value=0.3,
        ),
        SceneBeat(
            beat_id="beat_secret",
            scene_id="scene_assembly",
            beat_index=2,
            beat_type="secret_pressure",
            purpose="Keep secret hidden.",
            character_ids=["char_kael", "char_seren"],
            causal_links=["cause_trial_reveal"],
            tension_value=0.7,
        ),
    ]


def test_scene_assembly_engine_assembles_scene():
    engine = SceneAssemblyEngine()

    result = engine.assemble_scene(
        blueprint=build_blueprint(),
        scene_draft=build_scene_draft(),
        dialogue_block=build_dialogue_block(),
        scene_beats=build_scene_beats(),
        prose_style_profile={"prose_style_profile_id": "prose_style_scene_assembly"},
        story_context={"story_context_id": "storyctx_assembly"},
        world_detail_pack={"world_detail_pack_id": "worlddetails_assembly"},
    )

    assembled = result["assembled_scene"]

    assert result["success"] is True
    assert assembled.assembled_scene_id == "assembled_scene_assembly"
    assert assembled.scene_id == "scene_assembly"
    assert assembled.draft_id == "draft_scene_assembly"
    assert assembled.dialogue_block_id == "dialogue_block_scene_assembly"
    assert assembled.assembled_text
    assert len(assembled.sections) == 4


def test_scene_assembly_engine_tracks_continuity():
    engine = SceneAssemblyEngine()

    assembled = engine.assemble_scene(
        blueprint=build_blueprint(),
        scene_draft=build_scene_draft(),
        dialogue_block=build_dialogue_block(),
        scene_beats=build_scene_beats(),
        prose_style_profile={"prose_style_profile_id": "prose_style_scene_assembly"},
        story_context={"story_context_id": "storyctx_assembly"},
        world_detail_pack={"world_detail_pack_id": "worlddetails_assembly"},
    )["assembled_scene"]

    trace = assembled.continuity_trace

    assert trace["blueprint_id"] == "blueprint_assembly"
    assert trace["draft_id"] == "draft_scene_assembly"
    assert trace["dialogue_block_id"] == "dialogue_block_scene_assembly"
    assert "beat_setup" in trace["scene_beat_ids"]
    assert "line_scene_assembly_01" in trace["dialogue_line_ids"]
    assert trace["style_profile_id"] == "prose_style_scene_assembly"


def test_scene_assembly_engine_preserves_used_ids():
    engine = SceneAssemblyEngine()

    assembled = engine.assemble_scene(
        blueprint=build_blueprint(),
        scene_draft=build_scene_draft(),
        dialogue_block=build_dialogue_block(),
        scene_beats=build_scene_beats(),
    )["assembled_scene"]

    assert "char_kael" in assembled.used_character_ids
    assert "char_seren" in assembled.used_character_ids
    assert "rel_kael_seren" in assembled.used_relationship_ids
    assert "secret_seren_source" in assembled.used_secret_ids
    assert "cause_trial_reveal" in assembled.used_causal_ids
    assert "Oath Court" in assembled.used_world_details


def test_scene_assembly_engine_validates_assembled_scene():
    engine = SceneAssemblyEngine()

    assembled = engine.assemble_scene(
        blueprint=build_blueprint(),
        scene_draft=build_scene_draft(),
        dialogue_block=build_dialogue_block(),
        scene_beats=build_scene_beats(),
    )["assembled_scene"]

    validation = engine.validate_assembled_scene(assembled_scene=assembled)

    assert validation["success"] is True
    assert validation["valid"] is True
    assert "assembled_scene_id_present" in validation["passed_checks"]
    assert "assembled_text_present" in validation["passed_checks"]
    assert "continuity_trace_present" in validation["passed_checks"]


def test_scene_assembly_engine_summarizes_scene():
    engine = SceneAssemblyEngine()

    assembled = engine.assemble_scene(
        blueprint=build_blueprint(),
        scene_draft=build_scene_draft(),
        dialogue_block=build_dialogue_block(),
        scene_beats=build_scene_beats(),
    )["assembled_scene"]

    summary = engine.summarize_assembled_scene(assembled_scene=assembled)

    assert summary["success"] is True
    assert summary["summary"]["scene_id"] == "scene_assembly"
    assert summary["summary"]["section_count"] == 4
    assert summary["summary"]["used_character_count"] == 2
    assert summary["summary"]["used_secret_count"] == 1


def test_scene_assembly_engine_builds_chapter_handoff_payload():
    engine = SceneAssemblyEngine()

    assembled = engine.assemble_scene(
        blueprint=build_blueprint(),
        scene_draft=build_scene_draft(),
        dialogue_block=build_dialogue_block(),
        scene_beats=build_scene_beats(),
    )["assembled_scene"]

    result = engine.build_chapter_handoff_payload(assembled_scene=assembled)
    payload = result["chapter_handoff_payload"]

    assert result["success"] is True
    assert payload["scene_id"] == "scene_assembly"
    assert payload["assembled_scene_id"] == "assembled_scene_assembly"
    assert payload["text"] == assembled.assembled_text
    assert payload["continuity_trace"]


def test_scene_assembly_engine_supports_missing_dialogue_block():
    engine = SceneAssemblyEngine()

    assembled = engine.assemble_scene(
        blueprint=build_blueprint(),
        scene_draft=build_scene_draft(),
        dialogue_block=None,
        scene_beats=build_scene_beats(),
    )["assembled_scene"]

    assert assembled.dialogue_block_id is None
    assert any("No dialogue block supplied" in warning for warning in assembled.warnings)

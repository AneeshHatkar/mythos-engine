from backend.app.engines.story_generation.dialogue_line_generator import DialogueLineGenerator
from backend.app.schemas.story_generation import (
    DialogueBeat,
    GeneratedSceneDraft,
    RelationshipBeat,
    SceneBlueprint,
)


def build_blueprint():
    return SceneBlueprint(
        blueprint_id="blueprint_dialogue_lines",
        scene_id="scene_dialogue_lines",
        scene_purpose="Force a difficult exchange.",
        pov_character_id="char_kael",
        active_character_ids=["char_kael", "char_seren"],
        location_id="location_court",
        scene_objective="Kael must expose the cracked badge.",
        secret_pressure=["char_kael lacks required secret knowledge: secret_seren_source."],
        relationship_pressure=["rel_kael_seren pressure"],
        ending_hook="Seren refuses to deny the badge.",
    )


def build_scene_draft():
    return GeneratedSceneDraft(
        draft_id="draft_scene_dialogue_lines",
        scene_id="scene_dialogue_lines",
        blueprint_id="blueprint_dialogue_lines",
        selected_format="scene",
        title="Scene at location_court",
        draft_text="# Scene at location_court\n\nA draft exists.",
        sections=[],
        used_character_ids=["char_kael", "char_seren"],
        used_world_details=["Oath Court"],
    )


def build_dialogue_beats():
    return [
        DialogueBeat(
            dialogue_beat_id="dialogue_scene_dialogue_lines_01_secret_pressure",
            scene_id="scene_dialogue_lines",
            speaker_id="char_seren",
            listener_ids=["char_kael"],
            surface_meaning="Seren avoids the answer.",
            hidden_meaning="She protects the source.",
            subtext="guilt under control",
            emotion="guilt",
            secret_risk=0.85,
            relationship_effect="trust shifts",
            voice_rules={"vocabulary_style": "precise"},
        ),
        DialogueBeat(
            dialogue_beat_id="dialogue_scene_dialogue_lines_02_choice",
            scene_id="scene_dialogue_lines",
            speaker_id="char_kael",
            listener_ids=["char_seren"],
            surface_meaning="Kael demands clarity.",
            hidden_meaning="He needs her to choose him or the secret.",
            subtext="hurt disguised as proof",
            emotion="resolve",
            secret_risk=0.35,
            relationship_effect="resentment rises",
            voice_rules={"vocabulary_style": "plain_defensive"},
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
            betrayal_risk=0.7,
            turning_point="Evidence changes trust.",
            expected_end_state_shift={"trust_delta": -0.05, "resentment_delta": 0.08},
        )
    ]


def test_dialogue_line_generator_builds_dialogue_block():
    engine = DialogueLineGenerator()

    result = engine.generate_dialogue_block(
        blueprint=build_blueprint(),
        scene_draft=build_scene_draft(),
        dialogue_beats=build_dialogue_beats(),
        relationship_beats=build_relationship_beats(),
        prose_style_profile={"selected_format": "scene"},
        story_context={},
    )

    block = result["dialogue_block"]

    assert result["success"] is True
    assert block.dialogue_block_id == "dialogue_block_scene_dialogue_lines"
    assert len(block.lines) == 2
    assert block.rendered_text
    assert "char_seren" in block.used_speaker_ids


def test_dialogue_line_generator_preserves_subtext_and_risk():
    engine = DialogueLineGenerator()

    block = engine.generate_dialogue_block(
        blueprint=build_blueprint(),
        scene_draft=build_scene_draft(),
        dialogue_beats=build_dialogue_beats(),
        relationship_beats=build_relationship_beats(),
        prose_style_profile={"selected_format": "scene"},
        story_context={},
    )["dialogue_block"]

    first = block.lines[0]

    assert first.subtext == "guilt under control"
    assert first.hidden_meaning == "She protects the source."
    assert first.secret_risk == 0.85
    assert first.relationship_effect == "trust shifts"


def test_dialogue_line_generator_merges_dialogue_into_draft():
    engine = DialogueLineGenerator()

    block = engine.generate_dialogue_block(
        blueprint=build_blueprint(),
        scene_draft=build_scene_draft(),
        dialogue_beats=build_dialogue_beats(),
        relationship_beats=build_relationship_beats(),
        prose_style_profile={"selected_format": "scene"},
        story_context={},
    )["dialogue_block"]

    result = engine.merge_dialogue_into_draft(
        scene_draft=build_scene_draft(),
        dialogue_block=block,
    )

    draft = result["scene_draft"]

    assert result["success"] is True
    assert block.rendered_text in draft.draft_text
    assert "char_seren" in draft.used_character_ids
    assert any(section["beat_type"] == "generated_dialogue_block" for section in draft.sections)


def test_dialogue_line_generator_validates_block():
    engine = DialogueLineGenerator()

    block = engine.generate_dialogue_block(
        blueprint=build_blueprint(),
        scene_draft=build_scene_draft(),
        dialogue_beats=build_dialogue_beats(),
        relationship_beats=build_relationship_beats(),
        prose_style_profile={"selected_format": "scene"},
        story_context={},
    )["dialogue_block"]

    validation = engine.validate_dialogue_block(dialogue_block=block)

    assert validation["success"] is True
    assert validation["valid"] is True
    assert "dialogue_block_id_present" in validation["passed_checks"]
    assert "dialogue_lines_present" in validation["passed_checks"]
    assert "subtext_preserved" in validation["passed_checks"]
    assert "secret_risk_preserved" in validation["passed_checks"]


def test_dialogue_line_generator_summarizes_block():
    engine = DialogueLineGenerator()

    block = engine.generate_dialogue_block(
        blueprint=build_blueprint(),
        scene_draft=build_scene_draft(),
        dialogue_beats=build_dialogue_beats(),
        relationship_beats=build_relationship_beats(),
        prose_style_profile={"selected_format": "scene"},
        story_context={},
    )["dialogue_block"]

    summary = engine.summarize_dialogue_block(dialogue_block=block)

    assert summary["success"] is True
    assert summary["summary"]["line_count"] == 2
    assert summary["summary"]["speaker_count"] == 2
    assert summary["summary"]["average_secret_risk"] > 0.0


def test_dialogue_line_generator_supports_screenplay_rendering():
    engine = DialogueLineGenerator()

    block = engine.generate_dialogue_block(
        blueprint=build_blueprint(),
        scene_draft=build_scene_draft(),
        dialogue_beats=build_dialogue_beats(),
        relationship_beats=build_relationship_beats(),
        prose_style_profile={"selected_format": "screenplay"},
        story_context={},
    )["dialogue_block"]

    assert block.selected_format == "screenplay"
    assert "CHAR_SEREN" in block.rendered_text


def test_dialogue_line_generator_fallback_when_no_beats():
    engine = DialogueLineGenerator()

    block = engine.generate_dialogue_block(
        blueprint=build_blueprint(),
        scene_draft=build_scene_draft(),
        dialogue_beats=[],
        relationship_beats=[],
        prose_style_profile={"selected_format": "scene"},
        story_context={},
    )["dialogue_block"]

    assert len(block.lines) == 1
    assert block.lines[0].dialogue_beat_id == "fallback_dialogue_beat"
    assert any("fallback dialogue generated" in warning for warning in block.warnings)

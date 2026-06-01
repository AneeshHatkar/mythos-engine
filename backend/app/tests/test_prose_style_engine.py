from backend.app.engines.story_generation.prose_style_engine import ProseStyleEngine
from backend.app.schemas.story_generation import (
    CharacterVoiceInstruction,
    ConstraintSatisfactionReport,
    DialogueBeat,
    GenerationContract,
    HandoffReference,
    SceneBeat,
    SceneBlueprint,
    StoryFormat,
)


def build_contract():
    return GenerationContract(
        generation_contract_id="contract_style",
        story_intent_id="intent_style",
        handoff_reference=HandoffReference(simulation_id="sim_style"),
        allowed_formats=[StoryFormat.scene],
        selected_format=StoryFormat.scene,
        required_character_ids=["char_kael", "char_seren"],
        tone_contract={
            "tone_tags": ["tense", "dark"],
            "genres": ["dark_academy"],
            "dialogue_density": 0.6,
        },
        format_contract={"selected_format": "scene", "requires_ending_hook": True},
        quality_thresholds={"overall_score": 0.7},
        originality_rules={"forbidden_elements": ["cheesy"], "no_raw_source_text": True},
        validation_required=True,
        provenance_required=True,
    )


def build_blueprint():
    return SceneBlueprint(
        blueprint_id="blueprint_style",
        scene_id="scene_style",
        scene_purpose="Pressure Kael and Seren in the Oath Court.",
        pov_character_id="char_kael",
        active_character_ids=["char_kael", "char_seren"],
        location_id="location_court",
        scene_objective="Kael must confront the court with proof.",
        stakes=["Public proof changes legal rank."],
        secret_pressure=["char_kael lacks required secret knowledge."],
        relationship_pressure=["rel_kael_seren pressure"],
        emotional_turn="Seren's guilt must leak.",
        tension_curve=[0.3, 0.5, 0.8, 0.9],
        ending_hook="The pressure becomes harder to hide.",
        required_world_details=["Oath Court", "public proof changes legal rank"],
    )


def build_scene_beats():
    return [
        SceneBeat(
            beat_id="beat_style",
            scene_id="scene_style",
            beat_index=1,
            beat_type="setup",
            purpose="Create pressure in the Oath Court.",
            character_ids=["char_kael", "char_seren"],
            emotional_state={"char_seren:guilt": 0.8},
            causal_links=["cause_trial_reveal"],
            tension_value=0.8,
        )
    ]


def build_dialogue_beats():
    return [
        DialogueBeat(
            dialogue_beat_id="dialogue_style",
            scene_id="scene_style",
            speaker_id="char_seren",
            listener_ids=["char_kael"],
            surface_meaning="Seren avoids the answer.",
            hidden_meaning="She hides the source.",
            subtext="guilt under control",
            emotion="guilt",
            secret_risk=0.7,
        )
        for _ in range(5)
    ]


def build_voice_instructions():
    return [
        CharacterVoiceInstruction(
            character_id="char_kael",
            formality=0.6,
            sentence_length="medium",
            vocabulary_style="plain_defensive",
            rhythm="steady",
            power_behavior="claims power by naming facts",
            silence_behavior="silence signals withheld information",
        ),
        CharacterVoiceInstruction(
            character_id="char_seren",
            formality=0.75,
            sentence_length="short",
            vocabulary_style="precise",
            rhythm="controlled_with_breaks",
            power_behavior="keeps power by withholding emotional truth",
            silence_behavior="pauses before truthful words",
        ),
    ]


def build_constraint_report(satisfied=True):
    return ConstraintSatisfactionReport(
        report_id="constraint_report_style",
        satisfied=satisfied,
        required_characters_present=True,
        forbidden_elements_avoided=True,
        requested_format_followed=True,
        requested_tone_followed=True,
        emotional_beats_included=True,
        relationship_beats_included=True,
        ending_hook_included=True,
        knowledge_rules_obeyed=True,
        failed_constraints=[] if satisfied else ["knowledge boundary report is invalid"],
        warnings=[],
    )


def build_story_context():
    return {
        "emotional_pressure": [
            {
                "character_id": "char_seren",
                "dominant_emotion": "guilt",
                "dominant_intensity": 0.85,
            }
        ]
    }


def build_world_detail_pack():
    return {
        "specificity_score": 0.85,
        "sensory_detail_hints": ["Use silence in the Oath Court."],
        "law_and_rule_anchors": [{"detail": "public proof changes legal rank"}],
    }


def test_prose_style_engine_builds_profile():
    engine = ProseStyleEngine()

    result = engine.build_prose_style_profile(
        contract=build_contract(),
        blueprint=build_blueprint(),
        scene_beats=build_scene_beats(),
        dialogue_beats=build_dialogue_beats(),
        voice_instructions=build_voice_instructions(),
        constraint_report=build_constraint_report(),
        story_context=build_story_context(),
        world_detail_pack=build_world_detail_pack(),
    )

    profile = result["prose_style_profile"]

    assert result["success"] is True
    assert profile["prose_style_profile_id"] == "prose_style_scene_style"
    assert profile["selected_format"] == "scene"
    assert "tense" in profile["tone_tags"]
    assert profile["style_specificity_score"] >= 0.8


def test_prose_style_engine_builds_world_voice_and_emotion_rules():
    engine = ProseStyleEngine()

    profile = engine.build_prose_style_profile(
        contract=build_contract(),
        blueprint=build_blueprint(),
        scene_beats=build_scene_beats(),
        dialogue_beats=build_dialogue_beats(),
        voice_instructions=build_voice_instructions(),
        story_context=build_story_context(),
        world_detail_pack=build_world_detail_pack(),
    )["prose_style_profile"]

    assert any("Oath Court" in item for item in profile["world_detail_usage_rules"])
    assert any("char_seren" in item for item in profile["character_voice_usage_rules"])
    assert any("guilt" in item for item in profile["emotional_rendering_rules"])


def test_prose_style_engine_tracks_generic_phrase_bans():
    engine = ProseStyleEngine()

    profile = engine.build_prose_style_profile(
        contract=build_contract(),
        blueprint=build_blueprint(),
        scene_beats=build_scene_beats(),
        dialogue_beats=build_dialogue_beats(),
        voice_instructions=build_voice_instructions(),
    )["prose_style_profile"]

    assert "heart skipped a beat" in profile["generic_phrase_bans"]
    assert "cheesy" in profile["generic_phrase_bans"]


def test_prose_style_engine_builds_style_prompt_payload():
    engine = ProseStyleEngine()

    profile = engine.build_prose_style_profile(
        contract=build_contract(),
        blueprint=build_blueprint(),
        scene_beats=build_scene_beats(),
        dialogue_beats=build_dialogue_beats(),
        voice_instructions=build_voice_instructions(),
        story_context=build_story_context(),
        world_detail_pack=build_world_detail_pack(),
    )["prose_style_profile"]

    result = engine.build_style_prompt_payload(prose_style_profile=profile)
    payload = result["style_prompt_payload"]

    assert result["success"] is True
    assert payload["format"] == "scene"
    assert payload["must_do"]
    assert payload["must_avoid"]
    assert payload["voice_rules"]


def test_prose_style_engine_validates_profile():
    engine = ProseStyleEngine()

    profile = engine.build_prose_style_profile(
        contract=build_contract(),
        blueprint=build_blueprint(),
        scene_beats=build_scene_beats(),
        dialogue_beats=build_dialogue_beats(),
        voice_instructions=build_voice_instructions(),
        story_context=build_story_context(),
        world_detail_pack=build_world_detail_pack(),
    )["prose_style_profile"]

    validation = engine.validate_prose_style_profile(prose_style_profile=profile)

    assert validation["success"] is True
    assert validation["valid"] is True
    assert "prose_style_profile_id_present" in validation["passed_checks"]
    assert "format_rules_present" in validation["passed_checks"]
    assert "style_specificity_usable" in validation["passed_checks"]


def test_prose_style_engine_summarizes_profile():
    engine = ProseStyleEngine()

    profile = engine.build_prose_style_profile(
        contract=build_contract(),
        blueprint=build_blueprint(),
        scene_beats=build_scene_beats(),
        dialogue_beats=build_dialogue_beats(),
        voice_instructions=build_voice_instructions(),
        story_context=build_story_context(),
        world_detail_pack=build_world_detail_pack(),
    )["prose_style_profile"]

    summary = engine.summarize_prose_style_profile(prose_style_profile=profile)

    assert summary["success"] is True
    assert summary["summary"]["selected_format"] == "scene"
    assert summary["summary"]["tone_count"] == 2
    assert summary["summary"]["generic_phrase_ban_count"] >= 5
    assert summary["summary"]["voice_rule_count"] >= 2


def test_prose_style_engine_warns_when_constraints_unsatisfied():
    engine = ProseStyleEngine()

    profile = engine.build_prose_style_profile(
        contract=build_contract(),
        blueprint=build_blueprint(),
        scene_beats=build_scene_beats(),
        dialogue_beats=build_dialogue_beats(),
        voice_instructions=[],
        constraint_report=build_constraint_report(satisfied=False),
        story_context={},
        world_detail_pack={},
    )["prose_style_profile"]

    assert any("Constraint report is not satisfied" in warning for warning in profile["warnings"])
    assert profile["revision_pressure"]["needs_repair_before_draft"] is True

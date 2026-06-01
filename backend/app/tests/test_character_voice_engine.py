from backend.app.engines.story_generation.character_voice_engine import CharacterVoiceEngine
from backend.app.schemas.story_generation import DialogueBeat


def build_active_cast():
    return [
        {
            "character_id": "char_kael",
            "display_name": "Kael",
            "required": True,
            "voice_profile": {"style": "guarded"},
            "emotional_state": {"resolve": 0.8, "shame": 0.7},
            "role_tags": ["protagonist"],
            "story_function_tags": ["drive_plot"],
        },
        {
            "character_id": "char_seren",
            "display_name": "Seren",
            "required": False,
            "voice_profile": {"style": "controlled"},
            "emotional_state": {"guilt": 0.8},
            "role_tags": ["love_interest"],
            "story_function_tags": ["anchor_romance"],
        },
    ]


def build_dialogue_beats():
    return [
        DialogueBeat(
            dialogue_beat_id="dialogue_001",
            scene_id="scene_001",
            speaker_id="char_kael",
            listener_ids=["char_seren"],
            surface_meaning="Kael presses the evidence.",
            hidden_meaning="He wants Seren to admit she knew.",
            subtext="hurt disguised as proof",
            emotion="resolve",
            secret_risk=0.4,
            power_shift="power shifts through evidence",
            relationship_effect="trust moves under pressure",
        ),
        DialogueBeat(
            dialogue_beat_id="dialogue_002",
            scene_id="scene_001",
            speaker_id="char_seren",
            listener_ids=["char_kael"],
            surface_meaning="Seren avoids the direct answer.",
            hidden_meaning="She protects her source.",
            subtext="guilt hidden under control",
            emotion="guilt",
            secret_risk=0.85,
            power_shift="power shifts toward whoever knows more",
            relationship_effect="resentment rises",
        ),
    ]


def test_character_voice_engine_builds_instructions():
    engine = CharacterVoiceEngine()

    result = engine.build_voice_instructions(
        active_cast=build_active_cast(),
        dialogue_beats=build_dialogue_beats(),
        story_context={},
    )

    instructions = result["voice_instructions"]

    assert result["success"] is True
    assert len(instructions) == 2
    assert instructions[0].character_id == "char_kael"
    assert instructions[1].character_id == "char_seren"


def test_character_voice_engine_creates_distinct_voice_rules():
    engine = CharacterVoiceEngine()

    instructions = engine.build_voice_instructions(
        active_cast=build_active_cast(),
        dialogue_beats=build_dialogue_beats(),
    )["voice_instructions"]

    kael = next(item for item in instructions if item.character_id == "char_kael")
    seren = next(item for item in instructions if item.character_id == "char_seren")

    assert kael.vocabulary_style == "plain_defensive"
    assert seren.vocabulary_style == "precise"
    assert seren.rhythm == "controlled_with_breaks"
    assert "almost-confessions" in seren.romance_behavior
    assert kael.power_behavior == "claims power by naming facts"


def test_character_voice_engine_applies_voice_to_dialogue_beats():
    engine = CharacterVoiceEngine()

    instructions = engine.build_voice_instructions(
        active_cast=build_active_cast(),
        dialogue_beats=build_dialogue_beats(),
    )["voice_instructions"]

    result = engine.apply_voice_to_dialogue_beats(
        dialogue_beats=build_dialogue_beats(),
        voice_instructions=instructions,
    )

    updated = result["dialogue_beats"]

    assert result["success"] is True
    assert updated[0].voice_rules["source"] == "character_voice_engine"
    assert updated[0].voice_rules["vocabulary_style"] == "plain_defensive"
    assert updated[1].voice_rules["vocabulary_style"] == "precise"


def test_character_voice_engine_validates_instructions():
    engine = CharacterVoiceEngine()

    instructions = engine.build_voice_instructions(
        active_cast=build_active_cast(),
        dialogue_beats=build_dialogue_beats(),
    )["voice_instructions"]

    validation = engine.validate_voice_instructions(voice_instructions=instructions)

    assert validation["success"] is True
    assert validation["valid"] is True
    assert "voice_instructions_present" in validation["passed_checks"]
    assert "character_ids_present" in validation["passed_checks"]
    assert "voice_distinctiveness_usable" in validation["passed_checks"]


def test_character_voice_engine_summarizes_instructions():
    engine = CharacterVoiceEngine()

    instructions = engine.build_voice_instructions(
        active_cast=build_active_cast(),
        dialogue_beats=build_dialogue_beats(),
    )["voice_instructions"]

    summary = engine.summarize_voice_instructions(voice_instructions=instructions)

    assert summary["success"] is True
    assert summary["summary"]["voice_instruction_count"] == 2
    assert "char_kael" in summary["summary"]["character_ids"]
    assert "plain_defensive" in summary["summary"]["vocabulary_styles"]
    assert summary["summary"]["average_distinctiveness"] > 0.5


def test_character_voice_engine_warns_on_weak_voice():
    engine = CharacterVoiceEngine()

    result = engine.build_voice_instructions(
        active_cast=[{"character_id": "char_blank"}],
        dialogue_beats=[],
    )

    assert result["success"] is True
    assert any("Low voice distinctiveness" in warning for warning in result["warnings"])

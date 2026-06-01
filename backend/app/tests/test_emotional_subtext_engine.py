from backend.app.engines.story_generation.character_voice_engine import CharacterVoiceEngine
from backend.app.engines.story_generation.emotional_subtext_engine import EmotionalSubtextEngine
from backend.app.schemas.story_generation import DialogueBeat


def build_active_cast():
    return [
        {
            "character_id": "char_kael",
            "display_name": "Kael",
            "voice_profile": {"style": "guarded"},
            "emotional_state": {"resolve": 0.8, "shame": 0.7},
            "role_tags": ["protagonist"],
        },
        {
            "character_id": "char_seren",
            "display_name": "Seren",
            "voice_profile": {"style": "controlled"},
            "emotional_state": {"guilt": 0.85},
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
            surface_meaning="Kael names the evidence.",
            hidden_meaning="He wants Seren to stop hiding.",
            subtext="hurt disguised as proof",
            emotion="resolve",
            secret_risk=0.35,
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


def build_voice_instructions():
    return CharacterVoiceEngine().build_voice_instructions(
        active_cast=build_active_cast(),
        dialogue_beats=build_dialogue_beats(),
    )["voice_instructions"]


def test_emotional_subtext_engine_builds_instructions():
    engine = EmotionalSubtextEngine()

    result = engine.build_emotional_subtext(
        active_cast=build_active_cast(),
        voice_instructions=build_voice_instructions(),
        dialogue_beats=build_dialogue_beats(),
    )

    instructions = result["emotional_subtext_instructions"]

    assert result["success"] is True
    assert len(instructions) == 2
    assert {item.character_id for item in instructions} == {"char_kael", "char_seren"}


def test_emotional_subtext_engine_detects_dominant_emotions():
    engine = EmotionalSubtextEngine()

    instructions = engine.build_emotional_subtext(
        active_cast=build_active_cast(),
        voice_instructions=build_voice_instructions(),
        dialogue_beats=build_dialogue_beats(),
    )["emotional_subtext_instructions"]

    kael = next(item for item in instructions if item.character_id == "char_kael")
    seren = next(item for item in instructions if item.character_id == "char_seren")

    assert kael.dominant_emotion == "resolve"
    assert seren.dominant_emotion == "guilt"
    assert seren.intensity == 0.85


def test_emotional_subtext_engine_creates_behavioral_hints():
    engine = EmotionalSubtextEngine()

    instructions = engine.build_emotional_subtext(
        active_cast=build_active_cast(),
        voice_instructions=build_voice_instructions(),
        dialogue_beats=build_dialogue_beats(),
    )["emotional_subtext_instructions"]

    seren = next(item for item in instructions if item.character_id == "char_seren")

    assert seren.body_language_hints
    assert seren.dialogue_pressure_hints
    assert seren.internal_narration_hints
    assert seren.emotional_leakage_rules
    assert any("truth" in hint.lower() or "direct" in hint.lower() for hint in seren.dialogue_pressure_hints)


def test_emotional_subtext_engine_applies_to_dialogue_beats():
    engine = EmotionalSubtextEngine()

    subtext = engine.build_emotional_subtext(
        active_cast=build_active_cast(),
        voice_instructions=build_voice_instructions(),
        dialogue_beats=build_dialogue_beats(),
    )["emotional_subtext_instructions"]

    result = engine.apply_subtext_to_dialogue_beats(
        dialogue_beats=build_dialogue_beats(),
        emotional_subtext=subtext,
    )

    updated = result["dialogue_beats"]

    assert result["success"] is True
    assert "emotional_subtext" in updated[0].voice_rules
    assert updated[1].voice_rules["emotional_subtext"]["dominant_emotion"] == "guilt"


def test_emotional_subtext_engine_validates_instructions():
    engine = EmotionalSubtextEngine()

    subtext = engine.build_emotional_subtext(
        active_cast=build_active_cast(),
        voice_instructions=build_voice_instructions(),
        dialogue_beats=build_dialogue_beats(),
    )["emotional_subtext_instructions"]

    validation = engine.validate_emotional_subtext(emotional_subtext=subtext)

    assert validation["success"] is True
    assert validation["valid"] is True
    assert "emotional_subtext_present" in validation["passed_checks"]
    assert "body_language_hints_present" in validation["passed_checks"]
    assert "dialogue_pressure_hints_present" in validation["passed_checks"]
    assert "emotion_intensities_bounded" in validation["passed_checks"]


def test_emotional_subtext_engine_summarizes_instructions():
    engine = EmotionalSubtextEngine()

    subtext = engine.build_emotional_subtext(
        active_cast=build_active_cast(),
        voice_instructions=build_voice_instructions(),
        dialogue_beats=build_dialogue_beats(),
    )["emotional_subtext_instructions"]

    summary = engine.summarize_emotional_subtext(emotional_subtext=subtext)

    assert summary["success"] is True
    assert summary["summary"]["instruction_count"] == 2
    assert summary["summary"]["emotion_counts"]["guilt"] == 1
    assert summary["summary"]["average_intensity"] > 0.7


def test_emotional_subtext_engine_warns_on_weak_signal():
    engine = EmotionalSubtextEngine()

    result = engine.build_emotional_subtext(
        active_cast=[{"character_id": "char_blank"}],
        voice_instructions=[],
        dialogue_beats=[],
    )

    assert result["success"] is True
    assert any("Weak emotional signal" in warning for warning in result["warnings"])

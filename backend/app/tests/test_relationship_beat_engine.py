from backend.app.engines.story_generation.relationship_beat_engine import RelationshipBeatEngine
from backend.app.schemas.story_generation import DialogueBeat, EmotionalSubtextInstruction, SceneBlueprint


def build_blueprint():
    return SceneBlueprint(
        blueprint_id="blueprint_relationship",
        scene_id="scene_relationship",
        scene_purpose="Pressure Kael and Seren through evidence.",
        pov_character_id="char_kael",
        active_character_ids=["char_kael", "char_seren"],
        location_id="location_court",
        scene_objective="Kael forces the court to face the truth.",
        relationship_pressure=[
            "rel_kael_seren has pressure=0.7 trust=0.3 resentment=0.5 betrayal_risk=0.7."
        ],
        secret_pressure=["char_kael lacks required secret knowledge: secret_seren_source."],
        ending_hook="Seren refuses to deny the evidence.",
    )


def build_story_context():
    return {
        "relationship_pressure": [
            {
                "relationship_id": "rel_kael_seren",
                "character_a_id": "char_kael",
                "character_b_id": "char_seren",
                "trust": 0.3,
                "resentment": 0.5,
                "romantic_tension": 0.4,
                "betrayal_risk": 0.7,
                "repair_potential": 0.2,
                "pressure_score": 0.7,
            }
        ],
        "knowledge_boundaries": [
            {
                "holder_id": "char_kael",
                "missing_required_secret_ids": ["secret_seren_source"],
                "forbidden_secret_reveals": [],
            },
            {
                "holder_id": "char_seren",
                "missing_required_secret_ids": [],
                "forbidden_secret_reveals": ["major_mystery_solution_until_planned_reveal"],
            },
        ],
    }


def build_dialogue_beats():
    return [
        DialogueBeat(
            dialogue_beat_id="dialogue_001",
            scene_id="scene_relationship",
            speaker_id="char_kael",
            listener_ids=["char_seren"],
            surface_meaning="Kael names the evidence.",
            hidden_meaning="He wants Seren to admit what she knew.",
            subtext="hurt disguised as proof",
            emotion="resolve",
            secret_risk=0.35,
            power_shift="power shifts through evidence",
            relationship_effect="trust moves under pressure",
        ),
        DialogueBeat(
            dialogue_beat_id="dialogue_002",
            scene_id="scene_relationship",
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


def build_emotional_subtext():
    return [
        EmotionalSubtextInstruction(
            character_id="char_kael",
            dominant_emotion="resolve",
            intensity=0.8,
            body_language_hints=["steady posture"],
            dialogue_pressure_hints=["names facts plainly"],
            internal_narration_hints=["narrows the world to action"],
            emotional_leakage_rules=["fear shows after decision"],
        ),
        EmotionalSubtextInstruction(
            character_id="char_seren",
            dominant_emotion="guilt",
            intensity=0.85,
            body_language_hints=["delayed eye contact"],
            dialogue_pressure_hints=["answers beside the truth"],
            internal_narration_hints=["measures every word"],
            emotional_leakage_rules=["truth leaks through pauses"],
        ),
    ]


def test_relationship_beat_engine_builds_relationship_beats():
    engine = RelationshipBeatEngine()

    result = engine.build_relationship_beats(
        blueprint=build_blueprint(),
        story_context=build_story_context(),
        dialogue_beats=build_dialogue_beats(),
        emotional_subtext=build_emotional_subtext(),
    )

    beats = result["relationship_beats"]

    assert result["success"] is True
    assert len(beats) == 1
    assert beats[0].relationship_id == "rel_kael_seren"
    assert beats[0].character_a_id == "char_kael"
    assert beats[0].character_b_id == "char_seren"


def test_relationship_beat_engine_tracks_relationship_metrics():
    engine = RelationshipBeatEngine()

    beat = engine.build_relationship_beats(
        blueprint=build_blueprint(),
        story_context=build_story_context(),
        dialogue_beats=build_dialogue_beats(),
        emotional_subtext=build_emotional_subtext(),
    )["relationship_beats"][0]

    assert beat.starting_trust == 0.3
    assert beat.starting_resentment == 0.5
    assert beat.romantic_tension == 0.4
    assert beat.betrayal_risk == 0.7
    assert beat.repair_potential >= 0.4
    assert beat.power_imbalance > 0.0


def test_relationship_beat_engine_tracks_knowledge_asymmetry():
    engine = RelationshipBeatEngine()

    beat = engine.build_relationship_beats(
        blueprint=build_blueprint(),
        story_context=build_story_context(),
        dialogue_beats=build_dialogue_beats(),
        emotional_subtext=build_emotional_subtext(),
    )["relationship_beats"][0]

    assert any("char_kael does not know secret_seren_source" in item for item in beat.knowledge_asymmetry)
    assert any("char_seren must not reveal" in item for item in beat.knowledge_asymmetry)


def test_relationship_beat_engine_creates_turning_point_and_shift():
    engine = RelationshipBeatEngine()

    beat = engine.build_relationship_beats(
        blueprint=build_blueprint(),
        story_context=build_story_context(),
        dialogue_beats=build_dialogue_beats(),
        emotional_subtext=build_emotional_subtext(),
    )["relationship_beats"][0]

    assert "Betrayal risk" in beat.turning_point
    assert beat.expected_end_state_shift["resentment_delta"] > 0
    assert beat.expected_end_state_shift["repair_potential_delta"] > 0


def test_relationship_beat_engine_applies_relationship_to_dialogue():
    engine = RelationshipBeatEngine()

    relationship_beats = engine.build_relationship_beats(
        blueprint=build_blueprint(),
        story_context=build_story_context(),
        dialogue_beats=build_dialogue_beats(),
        emotional_subtext=build_emotional_subtext(),
    )["relationship_beats"]

    result = engine.apply_relationship_beats_to_dialogue(
        dialogue_beats=build_dialogue_beats(),
        relationship_beats=relationship_beats,
    )

    updated = result["dialogue_beats"]

    assert result["success"] is True
    assert updated[0].voice_rules["relationship_beat"]["relationship_id"] == "rel_kael_seren"
    assert updated[1].voice_rules["relationship_beat"]["expected_end_state_shift"]


def test_relationship_beat_engine_validates_relationship_beats():
    engine = RelationshipBeatEngine()

    beats = engine.build_relationship_beats(
        blueprint=build_blueprint(),
        story_context=build_story_context(),
        dialogue_beats=build_dialogue_beats(),
        emotional_subtext=build_emotional_subtext(),
    )["relationship_beats"]

    validation = engine.validate_relationship_beats(relationship_beats=beats)

    assert validation["success"] is True
    assert validation["valid"] is True
    assert "relationship_beats_present" in validation["passed_checks"]
    assert "turning_points_present" in validation["passed_checks"]
    assert "expected_end_state_shift_present" in validation["passed_checks"]
    assert "knowledge_asymmetry_tracked" in validation["passed_checks"]


def test_relationship_beat_engine_summarizes_relationship_beats():
    engine = RelationshipBeatEngine()

    beats = engine.build_relationship_beats(
        blueprint=build_blueprint(),
        story_context=build_story_context(),
        dialogue_beats=build_dialogue_beats(),
        emotional_subtext=build_emotional_subtext(),
    )["relationship_beats"]

    summary = engine.summarize_relationship_beats(relationship_beats=beats)

    assert summary["success"] is True
    assert summary["summary"]["relationship_beat_count"] == 1
    assert summary["summary"]["average_betrayal_risk"] == 0.7
    assert summary["summary"]["turning_point_count"] == 1


def test_relationship_beat_engine_fallback_when_no_relationship_context():
    engine = RelationshipBeatEngine()

    result = engine.build_relationship_beats(
        blueprint=build_blueprint(),
        story_context={"knowledge_boundaries": []},
        dialogue_beats=[],
        emotional_subtext=[],
    )

    beats = result["relationship_beats"]

    assert result["success"] is True
    assert len(beats) == 1
    assert beats[0].relationship_id == "rel_char_kael_char_seren"
    assert beats[0].turning_point

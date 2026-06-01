from backend.app.engines.story_generation.dialogue_beat_engine import DialogueBeatEngine
from backend.app.engines.story_generation.scene_beat_planner import SceneBeatPlanner
from backend.app.schemas.story_generation import SceneBlueprint


def build_blueprint():
    return SceneBlueprint(
        blueprint_id="blueprint_dialogue",
        scene_id="scene_dialogue",
        scene_purpose="Force a truth into the open.",
        opening_image="Oath Court: silence under witness tiers.",
        pov_character_id="char_kael",
        active_character_ids=["char_kael", "char_seren"],
        location_id="location_court",
        scene_objective="Kael must prove the badge was altered.",
        opposition="Seren's silence creates opposition.",
        stakes=["Public proof changes legal rank."],
        secret_pressure=["char_kael lacks required secret knowledge: secret_seren_source."],
        relationship_pressure=["rel_kael_seren has pressure=0.7 trust=0.3 resentment=0.5 betrayal_risk=0.7."],
        emotional_turn="char_seren's guilt must leak under pressure.",
        tension_curve=[0.3, 0.5, 0.75, 0.9],
        ending_hook="End with the secret pressure becoming harder to hide.",
        required_world_details=["Oath Court", "cracked badge"],
    )


def build_story_context():
    return {
        "active_cast": [
            {
                "character_id": "char_kael",
                "display_name": "Kael",
                "required": True,
                "voice_profile": {"style": "guarded"},
            },
            {
                "character_id": "char_seren",
                "display_name": "Seren",
                "required": False,
                "voice_profile": {"style": "controlled"},
            },
        ],
        "emotional_pressure": [
            {
                "character_id": "char_seren",
                "dominant_emotion": "guilt",
                "dominant_intensity": 0.8,
            }
        ],
        "relationship_pressure": [
            {
                "relationship_id": "rel_kael_seren",
                "pressure_score": 0.7,
            }
        ],
        "causal_obligations": [
            {"obligation_type": "causal_node", "id": "cause_trial_reveal"},
            {"obligation_type": "consequence", "id": "cons_reputation_shift"},
        ],
    }


def build_scene_beats():
    planner = SceneBeatPlanner()
    return planner.build_scene_beats(
        blueprint=build_blueprint(),
        story_context=build_story_context(),
        world_detail_pack={"format_specific_world_notes": []},
    )["scene_beats"]


def test_dialogue_beat_engine_builds_dialogue_beats():
    engine = DialogueBeatEngine()

    result = engine.build_dialogue_beats(
        blueprint=build_blueprint(),
        scene_beats=build_scene_beats(),
        story_context=build_story_context(),
    )

    beats = result["dialogue_beats"]

    assert result["success"] is True
    assert len(beats) >= 4
    assert beats[0].scene_id == "scene_dialogue"
    assert beats[0].speaker_id in {"char_kael", "char_seren"}
    assert beats[0].listener_ids
    assert beats[0].surface_meaning


def test_dialogue_beat_engine_tracks_secret_risk_and_subtext():
    engine = DialogueBeatEngine()

    beats = engine.build_dialogue_beats(
        blueprint=build_blueprint(),
        scene_beats=build_scene_beats(),
        story_context=build_story_context(),
    )["dialogue_beats"]

    secret_beats = [beat for beat in beats if beat.secret_risk > 0]

    assert secret_beats
    assert any(beat.subtext for beat in beats)
    assert any("secret" in (beat.hidden_meaning or "").lower() for beat in beats)


def test_dialogue_beat_engine_tracks_relationship_effects():
    engine = DialogueBeatEngine()

    beats = engine.build_dialogue_beats(
        blueprint=build_blueprint(),
        scene_beats=build_scene_beats(),
        story_context=build_story_context(),
    )["dialogue_beats"]

    assert any(beat.relationship_effect for beat in beats)
    assert any(beat.power_shift for beat in beats)


def test_dialogue_beat_engine_uses_voice_profile_placeholder():
    engine = DialogueBeatEngine()

    beats = engine.build_dialogue_beats(
        blueprint=build_blueprint(),
        scene_beats=build_scene_beats(),
        story_context=build_story_context(),
    )["dialogue_beats"]

    assert any(beat.voice_rules.get("source") == "character_voice_profile" for beat in beats)


def test_dialogue_beat_engine_validates_dialogue_beats():
    engine = DialogueBeatEngine()
    blueprint = build_blueprint()

    beats = engine.build_dialogue_beats(
        blueprint=blueprint,
        scene_beats=build_scene_beats(),
        story_context=build_story_context(),
    )["dialogue_beats"]

    validation = engine.validate_dialogue_beats(
        dialogue_beats=beats,
        blueprint=blueprint,
    )

    assert validation["success"] is True
    assert validation["valid"] is True
    assert "dialogue_beats_present" in validation["passed_checks"]
    assert "speakers_present" in validation["passed_checks"]
    assert "subtext_present" in validation["passed_checks"]
    assert "secret_risk_tracked" in validation["passed_checks"]


def test_dialogue_beat_engine_summarizes_dialogue_beats():
    engine = DialogueBeatEngine()

    beats = engine.build_dialogue_beats(
        blueprint=build_blueprint(),
        scene_beats=build_scene_beats(),
        story_context=build_story_context(),
    )["dialogue_beats"]

    summary = engine.summarize_dialogue_beats(dialogue_beats=beats)

    assert summary["success"] is True
    assert summary["summary"]["dialogue_beat_count"] == len(beats)
    assert summary["summary"]["average_secret_risk"] >= 0.0
    assert summary["summary"]["subtext_count"] >= 1
    assert summary["summary"]["relationship_effect_count"] >= 1


def test_dialogue_beat_engine_warns_with_single_character():
    engine = DialogueBeatEngine()
    blueprint = SceneBlueprint(
        blueprint_id="blueprint_single",
        scene_id="scene_single",
        scene_purpose="Internal choice.",
        pov_character_id="char_kael",
        active_character_ids=["char_kael"],
        scene_objective="Kael chooses whether to reveal proof.",
        secret_pressure=["char_kael must not reveal everything."],
        relationship_pressure=[],
        tension_curve=[0.2, 0.4, 0.6],
    )

    scene_beats = SceneBeatPlanner().build_scene_beats(
        blueprint=blueprint,
        story_context={"emotional_pressure": [], "causal_obligations": []},
        world_detail_pack={},
    )["scene_beats"]

    result = engine.build_dialogue_beats(
        blueprint=blueprint,
        scene_beats=scene_beats,
        story_context={"active_cast": [{"character_id": "char_kael"}], "emotional_pressure": []},
    )

    assert any("Only one active character" in warning for warning in result["warnings"])

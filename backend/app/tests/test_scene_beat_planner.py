from backend.app.engines.story_generation.scene_beat_planner import SceneBeatPlanner
from backend.app.schemas.story_generation import SceneBlueprint


def build_blueprint():
    return SceneBlueprint(
        blueprint_id="blueprint_scene_trial",
        scene_id="scene_trial",
        scene_purpose="Force Kael to expose evidence in the Oath Court.",
        opening_image="Oath Court: Use silence to show social pressure.",
        pov_character_id="char_kael",
        active_character_ids=["char_kael", "char_seren"],
        location_id="location_court",
        scene_objective="Kael must prove the ranking fraud.",
        opposition="Seren's silence creates opposition.",
        stakes=["Public proof changes legal rank."],
        secret_pressure=["char_kael lacks required secret knowledge: secret_seren_source."],
        relationship_pressure=["rel_kael_seren has pressure=0.7 trust=0.3 resentment=0.5 betrayal_risk=0.7."],
        emotional_turn="char_seren's guilt must leak under pressure.",
        tension_curve=[0.3, 0.5, 0.75, 0.9],
        ending_hook="End with the secret pressure becoming harder to hide.",
        required_world_details=[
            "In the Oath Court, public proof changes legal rank.",
            "Oath Court",
            "The cracked badge can act as evidence.",
        ],
    )


def build_story_context():
    return {
        "emotional_pressure": [
            {
                "character_id": "char_seren",
                "dominant_emotion": "guilt",
                "dominant_intensity": 0.8,
            }
        ],
        "causal_obligations": [
            {"obligation_type": "causal_node", "id": "cause_trial_reveal"},
            {"obligation_type": "consequence", "id": "cons_reputation_shift"},
        ],
    }


def build_world_detail_pack():
    return {
        "world_detail_pack_id": "worlddetails_scene_trial",
        "format_specific_world_notes": ["World details may appear through social pressure."],
    }


def test_scene_beat_planner_builds_ordered_beats():
    planner = SceneBeatPlanner()

    result = planner.build_scene_beats(
        blueprint=build_blueprint(),
        story_context=build_story_context(),
        world_detail_pack=build_world_detail_pack(),
    )

    beats = result["scene_beats"]

    assert result["success"] is True
    assert len(beats) >= 7
    assert beats[0].beat_type == "setup"
    assert beats[-1].beat_type == "ending_hook"
    assert [beat.beat_index for beat in beats] == list(range(1, len(beats) + 1))


def test_scene_beat_planner_includes_pressure_beats():
    planner = SceneBeatPlanner()

    beats = planner.build_scene_beats(
        blueprint=build_blueprint(),
        story_context=build_story_context(),
        world_detail_pack=build_world_detail_pack(),
    )["scene_beats"]

    beat_types = [beat.beat_type for beat in beats]

    assert "world_pressure" in beat_types
    assert "relationship_pressure" in beat_types
    assert "secret_pressure" in beat_types
    assert "dialogue_pressure" in beat_types
    assert "choice" in beat_types
    assert "consequence" in beat_types


def test_scene_beat_planner_preserves_knowledge_and_causal_links():
    planner = SceneBeatPlanner()

    beats = planner.build_scene_beats(
        blueprint=build_blueprint(),
        story_context=build_story_context(),
        world_detail_pack=build_world_detail_pack(),
    )["scene_beats"]

    secret_beat = next(beat for beat in beats if beat.beat_type == "secret_pressure")
    consequence_beat = next(beat for beat in beats if beat.beat_type == "consequence")

    assert secret_beat.knowledge_constraints
    assert "cause_trial_reveal" in secret_beat.causal_links
    assert "cons_reputation_shift" in consequence_beat.causal_links


def test_scene_beat_planner_validates_beats():
    planner = SceneBeatPlanner()
    blueprint = build_blueprint()

    beats = planner.build_scene_beats(
        blueprint=blueprint,
        story_context=build_story_context(),
        world_detail_pack=build_world_detail_pack(),
    )["scene_beats"]

    validation = planner.validate_scene_beats(beats=beats, blueprint=blueprint)

    assert validation["success"] is True
    assert validation["valid"] is True
    assert "beats_present" in validation["passed_checks"]
    assert "choice_beat_present" in validation["passed_checks"]
    assert "consequence_beat_present" in validation["passed_checks"]
    assert "tension_values_bounded" in validation["passed_checks"]


def test_scene_beat_planner_summarizes_beats():
    planner = SceneBeatPlanner()

    beats = planner.build_scene_beats(
        blueprint=build_blueprint(),
        story_context=build_story_context(),
        world_detail_pack=build_world_detail_pack(),
    )["scene_beats"]

    summary = planner.summarize_beats(beats=beats)

    assert summary["success"] is True
    assert summary["summary"]["beat_count"] == len(beats)
    assert summary["summary"]["average_tension"] > 0.0
    assert summary["summary"]["max_tension"] == 0.9
    assert summary["summary"]["causal_link_count"] >= 1


def test_scene_beat_planner_handles_minimal_blueprint():
    planner = SceneBeatPlanner()

    blueprint = SceneBlueprint(
        blueprint_id="blueprint_min",
        scene_id="scene_min",
        scene_purpose="Move the story.",
        pov_character_id="char_a",
        active_character_ids=["char_a"],
        scene_objective="char_a must choose.",
        stakes=[],
        tension_curve=[0.2, 0.4, 0.6],
        required_world_details=[],
    )

    result = planner.build_scene_beats(
        blueprint=blueprint,
        story_context={"emotional_pressure": [], "causal_obligations": []},
        world_detail_pack={},
    )

    beats = result["scene_beats"]
    beat_types = [beat.beat_type for beat in beats]

    assert "setup" in beat_types
    assert "choice" in beat_types
    assert "consequence" in beat_types
    assert "ending_hook" in beat_types

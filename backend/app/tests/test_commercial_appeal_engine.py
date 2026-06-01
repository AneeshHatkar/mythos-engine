from backend.app.engines.story_generation.commercial_appeal_engine import CommercialAppealEngine
from backend.app.schemas.story_generation import (
    DialogueBeat,
    GenerationContract,
    HandoffReference,
    RelationshipBeat,
    SceneBeat,
    SceneBlueprint,
    StoryFormat,
)


def build_contract():
    return GenerationContract(
        generation_contract_id="contract_commercial",
        story_intent_id="intent_commercial",
        handoff_reference=HandoffReference(simulation_id="sim_commercial"),
        allowed_formats=[StoryFormat.scene],
        selected_format=StoryFormat.scene,
        required_character_ids=["char_kael", "char_seren"],
        tone_contract={"tone_tags": ["tense"], "genres": ["dark_academy"]},
        format_contract={"selected_format": "scene"},
        quality_thresholds={"overall_score": 0.7},
        originality_rules={"no_raw_source_text": True},
    )


def build_blueprint():
    return SceneBlueprint(
        blueprint_id="blueprint_commercial",
        scene_id="scene_commercial",
        scene_purpose="Force proof into public view.",
        opening_image="Oath Court: silence under black witness tiers.",
        pov_character_id="char_kael",
        active_character_ids=["char_kael", "char_seren"],
        location_id="location_court",
        scene_objective="Kael must expose the cracked badge.",
        opposition="Seren's silence and the court's pressure oppose him.",
        stakes=["Public proof changes legal rank.", "If Kael fails, his exile becomes permanent."],
        secret_pressure=["char_kael lacks required secret knowledge: secret_seren_source."],
        relationship_pressure=["rel_kael_seren pressure"],
        emotional_turn="Seren's guilt must leak.",
        tension_curve=[0.3, 0.5, 0.8, 0.9],
        ending_hook="Seren refuses to deny the badge.",
        required_world_details=["Oath Court", "public proof changes legal rank", "cracked badge"],
    )


def build_scene_beats():
    return [
        SceneBeat(
            beat_id="beat_setup",
            scene_id="scene_commercial",
            beat_index=1,
            beat_type="setup",
            purpose="Set up court pressure.",
            character_ids=["char_kael", "char_seren"],
            emotional_state={"char_seren:guilt": 0.8},
            causal_links=["cause_trial_reveal"],
            tension_value=0.3,
        ),
        SceneBeat(
            beat_id="beat_choice",
            scene_id="scene_commercial",
            beat_index=2,
            beat_type="choice",
            purpose="Kael chooses to expose the badge.",
            character_ids=["char_kael"],
            causal_links=["cause_trial_reveal"],
            tension_value=0.8,
        ),
        SceneBeat(
            beat_id="beat_consequence",
            scene_id="scene_commercial",
            beat_index=3,
            beat_type="consequence",
            purpose="The court reacts.",
            character_ids=["char_kael", "char_seren"],
            causal_links=["cons_reputation_shift"],
            tension_value=0.9,
        ),
        SceneBeat(
            beat_id="beat_ending",
            scene_id="scene_commercial",
            beat_index=4,
            beat_type="ending_hook",
            purpose="Seren refuses to deny the badge.",
            character_ids=["char_kael", "char_seren"],
            causal_links=["cause_trial_reveal"],
            tension_value=0.9,
        ),
    ]


def build_dialogue_beats():
    return [
        DialogueBeat(
            dialogue_beat_id="dialogue_001",
            scene_id="scene_commercial",
            speaker_id="char_seren",
            listener_ids=["char_kael"],
            surface_meaning="Seren avoids the answer.",
            hidden_meaning="She hides the source.",
            subtext="guilt under control",
            emotion="guilt",
            secret_risk=0.8,
            relationship_effect="trust shifts",
        )
    ]


def build_relationship_beats():
    return [
        RelationshipBeat(
            relationship_id="rel_kael_seren",
            character_a_id="char_kael",
            character_b_id="char_seren",
            starting_trust=0.3,
            starting_resentment=0.5,
            romantic_tension=0.5,
            betrayal_risk=0.7,
            turning_point="Evidence changes trust.",
            expected_end_state_shift={"trust_delta": -0.05, "resentment_delta": 0.08},
        )
    ]


def build_story_context():
    return {
        "active_cast": [
            {
                "character_id": "char_kael",
                "display_name": "Kael",
                "goals": {"main": "prove the fraud"},
                "psychology": {"wound": "exile"},
                "voice_profile": {"style": "guarded"},
                "role_tags": ["protagonist"],
            },
            {
                "character_id": "char_seren",
                "display_name": "Seren",
                "voice_profile": {"style": "controlled"},
                "role_tags": ["love_interest"],
            },
        ],
        "emotional_pressure": [
            {"character_id": "char_seren", "dominant_emotion": "guilt", "dominant_intensity": 0.85}
        ],
    }


def build_world_detail_pack():
    return {
        "specificity_score": 0.85,
        "law_and_rule_anchors": [{"detail": "public proof changes legal rank"}],
        "ritual_anchors": [{"detail": "proof must be spoken before witness tiers"}],
        "sensory_detail_hints": ["Use silence in the Oath Court."],
    }


def build_prose_style_profile():
    return {
        "world_detail_usage_rules": ["Use Oath Court concretely."],
    }


def test_commercial_appeal_engine_scores_scene():
    engine = CommercialAppealEngine()

    result = engine.evaluate_commercial_appeal(
        contract=build_contract(),
        blueprint=build_blueprint(),
        scene_beats=build_scene_beats(),
        dialogue_beats=build_dialogue_beats(),
        relationship_beats=build_relationship_beats(),
        prose_style_profile=build_prose_style_profile(),
        story_context=build_story_context(),
        world_detail_pack=build_world_detail_pack(),
    )

    report = result["commercial_appeal_report"]

    assert result["success"] is True
    assert report.report_id == "commercial_report_scene_commercial"
    assert report.overall_score >= 0.65
    assert report.hook_strength >= 0.65
    assert report.world_uniqueness >= 0.65


def test_commercial_appeal_engine_builds_audience_positioning():
    engine = CommercialAppealEngine()

    result = engine.evaluate_commercial_appeal(
        contract=build_contract(),
        blueprint=build_blueprint(),
        scene_beats=build_scene_beats(),
        dialogue_beats=build_dialogue_beats(),
        relationship_beats=build_relationship_beats(),
        prose_style_profile=build_prose_style_profile(),
        story_context=build_story_context(),
        world_detail_pack=build_world_detail_pack(),
    )

    positioning = result["audience_positioning"]

    assert "dark academia / mystery readers" in positioning["likely_audience"]
    assert positioning["commercial_positioning_note"]


def test_commercial_appeal_engine_validates_report():
    engine = CommercialAppealEngine()

    report = engine.evaluate_commercial_appeal(
        contract=build_contract(),
        blueprint=build_blueprint(),
        scene_beats=build_scene_beats(),
        dialogue_beats=build_dialogue_beats(),
        relationship_beats=build_relationship_beats(),
        prose_style_profile=build_prose_style_profile(),
        story_context=build_story_context(),
        world_detail_pack=build_world_detail_pack(),
    )["commercial_appeal_report"]

    validation = engine.validate_commercial_appeal_report(report=report)

    assert validation["success"] is True
    assert validation["valid"] is True
    assert "scores_bounded" in validation["passed_checks"]
    assert "commercial_appeal_usable" in validation["passed_checks"]


def test_commercial_appeal_engine_builds_improvement_plan():
    engine = CommercialAppealEngine()

    weak_blueprint = SceneBlueprint(
        blueprint_id="blueprint_weak",
        scene_id="scene_weak",
        scene_purpose="A quiet generic scene.",
        active_character_ids=["char_a"],
        scene_objective="Talk.",
    )

    report = engine.evaluate_commercial_appeal(
        contract=build_contract(),
        blueprint=weak_blueprint,
        scene_beats=[],
        dialogue_beats=[],
        relationship_beats=[],
        story_context={},
        world_detail_pack={},
    )["commercial_appeal_report"]

    plan = engine.build_appeal_improvement_plan(report=report)

    assert plan["success"] is True
    assert plan["priority"] in {"medium", "high"}
    assert plan["suggestions"]
    assert plan["lowest_dimensions"]


def test_commercial_appeal_engine_summarizes_report():
    engine = CommercialAppealEngine()

    report = engine.evaluate_commercial_appeal(
        contract=build_contract(),
        blueprint=build_blueprint(),
        scene_beats=build_scene_beats(),
        dialogue_beats=build_dialogue_beats(),
        relationship_beats=build_relationship_beats(),
        prose_style_profile=build_prose_style_profile(),
        story_context=build_story_context(),
        world_detail_pack=build_world_detail_pack(),
    )["commercial_appeal_report"]

    summary = engine.summarize_commercial_appeal(report=report)

    assert summary["success"] is True
    assert summary["summary"]["report_id"] == "commercial_report_scene_commercial"
    assert summary["summary"]["overall_score"] >= 0.65
    assert summary["summary"]["draft_ready"] is True


def test_commercial_appeal_engine_gives_suggestions_for_weak_scene():
    engine = CommercialAppealEngine()

    weak_blueprint = SceneBlueprint(
        blueprint_id="blueprint_weak",
        scene_id="scene_weak",
        scene_purpose="A quiet generic scene.",
        active_character_ids=["char_a"],
        scene_objective="Talk.",
    )

    report = engine.evaluate_commercial_appeal(
        contract=build_contract(),
        blueprint=weak_blueprint,
        scene_beats=[],
        dialogue_beats=[],
        relationship_beats=[],
        story_context={},
        world_detail_pack={},
    )["commercial_appeal_report"]

    assert report.overall_score < 0.65
    assert report.improvement_suggestions

from backend.app.engines.story_generation.scene_draft_engine import SceneDraftEngine
from backend.app.schemas.story_generation import (
    CommercialAppealReport,
    DialogueBeat,
    RelationshipBeat,
    SceneBeat,
    SceneBlueprint,
)


def build_blueprint():
    return SceneBlueprint(
        blueprint_id="blueprint_draft",
        scene_id="scene_draft",
        scene_purpose="Force proof into public view.",
        opening_image="Oath Court: silence under black witness tiers.",
        pov_character_id="char_kael",
        active_character_ids=["char_kael", "char_seren"],
        location_id="location_court",
        scene_objective="Kael must expose the cracked badge.",
        stakes=["Public proof changes legal rank."],
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
            scene_id="scene_draft",
            beat_index=1,
            beat_type="setup",
            purpose="Set up court pressure.",
            character_ids=["char_kael", "char_seren"],
            emotional_state={"char_seren:guilt": 0.8},
            causal_links=["cause_trial_reveal"],
            tension_value=0.3,
        ),
        SceneBeat(
            beat_id="beat_secret",
            scene_id="scene_draft",
            beat_index=2,
            beat_type="secret_pressure",
            purpose="Keep secret_seren_source hidden.",
            character_ids=["char_kael", "char_seren"],
            knowledge_constraints=["char_kael does not know secret_seren_source"],
            causal_links=["cause_trial_reveal"],
            tension_value=0.7,
        ),
        SceneBeat(
            beat_id="beat_consequence",
            scene_id="scene_draft",
            beat_index=3,
            beat_type="consequence",
            purpose="Show consequence cons_reputation_shift.",
            character_ids=["char_kael", "char_seren"],
            causal_links=["cons_reputation_shift"],
            tension_value=0.9,
        ),
        SceneBeat(
            beat_id="beat_ending",
            scene_id="scene_draft",
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
            dialogue_beat_id="dialogue_scene_draft_01_secret_pressure",
            scene_id="scene_draft",
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
            betrayal_risk=0.7,
            turning_point="Evidence changes trust.",
            expected_end_state_shift={"trust_delta": -0.05, "resentment_delta": 0.08},
        )
    ]


def build_style_profile():
    return {
        "prose_style_profile_id": "prose_style_scene_draft",
        "selected_format": "scene",
        "drafting_instructions": [
            "Use concrete world details instead of generic filler.",
            "Keep character voice distinct.",
        ],
        "warnings": [],
    }


def build_commercial_report():
    return CommercialAppealReport(
        report_id="commercial_report_scene_draft",
        overall_score=0.82,
        hook_strength=0.8,
        emotional_investment=0.8,
        character_appeal=0.8,
        relationship_appeal=0.8,
        stakes_clarity=0.8,
        world_uniqueness=0.9,
        scene_momentum=0.8,
        continuation_pull=0.8,
        adaptation_potential=0.7,
        improvement_suggestions=[],
    )


def build_story_context():
    return {
        "knowledge_boundaries": [
            {
                "holder_id": "char_kael",
                "known_secret_ids": ["secret_rank_system"],
                "missing_required_secret_ids": ["secret_seren_source"],
            }
        ],
        "causal_obligations": [
            {"obligation_type": "causal_node", "id": "cause_trial_reveal"},
            {"obligation_type": "consequence", "id": "cons_reputation_shift"},
        ],
    }


def build_world_detail_pack():
    return {
        "law_and_rule_anchors": [{"detail": "public proof changes legal rank"}],
        "location_anchors": [{"detail": "Oath Court"}],
        "ritual_anchors": [{"detail": "proof must be spoken before witness tiers"}],
    }


def test_scene_draft_engine_generates_draft():
    engine = SceneDraftEngine()

    result = engine.generate_scene_draft(
        blueprint=build_blueprint(),
        scene_beats=build_scene_beats(),
        dialogue_beats=build_dialogue_beats(),
        relationship_beats=build_relationship_beats(),
        prose_style_profile=build_style_profile(),
        commercial_report=build_commercial_report(),
        story_context=build_story_context(),
        world_detail_pack=build_world_detail_pack(),
    )

    draft = result["scene_draft"]

    assert result["success"] is True
    assert draft.draft_id == "draft_scene_draft"
    assert draft.scene_id == "scene_draft"
    assert draft.blueprint_id == "blueprint_draft"
    assert draft.draft_text
    assert len(draft.sections) == 4


def test_scene_draft_engine_tracks_used_context():
    engine = SceneDraftEngine()

    draft = engine.generate_scene_draft(
        blueprint=build_blueprint(),
        scene_beats=build_scene_beats(),
        dialogue_beats=build_dialogue_beats(),
        relationship_beats=build_relationship_beats(),
        prose_style_profile=build_style_profile(),
        commercial_report=build_commercial_report(),
        story_context=build_story_context(),
        world_detail_pack=build_world_detail_pack(),
    )["scene_draft"]

    assert "char_kael" in draft.used_character_ids
    assert "rel_kael_seren" in draft.used_relationship_ids
    assert "secret_seren_source" in draft.used_secret_ids
    assert "cause_trial_reveal" in draft.used_causal_ids
    assert "Oath Court" in draft.used_world_details


def test_scene_draft_engine_validates_draft():
    engine = SceneDraftEngine()

    draft = engine.generate_scene_draft(
        blueprint=build_blueprint(),
        scene_beats=build_scene_beats(),
        dialogue_beats=build_dialogue_beats(),
        relationship_beats=build_relationship_beats(),
        prose_style_profile=build_style_profile(),
        commercial_report=build_commercial_report(),
        story_context=build_story_context(),
        world_detail_pack=build_world_detail_pack(),
    )["scene_draft"]

    validation = engine.validate_scene_draft(draft=draft)

    assert validation["success"] is True
    assert validation["valid"] is True
    assert "draft_id_present" in validation["passed_checks"]
    assert "draft_text_present" in validation["passed_checks"]
    assert "sections_present" in validation["passed_checks"]


def test_scene_draft_engine_summarizes_draft():
    engine = SceneDraftEngine()

    draft = engine.generate_scene_draft(
        blueprint=build_blueprint(),
        scene_beats=build_scene_beats(),
        dialogue_beats=build_dialogue_beats(),
        relationship_beats=build_relationship_beats(),
        prose_style_profile=build_style_profile(),
        commercial_report=build_commercial_report(),
        story_context=build_story_context(),
        world_detail_pack=build_world_detail_pack(),
    )["scene_draft"]

    summary = engine.summarize_scene_draft(draft=draft)

    assert summary["success"] is True
    assert summary["summary"]["scene_id"] == "scene_draft"
    assert summary["summary"]["section_count"] == 4
    assert summary["summary"]["used_character_count"] == 2
    assert summary["summary"]["used_world_detail_count"] >= 3


def test_scene_draft_engine_builds_revision_targets():
    engine = SceneDraftEngine()

    draft = engine.generate_scene_draft(
        blueprint=build_blueprint(),
        scene_beats=build_scene_beats(),
        dialogue_beats=build_dialogue_beats(),
        relationship_beats=build_relationship_beats(),
        prose_style_profile=build_style_profile(),
        commercial_report=build_commercial_report(),
        story_context=build_story_context(),
        world_detail_pack=build_world_detail_pack(),
    )["scene_draft"]

    result = engine.build_revision_targets(draft=draft)

    assert result["success"] is True
    assert result["needs_revision"] is True
    assert result["revision_targets"]


def test_scene_draft_engine_supports_screenplay_format():
    engine = SceneDraftEngine()
    style = build_style_profile()
    style["selected_format"] = "screenplay"

    draft = engine.generate_scene_draft(
        blueprint=build_blueprint(),
        scene_beats=build_scene_beats(),
        dialogue_beats=build_dialogue_beats(),
        relationship_beats=build_relationship_beats(),
        prose_style_profile=style,
        story_context=build_story_context(),
        world_detail_pack=build_world_detail_pack(),
    )["scene_draft"]

    assert draft.selected_format == "screenplay"
    assert "ACTION:" in draft.draft_text

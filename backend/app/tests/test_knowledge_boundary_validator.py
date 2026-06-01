from backend.app.engines.story_generation.knowledge_boundary_validator import KnowledgeBoundaryValidator
from backend.app.schemas.story_generation import DialogueBeat, RelationshipBeat, SceneBeat, SceneBlueprint


def build_blueprint():
    return SceneBlueprint(
        blueprint_id="blueprint_knowledge",
        scene_id="scene_knowledge",
        scene_purpose="Keep the mystery intact while evidence is shown.",
        pov_character_id="char_kael",
        active_character_ids=["char_kael", "char_seren"],
        scene_objective="Kael exposes badge evidence without knowing Seren's source.",
        secret_pressure=[
            "char_kael lacks required secret knowledge: secret_seren_source.",
            "char_seren must not reveal: major_mystery_solution_until_planned_reveal.",
        ],
        relationship_pressure=["rel_kael_seren pressure"],
        tension_curve=[0.3, 0.5, 0.7, 0.9],
    )


def build_story_context():
    return {
        "knowledge_boundaries": [
            {
                "holder_id": "char_kael",
                "known_secret_ids": ["secret_rank_system"],
                "evidence_seen_ids": ["evidence_cracked_badge"],
                "required_secret_ids": ["secret_rank_system", "secret_seren_source"],
                "missing_required_secret_ids": ["secret_seren_source"],
                "forbidden_secret_reveals": [],
            },
            {
                "holder_id": "char_seren",
                "known_secret_ids": ["secret_rank_system", "secret_seren_source"],
                "evidence_seen_ids": ["evidence_cracked_badge"],
                "required_secret_ids": ["secret_rank_system"],
                "missing_required_secret_ids": [],
                "forbidden_secret_reveals": ["major_mystery_solution_until_planned_reveal"],
            },
        ]
    }


def build_safe_scene_beats():
    return [
        SceneBeat(
            beat_id="beat_safe",
            scene_id="scene_knowledge",
            beat_index=1,
            beat_type="secret_pressure",
            purpose="Kael lacks secret_seren_source and must speak around the missing knowledge.",
            character_ids=["char_kael"],
            knowledge_constraints=["char_kael does not know secret_seren_source"],
            causal_links=[],
            tension_value=0.7,
        )
    ]


def build_safe_dialogue_beats():
    return [
        DialogueBeat(
            dialogue_beat_id="dialogue_safe",
            scene_id="scene_knowledge",
            speaker_id="char_kael",
            listener_ids=["char_seren"],
            surface_meaning="Kael speaks about the badge, not Seren's source.",
            hidden_meaning="He knows something is hidden but not what.",
            subtext="suspicion without knowledge",
            secret_risk=0.35,
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
            romantic_tension=0.4,
            betrayal_risk=0.7,
            knowledge_asymmetry=[
                "char_kael does not know secret_seren_source",
                "char_seren must not reveal major_mystery_solution_until_planned_reveal",
            ],
            turning_point="Secret pressure changes trust.",
            expected_end_state_shift={"trust_delta": -0.05},
        )
    ]


def test_knowledge_boundary_validator_passes_safe_context():
    validator = KnowledgeBoundaryValidator()

    result = validator.validate_knowledge_boundaries(
        blueprint=build_blueprint(),
        scene_beats=build_safe_scene_beats(),
        dialogue_beats=build_safe_dialogue_beats(),
        relationship_beats=build_relationship_beats(),
        story_context=build_story_context(),
    )

    report = result["knowledge_boundary_report"]

    assert result["success"] is True
    assert report.valid is True
    assert "secret_seren_source" in report.checked_secret_ids
    assert "evidence_cracked_badge" in report.checked_evidence_ids
    assert report.impossible_knowledge_violations == []


def test_knowledge_boundary_validator_blocks_unknown_secret_in_dialogue():
    validator = KnowledgeBoundaryValidator()

    unsafe_dialogue = [
        DialogueBeat(
            dialogue_beat_id="dialogue_bad",
            scene_id="scene_knowledge",
            speaker_id="char_kael",
            listener_ids=["char_seren"],
            surface_meaning="Kael says secret_seren_source aloud as if he knows it.",
            hidden_meaning="He exposes secret_seren_source.",
            subtext="impossible knowledge",
            secret_risk=0.8,
        )
    ]

    result = validator.validate_knowledge_boundaries(
        blueprint=build_blueprint(),
        scene_beats=build_safe_scene_beats(),
        dialogue_beats=unsafe_dialogue,
        relationship_beats=build_relationship_beats(),
        story_context=build_story_context(),
    )

    report = result["knowledge_boundary_report"]

    assert report.valid is False
    assert any("mentions secret_seren_source but does not know it" in item for item in report.impossible_knowledge_violations)


def test_knowledge_boundary_validator_blocks_forbidden_reveal():
    validator = KnowledgeBoundaryValidator()

    unsafe_dialogue = [
        DialogueBeat(
            dialogue_beat_id="dialogue_forbidden",
            scene_id="scene_knowledge",
            speaker_id="char_seren",
            listener_ids=["char_kael"],
            surface_meaning="Seren reveals major_mystery_solution_until_planned_reveal.",
            hidden_meaning="The mystery answer is exposed early.",
            subtext="forbidden reveal",
            secret_risk=0.9,
        )
    ]

    result = validator.validate_knowledge_boundaries(
        blueprint=build_blueprint(),
        scene_beats=build_safe_scene_beats(),
        dialogue_beats=unsafe_dialogue,
        relationship_beats=build_relationship_beats(),
        story_context=build_story_context(),
    )

    report = result["knowledge_boundary_report"]

    assert report.valid is False
    assert any("risks forbidden reveal" in item for item in report.impossible_knowledge_violations)


def test_knowledge_boundary_validator_builds_safe_reveal_plan():
    validator = KnowledgeBoundaryValidator()

    unsafe_dialogue = [
        DialogueBeat(
            dialogue_beat_id="dialogue_bad",
            scene_id="scene_knowledge",
            speaker_id="char_kael",
            listener_ids=["char_seren"],
            surface_meaning="Kael says secret_seren_source aloud.",
            hidden_meaning="He exposes secret_seren_source.",
            subtext="impossible knowledge",
            secret_risk=0.8,
        )
    ]

    report = validator.validate_knowledge_boundaries(
        blueprint=build_blueprint(),
        scene_beats=build_safe_scene_beats(),
        dialogue_beats=unsafe_dialogue,
        relationship_beats=build_relationship_beats(),
        story_context=build_story_context(),
    )["knowledge_boundary_report"]

    plan = validator.build_safe_reveal_plan(
        report=report,
        story_context=build_story_context(),
    )

    assert plan["success"] is True
    assert "add prior knowledge/reveal scene" in plan["required_setup"]
    assert plan["ready_for_generation"] is False
    assert any(item["secret_id"] == "secret_rank_system" for item in plan["safe_reveal_candidates"])


def test_knowledge_boundary_validator_validates_report():
    validator = KnowledgeBoundaryValidator()

    report = validator.validate_knowledge_boundaries(
        blueprint=build_blueprint(),
        scene_beats=build_safe_scene_beats(),
        dialogue_beats=build_safe_dialogue_beats(),
        relationship_beats=build_relationship_beats(),
        story_context=build_story_context(),
    )["knowledge_boundary_report"]

    validation = validator.validate_report(report=report)

    assert validation["success"] is True
    assert validation["valid"] is True
    assert "knowledge_boundaries_valid" in validation["passed_checks"]
    assert "secrets_checked" in validation["passed_checks"]


def test_knowledge_boundary_validator_summarizes_report():
    validator = KnowledgeBoundaryValidator()

    report = validator.validate_knowledge_boundaries(
        blueprint=build_blueprint(),
        scene_beats=build_safe_scene_beats(),
        dialogue_beats=build_safe_dialogue_beats(),
        relationship_beats=build_relationship_beats(),
        story_context=build_story_context(),
    )["knowledge_boundary_report"]

    summary = validator.summarize_report(report=report)

    assert summary["success"] is True
    assert summary["summary"]["valid"] is True
    assert summary["summary"]["checked_secret_count"] >= 2
    assert summary["summary"]["violation_count"] == 0


def test_knowledge_boundary_validator_warns_without_knowledge_index():
    validator = KnowledgeBoundaryValidator()

    result = validator.validate_knowledge_boundaries(
        blueprint=build_blueprint(),
        scene_beats=[],
        dialogue_beats=[],
        relationship_beats=[],
        story_context={},
    )

    report = result["knowledge_boundary_report"]

    assert report.valid is True
    assert any("No knowledge index found" in warning for warning in report.warnings)
    assert any("No knowledge boundary record" in warning for warning in report.warnings)

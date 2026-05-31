from backend.app.engines.character.character_quality_scorer import CharacterQualityScorer
from backend.app.schemas.foundation import EngineRunResult
from backend.app.schemas.learning import EngineLearningMetadata, LearnedOntologyRecord


def strong_payload():
    return {
        "character_seed": {
            "character_id": "char_kael",
            "name": "Kael Veyran",
            "role": "protagonist",
            "social_class": "academy_sponsored",
            "family_name_status": "distrusted",
            "destiny_type": "hidden_kingmaker",
        },
        "consistency_report": {
            "overall_consistency_score": 0.94,
            "critical_issue_count": 0,
            "violation_count": 0,
        },
        "originality_report": {
            "overall_originality_score": 0.78,
            "coherence_adjusted_originality": 0.8,
            "novelty_score": 0.82,
            "strong_originality_sources": ["power_redirector_plus_cognitive_inference"],
        },
        "anti_genericity_report": {
            "genericity_risk_score": 0.12,
            "genericity_risks": [],
        },
        "repair_plan": {
            "requires_repair": False,
            "repair_count": 0,
        },
        "origin_profile": {
            "character_id": "char_kael",
            "social_class": "academy_sponsored",
            "family_name_status": "distrusted",
            "education_access": 0.82,
        },
        "family_profile": {
            "character_id": "char_kael",
            "family_name_status": "distrusted",
        },
        "psychology_profile": {
            "character_id": "char_kael",
            "core_wound": "believes belonging can be revoked after public failure",
            "betrayal_response": "goes cold, protects family secrets, and remembers exact words",
            "love_response": "tests intimacy through duty, truth, and public pressure",
        },
        "goal_profile": {
            "character_id": "char_kael",
            "hidden_goal": "find proof that the ranking system is edited",
            "true_need": "belonging is not the same as permission",
            "false_need": "worth can be revoked by public failure",
        },
        "moral_profile": {
            "character_id": "char_kael",
            "dominant_moral_value": "justice",
            "forbidden_lines": ["will not knowingly sacrifice someone powerless for personal advancement"],
        },
        "memory_records": [
            {"memory_id": "mem_core", "content": "public failure and family secret memory"},
        ],
        "skill_ontology": {
            "skill_family": "cognitive_inference",
            "skill_subtype": "pattern_detection",
            "cost_family": ["mental_fatigue"],
            "counter_family": ["false_signal"],
            "growth_model": "precision_refinement",
        },
        "character_type_ontology": {
            "type_family": "power_redirector",
            "type_subtype": "hidden_kingmaker",
        },
        "adaptability_profile": {
            "adaptability_family": "earned_moral_breakthrough",
            "trigger_model": "moral_threshold: protects someone weaker",
            "cost_model": {"cost_families": ["mental_fatigue"]},
        },
        "limit_break_rules": {
            "hard_prohibitions": ["cannot activate for convenience"],
        },
        "destiny_profile": {
            "destiny_family": "power_flow_destiny",
            "destiny_is_absolute": False,
            "destiny_burdens": ["others may treat the character as a means to power"],
        },
        "prophecy_model": {
            "prophecy_requires_choice": True,
        },
        "relationship_readiness_profile": {
            "relationship_readiness_family": "high_loyalty_power_broker_readiness",
            "attachment_pattern": "guarded_attachment_with_secret_testing",
            "trust_model": "trust_requires_truth_protection_without_weaponization",
            "intimacy_risk": 0.72,
        },
        "boundary_model": {
            "relationship_boundaries": [
                "relationship cannot erase independent agency",
                "destiny cannot force love, loyalty, or forgiveness",
            ],
        },
        "dialogue_voice_profile": {
            "voice_family": "controlled_subtext_voice",
        },
        "speech_pattern_model": {
            "sentence_rhythm": "short_precise_lines_with_held_back_explanations",
            "subtext_density": "high_subtext",
        },
        "forbidden_dialogue_patterns": {
            "generic_voice_failure_modes": ["generic witty banter disconnected from wound"],
        },
        "source_mode": "human_approved_synthetic",
        "user_rating": 9,
    }


def weak_payload():
    return {
        "character_seed": {
            "character_id": "char_weak",
            "name": "Arin",
            "role": "protagonist",
        },
        "consistency_report": {
            "overall_consistency_score": 0.62,
            "critical_issue_count": 0,
            "violation_count": 1,
        },
        "originality_report": {
            "overall_originality_score": 0.48,
            "novelty_score": 0.5,
            "strong_originality_sources": [],
        },
        "anti_genericity_report": {
            "genericity_risk_score": 0.72,
            "genericity_risks": ["generic_chosen_protagonist_risk"],
        },
        "repair_plan": {
            "requires_repair": True,
            "repair_count": 3,
        },
        "skill_ontology": {
            "skill_family": "elemental_authority",
            "cost_family": [],
            "counter_family": [],
        },
        "source_mode": "human_approved_synthetic",
        "user_rating": 9,
    }


def test_quality_scorer_returns_engine_result():
    engine = CharacterQualityScorer()

    result = engine.run(strong_payload())

    assert isinstance(result, EngineRunResult)
    assert result.success is True
    assert result.engine_name == "character.quality_scorer"
    assert "character_quality_axis_scores" in result.data
    assert "quality_report" in result.data
    assert "readiness_report" in result.data
    assert "quality_recommendation_report" in result.data
    assert "learning_metadata" in result.data


def test_quality_scorer_scores_strong_character_highly():
    engine = CharacterQualityScorer()

    result = engine.run(strong_payload())

    report = result.data["quality_report"]
    readiness = result.data["readiness_report"]
    axes = result.data["character_quality_axis_scores"]

    assert report["character_id"] == "char_kael"
    assert report["overall_quality_score"] >= 0.78
    assert report["quality_tier"] in {"strong_character_ready", "elite_franchise_ready"}
    assert report["franchise_potential_score"] >= 0.75
    assert "consistency" in report["strong_axes"]
    assert readiness["character_bible_ready"] is True
    assert readiness["orchestrator_ready"] is True
    assert readiness["training_queue_ready"] is True
    assert axes["dialogue_voice"]["score"] >= 0.7
    assert axes["relationship_readiness"]["score"] >= 0.7


def test_quality_scorer_detects_weak_character_blockers():
    engine = CharacterQualityScorer()

    result = engine.run(weak_payload())

    report = result.data["quality_report"]
    readiness = result.data["readiness_report"]
    recommendations = result.data["quality_recommendation_report"]

    assert report["overall_quality_score"] < 0.7
    assert report["quality_tier"] in {"repair_needed", "major_rebuild_needed", "good_but_needs_polish"}
    assert "consistency violations" in report["export_blockers"]
    assert "unresolved repair plan" in report["export_blockers"]
    assert readiness["character_bible_ready"] is False
    assert readiness["training_queue_ready"] is False
    assert recommendations["major_risks"]


def test_quality_scorer_axis_scores_include_all_major_character_layers():
    engine = CharacterQualityScorer()

    result = engine.run(strong_payload())

    axes = result.data["character_quality_axis_scores"]

    expected_axes = [
        "consistency",
        "originality",
        "world_grounding",
        "psychological_depth",
        "goal_agency",
        "skill_integrity",
        "adaptability_integrity",
        "destiny_agency",
        "relationship_readiness",
        "dialogue_voice",
        "repair_status",
    ]

    for axis in expected_axes:
        assert axis in axes
        assert "score" in axes[axis]
        assert "purpose" in axes[axis]
        assert "passed" in axes[axis]


def test_quality_scorer_outputs_learning_metadata():
    engine = CharacterQualityScorer()

    result = engine.run(strong_payload())

    ontology_record = LearnedOntologyRecord.model_validate(result.data["ontology_record"])
    learning_metadata = EngineLearningMetadata.model_validate(result.data["learning_metadata"])

    assert ontology_record.ontology_type == "character_quality"
    assert ontology_record.family == "character_quality"
    assert ontology_record.generated_by_engine == "character.quality_scorer"

    assert learning_metadata.engine_name == "character.quality_scorer"
    assert learning_metadata.target_object_id == "char_kael"
    assert learning_metadata.generated_training_labels["character_bible_ready"] is True
    assert learning_metadata.generated_training_labels["training_queue_ready"] is True
    assert learning_metadata.training_eligibility.training_eligible is True


def test_quality_scorer_is_conservative_when_source_not_approved():
    engine = CharacterQualityScorer()

    payload = strong_payload()
    payload["source_mode"] = "unknown_web_text"

    result = engine.run(payload)

    metadata = result.data["learning_metadata"]

    assert metadata["training_eligibility"]["training_eligible"] is False
    assert metadata["training_eligibility"]["do_not_train"] is True
    assert "source mode is not approved for training" in metadata["training_eligibility"]["rejection_reasons"]


def test_quality_scorer_builds_next_payloads():
    engine = CharacterQualityScorer()

    result = engine.run(strong_payload())

    payload = result.data["next_engine_payload"]

    assert "character_seed" in payload
    assert "full_profile_orchestrator_payload" in payload
    assert "character_bible_export_payload" in payload
    assert "benchmark_payload" in payload
    assert "chunk8_training_payload_later" in payload
    assert payload["character_seed"]["quality_report"]["character_id"] == "char_kael"


def test_quality_scorer_warns_without_character_seed():
    engine = CharacterQualityScorer()

    result = engine.run({})

    assert result.success is True
    assert len(result.warnings) == 1
    assert "character_seed" in result.warnings[0]
    assert result.data["quality_report"]["character_id"].startswith("char_")

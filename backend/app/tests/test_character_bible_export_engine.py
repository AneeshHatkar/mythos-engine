from pathlib import Path

from backend.app.engines.character.character_bible_export_engine import CharacterBibleExportEngine
from backend.app.schemas.foundation import EngineRunResult
from backend.app.schemas.learning import EngineLearningMetadata, LearnedOntologyRecord


def sample_full_profile():
    return {
        "profile_id": "charprofile_test",
        "character_id": "char_kael",
        "identity": {
            "character_id": "char_kael",
            "name": "Kael Veyran",
            "role": "protagonist",
            "archetype_label": "Hidden Kingmaker",
            "project_id": "proj_ashen",
            "universe_id": "velmora",
            "profile_version": "v0.3.0-character-layer",
        },
        "origin": {
            "social_class": "academy_sponsored",
            "family_name_status": "distrusted",
            "origin_profile": {"education_access": 0.82},
            "family_profile": {"family_name_status": "distrusted"},
        },
        "psychology": {
            "psychology_profile": {
                "core_wound": "believes belonging can be revoked after public failure",
                "betrayal_response": "goes cold, protects family secrets, and remembers exact words",
            },
            "goal_profile": {
                "hidden_goal": "find proof that the ranking system is edited",
                "true_need": "belonging is not the same as permission",
                "false_need": "worth can be revoked by public failure",
            },
            "moral_profile": {"dominant_moral_value": "justice"},
            "memory_records": [{"memory_id": "mem_core", "content": "public failure and family secret memory"}],
            "emotional_arc_profile": {"arc_type": "adaptive_breakthrough_arc"},
        },
        "power": {
            "skill_ontology": {
                "skill_family": "cognitive_inference",
                "skill_subtype": "pattern_detection",
                "cost_family": ["mental_fatigue"],
                "counter_family": ["false_signal"],
            },
            "character_type_ontology": {
                "type_family": "power_redirector",
                "type_subtype": "hidden_kingmaker",
            },
            "adaptability_profile": {"adaptability_family": "earned_moral_breakthrough"},
            "limit_break_rules": {"hard_prohibitions": ["cannot activate for convenience"]},
        },
        "destiny": {
            "destiny_profile": {
                "destiny_family": "power_flow_destiny",
                "destiny_burdens": ["others may treat the character as a means to power"],
            },
            "prophecy_model": {"prophecy_requires_choice": True},
            "legacy_model": {"legacy_pressure_type": "contested_name_legacy"},
        },
        "relationships": {
            "relationship_readiness_profile": {
                "relationship_readiness_family": "high_loyalty_power_broker_readiness",
                "intimacy_risk": 0.72,
            },
            "relationship_hooks": {"friendship_hooks": ["friend notices controlled distance"]},
            "compatibility_vectors": {"friendship_vector": {"readiness_score": 0.72}},
            "boundary_model": {"relationship_boundaries": ["relationship cannot erase independent agency"]},
        },
        "dialogue": {
            "dialogue_voice_profile": {"voice_family": "controlled_subtext_voice"},
            "speech_pattern_model": {
                "sentence_rhythm": "short_precise_lines_with_held_back_explanations",
                "subtext_density": "high_subtext",
            },
            "relationship_dialogue_variants": {"friend_voice": "practical warmth"},
            "destiny_dialogue_layer": {"destiny_denial_voice": "rejects simplistic labels"},
            "forbidden_dialogue_patterns": {"generic_voice_failure_modes": ["generic witty banter disconnected from wound"]},
        },
        "validation": {
            "consistency_report": {"overall_consistency_score": 0.94, "critical_issue_count": 0, "violation_count": 0},
            "originality_report": {"overall_originality_score": 0.78, "novelty_score": 0.82},
            "quality_report": {
                "overall_quality_score": 0.84,
                "quality_tier": "strong_character_ready",
                "weak_axes": [],
            },
            "readiness_report": {
                "character_bible_ready": True,
                "orchestrator_ready": True,
                "training_queue_ready": True,
            },
        },
        "learning": {
            "learning_metadata_records": {"quality_learning_metadata": {"engine_name": "character.quality_scorer"}},
            "future_chunk8_training_ready": True,
            "provenance_ready": True,
        },
    }


def test_character_bible_export_returns_engine_result():
    engine = CharacterBibleExportEngine()

    result = engine.run(
        {
            "character_full_profile": sample_full_profile(),
            "source_mode": "human_approved_synthetic",
            "user_rating": 9,
        }
    )

    assert isinstance(result, EngineRunResult)
    assert result.success is True
    assert result.engine_name == "character.bible_export_engine"
    assert "character_bible" in result.data
    assert "character_bible_markdown" in result.data
    assert "export_report" in result.data
    assert "learning_metadata" in result.data


def test_character_bible_export_builds_all_major_sections():
    engine = CharacterBibleExportEngine()

    result = engine.run({"character_full_profile": sample_full_profile()})

    bible = result.data["character_bible"]

    assert bible["character_id"] == "char_kael"
    assert bible["bible_id"].startswith("charbible_")
    assert bible["identity"]["name"] == "Kael Veyran"
    assert "one_page_summary" in bible
    assert "origin_and_world_grounding" in bible
    assert "psychology_and_goals" in bible
    assert "morality_and_memory" in bible
    assert "skills_power_and_adaptability" in bible
    assert "destiny_prophecy_and_legacy" in bible
    assert "relationship_readiness" in bible
    assert "dialogue_voice" in bible
    assert "validation_quality_and_originality" in bible
    assert "learning_and_training_metadata" in bible
    assert "chunk4_handoff" in bible
    assert "chunk8_handoff" in bible


def test_character_bible_export_summary_is_non_generic():
    engine = CharacterBibleExportEngine()

    result = engine.run({"character_full_profile": sample_full_profile()})

    summary = result.data["character_bible"]["one_page_summary"]

    assert "Kael Veyran is a protagonist" in summary["logline"]
    assert "cognitive_inference" in summary["logline"]
    assert "power_flow_destiny" in summary["logline"]
    assert "believes 'worth can be revoked by public failure'" in summary["core_contradiction"]
    assert "redirects power flow" in summary["main_story_function"]
    assert "voice=controlled_subtext_voice" in summary["why_the_character_is_not_generic"]


def test_character_bible_export_builds_markdown():
    engine = CharacterBibleExportEngine()

    result = engine.run({"character_full_profile": sample_full_profile()})

    markdown = result.data["character_bible_markdown"]

    assert markdown.startswith("# Character Bible: Kael Veyran")
    assert "## One-Page Summary" in markdown
    assert "## Origin and World Grounding" in markdown
    assert "## Skills, Power, and Adaptability" in markdown
    assert "## Dialogue Voice" in markdown
    assert "## Chunk 8 Handoff" in markdown


def test_character_bible_export_report_and_diagnostics_ready():
    engine = CharacterBibleExportEngine()

    result = engine.run(
        {
            "character_full_profile": sample_full_profile(),
            "source_mode": "human_approved_synthetic",
            "user_rating": 9,
        }
    )

    report = result.data["export_report"]
    diagnostics = result.data["export_diagnostics"]

    assert report["export_completeness_score"] >= 0.95
    assert report["export_tier"] == "complete_character_bible"
    assert report["missing_sections"] == []
    assert diagnostics["json_ready"] is True
    assert diagnostics["markdown_ready"] is True
    assert diagnostics["physical_export_ready_later"] is True
    assert diagnostics["chunk4_ready"] is True
    assert diagnostics["training_queue_ready"] is True


def test_character_bible_export_writes_files_when_requested(tmp_path):
    engine = CharacterBibleExportEngine()

    result = engine.run(
        {
            "character_full_profile": sample_full_profile(),
            "write_to_disk": True,
            "output_dir": str(tmp_path / "bibles"),
        }
    )

    outputs = result.data["file_outputs"]

    assert outputs["written"] is True
    assert Path(outputs["json_path"]).exists()
    assert Path(outputs["markdown_path"]).exists()
    assert Path(outputs["markdown_path"]).read_text(encoding="utf-8").startswith("# Character Bible: Kael Veyran")


def test_character_bible_export_outputs_learning_metadata():
    engine = CharacterBibleExportEngine()

    result = engine.run(
        {
            "character_full_profile": sample_full_profile(),
            "source_mode": "human_approved_synthetic",
            "user_rating": 9,
        }
    )

    ontology_record = LearnedOntologyRecord.model_validate(result.data["ontology_record"])
    learning_metadata = EngineLearningMetadata.model_validate(result.data["learning_metadata"])

    assert ontology_record.ontology_type == "character_bible_export"
    assert ontology_record.family == "character_bible_export"
    assert ontology_record.generated_by_engine == "character.bible_export_engine"

    assert learning_metadata.engine_name == "character.bible_export_engine"
    assert learning_metadata.target_object_id == "char_kael"
    assert learning_metadata.generated_training_labels["markdown_ready"] is True
    assert learning_metadata.generated_training_labels["physical_export_ready_later"] is True
    assert learning_metadata.training_eligibility.training_eligible is True


def test_character_bible_export_is_conservative_when_source_not_approved():
    engine = CharacterBibleExportEngine()

    result = engine.run(
        {
            "character_full_profile": sample_full_profile(),
            "source_mode": "unknown_web_text",
            "user_rating": 9,
        }
    )

    metadata = result.data["learning_metadata"]

    assert metadata["training_eligibility"]["training_eligible"] is False
    assert metadata["training_eligibility"]["do_not_train"] is True
    assert "source mode is not approved for training" in metadata["training_eligibility"]["rejection_reasons"]


def test_character_bible_export_builds_next_payloads():
    engine = CharacterBibleExportEngine()

    result = engine.run({"character_full_profile": sample_full_profile()})

    payload = result.data["next_engine_payload"]

    assert "character_bible" in payload
    assert "character_bible_markdown" in payload
    assert "frontend_payload_later" in payload
    assert "physical_pdf_docx_export_payload_later" in payload
    assert "chunk4_relationship_payload_later" in payload
    assert "chunk8_training_payload_later" in payload
    assert payload["character_id"] == "char_kael"


def test_character_bible_export_warns_without_full_profile():
    engine = CharacterBibleExportEngine()

    result = engine.run(
        {
            "character_seed": {
                "character_id": "char_seed_only",
                "name": "Seed Only",
                "role": "supporting",
            }
        }
    )

    assert result.success is True
    assert len(result.warnings) == 1
    assert "character_full_profile" in result.warnings[0]
    assert result.data["character_bible"]["character_id"] == "char_seed_only"

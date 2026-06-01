from backend.app.engines.story_generation.generated_scene_delta_extractor import GeneratedSceneDeltaExtractor
from backend.app.schemas.story_generation import GeneratedChapter, StoryProvenanceRecord


def build_chapter():
    return GeneratedChapter(
        chapter_id="chapter_delta",
        chapter_number=1,
        title="The Badge",
        chapter_text="char_kael exposes secret_seren_source because cause_trial_reveal forces the Oath Court to respond.",
        scene_ids=["scene_001"],
        assembled_scene_ids=["assembled_scene_001"],
        used_character_ids=["char_kael"],
        used_relationship_ids=["rel_kael_seren"],
        used_secret_ids=["secret_seren_source"],
        used_causal_ids=["cause_trial_reveal"],
        used_world_details=["Oath Court"],
        open_loops=[{"loop_id": "open_loop_secret"}],
    )


def build_provenance(approved=True):
    return StoryProvenanceRecord(
        provenance_id="provenance_delta",
        provenance_record_id="provenance_delta",
        source_id="delta_source",
        draft_id="draft_delta",
        approved_for_memory_update=approved,
        approved_for_export=approved,
        memory_update_candidates=[
            {"candidate_id": "memory_existing_world", "candidate_type": "world_state", "value": "Oath Court"}
        ],
        protected_elements_snapshot=[
            {"element_id": "protect_character_char_kael", "element_type": "character", "value": "char_kael"},
            {"element_id": "protect_secret_secret_seren_source", "element_type": "secret", "value": "secret_seren_source"},
            {"element_id": "protect_world_oath_court", "element_type": "world_detail", "value": "Oath Court"},
        ],
    )


def test_generated_scene_delta_extractor_builds_report():
    extractor = GeneratedSceneDeltaExtractor()

    result = extractor.extract_deltas(
        source_id="delta_source",
        draft_id="draft_delta",
        generated_text="char_kael reveals secret_seren_source. The cracked badge changes the Oath Court.",
        chapter=build_chapter(),
        provenance_record=build_provenance(),
        story_context={
            "known_object_ids": ["cracked badge"],
            "known_open_loop_ids": ["open_loop_secret"],
        },
    )

    report = result["generated_story_delta_report"]

    assert result["success"] is True
    assert report.delta_report_id == "generated_story_delta_delta_source_draft_delta"
    assert report.character_deltas
    assert report.secret_deltas
    assert report.causal_deltas
    assert report.world_deltas
    assert report.object_deltas
    assert report.memory_update_candidates
    assert report.protected_element_impacts


def test_generated_scene_delta_extractor_detects_resolved_loop():
    extractor = GeneratedSceneDeltaExtractor()

    report = extractor.extract_deltas(
        source_id="delta_source",
        draft_id="draft_delta",
        generated_text="The truth is known and the case is closed.",
        story_context={"known_open_loop_ids": ["open_loop_secret"]},
    )["generated_story_delta_report"]

    assert report.resolved_loop_deltas
    assert report.resolved_loop_deltas[0]["target_id"] == "open_loop_secret"


def test_generated_scene_delta_extractor_warns_without_approved_provenance():
    extractor = GeneratedSceneDeltaExtractor()

    report = extractor.extract_deltas(
        source_id="delta_source",
        draft_id="draft_delta",
        generated_text="char_kael enters the Oath Court.",
        provenance_record=build_provenance(approved=False),
        story_context={"known_character_ids": ["char_kael"], "known_world_details": ["Oath Court"]},
    )["generated_story_delta_report"]

    assert any("not approved" in warning for warning in report.warnings)


def test_generated_scene_delta_extractor_validates_report():
    extractor = GeneratedSceneDeltaExtractor()

    report = extractor.extract_deltas(
        source_id="delta_source",
        draft_id="draft_delta",
        generated_text="char_kael enters the Oath Court.",
        provenance_record=build_provenance(),
        story_context={"known_character_ids": ["char_kael"], "known_world_details": ["Oath Court"]},
    )["generated_story_delta_report"]

    validation = extractor.validate_delta_report(report=report)

    assert validation["success"] is True
    assert validation["valid"] is True
    assert "delta_report_id_present" in validation["passed_checks"]
    assert "delta_summary_present" in validation["passed_checks"]


def test_generated_scene_delta_extractor_summarizes_report():
    extractor = GeneratedSceneDeltaExtractor()

    report = extractor.extract_deltas(
        source_id="delta_source",
        draft_id="draft_delta",
        generated_text="char_kael enters the Oath Court.",
        story_context={"known_character_ids": ["char_kael"], "known_world_details": ["Oath Court"]},
    )["generated_story_delta_report"]

    summary = extractor.summarize_delta_report(report=report)

    assert summary["success"] is True
    assert summary["summary"]["source_id"] == "delta_source"
    assert "memory_candidate_count" in summary["summary"]


def test_generated_scene_delta_extractor_builds_text():
    extractor = GeneratedSceneDeltaExtractor()

    report = extractor.extract_deltas(
        source_id="delta_source",
        draft_id="draft_delta",
        generated_text="char_kael enters the Oath Court.",
        story_context={"known_character_ids": ["char_kael"], "known_world_details": ["Oath Court"]},
    )["generated_story_delta_report"]

    text = extractor.build_delta_report_text(report=report)["delta_report_text"]

    assert "Generated Story Delta Report" in text
    assert "Delta Summary" in text
    assert "Memory Update Candidates" in text

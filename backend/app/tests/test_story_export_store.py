from pathlib import Path

from backend.app.engines.story_generation.story_export_store import StoryExportStore
from backend.app.schemas.story_generation import (
    GeneratedStoryDeltaReport,
    StoryExportPackage,
    StoryGenerationOrchestrationReport,
    StoryMemoryUpdateContract,
    StoryProvenanceRecord,
)


def build_orchestration(ready=True):
    return StoryGenerationOrchestrationReport(
        orchestration_report_id="orchestration_export",
        source_id="export_source",
        request_id="request_export",
        orchestration_status="ready" if ready else "blocked",
        ready_for_export=ready,
        ready_for_memory_apply=ready,
    )


def build_provenance(approved=True):
    return StoryProvenanceRecord(
        provenance_id="provenance_export",
        provenance_record_id="provenance_export",
        source_id="export_source",
        draft_id="draft_export",
        provenance_status="approved" if approved else "blocked",
        approved_for_memory_update=approved,
        approved_for_export=approved,
    )


def build_delta():
    return GeneratedStoryDeltaReport(
        delta_report_id="delta_export",
        source_id="export_source",
        draft_id="draft_export",
        memory_update_candidates=[
            {"candidate_id": "memory_char", "candidate_type": "character_state", "value": "char_kael"}
        ],
    )


def build_memory_contract(approved=True):
    return StoryMemoryUpdateContract(
        memory_update_contract_id="memory_export",
        memory_contract_id="memory_export",
        source_id="export_source",
        draft_id="draft_export",
        approved_for_apply=approved,
        apply_mode="auto_apply" if approved else "blocked",
        contract_status="approved" if approved else "blocked",
    )


def test_story_export_store_builds_approved_package(tmp_path):
    store = StoryExportStore()

    result = store.build_export_package(
        source_id="export_source",
        draft_id="draft_export",
        request_id="request_export",
        story_payload={"title": "The Oath Court", "text": "char_kael enters the Oath Court."},
        orchestration_report=build_orchestration(True),
        provenance_record=build_provenance(True),
        delta_report=build_delta(),
        memory_update_contract=build_memory_contract(True),
        export_root=tmp_path,
    )

    package = result["story_export_package"]

    assert result["success"] is True
    assert package.export_package_id == "story_export_export_source_draft_export_request_export"
    assert package.approved_for_export is True
    assert package.export_status == "approved"
    assert package.export_manifest
    assert package.artifact_paths
    assert not package.blocked_reasons


def test_story_export_store_blocks_unapproved_package(tmp_path):
    store = StoryExportStore()

    package = store.build_export_package(
        source_id="export_source",
        draft_id="draft_export",
        request_id="request_export",
        story_payload={"title": "Blocked"},
        orchestration_report=build_orchestration(False),
        provenance_record=build_provenance(False),
        delta_report=build_delta(),
        memory_update_contract=build_memory_contract(False),
        export_root=tmp_path,
    )["story_export_package"]

    assert package.approved_for_export is False
    assert package.export_status == "staged_blocked"
    assert package.blocked_reasons
    assert package.warnings


def test_story_export_store_writes_and_reads_package(tmp_path):
    store = StoryExportStore()

    package = store.build_export_package(
        source_id="export_source",
        draft_id="draft_export",
        request_id="request_export",
        story_payload={"title": "The Oath Court", "text": "char_kael enters the Oath Court."},
        orchestration_report=build_orchestration(True),
        provenance_record=build_provenance(True),
        delta_report=build_delta(),
        memory_update_contract=build_memory_contract(True),
        export_root=tmp_path,
    )["story_export_package"]

    write_result = store.write_export_package(package=package)

    assert write_result["success"] is True
    assert Path(write_result["written_files"]["manifest"]).exists()
    assert Path(write_result["written_files"]["export_package"]).exists()

    read_result = store.read_export_package(export_path=package.export_path)

    assert read_result["success"] is True
    assert read_result["story_export_package"].export_package_id == package.export_package_id


def test_story_export_store_validates_package(tmp_path):
    store = StoryExportStore()

    package = store.build_export_package(
        source_id="export_source",
        draft_id="draft_export",
        request_id="request_export",
        story_payload={"title": "The Oath Court"},
        orchestration_report=build_orchestration(True),
        provenance_record=build_provenance(True),
        delta_report=build_delta(),
        memory_update_contract=build_memory_contract(True),
        export_root=tmp_path,
    )["story_export_package"]

    validation = store.validate_export_package(package=package)

    assert validation["success"] is True
    assert validation["valid"] is True
    assert "export_package_id_present" in validation["passed_checks"]
    assert "export_manifest_present" in validation["passed_checks"]


def test_story_export_store_summarizes_package(tmp_path):
    store = StoryExportStore()

    package = store.build_export_package(
        source_id="export_source",
        draft_id="draft_export",
        request_id="request_export",
        story_payload={"title": "The Oath Court"},
        orchestration_report=build_orchestration(True),
        provenance_record=build_provenance(True),
        delta_report=build_delta(),
        memory_update_contract=build_memory_contract(True),
        export_root=tmp_path,
    )["story_export_package"]

    summary = store.summarize_export_package(package=package)

    assert summary["success"] is True
    assert summary["summary"]["source_id"] == "export_source"
    assert summary["summary"]["approved_for_export"] is True


def test_story_export_store_builds_text(tmp_path):
    store = StoryExportStore()

    package = store.build_export_package(
        source_id="export_source",
        draft_id="draft_export",
        request_id="request_export",
        story_payload={"title": "The Oath Court"},
        orchestration_report=build_orchestration(True),
        provenance_record=build_provenance(True),
        delta_report=build_delta(),
        memory_update_contract=build_memory_contract(True),
        export_root=tmp_path,
    )["story_export_package"]

    text = store.build_export_text(package=package)["export_text"]

    assert "Story Export Package" in text
    assert "Export Checks" in text
    assert "Artifact Paths" in text

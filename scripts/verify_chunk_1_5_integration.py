from __future__ import annotations

import importlib
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


ROOT = Path(__file__).resolve().parents[1]
REPORT_PATH = ROOT / "reports" / "chunk_1_5_integration_verification.json"


REQUIRED_FILES = [
    "backend/app/schemas/story_generation.py",
    "backend/app/api/story_generation_routes.py",
    "backend/app/engines/story_generation/story_generation_orchestrator.py",
    "backend/app/engines/story_generation/story_export_store.py",
    "backend/app/engines/story_generation/story_benchmark_pack.py",
    "backend/app/engines/story_generation/story_smoke_test.py",
    "backend/app/engines/story_generation/learning_feedback_adapter.py",
    "backend/app/tests/test_story_generation_orchestrator.py",
    "backend/app/tests/test_story_generation_api_routes.py",
    "backend/app/tests/test_story_export_store.py",
    "backend/app/tests/test_story_benchmark_pack.py",
    "backend/app/tests/test_story_smoke_test.py",
    "backend/app/tests/test_learning_feedback_adapter.py",
]

REQUIRED_SCHEMA_CLASSES = [
    "StoryGenerationOrchestrationReport",
    "StoryExportPackage",
    "StoryBenchmarkPack",
    "StorySmokeTestReport",
    "LearningFeedbackPackage",
    "StoryMemoryUpdateContract",
    "GeneratedStoryDeltaReport",
    "StoryProvenanceRecord",
]

REQUIRED_ENGINE_IMPORTS = [
    "backend.app.engines.story_generation.story_generation_orchestrator",
    "backend.app.engines.story_generation.story_export_store",
    "backend.app.engines.story_generation.story_benchmark_pack",
    "backend.app.engines.story_generation.story_smoke_test",
    "backend.app.engines.story_generation.learning_feedback_adapter",
    "backend.app.api.story_generation_routes",
]

REQUIRED_TEST_COMMANDS = [
    [sys.executable, "-m", "py_compile", "backend/app/schemas/story_generation.py"],
    [sys.executable, "-m", "py_compile", "backend/app/api/story_generation_routes.py"],
    [sys.executable, "-m", "py_compile", "backend/app/engines/story_generation/story_generation_orchestrator.py"],
    [sys.executable, "-m", "py_compile", "backend/app/engines/story_generation/story_export_store.py"],
    [sys.executable, "-m", "py_compile", "backend/app/engines/story_generation/story_benchmark_pack.py"],
    [sys.executable, "-m", "py_compile", "backend/app/engines/story_generation/story_smoke_test.py"],
    [sys.executable, "-m", "py_compile", "backend/app/engines/story_generation/learning_feedback_adapter.py"],
    [sys.executable, "-m", "pytest", "backend/app/tests/test_story_generation_orchestrator.py", "-q"],
    [sys.executable, "-m", "pytest", "backend/app/tests/test_story_generation_api_routes.py", "-q"],
    [sys.executable, "-m", "pytest", "backend/app/tests/test_story_export_store.py", "-q"],
    [sys.executable, "-m", "pytest", "backend/app/tests/test_story_benchmark_pack.py", "-q"],
    [sys.executable, "-m", "pytest", "backend/app/tests/test_story_smoke_test.py", "-q"],
    [sys.executable, "-m", "pytest", "backend/app/tests/test_learning_feedback_adapter.py", "-q"],
]


def run_command(command: List[str]) -> Dict[str, Any]:
    completed = subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env={**os.environ, "PYTHONPATH": str(ROOT)},
    )

    output = completed.stdout or ""

    return {
        "command": " ".join(command),
        "ok": completed.returncode == 0,
        "returncode": completed.returncode,
        "output_tail": output[-4000:],
    }


def check_required_files() -> Dict[str, Any]:
    missing = [path for path in REQUIRED_FILES if not (ROOT / path).exists()]
    return {
        "passed": not missing,
        "required_count": len(REQUIRED_FILES),
        "missing": missing,
    }


def check_schema_classes() -> Dict[str, Any]:
    module = importlib.import_module("backend.app.schemas.story_generation")
    missing = [name for name in REQUIRED_SCHEMA_CLASSES if not hasattr(module, name)]
    return {
        "passed": not missing,
        "required_count": len(REQUIRED_SCHEMA_CLASSES),
        "missing": missing,
    }


def check_imports() -> Dict[str, Any]:
    missing = []
    errors = {}

    for module_name in REQUIRED_ENGINE_IMPORTS:
        try:
            importlib.import_module(module_name)
        except Exception as exc:
            missing.append(module_name)
            errors[module_name] = repr(exc)

    return {
        "passed": not missing,
        "required_count": len(REQUIRED_ENGINE_IMPORTS),
        "missing": missing,
        "errors": errors,
    }


def check_main_router_registration() -> Dict[str, Any]:
    main_path = ROOT / "backend/app/main.py"
    text = main_path.read_text(encoding="utf-8") if main_path.exists() else ""

    required_fragments = [
        "story_generation_router",
        "app.include_router(story_generation_router)",
    ]

    missing = [fragment for fragment in required_fragments if fragment not in text]

    return {
        "passed": not missing,
        "missing_fragments": missing,
    }


def check_late_chunk5_chain() -> Dict[str, Any]:
    from backend.app.engines.story_generation.story_benchmark_pack import StoryBenchmarkPackBuilder
    from backend.app.engines.story_generation.story_export_store import StoryExportStore
    from backend.app.engines.story_generation.story_generation_orchestrator import StoryGenerationOrchestrator
    from backend.app.engines.story_generation.story_smoke_test import StorySmokeTestRunner
    from backend.app.engines.story_generation.learning_feedback_adapter import LearningFeedbackAdapter
    from backend.app.schemas.story_generation import (
        GeneratedStoryDeltaReport,
        GenerationContract,
        OriginalityCopyRiskReport,
        StoryAntiGenericityReport,
        StoryContinuityValidationReport,
        StoryMemoryUpdateContract,
        StoryProvenanceRecord,
        StoryQualityScoreReport,
        StoryRevisionPlan,
        DraftComparisonReport,
        GenerationImprovementLoopDecision,
    )

    source_id = "integration_source"
    request_id = "integration_request"
    draft_id = "integration_draft"

    generation_contract = GenerationContract(
        generation_contract_id="integration_contract",
        contract_id="integration_contract",
        story_intent_id="integration_intent",
        source_id=source_id,
        target_format="chapter",
        generation_mode="draft",
        handoff_reference={
            "handoff_id": "integration_handoff",
            "simulation_id": "integration_simulation",
            "source": "chunk_1_5_integration_verifier",
            "status": "available",
        },
    )

    quality_report = StoryQualityScoreReport(
        quality_report_id="integration_quality",
        source_id=source_id,
        overall_score=0.85,
        readiness_level="ready",
        anti_generic_score=0.82,
    )

    anti_genericity_report = StoryAntiGenericityReport(
        report_id="integration_anti",
        draft_id=draft_id,
        anti_genericity_report_id="integration_anti",
        source_id=source_id,
        overall_anti_genericity_score=0.82,
        genericity_risk_level="medium",
    )

    continuity_report = StoryContinuityValidationReport(
        continuity_report_id="integration_continuity",
        source_id=source_id,
        valid=True,
        continuity_score=0.86,
        readiness_level="ready",
    )

    originality_report = OriginalityCopyRiskReport(
        originality_report_id="integration_originality",
        source_id=source_id,
        safe_for_export=True,
        overall_originality_score=0.84,
        copy_risk_level="low",
    )

    revision_plan = StoryRevisionPlan(
        revision_plan_id="integration_revision",
        source_id=source_id,
        revision_mode="targeted",
        overall_revision_priority="medium",
    )

    comparison_report = DraftComparisonReport(
        comparison_report_id="integration_comparison",
        source_id=source_id,
        original_draft_id="draft_original",
        revised_draft_id=draft_id,
        approved=True,
        improvement_score=0.75,
        regression_risk_score=0.05,
    )

    loop_decision = GenerationImprovementLoopDecision(
        loop_decision_id="integration_loop",
        source_id=source_id,
        current_iteration=1,
        max_iterations=3,
        action="approve_and_handoff",
        approved_for_handoff=True,
        stop_loop=True,
        improvement_status="approved",
        next_priority="low",
    )

    provenance_record = StoryProvenanceRecord(
        provenance_id="integration_provenance",
        provenance_record_id="integration_provenance",
        source_id=source_id,
        draft_id=draft_id,
        provenance_status="approved",
        approved_for_memory_update=True,
        approved_for_export=True,
    )

    delta_report = GeneratedStoryDeltaReport(
        delta_report_id="integration_delta",
        source_id=source_id,
        draft_id=draft_id,
        memory_update_candidates=[
            {"candidate_id": "memory_integration_char", "candidate_type": "character_state", "value": "char_kael"}
        ],
    )

    memory_update_contract = StoryMemoryUpdateContract(
        memory_update_contract_id="integration_memory_contract",
        memory_contract_id="integration_memory_contract",
        source_id=source_id,
        draft_id=draft_id,
        approved_for_apply=True,
        apply_mode="auto_apply",
        contract_status="approved",
    )

    orchestrator = StoryGenerationOrchestrator()
    orchestration_report = orchestrator.orchestrate_generation_state(
        source_id=source_id,
        request_id=request_id,
        generation_contract=generation_contract,
        quality_report=quality_report,
        anti_genericity_report=anti_genericity_report,
        continuity_report=continuity_report,
        originality_report=originality_report,
        revision_plan=revision_plan,
        comparison_report=comparison_report,
        loop_decision=loop_decision,
        provenance_record=provenance_record,
        delta_report=delta_report,
        memory_update_contract=memory_update_contract,
        story_context={"known_character_ids": ["char_kael"]},
    )["story_generation_orchestration_report"]

    export_store = StoryExportStore()
    export_package = export_store.build_export_package(
        source_id=source_id,
        draft_id=draft_id,
        request_id=request_id,
        story_payload={"title": "Integration Story", "text": "char_kael enters the Oath Court."},
        orchestration_report=orchestration_report,
        provenance_record=provenance_record,
        delta_report=delta_report,
        memory_update_contract=memory_update_contract,
        export_root=ROOT / "exports" / "integration_smoke",
    )["story_export_package"]

    benchmark_pack = StoryBenchmarkPackBuilder().build_benchmark_pack(
        source_id=source_id,
        request_id=request_id,
        draft_id=draft_id,
        story_payload={"title": "Integration Story", "text": "char_kael enters the Oath Court."},
        export_package=export_package,
        orchestration_report=orchestration_report,
        provenance_record=provenance_record,
        delta_report=delta_report,
        memory_update_contract=memory_update_contract,
    )["story_benchmark_pack"]

    smoke_report = StorySmokeTestRunner().run_smoke_test(
        source_id=source_id,
        request_id=request_id,
        draft_id=draft_id,
        orchestration_report=orchestration_report,
        export_package=export_package,
        benchmark_pack=benchmark_pack,
        story_context={"known_character_ids": ["char_kael"]},
    )["story_smoke_test_report"]

    learning_feedback = LearningFeedbackAdapter().build_learning_feedback_package(
        source_id=source_id,
        request_id=request_id,
        draft_id=draft_id,
        story_payload={"title": "Integration Story", "text": "char_kael enters the Oath Court."},
        orchestration_report=orchestration_report,
        export_package=export_package,
        benchmark_pack=benchmark_pack,
        smoke_test_report=smoke_report,
        story_context={"known_character_ids": ["char_kael"]},
    )["learning_feedback_package"]

    checks = {
        "orchestration_ready": orchestration_report.ready_for_export is True,
        "export_approved": export_package.approved_for_export is True,
        "benchmark_no_critical_failures": benchmark_pack.score_summary.get("critical_failed_count", 1) == 0,
        "smoke_passed": smoke_report.passed is True,
        "learning_feedback_created": bool(learning_feedback.learning_feedback_id),
    }

    return {
        "passed": all(checks.values()),
        "checks": checks,
        "artifacts": {
            "orchestration_report_id": orchestration_report.orchestration_report_id,
            "export_package_id": export_package.export_package_id,
            "benchmark_pack_id": benchmark_pack.benchmark_pack_id,
            "smoke_test_report_id": smoke_report.smoke_test_report_id,
            "learning_feedback_id": learning_feedback.learning_feedback_id,
        },
    }


def main() -> int:
    sys.path.insert(0, str(ROOT))

    checks: Dict[str, Any] = {}

    checks["required_files"] = check_required_files()
    checks["schema_classes"] = check_schema_classes()
    checks["imports"] = check_imports()
    checks["main_router_registration"] = check_main_router_registration()

    command_results = {}
    for command in REQUIRED_TEST_COMMANDS:
        key = "_".join(command).replace("/", "_")
        command_results[key] = run_command(command)

    checks["commands"] = {
        "passed": all(result["ok"] for result in command_results.values()),
        "results": command_results,
    }

    try:
        checks["late_chunk5_chain"] = check_late_chunk5_chain()
    except Exception as exc:
        checks["late_chunk5_chain"] = {
            "passed": False,
            "error": repr(exc),
        }

    passed = all(check.get("passed", False) for check in checks.values())

    report = {
        "report_id": "chunk_1_5_integration_verification",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "passed": passed,
        "summary": {
            "message": "Chunk 1-5 integration verification passed." if passed else "Chunk 1-5 integration verification failed.",
            "passed": passed,
            "check_count": len(checks),
        },
        "checks": checks,
    }

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")

    print(json.dumps(report["summary"], indent=2, sort_keys=True))
    print(f"Full report written to: {REPORT_PATH}")

    if not passed:
        print("\nFAILED DETAILS:")
        for name, check in checks.items():
            if not check.get("passed", False):
                print(f"\n[{name}]")
                print(json.dumps(check, indent=2, sort_keys=True)[-4000:])
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

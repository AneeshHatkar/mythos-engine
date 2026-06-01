from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
REPORT_PATH = ROOT / "reports" / "chunk_1_to_5_perfection.json"

REQUIRED_FILES = [
    "README.md",
    "docs/chunk_1_to_5_perfection_standard.md",
    "docs/chunk_1_to_5_deep_world_hook_contract.md",
    "docs/chunk_1_to_5_engine_coverage_matrix.md",
    "scripts/verify_chunk_1_5_integration.py",
    "scripts/final_chunk5_verification.py",
    "backend/app/schemas/story_generation.py",
    "backend/app/engines/story_generation/story_generation_orchestrator.py",
    "backend/app/engines/story_generation/story_export_store.py",
    "backend/app/engines/story_generation/story_benchmark_pack.py",
    "backend/app/engines/story_generation/story_smoke_test.py",
    "backend/app/engines/story_generation/learning_feedback_adapter.py",
]

REQUIRED_DOC_FRAGMENTS = {
    "docs/chunk_1_to_5_perfection_standard.md": [
        "Schema Stability",
        "Engine Boundary Stability",
        "Deep World Readiness",
        "Memory Readiness",
        "Story Generation Readiness",
        "Dataset and ML Readiness",
    ],
    "docs/chunk_1_to_5_deep_world_hook_contract.md": [
        "DeepWorldPacket",
        "GeographyPacket",
        "ClimatePacket",
        "SpeciesPacket",
        "CivilizationPacket",
        "SettlementPacket",
        "ObjectArtifactPacket",
        "WorldStateMemoryPacket",
        "Chunk 5 Hook Responsibilities",
    ],
    "docs/chunk_1_to_5_engine_coverage_matrix.md": [
        "Character identity",
        "World foundations",
        "Plot causality",
        "Memory state",
        "Story context",
        "Learning feedback",
    ],
}

REQUIRED_SCHEMA_CLASSES = [
    "GenerationContract",
    "StoryGenerationOrchestrationReport",
    "StoryExportPackage",
    "StoryBenchmarkPack",
    "StorySmokeTestReport",
    "LearningFeedbackPackage",
    "StoryMemoryUpdateContract",
    "GeneratedStoryDeltaReport",
    "StoryProvenanceRecord",
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
        "output_tail": output[-5000:],
    }

def check_required_files() -> Dict[str, Any]:
    missing = [path for path in REQUIRED_FILES if not (ROOT / path).exists()]
    return {"passed": not missing, "missing": missing, "required_count": len(REQUIRED_FILES)}

def check_doc_fragments() -> Dict[str, Any]:
    missing: Dict[str, List[str]] = {}
    for rel_path, fragments in REQUIRED_DOC_FRAGMENTS.items():
        path = ROOT / rel_path
        text = path.read_text(encoding="utf-8") if path.exists() else ""
        gaps = [fragment for fragment in fragments if fragment not in text]
        if gaps:
            missing[rel_path] = gaps
    return {"passed": not missing, "missing_fragments": missing}

def check_schema_classes() -> Dict[str, Any]:
    sys.path.insert(0, str(ROOT))
    import backend.app.schemas.story_generation as sg
    missing = [name for name in REQUIRED_SCHEMA_CLASSES if not hasattr(sg, name)]
    return {"passed": not missing, "missing": missing, "required_count": len(REQUIRED_SCHEMA_CLASSES)}

def check_reports_exist() -> Dict[str, Any]:
    report_paths = [
        ROOT / "reports" / "chunk_1_5_integration_verification.json",
        ROOT / "reports" / "final_chunk5_verification.json",
    ]
    missing = [str(path.relative_to(ROOT)) for path in report_paths if not path.exists()]
    parsed_failures = []
    for path in report_paths:
        if path.exists():
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
                if data.get("passed") is not True:
                    parsed_failures.append(str(path.relative_to(ROOT)))
            except Exception:
                parsed_failures.append(str(path.relative_to(ROOT)))
    return {"passed": not missing and not parsed_failures, "missing": missing, "parsed_failures": parsed_failures}

def check_compilation() -> Dict[str, Any]:
    files = [
        "scripts/verify_chunk_1_5_integration.py",
        "scripts/final_chunk5_verification.py",
        "backend/app/schemas/story_generation.py",
        "backend/app/tests/test_final_chunk5_verification.py",
    ]
    results = {path: run_command([sys.executable, "-m", "py_compile", path]) for path in files}
    return {"passed": all(item["ok"] for item in results.values()), "results": results}

def main() -> int:
    checks: Dict[str, Any] = {}
    checks["required_files"] = check_required_files()
    checks["doc_fragments"] = check_doc_fragments()
    checks["schema_classes"] = check_schema_classes()
    checks["reports_exist"] = check_reports_exist()
    checks["compilation"] = check_compilation()

    passed = all(check.get("passed", False) for check in checks.values())

    report = {
        "report_id": "chunk_1_to_5_perfection",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "passed": passed,
        "summary": {
            "message": "Chunk 1 to 5 perfection verification passed." if passed else "Chunk 1 to 5 perfection verification failed.",
            "passed": passed,
            "next_locked_step": "Pre-Chunk 6 Roadmap Lock and Readiness, then 6.1 Deep World Expansion Schemas plus Chunk 6 Design Contract",
        },
        "checks": checks,
    }

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")

    print(json.dumps(report["summary"], indent=2, sort_keys=True))
    print(f"Full report written to: {REPORT_PATH}")

    if not passed:
        print()
        print("FAILED DETAILS:")
        for name, check in checks.items():
            if not check.get("passed", False):
                print()
                print(f"[{name}]")
                print(json.dumps(check, indent=2, sort_keys=True)[-5000:])
        return 1

    return 0

if __name__ == "__main__":
    raise SystemExit(main())

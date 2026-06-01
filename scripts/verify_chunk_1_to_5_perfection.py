from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT_PATH = ROOT / "reports" / "chunk_1_to_5_perfection.json"

REQUIRED_DOCS = [
    "docs/chunk_1_to_5_perfection_standard.md",
    "docs/chunk_1_to_5_deep_world_hook_contract.md",
    "docs/chunk_1_to_5_engine_coverage_matrix.md",
    "docs/master_project_roadmap_chunks_1_to_9.md",
    "docs/chunk_1_to_5_compatibility_audit_before_chunk6.md",
]

REQUIRED_FILES = [
    "backend/app/engines/story_generation/chunk_1_to_5_future_compatibility_bridge.py",
    "backend/app/tests/test_chunk_1_to_5_future_compatibility_bridge.py",
    "scripts/final_chunk5_verification.py",
    "scripts/verify_chunk_1_5_integration.py",
    "reports/final_chunk5_verification.json",
    "reports/chunk_1_5_integration_verification.json",
]

REQUIRED_SCHEMA_TERMS = [
    "FutureWorldReferencePacket",
    "DeepWorldReferencePacket",
    "GeographyReferencePacket",
    "EcologyReferencePacket",
    "CivilizationReferencePacket",
    "SpeciesReferencePacket",
    "CultureReferencePacket",
    "SettlementReferencePacket",
    "ObjectArtifactReferencePacket",
    "WeatherReferencePacket",
    "TravelConstraintReferencePacket",
    "DailyLifeReferencePacket",
    "SecretLocationReferencePacket",
    "WorldStateMemoryReference",
    "StoryWorldExpansionBridge",
    "ChunkFutureCompatibilityContract",
]


def exists_check(paths):
    missing = [path for path in paths if not (ROOT / path).exists()]
    return {"passed": not missing, "missing": missing}


def schema_check():
    text = (ROOT / "backend/app/schemas/story_generation.py").read_text(encoding="utf-8")
    missing = [term for term in REQUIRED_SCHEMA_TERMS if term not in text]
    return {"passed": not missing, "missing": missing}


def compile_check():
    targets = [
        "backend/app/schemas/story_generation.py",
        "backend/app/engines/story_generation/chunk_1_to_5_future_compatibility_bridge.py",
        "backend/app/tests/test_chunk_1_to_5_future_compatibility_bridge.py",
    ]
    failures = []
    for target in targets:
        result = subprocess.run([sys.executable, "-m", "py_compile", target], cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        if result.returncode != 0:
            failures.append({"target": target, "output": result.stdout[-2000:]})
    return {"passed": not failures, "failures": failures}


def bridge_test_check():
    result = subprocess.run([sys.executable, "-m", "pytest", "backend/app/tests/test_chunk_1_to_5_future_compatibility_bridge.py", "-q"], cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env={"PYTHONPATH": str(ROOT)})
    return {"passed": result.returncode == 0, "output_tail": result.stdout[-3000:]}


def report_check():
    results = {}
    for path in ["reports/final_chunk5_verification.json", "reports/chunk_1_5_integration_verification.json"]:
        report_path = ROOT / path
        if not report_path.exists():
            results[path] = {"passed": False, "reason": "missing"}
            continue
        data = json.loads(report_path.read_text(encoding="utf-8"))
        results[path] = {"passed": data.get("passed") is True}
    return {"passed": all(item["passed"] for item in results.values()), "reports": results}


def main():
    checks = {
        "required_docs": exists_check(REQUIRED_DOCS),
        "required_files": exists_check(REQUIRED_FILES),
        "future_schema_terms": schema_check(),
        "py_compile": compile_check(),
        "bridge_tests": bridge_test_check(),
        "prior_reports": report_check(),
    }

    passed = all(check.get("passed", False) for check in checks.values())

    report = {
        "report_id": "chunk_1_to_5_perfection",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "passed": passed,
        "summary": {
            "message": "Chunk 1-5 perfection verification passed." if passed else "Chunk 1-5 perfection verification failed.",
            "next_locked_step": "verify_pre_chunk6_readiness",
            "passed": passed,
        },
        "checks": checks,
    }

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(report["summary"], indent=2, sort_keys=True))
    print(f"Full report written to: {REPORT_PATH}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())

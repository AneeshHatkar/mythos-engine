from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


ROOT = Path(__file__).resolve().parents[1]
REPORT_PATH = ROOT / "reports" / "pre_chunk6_readiness.json"


REQUIRED_FILES = [
    "README.md",
    "docs/master_project_roadmap_chunks_1_to_9.md",
    "docs/chunk_1_to_5_compatibility_audit_before_chunk6.md",
    "scripts/verify_chunk_1_5_integration.py",
    "scripts/final_chunk5_verification.py",
    "backend/app/schemas/story_generation.py",
    "backend/app/engines/story_generation/story_generation_orchestrator.py",
    "backend/app/engines/story_generation/story_export_store.py",
    "backend/app/engines/story_generation/story_benchmark_pack.py",
    "backend/app/engines/story_generation/story_smoke_test.py",
    "backend/app/engines/story_generation/learning_feedback_adapter.py",
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
    return {
        "passed": not missing,
        "required_count": len(REQUIRED_FILES),
        "missing": missing,
    }


def check_roadmap_order() -> Dict[str, Any]:
    path = ROOT / "docs/master_project_roadmap_chunks_1_to_9.md"
    text = path.read_text(encoding="utf-8") if path.exists() else ""

    required_fragments = [
        "Chunk 1",
        "Chunk 2",
        "Chunk 3",
        "Chunk 4",
        "Chunk 5",
        "Chunk 6 — Deep World",
        "Chunk 7 — Genre Engines",
        "Chunk 8 — Real-World Adaptation",
        "Chunk 9 — ML",
    ]

    missing = [fragment for fragment in required_fragments if fragment not in text]

    positions = {}
    for fragment in required_fragments:
        positions[fragment] = text.find(fragment)

    ordered = all(positions[item] >= 0 for item in required_fragments)
    if ordered:
        ordered = positions["Chunk 6 — Deep World"] < positions["Chunk 7 — Genre Engines"] < positions["Chunk 8 — Real-World Adaptation"] < positions["Chunk 9 — ML"]

    return {
        "passed": not missing and ordered,
        "missing_fragments": missing,
        "ordered": ordered,
        "positions": positions,
    }


def check_compatibility_audit() -> Dict[str, Any]:
    path = ROOT / "docs/chunk_1_to_5_compatibility_audit_before_chunk6.md"
    text = path.read_text(encoding="utf-8") if path.exists() else ""

    required_fragments = [
        "Chunk 1 Compatibility Needs",
        "Chunk 2 Compatibility Needs",
        "Chunk 3 Compatibility Needs",
        "Chunk 4 Compatibility Needs",
        "Chunk 5 Compatibility Needs",
        "Deep World Expansion Schemas",
        "World-State Memory Bridge",
        "Story Context Injection Bridge",
    ]

    missing = [fragment for fragment in required_fragments if fragment not in text]

    return {
        "passed": not missing,
        "missing_fragments": missing,
    }


def check_readme_mentions_next_phase() -> Dict[str, Any]:
    path = ROOT / "README.md"
    text = path.read_text(encoding="utf-8") if path.exists() else ""

    required_fragments = [
        "Chunk 5 Status",
        "5.50",
        "Push to GitHub",
    ]

    missing = [fragment for fragment in required_fragments if fragment not in text]

    return {
        "passed": not missing,
        "missing_fragments": missing,
    }


def main() -> int:
    checks: Dict[str, Any] = {}

    checks["required_files"] = check_required_files()
    checks["roadmap_order"] = check_roadmap_order()
    checks["compatibility_audit"] = check_compatibility_audit()
    checks["readme_next_phase"] = check_readme_mentions_next_phase()
    checks["final_chunk5_verification"] = run_command([sys.executable, "scripts/final_chunk5_verification.py"])

    checks["final_chunk5_verification"]["passed"] = checks["final_chunk5_verification"].get("ok", False)

    passed = all(check.get("passed", False) for check in checks.values())

    report = {
        "report_id": "pre_chunk6_readiness",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "passed": passed,
        "summary": {
            "message": "Pre-Chunk 6 readiness verification passed." if passed else "Pre-Chunk 6 readiness verification failed.",
            "passed": passed,
            "next_locked_step": "6.1 Deep World Expansion Schemas + Chunk 6 Design Contract",
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

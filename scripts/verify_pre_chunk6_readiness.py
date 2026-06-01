from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT_PATH = ROOT / "reports" / "pre_chunk6_readiness.json"
ROADMAP_PATH = ROOT / "docs" / "master_project_roadmap_chunks_1_to_9.md"


def roadmap_check():
    if not ROADMAP_PATH.exists():
        return {"passed": False, "reason": "roadmap missing"}

    text = ROADMAP_PATH.read_text(encoding="utf-8")
    required = [
        "Chunk 1",
        "Chunk 2",
        "Chunk 3",
        "Chunk 4",
        "Chunk 5",
        "Chunk 6",
        "Chunk 7",
        "Chunk 8",
        "Chunk 9",
        "6.1",
    ]
    missing = [item for item in required if item not in text]

    order_ok = all(text.index(f"Chunk {i}") < text.index(f"Chunk {i+1}") for i in range(1, 9) if f"Chunk {i}" in text and f"Chunk {i+1}" in text)

    return {"passed": not missing and order_ok, "missing": missing, "order_ok": order_ok}


def perfection_check():
    result = subprocess.run([sys.executable, "scripts/verify_chunk_1_to_5_perfection.py"], cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env={"PYTHONPATH": str(ROOT)})
    return {"passed": result.returncode == 0, "output_tail": result.stdout[-3000:]}


def readme_check():
    path = ROOT / "README.md"
    if not path.exists():
        return {"passed": False, "reason": "README missing"}
    text = path.read_text(encoding="utf-8")
    required = ["Chunk 5", "Chunk 6", "future compatibility", "6.1"]
    missing = [term for term in required if term.lower() not in text.lower()]
    return {"passed": not missing, "missing": missing}


def bridge_check():
    paths = [
        ROOT / "backend/app/engines/story_generation/chunk_1_to_5_future_compatibility_bridge.py",
        ROOT / "backend/app/tests/test_chunk_1_to_5_future_compatibility_bridge.py",
    ]
    return {"passed": all(path.exists() for path in paths), "paths": [str(path) for path in paths]}


def main():
    checks = {
        "roadmap": roadmap_check(),
        "chunk_1_to_5_perfection": perfection_check(),
        "readme": readme_check(),
        "future_bridge": bridge_check(),
    }

    passed = all(check.get("passed", False) for check in checks.values())

    report = {
        "report_id": "pre_chunk6_readiness",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "passed": passed,
        "summary": {
            "message": "Pre-Chunk 6 readiness verification passed." if passed else "Pre-Chunk 6 readiness verification failed.",
            "next_locked_step": "6.1 Deep World Expansion Schemas + Chunk 6 Design Contract",
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

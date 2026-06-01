from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
REPORT_PATH = ROOT / "reports" / "final_chunk5_verification.json"

COMMANDS = {
    "chunk_1_5_integration": [sys.executable, "scripts/verify_chunk_1_5_integration.py"],
    "full_pytest_suite": [sys.executable, "-m", "pytest", "backend/app/tests", "-q", "--ignore=backend/app/tests/test_final_chunk5_verification.py"],
    "story_generation_api_tests": [sys.executable, "-m", "pytest", "backend/app/tests/test_story_generation_api_routes.py", "-q"],
    "learning_feedback_tests": [sys.executable, "-m", "pytest", "backend/app/tests/test_learning_feedback_adapter.py", "-q"],
}

REQUIRED_FINAL_FILES = [
    "README.md",
    "scripts/verify_chunk_1_5_integration.py",
    "scripts/final_chunk5_verification.py",
    "backend/app/api/story_generation_routes.py",
    "backend/app/engines/story_generation/story_generation_orchestrator.py",
    "backend/app/engines/story_generation/story_export_store.py",
    "backend/app/engines/story_generation/story_benchmark_pack.py",
    "backend/app/engines/story_generation/story_smoke_test.py",
    "backend/app/engines/story_generation/learning_feedback_adapter.py",
]

def run_command(command: List[str]) -> Dict[str, Any]:
    completed = subprocess.run(command, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env={**os.environ, "PYTHONPATH": str(ROOT)})
    output = completed.stdout or ""
    return {"command": " ".join(command), "ok": completed.returncode == 0, "returncode": completed.returncode, "output_tail": output[-5000:]}

def check_required_files() -> Dict[str, Any]:
    missing = [path for path in REQUIRED_FINAL_FILES if not (ROOT / path).exists()]
    return {"passed": not missing, "required_count": len(REQUIRED_FINAL_FILES), "missing": missing}

def check_readme_chunk5_section() -> Dict[str, Any]:
    readme_path = ROOT / "README.md"
    text = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""
    required_fragments = ["Chunk 5 Status", "StoryGenerationOrchestrator", "StoryExportStore", "StoryBenchmarkPackBuilder", "StorySmokeTestRunner", "LearningFeedbackAdapter", "5.50 — Push to GitHub"]
    missing = [fragment for fragment in required_fragments if fragment not in text]
    return {"passed": not missing, "missing_fragments": missing}

def check_git_status() -> Dict[str, Any]:
    result = run_command(["git", "status", "--short"])
    return {"passed": result["ok"], "status_short": result["output_tail"]}

def main() -> int:
    checks: Dict[str, Any] = {}
    checks["required_files"] = check_required_files()
    checks["readme_chunk5_section"] = check_readme_chunk5_section()
    command_results = {name: run_command(command) for name, command in COMMANDS.items()}
    checks["commands"] = {"passed": all(item["ok"] for item in command_results.values()), "results": command_results}
    checks["git_status"] = check_git_status()
    passed = all(check.get("passed", False) for check in checks.values())
    report = {"report_id": "final_chunk5_verification", "created_at_utc": datetime.now(timezone.utc).isoformat(), "passed": passed, "summary": {"message": "Final Chunk 5 verification passed." if passed else "Final Chunk 5 verification failed.", "passed": passed, "next_locked_step": "5.50 Push to GitHub"}, "checks": checks}
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

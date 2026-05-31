from __future__ import annotations

import importlib
import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_CHUNK4_FILES = [
    "backend/app/schemas/simulation.py",
    "backend/app/api/simulation_routes.py",
    "backend/app/engines/simulation/interaction_simulation_orchestrator.py",
    "backend/app/engines/simulation/simulation_quality_scorer.py",
    "backend/app/engines/simulation/simulation_anti_genericity_validator.py",
    "backend/app/engines/simulation/simulation_run_store.py",
    "backend/app/engines/simulation/simulation_benchmark_pack.py",
    "backend/app/engines/simulation/simulation_learning_adapter.py",
    "backend/app/engines/simulation/simulation_learning_metadata_verifier.py",
    "scripts/chunk4_simulation_smoke_test.py",
    "scripts/verify_chunks_1_to_4_integrity.py",
    "docs/chunk4_simulation_layer_summary.md",
]


REQUIRED_IMPORTS = [
    "backend.app.main",
    "backend.app.api.simulation_routes",
    "backend.app.schemas.simulation",
    "backend.app.engines.simulation.interaction_simulation_orchestrator",
    "backend.app.engines.simulation.simulation_quality_scorer",
    "backend.app.engines.simulation.simulation_anti_genericity_validator",
    "backend.app.engines.simulation.simulation_run_store",
    "backend.app.engines.simulation.simulation_benchmark_pack",
    "backend.app.engines.simulation.simulation_learning_adapter",
    "backend.app.engines.simulation.simulation_learning_metadata_verifier",
]


REQUIRED_TESTS = [
    "backend/app/tests/test_chunk4_simulation_api_routes.py",
    "backend/app/tests/test_chunk4_simulation_benchmark_pack.py",
    "backend/app/tests/test_chunk4_simulation_smoke_test.py",
    "backend/app/tests/test_chunk4_simulation_learning_adapter.py",
    "backend/app/tests/test_chunk4_simulation_learning_metadata_verifier.py",
]


def run(cmd: list[str], timeout: int = 180) -> dict:
    proc = subprocess.run(
        cmd,
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        timeout=timeout,
    )
    return {
        "cmd": " ".join(cmd),
        "ok": proc.returncode == 0,
        "returncode": proc.returncode,
        "output": proc.stdout,
    }


def main() -> int:
    report = {
        "files": {},
        "imports": {},
        "routes": {},
        "commands": {},
        "summary": {},
    }

    missing_files = [path for path in REQUIRED_CHUNK4_FILES if not (ROOT / path).is_file()]
    missing_tests = [path for path in REQUIRED_TESTS if not (ROOT / path).is_file()]

    report["files"] = {
        "required_chunk4_file_count": len(REQUIRED_CHUNK4_FILES),
        "missing_chunk4_files": missing_files,
        "required_test_count": len(REQUIRED_TESTS),
        "missing_tests": missing_tests,
        "passed": not missing_files and not missing_tests,
    }

    failed_imports = []
    for module in REQUIRED_IMPORTS:
        try:
            importlib.import_module(module)
        except Exception as exc:
            failed_imports.append(f"{module}: {type(exc).__name__}: {exc}")

    report["imports"] = {
        "required_import_count": len(REQUIRED_IMPORTS),
        "failed_imports": failed_imports,
        "passed": not failed_imports,
    }

    route_problems = []
    try:
        app = importlib.import_module("backend.app.main").app
        route_paths = sorted({getattr(route, "path", "") for route in app.routes})
        for required in ["/simulation/health", "/simulation/run"]:
            if required not in route_paths:
                route_problems.append(f"missing route {required}")
    except Exception as exc:
        route_problems.append(f"route inspection failed: {type(exc).__name__}: {exc}")

    report["routes"] = {
        "problems": route_problems,
        "passed": not route_problems,
    }

    report["commands"]["integrity_1_to_4"] = run(
        ["python", "scripts/verify_chunks_1_to_4_integrity.py"],
        timeout=300,
    )

    report["commands"]["smoke_test"] = run(
        ["python", "scripts/chunk4_simulation_smoke_test.py"],
        timeout=180,
    )

    report["commands"]["focused_chunk4_late_tests"] = run(
        [
            "python",
            "-m",
            "pytest",
            "backend/app/tests/test_chunk4_simulation_api_routes.py",
            "backend/app/tests/test_chunk4_simulation_benchmark_pack.py",
            "backend/app/tests/test_chunk4_simulation_smoke_test.py",
            "backend/app/tests/test_chunk4_simulation_learning_adapter.py",
            "backend/app/tests/test_chunk4_simulation_learning_metadata_verifier.py",
            "-q",
        ],
        timeout=240,
    )

    report["commands"]["full_tests"] = run(
        ["python", "-m", "pytest", "backend/app/tests", "-q"],
        timeout=360,
    )

    passed = (
        report["files"]["passed"]
        and report["imports"]["passed"]
        and report["routes"]["passed"]
        and all(command["ok"] for command in report["commands"].values())
    )

    report["summary"] = {
        "passed": passed,
        "message": "Chunk 4 final verification passed." if passed else "Chunk 4 final verification failed.",
    }

    output_path = ROOT / "reports/chunk4_final_verification_report.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")

    print(json.dumps(report["summary"], indent=2, sort_keys=True))
    print(f"Full report written to: {output_path}")

    if not passed:
        print("\nFAILED DETAILS:")
        if not report["files"]["passed"]:
            print(json.dumps(report["files"], indent=2, sort_keys=True))
        if not report["imports"]["passed"]:
            print(json.dumps(report["imports"], indent=2, sort_keys=True))
        if not report["routes"]["passed"]:
            print(json.dumps(report["routes"], indent=2, sort_keys=True))
        for name, command in report["commands"].items():
            if not command["ok"]:
                print(f"\n[{name}]")
                print(command["output"][-4000:])
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

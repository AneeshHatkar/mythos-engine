from __future__ import annotations

import compileall
import importlib
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


EXPECTED_DIRS = [
    "backend",
    "backend/app",
    "backend/app/api",
    "backend/app/core",
    "backend/app/engines",
    "backend/app/engines/simulation",
    "backend/app/schemas",
    "backend/app/services",
    "backend/app/tests",
    "scripts",
]


EXPECTED_FILES = [
    # Core app
    "backend/app/main.py",
    "backend/app/__init__.py",
    "backend/__init__.py",

    # Existing API route groups from earlier chunks
    "backend/app/api/__init__.py",
    "backend/app/api/routes_foundation.py",
    "backend/app/api/routes_world.py",
    "backend/app/api/routes_world_engines.py",
    "backend/app/api/routes_characters.py",
    "backend/app/api/routes_character_engines.py",
    "backend/app/api/routes_learning.py",

    # Chunk 4 API route
    "backend/app/api/simulation_routes.py",

    # Chunk 4 simulation schemas / models
    "backend/app/schemas/simulation.py",

    # Chunk 4 late-stage engines
    "backend/app/engines/simulation/interaction_simulation_orchestrator.py",
    "backend/app/engines/simulation/simulation_quality_scorer.py",
    "backend/app/engines/simulation/simulation_anti_genericity_validator.py",
    "backend/app/engines/simulation/simulation_run_store.py",
    "backend/app/engines/simulation/simulation_benchmark_pack.py",

    # Chunk 4 tests
    "backend/app/tests/test_chunk4_interaction_simulation_orchestrator.py",
    "backend/app/tests/test_chunk4_simulation_quality_scorer.py",
    "backend/app/tests/test_chunk4_simulation_anti_genericity_validator.py",
    "backend/app/tests/test_chunk4_simulation_run_store.py",
    "backend/app/tests/test_chunk4_simulation_api_routes.py",
    "backend/app/tests/test_chunk4_simulation_benchmark_pack.py",
]


OPTIONAL_FILES = [
    "scripts/chunk4_simulation_smoke_test.py",
    "backend/app/tests/test_chunk4_simulation_smoke_test.py",
]


IMPORTANT_IMPORTS = [
    "backend.app.main",
    "backend.app.schemas.simulation",
    "backend.app.engines.simulation.interaction_simulation_orchestrator",
    "backend.app.engines.simulation.simulation_quality_scorer",
    "backend.app.engines.simulation.simulation_anti_genericity_validator",
    "backend.app.engines.simulation.simulation_run_store",
    "backend.app.engines.simulation.simulation_benchmark_pack",
    "backend.app.api.simulation_routes",
]


def run_cmd(cmd: list[str], *, timeout: int = 120) -> dict:
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
        "returncode": proc.returncode,
        "output": proc.stdout,
        "ok": proc.returncode == 0,
    }


def check_dirs() -> tuple[list[str], list[str]]:
    ok, missing = [], []
    for rel in EXPECTED_DIRS:
        path = ROOT / rel
        if path.is_dir():
            ok.append(rel)
        else:
            missing.append(rel)
    return ok, missing


def check_files() -> tuple[list[str], list[str]]:
    ok, missing = [], []
    for rel in EXPECTED_FILES:
        path = ROOT / rel
        if path.is_file():
            ok.append(rel)
        else:
            missing.append(rel)
    return ok, missing


def check_optional_files() -> tuple[list[str], list[str]]:
    present, missing = [], []
    for rel in OPTIONAL_FILES:
        path = ROOT / rel
        if path.is_file():
            present.append(rel)
        else:
            missing.append(rel)
    return present, missing


def check_main_not_corrupted() -> tuple[bool, list[str]]:
    main_path = ROOT / "backend/app/main.py"
    if not main_path.exists():
        return False, ["backend/app/main.py missing"]

    text = main_path.read_text(encoding="utf-8")
    problems = []

    bad_literals = [
        r"\nfrom backend.app.api.simulation_routes",
        r"\napp.include_router(simulation_router)",
    ]

    for bad in bad_literals:
        if bad in text:
            problems.append(f"literal escaped newline found in main.py: {bad}")

    if "from backend.app.api.simulation_routes import router as simulation_router" not in text:
        problems.append("simulation router import missing from main.py")

    if "app.include_router(simulation_router)" not in text:
        problems.append("simulation router include missing from main.py")

    if "app = FastAPI" not in text:
        problems.append("FastAPI app declaration missing from main.py")

    return len(problems) == 0, problems


def check_compile_all() -> dict:
    ok = compileall.compile_dir(str(ROOT / "backend"), quiet=1, force=False)
    ok_scripts = compileall.compile_dir(str(ROOT / "scripts"), quiet=1, force=False)
    return {
        "ok": bool(ok and ok_scripts),
        "backend_compile_ok": bool(ok),
        "scripts_compile_ok": bool(ok_scripts),
    }


def check_imports() -> tuple[list[str], list[str]]:
    ok, failed = [], []
    for module_name in IMPORTANT_IMPORTS:
        try:
            importlib.import_module(module_name)
            ok.append(module_name)
        except Exception as exc:
            failed.append(f"{module_name}: {type(exc).__name__}: {exc}")
    return ok, failed


def check_fastapi_app() -> tuple[bool, list[str]]:
    problems = []
    try:
        mod = importlib.import_module("backend.app.main")
        app = getattr(mod, "app", None)
        if app is None:
            problems.append("backend.app.main has no app object")
        else:
            route_paths = sorted({getattr(route, "path", "") for route in app.routes})
            required = ["/simulation/health", "/simulation/run"]
            for path in required:
                if path not in route_paths:
                    problems.append(f"missing FastAPI route: {path}")
    except Exception as exc:
        problems.append(f"FastAPI app import failed: {type(exc).__name__}: {exc}")

    return len(problems) == 0, problems


def main() -> int:
    report = {
        "checks": {},
        "commands": {},
        "summary": {},
    }

    dirs_ok, dirs_missing = check_dirs()
    files_ok, files_missing = check_files()
    optional_present, optional_missing = check_optional_files()
    main_ok, main_problems = check_main_not_corrupted()
    compile_report = check_compile_all()
    imports_ok, imports_failed = check_imports()
    fastapi_ok, fastapi_problems = check_fastapi_app()

    report["checks"]["dirs"] = {
        "ok_count": len(dirs_ok),
        "missing": dirs_missing,
        "passed": not dirs_missing,
    }
    report["checks"]["files"] = {
        "ok_count": len(files_ok),
        "missing": files_missing,
        "passed": not files_missing,
    }
    report["checks"]["optional_files"] = {
        "present": optional_present,
        "missing": optional_missing,
        "passed": True,
    }
    report["checks"]["main_integrity"] = {
        "passed": main_ok,
        "problems": main_problems,
    }
    report["checks"]["compile_all"] = compile_report
    report["checks"]["imports"] = {
        "ok_count": len(imports_ok),
        "failed": imports_failed,
        "passed": not imports_failed,
    }
    report["checks"]["fastapi_app"] = {
        "passed": fastapi_ok,
        "problems": fastapi_problems,
    }

    # Run focused route test if it exists.
    if (ROOT / "backend/app/tests/test_chunk4_simulation_api_routes.py").exists():
        report["commands"]["simulation_api_tests"] = run_cmd(
            ["python", "-m", "pytest", "backend/app/tests/test_chunk4_simulation_api_routes.py", "-q"],
            timeout=120,
        )

    # Run smoke script if it exists.
    if (ROOT / "scripts/chunk4_simulation_smoke_test.py").exists():
        report["commands"]["chunk4_smoke_script"] = run_cmd(
            ["python", "scripts/chunk4_simulation_smoke_test.py"],
            timeout=120,
        )

    # Run full test suite.
    report["commands"]["full_test_suite"] = run_cmd(
        ["python", "-m", "pytest", "backend/app/tests", "-q"],
        timeout=240,
    )

    report["commands"]["git_status"] = run_cmd(
        ["git", "status", "--short"],
        timeout=30,
    )

    passed = True

    for check in report["checks"].values():
        if check.get("passed") is False or check.get("ok") is False:
            passed = False

    for name, command_report in report["commands"].items():
        if name == "git_status":
            continue
        if not command_report.get("ok", False):
            passed = False

    report["summary"] = {
        "passed": passed,
        "message": "Chunks 1–4 integrity verification passed." if passed else "Chunks 1–4 integrity verification failed. Review failed checks above.",
    }

    output_path = ROOT / "reports/chunks_1_to_4_integrity_report.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")

    print(json.dumps(report["summary"], indent=2, sort_keys=True))
    print(f"Full report written to: {output_path}")

    if not passed:
        print("\nFAILED CHECK DETAILS:")
        for name, check in report["checks"].items():
            if check.get("passed") is False or check.get("ok") is False:
                print(f"\n[{name}]")
                print(json.dumps(check, indent=2, sort_keys=True))

        for name, command_report in report["commands"].items():
            if name != "git_status" and not command_report.get("ok", False):
                print(f"\n[{name}]")
                print(command_report["output"][-4000:])

        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

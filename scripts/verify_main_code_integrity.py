from __future__ import annotations

import ast
import importlib
import json
import subprocess
import sys
import traceback
from pathlib import Path
from typing import Any, Dict, List


ROOT = Path(__file__).resolve().parents[1]


EXCLUDED_DIR_PARTS = {
    "__pycache__",
    ".venv",
    ".git",
    ".pytest_cache",
    "node_modules",
}


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def is_excluded(path: Path) -> bool:
    parts = set(path.parts)
    return bool(parts & EXCLUDED_DIR_PARTS)


def is_test_file(path: Path) -> bool:
    return (
        "/tests/" in str(path)
        or path.name.startswith("test_")
        or path.parent.name == "tests"
    )


def module_name_from_path(path: Path) -> str:
    relative = path.relative_to(ROOT).with_suffix("")
    return ".".join(relative.parts)


def run_command(command: List[str], timeout: int = 120) -> Dict[str, Any]:
    try:
        completed = subprocess.run(
            command,
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=timeout,
        )
        return {
            "ok": completed.returncode == 0,
            "returncode": completed.returncode,
            "command": command,
            "output": completed.stdout,
        }
    except subprocess.TimeoutExpired as exc:
        return {
            "ok": False,
            "returncode": None,
            "command": command,
            "output": f"TIMEOUT after {timeout}s\n{exc}",
        }


def collect_main_python_files() -> List[Path]:
    files = []
    for base in [ROOT / "backend", ROOT / "scripts"]:
        if not base.exists():
            continue
        for path in base.rglob("*.py"):
            if is_excluded(path):
                continue
            if is_test_file(path):
                continue
            files.append(path)
    return sorted(files)


def check_ast(files: List[Path]) -> Dict[str, Any]:
    failures = []

    for path in files:
        try:
            ast.parse(path.read_text(encoding="utf-8"))
        except Exception as exc:
            failures.append(
                {
                    "file": rel(path),
                    "error": repr(exc),
                    "traceback": traceback.format_exc(),
                }
            )

    return {
        "passed": not failures,
        "checked_count": len(files),
        "failures": failures,
    }


def check_py_compile(files: List[Path]) -> Dict[str, Any]:
    failures = []

    for path in files:
        result = run_command([sys.executable, "-m", "py_compile", rel(path)], timeout=30)
        if not result["ok"]:
            failures.append(
                {
                    "file": rel(path),
                    "output": result["output"][-4000:],
                }
            )

    return {
        "passed": not failures,
        "checked_count": len(files),
        "failures": failures,
    }


def check_imports(files: List[Path]) -> Dict[str, Any]:
    failures = []
    imported = []

    for path in files:
        if not str(path).startswith(str(ROOT / "backend")):
            continue
        if path.name == "__init__.py":
            continue

        module_name = module_name_from_path(path)

        try:
            importlib.import_module(module_name)
            imported.append(module_name)
        except Exception:
            failures.append(
                {
                    "file": rel(path),
                    "module": module_name,
                    "traceback": traceback.format_exc(),
                }
            )

    return {
        "passed": not failures,
        "imported_count": len(imported),
        "failure_count": len(failures),
        "failures": failures,
    }


def check_critical_modules() -> Dict[str, Any]:
    critical_modules = [
        "backend.app.main",
        "backend.app.schemas.story_generation",
        "backend.app.engines.story_generation.story_intent_interpreter",
        "backend.app.engines.story_generation.generation_mode_controller",
        "backend.app.engines.story_generation.generation_contract_resolver",
        "backend.app.engines.story_generation.handoff_package_loader",
        "backend.app.engines.story_generation.story_context_builder",
        "backend.app.engines.story_generation.world_detail_injection_engine",
        "backend.app.engines.story_generation.scene_blueprint_engine",
        "backend.app.engines.story_generation.scene_beat_planner",
        "backend.app.engines.story_generation.dialogue_beat_engine",
        "backend.app.engines.story_generation.character_voice_engine",
        "backend.app.engines.story_generation.emotional_subtext_engine",
        "backend.app.engines.story_generation.relationship_beat_engine",
        "backend.app.engines.story_generation.knowledge_boundary_validator",
        "backend.app.engines.story_generation.causal_continuity_validator",
        "backend.app.engines.story_generation.consequence_payoff_engine",
    ]

    failures = []
    imported = []

    for module_name in critical_modules:
        try:
            importlib.import_module(module_name)
            imported.append(module_name)
        except Exception:
            failures.append(
                {
                    "module": module_name,
                    "traceback": traceback.format_exc(),
                }
            )

    return {
        "passed": not failures,
        "imported": imported,
        "failures": failures,
    }


def check_expected_files_exist() -> Dict[str, Any]:
    expected = [
        "backend/app/schemas/story_generation.py",
        "backend/app/engines/story_generation/story_intent_interpreter.py",
        "backend/app/engines/story_generation/generation_mode_controller.py",
        "backend/app/engines/story_generation/generation_contract_resolver.py",
        "backend/app/engines/story_generation/handoff_package_loader.py",
        "backend/app/engines/story_generation/story_context_builder.py",
        "backend/app/engines/story_generation/world_detail_injection_engine.py",
        "backend/app/engines/story_generation/scene_blueprint_engine.py",
        "backend/app/engines/story_generation/scene_beat_planner.py",
        "backend/app/engines/story_generation/dialogue_beat_engine.py",
        "backend/app/engines/story_generation/character_voice_engine.py",
        "backend/app/engines/story_generation/emotional_subtext_engine.py",
        "backend/app/engines/story_generation/relationship_beat_engine.py",
        "backend/app/engines/story_generation/knowledge_boundary_validator.py",
        "backend/app/engines/story_generation/causal_continuity_validator.py",
        "backend/app/engines/story_generation/consequence_payoff_engine.py",
    ]

    missing = [path for path in expected if not (ROOT / path).exists()]

    return {
        "passed": not missing,
        "expected_count": len(expected),
        "missing": missing,
    }


def check_git_status() -> Dict[str, Any]:
    return run_command(["git", "status", "--short"], timeout=30)


def main() -> int:
    files = collect_main_python_files()

    report: Dict[str, Any] = {
        "project_root": str(ROOT),
        "main_python_file_count": len(files),
        "main_python_files": [rel(path) for path in files],
        "checks": {},
        "commands": {},
    }

    report["checks"]["expected_files_exist"] = check_expected_files_exist()
    report["checks"]["ast_parse"] = check_ast(files)
    report["checks"]["py_compile"] = check_py_compile(files)
    report["checks"]["backend_imports"] = check_imports(files)
    report["checks"]["critical_modules"] = check_critical_modules()

    report["commands"]["full_pytest_suite"] = run_command(
        [sys.executable, "-m", "pytest", "backend/app/tests", "-q"],
        timeout=180,
    )
    report["commands"]["git_status"] = check_git_status()

    passed = True

    for check in report["checks"].values():
        if not check.get("passed", False):
            passed = False

    if not report["commands"]["full_pytest_suite"].get("ok", False):
        passed = False

    report["summary"] = {
        "passed": passed,
        "message": (
            "Main code integrity verification passed."
            if passed
            else "Main code integrity verification failed. Review failed checks below."
        ),
    }

    output_path = ROOT / "reports/main_code_integrity_report.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")

    print(json.dumps(report["summary"], indent=2, sort_keys=True))
    print(f"Full report written to: {output_path}")

    if not passed:
        print("\nFAILED CHECK DETAILS:")

        for name, check in report["checks"].items():
            if not check.get("passed", False):
                print(f"\n[{name}]")
                print(json.dumps(check, indent=2, sort_keys=True)[-6000:])

        for name, command in report["commands"].items():
            if name != "git_status" and not command.get("ok", False):
                print(f"\n[{name}]")
                print(command.get("output", "")[-6000:])

        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

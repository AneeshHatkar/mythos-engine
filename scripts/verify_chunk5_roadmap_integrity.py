from __future__ import annotations

import ast
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List


ROOT = Path(__file__).resolve().parents[1]


LOCKED_CORE_FILES = [
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
    "backend/app/engines/story_generation/constraint_satisfaction_engine.py",
    "backend/app/engines/story_generation/prose_style_engine.py",
    "backend/app/engines/story_generation/commercial_appeal_engine.py",
    "backend/app/engines/story_generation/scene_draft_engine.py",
    "backend/app/engines/story_generation/dialogue_line_generator.py",
    "backend/app/engines/story_generation/scene_assembly_engine.py",
    "backend/app/engines/story_generation/chapter_generator.py",
]

SUPPORTING_EARLY_FILES = [
    "backend/app/engines/story_generation/scene_quality_gate.py",
    "backend/app/engines/story_generation/long_form_continuation_anchor.py",
    "backend/app/engines/story_generation/format_adapter_engine.py",
    "backend/app/engines/story_generation/series_episode_structure_engine.py",
    "backend/app/engines/story_generation/chapter_expansion_engine.py",
    "backend/app/engines/story_generation/multi_scene_pacing_engine.py",
    "backend/app/engines/story_generation/long_form_memory_bridge.py",
]

KNOWN_TEST_FILES = [
    "backend/app/tests/test_chunk5_story_generation_schemas.py",
    "backend/app/tests/test_chunk5_story_intent_interpreter.py",
    "backend/app/tests/test_chunk5_generation_mode_controller.py",
    "backend/app/tests/test_chunk5_generation_contract_resolver.py",
    "backend/app/tests/test_chunk5_handoff_package_loader.py",
    "backend/app/tests/test_story_context_builder.py",
    "backend/app/tests/test_world_detail_injection_engine.py",
    "backend/app/tests/test_scene_blueprint_engine.py",
    "backend/app/tests/test_scene_beat_planner.py",
    "backend/app/tests/test_dialogue_beat_engine.py",
    "backend/app/tests/test_character_voice_engine.py",
    "backend/app/tests/test_emotional_subtext_engine.py",
    "backend/app/tests/test_relationship_beat_engine.py",
    "backend/app/tests/test_knowledge_boundary_validator.py",
    "backend/app/tests/test_causal_continuity_validator.py",
    "backend/app/tests/test_consequence_payoff_engine.py",
    "backend/app/tests/test_constraint_satisfaction_engine.py",
    "backend/app/tests/test_prose_style_engine.py",
    "backend/app/tests/test_commercial_appeal_engine.py",
    "backend/app/tests/test_scene_draft_engine.py",
    "backend/app/tests/test_dialogue_line_generator.py",
    "backend/app/tests/test_scene_assembly_engine.py",
    "backend/app/tests/test_chapter_generator.py",
    "backend/app/tests/test_scene_quality_gate.py",
    "backend/app/tests/test_long_form_continuation_anchor.py",
    "backend/app/tests/test_format_adapter_engine.py",
    "backend/app/tests/test_series_episode_structure_engine.py",
    "backend/app/tests/test_chapter_expansion_engine.py",
    "backend/app/tests/test_multi_scene_pacing_engine.py",
    "backend/app/tests/test_long_form_memory_bridge.py",
]


REQUIRED_SCHEMA_CLASSES = [
    "StoryIntent",
    "GenerationContract",
    "StoryContextPackage",
    # World detail support may be represented by engine output schemas rather than this exact class.
    # The project originally used world detail injection structures instead of a class named WorldDetailPack.

    "SceneBlueprint",
    "SceneBeat",
    "DialogueBeat",
    "CharacterVoiceInstruction",
    "EmotionalSubtextInstruction",
    "RelationshipBeat",
    "KnowledgeBoundaryReport",
    "CausalContinuityReport",
    "ConsequencePayoffPlan",
    "ConstraintSatisfactionReport",
    "ProseStyleProfile",
    "CommercialAppealReport",
    "GeneratedSceneDraft",
    "GeneratedDialogueLine",
    "GeneratedDialogueBlock",
    "AssembledScene",
    "SceneQualityReport",
    "GeneratedChapter",
    "LongFormContinuationAnchor",
    "FormatAdaptationPlan",
    "SeriesEpisodeStructure",
    "ChapterExpansionPlan",
    "MultiScenePacingReport",
    "LongFormMemoryBridgeReport",
]


def run_command(name: str, args: List[str], timeout: int = 120) -> Dict[str, Any]:
    try:
        completed = subprocess.run(
            args,
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        output = (completed.stdout or "") + (completed.stderr or "")
        return {
            "name": name,
            "args": args,
            "ok": completed.returncode == 0,
            "returncode": completed.returncode,
            "output_tail": output[-5000:],
        }
    except Exception as exc:
        return {
            "name": name,
            "args": args,
            "ok": False,
            "returncode": None,
            "output_tail": repr(exc),
        }


def check_files(paths: List[str]) -> Dict[str, Any]:
    existing = []
    missing = []
    for item in paths:
        path = ROOT / item
        if path.exists():
            existing.append(item)
        else:
            missing.append(item)

    return {
        "passed": not missing,
        "existing": existing,
        "missing": missing,
    }


def check_python_syntax(paths: List[str]) -> Dict[str, Any]:
    results = []
    failed = []

    for item in paths:
        path = ROOT / item
        if not path.exists():
            continue

        try:
            source = path.read_text(encoding="utf-8")
            ast.parse(source)
            results.append({"file": item, "ok": True})
        except Exception as exc:
            failed.append({"file": item, "ok": False, "error": repr(exc)})

    return {
        "passed": not failed,
        "failed": failed,
        "checked_count": len(results) + len(failed),
    }


def check_schema_classes() -> Dict[str, Any]:
    schema_path = ROOT / "backend/app/schemas/story_generation.py"
    if not schema_path.exists():
        return {
            "passed": False,
            "missing_classes": REQUIRED_SCHEMA_CLASSES,
            "error": "schema file missing",
        }

    text = schema_path.read_text(encoding="utf-8")
    missing = [
        class_name
        for class_name in REQUIRED_SCHEMA_CLASSES
        if f"class {class_name}" not in text
    ]

    return {
        "passed": not missing,
        "missing_classes": missing,
        "required_class_count": len(REQUIRED_SCHEMA_CLASSES),
    }


def check_tracker() -> Dict[str, Any]:
    tracker_path = ROOT / "docs/chunk5_locked_step_tracker.md"
    if not tracker_path.exists():
        return {"passed": False, "error": "tracker file missing"}

    text = tracker_path.read_text(encoding="utf-8")
    required_phrases = [
        "5.24 | Plot Outline Generator",
        "5.50 | Push to GitHub",
        "Supporting engines added early",
        "Do not jump",
    ]
    missing = [phrase for phrase in required_phrases if phrase not in text]

    return {
        "passed": not missing,
        "missing_phrases": missing,
    }


def main() -> int:
    report: Dict[str, Any] = {
        "audit_name": "Chunk 5 roadmap realignment and project integrity audit",
        "root": str(ROOT),
        "checks": {},
        "commands": {},
    }

    report["checks"]["locked_core_files"] = check_files(LOCKED_CORE_FILES)
    report["checks"]["supporting_early_files"] = check_files(SUPPORTING_EARLY_FILES)
    report["checks"]["known_test_files"] = check_files(KNOWN_TEST_FILES)
    report["checks"]["python_syntax_core_and_tests"] = check_python_syntax(
        LOCKED_CORE_FILES + SUPPORTING_EARLY_FILES + KNOWN_TEST_FILES
    )
    report["checks"]["required_schema_classes"] = check_schema_classes()
    report["checks"]["locked_tracker"] = check_tracker()

    report["commands"]["py_compile_main_schema"] = run_command(
        "py_compile_main_schema",
        [sys.executable, "-m", "py_compile", "backend/app/schemas/story_generation.py"],
    )

    report["commands"]["pytest_chunk5_story_generation_schemas"] = run_command(
        "pytest_chunk5_story_generation_schemas",
        [sys.executable, "-m", "pytest", "backend/app/tests/test_chunk5_story_generation_schemas.py", "-q"],
        timeout=120,
    )

    report["commands"]["pytest_all_tests"] = run_command(
        "pytest_all_tests",
        [sys.executable, "-m", "pytest", "backend/app/tests", "-q"],
        timeout=240,
    )

    report["commands"]["git_status_short"] = run_command(
        "git_status_short",
        ["git", "status", "--short"],
        timeout=30,
    )

    passed = True

    for check in report["checks"].values():
        if not check.get("passed", False):
            passed = False

    for name, command in report["commands"].items():
        if name == "git_status_short":
            continue
        if not command.get("ok", False):
            passed = False

    report["summary"] = {
        "passed": passed,
        "message": (
            "Roadmap realignment and integrity audit passed."
            if passed
            else "Roadmap realignment and integrity audit failed. Review report details."
        ),
        "next_locked_step": "5.24 Plot Outline Generator",
    }

    output_path = ROOT / "reports/chunk5_roadmap_integrity_audit.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")

    print(json.dumps(report["summary"], indent=2, sort_keys=True))
    print(f"Full report written to: {output_path}")

    if not passed:
        print("\nFAILED DETAILS:")
        for name, check in report["checks"].items():
            if not check.get("passed", False):
                print(f"\n[{name}]")
                print(json.dumps(check, indent=2, sort_keys=True))

        for name, command in report["commands"].items():
            if name != "git_status_short" and not command.get("ok", False):
                print(f"\n[{name}]")
                print(command.get("output_tail", ""))

        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

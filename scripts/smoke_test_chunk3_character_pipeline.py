#!/usr/bin/env python3
"""Smoke test for Chunk 3 character intelligence pipeline.

This script can run in two modes:

1. In-process mode, no server needed:
   python scripts/smoke_test_chunk3_character_pipeline.py

2. API mode, server needed:
   MYTHOS_CHARACTER_SMOKE_MODE=api python scripts/smoke_test_chunk3_character_pipeline.py

For API mode, start the app first:
   PYTHONPATH=. uvicorn backend.app.main:app --reload
"""

import json
import os
import sys
from pathlib import Path

import httpx

from backend.app.benchmarks.character_benchmark_pack import chunk3_character_benchmark_cases
from backend.app.engines.character.character_full_profile_orchestrator import CharacterFullProfileOrchestrator
from backend.app.services.character_run_store import CharacterRunStore


BASE_URL = os.getenv("MYTHOS_API_BASE_URL", "http://127.0.0.1:8000")
MODE = os.getenv("MYTHOS_CHARACTER_SMOKE_MODE", "local")


def run_local() -> int:
    print("Running MythOS Engine Chunk 3 character pipeline smoke test in local mode...")

    engine = CharacterFullProfileOrchestrator()
    store = CharacterRunStore("reports/characters_smoke")

    cases = chunk3_character_benchmark_cases()
    results = []

    for case in cases:
        result = engine.run(case["payload"])
        result_data = result.model_dump()
        profile = result_data["data"]["character_full_profile"]
        report = result_data["data"]["orchestration_report"]
        quality = profile["validation"].get("quality_report", {})

        store_result = store.save_character_profile(
            character_id=profile["character_id"],
            profile=profile,
            orchestration_report=report,
            quality_report=quality,
            learning_metadata=result_data["data"].get("learning_metadata", {}),
            project_id=case["payload"]["character_seed"].get("project_id", "benchmark_project"),
            universe_id=case["payload"]["character_seed"].get("universe_id", "benchmark_universe"),
        )

        passed = (
            result.success
            and report["profile_tier"] in case["expected_profile_tier"]
            and float(quality.get("overall_quality_score", 0.0)) >= float(case["expected_min_quality"])
        )

        results.append(
            {
                "case_id": case["case_id"],
                "passed": passed,
                "character_id": profile["character_id"],
                "profile_tier": report["profile_tier"],
                "quality_score": quality.get("overall_quality_score", 0.0),
                "stored": store_result["success"],
            }
        )

        print(f"- {case['case_id']}: {'PASS' if passed else 'FAIL'} | tier={report['profile_tier']} | quality={quality.get('overall_quality_score', 0.0)}")

    summary = {
        "mode": "local",
        "case_count": len(results),
        "passed_count": sum(1 for item in results if item["passed"]),
        "failed_count": sum(1 for item in results if not item["passed"]),
        "results": results,
        "store_summary": store.get_store_summary(),
    }

    output_path = Path("reports/characters_smoke/chunk3_character_smoke_summary.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")

    print(f"Saved smoke summary to: {output_path}")

    if summary["failed_count"] > 0:
        return 1

    print("Chunk 3 character pipeline smoke test passed.")
    return 0


def run_api() -> int:
    print("Running MythOS Engine Chunk 3 character pipeline smoke test in API mode...")
    print(f"Target: {BASE_URL}")

    cases = chunk3_character_benchmark_cases()
    results = []

    with httpx.Client(timeout=20.0) as client:
        health = client.get(f"{BASE_URL}/character/engines/health")
        health.raise_for_status()

        for case in cases:
            response = client.post(
                f"{BASE_URL}/character/engines/full-profile-orchestrator",
                json={
                    "payload": case["payload"],
                    "persist": True,
                    "project_id": case["payload"]["character_seed"].get("project_id", "benchmark_project"),
                    "universe_id": case["payload"]["character_seed"].get("universe_id", "benchmark_universe"),
                    "run_label": f"smoke:{case['case_id']}",
                },
            )
            response.raise_for_status()
            data = response.json()

            profile = data["data"]["character_full_profile"]
            report = data["data"]["orchestration_report"]
            quality = profile["validation"].get("quality_report", {})

            passed = (
                data["success"]
                and report["profile_tier"] in case["expected_profile_tier"]
                and float(quality.get("overall_quality_score", 0.0)) >= float(case["expected_min_quality"])
            )

            results.append(
                {
                    "case_id": case["case_id"],
                    "passed": passed,
                    "character_id": profile["character_id"],
                    "profile_tier": report["profile_tier"],
                    "quality_score": quality.get("overall_quality_score", 0.0),
                    "api_persisted": data.get("profile_persistence", {}).get("persisted", False),
                }
            )

            print(f"- {case['case_id']}: {'PASS' if passed else 'FAIL'} | tier={report['profile_tier']} | quality={quality.get('overall_quality_score', 0.0)}")

    summary = {
        "mode": "api",
        "case_count": len(results),
        "passed_count": sum(1 for item in results if item["passed"]),
        "failed_count": sum(1 for item in results if not item["passed"]),
        "results": results,
    }

    output_path = Path("reports/characters_smoke/chunk3_character_api_smoke_summary.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")

    print(f"Saved API smoke summary to: {output_path}")

    if summary["failed_count"] > 0:
        return 1

    print("Chunk 3 character API smoke test passed.")
    return 0


def main() -> int:
    if MODE == "api":
        return run_api()
    return run_local()


if __name__ == "__main__":
    sys.exit(main())

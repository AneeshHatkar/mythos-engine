import json
import sys
from pathlib import Path

import httpx


BASE_URL = "http://127.0.0.1:8000"


def assert_status(response: httpx.Response, expected: int, label: str) -> dict:
    if response.status_code != expected:
        print(f"FAILED: {label}")
        print(f"Expected status: {expected}")
        print(f"Actual status: {response.status_code}")
        print(response.text)
        sys.exit(1)

    try:
        return response.json()
    except Exception:
        print(f"FAILED: {label} did not return JSON")
        print(response.text)
        sys.exit(1)


def assert_true(condition: bool, label: str) -> None:
    if not condition:
        print(f"FAILED: {label}")
        sys.exit(1)


def main() -> None:
    print("Running MythOS Engine Chunk 2 world pipeline smoke test...")
    print(f"Target: {BASE_URL}")

    with httpx.Client(timeout=60.0) as client:
        health = assert_status(
            client.get(f"{BASE_URL}/world/engines/health"),
            200,
            "world engine health",
        )

        assert_true(health["status"] == "ok", "world engine health status")
        print("World engine API health OK")

        templates = assert_status(
            client.get(f"{BASE_URL}/world/engines/templates"),
            200,
            "world template catalog",
        )

        template_count = templates["data"]["template_count"]
        assert_true(template_count >= 7, "template count >= 7")
        print(f"Template catalog OK: {template_count} templates")

        payload = {
            "template_id": "seven_novel_saga",
            "world_name": "Velmora",
            "seed_premise": (
                "Velmora is a late imperial collapse world where noble academies, "
                "relic mines, oath law, sealed archives, family-name trust, "
                "class hierarchy, forbidden exams, and 27 destiny-bearing students "
                "destabilize civilization."
            ),
            "user_rating": 9,
            "source_mode": "human_approved_synthetic",
            "export_format": "markdown_and_json",
            "audience": "internal_research_and_development",
        }

        orchestrated = assert_status(
            client.post(f"{BASE_URL}/world/engines/orchestrate", json=payload),
            200,
            "world orchestration",
        )

        assert_true(orchestrated["success"] is True, "orchestration success")

        data = orchestrated["data"]
        world_state = data["world_state"]
        summary = data["orchestration_summary"]

        print(f"Orchestrator engines run: {summary['engine_count']}")
        print(f"Successful engines: {summary['successful_engine_count']}")
        print(f"Failed engines: {summary['failed_engine_count']}")

        assert_true(summary["failed_engine_count"] == 0, "no failed engines")
        assert_true(summary["core_section_completion_ratio"] >= 0.9, "core section completion >= 0.9")

        required_sections = [
            "identity",
            "rules",
            "chronology",
            "geography",
            "environment",
            "infrastructure",
            "demographics",
            "society",
            "power_structure",
            "military_security",
            "economy",
            "law",
            "belief",
            "culture",
            "knowledge_education",
            "institutions",
            "technology_magic_science",
            "species_creatures",
            "artifacts",
            "aesthetic_texture",
            "civilization_pressure",
            "causality_graph",
            "quality_summary",
            "dataset_metadata",
            "snapshot",
            "world_bible_export",
        ]

        for section in required_sections:
            assert_true(section in world_state, f"{section} exists")
            assert_true(world_state[section] not in (None, {}, [], ""), f"{section} is not empty")

        quality = world_state["quality_summary"]
        dataset = world_state["dataset_metadata"]
        snapshot = world_state["snapshot"]
        export_package = world_state["world_bible_export"]

        print(f"Quality tier: {quality.get('quality_tier')}")
        print(f"Training eligible: {dataset.get('training_eligible')}")
        print(f"Do not train: {dataset.get('do_not_train')}")
        print(f"Snapshot ID: {snapshot.get('snapshot_id')}")
        print(f"World Bible Export ID: {export_package.get('export_id')}")

        assert_true("quality_tier" in quality, "quality tier exists")
        assert_true("training_eligible" in dataset, "training eligibility exists")
        assert_true("do_not_train" in dataset, "do_not_train flag exists")
        assert_true(snapshot.get("snapshot_id", "").startswith("wsnap_"), "snapshot id valid")
        assert_true(export_package.get("export_id", "").startswith("wbible_"), "world bible export id valid")
        assert_true("world_bible_markdown" in export_package, "markdown export exists")
        assert_true("world_bible_json" in export_package, "json export exists")

        markdown = export_package["world_bible_markdown"]
        assert_true("# " in markdown, "markdown has title")
        assert_true("## Executive Summary" in markdown, "markdown has executive summary")
        assert_true("## World Identity" in markdown, "markdown has world identity")
        assert_true("## Civilization Pressure" in markdown, "markdown has civilization pressure")

        output_dir = Path("exports/world_bibles")
        output_dir.mkdir(parents=True, exist_ok=True)

        markdown_path = output_dir / "chunk2_smoke_test_world_bible.md"
        json_path = output_dir / "chunk2_smoke_test_world_bible.json"

        markdown_path.write_text(markdown, encoding="utf-8")
        json_path.write_text(
            json.dumps(export_package["world_bible_json"], indent=2),
            encoding="utf-8",
        )

        print(f"Saved smoke test markdown export: {markdown_path}")
        print(f"Saved smoke test JSON export: {json_path}")

        quality_check = assert_status(
            client.post(
                f"{BASE_URL}/world/engines/quality",
                json={"world_state": world_state},
            ),
            200,
            "quality endpoint",
        )

        assert_true(quality_check["success"] is True, "quality endpoint success")
        assert_true("audit_integration" in quality_check, "quality audit metadata exists")
        print("Quality endpoint OK")

    print("Chunk 2 world pipeline smoke test passed.")


if __name__ == "__main__":
    main()

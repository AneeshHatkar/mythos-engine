import json
import sys
from pathlib import Path
from typing import Any, Dict

import httpx


BASE_URL = "http://127.0.0.1:8000"


def assert_status(response: httpx.Response, expected: int, label: str) -> Dict[str, Any]:
    if response.status_code != expected:
        print(f"FAILED: {label}")
        print(f"Expected status: {expected}")
        print(f"Actual status: {response.status_code}")
        print(response.text)
        sys.exit(1)

    try:
        return response.json()
    except json.JSONDecodeError:
        return {}


def main() -> None:
    print("Running MythOS Engine foundation smoke test...")
    print(f"Target: {BASE_URL}")

    with httpx.Client(timeout=10.0) as client:
        health = assert_status(client.get(f"{BASE_URL}/health"), 200, "health")
        print(f"Health OK: {health['status']}")

        project = assert_status(
            client.post(
                f"{BASE_URL}/projects",
                json={
                    "name": "Smoke Test MythOS Project",
                    "description": "Created by smoke_test_foundation_api.py",
                },
            ),
            201,
            "create project",
        )
        project_id = project["project_id"]
        print(f"Project created: {project_id}")

        universe = assert_status(
            client.post(
                f"{BASE_URL}/projects/{project_id}/universes",
                json={
                    "project_id": project_id,
                    "name": "Smoke Test Universe",
                    "seed_premise": (
                        "A dark academy civilization where 27 destined people "
                        "reshape the world across multiple timelines."
                    ),
                    "genres": ["dark_academy", "political_fantasy"],
                    "target_formats": ["seven_novel_series"],
                },
            ),
            201,
            "create universe",
        )
        universe_id = universe["universe_id"]
        print(f"Universe created: {universe_id}")

        seeded = assert_status(
            client.post(f"{BASE_URL}/registry/seed/foundation"),
            201,
            "seed foundation registry",
        )
        print(f"Registry seeded: {len(seeded)} types returned")

        canon_lock = assert_status(
            client.post(
                f"{BASE_URL}/canon/locks",
                json={
                    "project_id": project_id,
                    "universe_id": universe_id,
                    "object_type": "world_rule",
                    "object_id": "destined_people_count",
                    "field_path": "destined_people.total_count",
                    "locked_value": {"total_count": 27},
                    "reason": "Smoke test locks the destined people count.",
                },
            ),
            201,
            "create canon lock",
        )
        print(f"Canon lock created: {canon_lock['canon_lock_id']}")

        branch = assert_status(
            client.post(
                f"{BASE_URL}/branches",
                json={
                    "project_id": project_id,
                    "universe_id": universe_id,
                    "branch_name": "Smoke Test Alternate Timeline",
                    "branch_type": "alternate_timeline",
                    "reason": "Smoke test branch.",
                },
            ),
            201,
            "create branch",
        )
        print(f"Branch created: {branch['branch_id']}")

        version = assert_status(
            client.post(
                f"{BASE_URL}/versions",
                json={
                    "project_id": project_id,
                    "universe_id": universe_id,
                    "object_type": "universe",
                    "object_id": universe_id,
                    "version_label": "smoke-v0.1",
                    "summary": "Smoke test universe version.",
                    "snapshot": {"universe_name": universe["name"]},
                },
            ),
            201,
            "create version",
        )
        print(f"Version created: {version['version_id']}")

        audit = assert_status(
            client.post(
                f"{BASE_URL}/audit/records",
                json={
                    "project_id": project_id,
                    "universe_id": universe_id,
                    "engine_name": "foundation.smoke_test",
                    "event_type": "engine_run",
                    "input_summary": "Smoke test input.",
                    "output_summary": "Smoke test output.",
                    "quality_score": 1.0,
                },
            ),
            201,
            "create audit record",
        )
        print(f"Audit created: {audit['audit_id']}")

        feedback = assert_status(
            client.post(
                f"{BASE_URL}/feedback",
                json={
                    "project_id": project_id,
                    "universe_id": universe_id,
                    "object_type": "universe",
                    "object_id": universe_id,
                    "feedback_type": "smoke_test_feedback",
                    "rating": 10,
                    "comment": "Foundation smoke test succeeded.",
                },
            ),
            201,
            "create feedback",
        )
        print(f"Feedback created: {feedback['feedback_id']}")

        export_endpoints = [
            ("json", "/exports/json"),
            ("csv", "/exports/csv"),
            ("markdown", "/exports/markdown"),
            ("db_snapshot", "/exports/db-snapshot"),
        ]

        for label, endpoint in export_endpoints:
            export_record = assert_status(
                client.post(
                    f"{BASE_URL}{endpoint}",
                    json={"project_id": project_id},
                ),
                201,
                f"create {label} export",
            )

            path = Path(export_record["file_path"])
            if not path.exists():
                print(f"FAILED: {label} export path does not exist: {path}")
                sys.exit(1)

            print(f"{label} export created: {path}")

        exports = assert_status(
            client.get(f"{BASE_URL}/exports?project_id={project_id}"),
            200,
            "list exports",
        )
        print(f"Exports listed: {len(exports)} records")

    print("Foundation smoke test passed.")


if __name__ == "__main__":
    main()
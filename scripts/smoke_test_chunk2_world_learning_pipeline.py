#!/usr/bin/env python3
"""Smoke test for Upgrade Pass B world learning integration."""

import json
import sys
from pathlib import Path

from backend.app.services.learning_integration import LearningIntegrationService
from backend.app.services.world_learning_adapter import WorldLearningAdapter
from backend.app.services.world_learning_metadata_verifier import WorldLearningMetadataVerifier


def sample_world_profile():
    return {
        "world_id": "world_smoke_velmora",
        "world_name": "Velmora Smoke",
        "quality_score": 0.84,
        "originality_score": 0.78,
        "consistency_score": 0.86,
        "social_classes": ["erased", "academy_sponsored", "old_nobility"],
        "magic_rules": [
            "relic power requires contract cost",
            "memory magic leaves social trace",
        ],
        "legal_constraints": [
            "erased family names cannot testify without sponsor",
            "academy access requires sponsor, exam route, debt, or illegal patronage",
        ],
        "factions": ["Oath Court", "Relic Guild", "Archive Church"],
        "academy_access": ["sponsor seat", "exam route", "debt contract", "illegal patron route"],
        "economy": ["relic labor economy", "memory-tax bureaucracy"],
        "culture": ["public names carry legal trust", "oath-breaking marks family reputation"],
        "geography": ["capital rings", "outer academy district", "relic mines"],
        "taboos": ["false testimony under oath magic", "memory theft without witness"],
    }


def sample_world_result():
    return {
        "success": True,
        "engine_name": "world.world_orchestrator_engine",
        "data": {
            "world_profile": sample_world_profile(),
        },
        "warnings": [],
        "errors": [],
        "generated_object_ids": ["world_smoke_velmora"],
    }


def main() -> int:
    print("Running Upgrade Pass B world learning smoke test...")

    root = Path("reports/world_learning_smoke")
    root.mkdir(parents=True, exist_ok=True)

    integration = LearningIntegrationService(
        learning_root=root / "learning",
        provenance_root=root / "provenance",
        training_queue_root=root / "training_queue",
        embedding_root=root / "embeddings",
    )

    adapter = WorldLearningAdapter(integration_service=integration)
    verifier = WorldLearningMetadataVerifier(adapter=adapter)

    result_payload = sample_world_result()

    normalized = adapter.normalize_world_result(
        result_payload=result_payload,
        project_id="proj_world_smoke",
        universe_id="velmora_smoke",
    )

    verification = verifier.verify_world_result(
        result_payload=result_payload,
        project_id="proj_world_smoke",
        universe_id="velmora_smoke",
        allow_synthesis=True,
    )

    registration = adapter.register_world_engine_result(
        result_payload=result_payload,
        project_id="proj_world_smoke",
        universe_id="velmora_smoke",
        enforce_quality_gates=True,
    )

    summary = integration.get_global_learning_summary()

    checks = {
        "normalized_world_id": normalized["world_id"] == "world_smoke_velmora",
        "contract_usable": verification["world_to_character_contract_report"]["contract_usable"] is True,
        "global_learning_ready": verification["readiness_report"]["global_learning_ready"] is True,
        "training_queue_ready": verification["readiness_report"]["training_queue_ready"] is True,
        "registered": registration["registered"] is True,
        "embedding_registered": registration["learning_registration"]["embedding_registered"] is True,
        "training_enqueued": registration["learning_registration"]["training_enqueued"] is True,
        "learning_registry_has_metadata": summary["learning_registry"]["counts"]["engine_learning_metadata"] >= 1,
        "provenance_has_record": summary["provenance"]["record_count"] >= 1,
        "embedding_registry_has_record": summary["embedding_registry"]["record_count"] >= 1,
        "training_queue_has_record": summary["training_queue"]["record_count"] >= 1,
    }

    smoke_summary = {
        "success": all(checks.values()),
        "checks": checks,
        "normalized": {
            "world_id": normalized["world_id"],
            "target_object_type": normalized["learning_metadata"]["target_object_type"],
            "world_to_character_contract": normalized["world_to_character_contract"],
        },
        "verification": {
            "metadata_synthesized": verification["metadata_synthesized"],
            "readiness_report": verification["readiness_report"],
            "contract_report": verification["world_to_character_contract_report"],
        },
        "registration": {
            "registered": registration["registered"],
            "quality_gate_report": registration["quality_gate_report"],
            "world_id": registration["world_id"],
        },
        "global_learning_summary": summary,
    }

    output_path = root / "chunk2_world_learning_smoke_summary.json"
    output_path.write_text(
        json.dumps(smoke_summary, indent=2, sort_keys=True, ensure_ascii=False),
        encoding="utf-8",
    )

    for name, passed in checks.items():
        print(f"- {name}: {'PASS' if passed else 'FAIL'}")

    print(f"Saved smoke summary to: {output_path}")

    if not smoke_summary["success"]:
        print("World learning smoke test failed.")
        return 1

    print("Upgrade Pass B world learning smoke test passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

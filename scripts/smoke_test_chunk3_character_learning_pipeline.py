#!/usr/bin/env python3
"""Smoke test for Upgrade Pass C character learning integration."""

import json
import sys
from pathlib import Path

from backend.app.services.character_learning_adapter import CharacterLearningAdapter
from backend.app.services.character_learning_metadata_verifier import CharacterLearningMetadataVerifier
from backend.app.services.learning_integration import LearningIntegrationService


def sample_world_contract():
    return {
        "contract_id": "worldchar_smoke_velmora",
        "world_id": "world_smoke_velmora",
        "social_classes": ["erased", "academy_sponsored", "old_nobility"],
        "power_laws": ["relic power requires cost and counterplay"],
        "legal_constraints": ["distrusted family names require sponsor to testify"],
        "education_access_constraints": ["sponsor seat", "exam route", "debt contract"],
        "character_permission_boundaries": [
            "characters must obey class/status access constraints unless an explicit exception route exists",
            "skills and limit-breaks must obey world power laws, costs, counters, and exceptions",
        ],
    }


def sample_character_profile():
    return {
        "character_id": "char_smoke_kael",
        "identity": {
            "character_id": "char_smoke_kael",
            "name": "Kael Veyran",
            "role": "protagonist",
        },
        "origin": {
            "social_class": "academy_sponsored",
            "family_name_status": "distrusted",
            "origin_profile": {
                "education_access": "conditional sponsor seat",
            },
        },
        "psychology": {
            "psychology_profile": {
                "core_wound": "believes belonging can be revoked after public failure",
            },
            "goal_profile": {
                "surface_goal": "survive academy ranking",
                "hidden_goal": "prove the ranking system is edited",
                "true_need": "belonging is not permission",
            },
            "memory_records": [
                {"memory_id": "mem_core", "content": "public failure and family secret memory"}
            ],
        },
        "power": {
            "skill_ontology": {
                "skill_family": "cognitive_inference",
            },
            "adaptability_profile": {
                "cost_model": "identity instability after breakthrough",
            },
        },
        "relationships": {
            "relationship_readiness_profile": {
                "relationship_readiness_family": "high_loyalty_power_broker_readiness",
            }
        },
        "dialogue": {
            "dialogue_voice_profile": {
                "voice_family": "controlled_subtext_voice",
            }
        },
        "validation": {
            "quality_report": {
                "overall_quality_score": 0.86,
            },
            "originality_report": {
                "overall_originality_score": 0.8,
            },
            "consistency_report": {
                "overall_consistency_score": 0.9,
            },
            "anti_genericity_report": {
                "genericity_risk_score": 0.16,
            },
        },
    }


def sample_character_result():
    return {
        "success": True,
        "engine_name": "character.full_profile_orchestrator",
        "data": {
            "character_full_profile": sample_character_profile(),
        },
        "warnings": [],
        "errors": [],
        "generated_object_ids": ["char_smoke_kael"],
    }


def main() -> int:
    print("Running Upgrade Pass C character learning smoke test...")

    root = Path("reports/character_learning_smoke")
    root.mkdir(parents=True, exist_ok=True)

    integration = LearningIntegrationService(
        learning_root=root / "learning",
        provenance_root=root / "provenance",
        training_queue_root=root / "training_queue",
        embedding_root=root / "embeddings",
    )

    adapter = CharacterLearningAdapter(integration_service=integration)
    verifier = CharacterLearningMetadataVerifier(adapter=adapter)

    result_payload = sample_character_result()
    world_contract = sample_world_contract()

    normalized = adapter.normalize_character_result(
        result_payload=result_payload,
        project_id="proj_character_smoke",
        universe_id="velmora_smoke",
        world_contract=world_contract,
    )

    verification = verifier.verify_character_result(
        result_payload=result_payload,
        project_id="proj_character_smoke",
        universe_id="velmora_smoke",
        world_contract=world_contract,
        allow_synthesis=True,
    )

    registration = adapter.register_character_engine_result(
        result_payload=result_payload,
        project_id="proj_character_smoke",
        universe_id="velmora_smoke",
        world_contract=world_contract,
        enforce_quality_gates=True,
    )

    summary = integration.get_global_learning_summary()

    checks = {
        "normalized_character_id": normalized["character_id"] == "char_smoke_kael",
        "world_contract_valid": verification["world_contract_report"]["world_contract_valid"] is True,
        "chunk4_ready": verification["readiness_report"]["chunk4_ready"] is True,
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
            "character_id": normalized["character_id"],
            "target_object_type": normalized["learning_metadata"]["target_object_type"],
            "world_contract_validation": normalized["world_contract_validation"],
            "chunk4_handoff_contract": normalized["chunk4_handoff_contract"],
        },
        "verification": {
            "metadata_synthesized": verification["metadata_synthesized"],
            "readiness_report": verification["readiness_report"],
            "world_contract_report": verification["world_contract_report"],
            "chunk4_handoff_report": verification["chunk4_handoff_report"],
        },
        "registration": {
            "registered": registration["registered"],
            "quality_gate_report": registration["quality_gate_report"],
            "character_id": registration["character_id"],
        },
        "global_learning_summary": summary,
    }

    output_path = root / "chunk3_character_learning_smoke_summary.json"
    output_path.write_text(
        json.dumps(smoke_summary, indent=2, sort_keys=True, ensure_ascii=False),
        encoding="utf-8",
    )

    for name, passed in checks.items():
        print(f"- {name}: {'PASS' if passed else 'FAIL'}")

    print(f"Saved smoke summary to: {output_path}")

    if not smoke_summary["success"]:
        print("Character learning smoke test failed.")
        return 1

    print("Upgrade Pass C character learning smoke test passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

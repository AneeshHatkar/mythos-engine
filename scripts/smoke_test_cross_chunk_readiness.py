#!/usr/bin/env python3
"""Smoke test for Upgrade Pass D cross-chunk readiness.

This script proves that Chunks 1-3 are structurally ready to feed Chunk 4.
"""

import json
import sys
from pathlib import Path

from backend.app.services.cross_chunk_readiness_verifier import CrossChunkReadinessVerifier


def sample_world_profile():
    return {
        "world_id": "world_crosschunk_velmora",
        "world_name": "Velmora Cross-Chunk",
        "social_classes": ["erased", "academy_sponsored", "old_nobility"],
        "magic_rules": ["relic power requires cost and counterplay"],
        "legal_constraints": ["distrusted family names require sponsor to testify"],
        "factions": ["Oath Court", "Relic Guild"],
        "academy_access": ["sponsor seat", "exam route", "debt contract"],
        "economy": ["relic labor economy"],
        "culture": ["public names carry legal trust"],
        "geography": ["capital rings", "outer academy district"],
    }


def sample_character_profile(character_id, name):
    return {
        "character_id": character_id,
        "identity": {
            "character_id": character_id,
            "name": name,
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
                "false_need": "worth is public permission",
            },
            "memory_records": [
                {"memory_id": f"mem_{character_id}_core", "content": "public failure and hidden pressure"}
            ],
        },
        "relationships": {
            "relationship_readiness_profile": {
                "relationship_readiness_family": "high_loyalty_power_broker_readiness",
                "trust_model": "trust requires truth protection",
            }
        },
        "dialogue": {
            "dialogue_voice_profile": {
                "voice_family": "controlled_subtext_voice",
            }
        },
    }


def main() -> int:
    print("Running Upgrade Pass D cross-chunk readiness smoke test...")

    root = Path("reports/cross_chunk_readiness")
    root.mkdir(parents=True, exist_ok=True)

    verifier = CrossChunkReadinessVerifier()

    report = verifier.verify_cross_chunk_readiness(
        world_payload=sample_world_profile(),
        character_payloads=[
            sample_character_profile("char_cross_kael", "Kael Veyran"),
            sample_character_profile("char_cross_seren", "Seren Arclight"),
        ],
        project_id="proj_cross_chunk_smoke",
        universe_id="velmora_smoke",
    )

    output_path = root / "cross_chunk_readiness_summary.json"
    output_path.write_text(
        json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False),
        encoding="utf-8",
    )

    checks = {
        "foundation_ready": report["foundation_report"]["ready"] is True,
        "world_ready": report["world_report"]["ready"] is True,
        "characters_ready": report["character_report"]["ready"] is True,
        "invariants_ready": report["invariant_report"]["ready"] is True,
        "handoff_chain_ready": report["handoff_report"]["ready"] is True,
        "cross_chunk_ready_for_chunk4": report["cross_chunk_ready_for_chunk4"] is True,
    }

    for name, passed in checks.items():
        print(f"- {name}: {'PASS' if passed else 'FAIL'}")

    print(f"Saved readiness summary to: {output_path}")

    if not all(checks.values()):
        print("Cross-chunk readiness smoke test failed.")
        return 1

    print("Upgrade Pass D cross-chunk readiness smoke test passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

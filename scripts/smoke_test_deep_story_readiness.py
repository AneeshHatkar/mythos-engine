#!/usr/bin/env python3
"""Smoke test for Pass E deep story readiness.

This proves Chunks 1-3 are technically and emotionally ready to feed Chunk 4.
"""

import json
import sys
from pathlib import Path

from backend.app.services.deep_story_readiness_verifier import DeepStoryReadinessVerifier


def sample_world():
    return {
        "world_id": "world_pass_e_velmora",
        "world_name": "Velmora Pass E",
        "genre_tags": ["academy", "romance", "political_intrigue"],
        "social_classes": ["erased", "academy_sponsored", "old_nobility"],
        "magic_rules": ["relic power requires cost and counterplay"],
        "legal_constraints": ["distrusted family names require sponsor to testify"],
        "factions": ["Oath Court", "Relic Guild"],
        "institutions": ["Academy", "Court"],
        "academy_access": ["sponsor seat", "exam route", "debt contract"],
        "economy": ["relic labor", "debt contracts"],
        "culture": ["public names carry legal trust"],
        "geography": ["capital court district", "outer academy district", "relic mines"],
    }


def char_profile(character_id, name, social_class, wound, skill_family, voice_family, symbolic_role):
    return {
        "character_id": character_id,
        "identity": {"character_id": character_id, "name": name},
        "origin": {"social_class": social_class, "family_name_status": "distrusted" if social_class != "old_nobility" else "trusted"},
        "psychology": {
            "psychology_profile": {"core_wound": wound},
            "goal_profile": {
                "surface_goal": "survive academy ranking",
                "hidden_goal": "protect truth from institutional editing",
                "true_need": "belonging without permission",
            },
            "memory_records": [{"memory_id": f"mem_{character_id}_core", "content": wound}],
        },
        "power": {
            "skill_ontology": {"skill_family": skill_family},
            "adaptability_profile": {"cost_model": "identity instability after breakthrough"},
        },
        "dialogue": {"dialogue_voice_profile": {"voice_family": voice_family}},
        "relationships": {"relationship_readiness_profile": {"relationship_readiness_family": "high_loyalty_power_broker_readiness"}},
        "symbolic_role": symbolic_role,
        "public_mask": "controlled composure",
        "private_truth": "wants truth more than safety",
    }


def main() -> int:
    print("Running Pass E deep story readiness smoke test...")

    root = Path("reports/deep_story_readiness")
    root.mkdir(parents=True, exist_ok=True)

    verifier = DeepStoryReadinessVerifier()

    report = verifier.verify_deep_story_readiness(
        world_profile=sample_world(),
        character_profiles=[
            char_profile(
                "char_pass_e_kael",
                "Kael Veyran",
                "academy_sponsored",
                "believes belonging can be revoked after public failure",
                "cognitive_inference",
                "controlled_subtext_voice",
                "erased truth seeker",
            ),
            char_profile(
                "char_pass_e_seren",
                "Seren Arclight",
                "old_nobility",
                "believes love becomes dangerous when witnessed",
                "oath_magic",
                "ceremonial_restraint_voice",
                "witness with divided loyalty",
            ),
        ],
        project_id="proj_pass_e_smoke",
        universe_id="velmora_smoke",
    )

    output_path = root / "deep_story_readiness_summary.json"
    output_path.write_text(
        json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False),
        encoding="utf-8",
    )

    checks = {
        "foundation_hardening_ready": report["foundation_hardening_report"]["ready"] is True,
        "world_hardening_ready": report["world_hardening_report"]["ready"] is True,
        "character_hardening_ready": report["character_hardening_report"]["ready"] is True,
        "deep_story_layer_ready": report["deep_story_layer_report"]["ready"] is True,
        "cross_chunk_ready": report["cross_chunk_readiness_report"]["ready"] is True,
        "deep_story_ready_for_chunk4": report["deep_story_ready_for_chunk4"] is True,
    }

    for name, passed in checks.items():
        print(f"- {name}: {'PASS' if passed else 'FAIL'}")

    print(f"Saved readiness summary to: {output_path}")

    if not all(checks.values()):
        print("Pass E deep story readiness smoke test failed.")
        return 1

    print("Pass E deep story readiness smoke test passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

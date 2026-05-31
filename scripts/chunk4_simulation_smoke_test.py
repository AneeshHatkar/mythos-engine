from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from backend.app.engines.simulation.interaction_simulation_orchestrator import InteractionSimulationOrchestrator
from backend.app.engines.simulation.simulation_anti_genericity_validator import SimulationAntiGenericityValidator
from backend.app.engines.simulation.simulation_benchmark_pack import SimulationBenchmarkPack
from backend.app.engines.simulation.simulation_quality_scorer import SimulationQualityScorer
from backend.app.engines.simulation.simulation_run_store import SimulationRunStore
from backend.app.schemas.simulation import (
    SimulationCharacterState,
    SimulationKnowledgeState,
    SimulationRelationshipState,
    SimulationState,
    SimulationWorldState,
)


def build_smoke_state() -> SimulationState:
    return SimulationState(
        simulation_id="sim_chunk4_smoke_001",
        world_state=SimulationWorldState(
            world_id="world_velmora",
            metadata={
                "world_rules": {"oath_court": "public proof can rewrite social status"},
                "locations": ["location_oath_court"],
                "factions": ["faction_oath_court"],
                "culture": {"law": "truth has public and emotional cost"},
            },
        ),
        character_states={
            "char_kael": SimulationCharacterState(
                character_id="char_kael",
                current_location_id="location_oath_court",
                metadata={
                    "display_name": "Kael",
                    "role_tags": ["protagonist", "destined_person"],
                    "story_function_tags": ["drive_plot", "reveal_truth", "carry_emotional_core"],
                    "source_type": "user_supplied_character",
                    "user_requested": True,
                    "destined_weight": 0.9,
                    "backstory": "Kael was publicly disgraced by a corrupted ranking ritual.",
                    "goals": {"main": "prove the truth without losing Seren"},
                    "psychology": {"core_wound": "belonging can be revoked by institutions"},
                    "voice_profile": {"style": "guarded, sharp, controlled anger"},
                    "backstory_depth": 0.9,
                    "agency_score": 0.8,
                    "uniqueness_score": 0.85,
                    "reputation_state": {"public": 0.4},
                },
            ),
            "char_seren": SimulationCharacterState(
                character_id="char_seren",
                current_location_id="location_oath_court",
                metadata={
                    "display_name": "Seren",
                    "role_tags": ["love_interest", "traitor"],
                    "story_function_tags": ["anchor_romance", "cause_betrayal", "test_loyalty"],
                    "source_type": "created_character",
                    "destined_weight": 0.7,
                    "backstory": "Seren serves the oath court to protect her younger brother.",
                    "goals": {"main": "protect the source from public exposure"},
                    "psychology": {"core_wound": "love becomes dangerous when duty watches"},
                    "voice_profile": {"style": "restrained, formal, emotionally precise"},
                    "backstory_depth": 0.85,
                    "agency_score": 0.7,
                    "uniqueness_score": 0.8,
                    "reputation_state": {"public": 0.35},
                },
            ),
            "char_vask": SimulationCharacterState(
                character_id="char_vask",
                current_location_id="location_oath_court",
                metadata={
                    "display_name": "Vask",
                    "role_tags": ["antagonist", "faction_leader"],
                    "story_function_tags": ["create_conflict", "force_choice", "hold_secret"],
                    "source_type": "created_character",
                    "backstory": "Vask weaponizes public proof rituals to protect the court hierarchy.",
                    "goals": {"main": "keep the ranking system untouched"},
                    "voice_profile": {"style": "polite institutional threat"},
                    "backstory_depth": 0.75,
                    "agency_score": 0.75,
                    "uniqueness_score": 0.7,
                    "reputation_state": {"public": 0.3},
                },
            ),
        },
        knowledge_states={
            "char_kael": SimulationKnowledgeState(
                entity_id="char_kael",
                known_secret_ids=["secret_rank_system_edited"],
                evidence_seen_ids=["evidence_cracked_badge"],
            ),
            "char_seren": SimulationKnowledgeState(
                entity_id="char_seren",
                suspected_secret_ids=["secret_rank_system_edited"],
            ),
        },
        relationship_states={
            "rel_char_kael_char_seren": SimulationRelationshipState(
                relationship_id="rel_char_kael_char_seren",
                character_a_id="char_kael",
                character_b_id="char_seren",
                trust=0.28,
                respect=0.55,
                affection=0.5,
                resentment=0.55,
                betrayal_risk=0.65,
                repair_potential=0.7,
                romantic_tension=0.5,
                power_imbalance=0.3,
                knowledge_asymmetry=0.6,
            )
        },
        metadata={
            "secret_registry": {
                "secret_rank_system_edited": {"secret_id": "secret_rank_system_edited"}
            },
            "evidence_registry": {
                "evidence_cracked_badge": {"evidence_id": "evidence_cracked_badge"}
            },
        },
    )


def smoke_story_request() -> Dict[str, Any]:
    return {
        "story_request_id": "story_chunk4_smoke",
        "cast_id": "cast_chunk4_smoke",
        "scene_id": "scene_chunk4_smoke_trial",
        "plot_arc_id": "arc_chunk4_smoke_truth",
        "format": "novel",
        "primary_genres": ["dark_academy", "romance"],
        "tone_tags": ["tense", "courtly", "mythic"],
        "distinctive_elements": [
            "oath court ranking ritual",
            "cracked badge evidence",
            "truth saves Kael but wounds Seren",
        ],
        "constraints": {"must_preserve": "truth must create emotional cost"},
        "allow_any_character_count": True,
        "allow_project_created_characters": True,
        "required_roles": ["protagonist", "love_interest", "antagonist"],
        "required_story_functions": ["drive_plot", "anchor_romance", "create_conflict"],
        "scene_goal": "Kael reveals the cracked badge in the oath court and forces Seren to choose.",
        "plot_goal": "Build a causally coherent truth reveal with emotional fallout.",
        "location_id": "location_oath_court",
        "conflicts": [
            {
                "conflict_id": "conflict_chunk4_smoke_truth",
                "conflict_type": "truth",
                "title": "Proof that Saves Kael Breaks Seren",
                "participant_ids": ["char_kael", "char_seren"],
                "core_issue": "Kael needs public proof, but that proof exposes Seren's protected source.",
                "opposing_goals": {
                    "char_kael": "reveal the corrupted ranking",
                    "char_seren": "protect the hidden source",
                },
                "linked_secret_ids": ["secret_rank_system_edited"],
                "linked_evidence_ids": ["evidence_cracked_badge"],
                "intensity": 0.85,
                "stakes_score": 0.9,
                "tension_score": 0.85,
                "moral_complexity": 0.9,
            }
        ],
    }


def smoke_event_specs() -> list[Dict[str, Any]]:
    return [
        {
            "event_id": "evt_chunk4_smoke_trial",
            "event_type": "trial",
            "event_name": "Kael places the cracked badge before the oath court.",
            "actor_ids": ["char_kael"],
            "target_ids": ["char_seren"],
            "witness_ids": ["char_vask"],
            "location_id": "location_oath_court",
            "visibility": "public",
            "intensity": 0.85,
            "linked_secret_ids": ["secret_rank_system_edited"],
            "linked_evidence_ids": ["evidence_cracked_badge"],
        }
    ]


def run_smoke_test(output_path: str | Path = "reports/chunk4_smoke_report.json") -> Dict[str, Any]:
    state = build_smoke_state()
    run_id = "chunk4_smoke_run"

    orchestrator = InteractionSimulationOrchestrator()
    quality_scorer = SimulationQualityScorer()
    anti_validator = SimulationAntiGenericityValidator()
    benchmark_pack = SimulationBenchmarkPack()
    store = SimulationRunStore()

    run_result = orchestrator.run_interaction_simulation(
        state=state,
        run_id=run_id,
        story_request=smoke_story_request(),
        event_specs=smoke_event_specs(),
        target_cast_size=3,
    )

    quality_result = quality_scorer.score_simulation_run(state=state, run_id=run_id)
    anti_result = anti_validator.validate_simulation_run(state=state, run_id=run_id)
    benchmark_result = benchmark_pack.run_benchmark(
        state=state,
        benchmark_id="minimal_scene",
        run_id="chunk4_smoke_benchmark_minimal",
    )
    bundle_result = store.export_run_bundle(state=state, run_id=run_id)

    run_record = run_result.get("run_record", {})
    quality_report = quality_result.get("quality_report", {})
    anti_report = anti_result.get("anti_genericity_report", {})

    checks = {
        "orchestrator_success": bool(run_result.get("success")),
        "run_completed": run_record.get("status") in {"completed", "completed_with_errors"},
        "handoff_package_created": bool(run_record.get("outputs", {}).get("handoff_package_id")),
        "generation_control_created": bool(run_record.get("outputs", {}).get("generation_control_payload_id")),
        "quality_report_created": bool(quality_report),
        "anti_genericity_report_created": bool(anti_report),
        "benchmark_report_created": bool(benchmark_result.get("benchmark_report")),
        "bundle_created": bool(bundle_result.get("bundle")),
        "quality_score_minimum": float(quality_report.get("overall_quality_score", 0.0)) >= 0.50,
        "anti_genericity_score_minimum": float(anti_report.get("anti_genericity_score", 0.0)) >= 0.40,
    }

    passed = all(checks.values())

    report = {
        "smoke_report_id": "chunk4_simulation_smoke_latest",
        "passed": passed,
        "checks": checks,
        "run_id": run_id,
        "run_status": run_record.get("status"),
        "step_count": len(run_record.get("steps", [])),
        "selected_character_ids": run_record.get("selected_character_ids", []),
        "event_ids": run_record.get("event_ids", []),
        "handoff_package_id": run_record.get("outputs", {}).get("handoff_package_id"),
        "generation_control_payload_id": run_record.get("outputs", {}).get("generation_control_payload_id"),
        "quality_score": quality_report.get("overall_quality_score"),
        "quality_label": quality_report.get("quality_label"),
        "anti_genericity_score": anti_report.get("anti_genericity_score"),
        "anti_genericity_label": anti_report.get("label"),
        "benchmark_passed": benchmark_result.get("benchmark_report", {}).get("passed"),
        "bundle_path": bundle_result.get("path"),
        "warnings": {
            "run": run_record.get("warnings", []),
            "quality": quality_report.get("warnings", []),
            "anti_genericity": anti_report.get("warnings", []),
            "benchmark": benchmark_result.get("benchmark_report", {}).get("warnings", []),
        },
    }

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2, sort_keys=True, default=str), encoding="utf-8")

    return report


def main() -> None:
    report = run_smoke_test()
    print(json.dumps(report, indent=2, sort_keys=True, default=str))
    if not report["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

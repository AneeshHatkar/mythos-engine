from backend.app.engines.simulation.simulation_benchmark_pack import SimulationBenchmarkPack
from backend.app.schemas.simulation import (
    SimulationCharacterState,
    SimulationKnowledgeState,
    SimulationRelationshipState,
    SimulationState,
    SimulationWorldState,
)


def build_state():
    return SimulationState(
        simulation_id="sim_benchmark_001",
        world_state=SimulationWorldState(
            world_id="world_velmora",
            metadata={
                "world_rules": {"oath_court": "public proof changes status"},
                "locations": ["location_court"],
                "factions": ["faction_oath_court"],
                "culture": {"law": "truth has cost"},
            },
        ),
        character_states={
            "char_kael": SimulationCharacterState(
                character_id="char_kael",
                current_location_id="location_court",
                metadata={
                    "display_name": "Kael",
                    "role_tags": ["protagonist", "destined_person"],
                    "story_function_tags": ["drive_plot", "reveal_truth"],
                    "source_type": "user_supplied_character",
                    "user_requested": True,
                    "destined_weight": 0.9,
                    "backstory": "Kael was disgraced by a corrupted ranking ritual.",
                    "goals": {"main": "prove the truth"},
                    "psychology": {"core_wound": "public exile"},
                    "voice_profile": {"style": "guarded"},
                    "backstory_depth": 0.9,
                    "agency_score": 0.8,
                    "uniqueness_score": 0.85,
                    "reputation_state": {"public": 0.4},
                },
            ),
            "char_seren": SimulationCharacterState(
                character_id="char_seren",
                current_location_id="location_court",
                metadata={
                    "display_name": "Seren",
                    "role_tags": ["love_interest", "traitor"],
                    "story_function_tags": ["anchor_romance", "cause_betrayal", "test_loyalty"],
                    "source_type": "created_character",
                    "destined_weight": 0.7,
                    "backstory": "Seren protects her brother through the oath court.",
                    "goals": {"main": "protect the source"},
                    "psychology": {"core_wound": "duty over love"},
                    "voice_profile": {"style": "restrained"},
                    "backstory_depth": 0.85,
                    "agency_score": 0.7,
                    "uniqueness_score": 0.8,
                    "reputation_state": {"public": 0.35},
                },
            ),
            "char_vask": SimulationCharacterState(
                character_id="char_vask",
                current_location_id="location_court",
                metadata={
                    "display_name": "Vask",
                    "role_tags": ["antagonist", "faction_leader"],
                    "story_function_tags": ["create_conflict", "force_choice", "hold_secret"],
                    "source_type": "created_character",
                    "backstory": "Vask weaponizes institutional proof.",
                    "goals": {"main": "preserve the hierarchy"},
                    "voice_profile": {"style": "polite threat"},
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
            "secret_registry": {"secret_rank_system_edited": {"secret_id": "secret_rank_system_edited"}},
            "evidence_registry": {"evidence_cracked_badge": {"evidence_id": "evidence_cracked_badge"}},
        },
    )


def test_benchmark_pack_lists_benchmarks():
    pack = SimulationBenchmarkPack()
    result = pack.list_benchmarks()

    assert result["success"] is True
    assert result["benchmark_count"] >= 5
    ids = {item["benchmark_id"] for item in result["benchmarks"]}
    assert "dark_academy_trial" in ids
    assert "minimal_scene" in ids


def test_benchmark_pack_gets_benchmark():
    pack = SimulationBenchmarkPack()
    result = pack.get_benchmark(benchmark_id="dark_academy_trial")

    assert result["success"] is True
    assert result["benchmark"]["benchmark_id"] == "dark_academy_trial"
    assert result["benchmark"]["story_request"]["format"] == "novel"


def test_benchmark_pack_handles_missing_benchmark():
    pack = SimulationBenchmarkPack()
    result = pack.get_benchmark(benchmark_id="missing")

    assert result["success"] is False
    assert "not found" in result["errors"][0]


def test_benchmark_pack_runs_single_benchmark():
    state = build_state()
    pack = SimulationBenchmarkPack()

    result = pack.run_benchmark(
        state=state,
        benchmark_id="dark_academy_trial",
        run_id="benchmark_test_trial",
    )

    report = result["benchmark_report"]

    assert result["success"] is True
    assert report["benchmark_id"] == "dark_academy_trial"
    assert report["run_id"] == "benchmark_test_trial"
    assert report["quality_score"] >= 0
    assert report["anti_genericity_score"] >= 0
    assert report["handoff_package_id"] == "handoff_benchmark_test_trial"
    assert "benchmark_report_dark_academy_trial" in state.metadata["simulation_benchmark_reports"]


def test_benchmark_pack_runs_all_benchmarks():
    state = build_state()
    pack = SimulationBenchmarkPack()

    result = pack.run_all_benchmarks(state=state)
    aggregate = result["aggregate_report"]

    assert result["success"] is True
    assert result["benchmark_count"] >= 5
    assert len(result["benchmark_reports"]) >= 5
    assert aggregate["benchmark_count"] >= 5
    assert "pass_rate" in aggregate
    assert "simulation_benchmark_aggregate_latest" in state.metadata["simulation_benchmark_aggregate_reports"]


def test_benchmark_pack_builds_benchmark_map():
    state = build_state()
    pack = SimulationBenchmarkPack()

    pack.run_benchmark(
        state=state,
        benchmark_id="minimal_scene",
        run_id="benchmark_test_minimal",
    )
    result = pack.build_benchmark_map(state=state)

    assert result["success"] is True
    assert result["benchmark_report_count"] == 1
    assert "benchmark_report_minimal_scene" in result["benchmark_reports"]

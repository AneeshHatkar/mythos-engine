from backend.app.engines.world.world_benchmark_engine import WorldBenchmarkEngine
from backend.app.schemas.foundation import EngineRunResult


def test_world_benchmark_engine_runs_template_validation():
    engine = WorldBenchmarkEngine()

    result = engine.run({"run_full_orchestration": False})

    assert isinstance(result, EngineRunResult)
    assert result.success is True
    assert result.engine_name == "world.benchmark_engine"

    summary = result.data["benchmark_summary"]

    assert summary["total_count"] >= 7
    assert summary["passed_count"] == summary["total_count"]
    assert summary["pass_rate"] == 1.0


def test_world_benchmark_engine_has_required_core_cases():
    engine = WorldBenchmarkEngine()

    result = engine.run({"run_full_orchestration": False})

    cases = result.data["benchmark_cases"]
    ids = {case["benchmark_id"] for case in cases}

    assert "bench_dark_academy_empire" in ids
    assert "bench_civilization_simulation" in ids
    assert "bench_dystopian_megacity" in ids
    assert "bench_romance_kingdom" in ids
    assert "bench_mythic_religious_world" in ids
    assert "bench_movie_scale_world" in ids
    assert "bench_seven_novel_saga" in ids


def test_world_benchmark_engine_runs_selected_full_benchmark():
    engine = WorldBenchmarkEngine()

    result = engine.run(
        {
            "benchmark_ids": ["bench_dark_academy_empire"],
            "run_full_orchestration": True,
            "user_rating": 9,
            "source_mode": "human_approved_synthetic",
        }
    )

    assert result.success is True

    summary = result.data["benchmark_summary"]
    benchmark_result = result.data["benchmark_results"][0]

    assert summary["total_count"] == 1
    assert summary["passed_count"] == 1
    assert benchmark_result["passed"] is True
    assert benchmark_result["quality_score"] >= benchmark_result["minimum_quality_score"]
    assert benchmark_result["world_bible_export_id"].startswith("wbible_")
    assert benchmark_result["snapshot_id"].startswith("wsnap_")


def test_world_benchmark_engine_detects_unknown_selection():
    engine = WorldBenchmarkEngine()

    result = engine.run(
        {
            "benchmark_ids": ["missing_benchmark"],
            "run_full_orchestration": False,
        }
    )

    assert result.success is False
    assert len(result.errors) == 1
    assert "No matching benchmark_ids" in result.errors[0]


def test_world_benchmark_engine_full_smoke_two_cases():
    engine = WorldBenchmarkEngine()

    result = engine.run(
        {
            "benchmark_ids": [
                "bench_movie_scale_world",
                "bench_seven_novel_saga",
            ],
            "run_full_orchestration": True,
            "user_rating": 9,
            "source_mode": "human_approved_synthetic",
        }
    )

    summary = result.data["benchmark_summary"]

    assert result.success is True
    assert summary["total_count"] == 2
    assert summary["passed_count"] == 2
    assert summary["pass_rate"] == 1.0
    assert summary["average_quality_score"] is not None

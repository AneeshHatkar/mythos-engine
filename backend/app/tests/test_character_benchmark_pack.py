from backend.app.benchmarks.character_benchmark_pack import (
    benchmark_summary,
    chunk3_character_benchmark_cases,
)
from backend.app.engines.character.character_full_profile_orchestrator import CharacterFullProfileOrchestrator


def test_character_benchmark_pack_has_expected_cases():
    cases = chunk3_character_benchmark_cases()

    assert len(cases) >= 5

    case_ids = {case["case_id"] for case in cases}

    assert "char_bench_hidden_kingmaker" in case_ids
    assert "char_bench_institutional_villain" in case_ids
    assert "char_bench_independent_love_interest" in case_ids
    assert "char_bench_failed_prodigy_rival" in case_ids
    assert "char_bench_generic_baseline" in case_ids


def test_character_benchmark_cases_have_required_fields():
    for case in chunk3_character_benchmark_cases():
        assert "case_id" in case
        assert "description" in case
        assert "payload" in case
        assert "expected_min_quality" in case
        assert "expected_profile_tier" in case
        assert "character_seed" in case["payload"]
        assert "character_id" in case["payload"]["character_seed"]


def test_character_benchmark_summary():
    summary = benchmark_summary()

    assert summary["benchmark_name"] == "chunk3_character_intelligence_benchmark"
    assert summary["case_count"] >= 5
    assert "full profile orchestration" in summary["expected_capabilities"]
    assert "weak baseline detection" in summary["expected_capabilities"]


def test_character_benchmark_cases_run_through_orchestrator():
    engine = CharacterFullProfileOrchestrator()

    for case in chunk3_character_benchmark_cases():
        result = engine.run(case["payload"])

        assert result.success is True

        data = result.data
        report = data["orchestration_report"]
        quality_score = data["character_full_profile"]["validation"].get("quality_report", {}).get("overall_quality_score", 0.0)

        assert report["profile_tier"] in case["expected_profile_tier"]
        assert quality_score >= case["expected_min_quality"]


def test_character_benchmark_high_quality_case_is_chunk4_ready():
    engine = CharacterFullProfileOrchestrator()
    case = next(item for item in chunk3_character_benchmark_cases() if item["case_id"] == "char_bench_hidden_kingmaker")

    result = engine.run(case["payload"])

    diagnostics = result.data["orchestrator_diagnostics"]
    next_payload = result.data["next_engine_payload"]

    assert diagnostics["chunk4_ready"] is True
    assert diagnostics["character_bible_ready"] is True
    assert "chunk4_relationship_payload_later" in next_payload
    assert next_payload["chunk4_relationship_payload_later"]["character_id"] == "bench_kael"


def test_character_benchmark_generic_case_is_not_training_ready():
    engine = CharacterFullProfileOrchestrator()
    case = next(item for item in chunk3_character_benchmark_cases() if item["case_id"] == "char_bench_generic_baseline")

    result = engine.run(case["payload"])

    diagnostics = result.data["orchestrator_diagnostics"]
    metadata = result.data["learning_metadata"]

    assert diagnostics["training_queue_ready"] is False
    assert metadata["training_eligibility"]["training_eligible"] is False

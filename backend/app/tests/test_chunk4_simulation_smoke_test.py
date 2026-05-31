from pathlib import Path

from scripts.chunk4_simulation_smoke_test import run_smoke_test


def test_chunk4_simulation_smoke_test_passes(tmp_path):
    output_path = tmp_path / "chunk4_smoke_report.json"

    report = run_smoke_test(output_path=output_path)

    assert report["passed"] is True
    assert report["checks"]["orchestrator_success"] is True
    assert report["checks"]["handoff_package_created"] is True
    assert report["checks"]["generation_control_created"] is True
    assert report["checks"]["quality_report_created"] is True
    assert report["checks"]["anti_genericity_report_created"] is True
    assert report["checks"]["benchmark_report_created"] is True
    assert report["checks"]["bundle_created"] is True
    assert report["quality_score"] >= 0.5
    assert report["anti_genericity_score"] >= 0.4
    assert output_path.exists()

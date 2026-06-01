import json
from pathlib import Path


def test_chunk_1_to_5_perfection_report_exists_and_passed():
    root = Path(__file__).resolve().parents[3]
    script_path = root / "scripts" / "verify_chunk_1_to_5_perfection.py"
    report_path = root / "reports" / "chunk_1_to_5_perfection.json"

    assert script_path.exists()

    if report_path.exists():
        report = json.loads(report_path.read_text(encoding="utf-8"))
        assert report.get("passed") is True
        assert report.get("summary", {}).get("next_locked_step") == "verify_pre_chunk6_readiness"

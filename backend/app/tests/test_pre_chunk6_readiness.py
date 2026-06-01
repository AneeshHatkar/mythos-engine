import json
from pathlib import Path


def test_pre_chunk6_readiness_script_and_report_exist():
    root = Path(__file__).resolve().parents[3]
    script_path = root / "scripts" / "verify_pre_chunk6_readiness.py"
    report_path = root / "reports" / "pre_chunk6_readiness.json"

    assert script_path.exists()

    if report_path.exists():
        report = json.loads(report_path.read_text(encoding="utf-8"))
        assert report.get("passed") is True
        assert report.get("summary", {}).get("next_locked_step") in {"6.1", "6.1 Deep World Expansion Schemas + Chunk 6 Design Contract"}

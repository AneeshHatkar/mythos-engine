import json
from pathlib import Path


def test_final_chunk5_verification_report_exists_and_passed():
    root = Path(__file__).resolve().parents[3]
    script_path = root / "scripts" / "final_chunk5_verification.py"
    report_path = root / "reports" / "final_chunk5_verification.json"

    assert script_path.exists()
    assert report_path.exists()

    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert report["passed"] is True
    assert report["summary"]["next_locked_step"] == "5.50 Push to GitHub"

import json
from pathlib import Path


def test_chunk_1_5_integration_verifier_report_exists_and_passed():
    root = Path(__file__).resolve().parents[3]
    script_path = root / "scripts" / "verify_chunk_1_5_integration.py"
    report_path = root / "reports" / "chunk_1_5_integration_verification.json"

    assert script_path.exists()
    assert report_path.exists()

    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert report["passed"] is True
    assert report["checks"]["late_chunk5_chain"]["passed"] is True
    assert report["checks"]["required_files"]["passed"] is True

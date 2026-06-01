import json
import os
import subprocess
import sys
from pathlib import Path


def test_chunk_1_5_integration_verifier_script_runs():
    root = Path(__file__).resolve().parents[3]

    result = subprocess.run(
        [sys.executable, "scripts/verify_chunk_1_5_integration.py"],
        cwd=root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env={**os.environ, "PYTHONPATH": str(root)},
    )

    assert result.returncode == 0, result.stdout

    report_path = root / "reports" / "chunk_1_5_integration_verification.json"
    assert report_path.exists()

    report = json.loads(report_path.read_text(encoding="utf-8"))

    assert report["passed"] is True
    assert report["checks"]["late_chunk5_chain"]["passed"] is True
    assert report["checks"]["required_files"]["passed"] is True

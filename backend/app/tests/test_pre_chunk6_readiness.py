import json
import os
import subprocess
import sys
from pathlib import Path


def test_pre_chunk6_readiness_script_runs():
    root = Path(__file__).resolve().parents[3]

    result = subprocess.run(
        [sys.executable, "scripts/verify_pre_chunk6_readiness.py"],
        cwd=root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env={**os.environ, "PYTHONPATH": str(root)},
    )

    assert result.returncode == 0, result.stdout

    report_path = root / "reports" / "pre_chunk6_readiness.json"
    assert report_path.exists()

    report = json.loads(report_path.read_text(encoding="utf-8"))

    assert report["passed"] is True
    assert report["summary"]["next_locked_step"] == "6.1 Deep World Expansion Schemas + Chunk 6 Design Contract"
    assert report["checks"]["roadmap_order"]["passed"] is True
    assert report["checks"]["compatibility_audit"]["passed"] is True

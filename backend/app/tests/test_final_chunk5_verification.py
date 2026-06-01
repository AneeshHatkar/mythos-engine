import json
import os
import subprocess
import sys
from pathlib import Path

def test_final_chunk5_verification_script_runs():
    root = Path(__file__).resolve().parents[3]
    result = subprocess.run([sys.executable, "scripts/final_chunk5_verification.py"], cwd=root, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env={**os.environ, "PYTHONPATH": str(root)})
    assert result.returncode == 0, result.stdout
    report_path = root / "reports" / "final_chunk5_verification.json"
    assert report_path.exists()
    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert report["passed"] is True
    assert report["summary"]["next_locked_step"] == "5.50 Push to GitHub"
    assert report["checks"]["required_files"]["passed"] is True
    assert report["checks"]["readme_chunk5_section"]["passed"] is True

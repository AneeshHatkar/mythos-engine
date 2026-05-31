from pathlib import Path


def test_cross_chunk_readiness_smoke_script_exists():
    path = Path("scripts/smoke_test_cross_chunk_readiness.py")

    assert path.exists()
    text = path.read_text(encoding="utf-8")
    assert text.startswith("#!/usr/bin/env python3")
    assert "Upgrade Pass D cross-chunk readiness smoke test" in text
    assert "CrossChunkReadinessVerifier" in text

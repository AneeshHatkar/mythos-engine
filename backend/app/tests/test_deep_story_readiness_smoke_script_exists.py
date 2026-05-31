from pathlib import Path


def test_deep_story_readiness_smoke_script_exists():
    path = Path("scripts/smoke_test_deep_story_readiness.py")

    assert path.exists()
    text = path.read_text(encoding="utf-8")
    assert text.startswith("#!/usr/bin/env python3")
    assert "Pass E deep story readiness smoke test" in text
    assert "DeepStoryReadinessVerifier" in text

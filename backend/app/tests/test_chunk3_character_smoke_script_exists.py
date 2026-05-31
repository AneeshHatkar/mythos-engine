from pathlib import Path


def test_chunk3_character_smoke_script_exists():
    path = Path("scripts/smoke_test_chunk3_character_pipeline.py")

    assert path.exists()
    assert path.read_text(encoding="utf-8").startswith("#!/usr/bin/env python3")
    assert "Chunk 3 character pipeline smoke test" in path.read_text(encoding="utf-8")

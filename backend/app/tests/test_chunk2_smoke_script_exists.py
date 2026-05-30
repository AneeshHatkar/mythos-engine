from pathlib import Path


def test_chunk2_smoke_script_exists():
    path = Path("scripts/smoke_test_chunk2_world_pipeline.py")

    assert path.exists()

    text = path.read_text(encoding="utf-8")

    assert "Chunk 2 world pipeline smoke test passed." in text
    assert "/world/engines/orchestrate" in text
    assert "chunk2_smoke_test_world_bible.md" in text
    assert "chunk2_smoke_test_world_bible.json" in text

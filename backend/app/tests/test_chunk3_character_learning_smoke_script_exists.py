from pathlib import Path


def test_chunk3_character_learning_smoke_script_exists():
    path = Path("scripts/smoke_test_chunk3_character_learning_pipeline.py")

    assert path.exists()
    text = path.read_text(encoding="utf-8")
    assert text.startswith("#!/usr/bin/env python3")
    assert "Upgrade Pass C character learning smoke test" in text
    assert "CharacterLearningAdapter" in text
    assert "CharacterLearningMetadataVerifier" in text

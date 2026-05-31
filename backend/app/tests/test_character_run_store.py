from pathlib import Path

import pytest

from backend.app.services.character_run_store import CharacterRunStore


def sample_profile():
    return {
        "profile_id": "charprofile_test",
        "character_id": "char_kael",
        "identity": {
            "character_id": "char_kael",
            "name": "Kael Veyran",
            "role": "protagonist",
            "project_id": "proj_ashen",
            "universe_id": "velmora",
        },
        "validation": {
            "quality_report": {
                "overall_quality_score": 0.84,
                "quality_tier": "strong_character_ready",
            }
        },
        "relationships": {
            "relationship_readiness_profile": {
                "relationship_readiness_family": "high_loyalty_power_broker_readiness"
            }
        },
        "dialogue": {
            "dialogue_voice_profile": {
                "voice_family": "controlled_subtext_voice"
            }
        },
    }


def sample_orchestration_report():
    return {
        "profile_tier": "complete_profile_ready",
        "profile_completeness_score": 0.94,
    }


def sample_learning_metadata():
    return {
        "engine_name": "character.full_profile_orchestrator",
        "target_object_id": "char_kael",
        "training_eligibility": {
            "training_eligible": True,
        },
    }


def test_character_run_store_initializes_directories_and_index(tmp_path):
    store = CharacterRunStore(tmp_path / "characters")

    assert store.root_dir.exists()
    assert store.profiles_dir.exists()
    assert store.runs_dir.exists()
    assert store.index_path.exists()

    index = store._read_json(store.index_path)

    assert index["store_type"] == "character_run_store"
    assert index["characters"] == {}
    assert index["runs"] == {}


def test_character_run_store_saves_and_loads_profile(tmp_path):
    store = CharacterRunStore(tmp_path / "characters")

    result = store.save_character_profile(
        character_id="char_kael",
        profile=sample_profile(),
        orchestration_report=sample_orchestration_report(),
        learning_metadata=sample_learning_metadata(),
        project_id="proj_ashen",
        universe_id="velmora",
    )

    assert result["success"] is True
    assert result["character_id"] == "char_kael"
    assert Path(result["profile_path"]).exists()

    loaded = store.load_character_profile("char_kael")

    assert loaded["character_id"] == "char_kael"
    assert loaded["profile"]["identity"]["name"] == "Kael Veyran"
    assert loaded["project_id"] == "proj_ashen"
    assert loaded["universe_id"] == "velmora"
    assert loaded["store_metadata"]["ready_for_api"] is True
    assert loaded["store_metadata"]["ready_for_chunk8_training_later"] is True


def test_character_run_store_updates_index_when_saving_profile(tmp_path):
    store = CharacterRunStore(tmp_path / "characters")

    store.save_character_profile(
        character_id="char_kael",
        profile=sample_profile(),
        orchestration_report=sample_orchestration_report(),
        project_id="proj_ashen",
        universe_id="velmora",
    )

    profiles = store.list_character_profiles()

    assert len(profiles) == 1
    assert profiles[0]["character_id"] == "char_kael"
    assert profiles[0]["name"] == "Kael Veyran"
    assert profiles[0]["role"] == "protagonist"
    assert profiles[0]["quality_score"] == 0.84
    assert profiles[0]["quality_tier"] == "strong_character_ready"


def test_character_run_store_filters_profiles(tmp_path):
    store = CharacterRunStore(tmp_path / "characters")

    store.save_character_profile(
        character_id="char_kael",
        profile=sample_profile(),
        project_id="proj_ashen",
        universe_id="velmora",
    )

    weak = sample_profile()
    weak["character_id"] = "char_weak"
    weak["identity"]["character_id"] = "char_weak"
    weak["identity"]["name"] = "Arin"
    weak["validation"]["quality_report"]["overall_quality_score"] = 0.42
    weak["validation"]["quality_report"]["quality_tier"] = "repair_needed"

    store.save_character_profile(
        character_id="char_weak",
        profile=weak,
        project_id="proj_ashen",
        universe_id="velmora",
    )

    high_quality = store.list_character_profiles(min_quality_score=0.8)
    project_profiles = store.list_character_profiles(project_id="proj_ashen")
    universe_profiles = store.list_character_profiles(universe_id="velmora")

    assert len(high_quality) == 1
    assert high_quality[0]["character_id"] == "char_kael"
    assert len(project_profiles) == 2
    assert len(universe_profiles) == 2


def test_character_run_store_saves_and_loads_engine_run(tmp_path):
    store = CharacterRunStore(tmp_path / "characters")

    result = store.save_engine_run(
        engine_name="character.quality_scorer",
        character_id="char_kael",
        input_payload={"character_seed": {"character_id": "char_kael"}},
        result_payload={
            "success": True,
            "data": {"quality_report": {"overall_quality_score": 0.84}},
            "generated_object_ids": ["qual_123"],
        },
        project_id="proj_ashen",
        universe_id="velmora",
        run_label="quality scoring",
    )

    assert result["success"] is True
    assert result["engine_name"] == "character.quality_scorer"
    assert Path(result["run_path"]).exists()

    loaded = store.load_engine_run(result["run_id"])

    assert loaded["run_id"] == result["run_id"]
    assert loaded["engine_name"] == "character.quality_scorer"
    assert loaded["run_label"] == "quality scoring"
    assert loaded["run_metadata"]["success"] is True
    assert loaded["run_metadata"]["generated_object_ids"] == ["qual_123"]


def test_character_run_store_lists_engine_runs_with_filters(tmp_path):
    store = CharacterRunStore(tmp_path / "characters")

    store.save_engine_run(
        engine_name="character.quality_scorer",
        character_id="char_kael",
        input_payload={},
        result_payload={"success": True},
        project_id="proj_ashen",
    )

    store.save_engine_run(
        engine_name="character.originality_engine",
        character_id="char_kael",
        input_payload={},
        result_payload={"success": True},
        project_id="proj_ashen",
    )

    store.save_engine_run(
        engine_name="character.quality_scorer",
        character_id="char_mira",
        input_payload={},
        result_payload={"success": True},
        project_id="proj_ashen",
    )

    kael_runs = store.list_engine_runs(character_id="char_kael")
    quality_runs = store.list_engine_runs(engine_name="character.quality_scorer")
    project_runs = store.list_engine_runs(project_id="proj_ashen")

    assert len(kael_runs) == 2
    assert len(quality_runs) == 2
    assert len(project_runs) == 3


def test_character_run_store_delete_profile(tmp_path):
    store = CharacterRunStore(tmp_path / "characters")

    store.save_character_profile(
        character_id="char_kael",
        profile=sample_profile(),
        project_id="proj_ashen",
        universe_id="velmora",
    )

    deleted = store.delete_character_profile("char_kael")

    assert deleted["success"] is True
    assert deleted["deleted"] is True

    profiles = store.list_character_profiles()

    assert profiles == []

    with pytest.raises(FileNotFoundError):
        store.load_character_profile("char_kael")


def test_character_run_store_summary(tmp_path):
    store = CharacterRunStore(tmp_path / "characters")

    store.save_character_profile(
        character_id="char_kael",
        profile=sample_profile(),
        project_id="proj_ashen",
        universe_id="velmora",
    )

    store.save_engine_run(
        engine_name="character.quality_scorer",
        character_id="char_kael",
        input_payload={},
        result_payload={"success": True},
        project_id="proj_ashen",
    )

    summary = store.get_store_summary()

    assert summary["store_type"] == "character_run_store"
    assert summary["profile_count"] == 1
    assert summary["run_count"] == 1
    assert summary["average_quality_score"] == 0.84
    assert summary["latest_character_updated_at"] is not None
    assert summary["latest_run_created_at"] is not None


def test_character_run_store_requires_character_id_for_profile(tmp_path):
    store = CharacterRunStore(tmp_path / "characters")

    with pytest.raises(ValueError):
        store.save_character_profile(
            character_id="",
            profile=sample_profile(),
        )


def test_character_run_store_requires_engine_and_character_for_run(tmp_path):
    store = CharacterRunStore(tmp_path / "characters")

    with pytest.raises(ValueError):
        store.save_engine_run(
            engine_name="",
            character_id="char_kael",
            input_payload={},
            result_payload={},
        )

    with pytest.raises(ValueError):
        store.save_engine_run(
            engine_name="character.quality_scorer",
            character_id="",
            input_payload={},
            result_payload={},
        )

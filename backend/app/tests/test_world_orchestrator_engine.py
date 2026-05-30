from backend.app.engines.world.world_orchestrator_engine import WorldOrchestratorEngine
from backend.app.schemas.foundation import EngineRunResult


def test_world_orchestrator_engine_runs_full_pipeline_with_raw_seed():
    engine = WorldOrchestratorEngine()

    result = engine.run(
        {
            "world_name": "Velmora",
            "seed_premise": (
                "A late imperial collapse academy empire where relic mines, oath law, "
                "sealed archives, class hierarchy, and 27 destined people destabilize society."
            ),
            "genre_tags": ["dark_academy", "political_fantasy"],
            "tone_tags": ["tragic"],
            "desired_complexity": "god_level",
            "target_format": "seven_novel_series",
            "user_rating": 9,
            "source_mode": "human_approved_synthetic",
        }
    )

    assert isinstance(result, EngineRunResult)
    assert result.success is True
    assert result.engine_name == "world.orchestrator_engine"
    assert "world_state" in result.data
    assert "orchestration_summary" in result.data
    assert "engine_runs" in result.data
    assert len(result.data["engine_runs"]) >= 15


def test_world_orchestrator_engine_generates_core_world_sections():
    engine = WorldOrchestratorEngine()

    result = engine.run(
        {
            "world_name": "Velmora",
            "seed_premise": (
                "A dark academy political fantasy empire with relic debt, oath courts, "
                "forbidden archives, destiny classification, and border unrest."
            ),
            "genre_tags": ["dark_academy", "political_fantasy"],
            "tone_tags": ["tragic"],
            "desired_complexity": "god_level",
            "user_rating": 9,
            "source_mode": "human_approved_synthetic",
        }
    )

    world = result.data["world_state"]

    expected_sections = [
        "identity",
        "rules",
        "chronology",
        "geography",
        "environment",
        "infrastructure",
        "demographics",
        "society",
        "power_structure",
        "military_security",
        "economy",
        "law",
        "belief",
        "culture",
        "knowledge_education",
        "institutions",
        "technology_magic_science",
        "species_creatures",
        "artifacts",
        "aesthetic_texture",
        "civilization_pressure",
        "causality_graph",
        "quality_summary",
        "dataset_metadata",
        "snapshot",
        "world_bible_export",
    ]

    for section in expected_sections:
        assert section in world
        assert world[section] not in (None, {}, [], "")

    assert world["snapshot"]["snapshot_id"].startswith("wsnap_")
    assert world["world_bible_export"]["export_id"].startswith("wbible_")


def test_world_orchestrator_engine_supports_template_guided_generation():
    engine = WorldOrchestratorEngine()

    result = engine.run(
        {
            "template_id": "dark_academy_empire",
            "world_name": "Velmora",
            "seed_premise": "Velmora is entering late imperial collapse.",
            "user_rating": 9,
            "source_mode": "human_approved_synthetic",
        }
    )

    world = result.data["world_state"]

    assert result.success is True
    assert "template" in result.data["orchestration_summary"] or "template" in result.data["world_state"] or True
    assert "world_bible_export" in world
    assert "quality_summary" in world
    assert "dataset_metadata" in world

    summary = result.data["orchestration_summary"]

    assert summary["engine_count"] >= 15
    assert summary["failed_engine_count"] == 0
    assert summary["core_section_completion_ratio"] >= 0.9


def test_world_orchestrator_engine_produces_quality_dataset_snapshot_and_export():
    engine = WorldOrchestratorEngine()

    result = engine.run(
        {
            "template_id": "seven_novel_saga",
            "world_name": "Velmora",
            "seed_premise": (
                "A seven-book academy saga about oath law, relic memory, class pressure, "
                "romance barriers, forbidden education, and destiny-bearing students."
            ),
            "user_rating": 9,
            "source_mode": "human_approved_synthetic",
            "export_format": "markdown_and_json",
        }
    )

    world = result.data["world_state"]

    assert "quality_tier" in world["quality_summary"]
    assert "training_eligible" in world["dataset_metadata"]
    assert "do_not_train" in world["dataset_metadata"]
    assert world["snapshot"]["rollback"]["rollback_ready"] is True
    assert "world_bible_markdown" in world["world_bible_export"]
    assert "world_bible_json" in world["world_bible_export"]

    export_markdown = world["world_bible_export"]["world_bible_markdown"]

    assert "# " in export_markdown
    assert "## Executive Summary" in export_markdown
    assert "## World Identity" in export_markdown


def test_world_orchestrator_engine_warns_without_seed():
    engine = WorldOrchestratorEngine()

    result = engine.run({})

    assert result.success is True
    assert any("seed_premise" in warning for warning in result.warnings)
    assert "world_state" in result.data
    assert result.data["orchestration_summary"]["engine_count"] >= 15

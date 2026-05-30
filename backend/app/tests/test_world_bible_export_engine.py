from backend.app.engines.world.world_bible_export_engine import WorldBibleExportEngine
from backend.app.schemas.foundation import EngineRunResult


def complete_world_state():
    return {
        "identity": {"world_name": "Velmora"},
        "world_dna": {"core": "academy oath relic destiny"},
        "scale_granularity": {"scale": "seven novel saga"},
        "rules": {"magic": "academy law controls royal magic"},
        "chronology": {"history": "founding oath betrayal"},
        "geography": {"regions": ["capital", "border", "low market"]},
        "environment": {"climate": ["fog canals", "relic ridge"]},
        "infrastructure": {"roads": ["Crown Road"]},
        "demographics": {"population": 38000000},
        "society": {"classes": ["noble", "commoner", "erased"]},
        "power_structure": {"factions": ["Academy Orthodoxy", "Silent Register"]},
        "military_security": {"armies": ["Border March Battalion"]},
        "economy": {"resources": ["relic debt", "academy funding"]},
        "law": {"courts": ["Oath Court"]},
        "belief": {"rituals": ["oath bell ceremony"]},
        "culture": {"naming_rules": ["family names control trust"]},
        "knowledge_education": {"forbidden_books": ["Forbidden Exam Scroll"]},
        "institutions": [{"name": "The Ashen Crown Academy"}],
        "technology_magic_science": {"communication_level": "couriers and seals"},
        "species_creatures": {"sacred_animals": ["ledger-crows"]},
        "artifacts": [{"name": "The Ashen Crown Shard"}],
        "aesthetic_texture": {"visual_palette": ["ash white", "ink black"]},
        "civilization_pressure": {"current_crisis": "destiny collapse pressure"},
        "causality_graph": {"links": ["education causes class pressure"]},
        "quality_summary": {
            "consistency_score": 0.85,
            "originality_score": 0.84,
            "story_potential_score": 0.88,
            "training_readiness_score": 0.82,
            "genericness_risk_score": 0.16,
            "quality_tier": "strong",
            "training_eligible": True,
        },
        "dataset_metadata": {
            "training_eligible": True,
            "do_not_train": False,
            "recommended_dataset_split": "train_candidate",
            "dataset_tags": ["dark_academy", "political_fantasy"],
            "risk_tags": [],
        },
        "snapshot": {
            "snapshot_id": "wsnap_demo",
            "snapshot_label": "world_v1",
            "rollback": {"rollback_ready": True},
        },
    }


def test_world_bible_export_engine_returns_engine_result():
    engine = WorldBibleExportEngine()

    result = engine.run(
        {
            "world_state": complete_world_state(),
            "export_format": "markdown_and_json",
        }
    )

    assert isinstance(result, EngineRunResult)
    assert result.success is True
    assert result.engine_name == "world.world_bible_export_engine"
    assert "export_package" in result.data
    assert "training_notes" in result.data
    assert len(result.generated_object_ids) == 1


def test_world_bible_export_engine_generates_markdown_and_json():
    engine = WorldBibleExportEngine()

    result = engine.run(
        {
            "world_state": complete_world_state(),
            "export_format": "markdown_and_json",
        }
    )

    package = result.data["export_package"]

    assert package["export_id"].startswith("wbible_")
    assert package["export_title"] == "Velmora World Bible"
    assert "world_bible_json" in package
    assert "world_bible_markdown" in package
    assert "# Velmora World Bible" in package["world_bible_markdown"]
    assert "## World Identity" in package["world_bible_markdown"]
    assert "## Civilization Pressure" in package["world_bible_markdown"]


def test_world_bible_export_engine_scores_export_readiness():
    engine = WorldBibleExportEngine()

    result = engine.run(
        {
            "world_state": complete_world_state(),
            "export_format": "json",
        }
    )

    package = result.data["export_package"]
    readiness = package["export_readiness"]

    assert readiness["score"] >= 0.78
    assert readiness["readiness_tier"] in {
        "strong_internal_export",
        "publication_ready_internal",
    }
    assert readiness["recommended_next_step"] == "export_to_markdown_or_docx"
    assert package["section_completeness"]["completion_ratio"] >= 0.9


def test_world_bible_export_engine_supports_markdown_only():
    engine = WorldBibleExportEngine()

    result = engine.run(
        {
            "world_state": complete_world_state(),
            "export_format": "markdown",
            "export_title": "Custom Velmora Bible",
        }
    )

    package = result.data["export_package"]

    assert package["export_format"] == "markdown"
    assert "world_bible_markdown" in package
    assert "world_bible_json" not in package
    assert "# Custom Velmora Bible" in package["world_bible_markdown"]


def test_world_bible_export_engine_warns_for_bad_format_and_missing_world():
    engine = WorldBibleExportEngine()

    result = engine.run(
        {
            "world_state": {},
            "export_format": "bad_format",
        }
    )

    assert result.success is True
    assert len(result.warnings) == 2
    assert result.data["export_package"]["export_format"] == "markdown_and_json"
    assert result.data["export_package"]["export_readiness"]["score"] < 0.7

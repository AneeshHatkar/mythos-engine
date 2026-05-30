from backend.app.engines.world.world_template_engine import WorldTemplateEngine
from backend.app.schemas.foundation import EngineRunResult


def test_world_template_engine_returns_catalog_when_no_template_id():
    engine = WorldTemplateEngine()

    result = engine.run({})

    assert isinstance(result, EngineRunResult)
    assert result.success is True
    assert result.engine_name == "world.template_engine"
    assert "available_templates" in result.data
    assert result.data["template_count"] >= 7
    assert len(result.warnings) == 1


def test_world_template_engine_returns_dark_academy_template():
    engine = WorldTemplateEngine()

    result = engine.run(
        {
            "template_id": "dark_academy_empire",
            "seed_premise": "Velmora is entering late imperial collapse.",
        }
    )

    assert result.success is True

    template = result.data["template"]
    payload = result.data["orchestrator_payload"]

    assert template["template_id"] == "dark_academy_empire"
    assert "dark_academy" in template["recommended_genre_tags"]
    assert "political_fantasy" in template["recommended_genre_tags"]
    assert payload["template_id"] == "dark_academy_empire"
    assert "Velmora" in payload["seed_premise"]
    assert "Noble academies control access to power." in payload["seed_premise"]
    assert payload["generation_mode"] == "template_guided_world_orchestration"


def test_world_template_engine_supports_all_core_templates():
    engine = WorldTemplateEngine()

    required_templates = {
        "dark_academy_empire",
        "civilization_simulation",
        "dystopian_megacity",
        "romance_kingdom",
        "mythic_religious_world",
        "movie_scale_world",
        "seven_novel_saga",
    }

    catalog = engine.run({}).data["available_templates"]
    ids = {item["template_id"] for item in catalog}

    assert required_templates.issubset(ids)


def test_world_template_engine_applies_safe_overrides():
    engine = WorldTemplateEngine()

    result = engine.run(
        {
            "template_id": "movie_scale_world",
            "seed_premise": "A single city hides one impossible record.",
            "overrides": {
                "recommended_complexity": "extreme",
                "target_formats": ["film", "pitch_deck"],
                "unsafe_key": "should be ignored",
            },
        }
    )

    template = result.data["template"]
    payload = result.data["orchestrator_payload"]

    assert template["recommended_complexity"] == "extreme"
    assert template["target_formats"] == ["film", "pitch_deck"]
    assert "unsafe_key" in template["ignored_override_keys"]
    assert payload["desired_complexity"] == "extreme"
    assert payload["target_formats"] == ["film", "pitch_deck"]


def test_world_template_engine_rejects_unknown_template():
    engine = WorldTemplateEngine()

    result = engine.run({"template_id": "unknown_template"})

    assert result.success is False
    assert len(result.errors) == 1
    assert "Unknown template_id" in result.errors[0]
    assert "available_templates" in result.data

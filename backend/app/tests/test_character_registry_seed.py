from backend.app.engines.character.character_registry_seed import CharacterRegistrySeedEngine
from backend.app.schemas.foundation import EngineRunResult


def test_character_registry_seed_returns_engine_result():
    engine = CharacterRegistrySeedEngine()

    result = engine.run({})

    assert isinstance(result, EngineRunResult)
    assert result.success is True
    assert result.engine_name == "character.registry_seed_engine"
    assert "registry" in result.data
    assert "registry_summary" in result.data
    assert "training_notes" in result.data


def test_character_registry_contains_required_categories():
    engine = CharacterRegistrySeedEngine()

    result = engine.run({})
    registry = result.data["registry"]

    required_categories = [
        "people_types",
        "character_roles",
        "birth_statuses",
        "social_classes",
        "psychological_wounds",
        "defense_mechanisms",
        "trauma_triggers",
        "goal_types",
        "moral_axes",
        "skill_domains",
        "skill_rarities",
        "skill_ranks",
        "growth_arcs",
        "adaptability_types",
        "limit_break_types",
        "destiny_types",
        "prophecy_roles",
        "legacy_types",
        "mirror_types",
        "dataset_tags",
    ]

    for category in required_categories:
        assert category in registry
        assert len(registry[category]) > 0


def test_character_registry_includes_adaptability_and_limit_break_terms():
    engine = CharacterRegistrySeedEngine()

    result = engine.run({})
    registry = result.data["registry"]

    assert "emotional_adaptability" in registry["adaptability_types"]
    assert "skill_adaptability" in registry["adaptability_types"]
    assert "destiny_adaptability" in registry["adaptability_types"]
    assert "earned_breakthrough" in registry["limit_break_types"]
    assert "relationship_triggered_break" in registry["limit_break_types"]
    assert "world_anomaly_exception" in registry["limit_break_types"]


def test_character_registry_includes_deep_people_types():
    engine = CharacterRegistrySeedEngine()

    result = engine.run({})
    people_types = result.data["registry"]["people_types"]

    ids = {item["id"] for item in people_types}

    assert "people.hidden_kingmaker" in ids
    assert "people.failed_prodigy" in ids
    assert "people.false_saint" in ids
    assert "people.institutional_villain" in ids
    assert "people.adaptive_survivor" in ids
    assert "people.limit_break_anomaly" in ids
    assert "people.ordinary_witness" in ids

    anomaly = next(item for item in people_types if item["id"] == "people.limit_break_anomaly")

    assert "condition" in anomaly["anti_cliche_rule"].lower()
    assert "cost" in anomaly["anti_cliche_rule"].lower()


def test_character_registry_summary_counts_are_correct():
    engine = CharacterRegistrySeedEngine()

    result = engine.run({})
    registry = result.data["registry"]
    summary = result.data["registry_summary"]

    assert summary["people_types"] == len(registry["people_types"])
    assert summary["skill_ranks"] == len(registry["skill_ranks"])
    assert summary["limit_break_types"] == len(registry["limit_break_types"])
    assert summary["dataset_tags"] == len(registry["dataset_tags"])


def test_character_registry_compact_mode_returns_people_type_ids():
    engine = CharacterRegistrySeedEngine()

    result = engine.run({"include_descriptions": False})
    people_types = result.data["registry"]["people_types"]

    assert isinstance(people_types[0], str)
    assert "people.hidden_kingmaker" in people_types


def test_character_registry_lookup_helper():
    engine = CharacterRegistrySeedEngine()

    assert engine.lookup("character_roles", "protagonist") is True
    assert engine.lookup("skill_ranks", "S") is True
    assert engine.lookup("limit_break_types", "earned_breakthrough") is True
    assert engine.lookup("people_types", "people.hidden_kingmaker") is True
    assert engine.lookup("people_types", "Hidden Kingmaker") is True
    assert engine.lookup("character_roles", "random_invalid_role") is False

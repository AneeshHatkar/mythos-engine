from backend.app.engines.world.civilization_pressure_engine import (
    CivilizationPressureEngine,
)
from backend.app.schemas.foundation import EngineRunResult
from backend.app.schemas.world import CivilizationPressureProfile, WorldCausalityGraph


def test_civilization_pressure_engine_returns_engine_result():
    engine = CivilizationPressureEngine()

    result = engine.run(
        {
            "seed_premise": (
                "A late imperial collapse academy empire where relics, oath law, "
                "and 27 destined people create civilization pressure."
            ),
            "genre_tags": ["dark_academy", "political_fantasy"],
            "tone_tags": ["tragic"],
            "desired_complexity": "extreme",
        }
    )

    assert isinstance(result, EngineRunResult)
    assert result.success is True
    assert result.engine_name == "world.civilization_pressure_engine"
    assert "civilization_pressure" in result.data
    assert "causality_graph" in result.data
    assert "training_notes" in result.data


def test_civilization_pressure_engine_generates_pressure_profile():
    engine = CivilizationPressureEngine()

    result = engine.run(
        {
            "seed_premise": (
                "A tragic relic academy empire where oath law hides a founding betrayal "
                "and 27 destined people awaken too quickly."
            ),
            "genre_tags": ["dark_academy", "political_fantasy"],
            "tone_tags": ["tragic"],
            "desired_complexity": "god_level",
        }
    )

    pressure = CivilizationPressureProfile.model_validate(
        result.data["civilization_pressure"]
    )

    assert pressure.current_crisis != ""
    assert pressure.hidden_crisis != ""
    assert pressure.social_pressure != ""
    assert pressure.economic_pressure != ""
    assert pressure.spiritual_pressure != ""
    assert pressure.war_pressure != ""
    assert pressure.mystery_pressure != ""
    assert pressure.villain_pressure != ""
    assert pressure.destiny_pressure != ""
    assert pressure.collapse_timeline != ""
    assert pressure.if_nobody_acts != ""
    assert pressure.if_villain_wins != ""
    assert len(pressure.system_breaking_points) >= 8

    assert "Destiny" in pressure.destiny_pressure or "destiny" in pressure.destiny_pressure
    assert any("relic" in point.lower() for point in pressure.system_breaking_points)


def test_civilization_pressure_engine_generates_causality_graph():
    engine = CivilizationPressureEngine()

    result = engine.run(
        {
            "seed_premise": (
                "A relic academy empire where destiny, oath law, and hidden archives connect all systems."
            ),
            "genre_tags": ["dark_academy", "political_fantasy"],
            "desired_complexity": "god_level",
        }
    )

    graph = WorldCausalityGraph.model_validate(result.data["causality_graph"])

    assert len(graph.links) >= 12
    assert len(graph.root_causes) >= 5
    assert len(graph.likely_future_effects) >= 5

    for link in graph.links:
        assert link.cause != ""
        assert link.effect != ""
        assert 0.0 <= link.strength <= 1.0
        assert len(link.affected_systems) >= 2
        assert link.story_use != ""

    assert any("relic" in link.cause.lower() for link in graph.links)
    assert any("destiny" in link.cause.lower() for link in graph.links)
    assert any("oath" in link.cause.lower() for link in graph.links)


def test_civilization_pressure_engine_has_ml_ready_transition_logic():
    engine = CivilizationPressureEngine()

    result = engine.run(
        {
            "seed_premise": "A complex academy empire with institutions depending on each other's lies.",
            "genre_tags": ["dark_academy"],
            "desired_complexity": "god_level",
        }
    )

    graph = WorldCausalityGraph.model_validate(result.data["causality_graph"])

    assert any("training_metadata" in link.affected_systems for link in graph.links)
    assert any("orchestrator" in effect.lower() for effect in graph.likely_future_effects)


def test_civilization_pressure_engine_warns_when_seed_missing():
    engine = CivilizationPressureEngine()

    result = engine.run({})

    assert result.success is True
    assert len(result.warnings) == 1
    assert "seed_premise" in result.warnings[0]

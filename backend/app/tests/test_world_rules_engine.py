from backend.app.engines.world.world_rules_engine import WorldRulesEngine
from backend.app.schemas.foundation import EngineRunResult
from backend.app.schemas.world import (
    WorldBoundaryConstraintProfile,
    WorldContradictionIntent,
    WorldRuleSet,
)


def test_world_rules_engine_returns_engine_result():
    engine = WorldRulesEngine()

    result = engine.run(
        {
            "seed_premise": (
                "A late imperial collapse world where noble academies control magic, "
                "relics, oaths, and 27 destined people awaken too quickly."
            ),
            "genre_tags": ["dark_academy", "political_fantasy"],
            "tone_tags": ["tragic"],
            "desired_complexity": "extreme",
        }
    )

    assert isinstance(result, EngineRunResult)
    assert result.success is True
    assert result.engine_name == "world.rules_engine"
    assert "rules" in result.data
    assert "boundary_constraints" in result.data
    assert "contradiction_intent" in result.data


def test_world_rules_engine_generates_deep_rule_set():
    engine = WorldRulesEngine()

    result = engine.run(
        {
            "seed_premise": (
                "An academy empire where commoners cannot legally study royal magic, "
                "relic mines fund institutions, and destined people destabilize society."
            ),
            "genre_tags": ["dark_academy", "political_fantasy"],
            "desired_complexity": "god_level",
        }
    )

    rules = WorldRuleSet.model_validate(result.data["rules"])

    assert len(rules.magic_rules) >= 1
    assert len(rules.destiny_rules) >= 1
    assert len(rules.artifact_rules) >= 1
    assert len(rules.knowledge_rules) >= 1
    assert len(rules.social_mobility_rules) >= 1
    assert len(rules.global_constraints) >= 5

    magic_rule = rules.magic_rules[0]
    assert "approved institutions" in magic_rule.description
    assert len(magic_rule.loopholes) >= 1
    assert len(magic_rule.story_uses) >= 1


def test_world_rules_engine_generates_boundaries():
    engine = WorldRulesEngine()

    result = engine.run(
        {
            "seed_premise": "A magic academy empire with forbidden provinces.",
            "genre_tags": ["dark_academy"],
            "desired_complexity": "extreme",
        }
    )

    boundaries = WorldBoundaryConstraintProfile.model_validate(
        result.data["boundary_constraints"]
    )

    assert len(boundaries.known_world_boundaries) >= 1
    assert len(boundaries.believed_outside_world) >= 1
    assert len(boundaries.actual_outside_world) >= 1
    assert len(boundaries.knowledge_boundaries) >= 1
    assert len(boundaries.sequel_expansion_potential) >= 1
    assert any("archive" in item.lower() for item in boundaries.knowledge_boundaries)


def test_world_rules_engine_generates_intentional_contradictions():
    engine = WorldRulesEngine()

    result = engine.run(
        {
            "seed_premise": (
                "A relic academy empire where noble law claims merit but blocks commoners."
            ),
            "genre_tags": ["dark_academy", "romance"],
            "desired_complexity": "god_level",
        }
    )

    contradictions = WorldContradictionIntent.model_validate(
        result.data["contradiction_intent"]
    )

    assert len(contradictions.intentional_hypocrisies) >= 1
    assert len(contradictions.social_contradictions) >= 1
    assert len(contradictions.legal_contradictions) >= 1
    assert len(contradictions.economic_contradictions) >= 1
    assert len(contradictions.bad_contradiction_risks) >= 1
    assert any("merit" in item.lower() for item in contradictions.intentional_hypocrisies)


def test_world_rules_engine_warns_when_seed_missing():
    engine = WorldRulesEngine()

    result = engine.run({})

    assert result.success is True
    assert len(result.warnings) == 1
    assert "seed_premise" in result.warnings[0]

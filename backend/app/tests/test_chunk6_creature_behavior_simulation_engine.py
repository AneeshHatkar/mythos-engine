from backend.app.engines.deep_world.creature_behavior_simulation_engine import CreatureBehaviorSimulationEngine
from backend.app.engines.deep_world.fauna_generator import FaunaGenerator


def build_fauna():
    generator = FaunaGenerator()
    return generator.build_fauna(source_id="behavior_fauna_source")["deep_world_fauna"]


def test_creature_behavior_engine_builds_behavior_profile():
    fauna = build_fauna()
    engine = CreatureBehaviorSimulationEngine()

    profile = engine.build_behavior_profile(
        source_id="behavior_profile_test",
        fauna=fauna,
    )["creature_behavior_profile"]

    assert profile["fauna_id"] == fauna.element_id
    assert profile["fauna_name"] == fauna.name
    assert profile["species_identity"]["unique_name"] == fauna.name
    assert profile["baseline_behavior"]
    assert profile["migration_triggers"]
    assert profile["fear_triggers"]
    assert profile["aggression_triggers"]
    assert profile["social_behavior"]
    assert profile["human_interaction_rules"]
    assert profile["detail_depth_score"] >= 0.75


def test_creature_behavior_engine_simulates_behavior_event():
    fauna = build_fauna()
    engine = CreatureBehaviorSimulationEngine()
    profile = engine.build_behavior_profile(
        source_id="behavior_event_test",
        fauna=fauna,
    )["creature_behavior_profile"]

    event = engine.simulate_behavior_event(
        source_id="behavior_event_test",
        behavior_profile=profile,
        event_seed={
            "event_name": "Bellhorn Road Refusal",
            "event_type": "route_warning",
            "trigger": "the herd refused to cross the old witness road",
            "location": "north road shrine",
            "hidden_cause": "fresh predator musk and buried oath-blood marked the crossing",
        },
    )["creature_behavior_event"]

    assert event["behavior_profile_id"] == profile["behavior_profile_id"]
    assert event["fauna_id"] == fauna.element_id
    assert event["event_name"] == "Bellhorn Road Refusal"
    assert event["story_use"]
    assert event["character_effect"]
    assert event["plot_effect"]
    assert event["memory_effect"]
    assert event["lore_effect"]
    assert event["detail_depth_score"] >= 0.75


def test_creature_behavior_engine_builds_story_context_patch():
    fauna = build_fauna()
    engine = CreatureBehaviorSimulationEngine()
    profile = engine.build_behavior_profile(source_id="behavior_patch_test", fauna=fauna)["creature_behavior_profile"]
    event = engine.simulate_behavior_event(
        source_id="behavior_patch_test",
        behavior_profile=profile,
    )["creature_behavior_event"]

    patch = engine.build_story_context_patch(
        behavior_profile=profile,
        behavior_event=event,
    )["story_context_patch"]

    assert patch["behavior_profile_id"] == profile["behavior_profile_id"]
    assert patch["active_behavior_event"]["behavior_event_id"] == event["behavior_event_id"]
    assert "generation_hints" in patch
    assert "memory_update_candidates" in patch
    assert len(patch["memory_update_candidates"]) == 2


def test_creature_behavior_engine_validates_profile_and_event():
    fauna = build_fauna()
    engine = CreatureBehaviorSimulationEngine()
    profile = engine.build_behavior_profile(source_id="behavior_validate_test", fauna=fauna)["creature_behavior_profile"]
    event = engine.simulate_behavior_event(
        source_id="behavior_validate_test",
        behavior_profile=profile,
    )["creature_behavior_event"]

    profile_validation = engine.validate_behavior_profile(behavior_profile=profile)
    event_validation = engine.validate_behavior_event(behavior_event=event)

    assert profile_validation["passed"] is True
    assert profile_validation["missing_fields"] == []
    assert event_validation["passed"] is True
    assert event_validation["missing_fields"] == []


def test_creature_behavior_engine_detects_bad_behavior_records():
    engine = CreatureBehaviorSimulationEngine()

    profile_validation = engine.validate_behavior_profile(
        behavior_profile={
            "behavior_profile_id": "bad_profile",
            "fauna_id": "fauna_bad",
            "story_use": "Bad.",
        }
    )

    event_validation = engine.validate_behavior_event(
        behavior_event={
            "behavior_event_id": "bad_event",
            "event_name": "Animal did thing",
            "plot_effect": "Bad.",
        }
    )

    assert profile_validation["passed"] is False
    assert profile_validation["missing_fields"]
    assert "story_use" in profile_validation["shallow_fields"]

    assert event_validation["passed"] is False
    assert event_validation["missing_fields"]
    assert "plot_effect" in event_validation["shallow_fields"]


def test_creature_behavior_engine_summarizes_and_textualizes():
    fauna = build_fauna()
    engine = CreatureBehaviorSimulationEngine()
    profile = engine.build_behavior_profile(source_id="behavior_text_test", fauna=fauna)["creature_behavior_profile"]

    summary = engine.summarize_behavior_profile(behavior_profile=profile)
    text = engine.build_behavior_text(behavior_profile=profile)["behavior_text"]

    assert summary["success"] is True
    assert summary["summary"]["behavior_profile_id"] == profile["behavior_profile_id"]
    assert "Creature Behavior Simulation Profile" in text
    assert "Migration Triggers" in text
    assert "Memory Effect" in text

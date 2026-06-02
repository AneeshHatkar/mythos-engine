from backend.app.engines.deep_world.climate_weather_engine import ClimateWeatherSimulationEngine
from backend.app.schemas.deep_world import DeepWorldClimateSystem, DeepWorldValidationStatus


def test_climate_weather_engine_builds_climate_system():
    engine = ClimateWeatherSimulationEngine()

    climate = engine.build_climate_system(
        source_id="climate_test",
        climate_seed={
            "name": "Ashglass Storm Cycle",
            "region_name": "Ashglass Coast",
            "climate_type": "coastal ash-storm climate",
            "dominant_weather": "salt lightning and ash rain",
            "dangerous_weather": "glass-cutting storm wind",
            "sacred_weather": "blue lightning over drowned temples",
            "disaster_risk": "red tide storm surge",
            "climate_lore": "sailors believe blue lightning marks drowned saints watching the shore.",
            "tags": ["coast", "storm"],
        },
        story_context={"genre": "fantasy", "tone": "mythic"},
    )["deep_world_climate_system"]

    assert isinstance(climate, DeepWorldClimateSystem)
    assert climate.name == "Ashglass Storm Cycle"
    assert climate.validation_status == DeepWorldValidationStatus.VALIDATED
    assert "salt lightning" in climate.weather_patterns[0]
    assert "glass-cutting" in climate.metadata["dangerous_weather"]
    assert "fantasy" in climate.tags
    assert climate.story_use
    assert climate.character_effect
    assert climate.plot_effect
    assert climate.memory_effect


def test_climate_weather_engine_simulates_weather_event():
    engine = ClimateWeatherSimulationEngine()
    climate = engine.build_climate_system(source_id="weather_event_test")["deep_world_climate_system"]

    event = engine.simulate_weather_event(
        source_id="weather_event_test",
        climate=climate,
        event_seed={
            "event_name": "Bell Rain Road Flood",
            "severity": "medium",
            "duration": "two days",
            "affected_locations": ["north road", "lower market"],
        },
    )["weather_event"]

    assert event["event_name"] == "Bell Rain Road Flood"
    assert event["climate_id"] == climate.element_id
    assert event["character_effect"]
    assert event["plot_effect"]
    assert event["memory_effect"]
    assert event["lore_effect"]
    assert event["detail_depth_score"] >= 0.75


def test_climate_weather_engine_builds_story_context_patch():
    engine = ClimateWeatherSimulationEngine()
    climate = engine.build_climate_system(source_id="climate_patch_test")["deep_world_climate_system"]
    event = engine.simulate_weather_event(source_id="climate_patch_test", climate=climate)["weather_event"]

    patch = engine.build_story_context_patch(
        climate=climate,
        weather_event=event,
    )["story_context_patch"]

    assert patch["climate_id"] == climate.element_id
    assert patch["active_weather_event"]["weather_event_id"] == event["weather_event_id"]
    assert "generation_hints" in patch
    assert "memory_update_candidates" in patch
    assert len(patch["memory_update_candidates"]) >= 2


def test_climate_weather_engine_validates_climate_and_weather_event():
    engine = ClimateWeatherSimulationEngine()
    climate = engine.build_climate_system(source_id="climate_validate_test")["deep_world_climate_system"]
    event = engine.simulate_weather_event(source_id="climate_validate_test", climate=climate)["weather_event"]

    climate_validation = engine.validate_climate_system(climate=climate)
    event_validation = engine.validate_weather_event(weather_event=event)

    assert climate_validation["passed"] is True
    assert climate_validation["blockers"] == []
    assert event_validation["passed"] is True
    assert event_validation["missing_fields"] == []


def test_climate_weather_engine_detects_bad_weather_event():
    engine = ClimateWeatherSimulationEngine()

    validation = engine.validate_weather_event(
        weather_event={
            "weather_event_id": "bad_weather",
            "event_name": "Rain",
            "plot_effect": "Bad.",
        }
    )

    assert validation["passed"] is False
    assert validation["missing_fields"]
    assert "plot_effect" in validation["shallow_fields"]


def test_climate_weather_engine_summarizes_and_textualizes():
    engine = ClimateWeatherSimulationEngine()
    climate = engine.build_climate_system(source_id="climate_text_test")["deep_world_climate_system"]

    summary = engine.summarize_climate_system(climate=climate)
    text = engine.build_climate_text(climate=climate)["climate_text"]

    assert summary["success"] is True
    assert summary["summary"]["climate_id"] == climate.element_id
    assert "Deep World Climate + Weather System" in text
    assert "Story Use" in text
    assert "Memory Effect" in text

from backend.app.engines.world.chronology_engine import ChronologyEngine
from backend.app.schemas.foundation import EngineRunResult
from backend.app.schemas.world import ChronologyProfile, WorldMemoryArchive


def test_chronology_engine_returns_engine_result():
    engine = ChronologyEngine()

    result = engine.run(
        {
            "world_name": "Velmora",
            "seed_premise": (
                "A late imperial collapse world where noble academies control relics, "
                "oaths, royal magic, and 27 destined people awaken too quickly."
            ),
            "genre_tags": ["dark_academy", "political_fantasy"],
            "tone_tags": ["tragic"],
            "desired_complexity": "extreme",
        }
    )

    assert isinstance(result, EngineRunResult)
    assert result.success is True
    assert result.engine_name == "world.chronology_engine"
    assert "chronology" in result.data
    assert "memory_archive" in result.data
    assert "training_notes" in result.data


def test_chronology_engine_generates_deep_history():
    engine = ChronologyEngine()

    result = engine.run(
        {
            "world_name": "Velmora",
            "seed_premise": (
                "A late imperial collapse world where academies control relics, "
                "oaths, and 27 destined people."
            ),
            "genre_tags": ["dark_academy", "political_fantasy"],
            "tone_tags": ["tragic"],
            "desired_complexity": "god_level",
        }
    )

    chronology = ChronologyProfile.model_validate(result.data["chronology"])

    assert chronology.creation_myth != ""
    assert chronology.official_history_summary != ""
    assert chronology.true_history_summary != ""
    assert chronology.current_era in {"Late Imperial Collapse", "The Era of Unstable Fates"}
    assert len(chronology.eras) >= 5
    assert len(chronology.erased_history) >= 3
    assert len(chronology.historical_lies) >= 3
    assert len(chronology.historical_wounds) >= 2


def test_chronology_engine_separates_public_and_true_history():
    engine = ChronologyEngine()

    result = engine.run(
        {
            "world_name": "Velmora",
            "seed_premise": "An academy empire built on erased history and oath law.",
            "genre_tags": ["dark_academy"],
        }
    )

    chronology = ChronologyProfile.model_validate(result.data["chronology"])

    assert chronology.official_history_summary != chronology.true_history_summary

    all_events = [
        event
        for era in chronology.eras
        for event in era.major_events
    ]

    assert any(event.public_version != event.true_version for event in all_events)
    assert any("academy" in event.public_version.lower() or "academy" in event.true_version.lower() for event in all_events)


def test_chronology_engine_generates_destiny_history_when_seed_has_destiny():
    engine = ChronologyEngine()

    result = engine.run(
        {
            "world_name": "Velmora",
            "seed_premise": (
                "A world where 27 destined people awaken and destabilize academy law."
            ),
            "genre_tags": ["dark_academy"],
            "desired_complexity": "extreme",
        }
    )

    chronology = ChronologyProfile.model_validate(result.data["chronology"])

    all_event_names = [
        event.name
        for era in chronology.eras
        for event in era.major_events
    ]

    all_wound_names = [wound.name for wound in chronology.historical_wounds]

    assert any("Destiny" in name for name in all_event_names)
    assert any("Destiny" in name for name in all_wound_names)


def test_chronology_engine_generates_world_memory_archive():
    engine = ChronologyEngine()

    result = engine.run(
        {
            "world_name": "Velmora",
            "seed_premise": (
                "A relic academy empire where oath law hides a founding betrayal."
            ),
            "genre_tags": ["dark_academy", "political_fantasy"],
            "desired_complexity": "god_level",
        }
    )

    memory = WorldMemoryArchive.model_validate(result.data["memory_archive"])

    assert len(memory.archived_events) >= 5
    assert len(memory.law_changes) >= 3
    assert len(memory.faction_changes) >= 3
    assert len(memory.destroyed_locations) >= 1
    assert len(memory.lost_artifacts) >= 1
    assert len(memory.broken_promises) >= 1
    assert len(memory.world_state_snapshots) >= 1


def test_chronology_engine_warns_when_seed_missing():
    engine = ChronologyEngine()

    result = engine.run({})

    assert result.success is True
    assert len(result.warnings) == 1
    assert "seed_premise" in result.warnings[0]

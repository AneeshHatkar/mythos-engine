from backend.app.engines.world.power_faction_military_engine import (
    PowerFactionMilitaryEngine,
)
from backend.app.schemas.foundation import EngineRunResult
from backend.app.schemas.world import MilitarySecurityProfile, PowerStructureProfile


def test_power_faction_military_engine_returns_engine_result():
    engine = PowerFactionMilitaryEngine()

    result = engine.run(
        {
            "seed_premise": (
                "A late imperial academy empire where relic financiers, noble houses, "
                "hidden archivists, and destiny boards fight for power."
            ),
            "genre_tags": ["dark_academy", "political_fantasy"],
            "tone_tags": ["tragic"],
            "desired_complexity": "extreme",
        }
    )

    assert isinstance(result, EngineRunResult)
    assert result.success is True
    assert result.engine_name == "world.power_faction_military_engine"
    assert "power_structure" in result.data
    assert "military_security" in result.data
    assert "training_notes" in result.data


def test_power_faction_military_engine_generates_power_structure():
    engine = PowerFactionMilitaryEngine()

    result = engine.run(
        {
            "seed_premise": (
                "A relic academy empire where noble houses, hidden archivists, "
                "and destiny classification boards control society."
            ),
            "genre_tags": ["dark_academy", "political_fantasy"],
            "desired_complexity": "god_level",
        }
    )

    power = PowerStructureProfile.model_validate(result.data["power_structure"])

    assert power.public_authority != ""
    assert power.real_authority != ""
    assert len(power.ruling_groups) >= 4
    assert len(power.hidden_rulers) >= 3
    assert len(power.kingmakers) >= 4
    assert len(power.factions) >= 6
    assert len(power.alliance_map) >= 4
    assert len(power.power_instability_notes) >= 4

    faction_names = [faction.name for faction in power.factions]

    assert "The Founding Houses Bloc" in faction_names
    assert "The Academy Orthodoxy" in faction_names
    assert "The Silent Register" in faction_names
    assert "The Relic Investment Consortium" in faction_names
    assert "The Destiny Classification Board" in faction_names


def test_power_faction_military_engine_generates_faction_depth():
    engine = PowerFactionMilitaryEngine()

    result = engine.run(
        {
            "seed_premise": "An academy empire with relic mines and hidden archive power.",
            "genre_tags": ["dark_academy", "political_fantasy"],
            "desired_complexity": "extreme",
        }
    )

    power = PowerStructureProfile.model_validate(result.data["power_structure"])

    for faction in power.factions:
        assert faction.name != ""
        assert faction.faction_type != ""
        assert faction.public_goal != ""
        assert faction.hidden_goal != ""
        assert len(faction.resources) >= 3
        assert len(faction.story_uses) >= 2
        assert 0.0 <= faction.betrayal_probability <= 1.0


def test_power_faction_military_engine_generates_military_security():
    engine = PowerFactionMilitaryEngine()

    result = engine.run(
        {
            "seed_premise": (
                "A border empire with relic convoys, destiny-bearing people, "
                "academy security, and surveillance pressure."
            ),
            "genre_tags": ["dark_academy", "political_fantasy", "dystopian"],
            "desired_complexity": "god_level",
        }
    )

    military = MilitarySecurityProfile.model_validate(result.data["military_security"])

    assert len(military.armies) >= 3
    assert len(military.elite_units) >= 3
    assert len(military.police_or_security_forces) >= 4
    assert len(military.spy_networks) >= 4
    assert len(military.assassin_or_special_orders) >= 2
    assert len(military.military_ranks) >= 6
    assert military.war_readiness_score >= 0.6
    assert len(military.current_war_risks) >= 4
    assert military.military_corruption != ""

    assert any("Fate" in unit or "destiny" in unit.lower() for unit in military.elite_units)
    assert any("surveillance" in risk.lower() for risk in military.current_war_risks)


def test_power_faction_military_engine_warns_when_seed_missing():
    engine = PowerFactionMilitaryEngine()

    result = engine.run({})

    assert result.success is True
    assert len(result.warnings) == 1
    assert "seed_premise" in result.warnings[0]

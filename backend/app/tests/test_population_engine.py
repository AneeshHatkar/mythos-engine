from backend.app.engines.character.population_engine import PopulationEngine
from backend.app.schemas.character import PopulationGroup
from backend.app.schemas.foundation import EngineRunResult


def test_population_engine_returns_engine_result():
    engine = PopulationEngine()

    result = engine.run(
        {
            "world_id": "world_velmora",
            "world_name": "Velmora",
            "target_population": 100000,
            "world_state": {
                "identity": {"world_name": "Velmora"},
                "rules": {"magic": "commoners cannot legally study royal magic"},
            },
        }
    )

    assert isinstance(result, EngineRunResult)
    assert result.success is True
    assert result.engine_name == "character.population_engine"
    assert "population_groups" in result.data
    assert "population_summary" in result.data
    assert "rarity_controls" in result.data
    assert "character_generation_guidance" in result.data


def test_population_engine_generates_valid_population_groups():
    engine = PopulationEngine()

    result = engine.run(
        {
            "world_id": "world_velmora",
            "world_name": "Velmora",
            "target_population": 100000,
            "world_state": {
                "identity": {"world_name": "Velmora"},
                "economy": {"core_resource": "relic mining"},
                "institutions": {"academy": "elite institutions"},
            },
        }
    )

    groups = [
        PopulationGroup.model_validate(item)
        for item in result.data["population_groups"]
    ]

    assert len(groups) >= 8
    assert all(group.world_id == "world_velmora" for group in groups)
    assert all(group.estimated_count >= 0 for group in groups)
    assert all(0.0 <= group.education_access <= 1.0 for group in groups)
    assert all(0.0 <= group.destiny_density <= 1.0 for group in groups)

    names = {group.group_name for group in groups}

    assert "Imperial elite houses" in names
    assert "Relic-mining labor populations" in names
    assert "Erased, undocumented, and underclass people" in names


def test_population_engine_creates_rarity_controls():
    engine = PopulationEngine()

    result = engine.run(
        {
            "world_id": "world_velmora",
            "world_name": "Velmora",
            "target_population": 200000,
            "world_state": {
                "identity": {"world_name": "Velmora"},
                "civilization_pressure": {"destiny": "destiny-bearing people appearing too fast"},
            },
        }
    )

    controls = result.data["rarity_controls"]

    assert controls["total_population_modeled"] > 0
    assert controls["estimated_destiny_bearers"] > 0
    assert controls["estimated_rare_skill_people"] > 0
    assert controls["destiny_ratio"] < 0.1
    assert controls["rare_skill_ratio"] < 0.1
    assert controls["recommended_major_character_destiny_cap"] >= 1
    assert controls["limit_break_anomaly_cap"] >= 1


def test_population_engine_guidance_prevents_generic_casts():
    engine = PopulationEngine()

    result = engine.run(
        {
            "world_id": "world_velmora",
            "world_name": "Velmora",
            "target_population": 100000,
            "world_state": {
                "identity": {"world_name": "Velmora"},
                "locations": ["academy", "border ruins", "underground market"],
            },
        }
    )

    guidance = result.data["character_generation_guidance"]

    anti_generic = " ".join(guidance["anti_generic_rules"]).lower()

    assert "not make every major character noble" in anti_generic
    assert "rare skills require cost" in anti_generic
    assert "limit-break anomaly" in anti_generic
    assert len(guidance["high_pressure_groups"]) >= 2
    assert len(guidance["low_access_groups"]) >= 2


def test_population_engine_uses_world_pressure_terms():
    engine = PopulationEngine()

    academy_result = engine.run(
        {
            "world_id": "world_velmora",
            "world_name": "Velmora",
            "target_population": 100000,
            "desired_complexity": "god_level",
            "world_state": {
                "identity": {"world_name": "Velmora"},
                "main_conflict": "noble academies control access to power",
                "economy": "relic mining cities fund elite institutions",
                "locations": ["academy", "border ruins"],
            },
        }
    )

    groups = {
        item["social_class"]: item
        for item in academy_result.data["population_groups"]
    }

    assert groups["academy_sponsored"]["destiny_density"] > 0.035
    assert groups["relic_miner"]["danger_exposure"] > 0.86
    assert groups["borderfolk"]["rare_skill_density"] > 0.035


def test_population_engine_warns_without_world_state():
    engine = PopulationEngine()

    result = engine.run({})

    assert result.success is True
    assert len(result.warnings) == 1
    assert "world_state" in result.warnings[0]
    assert result.data["population_summary"]["world_name"] == "Velmora"


def test_population_engine_generated_object_ids_match_groups():
    engine = PopulationEngine()

    result = engine.run(
        {
            "world_id": "world_velmora",
            "world_name": "Velmora",
            "target_population": 100000,
        }
    )

    group_ids = {group["group_id"] for group in result.data["population_groups"]}

    assert set(result.generated_object_ids) == group_ids

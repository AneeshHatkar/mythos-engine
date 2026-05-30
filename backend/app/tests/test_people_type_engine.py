from backend.app.engines.character.people_type_engine import PeopleTypeEngine
from backend.app.schemas.character import PeopleTypeProfile
from backend.app.schemas.foundation import EngineRunResult


def sample_population_groups():
    return [
        {
            "group_name": "Imperial elite houses",
            "social_class": "imperial_elite",
            "danger_exposure": 0.25,
        },
        {
            "group_name": "Academy-sponsored strivers",
            "social_class": "academy_sponsored",
            "danger_exposure": 0.55,
        },
        {
            "group_name": "Relic-mining labor populations",
            "social_class": "relic_miner",
            "danger_exposure": 0.88,
        },
        {
            "group_name": "Erased, undocumented, and underclass people",
            "social_class": "erased",
            "danger_exposure": 0.82,
        },
        {
            "group_name": "Commoner households",
            "social_class": "commoner",
            "danger_exposure": 0.5,
        },
    ]


def test_people_type_engine_returns_engine_result():
    engine = PeopleTypeEngine()

    result = engine.run(
        {
            "world_state": {
                "identity": {"world_name": "Velmora"},
                "religion": "oath gods",
            },
            "population_groups": sample_population_groups(),
        }
    )

    assert isinstance(result, EngineRunResult)
    assert result.success is True
    assert result.engine_name == "character.people_type_engine"
    assert "people_types" in result.data
    assert "role_type_map" in result.data
    assert "people_type_summary" in result.data
    assert "sampling_guidance" in result.data


def test_people_type_engine_generates_valid_profiles():
    engine = PeopleTypeEngine()

    result = engine.run(
        {
            "world_state": {
                "identity": {"world_name": "Velmora"},
                "main_conflict": "noble academies control power",
            },
            "population_groups": sample_population_groups(),
        }
    )

    profiles = [
        PeopleTypeProfile.model_validate(item)
        for item in result.data["people_types"]
    ]

    assert len(profiles) >= 7
    assert all(profile.people_type_id.startswith("ptype_") for profile in profiles)
    assert all(profile.description for profile in profiles)
    assert all(profile.anti_cliche_notes for profile in profiles)

    names = {profile.name for profile in profiles}

    assert "Hidden Kingmaker" in names
    assert "Institutional Villain" in names
    assert "Ordinary Witness" in names
    assert "Limit-Break Anomaly" in names


def test_people_type_engine_includes_limit_break_logic():
    engine = PeopleTypeEngine()

    result = engine.run(
        {
            "world_state": {
                "identity": {"world_name": "Velmora"},
                "rules": {"destiny": "destiny-bearing people are appearing too fast"},
            },
            "population_groups": sample_population_groups(),
            "include_limit_break_types": True,
        }
    )

    people_types = result.data["people_types"]
    anomaly = next(item for item in people_types if item["people_type_id"] == "ptype_limit_break_anomaly")

    notes = " ".join(anomaly["anti_cliche_notes"]).lower()
    pressure = " ".join(anomaly["pressure_responses"]).lower()

    assert "condition" in notes
    assert "cost" in notes
    assert "risk" in notes
    assert "consequence" in notes
    assert "threshold" in pressure or "surges" in pressure


def test_people_type_engine_can_disable_limit_break_type():
    engine = PeopleTypeEngine()

    result = engine.run(
        {
            "world_state": {"identity": {"world_name": "Velmora"}},
            "population_groups": sample_population_groups(),
            "include_limit_break_types": False,
        }
    )

    ids = {item["people_type_id"] for item in result.data["people_types"]}

    assert "ptype_limit_break_anomaly" not in ids
    assert result.data["people_type_summary"]["has_limit_break_type"] is False


def test_people_type_engine_adds_oath_burdened_believer_for_religious_worlds():
    engine = PeopleTypeEngine()

    result = engine.run(
        {
            "world_state": {
                "identity": {"world_name": "Velmora"},
                "religion": "people worship forgotten oath-gods",
                "law": "oath courts punish broken promises",
            },
            "population_groups": sample_population_groups(),
        }
    )

    ids = {item["people_type_id"] for item in result.data["people_types"]}

    assert "ptype_oath_burdened_believer" in ids


def test_people_type_engine_builds_role_map():
    engine = PeopleTypeEngine()

    result = engine.run(
        {
            "world_state": {"identity": {"world_name": "Velmora"}},
            "population_groups": sample_population_groups(),
        }
    )

    role_map = result.data["role_type_map"]

    assert "protagonist" in role_map
    assert "villain" in role_map
    assert "love_interest" in role_map
    assert "ordinary_citizen" in role_map
    assert "ptype_institutional_villain" in role_map["villain"]


def test_people_type_engine_prioritizes_target_roles():
    engine = PeopleTypeEngine()

    result = engine.run(
        {
            "world_state": {"identity": {"world_name": "Velmora"}},
            "population_groups": sample_population_groups(),
            "target_roles": ["villain"],
        }
    )

    first = result.data["people_types"][0]

    assert "villain" in first["compatible_roles"]


def test_people_type_engine_sampling_guidance_prevents_cliches():
    engine = PeopleTypeEngine()

    result = engine.run(
        {
            "world_state": {"identity": {"world_name": "Velmora"}},
            "population_groups": sample_population_groups(),
        }
    )

    guidance = result.data["sampling_guidance"]
    anti_cliche = " ".join(guidance["anti_cliche_rules"]).lower()

    assert "villain needs ideology" in anti_cliche
    assert "love interest needs independent goals" in anti_cliche
    assert "limit-break character needs condition" in anti_cliche
    assert len(guidance["recommended_pressure_groups"]) >= 2


def test_people_type_engine_warns_when_context_missing():
    engine = PeopleTypeEngine()

    result = engine.run({})

    assert result.success is True
    assert len(result.warnings) == 2
    assert "world_state" in result.warnings[0]
    assert "population_groups" in result.warnings[1]

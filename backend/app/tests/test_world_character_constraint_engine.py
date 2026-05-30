from backend.app.engines.character.world_character_constraint_engine import WorldCharacterConstraintEngine
from backend.app.schemas.foundation import EngineRunResult


def velmora_world_state():
    return {
        "identity": {"world_name": "Velmora"},
        "rules": {
            "magic": "commoners cannot legally study royal magic",
            "trust": "family names determine legal trust",
        },
        "society": {
            "hierarchy": "noble academies control access to power",
        },
        "economy": {
            "core": "relic-mining cities fund elite institutions",
        },
        "belief": {
            "religion": "people worship forgotten oath-gods and obey oath law",
        },
        "civilization_pressure": {
            "destiny": "destiny-bearing people are appearing too fast",
        },
        "locations": ["academy", "capital", "border ruins", "underground market"],
    }


def population_context():
    return {
        "population_groups": [
            {"group_name": "Commoners", "social_class": "commoner"},
            {"group_name": "Academy sponsored", "social_class": "academy_sponsored"},
            {"group_name": "Old nobles", "social_class": "old_nobility"},
            {"group_name": "Erased people", "social_class": "erased"},
        ]
    }


def test_world_character_constraint_engine_returns_engine_result():
    engine = WorldCharacterConstraintEngine()

    result = engine.run(
        {
            "world_state": velmora_world_state(),
            "character_seed": {
                "name": "Kael Veyran",
                "role": "protagonist",
                "social_class": "commoner",
            },
            "population_context": population_context(),
        }
    )

    assert isinstance(result, EngineRunResult)
    assert result.success is True
    assert result.engine_name == "character.world_character_constraint_engine"
    assert "world_constraints" in result.data
    assert "constraint_checks" in result.data
    assert "constraint_risk_summary" in result.data
    assert "repair_plan" in result.data
    assert "grounding_profile" in result.data


def test_constraint_engine_detects_commoner_royal_magic_violation():
    engine = WorldCharacterConstraintEngine()

    result = engine.run(
        {
            "world_state": velmora_world_state(),
            "character_seed": {
                "name": "Kael Veyran",
                "role": "protagonist",
                "social_class": "commoner",
                "desired_power": "royal magic",
                "education_goal": "academy royal magic training",
                "family_name_status": "erased",
            },
            "population_context": population_context(),
        }
    )

    checks = result.data["constraint_checks"]
    magic_check = next(check for check in checks if check["check_id"] == "commoner_magic_access")

    assert magic_check["status"] == "violation"
    assert magic_check["severity"] == "high"
    assert "sponsor" in magic_check["required_fix"].lower()

    summary = result.data["constraint_risk_summary"]

    assert summary["violation_count"] >= 1
    assert summary["world_grounding_score"] < 1.0
    assert result.data["grounding_profile"]["can_advance_to_genesis"] is False


def test_constraint_engine_accepts_explained_commoner_magic_exception():
    engine = WorldCharacterConstraintEngine()

    result = engine.run(
        {
            "world_state": velmora_world_state(),
            "character_seed": {
                "name": "Kael Veyran",
                "role": "protagonist",
                "social_class": "commoner",
                "desired_power": "royal magic",
                "education_goal": "academy royal magic training",
                "family_name_status": "erased",
                "access_explanation": "forged scholarship under a dead noble name",
            },
            "population_context": population_context(),
        }
    )

    checks = result.data["constraint_checks"]
    magic_check = next(check for check in checks if check["check_id"] == "commoner_magic_access")

    assert magic_check["status"] == "explained_exception"
    assert "Forbidden education" in magic_check["story_hook"]


def test_constraint_engine_requires_family_name_status_when_world_uses_legal_trust():
    engine = WorldCharacterConstraintEngine()

    result = engine.run(
        {
            "world_state": velmora_world_state(),
            "character_seed": {
                "name": "Mira Solen",
                "role": "love_interest",
                "social_class": "old_nobility",
            },
            "population_context": population_context(),
        }
    )

    checks = result.data["constraint_checks"]
    trust_check = next(check for check in checks if check["check_id"] == "family_name_trust")

    assert trust_check["status"] == "needs_detail"
    assert "family-name status" in trust_check["required_fix"]


def test_constraint_engine_checks_academy_access_for_low_class_character():
    engine = WorldCharacterConstraintEngine()

    result = engine.run(
        {
            "world_state": velmora_world_state(),
            "character_seed": {
                "name": "Sera Ash",
                "role": "rival",
                "social_class": "erased",
                "education_goal": "academy entrance",
                "family_name_status": "erased",
            },
            "population_context": population_context(),
        }
    )

    checks = result.data["constraint_checks"]
    academy_check = next(check for check in checks if check["check_id"] == "academy_access")

    assert academy_check["status"] == "violation"
    assert "sponsor" in academy_check["required_fix"].lower()


def test_constraint_engine_accepts_academy_access_with_scholarship():
    engine = WorldCharacterConstraintEngine()

    result = engine.run(
        {
            "world_state": velmora_world_state(),
            "character_seed": {
                "name": "Sera Ash",
                "role": "rival",
                "social_class": "erased",
                "education_goal": "academy entrance",
                "family_name_status": "erased",
                "scholarship": "dangerous experimental scholarship",
            },
            "population_context": population_context(),
        }
    )

    checks = result.data["constraint_checks"]
    academy_check = next(check for check in checks if check["check_id"] == "academy_access")

    assert academy_check["status"] == "explained_exception"
    assert "blackmail" in academy_check["story_hook"]


def test_constraint_engine_requires_cost_for_rare_skill():
    engine = WorldCharacterConstraintEngine()

    result = engine.run(
        {
            "world_state": velmora_world_state(),
            "character_seed": {
                "name": "Kael Veyran",
                "role": "protagonist",
                "social_class": "academy_sponsored",
                "family_name_status": "distrusted",
                "skill_rarity": "S",
            },
            "population_context": population_context(),
        }
    )

    checks = result.data["constraint_checks"]
    skill_check = next(check for check in checks if check["check_id"] == "rare_skill_cost")

    assert skill_check["status"] == "violation"
    assert "cost" in skill_check["required_fix"].lower()


def test_constraint_engine_accepts_rare_skill_with_limitations():
    engine = WorldCharacterConstraintEngine()

    result = engine.run(
        {
            "world_state": velmora_world_state(),
            "character_seed": {
                "name": "Kael Veyran",
                "role": "protagonist",
                "social_class": "academy_sponsored",
                "family_name_status": "distrusted",
                "skill_rarity": "S",
                "skill_cost": "emotional exhaustion",
                "limitation": "fails when personally attached",
            },
            "population_context": population_context(),
        }
    )

    checks = result.data["constraint_checks"]
    skill_check = next(check for check in checks if check["check_id"] == "rare_skill_cost")

    assert skill_check["status"] == "pass"


def test_constraint_engine_requires_limit_break_condition_cost_risk_consequence():
    engine = WorldCharacterConstraintEngine()

    result = engine.run(
        {
            "world_state": velmora_world_state(),
            "character_seed": {
                "name": "Anomaly Student",
                "role": "protagonist",
                "social_class": "academy_sponsored",
                "family_name_status": "trusted",
                "adaptability_type": "limit_break_anomaly",
                "breakthrough_condition": "protects someone weaker",
                "adaptation_cost": "burns safe anonymity",
            },
            "people_type": {
                "people_type_id": "ptype_limit_break_anomaly",
            },
            "population_context": population_context(),
        }
    )

    checks = result.data["constraint_checks"]
    adapt_check = next(check for check in checks if check["check_id"] == "adaptability_exception")

    assert adapt_check["status"] == "violation"
    assert "adaptation_risk" in adapt_check["explanation"]
    assert "post_break_consequence" in adapt_check["explanation"]


def test_constraint_engine_accepts_complete_limit_break_exception():
    engine = WorldCharacterConstraintEngine()

    result = engine.run(
        {
            "world_state": velmora_world_state(),
            "character_seed": {
                "name": "Anomaly Student",
                "role": "protagonist",
                "social_class": "academy_sponsored",
                "family_name_status": "trusted",
                "adaptability_type": "limit_break_anomaly",
                "breakthrough_condition": "protects someone weaker",
                "adaptation_cost": "burns safe anonymity",
                "adaptation_risk": "emotional collapse",
                "post_break_consequence": "becomes visible to oath courts",
            },
            "people_type": {
                "people_type_id": "ptype_limit_break_anomaly",
            },
            "population_context": population_context(),
        }
    )

    checks = result.data["constraint_checks"]
    adapt_check = next(check for check in checks if check["check_id"] == "adaptability_exception")

    assert adapt_check["status"] == "pass"
    assert "controlled exception" in adapt_check["story_hook"]


def test_constraint_engine_grounding_profile_collects_world_dependency_tags():
    engine = WorldCharacterConstraintEngine()

    result = engine.run(
        {
            "world_state": velmora_world_state(),
            "character_seed": {
                "name": "Kael Veyran",
                "role": "protagonist",
                "social_class": "academy_sponsored",
                "family_name_status": "distrusted",
                "destiny_type": "hidden_kingmaker",
            },
            "people_type": {
                "people_type_id": "ptype_hidden_kingmaker",
            },
            "population_context": population_context(),
        }
    )

    profile = result.data["grounding_profile"]

    assert "magic_access_law" in profile["world_dependency_tags"]
    assert "family_name_legal_trust" in profile["world_dependency_tags"]
    assert "academy_gatekeeping" in profile["world_dependency_tags"]
    assert "relic_economy" in profile["world_dependency_tags"]
    assert "oath_religion" in profile["world_dependency_tags"]
    assert "destiny_pressure" in profile["world_dependency_tags"]


def test_constraint_engine_warns_when_inputs_missing():
    engine = WorldCharacterConstraintEngine()

    result = engine.run({})

    assert result.success is True
    assert len(result.warnings) == 2
    assert "world_state" in result.warnings[0]
    assert "character_seed" in result.warnings[1]

from backend.app.engines.character.skill_power_engine import SkillPowerEngine
from backend.app.schemas.foundation import EngineRunResult


def sample_seed():
    return {
        "character_id": "char_kael",
        "name": "Kael Veyran",
        "role": "protagonist",
        "social_class": "academy_sponsored",
        "family_name_status": "distrusted",
        "primary_skill": "Pattern Reading",
        "skill_domain": "cognitive",
        "skill_rank": "S",
        "skill_rarity": "rare",
        "skill_cost": "emotional exhaustion",
        "limitation": "fails when personally attached",
        "destiny_type": "hidden_kingmaker",
        "adaptability_type": "earned_breakthrough",
        "breakthrough_condition": "protects someone weaker from public punishment",
        "adaptation_cost": "burns safe anonymity",
    }


def sample_goal():
    return {
        "character_id": "char_kael",
        "hidden_goal": "find proof that the ranking system is edited",
        "true_need": "belonging is not the same as permission",
    }


def sample_moral():
    return {
        "character_id": "char_kael",
        "corruption_risk": 0.43,
        "moral_flexibility": 0.57,
        "forbidden_lines": [
            "will not knowingly sacrifice someone powerless for personal advancement",
            "will not ignore someone weaker being publicly harmed",
        ],
    }


def sample_dilemma():
    return {
        "dilemmas": [
            {"dilemma_id": "truth_vs_safety"},
            {"dilemma_id": "power_vs_restraint"},
        ]
    }


def sample_world_grounding():
    return {
        "world_dependency_tags": [
            "academy_gatekeeping",
            "family_name_legal_trust",
            "magic_access_law",
        ]
    }


def sample_world_constraints():
    return {
        "commoner_royal_magic_restricted": True,
    }


def test_skill_engine_returns_engine_result():
    engine = SkillPowerEngine()

    result = engine.run(
        {
            "character_seed": sample_seed(),
            "goal_profile": sample_goal(),
            "moral_profile": sample_moral(),
            "dilemma_matrix": sample_dilemma(),
            "world_grounding": sample_world_grounding(),
            "world_constraints": sample_world_constraints(),
        }
    )

    assert isinstance(result, EngineRunResult)
    assert result.success is True
    assert result.engine_name == "character.skill_power_engine"
    assert "skill_profile" in result.data
    assert "power_limits" in result.data
    assert "training_path" in result.data
    assert "counterplay_matrix" in result.data
    assert "ability_diagnostics" in result.data
    assert "next_engine_payload" in result.data


def test_skill_engine_builds_skill_profile():
    engine = SkillPowerEngine()

    result = engine.run(
        {
            "character_seed": sample_seed(),
            "goal_profile": sample_goal(),
            "moral_profile": sample_moral(),
            "world_grounding": sample_world_grounding(),
            "world_constraints": sample_world_constraints(),
        }
    )

    profile = result.data["skill_profile"]

    assert profile["character_id"] == "char_kael"
    assert profile["skill_profile_id"].startswith("skill_")
    assert profile["primary_skill"] == "Pattern Reading"
    assert profile["skill_domain"] == "cognitive"
    assert profile["skill_rank"] == "S"
    assert profile["skill_rarity"] == "rare"
    assert profile["mastery_score"] > 0.6
    assert profile["raw_potential_score"] > profile["mastery_score"]
    assert profile["growth_ceiling"] >= 0.8
    assert "hidden systems" in profile["narrative_function"]


def test_skill_engine_adds_costs_limits_and_cannot_do_rules():
    engine = SkillPowerEngine()

    result = engine.run(
        {
            "character_seed": sample_seed(),
            "goal_profile": sample_goal(),
            "moral_profile": sample_moral(),
            "world_grounding": sample_world_grounding(),
        }
    )

    limits = result.data["power_limits"]

    assert "emotional exhaustion" in limits["costs"]
    assert "burns safe anonymity" in limits["costs"]
    assert "decision fatigue and social isolation" in limits["costs"]
    assert "fails when personally attached" in limits["limitations"]
    assert "cannot solve every conflict without cost" in limits["cannot_do"]
    assert "cannot read completely hidden information without evidence" in limits["cannot_do"]


def test_skill_engine_builds_training_path_with_required_failures():
    engine = SkillPowerEngine()

    result = engine.run(
        {
            "character_seed": sample_seed(),
            "goal_profile": sample_goal(),
            "moral_profile": sample_moral(),
        }
    )

    path = result.data["training_path"]
    stages = {stage["stage"] for stage in path["training_stages"]}

    assert "recognition" in stages
    assert "control" in stages
    assert "counterplay" in stages
    assert "ethical_use" in stages
    assert "integrated_mastery" in stages
    assert path["mentor_needed"] is True
    assert len(path["required_failures"]) >= 4
    assert "belonging is not the same as permission" in path["mastery_gate"]


def test_skill_engine_builds_counterplay_matrix_from_domain():
    engine = SkillPowerEngine()

    result = engine.run(
        {
            "character_seed": sample_seed(),
            "goal_profile": sample_goal(),
            "moral_profile": sample_moral(),
            "dilemma_matrix": sample_dilemma(),
        }
    )

    matrix = result.data["counterplay_matrix"]

    assert "feed false patterns" in matrix["direct_counters"]
    assert "force emotional attachment into the read" in matrix["direct_counters"]
    assert "moral dilemma delays use" in matrix["soft_counters"]
    assert matrix["enemy_learning_risk"] >= 0.5
    assert "truth_vs_safety" in matrix["dilemma_links"]
    assert matrix["counter_training_needed"] is True


def test_skill_engine_adaptive_anomaly_has_breakthrough_limits():
    engine = SkillPowerEngine()

    result = engine.run(
        {
            "character_seed": {
                "character_id": "char_ilyen",
                "name": "Ilyen Var",
                "role": "protagonist",
                "primary_skill": "Pressure Adaptation",
                "skill_domain": "adaptive",
                "skill_rank": "SS",
                "skill_rarity": "anomaly",
                "adaptability_type": "limit_break_anomaly",
                "breakthrough_condition": "someone weaker will be erased unless they exceed a limit",
                "adaptation_cost": "identity instability after breakthrough",
            },
            "moral_profile": sample_moral(),
        }
    )

    profile = result.data["skill_profile"]
    limits = result.data["power_limits"]
    path = result.data["training_path"]
    matrix = result.data["counterplay_matrix"]

    assert profile["skill_domain"] == "adaptive"
    assert profile["skill_rarity"] == "anomaly"
    assert profile["world_legality"] == "unclassified_by_current_law"
    assert "cannot repeat breakthrough safely without recovery" in limits["limitations"]
    assert "post_break_recovery" in {stage["stage"] for stage in path["training_stages"]}
    assert "attack recovery window" in matrix["direct_counters"]


def test_skill_engine_villain_institutional_power_is_regulated():
    engine = SkillPowerEngine()

    result = engine.run(
        {
            "character_seed": {
                "character_id": "char_oren",
                "name": "Magister Oren Vaul",
                "role": "villain",
                "social_class": "old_nobility",
            },
            "goal_profile": {
                "character_id": "char_oren",
                "true_need": "order without mercy is cowardice",
            },
            "moral_profile": {
                "character_id": "char_oren",
                "corruption_risk": 0.72,
                "moral_flexibility": 0.3,
                "forbidden_lines": ["will not admit the system itself may be immoral until forced"],
            },
        }
    )

    profile = result.data["skill_profile"]
    limits = result.data["power_limits"]
    matrix = result.data["counterplay_matrix"]

    assert profile["primary_skill"] == "Legal Weaponization"
    assert profile["skill_domain"] == "institutional"
    assert profile["world_legality"] == "regulated"
    assert "turns law into weapon instead of protection" in limits["misuse_risks"]
    assert "move conflict outside jurisdiction" in matrix["direct_counters"]


def test_skill_engine_diagnostics_confirm_balanced_ability():
    engine = SkillPowerEngine()

    result = engine.run(
        {
            "character_seed": sample_seed(),
            "goal_profile": sample_goal(),
            "moral_profile": sample_moral(),
            "dilemma_matrix": sample_dilemma(),
            "world_grounding": sample_world_grounding(),
        }
    )

    diagnostics = result.data["ability_diagnostics"]

    assert diagnostics["ability_completeness_score"] >= 0.9
    assert diagnostics["has_cost"] is True
    assert diagnostics["has_limitations"] is True
    assert diagnostics["has_counterplay"] is True
    assert diagnostics["has_training_path"] is True
    assert diagnostics["has_misuse_risk"] is True
    assert diagnostics["has_cannot_do_rules"] is True
    assert diagnostics["is_balanced"] is True
    assert diagnostics["conflict_ready"] is True
    assert diagnostics["adaptability_ready"] is True


def test_skill_engine_builds_next_engine_payloads():
    engine = SkillPowerEngine()

    result = engine.run(
        {
            "character_seed": sample_seed(),
            "goal_profile": sample_goal(),
            "moral_profile": sample_moral(),
            "dilemma_matrix": sample_dilemma(),
            "world_grounding": sample_world_grounding(),
        }
    )

    payload = result.data["next_engine_payload"]

    assert "character_seed" in payload
    assert "adaptability_engine_payload" in payload
    assert "destiny_engine_payload" in payload
    assert "relationship_readiness_payload" in payload
    assert "conflict_simulation_payload_later" in payload
    assert payload["character_seed"]["skill_profile"]["character_id"] == "char_kael"


def test_skill_engine_warns_without_character_seed():
    engine = SkillPowerEngine()

    result = engine.run({})

    assert result.success is True
    assert len(result.warnings) == 1
    assert "character_seed" in result.warnings[0]
    assert result.data["skill_profile"]["character_id"].startswith("char_")

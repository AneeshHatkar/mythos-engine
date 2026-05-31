from backend.app.engines.character.moral_compass_engine import MoralCompassEngine
from backend.app.schemas.foundation import EngineRunResult


def sample_seed():
    return {
        "character_id": "char_kael",
        "name": "Kael Veyran",
        "role": "protagonist",
        "social_class": "academy_sponsored",
        "family_name_status": "distrusted",
        "skill_rarity": "S",
        "destiny_type": "hidden_kingmaker",
        "adaptability_type": "earned_breakthrough",
        "breakthrough_condition": "protects someone weaker from public punishment",
        "adaptation_cost": "burns safe anonymity",
    }


def sample_psychology():
    return {
        "character_id": "char_kael",
        "core_wound": "believes belonging can be revoked at any public failure",
        "core_fear": "belonging being revoked after one visible failure",
        "core_lie": "worth can be revoked by public failure",
        "core_truth": "belonging is not the same as permission",
        "healing_condition": "someone learns the family truth and protects them without using it",
        "corruption_condition": "sacrifices another person to escape family pressure",
        "shame_trigger": "being treated as useful but replaceable",
    }


def sample_goal():
    return {
        "character_id": "char_kael",
        "surface_goal": "understand why destiny has marked them",
        "hidden_goal": "find proof that the ranking system is edited",
        "false_need": "worth can be revoked by public failure",
        "true_need": "belonging is not the same as permission",
        "agency_score": 0.72,
    }


def sample_reputation():
    return {
        "character_id": "char_kael",
        "institutional_reputation": 0.28,
        "exposure_risk": 0.72,
        "enemy_threat_reputation": 0.58,
    }


def test_moral_engine_returns_engine_result():
    engine = MoralCompassEngine()

    result = engine.run(
        {
            "character_seed": sample_seed(),
            "psychology_profile": sample_psychology(),
            "goal_profile": sample_goal(),
            "reputation_profile": sample_reputation(),
        }
    )

    assert isinstance(result, EngineRunResult)
    assert result.success is True
    assert result.engine_name == "character.moral_compass_engine"
    assert "moral_profile" in result.data
    assert "dilemma_matrix" in result.data
    assert "moral_arc" in result.data
    assert "relationship_ethics" in result.data
    assert "moral_diagnostics" in result.data
    assert "next_engine_payload" in result.data


def test_moral_engine_builds_moral_profile():
    engine = MoralCompassEngine()

    result = engine.run(
        {
            "character_seed": sample_seed(),
            "psychology_profile": sample_psychology(),
            "goal_profile": sample_goal(),
            "reputation_profile": sample_reputation(),
        }
    )

    profile = result.data["moral_profile"]

    assert profile["character_id"] == "char_kael"
    assert profile["moral_profile_id"].startswith("moral_")
    assert profile["dominant_moral_value"] in profile["moral_values"]
    assert profile["moral_values"]["justice"] >= 0.7
    assert profile["moral_values"]["truth"] >= 0.7
    assert len(profile["forbidden_lines"]) >= 2
    assert len(profile["conditional_exceptions"]) >= 2
    assert profile["corruption_risk"] >= 0.4
    assert profile["redemption_potential"] >= 0.5


def test_moral_engine_includes_limit_break_exception_with_cost():
    engine = MoralCompassEngine()

    result = engine.run(
        {
            "character_seed": sample_seed(),
            "psychology_profile": sample_psychology(),
            "goal_profile": sample_goal(),
            "reputation_profile": sample_reputation(),
        }
    )

    exceptions = result.data["moral_profile"]["conditional_exceptions"]
    text = " ".join(item["condition"] + " " + item["exception"] + " " + item["required_cost"] for item in exceptions)

    assert "protects someone weaker" in text
    assert "burns safe anonymity" in text


def test_moral_engine_builds_dilemma_matrix():
    engine = MoralCompassEngine()

    result = engine.run(
        {
            "character_seed": sample_seed(),
            "psychology_profile": sample_psychology(),
            "goal_profile": sample_goal(),
            "reputation_profile": sample_reputation(),
        }
    )

    matrix = result.data["dilemma_matrix"]
    dilemma_ids = {item["dilemma_id"] for item in matrix["dilemmas"]}

    assert "truth_vs_safety" in dilemma_ids
    assert "mercy_vs_order" in dilemma_ids
    assert "loyalty_vs_true_need" in dilemma_ids
    assert "power_vs_restraint" in dilemma_ids
    assert matrix["highest_risk_dilemma"] in dilemma_ids
    assert matrix["dilemma_simulation_ready"] is True


def test_moral_engine_builds_moral_arc_with_climax_and_resolution():
    engine = MoralCompassEngine()

    result = engine.run(
        {
            "character_seed": sample_seed(),
            "psychology_profile": sample_psychology(),
            "goal_profile": sample_goal(),
            "reputation_profile": sample_reputation(),
        }
    )

    arc = result.data["moral_arc"]

    assert arc["moral_arc_id"].startswith("marc_")
    assert arc["arc_type"] in {"temptation_to_integrity", "wound_to_chosen_ethics"}
    assert "protects someone weaker" in arc["moral_climax"]
    assert "belonging is not the same as permission" in arc["moral_resolution"]
    assert len(arc["corruption_path"]) >= 4
    assert len(arc["redemption_path"]) >= 4


def test_moral_engine_relationship_ethics_are_chunk4_ready():
    engine = MoralCompassEngine()

    result = engine.run(
        {
            "character_seed": sample_seed(),
            "psychology_profile": sample_psychology(),
            "goal_profile": sample_goal(),
            "reputation_profile": sample_reputation(),
        }
    )

    ethics = result.data["relationship_ethics"]

    assert "friendship_ethic" in ethics
    assert "romance_ethic" in ethics
    assert "rivalry_ethic" in ethics
    assert "enemy_ethic" in ethics
    assert "betrayal_boundary" in ethics
    assert "relationship_simulation_notes" in ethics


def test_moral_engine_villain_has_order_corruption_logic():
    engine = MoralCompassEngine()

    result = engine.run(
        {
            "character_seed": {
                "character_id": "char_oren",
                "name": "Magister Oren Vaul",
                "role": "villain",
                "social_class": "old_nobility",
            },
            "psychology_profile": {
                "character_id": "char_oren",
                "core_lie": "order matters more than innocent exceptions",
                "core_truth": "order without mercy is cowardice",
                "corruption_condition": "chooses order over innocent exceptions",
            },
            "goal_profile": {
                "character_id": "char_oren",
                "true_need": "order without mercy is cowardice",
                "agency_score": 0.8,
            },
        }
    )

    profile = result.data["moral_profile"]
    arc = result.data["moral_arc"]

    assert profile["moral_values"]["order"] >= 0.7
    assert profile["corruption_risk"] >= 0.6
    assert "confuses order with goodness" in profile["moral_blind_spots"]
    assert arc["arc_type"] == "order_to_accountability_or_collapse"
    assert "innocent sacrifice" in arc["moral_climax"]


def test_moral_engine_diagnostics_confirm_simulation_ready():
    engine = MoralCompassEngine()

    result = engine.run(
        {
            "character_seed": sample_seed(),
            "psychology_profile": sample_psychology(),
            "goal_profile": sample_goal(),
            "reputation_profile": sample_reputation(),
        }
    )

    diagnostics = result.data["moral_diagnostics"]

    assert diagnostics["moral_completeness_score"] >= 0.9
    assert diagnostics["has_forbidden_lines"] is True
    assert diagnostics["has_conditional_exceptions"] is True
    assert diagnostics["has_dilemma_matrix"] is True
    assert diagnostics["has_corruption_path"] is True
    assert diagnostics["has_redemption_path"] is True
    assert diagnostics["has_relationship_ethics"] is True
    assert diagnostics["moral_simulation_ready"] is True
    assert diagnostics["plot_ready"] is True


def test_moral_engine_builds_next_engine_payloads():
    engine = MoralCompassEngine()

    result = engine.run(
        {
            "character_seed": sample_seed(),
            "psychology_profile": sample_psychology(),
            "goal_profile": sample_goal(),
            "reputation_profile": sample_reputation(),
        }
    )

    payload = result.data["next_engine_payload"]

    assert "character_seed" in payload
    assert "skill_engine_payload" in payload
    assert "adaptability_engine_payload" in payload
    assert "destiny_engine_payload" in payload
    assert "relationship_simulation_payload_later" in payload
    assert "plot_engine_payload_later" in payload
    assert payload["character_seed"]["moral_profile"]["character_id"] == "char_kael"


def test_moral_engine_warns_without_character_seed():
    engine = MoralCompassEngine()

    result = engine.run({})

    assert result.success is True
    assert len(result.warnings) == 1
    assert "character_seed" in result.warnings[0]
    assert result.data["moral_profile"]["character_id"].startswith("char_")

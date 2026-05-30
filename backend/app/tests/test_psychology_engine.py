from backend.app.engines.character.psychology_engine import PsychologyEngine
from backend.app.schemas.character import PsychologyProfile
from backend.app.schemas.foundation import EngineRunResult


def sample_seed():
    return {
        "character_id": "char_kael",
        "name": "Kael Veyran",
        "role": "protagonist",
        "social_class": "academy_sponsored",
        "hidden_goal": "find proof that the ranking system is edited",
        "skill_rarity": "rare",
        "skill_cost": "emotional exhaustion",
        "destiny_type": "hidden_kingmaker",
        "destiny_burden": "must decide who receives power",
        "adaptability_type": "earned_breakthrough",
        "breakthrough_condition": "protects someone weaker from public punishment",
        "adaptation_cost": "burns safe anonymity",
    }


def sample_origin():
    return {
        "character_id": "char_kael",
        "social_class": "academy_sponsored",
        "class_wound": "believes belonging can be revoked at any public failure",
        "public_assumptions": ["useful but replaceable", "must prove merit repeatedly"],
    }


def sample_family():
    return {
        "character_id": "char_kael",
        "family_status": "conditionally_recognized",
        "family_secrets": ["sponsor support is tied to an undisclosed obligation"],
        "family_debt": ["sponsor debt tied to academy access"],
        "inherited_obligations": ["repay sponsor investment", "avoid public embarrassment"],
        "inherited_trauma": ["fear of public failure causing family disgrace"],
    }


def sample_family_pressure():
    return {
        "pressure_tier": "high_family_pressure",
        "main_pressure_sources": [
            "sponsor debt tied to academy access",
            "sponsor support is tied to an undisclosed obligation",
        ],
    }


def test_psychology_engine_returns_engine_result():
    engine = PsychologyEngine()

    result = engine.run(
        {
            "character_seed": sample_seed(),
            "origin_profile": sample_origin(),
            "family_profile": sample_family(),
            "family_pressure": sample_family_pressure(),
        }
    )

    assert isinstance(result, EngineRunResult)
    assert result.success is True
    assert result.engine_name == "character.psychology_engine"
    assert "psychology_profile" in result.data
    assert "psychology_diagnostics" in result.data
    assert "interaction_readiness" in result.data
    assert "next_engine_payload" in result.data


def test_psychology_engine_generates_valid_profile():
    engine = PsychologyEngine()

    result = engine.run(
        {
            "character_seed": sample_seed(),
            "origin_profile": sample_origin(),
            "family_profile": sample_family(),
            "family_pressure": sample_family_pressure(),
        }
    )

    profile = PsychologyProfile.model_validate(result.data["psychology_profile"])

    assert profile.character_id == "char_kael"
    assert profile.core_wound == "believes belonging can be revoked at any public failure"
    assert profile.core_desire == "find proof that the ranking system is edited"
    assert profile.core_fear == "belonging being revoked after one visible failure"
    assert profile.defense_mechanism == "controlled self-erasure"
    assert profile.attachment_tendency == "slow trust with secrecy tests"
    assert profile.healing_condition == "someone learns the family truth and protects them without using it"
    assert len(profile.behavior_rules) >= 3


def test_psychology_engine_links_family_secrets_to_relationship_behavior():
    engine = PsychologyEngine()

    result = engine.run(
        {
            "character_seed": sample_seed(),
            "origin_profile": sample_origin(),
            "family_profile": sample_family(),
            "family_pressure": sample_family_pressure(),
        }
    )

    profile = result.data["psychology_profile"]
    readiness = result.data["interaction_readiness"]

    assert "intimacy" in profile["love_response"].lower()
    assert "family secrets" in profile["betrayal_response"].lower()
    assert readiness["chunk4_relationship_simulation_ready"] is True
    assert readiness["romance_response_ready"] is True
    assert readiness["betrayal_response_ready"] is True


def test_psychology_engine_creates_corruption_and_healing_paths():
    engine = PsychologyEngine()

    result = engine.run(
        {
            "character_seed": sample_seed(),
            "origin_profile": sample_origin(),
            "family_profile": sample_family(),
            "family_pressure": sample_family_pressure(),
        }
    )

    profile = result.data["psychology_profile"]

    assert profile["healing_condition"] is not None
    assert profile["corruption_condition"] is not None
    assert "sacrifices another person" in profile["corruption_condition"]


def test_psychology_engine_elite_character_has_reputation_based_wound_logic():
    engine = PsychologyEngine()

    result = engine.run(
        {
            "character_seed": {
                "character_id": "char_mira",
                "name": "Mira Vaul",
                "social_class": "old_nobility",
            },
            "origin_profile": {
                "character_id": "char_mira",
                "social_class": "old_nobility",
                "public_assumptions": ["competent by birth"],
            },
            "family_profile": {
                "character_id": "char_mira",
                "family_status": "publicly_established",
                "family_secrets": ["family prestige depends on an edited historical account"],
                "inherited_obligations": ["protect family reputation"],
            },
        }
    )

    profile = result.data["psychology_profile"]

    assert profile["core_fear"] == "becoming a disgrace to the family name"
    assert profile["core_lie"] == "love must be earned by preserving reputation"
    assert profile["core_truth"] == "a name is not worth more than the people harmed to preserve it"
    assert "etiquette" in profile["stress_response"]


def test_psychology_engine_erased_character_has_legal_erasure_fear():
    engine = PsychologyEngine()

    result = engine.run(
        {
            "character_seed": {
                "character_id": "char_sera",
                "name": "Sera Ash",
                "social_class": "erased",
            },
            "origin_profile": {
                "character_id": "char_sera",
                "social_class": "erased",
                "class_wound": "believes visibility invites legal erasure",
            },
            "family_profile": {
                "character_id": "char_sera",
                "family_status": "erased_or_unverified",
                "family_secrets": ["family records were deliberately removed from public trust archives"],
            },
        }
    )

    profile = result.data["psychology_profile"]

    assert profile["core_wound"] == "believes visibility invites legal erasure"
    assert profile["core_fear"] == "being exposed and erased by legal authority"
    assert profile["core_lie"] == "truth only matters when powerful people recognize it"
    assert "exits" in profile["stress_response"]


def test_psychology_engine_diagnostics_scores_depth():
    engine = PsychologyEngine()

    result = engine.run(
        {
            "character_seed": sample_seed(),
            "origin_profile": sample_origin(),
            "family_profile": sample_family(),
            "family_pressure": sample_family_pressure(),
        }
    )

    diagnostics = result.data["psychology_diagnostics"]

    assert diagnostics["psychological_depth_score"] >= 0.8
    assert diagnostics["behavior_rule_count"] >= 3
    assert diagnostics["has_origin_link"] is True
    assert diagnostics["has_family_link"] is True
    assert diagnostics["has_healing_and_corruption_paths"] is True
    assert diagnostics["ready_for_emotion_engine"] is True


def test_psychology_engine_flags_missing_costs_for_rare_skill_or_destiny():
    engine = PsychologyEngine()

    result = engine.run(
        {
            "character_seed": {
                "character_id": "char_bad",
                "skill_rarity": "rare",
                "destiny_type": "chosen_heir",
                "adaptability_type": "earned_breakthrough",
            },
            "origin_profile": {
                "character_id": "char_bad",
                "social_class": "academy_sponsored",
            },
            "family_profile": {
                "character_id": "char_bad",
                "family_secrets": ["secret without pressure"],
            },
        }
    )

    notes = " ".join(result.data["psychology_profile"]["contradiction_notes"]).lower()

    assert "rare skill" in notes
    assert "destiny" in notes
    assert "adaptability" in notes


def test_psychology_engine_builds_next_engine_payloads():
    engine = PsychologyEngine()

    result = engine.run(
        {
            "character_seed": sample_seed(),
            "origin_profile": sample_origin(),
            "family_profile": sample_family(),
            "family_pressure": sample_family_pressure(),
            "origin_story_hooks": ["origin hook"],
            "family_story_hooks": ["family hook"],
        }
    )

    payload = result.data["next_engine_payload"]

    assert "character_seed" in payload
    assert "trauma_engine_payload" in payload
    assert "emotion_engine_payload" in payload
    assert "goal_engine_payload" in payload
    assert "adaptability_engine_payload" in payload
    assert payload["character_seed"]["psychology"]["character_id"] == "char_kael"


def test_psychology_engine_warns_without_character_seed():
    engine = PsychologyEngine()

    result = engine.run({})

    assert result.success is True
    assert len(result.warnings) == 1
    assert "character_seed" in result.warnings[0]
    assert result.data["psychology_profile"]["character_id"].startswith("char_")

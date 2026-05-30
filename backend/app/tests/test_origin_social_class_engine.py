from backend.app.engines.character.origin_social_class_engine import OriginSocialClassEngine
from backend.app.schemas.character import OriginProfile
from backend.app.schemas.foundation import EngineRunResult


def sample_constraints():
    return {
        "commoner_royal_magic_restricted": True,
        "family_name_affects_legal_trust": True,
        "noble_academy_gatekeeping": True,
        "relic_economy_pressure": True,
    }


def sample_grounding():
    return {
        "world_dependency_tags": [
            "magic_access_law",
            "family_name_legal_trust",
            "academy_gatekeeping",
            "relic_economy",
        ]
    }


def test_origin_engine_returns_engine_result():
    engine = OriginSocialClassEngine()

    result = engine.run(
        {
            "character_seed": {
                "character_id": "char_kael",
                "social_class": "academy_sponsored",
                "family_name_status": "distrusted",
            },
            "world_constraints": sample_constraints(),
            "world_grounding": sample_grounding(),
        }
    )

    assert isinstance(result, EngineRunResult)
    assert result.success is True
    assert result.engine_name == "character.origin_social_class_engine"
    assert "origin_profile" in result.data
    assert "access_risks" in result.data
    assert "origin_story_hooks" in result.data
    assert "next_engine_payload" in result.data


def test_origin_engine_generates_valid_origin_profile():
    engine = OriginSocialClassEngine()

    result = engine.run(
        {
            "character_seed": {
                "character_id": "char_kael",
                "social_class": "academy_sponsored",
                "family_name_status": "distrusted",
                "scholarship": "conditional sponsor seat",
            },
            "world_constraints": sample_constraints(),
            "world_grounding": sample_grounding(),
        }
    )

    profile = OriginProfile.model_validate(result.data["origin_profile"])

    assert profile.character_id == "char_kael"
    assert profile.birth_status == "common_birth"
    assert profile.social_class == "academy_sponsored"
    assert profile.origin_location == "outer academy district"
    assert profile.family_name_trust == 0.25
    assert profile.education_access > 0.7
    assert "conditional academy access" in profile.institution_access
    assert "elite academy upper halls" in profile.forbidden_access
    assert profile.class_wound is not None


def test_origin_engine_low_class_has_forbidden_access_and_story_hooks():
    engine = OriginSocialClassEngine()

    result = engine.run(
        {
            "character_seed": {
                "character_id": "char_tovin",
                "social_class": "commoner",
                "family_name_status": "recognized",
            },
            "world_constraints": sample_constraints(),
            "world_grounding": sample_grounding(),
        }
    )

    profile = result.data["origin_profile"]
    risks = result.data["access_risks"]
    hooks = " ".join(result.data["origin_story_hooks"]).lower()

    assert "royal magic curriculum" in profile["forbidden_access"]
    assert "elite academy upper halls" in profile["forbidden_access"]
    assert risks["has_story_useful_pressure"] is True
    assert "forbidden access" in hooks or "unofficial" in hooks


def test_origin_engine_erased_character_has_low_trust_and_identity_pressure():
    engine = OriginSocialClassEngine()

    result = engine.run(
        {
            "character_seed": {
                "character_id": "char_sera",
                "social_class": "erased",
                "family_name_status": "erased",
            },
            "world_constraints": sample_constraints(),
            "world_grounding": sample_grounding(),
        }
    )

    profile = result.data["origin_profile"]
    risks = result.data["access_risks"]
    hooks = " ".join(result.data["origin_story_hooks"]).lower()

    assert profile["birth_status"] == "erased_family_record"
    assert profile["family_name_trust"] == 0.05
    assert profile["mobility_score"] <= 0.2
    assert "identity instability" in profile["inherited_disadvantages"]
    assert risks["requires_legal_trust_repair"] is True
    assert "not be believed" in hooks


def test_origin_engine_elite_character_gets_privilege_and_blindness_risk():
    engine = OriginSocialClassEngine()

    result = engine.run(
        {
            "character_seed": {
                "character_id": "char_mira",
                "social_class": "old_nobility",
                "family_name_status": "trusted",
            },
            "world_constraints": sample_constraints(),
            "world_grounding": sample_grounding(),
        }
    )

    profile = result.data["origin_profile"]
    risks = result.data["access_risks"]
    hooks = " ".join(result.data["origin_story_hooks"]).lower()

    assert profile["birth_status"] == "noble_birth"
    assert profile["family_name_trust"] == 0.9
    assert profile["wealth_rank"] == 0.9
    assert "restricted archives" in profile["institution_access"]
    assert "legal credibility" in profile["inherited_privileges"]
    assert "privilege blindness risk" in risks["risks"]
    assert "status protects" in hooks


def test_origin_engine_relic_miner_connects_to_relic_labor_pressure():
    engine = OriginSocialClassEngine()

    result = engine.run(
        {
            "character_seed": {
                "character_id": "char_relic",
                "social_class": "relic_miner",
                "family_name_status": "distrusted",
            },
            "world_constraints": sample_constraints(),
            "world_grounding": sample_grounding(),
        }
    )

    profile = result.data["origin_profile"]

    assert profile["origin_location"] == "relic-mining city"
    assert "relic labor knowledge" in profile["resource_access"]
    assert "relic labor injury exposure" in profile["inherited_disadvantages"]
    assert "poor bodies" in profile["class_wound"]


def test_origin_engine_includes_adaptability_hook_from_genesis_seed():
    engine = OriginSocialClassEngine()

    result = engine.run(
        {
            "character_seed": {
                "character_id": "char_kael",
                "social_class": "academy_sponsored",
                "family_name_status": "distrusted",
                "breakthrough_condition": "protects someone weaker from public punishment",
            },
            "world_constraints": sample_constraints(),
            "world_grounding": sample_grounding(),
        }
    )

    hooks = " ".join(result.data["origin_story_hooks"]).lower()

    assert "trigger adaptability" in hooks
    assert "protects someone weaker" in hooks


def test_origin_engine_builds_next_engine_payloads():
    engine = OriginSocialClassEngine()

    result = engine.run(
        {
            "character_seed": {
                "character_id": "char_kael",
                "social_class": "academy_sponsored",
                "family_name_status": "distrusted",
            },
            "world_constraints": sample_constraints(),
            "world_grounding": sample_grounding(),
        }
    )

    payload = result.data["next_engine_payload"]

    assert "character_seed" in payload
    assert "family_engine_payload" in payload
    assert "psychology_engine_payload" in payload
    assert payload["character_seed"]["origin"]["character_id"] == "char_kael"
    assert payload["psychology_engine_payload"]["class_wound"] is not None


def test_origin_engine_warns_without_character_seed():
    engine = OriginSocialClassEngine()

    result = engine.run({})

    assert result.success is True
    assert len(result.warnings) == 1
    assert "character_seed" in result.warnings[0]
    assert result.data["origin_profile"]["social_class"] == "commoner"

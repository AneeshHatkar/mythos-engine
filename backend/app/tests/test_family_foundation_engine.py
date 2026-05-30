from backend.app.engines.character.family_foundation_engine import FamilyFoundationEngine
from backend.app.schemas.character import FamilyProfile
from backend.app.schemas.foundation import EngineRunResult


def sample_constraints():
    return {
        "family_name_affects_legal_trust": True,
        "noble_academy_gatekeeping": True,
    }


def sample_grounding():
    return {
        "world_dependency_tags": [
            "family_name_legal_trust",
            "academy_gatekeeping",
            "oath_religion",
        ]
    }


def test_family_engine_returns_engine_result():
    engine = FamilyFoundationEngine()

    result = engine.run(
        {
            "character_seed": {
                "character_id": "char_kael",
                "name": "Kael Veyran",
                "social_class": "academy_sponsored",
                "family_name_status": "distrusted",
            },
            "world_constraints": sample_constraints(),
            "world_grounding": sample_grounding(),
        }
    )

    assert isinstance(result, EngineRunResult)
    assert result.success is True
    assert result.engine_name == "character.family_foundation_engine"
    assert "family_profile" in result.data
    assert "family_graph" in result.data
    assert "family_pressure" in result.data
    assert "family_story_hooks" in result.data
    assert "next_engine_payload" in result.data


def test_family_engine_generates_valid_profile_for_academy_sponsored_character():
    engine = FamilyFoundationEngine()

    result = engine.run(
        {
            "character_seed": {
                "character_id": "char_kael",
                "name": "Kael Veyran",
                "social_class": "academy_sponsored",
                "family_name_status": "distrusted",
            },
            "origin_profile": {
                "character_id": "char_kael",
                "social_class": "academy_sponsored",
                "family_name_trust": 0.25,
                "forbidden_access": ["elite academy upper halls"],
            },
            "world_constraints": sample_constraints(),
            "world_grounding": sample_grounding(),
        }
    )

    profile = FamilyProfile.model_validate(result.data["family_profile"])

    assert profile.character_id == "char_kael"
    assert profile.family_name == "Veyran"
    assert profile.family_status == "conditionally_recognized"
    assert "sponsor debt tied to academy access" in profile.family_debt
    assert "sponsor support is tied to an undisclosed obligation" in profile.family_secrets
    assert "conditional academic pathway" in profile.inherited_privilege
    assert len(profile.guardians) >= 1
    assert profile.guardians[0].relation == "academic sponsor"


def test_family_engine_erased_family_creates_records_secret_and_low_trust_pressure():
    engine = FamilyFoundationEngine()

    result = engine.run(
        {
            "character_seed": {
                "character_id": "char_sera",
                "name": "Sera Ash",
                "social_class": "erased",
                "family_name_status": "erased",
            },
            "origin_profile": {
                "character_id": "char_sera",
                "social_class": "erased",
                "family_name_trust": 0.05,
            },
            "world_constraints": sample_constraints(),
            "world_grounding": sample_grounding(),
        }
    )

    profile = result.data["family_profile"]
    pressure = result.data["family_pressure"]
    hooks = " ".join(result.data["family_story_hooks"]).lower()

    assert profile["family_status"] == "erased_or_unverified"
    assert "family records were deliberately removed from public trust archives" in profile["family_secrets"]
    assert "identity insecurity passed through silence" in profile["inherited_trauma"]
    assert pressure["family_pressure_score"] >= 0.5
    assert "secret" in hooks
    assert "identity" in hooks


def test_family_engine_elite_family_creates_privilege_obligation_and_rival_sibling():
    engine = FamilyFoundationEngine()

    result = engine.run(
        {
            "character_seed": {
                "character_id": "char_mira",
                "name": "Mira Vaul",
                "social_class": "old_nobility",
                "family_name_status": "trusted",
            },
            "world_constraints": sample_constraints(),
            "world_grounding": sample_grounding(),
        }
    )

    profile = result.data["family_profile"]
    graph = result.data["family_graph"]
    hooks = " ".join(result.data["family_story_hooks"]).lower()

    assert profile["family_status"] == "publicly_established"
    assert "legal credibility" in profile["inherited_privilege"]
    assert "protect family reputation" in profile["inherited_obligations"]
    assert "family prestige depends on an edited historical account" in profile["family_secrets"]
    assert graph["highest_conflict_relation"] in {"father", "sibling"}
    assert "secret" in hooks


def test_family_engine_relic_miner_family_creates_labor_debt_and_artifact():
    engine = FamilyFoundationEngine()

    result = engine.run(
        {
            "character_seed": {
                "character_id": "char_ren",
                "name": "Ren Ash",
                "social_class": "relic_miner",
                "family_name_status": "distrusted",
            },
            "world_constraints": sample_constraints(),
            "world_grounding": sample_grounding(),
        }
    )

    profile = result.data["family_profile"]
    pressure = result.data["family_pressure"]

    assert "relic labor debt" in profile["family_debt"]
    assert "normalization of bodily sacrifice for survival" in profile["inherited_trauma"]
    assert "relic-dusted work token" in profile["family_artifact_links"]
    assert pressure["family_pressure_score"] > 0.0


def test_family_engine_builds_family_graph_nodes():
    engine = FamilyFoundationEngine()

    result = engine.run(
        {
            "character_seed": {
                "character_id": "char_kael",
                "name": "Kael Veyran",
                "social_class": "academy_sponsored",
                "family_name_status": "distrusted",
            },
            "world_constraints": sample_constraints(),
            "world_grounding": sample_grounding(),
        }
    )

    graph = result.data["family_graph"]

    assert graph["character_id"] == "char_kael"
    assert graph["family_name"] == "Veyran"
    assert graph["edge_count"] >= 1
    assert len(graph["nodes"]) >= 1
    assert "highest_conflict_relation" in graph
    assert "closest_relation" in graph


def test_family_engine_family_pressure_affects_relationships_and_plot():
    engine = FamilyFoundationEngine()

    result = engine.run(
        {
            "character_seed": {
                "character_id": "char_kael",
                "name": "Kael Veyran",
                "social_class": "academy_sponsored",
                "family_name_status": "distrusted",
                "breakthrough_condition": "protects someone weaker from public punishment",
            },
            "origin_profile": {
                "character_id": "char_kael",
                "social_class": "academy_sponsored",
                "family_name_trust": 0.25,
                "forbidden_access": ["elite academy upper halls"],
            },
            "world_constraints": sample_constraints(),
            "world_grounding": sample_grounding(),
        }
    )

    pressure = result.data["family_pressure"]
    hooks = " ".join(result.data["family_story_hooks"]).lower()

    assert pressure["pressure_tier"] in {
        "moderate_family_pressure",
        "high_family_pressure",
        "extreme_family_pressure",
    }
    assert len(pressure["relationship_risks"]) > 0
    assert len(pressure["plot_risks"]) > 0
    assert "limit-break" in hooks


def test_family_engine_builds_next_engine_payloads():
    engine = FamilyFoundationEngine()

    result = engine.run(
        {
            "character_seed": {
                "character_id": "char_kael",
                "name": "Kael Veyran",
                "social_class": "academy_sponsored",
                "family_name_status": "distrusted",
            },
            "world_constraints": sample_constraints(),
            "world_grounding": sample_grounding(),
        }
    )

    payload = result.data["next_engine_payload"]

    assert "character_seed" in payload
    assert "psychology_engine_payload" in payload
    assert "trauma_engine_payload" in payload
    assert "legacy_engine_payload" in payload
    assert payload["character_seed"]["family"]["character_id"] == "char_kael"
    assert len(payload["trauma_engine_payload"]["inherited_trauma"]) >= 1


def test_family_engine_warns_without_character_seed():
    engine = FamilyFoundationEngine()

    result = engine.run({})

    assert result.success is True
    assert len(result.warnings) == 1
    assert "character_seed" in result.warnings[0]
    assert result.data["family_profile"]["character_id"].startswith("char_")

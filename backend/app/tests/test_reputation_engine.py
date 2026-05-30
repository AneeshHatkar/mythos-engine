from backend.app.engines.character.reputation_engine import ReputationEngine
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
    }


def sample_origin():
    return {
        "character_id": "char_kael",
        "social_class": "academy_sponsored",
        "family_name_trust": 0.25,
        "education_access": 0.82,
        "forbidden_access": ["elite academy upper halls", "royal magic curriculum"],
    }


def sample_family():
    return {
        "character_id": "char_kael",
        "family_status": "conditionally_recognized",
        "family_secrets": ["sponsor support is tied to an undisclosed obligation"],
        "family_debt": ["sponsor debt tied to academy access"],
        "family_allies": ["lower-rank study circle"],
        "family_enemies": ["legal trust clerks"],
        "inherited_privilege": ["conditional academic pathway"],
    }


def sample_memories():
    return [
        {
            "memory_id": "mem_core",
            "character_id": "char_kael",
            "content": "public failure memory",
            "emotional_weight": 0.82,
            "trigger_terms": ["failure", "replaceable"],
        },
        {
            "memory_id": "mem_limit",
            "character_id": "char_kael",
            "content": "protects someone weaker from public punishment",
            "emotional_weight": 0.79,
            "trigger_terms": ["weaker person", "threshold"],
        },
        {
            "memory_id": "mem_secret",
            "character_id": "char_kael",
            "content": "family secret memory",
            "emotional_weight": 0.74,
            "trigger_terms": ["secret", "record"],
        },
    ]


def sample_memory_network():
    return {
        "character_id": "char_kael",
        "trigger_index": {
            "failure": ["mem_core"],
            "secret": ["mem_secret"],
            "threshold": ["mem_limit"],
        },
    }


def sample_world_grounding():
    return {
        "world_dependency_tags": [
            "family_name_legal_trust",
            "academy_gatekeeping",
            "magic_access_law",
        ]
    }


def sample_world_constraints():
    return {
        "family_name_affects_legal_trust": True,
        "noble_academy_gatekeeping": True,
    }


def test_reputation_engine_returns_engine_result():
    engine = ReputationEngine()

    result = engine.run(
        {
            "character_seed": sample_seed(),
            "origin_profile": sample_origin(),
            "family_profile": sample_family(),
            "memory_records": sample_memories(),
            "memory_network": sample_memory_network(),
            "world_grounding": sample_world_grounding(),
            "world_constraints": sample_world_constraints(),
        }
    )

    assert isinstance(result, EngineRunResult)
    assert result.success is True
    assert result.engine_name == "character.reputation_engine"
    assert "reputation_profile" in result.data
    assert "reputation_dynamics" in result.data
    assert "rumor_network" in result.data
    assert "consequence_hooks" in result.data
    assert "next_engine_payload" in result.data


def test_reputation_engine_builds_audience_specific_reputation():
    engine = ReputationEngine()

    result = engine.run(
        {
            "character_seed": sample_seed(),
            "origin_profile": sample_origin(),
            "family_profile": sample_family(),
            "memory_records": sample_memories(),
            "memory_network": sample_memory_network(),
            "world_grounding": sample_world_grounding(),
            "world_constraints": sample_world_constraints(),
        }
    )

    profile = result.data["reputation_profile"]

    assert profile["character_id"] == "char_kael"
    assert profile["reputation_id"].startswith("rep_")
    assert 0.0 <= profile["public_reputation"] <= 1.0
    assert 0.0 <= profile["institutional_reputation"] <= 1.0
    assert 0.0 <= profile["elite_reputation"] <= 1.0
    assert 0.0 <= profile["commoner_reputation"] <= 1.0
    assert profile["exposure_risk"] >= 0.5
    assert profile["reputation_volatility"] >= 0.4
    assert "conditional merit student" in profile["public_labels"]
    assert "legally questionable name" in profile["public_labels"]


def test_reputation_engine_tracks_assets_and_liabilities():
    engine = ReputationEngine()

    result = engine.run(
        {
            "character_seed": sample_seed(),
            "origin_profile": sample_origin(),
            "family_profile": sample_family(),
            "memory_records": sample_memories(),
            "world_grounding": sample_world_grounding(),
            "world_constraints": sample_world_constraints(),
        }
    )

    profile = result.data["reputation_profile"]

    assert "education access" in profile["reputation_assets"]
    assert "rare skill visibility" in profile["reputation_assets"]
    assert "destiny significance" in profile["reputation_assets"]
    assert "protective public action" in profile["reputation_assets"]

    assert "forbidden access" in profile["reputation_liabilities"]
    assert "family secrets" in profile["reputation_liabilities"]
    assert "family debt" in profile["reputation_liabilities"]
    assert "uncontrolled breakthrough risk" in profile["reputation_liabilities"]


def test_reputation_engine_builds_update_rules():
    engine = ReputationEngine()

    result = engine.run(
        {
            "character_seed": sample_seed(),
            "origin_profile": sample_origin(),
            "family_profile": sample_family(),
            "memory_records": sample_memories(),
            "world_constraints": sample_world_constraints(),
        }
    )

    dynamics = result.data["reputation_dynamics"]
    events = {rule["event"] for rule in dynamics["reputation_update_rules"]}

    assert "public_skill_display" in events
    assert "family_secret_exposed" in events
    assert "protects_powerless_person_publicly" in events
    assert "caught_using_forbidden_access" in events
    assert "trusted_person_defends_character" in events
    assert "institutions" in dynamics["audience_specific_repair_paths"]
    assert "commoners" in dynamics["audience_specific_damage_paths"]


def test_reputation_engine_builds_rumor_network_from_secrets_skills_and_breakthroughs():
    engine = ReputationEngine()

    result = engine.run(
        {
            "character_seed": sample_seed(),
            "origin_profile": sample_origin(),
            "family_profile": sample_family(),
            "memory_records": sample_memories(),
            "memory_network": sample_memory_network(),
            "world_grounding": sample_world_grounding(),
            "world_constraints": sample_world_constraints(),
        }
    )

    rumor_network = result.data["rumor_network"]
    claims = " ".join(rumor["claim"] for rumor in rumor_network["active_rumors"]).lower()

    assert rumor_network["character_id"] == "char_kael"
    assert len(rumor_network["active_rumors"]) >= 3
    assert rumor_network["highest_spread_risk"] >= 0.6
    assert "family name" in claims
    assert "ability" in claims
    assert "cornered" in claims
    assert rumor_network["rumor_simulation_ready"] is True


def test_reputation_engine_creates_consequence_hooks_for_story_and_simulation():
    engine = ReputationEngine()

    result = engine.run(
        {
            "character_seed": sample_seed(),
            "origin_profile": sample_origin(),
            "family_profile": sample_family(),
            "memory_records": sample_memories(),
            "memory_network": sample_memory_network(),
            "world_grounding": sample_world_grounding(),
            "world_constraints": sample_world_constraints(),
        }
    )

    hooks = result.data["consequence_hooks"]
    hook_types = {hook["hook_type"] for hook in hooks}

    assert "exposure_event" in hook_types
    assert "enemy_attention" in hook_types
    assert "rumor_cascade" in hook_types


def test_reputation_engine_elite_character_has_high_elite_and_institutional_reputation():
    engine = ReputationEngine()

    result = engine.run(
        {
            "character_seed": {
                "character_id": "char_mira",
                "name": "Mira Vaul",
                "role": "love_interest",
                "social_class": "old_nobility",
                "family_name_status": "trusted",
            },
            "origin_profile": {
                "character_id": "char_mira",
                "social_class": "old_nobility",
                "family_name_trust": 0.9,
                "education_access": 0.92,
            },
            "family_profile": {
                "character_id": "char_mira",
                "family_status": "publicly_established",
                "inherited_privilege": ["legal credibility"],
            },
            "world_constraints": sample_world_constraints(),
        }
    )

    profile = result.data["reputation_profile"]

    assert profile["institutional_reputation"] >= 0.7
    assert profile["elite_reputation"] >= 0.8
    assert "high-status name" in profile["public_labels"]
    assert "family privilege" in profile["reputation_assets"]


def test_reputation_engine_erased_character_has_low_institutional_reputation():
    engine = ReputationEngine()

    result = engine.run(
        {
            "character_seed": {
                "character_id": "char_sera",
                "name": "Sera Ash",
                "role": "rival",
                "social_class": "erased",
                "family_name_status": "erased",
            },
            "origin_profile": {
                "character_id": "char_sera",
                "social_class": "erased",
                "family_name_trust": 0.05,
            },
            "family_profile": {
                "character_id": "char_sera",
                "family_status": "erased_or_unverified",
                "family_secrets": ["family records were deliberately removed"],
            },
            "world_constraints": sample_world_constraints(),
        }
    )

    profile = result.data["reputation_profile"]

    assert profile["institutional_reputation"] <= 0.2
    assert profile["elite_reputation"] <= 0.25
    assert "low-trust outsider" in profile["public_labels"]
    assert "legally questionable name" in profile["public_labels"]
    assert "family secrets" in profile["reputation_liabilities"]


def test_reputation_engine_builds_next_engine_payloads():
    engine = ReputationEngine()

    result = engine.run(
        {
            "character_seed": sample_seed(),
            "origin_profile": sample_origin(),
            "family_profile": sample_family(),
            "memory_records": sample_memories(),
            "memory_network": sample_memory_network(),
            "world_grounding": sample_world_grounding(),
            "world_constraints": sample_world_constraints(),
        }
    )

    payload = result.data["next_engine_payload"]

    assert "character_seed" in payload
    assert "goal_engine_payload" in payload
    assert "moral_engine_payload" in payload
    assert "relationship_simulation_payload_later" in payload
    assert "plot_engine_payload_later" in payload
    assert payload["character_seed"]["reputation"]["character_id"] == "char_kael"


def test_reputation_engine_warns_without_character_seed():
    engine = ReputationEngine()

    result = engine.run({})

    assert result.success is True
    assert len(result.warnings) == 1
    assert "character_seed" in result.warnings[0]
    assert result.data["reputation_profile"]["character_id"].startswith("char_")

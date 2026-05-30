from backend.app.engines.character.character_genesis_engine import CharacterGenesisEngine
from backend.app.schemas.character import CharacterIdentity
from backend.app.schemas.foundation import EngineRunResult


def sample_world_state():
    return {
        "identity": {"world_id": "world_velmora", "world_name": "Velmora"},
        "rules": {"magic": "commoners cannot legally study royal magic"},
        "belief": {"religion": "oath-gods and oath law"},
        "society": {"hierarchy": "noble academies control power"},
    }


def sample_population_context():
    return {
        "population_groups": [
            {"group_name": "Academy sponsored", "social_class": "academy_sponsored"},
            {"group_name": "Commoners", "social_class": "commoner"},
            {"group_name": "Old nobles", "social_class": "old_nobility"},
        ]
    }


def sample_people_type():
    return {
        "people_type_id": "ptype_hidden_kingmaker",
        "name": "Hidden Kingmaker",
        "compatible_roles": ["protagonist", "mentor", "catalyst"],
        "compatible_classes": ["academy_sponsored", "commoner", "erased"],
        "compatible_destinies": ["hidden_kingmaker", "crown_refuser"],
        "likely_wounds": ["unseen worth", "performance-based love"],
        "likely_goals": ["prove the system is edited"],
        "relationship_tendencies": ["slow trust", "protective from the shadows"],
    }


def sample_world_grounding():
    return {
        "world_dependency_tags": [
            "magic_access_law",
            "family_name_legal_trust",
            "academy_gatekeeping",
            "oath_religion",
        ],
        "active_story_hooks": [
            "Forbidden education can become a legal, class, and institutional conflict.",
        ],
    }


def sample_agent_state():
    return {
        "internal_state": {
            "core_wound": "performance-based love",
            "core_desire": "to be chosen without proving usefulness",
            "core_fear": "being disposable",
        },
        "agency_state": {
            "agency_score": 0.8,
        },
    }


def test_character_genesis_engine_returns_engine_result():
    engine = CharacterGenesisEngine()

    result = engine.run(
        {
            "project_id": "proj_ashen",
            "universe_id": "uni_main",
            "world_state": sample_world_state(),
            "population_context": sample_population_context(),
            "people_type": sample_people_type(),
            "world_grounding": sample_world_grounding(),
            "agent_state": sample_agent_state(),
            "character_mode": "protagonist",
        }
    )

    assert isinstance(result, EngineRunResult)
    assert result.success is True
    assert result.engine_name == "character.genesis_engine"
    assert "character_identity" in result.data
    assert "genesis_seed" in result.data
    assert "relationship_hooks" in result.data
    assert "interaction_potential" in result.data
    assert "next_engine_payload" in result.data


def test_character_genesis_engine_generates_valid_identity():
    engine = CharacterGenesisEngine()

    result = engine.run(
        {
            "project_id": "proj_ashen",
            "universe_id": "uni_main",
            "world_state": sample_world_state(),
            "population_context": sample_population_context(),
            "people_type": sample_people_type(),
            "world_grounding": sample_world_grounding(),
            "character_mode": "protagonist",
            "seed_hint": "hidden kingmaker named Kael",
        }
    )

    identity = CharacterIdentity.model_validate(result.data["character_identity"])

    assert identity.character_id.startswith("char_")
    assert identity.project_id == "proj_ashen"
    assert identity.universe_id == "uni_main"
    assert identity.world_id == "world_velmora"
    assert identity.name == "Kael Veyran"
    assert identity.role == "protagonist"
    assert identity.importance_level == 5
    assert "ptype_hidden_kingmaker" in identity.tags


def test_character_genesis_engine_creates_world_grounded_seed():
    engine = CharacterGenesisEngine()

    result = engine.run(
        {
            "project_id": "proj_ashen",
            "universe_id": "uni_main",
            "world_state": sample_world_state(),
            "population_context": sample_population_context(),
            "people_type": sample_people_type(),
            "world_grounding": sample_world_grounding(),
            "agent_state": sample_agent_state(),
            "character_mode": "protagonist",
        }
    )

    seed = result.data["genesis_seed"]

    assert seed["social_class"] == "academy_sponsored"
    assert seed["family_name_status"] in {"recognized", "distrusted", "trusted"}
    assert seed["core_wound"] == "performance-based love"
    assert seed["core_desire"] == "to be chosen without proving usefulness"
    assert seed["core_fear"] == "being disposable"
    assert seed["primary_skill"] == "Pattern Reading"
    assert seed["skill_rarity"] == "rare"
    assert seed["skill_cost"] is not None
    assert "academy_gatekeeping" in seed["world_dependency_tags"]


def test_character_genesis_engine_includes_adaptability_and_limit_break_ready_fields():
    engine = CharacterGenesisEngine()

    people_type = {
        "people_type_id": "ptype_limit_break_anomaly",
        "name": "Limit-Break Anomaly",
        "compatible_roles": ["protagonist"],
        "compatible_classes": ["academy_sponsored"],
        "compatible_destinies": ["anomaly_bearer"],
        "likely_wounds": ["unwanted power"],
        "likely_goals": ["control the breakthrough"],
    }

    result = engine.run(
        {
            "project_id": "proj_ashen",
            "universe_id": "uni_main",
            "world_state": sample_world_state(),
            "population_context": sample_population_context(),
            "people_type": people_type,
            "world_grounding": sample_world_grounding(),
            "character_mode": "protagonist",
        }
    )

    seed = result.data["genesis_seed"]

    assert seed["skill_rarity"] == "anomaly"
    assert seed["adaptability_type"] == "limit_break_anomaly"
    assert seed["breakthrough_condition"] is not None
    assert seed["adaptation_cost"] is not None
    assert seed["adaptation_risk"] is not None
    assert seed["post_break_consequence"] is not None

    payload = result.data["next_engine_payload"]["adaptability_engine_payload"]

    assert payload["breakthrough_condition"] == seed["breakthrough_condition"]
    assert payload["adaptation_cost"] == seed["adaptation_cost"]
    assert payload["adaptation_risk"] == seed["adaptation_risk"]


def test_character_genesis_engine_builds_relationship_hooks_for_future_chunk4():
    engine = CharacterGenesisEngine()

    result = engine.run(
        {
            "project_id": "proj_ashen",
            "universe_id": "uni_main",
            "world_state": sample_world_state(),
            "population_context": sample_population_context(),
            "people_type": sample_people_type(),
            "world_grounding": sample_world_grounding(),
            "character_mode": "protagonist",
        }
    )

    hooks = result.data["relationship_hooks"]

    assert "trust_triggers" in hooks
    assert "betrayal_triggers" in hooks
    assert "romantic_response" in hooks
    assert "rivalry_response" in hooks
    assert "loyalty_threshold" in hooks
    assert "secret_pressure" in hooks
    assert "limit_break_relationship_trigger" in hooks


def test_character_genesis_engine_builds_interaction_potential_for_franchise_story():
    engine = CharacterGenesisEngine()

    result = engine.run(
        {
            "project_id": "proj_ashen",
            "universe_id": "uni_main",
            "world_state": sample_world_state(),
            "population_context": sample_population_context(),
            "people_type": sample_people_type(),
            "world_grounding": sample_world_grounding(),
            "character_mode": "protagonist",
        }
    )

    interaction = result.data["interaction_potential"]

    assert interaction["chunk4_ready"] is True
    assert "elite truth-seeker" in interaction["best_pairings"]
    assert "institutional antagonist" in interaction["best_pairings"]
    assert "force hidden goal into public action" in interaction["scene_functions"]
    assert "fan debate over moral choice" in interaction["franchise_potential_hooks"]


def test_character_genesis_engine_generates_villain_from_institutional_type():
    engine = CharacterGenesisEngine()

    result = engine.run(
        {
            "project_id": "proj_ashen",
            "universe_id": "uni_main",
            "world_state": sample_world_state(),
            "population_context": sample_population_context(),
            "people_type": {
                "people_type_id": "ptype_institutional_villain",
                "name": "Institutional Villain",
                "compatible_roles": ["villain"],
                "compatible_classes": ["imperial_elite"],
                "compatible_destinies": ["false_savior"],
                "likely_wounds": ["fear of chaos"],
                "likely_goals": ["preserve institutional continuity"],
            },
            "character_mode": "villain",
        }
    )

    identity = result.data["character_identity"]
    seed = result.data["genesis_seed"]

    assert identity["name"] == "Magister Oren Vaul"
    assert identity["role"] == "villain"
    assert seed["surface_goal"] == "preserve institutional order"
    assert seed["hidden_goal"] == "prove that order was worth the people it harmed"
    assert seed["primary_skill"] == "Legal Weaponization"


def test_character_genesis_engine_warns_without_context():
    engine = CharacterGenesisEngine()

    result = engine.run({})

    assert result.success is True
    assert len(result.warnings) == 3
    assert "world_state" in result.warnings[0]
    assert "people_type" in result.warnings[1]
    assert "population_context" in result.warnings[2]
    assert result.data["genesis_seed"]["name"] == result.data["character_identity"]["name"]

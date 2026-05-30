from backend.app.engines.character.character_agent_state_engine import CharacterAgentStateEngine
from backend.app.schemas.character import CharacterAgentState
from backend.app.schemas.foundation import EngineRunResult


def sample_people_type():
    return {
        "people_type_id": "ptype_hidden_kingmaker",
        "name": "Hidden Kingmaker",
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
        ],
        "active_story_hooks": [
            "Forbidden education can become a legal, class, and institutional conflict.",
        ],
        "requires_human_review": False,
    }


def sample_character_seed():
    return {
        "character_id": "char_kael",
        "name": "Kael Veyran",
        "role": "protagonist",
        "social_class": "academy_sponsored",
        "family_name_status": "distrusted",
        "core_wound": "performance-based love",
        "core_desire": "to be chosen without proving usefulness",
        "core_fear": "being disposable",
        "defense_mechanism": "cold restraint",
        "surface_goal": "survive the academy exam",
        "hidden_goal": "find proof that the ranking system is edited",
        "primary_skill": "Pattern Reading",
        "skill_domain": "observation",
        "skill_rank": "S",
        "skill_rarity": "rare",
        "skill_cost": "emotional exhaustion",
        "limitation": "fails when personally attached",
        "destiny_type": "hidden_kingmaker",
        "destiny_burden": "must decide who receives power",
        "adaptability_type": "earned_breakthrough",
        "breakthrough_condition": "protects someone weaker from public punishment",
        "adaptation_cost": "burns safe anonymity",
        "adaptation_risk": "emotional crash",
        "post_break_consequence": "oath courts notice him",
    }


def test_agent_state_engine_returns_engine_result():
    engine = CharacterAgentStateEngine()

    result = engine.run(
        {
            "character_seed": sample_character_seed(),
            "world_grounding": sample_world_grounding(),
            "people_type": sample_people_type(),
        }
    )

    assert isinstance(result, EngineRunResult)
    assert result.success is True
    assert result.engine_name == "character.agent_state_engine"
    assert "agent_state" in result.data
    assert "state_diagnostics" in result.data
    assert "character_agent_summary" in result.data


def test_agent_state_engine_generates_valid_agent_state():
    engine = CharacterAgentStateEngine()

    result = engine.run(
        {
            "character_seed": sample_character_seed(),
            "world_grounding": sample_world_grounding(),
            "people_type": sample_people_type(),
        }
    )

    agent_state = CharacterAgentState.model_validate(result.data["agent_state"])

    assert agent_state.character_id == "char_kael"
    assert agent_state.agent_state_id.startswith("agent_")
    assert agent_state.internal_state["core_wound"] == "performance-based love"
    assert agent_state.external_state["social_class"] == "academy_sponsored"
    assert agent_state.social_state["family_name_status"] == "distrusted"
    assert agent_state.goal_state["hidden_goal"] == "find proof that the ranking system is edited"
    assert agent_state.skill_state["skill_rank"] == "S"
    assert agent_state.destiny_state["destiny_type"] == "hidden_kingmaker"
    assert agent_state.adaptability_state["limit_break_locked"] is False


def test_agent_state_engine_scores_simulation_readiness_high_for_deep_character():
    engine = CharacterAgentStateEngine()

    result = engine.run(
        {
            "character_seed": sample_character_seed(),
            "world_grounding": sample_world_grounding(),
            "people_type": sample_people_type(),
            "constraint_checks": [
                {"check_id": "rare_skill_cost", "status": "pass"},
                {"check_id": "adaptability_exception", "status": "pass"},
            ],
        }
    )

    summary = result.data["character_agent_summary"]
    diagnostics = result.data["state_diagnostics"]

    assert summary["simulation_readiness"] >= 0.65
    assert summary["can_enter_relationship_simulation"] is True
    assert diagnostics["readiness_tier"] in {"usable_with_minor_gaps", "simulation_ready"}
    assert diagnostics["next_recommended_step"] == "advance_to_character_genesis"


def test_agent_state_engine_locks_limit_break_when_missing_cost_risk_consequence():
    engine = CharacterAgentStateEngine()

    seed = sample_character_seed()
    seed.pop("adaptation_risk")
    seed.pop("post_break_consequence")

    result = engine.run(
        {
            "character_seed": seed,
            "world_grounding": sample_world_grounding(),
            "people_type": {
                "people_type_id": "ptype_limit_break_anomaly",
                "name": "Limit-Break Anomaly",
            },
        }
    )

    agent_state = result.data["agent_state"]
    diagnostics = result.data["state_diagnostics"]

    assert agent_state["adaptability_state"]["has_limit_break_concept"] is True
    assert agent_state["adaptability_state"]["limit_break_locked"] is True
    assert diagnostics["limit_break_locked"] is True


def test_agent_state_engine_reduces_readiness_when_constraints_violate_world_logic():
    engine = CharacterAgentStateEngine()

    result = engine.run(
        {
            "character_seed": sample_character_seed(),
            "world_grounding": sample_world_grounding(),
            "people_type": sample_people_type(),
            "constraint_checks": [
                {"check_id": "commoner_magic_access", "status": "violation"},
                {"check_id": "academy_access", "status": "violation"},
            ],
        }
    )

    diagnostics = result.data["state_diagnostics"]

    assert "commoner_magic_access" in diagnostics["constraint_violations"]
    assert "academy_access" in diagnostics["constraint_violations"]
    assert diagnostics["next_recommended_step"] == "repair_character_state_before_simulation"


def test_agent_state_engine_builds_interaction_ready_social_state():
    engine = CharacterAgentStateEngine()

    result = engine.run(
        {
            "character_seed": sample_character_seed(),
            "world_grounding": sample_world_grounding(),
            "people_type": sample_people_type(),
        }
    )

    social_state = result.data["agent_state"]["social_state"]

    assert "trust_triggers" in social_state
    assert "betrayal_triggers" in social_state
    assert "conflict_style" in social_state
    assert "dialogue_style" in social_state
    assert "slow trust" in social_state["relationship_tendencies"]


def test_agent_state_engine_warns_when_empty_payload():
    engine = CharacterAgentStateEngine()

    result = engine.run({})

    assert result.success is True
    assert len(result.warnings) == 1
    assert "character_seed" in result.warnings[0]
    assert result.data["agent_state"]["simulation_readiness"] > 0.0

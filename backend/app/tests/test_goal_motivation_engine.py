from backend.app.engines.character.goal_motivation_engine import GoalMotivationEngine
from backend.app.schemas.foundation import EngineRunResult


def sample_seed():
    return {
        "character_id": "char_kael",
        "name": "Kael Veyran",
        "role": "protagonist",
        "social_class": "academy_sponsored",
        "family_name_status": "distrusted",
        "hidden_goal": "find proof that the ranking system is edited",
        "destiny_type": "hidden_kingmaker",
        "adaptability_type": "earned_breakthrough",
        "breakthrough_condition": "protects someone weaker from public punishment",
        "adaptation_cost": "burns safe anonymity",
    }


def sample_psychology():
    return {
        "character_id": "char_kael",
        "core_fear": "belonging being revoked after one visible failure",
        "core_lie": "worth can be revoked by public failure",
        "core_truth": "belonging is not the same as permission",
        "core_desire": "find proof that the ranking system is edited",
        "defense_mechanism": "controlled self-erasure",
        "shame_trigger": "being treated as useful but replaceable",
        "healing_condition": "someone learns the family truth and protects them without using it",
        "betrayal_response": "goes cold, protects family secrets, and remembers exact words",
    }


def sample_reputation():
    return {
        "character_id": "char_kael",
        "institutional_reputation": 0.28,
        "enemy_threat_reputation": 0.58,
        "exposure_risk": 0.72,
        "reputation_liabilities": ["family secrets", "forbidden access"],
    }


def sample_consequence_hooks():
    return [
        {
            "hook_type": "exposure_event",
            "description": "A public event can expose secret, forbidden access, family truth, or anomaly behavior.",
            "story_use": "midpoint pressure",
        },
        {
            "hook_type": "enemy_attention",
            "description": "Enemies begin treating the character as strategically dangerous.",
            "story_use": "antagonist escalation",
        },
    ]


def sample_world_grounding():
    return {
        "world_dependency_tags": [
            "academy_gatekeeping",
            "family_name_legal_trust",
            "magic_access_law",
        ]
    }


def test_goal_engine_returns_engine_result():
    engine = GoalMotivationEngine()

    result = engine.run(
        {
            "character_seed": sample_seed(),
            "psychology_profile": sample_psychology(),
            "reputation_profile": sample_reputation(),
            "consequence_hooks": sample_consequence_hooks(),
            "world_grounding": sample_world_grounding(),
        }
    )

    assert isinstance(result, EngineRunResult)
    assert result.success is True
    assert result.engine_name == "character.goal_motivation_engine"
    assert "goal_profile" in result.data
    assert "motivation_stack" in result.data
    assert "agency_rules" in result.data
    assert "conflict_hooks" in result.data
    assert "goal_diagnostics" in result.data
    assert "next_engine_payload" in result.data


def test_goal_engine_builds_goal_profile_with_want_need_split():
    engine = GoalMotivationEngine()

    result = engine.run(
        {
            "character_seed": sample_seed(),
            "psychology_profile": sample_psychology(),
            "reputation_profile": sample_reputation(),
            "consequence_hooks": sample_consequence_hooks(),
            "world_grounding": sample_world_grounding(),
        }
    )

    profile = result.data["goal_profile"]

    assert profile["character_id"] == "char_kael"
    assert profile["goal_profile_id"].startswith("goal_")
    assert profile["surface_goal"] == "understand why destiny has marked them"
    assert profile["hidden_goal"] == "find proof that the ranking system is edited"
    assert profile["false_need"] == "worth can be revoked by public failure"
    assert profile["true_need"] == "belonging is not the same as permission"
    assert "exposure_event" in profile["primary_stake"]
    assert profile["agency_score"] >= 0.6


def test_goal_engine_builds_external_and_internal_blockers():
    engine = GoalMotivationEngine()

    result = engine.run(
        {
            "character_seed": sample_seed(),
            "psychology_profile": sample_psychology(),
            "reputation_profile": sample_reputation(),
            "world_grounding": sample_world_grounding(),
        }
    )

    profile = result.data["goal_profile"]

    assert "institutions do not trust them" in profile["external_blockers"]
    assert "public exposure risk" in profile["external_blockers"]
    assert "academy gatekeeping" in profile["external_blockers"]
    assert "low-trust family name" in profile["external_blockers"]
    assert "belonging being revoked after one visible failure" in profile["internal_blockers"]
    assert "defense mechanism: controlled self-erasure" in profile["internal_blockers"]


def test_goal_engine_builds_motivation_stack_from_memory_and_reputation():
    engine = GoalMotivationEngine()

    result = engine.run(
        {
            "character_seed": sample_seed(),
            "psychology_profile": sample_psychology(),
            "memory_records": [
                {
                    "memory_id": "mem_1",
                    "emotional_weight": 0.82,
                    "behavioral_influence": ["reacts strongly to public failure"],
                },
                {
                    "memory_id": "mem_2",
                    "emotional_weight": 0.62,
                    "behavioral_influence": ["protects family secret"],
                },
            ],
            "reputation_profile": sample_reputation(),
            "world_grounding": sample_world_grounding(),
        }
    )

    stack = result.data["motivation_stack"]

    assert stack["primary_motivation"] == "find proof that the ranking system is edited"
    assert stack["reputation_motivation"] == "avoid exposure while shaping public interpretation"
    assert len(stack["memory_drivers"]) == 2
    assert stack["need_hierarchy"][0] == "worth can be revoked by public failure"


def test_goal_engine_agency_rules_include_limit_break_condition():
    engine = GoalMotivationEngine()

    result = engine.run(
        {
            "character_seed": sample_seed(),
            "psychology_profile": sample_psychology(),
            "reputation_profile": sample_reputation(),
            "world_grounding": sample_world_grounding(),
        }
    )

    rules = result.data["agency_rules"]
    conditions = " ".join(rule["condition"] for rule in rules["escalation_rules"]).lower()

    assert rules["can_initiate_plot"] is True
    assert rules["can_escalate_conflict"] is True
    assert "protects someone weaker" in conditions
    assert rules["risk_tolerance"] >= 0.5
    assert "controlled self-erasure" in rules["agency_failure_mode"]


def test_goal_engine_builds_conflict_hooks_for_plot():
    engine = GoalMotivationEngine()

    result = engine.run(
        {
            "character_seed": sample_seed(),
            "psychology_profile": sample_psychology(),
            "reputation_profile": sample_reputation(),
            "consequence_hooks": sample_consequence_hooks(),
            "world_grounding": sample_world_grounding(),
        }
    )

    hooks = result.data["conflict_hooks"]
    hook_types = {hook["hook_type"] for hook in hooks}

    assert "want_vs_need" in hook_types
    assert "goal_vs_exposure" in hook_types
    assert "choice_pressure" in hook_types
    assert "reputation_exposure_event" in hook_types


def test_goal_engine_villain_goals_center_order_control_and_accountability():
    engine = GoalMotivationEngine()

    result = engine.run(
        {
            "character_seed": {
                "character_id": "char_oren",
                "name": "Magister Oren Vaul",
                "role": "villain",
            },
            "psychology_profile": {
                "character_id": "char_oren",
                "core_lie": "order matters more than innocent exceptions",
                "core_truth": "order without mercy is cowardice",
            },
            "reputation_profile": {
                "character_id": "char_oren",
                "institutional_reputation": 0.9,
                "exposure_risk": 0.2,
            },
        }
    )

    profile = result.data["goal_profile"]
    rules = result.data["agency_rules"]

    assert profile["surface_goal"] == "preserve the system that gives them authority"
    assert profile["true_need"] == "order without mercy is cowardice"
    assert "Order conflicts with mercy." in profile["goal_conflicts"]
    assert "control" in rules["decision_style"]


def test_goal_engine_diagnostics_are_plot_ready():
    engine = GoalMotivationEngine()

    result = engine.run(
        {
            "character_seed": sample_seed(),
            "psychology_profile": sample_psychology(),
            "reputation_profile": sample_reputation(),
            "consequence_hooks": sample_consequence_hooks(),
            "world_grounding": sample_world_grounding(),
        }
    )

    diagnostics = result.data["goal_diagnostics"]

    assert diagnostics["goal_completeness_score"] >= 0.9
    assert diagnostics["has_want_need_split"] is True
    assert diagnostics["has_false_true_need_split"] is True
    assert diagnostics["has_external_blockers"] is True
    assert diagnostics["has_internal_blockers"] is True
    assert diagnostics["has_sacrifices"] is True
    assert diagnostics["has_escalation_rules"] is True
    assert diagnostics["has_conflict_hooks"] is True
    assert diagnostics["agency_ready"] is True
    assert diagnostics["plot_ready"] is True


def test_goal_engine_builds_next_engine_payloads():
    engine = GoalMotivationEngine()

    result = engine.run(
        {
            "character_seed": sample_seed(),
            "psychology_profile": sample_psychology(),
            "reputation_profile": sample_reputation(),
            "consequence_hooks": sample_consequence_hooks(),
            "world_grounding": sample_world_grounding(),
        }
    )

    payload = result.data["next_engine_payload"]

    assert "character_seed" in payload
    assert "moral_engine_payload" in payload
    assert "skill_engine_payload" in payload
    assert "adaptability_engine_payload" in payload
    assert "plot_engine_payload_later" in payload
    assert payload["character_seed"]["goal_profile"]["character_id"] == "char_kael"


def test_goal_engine_warns_without_character_seed():
    engine = GoalMotivationEngine()

    result = engine.run({})

    assert result.success is True
    assert len(result.warnings) == 1
    assert "character_seed" in result.warnings[0]
    assert result.data["goal_profile"]["character_id"].startswith("char_")

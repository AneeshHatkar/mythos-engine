from backend.app.engines.character.emotional_arc_engine import EmotionalArcEngine
from backend.app.schemas.character import EmotionalArcProfile
from backend.app.schemas.foundation import EngineRunResult


def sample_seed():
    return {
        "character_id": "char_kael",
        "name": "Kael Veyran",
        "role": "protagonist",
        "adaptability_type": "earned_breakthrough",
        "breakthrough_condition": "protects someone weaker from public punishment",
    }


def sample_psychology():
    return {
        "character_id": "char_kael",
        "core_wound": "believes belonging can be revoked at any public failure",
        "core_truth": "worth exists before usefulness",
        "defense_mechanism": "controlled self-erasure",
        "shame_trigger": "being treated as useful but replaceable",
        "love_response": "wants closeness but fears what intimacy will expose",
        "healing_condition": "someone learns the family truth and protects them without using it",
        "corruption_condition": "sacrifices another person to escape family pressure",
    }


def sample_trauma_records():
    return [
        {
            "trauma_id": "trauma_core",
            "character_id": "char_kael",
            "trauma_source": "core wound: public failure",
            "trauma_intensity": 0.72,
        },
        {
            "trauma_id": "trauma_family",
            "character_id": "char_kael",
            "trauma_source": "family secrecy",
            "trauma_intensity": 0.62,
        },
    ]


def sample_healing_profile():
    return {
        "character_id": "char_kael",
        "primary_healing_condition": "someone learns the family truth and protects them without using it",
        "recovery_milestones": ["admits one partial truth", "chooses disclosure before coercion"],
    }


def sample_emotional_state():
    return {
        "character_id": "char_kael",
        "baseline": {
            "hope": 0.5,
            "despair": 0.3,
            "anger": 0.4,
        },
        "current": {
            "hope": 0.48,
            "despair": 0.36,
            "anger": 0.45,
        },
    }


def sample_update_rules():
    return [
        {"trigger": "shame_trigger_repeated", "updates": {"shame": 0.12}},
        {"trigger": "healing_condition_met", "updates": {"hope": 0.15}},
    ]


def test_emotional_arc_engine_returns_engine_result():
    engine = EmotionalArcEngine()

    result = engine.run(
        {
            "character_seed": sample_seed(),
            "psychology_profile": sample_psychology(),
            "trauma_records": sample_trauma_records(),
            "healing_profile": sample_healing_profile(),
            "emotional_state_profile": sample_emotional_state(),
            "emotion_update_rules": sample_update_rules(),
        }
    )

    assert isinstance(result, EngineRunResult)
    assert result.success is True
    assert result.engine_name == "character.emotional_arc_engine"
    assert "emotional_arc_profile" in result.data
    assert "arc_beats" in result.data
    assert "arc_diagnostics" in result.data
    assert "next_engine_payload" in result.data


def test_emotional_arc_engine_generates_valid_arc_profile():
    engine = EmotionalArcEngine()

    result = engine.run(
        {
            "character_seed": sample_seed(),
            "psychology_profile": sample_psychology(),
            "trauma_records": sample_trauma_records(),
            "healing_profile": sample_healing_profile(),
            "emotional_state_profile": sample_emotional_state(),
            "emotion_update_rules": sample_update_rules(),
        }
    )

    arc = EmotionalArcProfile.model_validate(result.data["emotional_arc_profile"])

    assert arc.character_id == "char_kael"
    assert arc.emotional_arc_id.startswith("earc_")
    assert arc.arc_type == "adaptive_breakthrough_arc"
    assert len(arc.hope_curve) == 6
    assert len(arc.despair_cycle) == 6
    assert len(arc.romantic_tension_curve) == 6
    assert len(arc.rage_escalation) == 6
    assert len(arc.corruption_curve) == 6
    assert len(arc.redemption_curve) == 6
    assert arc.emotional_climax is not None
    assert arc.emotional_resolution is not None


def test_emotional_arc_engine_limit_break_climax_uses_breakthrough_condition():
    engine = EmotionalArcEngine()

    result = engine.run(
        {
            "character_seed": sample_seed(),
            "psychology_profile": sample_psychology(),
            "trauma_records": sample_trauma_records(),
            "healing_profile": sample_healing_profile(),
            "emotional_state_profile": sample_emotional_state(),
        }
    )

    arc = result.data["emotional_arc_profile"]

    assert "Limit-break emotional climax" in arc["emotional_climax"]
    assert "protects someone weaker" in arc["emotional_climax"]


def test_emotional_arc_engine_builds_arc_beats_for_plot_and_relationships():
    engine = EmotionalArcEngine()

    result = engine.run(
        {
            "character_seed": sample_seed(),
            "psychology_profile": sample_psychology(),
            "trauma_records": sample_trauma_records(),
            "healing_profile": sample_healing_profile(),
            "emotional_state_profile": sample_emotional_state(),
        }
    )

    beats = result.data["arc_beats"]
    beat_names = {beat["beat"] for beat in beats}

    assert "initial_mask" in beat_names
    assert "first_trigger" in beat_names
    assert "relationship_pressure" in beat_names
    assert "midpoint_collapse_or_breakthrough" in beat_names
    assert "resolution_choice" in beat_names


def test_emotional_arc_engine_diagnostics_are_plot_ready():
    engine = EmotionalArcEngine()

    result = engine.run(
        {
            "character_seed": sample_seed(),
            "psychology_profile": sample_psychology(),
            "trauma_records": sample_trauma_records(),
            "healing_profile": sample_healing_profile(),
            "emotional_state_profile": sample_emotional_state(),
            "emotion_update_rules": sample_update_rules(),
        }
    )

    diagnostics = result.data["arc_diagnostics"]

    assert diagnostics["has_consistent_curves"] is True
    assert diagnostics["has_healing_milestones"] is True
    assert diagnostics["has_climax"] is True
    assert diagnostics["has_resolution"] is True
    assert diagnostics["has_update_rules"] is True
    assert diagnostics["plot_ready"] is True
    assert diagnostics["relationship_arc_ready"] is True
    assert diagnostics["corruption_or_redemption_ready"] is True


def test_emotional_arc_engine_villain_uses_corruption_arc():
    engine = EmotionalArcEngine()

    result = engine.run(
        {
            "character_seed": {
                "character_id": "char_oren",
                "name": "Magister Oren Vaul",
                "role": "villain",
            },
            "psychology_profile": {
                "character_id": "char_oren",
                "corruption_condition": "chooses order over innocent exceptions",
            },
            "emotional_state_profile": {
                "character_id": "char_oren",
                "current": {"hope": 0.3, "despair": 0.4, "anger": 0.5},
            },
        }
    )

    arc = result.data["emotional_arc_profile"]

    assert arc["arc_type"] == "corruption_or_accountability_arc"
    assert max(arc["corruption_curve"]) >= 0.8
    assert "accountability" in arc["emotional_resolution"].lower()


def test_emotional_arc_engine_builds_next_engine_payloads():
    engine = EmotionalArcEngine()

    result = engine.run(
        {
            "character_seed": sample_seed(),
            "psychology_profile": sample_psychology(),
            "trauma_records": sample_trauma_records(),
            "healing_profile": sample_healing_profile(),
            "emotional_state_profile": sample_emotional_state(),
            "emotion_update_rules": sample_update_rules(),
        }
    )

    payload = result.data["next_engine_payload"]

    assert "character_seed" in payload
    assert "memory_engine_payload" in payload
    assert "goal_engine_payload" in payload
    assert "plot_engine_payload_later" in payload
    assert payload["character_seed"]["emotional_arc"]["character_id"] == "char_kael"
    assert "curves" in payload["plot_engine_payload_later"]


def test_emotional_arc_engine_warns_without_context():
    engine = EmotionalArcEngine()

    result = engine.run({})

    assert result.success is True
    assert len(result.warnings) == 2
    assert "character_seed" in result.warnings[0]
    assert "emotional_state_profile" in result.warnings[1]
    assert result.data["emotional_arc_profile"]["character_id"].startswith("char_")

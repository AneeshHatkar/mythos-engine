from backend.app.engines.character.emotion_engine import EmotionEngine
from backend.app.schemas.character import EmotionalStateProfile
from backend.app.schemas.foundation import EngineRunResult


def sample_seed():
    return {
        "character_id": "char_kael",
        "name": "Kael Veyran",
        "role": "protagonist",
        "family_pressure": {
            "pressure_tier": "high_family_pressure",
        },
        "destiny_type": "hidden_kingmaker",
        "adaptability_type": "earned_breakthrough",
        "breakthrough_condition": "protects someone weaker from public punishment",
    }


def sample_psychology():
    return {
        "character_id": "char_kael",
        "core_wound": "believes belonging can be revoked at any public failure",
        "core_fear": "belonging being revoked after one visible failure",
        "core_desire": "find proof that the ranking system is edited",
        "defense_mechanism": "controlled self-erasure",
        "attachment_tendency": "slow trust with secrecy tests",
        "shame_trigger": "being treated as useful but replaceable",
        "love_response": "wants closeness but fears what intimacy will expose",
        "betrayal_response": "goes cold, protects family secrets, and remembers exact words",
        "healing_condition": "someone learns the family truth and protects them without using it",
        "corruption_condition": "sacrifices another person to escape family pressure",
    }


def sample_trauma_records():
    return [
        {
            "trauma_id": "trauma_core",
            "character_id": "char_kael",
            "trauma_source": "core wound",
            "trauma_intensity": 0.72,
            "trigger_events": ["public failure", "rank comparison"],
            "coping_behavior": "controlled self-erasure",
            "healing_condition": "protected truth",
            "setback_conditions": ["public shame"],
        },
        {
            "trauma_id": "trauma_family",
            "character_id": "char_kael",
            "trauma_source": "family secrecy",
            "trauma_intensity": 0.62,
            "trigger_events": ["family record request"],
            "coping_behavior": "keeps explanations ready",
            "healing_condition": "family truth not weaponized",
            "setback_conditions": ["secret exposed publicly"],
        },
    ]


def sample_healing_profile():
    return {
        "character_id": "char_kael",
        "primary_healing_condition": "someone learns the family truth and protects them without using it",
        "recovery_milestones": ["admits one partial truth", "chooses disclosure before coercion"],
    }


def test_emotion_engine_returns_engine_result():
    engine = EmotionEngine()

    result = engine.run(
        {
            "character_seed": sample_seed(),
            "psychology_profile": sample_psychology(),
            "trauma_records": sample_trauma_records(),
            "healing_profile": sample_healing_profile(),
        }
    )

    assert isinstance(result, EngineRunResult)
    assert result.success is True
    assert result.engine_name == "character.emotion_engine"
    assert "emotional_state_profile" in result.data
    assert "emotion_drivers" in result.data
    assert "emotion_update_rules" in result.data
    assert "emotion_diagnostics" in result.data
    assert "next_engine_payload" in result.data


def test_emotion_engine_generates_valid_emotional_state_profile():
    engine = EmotionEngine()

    result = engine.run(
        {
            "character_seed": sample_seed(),
            "psychology_profile": sample_psychology(),
            "trauma_records": sample_trauma_records(),
            "healing_profile": sample_healing_profile(),
        }
    )

    profile = EmotionalStateProfile.model_validate(result.data["emotional_state_profile"])

    assert profile.character_id == "char_kael"
    assert profile.emotional_state_id.startswith("emo_")
    assert profile.baseline.fear > 0.0
    assert profile.current.shame > 0.0
    assert profile.volatility >= 0.45
    assert profile.recovery_rate > 0.0
    assert profile.dominant_state is not None
    assert len(profile.suppressed_emotions) >= 1


def test_emotion_engine_family_secrecy_and_limit_break_create_deltas():
    engine = EmotionEngine()

    result = engine.run(
        {
            "character_seed": sample_seed(),
            "psychology_profile": sample_psychology(),
            "trauma_records": sample_trauma_records(),
            "healing_profile": sample_healing_profile(),
        }
    )

    deltas = result.data["emotional_state_profile"]["recent_emotion_deltas"]
    sources = {delta["source"] for delta in deltas}

    assert "family secrecy pressure" in sources
    assert "limit-break pressure" in sources
    assert "public shame pressure" in sources


def test_emotion_engine_update_rules_include_relationship_and_limit_break_triggers():
    engine = EmotionEngine()

    result = engine.run(
        {
            "character_seed": sample_seed(),
            "psychology_profile": sample_psychology(),
            "trauma_records": sample_trauma_records(),
            "healing_profile": sample_healing_profile(),
        }
    )

    triggers = {rule["trigger"] for rule in result.data["emotion_update_rules"]}

    assert "shame_trigger_repeated" in triggers
    assert "trusted_person_protects_secret" in triggers
    assert "betrayal_pattern_repeats" in triggers
    assert "limit_break_condition_approaches" in triggers
    assert "healing_condition_met" in triggers


def test_emotion_engine_diagnostics_confirm_scene_readiness():
    engine = EmotionEngine()

    result = engine.run(
        {
            "character_seed": sample_seed(),
            "psychology_profile": sample_psychology(),
            "trauma_records": sample_trauma_records(),
            "healing_profile": sample_healing_profile(),
        }
    )

    diagnostics = result.data["emotion_diagnostics"]

    assert diagnostics["emotion_vector_complete"] is True
    assert diagnostics["has_recent_deltas"] is True
    assert diagnostics["has_suppressed_emotions"] is True
    assert diagnostics["stateful_scene_ready"] is True
    assert diagnostics["relationship_simulation_ready"] is True
    assert diagnostics["volatility_tier"] in {"moderate_volatility", "high_volatility"}


def test_emotion_engine_preserves_character_id_from_trauma_records_when_seed_missing_id():
    engine = EmotionEngine()

    result = engine.run(
        {
            "character_seed": {},
            "psychology_profile": {},
            "trauma_records": sample_trauma_records(),
            "healing_profile": {},
        }
    )

    assert result.data["emotional_state_profile"]["character_id"] == "char_kael"


def test_emotion_engine_builds_next_engine_payloads():
    engine = EmotionEngine()

    result = engine.run(
        {
            "character_seed": sample_seed(),
            "psychology_profile": sample_psychology(),
            "trauma_records": sample_trauma_records(),
            "healing_profile": sample_healing_profile(),
        }
    )

    payload = result.data["next_engine_payload"]

    assert "character_seed" in payload
    assert "emotional_arc_engine_payload" in payload
    assert "memory_engine_payload" in payload
    assert "relationship_simulation_payload_later" in payload
    assert payload["character_seed"]["emotional_state"]["character_id"] == "char_kael"


def test_emotion_engine_warns_without_character_seed():
    engine = EmotionEngine()

    result = engine.run({})

    assert result.success is True
    assert len(result.warnings) == 1
    assert "character_seed" in result.warnings[0]
    assert result.data["emotional_state_profile"]["character_id"].startswith("char_")

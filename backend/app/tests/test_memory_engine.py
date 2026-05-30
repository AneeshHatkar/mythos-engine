from backend.app.engines.character.memory_engine import MemoryEngine
from backend.app.schemas.character import MemoryRecord
from backend.app.schemas.foundation import EngineRunResult


def sample_seed():
    return {
        "character_id": "char_kael",
        "name": "Kael Veyran",
        "role": "protagonist",
        "family_name_status": "distrusted",
        "skill_rarity": "S",
        "destiny_type": "hidden_kingmaker",
        "breakthrough_condition": "protects someone weaker from public punishment",
    }


def sample_psychology():
    return {
        "character_id": "char_kael",
        "core_wound": "believes belonging can be revoked at any public failure",
        "shame_trigger": "being treated as useful but replaceable",
        "healing_condition": "someone learns the family truth and protects them without using it",
        "betrayal_response": "goes cold, protects family secrets, and remembers exact words",
    }


def sample_trauma_records():
    return [
        {
            "trauma_id": "trauma_core",
            "character_id": "char_kael",
            "trauma_source": "core wound: public failure",
            "trauma_intensity": 0.72,
            "trigger_events": ["public failure", "rank comparison"],
            "avoidance_behavior": "becomes quiet and hyper-observant",
            "coping_behavior": "relies on controlled self-erasure",
        },
        {
            "trauma_id": "trauma_family",
            "character_id": "char_kael",
            "trauma_source": "family secrecy",
            "trauma_intensity": 0.62,
            "trigger_events": ["family record request", "intimacy that requires disclosure"],
            "avoidance_behavior": "redirects family questions",
            "coping_behavior": "keeps parallel explanations ready",
        },
    ]


def sample_healing_profile():
    return {
        "character_id": "char_kael",
        "primary_healing_condition": "someone learns the family truth and protects them without using it",
    }


def sample_emotional_state():
    return {
        "character_id": "char_kael",
        "current": {
            "fear": 0.58,
            "shame": 0.7,
            "hope": 0.48,
        },
    }


def sample_emotional_arc():
    return {
        "character_id": "char_kael",
        "arc_type": "adaptive_breakthrough_arc",
        "emotional_climax": "Limit-break emotional climax occurs when protecting someone weaker.",
    }


def sample_arc_beats():
    return [
        {"beat": "initial_mask"},
        {"beat": "first_trigger"},
        {"beat": "relationship_pressure"},
        {"beat": "midpoint_collapse_or_breakthrough"},
        {"beat": "resolution_choice"},
    ]


def test_memory_engine_returns_engine_result():
    engine = MemoryEngine()

    result = engine.run(
        {
            "character_seed": sample_seed(),
            "psychology_profile": sample_psychology(),
            "trauma_records": sample_trauma_records(),
            "healing_profile": sample_healing_profile(),
            "emotional_state_profile": sample_emotional_state(),
            "emotional_arc_profile": sample_emotional_arc(),
            "arc_beats": sample_arc_beats(),
        }
    )

    assert isinstance(result, EngineRunResult)
    assert result.success is True
    assert result.engine_name == "character.memory_engine"
    assert "memory_records" in result.data
    assert "memory_network" in result.data
    assert "memory_diagnostics" in result.data
    assert "next_engine_payload" in result.data


def test_memory_engine_generates_valid_memory_records():
    engine = MemoryEngine()

    result = engine.run(
        {
            "character_seed": sample_seed(),
            "psychology_profile": sample_psychology(),
            "trauma_records": sample_trauma_records(),
            "healing_profile": sample_healing_profile(),
            "emotional_state_profile": sample_emotional_state(),
            "emotional_arc_profile": sample_emotional_arc(),
            "arc_beats": sample_arc_beats(),
        }
    )

    records = [MemoryRecord.model_validate(item) for item in result.data["memory_records"]]

    assert len(records) >= 6
    assert all(record.character_id == "char_kael" for record in records)
    assert all(record.content for record in records)
    assert all(record.emotional_weight > 0.0 for record in records)
    assert all(0.0 <= record.reliability <= 1.0 for record in records)
    assert all(record.trigger_terms for record in records)
    assert all(record.behavioral_influence for record in records)


def test_memory_engine_core_wound_memory_has_high_weight_and_triggers():
    engine = MemoryEngine()

    result = engine.run(
        {
            "character_seed": sample_seed(),
            "psychology_profile": sample_psychology(),
            "trauma_records": sample_trauma_records(),
            "healing_profile": sample_healing_profile(),
        }
    )

    core_memory = result.data["memory_records"][0]

    assert "core wound" in core_memory["event_id"]
    assert core_memory["emotional_weight"] >= 0.8
    assert "failure" in core_memory["trigger_terms"]
    assert "replaceable" in core_memory["trigger_terms"]


def test_memory_engine_creates_limit_break_trigger_memory():
    engine = MemoryEngine()

    result = engine.run(
        {
            "character_seed": sample_seed(),
            "psychology_profile": sample_psychology(),
            "trauma_records": sample_trauma_records(),
            "healing_profile": sample_healing_profile(),
        }
    )

    limit_memories = [
        memory for memory in result.data["memory_records"]
        if memory["event_id"] == "evt_limit_break_trigger_memory"
    ]

    assert len(limit_memories) == 1

    memory = limit_memories[0]

    assert "adaptability" in " ".join(memory["behavioral_influence"]).lower()
    assert "weaker person" in memory["trigger_terms"]
    assert "threshold symbol" in memory["related_objects"]


def test_memory_engine_builds_memory_network_indexes():
    engine = MemoryEngine()

    result = engine.run(
        {
            "character_seed": sample_seed(),
            "psychology_profile": sample_psychology(),
            "trauma_records": sample_trauma_records(),
            "healing_profile": sample_healing_profile(),
            "arc_beats": sample_arc_beats(),
        }
    )

    network = result.data["memory_network"]

    assert network["character_id"] == "char_kael"
    assert network["memory_count"] >= 6
    assert network["strongest_memory_id"] is not None
    assert network["strongest_memory_weight"] > 0.0
    assert "trigger_index" in network
    assert "people_index" in network
    assert "object_index" in network
    assert "location_index" in network
    assert "family-name badge" in network["object_index"]


def test_memory_engine_diagnostics_confirm_relationship_and_rag_readiness():
    engine = MemoryEngine()

    result = engine.run(
        {
            "character_seed": sample_seed(),
            "psychology_profile": sample_psychology(),
            "trauma_records": sample_trauma_records(),
            "healing_profile": sample_healing_profile(),
            "arc_beats": sample_arc_beats(),
        }
    )

    diagnostics = result.data["memory_diagnostics"]

    assert diagnostics["memory_count"] >= 6
    assert diagnostics["has_trigger_logic"] is True
    assert diagnostics["has_behavioral_influence"] is True
    assert diagnostics["has_related_links"] is True
    assert diagnostics["has_reliability_scores"] is True
    assert diagnostics["memory_network_ready"] is True
    assert diagnostics["relationship_simulation_ready"] is True
    assert diagnostics["rag_memory_ready_later"] is True


def test_memory_engine_builds_next_engine_payloads():
    engine = MemoryEngine()

    result = engine.run(
        {
            "character_seed": sample_seed(),
            "psychology_profile": sample_psychology(),
            "trauma_records": sample_trauma_records(),
            "healing_profile": sample_healing_profile(),
            "emotional_state_profile": sample_emotional_state(),
            "emotional_arc_profile": sample_emotional_arc(),
            "arc_beats": sample_arc_beats(),
        }
    )

    payload = result.data["next_engine_payload"]

    assert "character_seed" in payload
    assert "reputation_engine_payload" in payload
    assert "goal_engine_payload" in payload
    assert "relationship_simulation_payload_later" in payload
    assert len(payload["character_seed"]["memories"]) >= 6
    assert payload["relationship_simulation_payload_later"]["character_id"] == "char_kael"


def test_memory_engine_handles_low_context_character():
    engine = MemoryEngine()

    result = engine.run(
        {
            "character_seed": {
                "character_id": "char_tovin",
                "name": "Tovin Reed",
            }
        }
    )

    assert result.success is True
    assert len(result.data["memory_records"]) == 1
    assert result.data["memory_records"][0]["character_id"] == "char_tovin"
    assert result.data["memory_records"][0]["emotional_weight"] <= 0.4


def test_memory_engine_warns_without_character_seed():
    engine = MemoryEngine()

    result = engine.run({})

    assert result.success is True
    assert len(result.warnings) == 1
    assert "character_seed" in result.warnings[0]
    assert result.data["memory_summary"]["memory_count"] >= 1

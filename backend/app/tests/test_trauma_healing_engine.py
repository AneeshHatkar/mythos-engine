from backend.app.engines.character.trauma_healing_engine import TraumaHealingEngine
from backend.app.schemas.character import TraumaRecord
from backend.app.schemas.foundation import EngineRunResult


def sample_seed():
    return {
        "character_id": "char_kael",
        "name": "Kael Veyran",
        "role": "protagonist",
        "social_class": "academy_sponsored",
        "hidden_goal": "find proof that the ranking system is edited",
        "breakthrough_condition": "protects someone weaker from public punishment",
    }


def sample_psychology():
    return {
        "character_id": "char_kael",
        "core_wound": "believes belonging can be revoked at any public failure",
        "core_desire": "find proof that the ranking system is edited",
        "core_fear": "belonging being revoked after one visible failure",
        "defense_mechanism": "controlled self-erasure",
        "attachment_tendency": "slow trust with secrecy tests",
        "shame_trigger": "being treated as useful but replaceable",
        "stress_response": "becomes quiet, over-controlled, and hyper-observant",
        "love_response": "wants closeness but fears what intimacy will expose",
        "betrayal_response": "goes cold, protects family secrets, and remembers exact words",
        "healing_condition": "someone learns the family truth and protects them without using it",
        "corruption_condition": "sacrifices another person to escape family pressure",
    }


def sample_origin():
    return {
        "character_id": "char_kael",
        "social_class": "academy_sponsored",
        "class_wound": "believes belonging can be revoked at any public failure",
        "public_assumptions": ["useful but replaceable"],
    }


def sample_family():
    return {
        "character_id": "char_kael",
        "family_status": "conditionally_recognized",
        "family_secrets": ["sponsor support is tied to an undisclosed obligation"],
        "family_debt": ["sponsor debt tied to academy access"],
        "inherited_trauma": ["fear of public failure causing family disgrace"],
    }


def test_trauma_healing_engine_returns_engine_result():
    engine = TraumaHealingEngine()

    result = engine.run(
        {
            "character_seed": sample_seed(),
            "psychology_profile": sample_psychology(),
            "origin_profile": sample_origin(),
            "family_profile": sample_family(),
        }
    )

    assert isinstance(result, EngineRunResult)
    assert result.success is True
    assert result.engine_name == "character.trauma_healing_engine"
    assert "trauma_records" in result.data
    assert "healing_profile" in result.data
    assert "trauma_diagnostics" in result.data
    assert "next_engine_payload" in result.data


def test_trauma_healing_engine_generates_valid_trauma_records():
    engine = TraumaHealingEngine()

    result = engine.run(
        {
            "character_seed": sample_seed(),
            "psychology_profile": sample_psychology(),
            "origin_profile": sample_origin(),
            "family_profile": sample_family(),
        }
    )

    records = [TraumaRecord.model_validate(item) for item in result.data["trauma_records"]]

    assert len(records) >= 3
    assert all(record.character_id == "char_kael" for record in records)
    assert all(record.trauma_source for record in records)
    assert all(record.trigger_events for record in records)
    assert all(record.coping_behavior for record in records)
    assert all(record.healing_condition for record in records)
    assert all(record.recovery_milestones for record in records)
    assert all(record.setback_conditions for record in records)


def test_trauma_engine_core_wound_record_has_behavioral_logic():
    engine = TraumaHealingEngine()

    result = engine.run(
        {
            "character_seed": sample_seed(),
            "psychology_profile": sample_psychology(),
            "origin_profile": sample_origin(),
            "family_profile": sample_family(),
        }
    )

    core_record = result.data["trauma_records"][0]

    assert "core wound" in core_record["trauma_source"]
    assert core_record["trauma_intensity"] >= 0.6
    assert "public failure" in core_record["trigger_events"]
    assert core_record["avoidance_behavior"] == "becomes quiet, over-controlled, and hyper-observant"
    assert "controlled self-erasure" in core_record["coping_behavior"]


def test_trauma_engine_family_secret_creates_intimacy_disclosure_trauma():
    engine = TraumaHealingEngine()

    result = engine.run(
        {
            "character_seed": sample_seed(),
            "psychology_profile": sample_psychology(),
            "origin_profile": sample_origin(),
            "family_profile": sample_family(),
        }
    )

    family_records = [
        record for record in result.data["trauma_records"]
        if "family secrecy" in record["trauma_source"]
    ]

    assert len(family_records) == 1

    record = family_records[0]

    assert "intimacy that requires disclosure" in record["trigger_events"]
    assert "family truth is known" in record["healing_condition"]
    assert "secret exposed publicly" in record["setback_conditions"]


def test_trauma_engine_builds_healing_profile_with_unsafe_shortcuts():
    engine = TraumaHealingEngine()

    result = engine.run(
        {
            "character_seed": sample_seed(),
            "psychology_profile": sample_psychology(),
            "origin_profile": sample_origin(),
            "family_profile": sample_family(),
        }
    )

    healing = result.data["healing_profile"]

    assert healing["character_id"] == "char_kael"
    assert healing["primary_healing_condition"] is not None
    assert healing["primary_healing_relationship"] is not None
    assert healing["healing_style"] == "slow relational trust with repeated proof"
    assert "instant forgiveness" in healing["unsafe_shortcuts"]
    assert "power-up replacing emotional recovery" in healing["unsafe_shortcuts"]


def test_trauma_engine_diagnostics_confirm_not_decorative():
    engine = TraumaHealingEngine()

    result = engine.run(
        {
            "character_seed": sample_seed(),
            "psychology_profile": sample_psychology(),
            "origin_profile": sample_origin(),
            "family_profile": sample_family(),
        }
    )

    diagnostics = result.data["trauma_diagnostics"]

    assert diagnostics["trauma_record_count"] >= 3
    assert diagnostics["behavioral_completeness_score"] >= 0.8
    assert diagnostics["has_trigger_logic"] is True
    assert diagnostics["has_coping_logic"] is True
    assert diagnostics["has_healing_logic"] is True
    assert diagnostics["has_setback_logic"] is True
    assert diagnostics["trauma_not_decorative"] is True
    assert diagnostics["ready_for_emotion_engine"] is True


def test_trauma_engine_handles_low_intensity_character_without_extreme_trauma():
    engine = TraumaHealingEngine()

    result = engine.run(
        {
            "character_seed": {
                "character_id": "char_tovin",
                "name": "Tovin Reed",
                "role": "ordinary_citizen",
            },
            "psychology_profile": {},
            "origin_profile": {},
            "family_profile": {},
        }
    )

    records = result.data["trauma_records"]

    assert len(records) == 1
    assert records[0]["trauma_source"] == "low-intensity identity pressure"
    assert records[0]["trauma_intensity"] <= 0.4
    assert "not every character needs extreme trauma" in " ".join(records[0]["content_safety_notes"]).lower()


def test_trauma_engine_marks_high_intensity_for_erasure_or_betrayal():
    engine = TraumaHealingEngine()

    result = engine.run(
        {
            "character_seed": {
                "character_id": "char_sera",
            },
            "psychology_profile": {
                "character_id": "char_sera",
                "core_wound": "legal erasure after guardian betrayal",
                "healing_condition": "is believed without documents",
                "defense_mechanism": "avoidance",
            },
            "origin_profile": {
                "character_id": "char_sera",
                "social_class": "erased",
            },
            "family_profile": {},
        }
    )

    records = result.data["trauma_records"]

    assert records[0]["trauma_intensity"] >= 0.8
    assert result.data["trauma_diagnostics"]["needs_content_review"] is False


def test_trauma_engine_builds_next_engine_payloads():
    engine = TraumaHealingEngine()

    result = engine.run(
        {
            "character_seed": sample_seed(),
            "psychology_profile": sample_psychology(),
            "origin_profile": sample_origin(),
            "family_profile": sample_family(),
        }
    )

    payload = result.data["next_engine_payload"]

    assert "character_seed" in payload
    assert "emotion_engine_payload" in payload
    assert "emotional_arc_engine_payload" in payload
    assert "memory_engine_payload" in payload
    assert len(payload["character_seed"]["trauma_records"]) >= 3
    assert payload["emotion_engine_payload"]["healing_profile"]["character_id"] == "char_kael"


def test_trauma_engine_warns_without_character_seed():
    engine = TraumaHealingEngine()

    result = engine.run({})

    assert result.success is True
    assert len(result.warnings) == 1
    assert "character_seed" in result.warnings[0]
    assert result.data["trauma_summary"]["trauma_count"] >= 1

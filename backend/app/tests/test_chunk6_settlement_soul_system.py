from backend.app.engines.deep_world.settlement_engine import SettlementEngine
from backend.app.engines.deep_world.settlement_soul_system import SettlementSoulSystem


def build_settlement():
    engine = SettlementEngine()
    return engine.build_settlement(source_id="soul_settlement_source")["settlement"]


def test_settlement_soul_system_builds_soul():
    settlement = build_settlement()
    system = SettlementSoulSystem()

    soul = system.build_settlement_soul(
        source_id="soul_test",
        settlement=settlement,
    )["settlement_soul"]

    assert soul["settlement_id"] == settlement["settlement_id"]
    assert soul["settlement_name"] == settlement["unique_name"]
    assert soul["emotional_identity"]
    assert soul["civic_wound"]
    assert soul["daily_rhythm"]
    assert soul["hospitality_rules"]
    assert soul["taboo_behaviors"]
    assert soul["festival_calendar"]
    assert soul["sensory_signature"]
    assert soul["scene_behavior_rules"]
    assert soul["detail_depth_score"] >= 0.75


def test_settlement_soul_system_builds_shift_event():
    settlement = build_settlement()
    system = SettlementSoulSystem()
    soul = system.build_settlement_soul(source_id="shift_test", settlement=settlement)["settlement_soul"]

    shift = system.build_soul_shift_event(
        source_id="shift_test",
        settlement_soul=soul,
        shift_seed={
            "shift_name": "Foglamp Public Vigil",
            "trigger": "no-bell children lit every foglamp before curfew",
        },
    )["settlement_soul_shift"]

    assert shift["settlement_soul_id"] == soul["settlement_soul_id"]
    assert shift["shift_name"] == "Foglamp Public Vigil"
    assert shift["trigger"] == "no-bell children lit every foglamp before curfew"
    assert shift["public_interpretation"]
    assert shift["private_interpretation"]
    assert shift["mood_change"]
    assert shift["behavior_change"]
    assert shift["memory_effect"]


def test_settlement_soul_system_builds_story_context_patch():
    settlement = build_settlement()
    system = SettlementSoulSystem()
    soul = system.build_settlement_soul(source_id="patch_test", settlement=settlement)["settlement_soul"]
    shift = system.build_soul_shift_event(source_id="patch_test", settlement_soul=soul)["settlement_soul_shift"]

    patch = system.build_story_context_patch(
        settlement_soul=soul,
        soul_shift=shift,
    )["story_context_patch"]

    assert patch["settlement_soul_id"] == soul["settlement_soul_id"]
    assert patch["active_settlement_soul_shift"]["settlement_soul_shift_id"] == shift["settlement_soul_shift_id"]
    assert "generation_hints" in patch
    assert "memory_update_candidates" in patch
    assert len(patch["memory_update_candidates"]) == 2


def test_settlement_soul_system_validates_soul_and_shift():
    settlement = build_settlement()
    system = SettlementSoulSystem()
    soul = system.build_settlement_soul(source_id="validate_test", settlement=settlement)["settlement_soul"]
    shift = system.build_soul_shift_event(source_id="validate_test", settlement_soul=soul)["settlement_soul_shift"]

    soul_validation = system.validate_settlement_soul(settlement_soul=soul)
    shift_validation = system.validate_soul_shift(soul_shift=shift)

    assert soul_validation["passed"] is True
    assert soul_validation["missing_fields"] == []
    assert shift_validation["passed"] is True
    assert shift_validation["missing_fields"] == []


def test_settlement_soul_system_detects_bad_records():
    system = SettlementSoulSystem()

    soul_validation = system.validate_settlement_soul(
        settlement_soul={
            "settlement_soul_id": "bad_soul",
            "settlement_name": "Generic Town",
            "story_use": "Bad.",
        }
    )

    shift_validation = system.validate_soul_shift(
        soul_shift={
            "settlement_soul_shift_id": "bad_shift",
            "shift_name": "Mood",
            "plot_effect": "Bad.",
        }
    )

    assert soul_validation["passed"] is False
    assert soul_validation["missing_fields"]
    assert "story_use" in soul_validation["shallow_fields"]

    assert shift_validation["passed"] is False
    assert shift_validation["missing_fields"]
    assert "plot_effect" in shift_validation["shallow_fields"]


def test_settlement_soul_system_summarizes_and_textualizes():
    settlement = build_settlement()
    system = SettlementSoulSystem()
    soul = system.build_settlement_soul(source_id="text_test", settlement=settlement)["settlement_soul"]
    shift = system.build_soul_shift_event(source_id="text_test", settlement_soul=soul)["settlement_soul_shift"]

    summary = system.summarize_settlement_soul(settlement_soul=soul, soul_shift=shift)
    text = system.build_settlement_soul_text(settlement_soul=soul, soul_shift=shift)["settlement_soul_text"]

    assert summary["success"] is True
    assert summary["summary"]["settlement_soul_id"] == soul["settlement_soul_id"]
    assert "Settlement Soul Profile" in text
    assert "Civic Wound" in text
    assert "Memory Effect" in text

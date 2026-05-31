from backend.app.services.character_agency_state_updater import CharacterAgencyStateUpdater
from backend.app.services.character_consistency_invariant_checker import CharacterConsistencyInvariantChecker
from backend.app.services.character_emotion_carryover_adapter import CharacterEmotionCarryoverAdapter
from backend.app.services.character_memory_update_adapter import CharacterMemoryUpdateAdapter
from backend.app.services.character_state_snapshot_store import CharacterStateSnapshotStore


def sample_character_profile():
    return {
        "character_id": "char_kael",
        "identity": {"character_id": "char_kael", "name": "Kael Veyran"},
        "psychology": {
            "psychology_profile": {
                "core_wound": "believes belonging can be revoked after public failure",
            },
            "memory_records": [{"memory_id": "mem_core", "content": "public failure"}],
        },
        "power": {
            "skill_ontology": {"skill_family": "cognitive_inference"},
            "adaptability_profile": {"cost_model": "identity instability after breakthrough"},
        },
        "dialogue": {
            "dialogue_voice_profile": {
                "voice_family": "controlled_subtext_voice",
            }
        },
        "relationships": {
            "relationship_readiness_profile": {
                "relationship_readiness_family": "high_loyalty_power_broker_readiness",
            }
        },
    }


def test_character_state_snapshot_store_creates_and_fetches_snapshot(tmp_path):
    store = CharacterStateSnapshotStore(root=tmp_path / "character_snapshots")

    state = {
        "character_id": "char_kael",
        "current_emotion_state": {"dominant_emotion": "controlled_pressure"},
        "current_memory_state": {"active_memory_ids": ["mem_core"]},
    }

    result = store.create_snapshot(
        character_id="char_kael",
        character_state=state,
        project_id="proj_ashen",
        universe_id="velmora",
        tick_number=2,
    )

    fetched = store.get_snapshot(result["snapshot_id"])
    latest = store.latest_snapshot("char_kael")

    assert result["success"] is True
    assert result["state_hash"]
    assert fetched["character_id"] == "char_kael"
    assert latest["snapshot_id"] == result["snapshot_id"]


def test_character_memory_update_adapter_builds_and_applies_memory():
    adapter = CharacterMemoryUpdateAdapter()

    update = adapter.build_memory_update(
        character_id="char_kael",
        event_payload={
            "event_id": "evt_public_humiliation",
            "event_type": "public_humiliation",
            "description": "Kael is humiliated during the public ranking ceremony.",
        },
        intensity=0.86,
    )

    applied = adapter.apply_memory_update(
        character_state={"character_id": "char_kael", "memory_records": []},
        memory_update=update,
    )

    assert update["success"] is True
    assert update["should_persist"] is True
    assert update["memory_record"]["memory_type"] == "wound_activation_memory"
    assert "shame" in update["memory_record"]["emotional_tags"]
    assert applied["updated_character_state"]["memory_records"]
    assert applied["added_memory_id"].startswith("mem_")


def test_character_emotion_carryover_adapter_updates_and_decays_emotion():
    adapter = CharacterEmotionCarryoverAdapter()

    update = adapter.build_emotion_update(
        character_id="char_kael",
        event_payload={"event_type": "public_humiliation"},
        current_emotion_state={"emotion_vector": {"hope": 0.2}},
        intensity=0.8,
    )

    decayed = adapter.decay_emotions(update["emotion_update"], ticks=1)

    assert update["success"] is True
    assert update["emotion_update"]["dominant_emotion"] == "shame"
    assert update["emotion_update"]["triggered_wound"] == "belonging can be revoked publicly"
    assert decayed["decayed_emotion_state"]["emotion_intensity"] < update["emotion_update"]["emotion_intensity"]


def test_character_agency_state_updater_outputs_available_and_blocked_actions():
    updater = CharacterAgencyStateUpdater()

    result = updater.update_agency_state(
        character_id="char_kael",
        event_payload={"event_type": "blackmail_attempt"},
        emotion_state={"emotion_vector": {"fear": 0.4, "dread": 0.3}},
        knowledge_state={"known_secret_ids": ["secret_1"], "evidence_seen_ids": ["ev_1"]},
        relationship_state={"betrayal_risk": 0.2},
        world_constraints={"legal_constraints": ["distrusted names need sponsor"]},
    )

    state = result["agency_state"]

    assert result["success"] is True
    assert "negotiate_terms" in state["available_actions"]
    assert "search_for_counter_leverage" in state["available_actions"]
    assert state["blocked_actions"]
    assert 0.0 <= state["agency_capacity"] <= 1.0


def test_character_consistency_checker_blocks_betrayal_without_trigger():
    checker = CharacterConsistencyInvariantChecker()

    report = checker.check_update(
        character_profile=sample_character_profile(),
        proposed_update={"action": "betray closest ally"},
        event_context={"event_type": "conversation", "intensity": 0.2},
    )

    assert report["success"] is True
    assert report["consistent"] is False
    assert "betrayal proposed without sufficient trigger, leverage, fear, or moral pressure" in report["violations"]


def test_character_consistency_checker_blocks_skill_cost_violation():
    checker = CharacterConsistencyInvariantChecker()

    report = checker.check_update(
        character_profile=sample_character_profile(),
        proposed_update={"uses_skill": True, "skill_used": "Pattern Reading"},
        event_context={"event_type": "trial", "intensity": 0.7},
    )

    assert report["consistent"] is False
    assert "skill/power use ignores established cost model" in report["violations"]


def test_character_consistency_checker_accepts_pressured_betrayal_with_cost():
    checker = CharacterConsistencyInvariantChecker()

    report = checker.check_update(
        character_profile=sample_character_profile(),
        proposed_update={
            "action": "betray closest ally under blackmail",
            "uses_skill": True,
            "skill_cost_paid": True,
        },
        event_context={
            "event_type": "blackmail_attempt",
            "intensity": 0.9,
            "blackmail_active": True,
            "fear_pressure": 0.85,
        },
    )

    assert report["success"] is True
    assert report["consistent"] is True
    assert report["violations"] == []

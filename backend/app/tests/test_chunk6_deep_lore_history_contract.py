from backend.app.engines.deep_world.deep_lore_history_contract import DeepLoreHistoryContractBuilder
from backend.app.schemas.deep_world import DeepLoreContract, HistoricalMemoryRecord


def test_deep_lore_contract_includes_public_secret_false_history():
    builder = DeepLoreHistoryContractBuilder()
    contract = builder.build_lore_contract(source_id="lore_contract_test")["deep_lore_contract"]

    assert isinstance(contract, DeepLoreContract)
    assert "public_history" in contract.required_lore_categories
    assert "secret_history" in contract.required_lore_categories
    assert "false_history" in contract.required_lore_categories
    assert "what_happened_here_before" in contract.required_questions
    assert contract.require_memory_state_updates is True


def test_deep_lore_builds_historical_memory_record():
    builder = DeepLoreHistoryContractBuilder()

    record = builder.build_historical_memory_record(
        source_id="lore_record_test",
        event_seed={
            "event_name": "The Glass Treaty Betrayal",
            "era_name": "Red Tide Era",
            "event_type": "political_betrayal",
        },
    )["historical_memory_record"]

    assert isinstance(record, HistoricalMemoryRecord)
    assert record.event_name == "The Glass Treaty Betrayal"
    assert record.public_version
    assert record.secret_version
    assert record.false_version
    assert record.physical_evidence
    assert record.character_trauma_hooks
    assert record.plot_conflict_hooks
    assert record.memory_state_updates


def test_deep_lore_validates_historical_memory_record():
    builder = DeepLoreHistoryContractBuilder()
    record = builder.build_historical_memory_record(source_id="lore_validate_test")["historical_memory_record"]

    validation = builder.validate_historical_record(record=record)

    assert validation["passed"] is True
    assert validation["blockers"] == []


def test_deep_lore_context_patch_links_lore_to_story_generation():
    builder = DeepLoreHistoryContractBuilder()
    record = builder.build_historical_memory_record(source_id="lore_patch_test")["historical_memory_record"]

    patch = builder.build_story_context_patch(record=record)["story_context_patch"]

    assert patch["historical_record_id"] == record.historical_record_id
    assert "public_version" in patch
    assert "secret_version" in patch
    assert "physical_evidence" in patch
    assert "generation_hints" in patch


def test_deep_lore_summarizes_historical_record():
    builder = DeepLoreHistoryContractBuilder()
    record = builder.build_historical_memory_record(source_id="lore_summary_test")["historical_memory_record"]

    summary = builder.summarize_historical_record(record=record)

    assert summary["success"] is True
    assert summary["summary"]["historical_record_id"] == record.historical_record_id
    assert summary["summary"]["evidence_count"] >= 1

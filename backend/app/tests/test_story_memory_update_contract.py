from backend.app.engines.story_generation.story_memory_update_contract import StoryMemoryUpdateContractBuilder
from backend.app.schemas.story_generation import GeneratedStoryDeltaReport, StoryProvenanceRecord


def build_delta_report():
    return GeneratedStoryDeltaReport(
        delta_report_id="delta_memory",
        source_id="memory_source",
        draft_id="draft_memory",
        character_deltas=[
            {"delta_id": "character_delta_char_kael", "delta_type": "character", "target_id": "char_kael", "value": "char_kael", "delta_action": "mentioned_or_preserved"}
        ],
        relationship_deltas=[
            {"delta_id": "relationship_delta_rel_kael_seren", "delta_type": "relationship", "target_id": "rel_kael_seren", "value": "rel_kael_seren", "delta_action": "mentioned_or_preserved"}
        ],
        secret_deltas=[
            {"delta_id": "secret_delta_secret_seren_source", "delta_type": "secret", "target_id": "secret_seren_source", "value": "secret_seren_source", "delta_action": "reveal_or_pressure"}
        ],
        causal_deltas=[
            {"delta_id": "causal_delta_cause_trial_reveal", "delta_type": "causal", "target_id": "cause_trial_reveal", "value": "cause_trial_reveal", "delta_action": "causal_progression"}
        ],
        world_deltas=[
            {"delta_id": "world_delta_oath_court", "delta_type": "world_detail", "target_id": "Oath Court", "value": "Oath Court", "delta_action": "mentioned_or_preserved"}
        ],
        object_deltas=[
            {"delta_id": "object_delta_cracked_badge", "delta_type": "object", "target_id": "cracked badge", "value": "cracked badge", "delta_action": "mentioned_or_preserved"}
        ],
        open_loop_deltas=[
            {"delta_id": "open_loop_delta_secret", "delta_type": "open_loop", "target_id": "open_loop_secret", "value": "open_loop_secret", "delta_action": "mentioned_or_preserved"}
        ],
        resolved_loop_deltas=[
            {"delta_id": "resolved_loop_open_loop_trial", "delta_type": "resolved_loop", "target_id": "open_loop_trial", "value": "open_loop_trial", "delta_action": "resolved"}
        ],
        memory_update_candidates=[
            {"candidate_id": "memory_candidate_extra", "candidate_type": "world_state", "value": "storm season", "delta_action": "candidate"}
        ],
    )


def build_provenance(approved=True):
    return StoryProvenanceRecord(
        provenance_id="provenance_memory",
        provenance_record_id="provenance_memory",
        source_id="memory_source",
        draft_id="draft_memory",
        approved_for_memory_update=approved,
        approved_for_export=approved,
        protected_elements_snapshot=[
            {"element_id": "protect_character_char_kael", "element_type": "character", "value": "char_kael"},
            {"element_id": "protect_secret_secret_seren_source", "element_type": "secret", "value": "secret_seren_source"},
            {"element_id": "protect_world_oath_court", "element_type": "world_detail", "value": "Oath Court"},
        ],
    )


def test_story_memory_update_contract_builds_auto_apply_contract():
    builder = StoryMemoryUpdateContractBuilder()

    result = builder.build_memory_update_contract(
        source_id="memory_source",
        draft_id="draft_memory",
        delta_report=build_delta_report(),
        provenance_record=build_provenance(approved=True),
    )

    contract = result["story_memory_update_contract"]

    assert result["success"] is True
    assert contract.memory_contract_id == "story_memory_contract_memory_source_draft_memory"
    assert contract.approved_for_apply is True
    assert contract.apply_mode == "auto_apply"
    assert contract.character_state_updates
    assert contract.secret_state_updates
    assert contract.causal_state_updates
    assert contract.world_state_updates
    assert contract.object_state_updates
    assert contract.open_loop_updates
    assert contract.resolved_loop_updates
    assert contract.rollback_plan
    assert contract.downstream_constraints


def test_story_memory_update_contract_blocks_unapproved_provenance():
    builder = StoryMemoryUpdateContractBuilder()

    contract = builder.build_memory_update_contract(
        source_id="memory_source",
        draft_id="draft_memory",
        delta_report=build_delta_report(),
        provenance_record=build_provenance(approved=False),
    )["story_memory_update_contract"]

    assert contract.approved_for_apply is False
    assert contract.apply_mode == "blocked"
    assert contract.blocked_updates
    assert any("not approved" in warning for warning in contract.warnings)


def test_story_memory_update_contract_requires_review_on_existing_conflict():
    builder = StoryMemoryUpdateContractBuilder()

    contract = builder.build_memory_update_contract(
        source_id="memory_source",
        draft_id="draft_memory",
        delta_report=build_delta_report(),
        provenance_record=build_provenance(approved=True),
        existing_memory_state={
            "world_state": {"Oath Court": "Old Oath Court state"}
        },
    )["story_memory_update_contract"]

    assert contract.approved_for_apply is False
    assert contract.apply_mode == "manual_review"
    assert contract.review_required_updates
    assert contract.conflict_checks


def test_story_memory_update_contract_validates_contract():
    builder = StoryMemoryUpdateContractBuilder()

    contract = builder.build_memory_update_contract(
        source_id="memory_source",
        draft_id="draft_memory",
        delta_report=build_delta_report(),
        provenance_record=build_provenance(approved=True),
    )["story_memory_update_contract"]

    validation = builder.validate_memory_update_contract(contract=contract)

    assert validation["success"] is True
    assert validation["valid"] is True
    assert "memory_contract_id_present" in validation["passed_checks"]
    assert "memory_apply_summary_present" in validation["passed_checks"]


def test_story_memory_update_contract_summarizes_contract():
    builder = StoryMemoryUpdateContractBuilder()

    contract = builder.build_memory_update_contract(
        source_id="memory_source",
        draft_id="draft_memory",
        delta_report=build_delta_report(),
        provenance_record=build_provenance(approved=True),
    )["story_memory_update_contract"]

    summary = builder.summarize_memory_update_contract(contract=contract)

    assert summary["success"] is True
    assert summary["summary"]["source_id"] == "memory_source"
    assert "memory_update_count" in summary["summary"]


def test_story_memory_update_contract_builds_text():
    builder = StoryMemoryUpdateContractBuilder()

    contract = builder.build_memory_update_contract(
        source_id="memory_source",
        draft_id="draft_memory",
        delta_report=build_delta_report(),
        provenance_record=build_provenance(approved=True),
    )["story_memory_update_contract"]

    text = builder.build_memory_contract_text(contract=contract)["memory_contract_text"]

    assert "Story Memory Update Contract" in text
    assert "Memory Apply Summary" in text
    assert "Staged Updates" in text


from backend.app.engines.deep_world.deep_world_design_contract import DeepWorldDesignContractBuilder
from backend.app.schemas.deep_world import Chunk6DeepWorldDesignContract


def test_design_contract_builder_builds_approved_contract():
    builder = DeepWorldDesignContractBuilder()

    contract = builder.build_contract(
        source_id="chunk6_design_test",
        story_context={"project_id": "mythos", "world_seed": "saltroot"},
    )["chunk6_deep_world_design_contract"]

    assert isinstance(contract, Chunk6DeepWorldDesignContract)
    assert contract.approved_for_implementation is True
    assert contract.total_locked_steps == 55
    assert "story_use" in contract.required_output_fields
    assert "ChunkFutureCompatibilityContract" in contract.bridge_contracts
    assert contract.warnings == []


def test_design_contract_warns_without_seed_context():
    builder = DeepWorldDesignContractBuilder()

    contract = builder.build_contract(
        source_id="chunk6_design_test",
        story_context={},
    )["chunk6_deep_world_design_contract"]

    assert len(contract.warnings) >= 1
    assert any("world_seed" in warning for warning in contract.warnings)


def test_design_contract_validation_passes():
    builder = DeepWorldDesignContractBuilder()
    contract = builder.build_contract(
        source_id="chunk6_design_test",
        story_context={"project_id": "mythos", "world_seed": "saltroot"},
    )["chunk6_deep_world_design_contract"]

    validation = builder.validate_contract(contract=contract)

    assert validation["passed"] is True
    assert validation["bridge_contracts_ok"] is True
    assert validation["missing_required_output_fields"] == []


def test_design_contract_summary_and_text():
    builder = DeepWorldDesignContractBuilder()
    contract = builder.build_contract(
        source_id="chunk6_design_test",
        story_context={"project_id": "mythos", "world_seed": "saltroot"},
    )["chunk6_deep_world_design_contract"]

    summary = builder.summarize_contract(contract=contract)
    text = builder.build_contract_text(contract=contract)["contract_text"]

    assert summary["success"] is True
    assert summary["summary"]["total_locked_steps"] == 55
    assert "Chunk 6 Deep World Design Contract" in text
    assert "Required Output Fields" in text
    assert "StoryWorldExpansionBridge" in text

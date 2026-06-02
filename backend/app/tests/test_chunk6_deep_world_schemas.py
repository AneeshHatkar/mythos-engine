
from backend.app.schemas.deep_world import (
    Chunk6DeepWorldDesignContract,
    DeepWorldElementType,
    DeepWorldRegion,
    DeepWorldSettlement,
    DeepWorldValidationReport,
)


def test_deep_world_region_requires_story_use_contract():
    region = DeepWorldRegion(
        element_id="region_salt_forest",
        source_id="chunk6_test",
        name="Saltroot Forest",
        summary="A silver-fog forest where salt-root trees preserve memory in bark.",
        story_use="Creates travel danger, memory clues, and ritual material.",
        character_effect="Characters raised nearby fear fog and speak in memory metaphors.",
        plot_effect="Fog season closes routes and delays a rescue.",
        memory_effect="Region state stores fog closures and memory sickness risk.",
        compression_summary="Memory-preserving forest with dangerous fog routes.",
        terrain_signature=["salt-root trees", "silver fog", "hidden ravines"],
        climate_signature=["wet fog season", "dry salt wind"],
        visual_signature=["white bark", "silver mist"],
        emotional_signature=["wonder", "dread"],
        danger_signature=["memory sickness"],
        secret_signature=["buried oath road"],
    )

    assert region.element_type == DeepWorldElementType.REGION
    assert "memory" in region.summary.lower()
    assert region.story_use
    assert region.character_effect
    assert region.plot_effect
    assert region.memory_effect
    assert region.compression_summary


def test_deep_world_settlement_has_reason_resources_and_soul():
    settlement = DeepWorldSettlement(
        element_id="settlement_oath_bell",
        source_id="chunk6_test",
        name="Oath Bell Village",
        summary="A village built around bells that guide travelers through fog.",
        story_use="Functions as a rescue waypoint and secret-keeper settlement.",
        character_effect="Locals value silence, bells, and oath memory.",
        plot_effect="The village can hide a fugitive or expose them through bell law.",
        memory_effect="Stores who rang the forbidden bell and when.",
        compression_summary="Fog village with bells, oath law, and hidden fugitives.",
        settlement_type="village",
        reason_for_location="Built beside the only stable path through Saltroot Forest.",
        sustaining_resources=["salt bark", "bell metal trade", "fog herbs"],
        controlling_powers=["Bell Council"],
        suffering_groups=["route orphans"],
        hidden_secrets=["buried oath road entrance"],
        threats=["fog sickness", "road raiders"],
        settlement_soul={
            "smell": "salt bark smoke",
            "children_are_taught": "never ring a bell without witness",
            "outsiders_misunderstand": "silence is respect, not hostility",
        },
    )

    assert settlement.reason_for_location
    assert settlement.sustaining_resources
    assert settlement.settlement_soul["smell"] == "salt bark smoke"


def test_deep_world_validation_report_scores_are_bounded():
    report = DeepWorldValidationReport(
        validation_report_id="validation_chunk6_test",
        source_id="chunk6_test",
        passed=True,
        specificity_score=0.91,
        consistency_score=0.88,
        novelty_score=0.84,
        story_usefulness_score=0.9,
        emotional_resonance_score=0.86,
    )

    assert report.passed is True
    assert report.specificity_score >= 0.9


def test_chunk6_design_contract_schema_locks_55_steps_and_connections():
    contract = Chunk6DeepWorldDesignContract(
        contract_id="contract_chunk6_test",
        source_id="chunk6_test",
        approved_for_implementation=True,
    )

    assert contract.chunk_number == 6
    assert contract.total_locked_steps == 55
    assert "StoryWorldExpansionBridge" in contract.bridge_contracts
    assert "chunk_5_story_generation_pipeline" in contract.backward_connections
    assert "chunk_9_ml_data_research_deployment" in contract.forward_connections
    assert "story_use" in contract.required_output_fields

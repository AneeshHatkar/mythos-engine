from backend.app.engines.deep_world.generated_identity_contract import GeneratedIdentityContractBuilder
from backend.app.schemas.deep_world import DetailDepthContract, GeneratedNameProfile


def test_generated_identity_builds_original_people_name_profile():
    builder = GeneratedIdentityContractBuilder()

    profile = builder.build_name_profile(
        source_id="identity_contract_test",
        generated_for_type="person",
        base_name="kael",
        culture_context={
            "culture": "Bellmarch witness families",
            "region": "Saltroot Forest",
            "name_meaning": "one who returns through fog",
            "related_place_or_family": "Veyrann witness line",
        },
    )["generated_name_profile"]

    assert isinstance(profile, GeneratedNameProfile)
    assert profile.unique_name == "Kael Veyrann"
    assert "Bellmarch" in profile.cultural_context
    assert "fog" in profile.name_meaning
    assert profile.detail_depth_score >= 0.75
    assert profile.name_origin
    assert profile.name_language_logic
    assert profile.anti_genericity_signal


def test_generated_identity_contract_applies_to_everything():
    builder = GeneratedIdentityContractBuilder()
    contract = builder.build_detail_depth_contract(source_id="depth_contract_test")["detail_depth_contract"]

    assert isinstance(contract, DetailDepthContract)
    assert "people" in contract.applies_to_types
    assert "countries" in contract.applies_to_types
    assert "flora" in contract.applies_to_types
    assert "fauna" in contract.applies_to_types
    assert "species" in contract.applies_to_types
    assert "artifacts" in contract.applies_to_types
    assert "unique_name" in contract.required_identity_fields
    assert contract.no_one_liner_rule is True


def test_generated_identity_evaluates_detailed_payload():
    builder = GeneratedIdentityContractBuilder()

    payload = {
        "unique_name": "Velmarin Ashbloom",
        "name_origin": "Named from ashfall mourning dialect.",
        "name_meaning": "grief-light flower after volcanic ash.",
        "name_language_logic": "compound grief-root plus bloom suffix.",
        "cultural_context": "Used by ashfall families in funeral tea and poison trials.",
        "world_context": "Grows near old volcanic funeral terraces.",
        "visual_identity": "black stem, pale blue petals, ash-dusted leaves.",
        "sensory_identity": "smells like rain on cold stone.",
        "social_function": "Marks mourning status and family grief.",
        "economic_function": "Sold by licensed funeral herbalists.",
        "belief_function": "Used to ask ancestors whether a death was clean.",
        "story_use": "Can reveal poison because petals darken near certain toxins.",
        "character_effect": "Characters from ashfall regions associate its smell with funerals and childhood loss.",
        "plot_effect": "A missing harvest can expose a poisoning conspiracy.",
        "memory_effect": "Burning fields affects future medicine, rituals, trade, and grief customs.",
        "validation_status": "validated",
        "provenance": {"test": True},
        "anti_genericity_signal": "Specific to ashfall death rites and poison evidence.",
        "detail_depth_score": 0.92,
        "compression_summary": "Funeral flower tied to poison, grief, and ashfall culture.",
        "lore_connection": "First bloomed after the Black Terrace eruption.",
    }

    report = builder.evaluate_generated_element(
        source_id="depth_eval_test",
        target_element_id="flora_velmarin_ashbloom",
        target_element_type="flora",
        element_payload=payload,
    )["generated_element_depth_report"]

    assert report.passed is True
    assert report.missing_fields == []
    assert report.detail_depth_score >= 0.75


def test_generated_identity_detects_one_liner_bullshit():
    builder = GeneratedIdentityContractBuilder()

    payload = {
        "unique_name": "Moonflower",
        "story_use": "Pretty flower.",
    }

    report = builder.evaluate_generated_element(
        source_id="depth_bad_test",
        target_element_id="flora_moonflower",
        target_element_type="flora",
        element_payload=payload,
    )["generated_element_depth_report"]

    assert report.passed is False
    assert report.missing_fields
    assert report.repair_actions


def test_generated_identity_validates_and_summarizes_name_profile():
    builder = GeneratedIdentityContractBuilder()
    profile = builder.build_name_profile(
        source_id="identity_summary_test",
        generated_for_type="country",
        base_name="Avar",
    )["generated_name_profile"]

    validation = builder.validate_name_profile(profile=profile)
    summary = builder.summarize_name_profile(profile=profile)

    assert validation["passed"] is True
    assert summary["success"] is True
    assert summary["summary"]["unique_name"] == profile.unique_name

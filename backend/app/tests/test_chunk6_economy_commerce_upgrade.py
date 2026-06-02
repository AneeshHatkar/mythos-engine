from backend.app.engines.deep_world.economy_resource_ecology_engine import (
    CommerceMarketsUpgrade,
    EconomyResourceEcologyEngine,
)


def build_economy():
    economy_engine = EconomyResourceEcologyEngine()
    return economy_engine.build_resource_economy_profile(source_id="commerce_context")["resource_economy_profile"]


def test_commerce_upgrade_builds_commerce_system():
    economy = build_economy()
    commerce = CommerceMarketsUpgrade()

    system = commerce.build_commerce_system(
        source_id="commerce_test",
        resource_economy_profile=economy,
        commerce_seed={
            "commerce_name": "Ashglass Tide-Market Commerce",
            "region_name": "Ashglass Coast",
        },
    )["commerce_system"]

    assert system["commerce_name"] == "Ashglass Tide-Market Commerce"
    assert system["region_name"] == "Ashglass Coast"
    assert system["resource_economy_profile_id"] == economy["resource_economy_profile_id"]
    assert system["markets_and_shops"]
    assert system["merchant_houses"]
    assert system["currency_and_payment"]
    assert system["credit_debt_and_banking"]
    assert system["contracts_and_law"]
    assert system["insurance_and_risk"]
    assert system["luxury_and_counterfeit_goods"]
    assert system["market_shock_rules"]
    assert system["detail_depth_score"] >= 0.75


def test_commerce_upgrade_builds_commercial_event():
    economy = build_economy()
    commerce = CommerceMarketsUpgrade()
    system = commerce.build_commerce_system(
        source_id="commercial_event_test",
        resource_economy_profile=economy,
    )["commerce_system"]

    event = commerce.build_commercial_event(
        source_id="commercial_event_test",
        commerce_system=system,
        event_seed={
            "event_name": "Nine-Bell Contract Panic",
            "trigger": "a merchant ledger showed three contracts using the same false family seal",
        },
    )["commercial_event"]

    assert event["commerce_system_id"] == system["commerce_system_id"]
    assert event["event_name"] == "Nine-Bell Contract Panic"
    assert event["trigger"] == "a merchant ledger showed three contracts using the same false family seal"
    assert event["affected_markets"]
    assert event["affected_groups"]
    assert event["commercial_consequence"]
    assert event["legal_consequence"]
    assert event["memory_effect"]


def test_commerce_upgrade_builds_story_context_patch():
    economy = build_economy()
    commerce = CommerceMarketsUpgrade()
    system = commerce.build_commerce_system(source_id="commerce_patch_test", resource_economy_profile=economy)[
        "commerce_system"
    ]
    event = commerce.build_commercial_event(source_id="commerce_patch_test", commerce_system=system)["commercial_event"]

    patch = commerce.build_commerce_story_context_patch(commerce_system=system, commercial_event=event)[
        "story_context_patch"
    ]

    assert patch["commerce_system_id"] == system["commerce_system_id"]
    assert patch["active_commercial_event"]["commercial_event_id"] == event["commercial_event_id"]
    assert "generation_hints" in patch
    assert "memory_update_candidates" in patch
    assert len(patch["memory_update_candidates"]) == 2


def test_commerce_upgrade_validates_system_and_event():
    economy = build_economy()
    commerce = CommerceMarketsUpgrade()
    system = commerce.build_commerce_system(source_id="commerce_validate_test", resource_economy_profile=economy)[
        "commerce_system"
    ]
    event = commerce.build_commercial_event(source_id="commerce_validate_test", commerce_system=system)[
        "commercial_event"
    ]

    system_validation = commerce.validate_commerce_system(commerce_system=system)
    event_validation = commerce.validate_commercial_event(commercial_event=event)

    assert system_validation["passed"] is True
    assert system_validation["missing_fields"] == []
    assert event_validation["passed"] is True
    assert event_validation["missing_fields"] == []


def test_commerce_upgrade_detects_bad_records():
    commerce = CommerceMarketsUpgrade()

    system_validation = commerce.validate_commerce_system(
        commerce_system={
            "commerce_system_id": "bad_commerce",
            "commerce_name": "Generic Market",
            "story_use": "Bad.",
        }
    )

    event_validation = commerce.validate_commercial_event(
        commercial_event={
            "commercial_event_id": "bad_event",
            "event_name": "Sale",
            "plot_effect": "Bad.",
        }
    )

    assert system_validation["passed"] is False
    assert system_validation["missing_fields"]
    assert "story_use" in system_validation["shallow_fields"]

    assert event_validation["passed"] is False
    assert event_validation["missing_fields"]
    assert "plot_effect" in event_validation["shallow_fields"]


def test_commerce_upgrade_summarizes_and_textualizes():
    economy = build_economy()
    commerce = CommerceMarketsUpgrade()
    system = commerce.build_commerce_system(source_id="commerce_text_test", resource_economy_profile=economy)[
        "commerce_system"
    ]
    event = commerce.build_commercial_event(source_id="commerce_text_test", commerce_system=system)["commercial_event"]

    summary = commerce.summarize_commerce_system(commerce_system=system, commercial_event=event)
    text = commerce.build_commerce_text(commerce_system=system, commercial_event=event)["commerce_text"]

    assert summary["success"] is True
    assert summary["summary"]["commerce_system_id"] == system["commerce_system_id"]
    assert "Commerce, Markets, Currency, Contracts, and Merchant Systems Profile" in text
    assert "Merchant Houses" in text
    assert "Memory Effect" in text

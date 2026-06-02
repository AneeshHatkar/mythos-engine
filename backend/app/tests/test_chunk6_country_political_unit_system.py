from backend.app.engines.deep_world.country_political_unit_system import CountryPoliticalUnitSystem


def test_country_political_unit_system_builds_political_unit():
    system = CountryPoliticalUnitSystem()

    unit = system.build_political_unit(
        source_id="political_unit_test",
        political_seed={
            "base_name": "Mirel",
            "unique_name": "The Tideglass Compact of Mirel",
            "political_unit_type": "coastal city-state compact",
            "government_type": "tide-court republic",
            "region_name": "Ashglass Coast",
            "culture": "drowned temple tide culture",
        },
        story_context={"genre": "fantasy", "tone": "political"},
    )["political_unit"]

    assert unit["unique_name"] == "The Tideglass Compact of Mirel"
    assert unit["political_unit_type"] == "coastal city-state compact"
    assert unit["government_type"] == "tide-court republic"
    assert unit["name_origin"]
    assert unit["government_structure"]
    assert unit["law_system"]
    assert unit["religion_myth_links"]
    assert unit["public_history"]
    assert unit["secret_history"]
    assert unit["false_history"]
    assert unit["detail_depth_score"] >= 0.75


def test_country_political_unit_system_builds_border_conflict():
    system = CountryPoliticalUnitSystem()
    unit = system.build_political_unit(source_id="border_test")["political_unit"]

    conflict = system.build_border_conflict(
        source_id="border_test",
        political_unit=unit,
        conflict_seed={
            "conflict_name": "Nine Roads Treaty Dispute",
            "conflict_type": "treaty_boundary_crisis",
        },
    )["border_conflict"]

    assert conflict["political_unit_id"] == unit["political_unit_id"]
    assert conflict["conflict_name"] == "Nine Roads Treaty Dispute"
    assert conflict["public_claim"]
    assert conflict["secret_truth"]
    assert conflict["false_claim"]
    assert conflict["affected_groups"]
    assert conflict["evidence"]
    assert conflict["memory_effect"]


def test_country_political_unit_system_builds_story_context_patch():
    system = CountryPoliticalUnitSystem()
    unit = system.build_political_unit(source_id="patch_test")["political_unit"]
    conflict = system.build_border_conflict(source_id="patch_test", political_unit=unit)["border_conflict"]

    patch = system.build_story_context_patch(
        political_unit=unit,
        border_conflict=conflict,
    )["story_context_patch"]

    assert patch["political_unit_id"] == unit["political_unit_id"]
    assert patch["active_border_conflict"]["border_conflict_id"] == conflict["border_conflict_id"]
    assert "generation_hints" in patch
    assert "memory_update_candidates" in patch
    assert len(patch["memory_update_candidates"]) == 2


def test_country_political_unit_system_validates_unit_and_conflict():
    system = CountryPoliticalUnitSystem()
    unit = system.build_political_unit(source_id="validate_test")["political_unit"]
    conflict = system.build_border_conflict(source_id="validate_test", political_unit=unit)["border_conflict"]

    unit_validation = system.validate_political_unit(political_unit=unit)
    conflict_validation = system.validate_border_conflict(border_conflict=conflict)

    assert unit_validation["passed"] is True
    assert unit_validation["missing_fields"] == []
    assert conflict_validation["passed"] is True
    assert conflict_validation["missing_fields"] == []


def test_country_political_unit_system_detects_bad_records():
    system = CountryPoliticalUnitSystem()

    unit_validation = system.validate_political_unit(
        political_unit={
            "political_unit_id": "bad_unit",
            "unique_name": "Generic Kingdom",
            "story_use": "Bad.",
        }
    )

    conflict_validation = system.validate_border_conflict(
        border_conflict={
            "border_conflict_id": "bad_conflict",
            "conflict_name": "War",
            "plot_effect": "Bad.",
        }
    )

    assert unit_validation["passed"] is False
    assert unit_validation["missing_fields"]
    assert "story_use" in unit_validation["shallow_fields"]

    assert conflict_validation["passed"] is False
    assert conflict_validation["missing_fields"]
    assert "plot_effect" in conflict_validation["shallow_fields"]


def test_country_political_unit_system_summarizes_and_textualizes():
    system = CountryPoliticalUnitSystem()
    unit = system.build_political_unit(source_id="text_test")["political_unit"]
    conflict = system.build_border_conflict(source_id="text_test", political_unit=unit)["border_conflict"]

    summary = system.summarize_political_unit(
        political_unit=unit,
        border_conflict=conflict,
    )
    text = system.build_political_unit_text(
        political_unit=unit,
        border_conflict=conflict,
    )["political_unit_text"]

    assert summary["success"] is True
    assert summary["summary"]["political_unit_id"] == unit["political_unit_id"]
    assert "Country / Political Unit Profile" in text
    assert "Secret History" in text
    assert "Memory Effect" in text

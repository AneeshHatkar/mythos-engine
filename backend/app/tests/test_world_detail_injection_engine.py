from backend.app.engines.story_generation.world_detail_injection_engine import WorldDetailInjectionEngine


def build_story_context():
    return {
        "story_context_id": "storyctx_test",
        "active_cast": [
            {
                "character_id": "char_kael",
                "display_name": "Kael",
                "current_location_id": "location_court",
            },
            {
                "character_id": "char_seren",
                "display_name": "Seren",
                "current_location_id": "location_court",
            },
        ],
        "world_rules": [
            {
                "rule_id": "rule_oath_court_proof",
                "description": "In the Oath Court, public proof changes legal rank.",
                "required": True,
            }
        ],
        "location_anchor": {
            "location_id": "location_court",
            "name": "Oath Court",
            "details": {
                "name": "Oath Court",
                "architecture": "black stone witness tiers",
            },
            "missing": False,
        },
        "format_requirements": {
            "selected_format": "novel",
            "format_contract": {"allows_internality": True},
        },
        "large_pool_summary": {
            "character_count": 2,
            "skill_count": 120,
            "power_count": 7,
            "artifact_count": 3,
            "faction_count": 1,
            "needs_scaling_controller": True,
        },
    }


def test_world_detail_engine_builds_detail_pack():
    engine = WorldDetailInjectionEngine()

    result = engine.build_world_detail_pack(story_context=build_story_context())
    pack = result["world_detail_pack"]

    assert result["success"] is True
    assert pack["world_detail_pack_id"] == "worlddetails_storyctx_test"
    assert pack["law_and_rule_anchors"]
    assert pack["location_anchors"]
    assert pack["ritual_anchors"]
    assert pack["skill_power_artifact_hooks"]
    assert pack["specificity_score"] >= 0.6


def test_world_detail_engine_builds_ritual_and_culture_anchors():
    engine = WorldDetailInjectionEngine()

    pack = engine.build_world_detail_pack(story_context=build_story_context())["world_detail_pack"]

    assert any(anchor["anchor_type"] == "ritual_or_ceremony" for anchor in pack["ritual_anchors"])
    assert any(anchor["anchor_type"] == "culture_marker" for anchor in pack["culture_anchors"])
    assert any("Oath Court" in hint for hint in pack["sensory_detail_hints"])


def test_world_detail_engine_links_characters_to_location():
    engine = WorldDetailInjectionEngine()

    pack = engine.build_world_detail_pack(story_context=build_story_context())["world_detail_pack"]
    links = pack["character_world_links"]

    assert len(links) == 2
    assert all(link["is_at_scene_location"] is True for link in links)
    assert links[0]["story_use"]


def test_world_detail_engine_validates_pack():
    engine = WorldDetailInjectionEngine()

    pack = engine.build_world_detail_pack(story_context=build_story_context())["world_detail_pack"]
    validation = engine.validate_world_detail_pack(world_detail_pack=pack)

    assert validation["success"] is True
    assert validation["valid"] is True
    assert "law_and_rule_anchors_present" in validation["passed_checks"]
    assert "location_anchors_present" in validation["passed_checks"]
    assert "specificity_score_usable" in validation["passed_checks"]


def test_world_detail_engine_builds_anti_generic_requirements():
    engine = WorldDetailInjectionEngine()

    pack = engine.build_world_detail_pack(story_context=build_story_context())["world_detail_pack"]
    result = engine.build_anti_generic_world_requirements(world_detail_pack=pack)

    assert result["success"] is True
    assert result["candidate_anchor_count"] >= 3
    assert any("world-specific rule" in requirement for requirement in result["requirements"])
    assert any("faction" in requirement.lower() for requirement in result["requirements"])


def test_world_detail_engine_injects_into_scene_seed():
    engine = WorldDetailInjectionEngine()

    story_context = build_story_context()
    pack = engine.build_world_detail_pack(story_context=story_context)["world_detail_pack"]
    result = engine.inject_into_scene_seed(
        story_context=story_context,
        world_detail_pack=pack,
        scene_seed={"scene_id": "scene_001"},
    )

    seed = result["scene_seed"]

    assert result["success"] is True
    assert seed["scene_id"] == "scene_001"
    assert seed["world_detail_pack_id"] == "worlddetails_storyctx_test"
    assert seed["required_world_anchors"]
    assert seed["anti_generic_world_requirements"]


def test_world_detail_engine_summarizes_pack():
    engine = WorldDetailInjectionEngine()

    pack = engine.build_world_detail_pack(story_context=build_story_context())["world_detail_pack"]
    summary = engine.summarize_world_detail_pack(world_detail_pack=pack)

    assert summary["success"] is True
    assert summary["summary"]["world_detail_pack_id"] == "worlddetails_storyctx_test"
    assert summary["summary"]["law_anchor_count"] >= 1
    assert summary["summary"]["location_anchor_count"] >= 1
    assert summary["summary"]["skill_power_artifact_hook_count"] >= 1


def test_world_detail_engine_warns_on_weak_world_context():
    engine = WorldDetailInjectionEngine()

    weak_context = {
        "story_context_id": "storyctx_weak",
        "active_cast": [],
        "world_rules": [],
        "location_anchor": {"missing": True},
        "format_requirements": {"selected_format": "scene"},
        "large_pool_summary": {},
    }

    pack = engine.build_world_detail_pack(story_context=weak_context)["world_detail_pack"]

    assert pack["specificity_score"] < 0.45
    assert any("specificity is low" in warning for warning in pack["warnings"])

from backend.app.engines.story_generation.scene_blueprint_engine import SceneBlueprintEngine


def build_story_context():
    return {
        "story_context_id": "storyctx_blueprint",
        "active_cast": [
            {
                "character_id": "char_kael",
                "display_name": "Kael",
                "required": True,
                "current_location_id": "location_court",
                "emotional_state": {"resolve": 0.8},
            },
            {
                "character_id": "char_seren",
                "display_name": "Seren",
                "required": False,
                "current_location_id": "location_court",
                "emotional_state": {"guilt": 0.8},
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
            "missing": False,
        },
        "relationship_pressure": [
            {
                "relationship_id": "rel_kael_seren",
                "trust": 0.3,
                "resentment": 0.5,
                "betrayal_risk": 0.7,
                "pressure_score": 0.7,
            }
        ],
        "knowledge_boundaries": [
            {
                "holder_id": "char_kael",
                "known_secret_ids": ["secret_rank_system"],
                "missing_required_secret_ids": ["secret_seren_source"],
                "forbidden_secret_reveals": ["major_mystery_solution_until_planned_reveal"],
            }
        ],
        "emotional_pressure": [
            {
                "character_id": "char_seren",
                "dominant_emotion": "guilt",
                "dominant_intensity": 0.8,
            }
        ],
        "causal_obligations": [
            {
                "obligation_type": "causal_node",
                "id": "cause_trial_reveal",
                "required": True,
            },
            {
                "obligation_type": "consequence",
                "id": "cons_reputation_shift",
                "required": True,
            },
        ],
        "readiness": {"ready_for_blueprint": True},
    }


def build_world_detail_pack():
    return {
        "world_detail_pack_id": "worlddetails_blueprint",
        "law_and_rule_anchors": [
            {
                "anchor_type": "world_rule",
                "detail": "In the Oath Court, public proof changes legal rank.",
            }
        ],
        "location_anchors": [
            {
                "anchor_type": "location",
                "detail": "Oath Court",
            },
            {
                "anchor_type": "location_architecture",
                "detail": "architecture: black stone witness tiers",
            },
        ],
        "faction_anchors": [
            {
                "anchor_type": "institutional_pressure",
                "detail": "The court watches every proof claim.",
            }
        ],
        "ritual_anchors": [
            {
                "anchor_type": "ritual_or_ceremony",
                "detail": "Proof must be spoken before the witness tiers.",
            }
        ],
        "skill_power_artifact_hooks": [
            {
                "anchor_type": "artifact_pool",
                "detail": "The cracked badge can act as evidence.",
            }
        ],
        "sensory_detail_hints": ["Use sound or silence to show social pressure in Oath Court."],
        "specificity_score": 0.85,
    }


def test_scene_blueprint_engine_builds_blueprint():
    engine = SceneBlueprintEngine()

    result = engine.build_scene_blueprint(
        story_context=build_story_context(),
        world_detail_pack=build_world_detail_pack(),
        scene_seed={"scene_id": "scene_trial"},
    )

    blueprint = result["scene_blueprint"]

    assert result["success"] is True
    assert blueprint.blueprint_id == "blueprint_scene_trial"
    assert blueprint.scene_id == "scene_trial"
    assert blueprint.pov_character_id == "char_kael"
    assert "char_kael" in blueprint.active_character_ids
    assert blueprint.location_id == "location_court"
    assert blueprint.stakes
    assert blueprint.secret_pressure
    assert blueprint.relationship_pressure
    assert blueprint.required_world_details
    assert blueprint.ending_hook is not None


def test_scene_blueprint_engine_uses_seed_overrides():
    engine = SceneBlueprintEngine()

    result = engine.build_scene_blueprint(
        story_context=build_story_context(),
        world_detail_pack=build_world_detail_pack(),
        scene_seed={
            "scene_id": "scene_custom",
            "blueprint_id": "blueprint_custom",
            "pov_character_id": "char_seren",
            "scene_purpose": "Force Seren to choose silence or confession.",
            "scene_objective": "Seren must protect her source without losing Kael.",
            "ending_hook": "Seren finally says Kael's name.",
        },
    )

    blueprint = result["scene_blueprint"]

    assert blueprint.blueprint_id == "blueprint_custom"
    assert blueprint.pov_character_id == "char_seren"
    assert blueprint.scene_purpose == "Force Seren to choose silence or confession."
    assert blueprint.scene_objective == "Seren must protect her source without losing Kael."
    assert blueprint.ending_hook == "Seren finally says Kael's name."


def test_scene_blueprint_engine_validates_blueprint():
    engine = SceneBlueprintEngine()

    blueprint = engine.build_scene_blueprint(
        story_context=build_story_context(),
        world_detail_pack=build_world_detail_pack(),
        scene_seed={"scene_id": "scene_trial"},
    )["scene_blueprint"]

    validation = engine.validate_blueprint(blueprint=blueprint)

    assert validation["success"] is True
    assert validation["valid"] is True
    assert "active_characters_present" in validation["passed_checks"]
    assert "scene_objective_present" in validation["passed_checks"]
    assert "world_details_present" in validation["passed_checks"]


def test_scene_blueprint_engine_summarizes_blueprint():
    engine = SceneBlueprintEngine()

    blueprint = engine.build_scene_blueprint(
        story_context=build_story_context(),
        world_detail_pack=build_world_detail_pack(),
        scene_seed={"scene_id": "scene_trial"},
    )["scene_blueprint"]

    summary = engine.summarize_blueprint(blueprint=blueprint)

    assert summary["success"] is True
    assert summary["summary"]["scene_id"] == "scene_trial"
    assert summary["summary"]["pov_character_id"] == "char_kael"
    assert summary["summary"]["active_character_count"] == 2
    assert summary["summary"]["world_detail_count"] >= 3
    assert summary["summary"]["max_tension"] > 0.5


def test_scene_blueprint_engine_builds_tension_curve():
    engine = SceneBlueprintEngine()

    blueprint = engine.build_scene_blueprint(
        story_context=build_story_context(),
        world_detail_pack=build_world_detail_pack(),
        scene_seed={"scene_id": "scene_trial"},
    )["scene_blueprint"]

    assert len(blueprint.tension_curve) == 4
    assert blueprint.tension_curve[-1] >= blueprint.tension_curve[0]


def test_scene_blueprint_engine_warns_on_weak_blueprint():
    engine = SceneBlueprintEngine()

    weak_context = {
        "story_context_id": "weak",
        "active_cast": [],
        "world_rules": [],
        "location_anchor": {"missing": True},
        "relationship_pressure": [],
        "knowledge_boundaries": [],
        "emotional_pressure": [],
        "causal_obligations": [],
        "readiness": {"ready_for_blueprint": False},
    }
    weak_pack = {
        "world_detail_pack_id": "weakpack",
        "specificity_score": 0.1,
        "sensory_detail_hints": [],
    }

    result = engine.build_scene_blueprint(
        story_context=weak_context,
        world_detail_pack=weak_pack,
        scene_seed={"scene_id": "weak_scene"},
    )

    assert any("no active characters" in warning.lower() for warning in result["warnings"])
    assert any("world details" in warning.lower() for warning in result["warnings"])
    assert any("not fully ready" in warning.lower() for warning in result["warnings"])

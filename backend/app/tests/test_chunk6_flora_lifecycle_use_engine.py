from backend.app.engines.deep_world.flora_generator import FloraGenerator
from backend.app.engines.deep_world.flora_lifecycle_use_engine import FloraLifecycleUseEngine


def build_flora():
    generator = FloraGenerator()
    return generator.build_flora(source_id="lifecycle_flora_source")["deep_world_flora"]


def test_flora_lifecycle_engine_builds_lifecycle_profile():
    flora = build_flora()
    engine = FloraLifecycleUseEngine()

    profile = engine.build_lifecycle_profile(
        source_id="lifecycle_test",
        flora=flora,
    )["flora_lifecycle_profile"]

    assert profile["flora_id"] == flora.element_id
    assert profile["growth_stages"]
    assert profile["harvest_rules"]
    assert profile["use_windows"]
    assert profile["misuse_risks"]
    assert profile["story_use"]
    assert profile["character_effect"]
    assert profile["plot_effect"]
    assert profile["memory_effect"]
    assert profile["detail_depth_score"] >= 0.75


def test_flora_lifecycle_engine_builds_use_profile():
    flora = build_flora()
    engine = FloraLifecycleUseEngine()
    lifecycle = engine.build_lifecycle_profile(
        source_id="use_test",
        flora=flora,
    )["flora_lifecycle_profile"]

    use_profile = engine.build_use_profile(
        source_id="use_test",
        flora=flora,
        lifecycle_profile=lifecycle,
    )["flora_use_profile"]

    assert use_profile["flora_id"] == flora.element_id
    assert use_profile["lifecycle_profile_id"] == lifecycle["lifecycle_profile_id"]
    assert use_profile["use_cases"]
    assert use_profile["regulation_rules"]
    assert use_profile["access_conflicts"]
    assert use_profile["story_use"]
    assert use_profile["character_effect"]
    assert use_profile["plot_effect"]
    assert use_profile["memory_effect"]


def test_flora_lifecycle_engine_builds_story_context_patch():
    flora = build_flora()
    engine = FloraLifecycleUseEngine()
    lifecycle = engine.build_lifecycle_profile(source_id="patch_test", flora=flora)["flora_lifecycle_profile"]
    use_profile = engine.build_use_profile(
        source_id="patch_test",
        flora=flora,
        lifecycle_profile=lifecycle,
    )["flora_use_profile"]

    patch = engine.build_story_context_patch(
        flora=flora,
        lifecycle_profile=lifecycle,
        use_profile=use_profile,
    )["story_context_patch"]

    assert patch["flora_id"] == flora.element_id
    assert patch["lifecycle_profile_id"] == lifecycle["lifecycle_profile_id"]
    assert patch["use_profile_id"] == use_profile["use_profile_id"]
    assert "memory_update_candidates" in patch
    assert len(patch["memory_update_candidates"]) == 2
    assert "generation_hints" in patch


def test_flora_lifecycle_engine_validates_profiles():
    flora = build_flora()
    engine = FloraLifecycleUseEngine()
    lifecycle = engine.build_lifecycle_profile(source_id="validate_test", flora=flora)["flora_lifecycle_profile"]
    use_profile = engine.build_use_profile(
        source_id="validate_test",
        flora=flora,
        lifecycle_profile=lifecycle,
    )["flora_use_profile"]

    lifecycle_validation = engine.validate_lifecycle_profile(lifecycle_profile=lifecycle)
    use_validation = engine.validate_use_profile(use_profile=use_profile)

    assert lifecycle_validation["passed"] is True
    assert lifecycle_validation["missing_fields"] == []
    assert use_validation["passed"] is True
    assert use_validation["missing_fields"] == []


def test_flora_lifecycle_engine_detects_bad_profiles():
    engine = FloraLifecycleUseEngine()

    lifecycle_validation = engine.validate_lifecycle_profile(
        lifecycle_profile={
            "lifecycle_profile_id": "bad_lifecycle",
            "flora_id": "flora_bad",
            "story_use": "Bad.",
        }
    )

    use_validation = engine.validate_use_profile(
        use_profile={
            "use_profile_id": "bad_use",
            "flora_id": "flora_bad",
            "plot_effect": "Bad.",
        }
    )

    assert lifecycle_validation["passed"] is False
    assert lifecycle_validation["missing_fields"]
    assert "story_use" in lifecycle_validation["shallow_fields"]

    assert use_validation["passed"] is False
    assert use_validation["missing_fields"]
    assert "plot_effect" in use_validation["shallow_fields"]


def test_flora_lifecycle_engine_summarizes_and_textualizes():
    flora = build_flora()
    engine = FloraLifecycleUseEngine()
    lifecycle = engine.build_lifecycle_profile(source_id="text_test", flora=flora)["flora_lifecycle_profile"]
    use_profile = engine.build_use_profile(
        source_id="text_test",
        flora=flora,
        lifecycle_profile=lifecycle,
    )["flora_use_profile"]

    summary = engine.summarize_lifecycle_and_use(
        lifecycle_profile=lifecycle,
        use_profile=use_profile,
    )

    text = engine.build_lifecycle_use_text(
        lifecycle_profile=lifecycle,
        use_profile=use_profile,
    )["lifecycle_use_text"]

    assert summary["success"] is True
    assert summary["summary"]["lifecycle_profile_id"] == lifecycle["lifecycle_profile_id"]
    assert "Flora Lifecycle + Use Profile" in text
    assert "Growth Stages" in text
    assert "Memory Effect" in text

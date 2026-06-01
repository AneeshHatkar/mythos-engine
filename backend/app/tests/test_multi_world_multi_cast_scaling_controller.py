from backend.app.engines.story_generation.multi_world_multi_cast_scaling_controller import (
    MultiWorldMultiCastScalingController,
)
from backend.app.schemas.story_generation import (
    GameInteractiveScenePackage,
    GeneratedChapter,
    LongFormContinuationAnchor,
    PlotOutline,
    SeriesSeasonFormatPackage,
)


def build_plot_outline():
    return PlotOutline(
        outline_id="plot_outline_scaling",
        source_id="scaling_source",
        title="Court Secrets",
        premise="A public proof system threatens private loyalties.",
        scene_sequence=[{"scene_id": "scene_001", "purpose": "Expose the badge."}],
        act_structure=[{"act_number": 1, "act_purpose": "Setup", "scene_ids": ["scene_001"]}],
        character_arc_threads=[
            {"thread_id": "character_arc_char_kael", "character_id": "char_kael"},
            {"thread_id": "character_arc_char_seren", "character_id": "char_seren"},
        ],
        relationship_arc_threads=[
            {"thread_id": "relationship_arc_rel_kael_seren", "relationship_id": "rel_kael_seren"}
        ],
        secret_threads=[
            {"thread_id": "secret_thread_secret_seren_source", "secret_id": "secret_seren_source"}
        ],
        causal_threads=[
            {"thread_id": "causal_thread_cause_trial_reveal", "causal_id": "cause_trial_reveal"}
        ],
        world_state_threads=[
            {"thread_id": "world_thread_oath_court", "world_detail": "Oath Court"},
            {"thread_id": "world_thread_badge_law", "world_detail": "badge law"},
        ],
        open_loops=[{"loop_id": "open_loop_secret", "description": "Secret remains hidden."}],
        payoff_setups=[{"payoff_id": "payoff_secret", "description": "Reveal carefully."}],
        continuity_requirements={
            "required_character_ids": ["char_kael", "char_seren"],
            "required_relationship_ids": ["rel_kael_seren"],
            "required_secret_ids": ["secret_seren_source"],
            "required_causal_ids": ["cause_trial_reveal"],
            "required_world_details": ["Oath Court", "badge law"],
        },
    )


def build_chapter():
    return GeneratedChapter(
        chapter_id="chapter_scaling",
        chapter_number=1,
        title="The Badge",
        chapter_text="Kael exposes the badge.",
        scene_ids=["scene_001"],
        assembled_scene_ids=["assembled_scene_001"],
        used_character_ids=["char_kael", "char_seren"],
        used_relationship_ids=["rel_kael_seren"],
        used_secret_ids=["secret_seren_source"],
        used_causal_ids=["cause_trial_reveal"],
        used_world_details=["Oath Court", "cracked badge"],
    )


def build_anchor():
    return LongFormContinuationAnchor(
        anchor_id="continuation_anchor_scaling",
        chapter_id="chapter_scaling",
        chapter_number=1,
        active_character_ids=["char_kael", "char_seren"],
        active_relationship_ids=["rel_kael_seren"],
        active_secret_ids=["secret_seren_source"],
        active_causal_ids=["cause_trial_reveal"],
        active_world_details=["Oath Court", "cracked badge"],
        open_loops=[{"loop_id": "open_loop_secret", "description": "Secret remains hidden."}],
        next_chapter_hooks=["Seren refuses to deny the badge."],
    )


def build_series_package():
    return SeriesSeasonFormatPackage(
        series_package_id="series_package_scaling",
        source_id="scaling_source",
        series_title="Court Secrets",
        episode_count=1,
        plot_lanes={
            "A_plot": [{"plot_beat_id": "a_plot_cause", "description": "Causal pressure.", "source_id": "cause_trial_reveal"}],
            "B_plot": [{"plot_beat_id": "b_plot_relationship", "description": "Relationship pressure.", "source_id": "rel_kael_seren"}],
        },
        recurring_character_dynamics=[
            {"dynamic_id": "recurring_character_char_kael", "character_id": "char_kael"},
            {"dynamic_id": "recurring_relationship_rel_kael_seren", "relationship_id": "rel_kael_seren"},
        ],
        formatted_text="Series text.",
    )


def build_game_package():
    return GameInteractiveScenePackage(
        game_package_id="game_package_scaling",
        source_id="scaling_source",
        scene_title="Interactive Court",
        player_objective="Expose or hide the badge.",
        npc_dialogue_blocks=[
            {"dialogue_block_id": "npc_dialogue_char_kael", "npc_id": "char_kael"},
            {"dialogue_block_id": "npc_dialogue_char_seren", "npc_id": "char_seren"},
        ],
        branching_outcomes=[
            {"outcome_id": "outcome_push_truth", "description": "Truth is pushed."}
        ],
        relationship_state_hooks=[
            {"relationship_hook_id": "relationship_hook_rel_kael_seren", "relationship_id": "rel_kael_seren"}
        ],
        world_state_hooks=[
            {"world_hook_id": "world_hook_oath_court", "world_detail": "Oath Court"}
        ],
        formatted_text="Game text.",
    )


def test_scaling_controller_builds_plan():
    controller = MultiWorldMultiCastScalingController()

    result = controller.build_scaling_plan(
        source_id="scaling_source",
        plot_outline=build_plot_outline(),
        chapters=[build_chapter()],
        continuation_anchor=build_anchor(),
        series_package=build_series_package(),
        game_package=build_game_package(),
    )

    plan = result["multi_world_multi_cast_scaling_plan"]

    assert result["success"] is True
    assert plan.scaling_plan_id == "multi_world_multi_cast_scaling_scaling_source"
    assert plan.world_count >= 1
    assert plan.cast_count >= 1
    assert plan.total_character_count >= 2
    assert plan.generation_batch_plan


def test_scaling_controller_tracks_worlds_casts_and_lanes():
    controller = MultiWorldMultiCastScalingController()

    plan = controller.build_scaling_plan(
        source_id="scaling_source",
        plot_outline=build_plot_outline(),
        chapters=[build_chapter()],
        continuation_anchor=build_anchor(),
        series_package=build_series_package(),
        game_package=build_game_package(),
    )["multi_world_multi_cast_scaling_plan"]

    world_ids = {item["world_id"] for item in plan.world_registry}
    cast_ids = {item["cast_id"] for item in plan.cast_registry}
    lane_types = {item["lane_type"] for item in plan.storyline_lanes}

    assert "world_oath_court" in world_ids
    assert "cast_primary" in cast_ids
    assert "causal" in lane_types
    assert "secret" in lane_types
    assert "interactive_branch" in lane_types


def test_scaling_controller_builds_partition_rules():
    controller = MultiWorldMultiCastScalingController()

    plan = controller.build_scaling_plan(
        source_id="scaling_source",
        plot_outline=build_plot_outline(),
        chapters=[build_chapter()],
        continuation_anchor=build_anchor(),
    )["multi_world_multi_cast_scaling_plan"]

    rule_types = {item["rule_type"] for item in plan.continuity_partition_rules}

    assert "world_partition" in rule_types
    assert "cast_partition" in rule_types
    assert "storyline_lane" in rule_types


def test_scaling_controller_builds_cross_links():
    controller = MultiWorldMultiCastScalingController()

    plan = controller.build_scaling_plan(
        source_id="scaling_source",
        plot_outline=build_plot_outline(),
        chapters=[build_chapter()],
        continuation_anchor=build_anchor(),
    )["multi_world_multi_cast_scaling_plan"]

    assert plan.cross_world_links
    assert plan.cross_cast_relationships
    assert any(item["relationship_id"] == "rel_kael_seren" for item in plan.cross_cast_relationships)


def test_scaling_controller_validates_plan():
    controller = MultiWorldMultiCastScalingController()

    plan = controller.build_scaling_plan(
        source_id="scaling_source",
        plot_outline=build_plot_outline(),
        chapters=[build_chapter()],
        continuation_anchor=build_anchor(),
    )["multi_world_multi_cast_scaling_plan"]

    validation = controller.validate_scaling_plan(plan=plan)

    assert validation["success"] is True
    assert validation["valid"] is True
    assert "scaling_plan_id_present" in validation["passed_checks"]
    assert "world_registry_present" in validation["passed_checks"]
    assert "cast_registry_present" in validation["passed_checks"]


def test_scaling_controller_summarizes_plan():
    controller = MultiWorldMultiCastScalingController()

    plan = controller.build_scaling_plan(
        source_id="scaling_source",
        plot_outline=build_plot_outline(),
        chapters=[build_chapter()],
        continuation_anchor=build_anchor(),
    )["multi_world_multi_cast_scaling_plan"]

    summary = controller.summarize_scaling_plan(plan=plan)

    assert summary["success"] is True
    assert summary["summary"]["source_id"] == "scaling_source"
    assert summary["summary"]["world_count"] >= 1
    assert summary["summary"]["cast_count"] >= 1


def test_scaling_controller_builds_report_text():
    controller = MultiWorldMultiCastScalingController()

    plan = controller.build_scaling_plan(
        source_id="scaling_source",
        plot_outline=build_plot_outline(),
        chapters=[build_chapter()],
        continuation_anchor=build_anchor(),
    )["multi_world_multi_cast_scaling_plan"]

    report = controller.build_scaling_report_text(plan=plan)

    assert report["success"] is True
    assert "Worlds" in report["scaling_report_text"]
    assert "Casts" in report["scaling_report_text"]
    assert "Batch Plan" in report["scaling_report_text"]


def test_scaling_controller_handles_large_cast_batching():
    controller = MultiWorldMultiCastScalingController()
    outline = build_plot_outline()

    outline.continuity_requirements["required_character_ids"] = [
        f"char_{index}" for index in range(30)
    ]
    outline.character_arc_threads = [
        {"thread_id": f"character_arc_char_{index}", "character_id": f"char_{index}"}
        for index in range(30)
    ]

    plan = controller.build_scaling_plan(
        source_id="large_cast_source",
        plot_outline=outline,
        max_characters_per_batch=10,
    )["multi_world_multi_cast_scaling_plan"]

    assert plan.total_character_count >= 30
    assert len(plan.generation_batch_plan) >= 3

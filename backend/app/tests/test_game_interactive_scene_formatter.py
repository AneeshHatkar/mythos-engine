from backend.app.engines.story_generation.game_interactive_scene_formatter import GameInteractiveSceneFormatter
from backend.app.schemas.story_generation import (
    AssembledScene,
    FormatAdaptationPlan,
    GeneratedChapter,
    LongFormContinuationAnchor,
    PlotOutline,
    SeriesSeasonFormatPackage,
)


def build_format_plan():
    return FormatAdaptationPlan(
        adaptation_plan_id="format_plan_game",
        source_id="game_source",
        target_format="game_scene",
        structure_rules={"unit_type": "interactive_scene", "requires_player_choice": True},
        prose_rules={"internality": "low_to_medium"},
        dialogue_rules={"dialogue_density": "choice_aware"},
        pacing_rules={"shape": "setup-choice-consequence-state-update"},
        continuity_rules={
            "must_preserve_player_agency": True,
            "must_emit_state_delta": True,
            "must_preserve_secret_ids": ["secret_seren_source"],
        },
        required_sections=["scene setup", "NPC exchange", "choice options", "state delta"],
        forbidden_patterns=["single fixed outcome only"],
    )


def build_plot_outline():
    return PlotOutline(
        outline_id="plot_outline_game",
        source_id="game_source",
        title="Court Secrets",
        premise="A public proof system threatens private loyalties.",
        scene_sequence=[
            {"scene_id": "scene_001", "purpose": "Expose the cracked badge."}
        ],
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
            {"thread_id": "world_thread_cracked_badge", "world_detail": "cracked badge"},
        ],
        open_loops=[
            {"loop_id": "open_loop_secret", "description": "Secret remains hidden.", "status": "open"}
        ],
        payoff_setups=[
            {"payoff_id": "payoff_secret_seren_source", "description": "Pay off the secret reveal carefully."}
        ],
        next_outline_hooks=["Seren refuses to deny the badge."],
        continuity_requirements={
            "required_character_ids": ["char_kael", "char_seren"],
            "required_relationship_ids": ["rel_kael_seren"],
            "required_secret_ids": ["secret_seren_source"],
            "required_causal_ids": ["cause_trial_reveal"],
            "required_world_details": ["Oath Court", "cracked badge"],
        },
    )


def build_chapter():
    return GeneratedChapter(
        chapter_id="chapter_game",
        chapter_number=1,
        title="The Badge",
        chapter_text="Kael exposes the badge. Seren refuses to answer.",
        scene_ids=["scene_001"],
        assembled_scene_ids=["assembled_scene_001"],
        used_character_ids=["char_kael", "char_seren"],
        used_relationship_ids=["rel_kael_seren"],
        used_secret_ids=["secret_seren_source"],
        used_causal_ids=["cause_trial_reveal"],
        used_world_details=["Oath Court", "cracked badge"],
        open_loops=[
            {"loop_id": "open_loop_secret", "description": "Secret remains hidden.", "status": "open"}
        ],
        next_chapter_hooks=["Seren refuses to deny the badge."],
    )


def build_scene():
    return AssembledScene(
        assembled_scene_id="assembled_scene_game",
        scene_id="scene_001",
        title="Oath Court",
        assembled_text="Kael exposes the cracked badge. Seren refuses to answer.",
        continuity_trace={
            "scene_objective": "Make the badge public.",
            "ending_hook": "Seren refuses to deny the badge.",
        },
        used_character_ids=["char_kael", "char_seren"],
        used_relationship_ids=["rel_kael_seren"],
        used_secret_ids=["secret_seren_source"],
        used_causal_ids=["cause_trial_reveal"],
        used_world_details=["Oath Court", "cracked badge"],
    )


def build_anchor():
    return LongFormContinuationAnchor(
        anchor_id="continuation_anchor_game",
        chapter_id="chapter_game",
        chapter_number=1,
        active_character_ids=["char_kael", "char_seren"],
        active_relationship_ids=["rel_kael_seren"],
        active_secret_ids=["secret_seren_source"],
        active_causal_ids=["cause_trial_reveal"],
        active_world_details=["Oath Court", "cracked badge"],
        open_loops=[
            {"loop_id": "open_loop_secret", "description": "Secret remains hidden.", "status": "open"}
        ],
        next_chapter_hooks=["Seren refuses to deny the badge."],
    )


def build_series_package():
    return SeriesSeasonFormatPackage(
        series_package_id="series_package_game",
        source_id="game_source",
        series_title="Court Secrets",
        episode_count=1,
        episode_cards=[
            {"episode_card_id": "episode_001", "episode_title": "The Badge"}
        ],
        formatted_text="Series package context.",
    )


def test_game_interactive_scene_formatter_builds_package():
    formatter = GameInteractiveSceneFormatter()

    result = formatter.format_game_scene(
        source_id="game_source",
        scene_title="The Oath Court Choice",
        format_plan=build_format_plan(),
        plot_outline=build_plot_outline(),
        chapter=build_chapter(),
        assembled_scenes=[build_scene()],
        continuation_anchor=build_anchor(),
        series_package=build_series_package(),
    )

    package = result["game_interactive_scene_package"]

    assert result["success"] is True
    assert package.scene_title == "The Oath Court Choice"
    assert package.target_format == "game_scene"
    assert package.player_objective
    assert package.choice_menu
    assert package.branching_outcomes
    assert package.state_deltas


def test_game_interactive_scene_formatter_tracks_state_hooks():
    formatter = GameInteractiveSceneFormatter()

    package = formatter.format_game_scene(
        source_id="game_source",
        format_plan=build_format_plan(),
        plot_outline=build_plot_outline(),
        chapter=build_chapter(),
        assembled_scenes=[build_scene()],
        continuation_anchor=build_anchor(),
    )["game_interactive_scene_package"]

    assert package.relationship_state_hooks
    assert package.secret_state_hooks
    assert package.causal_state_hooks
    assert package.world_state_hooks
    assert any(item["secret_id"] == "secret_seren_source" for item in package.secret_state_hooks)


def test_game_interactive_scene_formatter_builds_inventory_hooks():
    formatter = GameInteractiveSceneFormatter()

    package = formatter.format_game_scene(
        source_id="game_source",
        plot_outline=build_plot_outline(),
        chapter=build_chapter(),
        assembled_scenes=[build_scene()],
    )["game_interactive_scene_package"]

    item_names = {item["item_name"] for item in package.inventory_hooks}

    assert "cracked badge" in item_names


def test_game_interactive_scene_formatter_builds_quest_updates():
    formatter = GameInteractiveSceneFormatter()

    package = formatter.format_game_scene(
        source_id="game_source",
        plot_outline=build_plot_outline(),
        chapter=build_chapter(),
        continuation_anchor=build_anchor(),
    )["game_interactive_scene_package"]

    assert package.quest_log_updates
    assert any(item["quest_type"] == "main" for item in package.quest_log_updates)
    assert any(item["quest_type"] == "payoff" for item in package.quest_log_updates)


def test_game_interactive_scene_formatter_validates_package():
    formatter = GameInteractiveSceneFormatter()

    package = formatter.format_game_scene(
        source_id="game_source",
        format_plan=build_format_plan(),
        plot_outline=build_plot_outline(),
        chapter=build_chapter(),
        assembled_scenes=[build_scene()],
        continuation_anchor=build_anchor(),
    )["game_interactive_scene_package"]

    validation = formatter.validate_game_package(package=package)

    assert validation["success"] is True
    assert validation["valid"] is True
    assert "game_package_id_present" in validation["passed_checks"]
    assert "choice_menu_present" in validation["passed_checks"]
    assert "branching_outcomes_present" in validation["passed_checks"]


def test_game_interactive_scene_formatter_summarizes_package():
    formatter = GameInteractiveSceneFormatter()

    package = formatter.format_game_scene(
        source_id="game_source",
        plot_outline=build_plot_outline(),
        chapter=build_chapter(),
        assembled_scenes=[build_scene()],
        continuation_anchor=build_anchor(),
    )["game_interactive_scene_package"]

    summary = formatter.summarize_game_package(package=package)

    assert summary["success"] is True
    assert summary["summary"]["choice_count"] >= 3
    assert summary["summary"]["branching_outcome_count"] >= 3
    assert summary["summary"]["state_delta_count"] >= 3


def test_game_interactive_scene_formatter_builds_export_text():
    formatter = GameInteractiveSceneFormatter()

    package = formatter.format_game_scene(
        source_id="game_source",
        plot_outline=build_plot_outline(),
        chapter=build_chapter(),
    )["game_interactive_scene_package"]

    result = formatter.build_export_text(package=package)

    assert result["success"] is True
    assert result["export_text"] == package.formatted_text
    assert result["export_metadata"]["target_format"] == "game_scene"


def test_game_interactive_scene_formatter_warns_on_wrong_format_plan():
    formatter = GameInteractiveSceneFormatter()
    plan = build_format_plan()
    plan.target_format = "movie"

    package = formatter.format_game_scene(
        source_id="game_source",
        format_plan=plan,
        plot_outline=build_plot_outline(),
    )["game_interactive_scene_package"]

    assert any("Format plan target is movie" in warning for warning in package.warnings)

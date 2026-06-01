from backend.app.engines.story_generation.screenplay_movie_formatter import ScreenplayMovieFormatter
from backend.app.schemas.story_generation import (
    AssembledScene,
    FormatAdaptationPlan,
    GeneratedChapter,
    PlotOutline,
)


def build_format_plan(target_format="screenplay"):
    return FormatAdaptationPlan(
        adaptation_plan_id=f"format_plan_{target_format}",
        source_id="screenplay_source",
        target_format=target_format,
        structure_rules={"unit_type": "screenplay_scene" if target_format == "screenplay" else "film_sequence"},
        prose_rules={"internality": "none", "description_style": "performable"},
        dialogue_rules={"dialogue_density": "high", "speaker_tags": "screenplay"},
        pacing_rules={"shape": "visual-beat-dialogue-turn"},
        continuity_rules={
            "must_preserve_character_ids": ["char_kael", "char_seren"],
            "must_preserve_secret_ids": ["secret_seren_source"],
            "must_preserve_causal_ids": ["cause_trial_reveal"],
        },
        required_sections=["scene heading", "action", "dialogue"],
        forbidden_patterns=["internal monologue", "unfilmable feelings"],
    )


def build_plot_outline():
    return PlotOutline(
        outline_id="plot_outline_screenplay",
        source_id="screenplay_source",
        title="Court Secrets",
        premise="A public proof system threatens private loyalties.",
        scene_sequence=[
            {
                "scene_id": "scene_001",
                "purpose": "Kael exposes the cracked badge.",
                "used_character_ids": ["char_kael", "char_seren"],
                "used_secret_ids": ["secret_seren_source"],
                "used_causal_ids": ["cause_trial_reveal"],
                "used_world_details": ["Oath Court", "cracked badge"],
            }
        ],
        act_structure=[{"act_number": 1, "act_purpose": "Setup", "scene_ids": ["scene_001"]}],
        major_turning_points=[
            {
                "turning_point_id": "turn_001",
                "turning_point_type": "chapter_hook",
                "source_id": "scene_001",
                "description": "Seren refuses to deny the badge.",
            }
        ],
        continuity_requirements={
            "required_character_ids": ["char_kael", "char_seren"],
            "required_secret_ids": ["secret_seren_source"],
            "required_causal_ids": ["cause_trial_reveal"],
            "required_world_details": ["Oath Court", "cracked badge"],
        },
        next_outline_hooks=["Seren refuses to deny the badge."],
    )


def build_chapter():
    return GeneratedChapter(
        chapter_id="chapter_screenplay",
        chapter_number=1,
        title="The Badge in the Court",
        chapter_text="Kael exposes the badge. Seren refuses to answer.",
        scene_ids=["scene_001"],
        assembled_scene_ids=["assembled_scene_001"],
        sections=[
            {
                "scene_id": "scene_001",
                "title": "Oath Court",
                "text": "Kael exposes the cracked badge. Seren refuses to answer.",
                "used_character_ids": ["char_kael", "char_seren"],
                "used_secret_ids": ["secret_seren_source"],
                "used_causal_ids": ["cause_trial_reveal"],
                "used_world_details": ["Oath Court", "cracked badge"],
            }
        ],
        used_character_ids=["char_kael", "char_seren"],
        used_secret_ids=["secret_seren_source"],
        used_causal_ids=["cause_trial_reveal"],
        used_world_details=["Oath Court", "cracked badge"],
        next_chapter_hooks=["Seren refuses to deny the badge."],
    )


def build_assembled_scene():
    return AssembledScene(
        assembled_scene_id="assembled_scene_screenplay",
        scene_id="scene_001",
        title="Oath Court",
        assembled_text="Kael exposes the cracked badge. Seren refuses to answer.",
        continuity_trace={
            "scene_objective": "Kael must make the badge public.",
            "ending_hook": "Seren refuses to deny the badge.",
        },
        used_character_ids=["char_kael", "char_seren"],
        used_secret_ids=["secret_seren_source"],
        used_causal_ids=["cause_trial_reveal"],
        used_world_details=["Oath Court", "cracked badge"],
    )


def test_screenplay_movie_formatter_builds_screenplay_package():
    formatter = ScreenplayMovieFormatter()

    result = formatter.format_for_screenplay_or_movie(
        source_id="screenplay_source",
        target_format="screenplay",
        format_plan=build_format_plan("screenplay"),
        plot_outline=build_plot_outline(),
        chapter=build_chapter(),
        assembled_scenes=[build_assembled_scene()],
    )

    package = result["screenplay_movie_format_package"]

    assert result["success"] is True
    assert package.target_format == "screenplay"
    assert package.scene_headings
    assert package.action_blocks
    assert package.dialogue_blocks
    assert "INT." in package.formatted_text
    assert package.export_payload["suggested_extension"] == ".fountain"


def test_screenplay_movie_formatter_builds_movie_package():
    formatter = ScreenplayMovieFormatter()

    package = formatter.format_for_screenplay_or_movie(
        source_id="movie_source",
        target_format="movie",
        format_plan=build_format_plan("movie"),
        plot_outline=build_plot_outline(),
        chapter=build_chapter(),
        assembled_scenes=[build_assembled_scene()],
    )["screenplay_movie_format_package"]

    assert package.target_format == "movie"
    assert package.movie_sequence_beats
    assert "MOVIE SEQUENCE BEATS" in package.formatted_text
    assert package.export_payload["suggested_extension"] == ".md"


def test_screenplay_movie_formatter_preserves_continuity_requirements():
    formatter = ScreenplayMovieFormatter()

    package = formatter.format_for_screenplay_or_movie(
        source_id="screenplay_source",
        target_format="screenplay",
        format_plan=build_format_plan("screenplay"),
        plot_outline=build_plot_outline(),
        chapter=build_chapter(),
        assembled_scenes=[build_assembled_scene()],
    )["screenplay_movie_format_package"]

    requirements = package.continuity_requirements

    assert requirements["visual_only_rule"] is True
    assert requirements["plot_outline_id"] == "plot_outline_screenplay"
    assert "secret_seren_source" in requirements["chapter_id"] or requirements["chapter_id"] == "chapter_screenplay"
    assert "used_secret_ids" in requirements


def test_screenplay_movie_formatter_builds_visual_motifs():
    formatter = ScreenplayMovieFormatter()

    package = formatter.format_for_screenplay_or_movie(
        source_id="screenplay_source",
        target_format="screenplay",
        format_plan=build_format_plan("screenplay"),
        plot_outline=build_plot_outline(),
        chapter=build_chapter(),
        assembled_scenes=[build_assembled_scene()],
    )["screenplay_movie_format_package"]

    motif_sources = {item["source_detail"] for item in package.visual_motifs}

    assert "Oath Court" in motif_sources
    assert "cracked badge" in motif_sources


def test_screenplay_movie_formatter_validates_package():
    formatter = ScreenplayMovieFormatter()

    package = formatter.format_for_screenplay_or_movie(
        source_id="screenplay_source",
        target_format="screenplay",
        format_plan=build_format_plan("screenplay"),
        plot_outline=build_plot_outline(),
        chapter=build_chapter(),
        assembled_scenes=[build_assembled_scene()],
    )["screenplay_movie_format_package"]

    validation = formatter.validate_format_package(package=package)

    assert validation["success"] is True
    assert validation["valid"] is True
    assert "format_package_id_present" in validation["passed_checks"]
    assert "scene_headings_present" in validation["passed_checks"]
    assert "action_blocks_present" in validation["passed_checks"]


def test_screenplay_movie_formatter_summarizes_package():
    formatter = ScreenplayMovieFormatter()

    package = formatter.format_for_screenplay_or_movie(
        source_id="movie_source",
        target_format="movie",
        format_plan=build_format_plan("movie"),
        plot_outline=build_plot_outline(),
        chapter=build_chapter(),
        assembled_scenes=[build_assembled_scene()],
    )["screenplay_movie_format_package"]

    summary = formatter.summarize_format_package(package=package)

    assert summary["success"] is True
    assert summary["summary"]["target_format"] == "movie"
    assert summary["summary"]["scene_heading_count"] >= 1
    assert summary["summary"]["movie_sequence_beat_count"] >= 1


def test_screenplay_movie_formatter_builds_export_text():
    formatter = ScreenplayMovieFormatter()

    package = formatter.format_for_screenplay_or_movie(
        source_id="screenplay_source",
        target_format="screenplay",
        format_plan=build_format_plan("screenplay"),
        plot_outline=build_plot_outline(),
        chapter=build_chapter(),
        assembled_scenes=[build_assembled_scene()],
    )["screenplay_movie_format_package"]

    result = formatter.build_export_text(package=package)

    assert result["success"] is True
    assert result["export_text"] == package.formatted_text
    assert result["export_metadata"]["target_format"] == "screenplay"


def test_screenplay_movie_formatter_warns_without_scene_units():
    formatter = ScreenplayMovieFormatter()

    package = formatter.format_for_screenplay_or_movie(
        source_id="empty_source",
        target_format="screenplay",
        format_plan=build_format_plan("screenplay"),
        plot_outline=None,
        chapter=None,
        assembled_scenes=[],
    )["screenplay_movie_format_package"]

    assert any("No scene units" in warning for warning in package.warnings)

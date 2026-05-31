from backend.app.engines.simulation.genre_adaptation_ml_hook_engine import GenreAdaptationMLHookEngine
from backend.app.schemas.simulation import SimulationState, SimulationWorldState


def build_state():
    return SimulationState(
        simulation_id="sim_genre_001",
        world_state=SimulationWorldState(world_id="world_velmora"),
    )


def test_genre_engine_creates_genre_profile():
    engine = GenreAdaptationMLHookEngine()

    profile = engine.create_genre_profile(
        profile_id="genre_dark_academy_romance",
        primary_genres=["dark_academy", "romance"],
        secondary_genres=["mystery", "unknown_genre"],
        tone_tags=["tense", "ancient", "tragic"],
        intensity_targets={"romance": 0.7, "mystery": 0.8},
        convention_targets={"twist_targets": ["romance reveal changes political stakes"]},
    )

    assert profile["profile_id"] == "genre_dark_academy_romance"
    assert "dark_academy" in profile["primary_genres"]
    assert "romance" in profile["primary_genres"]
    assert "drama" in profile["secondary_genres"]
    assert profile["intensity_targets"]["romance"] == 0.7


def test_genre_engine_creates_adaptation_profile():
    engine = GenreAdaptationMLHookEngine()

    profile = engine.create_adaptation_profile(
        adaptation_id="adapt_movie",
        output_format="movie",
        target_length="120 minutes",
        prose_density=0.2,
        dialogue_density=0.7,
        visuality_target=0.9,
        interiority_target=0.3,
    )

    assert profile["adaptation_id"] == "adapt_movie"
    assert profile["output_format"] == "movie"
    assert profile["act_structure"] == "three_act_feature"
    assert profile["format_constraints"]["require_visual_beats"] is True


def test_genre_engine_creates_ml_learning_hook():
    engine = GenreAdaptationMLHookEngine()

    hook = engine.create_ml_learning_hook(
        hook_id="hook_style",
        hook_type="style_profile",
        source_type="pdf_corpus",
        source_id="corpus_001",
        learning_target="learn abstract prose rhythm",
        extracted_features={"sentence_variation": "high"},
        evaluation_metrics={"abstraction_safety": 0.9},
        confidence=0.8,
        requires_human_review=True,
    )

    assert hook["hook_id"] == "hook_style"
    assert hook["hook_type"] == "style_profile"
    assert hook["confidence"] == 0.8
    assert hook["requires_human_review"] is True


def test_genre_engine_builds_generation_control_payload():
    engine = GenreAdaptationMLHookEngine()

    genre = engine.create_genre_profile(
        profile_id="genre_1",
        primary_genres=["dark_academy", "romance"],
        tone_tags=["tense", "mythic"],
    )
    adaptation = engine.create_adaptation_profile(
        adaptation_id="adapt_1",
        output_format="novel",
    )
    hook = engine.create_ml_learning_hook(
        hook_id="hook_1",
        hook_type="character_pattern",
        source_type="simulation",
        source_id="sim_1",
        learning_target="track character-specific wounds",
    )

    result = engine.build_generation_control_payload(
        payload_id="gen_control_1",
        story_request={
            "format": "novel",
            "allow_project_created_characters": True,
            "allow_any_character_count": True,
            "distinctive_elements": ["ancient oath court", "forbidden romance"],
        },
        genre_profile=genre,
        adaptation_profile=adaptation,
        handoff_package={"package_id": "handoff_1"},
        learning_hooks=[hook],
    )

    payload = result["payload"]

    assert result["success"] is True
    assert payload["payload_id"] == "gen_control_1"
    assert payload["generation_rules"]["must_not_force_fixed_character_count"] is True
    assert payload["continuity_contract"]["allow_any_character_count"] is True
    assert payload["quality_contract"]["requires_eval_report"] is True
    assert payload["anti_genericity_contract"]["must_avoid_generic_plot"] is True


def test_genre_engine_builds_pdf_learning_hook_payload():
    engine = GenreAdaptationMLHookEngine()

    result = engine.build_pdf_learning_hook_payload(
        corpus_id="corpus_novels_001",
        document_ids=["doc_a", "doc_b"],
        learning_goals=[
            "learn prose style rhythm",
            "learn character arc patterns",
            "learn worldbuilding density",
            "learn dialogue dynamics",
        ],
        user_notes="Use as abstract reference only.",
    )

    assert result["success"] is True
    assert result["corpus_id"] == "corpus_novels_001"
    assert len(result["learning_hooks"]) == 4
    assert result["safety_contract"]["learn_abstract_patterns_only"] is True
    assert result["safety_contract"]["do_not_reproduce_source_verbatim"] is True
    assert any(hook["hook_type"] == "style_profile" for hook in result["learning_hooks"])
    assert any(hook["hook_type"] == "character_pattern" for hook in result["learning_hooks"])


def test_genre_engine_builds_adaptation_plan():
    engine = GenreAdaptationMLHookEngine()

    source_payload = {"payload_id": "plot_payload_1"}

    result = engine.build_adaptation_plan(
        plan_id="adapt_plan_1",
        story_request={
            "target_length": "feature length",
            "pov_mode": "third_person_limited",
        },
        source_payload=source_payload,
        target_formats=["novel", "movie", "series_episode"],
    )

    assert result["success"] is True
    assert result["plan_id"] == "adapt_plan_1"
    assert len(result["adaptation_profiles"]) == 3
    assert result["adaptation_rules"]["preserve_core_causal_chain"] is True
    assert {profile["output_format"] for profile in result["adaptation_profiles"]} == {
        "novel",
        "movie",
        "series_episode",
    }


def test_genre_engine_registers_generation_control_and_builds_map():
    state = build_state()
    engine = GenreAdaptationMLHookEngine()

    genre = engine.create_genre_profile(
        profile_id="genre_1",
        primary_genres=["fantasy"],
        tone_tags=["mythic"],
    )
    adaptation = engine.create_adaptation_profile(
        adaptation_id="adapt_1",
        output_format="screenplay",
    )

    payload = engine.build_generation_control_payload(
        payload_id="gen_control_1",
        story_request={"format": "screenplay"},
        genre_profile=genre,
        adaptation_profile=adaptation,
    )["payload"]

    registered = engine.register_generation_control_on_state(state=state, payload=payload)
    control_map = engine.build_generation_control_map(state=state)

    assert registered["success"] is True
    assert "gen_control_1" in state.metadata["generation_control_payloads"]
    assert control_map["success"] is True
    assert control_map["payload_count"] == 1
    assert control_map["generation_control_records"]["gen_control_1"]["output_format"] == "screenplay"

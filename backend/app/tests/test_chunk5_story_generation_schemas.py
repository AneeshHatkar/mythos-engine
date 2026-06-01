from backend.app.schemas.story_generation import (
    AdaptiveLearningSignal,
    ChapterDraft,
    Chunk5DesignContract,
    ConstraintSatisfactionReport,
    DialogueBeat,
    GenerationContract,
    GenerationMode,
    GeneratedSceneDelta,
    HandoffReference,
    SceneBeat,
    SceneBlueprint,
    SceneDraft,
    StoryExportBundle,
    StoryFormat,
    StoryGenerationRun,
    StoryIntent,
    StoryMemoryUpdateContract,
    StoryProvenanceRecord,
)


def test_chunk5_design_contract_defaults_are_research_grade():
    contract = Chunk5DesignContract()

    assert contract.must_preserve_user_intent is True
    assert contract.must_preserve_hidden_knowledge_boundaries is True
    assert contract.must_preserve_causal_continuity is True
    assert contract.must_be_provider_agnostic is True
    assert contract.must_support_future_corpus_learning_without_source_copying is True
    assert contract.must_support_large_entity_pools is True
    assert contract.must_support_long_form_generation is True


def test_story_intent_bounds_density_values():
    intent = StoryIntent(
        intent_id="intent_001",
        user_prompt="Write a tragic dark academy scene.",
        desired_format=StoryFormat.novel,
        generation_mode=GenerationMode.full_scene,
        dialogue_density=2.5,
        worldbuilding_density=-0.5,
        romance_intensity=0.8,
    )

    assert intent.dialogue_density == 1.0
    assert intent.worldbuilding_density == 0.0
    assert intent.romance_intensity == 0.8


def test_handoff_reference_supports_chunk4_bridge():
    ref = HandoffReference(
        simulation_id="sim_001",
        run_id="run_001",
        handoff_package_id="handoff_001",
        scene_payload_id="scene_payload_001",
        generation_control_payload_id="gen_control_001",
        quality_report_id="quality_001",
        anti_genericity_report_id="anti_001",
    )

    assert ref.simulation_id == "sim_001"
    assert ref.handoff_package_id == "handoff_001"
    assert ref.generation_control_payload_id == "gen_control_001"


def test_generation_contract_preserves_required_constraints():
    ref = HandoffReference(simulation_id="sim_001", run_id="run_001")
    contract = GenerationContract(
        generation_contract_id="contract_001",
        story_intent_id="intent_001",
        handoff_reference=ref,
        selected_format=StoryFormat.screenplay,
        required_character_ids=["char_kael", "char_seren"],
        forbidden_secret_reveals=["secret_seren_source"],
        required_causal_node_ids=["cause_trial_reveal"],
    )

    assert contract.validation_required is True
    assert contract.provenance_required is True
    assert "char_kael" in contract.required_character_ids
    assert "secret_seren_source" in contract.forbidden_secret_reveals


def test_scene_blueprint_and_beats_support_story_planning():
    blueprint = SceneBlueprint(
        blueprint_id="blueprint_001",
        scene_id="scene_001",
        scene_purpose="Expose the cracked badge evidence.",
        scene_objective="Kael forces the oath court to confront the truth.",
        active_character_ids=["char_kael", "char_seren", "char_vask"],
        stakes=["Kael may be exiled"],
        secret_pressure=["Seren knows the source"],
        tension_curve=[0.2, 0.6, 0.9],
        ending_hook="Seren refuses to deny the evidence.",
    )

    beat = SceneBeat(
        beat_id="beat_001",
        scene_id="scene_001",
        beat_index=1,
        beat_type="reveal",
        purpose="Reveal evidence without revealing Seren's hidden source.",
        character_ids=["char_kael"],
        knowledge_constraints=["Kael knows badge fraud but not Seren source"],
        causal_links=["cause_trial_reveal"],
        tension_value=1.5,
    )

    assert blueprint.scene_id == "scene_001"
    assert blueprint.ending_hook is not None
    assert beat.tension_value == 1.0


def test_dialogue_beat_supports_voice_subtext_and_secret_risk():
    beat = DialogueBeat(
        dialogue_beat_id="dialogue_001",
        scene_id="scene_001",
        speaker_id="char_seren",
        listener_ids=["char_kael"],
        surface_meaning="You should not have brought this here.",
        hidden_meaning="I am afraid this will expose the person I am protecting.",
        subtext="fear hidden as accusation",
        secret_risk=3.0,
        voice_rules={"formality": "controlled", "anger": "quiet"},
    )

    assert beat.secret_risk == 1.0
    assert beat.hidden_meaning is not None
    assert beat.voice_rules["anger"] == "quiet"


def test_scene_and_chapter_drafts_are_structured_outputs():
    scene = SceneDraft(
        draft_id="draft_scene_001",
        scene_id="scene_001",
        title="The Cracked Badge",
        format=StoryFormat.scene,
        text="Kael placed the cracked badge on the oath court table.",
        word_count=9,
        source_blueprint_id="blueprint_001",
        source_contract_id="contract_001",
    )

    chapter = ChapterDraft(
        chapter_id="chapter_001",
        title="The Oath Court",
        scene_draft_ids=[scene.draft_id],
        text=scene.text,
        chapter_objective="Begin the public truth arc.",
        ending_hook="The court doors opened behind Seren.",
    )

    assert scene.source_contract_id == "contract_001"
    assert chapter.scene_draft_ids == ["draft_scene_001"]
    assert chapter.ending_hook is not None


def test_story_provenance_tracks_generation_lineage():
    provenance = StoryProvenanceRecord(
        provenance_id="prov_001",
        draft_id="draft_scene_001",
        simulation_id="sim_001",
        run_id="run_001",
        handoff_package_id="handoff_001",
        generation_contract_id="contract_001",
        character_ids_used=["char_kael", "char_seren"],
        relationship_ids_used=["rel_kael_seren"],
        secret_ids_referenced=["secret_rank_system"],
        evidence_ids_referenced=["evidence_cracked_badge"],
        causal_node_ids_used=["cause_trial_reveal"],
        validators_run=["knowledge_boundary", "causal_continuity"],
        rewrite_passes=1,
    )

    assert provenance.simulation_id == "sim_001"
    assert "char_seren" in provenance.character_ids_used
    assert "knowledge_boundary" in provenance.validators_run


def test_story_memory_update_contract_supports_feedback_to_simulation():
    delta = GeneratedSceneDelta(
        generated_delta_id="delta_001",
        draft_id="draft_scene_001",
        scene_id="scene_001",
        delta_type="relationship_shift",
        target_entity_id="rel_kael_seren",
        proposed_change={"trust_delta": -0.1, "resentment_delta": 0.2},
        confidence=0.8,
        requires_user_approval=True,
    )

    contract = StoryMemoryUpdateContract(
        memory_update_contract_id="memory_contract_001",
        draft_id="draft_scene_001",
        possible_changes=[delta],
        memory_summary="Kael publicly exposed evidence and Seren did not stop him.",
        continuation_anchors=["Seren must explain why she stayed silent"],
        open_loops=["Who altered the ranking records?"],
    )

    assert contract.requires_user_approval is True
    assert contract.possible_changes[0].target_entity_id == "rel_kael_seren"
    assert contract.open_loops


def test_adaptive_learning_signal_is_safe_by_default():
    signal = AdaptiveLearningSignal(
        signal_id="learning_001",
        source_draft_id="draft_scene_001",
        signal_type="quality",
        target_area="voice_consistency",
        value=2.0,
        label="strong",
    )

    assert signal.value == 1.0
    assert signal.abstract_learning_only is True
    assert signal.contains_source_text is False


def test_story_generation_run_and_export_bundle():
    intent = StoryIntent(
        intent_id="intent_001",
        user_prompt="Generate a dark academy trial scene.",
    )

    run = StoryGenerationRun(
        run_id="story_run_001",
        story_intent=intent,
        generated_draft_ids=["draft_scene_001"],
        selected_draft_id="draft_scene_001",
    )

    bundle = StoryExportBundle(
        export_bundle_id="export_001",
        run_id=run.run_id,
        draft_ids=run.generated_draft_ids,
        export_format="markdown",
        export_paths=["exports/markdown/story_run_001.md"],
    )

    assert run.story_intent.intent_id == "intent_001"
    assert bundle.run_id == "story_run_001"
    assert bundle.export_paths[0].endswith(".md")

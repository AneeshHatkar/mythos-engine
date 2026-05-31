from backend.app.schemas.learning import (
    ContinuousLearningEvent,
    DatasetProvenanceRecord,
    EmbeddingMetadata,
    EngineLearningMetadata,
    HumanFeedbackRecord,
    LearnedOntologyRecord,
    LearnedTypeRegistryRecord,
    TrainingEligibility,
)


def test_dataset_provenance_defaults_are_safe():
    record = DatasetProvenanceRecord(
        source_name="human approved synthetic seed pack",
        source_type="synthetic",
        dataset_family="character",
    )

    assert record.provenance_id.startswith("prov_")
    assert record.usage_allowed is False
    assert record.human_review_required is True
    assert record.license_status == "unknown"
    assert record.created_at


def test_embedding_metadata_supports_similarity_and_novelty_tracking():
    metadata = EmbeddingMetadata(
        embedding_model="future-local-embedding-model",
        embedding_dimension=768,
        similarity_tags=["cognitive_inference", "pattern_detection"],
        novelty_score=0.82,
        originality_score=0.76,
    )

    assert metadata.embedding_id.startswith("emb_")
    assert metadata.embedding_dimension == 768
    assert "pattern_detection" in metadata.similarity_tags
    assert metadata.novelty_score == 0.82


def test_training_eligibility_defaults_to_do_not_train():
    eligibility = TrainingEligibility()

    assert eligibility.eligibility_id.startswith("elig_")
    assert eligibility.training_eligible is False
    assert eligibility.human_review_required is True
    assert eligibility.do_not_train is True
    assert eligibility.recommended_split == "human_review_queue"


def test_human_feedback_record_tracks_review_and_editing():
    feedback = HumanFeedbackRecord(
        target_id="char_kael",
        target_type="character",
        rating=9,
        feedback_text="Strong character concept, improve skill limitation.",
        accepted=True,
        edited_by_human=True,
        edit_summary="Added clearer cost.",
        improvement_tags=["skill_cost", "character_depth"],
    )

    assert feedback.feedback_id.startswith("fb_")
    assert feedback.rating == 9
    assert feedback.accepted is True
    assert "skill_cost" in feedback.improvement_tags


def test_learned_ontology_record_can_represent_scalable_skill_type():
    record = LearnedOntologyRecord(
        ontology_type="skill",
        name="Pattern Reading",
        family="cognitive_inference",
        subtype="hidden_system_detection",
        description="Reads hidden patterns in institutions, behavior, and social pressure.",
        axes={
            "activation_model": "passive_focus",
            "cost_family": ["mental_fatigue", "emotional_exposure"],
            "counter_family": ["false_signal", "missing_evidence", "emotional_bias"],
            "growth_model": "precision_refinement",
            "adaptability_compatibility": 0.72,
        },
        tags=["inference", "non_combat_power", "system_detection"],
        examples=["Pattern Reading", "Oath Clause Recognition"],
        counterexamples=["raw firepower", "brute force"],
        confidence_score=0.86,
        novelty_score=0.64,
        quality_score=0.82,
        learned_from_data=False,
        generated_by_engine="character.skill_ontology_engine",
    )

    assert record.ontology_id.startswith("onto_")
    assert record.ontology_type == "skill"
    assert record.family == "cognitive_inference"
    assert record.axes["activation_model"] == "passive_focus"
    assert "false_signal" in record.axes["counter_family"]


def test_learned_ontology_record_can_represent_people_type():
    record = LearnedOntologyRecord(
        ontology_type="people_type",
        name="Hidden Kingmaker",
        family="power_redirector",
        subtype="low_visible_status_high_hidden_influence",
        axes={
            "role_function": ["catalyst", "strategist", "protagonist_possible"],
            "social_position": "low_visible_status",
            "power_access": "indirect",
            "relationship_function": "slow_trust_high_loyalty",
            "plot_function": "redirects_power_flow",
            "adaptability_potential": 0.82,
            "destiny_relevance": 0.78,
        },
        tags=["kingmaker", "hidden_influence", "strategic_character"],
    )

    assert record.ontology_type == "people_type"
    assert record.axes["power_access"] == "indirect"
    assert record.axes["adaptability_potential"] >= 0.8


def test_learned_type_registry_record_combines_ontology_embedding_provenance_and_training():
    ontology = LearnedOntologyRecord(
        ontology_type="skill",
        name="Dream Thread Cartography",
        family="psychic_cognitive_mapping",
    )
    embedding = EmbeddingMetadata(
        similarity_tags=["dream_mapping", "symbolic_navigation"],
        novelty_score=0.9,
    )
    provenance = DatasetProvenanceRecord(
        source_name="human approved synthetic examples",
        source_type="synthetic",
        dataset_family="skill",
        usage_allowed=True,
        human_review_required=False,
    )
    eligibility = TrainingEligibility(
        training_eligible=True,
        human_review_required=False,
        do_not_train=False,
        recommended_split="train",
        quality_score=0.88,
        consistency_score=0.86,
        originality_score=0.9,
        safety_score=0.92,
    )

    registry = LearnedTypeRegistryRecord(
        type_name="Dream Thread Cartography",
        type_family="skill",
        type_subfamily="psychic_cognitive_mapping",
        type_scope="character_skill",
        ontology_ids=[ontology.ontology_id],
        embedding_metadata=embedding,
        provenance_records=[provenance],
        training_eligibility=eligibility,
        reusable_prompt_tags=["dream", "mapping", "memory"],
        generation_constraints=["must include memory distortion cost"],
        learned_axes={"cost_family": ["sleep_loss", "memory_blur"]},
    )

    assert registry.registry_id.startswith("ltype_")
    assert registry.training_eligibility.training_eligible is True
    assert registry.training_eligibility.do_not_train is False
    assert registry.embedding_metadata.novelty_score == 0.9
    assert registry.provenance_records[0].usage_allowed is True


def test_engine_learning_metadata_attaches_learning_layer_to_engine_output():
    ontology = LearnedOntologyRecord(
        ontology_type="skill",
        name="Pattern Reading",
        family="cognitive_inference",
    )

    metadata = EngineLearningMetadata(
        engine_name="character.skill_power_engine",
        target_object_id="char_kael",
        target_object_type="character",
        ontology_records=[ontology],
        retrieval_context_used=["similar:cognitive_inference:pattern_detection"],
        generated_training_labels={
            "skill_family": "cognitive_inference",
            "skill_subtype": "pattern_detection",
        },
        learning_notes=[
            "This output should be used as structured metadata for future model training."
        ],
    )

    assert metadata.learning_metadata_id.startswith("learn_")
    assert metadata.engine_name == "character.skill_power_engine"
    assert metadata.ontology_records[0].family == "cognitive_inference"
    assert metadata.training_eligibility.do_not_train is True
    assert "skill_family" in metadata.generated_training_labels


def test_continuous_learning_event_controls_future_registry_updates():
    event = ContinuousLearningEvent(
        event_type="human_approved_new_skill_type",
        target_id="skill_dream_thread_cartography",
        target_type="skill_ontology",
        source_engine="character.skill_ontology_engine",
        action="queue_for_registry_update",
        payload={"family": "psychic_cognitive_mapping"},
        should_update_registry=True,
        should_update_embedding_index=True,
        should_enter_training_queue=True,
        human_review_required=False,
    )

    assert event.event_id.startswith("clearn_")
    assert event.should_update_registry is True
    assert event.should_update_embedding_index is True
    assert event.should_enter_training_queue is True
    assert event.human_review_required is False

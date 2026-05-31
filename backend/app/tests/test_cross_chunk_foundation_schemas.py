from backend.app.schemas.artifacts import ArtifactRecord, ArtifactRegistrySummary
from backend.app.schemas.canon import CanonLock, CanonLockType, CanonStatusRecord, CanonValidationResult
from backend.app.schemas.engine_ops import (
    EngineConfigRecord,
    EngineErrorRecord,
    EngineErrorType,
    EngineRunMetrics,
    EngineThresholdConfig,
)
from backend.app.schemas.evaluation import (
    BenchmarkLabel,
    EvaluationCase,
    ExpectedBehavior,
    InvariantCheckResult,
    InvariantType,
    QualityGateResult,
)
from backend.app.schemas.global_refs import (
    ArtifactRef,
    BranchRef,
    CanonStatus,
    EntityRef,
    EntityType,
    ProjectUniverseRef,
    StateSnapshotRef,
    TimelineRef,
)
from backend.app.schemas.handoffs import (
    CharacterToSimulationContract,
    CrossChunkHandoffContract,
    GenreToAdaptationContract,
    SceneToGenreContract,
    SimulationToSceneContract,
    SystemToMLTrainingContract,
    WorldToCharacterContract,
)
from backend.app.schemas.human_review import HumanReviewRecord, ReviewQueueType
from backend.app.schemas.timeline import BranchRecord, TimelineBranchBundle, TimelineRecord


def test_entity_ref_and_artifact_ref_validate():
    entity = EntityRef(
        entity_type=EntityType.CHARACTER,
        entity_id="char_kael",
        display_name="Kael Veyran",
        project_id="proj_ashen",
        universe_id="velmora",
        canon_status=CanonStatus.CANDIDATE,
    )

    artifact = ArtifactRef(
        artifact_type="character_bible",
        project_id="proj_ashen",
        universe_id="velmora",
        source_engine="character.bible_export_engine",
        provenance_ids=["prov_001"],
        learning_metadata_ids=["learn_001"],
    )

    assert entity.entity_type == EntityType.CHARACTER
    assert entity.entity_id == "char_kael"
    assert artifact.artifact_id.startswith("artifact_")
    assert artifact.provenance_ids == ["prov_001"]


def test_project_branch_timeline_snapshot_refs_validate():
    project_ref = ProjectUniverseRef(
        project_id="proj_ashen",
        universe_id="velmora",
        branch_id="branch_main",
        timeline_id="timeline_main",
    )
    branch = BranchRef(
        branch_id="branch_alt",
        parent_branch_id="branch_main",
        branch_reason="Seren refuses Vask bargain",
        divergence_event_id="evt_bargain",
    )
    timeline = TimelineRef(
        timeline_id="timeline_main",
        tick_number=3,
        event_order=["evt_1", "evt_2"],
        branch_id="branch_main",
    )
    snapshot = StateSnapshotRef(
        simulation_id="sim_001",
        tick_number=3,
        state_hash="hash_abc",
    )

    assert project_ref.project_id == "proj_ashen"
    assert branch.parent_branch_id == "branch_main"
    assert timeline.tick_number == 3
    assert snapshot.snapshot_id.startswith("snapshot_")


def test_artifact_record_and_summary_validate():
    character_ref = EntityRef(entity_type=EntityType.CHARACTER, entity_id="char_kael")

    artifact = ArtifactRecord(
        artifact_type="simulation_trace",
        project_id="proj_ashen",
        universe_id="velmora",
        source_engine="simulation.orchestrator",
        source_entity_refs=[character_ref],
        quality_scores={"causal_coherence": 0.91},
        tags=["simulation", "relationship"],
    )

    summary = ArtifactRegistrySummary(
        project_id="proj_ashen",
        universe_id="velmora",
        artifact_count=1,
        artifact_types={"simulation_trace": 1},
        draft_count=1,
        latest_artifact_ids=[artifact.artifact_id],
    )

    assert artifact.artifact_id.startswith("artifact_")
    assert artifact.quality_scores["causal_coherence"] == 0.91
    assert summary.artifact_count == 1


def test_canon_schemas_validate():
    target = EntityRef(entity_type=EntityType.SECRET, entity_id="secret_family_name")

    lock = CanonLock(
        lock_type=CanonLockType.SECRET_STATUS,
        target_ref=target,
        locked_value={"revealed": False},
        reason="Secret must remain hidden before trial arc.",
        created_by_engine="simulation.constraint_solver",
    )

    status = CanonStatusRecord(
        target_ref=target,
        canon_status=CanonStatus.CANON,
        related_lock_ids=[lock.lock_id],
    )

    validation = CanonValidationResult(
        valid=False,
        violations=["secret reveal violates canon lock"],
        blocked_by_lock_ids=[lock.lock_id],
        retcon_required=True,
    )

    assert lock.lock_id.startswith("canonlock_")
    assert status.canon_status == CanonStatus.CANON
    assert validation.valid is False
    assert validation.retcon_required is True


def test_timeline_schemas_validate():
    branch = BranchRecord(
        branch_name="Seren rejects bargain",
        branch_reason="Counterfactual choice path",
        divergence_event_id="evt_blackmail_offer",
    )

    snapshot = StateSnapshotRef(simulation_id="sim_001", tick_number=1)
    timeline = TimelineRecord(
        project_id="proj_ashen",
        universe_id="velmora",
        branch_id=branch.branch_id,
        event_order=["evt_1"],
        current_tick=1,
        snapshot_refs=[snapshot],
    )

    bundle = TimelineBranchBundle(
        branch_ref=BranchRef(branch_id=branch.branch_id),
        timeline_ref=TimelineRef(timeline_id=timeline.timeline_id),
        branch_record=branch,
        timeline_record=timeline,
    )

    assert branch.branch_id.startswith("branch_")
    assert timeline.snapshot_refs[0].snapshot_id.startswith("snapshot_")
    assert bundle.branch_record.branch_id == branch.branch_id


def test_engine_ops_schemas_validate():
    threshold = EngineThresholdConfig(
        threshold_name="max_relationship_delta_per_event",
        value=0.18,
        min_value=0.0,
        max_value=1.0,
    )

    config = EngineConfigRecord(
        engine_name="simulation.relationship_graph_engine",
        thresholds={"max_relationship_delta_per_event": threshold},
        weights={"trust": 0.4, "respect": 0.2},
        flags={"blackmail_auto_compliance_forbidden": True},
    )

    metrics = EngineRunMetrics(
        engine_name="simulation.relationship_graph_engine",
        runtime_ms=12.5,
        input_count=2,
        output_count=1,
        quality_score=0.88,
        registered_to_learning=True,
        artifact_ids=["artifact_001"],
    )

    error = EngineErrorRecord(
        engine_name="simulation.knowledge_engine",
        error_type=EngineErrorType.KNOWLEDGE_LEAK_ERROR,
        message="Character acted on secret without knowledge path.",
        recoverable=True,
    )

    assert config.thresholds["max_relationship_delta_per_event"].value == 0.18
    assert metrics.registered_to_learning is True
    assert error.error_type == EngineErrorType.KNOWLEDGE_LEAK_ERROR


def test_evaluation_and_invariant_schemas_validate():
    expected = ExpectedBehavior(
        expected_deltas=[{"delta_type": "relationship_delta"}],
        expected_blockers=[],
        expected_quality_labels=[BenchmarkLabel.CAUSAL_COHERENCE],
        expected_invariant_results={InvariantType.NO_MAGIC_KNOWLEDGE: True},
    )

    case = EvaluationCase(
        case_name="secret discovery requires evidence path",
        dataset_family="relationship_simulation",
        expected_behavior=expected,
        benchmark_labels=[BenchmarkLabel.KNOWLEDGE_CONSISTENCY],
    )

    invariant = InvariantCheckResult(
        invariant_type=InvariantType.NO_MAGIC_KNOWLEDGE,
        passed=True,
        message="All knowledge actions have valid source path.",
    )

    gate = QualityGateResult(
        gate_name="simulation_trace_quality",
        passed=True,
        score=0.89,
        threshold=0.75,
    )

    assert case.case_id.startswith("evalcase_")
    assert invariant.passed is True
    assert gate.passed is True


def test_human_review_schema_validates():
    target = EntityRef(entity_type=EntityType.TRAINING_RECORD, entity_id="trainq_001")

    review = HumanReviewRecord(
        target_ref=target,
        review_queue_type=ReviewQueueType.TRAINING_APPROVAL,
        review_reason="High-quality synthetic trace requires approval before training.",
        review_priority="high",
        requested_by_engine="simulation.learning_adapter",
    )

    assert review.review_id.startswith("review_")
    assert review.review_queue_type == ReviewQueueType.TRAINING_APPROVAL
    assert review.review_status == "pending"


def test_cross_chunk_handoff_contracts_validate():
    project_ref = ProjectUniverseRef(project_id="proj_ashen", universe_id="velmora")
    character_ref = EntityRef(entity_type=EntityType.CHARACTER, entity_id="char_kael")

    base = CrossChunkHandoffContract(
        handoff_type="custom",
        from_chunk="a",
        to_chunk="b",
        project_ref=project_ref,
        required_entity_refs=[character_ref],
        readiness_score=0.9,
        ready=True,
    )

    wtc = WorldToCharacterContract(project_ref=project_ref, ready=True, readiness_score=0.9)
    cts = CharacterToSimulationContract(project_ref=project_ref, ready=True, readiness_score=0.9)
    stc = SimulationToSceneContract(project_ref=project_ref)
    stg = SceneToGenreContract(project_ref=project_ref)
    gta = GenreToAdaptationContract(project_ref=project_ref)
    ml = SystemToMLTrainingContract(project_ref=project_ref)

    assert base.ready is True
    assert wtc.handoff_type == "world_to_character"
    assert cts.to_chunk == "relationship_simulation"
    assert stc.handoff_type == "simulation_to_scene"
    assert stg.handoff_type == "scene_to_genre"
    assert gta.handoff_type == "genre_to_adaptation"
    assert ml.to_chunk == "ml_data_research"

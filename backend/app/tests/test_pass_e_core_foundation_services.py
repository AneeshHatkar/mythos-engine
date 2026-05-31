from backend.app.schemas.artifacts import ArtifactRecord
from backend.app.schemas.canon import CanonLock, CanonLockType
from backend.app.schemas.global_refs import CanonStatus, EntityRef, EntityType, ReviewStatus
from backend.app.schemas.human_review import HumanReviewRecord, ReviewQueueType
from backend.app.services.artifact_registry_store import ArtifactRegistryStore
from backend.app.services.canon_lock_service import CanonLockService
from backend.app.services.engine_config_store import EngineConfigStore
from backend.app.services.human_review_store import HumanReviewStore


def test_artifact_registry_store_saves_lists_gets_and_summarizes(tmp_path):
    store = ArtifactRegistryStore(root=tmp_path / "artifacts")

    artifact = ArtifactRecord(
        artifact_type="character_bible",
        project_id="proj_ashen",
        universe_id="velmora",
        source_engine="character.bible_export_engine",
        canon_status=CanonStatus.CANDIDATE,
        provenance_ids=["prov_001"],
        learning_metadata_ids=["learn_001"],
        quality_scores={"overall": 0.91},
    )

    result = store.save_artifact(artifact)

    assert result["success"] is True
    assert result["artifact_id"] == artifact.artifact_id

    listed = store.list_artifacts(project_id="proj_ashen", universe_id="velmora")
    fetched = store.get_artifact(artifact.artifact_id)
    summary = store.summarize(project_id="proj_ashen", universe_id="velmora")

    assert len(listed) == 1
    assert fetched["artifact_id"] == artifact.artifact_id
    assert summary["artifact_count"] == 1
    assert summary["artifact_types"]["character_bible"] == 1


def test_canon_lock_service_blocks_locked_change_and_allows_same_value():
    service = CanonLockService()

    target = EntityRef(entity_type=EntityType.SECRET, entity_id="secret_family_name")

    lock = CanonLock(
        lock_type=CanonLockType.SECRET_STATUS,
        target_ref=target,
        locked_value={"revealed": False},
        reason="Secret must remain hidden before trial.",
        created_by_engine="canon.test",
    )

    service.add_lock(lock)

    ok = service.validate_change(
        target_entity_id="secret_family_name",
        proposed_value={"revealed": False},
    )
    blocked = service.validate_change(
        target_entity_id="secret_family_name",
        proposed_value={"revealed": True},
    )

    assert ok["valid"] is True
    assert blocked["valid"] is False
    assert blocked["blocked_by_lock_ids"] == [lock.lock_id]
    assert blocked["retcon_required"] is True


def test_engine_config_store_creates_default_and_reads_threshold(tmp_path):
    store = EngineConfigStore(root=tmp_path / "configs")

    config = store.get_config("simulation.relationship_graph_engine")
    threshold = store.get_threshold(
        "simulation.relationship_graph_engine",
        "max_relationship_delta_per_event",
    )

    assert config["engine_name"] == "simulation.relationship_graph_engine"
    assert config["flags"]["blackmail_auto_compliance_forbidden"] is True
    assert threshold == 0.18


def test_human_review_store_enqueue_list_and_update(tmp_path):
    store = HumanReviewStore(root=tmp_path / "review")

    target = EntityRef(entity_type=EntityType.TRAINING_RECORD, entity_id="trainq_001")

    review = HumanReviewRecord(
        target_ref=target,
        review_queue_type=ReviewQueueType.TRAINING_APPROVAL,
        review_reason="Synthetic trace requires approval before training.",
        review_priority="high",
        requested_by_engine="simulation.learning_adapter",
    )

    enqueue = store.enqueue(review)
    listed = store.list_reviews(status=ReviewStatus.PENDING.value)
    update = store.update_status(
        review_id=review.review_id,
        status=ReviewStatus.APPROVED,
        reviewer="aneesh",
        note="Approved for synthetic training queue.",
    )
    approved = store.list_reviews(status=ReviewStatus.APPROVED.value)

    assert enqueue["success"] is True
    assert len(listed) == 1
    assert update["success"] is True
    assert approved[0]["approved_by_human"] == "aneesh"

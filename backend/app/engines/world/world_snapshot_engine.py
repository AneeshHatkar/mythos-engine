from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import uuid4

from backend.app.engines.base import BaseEngine
from backend.app.schemas.foundation import EngineRunResult


class WorldSnapshotEngine(BaseEngine):
    """Creates world snapshot/version metadata.

    This engine connects Chunk 2 world generation to Chunk 1's versioning idea.

    It does not replace database persistence yet. It creates clean snapshot
    payloads that can later be stored through the version API, audit API,
    export engine, or orchestrator.

    It supports:
    - world_v1
    - world_after_feedback
    - world_after_consistency_fix
    - world_after_template_change
    - world_after_dataset_review
    - quality snapshots
    - diff metadata
    - rollback readiness
    - version timeline entries
    """

    engine_name = "world.snapshot_engine"

    SNAPSHOT_TYPES = {
        "initial_generation",
        "after_feedback",
        "after_consistency_fix",
        "after_template_change",
        "after_dataset_review",
        "after_quality_scoring",
        "manual_checkpoint",
    }

    def run(self, payload: Dict[str, Any]) -> EngineRunResult:
        world_state = payload.get("world_state", {})
        project_id = payload.get("project_id")
        universe_id = payload.get("universe_id")
        snapshot_type = payload.get("snapshot_type", "manual_checkpoint")
        snapshot_label = payload.get("snapshot_label")
        parent_snapshot_id = payload.get("parent_snapshot_id")
        change_summary = payload.get("change_summary", "")
        quality_summary = payload.get("quality_summary") or world_state.get("quality_summary", {})
        diff_summary = payload.get("diff_summary", {})
        dataset_metadata = payload.get("dataset_metadata") or world_state.get("dataset_metadata", {})
        created_by = payload.get("created_by", "world.snapshot_engine")
        tags = payload.get("tags", [])

        warnings: List[str] = []

        if not world_state:
            warnings.append("No world_state provided; snapshot will be metadata-only.")

        if snapshot_type not in self.SNAPSHOT_TYPES:
            warnings.append(
                f"Unknown snapshot_type '{snapshot_type}'. Falling back to manual_checkpoint."
            )
            snapshot_type = "manual_checkpoint"

        snapshot = self._build_snapshot(
            world_state=world_state,
            project_id=project_id,
            universe_id=universe_id,
            snapshot_type=snapshot_type,
            snapshot_label=snapshot_label,
            parent_snapshot_id=parent_snapshot_id,
            change_summary=change_summary,
            quality_summary=quality_summary,
            diff_summary=diff_summary,
            dataset_metadata=dataset_metadata,
            created_by=created_by,
            tags=tags,
        )

        version_timeline_entry = self._build_version_timeline_entry(snapshot)

        return self.build_result(
            success=True,
            data={
                "snapshot": snapshot,
                "version_timeline_entry": version_timeline_entry,
                "training_notes": [
                    "Snapshots provide rollback-ready world checkpoints.",
                    "Snapshot metadata should later be stored through the version API or orchestrator.",
                    "Quality snapshots and dataset metadata prevent blind training on unreviewed outputs.",
                    "Future systems can use parent_snapshot_id to build world evolution timelines.",
                ],
            },
            warnings=warnings,
            errors=[],
            generated_object_ids=[snapshot["snapshot_id"]],
        )

    def _utc_now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _new_snapshot_id(self) -> str:
        return f"wsnap_{uuid4().hex[:12]}"

    def _flatten_text(self, obj: Any) -> str:
        if obj is None:
            return ""
        if isinstance(obj, str):
            return obj
        if isinstance(obj, (int, float, bool)):
            return str(obj)
        if isinstance(obj, list):
            return " ".join(self._flatten_text(item) for item in obj)
        if isinstance(obj, dict):
            return " ".join(
                str(key) + " " + self._flatten_text(value)
                for key, value in obj.items()
            )
        return str(obj)

    def _world_digest(self, world_state: Dict[str, Any]) -> Dict[str, Any]:
        text = self._flatten_text(world_state)
        system_keys = [
            key
            for key, value in world_state.items()
            if value not in (None, {}, [], "")
        ]

        motif_hits = []
        for motif in [
            "academy",
            "oath",
            "relic",
            "archive",
            "destiny",
            "class",
            "law",
            "belief",
            "border",
            "faction",
            "artifact",
            "causality",
            "training",
        ]:
            if motif in text.lower():
                motif_hits.append(motif)

        return {
            "system_count": len(system_keys),
            "system_keys": sorted(system_keys),
            "word_count_estimate": len(text.split()),
            "motif_hits": motif_hits,
        }

    def _rollback_readiness(
        self,
        *,
        world_state: Dict[str, Any],
        quality_summary: Dict[str, Any],
        parent_snapshot_id: Optional[str],
    ) -> Dict[str, Any]:
        has_world_state = bool(world_state)
        has_quality = bool(quality_summary)
        has_parent = bool(parent_snapshot_id)

        readiness_score = 0.0

        if has_world_state:
            readiness_score += 0.45
        if has_quality:
            readiness_score += 0.25
        if has_parent:
            readiness_score += 0.15

        digest = self._world_digest(world_state)

        if digest["system_count"] >= 10:
            readiness_score += 0.15
        elif digest["system_count"] >= 5:
            readiness_score += 0.08

        readiness_score = min(1.0, readiness_score)

        blockers = []

        if not has_world_state:
            blockers.append("Snapshot has no world_state.")

        if not has_quality:
            blockers.append("Snapshot has no quality_summary.")

        if digest["system_count"] < 5:
            blockers.append("Snapshot has low system coverage.")

        return {
            "rollback_ready": readiness_score >= 0.65 and has_world_state,
            "rollback_readiness_score": round(readiness_score, 3),
            "blockers": blockers,
        }

    def _build_snapshot(
        self,
        *,
        world_state: Dict[str, Any],
        project_id: Optional[str],
        universe_id: Optional[str],
        snapshot_type: str,
        snapshot_label: Optional[str],
        parent_snapshot_id: Optional[str],
        change_summary: str,
        quality_summary: Dict[str, Any],
        diff_summary: Dict[str, Any],
        dataset_metadata: Dict[str, Any],
        created_by: str,
        tags: List[str],
    ) -> Dict[str, Any]:
        snapshot_id = self._new_snapshot_id()
        created_at = self._utc_now()

        if snapshot_label is None:
            snapshot_label = self._default_label(snapshot_type)

        digest = self._world_digest(world_state)
        rollback = self._rollback_readiness(
            world_state=world_state,
            quality_summary=quality_summary,
            parent_snapshot_id=parent_snapshot_id,
        )

        version_kind = self._version_kind(snapshot_type)

        snapshot = {
            "snapshot_id": snapshot_id,
            "project_id": project_id,
            "universe_id": universe_id,
            "snapshot_label": snapshot_label,
            "snapshot_type": snapshot_type,
            "version_kind": version_kind,
            "parent_snapshot_id": parent_snapshot_id,
            "created_at": created_at,
            "created_by": created_by,
            "change_summary": change_summary or self._default_change_summary(snapshot_type),
            "tags": sorted(set(tags + [snapshot_type, version_kind])),
            "world_digest": digest,
            "quality_snapshot": {
                "consistency_score": quality_summary.get("consistency_score"),
                "originality_score": quality_summary.get("originality_score"),
                "story_potential_score": quality_summary.get("story_potential_score"),
                "training_readiness_score": quality_summary.get("training_readiness_score"),
                "genericness_risk_score": quality_summary.get("genericness_risk_score"),
                "quality_tier": quality_summary.get("quality_tier"),
                "training_eligible": quality_summary.get("training_eligible"),
            },
            "diff_snapshot": diff_summary,
            "dataset_snapshot": {
                "training_eligible": dataset_metadata.get("training_eligible"),
                "do_not_train": dataset_metadata.get("do_not_train"),
                "recommended_dataset_split": dataset_metadata.get("recommended_dataset_split"),
                "dataset_tags": dataset_metadata.get("dataset_tags", []),
                "risk_tags": dataset_metadata.get("risk_tags", []),
            },
            "rollback": rollback,
            "storage_recommendation": self._storage_recommendation(
                rollback_ready=rollback["rollback_ready"],
                quality_summary=quality_summary,
                dataset_metadata=dataset_metadata,
            ),
            "world_state": world_state,
        }

        return snapshot

    def _default_label(self, snapshot_type: str) -> str:
        labels = {
            "initial_generation": "world_v1",
            "after_feedback": "world_after_feedback",
            "after_consistency_fix": "world_after_consistency_fix",
            "after_template_change": "world_after_template_change",
            "after_dataset_review": "world_after_dataset_review",
            "after_quality_scoring": "world_after_quality_scoring",
            "manual_checkpoint": "world_manual_checkpoint",
        }
        return labels.get(snapshot_type, "world_manual_checkpoint")

    def _default_change_summary(self, snapshot_type: str) -> str:
        summaries = {
            "initial_generation": "Initial world snapshot created.",
            "after_feedback": "Snapshot created after user or reviewer feedback.",
            "after_consistency_fix": "Snapshot created after consistency fixes.",
            "after_template_change": "Snapshot created after template or preset update.",
            "after_dataset_review": "Snapshot created after dataset/training-readiness review.",
            "after_quality_scoring": "Snapshot created after quality scoring.",
            "manual_checkpoint": "Manual world checkpoint created.",
        }
        return summaries.get(snapshot_type, "Manual world checkpoint created.")

    def _version_kind(self, snapshot_type: str) -> str:
        if snapshot_type == "initial_generation":
            return "major"
        if snapshot_type in {"after_feedback", "after_consistency_fix", "after_template_change"}:
            return "minor"
        if snapshot_type in {"after_quality_scoring", "after_dataset_review"}:
            return "metadata"
        return "checkpoint"

    def _storage_recommendation(
        self,
        *,
        rollback_ready: bool,
        quality_summary: Dict[str, Any],
        dataset_metadata: Dict[str, Any],
    ) -> Dict[str, Any]:
        training_eligible = bool(
            quality_summary.get("training_eligible")
            or dataset_metadata.get("training_eligible")
        )
        do_not_train = bool(dataset_metadata.get("do_not_train"))

        if do_not_train:
            storage_tier = "archive_only_do_not_train"
        elif training_eligible and rollback_ready:
            storage_tier = "curated_training_candidate_snapshot"
        elif rollback_ready:
            storage_tier = "rollback_snapshot"
        else:
            storage_tier = "metadata_only_review"

        return {
            "storage_tier": storage_tier,
            "store_in_version_table": True,
            "store_in_audit_table": True,
            "export_recommended": rollback_ready,
            "notes": [
                "Snapshot can later be stored through Chunk 1 version APIs.",
                "Audit trail should include snapshot_type, quality_snapshot, and dataset_snapshot.",
                "Do not train on snapshot unless dataset_snapshot.training_eligible is true and do_not_train is false.",
            ],
        }

    def _build_version_timeline_entry(self, snapshot: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "snapshot_id": snapshot["snapshot_id"],
            "snapshot_label": snapshot["snapshot_label"],
            "snapshot_type": snapshot["snapshot_type"],
            "version_kind": snapshot["version_kind"],
            "parent_snapshot_id": snapshot["parent_snapshot_id"],
            "created_at": snapshot["created_at"],
            "change_summary": snapshot["change_summary"],
            "quality_tier": snapshot["quality_snapshot"].get("quality_tier"),
            "rollback_ready": snapshot["rollback"]["rollback_ready"],
            "storage_tier": snapshot["storage_recommendation"]["storage_tier"],
        }

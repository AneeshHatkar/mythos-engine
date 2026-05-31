from typing import Any, Dict, List

from backend.app.schemas.global_refs import CanonStatus, EntityRef, EntityType, ReviewStatus
from backend.app.schemas.artifacts import ArtifactRecord
from backend.app.schemas.canon import CanonLock, CanonLockType
from backend.app.schemas.human_review import HumanReviewRecord, ReviewQueueType
from backend.app.services.artifact_registry_store import ArtifactRegistryStore
from backend.app.services.canon_lock_service import CanonLockService
from backend.app.services.engine_config_store import EngineConfigStore
from backend.app.services.human_review_store import HumanReviewStore
from backend.app.services.world_state_snapshot_service import WorldStateSnapshotService
from backend.app.engines.world.world_rule_conflict_detector import WorldRuleConflictDetector
from backend.app.engines.world.world_location_access_engine import WorldLocationAccessEngine
from backend.app.engines.world.faction_institution_resource_engine import FactionInstitutionResourceEngine
from backend.app.services.character_state_snapshot_store import CharacterStateSnapshotStore
from backend.app.services.character_memory_update_adapter import CharacterMemoryUpdateAdapter
from backend.app.services.character_emotion_carryover_adapter import CharacterEmotionCarryoverAdapter
from backend.app.services.character_agency_state_updater import CharacterAgencyStateUpdater
from backend.app.services.character_consistency_invariant_checker import CharacterConsistencyInvariantChecker
from backend.app.services.story_dna_seed_service import StoryDNASeedService
from backend.app.services.emotional_resonance_seed_service import EmotionalResonanceSeedService
from backend.app.services.character_contrast_matrix_service import CharacterContrastMatrixService
from backend.app.services.world_character_pressure_matrix_service import WorldCharacterPressureMatrixService
from backend.app.services.cross_chunk_readiness_verifier import CrossChunkReadinessVerifier


class DeepStoryReadinessVerifier:
    """Final Pass E verifier before Chunk 4.

    This verifies Chunks 1-3 have traceability, canon protection, config,
    review hooks, world hardening, character mutable-state hardening, and
    deep story pressure layers.
    """

    def __init__(
        self,
        artifact_store: ArtifactRegistryStore | None = None,
        review_store: HumanReviewStore | None = None,
        world_snapshot_store: WorldStateSnapshotService | None = None,
        character_snapshot_store: CharacterStateSnapshotStore | None = None,
    ) -> None:
        self.artifact_store = artifact_store or ArtifactRegistryStore()
        self.review_store = review_store or HumanReviewStore()
        self.world_snapshot_store = world_snapshot_store or WorldStateSnapshotService()
        self.character_snapshot_store = character_snapshot_store or CharacterStateSnapshotStore()

        self.canon_service = CanonLockService()
        self.config_store = EngineConfigStore()
        self.cross_chunk_verifier = CrossChunkReadinessVerifier()

    def verify_deep_story_readiness(
        self,
        *,
        world_profile: Dict[str, Any],
        character_profiles: List[Dict[str, Any]],
        project_id: str = "default_project",
        universe_id: str = "default_universe",
    ) -> Dict[str, Any]:
        foundation_report = self.verify_foundation_hardening(
            world_profile=world_profile,
            character_profiles=character_profiles,
            project_id=project_id,
            universe_id=universe_id,
        )
        world_report = self.verify_world_hardening(
            world_profile=world_profile,
            project_id=project_id,
            universe_id=universe_id,
        )
        character_report = self.verify_character_hardening(
            character_profiles=character_profiles,
            project_id=project_id,
            universe_id=universe_id,
        )
        story_report = self.verify_deep_story_layers(
            world_profile=world_profile,
            character_profiles=character_profiles,
            project_id=project_id,
            universe_id=universe_id,
        )
        cross_chunk_report = self.cross_chunk_verifier.verify_cross_chunk_readiness(
            world_payload=world_profile,
            character_payloads=character_profiles,
            project_id=project_id,
            universe_id=universe_id,
        )

        reports = [foundation_report, world_report, character_report, story_report]
        blockers = []
        warnings = []
        for report in reports:
            blockers.extend(report.get("blockers", []))
            warnings.extend(report.get("warnings", []))

        if not cross_chunk_report.get("cross_chunk_ready_for_chunk4"):
            blockers.append("cross-chunk readiness verifier is not ready for Chunk 4")
            blockers.extend(cross_chunk_report.get("blockers", []))

        readiness_score = round(
            (
                foundation_report["readiness_score"]
                + world_report["readiness_score"]
                + character_report["readiness_score"]
                + story_report["readiness_score"]
                + cross_chunk_report.get("readiness_score", 0.0)
            )
            / 5,
            3,
        )

        ready = (
            foundation_report["ready"]
            and world_report["ready"]
            and character_report["ready"]
            and story_report["ready"]
            and cross_chunk_report.get("cross_chunk_ready_for_chunk4") is True
            and not blockers
        )

        return {
            "success": True,
            "deep_story_ready_for_chunk4": ready,
            "readiness_score": readiness_score,
            "project_id": project_id,
            "universe_id": universe_id,
            "foundation_hardening_report": foundation_report,
            "world_hardening_report": world_report,
            "character_hardening_report": character_report,
            "deep_story_layer_report": story_report,
            "cross_chunk_readiness_report": {
                "ready": cross_chunk_report.get("cross_chunk_ready_for_chunk4"),
                "readiness_score": cross_chunk_report.get("readiness_score"),
                "recommendation": cross_chunk_report.get("recommendation"),
            },
            "blockers": blockers,
            "warnings": warnings,
            "recommendation": "start_chunk4" if ready else "fix_deep_story_readiness_blockers",
        }

    def verify_foundation_hardening(
        self,
        *,
        world_profile: Dict[str, Any],
        character_profiles: List[Dict[str, Any]],
        project_id: str,
        universe_id: str,
    ) -> Dict[str, Any]:
        blockers = []
        warnings = []

        artifact = ArtifactRecord(
            artifact_type="deep_story_readiness_probe",
            project_id=project_id,
            universe_id=universe_id,
            source_engine="deep_story_readiness_verifier",
            canon_status=CanonStatus.DRAFT,
            tags=["pass_e", "readiness_probe"],
        )
        artifact_result = self.artifact_store.save_artifact(artifact)

        target = EntityRef(
            entity_type=EntityType.SECRET,
            entity_id="secret_readiness_probe",
            project_id=project_id,
            universe_id=universe_id,
        )
        lock = CanonLock(
            lock_type=CanonLockType.SECRET_STATUS,
            target_ref=target,
            locked_value={"revealed": False},
            reason="Readiness probe lock.",
            created_by_engine="deep_story_readiness_verifier",
        )
        self.canon_service.add_lock(lock)
        canon_block = self.canon_service.validate_change(
            target_entity_id="secret_readiness_probe",
            proposed_value={"revealed": True},
        )

        config = self.config_store.get_config("simulation.relationship_graph_engine")
        threshold = self.config_store.get_threshold(
            "simulation.relationship_graph_engine",
            "max_relationship_delta_per_event",
        )

        review_target = EntityRef(
            entity_type=EntityType.TRAINING_RECORD,
            entity_id="trainq_readiness_probe",
            project_id=project_id,
            universe_id=universe_id,
        )
        review = HumanReviewRecord(
            target_ref=review_target,
            review_queue_type=ReviewQueueType.TRAINING_APPROVAL,
            review_reason="Readiness probe for training review queue.",
            review_priority="medium",
            requested_by_engine="deep_story_readiness_verifier",
        )
        review_result = self.review_store.enqueue(review)

        checks = {
            "artifact_registry_store": artifact_result.get("success") is True,
            "canon_lock_service_blocks_invalid_change": canon_block.get("valid") is False,
            "engine_config_store": bool(config.get("engine_name")) and threshold > 0,
            "human_review_store": review_result.get("success") is True,
        }

        for key, ok in checks.items():
            if not ok:
                blockers.append(f"foundation hardening failed: {key}")

        score = sum(1 for ok in checks.values() if ok) / len(checks)

        return {
            "ready": score == 1.0,
            "readiness_score": round(score, 3),
            "checks": checks,
            "artifact_probe": artifact_result,
            "canon_probe": canon_block,
            "config_probe": {"engine_name": config.get("engine_name"), "max_relationship_delta_per_event": threshold},
            "review_probe": review_result,
            "blockers": blockers,
            "warnings": warnings,
        }

    def verify_world_hardening(
        self,
        *,
        world_profile: Dict[str, Any],
        project_id: str,
        universe_id: str,
    ) -> Dict[str, Any]:
        blockers = []
        warnings = []

        world_id = str(world_profile.get("world_id") or "unknown_world")

        snapshot = self.world_snapshot_store.create_snapshot(
            world_id=world_id,
            world_state=world_profile,
            project_id=project_id,
            universe_id=universe_id,
        )

        conflict = WorldRuleConflictDetector().run({"world_profile": world_profile})
        location = WorldLocationAccessEngine().run(
            {"world_profile": world_profile, "project_id": project_id, "universe_id": universe_id}
        )
        faction = FactionInstitutionResourceEngine().run(
            {"world_profile": world_profile, "project_id": project_id, "universe_id": universe_id}
        )

        checks = {
            "world_snapshot_created": snapshot.get("success") is True,
            "world_rule_conflict_detector": conflict.success is True and conflict.data.get("simulation_safe") is True,
            "world_location_access_engine": location.success is True and location.data.get("simulation_ready") is True,
            "faction_institution_resource_engine": faction.success is True and faction.data.get("simulation_ready") is True,
        }

        if conflict.data.get("conflicts"):
            blockers.extend(conflict.data["conflicts"])
        if conflict.data.get("warnings"):
            warnings.extend(conflict.data["warnings"])

        for key, ok in checks.items():
            if not ok:
                blockers.append(f"world hardening failed: {key}")

        score = sum(1 for ok in checks.values() if ok) / len(checks)

        return {
            "ready": score == 1.0 and not blockers,
            "readiness_score": round(score, 3),
            "checks": checks,
            "snapshot": snapshot,
            "world_rule_conflict_report": conflict.data,
            "location_access_report": location.data,
            "faction_resource_report": faction.data,
            "blockers": blockers,
            "warnings": warnings,
        }

    def verify_character_hardening(
        self,
        *,
        character_profiles: List[Dict[str, Any]],
        project_id: str,
        universe_id: str,
    ) -> Dict[str, Any]:
        blockers = []
        warnings = []
        character_reports = []

        memory_adapter = CharacterMemoryUpdateAdapter()
        emotion_adapter = CharacterEmotionCarryoverAdapter()
        agency_updater = CharacterAgencyStateUpdater()
        consistency_checker = CharacterConsistencyInvariantChecker()

        for profile in character_profiles:
            flat = self._flatten(profile)
            character_id = str(flat.get("character_id") or profile.get("character_id") or "unknown_character")

            snapshot = self.character_snapshot_store.create_snapshot(
                character_id=character_id,
                character_state={
                    "character_id": character_id,
                    "current_emotion_state": {"dominant_emotion": "controlled_pressure"},
                    "current_memory_state": {"active_memory_ids": []},
                    "current_agency_state": {"agency_capacity": 0.7},
                },
                project_id=project_id,
                universe_id=universe_id,
            )

            memory = memory_adapter.build_memory_update(
                character_id=character_id,
                event_payload={
                    "event_id": "evt_readiness_probe",
                    "event_type": "public_humiliation",
                    "description": "Readiness probe humiliation event.",
                },
                intensity=0.75,
            )
            emotion = emotion_adapter.build_emotion_update(
                character_id=character_id,
                event_payload={"event_type": "public_humiliation"},
                intensity=0.75,
            )
            agency = agency_updater.update_agency_state(
                character_id=character_id,
                event_payload={"event_type": "blackmail_attempt"},
                emotion_state=emotion["emotion_update"],
                knowledge_state={"known_secret_ids": ["secret_probe"], "evidence_seen_ids": ["evidence_probe"]},
                world_constraints={"legal_constraints": ["probe legal constraint"]},
            )
            consistency = consistency_checker.check_update(
                character_profile=profile,
                proposed_update={"uses_skill": True, "skill_cost_paid": True},
                event_context={"event_type": "trial", "intensity": 0.75},
            )

            checks = {
                "character_snapshot_created": snapshot.get("success") is True,
                "memory_update_ready": memory.get("success") is True and memory.get("should_persist") is True,
                "emotion_carryover_ready": emotion.get("success") is True and bool(emotion.get("emotion_update")),
                "agency_state_ready": agency.get("success") is True and bool(agency.get("agency_state")),
                "consistency_checker_ready": consistency.get("success") is True and consistency.get("consistent") is True,
            }

            char_blockers = [f"{character_id}: character hardening failed: {key}" for key, ok in checks.items() if not ok]
            blockers.extend(char_blockers)

            character_reports.append(
                {
                    "character_id": character_id,
                    "ready": not char_blockers,
                    "checks": checks,
                    "snapshot": snapshot,
                    "memory_probe": memory,
                    "emotion_probe": emotion,
                    "agency_probe": agency,
                    "consistency_probe": consistency,
                    "blockers": char_blockers,
                }
            )

        ready_count = sum(1 for item in character_reports if item["ready"])
        score = ready_count / len(character_reports) if character_reports else 0.0

        return {
            "ready": bool(character_reports) and ready_count == len(character_reports),
            "readiness_score": round(score, 3),
            "character_count": len(character_reports),
            "ready_character_count": ready_count,
            "character_reports": character_reports,
            "blockers": blockers,
            "warnings": warnings,
        }

    def verify_deep_story_layers(
        self,
        *,
        world_profile: Dict[str, Any],
        character_profiles: List[Dict[str, Any]],
        project_id: str,
        universe_id: str,
    ) -> Dict[str, Any]:
        blockers = []
        warnings = []

        dna = StoryDNASeedService().build_story_dna(
            project_id=project_id,
            universe_id=universe_id,
            world_profile=world_profile,
            character_profiles=character_profiles,
        )
        resonance = EmotionalResonanceSeedService().build_resonance_seed(
            project_id=project_id,
            universe_id=universe_id,
            story_dna=dna.get("story_dna", {}),
            relationship_mode="rivalry_with_hidden_care",
            target_intensity=0.8,
        )
        contrast = CharacterContrastMatrixService().build_contrast_matrix(
            character_profiles=character_profiles,
        )
        pressure = WorldCharacterPressureMatrixService().build_pressure_matrix(
            world_profile=world_profile,
            character_profiles=character_profiles,
        )

        checks = {
            "story_dna_ready": dna.get("success") is True and bool(dna.get("story_dna", {}).get("core_question")),
            "emotional_resonance_ready": resonance.get("success") is True and bool(resonance.get("emotional_resonance_seed")),
            "character_contrast_ready": contrast.get("success") is True and contrast.get("ensemble_ready") is True,
            "world_character_pressure_ready": pressure.get("success") is True and pressure.get("simulation_ready") is True,
        }

        for key, ok in checks.items():
            if not ok:
                blockers.append(f"deep story layer failed: {key}")

        if contrast.get("redundancy_warning_count", 0) > 0:
            warnings.append("character contrast matrix found redundancy warnings")

        score = sum(1 for ok in checks.values() if ok) / len(checks)

        return {
            "ready": score == 1.0 and not blockers,
            "readiness_score": round(score, 3),
            "checks": checks,
            "story_dna_report": dna,
            "emotional_resonance_report": resonance,
            "character_contrast_report": contrast,
            "world_character_pressure_report": pressure,
            "blockers": blockers,
            "warnings": warnings,
        }

    def _flatten(self, value: Any) -> Dict[str, Any]:
        flat: Dict[str, Any] = {}

        def walk(item: Any) -> None:
            if isinstance(item, dict):
                for key, val in item.items():
                    if key not in flat and not isinstance(val, (dict, list)):
                        flat[key] = val
                    walk(val)
            elif isinstance(item, list):
                for val in item:
                    walk(val)

        walk(value)
        return flat

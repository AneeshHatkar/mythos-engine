from typing import Any, Dict, List, Optional, Set

from backend.app.schemas.global_refs import CanonStatus
from backend.app.schemas.simulation import (
    CanonDelta,
    DeltaBatch,
    DeltaScope,
    SimulationBranch,
    SimulationEventPayload,
    SimulationState,
    SimulationStatus,
    StateDelta,
    TimelineDelta,
)


class CanonBranchTimelineValidator:
    """Validates canon, branch, and timeline safety before simulation mutation.

    This engine does not apply deltas. It verifies that events/deltas obey
    canon locks, branch boundaries, timeline order, prerequisites, and entity
    availability.
    """

    engine_name = "simulation.canon_branch_timeline_validator"

    def validate_event(
        self,
        *,
        state: SimulationState,
        event_payload: SimulationEventPayload,
    ) -> Dict[str, Any]:
        blockers: List[str] = []
        warnings: List[str] = []
        passed_checks: List[str] = []

        status_report = self._check_simulation_status(state)
        participant_report = self._check_event_participants(state, event_payload)
        prerequisite_report = self._check_event_prerequisites(state, event_payload)
        timeline_report = self._check_event_timeline_position(state, event_payload)
        branch_report = self._check_event_branch_context(state, event_payload)

        for report in [status_report, participant_report, prerequisite_report, timeline_report, branch_report]:
            blockers.extend(report.get("blockers", []))
            warnings.extend(report.get("warnings", []))
            passed_checks.extend(report.get("passed_checks", []))

        valid = len(blockers) == 0

        return {
            "success": True,
            "engine_name": self.engine_name,
            "event_id": event_payload.event_id,
            "valid": valid,
            "validation_score": self._score(blockers, warnings),
            "passed_checks": passed_checks,
            "blockers": blockers,
            "warnings": warnings,
            "reports": {
                "status": status_report,
                "participants": participant_report,
                "prerequisites": prerequisite_report,
                "timeline": timeline_report,
                "branch": branch_report,
            },
            "recommendation": "allow_event" if valid else "fix_canon_branch_timeline_blockers",
        }

    def validate_delta(
        self,
        *,
        state: SimulationState,
        delta: StateDelta,
    ) -> Dict[str, Any]:
        blockers: List[str] = []
        warnings: List[str] = []
        passed_checks: List[str] = []

        if delta.simulation_id != state.simulation_id:
            blockers.append("delta simulation_id does not match state")
        else:
            passed_checks.append("simulation_id_matches")

        canon_report = self._check_canon_delta_safety(state, delta)
        branch_report = self._check_delta_branch_safety(state, delta)
        timeline_report = self._check_timeline_delta_safety(state, delta)

        for report in [canon_report, branch_report, timeline_report]:
            blockers.extend(report.get("blockers", []))
            warnings.extend(report.get("warnings", []))
            passed_checks.extend(report.get("passed_checks", []))

        valid = len(blockers) == 0

        return {
            "success": True,
            "engine_name": self.engine_name,
            "delta_id": delta.delta_id,
            "valid": valid,
            "validation_score": self._score(blockers, warnings),
            "passed_checks": passed_checks,
            "blockers": blockers,
            "warnings": warnings,
            "recommendation": "allow_delta" if valid else "fix_delta_or_create_branch",
        }

    def validate_delta_batch(
        self,
        *,
        state: SimulationState,
        delta_batch: DeltaBatch,
    ) -> Dict[str, Any]:
        blockers: List[str] = []
        warnings: List[str] = []
        passed_checks: List[str] = []
        delta_reports: List[Dict[str, Any]] = []

        for delta in self._flatten_batch(delta_batch):
            report = self.validate_delta(state=state, delta=delta)
            delta_reports.append(report)
            blockers.extend([f"{delta.delta_id}: {item}" for item in report.get("blockers", [])])
            warnings.extend([f"{delta.delta_id}: {item}" for item in report.get("warnings", [])])
            passed_checks.extend(report.get("passed_checks", []))

        valid = len(blockers) == 0
        score = round(
            sum(report["validation_score"] for report in delta_reports) / len(delta_reports),
            3,
        ) if delta_reports else 1.0

        return {
            "success": True,
            "engine_name": self.engine_name,
            "batch_id": delta_batch.batch_id,
            "valid": valid,
            "validation_score": score,
            "delta_reports": delta_reports,
            "passed_checks": passed_checks,
            "blockers": blockers,
            "warnings": warnings,
            "recommendation": "allow_batch" if valid else "fix_batch_or_split_branch",
        }

    def validate_branch_creation(
        self,
        *,
        state: SimulationState,
        branch: SimulationBranch,
    ) -> Dict[str, Any]:
        blockers: List[str] = []
        warnings: List[str] = []
        passed_checks: List[str] = []

        if not branch.source_event_id and not branch.source_tick_id:
            blockers.append("branch requires source_event_id or source_tick_id")
        else:
            passed_checks.append("branch_has_source")

        if branch.source_event_id and branch.source_event_id not in set(state.timeline.event_order):
            warnings.append("branch source_event_id is not present in current timeline event_order")
        else:
            passed_checks.append("branch_source_event_known_or_not_required")

        if not branch.branch_reason:
            warnings.append("branch has no branch_reason")
        else:
            passed_checks.append("branch_reason_present")

        if branch.canon_status == CanonStatus.CANON:
            warnings.append("new branch starts as canon; usually branch should start as draft/alternate until approved")
        else:
            passed_checks.append("branch_not_auto_canon")

        valid = len(blockers) == 0

        return {
            "success": True,
            "engine_name": self.engine_name,
            "branch_id": branch.branch_id,
            "valid": valid,
            "validation_score": self._score(blockers, warnings),
            "passed_checks": passed_checks,
            "blockers": blockers,
            "warnings": warnings,
            "recommendation": "allow_branch" if valid else "fix_branch_metadata",
        }

    def _check_simulation_status(self, state: SimulationState) -> Dict[str, Any]:
        blockers: List[str] = []
        warnings: List[str] = []
        passed: List[str] = []

        if state.status in {SimulationStatus.FAILED, SimulationStatus.COMPLETED}:
            blockers.append(f"simulation status {state.status.value} cannot accept new canonical events")
        else:
            passed.append("simulation_status_allows_event")

        if state.dependency_contract and state.dependency_contract.blockers:
            blockers.append("dependency contract still has blockers")
        else:
            passed.append("dependency_contract_has_no_blockers_or_missing")

        return {"blockers": blockers, "warnings": warnings, "passed_checks": passed}

    def _check_event_participants(
        self,
        state: SimulationState,
        event: SimulationEventPayload,
    ) -> Dict[str, Any]:
        blockers: List[str] = []
        warnings: List[str] = []
        passed: List[str] = []

        participant_ids = event.actor_ids + event.target_ids + event.witness_ids

        for entity_id in participant_ids:
            if entity_id in state.character_states:
                character = state.character_states[entity_id]
                if character.metadata.get("dead") is True:
                    blockers.append(f"{entity_id} is dead and cannot participate/witness")
                elif character.metadata.get("inactive") is True:
                    warnings.append(f"{entity_id} is inactive but referenced in event")
                else:
                    passed.append(f"{entity_id}_character_available")
                continue

            if entity_id in state.entity_states:
                entity = state.entity_states[entity_id]
                if entity.active is False:
                    blockers.append(f"{entity_id} is inactive in entity_states")
                else:
                    passed.append(f"{entity_id}_entity_available")
                continue

            warnings.append(f"{entity_id} is referenced but not found in character_states/entity_states")

        return {"blockers": blockers, "warnings": warnings, "passed_checks": passed}

    def _check_event_prerequisites(
        self,
        state: SimulationState,
        event: SimulationEventPayload,
    ) -> Dict[str, Any]:
        blockers: List[str] = []
        warnings: List[str] = []
        passed: List[str] = []

        known_events = set(state.timeline.event_order)
        missing = [event_id for event_id in event.prerequisite_event_ids if event_id not in known_events]

        if missing:
            blockers.append(f"event prerequisites missing from timeline: {missing}")
        else:
            passed.append("event_prerequisites_satisfied")

        if event.event_id in known_events:
            blockers.append("event_id already exists in timeline")
        else:
            passed.append("event_id_not_duplicate")

        return {"blockers": blockers, "warnings": warnings, "passed_checks": passed}

    def _check_event_timeline_position(
        self,
        state: SimulationState,
        event: SimulationEventPayload,
    ) -> Dict[str, Any]:
        blockers: List[str] = []
        warnings: List[str] = []
        passed: List[str] = []

        metadata_tick = event.metadata.get("target_tick_number")
        if metadata_tick is not None:
            try:
                tick_number = int(metadata_tick)
                if tick_number < state.timeline.current_tick_number:
                    blockers.append("event attempts to insert into past timeline without branch/retcon metadata")
                else:
                    passed.append("event_tick_not_in_past")
            except Exception:
                warnings.append("event target_tick_number is not parseable")
        else:
            passed.append("event_has_no_forced_past_tick")

        if event.metadata.get("retcon") and not event.metadata.get("branch_id"):
            blockers.append("retcon event requires branch_id")
        elif event.metadata.get("retcon"):
            passed.append("retcon_has_branch_id")

        return {"blockers": blockers, "warnings": warnings, "passed_checks": passed}

    def _check_event_branch_context(
        self,
        state: SimulationState,
        event: SimulationEventPayload,
    ) -> Dict[str, Any]:
        blockers: List[str] = []
        warnings: List[str] = []
        passed: List[str] = []

        branch_id = event.metadata.get("branch_id")
        if branch_id:
            if branch_id not in state.branches:
                blockers.append(f"event references unknown branch_id {branch_id}")
            else:
                passed.append("event_branch_id_exists")
        else:
            passed.append("event_uses_main_timeline_context")

        if event.metadata.get("canon_promotion_requested"):
            if not event.metadata.get("human_review_approved"):
                warnings.append("canon promotion requested without human_review_approved")
            else:
                passed.append("canon_promotion_has_human_review")

        return {"blockers": blockers, "warnings": warnings, "passed_checks": passed}

    def _check_canon_delta_safety(
        self,
        state: SimulationState,
        delta: StateDelta,
    ) -> Dict[str, Any]:
        blockers: List[str] = []
        warnings: List[str] = []
        passed: List[str] = []

        entity_state = state.entity_states.get(delta.target_entity_id)
        if entity_state and delta.canon_sensitive:
            if delta.target_path in entity_state.locked_fields:
                blockers.append(f"canon-sensitive delta touches locked field {delta.target_path}")
            else:
                passed.append("canon_sensitive_delta_avoids_locked_fields")

        if isinstance(delta, CanonDelta):
            if delta.canon_status_after == CanonStatus.CANON and delta.requires_human_review:
                warnings.append("canon promotion requires human review approval before final promotion")
            if delta.retcon_required and not delta.alternate_branch_recommended:
                blockers.append("retcon_required delta must recommend alternate branch")
            if delta.lock_ids_affected and not delta.canon_change_summary:
                warnings.append("canon delta affects locks but has no canon_change_summary")
            passed.append("canon_delta_shape_checked")

        if not isinstance(delta, CanonDelta) and delta.delta_scope == DeltaScope.CANON:
            warnings.append("delta_scope is canon but delta is not CanonDelta")

        return {"blockers": blockers, "warnings": warnings, "passed_checks": passed}

    def _check_delta_branch_safety(
        self,
        state: SimulationState,
        delta: StateDelta,
    ) -> Dict[str, Any]:
        blockers: List[str] = []
        warnings: List[str] = []
        passed: List[str] = []

        branch_id = delta.metadata.get("branch_id") if isinstance(delta.metadata, dict) else None
        if branch_id:
            if branch_id not in state.branches:
                blockers.append(f"delta references unknown branch_id {branch_id}")
            else:
                passed.append("delta_branch_id_exists")
        else:
            passed.append("delta_uses_main_branch_context")

        if delta.metadata.get("retcon") and not branch_id:
            blockers.append("retcon delta requires branch_id")

        return {"blockers": blockers, "warnings": warnings, "passed_checks": passed}

    def _check_timeline_delta_safety(
        self,
        state: SimulationState,
        delta: StateDelta,
    ) -> Dict[str, Any]:
        blockers: List[str] = []
        warnings: List[str] = []
        passed: List[str] = []

        if isinstance(delta, TimelineDelta):
            known = set(state.timeline.event_order)
            missing_prereqs = [event_id for event_id in delta.prerequisite_event_ids if event_id not in known]
            if missing_prereqs:
                blockers.append(f"timeline delta missing prerequisite events: {missing_prereqs}")
            else:
                passed.append("timeline_delta_prerequisites_satisfied")

            duplicate_events = [event_id for event_id in delta.event_ids_added if event_id in known]
            if duplicate_events:
                blockers.append(f"timeline delta tries to add duplicate events: {duplicate_events}")
            else:
                passed.append("timeline_delta_events_not_duplicate")

            if delta.branch_id and delta.branch_id not in state.branches:
                blockers.append(f"timeline delta references unknown branch_id {delta.branch_id}")
            else:
                passed.append("timeline_delta_branch_known_or_missing")

        else:
            passed.append("non_timeline_delta_no_timeline_specific_checks")

        return {"blockers": blockers, "warnings": warnings, "passed_checks": passed}

    def _flatten_batch(self, batch: DeltaBatch) -> List[StateDelta]:
        deltas: List[StateDelta] = []
        deltas.extend(batch.deltas)
        deltas.extend(batch.relationship_deltas)
        deltas.extend(batch.knowledge_deltas)
        deltas.extend(batch.emotion_deltas)
        deltas.extend(batch.memory_deltas)
        deltas.extend(batch.reputation_deltas)
        deltas.extend(batch.faction_deltas)
        deltas.extend(batch.resource_deltas)
        deltas.extend(batch.legal_deltas)
        deltas.extend(batch.tension_deltas)
        deltas.extend(batch.stakes_deltas)
        deltas.extend(batch.canon_deltas)
        deltas.extend(batch.timeline_deltas)
        deltas.extend(batch.consequence_deltas)
        deltas.extend(batch.cast_scaling_deltas)
        deltas.extend(batch.backstory_deltas)
        return deltas

    def _score(self, blockers: List[str], warnings: List[str]) -> float:
        return round(max(0.0, 1.0 - 0.25 * len(blockers) - 0.06 * len(warnings)), 3)

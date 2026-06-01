from __future__ import annotations

from typing import Any, Dict, List

from backend.app.schemas.story_generation import (
    GeneratedStoryDeltaReport,
    StoryMemoryUpdateContract,
    StoryProvenanceRecord,
)


class StoryMemoryUpdateContractBuilder:
    """Builds a safe contract for updating long-form story memory.

    Locked Chunk 5.41. This engine does not persist memory yet. It converts
    provenance-approved deltas into staged/applyable/blocked memory updates.
    """

    engine_name = "story_generation.story_memory_update_contract"

    def build_memory_update_contract(
        self,
        *,
        source_id: str,
        draft_id: str,
        delta_report: GeneratedStoryDeltaReport,
        provenance_record: StoryProvenanceRecord | None = None,
        existing_memory_state: Dict[str, Any] | None = None,
        story_context: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        existing_memory_state = existing_memory_state or {}
        story_context = story_context or {}

        raw_updates = self._raw_updates_from_delta_report(delta_report=delta_report)
        conflict_checks = self._conflict_checks(
            raw_updates=raw_updates,
            existing_memory_state=existing_memory_state,
            provenance_record=provenance_record,
        )

        staged_updates = self._staged_updates(
            raw_updates=raw_updates,
            conflict_checks=conflict_checks,
            provenance_record=provenance_record,
        )
        blocked_updates = self._blocked_updates(
            raw_updates=raw_updates,
            conflict_checks=conflict_checks,
            provenance_record=provenance_record,
        )
        review_updates = self._review_required_updates(
            raw_updates=raw_updates,
            conflict_checks=conflict_checks,
            provenance_record=provenance_record,
        )

        approved_for_apply = self._approved_for_apply(
            staged_updates=staged_updates,
            blocked_updates=blocked_updates,
            review_updates=review_updates,
            provenance_record=provenance_record,
        )

        apply_mode = self._apply_mode(
            approved_for_apply=approved_for_apply,
            blocked_updates=blocked_updates,
            review_updates=review_updates,
            provenance_record=provenance_record,
        )

        memory_updates = staged_updates if approved_for_apply else []

        memory_contract_id = f"story_memory_contract_{source_id}_{draft_id}"

        contract = StoryMemoryUpdateContract(
            memory_update_contract_id=memory_contract_id,
            memory_contract_id=memory_contract_id,
            source_id=source_id,
            draft_id=draft_id,
            approved_for_apply=approved_for_apply,
            apply_mode=apply_mode,
            contract_status=self._contract_status(
                approved_for_apply=approved_for_apply,
                blocked_updates=blocked_updates,
                review_updates=review_updates,
            ),
            memory_updates=memory_updates,
            staged_updates=staged_updates,
            blocked_updates=blocked_updates,
            review_required_updates=review_updates,
            character_state_updates=self._filter_updates(staged_updates, "character_state"),
            relationship_state_updates=self._filter_updates(staged_updates, "relationship_state"),
            secret_state_updates=self._filter_updates(staged_updates, "secret_state"),
            causal_state_updates=self._filter_updates(staged_updates, "causal_state"),
            world_state_updates=self._filter_updates(staged_updates, "world_state"),
            object_state_updates=self._filter_updates(staged_updates, "object_state"),
            open_loop_updates=self._filter_updates(staged_updates, "open_loop_state"),
            resolved_loop_updates=self._filter_updates(staged_updates, "resolved_loop_state"),
            conflict_checks=conflict_checks,
            rollback_plan=self._rollback_plan(staged_updates=staged_updates, existing_memory_state=existing_memory_state),
            memory_apply_summary=self._memory_apply_summary(
                raw_updates=raw_updates,
                staged_updates=staged_updates,
                blocked_updates=blocked_updates,
                review_updates=review_updates,
                approved_for_apply=approved_for_apply,
                apply_mode=apply_mode,
            ),
            downstream_constraints=self._downstream_constraints(
                source_id=source_id,
                draft_id=draft_id,
                approved_for_apply=approved_for_apply,
                staged_updates=staged_updates,
                blocked_updates=blocked_updates,
                provenance_record=provenance_record,
            ),
            warnings=self._warnings(
                provenance_record=provenance_record,
                blocked_updates=blocked_updates,
                review_updates=review_updates,
                conflict_checks=conflict_checks,
            ),
        )

        return {
            "success": True,
            "engine_name": self.engine_name,
            "story_memory_update_contract": contract,
            "story_memory_update_contract_dict": contract.model_dump(mode="json"),
            "handoff_to_next_engine": {
                "next_engine": "story_generation.story_generation_orchestrator",
                "payload_keys": [
                    "story_memory_update_contract",
                    "generated_story_delta_report",
                    "story_provenance_record",
                    "story_context",
                ],
            },
        }

    def validate_memory_update_contract(self, *, contract: StoryMemoryUpdateContract) -> Dict[str, Any]:
        blockers: List[str] = []
        warnings: List[str] = []
        passed: List[str] = []

        if contract.memory_contract_id:
            passed.append("memory_contract_id_present")
        else:
            blockers.append("memory_contract_id missing")

        if contract.source_id and contract.draft_id:
            passed.append("source_and_draft_ids_present")
        else:
            blockers.append("source_id or draft_id missing")

        if contract.memory_apply_summary:
            passed.append("memory_apply_summary_present")
        else:
            warnings.append("memory apply summary missing")

        if contract.downstream_constraints:
            passed.append("downstream_constraints_present")
        else:
            warnings.append("downstream constraints missing")

        if contract.approved_for_apply and contract.blocked_updates:
            blockers.append("contract cannot be approved while blocked updates exist")

        if contract.blocked_updates:
            warnings.append("blocked updates present")

        if contract.review_required_updates:
            warnings.append("review-required updates present")

        if contract.warnings:
            warnings.extend(contract.warnings)

        return {
            "success": True,
            "engine_name": self.engine_name,
            "valid": not blockers,
            "blockers": blockers,
            "warnings": self._unique(warnings),
            "passed_checks": passed,
        }

    def summarize_memory_update_contract(self, *, contract: StoryMemoryUpdateContract) -> Dict[str, Any]:
        return {
            "success": True,
            "engine_name": self.engine_name,
            "summary": {
                "memory_contract_id": contract.memory_contract_id,
                "source_id": contract.source_id,
                "draft_id": contract.draft_id,
                "approved_for_apply": contract.approved_for_apply,
                "apply_mode": contract.apply_mode,
                "contract_status": contract.contract_status,
                "memory_update_count": len(contract.memory_updates),
                "staged_update_count": len(contract.staged_updates),
                "blocked_update_count": len(contract.blocked_updates),
                "review_required_update_count": len(contract.review_required_updates),
                "character_update_count": len(contract.character_state_updates),
                "relationship_update_count": len(contract.relationship_state_updates),
                "secret_update_count": len(contract.secret_state_updates),
                "causal_update_count": len(contract.causal_state_updates),
                "world_update_count": len(contract.world_state_updates),
                "object_update_count": len(contract.object_state_updates),
                "open_loop_update_count": len(contract.open_loop_updates),
                "resolved_loop_update_count": len(contract.resolved_loop_updates),
                "warning_count": len(contract.warnings),
            },
        }

    def build_memory_contract_text(self, *, contract: StoryMemoryUpdateContract) -> Dict[str, Any]:
        lines = [
            f"# Story Memory Update Contract: {contract.source_id}",
            "",
            f"Draft ID: {contract.draft_id}",
            f"Status: {contract.contract_status}",
            f"Approved for apply: {contract.approved_for_apply}",
            f"Apply mode: {contract.apply_mode}",
            "",
            "## Memory Apply Summary",
        ]

        for key, value in contract.memory_apply_summary.items():
            lines.append(f"- {key}: {value}")

        lines.append("")
        lines.append("## Staged Updates")
        for item in contract.staged_updates:
            lines.append(f"- {item.get('update_type')}: {item.get('target_id')} -> {item.get('value')}")

        lines.append("")
        lines.append("## Blocked Updates")
        for item in contract.blocked_updates:
            lines.append(f"- {item.get('update_type')}: {item.get('target_id')} because {item.get('block_reason')}")

        lines.append("")
        lines.append("## Review Required")
        for item in contract.review_required_updates:
            lines.append(f"- {item.get('update_type')}: {item.get('target_id')} because {item.get('review_reason')}")

        return {
            "success": True,
            "engine_name": self.engine_name,
            "memory_contract_text": "\n".join(lines),
        }

    def _raw_updates_from_delta_report(self, *, delta_report: GeneratedStoryDeltaReport) -> List[Dict[str, Any]]:
        updates = []
        all_delta_groups = [
            ("character_state", delta_report.character_deltas),
            ("relationship_state", delta_report.relationship_deltas),
            ("secret_state", delta_report.secret_deltas),
            ("causal_state", delta_report.causal_deltas),
            ("world_state", delta_report.world_deltas),
            ("object_state", delta_report.object_deltas),
            ("open_loop_state", delta_report.open_loop_deltas),
            ("resolved_loop_state", delta_report.resolved_loop_deltas),
        ]

        for update_type, deltas in all_delta_groups:
            for delta in deltas:
                updates.append(
                    {
                        "update_id": f"memory_update_{delta.get('delta_id')}",
                        "update_type": update_type,
                        "target_id": delta.get("target_id") or delta.get("value"),
                        "value": delta.get("value"),
                        "delta_action": delta.get("delta_action", "mentioned_or_preserved"),
                        "source_delta_id": delta.get("delta_id"),
                        "source_delta_type": delta.get("delta_type"),
                        "apply_strategy": self._apply_strategy(update_type=update_type, delta_action=delta.get("delta_action")),
                    }
                )

        for candidate in delta_report.memory_update_candidates:
            candidate_id = candidate.get("candidate_id")
            if candidate_id:
                updates.append(
                    {
                        "update_id": f"memory_update_candidate_{candidate_id}",
                        "update_type": candidate.get("candidate_type", "generic_memory"),
                        "target_id": candidate.get("value"),
                        "value": candidate.get("value"),
                        "delta_action": candidate.get("delta_action", "candidate"),
                        "source_delta_id": candidate.get("source_delta_id"),
                        "source_delta_type": "memory_candidate",
                        "apply_strategy": "merge_candidate",
                    }
                )

        return self._unique_dicts(updates, key="update_id")

    def _conflict_checks(
        self,
        *,
        raw_updates: List[Dict[str, Any]],
        existing_memory_state: Dict[str, Any],
        provenance_record: StoryProvenanceRecord | None,
    ) -> List[Dict[str, Any]]:
        checks = []

        protected_values = set()
        if provenance_record:
            protected_values = {str(item.get("value", "")) for item in provenance_record.protected_elements_snapshot if item.get("value")}

        for update in raw_updates:
            target_id = str(update.get("target_id", ""))
            update_type = update.get("update_type")
            existing_bucket = existing_memory_state.get(update_type, {})
            existing_value = existing_bucket.get(target_id) if isinstance(existing_bucket, dict) else None

            severity = "none"
            conflict_type = "none"
            description = "No conflict detected."

            if existing_value and existing_value != update.get("value"):
                severity = "medium"
                conflict_type = "existing_value_mismatch"
                description = "Existing memory value differs from proposed update."

            if target_id in protected_values and update.get("delta_action") in {"removed", "deleted", "contradicted"}:
                severity = "blocker"
                conflict_type = "protected_element_removal"
                description = "Proposed update would remove or contradict a protected element."

            if provenance_record and not provenance_record.approved_for_memory_update:
                severity = "blocker"
                conflict_type = "unapproved_provenance"
                description = "Provenance is not approved for automatic memory update."

            checks.append(
                {
                    "conflict_check_id": f"conflict_{self._safe_id(update.get('update_id'))}",
                    "update_id": update.get("update_id"),
                    "target_id": target_id,
                    "update_type": update_type,
                    "severity": severity,
                    "conflict_type": conflict_type,
                    "description": description,
                }
            )

        return checks

    def _staged_updates(
        self,
        *,
        raw_updates: List[Dict[str, Any]],
        conflict_checks: List[Dict[str, Any]],
        provenance_record: StoryProvenanceRecord | None,
    ) -> List[Dict[str, Any]]:
        blocker_ids = {item.get("update_id") for item in conflict_checks if item.get("severity") == "blocker"}
        review_ids = {item.get("update_id") for item in conflict_checks if item.get("severity") == "medium"}

        staged = []
        for update in raw_updates:
            if update.get("update_id") in blocker_ids:
                continue
            update = dict(update)
            update["contract_state"] = "review_required" if update.get("update_id") in review_ids else "staged"
            update["approved_by_provenance"] = bool(provenance_record and provenance_record.approved_for_memory_update)
            staged.append(update)

        return staged

    def _blocked_updates(
        self,
        *,
        raw_updates: List[Dict[str, Any]],
        conflict_checks: List[Dict[str, Any]],
        provenance_record: StoryProvenanceRecord | None,
    ) -> List[Dict[str, Any]]:
        checks_by_update = {item.get("update_id"): item for item in conflict_checks}
        blocked = []

        for update in raw_updates:
            check = checks_by_update.get(update.get("update_id"), {})
            if check.get("severity") == "blocker":
                update = dict(update)
                update["contract_state"] = "blocked"
                update["block_reason"] = check.get("description")
                update["conflict_type"] = check.get("conflict_type")
                blocked.append(update)

        return blocked

    def _review_required_updates(
        self,
        *,
        raw_updates: List[Dict[str, Any]],
        conflict_checks: List[Dict[str, Any]],
        provenance_record: StoryProvenanceRecord | None,
    ) -> List[Dict[str, Any]]:
        checks_by_update = {item.get("update_id"): item for item in conflict_checks}
        review = []

        for update in raw_updates:
            check = checks_by_update.get(update.get("update_id"), {})
            if check.get("severity") == "medium":
                update = dict(update)
                update["contract_state"] = "review_required"
                update["review_reason"] = check.get("description")
                update["conflict_type"] = check.get("conflict_type")
                review.append(update)

        return review

    def _approved_for_apply(
        self,
        *,
        staged_updates: List[Dict[str, Any]],
        blocked_updates: List[Dict[str, Any]],
        review_updates: List[Dict[str, Any]],
        provenance_record: StoryProvenanceRecord | None,
    ) -> bool:
        if not provenance_record or not provenance_record.approved_for_memory_update:
            return False
        if blocked_updates or review_updates:
            return False
        return bool(staged_updates)

    def _apply_mode(
        self,
        *,
        approved_for_apply: bool,
        blocked_updates: List[Dict[str, Any]],
        review_updates: List[Dict[str, Any]],
        provenance_record: StoryProvenanceRecord | None,
    ) -> str:
        if approved_for_apply:
            return "auto_apply"
        if blocked_updates:
            return "blocked"
        if review_updates:
            return "manual_review"
        if not provenance_record or not provenance_record.approved_for_memory_update:
            return "staged_pending_provenance"
        return "staged"

    def _contract_status(
        self,
        *,
        approved_for_apply: bool,
        blocked_updates: List[Dict[str, Any]],
        review_updates: List[Dict[str, Any]],
    ) -> str:
        if approved_for_apply:
            return "approved"
        if blocked_updates:
            return "blocked"
        if review_updates:
            return "needs_review"
        return "staged"

    def _filter_updates(self, updates: List[Dict[str, Any]], update_type: str) -> List[Dict[str, Any]]:
        return [item for item in updates if item.get("update_type") == update_type]

    def _apply_strategy(self, *, update_type: str, delta_action: Any) -> str:
        if update_type == "resolved_loop_state":
            return "mark_resolved"
        if update_type == "secret_state" and delta_action == "reveal_or_pressure":
            return "update_reveal_pressure"
        if update_type == "causal_state" and delta_action == "causal_progression":
            return "append_causal_progression"
        if update_type in {"character_state", "relationship_state", "world_state", "object_state"}:
            return "merge_state"
        return "append_observation"

    def _rollback_plan(
        self,
        *,
        staged_updates: List[Dict[str, Any]],
        existing_memory_state: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        rollback = []
        for update in staged_updates:
            update_type = update.get("update_type")
            target_id = update.get("target_id")
            existing_bucket = existing_memory_state.get(update_type, {})
            previous_value = existing_bucket.get(target_id) if isinstance(existing_bucket, dict) else None
            rollback.append(
                {
                    "rollback_id": f"rollback_{self._safe_id(update.get('update_id'))}",
                    "update_id": update.get("update_id"),
                    "update_type": update_type,
                    "target_id": target_id,
                    "previous_value": previous_value,
                    "rollback_action": "restore_previous_value" if previous_value is not None else "remove_new_value",
                }
            )
        return rollback

    def _memory_apply_summary(
        self,
        *,
        raw_updates: List[Dict[str, Any]],
        staged_updates: List[Dict[str, Any]],
        blocked_updates: List[Dict[str, Any]],
        review_updates: List[Dict[str, Any]],
        approved_for_apply: bool,
        apply_mode: str,
    ) -> Dict[str, Any]:
        return {
            "raw_update_count": len(raw_updates),
            "staged_update_count": len(staged_updates),
            "blocked_update_count": len(blocked_updates),
            "review_required_update_count": len(review_updates),
            "approved_for_apply": approved_for_apply,
            "apply_mode": apply_mode,
        }

    def _downstream_constraints(
        self,
        *,
        source_id: str,
        draft_id: str,
        approved_for_apply: bool,
        staged_updates: List[Dict[str, Any]],
        blocked_updates: List[Dict[str, Any]],
        provenance_record: StoryProvenanceRecord | None,
    ) -> Dict[str, Any]:
        return {
            "source_id": source_id,
            "draft_id": draft_id,
            "approved_for_apply": approved_for_apply,
            "staged_update_ids": [item.get("update_id") for item in staged_updates],
            "blocked_update_ids": [item.get("update_id") for item in blocked_updates],
            "provenance_record_id": getattr(provenance_record, "provenance_record_id", None),
            "rules": [
                "Do not auto-apply updates unless approved_for_apply is true.",
                "Blocked updates must never be persisted.",
                "Review-required updates need manual or validator approval.",
                "Rollback plan must be preserved with applied memory updates.",
            ],
        }

    def _warnings(
        self,
        *,
        provenance_record: StoryProvenanceRecord | None,
        blocked_updates: List[Dict[str, Any]],
        review_updates: List[Dict[str, Any]],
        conflict_checks: List[Dict[str, Any]],
    ) -> List[str]:
        warnings = []
        if not provenance_record:
            warnings.append("No provenance record supplied; contract cannot auto-apply.")
        elif not provenance_record.approved_for_memory_update:
            warnings.append("Provenance record is not approved for memory update.")
        if blocked_updates:
            warnings.append(f"{len(blocked_updates)} memory update(s) blocked.")
        if review_updates:
            warnings.append(f"{len(review_updates)} memory update(s) require review.")
        if any(item.get("severity") != "none" for item in conflict_checks):
            warnings.append("One or more memory conflict checks are non-clean.")
        return warnings

    def _safe_id(self, value: Any) -> str:
        return "".join(ch.lower() if ch.isalnum() else "_" for ch in str(value)).strip("_")[:80] or "item"

    def _unique(self, values: List[str]) -> List[str]:
        result = []
        seen = set()
        for value in values:
            if value and value not in seen:
                seen.add(value)
                result.append(value)
        return result

    def _unique_dicts(self, values: List[Dict[str, Any]], *, key: str) -> List[Dict[str, Any]]:
        result = []
        seen = set()
        for value in values:
            marker = value.get(key) or str(value)
            if marker and marker not in seen:
                seen.add(marker)
                result.append(value)
        return result

from typing import Any, Dict, List, Optional


class ConsequenceQueueEngine:
    """Queues and schedules consequences from choices, events, bargains, secrets, and relationships.

    This engine prevents consequences from disappearing. A choice can create:
    immediate effects, delayed fallout, conditional triggers, future scene hooks,
    branch risks, and cascading consequences.
    """

    engine_name = "simulation.consequence_queue_engine"

    CONSEQUENCE_TYPES = {
        "relationship",
        "reputation",
        "knowledge",
        "resource",
        "faction",
        "obligation",
        "leverage",
        "location",
        "timeline",
        "branch",
        "emotional",
        "plot_hook",
        "canon_risk",
    }

    TRIGGER_TYPES = {
        "immediate",
        "after_event_count",
        "at_timeline_tick",
        "when_secret_exposed",
        "when_relationship_threshold_crossed",
        "when_reputation_threshold_crossed",
        "when_location_entered",
        "when_obligation_broken",
        "when_leverage_refused",
        "manual",
    }

    STATUS_VALUES = {
        "queued",
        "ready",
        "triggered",
        "resolved",
        "cancelled",
        "expired",
        "blocked",
    }

    def create_consequence_record(
        self,
        *,
        consequence_id: str,
        consequence_type: str,
        source_event_id: Optional[str],
        source_choice_id: Optional[str],
        summary: str,
        affected_entity_ids: List[str] | None = None,
        trigger_type: str = "immediate",
        trigger_condition: Dict[str, Any] | None = None,
        severity: float = 0.5,
        delay_ticks: int = 0,
        branch_id: Optional[str] = None,
        timeline_id: Optional[str] = None,
        payload: Dict[str, Any] | None = None,
        metadata: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        if consequence_type not in self.CONSEQUENCE_TYPES:
            consequence_type = "plot_hook"
        if trigger_type not in self.TRIGGER_TYPES:
            trigger_type = "manual"

        status = "ready" if trigger_type == "immediate" and delay_ticks <= 0 else "queued"

        return {
            "consequence_id": consequence_id,
            "consequence_type": consequence_type,
            "source_event_id": source_event_id,
            "source_choice_id": source_choice_id,
            "summary": summary,
            "affected_entity_ids": affected_entity_ids or [],
            "trigger_type": trigger_type,
            "trigger_condition": trigger_condition or {},
            "severity": self._bounded(severity),
            "delay_ticks": max(0, int(delay_ticks)),
            "branch_id": branch_id,
            "timeline_id": timeline_id,
            "status": status,
            "created_tick": None,
            "ready_tick": None,
            "triggered_tick": None,
            "resolved_tick": None,
            "payload": payload or {},
            "metadata": metadata or {},
        }

    def register_consequence_on_state(
        self,
        *,
        state: Any,
        consequence_record: Dict[str, Any],
        current_tick: Optional[int] = None,
    ) -> Dict[str, Any]:
        consequence_id = consequence_record["consequence_id"]
        consequence = dict(consequence_record)

        tick = self._current_tick(state, current_tick)
        consequence["created_tick"] = tick
        consequence["ready_tick"] = tick + int(consequence.get("delay_ticks", 0))

        if consequence.get("trigger_type") == "immediate" and consequence.get("delay_ticks", 0) <= 0:
            consequence["status"] = "ready"

        state.metadata.setdefault("consequence_queue", {})[consequence_id] = consequence
        state.metadata.setdefault("consequence_history", []).append(
            {
                "action": "register_consequence",
                "consequence_id": consequence_id,
                "consequence_type": consequence.get("consequence_type"),
                "status": consequence.get("status"),
                "created_tick": tick,
                "ready_tick": consequence.get("ready_tick"),
            }
        )

        return {
            "success": True,
            "engine_name": self.engine_name,
            "consequence_id": consequence_id,
            "updated_state": state,
        }

    def queue_consequences_from_choice_report(
        self,
        *,
        state: Any,
        choice_report: Dict[str, Any],
        current_tick: Optional[int] = None,
    ) -> Dict[str, Any]:
        choice_id = choice_report.get("choice_id")
        actor_id = choice_report.get("actor_id")
        target_id = choice_report.get("target_id")
        action_type = choice_report.get("action_type")
        risk = choice_report.get("risk_profile", {})
        preview = self._preview_from_choice_report(choice_report)

        created = []

        if preview.get("relationship_consequence") and target_id:
            created.append(
                self.create_consequence_record(
                    consequence_id=f"cons_{choice_id}_relationship",
                    consequence_type="relationship",
                    source_event_id=None,
                    source_choice_id=choice_id,
                    summary=f"Relationship fallout from {action_type}.",
                    affected_entity_ids=[actor_id, target_id],
                    trigger_type="immediate",
                    severity=max(0.35, risk.get("emotional_cost", 0.4)),
                    payload={
                        "action_type": action_type,
                        "relationship_pair": [actor_id, target_id],
                    },
                )
            )

        if preview.get("reputation_consequence"):
            created.append(
                self.create_consequence_record(
                    consequence_id=f"cons_{choice_id}_reputation",
                    consequence_type="reputation",
                    source_event_id=None,
                    source_choice_id=choice_id,
                    summary=f"Reputation fallout from {action_type}.",
                    affected_entity_ids=[actor_id],
                    trigger_type="after_event_count",
                    trigger_condition={"event_count": 1},
                    delay_ticks=1,
                    severity=max(0.35, risk.get("social_risk", 0.4)),
                    payload={"action_type": action_type},
                )
            )

        if preview.get("knowledge_consequence"):
            created.append(
                self.create_consequence_record(
                    consequence_id=f"cons_{choice_id}_knowledge",
                    consequence_type="knowledge",
                    source_event_id=None,
                    source_choice_id=choice_id,
                    summary=f"Information spreads because of {action_type}.",
                    affected_entity_ids=[actor_id],
                    trigger_type="after_event_count",
                    trigger_condition={"event_count": 1},
                    delay_ticks=1,
                    severity=max(0.3, risk.get("social_risk", 0.4)),
                    payload={"action_type": action_type},
                )
            )

        if preview.get("branch_consequence"):
            created.append(
                self.create_consequence_record(
                    consequence_id=f"cons_{choice_id}_branch",
                    consequence_type="branch",
                    source_event_id=None,
                    source_choice_id=choice_id,
                    summary=f"Branch-level consequence from {action_type}.",
                    affected_entity_ids=[actor_id] + ([target_id] if target_id else []),
                    trigger_type="manual",
                    severity=max(0.45, risk.get("overall_risk", 0.5)),
                    payload={"action_type": action_type, "requires_branch_review": True},
                )
            )

        registered_ids = []
        for consequence in created:
            result = self.register_consequence_on_state(
                state=state,
                consequence_record=consequence,
                current_tick=current_tick,
            )
            registered_ids.append(result["consequence_id"])

        return {
            "success": True,
            "engine_name": self.engine_name,
            "choice_id": choice_id,
            "registered_consequence_ids": registered_ids,
            "consequence_count": len(registered_ids),
            "updated_state": state,
        }

    def advance_consequence_queue(
        self,
        *,
        state: Any,
        current_tick: Optional[int] = None,
        event_context: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        tick = self._current_tick(state, current_tick)
        context = event_context or {}
        ready_ids = []
        blocked_ids = []
        expired_ids = []

        queue = state.metadata.setdefault("consequence_queue", {})

        for consequence_id, consequence in queue.items():
            if consequence.get("status") not in {"queued", "ready"}:
                continue

            if consequence.get("metadata", {}).get("expires_at_tick") is not None:
                if tick > int(consequence["metadata"]["expires_at_tick"]):
                    consequence["status"] = "expired"
                    expired_ids.append(consequence_id)
                    continue

            if tick < int(consequence.get("ready_tick") or 0):
                continue

            triggered = self._trigger_condition_met(consequence, tick, context, state)

            if triggered:
                consequence["status"] = "ready"
                ready_ids.append(consequence_id)
            elif consequence.get("trigger_type") == "manual":
                blocked_ids.append(consequence_id)

        state.metadata.setdefault("consequence_history", []).append(
            {
                "action": "advance_consequence_queue",
                "tick": tick,
                "ready_ids": ready_ids,
                "blocked_ids": blocked_ids,
                "expired_ids": expired_ids,
            }
        )

        return {
            "success": True,
            "engine_name": self.engine_name,
            "current_tick": tick,
            "ready_consequence_ids": ready_ids,
            "blocked_consequence_ids": blocked_ids,
            "expired_consequence_ids": expired_ids,
            "updated_state": state,
        }

    def mark_consequence_triggered(
        self,
        *,
        state: Any,
        consequence_id: str,
        triggered_tick: Optional[int] = None,
    ) -> Dict[str, Any]:
        consequence = state.metadata.get("consequence_queue", {}).get(consequence_id)
        if not consequence:
            return {
                "success": False,
                "engine_name": self.engine_name,
                "consequence_id": consequence_id,
                "errors": [f"consequence {consequence_id} not found"],
                "updated_state": state,
            }

        tick = self._current_tick(state, triggered_tick)
        consequence["status"] = "triggered"
        consequence["triggered_tick"] = tick

        state.metadata.setdefault("consequence_history", []).append(
            {
                "action": "mark_consequence_triggered",
                "consequence_id": consequence_id,
                "triggered_tick": tick,
            }
        )

        return {
            "success": True,
            "engine_name": self.engine_name,
            "consequence_id": consequence_id,
            "updated_consequence": consequence,
            "updated_state": state,
        }

    def resolve_consequence(
        self,
        *,
        state: Any,
        consequence_id: str,
        resolution_summary: str,
        resolved_tick: Optional[int] = None,
        created_followup_consequences: List[Dict[str, Any]] | None = None,
    ) -> Dict[str, Any]:
        consequence = state.metadata.get("consequence_queue", {}).get(consequence_id)
        if not consequence:
            return {
                "success": False,
                "engine_name": self.engine_name,
                "consequence_id": consequence_id,
                "errors": [f"consequence {consequence_id} not found"],
                "updated_state": state,
            }

        tick = self._current_tick(state, resolved_tick)
        consequence["status"] = "resolved"
        consequence["resolved_tick"] = tick
        consequence["metadata"]["resolution_summary"] = resolution_summary

        followup_ids = []
        for followup in created_followup_consequences or []:
            result = self.register_consequence_on_state(
                state=state,
                consequence_record=followup,
                current_tick=tick,
            )
            followup_ids.append(result["consequence_id"])

        state.metadata.setdefault("consequence_history", []).append(
            {
                "action": "resolve_consequence",
                "consequence_id": consequence_id,
                "resolved_tick": tick,
                "resolution_summary": resolution_summary,
                "followup_ids": followup_ids,
            }
        )

        return {
            "success": True,
            "engine_name": self.engine_name,
            "consequence_id": consequence_id,
            "followup_consequence_ids": followup_ids,
            "updated_consequence": consequence,
            "updated_state": state,
        }

    def cancel_consequence(
        self,
        *,
        state: Any,
        consequence_id: str,
        reason: str = "",
    ) -> Dict[str, Any]:
        consequence = state.metadata.get("consequence_queue", {}).get(consequence_id)
        if not consequence:
            return {
                "success": False,
                "engine_name": self.engine_name,
                "consequence_id": consequence_id,
                "errors": [f"consequence {consequence_id} not found"],
                "updated_state": state,
            }

        consequence["status"] = "cancelled"
        consequence["metadata"]["cancel_reason"] = reason

        state.metadata.setdefault("consequence_history", []).append(
            {
                "action": "cancel_consequence",
                "consequence_id": consequence_id,
                "reason": reason,
            }
        )

        return {
            "success": True,
            "engine_name": self.engine_name,
            "consequence_id": consequence_id,
            "updated_consequence": consequence,
            "updated_state": state,
        }

    def build_consequence_map(self, *, state: Any) -> Dict[str, Any]:
        queue = state.metadata.get("consequence_queue", {})
        records = {}

        for consequence_id, consequence in queue.items():
            records[consequence_id] = {
                "consequence_id": consequence_id,
                "consequence_type": consequence.get("consequence_type"),
                "source_event_id": consequence.get("source_event_id"),
                "source_choice_id": consequence.get("source_choice_id"),
                "summary": consequence.get("summary"),
                "affected_entity_ids": consequence.get("affected_entity_ids", []),
                "trigger_type": consequence.get("trigger_type"),
                "status": consequence.get("status"),
                "severity": consequence.get("severity"),
                "created_tick": consequence.get("created_tick"),
                "ready_tick": consequence.get("ready_tick"),
                "triggered_tick": consequence.get("triggered_tick"),
                "resolved_tick": consequence.get("resolved_tick"),
                "branch_id": consequence.get("branch_id"),
                "timeline_id": consequence.get("timeline_id"),
                "future_scene_hook": self._future_scene_hook(consequence),
            }

        return {
            "success": True,
            "engine_name": self.engine_name,
            "consequence_count": len(records),
            "consequence_records": records,
            "summary": self._queue_summary(records),
            "warnings": self._queue_warnings(records),
        }

    def get_ready_consequences(self, *, state: Any) -> Dict[str, Any]:
        records = {
            consequence_id: consequence
            for consequence_id, consequence in state.metadata.get("consequence_queue", {}).items()
            if consequence.get("status") == "ready"
        }

        return {
            "success": True,
            "engine_name": self.engine_name,
            "ready_count": len(records),
            "ready_consequences": records,
        }

    def _trigger_condition_met(
        self,
        consequence: Dict[str, Any],
        tick: int,
        context: Dict[str, Any],
        state: Any,
    ) -> bool:
        trigger_type = consequence.get("trigger_type")
        condition = consequence.get("trigger_condition", {})

        if trigger_type == "immediate":
            return True

        if trigger_type == "after_event_count":
            required = int(condition.get("event_count", 1))
            current = int(context.get("event_count_since_source", required))
            return current >= required

        if trigger_type == "at_timeline_tick":
            target_tick = int(condition.get("tick", consequence.get("ready_tick", tick)))
            return tick >= target_tick

        if trigger_type == "when_secret_exposed":
            secret_id = condition.get("secret_id")
            registry = state.metadata.get("secret_registry", {})
            return bool(secret_id and registry.get(secret_id, {}).get("exposed"))

        if trigger_type == "when_relationship_threshold_crossed":
            relationship_id = condition.get("relationship_id")
            metric = condition.get("metric")
            threshold = float(condition.get("threshold", 0.0))
            direction = condition.get("direction", "gte")
            rel = state.relationship_states.get(relationship_id)
            if not rel or not hasattr(rel, metric):
                return False
            value = float(getattr(rel, metric))
            return value >= threshold if direction == "gte" else value <= threshold

        if trigger_type == "when_reputation_threshold_crossed":
            character_id = condition.get("character_id")
            audience_type = condition.get("audience_type", "public")
            threshold = float(condition.get("threshold", 0.0))
            direction = condition.get("direction", "lte")
            char = state.character_states.get(character_id)
            if not char:
                return False
            value = float(char.metadata.get("reputation_state", {}).get(audience_type, 0.0))
            return value <= threshold if direction == "lte" else value >= threshold

        if trigger_type == "when_location_entered":
            character_id = condition.get("character_id")
            location_id = condition.get("location_id")
            char = state.character_states.get(character_id)
            return bool(char and char.current_location_id == location_id)

        if trigger_type == "when_obligation_broken":
            obligation_id = condition.get("obligation_id")
            obligation = state.metadata.get("obligation_registry", {}).get(obligation_id, {})
            return obligation.get("status") == "broken"

        if trigger_type == "when_leverage_refused":
            leverage_id = condition.get("leverage_id")
            leverage = state.metadata.get("leverage_registry", {}).get(leverage_id, {})
            return leverage.get("status") == "refused"

        return False

    def _preview_from_choice_report(self, choice_report: Dict[str, Any]) -> Dict[str, Any]:
        preview = choice_report.get("consequence_preview")
        if preview:
            return preview
        return choice_report.get("chunk5_handoff", {}).get("consequence_preview", {}) or {
            "relationship_consequence": choice_report.get("action_type") in {"betray", "protect", "repair_relationship", "forgive", "resist_blackmail"},
            "reputation_consequence": choice_report.get("action_type") in {"expose_secret", "spread_rumor", "attempt_blackmail"},
            "knowledge_consequence": choice_report.get("action_type") in {"expose_secret", "spread_rumor", "attempt_blackmail"},
            "branch_consequence": choice_report.get("action_type") in {"sacrifice", "break_oath", "accept_bargain", "reject_bargain"},
        }

    def _future_scene_hook(self, consequence: Dict[str, Any]) -> Dict[str, Any]:
        ctype = consequence.get("consequence_type")
        severity = float(consequence.get("severity", 0.5))

        scene_type = {
            "relationship": "relationship_fallout_scene",
            "reputation": "public_reaction_scene",
            "knowledge": "information_spread_scene",
            "resource": "resource_cost_scene",
            "faction": "faction_response_scene",
            "obligation": "promise_consequence_scene",
            "leverage": "coercion_fallout_scene",
            "branch": "branch_point_review_scene",
            "emotional": "emotional_carryover_scene",
            "plot_hook": "future_hook_scene",
        }.get(ctype, "consequence_scene")

        return {
            "scene_type": scene_type,
            "priority": "high" if severity >= 0.7 else "medium" if severity >= 0.4 else "low",
            "summary": consequence.get("summary"),
            "affected_entity_ids": consequence.get("affected_entity_ids", []),
        }

    def _queue_summary(self, records: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        statuses: Dict[str, int] = {}
        types: Dict[str, int] = {}

        for record in records.values():
            statuses[record["status"]] = statuses.get(record["status"], 0) + 1
            types[record["consequence_type"]] = types.get(record["consequence_type"], 0) + 1

        return {
            "status_counts": statuses,
            "type_counts": types,
            "ready_count": statuses.get("ready", 0),
            "queued_count": statuses.get("queued", 0),
            "unresolved_count": sum(count for status, count in statuses.items() if status in {"queued", "ready", "triggered", "blocked"}),
        }

    def _queue_warnings(self, records: Dict[str, Dict[str, Any]]) -> List[str]:
        warnings = []
        summary = self._queue_summary(records)

        if summary["unresolved_count"] > 20:
            warnings.append("many unresolved consequences; consider resolving or grouping fallout")
        if summary["ready_count"] > 8:
            warnings.append("many ready consequences; next scene may be overloaded")
        for consequence_id, record in records.items():
            if record["severity"] >= 0.8 and record["status"] == "queued":
                warnings.append(f"{consequence_id} is high severity and still queued")
        return warnings

    def _current_tick(self, state: Any, current_tick: Optional[int]) -> int:
        if current_tick is not None:
            return int(current_tick)
        return int(state.metadata.get("current_tick", 0))

    def _bounded(self, value: float) -> float:
        return round(max(0.0, min(1.0, float(value))), 3)

from typing import Any, Dict, List, Optional


class ConflictResolutionEngine:
    """Models conflict creation, escalation, de-escalation, and resolution.

    This engine tracks conflicts as persistent story objects. A conflict can be
    emotional, social, political, romantic, moral, factional, truth-based, or
    branch-level. It can escalate, soften, resolve, compromise, or stay open.
    """

    engine_name = "simulation.conflict_resolution_engine"

    CONFLICT_TYPES = {
        "relationship",
        "faction",
        "truth",
        "moral",
        "romantic",
        "social",
        "resource",
        "legal",
        "identity",
        "agency",
        "branch",
        "world",
    }

    CONFLICT_STATUS_VALUES = {
        "active",
        "escalated",
        "deescalated",
        "compromised",
        "resolved",
        "unresolved",
        "suppressed",
        "transformed",
    }

    OUTCOME_TYPES = {
        "win_loss",
        "compromise",
        "mutual_loss",
        "mutual_gain",
        "temporary_truce",
        "avoidance",
        "sacrifice",
        "truth_reveal",
        "relationship_break",
        "relationship_repair",
        "power_shift",
        "open_wound",
    }

    def create_conflict_record(
        self,
        *,
        conflict_id: str,
        conflict_type: str,
        title: str,
        participant_ids: List[str],
        source_event_id: Optional[str] = None,
        source_choice_id: Optional[str] = None,
        source_consequence_id: Optional[str] = None,
        core_issue: str = "",
        opposing_goals: Dict[str, str] | None = None,
        linked_secret_ids: List[str] | None = None,
        linked_evidence_ids: List[str] | None = None,
        linked_obligation_ids: List[str] | None = None,
        linked_leverage_ids: List[str] | None = None,
        linked_bargain_ids: List[str] | None = None,
        linked_faction_ids: List[str] | None = None,
        intensity: float = 0.5,
        stakes_score: float = 0.5,
        tension_score: float = 0.5,
        moral_complexity: float = 0.4,
        metadata: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        if conflict_type not in self.CONFLICT_TYPES:
            conflict_type = "relationship"

        conflict_pressure = self._conflict_pressure(
            intensity=intensity,
            stakes_score=stakes_score,
            tension_score=tension_score,
            moral_complexity=moral_complexity,
            link_count=len(linked_secret_ids or [])
            + len(linked_evidence_ids or [])
            + len(linked_obligation_ids or [])
            + len(linked_leverage_ids or [])
            + len(linked_bargain_ids or []),
        )

        return {
            "conflict_id": conflict_id,
            "conflict_type": conflict_type,
            "title": title,
            "participant_ids": participant_ids,
            "source_event_id": source_event_id,
            "source_choice_id": source_choice_id,
            "source_consequence_id": source_consequence_id,
            "core_issue": core_issue,
            "opposing_goals": opposing_goals or {},
            "linked_secret_ids": linked_secret_ids or [],
            "linked_evidence_ids": linked_evidence_ids or [],
            "linked_obligation_ids": linked_obligation_ids or [],
            "linked_leverage_ids": linked_leverage_ids or [],
            "linked_bargain_ids": linked_bargain_ids or [],
            "linked_faction_ids": linked_faction_ids or [],
            "intensity": self._bounded(intensity),
            "stakes_score": self._bounded(stakes_score),
            "tension_score": self._bounded(tension_score),
            "moral_complexity": self._bounded(moral_complexity),
            "conflict_pressure": conflict_pressure,
            "status": "active",
            "escalation_history": [],
            "deescalation_history": [],
            "resolution_history": [],
            "unresolved_threads": [],
            "metadata": metadata or {},
        }

    def register_conflict_on_state(
        self,
        *,
        state: Any,
        conflict_record: Dict[str, Any],
    ) -> Dict[str, Any]:
        conflict_id = conflict_record["conflict_id"]
        state.metadata.setdefault("conflict_registry", {})[conflict_id] = dict(conflict_record)
        state.metadata.setdefault("conflict_history", []).append(
            {
                "action": "register_conflict",
                "conflict_id": conflict_id,
                "conflict_type": conflict_record.get("conflict_type"),
                "participant_ids": conflict_record.get("participant_ids", []),
                "conflict_pressure": conflict_record.get("conflict_pressure"),
                "status": conflict_record.get("status"),
            }
        )

        for participant_id in conflict_record.get("participant_ids", []):
            if participant_id in state.character_states:
                state.character_states[participant_id].metadata.setdefault("conflict_ids", [])
                state.character_states[participant_id].metadata["conflict_ids"] = self._unique(
                    state.character_states[participant_id].metadata["conflict_ids"] + [conflict_id]
                )

        return {
            "success": True,
            "engine_name": self.engine_name,
            "conflict_id": conflict_id,
            "updated_state": state,
        }

    def evaluate_conflict(
        self,
        *,
        state: Any,
        conflict_id: str,
    ) -> Dict[str, Any]:
        conflict = state.metadata.get("conflict_registry", {}).get(conflict_id)
        if not conflict:
            return {
                "success": False,
                "engine_name": self.engine_name,
                "conflict_id": conflict_id,
                "errors": [f"conflict {conflict_id} not found"],
            }

        participant_reports = []
        for participant_id in conflict.get("participant_ids", []):
            participant_reports.append(self._participant_conflict_position(state, conflict, participant_id))

        escalation_risk = self._escalation_risk(conflict, participant_reports)
        resolution_readiness = self._resolution_readiness(conflict, participant_reports)
        compromise_potential = self._compromise_potential(conflict, participant_reports)

        return {
            "success": True,
            "engine_name": self.engine_name,
            "conflict_id": conflict_id,
            "conflict_type": conflict.get("conflict_type"),
            "status": conflict.get("status"),
            "conflict_pressure": conflict.get("conflict_pressure"),
            "participant_reports": participant_reports,
            "escalation_risk": escalation_risk,
            "resolution_readiness": resolution_readiness,
            "compromise_potential": compromise_potential,
            "recommended_next_state": self._recommended_next_state(escalation_risk, resolution_readiness, compromise_potential),
            "warnings": self._evaluation_warnings(conflict, escalation_risk, resolution_readiness, compromise_potential),
        }

    def escalate_conflict(
        self,
        *,
        state: Any,
        conflict_id: str,
        escalation_event_id: Optional[str] = None,
        escalation_reason: str = "",
        escalation_amount: float = 0.15,
    ) -> Dict[str, Any]:
        conflict = state.metadata.get("conflict_registry", {}).get(conflict_id)
        if not conflict:
            return self._missing_conflict(conflict_id)

        conflict["status"] = "escalated"
        conflict["intensity"] = self._bounded(float(conflict.get("intensity", 0.5)) + escalation_amount)
        conflict["tension_score"] = self._bounded(float(conflict.get("tension_score", 0.5)) + escalation_amount * 0.8)
        conflict["conflict_pressure"] = self._conflict_pressure(
            intensity=conflict["intensity"],
            stakes_score=conflict.get("stakes_score", 0.5),
            tension_score=conflict["tension_score"],
            moral_complexity=conflict.get("moral_complexity", 0.4),
            link_count=self._link_count(conflict),
        )
        conflict["escalation_history"] = self._unique(
            conflict.get("escalation_history", [])
            + [
                {
                    "event_id": escalation_event_id,
                    "reason": escalation_reason,
                    "escalation_amount": self._bounded(escalation_amount),
                    "new_pressure": conflict["conflict_pressure"],
                }
            ]
        )

        state.metadata.setdefault("conflict_history", []).append(
            {
                "action": "escalate_conflict",
                "conflict_id": conflict_id,
                "event_id": escalation_event_id,
                "new_pressure": conflict["conflict_pressure"],
            }
        )

        return {
            "success": True,
            "engine_name": self.engine_name,
            "conflict_id": conflict_id,
            "updated_conflict": conflict,
            "updated_state": state,
        }

    def deescalate_conflict(
        self,
        *,
        state: Any,
        conflict_id: str,
        deescalation_event_id: Optional[str] = None,
        deescalation_reason: str = "",
        deescalation_amount: float = 0.15,
    ) -> Dict[str, Any]:
        conflict = state.metadata.get("conflict_registry", {}).get(conflict_id)
        if not conflict:
            return self._missing_conflict(conflict_id)

        conflict["status"] = "deescalated"
        conflict["intensity"] = self._bounded(float(conflict.get("intensity", 0.5)) - deescalation_amount)
        conflict["tension_score"] = self._bounded(float(conflict.get("tension_score", 0.5)) - deescalation_amount * 0.8)
        conflict["conflict_pressure"] = self._conflict_pressure(
            intensity=conflict["intensity"],
            stakes_score=conflict.get("stakes_score", 0.5),
            tension_score=conflict["tension_score"],
            moral_complexity=conflict.get("moral_complexity", 0.4),
            link_count=self._link_count(conflict),
        )
        conflict["deescalation_history"] = self._unique(
            conflict.get("deescalation_history", [])
            + [
                {
                    "event_id": deescalation_event_id,
                    "reason": deescalation_reason,
                    "deescalation_amount": self._bounded(deescalation_amount),
                    "new_pressure": conflict["conflict_pressure"],
                }
            ]
        )

        state.metadata.setdefault("conflict_history", []).append(
            {
                "action": "deescalate_conflict",
                "conflict_id": conflict_id,
                "event_id": deescalation_event_id,
                "new_pressure": conflict["conflict_pressure"],
            }
        )

        return {
            "success": True,
            "engine_name": self.engine_name,
            "conflict_id": conflict_id,
            "updated_conflict": conflict,
            "updated_state": state,
        }

    def resolve_conflict(
        self,
        *,
        state: Any,
        conflict_id: str,
        outcome_type: str,
        resolution_event_id: Optional[str] = None,
        winner_ids: List[str] | None = None,
        loser_ids: List[str] | None = None,
        compromise_terms: List[str] | None = None,
        unresolved_threads: List[str] | None = None,
        resolution_summary: str = "",
    ) -> Dict[str, Any]:
        conflict = state.metadata.get("conflict_registry", {}).get(conflict_id)
        if not conflict:
            return self._missing_conflict(conflict_id)

        if outcome_type not in self.OUTCOME_TYPES:
            outcome_type = "open_wound"

        if outcome_type in {"compromise", "temporary_truce"}:
            conflict["status"] = "compromised"
        elif outcome_type in {"open_wound", "avoidance"}:
            conflict["status"] = "unresolved"
        elif outcome_type in {"relationship_repair", "mutual_gain", "truth_reveal"}:
            conflict["status"] = "resolved"
        elif outcome_type in {"relationship_break", "mutual_loss", "power_shift", "win_loss"}:
            conflict["status"] = "transformed"
        else:
            conflict["status"] = "resolved"

        conflict["unresolved_threads"] = self._unique(conflict.get("unresolved_threads", []) + (unresolved_threads or []))
        conflict["resolution_history"] = self._unique(
            conflict.get("resolution_history", [])
            + [
                {
                    "event_id": resolution_event_id,
                    "outcome_type": outcome_type,
                    "winner_ids": winner_ids or [],
                    "loser_ids": loser_ids or [],
                    "compromise_terms": compromise_terms or [],
                    "unresolved_threads": unresolved_threads or [],
                    "resolution_summary": resolution_summary,
                }
            ]
        )

        pressure_reduction = self._resolution_pressure_reduction(outcome_type)
        conflict["conflict_pressure"] = self._bounded(float(conflict.get("conflict_pressure", 0.5)) - pressure_reduction)
        conflict["intensity"] = self._bounded(float(conflict.get("intensity", 0.5)) - pressure_reduction * 0.7)

        state.metadata.setdefault("conflict_history", []).append(
            {
                "action": "resolve_conflict",
                "conflict_id": conflict_id,
                "outcome_type": outcome_type,
                "status": conflict["status"],
            }
        )

        return {
            "success": True,
            "engine_name": self.engine_name,
            "conflict_id": conflict_id,
            "outcome_type": outcome_type,
            "updated_conflict": conflict,
            "resolution_consequences": self._resolution_consequences(conflict, outcome_type, winner_ids or [], loser_ids or []),
            "chunk5_handoff": self._chunk5_handoff(conflict),
            "updated_state": state,
        }

    def generate_resolution_options(
        self,
        *,
        state: Any,
        conflict_id: str,
    ) -> Dict[str, Any]:
        evaluation = self.evaluate_conflict(state=state, conflict_id=conflict_id)
        if not evaluation.get("success"):
            return evaluation

        conflict = state.metadata["conflict_registry"][conflict_id]
        options = []

        if evaluation["compromise_potential"] >= 0.35:
            options.append(
                {
                    "outcome_type": "compromise",
                    "label": "Compromise",
                    "fit_score": evaluation["compromise_potential"],
                    "cost": "both sides lose something but conflict pressure drops",
                }
            )

        if evaluation["resolution_readiness"] >= 0.45:
            options.append(
                {
                    "outcome_type": "truth_reveal" if conflict.get("conflict_type") == "truth" else "relationship_repair",
                    "label": "Direct resolution",
                    "fit_score": evaluation["resolution_readiness"],
                    "cost": "requires vulnerability or evidence",
                }
            )

        if evaluation["escalation_risk"] >= 0.45:
            options.append(
                {
                    "outcome_type": "power_shift",
                    "label": "Escalate into power shift",
                    "fit_score": evaluation["escalation_risk"],
                    "cost": "creates winners, losers, and aftermath",
                }
            )

        options.append(
            {
                "outcome_type": "open_wound",
                "label": "Leave unresolved",
                "fit_score": max(0.1, 1.0 - evaluation["resolution_readiness"]),
                "cost": "keeps future tension alive",
            }
        )

        options = sorted(options, key=lambda item: item["fit_score"], reverse=True)

        return {
            "success": True,
            "engine_name": self.engine_name,
            "conflict_id": conflict_id,
            "options": options,
            "recommended_option": options[0],
            "evaluation": evaluation,
        }

    def build_conflict_map(self, *, state: Any) -> Dict[str, Any]:
        registry = state.metadata.get("conflict_registry", {})
        records = {}

        for conflict_id, conflict in registry.items():
            records[conflict_id] = {
                "conflict_id": conflict_id,
                "conflict_type": conflict.get("conflict_type"),
                "title": conflict.get("title"),
                "participant_ids": conflict.get("participant_ids", []),
                "status": conflict.get("status"),
                "conflict_pressure": conflict.get("conflict_pressure"),
                "intensity": conflict.get("intensity"),
                "stakes_score": conflict.get("stakes_score"),
                "tension_score": conflict.get("tension_score"),
                "moral_complexity": conflict.get("moral_complexity"),
                "unresolved_thread_count": len(conflict.get("unresolved_threads", [])),
                "resolution_count": len(conflict.get("resolution_history", [])),
            }

        ranked = sorted(records.values(), key=lambda item: item.get("conflict_pressure", 0.0), reverse=True)

        return {
            "success": True,
            "engine_name": self.engine_name,
            "conflict_count": len(records),
            "conflict_records": records,
            "ranked_conflicts": ranked,
            "highest_pressure_conflict": ranked[0] if ranked else None,
            "warnings": self._map_warnings(ranked),
        }

    def _participant_conflict_position(self, state: Any, conflict: Dict[str, Any], participant_id: str) -> Dict[str, Any]:
        goal = conflict.get("opposing_goals", {}).get(participant_id, "")
        relationship_pressure = 0.0
        social_pressure = 0.0

        for rel in state.relationship_states.values():
            if participant_id in {rel.character_a_id, rel.character_b_id}:
                if any(other in {rel.character_a_id, rel.character_b_id} for other in conflict.get("participant_ids", []) if other != participant_id):
                    relationship_pressure += rel.resentment * 0.25 + rel.rivalry * 0.20 + rel.betrayal_risk * 0.20 + rel.fear * 0.15

        character = state.character_states.get(participant_id)
        if character:
            reputation = character.metadata.get("reputation_state", {})
            social_pressure = max(0.0, 0.5 - float(reputation.get("public", reputation.get("general", 0.5)) or 0.5))

        leverage_pressure = 0.0
        for leverage in state.metadata.get("leverage_registry", {}).values():
            if leverage.get("target_id") == participant_id and leverage.get("status") == "active":
                leverage_pressure += float(leverage.get("pressure_level", 0.5)) * 0.25

        obligation_pressure = 0.0
        for obligation in state.metadata.get("obligation_registry", {}).values():
            if participant_id in {obligation.get("promiser_id"), obligation.get("promisee_id")} and obligation.get("status") == "active":
                obligation_pressure += float(obligation.get("pressure_score", 0.5)) * 0.12

        pressure = self._bounded(relationship_pressure + social_pressure * 0.15 + leverage_pressure + obligation_pressure)

        return {
            "participant_id": participant_id,
            "goal": goal,
            "relationship_pressure": round(min(1.0, relationship_pressure), 3),
            "social_pressure": round(min(1.0, social_pressure), 3),
            "leverage_pressure": round(min(1.0, leverage_pressure), 3),
            "obligation_pressure": round(min(1.0, obligation_pressure), 3),
            "total_position_pressure": pressure,
        }

    def _escalation_risk(self, conflict: Dict[str, Any], participant_reports: List[Dict[str, Any]]) -> float:
        participant_pressure = self._average([p["total_position_pressure"] for p in participant_reports])
        unresolved_bonus = min(0.20, len(conflict.get("unresolved_threads", [])) * 0.05)
        link_bonus = min(0.20, self._link_count(conflict) * 0.03)

        return round(
            min(
                1.0,
                float(conflict.get("conflict_pressure", 0.5)) * 0.42
                + float(conflict.get("tension_score", 0.5)) * 0.20
                + participant_pressure * 0.22
                + unresolved_bonus
                + link_bonus,
            ),
            3,
        )

    def _resolution_readiness(self, conflict: Dict[str, Any], participant_reports: List[Dict[str, Any]]) -> float:
        pressure = float(conflict.get("conflict_pressure", 0.5))
        moral = float(conflict.get("moral_complexity", 0.4))
        participant_pressure = self._average([p["total_position_pressure"] for p in participant_reports])
        resolution_history_bonus = min(0.12, len(conflict.get("deescalation_history", [])) * 0.04)

        return round(
            max(
                0.0,
                min(
                    1.0,
                    0.55
                    - pressure * 0.24
                    + moral * 0.16
                    - participant_pressure * 0.12
                    + resolution_history_bonus,
                ),
            ),
            3,
        )

    def _compromise_potential(self, conflict: Dict[str, Any], participant_reports: List[Dict[str, Any]]) -> float:
        if len(participant_reports) < 2:
            return 0.1

        pressures = [p["total_position_pressure"] for p in participant_reports]
        pressure_spread = max(pressures) - min(pressures)
        moral = float(conflict.get("moral_complexity", 0.4))
        conflict_type = conflict.get("conflict_type")

        type_bonus = 0.12 if conflict_type in {"relationship", "romantic", "moral", "resource", "legal"} else 0.04

        return round(
            max(
                0.0,
                min(
                    1.0,
                    0.38
                    + moral * 0.18
                    + type_bonus
                    - pressure_spread * 0.20
                    - float(conflict.get("intensity", 0.5)) * 0.10,
                ),
            ),
            3,
        )

    def _recommended_next_state(self, escalation_risk: float, resolution_readiness: float, compromise_potential: float) -> str:
        if escalation_risk >= 0.65 and resolution_readiness < 0.4:
            return "escalate"
        if resolution_readiness >= 0.55:
            return "resolve"
        if compromise_potential >= 0.5:
            return "compromise"
        return "leave_unresolved"

    def _resolution_pressure_reduction(self, outcome_type: str) -> float:
        return {
            "win_loss": 0.18,
            "compromise": 0.28,
            "mutual_loss": 0.16,
            "mutual_gain": 0.35,
            "temporary_truce": 0.18,
            "avoidance": 0.08,
            "sacrifice": 0.24,
            "truth_reveal": 0.30,
            "relationship_break": 0.14,
            "relationship_repair": 0.34,
            "power_shift": 0.12,
            "open_wound": 0.04,
        }.get(outcome_type, 0.12)

    def _resolution_consequences(
        self,
        conflict: Dict[str, Any],
        outcome_type: str,
        winner_ids: List[str],
        loser_ids: List[str],
    ) -> List[Dict[str, Any]]:
        consequences = []

        if outcome_type in {"relationship_break", "open_wound", "mutual_loss"}:
            consequences.append(
                {
                    "consequence_type": "relationship",
                    "summary": "Conflict resolution leaves relationship damage.",
                    "affected_entity_ids": conflict.get("participant_ids", []),
                    "severity": max(0.45, conflict.get("conflict_pressure", 0.5)),
                }
            )

        if outcome_type in {"truth_reveal", "power_shift", "win_loss"}:
            consequences.append(
                {
                    "consequence_type": "reputation",
                    "summary": "Conflict outcome changes public/social standing.",
                    "affected_entity_ids": winner_ids + loser_ids,
                    "severity": max(0.40, conflict.get("stakes_score", 0.5)),
                }
            )

        if outcome_type in {"compromise", "temporary_truce", "relationship_repair"}:
            consequences.append(
                {
                    "consequence_type": "plot_hook",
                    "summary": "Conflict resolution creates a future trust test.",
                    "affected_entity_ids": conflict.get("participant_ids", []),
                    "severity": 0.45,
                }
            )

        return consequences

    def _chunk5_handoff(self, conflict: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "conflict_id": conflict.get("conflict_id"),
            "scene_type": self._scene_type(conflict),
            "status": conflict.get("status"),
            "conflict_pressure": conflict.get("conflict_pressure"),
            "participant_ids": conflict.get("participant_ids", []),
            "core_issue": conflict.get("core_issue"),
            "must_show_opposing_goals": bool(conflict.get("opposing_goals")),
            "must_show_cost": conflict.get("conflict_pressure", 0.0) >= 0.45,
            "must_leave_thread": conflict.get("status") in {"unresolved", "suppressed", "transformed"},
            "unresolved_threads": conflict.get("unresolved_threads", []),
        }

    def _scene_type(self, conflict: Dict[str, Any]) -> str:
        mapping = {
            "relationship": "relationship_conflict_scene",
            "faction": "faction_conflict_scene",
            "truth": "truth_conflict_scene",
            "moral": "moral_conflict_scene",
            "romantic": "romantic_conflict_scene",
            "social": "social_status_conflict_scene",
            "resource": "resource_conflict_scene",
            "legal": "trial_or_legal_conflict_scene",
            "identity": "identity_conflict_scene",
            "agency": "coercion_agency_conflict_scene",
            "branch": "branch_conflict_scene",
            "world": "world_conflict_scene",
        }
        return mapping.get(conflict.get("conflict_type"), "conflict_scene")

    def _evaluation_warnings(self, conflict: Dict[str, Any], escalation: float, readiness: float, compromise: float) -> List[str]:
        warnings = []
        if escalation >= 0.75:
            warnings.append("conflict has high escalation risk")
        if readiness < 0.25 and compromise < 0.25:
            warnings.append("conflict may be difficult to resolve believably")
        if conflict.get("conflict_pressure", 0.0) < 0.25:
            warnings.append("conflict pressure is low; may feel weak")
        return warnings

    def _map_warnings(self, ranked: List[Dict[str, Any]]) -> List[str]:
        warnings = []
        unresolved = [item for item in ranked if item.get("status") in {"active", "escalated", "unresolved"}]
        if len(unresolved) > 12:
            warnings.append("many unresolved conflicts; story may feel cluttered")
        if ranked and ranked[0].get("conflict_pressure", 0.0) >= 0.85:
            warnings.append("top conflict is extremely high pressure")
        if not ranked:
            warnings.append("no conflicts registered")
        return warnings

    def _conflict_pressure(
        self,
        *,
        intensity: float,
        stakes_score: float,
        tension_score: float,
        moral_complexity: float,
        link_count: int,
    ) -> float:
        return round(
            min(
                1.0,
                self._bounded(intensity) * 0.30
                + self._bounded(stakes_score) * 0.25
                + self._bounded(tension_score) * 0.25
                + self._bounded(moral_complexity) * 0.12
                + min(0.16, link_count * 0.025),
            ),
            3,
        )

    def _link_count(self, conflict: Dict[str, Any]) -> int:
        return (
            len(conflict.get("linked_secret_ids", []))
            + len(conflict.get("linked_evidence_ids", []))
            + len(conflict.get("linked_obligation_ids", []))
            + len(conflict.get("linked_leverage_ids", []))
            + len(conflict.get("linked_bargain_ids", []))
            + len(conflict.get("linked_faction_ids", []))
        )

    def _missing_conflict(self, conflict_id: str) -> Dict[str, Any]:
        return {
            "success": False,
            "engine_name": self.engine_name,
            "conflict_id": conflict_id,
            "errors": [f"conflict {conflict_id} not found"],
        }

    def _average(self, values: List[float]) -> float:
        if not values:
            return 0.0
        return round(sum(values) / len(values), 3)

    def _bounded(self, value: float) -> float:
        return round(max(0.0, min(1.0, float(value))), 3)

    def _unique(self, values: List[Any]) -> List[Any]:
        result = []
        seen = set()
        for value in values:
            key = str(value)
            if key not in seen:
                seen.add(key)
                result.append(value)
        return result

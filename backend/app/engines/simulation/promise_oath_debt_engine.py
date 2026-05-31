from copy import deepcopy
from typing import Any, Dict, List, Optional

from backend.app.schemas.simulation import (
    DeltaBatch,
    DeltaOperation,
    RelationshipDelta,
    ReputationDelta,
    SimulationEventPayload,
    SimulationState,
)


class PromiseOathDebtEngine:
    """Tracks promises, oaths, vows, favors, debts, and their consequences.

    This engine makes emotional/social obligations persistent. A promise is not
    just dialogue; it becomes state that can later be fulfilled, broken, delayed,
    weaponized, forgiven, or used as leverage.
    """

    engine_name = "simulation.promise_oath_debt_engine"

    OBLIGATION_TYPES = {
        "promise",
        "oath",
        "vow",
        "favor_debt",
        "life_debt",
        "blood_debt",
        "contract",
        "romantic_promise",
        "political_pact",
        "mentor_vow",
        "family_obligation",
    }

    STATUS_VALUES = {
        "active",
        "fulfilled",
        "partially_fulfilled",
        "broken",
        "forgiven",
        "weaponized",
        "expired",
        "cancelled",
    }

    def create_obligation_record(
        self,
        *,
        obligation_id: str,
        obligation_type: str,
        promiser_id: str,
        promisee_id: str,
        summary: str,
        terms: List[str] | None = None,
        source_event_id: Optional[str] = None,
        witness_ids: List[str] | None = None,
        involved_faction_ids: List[str] | None = None,
        linked_secret_ids: List[str] | None = None,
        linked_evidence_ids: List[str] | None = None,
        emotional_weight: float = 0.5,
        legal_weight: float = 0.0,
        magical_weight: float = 0.0,
        social_weight: float = 0.5,
        due_condition: Optional[str] = None,
        breach_condition: Optional[str] = None,
        metadata: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        if obligation_type not in self.OBLIGATION_TYPES:
            obligation_type = "promise"

        return {
            "obligation_id": obligation_id,
            "obligation_type": obligation_type,
            "promiser_id": promiser_id,
            "promisee_id": promisee_id,
            "summary": summary,
            "terms": terms or [],
            "source_event_id": source_event_id,
            "witness_ids": witness_ids or [],
            "involved_faction_ids": involved_faction_ids or [],
            "linked_secret_ids": linked_secret_ids or [],
            "linked_evidence_ids": linked_evidence_ids or [],
            "emotional_weight": self._bounded(emotional_weight),
            "legal_weight": self._bounded(legal_weight),
            "magical_weight": self._bounded(magical_weight),
            "social_weight": self._bounded(social_weight),
            "due_condition": due_condition,
            "breach_condition": breach_condition,
            "status": "active",
            "fulfillment_event_ids": [],
            "breach_event_ids": [],
            "forgiveness_event_ids": [],
            "debt_balance": self._initial_debt_balance(obligation_type, emotional_weight, legal_weight, magical_weight, social_weight),
            "pressure_score": self._pressure_score(emotional_weight, legal_weight, magical_weight, social_weight),
            "metadata": metadata or {},
        }

    def register_obligation_on_state(
        self,
        *,
        state: SimulationState,
        obligation_record: Dict[str, Any],
    ) -> Dict[str, Any]:
        obligation_id = obligation_record["obligation_id"]
        obligation_record = deepcopy(obligation_record)
        state.metadata.setdefault("obligation_registry", {})[obligation_id] = obligation_record

        for character_id in [obligation_record["promiser_id"], obligation_record["promisee_id"]]:
            if character_id in state.character_states:
                state.character_states[character_id].metadata.setdefault("obligation_ids", [])
                state.character_states[character_id].metadata["obligation_ids"] = self._unique(
                    state.character_states[character_id].metadata["obligation_ids"] + [obligation_id]
                )

        state.metadata.setdefault("obligation_history", []).append(
            {
                "action": "register_obligation",
                "obligation_id": obligation_id,
                "promiser_id": obligation_record["promiser_id"],
                "promisee_id": obligation_record["promisee_id"],
                "status": obligation_record["status"],
            }
        )

        return {
            "success": True,
            "engine_name": self.engine_name,
            "obligation_id": obligation_id,
            "updated_state": state,
        }

    def create_obligation_from_event(
        self,
        *,
        state: SimulationState,
        event_payload: SimulationEventPayload,
        promiser_id: str,
        promisee_id: str,
        obligation_type: str,
        summary: str,
        terms: List[str] | None = None,
        due_condition: Optional[str] = None,
        breach_condition: Optional[str] = None,
    ) -> Dict[str, Any]:
        obligation = self.create_obligation_record(
            obligation_id=f"obl_{event_payload.event_id}_{promiser_id}_{promisee_id}",
            obligation_type=obligation_type,
            promiser_id=promiser_id,
            promisee_id=promisee_id,
            summary=summary,
            terms=terms or [],
            source_event_id=event_payload.event_id,
            witness_ids=list(event_payload.witness_ids),
            involved_faction_ids=list(event_payload.involved_faction_ids),
            linked_secret_ids=list(event_payload.metadata.get("linked_secret_ids", [])),
            linked_evidence_ids=list(event_payload.metadata.get("linked_evidence_ids", [])),
            emotional_weight=float(event_payload.metadata.get("emotional_weight", event_payload.intensity or 0.5)),
            legal_weight=float(event_payload.metadata.get("legal_weight", 0.0)),
            magical_weight=float(event_payload.metadata.get("magical_weight", 0.0)),
            social_weight=float(event_payload.metadata.get("social_weight", 0.5)),
            due_condition=due_condition,
            breach_condition=breach_condition,
        )

        return {
            "success": True,
            "engine_name": self.engine_name,
            "obligation_record": obligation,
        }

    def evaluate_obligation_status(
        self,
        *,
        state: SimulationState,
        obligation_id: str,
        current_event: Optional[SimulationEventPayload] = None,
    ) -> Dict[str, Any]:
        obligation = state.metadata.get("obligation_registry", {}).get(obligation_id)
        blockers: List[str] = []
        warnings: List[str] = []
        passed: List[str] = []

        if not obligation:
            return {
                "success": False,
                "engine_name": self.engine_name,
                "obligation_id": obligation_id,
                "errors": [f"obligation {obligation_id} is not registered"],
            }

        passed.append("obligation_registered")

        if obligation["status"] not in self.STATUS_VALUES:
            warnings.append("obligation has unknown status")

        if obligation["status"] in {"fulfilled", "forgiven", "cancelled", "expired"}:
            passed.append("obligation_terminal_or_safe")

        if current_event:
            if self._event_matches_fulfillment(obligation, current_event):
                passed.append("current_event_matches_fulfillment")
            if self._event_matches_breach(obligation, current_event):
                warnings.append("current_event_may_breach_obligation")

        risk = self._breach_risk(obligation)

        return {
            "success": True,
            "engine_name": self.engine_name,
            "obligation_id": obligation_id,
            "status": obligation["status"],
            "pressure_score": obligation.get("pressure_score", 0.0),
            "debt_balance": obligation.get("debt_balance", 0.0),
            "breach_risk": risk,
            "passed_checks": passed,
            "blockers": blockers,
            "warnings": warnings,
            "recommendation": self._status_recommendation(obligation, risk),
        }

    def fulfill_obligation(
        self,
        *,
        state: SimulationState,
        obligation_id: str,
        fulfillment_event_id: str,
        fulfillment_strength: float = 1.0,
        notes: str = "",
    ) -> Dict[str, Any]:
        obligation = state.metadata.get("obligation_registry", {}).get(obligation_id)
        if not obligation:
            return {
                "success": False,
                "engine_name": self.engine_name,
                "obligation_id": obligation_id,
                "errors": [f"obligation {obligation_id} is not registered"],
                "updated_state": state,
            }

        fulfillment_strength = self._bounded(fulfillment_strength)
        obligation["fulfillment_event_ids"] = self._unique(obligation.get("fulfillment_event_ids", []) + [fulfillment_event_id])

        if fulfillment_strength >= 0.85:
            obligation["status"] = "fulfilled"
            obligation["debt_balance"] = 0.0
        else:
            obligation["status"] = "partially_fulfilled"
            obligation["debt_balance"] = self._bounded(float(obligation.get("debt_balance", 0.0)) * (1.0 - fulfillment_strength))

        state.metadata.setdefault("obligation_history", []).append(
            {
                "action": "fulfill_obligation",
                "obligation_id": obligation_id,
                "fulfillment_event_id": fulfillment_event_id,
                "fulfillment_strength": fulfillment_strength,
                "notes": notes,
            }
        )

        return {
            "success": True,
            "engine_name": self.engine_name,
            "obligation_id": obligation_id,
            "updated_obligation": obligation,
            "updated_state": state,
        }

    def break_obligation(
        self,
        *,
        state: SimulationState,
        obligation_id: str,
        breach_event_id: str,
        breach_severity: float = 0.7,
        reason: str = "",
    ) -> Dict[str, Any]:
        obligation = state.metadata.get("obligation_registry", {}).get(obligation_id)
        if not obligation:
            return {
                "success": False,
                "engine_name": self.engine_name,
                "obligation_id": obligation_id,
                "errors": [f"obligation {obligation_id} is not registered"],
                "updated_state": state,
            }

        breach_severity = self._bounded(breach_severity)
        obligation["status"] = "broken"
        obligation["breach_event_ids"] = self._unique(obligation.get("breach_event_ids", []) + [breach_event_id])
        obligation["debt_balance"] = self._bounded(float(obligation.get("debt_balance", 0.0)) + breach_severity * 0.4)
        obligation["pressure_score"] = self._bounded(float(obligation.get("pressure_score", 0.0)) + breach_severity * 0.35)

        state.metadata.setdefault("obligation_history", []).append(
            {
                "action": "break_obligation",
                "obligation_id": obligation_id,
                "breach_event_id": breach_event_id,
                "breach_severity": breach_severity,
                "reason": reason,
            }
        )

        return {
            "success": True,
            "engine_name": self.engine_name,
            "obligation_id": obligation_id,
            "updated_obligation": obligation,
            "updated_state": state,
        }

    def forgive_obligation(
        self,
        *,
        state: SimulationState,
        obligation_id: str,
        forgiveness_event_id: str,
        forgiveness_strength: float = 0.8,
        forgiven_by_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        obligation = state.metadata.get("obligation_registry", {}).get(obligation_id)
        if not obligation:
            return {
                "success": False,
                "engine_name": self.engine_name,
                "obligation_id": obligation_id,
                "errors": [f"obligation {obligation_id} is not registered"],
                "updated_state": state,
            }

        forgiveness_strength = self._bounded(forgiveness_strength)
        obligation["forgiveness_event_ids"] = self._unique(obligation.get("forgiveness_event_ids", []) + [forgiveness_event_id])
        obligation["debt_balance"] = self._bounded(float(obligation.get("debt_balance", 0.0)) * (1.0 - forgiveness_strength))

        if obligation["debt_balance"] <= 0.15:
            obligation["status"] = "forgiven"

        state.metadata.setdefault("obligation_history", []).append(
            {
                "action": "forgive_obligation",
                "obligation_id": obligation_id,
                "forgiveness_event_id": forgiveness_event_id,
                "forgiveness_strength": forgiveness_strength,
                "forgiven_by_id": forgiven_by_id,
            }
        )

        return {
            "success": True,
            "engine_name": self.engine_name,
            "obligation_id": obligation_id,
            "updated_obligation": obligation,
            "updated_state": state,
        }

    def build_relationship_delta_from_obligation(
        self,
        *,
        state: SimulationState,
        obligation_id: str,
        event_outcome: str,
    ) -> RelationshipDelta:
        obligation = state.metadata.get("obligation_registry", {}).get(obligation_id, {})
        promiser_id = obligation.get("promiser_id", "unknown_promiser")
        promisee_id = obligation.get("promisee_id", "unknown_promisee")
        relationship_id = self._relationship_id(promiser_id, promisee_id)

        pressure = float(obligation.get("pressure_score", 0.5))
        debt = float(obligation.get("debt_balance", 0.5))

        values = {
            "trust_delta": 0.0,
            "loyalty_delta": 0.0,
            "debt_delta": 0.0,
            "resentment_delta": 0.0,
            "respect_delta": 0.0,
            "betrayal_risk_delta": 0.0,
            "repair_potential_delta": 0.0,
        }

        if event_outcome == "fulfilled":
            values.update(
                trust_delta=0.18 * pressure,
                loyalty_delta=0.16 * pressure,
                debt_delta=-0.20 * debt,
                respect_delta=0.14 * pressure,
                repair_potential_delta=0.08,
            )
        elif event_outcome == "partially_fulfilled":
            values.update(
                trust_delta=0.06 * pressure,
                debt_delta=-0.08 * debt,
                resentment_delta=0.04,
                repair_potential_delta=0.06,
            )
        elif event_outcome == "broken":
            values.update(
                trust_delta=-0.24 * pressure,
                loyalty_delta=-0.18 * pressure,
                debt_delta=0.16 * pressure,
                resentment_delta=0.22 * pressure,
                betrayal_risk_delta=0.20 * pressure,
                repair_potential_delta=-0.10,
            )
        elif event_outcome == "forgiven":
            values.update(
                resentment_delta=-0.16 * pressure,
                repair_potential_delta=0.18,
                trust_delta=0.08,
                debt_delta=-0.18 * debt,
            )

        return RelationshipDelta(
            simulation_id=state.simulation_id,
            source_engine=self.engine_name,
            operation=DeltaOperation.INCREMENT,
            target_entity_id=relationship_id,
            target_path=f"relationship_states.{relationship_id}",
            relationship_id=relationship_id,
            character_a_id=promiser_id,
            character_b_id=promisee_id,
            relationship_event_label=f"obligation_{event_outcome}",
            reason=f"Obligation {obligation_id} outcome: {event_outcome}.",
            **{key: round(value, 3) for key, value in values.items()},
        )

    def build_reputation_delta_from_obligation(
        self,
        *,
        state: SimulationState,
        obligation_id: str,
        event_outcome: str,
        audience_type: str = "public",
    ) -> ReputationDelta:
        obligation = state.metadata.get("obligation_registry", {}).get(obligation_id, {})
        promiser_id = obligation.get("promiser_id", "unknown_promiser")

        pressure = float(obligation.get("pressure_score", 0.5))
        witness_bonus = min(0.25, len(obligation.get("witness_ids", [])) * 0.04)
        public_pressure = pressure + witness_bonus

        if event_outcome == "fulfilled":
            rep_delta = 0.18 * public_pressure
            respect_delta = 0.16 * public_pressure
            trust_delta = 0.14 * public_pressure
            fear_delta = 0.0
        elif event_outcome == "broken":
            rep_delta = -0.24 * public_pressure
            respect_delta = -0.20 * public_pressure
            trust_delta = -0.18 * public_pressure
            fear_delta = 0.05 * public_pressure
        elif event_outcome == "forgiven":
            rep_delta = 0.06 * public_pressure
            respect_delta = 0.04 * public_pressure
            trust_delta = 0.05 * public_pressure
            fear_delta = 0.0
        else:
            rep_delta = -0.05 * public_pressure
            respect_delta = -0.03 * public_pressure
            trust_delta = -0.03 * public_pressure
            fear_delta = 0.0

        return ReputationDelta(
            simulation_id=state.simulation_id,
            source_engine=self.engine_name,
            operation=DeltaOperation.INCREMENT,
            target_entity_id=promiser_id,
            target_path=f"character_states.{promiser_id}.metadata.reputation_state.{audience_type}",
            character_id=promiser_id,
            audience_type=audience_type,
            reputation_score_delta=round(rep_delta, 3),
            respect_score_delta=round(respect_delta, 3),
            trust_score_delta=round(trust_delta, 3),
            fear_score_delta=round(fear_delta, 3),
            reason=f"Obligation {obligation_id} reputation outcome: {event_outcome}.",
        )

    def build_delta_batch_for_obligation_outcome(
        self,
        *,
        state: SimulationState,
        obligation_id: str,
        event_outcome: str,
        audience_type: str = "public",
    ) -> DeltaBatch:
        relationship_delta = self.build_relationship_delta_from_obligation(
            state=state,
            obligation_id=obligation_id,
            event_outcome=event_outcome,
        )
        reputation_delta = self.build_reputation_delta_from_obligation(
            state=state,
            obligation_id=obligation_id,
            event_outcome=event_outcome,
            audience_type=audience_type,
        )

        return DeltaBatch(
            simulation_id=state.simulation_id,
            source_engine=self.engine_name,
            relationship_deltas=[relationship_delta],
            reputation_deltas=[reputation_delta],
            application_order=[relationship_delta.delta_id, reputation_delta.delta_id],
        )

    def build_obligation_map(self, *, state: SimulationState) -> Dict[str, Any]:
        registry = state.metadata.get("obligation_registry", {})
        records = {}

        for obligation_id, obligation in registry.items():
            records[obligation_id] = {
                "obligation_id": obligation_id,
                "obligation_type": obligation.get("obligation_type"),
                "promiser_id": obligation.get("promiser_id"),
                "promisee_id": obligation.get("promisee_id"),
                "summary": obligation.get("summary"),
                "status": obligation.get("status"),
                "pressure_score": obligation.get("pressure_score"),
                "debt_balance": obligation.get("debt_balance"),
                "breach_risk": self._breach_risk(obligation),
                "witness_count": len(obligation.get("witness_ids", [])),
                "socially_visible": bool(obligation.get("witness_ids") or obligation.get("involved_faction_ids")),
                "linked_secret_ids": obligation.get("linked_secret_ids", []),
                "linked_evidence_ids": obligation.get("linked_evidence_ids", []),
            }

        return {
            "success": True,
            "engine_name": self.engine_name,
            "obligation_count": len(records),
            "obligation_records": records,
            "warnings": self._obligation_map_warnings(records),
        }

    def _event_matches_fulfillment(self, obligation: Dict[str, Any], event: SimulationEventPayload) -> bool:
        condition = str(obligation.get("due_condition") or "").lower()
        if not condition:
            return False
        event_text = f"{event.event_type} {event.event_name} {event.metadata}".lower()
        return any(token in event_text for token in condition.split() if len(token) > 4)

    def _event_matches_breach(self, obligation: Dict[str, Any], event: SimulationEventPayload) -> bool:
        condition = str(obligation.get("breach_condition") or "").lower()
        if not condition:
            return False
        event_text = f"{event.event_type} {event.event_name} {event.metadata}".lower()
        return any(token in event_text for token in condition.split() if len(token) > 4)

    def _breach_risk(self, obligation: Dict[str, Any]) -> float:
        if obligation.get("status") in {"fulfilled", "forgiven", "cancelled", "expired"}:
            return 0.0

        pressure = float(obligation.get("pressure_score", 0.5))
        debt = float(obligation.get("debt_balance", 0.5))
        secrecy = 0.15 if obligation.get("linked_secret_ids") else 0.0
        witness_pressure = min(0.2, len(obligation.get("witness_ids", [])) * 0.04)

        if obligation.get("status") == "broken":
            return 1.0

        return round(min(1.0, pressure * 0.4 + debt * 0.35 + secrecy + witness_pressure), 3)

    def _status_recommendation(self, obligation: Dict[str, Any], risk: float) -> str:
        if obligation.get("status") == "broken":
            return "resolve_breach_with_consequence_or_repair"
        if obligation.get("status") == "active" and risk >= 0.65:
            return "create_pressure_scene_or_fulfillment_choice"
        if obligation.get("status") == "partially_fulfilled":
            return "schedule_remaining_debt_or_forgiveness"
        return "continue_tracking"

    def _initial_debt_balance(
        self,
        obligation_type: str,
        emotional_weight: float,
        legal_weight: float,
        magical_weight: float,
        social_weight: float,
    ) -> float:
        type_bonus = {
            "life_debt": 0.35,
            "blood_debt": 0.35,
            "oath": 0.25,
            "vow": 0.22,
            "contract": 0.20,
            "favor_debt": 0.18,
            "romantic_promise": 0.16,
            "political_pact": 0.20,
        }.get(obligation_type, 0.1)

        return self._bounded(
            emotional_weight * 0.28
            + legal_weight * 0.22
            + magical_weight * 0.25
            + social_weight * 0.15
            + type_bonus
        )

    def _pressure_score(self, emotional_weight: float, legal_weight: float, magical_weight: float, social_weight: float) -> float:
        return self._bounded(
            emotional_weight * 0.32
            + legal_weight * 0.22
            + magical_weight * 0.24
            + social_weight * 0.22
        )

    def _relationship_id(self, a: str, b: str) -> str:
        return "rel_" + "_".join(sorted([a, b]))

    def _obligation_map_warnings(self, records: Dict[str, Dict[str, Any]]) -> List[str]:
        warnings = []
        for obligation_id, record in records.items():
            if record["status"] == "active" and record["breach_risk"] >= 0.75:
                warnings.append(f"{obligation_id} has high breach risk")
            if record["status"] == "broken" and record["debt_balance"] >= 0.5:
                warnings.append(f"{obligation_id} is broken and still has major debt balance")
            if not record["socially_visible"] and record["pressure_score"] >= 0.7:
                warnings.append(f"{obligation_id} is high pressure but has no witnesses/faction visibility")
        return warnings

    def _bounded(self, value: float) -> float:
        return round(max(0.0, min(1.0, float(value))), 3)

    def _unique(self, values: List[Any]) -> List[Any]:
        seen = set()
        result = []
        for value in values:
            if value is None:
                continue
            key = str(value)
            if key not in seen:
                seen.add(key)
                result.append(value)
        return result

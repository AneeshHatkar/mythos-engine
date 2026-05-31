from typing import Any, Dict, List, Optional

from backend.app.schemas.simulation import (
    DeltaBatch,
    DeltaOperation,
    FactionDelta,
    KnowledgeDelta,
    RelationshipDelta,
    ResourceDelta,
    SimulationEventPayload,
    SimulationState,
)


class NegotiationBargainEngine:
    """Models offers, counteroffers, concessions, bargains, and deal outcomes.

    Negotiations convert character goals, leverage, obligations, resources,
    secrets, factions, and relationship state into structured bargaining state.
    """

    engine_name = "simulation.negotiation_bargain_engine"

    NEGOTIATION_TYPES = {
        "political_bargain",
        "resource_trade",
        "secret_exchange",
        "evidence_exchange",
        "debt_settlement",
        "romantic_boundary_bargain",
        "faction_treaty",
        "trial_deal",
        "mentor_terms",
        "hostage_exchange",
        "truce",
        "alliance_offer",
    }

    STATUS_VALUES = {
        "open",
        "accepted",
        "rejected",
        "countered",
        "collapsed",
        "fulfilled",
        "betrayed",
        "expired",
    }

    def create_bargain_record(
        self,
        *,
        bargain_id: str,
        negotiation_type: str,
        proposer_id: str,
        receiver_id: str,
        offer_summary: str,
        requested_terms: List[str] | None = None,
        offered_terms: List[str] | None = None,
        concession_terms: List[str] | None = None,
        linked_secret_ids: List[str] | None = None,
        linked_evidence_ids: List[str] | None = None,
        linked_resource_ids: List[str] | None = None,
        linked_obligation_ids: List[str] | None = None,
        linked_faction_ids: List[str] | None = None,
        pressure_level: float = 0.5,
        fairness_score: float = 0.5,
        trust_requirement: float = 0.4,
        betrayal_risk: float = 0.3,
        deadline_condition: Optional[str] = None,
        metadata: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        if negotiation_type not in self.NEGOTIATION_TYPES:
            negotiation_type = "political_bargain"

        return {
            "bargain_id": bargain_id,
            "negotiation_type": negotiation_type,
            "proposer_id": proposer_id,
            "receiver_id": receiver_id,
            "offer_summary": offer_summary,
            "requested_terms": requested_terms or [],
            "offered_terms": offered_terms or [],
            "concession_terms": concession_terms or [],
            "linked_secret_ids": linked_secret_ids or [],
            "linked_evidence_ids": linked_evidence_ids or [],
            "linked_resource_ids": linked_resource_ids or [],
            "linked_obligation_ids": linked_obligation_ids or [],
            "linked_faction_ids": linked_faction_ids or [],
            "pressure_level": self._bounded(pressure_level),
            "fairness_score": self._bounded(fairness_score),
            "trust_requirement": self._bounded(trust_requirement),
            "betrayal_risk": self._bounded(betrayal_risk),
            "deadline_condition": deadline_condition,
            "status": "open",
            "counteroffer_ids": [],
            "acceptance_event_ids": [],
            "rejection_event_ids": [],
            "collapse_event_ids": [],
            "fulfillment_event_ids": [],
            "betrayal_event_ids": [],
            "metadata": metadata or {},
        }

    def register_bargain_on_state(
        self,
        *,
        state: SimulationState,
        bargain_record: Dict[str, Any],
    ) -> Dict[str, Any]:
        bargain_id = bargain_record["bargain_id"]
        state.metadata.setdefault("bargain_registry", {})[bargain_id] = dict(bargain_record)

        for character_id in [bargain_record["proposer_id"], bargain_record["receiver_id"]]:
            if character_id in state.character_states:
                state.character_states[character_id].metadata.setdefault("bargain_ids", [])
                state.character_states[character_id].metadata["bargain_ids"] = self._unique(
                    state.character_states[character_id].metadata["bargain_ids"] + [bargain_id]
                )

        state.metadata.setdefault("bargain_history", []).append(
            {
                "action": "register_bargain",
                "bargain_id": bargain_id,
                "proposer_id": bargain_record["proposer_id"],
                "receiver_id": bargain_record["receiver_id"],
                "status": bargain_record["status"],
            }
        )

        return {
            "success": True,
            "engine_name": self.engine_name,
            "bargain_id": bargain_id,
            "updated_state": state,
        }

    def create_bargain_from_event(
        self,
        *,
        state: SimulationState,
        event_payload: SimulationEventPayload,
        proposer_id: str,
        receiver_id: str,
        offer_summary: str,
        negotiation_type: str = "political_bargain",
        requested_terms: List[str] | None = None,
        offered_terms: List[str] | None = None,
    ) -> Dict[str, Any]:
        bargain = self.create_bargain_record(
            bargain_id=f"bar_{event_payload.event_id}_{proposer_id}_{receiver_id}",
            negotiation_type=negotiation_type,
            proposer_id=proposer_id,
            receiver_id=receiver_id,
            offer_summary=offer_summary,
            requested_terms=requested_terms or list(event_payload.metadata.get("requested_terms", [])),
            offered_terms=offered_terms or list(event_payload.metadata.get("offered_terms", [])),
            concession_terms=list(event_payload.metadata.get("concession_terms", [])),
            linked_secret_ids=list(event_payload.metadata.get("linked_secret_ids", [])),
            linked_evidence_ids=list(event_payload.metadata.get("linked_evidence_ids", [])),
            linked_resource_ids=list(event_payload.metadata.get("linked_resource_ids", [])),
            linked_obligation_ids=list(event_payload.metadata.get("linked_obligation_ids", [])),
            linked_faction_ids=list(event_payload.involved_faction_ids),
            pressure_level=float(event_payload.metadata.get("pressure_level", event_payload.intensity or 0.5)),
            fairness_score=float(event_payload.metadata.get("fairness_score", 0.5)),
            trust_requirement=float(event_payload.metadata.get("trust_requirement", 0.4)),
            betrayal_risk=float(event_payload.metadata.get("betrayal_risk", 0.3)),
            deadline_condition=event_payload.metadata.get("deadline_condition"),
            metadata={"source_event_id": event_payload.event_id},
        )

        return {
            "success": True,
            "engine_name": self.engine_name,
            "bargain_record": bargain,
        }

    def evaluate_bargain_viability(
        self,
        *,
        state: SimulationState,
        bargain_id: str,
    ) -> Dict[str, Any]:
        bargain = state.metadata.get("bargain_registry", {}).get(bargain_id)
        blockers: List[str] = []
        warnings: List[str] = []
        passed: List[str] = []

        if not bargain:
            return {
                "success": False,
                "engine_name": self.engine_name,
                "bargain_id": bargain_id,
                "viable": False,
                "blockers": [f"bargain {bargain_id} is not registered"],
                "warnings": [],
                "passed_checks": [],
            }

        passed.append("bargain_registered")

        if bargain["status"] not in self.STATUS_VALUES:
            warnings.append("bargain has unknown status")

        if bargain["proposer_id"] not in state.character_states and bargain["proposer_id"] not in state.entity_states:
            blockers.append(f"proposer {bargain['proposer_id']} is missing")
        else:
            passed.append("proposer_exists")

        if bargain["receiver_id"] not in state.character_states and bargain["receiver_id"] not in state.entity_states:
            blockers.append(f"receiver {bargain['receiver_id']} is missing")
        else:
            passed.append("receiver_exists")

        resource_report = self._validate_resource_terms(state, bargain)
        secret_report = self._validate_secret_terms(state, bargain)
        obligation_report = self._validate_obligation_terms(state, bargain)

        for report in [resource_report, secret_report, obligation_report]:
            blockers.extend(report["blockers"])
            warnings.extend(report["warnings"])
            passed.extend(report["passed_checks"])

        trust_fit = self._trust_fit(state, bargain)
        acceptance_probability = self._acceptance_probability(state, bargain)

        if trust_fit < 0.25 and bargain.get("trust_requirement", 0.4) >= 0.5:
            warnings.append("relationship trust may be too weak for this bargain")

        viable = len(blockers) == 0

        return {
            "success": True,
            "engine_name": self.engine_name,
            "bargain_id": bargain_id,
            "viable": viable,
            "bargain_value_score": self._bargain_value_score(bargain),
            "trust_fit": trust_fit,
            "acceptance_probability": acceptance_probability,
            "passed_checks": passed,
            "blockers": blockers,
            "warnings": warnings,
            "recommendation": "allow_negotiation" if viable else "fix_bargain_terms",
        }

    def create_counteroffer(
        self,
        *,
        state: SimulationState,
        parent_bargain_id: str,
        counteroffer_id: str,
        proposer_id: str,
        receiver_id: str,
        offer_summary: str,
        requested_terms: List[str] | None = None,
        offered_terms: List[str] | None = None,
        fairness_score: float = 0.55,
    ) -> Dict[str, Any]:
        parent = state.metadata.get("bargain_registry", {}).get(parent_bargain_id)
        if not parent:
            return {
                "success": False,
                "engine_name": self.engine_name,
                "errors": [f"parent bargain {parent_bargain_id} is not registered"],
                "updated_state": state,
            }

        counter = self.create_bargain_record(
            bargain_id=counteroffer_id,
            negotiation_type=parent.get("negotiation_type", "political_bargain"),
            proposer_id=proposer_id,
            receiver_id=receiver_id,
            offer_summary=offer_summary,
            requested_terms=requested_terms or [],
            offered_terms=offered_terms or [],
            linked_secret_ids=list(parent.get("linked_secret_ids", [])),
            linked_evidence_ids=list(parent.get("linked_evidence_ids", [])),
            linked_resource_ids=list(parent.get("linked_resource_ids", [])),
            linked_obligation_ids=list(parent.get("linked_obligation_ids", [])),
            linked_faction_ids=list(parent.get("linked_faction_ids", [])),
            pressure_level=max(0.0, float(parent.get("pressure_level", 0.5)) - 0.08),
            fairness_score=fairness_score,
            trust_requirement=float(parent.get("trust_requirement", 0.4)),
            betrayal_risk=float(parent.get("betrayal_risk", 0.3)),
            metadata={"parent_bargain_id": parent_bargain_id},
        )

        parent["status"] = "countered"
        parent["counteroffer_ids"] = self._unique(parent.get("counteroffer_ids", []) + [counteroffer_id])
        self.register_bargain_on_state(state=state, bargain_record=counter)

        state.metadata.setdefault("bargain_history", []).append(
            {
                "action": "create_counteroffer",
                "parent_bargain_id": parent_bargain_id,
                "counteroffer_id": counteroffer_id,
            }
        )

        return {
            "success": True,
            "engine_name": self.engine_name,
            "counteroffer": counter,
            "updated_state": state,
        }

    def resolve_bargain_outcome(
        self,
        *,
        state: SimulationState,
        bargain_id: str,
        outcome: str,
        outcome_event_id: str,
        notes: str = "",
    ) -> Dict[str, Any]:
        bargain = state.metadata.get("bargain_registry", {}).get(bargain_id)
        if not bargain:
            return {
                "success": False,
                "engine_name": self.engine_name,
                "bargain_id": bargain_id,
                "errors": [f"bargain {bargain_id} is not registered"],
                "updated_state": state,
            }

        if outcome == "accepted":
            bargain["status"] = "accepted"
            bargain["acceptance_event_ids"] = self._unique(bargain.get("acceptance_event_ids", []) + [outcome_event_id])
        elif outcome == "rejected":
            bargain["status"] = "rejected"
            bargain["rejection_event_ids"] = self._unique(bargain.get("rejection_event_ids", []) + [outcome_event_id])
        elif outcome == "collapsed":
            bargain["status"] = "collapsed"
            bargain["collapse_event_ids"] = self._unique(bargain.get("collapse_event_ids", []) + [outcome_event_id])
        elif outcome == "fulfilled":
            bargain["status"] = "fulfilled"
            bargain["fulfillment_event_ids"] = self._unique(bargain.get("fulfillment_event_ids", []) + [outcome_event_id])
        elif outcome == "betrayed":
            bargain["status"] = "betrayed"
            bargain["betrayal_event_ids"] = self._unique(bargain.get("betrayal_event_ids", []) + [outcome_event_id])
        else:
            bargain["status"] = outcome if outcome in self.STATUS_VALUES else "collapsed"

        if notes:
            bargain.setdefault("resolution_notes", [])
            bargain["resolution_notes"] = self._unique(bargain["resolution_notes"] + [notes])

        state.metadata.setdefault("bargain_history", []).append(
            {
                "action": "resolve_bargain_outcome",
                "bargain_id": bargain_id,
                "outcome": outcome,
                "outcome_event_id": outcome_event_id,
                "notes": notes,
            }
        )

        return {
            "success": True,
            "engine_name": self.engine_name,
            "bargain_id": bargain_id,
            "outcome": outcome,
            "updated_bargain": bargain,
            "updated_state": state,
        }

    def build_relationship_delta_from_bargain(
        self,
        *,
        state: SimulationState,
        bargain_id: str,
        outcome: str,
    ) -> RelationshipDelta:
        bargain = state.metadata.get("bargain_registry", {}).get(bargain_id, {})
        proposer_id = bargain.get("proposer_id", "unknown_proposer")
        receiver_id = bargain.get("receiver_id", "unknown_receiver")
        relationship_id = self._relationship_id(proposer_id, receiver_id)

        value = self._bargain_value_score(bargain)
        fairness = float(bargain.get("fairness_score", 0.5))
        betrayal = float(bargain.get("betrayal_risk", 0.3))

        values = {
            "trust_delta": 0.0,
            "respect_delta": 0.0,
            "debt_delta": 0.0,
            "resentment_delta": 0.0,
            "loyalty_delta": 0.0,
            "betrayal_risk_delta": 0.0,
            "repair_potential_delta": 0.0,
        }

        if outcome == "accepted":
            values.update(
                trust_delta=0.08 * fairness,
                respect_delta=0.08 * value,
                debt_delta=0.08 * value,
                loyalty_delta=0.05 * fairness,
                betrayal_risk_delta=0.04 * betrayal,
            )
        elif outcome == "rejected":
            values.update(
                trust_delta=-0.05 * value,
                resentment_delta=0.08 * value,
                repair_potential_delta=0.03,
            )
        elif outcome == "countered":
            values.update(
                respect_delta=0.05 * fairness,
                trust_delta=0.03,
                repair_potential_delta=0.04,
            )
        elif outcome == "collapsed":
            values.update(
                trust_delta=-0.12 * value,
                resentment_delta=0.15 * value,
                betrayal_risk_delta=0.08,
            )
        elif outcome == "fulfilled":
            values.update(
                trust_delta=0.16 * fairness,
                respect_delta=0.12 * value,
                loyalty_delta=0.10 * fairness,
                debt_delta=-0.06 * value,
                repair_potential_delta=0.05,
            )
        elif outcome == "betrayed":
            values.update(
                trust_delta=-0.24 * value,
                resentment_delta=0.22 * value,
                betrayal_risk_delta=0.22,
                repair_potential_delta=-0.10,
            )

        return RelationshipDelta(
            simulation_id=state.simulation_id,
            source_engine=self.engine_name,
            operation=DeltaOperation.INCREMENT,
            target_entity_id=relationship_id,
            target_path=f"relationship_states.{relationship_id}",
            relationship_id=relationship_id,
            character_a_id=proposer_id,
            character_b_id=receiver_id,
            relationship_event_label=f"bargain_{outcome}",
            reason=f"Bargain {bargain_id} outcome: {outcome}.",
            **{key: round(value, 3) for key, value in values.items()},
        )

    def build_knowledge_delta_from_bargain(
        self,
        *,
        state: SimulationState,
        bargain_id: str,
        receiver_id: str,
    ) -> KnowledgeDelta:
        bargain = state.metadata.get("bargain_registry", {}).get(bargain_id, {})

        confidence = min(0.75, self._bargain_value_score(bargain) + 0.15)
        confidence_updates = {}

        for secret_id in bargain.get("linked_secret_ids", []):
            confidence_updates[secret_id] = confidence

        return KnowledgeDelta(
            simulation_id=state.simulation_id,
            source_engine=self.engine_name,
            operation=DeltaOperation.APPEND,
            target_entity_id=receiver_id,
            target_path=f"knowledge_states.{receiver_id}",
            knowledge_holder_id=receiver_id,
            suspected_secret_ids_added=list(bargain.get("linked_secret_ids", [])),
            evidence_ids_seen=list(bargain.get("linked_evidence_ids", [])),
            knowledge_confidence_updates=confidence_updates,
            knowledge_path=["bargain_exchange"],
            no_magic_knowledge_checked=True,
            reason=f"Bargain {bargain_id} transfers negotiation knowledge to {receiver_id}.",
        )

    def build_resource_delta_from_bargain(
        self,
        *,
        state: SimulationState,
        bargain_id: str,
        receiver_id: str,
        outcome: str,
    ) -> ResourceDelta:
        bargain = state.metadata.get("bargain_registry", {}).get(bargain_id, {})
        resource_ids = bargain.get("linked_resource_ids", [])

        amount_delta = 0.0
        if outcome in {"accepted", "fulfilled"}:
            amount_delta = min(1.0, 0.2 + len(resource_ids) * 0.1)
        elif outcome in {"betrayed", "collapsed"}:
            amount_delta = -min(1.0, 0.2 + len(resource_ids) * 0.1)

        primary_resource_id = resource_ids[0] if resource_ids else f"resource_from_{bargain_id}"

        return ResourceDelta(
            simulation_id=state.simulation_id,
            source_engine=self.engine_name,
            operation=DeltaOperation.INCREMENT,
            target_entity_id=receiver_id,
            target_path=f"character_states.{receiver_id}.metadata.resource_state",
            resource_id=primary_resource_id,
            resource_owner_id=receiver_id,
            resource_type="bargain_resource_bundle",
            amount_delta=round(amount_delta, 3),
            resource_ids_affected=resource_ids,
            reason=f"Bargain {bargain_id} resource outcome: {outcome}.",
        )

    def build_faction_delta_from_bargain(
        self,
        *,
        state: SimulationState,
        bargain_id: str,
        outcome: str,
    ) -> Optional[FactionDelta]:
        bargain = state.metadata.get("bargain_registry", {}).get(bargain_id, {})
        faction_ids = bargain.get("linked_faction_ids", [])

        if not faction_ids:
            return None

        trust_delta = 0.0
        influence_delta = 0.0

        if outcome in {"accepted", "fulfilled"}:
            trust_delta = 0.08
            influence_delta = 0.06
        elif outcome in {"betrayed", "collapsed"}:
            trust_delta = -0.14
            influence_delta = -0.08

        return FactionDelta(
            simulation_id=state.simulation_id,
            source_engine=self.engine_name,
            operation=DeltaOperation.INCREMENT,
            target_entity_id=faction_ids[0],
            target_path=f"world_state.faction_states.{faction_ids[0]}",
            faction_id=faction_ids[0],
            trust_delta=trust_delta,
            influence_delta=influence_delta,
            reason=f"Bargain {bargain_id} faction outcome: {outcome}.",
        )

    def build_delta_batch_for_bargain_outcome(
        self,
        *,
        state: SimulationState,
        bargain_id: str,
        outcome: str,
    ) -> DeltaBatch:
        bargain = state.metadata.get("bargain_registry", {}).get(bargain_id, {})
        receiver_id = bargain.get("receiver_id", "unknown_receiver")

        relationship_delta = self.build_relationship_delta_from_bargain(
            state=state,
            bargain_id=bargain_id,
            outcome=outcome,
        )
        knowledge_delta = self.build_knowledge_delta_from_bargain(
            state=state,
            bargain_id=bargain_id,
            receiver_id=receiver_id,
        )
        resource_delta = self.build_resource_delta_from_bargain(
            state=state,
            bargain_id=bargain_id,
            receiver_id=receiver_id,
            outcome=outcome,
        )
        faction_delta = self.build_faction_delta_from_bargain(
            state=state,
            bargain_id=bargain_id,
            outcome=outcome,
        )

        ordered = [relationship_delta, knowledge_delta, resource_delta]
        faction_deltas = []
        if faction_delta:
            faction_deltas.append(faction_delta)
            ordered.append(faction_delta)

        return DeltaBatch(
            simulation_id=state.simulation_id,
            source_engine=self.engine_name,
            relationship_deltas=[relationship_delta],
            knowledge_deltas=[knowledge_delta],
            resource_deltas=[resource_delta],
            faction_deltas=faction_deltas,
            application_order=[delta.delta_id for delta in ordered],
        )

    def build_bargain_map(self, *, state: SimulationState) -> Dict[str, Any]:
        registry = state.metadata.get("bargain_registry", {})
        records = {}

        for bargain_id, bargain in registry.items():
            records[bargain_id] = {
                "bargain_id": bargain_id,
                "negotiation_type": bargain.get("negotiation_type"),
                "proposer_id": bargain.get("proposer_id"),
                "receiver_id": bargain.get("receiver_id"),
                "status": bargain.get("status"),
                "offer_summary": bargain.get("offer_summary"),
                "bargain_value_score": self._bargain_value_score(bargain),
                "fairness_score": bargain.get("fairness_score"),
                "trust_fit": self._trust_fit(state, bargain),
                "acceptance_probability": self._acceptance_probability(state, bargain),
                "linked_secret_ids": bargain.get("linked_secret_ids", []),
                "linked_evidence_ids": bargain.get("linked_evidence_ids", []),
                "linked_resource_ids": bargain.get("linked_resource_ids", []),
                "linked_faction_ids": bargain.get("linked_faction_ids", []),
                "counteroffer_count": len(bargain.get("counteroffer_ids", [])),
            }

        return {
            "success": True,
            "engine_name": self.engine_name,
            "bargain_count": len(records),
            "bargain_records": records,
            "warnings": self._bargain_map_warnings(records),
        }

    def _validate_resource_terms(self, state: SimulationState, bargain: Dict[str, Any]) -> Dict[str, Any]:
        blockers: List[str] = []
        warnings: List[str] = []
        passed: List[str] = []

        if not bargain.get("linked_resource_ids"):
            return {"blockers": blockers, "warnings": warnings, "passed_checks": ["no_resource_terms_required"]}

        passed.append("resource_terms_present")
        if not bargain.get("offered_terms"):
            warnings.append("resources are linked but offered_terms is empty")

        return {"blockers": blockers, "warnings": warnings, "passed_checks": passed}

    def _validate_secret_terms(self, state: SimulationState, bargain: Dict[str, Any]) -> Dict[str, Any]:
        blockers: List[str] = []
        warnings: List[str] = []
        passed: List[str] = []

        secret_ids = bargain.get("linked_secret_ids", [])
        if not secret_ids:
            return {"blockers": blockers, "warnings": warnings, "passed_checks": ["no_secret_terms_required"]}

        proposer_id = bargain.get("proposer_id")
        knowledge = state.knowledge_states.get(proposer_id)

        for secret_id in secret_ids:
            if knowledge and secret_id in knowledge.known_secret_ids:
                passed.append(f"proposer_knows_{secret_id}")
            elif knowledge and secret_id in knowledge.suspected_secret_ids:
                warnings.append(f"proposer only suspects {secret_id}; secret bargain is weaker")
            else:
                blockers.append(f"proposer {proposer_id} does not know/suspect secret {secret_id}")

        return {"blockers": blockers, "warnings": warnings, "passed_checks": passed}

    def _validate_obligation_terms(self, state: SimulationState, bargain: Dict[str, Any]) -> Dict[str, Any]:
        blockers: List[str] = []
        warnings: List[str] = []
        passed: List[str] = []

        obligation_ids = bargain.get("linked_obligation_ids", [])
        if not obligation_ids:
            return {"blockers": blockers, "warnings": warnings, "passed_checks": ["no_obligation_terms_required"]}

        registry = state.metadata.get("obligation_registry", {})
        for obligation_id in obligation_ids:
            obligation = registry.get(obligation_id)
            if not obligation:
                blockers.append(f"linked obligation {obligation_id} missing")
            elif obligation.get("status") in {"fulfilled", "forgiven", "cancelled"}:
                warnings.append(f"obligation {obligation_id} may no longer strengthen bargain")
            else:
                passed.append(f"obligation_{obligation_id}_usable")

        return {"blockers": blockers, "warnings": warnings, "passed_checks": passed}

    def _bargain_value_score(self, bargain: Dict[str, Any]) -> float:
        return round(
            min(
                1.0,
                len(bargain.get("requested_terms", [])) * 0.06
                + len(bargain.get("offered_terms", [])) * 0.08
                + len(bargain.get("linked_secret_ids", [])) * 0.10
                + len(bargain.get("linked_evidence_ids", [])) * 0.08
                + len(bargain.get("linked_resource_ids", [])) * 0.08
                + len(bargain.get("linked_obligation_ids", [])) * 0.06
                + float(bargain.get("pressure_level", 0.5)) * 0.22
                + float(bargain.get("fairness_score", 0.5)) * 0.18,
            ),
            3,
        )

    def _trust_fit(self, state: SimulationState, bargain: Dict[str, Any]) -> float:
        proposer = bargain.get("proposer_id")
        receiver = bargain.get("receiver_id")

        for rel in state.relationship_states.values():
            if {rel.character_a_id, rel.character_b_id} == {proposer, receiver}:
                return round(
                    max(
                        0.0,
                        min(
                            1.0,
                            rel.trust * 0.45
                            + rel.respect * 0.25
                            + rel.loyalty * 0.15
                            - rel.betrayal_risk * 0.20
                            - rel.resentment * 0.10,
                        ),
                    ),
                    3,
                )

        return 0.35

    def _acceptance_probability(self, state: SimulationState, bargain: Dict[str, Any]) -> float:
        value = self._bargain_value_score(bargain)
        fairness = float(bargain.get("fairness_score", 0.5))
        pressure = float(bargain.get("pressure_level", 0.5))
        trust_fit = self._trust_fit(state, bargain)
        betrayal = float(bargain.get("betrayal_risk", 0.3))
        requirement = float(bargain.get("trust_requirement", 0.4))

        return round(
            max(
                0.0,
                min(
                    1.0,
                    value * 0.30
                    + fairness * 0.22
                    + pressure * 0.16
                    + trust_fit * 0.24
                    - betrayal * 0.18
                    - max(0.0, requirement - trust_fit) * 0.18,
                ),
            ),
            3,
        )

    def _relationship_id(self, a: str, b: str) -> str:
        return "rel_" + "_".join(sorted([a, b]))

    def _bargain_map_warnings(self, records: Dict[str, Dict[str, Any]]) -> List[str]:
        warnings = []
        for bargain_id, record in records.items():
            if record["status"] == "open" and record["acceptance_probability"] < 0.25:
                warnings.append(f"{bargain_id} has low acceptance probability")
            if record["trust_fit"] < 0.2 and record["fairness_score"] < 0.4:
                warnings.append(f"{bargain_id} is low-trust and unfair")
            if record["counteroffer_count"] >= 3:
                warnings.append(f"{bargain_id} has many counteroffers; negotiation may be stalling")
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

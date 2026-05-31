from typing import Any, Dict, List, Optional

from backend.app.schemas.simulation import (
    DeltaBatch,
    DeltaOperation,
    KnowledgeDelta,
    RelationshipDelta,
    ReputationDelta,
    SimulationEventPayload,
    SimulationState,
)


class LeverageBlackmailEngine:
    """Models leverage, blackmail, coercion, counter-leverage, and refusal.

    This engine connects secrets, evidence, rumors, promises, reputation, and
    relationship state into pressure systems that affect choices and consequences.
    """

    engine_name = "simulation.leverage_blackmail_engine"

    LEVERAGE_TYPES = {
        "secret_exposure",
        "evidence_threat",
        "reputation_threat",
        "legal_threat",
        "faction_threat",
        "romantic_threat",
        "family_threat",
        "debt_threat",
        "oath_threat",
        "physical_threat",
        "social_exclusion",
        "counter_leverage",
    }

    STATUS_VALUES = {
        "active",
        "accepted",
        "refused",
        "countered",
        "exposed",
        "resolved",
        "failed",
        "expired",
    }

    def create_leverage_record(
        self,
        *,
        leverage_id: str,
        leverage_type: str,
        holder_id: str,
        target_id: str,
        demand: str,
        threat: str,
        linked_secret_ids: List[str] | None = None,
        linked_evidence_ids: List[str] | None = None,
        linked_rumor_ids: List[str] | None = None,
        linked_obligation_ids: List[str] | None = None,
        witness_ids: List[str] | None = None,
        involved_faction_ids: List[str] | None = None,
        pressure_level: float = 0.5,
        exposure_risk: float = 0.5,
        target_resistance: float = 0.5,
        moral_cost: float = 0.5,
        deadline_condition: Optional[str] = None,
        metadata: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        if leverage_type not in self.LEVERAGE_TYPES:
            leverage_type = "secret_exposure"

        return {
            "leverage_id": leverage_id,
            "leverage_type": leverage_type,
            "holder_id": holder_id,
            "target_id": target_id,
            "demand": demand,
            "threat": threat,
            "linked_secret_ids": linked_secret_ids or [],
            "linked_evidence_ids": linked_evidence_ids or [],
            "linked_rumor_ids": linked_rumor_ids or [],
            "linked_obligation_ids": linked_obligation_ids or [],
            "witness_ids": witness_ids or [],
            "involved_faction_ids": involved_faction_ids or [],
            "pressure_level": self._bounded(pressure_level),
            "exposure_risk": self._bounded(exposure_risk),
            "target_resistance": self._bounded(target_resistance),
            "moral_cost": self._bounded(moral_cost),
            "deadline_condition": deadline_condition,
            "status": "active",
            "attempt_event_ids": [],
            "compliance_event_ids": [],
            "refusal_event_ids": [],
            "counter_event_ids": [],
            "exposure_event_ids": [],
            "resolution_notes": [],
            "metadata": metadata or {},
        }

    def register_leverage_on_state(
        self,
        *,
        state: SimulationState,
        leverage_record: Dict[str, Any],
    ) -> Dict[str, Any]:
        leverage_id = leverage_record["leverage_id"]
        state.metadata.setdefault("leverage_registry", {})[leverage_id] = dict(leverage_record)

        for character_id in [leverage_record["holder_id"], leverage_record["target_id"]]:
            if character_id in state.character_states:
                state.character_states[character_id].metadata.setdefault("leverage_ids", [])
                state.character_states[character_id].metadata["leverage_ids"] = self._unique(
                    state.character_states[character_id].metadata["leverage_ids"] + [leverage_id]
                )

        state.metadata.setdefault("leverage_history", []).append(
            {
                "action": "register_leverage",
                "leverage_id": leverage_id,
                "holder_id": leverage_record["holder_id"],
                "target_id": leverage_record["target_id"],
                "status": leverage_record["status"],
            }
        )

        return {
            "success": True,
            "engine_name": self.engine_name,
            "leverage_id": leverage_id,
            "updated_state": state,
        }

    def create_leverage_from_event(
        self,
        *,
        state: SimulationState,
        event_payload: SimulationEventPayload,
        holder_id: str,
        target_id: str,
        demand: str,
        threat: str,
        leverage_type: str = "secret_exposure",
    ) -> Dict[str, Any]:
        pressure = float(event_payload.metadata.get("pressure_level", event_payload.intensity or 0.5))
        exposure = float(event_payload.metadata.get("exposure_risk", 0.5))
        moral_cost = float(event_payload.metadata.get("moral_cost", 0.5))

        leverage = self.create_leverage_record(
            leverage_id=f"lev_{event_payload.event_id}_{holder_id}_{target_id}",
            leverage_type=leverage_type,
            holder_id=holder_id,
            target_id=target_id,
            demand=demand,
            threat=threat,
            linked_secret_ids=list(event_payload.metadata.get("linked_secret_ids", [])),
            linked_evidence_ids=list(event_payload.metadata.get("linked_evidence_ids", [])),
            linked_rumor_ids=list(event_payload.metadata.get("linked_rumor_ids", [])),
            linked_obligation_ids=list(event_payload.metadata.get("linked_obligation_ids", [])),
            witness_ids=list(event_payload.witness_ids),
            involved_faction_ids=list(event_payload.involved_faction_ids),
            pressure_level=pressure,
            exposure_risk=exposure,
            target_resistance=float(event_payload.metadata.get("target_resistance", 0.5)),
            moral_cost=moral_cost,
            deadline_condition=event_payload.metadata.get("deadline_condition"),
            metadata={"source_event_id": event_payload.event_id},
        )

        return {
            "success": True,
            "engine_name": self.engine_name,
            "leverage_record": leverage,
        }

    def evaluate_leverage_validity(
        self,
        *,
        state: SimulationState,
        leverage_id: str,
    ) -> Dict[str, Any]:
        leverage = state.metadata.get("leverage_registry", {}).get(leverage_id)
        blockers: List[str] = []
        warnings: List[str] = []
        passed: List[str] = []

        if not leverage:
            return {
                "success": False,
                "engine_name": self.engine_name,
                "leverage_id": leverage_id,
                "valid": False,
                "blockers": [f"leverage {leverage_id} is not registered"],
                "warnings": [],
                "passed_checks": [],
            }

        passed.append("leverage_registered")

        holder_id = leverage["holder_id"]
        target_id = leverage["target_id"]

        if holder_id not in state.character_states and holder_id not in state.entity_states:
            blockers.append(f"holder {holder_id} is missing from simulation state")
        else:
            passed.append("holder_exists")

        if target_id not in state.character_states and target_id not in state.entity_states:
            blockers.append(f"target {target_id} is missing from simulation state")
        else:
            passed.append("target_exists")

        if leverage["status"] not in self.STATUS_VALUES:
            warnings.append("leverage has unknown status")

        secret_report = self._validate_secret_access(state, leverage)
        evidence_report = self._validate_evidence_access(state, leverage)
        obligation_report = self._validate_obligation_access(state, leverage)

        for report in [secret_report, evidence_report, obligation_report]:
            blockers.extend(report["blockers"])
            warnings.extend(report["warnings"])
            passed.extend(report["passed_checks"])

        valid = len(blockers) == 0

        return {
            "success": True,
            "engine_name": self.engine_name,
            "leverage_id": leverage_id,
            "valid": valid,
            "pressure_score": self._pressure_score(leverage),
            "exposure_power": self._exposure_power(state, leverage),
            "target_compliance_probability": self._compliance_probability(state, leverage),
            "passed_checks": passed,
            "blockers": blockers,
            "warnings": warnings,
            "recommendation": "allow_leverage_attempt" if valid else "fix_leverage_basis",
        }

    def attempt_leverage(
        self,
        *,
        state: SimulationState,
        leverage_id: str,
        attempt_event_id: str,
        attempt_intensity: float = 0.7,
    ) -> Dict[str, Any]:
        validity = self.evaluate_leverage_validity(state=state, leverage_id=leverage_id)
        leverage = state.metadata.get("leverage_registry", {}).get(leverage_id)

        if not leverage:
            return {
                "success": False,
                "engine_name": self.engine_name,
                "leverage_id": leverage_id,
                "updated_state": state,
                "blockers": validity.get("blockers", []),
                "warnings": validity.get("warnings", []),
            }

        if not validity["valid"]:
            return {
                "success": False,
                "engine_name": self.engine_name,
                "leverage_id": leverage_id,
                "updated_state": state,
                "blockers": validity["blockers"],
                "warnings": validity["warnings"],
            }

        leverage["attempt_event_ids"] = self._unique(leverage.get("attempt_event_ids", []) + [attempt_event_id])
        leverage["pressure_level"] = self._bounded(float(leverage.get("pressure_level", 0.5)) + attempt_intensity * 0.12)
        leverage["exposure_risk"] = self._bounded(float(leverage.get("exposure_risk", 0.5)) + attempt_intensity * 0.08)

        compliance_probability = self._compliance_probability(state, leverage)

        state.metadata.setdefault("leverage_history", []).append(
            {
                "action": "attempt_leverage",
                "leverage_id": leverage_id,
                "attempt_event_id": attempt_event_id,
                "attempt_intensity": attempt_intensity,
                "compliance_probability": compliance_probability,
            }
        )

        return {
            "success": True,
            "engine_name": self.engine_name,
            "leverage_id": leverage_id,
            "validity": validity,
            "compliance_probability": compliance_probability,
            "updated_leverage": leverage,
            "updated_state": state,
        }

    def resolve_leverage_outcome(
        self,
        *,
        state: SimulationState,
        leverage_id: str,
        outcome: str,
        outcome_event_id: str,
        notes: str = "",
    ) -> Dict[str, Any]:
        leverage = state.metadata.get("leverage_registry", {}).get(leverage_id)
        if not leverage:
            return {
                "success": False,
                "engine_name": self.engine_name,
                "leverage_id": leverage_id,
                "errors": [f"leverage {leverage_id} is not registered"],
                "updated_state": state,
            }

        if outcome == "accepted":
            leverage["status"] = "accepted"
            leverage["compliance_event_ids"] = self._unique(leverage.get("compliance_event_ids", []) + [outcome_event_id])
        elif outcome == "refused":
            leverage["status"] = "refused"
            leverage["refusal_event_ids"] = self._unique(leverage.get("refusal_event_ids", []) + [outcome_event_id])
            leverage["exposure_risk"] = self._bounded(float(leverage.get("exposure_risk", 0.5)) + 0.22)
        elif outcome == "countered":
            leverage["status"] = "countered"
            leverage["counter_event_ids"] = self._unique(leverage.get("counter_event_ids", []) + [outcome_event_id])
            leverage["pressure_level"] = self._bounded(float(leverage.get("pressure_level", 0.5)) - 0.20)
        elif outcome == "exposed":
            leverage["status"] = "exposed"
            leverage["exposure_event_ids"] = self._unique(leverage.get("exposure_event_ids", []) + [outcome_event_id])
            leverage["exposure_risk"] = 1.0
        elif outcome == "resolved":
            leverage["status"] = "resolved"
        else:
            leverage["status"] = "failed"

        leverage["resolution_notes"] = self._unique(leverage.get("resolution_notes", []) + [notes] if notes else leverage.get("resolution_notes", []))

        state.metadata.setdefault("leverage_history", []).append(
            {
                "action": "resolve_leverage_outcome",
                "leverage_id": leverage_id,
                "outcome": outcome,
                "outcome_event_id": outcome_event_id,
                "notes": notes,
            }
        )

        return {
            "success": True,
            "engine_name": self.engine_name,
            "leverage_id": leverage_id,
            "outcome": outcome,
            "updated_leverage": leverage,
            "updated_state": state,
        }

    def build_relationship_delta_from_leverage(
        self,
        *,
        state: SimulationState,
        leverage_id: str,
        outcome: str,
    ) -> RelationshipDelta:
        leverage = state.metadata.get("leverage_registry", {}).get(leverage_id, {})
        holder_id = leverage.get("holder_id", "unknown_holder")
        target_id = leverage.get("target_id", "unknown_target")
        relationship_id = self._relationship_id(holder_id, target_id)

        pressure = self._pressure_score(leverage)
        moral = float(leverage.get("moral_cost", 0.5))

        values = {
            "trust_delta": 0.0,
            "fear_delta": 0.0,
            "resentment_delta": 0.0,
            "dependency_delta": 0.0,
            "power_imbalance_delta": 0.0,
            "knowledge_asymmetry_delta": 0.0,
            "betrayal_risk_delta": 0.0,
            "repair_potential_delta": 0.0,
        }

        if outcome == "attempted":
            values.update(
                trust_delta=-0.10 * pressure,
                fear_delta=0.10 * pressure,
                resentment_delta=0.12 * pressure,
                power_imbalance_delta=0.10 * pressure,
                knowledge_asymmetry_delta=0.12 * pressure,
            )
        elif outcome == "accepted":
            values.update(
                trust_delta=-0.18 * pressure,
                fear_delta=0.16 * pressure,
                resentment_delta=0.18 * pressure,
                dependency_delta=0.10 * pressure,
                power_imbalance_delta=0.18 * pressure,
                betrayal_risk_delta=0.12 * pressure,
                repair_potential_delta=-0.08 * moral,
            )
        elif outcome == "refused":
            values.update(
                trust_delta=-0.10 * pressure,
                resentment_delta=0.12 * pressure,
                rivalry_delta=0.0,
                betrayal_risk_delta=0.18 * pressure,
                repair_potential_delta=0.05,
            )
        elif outcome == "countered":
            values.update(
                trust_delta=-0.06 * pressure,
                resentment_delta=0.08 * pressure,
                power_imbalance_delta=-0.12 * pressure,
                repair_potential_delta=0.04,
            )
        elif outcome == "exposed":
            values.update(
                trust_delta=-0.25 * pressure,
                fear_delta=0.12 * pressure,
                resentment_delta=0.25 * pressure,
                betrayal_risk_delta=0.22 * pressure,
                repair_potential_delta=-0.14 * moral,
            )

        allowed = {
            "trust_delta",
            "fear_delta",
            "resentment_delta",
            "dependency_delta",
            "power_imbalance_delta",
            "knowledge_asymmetry_delta",
            "betrayal_risk_delta",
            "repair_potential_delta",
        }

        return RelationshipDelta(
            simulation_id=state.simulation_id,
            source_engine=self.engine_name,
            operation=DeltaOperation.INCREMENT,
            target_entity_id=relationship_id,
            target_path=f"relationship_states.{relationship_id}",
            relationship_id=relationship_id,
            character_a_id=holder_id,
            character_b_id=target_id,
            relationship_event_label=f"leverage_{outcome}",
            reason=f"Leverage {leverage_id} outcome: {outcome}.",
            **{key: round(value, 3) for key, value in values.items() if key in allowed},
        )

    def build_reputation_delta_from_leverage(
        self,
        *,
        state: SimulationState,
        leverage_id: str,
        affected_character_id: str,
        outcome: str,
        audience_type: str = "public",
    ) -> ReputationDelta:
        leverage = state.metadata.get("leverage_registry", {}).get(leverage_id, {})
        pressure = self._pressure_score(leverage)
        exposure = self._exposure_power(state, leverage)

        if outcome == "exposed":
            rep = -0.28 * exposure
            trust = -0.22 * exposure
            respect = -0.18 * exposure
            fear = 0.05 * pressure
        elif outcome == "accepted":
            rep = -0.06 * pressure
            trust = -0.08 * pressure
            respect = -0.05 * pressure
            fear = 0.04 * pressure
        elif outcome == "countered":
            rep = 0.06 * pressure
            trust = 0.04 * pressure
            respect = 0.08 * pressure
            fear = -0.02 * pressure
        else:
            rep = -0.04 * pressure
            trust = -0.04 * pressure
            respect = -0.02 * pressure
            fear = 0.02 * pressure

        return ReputationDelta(
            simulation_id=state.simulation_id,
            source_engine=self.engine_name,
            operation=DeltaOperation.INCREMENT,
            target_entity_id=affected_character_id,
            target_path=f"character_states.{affected_character_id}.metadata.reputation_state.{audience_type}",
            character_id=affected_character_id,
            audience_type=audience_type,
            reputation_score_delta=round(rep, 3),
            trust_score_delta=round(trust, 3),
            respect_score_delta=round(respect, 3),
            fear_score_delta=round(fear, 3),
            reason=f"Leverage {leverage_id} reputation outcome: {outcome}.",
        )

    def build_knowledge_delta_from_leverage_exposure(
        self,
        *,
        state: SimulationState,
        leverage_id: str,
        listener_id: str,
        source_event_id: Optional[str] = None,
    ) -> KnowledgeDelta:
        leverage = state.metadata.get("leverage_registry", {}).get(leverage_id, {})
        confidence_updates = {}

        for secret_id in leverage.get("linked_secret_ids", []):
            confidence_updates[secret_id] = min(0.85, self._exposure_power(state, leverage))

        return KnowledgeDelta(
            simulation_id=state.simulation_id,
            source_engine=self.engine_name,
            source_event_id=source_event_id,
            operation=DeltaOperation.APPEND,
            target_entity_id=listener_id,
            target_path=f"knowledge_states.{listener_id}",
            knowledge_holder_id=listener_id,
            suspected_secret_ids_added=list(leverage.get("linked_secret_ids", [])),
            evidence_ids_seen=list(leverage.get("linked_evidence_ids", [])),
            knowledge_confidence_updates=confidence_updates,
            knowledge_path=["leverage_exposure"],
            no_magic_knowledge_checked=True,
            reason=f"Leverage {leverage_id} exposed information to {listener_id}.",
        )

    def build_delta_batch_for_leverage_outcome(
        self,
        *,
        state: SimulationState,
        leverage_id: str,
        outcome: str,
        exposed_to_ids: List[str] | None = None,
        audience_type: str = "public",
    ) -> DeltaBatch:
        leverage = state.metadata.get("leverage_registry", {}).get(leverage_id, {})
        holder_id = leverage.get("holder_id", "unknown_holder")
        target_id = leverage.get("target_id", "unknown_target")

        relationship_delta = self.build_relationship_delta_from_leverage(
            state=state,
            leverage_id=leverage_id,
            outcome=outcome,
        )

        reputation_deltas = []
        if outcome in {"accepted", "refused", "countered", "exposed"}:
            affected = target_id if outcome in {"accepted", "exposed"} else holder_id
            reputation_deltas.append(
                self.build_reputation_delta_from_leverage(
                    state=state,
                    leverage_id=leverage_id,
                    affected_character_id=affected,
                    outcome=outcome,
                    audience_type=audience_type,
                )
            )

        knowledge_deltas = []
        if outcome == "exposed":
            for listener_id in exposed_to_ids or []:
                knowledge_deltas.append(
                    self.build_knowledge_delta_from_leverage_exposure(
                        state=state,
                        leverage_id=leverage_id,
                        listener_id=listener_id,
                    )
                )

        ordered = [relationship_delta] + reputation_deltas + knowledge_deltas

        return DeltaBatch(
            simulation_id=state.simulation_id,
            source_engine=self.engine_name,
            relationship_deltas=[relationship_delta],
            reputation_deltas=reputation_deltas,
            knowledge_deltas=knowledge_deltas,
            application_order=[delta.delta_id for delta in ordered],
        )

    def build_leverage_map(self, *, state: SimulationState) -> Dict[str, Any]:
        registry = state.metadata.get("leverage_registry", {})
        records = {}

        for leverage_id, leverage in registry.items():
            records[leverage_id] = {
                "leverage_id": leverage_id,
                "leverage_type": leverage.get("leverage_type"),
                "holder_id": leverage.get("holder_id"),
                "target_id": leverage.get("target_id"),
                "demand": leverage.get("demand"),
                "threat": leverage.get("threat"),
                "status": leverage.get("status"),
                "pressure_score": self._pressure_score(leverage),
                "exposure_power": self._exposure_power(state, leverage),
                "target_compliance_probability": self._compliance_probability(state, leverage),
                "linked_secret_ids": leverage.get("linked_secret_ids", []),
                "linked_evidence_ids": leverage.get("linked_evidence_ids", []),
                "linked_obligation_ids": leverage.get("linked_obligation_ids", []),
                "has_counter_leverage": self._has_counter_leverage(state, leverage),
            }

        return {
            "success": True,
            "engine_name": self.engine_name,
            "leverage_count": len(records),
            "leverage_records": records,
            "warnings": self._leverage_map_warnings(records),
        }

    def _validate_secret_access(self, state: SimulationState, leverage: Dict[str, Any]) -> Dict[str, Any]:
        blockers: List[str] = []
        warnings: List[str] = []
        passed: List[str] = []

        holder_id = leverage.get("holder_id")
        secret_ids = leverage.get("linked_secret_ids", [])

        if not secret_ids:
            return {"blockers": blockers, "warnings": warnings, "passed_checks": ["no_secret_leverage_required"]}

        knowledge = state.knowledge_states.get(holder_id)
        for secret_id in secret_ids:
            if knowledge and secret_id in knowledge.known_secret_ids:
                passed.append(f"holder_knows_{secret_id}")
            elif knowledge and secret_id in knowledge.suspected_secret_ids:
                warnings.append(f"holder only suspects {secret_id}; leverage is weaker")
            else:
                blockers.append(f"holder {holder_id} does not know/suspect linked secret {secret_id}")

        return {"blockers": blockers, "warnings": warnings, "passed_checks": passed}

    def _validate_evidence_access(self, state: SimulationState, leverage: Dict[str, Any]) -> Dict[str, Any]:
        blockers: List[str] = []
        warnings: List[str] = []
        passed: List[str] = []

        holder_id = leverage.get("holder_id")
        evidence_ids = leverage.get("linked_evidence_ids", [])

        if not evidence_ids:
            return {"blockers": blockers, "warnings": warnings, "passed_checks": ["no_evidence_leverage_required"]}

        evidence_registry = state.metadata.get("evidence_registry", {})
        holder_knowledge = state.knowledge_states.get(holder_id)

        for evidence_id in evidence_ids:
            evidence = evidence_registry.get(evidence_id)
            if not evidence:
                blockers.append(f"linked evidence {evidence_id} is not registered")
                continue
            if evidence.get("destroyed"):
                blockers.append(f"linked evidence {evidence_id} is destroyed")
            if holder_id == evidence.get("owner_id") or holder_id in evidence.get("seen_by_ids", []):
                passed.append(f"holder_has_evidence_{evidence_id}")
            elif holder_knowledge and evidence_id in holder_knowledge.evidence_seen_ids:
                passed.append(f"holder_has_seen_evidence_{evidence_id}")
            else:
                warnings.append(f"holder may not have direct access to evidence {evidence_id}")

        return {"blockers": blockers, "warnings": warnings, "passed_checks": passed}

    def _validate_obligation_access(self, state: SimulationState, leverage: Dict[str, Any]) -> Dict[str, Any]:
        blockers: List[str] = []
        warnings: List[str] = []
        passed: List[str] = []

        obligation_ids = leverage.get("linked_obligation_ids", [])
        if not obligation_ids:
            return {"blockers": blockers, "warnings": warnings, "passed_checks": ["no_obligation_leverage_required"]}

        obligation_registry = state.metadata.get("obligation_registry", {})
        for obligation_id in obligation_ids:
            obligation = obligation_registry.get(obligation_id)
            if not obligation:
                blockers.append(f"linked obligation {obligation_id} is not registered")
                continue
            if obligation.get("status") in {"fulfilled", "forgiven", "cancelled"}:
                warnings.append(f"obligation {obligation_id} may no longer be useful leverage")
            else:
                passed.append(f"obligation_{obligation_id}_usable")

        return {"blockers": blockers, "warnings": warnings, "passed_checks": passed}

    def _pressure_score(self, leverage: Dict[str, Any]) -> float:
        return round(
            min(
                1.0,
                float(leverage.get("pressure_level", 0.5)) * 0.35
                + float(leverage.get("exposure_risk", 0.5)) * 0.25
                + float(leverage.get("moral_cost", 0.5)) * 0.20
                + len(leverage.get("linked_secret_ids", [])) * 0.07
                + len(leverage.get("linked_evidence_ids", [])) * 0.06
                + len(leverage.get("linked_obligation_ids", [])) * 0.05,
            ),
            3,
        )

    def _exposure_power(self, state: SimulationState, leverage: Dict[str, Any]) -> float:
        evidence_registry = state.metadata.get("evidence_registry", {})
        evidence_power = 0.0
        for evidence_id in leverage.get("linked_evidence_ids", []):
            evidence = evidence_registry.get(evidence_id, {})
            evidence_power += float(evidence.get("reliability", 0.45)) * 0.12
            evidence_power += float(evidence.get("legal_validity", 0.45)) * 0.08

        secret_power = len(leverage.get("linked_secret_ids", [])) * 0.12
        rumor_power = len(leverage.get("linked_rumor_ids", [])) * 0.06

        return round(
            min(
                1.0,
                float(leverage.get("exposure_risk", 0.5)) * 0.35
                + evidence_power
                + secret_power
                + rumor_power,
            ),
            3,
        )

    def _compliance_probability(self, state: SimulationState, leverage: Dict[str, Any]) -> float:
        pressure = self._pressure_score(leverage)
        exposure = self._exposure_power(state, leverage)
        resistance = float(leverage.get("target_resistance", 0.5))
        counter = 0.18 if self._has_counter_leverage(state, leverage) else 0.0

        return round(max(0.0, min(1.0, pressure * 0.45 + exposure * 0.35 - resistance * 0.25 - counter)), 3)

    def _has_counter_leverage(self, state: SimulationState, leverage: Dict[str, Any]) -> bool:
        holder_id = leverage.get("holder_id")
        target_id = leverage.get("target_id")

        for other in state.metadata.get("leverage_registry", {}).values():
            if other.get("holder_id") == target_id and other.get("target_id") == holder_id and other.get("status") == "active":
                return True

        return False

    def _relationship_id(self, a: str, b: str) -> str:
        return "rel_" + "_".join(sorted([a, b]))

    def _leverage_map_warnings(self, records: Dict[str, Dict[str, Any]]) -> List[str]:
        warnings = []
        for leverage_id, record in records.items():
            if record["status"] == "active" and record["target_compliance_probability"] >= 0.75:
                warnings.append(f"{leverage_id} has high coercion/compliance pressure")
            if record["exposure_power"] >= 0.75:
                warnings.append(f"{leverage_id} has high exposure power")
            if record["has_counter_leverage"]:
                warnings.append(f"{leverage_id} has active counter-leverage")
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

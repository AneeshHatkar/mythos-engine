from typing import Any, Dict, List, Optional

from backend.app.schemas.simulation import (
    DeltaBatch,
    DeltaOperation,
    KnowledgeDelta,
    SimulationEventPayload,
    SimulationEventVisibility,
    SimulationState,
)


class EvidenceEngine:
    """Tracks evidence objects, reliability, legal validity, visibility, and belief effects.

    Evidence is the bridge between secrets and believable knowledge. Characters
    should not simply know a truth; they need evidence, witnesses, memory, rumor,
    or a valid information path.
    """

    engine_name = "simulation.evidence_engine"

    EVIDENCE_TYPES = {
        "physical",
        "document",
        "witness",
        "memory",
        "forged",
        "prophecy",
        "object_linked",
        "rumor_trace",
        "legal_record",
        "magical_trace",
        "digital_or_archive_record",
    }

    def create_evidence_record(
        self,
        *,
        evidence_id: str,
        evidence_type: str,
        summary: str,
        linked_secret_ids: List[str] | None = None,
        truth_value: str = "unknown",
        reliability: float = 0.5,
        legal_validity: float = 0.5,
        owner_id: Optional[str] = None,
        current_location_id: Optional[str] = None,
        seen_by_ids: List[str] | None = None,
        believed_by_ids: List[str] | None = None,
        disputed_by_ids: List[str] | None = None,
        forged_by_id: Optional[str] = None,
        risk_if_exposed: str = "reputation damage",
        metadata: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        if evidence_type not in self.EVIDENCE_TYPES:
            evidence_type = "object_linked"

        return {
            "evidence_id": evidence_id,
            "evidence_type": evidence_type,
            "summary": summary,
            "linked_secret_ids": linked_secret_ids or [],
            "truth_value": truth_value,
            "reliability": self._bounded_value(reliability),
            "legal_validity": self._bounded_value(legal_validity),
            "owner_id": owner_id,
            "current_location_id": current_location_id,
            "seen_by_ids": seen_by_ids or [],
            "believed_by_ids": believed_by_ids or [],
            "disputed_by_ids": disputed_by_ids or [],
            "forged_by_id": forged_by_id,
            "risk_if_exposed": risk_if_exposed,
            "exposed": False,
            "destroyed": False,
            "suppressed": False,
            "metadata": metadata or {},
        }

    def register_evidence_on_state(
        self,
        *,
        state: SimulationState,
        evidence_record: Dict[str, Any],
    ) -> Dict[str, Any]:
        evidence_id = evidence_record["evidence_id"]
        state.metadata.setdefault("evidence_registry", {})[evidence_id] = evidence_record

        for viewer_id in evidence_record.get("seen_by_ids", []):
            knowledge = self._get_or_create_knowledge(state, viewer_id)
            knowledge.evidence_seen_ids = self._unique(knowledge.evidence_seen_ids + [evidence_id])

            for secret_id in evidence_record.get("linked_secret_ids", []):
                if evidence_record.get("truth_value") == "true" and evidence_record.get("reliability", 0) >= 0.65:
                    knowledge.suspected_secret_ids = self._unique(knowledge.suspected_secret_ids + [secret_id])
                    knowledge.knowledge_confidence[secret_id] = max(
                        knowledge.knowledge_confidence.get(secret_id, 0.0),
                        min(0.75, evidence_record.get("reliability", 0.5)),
                    )

        state.metadata.setdefault("evidence_history", []).append(
            {
                "action": "register_evidence",
                "evidence_id": evidence_id,
                "linked_secret_ids": evidence_record.get("linked_secret_ids", []),
                "seen_by_ids": evidence_record.get("seen_by_ids", []),
            }
        )

        return {
            "success": True,
            "engine_name": self.engine_name,
            "evidence_id": evidence_id,
            "updated_state": state,
        }

    def evaluate_evidence_access(
        self,
        *,
        state: SimulationState,
        evidence_id: str,
        actor_id: str,
        event_payload: Optional[SimulationEventPayload] = None,
    ) -> Dict[str, Any]:
        evidence = state.metadata.get("evidence_registry", {}).get(evidence_id)
        blockers: List[str] = []
        warnings: List[str] = []
        passed: List[str] = []

        if not evidence:
            blockers.append(f"evidence {evidence_id} is not registered")
            return self._access_result(evidence_id, actor_id, False, blockers, warnings, passed)

        passed.append("evidence_registered")

        if evidence.get("destroyed"):
            blockers.append(f"evidence {evidence_id} is destroyed")

        if evidence.get("suppressed"):
            warnings.append(f"evidence {evidence_id} is suppressed; access may create legal/faction risk")

        actor_state = state.character_states.get(actor_id)
        actor_location = actor_state.current_location_id if actor_state else None
        evidence_location = evidence.get("current_location_id")

        if actor_id == evidence.get("owner_id"):
            passed.append("actor_owns_evidence")
        elif actor_id in evidence.get("seen_by_ids", []):
            passed.append("actor_already_saw_evidence")
        elif event_payload and actor_id in event_payload.actor_ids + event_payload.target_ids + event_payload.witness_ids:
            if not evidence_location or not event_payload.location_id or evidence_location == event_payload.location_id:
                passed.append("actor_can_access_evidence_through_event_presence")
            else:
                warnings.append("actor participates in event but evidence location differs")
        elif actor_location and evidence_location and actor_location == evidence_location:
            passed.append("actor_currently_at_evidence_location")
        else:
            blockers.append(f"{actor_id} has no valid access path to evidence {evidence_id}")

        valid = len(blockers) == 0
        return self._access_result(evidence_id, actor_id, valid, blockers, warnings, passed)

    def reveal_evidence_to_character(
        self,
        *,
        state: SimulationState,
        evidence_id: str,
        viewer_id: str,
        event_payload: Optional[SimulationEventPayload] = None,
        confidence_from_viewing: Optional[float] = None,
    ) -> Dict[str, Any]:
        access = self.evaluate_evidence_access(
            state=state,
            evidence_id=evidence_id,
            actor_id=viewer_id,
            event_payload=event_payload,
        )

        if not access["can_access"]:
            return {
                "success": False,
                "engine_name": self.engine_name,
                "evidence_id": evidence_id,
                "viewer_id": viewer_id,
                "updated_state": state,
                "blockers": access["blockers"],
                "warnings": access["warnings"],
            }

        evidence = state.metadata["evidence_registry"][evidence_id]
        evidence["seen_by_ids"] = self._unique(evidence.get("seen_by_ids", []) + [viewer_id])

        knowledge = self._get_or_create_knowledge(state, viewer_id)
        knowledge.evidence_seen_ids = self._unique(knowledge.evidence_seen_ids + [evidence_id])

        confidence = confidence_from_viewing
        if confidence is None:
            confidence = self._evidence_confidence(evidence)

        for secret_id in evidence.get("linked_secret_ids", []):
            if evidence.get("truth_value") == "true":
                if evidence.get("reliability", 0.0) >= 0.78 and evidence.get("legal_validity", 0.0) >= 0.6:
                    knowledge.known_secret_ids = self._unique(knowledge.known_secret_ids + [secret_id])
                else:
                    knowledge.suspected_secret_ids = self._unique(knowledge.suspected_secret_ids + [secret_id])

                knowledge.knowledge_confidence[secret_id] = max(
                    knowledge.knowledge_confidence.get(secret_id, 0.0),
                    confidence,
                )

            elif evidence.get("truth_value") == "false":
                falsehood_id = f"falsehood_from_{evidence_id}"
                knowledge.believed_falsehood_ids = self._unique(knowledge.believed_falsehood_ids + [falsehood_id])
                knowledge.knowledge_confidence[falsehood_id] = max(
                    knowledge.knowledge_confidence.get(falsehood_id, 0.0),
                    confidence,
                )

        state.metadata.setdefault("evidence_history", []).append(
            {
                "action": "reveal_evidence_to_character",
                "evidence_id": evidence_id,
                "viewer_id": viewer_id,
                "source_event_id": event_payload.event_id if event_payload else None,
                "confidence": confidence,
            }
        )

        return {
            "success": True,
            "engine_name": self.engine_name,
            "evidence_id": evidence_id,
            "viewer_id": viewer_id,
            "access": access,
            "updated_state": state,
        }

    def build_knowledge_delta_from_evidence(
        self,
        *,
        state: SimulationState,
        evidence_id: str,
        viewer_id: str,
        event_payload: SimulationEventPayload,
    ) -> KnowledgeDelta:
        evidence = state.metadata.get("evidence_registry", {}).get(evidence_id, {})
        confidence = self._evidence_confidence(evidence)

        secret_ids = []
        suspected_secret_ids = []
        falsehood_ids = []

        for secret_id in evidence.get("linked_secret_ids", []):
            if evidence.get("truth_value") == "true":
                if evidence.get("reliability", 0.0) >= 0.78 and evidence.get("legal_validity", 0.0) >= 0.6:
                    secret_ids.append(secret_id)
                else:
                    suspected_secret_ids.append(secret_id)
            elif evidence.get("truth_value") == "false":
                falsehood_ids.append(f"falsehood_from_{evidence_id}")

        confidence_updates = {}
        for item in secret_ids + suspected_secret_ids + falsehood_ids:
            confidence_updates[item] = confidence

        return KnowledgeDelta(
            simulation_id=state.simulation_id,
            source_engine=self.engine_name,
            source_event_id=event_payload.event_id,
            operation=DeltaOperation.APPEND,
            target_entity_id=viewer_id,
            target_path=f"knowledge_states.{viewer_id}",
            knowledge_holder_id=viewer_id,
            secret_ids_added=secret_ids,
            suspected_secret_ids_added=suspected_secret_ids,
            evidence_ids_seen=[evidence_id],
            falsehood_ids_believed=falsehood_ids,
            knowledge_confidence_updates=confidence_updates,
            knowledge_path=["evidence_seen"],
            witness_ids=[viewer_id] if viewer_id in event_payload.witness_ids else [],
            no_magic_knowledge_checked=True,
            reason=f"Evidence {evidence_id} viewed by {viewer_id}.",
        )

    def evaluate_evidence_for_trial_or_public_claim(
        self,
        *,
        state: SimulationState,
        evidence_ids: List[str],
        claim_secret_id: str,
        audience_type: str = "court",
    ) -> Dict[str, Any]:
        records = []
        blockers: List[str] = []
        warnings: List[str] = []
        passed: List[str] = []

        total_strength = 0.0

        for evidence_id in evidence_ids:
            evidence = state.metadata.get("evidence_registry", {}).get(evidence_id)
            if not evidence:
                blockers.append(f"evidence {evidence_id} is not registered")
                continue

            linked = claim_secret_id in evidence.get("linked_secret_ids", [])
            if not linked:
                warnings.append(f"evidence {evidence_id} is not linked to claim {claim_secret_id}")

            if evidence.get("destroyed"):
                blockers.append(f"evidence {evidence_id} is destroyed")
                continue

            strength = self._evidence_argument_strength(evidence, audience_type=audience_type)
            total_strength += strength

            records.append(
                {
                    "evidence_id": evidence_id,
                    "linked_to_claim": linked,
                    "truth_value": evidence.get("truth_value"),
                    "reliability": evidence.get("reliability"),
                    "legal_validity": evidence.get("legal_validity"),
                    "argument_strength": strength,
                    "evidence_type": evidence.get("evidence_type"),
                }
            )

        if total_strength >= 0.75:
            passed.append("evidence_strength_sufficient")
        elif total_strength >= 0.45:
            warnings.append("evidence strength is partial; claim may create suspicion but not proof")
        else:
            blockers.append("evidence strength is too weak to support claim")

        return {
            "success": True,
            "engine_name": self.engine_name,
            "claim_secret_id": claim_secret_id,
            "audience_type": audience_type,
            "evidence_records": records,
            "total_argument_strength": round(min(1.0, total_strength), 3),
            "claim_supported": len(blockers) == 0,
            "passed_checks": passed,
            "blockers": blockers,
            "warnings": warnings,
            "recommendation": "allow_claim" if len(blockers) == 0 else "add_evidence_or_lower_claim_strength",
        }

    def mark_evidence_forged_or_disputed(
        self,
        *,
        state: SimulationState,
        evidence_id: str,
        disputed_by_id: Optional[str] = None,
        forged_by_id: Optional[str] = None,
        reliability_delta: float = -0.25,
        reason: str = "",
    ) -> Dict[str, Any]:
        evidence = state.metadata.get("evidence_registry", {}).get(evidence_id)
        if not evidence:
            return {
                "success": False,
                "engine_name": self.engine_name,
                "evidence_id": evidence_id,
                "errors": [f"evidence {evidence_id} is not registered"],
                "updated_state": state,
            }

        if disputed_by_id:
            evidence["disputed_by_ids"] = self._unique(evidence.get("disputed_by_ids", []) + [disputed_by_id])

        if forged_by_id:
            evidence["forged_by_id"] = forged_by_id
            evidence["evidence_type"] = "forged"
            evidence["truth_value"] = "false"

        evidence["reliability"] = self._bounded_value(float(evidence.get("reliability", 0.5)) + reliability_delta)

        state.metadata.setdefault("evidence_history", []).append(
            {
                "action": "mark_evidence_forged_or_disputed",
                "evidence_id": evidence_id,
                "disputed_by_id": disputed_by_id,
                "forged_by_id": forged_by_id,
                "reliability_delta": reliability_delta,
                "reason": reason,
            }
        )

        return {
            "success": True,
            "engine_name": self.engine_name,
            "evidence_id": evidence_id,
            "updated_evidence": evidence,
            "updated_state": state,
        }

    def build_evidence_map(self, *, state: SimulationState) -> Dict[str, Any]:
        registry = state.metadata.get("evidence_registry", {})
        evidence_records = {}

        for evidence_id, evidence in registry.items():
            seen_by = []
            believed_by = list(evidence.get("believed_by_ids", []))
            disputed_by = list(evidence.get("disputed_by_ids", []))

            for entity_id, knowledge in state.knowledge_states.items():
                if evidence_id in knowledge.evidence_seen_ids:
                    seen_by.append(entity_id)

            evidence_records[evidence_id] = {
                "evidence_id": evidence_id,
                "evidence_type": evidence.get("evidence_type"),
                "summary": evidence.get("summary"),
                "linked_secret_ids": evidence.get("linked_secret_ids", []),
                "truth_value": evidence.get("truth_value"),
                "reliability": evidence.get("reliability"),
                "legal_validity": evidence.get("legal_validity"),
                "owner_id": evidence.get("owner_id"),
                "current_location_id": evidence.get("current_location_id"),
                "seen_by": self._unique(seen_by + evidence.get("seen_by_ids", [])),
                "believed_by": believed_by,
                "disputed_by": disputed_by,
                "forged_by_id": evidence.get("forged_by_id"),
                "exposed": evidence.get("exposed", False),
                "destroyed": evidence.get("destroyed", False),
                "suppressed": evidence.get("suppressed", False),
                "argument_strength": self._evidence_argument_strength(evidence),
            }

        return {
            "success": True,
            "engine_name": self.engine_name,
            "evidence_count": len(evidence_records),
            "evidence_records": evidence_records,
            "warnings": self._evidence_map_warnings(evidence_records),
        }

    def build_delta_batch_for_evidence_reveal(
        self,
        *,
        state: SimulationState,
        event_payload: SimulationEventPayload,
        evidence_id: str,
        reveal_to_ids: List[str],
    ) -> DeltaBatch:
        deltas = [
            self.build_knowledge_delta_from_evidence(
                state=state,
                evidence_id=evidence_id,
                viewer_id=viewer_id,
                event_payload=event_payload,
            )
            for viewer_id in reveal_to_ids
        ]

        return DeltaBatch(
            simulation_id=state.simulation_id,
            source_event_id=event_payload.event_id,
            source_engine=self.engine_name,
            knowledge_deltas=deltas,
            application_order=[delta.delta_id for delta in deltas],
        )

    def _get_or_create_knowledge(self, state: SimulationState, entity_id: str):
        if entity_id not in state.knowledge_states:
            from backend.app.schemas.simulation import SimulationKnowledgeState

            state.knowledge_states[entity_id] = SimulationKnowledgeState(entity_id=entity_id)
        return state.knowledge_states[entity_id]

    def _evidence_confidence(self, evidence: Dict[str, Any]) -> float:
        reliability = float(evidence.get("reliability", 0.5) or 0.5)
        legal = float(evidence.get("legal_validity", 0.5) or 0.5)
        truth_bonus = 0.12 if evidence.get("truth_value") == "true" else 0.0
        forged_penalty = 0.25 if evidence.get("evidence_type") == "forged" else 0.0
        return round(max(0.0, min(1.0, reliability * 0.55 + legal * 0.33 + truth_bonus - forged_penalty)), 3)

    def _evidence_argument_strength(self, evidence: Dict[str, Any], audience_type: str = "general") -> float:
        reliability = float(evidence.get("reliability", 0.5) or 0.5)
        legal = float(evidence.get("legal_validity", 0.5) or 0.5)

        type_bonus = {
            "legal_record": 0.18,
            "document": 0.12,
            "physical": 0.10,
            "witness": 0.08,
            "memory": 0.04,
            "prophecy": -0.02,
            "rumor_trace": -0.06,
            "forged": -0.40,
        }.get(evidence.get("evidence_type"), 0.0)

        audience_bonus = 0.10 if audience_type in {"court", "trial", "legal"} and legal >= 0.65 else 0.0
        destroyed_penalty = 0.35 if evidence.get("destroyed") else 0.0
        suppressed_penalty = 0.10 if evidence.get("suppressed") else 0.0

        return round(
            max(
                0.0,
                min(
                    1.0,
                    reliability * 0.45
                    + legal * 0.35
                    + type_bonus
                    + audience_bonus
                    - destroyed_penalty
                    - suppressed_penalty,
                ),
            ),
            3,
        )

    def _access_result(
        self,
        evidence_id: str,
        actor_id: str,
        can_access: bool,
        blockers: List[str],
        warnings: List[str],
        passed: List[str],
    ) -> Dict[str, Any]:
        return {
            "success": True,
            "engine_name": self.engine_name,
            "evidence_id": evidence_id,
            "actor_id": actor_id,
            "can_access": can_access,
            "access_score": self._score(blockers, warnings),
            "passed_checks": passed,
            "blockers": blockers,
            "warnings": warnings,
            "recommendation": "allow_access" if can_access else "fix_evidence_access_path",
        }

    def _evidence_map_warnings(self, records: Dict[str, Dict[str, Any]]) -> List[str]:
        warnings = []
        for evidence_id, record in records.items():
            if not record["seen_by"]:
                warnings.append(f"{evidence_id} has not been seen by any character")
            if record["truth_value"] == "true" and record["reliability"] < 0.4:
                warnings.append(f"{evidence_id} is true but low reliability; may only create suspicion")
            if record["evidence_type"] == "forged" and not record["disputed_by"]:
                warnings.append(f"{evidence_id} is forged but undisputed")
        return warnings

    def _score(self, blockers: List[str], warnings: List[str]) -> float:
        return round(max(0.0, 1.0 - 0.25 * len(blockers) - 0.06 * len(warnings)), 3)

    def _bounded_value(self, value: float) -> float:
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

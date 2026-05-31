from typing import Any, Dict, List, Optional

from backend.app.schemas.simulation import (
    DeltaBatch,
    DeltaOperation,
    KnowledgeDelta,
    SimulationEventPayload,
    SimulationEventType,
    SimulationEventVisibility,
    SimulationKnowledgeState,
    SimulationState,
)


class KnowledgeSecretStateEngine:
    """Tracks truth, belief, suspicion, lies, evidence, and exposure paths.

    This engine prevents magic knowledge and supports mystery, betrayal,
    political intrigue, trials, rumors, and dramatic irony.
    """

    engine_name = "simulation.knowledge_secret_state_engine"

    def create_secret_record(
        self,
        *,
        secret_id: str,
        truth_statement: str,
        owner_ids: List[str] | None = None,
        knower_ids: List[str] | None = None,
        suspect_ids: List[str] | None = None,
        false_believer_ids: List[str] | None = None,
        evidence_ids: List[str] | None = None,
        risk_if_exposed: str = "relationship/reputation damage",
        exposure_difficulty: float = 0.5,
        public_if_revealed: bool = False,
        metadata: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        return {
            "secret_id": secret_id,
            "truth_statement": truth_statement,
            "owner_ids": owner_ids or [],
            "knower_ids": knower_ids or [],
            "suspect_ids": suspect_ids or [],
            "false_believer_ids": false_believer_ids or [],
            "evidence_ids": evidence_ids or [],
            "risk_if_exposed": risk_if_exposed,
            "exposure_difficulty": max(0.0, min(1.0, float(exposure_difficulty))),
            "public_if_revealed": public_if_revealed,
            "exposed": False,
            "exposed_by": None,
            "exposed_event_id": None,
            "metadata": metadata or {},
        }

    def initialize_knowledge_state(
        self,
        *,
        state: SimulationState,
        entity_id: str,
        known_secret_ids: List[str] | None = None,
        suspected_secret_ids: List[str] | None = None,
        believed_falsehood_ids: List[str] | None = None,
        evidence_seen_ids: List[str] | None = None,
        rumors_heard_ids: List[str] | None = None,
    ) -> Dict[str, Any]:
        knowledge = SimulationKnowledgeState(
            entity_id=entity_id,
            known_secret_ids=known_secret_ids or [],
            suspected_secret_ids=suspected_secret_ids or [],
            believed_falsehood_ids=believed_falsehood_ids or [],
            evidence_seen_ids=evidence_seen_ids or [],
            rumors_heard_ids=rumors_heard_ids or [],
        )

        state.knowledge_states[entity_id] = knowledge
        state.metadata.setdefault("knowledge_state_history", []).append(
            {
                "action": "initialize_knowledge_state",
                "entity_id": entity_id,
                "known_secret_count": len(knowledge.known_secret_ids),
                "suspected_secret_count": len(knowledge.suspected_secret_ids),
            }
        )

        return {
            "success": True,
            "engine_name": self.engine_name,
            "entity_id": entity_id,
            "knowledge_state": knowledge.model_dump(),
            "updated_state": state,
        }

    def register_secret_on_state(
        self,
        *,
        state: SimulationState,
        secret_record: Dict[str, Any],
    ) -> Dict[str, Any]:
        secret_id = secret_record["secret_id"]
        state.metadata.setdefault("secret_registry", {})[secret_id] = secret_record

        for holder_id in secret_record.get("knower_ids", []):
            knowledge = self._get_or_create_knowledge(state, holder_id)
            knowledge.known_secret_ids = self._unique(knowledge.known_secret_ids + [secret_id])
            knowledge.knowledge_confidence[secret_id] = 1.0

        for holder_id in secret_record.get("suspect_ids", []):
            knowledge = self._get_or_create_knowledge(state, holder_id)
            knowledge.suspected_secret_ids = self._unique(knowledge.suspected_secret_ids + [secret_id])
            knowledge.knowledge_confidence[secret_id] = max(
                knowledge.knowledge_confidence.get(secret_id, 0.0),
                0.45,
            )

        for holder_id in secret_record.get("false_believer_ids", []):
            knowledge = self._get_or_create_knowledge(state, holder_id)
            falsehood_id = f"falsehood_about_{secret_id}"
            knowledge.believed_falsehood_ids = self._unique(knowledge.believed_falsehood_ids + [falsehood_id])
            knowledge.knowledge_confidence[falsehood_id] = 0.7

        state.metadata.setdefault("knowledge_secret_history", []).append(
            {
                "action": "register_secret",
                "secret_id": secret_id,
                "knower_ids": secret_record.get("knower_ids", []),
                "suspect_ids": secret_record.get("suspect_ids", []),
            }
        )

        return {
            "success": True,
            "engine_name": self.engine_name,
            "secret_id": secret_id,
            "updated_state": state,
        }

    def build_knowledge_delta_from_event(
        self,
        *,
        state: SimulationState,
        event_payload: SimulationEventPayload,
        knowledge_holder_id: str,
        secret_ids_added: List[str] | None = None,
        suspected_secret_ids_added: List[str] | None = None,
        evidence_ids_seen: List[str] | None = None,
        rumor_ids_heard: List[str] | None = None,
        falsehood_ids_believed: List[str] | None = None,
        confidence: float = 0.75,
    ) -> KnowledgeDelta:
        path = self.infer_knowledge_path(
            state=state,
            event_payload=event_payload,
            knowledge_holder_id=knowledge_holder_id,
            evidence_ids=evidence_ids_seen or [],
        )

        confidence_updates = {}
        for sid in secret_ids_added or []:
            confidence_updates[sid] = confidence
        for sid in suspected_secret_ids_added or []:
            confidence_updates[sid] = min(confidence, 0.55)
        for fid in falsehood_ids_believed or []:
            confidence_updates[fid] = min(confidence, 0.75)

        return KnowledgeDelta(
            simulation_id=state.simulation_id,
            source_engine=self.engine_name,
            source_event_id=event_payload.event_id,
            operation=DeltaOperation.APPEND,
            target_entity_id=knowledge_holder_id,
            target_path=f"knowledge_states.{knowledge_holder_id}",
            knowledge_holder_id=knowledge_holder_id,
            secret_ids_added=secret_ids_added or [],
            suspected_secret_ids_added=suspected_secret_ids_added or [],
            evidence_ids_seen=evidence_ids_seen or [],
            rumor_ids_heard=rumor_ids_heard or [],
            falsehood_ids_believed=falsehood_ids_believed or [],
            knowledge_confidence_updates=confidence_updates,
            knowledge_path=path["knowledge_path"],
            witness_ids=path["witness_ids"],
            no_magic_knowledge_checked=path["valid"],
            reason=path["reason"],
        )

    def infer_knowledge_path(
        self,
        *,
        state: SimulationState,
        event_payload: SimulationEventPayload,
        knowledge_holder_id: str,
        evidence_ids: List[str] | None = None,
    ) -> Dict[str, Any]:
        evidence_ids = evidence_ids or []
        path: List[str] = []
        witness_ids: List[str] = []
        blockers: List[str] = []
        warnings: List[str] = []

        if knowledge_holder_id in event_payload.actor_ids:
            path.append("actor_participated")
        if knowledge_holder_id in event_payload.target_ids:
            path.append("target_participated")
        if knowledge_holder_id in event_payload.witness_ids:
            path.append("direct_witness")
            witness_ids.append(knowledge_holder_id)

        if evidence_ids:
            path.append("evidence_seen")

        if event_payload.visibility == SimulationEventVisibility.PUBLIC:
            path.append("public_event_visibility")
        elif event_payload.visibility == SimulationEventVisibility.FACTION_KNOWN:
            path.append("faction_known_visibility")
        elif event_payload.visibility == SimulationEventVisibility.READER_ONLY:
            if knowledge_holder_id not in event_payload.actor_ids + event_payload.target_ids + event_payload.witness_ids:
                blockers.append("reader-only event cannot grant character knowledge without explicit evidence/path")

        if not path:
            blockers.append("no valid participation, witness, public, faction, or evidence path")

        valid = len(blockers) == 0

        return {
            "valid": valid,
            "knowledge_path": path,
            "witness_ids": witness_ids,
            "blockers": blockers,
            "warnings": warnings,
            "reason": "Knowledge path: " + ", ".join(path) if path else "No valid knowledge path.",
        }

    def evaluate_secret_exposure(
        self,
        *,
        state: SimulationState,
        secret_id: str,
        exposer_id: str,
        audience_ids: List[str] | None = None,
        evidence_ids_used: List[str] | None = None,
    ) -> Dict[str, Any]:
        audience_ids = audience_ids or []
        evidence_ids_used = evidence_ids_used or []

        secret = state.metadata.get("secret_registry", {}).get(secret_id)
        blockers: List[str] = []
        warnings: List[str] = []
        passed: List[str] = []

        if not secret:
            blockers.append(f"secret {secret_id} is not registered")
        else:
            passed.append("secret_registered")

        exposer_knowledge = state.knowledge_states.get(exposer_id)
        if not exposer_knowledge or secret_id not in exposer_knowledge.known_secret_ids:
            blockers.append(f"exposer {exposer_id} does not know secret {secret_id}")
        else:
            passed.append("exposer_knows_secret")

        required_evidence = set(secret.get("evidence_ids", [])) if secret else set()
        used_evidence = set(evidence_ids_used)

        if required_evidence and not used_evidence.intersection(required_evidence):
            warnings.append("secret exposure lacks registered supporting evidence")
        else:
            passed.append("supporting_evidence_present_or_not_required")

        exposure_strength = self._exposure_strength(
            secret=secret or {},
            evidence_ids_used=evidence_ids_used,
            audience_ids=audience_ids,
        )

        return {
            "success": True,
            "engine_name": self.engine_name,
            "secret_id": secret_id,
            "exposer_id": exposer_id,
            "audience_ids": audience_ids,
            "can_expose": len(blockers) == 0,
            "exposure_strength": exposure_strength,
            "passed_checks": passed,
            "blockers": blockers,
            "warnings": warnings,
            "recommendation": "allow_exposure" if not blockers else "fix_exposure_path",
        }

    def expose_secret(
        self,
        *,
        state: SimulationState,
        secret_id: str,
        exposer_id: str,
        audience_ids: List[str],
        source_event_id: Optional[str] = None,
        evidence_ids_used: List[str] | None = None,
    ) -> Dict[str, Any]:
        exposure = self.evaluate_secret_exposure(
            state=state,
            secret_id=secret_id,
            exposer_id=exposer_id,
            audience_ids=audience_ids,
            evidence_ids_used=evidence_ids_used or [],
        )

        if not exposure["can_expose"]:
            return {
                "success": False,
                "engine_name": self.engine_name,
                "secret_id": secret_id,
                "updated_state": state,
                "blockers": exposure["blockers"],
                "warnings": exposure["warnings"],
            }

        secret = state.metadata["secret_registry"][secret_id]
        secret["exposed"] = True
        secret["exposed_by"] = exposer_id
        secret["exposed_event_id"] = source_event_id

        for audience_id in audience_ids:
            knowledge = self._get_or_create_knowledge(state, audience_id)
            knowledge.known_secret_ids = self._unique(knowledge.known_secret_ids + [secret_id])
            knowledge.knowledge_confidence[secret_id] = max(
                knowledge.knowledge_confidence.get(secret_id, 0.0),
                exposure["exposure_strength"],
            )

        if secret.get("public_if_revealed"):
            state.metadata.setdefault("public_knowledge_ids", [])
            state.metadata["public_knowledge_ids"] = self._unique(
                state.metadata["public_knowledge_ids"] + [secret_id]
            )

        state.metadata.setdefault("knowledge_secret_history", []).append(
            {
                "action": "expose_secret",
                "secret_id": secret_id,
                "exposer_id": exposer_id,
                "audience_ids": audience_ids,
                "source_event_id": source_event_id,
                "exposure_strength": exposure["exposure_strength"],
            }
        )

        return {
            "success": True,
            "engine_name": self.engine_name,
            "secret_id": secret_id,
            "exposure": exposure,
            "updated_state": state,
        }

    def build_secret_map(self, *, state: SimulationState) -> Dict[str, Any]:
        registry = state.metadata.get("secret_registry", {})
        secret_records = {}

        for secret_id, secret in registry.items():
            known_by = []
            suspected_by = []
            false_believed_by = []
            evidence_seen_by = []

            falsehood_id = f"falsehood_about_{secret_id}"
            evidence_ids = set(secret.get("evidence_ids", []))

            for entity_id, knowledge in state.knowledge_states.items():
                if secret_id in knowledge.known_secret_ids:
                    known_by.append(entity_id)
                if secret_id in knowledge.suspected_secret_ids:
                    suspected_by.append(entity_id)
                if falsehood_id in knowledge.believed_falsehood_ids:
                    false_believed_by.append(entity_id)
                if evidence_ids and evidence_ids.intersection(set(knowledge.evidence_seen_ids)):
                    evidence_seen_by.append(entity_id)

            secret_records[secret_id] = {
                "secret_id": secret_id,
                "truth_statement": secret.get("truth_statement"),
                "known_by": known_by,
                "suspected_by": suspected_by,
                "false_believed_by": false_believed_by,
                "evidence_seen_by": evidence_seen_by,
                "exposed": secret.get("exposed", False),
                "risk_if_exposed": secret.get("risk_if_exposed"),
                "can_be_exposed_by": self._potential_exposers(secret_id, state),
            }

        return {
            "success": True,
            "engine_name": self.engine_name,
            "secret_count": len(secret_records),
            "secret_records": secret_records,
            "dramatic_irony_records": self._dramatic_irony_records(secret_records),
            "warnings": self._secret_map_warnings(secret_records),
        }

    def build_delta_batch_for_secret_reveal(
        self,
        *,
        state: SimulationState,
        event_payload: SimulationEventPayload,
        secret_id: str,
        reveal_to_ids: List[str],
        evidence_ids_seen: List[str] | None = None,
        confidence: float = 0.85,
    ) -> DeltaBatch:
        deltas = []
        for holder_id in reveal_to_ids:
            deltas.append(
                self.build_knowledge_delta_from_event(
                    state=state,
                    event_payload=event_payload,
                    knowledge_holder_id=holder_id,
                    secret_ids_added=[secret_id],
                    evidence_ids_seen=evidence_ids_seen or [],
                    confidence=confidence,
                )
            )

        return DeltaBatch(
            simulation_id=state.simulation_id,
            source_event_id=event_payload.event_id,
            source_engine=self.engine_name,
            knowledge_deltas=deltas,
            application_order=[delta.delta_id for delta in deltas],
        )

    def _get_or_create_knowledge(self, state: SimulationState, entity_id: str) -> SimulationKnowledgeState:
        if entity_id not in state.knowledge_states:
            state.knowledge_states[entity_id] = SimulationKnowledgeState(entity_id=entity_id)
        return state.knowledge_states[entity_id]

    def _exposure_strength(
        self,
        *,
        secret: Dict[str, Any],
        evidence_ids_used: List[str],
        audience_ids: List[str],
    ) -> float:
        base = 0.45
        required = set(secret.get("evidence_ids", []))
        used = set(evidence_ids_used)

        if required and required.intersection(used):
            base += 0.35
        if len(audience_ids) >= 3:
            base += 0.10
        if secret.get("public_if_revealed"):
            base += 0.10

        difficulty = float(secret.get("exposure_difficulty", 0.5))
        base -= difficulty * 0.12

        return round(max(0.0, min(1.0, base)), 3)

    def _potential_exposers(self, secret_id: str, state: SimulationState) -> List[str]:
        exposers = []
        for entity_id, knowledge in state.knowledge_states.items():
            if secret_id in knowledge.known_secret_ids and knowledge.evidence_seen_ids:
                exposers.append(entity_id)
        return exposers

    def _dramatic_irony_records(self, secret_records: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
        records = []
        for secret_id, record in secret_records.items():
            if record["known_by"] and record["false_believed_by"]:
                records.append(
                    {
                        "secret_id": secret_id,
                        "knowers": record["known_by"],
                        "false_believers": record["false_believed_by"],
                        "dramatic_irony_type": "truth_known_by_some_falsehood_believed_by_others",
                    }
                )
            if record["known_by"] and record["suspected_by"]:
                records.append(
                    {
                        "secret_id": secret_id,
                        "knowers": record["known_by"],
                        "suspects": record["suspected_by"],
                        "dramatic_irony_type": "truth_known_by_some_suspected_by_others",
                    }
                )
        return records

    def _secret_map_warnings(self, secret_records: Dict[str, Dict[str, Any]]) -> List[str]:
        warnings = []
        for secret_id, record in secret_records.items():
            if not record["known_by"]:
                warnings.append(f"{secret_id} has no known holders")
            if not record["can_be_exposed_by"] and not record["exposed"]:
                warnings.append(f"{secret_id} has no evidence-backed exposer")
        return warnings

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

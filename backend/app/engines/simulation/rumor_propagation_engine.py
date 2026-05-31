from typing import Any, Dict, List, Optional

from backend.app.schemas.simulation import (
    DeltaBatch,
    DeltaOperation,
    KnowledgeDelta,
    ReputationDelta,
    SimulationEventPayload,
    SimulationEventVisibility,
    SimulationState,
)


class RumorPropagationEngine:
    """Models rumor spread, distortion, credibility, and reputation effects.

    Rumors are not instant global truth. They require sources, channels,
    audience paths, credibility, faction/location reach, and distortion tracking.
    """

    engine_name = "simulation.rumor_propagation_engine"

    def create_rumor_record(
        self,
        *,
        rumor_id: str,
        source_event_id: Optional[str],
        originator_id: str,
        claim: str,
        linked_secret_ids: List[str] | None = None,
        linked_evidence_ids: List[str] | None = None,
        truth_status: str = "unverified",
        credibility: float = 0.45,
        distortion_level: float = 0.15,
        emotional_charge: float = 0.5,
        origin_location_id: Optional[str] = None,
        origin_faction_id: Optional[str] = None,
        target_character_ids: List[str] | None = None,
        audience_ids: List[str] | None = None,
        metadata: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        return {
            "rumor_id": rumor_id,
            "source_event_id": source_event_id,
            "originator_id": originator_id,
            "claim": claim,
            "linked_secret_ids": linked_secret_ids or [],
            "linked_evidence_ids": linked_evidence_ids or [],
            "truth_status": truth_status,
            "credibility": self._bounded(credibility),
            "distortion_level": self._bounded(distortion_level),
            "emotional_charge": self._bounded(emotional_charge),
            "origin_location_id": origin_location_id,
            "origin_faction_id": origin_faction_id,
            "target_character_ids": target_character_ids or [],
            "audience_ids": audience_ids or [],
            "heard_by_ids": list(audience_ids or []),
            "believed_by_ids": [],
            "rejected_by_ids": [],
            "amplified_by_ids": [],
            "suppressed_by_ids": [],
            "mutation_history": [],
            "metadata": metadata or {},
        }

    def register_rumor_on_state(
        self,
        *,
        state: SimulationState,
        rumor_record: Dict[str, Any],
    ) -> Dict[str, Any]:
        rumor_id = rumor_record["rumor_id"]
        state.metadata.setdefault("rumor_registry", {})[rumor_id] = rumor_record

        for listener_id in rumor_record.get("heard_by_ids", []):
            knowledge = self._get_or_create_knowledge(state, listener_id)
            knowledge.rumors_heard_ids = self._unique(knowledge.rumors_heard_ids + [rumor_id])

            for secret_id in rumor_record.get("linked_secret_ids", []):
                if rumor_record.get("credibility", 0.0) >= 0.65 and rumor_record.get("truth_status") in {"true", "partially_true"}:
                    knowledge.suspected_secret_ids = self._unique(knowledge.suspected_secret_ids + [secret_id])
                    knowledge.knowledge_confidence[secret_id] = max(
                        knowledge.knowledge_confidence.get(secret_id, 0.0),
                        min(0.55, float(rumor_record.get("credibility", 0.45))),
                    )

        state.metadata.setdefault("rumor_history", []).append(
            {
                "action": "register_rumor",
                "rumor_id": rumor_id,
                "originator_id": rumor_record.get("originator_id"),
                "heard_by_ids": rumor_record.get("heard_by_ids", []),
            }
        )

        return {
            "success": True,
            "engine_name": self.engine_name,
            "rumor_id": rumor_id,
            "updated_state": state,
        }

    def create_rumor_from_event(
        self,
        *,
        state: SimulationState,
        event_payload: SimulationEventPayload,
        originator_id: str,
        claim: str,
        linked_secret_ids: List[str] | None = None,
        linked_evidence_ids: List[str] | None = None,
        target_character_ids: List[str] | None = None,
    ) -> Dict[str, Any]:
        audience_ids = self._initial_audience_from_event(state=state, event_payload=event_payload)

        credibility = self._initial_credibility_from_event(
            state=state,
            event_payload=event_payload,
            originator_id=originator_id,
            linked_evidence_ids=linked_evidence_ids or [],
        )

        distortion = 0.08 if event_payload.visibility == SimulationEventVisibility.PUBLIC else 0.18
        if not linked_evidence_ids:
            distortion += 0.10

        rumor = self.create_rumor_record(
            rumor_id=f"rumor_{event_payload.event_id}_{originator_id}",
            source_event_id=event_payload.event_id,
            originator_id=originator_id,
            claim=claim,
            linked_secret_ids=linked_secret_ids or [],
            linked_evidence_ids=linked_evidence_ids or [],
            truth_status="unverified" if not linked_evidence_ids else "partially_true",
            credibility=credibility,
            distortion_level=distortion,
            emotional_charge=min(1.0, float(event_payload.intensity or 0.5) + 0.10),
            origin_location_id=event_payload.location_id,
            target_character_ids=target_character_ids or list(event_payload.target_ids),
            audience_ids=audience_ids,
        )

        return {
            "success": True,
            "engine_name": self.engine_name,
            "rumor_record": rumor,
            "initial_audience_ids": audience_ids,
        }

    def propagate_rumor(
        self,
        *,
        state: SimulationState,
        rumor_id: str,
        spreader_id: str,
        max_depth: int = 1,
        target_audience_ids: List[str] | None = None,
    ) -> Dict[str, Any]:
        rumor = state.metadata.get("rumor_registry", {}).get(rumor_id)
        blockers: List[str] = []
        warnings: List[str] = []

        if not rumor:
            return {
                "success": False,
                "engine_name": self.engine_name,
                "rumor_id": rumor_id,
                "updated_state": state,
                "blockers": [f"rumor {rumor_id} is not registered"],
                "warnings": [],
            }

        if spreader_id not in rumor.get("heard_by_ids", []) and spreader_id != rumor.get("originator_id"):
            blockers.append(f"{spreader_id} has not heard rumor {rumor_id} and cannot spread it")

        if blockers:
            return {
                "success": False,
                "engine_name": self.engine_name,
                "rumor_id": rumor_id,
                "updated_state": state,
                "blockers": blockers,
                "warnings": warnings,
            }

        audience = target_audience_ids or self._reachable_audience(
            state=state,
            rumor=rumor,
            spreader_id=spreader_id,
            max_depth=max_depth,
        )

        new_listeners = []
        newly_believed = []
        rejected = []

        for listener_id in audience:
            if listener_id == spreader_id:
                continue

            if listener_id not in state.character_states and listener_id not in state.entity_states:
                warnings.append(f"listener {listener_id} is not in simulation state")
                continue

            if listener_id not in rumor["heard_by_ids"]:
                rumor["heard_by_ids"].append(listener_id)
                new_listeners.append(listener_id)

            belief = self._belief_probability(
                state=state,
                rumor=rumor,
                spreader_id=spreader_id,
                listener_id=listener_id,
            )

            knowledge = self._get_or_create_knowledge(state, listener_id)
            knowledge.rumors_heard_ids = self._unique(knowledge.rumors_heard_ids + [rumor_id])

            if belief >= 0.55:
                rumor["believed_by_ids"] = self._unique(rumor.get("believed_by_ids", []) + [listener_id])
                newly_believed.append(listener_id)

                for secret_id in rumor.get("linked_secret_ids", []):
                    knowledge.suspected_secret_ids = self._unique(knowledge.suspected_secret_ids + [secret_id])
                    knowledge.knowledge_confidence[secret_id] = max(
                        knowledge.knowledge_confidence.get(secret_id, 0.0),
                        round(min(0.65, belief), 3),
                    )
            else:
                rumor["rejected_by_ids"] = self._unique(rumor.get("rejected_by_ids", []) + [listener_id])
                rejected.append(listener_id)

        mutation = self._mutate_rumor_for_spread(rumor=rumor, spreader_id=spreader_id, audience_size=len(new_listeners))
        rumor["credibility"] = mutation["credibility_after"]
        rumor["distortion_level"] = mutation["distortion_after"]
        rumor["mutation_history"].append(mutation)

        state.metadata.setdefault("rumor_history", []).append(
            {
                "action": "propagate_rumor",
                "rumor_id": rumor_id,
                "spreader_id": spreader_id,
                "new_listeners": new_listeners,
                "newly_believed": newly_believed,
                "rejected": rejected,
            }
        )

        return {
            "success": True,
            "engine_name": self.engine_name,
            "rumor_id": rumor_id,
            "spreader_id": spreader_id,
            "new_listeners": new_listeners,
            "newly_believed": newly_believed,
            "rejected": rejected,
            "mutation": mutation,
            "warnings": warnings,
            "updated_state": state,
        }

    def build_knowledge_delta_from_rumor(
        self,
        *,
        state: SimulationState,
        rumor_id: str,
        listener_id: str,
        source_event_id: Optional[str] = None,
    ) -> KnowledgeDelta:
        rumor = state.metadata.get("rumor_registry", {}).get(rumor_id, {})
        belief = self._belief_probability(
            state=state,
            rumor=rumor,
            spreader_id=rumor.get("originator_id", ""),
            listener_id=listener_id,
        )

        suspected = []
        falsehoods = []

        if rumor.get("truth_status") in {"true", "partially_true", "unverified"}:
            if belief >= 0.45:
                suspected = list(rumor.get("linked_secret_ids", []))
        elif rumor.get("truth_status") == "false":
            falsehoods = [f"falsehood_from_{rumor_id}"]

        confidence_updates = {}
        for item in suspected + falsehoods:
            confidence_updates[item] = round(min(0.65, belief), 3)

        return KnowledgeDelta(
            simulation_id=state.simulation_id,
            source_engine=self.engine_name,
            source_event_id=source_event_id or rumor.get("source_event_id"),
            operation=DeltaOperation.APPEND,
            target_entity_id=listener_id,
            target_path=f"knowledge_states.{listener_id}",
            knowledge_holder_id=listener_id,
            suspected_secret_ids_added=suspected,
            rumor_ids_heard=[rumor_id],
            falsehood_ids_believed=falsehoods,
            knowledge_confidence_updates=confidence_updates,
            knowledge_path=["rumor_heard"],
            witness_ids=[],
            no_magic_knowledge_checked=True,
            reason=f"Rumor {rumor_id} heard by {listener_id}.",
        )

    def build_reputation_delta_from_rumor(
        self,
        *,
        state: SimulationState,
        rumor_id: str,
        target_character_id: str,
        audience_type: str = "public",
    ) -> ReputationDelta:
        rumor = state.metadata.get("rumor_registry", {}).get(rumor_id, {})
        credibility = float(rumor.get("credibility", 0.45))
        emotional = float(rumor.get("emotional_charge", 0.5))
        distortion = float(rumor.get("distortion_level", 0.15))

        negative_pressure = credibility * 0.35 + emotional * 0.25 + distortion * 0.15

        if target_character_id not in rumor.get("target_character_ids", []):
            negative_pressure *= 0.45

        return ReputationDelta(
            simulation_id=state.simulation_id,
            source_engine=self.engine_name,
            source_event_id=rumor.get("source_event_id"),
            operation=DeltaOperation.INCREMENT,
            target_entity_id=target_character_id,
            target_path=f"character_states.{target_character_id}.metadata.reputation_state.{audience_type}",
            character_id=target_character_id,
            audience_type=audience_type,
            reputation_score_delta=round(-negative_pressure, 3),
            trust_score_delta=round(-negative_pressure * 0.5, 3),
            fear_score_delta=round(negative_pressure * 0.25, 3),
            respect_score_delta=round(-negative_pressure * 0.25, 3),
            rumor_ids_amplified=[rumor_id],
            reason=f"Rumor {rumor_id} affects {target_character_id}'s reputation.",
        )

    def suppress_rumor(
        self,
        *,
        state: SimulationState,
        rumor_id: str,
        suppressor_id: str,
        suppression_power: float = 0.5,
        reason: str = "",
    ) -> Dict[str, Any]:
        rumor = state.metadata.get("rumor_registry", {}).get(rumor_id)
        if not rumor:
            return {
                "success": False,
                "engine_name": self.engine_name,
                "rumor_id": rumor_id,
                "errors": [f"rumor {rumor_id} is not registered"],
                "updated_state": state,
            }

        rumor["suppressed_by_ids"] = self._unique(rumor.get("suppressed_by_ids", []) + [suppressor_id])
        rumor["credibility"] = self._bounded(float(rumor.get("credibility", 0.45)) - suppression_power * 0.25)
        rumor["distortion_level"] = self._bounded(float(rumor.get("distortion_level", 0.15)) + suppression_power * 0.10)

        state.metadata.setdefault("rumor_history", []).append(
            {
                "action": "suppress_rumor",
                "rumor_id": rumor_id,
                "suppressor_id": suppressor_id,
                "suppression_power": suppression_power,
                "reason": reason,
            }
        )

        return {
            "success": True,
            "engine_name": self.engine_name,
            "rumor_id": rumor_id,
            "updated_rumor": rumor,
            "updated_state": state,
        }

    def build_rumor_map(self, *, state: SimulationState) -> Dict[str, Any]:
        registry = state.metadata.get("rumor_registry", {})
        records = {}

        for rumor_id, rumor in registry.items():
            records[rumor_id] = {
                "rumor_id": rumor_id,
                "claim": rumor.get("claim"),
                "source_event_id": rumor.get("source_event_id"),
                "originator_id": rumor.get("originator_id"),
                "truth_status": rumor.get("truth_status"),
                "credibility": rumor.get("credibility"),
                "distortion_level": rumor.get("distortion_level"),
                "emotional_charge": rumor.get("emotional_charge"),
                "heard_by_count": len(rumor.get("heard_by_ids", [])),
                "believed_by_count": len(rumor.get("believed_by_ids", [])),
                "rejected_by_count": len(rumor.get("rejected_by_ids", [])),
                "target_character_ids": rumor.get("target_character_ids", []),
                "linked_secret_ids": rumor.get("linked_secret_ids", []),
                "linked_evidence_ids": rumor.get("linked_evidence_ids", []),
                "spread_risk": self._spread_risk(rumor),
                "reputation_risk": self._reputation_risk(rumor),
            }

        return {
            "success": True,
            "engine_name": self.engine_name,
            "rumor_count": len(records),
            "rumor_records": records,
            "warnings": self._rumor_map_warnings(records),
        }

    def build_delta_batch_for_rumor_spread(
        self,
        *,
        state: SimulationState,
        rumor_id: str,
        listener_ids: List[str],
        target_character_ids: List[str] | None = None,
    ) -> DeltaBatch:
        knowledge_deltas = [
            self.build_knowledge_delta_from_rumor(
                state=state,
                rumor_id=rumor_id,
                listener_id=listener_id,
            )
            for listener_id in listener_ids
        ]

        reputation_deltas = [
            self.build_reputation_delta_from_rumor(
                state=state,
                rumor_id=rumor_id,
                target_character_id=target_id,
            )
            for target_id in target_character_ids or []
        ]

        return DeltaBatch(
            simulation_id=state.simulation_id,
            source_engine=self.engine_name,
            knowledge_deltas=knowledge_deltas,
            reputation_deltas=reputation_deltas,
            application_order=[delta.delta_id for delta in knowledge_deltas + reputation_deltas],
        )

    def _initial_audience_from_event(
        self,
        *,
        state: SimulationState,
        event_payload: SimulationEventPayload,
    ) -> List[str]:
        audience = []

        if event_payload.visibility == SimulationEventVisibility.PUBLIC:
            audience.extend(event_payload.witness_ids)
            audience.extend(event_payload.actor_ids)
            audience.extend(event_payload.target_ids)

            same_location = [
                cid
                for cid, char in state.character_states.items()
                if char.current_location_id and char.current_location_id == event_payload.location_id
            ]
            audience.extend(same_location)

        elif event_payload.visibility == SimulationEventVisibility.WITNESSED:
            audience.extend(event_payload.witness_ids)

        elif event_payload.visibility == SimulationEventVisibility.FACTION_KNOWN:
            audience.extend(event_payload.witness_ids)
            audience.extend(event_payload.involved_faction_ids)

        else:
            audience.extend(event_payload.witness_ids)

        return self._unique(audience)

    def _initial_credibility_from_event(
        self,
        *,
        state: SimulationState,
        event_payload: SimulationEventPayload,
        originator_id: str,
        linked_evidence_ids: List[str],
    ) -> float:
        base = 0.38

        if originator_id in event_payload.witness_ids or originator_id in event_payload.actor_ids:
            base += 0.18

        if event_payload.visibility == SimulationEventVisibility.PUBLIC:
            base += 0.18

        if linked_evidence_ids:
            evidence_registry = state.metadata.get("evidence_registry", {})
            evidence_strength = 0.0
            for eid in linked_evidence_ids:
                evidence = evidence_registry.get(eid, {})
                evidence_strength += float(evidence.get("reliability", 0.45)) * 0.08
            base += min(0.22, evidence_strength)

        return self._bounded(base)

    def _reachable_audience(
        self,
        *,
        state: SimulationState,
        rumor: Dict[str, Any],
        spreader_id: str,
        max_depth: int,
    ) -> List[str]:
        spreader = state.character_states.get(spreader_id)
        spreader_location = spreader.current_location_id if spreader else None

        audience = []

        # Same location hears first.
        for cid, char in state.character_states.items():
            if cid == spreader_id:
                continue
            if char.current_location_id and char.current_location_id == spreader_location:
                audience.append(cid)

        # Rumor edges between locations.
        if max_depth >= 1 and spreader_location:
            rumor_edges = state.world_state.metadata.get("rumor_edges", [])
            reachable_locations = {spreader_location}
            for edge in rumor_edges:
                source = edge.get("from_location_id")
                target = edge.get("to_location_id")
                if source == spreader_location:
                    reachable_locations.add(target)
                if edge.get("bidirectional", True) and target == spreader_location:
                    reachable_locations.add(source)

            for cid, char in state.character_states.items():
                if char.current_location_id in reachable_locations:
                    audience.append(cid)

        return self._unique(audience)

    def _belief_probability(
        self,
        *,
        state: SimulationState,
        rumor: Dict[str, Any],
        spreader_id: str,
        listener_id: str,
    ) -> float:
        credibility = float(rumor.get("credibility", 0.45))
        emotional = float(rumor.get("emotional_charge", 0.5))
        distortion = float(rumor.get("distortion_level", 0.15))

        relationship_bonus = self._relationship_trust_bonus(state, spreader_id, listener_id)
        evidence_bonus = 0.15 if rumor.get("linked_evidence_ids") else 0.0
        target_bias = 0.08 if listener_id in rumor.get("target_character_ids", []) else 0.0

        probability = credibility * 0.45 + emotional * 0.18 + relationship_bonus + evidence_bonus + target_bias - distortion * 0.22
        return round(max(0.0, min(1.0, probability)), 3)

    def _relationship_trust_bonus(self, state: SimulationState, a: str, b: str) -> float:
        for rel in state.relationship_states.values():
            if {rel.character_a_id, rel.character_b_id} == {a, b}:
                return round(float(rel.trust) * 0.18 + float(rel.respect) * 0.08 - float(rel.resentment) * 0.08, 3)
        return 0.0

    def _mutate_rumor_for_spread(
        self,
        *,
        rumor: Dict[str, Any],
        spreader_id: str,
        audience_size: int,
    ) -> Dict[str, Any]:
        credibility_before = float(rumor.get("credibility", 0.45))
        distortion_before = float(rumor.get("distortion_level", 0.15))

        distortion_delta = min(0.12, 0.02 * max(1, audience_size))
        credibility_delta = -distortion_delta * 0.45

        if rumor.get("linked_evidence_ids"):
            credibility_delta += 0.04

        return {
            "spreader_id": spreader_id,
            "audience_size": audience_size,
            "credibility_before": round(credibility_before, 3),
            "credibility_after": self._bounded(credibility_before + credibility_delta),
            "distortion_before": round(distortion_before, 3),
            "distortion_after": self._bounded(distortion_before + distortion_delta),
            "distortion_delta": round(distortion_delta, 3),
        }

    def _spread_risk(self, rumor: Dict[str, Any]) -> float:
        return round(
            min(
                1.0,
                float(rumor.get("credibility", 0.45)) * 0.35
                + float(rumor.get("emotional_charge", 0.5)) * 0.35
                + len(rumor.get("heard_by_ids", [])) * 0.03
                - float(rumor.get("distortion_level", 0.15)) * 0.10,
            ),
            3,
        )

    def _reputation_risk(self, rumor: Dict[str, Any]) -> float:
        return round(
            min(
                1.0,
                float(rumor.get("credibility", 0.45)) * 0.38
                + float(rumor.get("emotional_charge", 0.5)) * 0.30
                + len(rumor.get("target_character_ids", [])) * 0.08
                + len(rumor.get("linked_secret_ids", [])) * 0.08,
            ),
            3,
        )

    def _rumor_map_warnings(self, records: Dict[str, Dict[str, Any]]) -> List[str]:
        warnings = []
        for rumor_id, record in records.items():
            if record["spread_risk"] >= 0.75:
                warnings.append(f"{rumor_id} has high spread risk")
            if record["distortion_level"] >= 0.65:
                warnings.append(f"{rumor_id} is heavily distorted")
            if record["truth_status"] == "false" and record["believed_by_count"] > 0:
                warnings.append(f"{rumor_id} is false but believed by characters")
        return warnings

    def _get_or_create_knowledge(self, state: SimulationState, entity_id: str):
        if entity_id not in state.knowledge_states:
            from backend.app.schemas.simulation import SimulationKnowledgeState

            state.knowledge_states[entity_id] = SimulationKnowledgeState(entity_id=entity_id)
        return state.knowledge_states[entity_id]

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

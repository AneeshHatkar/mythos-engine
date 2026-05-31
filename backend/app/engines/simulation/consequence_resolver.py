from typing import Any, Dict, List, Optional

from backend.app.schemas.simulation import (
    DeltaBatch,
    DeltaOperation,
    FactionDelta,
    KnowledgeDelta,
    RelationshipDelta,
    ReputationDelta,
    ResourceDelta,
)


class ConsequenceResolver:
    """Resolves queued consequences into concrete simulation deltas.

    The ConsequenceQueueEngine decides what fallout is pending.
    This resolver decides what state changes that fallout creates.
    """

    engine_name = "simulation.consequence_resolver"

    def resolve_ready_consequence(
        self,
        *,
        state: Any,
        consequence_id: str,
    ) -> Dict[str, Any]:
        consequence = state.metadata.get("consequence_queue", {}).get(consequence_id)

        if not consequence:
            return {
                "success": False,
                "engine_name": self.engine_name,
                "consequence_id": consequence_id,
                "errors": [f"consequence {consequence_id} not found"],
            }

        if consequence.get("status") not in {"ready", "triggered"}:
            return {
                "success": False,
                "engine_name": self.engine_name,
                "consequence_id": consequence_id,
                "errors": [f"consequence {consequence_id} is not ready"],
                "current_status": consequence.get("status"),
            }

        batch = self.build_delta_batch_from_consequence(
            state=state,
            consequence_id=consequence_id,
        )

        consequence["status"] = "triggered"
        consequence["metadata"]["resolver_engine"] = self.engine_name
        consequence["metadata"]["generated_delta_count"] = self._delta_count(batch)

        state.metadata.setdefault("consequence_resolution_history", []).append(
            {
                "action": "resolve_ready_consequence",
                "consequence_id": consequence_id,
                "consequence_type": consequence.get("consequence_type"),
                "generated_delta_count": self._delta_count(batch),
            }
        )

        return {
            "success": True,
            "engine_name": self.engine_name,
            "consequence_id": consequence_id,
            "delta_batch": batch,
            "updated_consequence": consequence,
            "updated_state": state,
        }

    def resolve_all_ready_consequences(
        self,
        *,
        state: Any,
        max_to_resolve: Optional[int] = None,
    ) -> Dict[str, Any]:
        ready_ids = [
            consequence_id
            for consequence_id, consequence in state.metadata.get("consequence_queue", {}).items()
            if consequence.get("status") in {"ready", "triggered"}
        ]

        if max_to_resolve is not None:
            ready_ids = ready_ids[:max_to_resolve]

        results = [
            self.resolve_ready_consequence(
                state=state,
                consequence_id=consequence_id,
            )
            for consequence_id in ready_ids
        ]

        successful = [result for result in results if result.get("success")]
        failed = [result for result in results if not result.get("success")]

        return {
            "success": True,
            "engine_name": self.engine_name,
            "ready_count": len(ready_ids),
            "resolved_count": len(successful),
            "failed_count": len(failed),
            "results": results,
            "warnings": self._bulk_warnings(results),
        }

    def build_delta_batch_from_consequence(
        self,
        *,
        state: Any,
        consequence_id: str,
    ) -> DeltaBatch:
        consequence = state.metadata.get("consequence_queue", {}).get(consequence_id, {})
        consequence_type = consequence.get("consequence_type")

        relationship_deltas = []
        reputation_deltas = []
        knowledge_deltas = []
        resource_deltas = []
        faction_deltas = []

        if consequence_type == "relationship":
            relationship_deltas.extend(self._relationship_deltas(state, consequence))
        elif consequence_type == "reputation":
            reputation_deltas.extend(self._reputation_deltas(state, consequence))
        elif consequence_type == "knowledge":
            knowledge_deltas.extend(self._knowledge_deltas(state, consequence))
        elif consequence_type == "resource":
            resource_deltas.extend(self._resource_deltas(state, consequence))
        elif consequence_type == "faction":
            faction_deltas.extend(self._faction_deltas(state, consequence))
        elif consequence_type == "obligation":
            relationship_deltas.extend(self._obligation_relationship_deltas(state, consequence))
            reputation_deltas.extend(self._obligation_reputation_deltas(state, consequence))
        elif consequence_type == "leverage":
            relationship_deltas.extend(self._leverage_relationship_deltas(state, consequence))
            reputation_deltas.extend(self._leverage_reputation_deltas(state, consequence))
        elif consequence_type == "branch":
            reputation_deltas.extend(self._branch_reputation_deltas(state, consequence))
        elif consequence_type == "emotional":
            relationship_deltas.extend(self._emotional_relationship_deltas(state, consequence))
        elif consequence_type == "plot_hook":
            # Plot hooks do not directly mutate state yet; they become Chunk 5 handoff.
            pass
        else:
            reputation_deltas.extend(self._generic_reputation_deltas(state, consequence))

        ordered = (
            relationship_deltas
            + reputation_deltas
            + knowledge_deltas
            + resource_deltas
            + faction_deltas
        )

        return DeltaBatch(
            simulation_id=state.simulation_id,
            source_engine=self.engine_name,
            source_event_id=consequence.get("source_event_id"),
            relationship_deltas=relationship_deltas,
            reputation_deltas=reputation_deltas,
            knowledge_deltas=knowledge_deltas,
            resource_deltas=resource_deltas,
            faction_deltas=faction_deltas,
            application_order=[delta.delta_id for delta in ordered],
            warnings=[
                f"source_consequence_id={consequence_id}",
                f"consequence_type={consequence_type}",
                f"source_choice_id={consequence.get('source_choice_id')}",
                f"chunk5_scene_type={self.build_chunk5_handoff_from_consequence(consequence)['scene_type']}",
            ],
        )

    def build_chunk5_handoff_from_consequence(self, consequence: Dict[str, Any]) -> Dict[str, Any]:
        consequence_type = consequence.get("consequence_type")
        severity = float(consequence.get("severity", 0.5))
        payload = consequence.get("payload", {})

        scene_type_map = {
            "relationship": "relationship_fallout_scene",
            "reputation": "public_reaction_scene",
            "knowledge": "information_spread_scene",
            "resource": "resource_cost_scene",
            "faction": "faction_response_scene",
            "obligation": "promise_debt_consequence_scene",
            "leverage": "blackmail_fallout_scene",
            "branch": "branch_point_scene",
            "emotional": "emotional_carryover_scene",
            "plot_hook": "future_plot_hook_scene",
        }

        return {
            "scene_type": scene_type_map.get(consequence_type, "consequence_scene"),
            "priority": "high" if severity >= 0.7 else "medium" if severity >= 0.4 else "low",
            "summary": consequence.get("summary"),
            "affected_entity_ids": consequence.get("affected_entity_ids", []),
            "source_choice_id": consequence.get("source_choice_id"),
            "source_event_id": consequence.get("source_event_id"),
            "plot_branch_required": consequence_type == "branch" or payload.get("requires_branch_review", False),
            "must_show_causal_link": True,
            "suggested_scene_goal": self._suggested_scene_goal(consequence),
        }

    def _relationship_deltas(self, state: Any, consequence: Dict[str, Any]) -> List[RelationshipDelta]:
        affected = consequence.get("affected_entity_ids", [])
        if len(affected) < 2:
            return []

        a, b = affected[0], affected[1]
        relationship_id = self._relationship_id(a, b)
        severity = float(consequence.get("severity", 0.5))
        action_type = consequence.get("payload", {}).get("action_type", "")

        trust_delta = -0.16 * severity
        resentment_delta = 0.14 * severity
        repair_delta = -0.06 * severity

        if action_type in {"protect", "repair_relationship", "forgive"}:
            trust_delta = 0.14 * severity
            resentment_delta = -0.08 * severity
            repair_delta = 0.12 * severity
        elif action_type in {"betray", "break_oath", "attempt_blackmail"}:
            trust_delta = -0.22 * severity
            resentment_delta = 0.22 * severity
            repair_delta = -0.10 * severity

        return [
            RelationshipDelta(
                simulation_id=state.simulation_id,
                source_engine=self.engine_name,
                source_event_id=consequence.get("source_event_id"),
                operation=DeltaOperation.INCREMENT,
                target_entity_id=relationship_id,
                target_path=f"relationship_states.{relationship_id}",
                relationship_id=relationship_id,
                character_a_id=a,
                character_b_id=b,
                trust_delta=round(trust_delta, 3),
                resentment_delta=round(resentment_delta, 3),
                repair_potential_delta=round(repair_delta, 3),
                relationship_event_label=f"consequence_{consequence.get('consequence_type')}",
                reason=consequence.get("summary", "Relationship consequence."),
            )
        ]

    def _reputation_deltas(self, state: Any, consequence: Dict[str, Any]) -> List[ReputationDelta]:
        affected = consequence.get("affected_entity_ids", [])
        severity = float(consequence.get("severity", 0.5))
        action_type = consequence.get("payload", {}).get("action_type", "")

        deltas = []
        for entity_id in affected:
            rep = -0.14 * severity
            trust = -0.10 * severity
            respect = -0.08 * severity
            fear = 0.03 * severity

            if action_type in {"protect", "fulfill_oath", "sacrifice"}:
                rep = 0.12 * severity
                trust = 0.10 * severity
                respect = 0.12 * severity
                fear = 0.0
            elif action_type in {"expose_secret", "spread_rumor"}:
                rep = -0.18 * severity
                trust = -0.12 * severity
                respect = -0.06 * severity
                fear = 0.04 * severity

            deltas.append(
                ReputationDelta(
                    simulation_id=state.simulation_id,
                    source_engine=self.engine_name,
                    source_event_id=consequence.get("source_event_id"),
                    operation=DeltaOperation.INCREMENT,
                    target_entity_id=entity_id,
                    target_path=f"character_states.{entity_id}.metadata.reputation_state.public",
                    character_id=entity_id,
                    audience_type="public",
                    reputation_score_delta=round(rep, 3),
                    trust_score_delta=round(trust, 3),
                    respect_score_delta=round(respect, 3),
                    fear_score_delta=round(fear, 3),
                    reason=consequence.get("summary", "Reputation consequence."),
                )
            )

        return deltas

    def _knowledge_deltas(self, state: Any, consequence: Dict[str, Any]) -> List[KnowledgeDelta]:
        affected = consequence.get("affected_entity_ids", [])
        payload = consequence.get("payload", {})
        severity = float(consequence.get("severity", 0.5))

        secret_ids = payload.get("secret_ids", [])
        evidence_ids = payload.get("evidence_ids", [])
        rumor_ids = payload.get("rumor_ids", [])

        if not secret_ids and payload.get("action_type") == "expose_secret":
            secret_ids = consequence.get("metadata", {}).get("linked_secret_ids", [])

        deltas = []
        for entity_id in affected:
            confidence_updates = {secret_id: min(0.8, 0.35 + severity * 0.45) for secret_id in secret_ids}

            deltas.append(
                KnowledgeDelta(
                    simulation_id=state.simulation_id,
                    source_engine=self.engine_name,
                    source_event_id=consequence.get("source_event_id"),
                    operation=DeltaOperation.APPEND,
                    target_entity_id=entity_id,
                    target_path=f"knowledge_states.{entity_id}",
                    knowledge_holder_id=entity_id,
                    suspected_secret_ids_added=secret_ids,
                    evidence_ids_seen=evidence_ids,
                    rumor_ids_heard=rumor_ids,
                    knowledge_confidence_updates=confidence_updates,
                    knowledge_path=["consequence_resolution"],
                    no_magic_knowledge_checked=True,
                    reason=consequence.get("summary", "Knowledge consequence."),
                )
            )

        return deltas

    def _resource_deltas(self, state: Any, consequence: Dict[str, Any]) -> List[ResourceDelta]:
        affected = consequence.get("affected_entity_ids", [])
        payload = consequence.get("payload", {})
        severity = float(consequence.get("severity", 0.5))
        resource_id = payload.get("resource_id", f"resource_from_{consequence.get('consequence_id')}")
        quantity_delta = float(payload.get("amount_delta", payload.get("quantity_delta", -severity * 0.25)))

        return [
            ResourceDelta(
                simulation_id=state.simulation_id,
                source_engine=self.engine_name,
                source_event_id=consequence.get("source_event_id"),
                operation=DeltaOperation.INCREMENT,
                target_entity_id=entity_id,
                target_path=f"character_states.{entity_id}.metadata.resource_state",
                resource_id=resource_id,
                resource_owner_id=entity_id,
                resource_type=payload.get("resource_type", "consequence_resource"),
                quantity_delta=round(quantity_delta, 3),
                resource_ids_affected=[resource_id],
                reason=consequence.get("summary", "Resource consequence."),
            )
            for entity_id in affected
        ]

    def _faction_deltas(self, state: Any, consequence: Dict[str, Any]) -> List[FactionDelta]:
        affected = consequence.get("affected_entity_ids", [])
        severity = float(consequence.get("severity", 0.5))

        return [
            FactionDelta(
                simulation_id=state.simulation_id,
                source_engine=self.engine_name,
                source_event_id=consequence.get("source_event_id"),
                operation=DeltaOperation.INCREMENT,
                target_entity_id=faction_id,
                target_path=f"world_state.faction_states.{faction_id}",
                faction_id=faction_id,
                influence_delta=round(-0.08 * severity, 3),
                legitimacy_delta=round(-0.10 * severity, 3),
                hostility_delta=round(0.12 * severity, 3),
                reason=consequence.get("summary", "Faction consequence."),
            )
            for faction_id in affected
        ]

    def _obligation_relationship_deltas(self, state: Any, consequence: Dict[str, Any]) -> List[RelationshipDelta]:
        affected = consequence.get("affected_entity_ids", [])
        if len(affected) < 2:
            return []

        severity = float(consequence.get("severity", 0.5))
        a, b = affected[0], affected[1]
        rid = self._relationship_id(a, b)

        return [
            RelationshipDelta(
                simulation_id=state.simulation_id,
                source_engine=self.engine_name,
                source_event_id=consequence.get("source_event_id"),
                operation=DeltaOperation.INCREMENT,
                target_entity_id=rid,
                target_path=f"relationship_states.{rid}",
                relationship_id=rid,
                character_a_id=a,
                character_b_id=b,
                debt_delta=round(0.12 * severity, 3),
                trust_delta=round(-0.08 * severity, 3),
                resentment_delta=round(0.10 * severity, 3),
                relationship_event_label="obligation_consequence",
                reason=consequence.get("summary", "Obligation consequence."),
            )
        ]

    def _obligation_reputation_deltas(self, state: Any, consequence: Dict[str, Any]) -> List[ReputationDelta]:
        return self._reputation_deltas(state, consequence)

    def _leverage_relationship_deltas(self, state: Any, consequence: Dict[str, Any]) -> List[RelationshipDelta]:
        affected = consequence.get("affected_entity_ids", [])
        if len(affected) < 2:
            return []

        severity = float(consequence.get("severity", 0.5))
        a, b = affected[0], affected[1]
        rid = self._relationship_id(a, b)

        return [
            RelationshipDelta(
                simulation_id=state.simulation_id,
                source_engine=self.engine_name,
                source_event_id=consequence.get("source_event_id"),
                operation=DeltaOperation.INCREMENT,
                target_entity_id=rid,
                target_path=f"relationship_states.{rid}",
                relationship_id=rid,
                character_a_id=a,
                character_b_id=b,
                trust_delta=round(-0.16 * severity, 3),
                fear_delta=round(0.12 * severity, 3),
                resentment_delta=round(0.16 * severity, 3),
                power_imbalance_delta=round(0.10 * severity, 3),
                relationship_event_label="leverage_consequence",
                reason=consequence.get("summary", "Leverage consequence."),
            )
        ]

    def _leverage_reputation_deltas(self, state: Any, consequence: Dict[str, Any]) -> List[ReputationDelta]:
        return self._reputation_deltas(state, consequence)

    def _branch_reputation_deltas(self, state: Any, consequence: Dict[str, Any]) -> List[ReputationDelta]:
        # Branch consequences are mainly story structure hooks, but severe public branches can dent reputation.
        if float(consequence.get("severity", 0.5)) < 0.65:
            return []
        return self._reputation_deltas(state, consequence)

    def _emotional_relationship_deltas(self, state: Any, consequence: Dict[str, Any]) -> List[RelationshipDelta]:
        affected = consequence.get("affected_entity_ids", [])
        if len(affected) < 2:
            return []

        severity = float(consequence.get("severity", 0.5))
        a, b = affected[0], affected[1]
        rid = self._relationship_id(a, b)

        return [
            RelationshipDelta(
                simulation_id=state.simulation_id,
                source_engine=self.engine_name,
                source_event_id=consequence.get("source_event_id"),
                operation=DeltaOperation.INCREMENT,
                target_entity_id=rid,
                target_path=f"relationship_states.{rid}",
                relationship_id=rid,
                character_a_id=a,
                character_b_id=b,
                emotional_intimacy_delta=round(0.08 * severity, 3),
                repair_potential_delta=round(0.06 * severity, 3),
                relationship_event_label="emotional_consequence",
                reason=consequence.get("summary", "Emotional consequence."),
            )
        ]

    def _generic_reputation_deltas(self, state: Any, consequence: Dict[str, Any]) -> List[ReputationDelta]:
        return self._reputation_deltas(state, consequence)

    def _suggested_scene_goal(self, consequence: Dict[str, Any]) -> str:
        ctype = consequence.get("consequence_type")
        if ctype == "relationship":
            return "show how the relationship changes because of the prior choice"
        if ctype == "reputation":
            return "show public reaction and social fallout"
        if ctype == "knowledge":
            return "show who learns, suspects, or misinterprets the truth"
        if ctype == "resource":
            return "show cost, scarcity, or lost access"
        if ctype == "faction":
            return "show institutional or political response"
        if ctype == "branch":
            return "make the branch consequence explicit"
        if ctype == "plot_hook":
            return "seed a future scene or unresolved thread"
        return "resolve consequence with causal clarity"

    def _delta_count(self, batch: DeltaBatch) -> int:
        return (
            len(batch.relationship_deltas)
            + len(batch.reputation_deltas)
            + len(batch.knowledge_deltas)
            + len(batch.resource_deltas)
            + len(batch.faction_deltas)
        )

    def _bulk_warnings(self, results: List[Dict[str, Any]]) -> List[str]:
        warnings = []
        if not results:
            warnings.append("no ready consequences to resolve")
        failures = [result for result in results if not result.get("success")]
        if failures:
            warnings.append(f"{len(failures)} consequences failed to resolve")
        return warnings

    def _relationship_id(self, a: str, b: str) -> str:
        return "rel_" + "_".join(sorted([a, b]))

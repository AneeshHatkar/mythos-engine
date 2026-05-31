from typing import Any, Dict, List, Optional, Tuple

from backend.app.engines.simulation.relationship_ontology_engine import RelationshipOntologyEngine
from backend.app.schemas.simulation import (
    DeltaBatch,
    DeltaOperation,
    RelationshipDelta,
    SimulationRelationshipState,
    SimulationState,
)


class RelationshipGraphEngine:
    """Builds and updates multi-dimensional relationship graph state.

    Relationships are not single labels. Each edge tracks trust, affection,
    respect, fear, envy, loyalty, debt, resentment, romantic tension, rivalry,
    dependency, power imbalance, knowledge asymmetry, betrayal risk, repair
    potential, and public/private alignment.
    """

    engine_name = "simulation.relationship_graph_engine"

    RELATIONSHIP_DIMENSIONS = [
        "trust",
        "affection",
        "respect",
        "fear",
        "envy",
        "loyalty",
        "debt",
        "resentment",
        "romantic_tension",
        "rivalry",
        "dependency",
        "power_imbalance",
        "knowledge_asymmetry",
        "public_alignment",
        "private_alignment",
        "repair_potential",
        "betrayal_risk",
    ]

    def __init__(self, ontology_engine: RelationshipOntologyEngine | None = None) -> None:
        self.ontology_engine = ontology_engine or RelationshipOntologyEngine()

    def build_relationship_graph(
        self,
        *,
        character_profiles: List[Dict[str, Any]],
        world_context: Dict[str, Any] | None = None,
        story_dna: Dict[str, Any] | None = None,
        user_intent: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        records = self.ontology_engine.classify_relationship_set(
            character_profiles=character_profiles,
            world_context=world_context or {},
            story_dna=story_dna or {},
            user_intent=user_intent or {},
        )

        relationship_states: Dict[str, Dict[str, Any]] = {}
        warnings: List[str] = list(records.get("warnings", []))

        for record in records["relationship_ontology_records"]:
            state = self._state_from_ontology(record)
            relationship_states[state.relationship_id] = state.model_dump()

        graph_metrics = self.score_graph_balance(relationship_states)

        return {
            "success": True,
            "engine_name": self.engine_name,
            "character_count": len(character_profiles),
            "relationship_count": len(relationship_states),
            "relationship_states": relationship_states,
            "ontology_records": records["relationship_ontology_records"],
            "graph_metrics": graph_metrics,
            "warnings": warnings + graph_metrics.get("warnings", []),
            "simulation_ready": bool(relationship_states),
        }

    def initialize_state_relationships(
        self,
        *,
        state: SimulationState,
        character_profiles: List[Dict[str, Any]],
        world_context: Dict[str, Any] | None = None,
        story_dna: Dict[str, Any] | None = None,
        user_intent: Dict[str, Any] | None = None,
        overwrite_existing: bool = False,
    ) -> Dict[str, Any]:
        graph = self.build_relationship_graph(
            character_profiles=character_profiles,
            world_context=world_context or state.world_state.model_dump(),
            story_dna=story_dna or {},
            user_intent=user_intent or {},
        )

        added_ids: List[str] = []
        skipped_ids: List[str] = []

        for rel_id, rel_payload in graph["relationship_states"].items():
            if rel_id in state.relationship_states and not overwrite_existing:
                skipped_ids.append(rel_id)
                continue

            state.relationship_states[rel_id] = SimulationRelationshipState.model_validate(rel_payload)
            added_ids.append(rel_id)

        state.metadata.setdefault("relationship_graph_history", []).append(
            {
                "source_engine": self.engine_name,
                "added_relationship_ids": added_ids,
                "skipped_relationship_ids": skipped_ids,
                "graph_metrics": graph["graph_metrics"],
            }
        )

        return {
            "success": True,
            "engine_name": self.engine_name,
            "simulation_id": state.simulation_id,
            "added_relationship_ids": added_ids,
            "skipped_relationship_ids": skipped_ids,
            "relationship_count": len(state.relationship_states),
            "graph_metrics": graph["graph_metrics"],
            "warnings": graph["warnings"],
            "updated_state": state,
        }

    def apply_relationship_delta_preview(
        self,
        *,
        relationship_state: SimulationRelationshipState,
        delta: RelationshipDelta,
    ) -> Dict[str, Any]:
        preview = relationship_state.model_copy(deep=True)

        for field, change in self._delta_values(delta).items():
            setattr(preview, field, self._bounded(getattr(preview, field), change))

        change_summary = {
            field: {
                "before": getattr(relationship_state, field),
                "delta": change,
                "after": getattr(preview, field),
            }
            for field, change in self._delta_values(delta).items()
            if change != 0
        }

        warnings = self._delta_warnings(change_summary, delta)

        return {
            "success": True,
            "engine_name": self.engine_name,
            "relationship_id": relationship_state.relationship_id,
            "preview_state": preview.model_dump(),
            "change_summary": change_summary,
            "warnings": warnings,
            "recommended": len([w for w in warnings if "too large" in w]) == 0,
        }

    def build_relationship_delta_from_event(
        self,
        *,
        simulation_id: str,
        relationship_id: str,
        character_a_id: str,
        character_b_id: str,
        event_type: str,
        intensity: float = 0.5,
        reason: str = "",
        source_event_id: Optional[str] = None,
    ) -> RelationshipDelta:
        intensity = max(0.0, min(1.0, float(intensity)))
        event_type = event_type.lower()

        values = {
            "trust_delta": 0.0,
            "affection_delta": 0.0,
            "respect_delta": 0.0,
            "fear_delta": 0.0,
            "envy_delta": 0.0,
            "loyalty_delta": 0.0,
            "debt_delta": 0.0,
            "resentment_delta": 0.0,
            "romantic_tension_delta": 0.0,
            "rivalry_delta": 0.0,
            "dependency_delta": 0.0,
            "power_imbalance_delta": 0.0,
            "knowledge_asymmetry_delta": 0.0,
            "repair_potential_delta": 0.0,
            "betrayal_risk_delta": 0.0,
        }

        if event_type == "public_humiliation":
            values.update(
                trust_delta=-0.10 * intensity,
                respect_delta=0.06 * intensity,
                resentment_delta=0.18 * intensity,
                rivalry_delta=0.10 * intensity,
                betrayal_risk_delta=0.08 * intensity,
            )
        elif event_type == "private_confession":
            values.update(
                trust_delta=0.18 * intensity,
                affection_delta=0.10 * intensity,
                romantic_tension_delta=0.08 * intensity,
                knowledge_asymmetry_delta=-0.12 * intensity,
                repair_potential_delta=0.12 * intensity,
            )
        elif event_type == "betrayal":
            values.update(
                trust_delta=-0.28 * intensity,
                resentment_delta=0.30 * intensity,
                fear_delta=0.10 * intensity,
                betrayal_risk_delta=0.22 * intensity,
                repair_potential_delta=-0.10 * intensity,
            )
        elif event_type == "rescue":
            values.update(
                trust_delta=0.12 * intensity,
                affection_delta=0.12 * intensity,
                debt_delta=0.20 * intensity,
                respect_delta=0.14 * intensity,
                romantic_tension_delta=0.08 * intensity,
            )
        elif event_type == "promise_broken":
            values.update(
                trust_delta=-0.22 * intensity,
                resentment_delta=0.22 * intensity,
                loyalty_delta=-0.12 * intensity,
                repair_potential_delta=-0.08 * intensity,
            )
        elif event_type == "romantic_boundary_crossing":
            values.update(
                romantic_tension_delta=0.22 * intensity,
                affection_delta=0.12 * intensity,
                trust_delta=0.08 * intensity,
                fear_delta=0.05 * intensity,
            )
        elif event_type == "social_duel":
            values.update(
                respect_delta=0.12 * intensity,
                rivalry_delta=0.20 * intensity,
                resentment_delta=0.08 * intensity,
                public_alignment_delta=0.0,
            )
        else:
            values.update(
                trust_delta=0.03 * intensity,
                respect_delta=0.04 * intensity,
            )

        allowed_keys = {
            "trust_delta",
            "affection_delta",
            "respect_delta",
            "fear_delta",
            "envy_delta",
            "loyalty_delta",
            "debt_delta",
            "resentment_delta",
            "romantic_tension_delta",
            "rivalry_delta",
            "dependency_delta",
            "power_imbalance_delta",
            "knowledge_asymmetry_delta",
            "repair_potential_delta",
            "betrayal_risk_delta",
        }
        values = {k: round(v, 3) for k, v in values.items() if k in allowed_keys}

        return RelationshipDelta(
            simulation_id=simulation_id,
            source_engine=self.engine_name,
            source_event_id=source_event_id,
            operation=DeltaOperation.INCREMENT,
            target_entity_id=relationship_id,
            target_path=f"relationship_states.{relationship_id}",
            relationship_id=relationship_id,
            character_a_id=character_a_id,
            character_b_id=character_b_id,
            relationship_event_label=event_type,
            reason=reason or f"Relationship changed due to {event_type}.",
            **values,
        )

    def score_graph_balance(self, relationship_states: Dict[str, Any]) -> Dict[str, Any]:
        if not relationship_states:
            return {
                "relationship_count": 0,
                "average_trust": 0.0,
                "average_conflict": 0.0,
                "average_romantic_tension": 0.0,
                "average_repair_potential": 0.0,
                "relationship_density_warning": False,
                "warnings": ["relationship graph is empty"],
            }

        normalized = [
            item if isinstance(item, dict) else item.model_dump()
            for item in relationship_states.values()
        ]

        count = len(normalized)
        avg_trust = self._avg(normalized, "trust")
        avg_conflict = round(self._avg(normalized, "rivalry") + self._avg(normalized, "resentment") + self._avg(normalized, "betrayal_risk"), 3)
        avg_romance = self._avg(normalized, "romantic_tension")
        avg_repair = self._avg(normalized, "repair_potential")
        avg_power_imbalance = self._avg(normalized, "power_imbalance")

        warnings = []
        if count > 200:
            warnings.append("relationship graph is dense; use focus tiers/main-cast filtering for scene simulation")
        if avg_conflict < 0.15 and avg_romance < 0.10:
            warnings.append("graph may be too flat; add stronger conflict, desire, secrets, or pressure")
        if avg_repair < 0.15 and avg_conflict > 0.5:
            warnings.append("many relationships may rupture without repair routes")

        return {
            "relationship_count": count,
            "average_trust": avg_trust,
            "average_conflict": avg_conflict,
            "average_romantic_tension": avg_romance,
            "average_repair_potential": avg_repair,
            "average_power_imbalance": avg_power_imbalance,
            "relationship_density_warning": count > 200,
            "warnings": warnings,
        }

    def _state_from_ontology(self, ontology_record: Dict[str, Any]) -> SimulationRelationshipState:
        initial = ontology_record.get("initial_state_recommendation", {})

        return SimulationRelationshipState(
            relationship_id=ontology_record["relationship_id"],
            character_a_id=ontology_record["character_a_id"],
            character_b_id=ontology_record["character_b_id"],
            relationship_type=ontology_record["relationship_label"],
            trust=float(initial.get("trust", 0.0)),
            affection=float(initial.get("affection", 0.0)),
            respect=float(initial.get("respect", 0.0)),
            fear=float(initial.get("fear", 0.0)),
            envy=float(initial.get("envy", 0.0)),
            loyalty=float(initial.get("loyalty", 0.0)),
            debt=float(initial.get("debt", 0.0)),
            resentment=float(initial.get("resentment", 0.0)),
            romantic_tension=float(initial.get("romantic_tension", 0.0)),
            rivalry=float(initial.get("rivalry", 0.0)),
            dependency=float(initial.get("dependency", 0.0)),
            power_imbalance=float(initial.get("power_imbalance", 0.0)),
            knowledge_asymmetry=float(initial.get("knowledge_asymmetry", 0.0)),
            public_alignment=float(initial.get("public_alignment", 0.0)),
            private_alignment=float(initial.get("private_alignment", 0.0)),
            repair_potential=float(initial.get("repair_potential", 0.0)),
            betrayal_risk=float(initial.get("betrayal_risk", 0.0)),
            metadata={
                "ontology_record": ontology_record,
                "relationship_family": ontology_record.get("relationship_family"),
                "relationship_subtype": ontology_record.get("relationship_subtype"),
                "rupture_triggers": ontology_record.get("rupture_triggers", []),
                "repair_conditions": ontology_record.get("repair_conditions", []),
                "event_fuel": ontology_record.get("event_fuel", []),
                "simulation_hooks": ontology_record.get("simulation_hooks", {}),
            },
        )

    def _delta_values(self, delta: RelationshipDelta) -> Dict[str, float]:
        return {
            "trust": delta.trust_delta,
            "affection": delta.affection_delta,
            "respect": delta.respect_delta,
            "fear": delta.fear_delta,
            "envy": delta.envy_delta,
            "loyalty": delta.loyalty_delta,
            "debt": delta.debt_delta,
            "resentment": delta.resentment_delta,
            "romantic_tension": delta.romantic_tension_delta,
            "rivalry": delta.rivalry_delta,
            "dependency": delta.dependency_delta,
            "power_imbalance": delta.power_imbalance_delta,
            "knowledge_asymmetry": delta.knowledge_asymmetry_delta,
            "repair_potential": delta.repair_potential_delta,
            "betrayal_risk": delta.betrayal_risk_delta,
        }

    def _delta_warnings(self, change_summary: Dict[str, Any], delta: RelationshipDelta) -> List[str]:
        warnings = []
        for field, values in change_summary.items():
            if abs(values["delta"]) > 0.35:
                warnings.append(f"{field} delta is too large for one event unless explicitly justified")

        if change_summary.get("romantic_tension", {}).get("delta", 0) > 0.18:
            reason = f"{delta.reason} {delta.relationship_event_label}".lower()
            if not any(token in reason for token in ["truth", "vulnerability", "sacrifice", "shared danger", "status", "repair"]):
                warnings.append("romantic tension increase needs pressure/vulnerability/status/shared-danger justification")

        if change_summary.get("trust", {}).get("delta", 0) < -0.25:
            reason = f"{delta.reason} {delta.relationship_event_label}".lower()
            if not any(token in reason for token in ["betrayal", "lie", "blackmail", "broken promise", "humiliation"]):
                warnings.append("trust collapse needs betrayal/lie/blackmail/broken-promise/humiliation justification")

        return warnings

    def _avg(self, records: List[Dict[str, Any]], field: str) -> float:
        return round(sum(float(item.get(field, 0.0) or 0.0) for item in records) / len(records), 3)

    def _bounded(self, current: float, delta: float, lower: float = 0.0, upper: float = 1.0) -> float:
        return round(max(lower, min(upper, float(current) + float(delta))), 3)

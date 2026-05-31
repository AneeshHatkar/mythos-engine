from typing import Any, Dict, List, Optional

from backend.app.schemas.simulation import (
    RelationshipDelta,
    SimulationRelationshipState,
    SimulationState,
)


class RelationshipArcEngine:
    """Tracks long-form relationship movement across simulation events.

    This engine turns relationship graph state and delta history into readable
    relationship arcs, rupture/repair status, and future arc recommendations.
    """

    engine_name = "simulation.relationship_arc_engine"

    ARC_FAMILIES = {
        "rivals_to_allies": [
            "competition",
            "hidden_respect",
            "forced_cooperation",
            "earned_trust",
            "alliance",
        ],
        "betrayal_rupture_repair": [
            "trust",
            "pressure",
            "betrayal",
            "rupture",
            "accountability",
            "repair_or_permanent_break",
        ],
        "status_blocked_romance": [
            "attraction_under_pressure",
            "public_constraint",
            "private_vulnerability",
            "status_risk",
            "choice_or_denial",
        ],
        "mentor_legacy_split": [
            "guidance",
            "dependence",
            "ideological_crack",
            "legacy_reveal",
            "break_or_transformation",
        ],
        "political_alliance_to_private_loyalty": [
            "utility",
            "distrust",
            "shared_threat",
            "private_risk",
            "chosen_loyalty",
        ],
        "mirror_wound_bond": [
            "recognition",
            "denial",
            "projection",
            "shared_truth",
            "healing_or_repetition",
        ],
    }

    def build_arc_record(
        self,
        *,
        relationship_state: SimulationRelationshipState,
        delta_history: List[Dict[str, Any]] | None = None,
        story_dna: Dict[str, Any] | None = None,
        user_intent: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        history = delta_history or relationship_state.metadata.get("relationship_delta_history", [])
        story = story_dna or {}
        intent = user_intent or {}

        arc_family = self._infer_arc_family(relationship_state, intent)
        stage = self._infer_current_stage(relationship_state, history, arc_family)
        movement = self._summarize_movement(history)
        rupture_status = self._rupture_status(relationship_state, history)
        repair_status = self._repair_status(relationship_state, history, rupture_status)
        next_beats = self._next_arc_beats(
            relationship_state=relationship_state,
            arc_family=arc_family,
            current_stage=stage,
            rupture_status=rupture_status,
            repair_status=repair_status,
        )

        return {
            "success": True,
            "engine_name": self.engine_name,
            "relationship_id": relationship_state.relationship_id,
            "character_a_id": relationship_state.character_a_id,
            "character_b_id": relationship_state.character_b_id,
            "relationship_type": relationship_state.relationship_type,
            "arc_family": arc_family,
            "arc_stage_sequence": self.ARC_FAMILIES.get(arc_family, []),
            "current_stage": stage,
            "arc_progress": self._arc_progress(arc_family, stage),
            "movement_summary": movement,
            "rupture_status": rupture_status,
            "repair_status": repair_status,
            "next_recommended_beats": next_beats,
            "stakes": self._relationship_stakes(relationship_state, story, intent),
            "quality_flags": self._quality_flags(relationship_state, history, rupture_status, repair_status),
            "chunk5_handoff": self._chunk5_handoff(relationship_state, arc_family, stage, next_beats),
        }

    def build_arc_map(
        self,
        *,
        state: SimulationState,
        delta_history_by_relationship: Dict[str, List[Dict[str, Any]]] | None = None,
        story_dna: Dict[str, Any] | None = None,
        user_intent: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        histories = delta_history_by_relationship or {}
        arc_records = {}

        for relationship_id, relationship_state in state.relationship_states.items():
            arc_records[relationship_id] = self.build_arc_record(
                relationship_state=relationship_state,
                delta_history=histories.get(relationship_id),
                story_dna=story_dna or {},
                user_intent=user_intent or {},
            )

        summary = self._arc_map_summary(arc_records)

        return {
            "success": True,
            "engine_name": self.engine_name,
            "simulation_id": state.simulation_id,
            "relationship_count": len(state.relationship_states),
            "arc_records": arc_records,
            "summary": summary,
            "warnings": summary.get("warnings", []),
            "simulation_ready": bool(arc_records),
        }

    def update_arc_from_delta(
        self,
        *,
        relationship_state: SimulationRelationshipState,
        delta: RelationshipDelta,
    ) -> Dict[str, Any]:
        previous_arc = self.build_arc_record(relationship_state=relationship_state)

        updated = relationship_state.model_copy(deep=True)
        for field, value in self._delta_values(delta).items():
            setattr(updated, field, self._bounded(getattr(updated, field), value))

        updated.metadata.setdefault("relationship_delta_history", []).append(
            {
                "delta_id": delta.delta_id,
                "source_event_id": delta.source_event_id,
                "relationship_event_label": delta.relationship_event_label,
                "reason": delta.reason,
                "delta_values": self._delta_values(delta),
            }
        )

        next_arc = self.build_arc_record(relationship_state=updated)

        return {
            "success": True,
            "engine_name": self.engine_name,
            "relationship_id": relationship_state.relationship_id,
            "previous_arc": previous_arc,
            "updated_arc": next_arc,
            "updated_relationship_state": updated.model_dump(),
            "stage_changed": previous_arc["current_stage"] != next_arc["current_stage"],
            "arc_family_changed": previous_arc["arc_family"] != next_arc["arc_family"],
        }

    def _infer_arc_family(self, rel: SimulationRelationshipState, intent: Dict[str, Any]) -> str:
        ontology_family = str(rel.metadata.get("relationship_family", "")).lower()
        ontology_subtype = str(rel.metadata.get("relationship_subtype", "")).lower()
        relationship_text = f"{rel.relationship_type} {ontology_family} {ontology_subtype}".lower()
        intent_text = str(intent).lower()

        explicit_betrayal_arc = (
            "loyalty_under_betrayal_pressure" in relationship_text
            or "betrayal_rupture" in relationship_text
            or "trust_tested_by_secret_leverage" in relationship_text
        )

        if explicit_betrayal_arc or rel.betrayal_risk >= 0.55 or "betrayal" in intent_text:
            return "betrayal_rupture_repair"

        if "romance" in relationship_text or rel.romantic_tension >= 0.25 or "romance" in intent_text:
            return "status_blocked_romance"

        if "mentor" in relationship_text or "legacy" in relationship_text:
            return "mentor_legacy_split"

        if "political" in relationship_text or "alliance" in relationship_text:
            return "political_alliance_to_private_loyalty"

        explicit_rivalry_arc = (
            "rivalry" in relationship_text
            or "rivals" in relationship_text
            or "hidden_respect" in relationship_text
            or "respect_hidden_inside_competition" in relationship_text
        )

        if explicit_rivalry_arc or rel.rivalry >= 0.35 or "rivals" in intent_text:
            return "rivals_to_allies"

        if "mirror" in relationship_text or (rel.repair_potential >= 0.55 and rel.rivalry <= 0.3):
            return "mirror_wound_bond"

        return "rivals_to_allies"

    def _infer_current_stage(
        self,
        rel: SimulationRelationshipState,
        history: List[Dict[str, Any]],
        arc_family: str,
    ) -> str:
        sequence = self.ARC_FAMILIES.get(arc_family, [])
        if not sequence:
            return "undefined"

        history_text = str(history).lower()

        if arc_family == "betrayal_rupture_repair":
            if rel.trust < 0.15 and rel.resentment > 0.45:
                return "rupture"
            if "accountability" in history_text or "apology" in history_text or rel.repair_potential > 0.55:
                return "accountability"
            if rel.betrayal_risk > 0.55:
                return "pressure"
            return "trust"

        if arc_family == "status_blocked_romance":
            if rel.romantic_tension >= 0.55 and rel.fear >= 0.25:
                return "status_risk"
            if rel.romantic_tension >= 0.35:
                return "private_vulnerability"
            if rel.power_imbalance >= 0.35:
                return "public_constraint"
            return "attraction_under_pressure"

        if arc_family == "rivals_to_allies":
            if rel.trust >= 0.55 and rel.rivalry <= 0.35:
                return "alliance"
            if rel.trust >= 0.35 and rel.respect >= 0.5:
                return "earned_trust"
            if "forced_teamwork" in history_text or "rescue" in history_text:
                return "forced_cooperation"
            if rel.respect >= 0.45:
                return "hidden_respect"
            return "competition"

        if arc_family == "political_alliance_to_private_loyalty":
            if rel.loyalty >= 0.45 and rel.trust >= 0.35:
                return "chosen_loyalty"
            if rel.trust >= 0.25 and rel.betrayal_risk < 0.35:
                return "private_risk"
            if rel.betrayal_risk >= 0.35:
                return "shared_threat"
            return "utility"

        if arc_family == "mentor_legacy_split":
            if rel.resentment >= 0.45:
                return "break_or_transformation"
            if rel.knowledge_asymmetry >= 0.45:
                return "legacy_reveal"
            if rel.dependency >= 0.35:
                return "dependence"
            return "guidance"

        if arc_family == "mirror_wound_bond":
            if rel.trust >= 0.45 and rel.repair_potential >= 0.55:
                return "shared_truth"
            if rel.resentment >= 0.3:
                return "projection"
            if rel.respect >= 0.35:
                return "recognition"
            return "denial"

        return sequence[0]

    def _summarize_movement(self, history: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not history:
            return {
                "event_count": 0,
                "dominant_movement": "not_started",
                "notable_events": [],
            }

        text = str(history).lower()
        if "betrayal" in text or "broken" in text:
            dominant = "rupture_pressure"
        elif "rescue" in text or "truth" in text or "confession" in text:
            dominant = "trust_opening"
        elif "humiliation" in text:
            dominant = "resentment_pressure"
        elif "promise" in text:
            dominant = "commitment_pressure"
        else:
            dominant = "slow_shift"

        notable = []
        for item in history[-5:]:
            notable.append(
                {
                    "source_event_id": item.get("source_event_id"),
                    "label": item.get("relationship_event_label") or item.get("label"),
                    "reason": item.get("reason"),
                }
            )

        return {
            "event_count": len(history),
            "dominant_movement": dominant,
            "notable_events": notable,
        }

    def _rupture_status(self, rel: SimulationRelationshipState, history: List[Dict[str, Any]]) -> Dict[str, Any]:
        history_text = str(history).lower()
        rupture_pressure = min(1.0, rel.resentment * 0.35 + rel.betrayal_risk * 0.35 + (1.0 - rel.trust) * 0.2 + rel.fear * 0.1)

        active = rupture_pressure >= 0.55 or "betrayal" in history_text or "promise_broken" in history_text

        return {
            "rupture_active": active,
            "rupture_pressure": round(rupture_pressure, 3),
            "likely_causes": self._likely_rupture_causes(rel, history_text),
            "needs_accountability": active and rel.repair_potential >= 0.25,
        }

    def _repair_status(
        self,
        rel: SimulationRelationshipState,
        history: List[Dict[str, Any]],
        rupture_status: Dict[str, Any],
    ) -> Dict[str, Any]:
        history_text = str(history).lower()
        repair_signals = 0.0
        if "apology" in history_text:
            repair_signals += 0.2
        if "truth" in history_text:
            repair_signals += 0.18
        if "rescue" in history_text or "sacrifice" in history_text:
            repair_signals += 0.22
        if "promise_fulfilled" in history_text:
            repair_signals += 0.18

        repair_possible = rel.repair_potential + repair_signals >= 0.45

        return {
            "repair_possible": repair_possible,
            "repair_pressure": round(min(1.0, rel.repair_potential + repair_signals), 3),
            "repair_requires_cost": rupture_status["rupture_active"],
            "missing_repair_conditions": self._missing_repair_conditions(rel, history_text, rupture_status),
        }

    def _next_arc_beats(
        self,
        *,
        relationship_state: SimulationRelationshipState,
        arc_family: str,
        current_stage: str,
        rupture_status: Dict[str, Any],
        repair_status: Dict[str, Any],
    ) -> List[str]:
        sequence = self.ARC_FAMILIES.get(arc_family, [])
        beats = []

        if current_stage in sequence:
            idx = sequence.index(current_stage)
            if idx + 1 < len(sequence):
                beats.append(sequence[idx + 1])

        if rupture_status["rupture_active"] and repair_status["repair_possible"]:
            beats.extend(["accountability_scene", "truth_with_cost", "earned_repair_attempt"])
        elif rupture_status["rupture_active"]:
            beats.extend(["distance_scene", "consequence_scene", "unrepaired_wound_echo"])

        if relationship_state.romantic_tension >= 0.35 and relationship_state.trust < 0.25:
            beats.append("desire_without_safety_scene")

        if relationship_state.knowledge_asymmetry >= 0.4:
            beats.append("secret_pressure_scene")

        return list(dict.fromkeys(beats))

    def _relationship_stakes(
        self,
        rel: SimulationRelationshipState,
        story_dna: Dict[str, Any],
        intent: Dict[str, Any],
    ) -> Dict[str, Any]:
        text = f"{rel.relationship_type} {story_dna} {intent}".lower()

        stakes = {
            "identity_stakes": rel.power_imbalance >= 0.35 or "identity" in text,
            "romantic_stakes": rel.romantic_tension >= 0.25 or "romance" in text,
            "betrayal_stakes": rel.betrayal_risk >= 0.35 or "betrayal" in text,
            "truth_stakes": rel.knowledge_asymmetry >= 0.35 or "truth" in text or "secret" in text,
            "status_stakes": rel.power_imbalance >= 0.35 or "status" in text or "class" in text,
        }

        stakes["overall_relationship_stakes_score"] = round(sum(1 for value in stakes.values() if value is True) / 5, 3)
        return stakes

    def _quality_flags(
        self,
        rel: SimulationRelationshipState,
        history: List[Dict[str, Any]],
        rupture_status: Dict[str, Any],
        repair_status: Dict[str, Any],
    ) -> List[str]:
        flags = []

        if rel.romantic_tension > 0.5 and rel.trust < 0.1 and not history:
            flags.append("romance_high_without_prior_trust_or_history")

        if rupture_status["rupture_active"] and not rupture_status["likely_causes"]:
            flags.append("rupture_without_clear_cause")

        if repair_status["repair_possible"] and not repair_status["repair_requires_cost"] and rupture_status["rupture_active"]:
            flags.append("repair_may_be_too_easy")

        if rel.betrayal_risk > 0.65 and rel.repair_potential < 0.2:
            flags.append("relationship_may_break_permanently")

        if rel.rivalry < 0.1 and rel.romantic_tension < 0.1 and rel.trust < 0.1 and rel.respect < 0.1:
            flags.append("relationship_edge_too_flat")

        return flags

    def _chunk5_handoff(
        self,
        rel: SimulationRelationshipState,
        arc_family: str,
        stage: str,
        next_beats: List[str],
    ) -> Dict[str, Any]:
        return {
            "relationship_id": rel.relationship_id,
            "arc_family": arc_family,
            "current_stage": stage,
            "recommended_plot_beats": next_beats,
            "scene_pressure_tags": self._scene_pressure_tags(rel, arc_family),
            "dialogue_pressure": self._dialogue_pressure(rel, arc_family),
        }

    def _scene_pressure_tags(self, rel: SimulationRelationshipState, arc_family: str) -> List[str]:
        tags = [arc_family]
        if rel.romantic_tension >= 0.25:
            tags.append("romantic_tension")
        if rel.betrayal_risk >= 0.35:
            tags.append("betrayal_pressure")
        if rel.knowledge_asymmetry >= 0.35:
            tags.append("secret_pressure")
        if rel.rivalry >= 0.35:
            tags.append("rivalry_pressure")
        if rel.repair_potential >= 0.45:
            tags.append("repair_possible")
        return tags

    def _dialogue_pressure(self, rel: SimulationRelationshipState, arc_family: str) -> Dict[str, Any]:
        return {
            "subtext_required": rel.knowledge_asymmetry >= 0.25 or rel.romantic_tension >= 0.25,
            "avoid_easy_confession": rel.romantic_tension >= 0.35 and rel.trust < 0.35,
            "power_dynamic_visible": rel.power_imbalance >= 0.35,
            "relationship_arc_family": arc_family,
        }

    def _arc_progress(self, arc_family: str, stage: str) -> float:
        seq = self.ARC_FAMILIES.get(arc_family, [])
        if not seq or stage not in seq:
            return 0.0
        return round((seq.index(stage) + 1) / len(seq), 3)

    def _likely_rupture_causes(self, rel: SimulationRelationshipState, history_text: str) -> List[str]:
        causes = []
        if rel.betrayal_risk >= 0.35 or "betrayal" in history_text:
            causes.append("betrayal_or_secret_leverage")
        if rel.resentment >= 0.35 or "humiliation" in history_text:
            causes.append("resentment_or_public_humiliation")
        if rel.knowledge_asymmetry >= 0.35:
            causes.append("knowledge_asymmetry")
        if rel.power_imbalance >= 0.45:
            causes.append("power_imbalance")
        return causes

    def _missing_repair_conditions(
        self,
        rel: SimulationRelationshipState,
        history_text: str,
        rupture_status: Dict[str, Any],
    ) -> List[str]:
        if not rupture_status["rupture_active"]:
            return []

        missing = []
        if "truth" not in history_text and rel.knowledge_asymmetry >= 0.35:
            missing.append("truth_disclosure")
        if "apology" not in history_text and rel.resentment >= 0.35:
            missing.append("accountability_or_apology")
        if "sacrifice" not in history_text and "rescue" not in history_text and rel.betrayal_risk >= 0.35:
            missing.append("costly_proof_of_changed_priority")
        return missing

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

    def _bounded(self, current: float, delta: float, lower: float = 0.0, upper: float = 1.0) -> float:
        return round(max(lower, min(upper, float(current) + float(delta))), 3)

    def _arc_map_summary(self, arc_records: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        family_counts: Dict[str, int] = {}
        warnings: List[str] = []
        rupture_count = 0
        repair_possible_count = 0

        for record in arc_records.values():
            family = record["arc_family"]
            family_counts[family] = family_counts.get(family, 0) + 1
            if record["rupture_status"]["rupture_active"]:
                rupture_count += 1
            if record["repair_status"]["repair_possible"]:
                repair_possible_count += 1
            warnings.extend(record.get("quality_flags", []))

        return {
            "arc_family_counts": family_counts,
            "rupture_count": rupture_count,
            "repair_possible_count": repair_possible_count,
            "quality_warning_count": len(warnings),
            "warnings": list(dict.fromkeys(warnings)),
        }

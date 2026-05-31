from copy import deepcopy
from typing import Any, Dict, List, Tuple

from backend.app.schemas.simulation import (
    BackstoryDelta,
    BackstoryStatus,
    CanonDelta,
    CastScalingDelta,
    DeltaBatch,
    DeltaOperation,
    DeltaScope,
    DeltaStatus,
    EmotionDelta,
    KnowledgeDelta,
    MemoryDelta,
    RelationshipDelta,
    ReputationDelta,
    SimulationCharacterState,
    SimulationKnowledgeState,
    SimulationRelationshipState,
    SimulationState,
    StateDelta,
)


class SimulationStateDeltaResolver:
    """Applies validated state deltas to SimulationState.

    Simulation engines should not mutate SimulationState directly. They should
    emit deltas, and this resolver applies them in one controlled place.
    """

    engine_name = "simulation.state_delta_resolver"

    RELATIONSHIP_JUMP_LIMIT = 0.35
    EMOTION_JUMP_LIMIT = 0.55

    def resolve_delta_batch(
        self,
        *,
        state: SimulationState,
        delta_batch: DeltaBatch,
        validate: bool = True,
    ) -> Dict[str, Any]:
        working_state = deepcopy(state)
        applied_delta_ids: List[str] = []
        rejected_delta_ids: List[str] = []
        warnings: List[str] = []
        errors: List[str] = []

        ordered_deltas = self._flatten_batch(delta_batch)
        ordered_deltas = self._order_deltas(ordered_deltas, delta_batch.application_order)

        for delta in ordered_deltas:
            validation = self.validate_delta(working_state, delta) if validate else {"valid": True, "warnings": [], "errors": []}
            warnings.extend(validation.get("warnings", []))

            if not validation["valid"]:
                rejected_delta_ids.append(delta.delta_id)
                errors.extend([f"{delta.delta_id}: {err}" for err in validation.get("errors", [])])
                continue

            apply_result = self.apply_delta(working_state, delta)
            warnings.extend(apply_result.get("warnings", []))

            if apply_result["success"]:
                applied_delta_ids.append(delta.delta_id)
            else:
                rejected_delta_ids.append(delta.delta_id)
                errors.extend([f"{delta.delta_id}: {err}" for err in apply_result.get("errors", [])])

        working_state.metadata.setdefault("delta_resolver_history", []).append(
            {
                "batch_id": delta_batch.batch_id,
                "source_engine": delta_batch.source_engine,
                "applied_delta_ids": applied_delta_ids,
                "rejected_delta_ids": rejected_delta_ids,
                "warning_count": len(warnings),
                "error_count": len(errors),
            }
        )

        return {
            "success": len(errors) == 0,
            "engine_name": self.engine_name,
            "simulation_id": state.simulation_id,
            "batch_id": delta_batch.batch_id,
            "applied_delta_ids": applied_delta_ids,
            "rejected_delta_ids": rejected_delta_ids,
            "updated_state": working_state,
            "warnings": warnings,
            "errors": errors,
        }

    def validate_delta(self, state: SimulationState, delta: StateDelta) -> Dict[str, Any]:
        warnings: List[str] = []
        errors: List[str] = []

        if delta.simulation_id != state.simulation_id:
            errors.append("delta simulation_id does not match state simulation_id")

        if delta.operation in {DeltaOperation.SET, DeltaOperation.INCREMENT, DeltaOperation.DECREMENT} and not delta.target_path:
            errors.append("delta target_path is required for value operations")

        if delta.delta_scope == DeltaScope.RELATIONSHIP and isinstance(delta, RelationshipDelta):
            if abs(delta.trust_delta) > self.RELATIONSHIP_JUMP_LIMIT:
                warnings.append("relationship trust delta exceeds recommended per-event jump limit")
            if abs(delta.romantic_tension_delta) > self.RELATIONSHIP_JUMP_LIMIT:
                warnings.append("romantic tension delta exceeds recommended per-event jump limit")
            if not delta.character_a_id or not delta.character_b_id:
                errors.append("relationship delta requires character_a_id and character_b_id")

        if delta.delta_scope == DeltaScope.KNOWLEDGE and isinstance(delta, KnowledgeDelta):
            if delta.secret_ids_added and not delta.no_magic_knowledge_checked:
                errors.append("knowledge delta adds secrets without no_magic_knowledge_checked=True")
            if delta.secret_ids_added and not (delta.knowledge_path or delta.evidence_ids_seen or delta.witness_ids):
                errors.append("knowledge delta adds secrets without evidence, witness, or knowledge path")

        if delta.delta_scope == DeltaScope.EMOTION and isinstance(delta, EmotionDelta):
            for emotion, value in delta.emotion_vector_delta.items():
                if abs(float(value)) > self.EMOTION_JUMP_LIMIT:
                    warnings.append(f"emotion delta for {emotion} is large and may need event intensity justification")

        if delta.delta_scope == DeltaScope.CANON and isinstance(delta, CanonDelta):
            if delta.retcon_required and not delta.alternate_branch_recommended:
                warnings.append("canon delta requires retcon but does not recommend alternate branch")

        if delta.delta_scope == DeltaScope.CAST_SCALING and isinstance(delta, CastScalingDelta):
            policy = delta.cast_scaling_policy_after
            if policy and (policy.no_fixed_cast_limit is not True or policy.no_fixed_destiny_limit is not True):
                errors.append("cast scaling policy must preserve no fixed cast/destiny limits")

        if delta.delta_scope == DeltaScope.BACKSTORY and isinstance(delta, BackstoryDelta):
            policy = delta.backstory_policy_after
            if policy and policy.backstory_status == BackstoryStatus.NONE and policy.importance_level.value not in ["statistical_background"]:
                warnings.append("non-statistical character has no backstory; expansion recommended")

        return {
            "valid": len(errors) == 0,
            "warnings": warnings,
            "errors": errors,
        }

    def apply_delta(self, state: SimulationState, delta: StateDelta) -> Dict[str, Any]:
        try:
            if isinstance(delta, RelationshipDelta):
                self._apply_relationship_delta(state, delta)
            elif isinstance(delta, KnowledgeDelta):
                self._apply_knowledge_delta(state, delta)
            elif isinstance(delta, EmotionDelta):
                self._apply_emotion_delta(state, delta)
            elif isinstance(delta, MemoryDelta):
                self._apply_memory_delta(state, delta)
            elif isinstance(delta, ReputationDelta):
                self._apply_reputation_delta(state, delta)
            elif isinstance(delta, CastScalingDelta):
                self._apply_cast_scaling_delta(state, delta)
            elif isinstance(delta, BackstoryDelta):
                self._apply_backstory_delta(state, delta)
            elif isinstance(delta, CanonDelta):
                self._apply_canon_delta(state, delta)
            else:
                self._apply_generic_delta(state, delta)

            state.audit_trace_ids.append(delta.delta_id)
            state.metadata.setdefault("applied_delta_ids", []).append(delta.delta_id)

            return {"success": True, "warnings": [], "errors": []}
        except Exception as exc:
            return {"success": False, "warnings": [], "errors": [str(exc)]}

    def _apply_relationship_delta(self, state: SimulationState, delta: RelationshipDelta) -> None:
        relationship_id = delta.relationship_id or self._find_or_create_relationship(
            state,
            delta.character_a_id,
            delta.character_b_id,
        )
        rel = state.relationship_states[relationship_id]

        for field, change in {
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
        }.items():
            setattr(rel, field, self._bounded(getattr(rel, field), change))

        rel.metadata.setdefault("relationship_delta_history", []).append(
            {
                "delta_id": delta.delta_id,
                "source_event_id": delta.source_event_id,
                "label": delta.relationship_event_label,
                "reason": delta.reason,
            }
        )

    def _apply_knowledge_delta(self, state: SimulationState, delta: KnowledgeDelta) -> None:
        holder_id = delta.knowledge_holder_id
        knowledge = state.knowledge_states.get(holder_id)
        if knowledge is None:
            knowledge = SimulationKnowledgeState(entity_id=holder_id)
            state.knowledge_states[holder_id] = knowledge

        knowledge.known_secret_ids = self._unique(knowledge.known_secret_ids + delta.secret_ids_added)
        knowledge.known_secret_ids = [item for item in knowledge.known_secret_ids if item not in delta.secret_ids_removed]
        knowledge.suspected_secret_ids = self._unique(knowledge.suspected_secret_ids + delta.suspected_secret_ids_added)
        knowledge.evidence_seen_ids = self._unique(knowledge.evidence_seen_ids + delta.evidence_ids_seen)
        knowledge.rumors_heard_ids = self._unique(knowledge.rumors_heard_ids + delta.rumor_ids_heard)
        knowledge.believed_falsehood_ids = self._unique(knowledge.believed_falsehood_ids + delta.falsehood_ids_believed)
        knowledge.knowledge_confidence.update(delta.knowledge_confidence_updates)
        knowledge.metadata.setdefault("knowledge_delta_history", []).append(
            {
                "delta_id": delta.delta_id,
                "knowledge_path": delta.knowledge_path,
                "witness_ids": delta.witness_ids,
                "no_magic_knowledge_checked": delta.no_magic_knowledge_checked,
            }
        )

    def _apply_emotion_delta(self, state: SimulationState, delta: EmotionDelta) -> None:
        character = self._get_character_state(state, delta.character_id)
        emotion_state = dict(character.current_emotion_state or {})
        vector = dict(emotion_state.get("emotion_vector", {}))

        for emotion, change in delta.emotion_vector_delta.items():
            vector[emotion] = self._bounded(float(vector.get(emotion, 0.0)), float(change))

        emotion_state["emotion_vector"] = vector
        if delta.dominant_emotion_after:
            emotion_state["dominant_emotion"] = delta.dominant_emotion_after
        elif vector:
            emotion_state["dominant_emotion"] = max(vector, key=vector.get)

        if delta.suppressed_emotion_after:
            emotion_state["suppressed_emotion"] = delta.suppressed_emotion_after
        if delta.triggered_wound:
            emotion_state["triggered_wound"] = delta.triggered_wound
        if delta.emotional_mask_after:
            emotion_state["emotional_mask"] = delta.emotional_mask_after

        emotion_state.setdefault("decay_rates", {}).update(delta.decay_rate_updates)
        emotion_state.setdefault("relationship_specific_emotional_leak", {}).update(delta.relationship_specific_leaks)
        emotion_state.setdefault("emotion_delta_history", []).append(delta.delta_id)

        character.current_emotion_state = emotion_state

    def _apply_memory_delta(self, state: SimulationState, delta: MemoryDelta) -> None:
        character = self._get_character_state(state, delta.character_id)
        memory_state = dict(character.current_memory_state or {})

        memory_state["active_memory_ids"] = self._unique(
            list(memory_state.get("active_memory_ids", []))
            + delta.memory_ids_added
            + delta.memory_ids_activated
        )
        memory_state["suppressed_memory_ids"] = self._unique(
            list(memory_state.get("suppressed_memory_ids", [])) + delta.memory_ids_suppressed
        )
        memory_state["memory_records"] = list(memory_state.get("memory_records", [])) + delta.memory_records_added
        memory_state["trigger_tags"] = self._unique(list(memory_state.get("trigger_tags", [])) + delta.trigger_tags_added)
        memory_state["dialogue_constraints"] = self._unique(
            list(memory_state.get("dialogue_constraints", [])) + delta.dialogue_constraints_added
        )
        memory_state.setdefault("future_agency_modifiers", {}).update(delta.future_agency_modifiers)
        memory_state.setdefault("memory_delta_history", []).append(delta.delta_id)

        character.current_memory_state = memory_state

    def _apply_reputation_delta(self, state: SimulationState, delta: ReputationDelta) -> None:
        character = self._get_character_state(state, delta.character_id)
        reputation_state = dict(character.metadata.get("reputation_state", {}))
        audience_key = delta.audience_id or delta.audience_type

        audience = dict(reputation_state.get(audience_key, {}))
        for field, change in {
            "reputation_score": delta.reputation_score_delta,
            "fear_score": delta.fear_score_delta,
            "respect_score": delta.respect_score_delta,
            "trust_score": delta.trust_score_delta,
        }.items():
            audience[field] = self._bounded(float(audience.get(field, 0.5)), float(change))

        audience["rumor_ids"] = self._unique(list(audience.get("rumor_ids", [])) + delta.rumor_ids_created + delta.rumor_ids_amplified)
        audience.setdefault("reputation_delta_history", []).append(delta.delta_id)

        reputation_state[audience_key] = audience
        character.metadata["reputation_state"] = reputation_state

    def _apply_cast_scaling_delta(self, state: SimulationState, delta: CastScalingDelta) -> None:
        if delta.cast_scaling_policy_after is not None:
            state.metadata["cast_scaling_policy"] = delta.cast_scaling_policy_after.model_dump()

        state.metadata.setdefault("cast_scaling_delta_history", []).append(
            {
                "delta_id": delta.delta_id,
                "character_ids_added": delta.character_ids_added,
                "character_ids_removed": delta.character_ids_removed,
                "scale_warning_flags": delta.scale_warning_flags,
            }
        )

    def _apply_backstory_delta(self, state: SimulationState, delta: BackstoryDelta) -> None:
        character = self._get_character_state(state, delta.character_id)
        if delta.backstory_policy_after is not None:
            character.metadata["backstory_policy"] = delta.backstory_policy_after.model_dump()

        backstory_state = dict(character.metadata.get("backstory_state", {}))
        backstory_state.update(delta.backstory_fields_added)
        backstory_state["formative_memory_ids"] = self._unique(
            list(backstory_state.get("formative_memory_ids", [])) + delta.formative_memory_ids_added
        )
        backstory_state.setdefault("backstory_delta_history", []).append(delta.delta_id)
        character.metadata["backstory_state"] = backstory_state

    def _apply_canon_delta(self, state: SimulationState, delta: CanonDelta) -> None:
        state.metadata.setdefault("canon_delta_history", []).append(
            {
                "delta_id": delta.delta_id,
                "target_entity_id": delta.target_entity_id,
                "canon_status_before": delta.canon_status_before,
                "canon_status_after": delta.canon_status_after,
                "lock_ids_affected": delta.lock_ids_affected,
                "retcon_required": delta.retcon_required,
                "alternate_branch_recommended": delta.alternate_branch_recommended,
                "summary": delta.canon_change_summary,
            }
        )

    def _apply_generic_delta(self, state: SimulationState, delta: StateDelta) -> None:
        state.metadata.setdefault("generic_delta_history", []).append(
            {
                "delta_id": delta.delta_id,
                "scope": delta.delta_scope,
                "operation": delta.operation,
                "target_entity_id": delta.target_entity_id,
                "target_path": delta.target_path,
                "after_value": delta.after_value,
                "delta_value": delta.delta_value,
            }
        )

    def _find_or_create_relationship(self, state: SimulationState, a: str, b: str) -> str:
        pair = {a, b}
        for rel_id, rel in state.relationship_states.items():
            if {rel.character_a_id, rel.character_b_id} == pair:
                return rel_id

        rel = SimulationRelationshipState(
            character_a_id=a,
            character_b_id=b,
            relationship_type="emergent_relationship",
        )
        state.relationship_states[rel.relationship_id] = rel
        return rel.relationship_id

    def _get_character_state(self, state: SimulationState, character_id: str) -> SimulationCharacterState:
        if character_id not in state.character_states:
            state.character_states[character_id] = SimulationCharacterState(character_id=character_id)
        return state.character_states[character_id]

    def _flatten_batch(self, batch: DeltaBatch) -> List[StateDelta]:
        deltas: List[StateDelta] = []
        deltas.extend(batch.deltas)
        deltas.extend(batch.relationship_deltas)
        deltas.extend(batch.knowledge_deltas)
        deltas.extend(batch.emotion_deltas)
        deltas.extend(batch.memory_deltas)
        deltas.extend(batch.reputation_deltas)
        deltas.extend(batch.faction_deltas)
        deltas.extend(batch.resource_deltas)
        deltas.extend(batch.legal_deltas)
        deltas.extend(batch.tension_deltas)
        deltas.extend(batch.stakes_deltas)
        deltas.extend(batch.canon_deltas)
        deltas.extend(batch.timeline_deltas)
        deltas.extend(batch.consequence_deltas)
        deltas.extend(batch.cast_scaling_deltas)
        deltas.extend(batch.backstory_deltas)
        return deltas

    def _order_deltas(self, deltas: List[StateDelta], application_order: List[str]) -> List[StateDelta]:
        if not application_order:
            return deltas

        by_id = {delta.delta_id: delta for delta in deltas}
        ordered = [by_id[delta_id] for delta_id in application_order if delta_id in by_id]
        remaining = [delta for delta in deltas if delta.delta_id not in set(application_order)]
        return ordered + remaining

    def _bounded(self, current: float, delta: float, lower: float = 0.0, upper: float = 1.0) -> float:
        return round(max(lower, min(upper, current + delta)), 3)

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

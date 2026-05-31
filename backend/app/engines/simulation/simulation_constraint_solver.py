from typing import Any, Dict, List, Optional

from backend.app.schemas.simulation import (
    DeltaBatch,
    DeltaScope,
    KnowledgeDelta,
    RelationshipDelta,
    SimulationEventPayload,
    SimulationEventType,
    SimulationEventVisibility,
    SimulationState,
    StateDelta,
)


class SimulationConstraintSolver:
    """Checks whether simulation events and deltas are possible.

    This is a pre-resolution guardrail. It does not mutate state. It answers:
    can this event happen, can this character know this, can this relationship
    move this much, and can this action obey world/canon/story constraints?
    """

    engine_name = "simulation.constraint_solver"

    MAX_RELATIONSHIP_JUMP = 0.35
    MAX_ROMANCE_JUMP_WITHOUT_PRESSURE = 0.18
    MAX_TRUST_COLLAPSE_WITHOUT_TRIGGER = -0.25

    PUBLIC_EVENT_VISIBILITIES = {
        SimulationEventVisibility.PUBLIC,
        SimulationEventVisibility.WITNESSED,
        SimulationEventVisibility.FACTION_KNOWN,
    }

    def evaluate_event_feasibility(
        self,
        *,
        state: SimulationState,
        event_payload: SimulationEventPayload,
    ) -> Dict[str, Any]:
        blockers: List[str] = []
        warnings: List[str] = []
        passed_checks: List[str] = []

        location_report = self._check_location_feasibility(state, event_payload)
        knowledge_report = self._check_event_knowledge_paths(state, event_payload)
        actor_report = self._check_actor_availability(state, event_payload)
        world_report = self._check_world_contract_event_rules(state, event_payload)
        stakes_report = self._check_event_intensity_and_stakes(event_payload)

        reports = [location_report, knowledge_report, actor_report, world_report, stakes_report]

        for report in reports:
            blockers.extend(report.get("blockers", []))
            warnings.extend(report.get("warnings", []))
            passed_checks.extend(report.get("passed_checks", []))

        feasible = len(blockers) == 0
        feasibility_score = self._score_from_reports(reports)

        return {
            "success": True,
            "engine_name": self.engine_name,
            "event_id": event_payload.event_id,
            "event_type": event_payload.event_type,
            "feasible": feasible,
            "feasibility_score": feasibility_score,
            "passed_checks": passed_checks,
            "blockers": blockers,
            "warnings": warnings,
            "reports": {
                "location": location_report,
                "knowledge": knowledge_report,
                "actors": actor_report,
                "world_contract": world_report,
                "stakes": stakes_report,
            },
            "recommendation": "allow_event" if feasible else "revise_or_branch_event",
        }

    def evaluate_delta_batch_feasibility(
        self,
        *,
        state: SimulationState,
        delta_batch: DeltaBatch,
    ) -> Dict[str, Any]:
        blockers: List[str] = []
        warnings: List[str] = []
        passed_checks: List[str] = []

        delta_reports = []
        for delta in self._flatten_batch(delta_batch):
            report = self.evaluate_delta_feasibility(state=state, delta=delta)
            delta_reports.append(report)
            blockers.extend([f"{delta.delta_id}: {item}" for item in report.get("blockers", [])])
            warnings.extend([f"{delta.delta_id}: {item}" for item in report.get("warnings", [])])
            passed_checks.extend(report.get("passed_checks", []))

        feasible = len(blockers) == 0
        score = (
            round(sum(item["feasibility_score"] for item in delta_reports) / len(delta_reports), 3)
            if delta_reports
            else 1.0
        )

        return {
            "success": True,
            "engine_name": self.engine_name,
            "batch_id": delta_batch.batch_id,
            "feasible": feasible,
            "feasibility_score": score,
            "delta_reports": delta_reports,
            "passed_checks": passed_checks,
            "blockers": blockers,
            "warnings": warnings,
            "recommendation": "allow_delta_batch" if feasible else "revise_or_split_delta_batch",
        }

    def evaluate_delta_feasibility(
        self,
        *,
        state: SimulationState,
        delta: StateDelta,
    ) -> Dict[str, Any]:
        blockers: List[str] = []
        warnings: List[str] = []
        passed_checks: List[str] = []

        if delta.simulation_id != state.simulation_id:
            blockers.append("delta belongs to a different simulation")
        else:
            passed_checks.append("simulation_id_matches")

        if delta.delta_scope == DeltaScope.KNOWLEDGE and isinstance(delta, KnowledgeDelta):
            report = self._check_knowledge_delta(state, delta)
            blockers.extend(report["blockers"])
            warnings.extend(report["warnings"])
            passed_checks.extend(report["passed_checks"])

        if delta.delta_scope == DeltaScope.RELATIONSHIP and isinstance(delta, RelationshipDelta):
            report = self._check_relationship_delta(state, delta)
            blockers.extend(report["blockers"])
            warnings.extend(report["warnings"])
            passed_checks.extend(report["passed_checks"])

        if delta.canon_sensitive:
            report = self._check_canon_sensitive_delta(state, delta)
            blockers.extend(report["blockers"])
            warnings.extend(report["warnings"])
            passed_checks.extend(report["passed_checks"])

        if delta.requires_human_review:
            warnings.append("delta requires human review before promotion to canon/training")
            passed_checks.append("human_review_warning_emitted")

        feasible = len(blockers) == 0
        score = round(max(0.0, 1.0 - 0.25 * len(blockers) - 0.08 * len(warnings)), 3)

        return {
            "success": True,
            "delta_id": delta.delta_id,
            "delta_scope": delta.delta_scope,
            "feasible": feasible,
            "feasibility_score": score,
            "passed_checks": passed_checks,
            "blockers": blockers,
            "warnings": warnings,
        }

    def _check_location_feasibility(
        self,
        state: SimulationState,
        event: SimulationEventPayload,
    ) -> Dict[str, Any]:
        blockers: List[str] = []
        warnings: List[str] = []
        passed: List[str] = []

        if not event.location_id:
            warnings.append("event has no location_id; location/presence validation is incomplete")
            return {"blockers": blockers, "warnings": warnings, "passed_checks": passed}

        active_location_ids = {
            item.get("location_id")
            for item in state.world_state.active_locations
            if isinstance(item, dict)
        }

        if active_location_ids and event.location_id not in active_location_ids:
            blockers.append(f"event location {event.location_id} is not in active world locations")
        else:
            passed.append("event_location_exists_or_world_does_not_restrict_locations")

        access_rules = state.world_state.location_access_rules or []
        for actor_id in event.actor_ids + event.target_ids:
            character = state.character_states.get(actor_id)
            if not character:
                continue

            if character.current_location_id and character.current_location_id != event.location_id:
                if not self._travel_or_remote_possible(state, character.current_location_id, event.location_id):
                    blockers.append(
                        f"{actor_id} is at {character.current_location_id} and cannot be present at {event.location_id}"
                    )

            rule = self._find_access_rule(access_rules, event.location_id)
            if rule and rule.get("requires_sponsor"):
                backstory = character.metadata.get("backstory_policy", {}) if character else {}
                has_sponsor = (
                    character.metadata.get("has_sponsor")
                    or character.metadata.get("access_route")
                    or "sponsor" in str(backstory).lower()
                    or "sponsor" in str(character.character_to_simulation_contract).lower()
                )
                if not has_sponsor and actor_id in event.actor_ids:
                    warnings.append(f"{actor_id} may need sponsor/access route for {event.location_id}")
                else:
                    passed.append(f"{actor_id}_access_route_checked")

        return {"blockers": blockers, "warnings": warnings, "passed_checks": passed}

    def _check_event_knowledge_paths(
        self,
        state: SimulationState,
        event: SimulationEventPayload,
    ) -> Dict[str, Any]:
        blockers: List[str] = []
        warnings: List[str] = []
        passed: List[str] = []

        secret_ids = list(event.metadata.get("secret_ids_revealed", []))
        evidence_ids = list(event.metadata.get("evidence_ids_used", []))
        required_knowers = list(event.metadata.get("required_knower_ids", []))

        if event.event_type in {SimulationEventType.SECRET_DISCOVERY, SimulationEventType.TRIAL} and secret_ids:
            if not evidence_ids and not event.witness_ids:
                blockers.append("secret-moving event lacks evidence_ids_used or witness_ids")
            else:
                passed.append("secret_movement_has_evidence_or_witness_path")

        for character_id in required_knowers:
            knowledge = state.knowledge_states.get(character_id)
            if not knowledge:
                blockers.append(f"{character_id} is required to know information but has no knowledge state")
                continue

            missing = [secret_id for secret_id in secret_ids if secret_id not in knowledge.known_secret_ids]
            if missing:
                warnings.append(f"{character_id} lacks known_secret_ids for {missing}; event may require discovery setup")
            else:
                passed.append(f"{character_id}_knowledge_requirement_satisfied")

        if event.visibility in self.PUBLIC_EVENT_VISIBILITIES and not event.witness_ids:
            warnings.append("public/witnessed event has no witness_ids; reputation/rumor consequences may be weak")
        else:
            passed.append("visibility_has_witness_support_or_private")

        return {"blockers": blockers, "warnings": warnings, "passed_checks": passed}

    def _check_actor_availability(
        self,
        state: SimulationState,
        event: SimulationEventPayload,
    ) -> Dict[str, Any]:
        blockers: List[str] = []
        warnings: List[str] = []
        passed: List[str] = []

        all_participants = event.actor_ids + event.target_ids
        for character_id in all_participants:
            character = state.character_states.get(character_id)
            if not character:
                blockers.append(f"participant {character_id} does not exist in simulation character_states")
                continue

            if character.metadata.get("dead") is True:
                blockers.append(f"participant {character_id} is marked dead and cannot act")
            else:
                passed.append(f"{character_id}_available")

            agency = character.current_agency_state or {}
            if event.event_type == SimulationEventType.BETRAYAL:
                if "betray_without_extreme_pressure" in agency.get("unthinkable_actions", []):
                    pressure = float(event.metadata.get("fear_pressure", 0.0)) + float(event.metadata.get("blackmail_pressure", 0.0))
                    if pressure < 0.7:
                        blockers.append(f"{character_id} cannot betray without sufficient pressure")
                else:
                    passed.append(f"{character_id}_betrayal_agency_checked")

        return {"blockers": blockers, "warnings": warnings, "passed_checks": passed}

    def _check_world_contract_event_rules(
        self,
        state: SimulationState,
        event: SimulationEventPayload,
    ) -> Dict[str, Any]:
        blockers: List[str] = []
        warnings: List[str] = []
        passed: List[str] = []

        constraints = state.world_state.world_simulation_constraints or {}
        text = str(constraints).lower()

        if event.event_type in {SimulationEventType.PHYSICAL_DUEL, SimulationEventType.SOCIAL_DUEL}:
            if "forbidden" in text and "duel" in text:
                warnings.append("duel event may violate world rules unless exception/illegal status is intentional")
            else:
                passed.append("duel_not_forbidden_by_world_contract")

        if event.event_type == SimulationEventType.TRIAL:
            if "sponsor" in text:
                if not event.metadata.get("sponsor_id") and not event.metadata.get("sponsor_exception"):
                    warnings.append("trial event may require sponsor_id or sponsor_exception under world contract")
                else:
                    passed.append("trial_sponsor_requirement_addressed")

        if event.event_type in {SimulationEventType.ROMANTIC_BOUNDARY_CROSSING}:
            if "public status" in text or "class" in text:
                if not event.metadata.get("romance_status_pressure_acknowledged"):
                    warnings.append("romantic boundary event should acknowledge public/class/status pressure")
                else:
                    passed.append("romance_status_pressure_acknowledged")

        if event.event_type in {SimulationEventType.RESCUE, SimulationEventType.SACRIFICE}:
            if "power_cost" in text or "requires cost" in text:
                if not event.metadata.get("cost_paid") and event.metadata.get("uses_power"):
                    blockers.append("power-based rescue/sacrifice violates power cost rule")
                else:
                    passed.append("power_cost_rule_checked")

        return {"blockers": blockers, "warnings": warnings, "passed_checks": passed}

    def _check_event_intensity_and_stakes(
        self,
        event: SimulationEventPayload,
    ) -> Dict[str, Any]:
        blockers: List[str] = []
        warnings: List[str] = []
        passed: List[str] = []

        if event.intensity < 0 or event.intensity > 1:
            blockers.append("event intensity must be between 0 and 1")
        else:
            passed.append("event_intensity_bounded")

        high_impact_events = {
            SimulationEventType.BETRAYAL,
            SimulationEventType.SACRIFICE,
            SimulationEventType.PROMISE_BROKEN,
            SimulationEventType.BLACKMAIL_ATTEMPT,
            SimulationEventType.TRIAL,
            SimulationEventType.ROMANTIC_BOUNDARY_CROSSING,
        }

        if event.event_type in high_impact_events and not event.stakes_tags:
            warnings.append("high-impact event has no stakes_tags")
        else:
            passed.append("stakes_tags_present_or_not_required")

        if event.event_type in high_impact_events and not event.theme_tags:
            warnings.append("high-impact event has no theme_tags; deep story echo may be weak")
        else:
            passed.append("theme_tags_present_or_not_required")

        return {"blockers": blockers, "warnings": warnings, "passed_checks": passed}

    def _check_knowledge_delta(
        self,
        state: SimulationState,
        delta: KnowledgeDelta,
    ) -> Dict[str, Any]:
        blockers: List[str] = []
        warnings: List[str] = []
        passed: List[str] = []

        if delta.knowledge_holder_id not in state.character_states and delta.knowledge_holder_id not in state.entity_states:
            blockers.append(f"knowledge holder {delta.knowledge_holder_id} is not in simulation state")
        else:
            passed.append("knowledge_holder_exists")

        if delta.secret_ids_added and not delta.no_magic_knowledge_checked:
            blockers.append("secret knowledge added without no_magic_knowledge_checked=True")
        else:
            passed.append("no_magic_knowledge_flag_checked")

        if delta.secret_ids_added and not (delta.evidence_ids_seen or delta.knowledge_path or delta.witness_ids):
            blockers.append("secret knowledge added without evidence, witness, or explicit knowledge path")
        else:
            passed.append("knowledge_path_exists")

        return {"blockers": blockers, "warnings": warnings, "passed_checks": passed}

    def _check_relationship_delta(
        self,
        state: SimulationState,
        delta: RelationshipDelta,
    ) -> Dict[str, Any]:
        blockers: List[str] = []
        warnings: List[str] = []
        passed: List[str] = []

        if delta.character_a_id not in state.character_states:
            blockers.append(f"character_a_id {delta.character_a_id} missing from state")
        if delta.character_b_id not in state.character_states:
            blockers.append(f"character_b_id {delta.character_b_id} missing from state")
        if not blockers:
            passed.append("relationship_characters_exist")

        large_changes = {
            "trust": delta.trust_delta,
            "affection": delta.affection_delta,
            "respect": delta.respect_delta,
            "romantic_tension": delta.romantic_tension_delta,
            "betrayal_risk": delta.betrayal_risk_delta,
        }

        for name, value in large_changes.items():
            if abs(float(value)) > self.MAX_RELATIONSHIP_JUMP:
                warnings.append(f"{name} changes more than recommended per-event jump")

        if delta.romantic_tension_delta > self.MAX_ROMANCE_JUMP_WITHOUT_PRESSURE:
            pressure_terms = str(delta.reason + " " + delta.relationship_event_label).lower()
            if not any(token in pressure_terms for token in ["shared danger", "truth", "sacrifice", "repair", "vulnerability", "status"]):
                warnings.append("romantic tension jump lacks pressure/repair/vulnerability explanation")

        if delta.trust_delta < self.MAX_TRUST_COLLAPSE_WITHOUT_TRIGGER:
            trigger_terms = str(delta.reason + " " + delta.relationship_event_label).lower()
            if not any(token in trigger_terms for token in ["betrayal", "lie", "blackmail", "humiliation", "broken promise"]):
                warnings.append("large trust collapse lacks betrayal/lie/blackmail/humiliation trigger")

        return {"blockers": blockers, "warnings": warnings, "passed_checks": passed}

    def _check_canon_sensitive_delta(
        self,
        state: SimulationState,
        delta: StateDelta,
    ) -> Dict[str, Any]:
        blockers: List[str] = []
        warnings: List[str] = []
        passed: List[str] = []

        locked_fields = []
        entity_state = state.entity_states.get(delta.target_entity_id)
        if entity_state:
            locked_fields = entity_state.locked_fields

        if delta.target_path in locked_fields:
            blockers.append(f"delta attempts to change locked field {delta.target_path}")
        else:
            passed.append("canon_sensitive_delta_does_not_touch_locked_field")

        return {"blockers": blockers, "warnings": warnings, "passed_checks": passed}

    def _travel_or_remote_possible(self, state: SimulationState, from_location_id: str, to_location_id: str) -> bool:
        if from_location_id == to_location_id:
            return True

        travel_edges = state.world_state.metadata.get("travel_edges", [])
        for edge in travel_edges:
            if edge.get("from_location_id") == from_location_id and edge.get("to_location_id") == to_location_id:
                return True
            if edge.get("to_location_id") == from_location_id and edge.get("from_location_id") == to_location_id:
                return True

        return False

    def _find_access_rule(self, access_rules: List[Dict[str, Any]], location_id: str) -> Optional[Dict[str, Any]]:
        for rule in access_rules:
            if rule.get("location_id") == location_id:
                return rule
        return None

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

    def _score_from_reports(self, reports: List[Dict[str, Any]]) -> float:
        blockers = sum(len(report.get("blockers", [])) for report in reports)
        warnings = sum(len(report.get("warnings", [])) for report in reports)
        return round(max(0.0, 1.0 - 0.2 * blockers - 0.04 * warnings), 3)

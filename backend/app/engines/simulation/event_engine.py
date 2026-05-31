from typing import Any, Dict, List, Optional


class EventEngine:
    """Validates, classifies, and routes simulation events.

    This engine is the central event gateway for Chunk 4. It does not replace
    specialized engines. Instead, it validates event payloads, determines which
    engines should respond, records event history, builds event cards, and
    produces handoff instructions for consequences, causal graphs, choices,
    relationships, knowledge, evidence, rumors, bargains, obligations, and plot.
    """

    engine_name = "simulation.event_engine"

    EVENT_FAMILIES = {
        "knowledge": {
            "secret_discovery",
            "evidence_reveal",
            "evidence_destroyed",
            "rumor_heard",
            "rumor_spread",
            "truth_confession",
            "lie_told",
            "falsehood_exposed",
        },
        "relationship": {
            "private_confession",
            "betrayal",
            "forgiveness",
            "repair_attempt",
            "public_humiliation",
            "rescue",
            "romantic_turn",
            "rivalry_escalation",
        },
        "obligation": {
            "promise_made",
            "oath_sworn",
            "debt_created",
            "promise_fulfilled",
            "promise_broken",
            "debt_repaid",
        },
        "leverage": {
            "blackmail_attempt",
            "blackmail_refused",
            "blackmail_accepted",
            "counter_leverage",
            "threat_made",
            "threat_exposed",
        },
        "bargain": {
            "negotiation_offer",
            "counteroffer_made",
            "bargain_accepted",
            "bargain_rejected",
            "bargain_betrayed",
            "truce_made",
        },
        "choice": {
            "choice_presented",
            "choice_selected",
            "choice_blocked",
            "choice_forced",
            "moral_dilemma",
        },
        "consequence": {
            "consequence_queued",
            "consequence_triggered",
            "consequence_resolved",
            "fallout_scene",
        },
        "world": {
            "trial",
            "faction_action",
            "location_change",
            "resource_loss",
            "resource_gain",
            "public_event",
            "combat",
        },
    }

    VISIBILITY_VALUES = {
        "private",
        "witnessed",
        "public",
        "faction_known",
        "rumored",
        "secret",
    }

    EVENT_SEVERITY_LABELS = {
        "minor": (0.0, 0.25),
        "moderate": (0.25, 0.55),
        "major": (0.55, 0.8),
        "critical": (0.8, 1.01),
    }

    def create_event_record(
        self,
        *,
        event_id: str,
        event_type: str,
        event_name: str,
        actor_ids: List[str] | None = None,
        target_ids: List[str] | None = None,
        witness_ids: List[str] | None = None,
        involved_faction_ids: List[str] | None = None,
        location_id: Optional[str] = None,
        visibility: str = "private",
        intensity: float = 0.5,
        branch_id: Optional[str] = None,
        timeline_id: Optional[str] = None,
        source_choice_id: Optional[str] = None,
        linked_secret_ids: List[str] | None = None,
        linked_evidence_ids: List[str] | None = None,
        linked_rumor_ids: List[str] | None = None,
        linked_obligation_ids: List[str] | None = None,
        linked_leverage_ids: List[str] | None = None,
        linked_bargain_ids: List[str] | None = None,
        metadata: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        visibility = visibility if visibility in self.VISIBILITY_VALUES else "private"
        family = self.classify_event_type(event_type)["event_family"]

        return {
            "event_id": event_id,
            "event_type": event_type,
            "event_family": family,
            "event_name": event_name,
            "actor_ids": actor_ids or [],
            "target_ids": target_ids or [],
            "witness_ids": witness_ids or [],
            "involved_faction_ids": involved_faction_ids or [],
            "location_id": location_id,
            "visibility": visibility,
            "intensity": self._bounded(intensity),
            "severity_label": self._severity_label(intensity),
            "branch_id": branch_id,
            "timeline_id": timeline_id,
            "source_choice_id": source_choice_id,
            "linked_secret_ids": linked_secret_ids or [],
            "linked_evidence_ids": linked_evidence_ids or [],
            "linked_rumor_ids": linked_rumor_ids or [],
            "linked_obligation_ids": linked_obligation_ids or [],
            "linked_leverage_ids": linked_leverage_ids or [],
            "linked_bargain_ids": linked_bargain_ids or [],
            "metadata": metadata or {},
        }

    def classify_event_type(self, event_type: str) -> Dict[str, Any]:
        normalized = str(event_type).lower().strip()

        for family, event_types in self.EVENT_FAMILIES.items():
            if normalized in event_types:
                return {
                    "success": True,
                    "engine_name": self.engine_name,
                    "event_type": normalized,
                    "event_family": family,
                    "known_event_type": True,
                }

        guessed_family = self._guess_family(normalized)

        return {
            "success": True,
            "engine_name": self.engine_name,
            "event_type": normalized,
            "event_family": guessed_family,
            "known_event_type": False,
        }

    def validate_event_record(
        self,
        *,
        state: Any,
        event_record: Dict[str, Any],
    ) -> Dict[str, Any]:
        blockers: List[str] = []
        warnings: List[str] = []
        passed: List[str] = []

        event_id = event_record.get("event_id")
        if not event_id:
            blockers.append("event_id is required")
        else:
            passed.append("event_id_present")

        if not event_record.get("event_type"):
            blockers.append("event_type is required")
        else:
            passed.append("event_type_present")

        if event_record.get("visibility") not in self.VISIBILITY_VALUES:
            blockers.append(f"invalid visibility {event_record.get('visibility')}")
        else:
            passed.append("visibility_valid")

        for actor_id in event_record.get("actor_ids", []):
            if actor_id in state.character_states or actor_id in state.entity_states:
                passed.append(f"actor_{actor_id}_exists")
            else:
                blockers.append(f"actor {actor_id} missing from state")

        for target_id in event_record.get("target_ids", []):
            if target_id in state.character_states or target_id in state.entity_states:
                passed.append(f"target_{target_id}_exists")
            else:
                blockers.append(f"target {target_id} missing from state")

        for witness_id in event_record.get("witness_ids", []):
            if witness_id in state.character_states or witness_id in state.entity_states:
                passed.append(f"witness_{witness_id}_exists")
            else:
                warnings.append(f"witness {witness_id} missing from state")

        location_id = event_record.get("location_id")
        if location_id:
            location_report = self._validate_location_presence(state, event_record)
            blockers.extend(location_report["blockers"])
            warnings.extend(location_report["warnings"])
            passed.extend(location_report["passed_checks"])
        else:
            warnings.append("event has no location_id")

        link_report = self._validate_linked_records(state, event_record)
        blockers.extend(link_report["blockers"])
        warnings.extend(link_report["warnings"])
        passed.extend(link_report["passed_checks"])

        visibility_report = self._validate_visibility_logic(event_record)
        blockers.extend(visibility_report["blockers"])
        warnings.extend(visibility_report["warnings"])
        passed.extend(visibility_report["passed_checks"])

        return {
            "success": True,
            "engine_name": self.engine_name,
            "event_id": event_id,
            "valid": len(blockers) == 0,
            "passed_checks": passed,
            "blockers": blockers,
            "warnings": warnings,
            "recommendation": "allow_event_processing" if not blockers else "fix_event_before_processing",
        }

    def register_event_on_state(
        self,
        *,
        state: Any,
        event_record: Dict[str, Any],
        validate: bool = True,
    ) -> Dict[str, Any]:
        validation = self.validate_event_record(state=state, event_record=event_record) if validate else {
            "valid": True,
            "blockers": [],
            "warnings": [],
            "passed_checks": [],
        }

        if not validation["valid"]:
            return {
                "success": False,
                "engine_name": self.engine_name,
                "event_id": event_record.get("event_id"),
                "validation": validation,
                "updated_state": state,
            }

        event_id = event_record["event_id"]
        event = dict(event_record)

        state.metadata.setdefault("event_registry", {})[event_id] = event
        state.metadata.setdefault("event_history", []).append(
            {
                "event_id": event_id,
                "event_type": event.get("event_type"),
                "event_family": event.get("event_family"),
                "actor_ids": event.get("actor_ids", []),
                "target_ids": event.get("target_ids", []),
                "visibility": event.get("visibility"),
                "intensity": event.get("intensity"),
            }
        )

        state.metadata["last_event_id"] = event_id
        state.metadata["event_count"] = len(state.metadata["event_registry"])

        return {
            "success": True,
            "engine_name": self.engine_name,
            "event_id": event_id,
            "event_record": event,
            "validation": validation,
            "updated_state": state,
        }

    def route_event_to_engines(
        self,
        *,
        event_record: Dict[str, Any],
    ) -> Dict[str, Any]:
        family = event_record.get("event_family") or self.classify_event_type(event_record.get("event_type", ""))["event_family"]
        event_type = event_record.get("event_type", "")

        routes = []

        if family == "knowledge":
            routes.extend(["knowledge_secret_state_engine"])
            if event_type in {"evidence_reveal", "evidence_destroyed"} or event_record.get("linked_evidence_ids"):
                routes.append("evidence_engine")
            if event_type in {"rumor_heard", "rumor_spread"} or event_record.get("linked_rumor_ids"):
                routes.append("rumor_propagation_engine")

        if family == "relationship":
            routes.extend(["relationship_graph_engine", "relationship_arc_engine"])
            if event_type in {"private_confession", "romantic_turn", "repair_attempt", "forgiveness"}:
                routes.append("opposite_nature_chemistry_engine")

        if family == "obligation":
            routes.append("promise_oath_debt_engine")

        if family == "leverage":
            routes.append("leverage_blackmail_engine")

        if family == "bargain":
            routes.append("negotiation_bargain_engine")

        if family == "choice":
            routes.extend(["choice_feasibility_engine", "choice_architecture_engine"])

        if family == "consequence":
            routes.extend(["consequence_queue_engine", "consequence_resolver"])

        if family == "world":
            routes.extend(["location_presence_witness_validator", "simulation_constraint_solver"])
            if event_type in {"trial", "public_event", "public_humiliation"}:
                routes.extend(["evidence_engine", "rumor_propagation_engine", "reputation_delta"])

        # Cross-cutting routes
        if event_record.get("source_choice_id"):
            routes.append("consequence_queue_engine")
        if event_record.get("linked_secret_ids"):
            routes.append("knowledge_secret_state_engine")
        if event_record.get("linked_evidence_ids"):
            routes.append("evidence_engine")
        if event_record.get("linked_obligation_ids"):
            routes.append("promise_oath_debt_engine")
        if event_record.get("linked_leverage_ids"):
            routes.append("leverage_blackmail_engine")
        if event_record.get("linked_bargain_ids"):
            routes.append("negotiation_bargain_engine")

        routes.append("causal_chain_explanation_engine")

        return {
            "success": True,
            "engine_name": self.engine_name,
            "event_id": event_record.get("event_id"),
            "event_family": family,
            "routes": self._unique(routes),
        }

    def build_event_processing_plan(
        self,
        *,
        state: Any,
        event_record: Dict[str, Any],
    ) -> Dict[str, Any]:
        validation = self.validate_event_record(state=state, event_record=event_record)
        routing = self.route_event_to_engines(event_record=event_record)

        plan_steps = []
        if validation["valid"]:
            plan_steps.append("register_event")
            for route in routing["routes"]:
                plan_steps.append(f"run_{route}")
            plan_steps.append("queue_consequences")
            plan_steps.append("update_causal_graph")
        else:
            plan_steps.append("fix_event_validation_errors")

        return {
            "success": True,
            "engine_name": self.engine_name,
            "event_id": event_record.get("event_id"),
            "valid": validation["valid"],
            "validation": validation,
            "routing": routing,
            "plan_steps": plan_steps,
            "estimated_impact_score": self._estimated_impact_score(event_record),
            "chunk5_handoff": self.build_event_chunk5_handoff(event_record),
        }

    def build_event_card(self, *, event_record: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "event_id": event_record.get("event_id"),
            "event_name": event_record.get("event_name"),
            "event_type": event_record.get("event_type"),
            "event_family": event_record.get("event_family"),
            "visibility": event_record.get("visibility"),
            "severity_label": event_record.get("severity_label"),
            "intensity": event_record.get("intensity"),
            "actor_ids": event_record.get("actor_ids", []),
            "target_ids": event_record.get("target_ids", []),
            "witness_ids": event_record.get("witness_ids", []),
            "location_id": event_record.get("location_id"),
            "linked_record_counts": {
                "secrets": len(event_record.get("linked_secret_ids", [])),
                "evidence": len(event_record.get("linked_evidence_ids", [])),
                "rumors": len(event_record.get("linked_rumor_ids", [])),
                "obligations": len(event_record.get("linked_obligation_ids", [])),
                "leverage": len(event_record.get("linked_leverage_ids", [])),
                "bargains": len(event_record.get("linked_bargain_ids", [])),
            },
            "story_function": self._event_story_function(event_record),
        }

    def build_event_map(self, *, state: Any) -> Dict[str, Any]:
        registry = state.metadata.get("event_registry", {})
        records = {}

        for event_id, event in registry.items():
            records[event_id] = self.build_event_card(event_record=event)

        family_counts: Dict[str, int] = {}
        for record in records.values():
            family = record.get("event_family", "unknown")
            family_counts[family] = family_counts.get(family, 0) + 1

        return {
            "success": True,
            "engine_name": self.engine_name,
            "event_count": len(records),
            "event_records": records,
            "family_counts": family_counts,
            "last_event_id": state.metadata.get("last_event_id"),
            "warnings": self._event_map_warnings(records),
        }

    def build_event_chunk5_handoff(self, event_record: Dict[str, Any]) -> Dict[str, Any]:
        family = event_record.get("event_family")
        event_type = event_record.get("event_type")
        intensity = float(event_record.get("intensity", 0.5))

        scene_type = {
            "knowledge": "reveal_or_information_scene",
            "relationship": "relationship_turning_point_scene",
            "obligation": "promise_oath_debt_scene",
            "leverage": "coercion_or_blackmail_scene",
            "bargain": "negotiation_scene",
            "choice": "choice_scene",
            "consequence": "fallout_scene",
            "world": "world_event_scene",
        }.get(family, "event_scene")

        if event_type == "trial":
            scene_type = "trial_scene"
        elif event_type == "public_humiliation":
            scene_type = "public_humiliation_scene"
        elif event_type == "private_confession":
            scene_type = "confession_scene"
        elif event_type == "betrayal":
            scene_type = "betrayal_scene"

        return {
            "event_id": event_record.get("event_id"),
            "scene_type": scene_type,
            "priority": "high" if intensity >= 0.7 else "medium" if intensity >= 0.4 else "low",
            "must_show_witnesses": bool(event_record.get("witness_ids")),
            "must_show_information_path": bool(
                event_record.get("linked_secret_ids")
                or event_record.get("linked_evidence_ids")
                or event_record.get("linked_rumor_ids")
            ),
            "must_show_consequence_seed": intensity >= 0.55,
            "plot_tags": self._plot_tags(event_record),
        }

    def _validate_location_presence(self, state: Any, event_record: Dict[str, Any]) -> Dict[str, List[str]]:
        blockers: List[str] = []
        warnings: List[str] = []
        passed: List[str] = []

        location_id = event_record.get("location_id")
        participants = self._unique(
            event_record.get("actor_ids", [])
            + event_record.get("target_ids", [])
            + event_record.get("witness_ids", [])
        )

        for character_id in participants:
            character = state.character_states.get(character_id)
            if not character:
                continue
            current = character.current_location_id
            if current is None:
                warnings.append(f"{character_id} has no current location")
            elif current == location_id:
                passed.append(f"{character_id}_present_at_location")
            else:
                warnings.append(f"{character_id} is at {current}, event is at {location_id}")

        return {"blockers": blockers, "warnings": warnings, "passed_checks": passed}

    def _validate_linked_records(self, state: Any, event_record: Dict[str, Any]) -> Dict[str, List[str]]:
        blockers: List[str] = []
        warnings: List[str] = []
        passed: List[str] = []

        registry_specs = [
            ("linked_secret_ids", "secret_registry", "secret"),
            ("linked_evidence_ids", "evidence_registry", "evidence"),
            ("linked_rumor_ids", "rumor_registry", "rumor"),
            ("linked_obligation_ids", "obligation_registry", "obligation"),
            ("linked_leverage_ids", "leverage_registry", "leverage"),
            ("linked_bargain_ids", "bargain_registry", "bargain"),
        ]

        for field, registry_name, label in registry_specs:
            registry = state.metadata.get(registry_name, {})
            for item_id in event_record.get(field, []):
                if item_id in registry:
                    passed.append(f"{label}_{item_id}_linked")
                else:
                    warnings.append(f"linked {label} {item_id} not found in {registry_name}")

        return {"blockers": blockers, "warnings": warnings, "passed_checks": passed}

    def _validate_visibility_logic(self, event_record: Dict[str, Any]) -> Dict[str, List[str]]:
        blockers: List[str] = []
        warnings: List[str] = []
        passed: List[str] = []

        visibility = event_record.get("visibility")
        witness_ids = event_record.get("witness_ids", [])

        if visibility == "public":
            passed.append("public_event_visibility_valid")
        elif visibility == "witnessed":
            if witness_ids:
                passed.append("witnessed_event_has_witnesses")
            else:
                warnings.append("event is witnessed but has no witness_ids")
        elif visibility == "private":
            if len(witness_ids) > 2:
                warnings.append("private event has many witnesses")
            else:
                passed.append("private_event_visibility_valid")
        elif visibility == "faction_known":
            if event_record.get("involved_faction_ids"):
                passed.append("faction_known_event_has_faction")
            else:
                warnings.append("faction_known event has no involved_faction_ids")
        else:
            passed.append("visibility_logic_checked")

        return {"blockers": blockers, "warnings": warnings, "passed_checks": passed}

    def _guess_family(self, event_type: str) -> str:
        if any(token in event_type for token in ["secret", "evidence", "rumor", "truth", "lie"]):
            return "knowledge"
        if any(token in event_type for token in ["betray", "confession", "repair", "romance", "humiliation"]):
            return "relationship"
        if any(token in event_type for token in ["promise", "oath", "debt"]):
            return "obligation"
        if any(token in event_type for token in ["blackmail", "threat", "leverage"]):
            return "leverage"
        if any(token in event_type for token in ["bargain", "negotiation", "truce", "offer"]):
            return "bargain"
        if any(token in event_type for token in ["choice", "dilemma"]):
            return "choice"
        if any(token in event_type for token in ["consequence", "fallout"]):
            return "consequence"
        return "world"

    def _estimated_impact_score(self, event_record: Dict[str, Any]) -> float:
        intensity = float(event_record.get("intensity", 0.5))
        link_count = (
            len(event_record.get("linked_secret_ids", []))
            + len(event_record.get("linked_evidence_ids", []))
            + len(event_record.get("linked_rumor_ids", []))
            + len(event_record.get("linked_obligation_ids", []))
            + len(event_record.get("linked_leverage_ids", []))
            + len(event_record.get("linked_bargain_ids", []))
        )
        participant_count = len(self._unique(event_record.get("actor_ids", []) + event_record.get("target_ids", []) + event_record.get("witness_ids", [])))
        visibility_bonus = 0.18 if event_record.get("visibility") == "public" else 0.08 if event_record.get("visibility") == "witnessed" else 0.0

        return round(min(1.0, intensity * 0.45 + link_count * 0.06 + participant_count * 0.04 + visibility_bonus), 3)

    def _event_story_function(self, event_record: Dict[str, Any]) -> str:
        family = event_record.get("event_family")
        event_type = event_record.get("event_type")

        direct = {
            "trial": "institutional_pressure_scene",
            "public_humiliation": "status_damage_scene",
            "private_confession": "vulnerability_turning_point",
            "betrayal": "trust_rupture_scene",
            "evidence_reveal": "proof_reveal_scene",
            "rumor_spread": "information_distortion_scene",
            "blackmail_attempt": "coercion_scene",
            "negotiation_offer": "deal_pressure_scene",
            "choice_selected": "branch_commitment_scene",
            "consequence_triggered": "fallout_scene",
        }

        if event_type in direct:
            return direct[event_type]

        return {
            "knowledge": "information_state_change",
            "relationship": "relationship_state_change",
            "obligation": "promise_debt_state_change",
            "leverage": "coercive_pressure_change",
            "bargain": "negotiated_tradeoff_change",
            "choice": "branch_choice_change",
            "consequence": "fallout_resolution_change",
            "world": "world_state_change",
        }.get(family, "general_event")

    def _plot_tags(self, event_record: Dict[str, Any]) -> List[str]:
        tags = [event_record.get("event_family", "event"), event_record.get("event_type", "event")]
        if event_record.get("visibility") == "public":
            tags.append("public_consequence")
        if event_record.get("linked_secret_ids"):
            tags.append("secret_linked")
        if event_record.get("linked_evidence_ids"):
            tags.append("evidence_linked")
        if event_record.get("source_choice_id"):
            tags.append("choice_consequence")
        return self._unique(tags)

    def _event_map_warnings(self, records: Dict[str, Dict[str, Any]]) -> List[str]:
        warnings = []
        if len(records) > 50:
            warnings.append("large event map; consider filtering by arc or timeline")
        public_count = sum(1 for record in records.values() if record.get("visibility") == "public")
        if public_count > 10:
            warnings.append("many public events; reputation/rumor systems may need resolution")
        high_count = sum(1 for record in records.values() if record.get("severity_label") in {"major", "critical"})
        if high_count > 15:
            warnings.append("many high-severity events; pacing may be overloaded")
        return warnings

    def _severity_label(self, intensity: float) -> str:
        value = self._bounded(intensity)
        for label, (low, high) in self.EVENT_SEVERITY_LABELS.items():
            if low <= value < high:
                return label
        return "moderate"

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

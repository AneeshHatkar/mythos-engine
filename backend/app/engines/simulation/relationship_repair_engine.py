from typing import Any, Dict, List, Optional


class RelationshipRepairEngine:
    """Models believable relationship repair after damage, betrayal, conflict, or distance.

    Repair should not be instant. This engine checks whether repair is possible,
    what kind of repair is needed, what proof is required, and what emotional
    carryover must be addressed before trust can improve.
    """

    engine_name = "simulation.relationship_repair_engine"

    REPAIR_TYPES = {
        "apology",
        "atonement",
        "truth_confession",
        "proof_of_loyalty",
        "wound_validation",
        "boundary_respect",
        "shared_danger",
        "forgiveness_request",
        "romantic_repair",
        "rival_reconciliation",
        "debt_repayment",
        "public_defense",
    }

    REPAIR_STATUS_VALUES = {
        "proposed",
        "blocked",
        "attempted",
        "failed",
        "partial",
        "successful",
        "delayed",
        "rejected",
    }

    def create_repair_attempt_record(
        self,
        *,
        repair_id: str,
        relationship_id: str,
        initiator_id: str,
        receiver_id: str,
        repair_type: str,
        summary: str,
        source_event_id: Optional[str] = None,
        source_conflict_id: Optional[str] = None,
        source_carryover_ids: List[str] | None = None,
        required_truth_ids: List[str] | None = None,
        required_evidence_ids: List[str] | None = None,
        required_obligation_ids: List[str] | None = None,
        apology_quality: float = 0.5,
        accountability: float = 0.5,
        emotional_risk: float = 0.5,
        sincerity: float = 0.5,
        timing_fit: float = 0.5,
        metadata: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        if repair_type not in self.REPAIR_TYPES:
            repair_type = "apology"

        return {
            "repair_id": repair_id,
            "relationship_id": relationship_id,
            "initiator_id": initiator_id,
            "receiver_id": receiver_id,
            "repair_type": repair_type,
            "summary": summary,
            "source_event_id": source_event_id,
            "source_conflict_id": source_conflict_id,
            "source_carryover_ids": source_carryover_ids or [],
            "required_truth_ids": required_truth_ids or [],
            "required_evidence_ids": required_evidence_ids or [],
            "required_obligation_ids": required_obligation_ids or [],
            "apology_quality": self._bounded(apology_quality),
            "accountability": self._bounded(accountability),
            "emotional_risk": self._bounded(emotional_risk),
            "sincerity": self._bounded(sincerity),
            "timing_fit": self._bounded(timing_fit),
            "status": "proposed",
            "outcome_history": [],
            "metadata": metadata or {},
        }

    def register_repair_attempt_on_state(
        self,
        *,
        state: Any,
        repair_record: Dict[str, Any],
    ) -> Dict[str, Any]:
        repair_id = repair_record["repair_id"]
        state.metadata.setdefault("relationship_repair_registry", {})[repair_id] = dict(repair_record)
        state.metadata.setdefault("relationship_repair_history", []).append(
            {
                "action": "register_repair_attempt",
                "repair_id": repair_id,
                "relationship_id": repair_record.get("relationship_id"),
                "initiator_id": repair_record.get("initiator_id"),
                "receiver_id": repair_record.get("receiver_id"),
                "repair_type": repair_record.get("repair_type"),
            }
        )

        for character_id in [repair_record.get("initiator_id"), repair_record.get("receiver_id")]:
            if character_id in state.character_states:
                state.character_states[character_id].metadata.setdefault("relationship_repair_ids", [])
                state.character_states[character_id].metadata["relationship_repair_ids"] = self._unique(
                    state.character_states[character_id].metadata["relationship_repair_ids"] + [repair_id]
                )

        return {
            "success": True,
            "engine_name": self.engine_name,
            "repair_id": repair_id,
            "updated_state": state,
        }

    def evaluate_repair_feasibility(
        self,
        *,
        state: Any,
        repair_id: str,
    ) -> Dict[str, Any]:
        repair = state.metadata.get("relationship_repair_registry", {}).get(repair_id)
        if not repair:
            return {
                "success": False,
                "engine_name": self.engine_name,
                "repair_id": repair_id,
                "errors": [f"repair attempt {repair_id} not found"],
            }

        blockers: List[str] = []
        warnings: List[str] = []
        passed: List[str] = []

        rel = state.relationship_states.get(repair.get("relationship_id"))
        if not rel:
            blockers.append(f"relationship {repair.get('relationship_id')} not found")
        else:
            passed.append("relationship_exists")

        if repair.get("initiator_id") not in state.character_states:
            blockers.append(f"initiator {repair.get('initiator_id')} missing")
        else:
            passed.append("initiator_exists")

        if repair.get("receiver_id") not in state.character_states:
            blockers.append(f"receiver {repair.get('receiver_id')} missing")
        else:
            passed.append("receiver_exists")

        knowledge_report = self._check_truth_and_evidence_requirements(state, repair)
        blockers.extend(knowledge_report["blockers"])
        warnings.extend(knowledge_report["warnings"])
        passed.extend(knowledge_report["passed_checks"])

        obligation_report = self._check_obligation_requirements(state, repair)
        blockers.extend(obligation_report["blockers"])
        warnings.extend(obligation_report["warnings"])
        passed.extend(obligation_report["passed_checks"])

        emotional_report = self._check_emotional_carryover_pressure(state, repair)
        warnings.extend(emotional_report["warnings"])
        passed.extend(emotional_report["passed_checks"])

        repair_score = self._repair_score(state, repair, rel, blockers, warnings)
        feasible = len(blockers) == 0 and repair_score >= 0.25

        if rel:
            if rel.betrayal_risk >= 0.7 and repair.get("repair_type") not in {"atonement", "truth_confession", "proof_of_loyalty"}:
                warnings.append("high betrayal risk needs stronger repair than simple apology")
            if rel.trust <= 0.2 and repair.get("accountability", 0.5) < 0.6:
                warnings.append("low trust requires stronger accountability")

        return {
            "success": True,
            "engine_name": self.engine_name,
            "repair_id": repair_id,
            "feasible": feasible,
            "repair_score": repair_score,
            "repair_label": self._repair_label(repair_score, blockers),
            "passed_checks": passed,
            "blockers": blockers,
            "warnings": warnings,
            "recommendation": self._recommendation(feasible, repair_score, blockers, warnings),
            "chunk5_handoff": self._chunk5_handoff(repair, repair_score, blockers, warnings),
        }

    def apply_repair_outcome(
        self,
        *,
        state: Any,
        repair_id: str,
        outcome: str,
        outcome_event_id: Optional[str] = None,
        notes: str = "",
    ) -> Dict[str, Any]:
        repair = state.metadata.get("relationship_repair_registry", {}).get(repair_id)
        if not repair:
            return {
                "success": False,
                "engine_name": self.engine_name,
                "repair_id": repair_id,
                "errors": [f"repair attempt {repair_id} not found"],
                "updated_state": state,
            }

        if outcome not in self.REPAIR_STATUS_VALUES:
            outcome = "partial"

        repair["status"] = outcome
        repair.setdefault("outcome_history", []).append(
            {
                "outcome": outcome,
                "outcome_event_id": outcome_event_id,
                "notes": notes,
            }
        )

        relationship_update = self._relationship_update_from_outcome(state, repair, outcome)
        carryover_updates = self._carryover_updates_from_outcome(state, repair, outcome)

        state.metadata.setdefault("relationship_repair_history", []).append(
            {
                "action": "apply_repair_outcome",
                "repair_id": repair_id,
                "outcome": outcome,
                "outcome_event_id": outcome_event_id,
                "relationship_update": relationship_update,
                "carryover_update_count": len(carryover_updates),
            }
        )

        return {
            "success": True,
            "engine_name": self.engine_name,
            "repair_id": repair_id,
            "outcome": outcome,
            "updated_repair": repair,
            "relationship_update": relationship_update,
            "carryover_updates": carryover_updates,
            "chunk5_handoff": self._outcome_handoff(repair, outcome),
            "updated_state": state,
        }

    def suggest_repair_paths(
        self,
        *,
        state: Any,
        relationship_id: str,
        initiator_id: str,
        receiver_id: str,
    ) -> Dict[str, Any]:
        rel = state.relationship_states.get(relationship_id)
        if not rel:
            return {
                "success": False,
                "engine_name": self.engine_name,
                "relationship_id": relationship_id,
                "errors": [f"relationship {relationship_id} not found"],
            }

        options = []

        if rel.trust < 0.35:
            options.append(
                {
                    "repair_type": "truth_confession",
                    "fit_score": 0.75,
                    "reason": "low trust requires truth before closeness",
                    "required_scene": "private truth scene",
                }
            )
            options.append(
                {
                    "repair_type": "proof_of_loyalty",
                    "fit_score": 0.68,
                    "reason": "trust can recover through action under pressure",
                    "required_scene": "loyalty proof scene",
                }
            )

        if rel.resentment > 0.35:
            options.append(
                {
                    "repair_type": "wound_validation",
                    "fit_score": 0.70,
                    "reason": "resentment requires naming the wound",
                    "required_scene": "wound validation scene",
                }
            )

        if rel.betrayal_risk > 0.45:
            options.append(
                {
                    "repair_type": "atonement",
                    "fit_score": 0.78,
                    "reason": "betrayal risk needs cost-bearing repair",
                    "required_scene": "atonement scene",
                }
            )

        if rel.affection > 0.3 or rel.romantic_tension > 0.3:
            options.append(
                {
                    "repair_type": "romantic_repair",
                    "fit_score": 0.62,
                    "reason": "romantic tension can soften repair if boundaries are respected",
                    "required_scene": "romantic boundary repair scene",
                }
            )

        if not options:
            options.append(
                {
                    "repair_type": "apology",
                    "fit_score": 0.50,
                    "reason": "basic apology is sufficient for mild relationship strain",
                    "required_scene": "apology scene",
                }
            )

        options = sorted(options, key=lambda item: item["fit_score"], reverse=True)

        return {
            "success": True,
            "engine_name": self.engine_name,
            "relationship_id": relationship_id,
            "initiator_id": initiator_id,
            "receiver_id": receiver_id,
            "options": options,
            "recommended_repair_type": options[0]["repair_type"],
        }

    def build_relationship_repair_map(self, *, state: Any) -> Dict[str, Any]:
        registry = state.metadata.get("relationship_repair_registry", {})
        records = {}

        for repair_id, repair in registry.items():
            feasibility = self.evaluate_repair_feasibility(state=state, repair_id=repair_id)
            records[repair_id] = {
                "repair_id": repair_id,
                "relationship_id": repair.get("relationship_id"),
                "initiator_id": repair.get("initiator_id"),
                "receiver_id": repair.get("receiver_id"),
                "repair_type": repair.get("repair_type"),
                "status": repair.get("status"),
                "repair_score": feasibility.get("repair_score", 0.0),
                "repair_label": feasibility.get("repair_label"),
                "feasible": feasibility.get("feasible", False),
                "warning_count": len(feasibility.get("warnings", [])),
            }

        ranked = sorted(records.values(), key=lambda item: item["repair_score"], reverse=True)

        return {
            "success": True,
            "engine_name": self.engine_name,
            "repair_attempt_count": len(records),
            "repair_records": records,
            "ranked_repairs": ranked,
            "best_repair_attempt": ranked[0] if ranked else None,
            "warnings": self._map_warnings(ranked),
        }

    def _check_truth_and_evidence_requirements(self, state: Any, repair: Dict[str, Any]) -> Dict[str, List[str]]:
        blockers: List[str] = []
        warnings: List[str] = []
        passed: List[str] = []

        initiator_id = repair.get("initiator_id")
        knowledge = state.knowledge_states.get(initiator_id)

        required_truth_ids = repair.get("required_truth_ids", [])
        required_evidence_ids = repair.get("required_evidence_ids", [])

        if not required_truth_ids and not required_evidence_ids:
            passed.append("no_truth_or_evidence_requirement")
            return {"blockers": blockers, "warnings": warnings, "passed_checks": passed}

        if not knowledge:
            blockers.append("initiator has no knowledge state for repair requirements")
            return {"blockers": blockers, "warnings": warnings, "passed_checks": passed}

        for truth_id in required_truth_ids:
            if truth_id in knowledge.known_secret_ids:
                passed.append(f"knows_truth_{truth_id}")
            elif truth_id in knowledge.suspected_secret_ids:
                warnings.append(f"initiator only suspects truth {truth_id}")
            else:
                blockers.append(f"initiator does not know required truth {truth_id}")

        for evidence_id in required_evidence_ids:
            if evidence_id in knowledge.evidence_seen_ids:
                passed.append(f"saw_evidence_{evidence_id}")
            else:
                blockers.append(f"initiator has not seen required evidence {evidence_id}")

        return {"blockers": blockers, "warnings": warnings, "passed_checks": passed}

    def _check_obligation_requirements(self, state: Any, repair: Dict[str, Any]) -> Dict[str, List[str]]:
        blockers: List[str] = []
        warnings: List[str] = []
        passed: List[str] = []

        required = repair.get("required_obligation_ids", [])
        if not required:
            passed.append("no_obligation_requirement")
            return {"blockers": blockers, "warnings": warnings, "passed_checks": passed}

        registry = state.metadata.get("obligation_registry", {})
        for obligation_id in required:
            obligation = registry.get(obligation_id)
            if not obligation:
                blockers.append(f"required obligation {obligation_id} missing")
            elif obligation.get("status") in {"fulfilled", "partially_fulfilled", "active", "broken"}:
                passed.append(f"obligation_{obligation_id}_usable")
            else:
                warnings.append(f"obligation {obligation_id} status may not support repair")

        return {"blockers": blockers, "warnings": warnings, "passed_checks": passed}

    def _check_emotional_carryover_pressure(self, state: Any, repair: Dict[str, Any]) -> Dict[str, List[str]]:
        warnings: List[str] = []
        passed: List[str] = []

        receiver_id = repair.get("receiver_id")
        relevant = [
            record
            for record in state.metadata.get("emotional_carryover_registry", {}).values()
            if record.get("character_id") == receiver_id
            and record.get("status") != "resolved"
            and (
                repair.get("initiator_id") in record.get("linked_character_ids", [])
                or record.get("carryover_id") in repair.get("source_carryover_ids", [])
            )
        ]

        if not relevant:
            passed.append("no_blocking_emotional_carryover_found")
            return {"warnings": warnings, "passed_checks": passed}

        high = [record for record in relevant if float(record.get("intensity", 0.0)) >= 0.7]
        if high:
            warnings.append("receiver has high-intensity emotional carryover tied to initiator")
        passed.append(f"{len(relevant)}_relevant_emotional_carryover_records_found")

        return {"warnings": warnings, "passed_checks": passed}

    def _repair_score(self, state: Any, repair: Dict[str, Any], rel: Any, blockers: List[str], warnings: List[str]) -> float:
        if not rel:
            return 0.0

        accountability = float(repair.get("accountability", 0.5))
        sincerity = float(repair.get("sincerity", 0.5))
        apology = float(repair.get("apology_quality", 0.5))
        timing = float(repair.get("timing_fit", 0.5))
        emotional_risk = float(repair.get("emotional_risk", 0.5))

        relationship_need = (
            max(0.0, 0.6 - rel.trust) * 0.22
            + rel.resentment * 0.18
            + rel.betrayal_risk * 0.18
            + rel.repair_potential * 0.20
        )

        repair_quality = (
            accountability * 0.22
            + sincerity * 0.22
            + apology * 0.14
            + timing * 0.14
            + emotional_risk * 0.10
        )

        type_bonus = self._repair_type_bonus(repair.get("repair_type"), rel)

        score = relationship_need + repair_quality + type_bonus
        score -= len(blockers) * 0.25
        score -= len(warnings) * 0.04

        return round(max(0.0, min(1.0, score)), 3)

    def _repair_type_bonus(self, repair_type: str, rel: Any) -> float:
        if repair_type == "atonement" and rel.betrayal_risk > 0.4:
            return 0.12
        if repair_type == "truth_confession" and rel.trust < 0.4:
            return 0.10
        if repair_type == "wound_validation" and rel.resentment > 0.3:
            return 0.10
        if repair_type == "proof_of_loyalty" and rel.trust < 0.45:
            return 0.11
        if repair_type == "romantic_repair" and (rel.affection > 0.25 or rel.romantic_tension > 0.25):
            return 0.08
        return 0.04

    def _relationship_update_from_outcome(self, state: Any, repair: Dict[str, Any], outcome: str) -> Dict[str, float]:
        rel = state.relationship_states.get(repair.get("relationship_id"))
        if not rel:
            return {}

        magnitude = self._outcome_magnitude(outcome, repair)
        update = {
            "trust_delta": 0.0,
            "resentment_delta": 0.0,
            "repair_potential_delta": 0.0,
            "betrayal_risk_delta": 0.0,
            "emotional_intimacy_delta": 0.0,
        }

        if outcome == "successful":
            update = {
                "trust_delta": round(0.18 * magnitude, 3),
                "resentment_delta": round(-0.14 * magnitude, 3),
                "repair_potential_delta": round(0.10 * magnitude, 3),
                "betrayal_risk_delta": round(-0.10 * magnitude, 3),
                "emotional_intimacy_delta": round(0.08 * magnitude, 3),
            }
        elif outcome == "partial":
            update = {
                "trust_delta": round(0.08 * magnitude, 3),
                "resentment_delta": round(-0.06 * magnitude, 3),
                "repair_potential_delta": round(0.08 * magnitude, 3),
                "betrayal_risk_delta": round(-0.04 * magnitude, 3),
                "emotional_intimacy_delta": round(0.04 * magnitude, 3),
            }
        elif outcome in {"failed", "rejected"}:
            update = {
                "trust_delta": round(-0.08 * magnitude, 3),
                "resentment_delta": round(0.10 * magnitude, 3),
                "repair_potential_delta": round(-0.06 * magnitude, 3),
                "betrayal_risk_delta": round(0.06 * magnitude, 3),
                "emotional_intimacy_delta": round(-0.02 * magnitude, 3),
            }
        elif outcome == "delayed":
            update = {
                "trust_delta": 0.0,
                "resentment_delta": round(0.03 * magnitude, 3),
                "repair_potential_delta": round(0.04 * magnitude, 3),
                "betrayal_risk_delta": 0.0,
                "emotional_intimacy_delta": 0.0,
            }

        return update

    def _carryover_updates_from_outcome(self, state: Any, repair: Dict[str, Any], outcome: str) -> List[Dict[str, Any]]:
        updates = []
        receiver_id = repair.get("receiver_id")
        initiator_id = repair.get("initiator_id")

        for carryover_id, record in state.metadata.get("emotional_carryover_registry", {}).items():
            if record.get("character_id") != receiver_id:
                continue
            if initiator_id not in record.get("linked_character_ids", []) and carryover_id not in repair.get("source_carryover_ids", []):
                continue
            if record.get("status") == "resolved":
                continue

            old_intensity = float(record.get("intensity", 0.0))
            if outcome == "successful":
                record["intensity"] = self._bounded(old_intensity * 0.55)
                record["status"] = "softened"
            elif outcome == "partial":
                record["intensity"] = self._bounded(old_intensity * 0.78)
                record["status"] = "softened"
            elif outcome in {"failed", "rejected"}:
                record["intensity"] = self._bounded(old_intensity + 0.12)
                record["status"] = "intensified"

            record.setdefault("history", []).append(
                {
                    "action": "relationship_repair_outcome",
                    "repair_id": repair.get("repair_id"),
                    "outcome": outcome,
                    "old_intensity": old_intensity,
                    "new_intensity": record.get("intensity"),
                }
            )

            updates.append(
                {
                    "carryover_id": carryover_id,
                    "old_intensity": old_intensity,
                    "new_intensity": record.get("intensity"),
                    "status": record.get("status"),
                }
            )

        return updates

    def _outcome_magnitude(self, outcome: str, repair: Dict[str, Any]) -> float:
        base = (
            float(repair.get("accountability", 0.5)) * 0.35
            + float(repair.get("sincerity", 0.5)) * 0.30
            + float(repair.get("apology_quality", 0.5)) * 0.20
            + float(repair.get("timing_fit", 0.5)) * 0.15
        )
        if outcome in {"failed", "rejected"}:
            return max(0.35, base)
        return self._bounded(base)

    def _repair_label(self, score: float, blockers: List[str]) -> str:
        if blockers:
            return "blocked"
        if score >= 0.75:
            return "strong_repair_path"
        if score >= 0.55:
            return "plausible_repair_path"
        if score >= 0.25:
            return "fragile_repair_path"
        return "weak_repair_path"

    def _recommendation(self, feasible: bool, score: float, blockers: List[str], warnings: List[str]) -> str:
        if blockers:
            return "resolve_missing_requirements_before_repair"
        if score >= 0.75:
            return "allow_repair_scene"
        if score >= 0.55:
            return "allow_repair_with_emotional_cost"
        if feasible:
            return "add_setup_before_repair_payoff"
        return "do_not_repair_yet"

    def _chunk5_handoff(self, repair: Dict[str, Any], score: float, blockers: List[str], warnings: List[str]) -> Dict[str, Any]:
        return {
            "repair_id": repair.get("repair_id"),
            "relationship_id": repair.get("relationship_id"),
            "scene_type": self._scene_type(repair.get("repair_type")),
            "repair_score": score,
            "must_show_accountability": repair.get("accountability", 0.0) >= 0.45,
            "must_show_receiver_hesitation": bool(warnings) or score < 0.65,
            "must_resolve_blockers_first": bool(blockers),
            "required_setup": self._required_setup(blockers, warnings),
        }

    def _outcome_handoff(self, repair: Dict[str, Any], outcome: str) -> Dict[str, Any]:
        return {
            "repair_id": repair.get("repair_id"),
            "scene_type": self._scene_type(repair.get("repair_type")),
            "outcome": outcome,
            "next_scene_need": {
                "successful": "show changed behavior later",
                "partial": "show fragile trust test later",
                "failed": "show worsened wound or defensive reaction",
                "rejected": "show boundary and emotional aftermath",
                "delayed": "show unresolved tension",
            }.get(outcome, "show repair consequence"),
        }

    def _scene_type(self, repair_type: str) -> str:
        return {
            "apology": "apology_scene",
            "atonement": "atonement_scene",
            "truth_confession": "truth_confession_repair_scene",
            "proof_of_loyalty": "loyalty_proof_scene",
            "wound_validation": "wound_validation_scene",
            "boundary_respect": "boundary_repair_scene",
            "shared_danger": "shared_danger_repair_scene",
            "forgiveness_request": "forgiveness_request_scene",
            "romantic_repair": "romantic_repair_scene",
            "rival_reconciliation": "rival_reconciliation_scene",
            "debt_repayment": "debt_repayment_scene",
            "public_defense": "public_defense_repair_scene",
        }.get(repair_type, "relationship_repair_scene")

    def _required_setup(self, blockers: List[str], warnings: List[str]) -> List[str]:
        setup = []
        for item in blockers + warnings:
            lower = item.lower()
            if "truth" in lower or "knowledge" in lower:
                setup.append("add truth discovery/confession setup")
            if "evidence" in lower:
                setup.append("add evidence access scene")
            if "obligation" in lower:
                setup.append("resolve or acknowledge obligation")
            if "emotional carryover" in lower:
                setup.append("acknowledge emotional residue before repair")
            if "accountability" in lower:
                setup.append("increase accountability before repair")
        return self._unique(setup)

    def _map_warnings(self, ranked: List[Dict[str, Any]]) -> List[str]:
        warnings = []
        if not ranked:
            warnings.append("no relationship repair attempts registered")
        blocked = [record for record in ranked if not record.get("feasible")]
        if blocked:
            warnings.append(f"{len(blocked)} repair attempt(s) are blocked or weak")
        return warnings

    def _bounded(self, value: float) -> float:
        return round(max(0.0, min(1.0, float(value))), 3)

    def _unique(self, values: List[Any]) -> List[Any]:
        result = []
        seen = set()
        for value in values:
            key = str(value)
            if key not in seen:
                seen.add(key)
                result.append(value)
        return result

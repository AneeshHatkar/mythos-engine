from typing import Any, Dict, List, Optional

from backend.app.engines.simulation.agency_model_engine import AgencyModelEngine
from backend.app.schemas.simulation import SimulationState


class ChoiceFeasibilityEngine:
    """Evaluates whether a character choice is possible, blocked, risky, or plot-forced.

    Choice feasibility is stricter than agency scoring. Agency asks:
    "Would this character believably choose this?"

    Feasibility asks:
    "Can this character actually do this right now, given knowledge, evidence,
    resources, location, relationships, obligations, leverage, canon locks, and state?"
    """

    engine_name = "simulation.choice_feasibility_engine"

    def __init__(self, agency_engine: Optional[AgencyModelEngine] = None) -> None:
        self.agency_engine = agency_engine or AgencyModelEngine()

    def create_choice_record(
        self,
        *,
        choice_id: str,
        actor_id: str,
        action_type: str,
        summary: str,
        target_id: Optional[str] = None,
        required_secret_ids: List[str] | None = None,
        required_evidence_ids: List[str] | None = None,
        required_resource_ids: List[str] | None = None,
        required_location_id: Optional[str] = None,
        required_relationship_thresholds: Dict[str, float] | None = None,
        required_obligation_ids: List[str] | None = None,
        required_leverage_ids: List[str] | None = None,
        blocked_by_statuses: List[str] | None = None,
        moral_cost: float = 0.4,
        social_risk: float = 0.4,
        emotional_cost: float = 0.4,
        external_pressure: float = 0.0,
        metadata: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        return {
            "choice_id": choice_id,
            "actor_id": actor_id,
            "action_type": action_type,
            "summary": summary,
            "target_id": target_id,
            "required_secret_ids": required_secret_ids or [],
            "required_evidence_ids": required_evidence_ids or [],
            "required_resource_ids": required_resource_ids or [],
            "required_location_id": required_location_id,
            "required_relationship_thresholds": required_relationship_thresholds or {},
            "required_obligation_ids": required_obligation_ids or [],
            "required_leverage_ids": required_leverage_ids or [],
            "blocked_by_statuses": blocked_by_statuses or [],
            "moral_cost": self._bounded(moral_cost),
            "social_risk": self._bounded(social_risk),
            "emotional_cost": self._bounded(emotional_cost),
            "external_pressure": self._bounded(external_pressure),
            "metadata": metadata or {},
        }

    def evaluate_choice_feasibility(
        self,
        *,
        state: SimulationState,
        choice: Dict[str, Any],
        user_intent: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        actor_id = choice["actor_id"]
        target_id = choice.get("target_id")
        blockers: List[str] = []
        warnings: List[str] = []
        passed: List[str] = []

        actor = state.character_states.get(actor_id)
        if not actor:
            return {
                "success": False,
                "engine_name": self.engine_name,
                "choice_id": choice.get("choice_id"),
                "actor_id": actor_id,
                "feasible": False,
                "feasibility_label": "blocked",
                "blockers": [f"actor {actor_id} not found"],
                "warnings": [],
                "passed_checks": [],
            }

        passed.append("actor_exists")

        if target_id:
            if target_id in state.character_states or target_id in state.entity_states:
                passed.append("target_exists")
            else:
                blockers.append(f"target {target_id} not found")

        for status in choice.get("blocked_by_statuses", []):
            if status in actor.metadata.get("status_flags", []):
                blockers.append(f"actor has blocking status {status}")

        location_report = self._check_location(state, choice)
        blockers.extend(location_report["blockers"])
        warnings.extend(location_report["warnings"])
        passed.extend(location_report["passed_checks"])

        knowledge_report = self._check_knowledge(state, choice)
        blockers.extend(knowledge_report["blockers"])
        warnings.extend(knowledge_report["warnings"])
        passed.extend(knowledge_report["passed_checks"])

        resource_report = self._check_resources(state, choice)
        blockers.extend(resource_report["blockers"])
        warnings.extend(resource_report["warnings"])
        passed.extend(resource_report["passed_checks"])

        relationship_report = self._check_relationship_requirements(state, choice)
        blockers.extend(relationship_report["blockers"])
        warnings.extend(relationship_report["warnings"])
        passed.extend(relationship_report["passed_checks"])

        obligation_report = self._check_obligations(state, choice)
        blockers.extend(obligation_report["blockers"])
        warnings.extend(obligation_report["warnings"])
        passed.extend(obligation_report["passed_checks"])

        leverage_report = self._check_leverage(state, choice)
        blockers.extend(leverage_report["blockers"])
        warnings.extend(leverage_report["warnings"])
        passed.extend(leverage_report["passed_checks"])

        canon_report = self._check_canon_locks(state, choice)
        blockers.extend(canon_report["blockers"])
        warnings.extend(canon_report["warnings"])
        passed.extend(canon_report["passed_checks"])

        agency = self.agency_engine.evaluate_action_agency(
            state=state,
            character_id=actor_id,
            action_type=choice.get("action_type", "negotiate"),
            action_summary=choice.get("summary", ""),
            target_id=target_id,
            required_secret_ids=choice.get("required_secret_ids", []),
            required_evidence_ids=choice.get("required_evidence_ids", []),
            required_resource_ids=choice.get("required_resource_ids", []),
            moral_cost=float(choice.get("moral_cost", 0.4)),
            social_risk=float(choice.get("social_risk", 0.4)),
            emotional_cost=float(choice.get("emotional_cost", 0.4)),
            external_pressure=float(choice.get("external_pressure", 0.0)),
            user_intent=user_intent or {},
        )

        if not agency.get("viable", False):
            warnings.append("agency engine marks this choice as weak or non-viable")

        feasibility_score = self._feasibility_score(
            blockers=blockers,
            warnings=warnings,
            agency_score=float(agency.get("agency_score", 0.0)),
            choice=choice,
        )

        feasible = len(blockers) == 0 and feasibility_score >= 0.25
        label = self._feasibility_label(feasible, feasibility_score, blockers, warnings)

        return {
            "success": True,
            "engine_name": self.engine_name,
            "choice_id": choice.get("choice_id"),
            "actor_id": actor_id,
            "target_id": target_id,
            "action_type": choice.get("action_type"),
            "summary": choice.get("summary"),
            "feasible": feasible,
            "feasibility_label": label,
            "feasibility_score": feasibility_score,
            "agency_score": agency.get("agency_score", 0.0),
            "agency_report": agency,
            "passed_checks": passed,
            "blockers": blockers,
            "warnings": warnings,
            "risk_profile": self._risk_profile(choice, warnings, agency),
            "recommendation": self._recommendation(feasible, label, blockers, warnings),
            "chunk5_handoff": {
                "choice_can_be_plotted": feasible,
                "choice_needs_setup_scene": label in {"risky", "weak_agency"},
                "choice_needs_blocker_resolution": bool(blockers),
                "required_setup": self._required_setup(blockers, warnings, choice),
            },
        }

    def rank_feasible_choices(
        self,
        *,
        state: SimulationState,
        choices: List[Dict[str, Any]],
        user_intent: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        reports = [
            self.evaluate_choice_feasibility(
                state=state,
                choice=choice,
                user_intent=user_intent or {},
            )
            for choice in choices
        ]

        ranked = sorted(
            reports,
            key=lambda item: (
                1 if item.get("feasible") else 0,
                item.get("feasibility_score", 0.0),
                item.get("agency_score", 0.0),
            ),
            reverse=True,
        )

        return {
            "success": True,
            "engine_name": self.engine_name,
            "choice_count": len(choices),
            "feasible_count": sum(1 for report in reports if report.get("feasible")),
            "blocked_count": sum(1 for report in reports if report.get("feasibility_label") == "blocked"),
            "ranked_choices": ranked,
            "best_choice": ranked[0] if ranked else None,
            "warnings": self._ranking_warnings(ranked),
        }

    def build_choice_feasibility_map(
        self,
        *,
        state: SimulationState,
        choices_by_character: Dict[str, List[Dict[str, Any]]],
        user_intent: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        records = {}

        for character_id, choices in choices_by_character.items():
            records[character_id] = self.rank_feasible_choices(
                state=state,
                choices=choices,
                user_intent=user_intent or {},
            )

        return {
            "success": True,
            "engine_name": self.engine_name,
            "character_count": len(records),
            "choice_feasibility_records": records,
            "total_choice_count": sum(record["choice_count"] for record in records.values()),
            "total_feasible_count": sum(record["feasible_count"] for record in records.values()),
            "warnings": self._map_warnings(records),
        }

    def _check_location(self, state: SimulationState, choice: Dict[str, Any]) -> Dict[str, List[str]]:
        blockers: List[str] = []
        warnings: List[str] = []
        passed: List[str] = []

        required = choice.get("required_location_id")
        actor_id = choice.get("actor_id")
        if not required:
            passed.append("no_location_requirement")
            return {"blockers": blockers, "warnings": warnings, "passed_checks": passed}

        actor = state.character_states.get(actor_id)
        current = actor.current_location_id if actor else None

        if current == required:
            passed.append("actor_at_required_location")
        else:
            travel_possible = self._travel_possible(state, current, required)
            if travel_possible:
                warnings.append(f"actor must travel from {current} to {required}")
                passed.append("travel_path_exists")
            else:
                blockers.append(f"actor is at {current}, required location is {required}, and no travel path exists")

        return {"blockers": blockers, "warnings": warnings, "passed_checks": passed}

    def _check_knowledge(self, state: SimulationState, choice: Dict[str, Any]) -> Dict[str, List[str]]:
        blockers: List[str] = []
        warnings: List[str] = []
        passed: List[str] = []

        actor_id = choice.get("actor_id")
        knowledge = state.knowledge_states.get(actor_id)

        required_secret_ids = choice.get("required_secret_ids", [])
        required_evidence_ids = choice.get("required_evidence_ids", [])

        if not required_secret_ids and not required_evidence_ids:
            passed.append("no_knowledge_requirement")
            return {"blockers": blockers, "warnings": warnings, "passed_checks": passed}

        if not knowledge:
            blockers.append("actor has no knowledge state")
            return {"blockers": blockers, "warnings": warnings, "passed_checks": passed}

        for secret_id in required_secret_ids:
            if secret_id in knowledge.known_secret_ids:
                passed.append(f"knows_{secret_id}")
            elif secret_id in knowledge.suspected_secret_ids:
                warnings.append(f"actor only suspects {secret_id}")
            else:
                blockers.append(f"actor does not know required secret {secret_id}")

        for evidence_id in required_evidence_ids:
            if evidence_id in knowledge.evidence_seen_ids:
                passed.append(f"saw_{evidence_id}")
            else:
                blockers.append(f"actor has not seen required evidence {evidence_id}")

        return {"blockers": blockers, "warnings": warnings, "passed_checks": passed}

    def _check_resources(self, state: SimulationState, choice: Dict[str, Any]) -> Dict[str, List[str]]:
        blockers: List[str] = []
        warnings: List[str] = []
        passed: List[str] = []

        actor = state.character_states.get(choice.get("actor_id"))
        required = choice.get("required_resource_ids", [])

        if not required:
            passed.append("no_resource_requirement")
            return {"blockers": blockers, "warnings": warnings, "passed_checks": passed}

        owned = set((actor.metadata or {}).get("resource_ids", [])) if actor else set()

        for resource_id in required:
            if resource_id in owned:
                passed.append(f"has_resource_{resource_id}")
            else:
                blockers.append(f"actor missing required resource {resource_id}")

        return {"blockers": blockers, "warnings": warnings, "passed_checks": passed}

    def _check_relationship_requirements(self, state: SimulationState, choice: Dict[str, Any]) -> Dict[str, List[str]]:
        blockers: List[str] = []
        warnings: List[str] = []
        passed: List[str] = []

        target_id = choice.get("target_id")
        actor_id = choice.get("actor_id")
        thresholds = choice.get("required_relationship_thresholds", {})

        if not target_id or not thresholds:
            passed.append("no_relationship_threshold_requirement")
            return {"blockers": blockers, "warnings": warnings, "passed_checks": passed}

        rel = self._relationship_between(state, actor_id, target_id)
        if not rel:
            blockers.append(f"no relationship state between {actor_id} and {target_id}")
            return {"blockers": blockers, "warnings": warnings, "passed_checks": passed}

        for metric, threshold in thresholds.items():
            if not hasattr(rel, metric):
                warnings.append(f"relationship metric {metric} does not exist")
                continue

            value = float(getattr(rel, metric))
            if value >= float(threshold):
                passed.append(f"{metric}_threshold_met")
            else:
                blockers.append(f"{metric} {value} is below required threshold {threshold}")

        return {"blockers": blockers, "warnings": warnings, "passed_checks": passed}

    def _check_obligations(self, state: SimulationState, choice: Dict[str, Any]) -> Dict[str, List[str]]:
        blockers: List[str] = []
        warnings: List[str] = []
        passed: List[str] = []

        required = choice.get("required_obligation_ids", [])
        if not required:
            passed.append("no_obligation_requirement")
            return {"blockers": blockers, "warnings": warnings, "passed_checks": passed}

        registry = state.metadata.get("obligation_registry", {})
        for obligation_id in required:
            obligation = registry.get(obligation_id)
            if not obligation:
                blockers.append(f"required obligation {obligation_id} missing")
            elif obligation.get("status") not in {"active", "partially_fulfilled", "broken"}:
                warnings.append(f"obligation {obligation_id} status {obligation.get('status')} may not support choice")
            else:
                passed.append(f"obligation_{obligation_id}_usable")

        return {"blockers": blockers, "warnings": warnings, "passed_checks": passed}

    def _check_leverage(self, state: SimulationState, choice: Dict[str, Any]) -> Dict[str, List[str]]:
        blockers: List[str] = []
        warnings: List[str] = []
        passed: List[str] = []

        required = choice.get("required_leverage_ids", [])
        if not required:
            passed.append("no_leverage_requirement")
            return {"blockers": blockers, "warnings": warnings, "passed_checks": passed}

        registry = state.metadata.get("leverage_registry", {})
        for leverage_id in required:
            leverage = registry.get(leverage_id)
            if not leverage:
                blockers.append(f"required leverage {leverage_id} missing")
            elif leverage.get("status") != "active":
                warnings.append(f"leverage {leverage_id} is not active")
            else:
                passed.append(f"leverage_{leverage_id}_active")

        return {"blockers": blockers, "warnings": warnings, "passed_checks": passed}

    def _check_canon_locks(self, state: SimulationState, choice: Dict[str, Any]) -> Dict[str, List[str]]:
        blockers: List[str] = []
        warnings: List[str] = []
        passed: List[str] = []

        canon_locks = state.metadata.get("canon_locks", [])
        choice_tags = set(choice.get("metadata", {}).get("canon_tags", []))

        if not canon_locks:
            passed.append("no_canon_locks")
            return {"blockers": blockers, "warnings": warnings, "passed_checks": passed}

        for lock in canon_locks:
            locked_tag = lock.get("tag")
            if locked_tag and locked_tag in choice_tags and lock.get("locked", True):
                if lock.get("mode") == "block":
                    blockers.append(f"choice conflicts with canon lock {locked_tag}")
                else:
                    warnings.append(f"choice touches canon lock {locked_tag}")

        if not blockers and not warnings:
            passed.append("canon_locks_do_not_block_choice")

        return {"blockers": blockers, "warnings": warnings, "passed_checks": passed}

    def _travel_possible(self, state: SimulationState, current: Optional[str], required: Optional[str]) -> bool:
        if not current or not required:
            return False
        if current == required:
            return True

        edges = state.world_state.metadata.get("travel_edges", [])
        for edge in edges:
            source = edge.get("from_location_id")
            target = edge.get("to_location_id")
            if source == current and target == required:
                return True
            if edge.get("bidirectional", True) and source == required and target == current:
                return True

        return False

    def _relationship_between(self, state: SimulationState, a: str, b: str):
        for rel in state.relationship_states.values():
            if {rel.character_a_id, rel.character_b_id} == {a, b}:
                return rel
        return None

    def _feasibility_score(
        self,
        *,
        blockers: List[str],
        warnings: List[str],
        agency_score: float,
        choice: Dict[str, Any],
    ) -> float:
        base = 0.42 + agency_score * 0.42
        base -= len(blockers) * 0.18
        base -= len(warnings) * 0.04

        if choice.get("required_secret_ids") or choice.get("required_evidence_ids"):
            base += 0.04
        if choice.get("required_relationship_thresholds"):
            base += 0.04

        return round(max(0.0, min(1.0, base)), 3)

    def _feasibility_label(
        self,
        feasible: bool,
        score: float,
        blockers: List[str],
        warnings: List[str],
    ) -> str:
        if blockers:
            return "blocked"
        if not feasible:
            return "not_feasible"
        if score >= 0.72 and not warnings:
            return "strongly_feasible"
        if score >= 0.55:
            return "feasible"
        if warnings:
            return "risky"
        return "weak_agency"

    def _risk_profile(self, choice: Dict[str, Any], warnings: List[str], agency: Dict[str, Any]) -> Dict[str, Any]:
        social = float(choice.get("social_risk", 0.4))
        moral = float(choice.get("moral_cost", 0.4))
        emotional = float(choice.get("emotional_cost", 0.4))
        coercion = float(agency.get("score_components", {}).get("coercion_pressure", 0.0))

        return {
            "social_risk": round(social, 3),
            "moral_cost": round(moral, 3),
            "emotional_cost": round(emotional, 3),
            "coercion_pressure": round(coercion, 3),
            "warning_count": len(warnings),
            "overall_risk": round(min(1.0, social * 0.25 + moral * 0.25 + emotional * 0.25 + coercion * 0.25), 3),
        }

    def _recommendation(self, feasible: bool, label: str, blockers: List[str], warnings: List[str]) -> str:
        if blockers:
            return "resolve_blockers_before_plotting_choice"
        if label == "strongly_feasible":
            return "allow_choice"
        if label in {"feasible", "risky"}:
            return "allow_choice_with_setup_or_consequence"
        if label == "weak_agency":
            return "strengthen_motive_pressure_or_relationship_context"
        return "do_not_use_without_revision"

    def _required_setup(self, blockers: List[str], warnings: List[str], choice: Dict[str, Any]) -> List[str]:
        setup = []

        if choice.get("required_secret_ids"):
            setup.append("add prior knowledge/reveal scene")
        if choice.get("required_evidence_ids"):
            setup.append("add evidence discovery/access scene")
        if choice.get("required_resource_ids"):
            setup.append("add resource acquisition scene")
        if choice.get("required_location_id"):
            setup.append("add travel/location setup")
        if choice.get("required_relationship_thresholds"):
            setup.append("add relationship setup")

        for item in blockers + warnings:
            lower = item.lower()
            if "secret" in lower or "knowledge" in lower:
                setup.append("add prior knowledge/reveal scene")
            if "evidence" in lower:
                setup.append("add evidence discovery/access scene")
            if "resource" in lower:
                setup.append("add resource acquisition scene")
            if "location" in lower or "travel" in lower:
                setup.append("add travel/location setup")
            if "relationship" in lower or "trust" in lower:
                setup.append("add relationship setup")
            if "canon" in lower:
                setup.append("branch timeline or revise canon lock")

        return list(dict.fromkeys(setup))

    def _ranking_warnings(self, ranked: List[Dict[str, Any]]) -> List[str]:
        if not ranked:
            return ["no choices to rank"]
        if not any(choice.get("feasible") for choice in ranked):
            return ["no feasible choices available"]
        if ranked[0].get("feasibility_score", 0.0) < 0.45:
            return ["best choice is still weak"]
        return []

    def _map_warnings(self, records: Dict[str, Dict[str, Any]]) -> List[str]:
        warnings = []
        for character_id, record in records.items():
            if record["feasible_count"] == 0 and record["choice_count"] > 0:
                warnings.append(f"{character_id} has no feasible choices")
        return warnings

    def _bounded(self, value: float) -> float:
        return round(max(0.0, min(1.0, float(value))), 3)

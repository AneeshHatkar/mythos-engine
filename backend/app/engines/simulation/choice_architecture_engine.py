from typing import Any, Dict, List, Optional

from backend.app.engines.simulation.choice_feasibility_engine import ChoiceFeasibilityEngine
from backend.app.schemas.simulation import SimulationState


class ChoiceArchitectureEngine:
    """Builds structured choice sets from feasible actions.

    This engine does not merely rank actions. It designs meaningful choice
    architecture: moral dilemmas, hidden choices, locked choices, forced choices,
    tradeoff labels, branch risk, and story handoff data.
    """

    engine_name = "simulation.choice_architecture_engine"

    CHOICE_SET_TYPES = {
        "open_choice",
        "forced_choice",
        "moral_dilemma",
        "strategic_branch",
        "relationship_choice",
        "secret_reveal_choice",
        "sacrifice_choice",
        "negotiation_choice",
        "blackmail_response",
        "trial_choice",
        "romance_boundary_choice",
    }

    def __init__(self, feasibility_engine: Optional[ChoiceFeasibilityEngine] = None) -> None:
        self.feasibility_engine = feasibility_engine or ChoiceFeasibilityEngine()

    def build_choice_set(
        self,
        *,
        state: SimulationState,
        choice_set_id: str,
        actor_id: str,
        candidate_choices: List[Dict[str, Any]],
        choice_set_type: str = "open_choice",
        user_intent: Dict[str, Any] | None = None,
        max_visible_choices: int = 5,
        include_blocked_choices: bool = True,
    ) -> Dict[str, Any]:
        if choice_set_type not in self.CHOICE_SET_TYPES:
            choice_set_type = "open_choice"

        ranked = self.feasibility_engine.rank_feasible_choices(
            state=state,
            choices=candidate_choices,
            user_intent=user_intent or {},
        )

        choice_reports = ranked["ranked_choices"]
        visible_choices = self._select_visible_choices(
            choice_reports=choice_reports,
            max_visible_choices=max_visible_choices,
            include_blocked_choices=include_blocked_choices,
        )

        hidden_choices = [
            report for report in choice_reports
            if report.get("choice_id") not in {choice.get("choice_id") for choice in visible_choices}
        ]

        architecture = {
            "choice_set_id": choice_set_id,
            "choice_set_type": choice_set_type,
            "actor_id": actor_id,
            "visible_choices": [self._choice_card(report) for report in visible_choices],
            "hidden_choices": [self._choice_card(report) for report in hidden_choices],
            "recommended_choice_id": self._recommended_choice_id(visible_choices),
            "forced_choice_pressure": self._forced_choice_pressure(choice_reports, choice_set_type),
            "moral_dilemma_score": self._moral_dilemma_score(choice_reports),
            "branch_complexity_score": self._branch_complexity_score(choice_reports),
            "stakes_profile": self._stakes_profile(choice_reports),
            "choice_balance_report": self._choice_balance_report(choice_reports),
            "warnings": self._choice_set_warnings(choice_reports, choice_set_type),
        }

        return {
            "success": True,
            "engine_name": self.engine_name,
            "choice_set": architecture,
            "feasibility_ranking": ranked,
            "chunk5_handoff": self._chunk5_handoff(architecture),
        }

    def build_moral_dilemma(
        self,
        *,
        state: SimulationState,
        choice_set_id: str,
        actor_id: str,
        good_choice: Dict[str, Any],
        costly_choice: Dict[str, Any],
        dangerous_choice: Dict[str, Any],
        user_intent: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        choices = [good_choice, costly_choice, dangerous_choice]

        result = self.build_choice_set(
            state=state,
            choice_set_id=choice_set_id,
            actor_id=actor_id,
            candidate_choices=choices,
            choice_set_type="moral_dilemma",
            user_intent=user_intent or {},
            max_visible_choices=3,
            include_blocked_choices=True,
        )

        result["choice_set"]["dilemma_axes"] = self._dilemma_axes(result["choice_set"]["visible_choices"])
        result["choice_set"]["dilemma_quality"] = self._dilemma_quality(result["choice_set"])
        result["chunk5_handoff"]["scene_type"] = "moral_dilemma_scene"

        return result

    def build_response_choices_from_pressure(
        self,
        *,
        state: SimulationState,
        choice_set_id: str,
        actor_id: str,
        pressure_source_type: str,
        pressure_source_id: str,
        target_id: Optional[str] = None,
        user_intent: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        choices = []

        if pressure_source_type == "blackmail":
            choices = [
                self.feasibility_engine.create_choice_record(
                    choice_id=f"{choice_set_id}_comply",
                    actor_id=actor_id,
                    action_type="accept_bargain",
                    summary="Comply with the blackmail demand to avoid exposure.",
                    target_id=target_id,
                    required_leverage_ids=[pressure_source_id],
                    external_pressure=0.8,
                    moral_cost=0.6,
                    social_risk=0.5,
                    emotional_cost=0.7,
                ),
                self.feasibility_engine.create_choice_record(
                    choice_id=f"{choice_set_id}_resist",
                    actor_id=actor_id,
                    action_type="resist_blackmail",
                    summary="Refuse the blackmail and risk exposure.",
                    target_id=target_id,
                    required_leverage_ids=[pressure_source_id],
                    external_pressure=0.9,
                    moral_cost=0.3,
                    social_risk=0.8,
                    emotional_cost=0.8,
                ),
                self.feasibility_engine.create_choice_record(
                    choice_id=f"{choice_set_id}_counter",
                    actor_id=actor_id,
                    action_type="negotiate",
                    summary="Counter the blackmail with a bargain or counter-leverage.",
                    target_id=target_id,
                    required_leverage_ids=[pressure_source_id],
                    external_pressure=0.7,
                    moral_cost=0.5,
                    social_risk=0.6,
                    emotional_cost=0.6,
                ),
            ]
            choice_set_type = "blackmail_response"
        elif pressure_source_type == "trial":
            choices = [
                self.feasibility_engine.create_choice_record(
                    choice_id=f"{choice_set_id}_truth",
                    actor_id=actor_id,
                    action_type="expose_secret",
                    summary="Reveal the truth in court.",
                    target_id=target_id,
                    external_pressure=0.7,
                    moral_cost=0.2,
                    social_risk=0.8,
                    emotional_cost=0.7,
                ),
                self.feasibility_engine.create_choice_record(
                    choice_id=f"{choice_set_id}_silence",
                    actor_id=actor_id,
                    action_type="hide_truth",
                    summary="Stay silent to protect someone.",
                    target_id=target_id,
                    external_pressure=0.8,
                    moral_cost=0.7,
                    social_risk=0.5,
                    emotional_cost=0.6,
                ),
                self.feasibility_engine.create_choice_record(
                    choice_id=f"{choice_set_id}_bargain",
                    actor_id=actor_id,
                    action_type="negotiate",
                    summary="Try to bargain before testimony.",
                    target_id=target_id,
                    external_pressure=0.6,
                    moral_cost=0.4,
                    social_risk=0.5,
                    emotional_cost=0.5,
                ),
            ]
            choice_set_type = "trial_choice"
        else:
            choices = [
                self.feasibility_engine.create_choice_record(
                    choice_id=f"{choice_set_id}_act",
                    actor_id=actor_id,
                    action_type="negotiate",
                    summary="Act under pressure.",
                    target_id=target_id,
                    external_pressure=0.5,
                ),
                self.feasibility_engine.create_choice_record(
                    choice_id=f"{choice_set_id}_retreat",
                    actor_id=actor_id,
                    action_type="retreat",
                    summary="Retreat and delay the decision.",
                    target_id=target_id,
                    external_pressure=0.5,
                ),
            ]
            choice_set_type = "strategic_branch"

        result = self.build_choice_set(
            state=state,
            choice_set_id=choice_set_id,
            actor_id=actor_id,
            candidate_choices=choices,
            choice_set_type=choice_set_type,
            user_intent=user_intent or {},
            max_visible_choices=len(choices),
            include_blocked_choices=True,
        )

        result["choice_set"]["pressure_source"] = {
            "pressure_source_type": pressure_source_type,
            "pressure_source_id": pressure_source_id,
        }

        return result

    def compare_choice_sets(
        self,
        *,
        state: SimulationState,
        choice_sets: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        scored_sets = []

        for choice_set in choice_sets:
            visible = choice_set.get("visible_choices", [])
            scored_sets.append(
                {
                    "choice_set_id": choice_set.get("choice_set_id"),
                    "choice_set_type": choice_set.get("choice_set_type"),
                    "recommended_choice_id": choice_set.get("recommended_choice_id"),
                    "moral_dilemma_score": choice_set.get("moral_dilemma_score", 0.0),
                    "branch_complexity_score": choice_set.get("branch_complexity_score", 0.0),
                    "forced_choice_pressure": choice_set.get("forced_choice_pressure", 0.0),
                    "visible_choice_count": len(visible),
                    "quality_score": self._choice_set_quality(choice_set),
                }
            )

        ranked = sorted(scored_sets, key=lambda item: item["quality_score"], reverse=True)

        return {
            "success": True,
            "engine_name": self.engine_name,
            "choice_set_count": len(choice_sets),
            "ranked_choice_sets": ranked,
            "best_choice_set": ranked[0] if ranked else None,
            "warnings": self._compare_warnings(ranked),
        }

    def _select_visible_choices(
        self,
        *,
        choice_reports: List[Dict[str, Any]],
        max_visible_choices: int,
        include_blocked_choices: bool,
    ) -> List[Dict[str, Any]]:
        if include_blocked_choices:
            pool = choice_reports
        else:
            pool = [report for report in choice_reports if report.get("feasible")]

        # Keep strongest feasible choices first, but include at least one blocked/risky option
        # when available to show why a route is locked.
        visible = pool[:max_visible_choices]

        if include_blocked_choices and len(visible) < max_visible_choices:
            existing = {item.get("choice_id") for item in visible}
            for report in choice_reports:
                if report.get("choice_id") not in existing:
                    visible.append(report)
                    existing.add(report.get("choice_id"))
                if len(visible) >= max_visible_choices:
                    break

        return visible

    def _choice_card(self, report: Dict[str, Any]) -> Dict[str, Any]:
        risk = report.get("risk_profile", {})
        return {
            "choice_id": report.get("choice_id"),
            "action_type": report.get("action_type"),
            "summary": report.get("summary"),
            "feasible": report.get("feasible"),
            "feasibility_label": report.get("feasibility_label"),
            "feasibility_score": report.get("feasibility_score"),
            "agency_score": report.get("agency_score"),
            "blockers": report.get("blockers", []),
            "warnings": report.get("warnings", []),
            "risk_profile": risk,
            "pressure_label": self._pressure_label(risk),
            "story_function": self._story_function(report),
            "choice_visibility": self._choice_visibility(report),
            "consequence_preview": self._consequence_preview(report),
            "required_setup": report.get("chunk5_handoff", {}).get("required_setup", []),
        }

    def _recommended_choice_id(self, reports: List[Dict[str, Any]]) -> Optional[str]:
        feasible = [report for report in reports if report.get("feasible")]
        if not feasible:
            return None
        return max(feasible, key=lambda item: item.get("feasibility_score", 0.0)).get("choice_id")

    def _forced_choice_pressure(self, reports: List[Dict[str, Any]], choice_set_type: str) -> float:
        if not reports:
            return 0.0

        feasible_count = sum(1 for report in reports if report.get("feasible"))
        avg_risk = self._average([
            report.get("risk_profile", {}).get("overall_risk", 0.0)
            for report in reports
        ])

        type_bonus = 0.20 if choice_set_type in {"forced_choice", "blackmail_response", "trial_choice"} else 0.0
        scarcity = 1.0 - min(1.0, feasible_count / max(1, len(reports)))

        return round(min(1.0, scarcity * 0.45 + avg_risk * 0.35 + type_bonus), 3)

    def _moral_dilemma_score(self, reports: List[Dict[str, Any]]) -> float:
        if not reports:
            return 0.0

        moral_costs = [report.get("risk_profile", {}).get("moral_cost", 0.0) for report in reports]
        emotional_costs = [report.get("risk_profile", {}).get("emotional_cost", 0.0) for report in reports]
        feasible_count = sum(1 for report in reports if report.get("feasible"))

        spread = (max(moral_costs) - min(moral_costs)) if moral_costs else 0.0
        emotional_avg = self._average(emotional_costs)
        feasibility_bonus = min(1.0, feasible_count / max(1, len(reports)))

        return round(min(1.0, spread * 0.35 + emotional_avg * 0.35 + feasibility_bonus * 0.30), 3)

    def _branch_complexity_score(self, reports: List[Dict[str, Any]]) -> float:
        if not reports:
            return 0.0

        action_types = {report.get("action_type") for report in reports}
        feasible_count = sum(1 for report in reports if report.get("feasible"))
        setup_count = sum(len(report.get("chunk5_handoff", {}).get("required_setup", [])) for report in reports)

        return round(
            min(
                1.0,
                len(action_types) * 0.10
                + feasible_count * 0.08
                + setup_count * 0.03
                + len(reports) * 0.04,
            ),
            3,
        )

    def _stakes_profile(self, reports: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not reports:
            return {
                "average_social_risk": 0.0,
                "average_moral_cost": 0.0,
                "average_emotional_cost": 0.0,
                "highest_risk_choice_id": None,
            }

        risk_items = [(report.get("choice_id"), report.get("risk_profile", {})) for report in reports]
        highest = max(risk_items, key=lambda item: item[1].get("overall_risk", 0.0))

        return {
            "average_social_risk": self._average([risk.get("social_risk", 0.0) for _, risk in risk_items]),
            "average_moral_cost": self._average([risk.get("moral_cost", 0.0) for _, risk in risk_items]),
            "average_emotional_cost": self._average([risk.get("emotional_cost", 0.0) for _, risk in risk_items]),
            "average_overall_risk": self._average([risk.get("overall_risk", 0.0) for _, risk in risk_items]),
            "highest_risk_choice_id": highest[0],
        }

    def _choice_balance_report(self, reports: List[Dict[str, Any]]) -> Dict[str, Any]:
        feasible = [report for report in reports if report.get("feasible")]
        blocked = [report for report in reports if report.get("feasibility_label") == "blocked"]
        risky = [report for report in reports if report.get("feasibility_label") == "risky"]

        return {
            "total_choices": len(reports),
            "feasible_choices": len(feasible),
            "blocked_choices": len(blocked),
            "risky_choices": len(risky),
            "has_real_choice": len(feasible) >= 2,
            "has_locked_choice": len(blocked) > 0,
            "has_risky_choice": len(risky) > 0,
        }

    def _choice_set_warnings(self, reports: List[Dict[str, Any]], choice_set_type: str) -> List[str]:
        warnings = []
        feasible_count = sum(1 for report in reports if report.get("feasible"))

        if not reports:
            warnings.append("choice set has no choices")
        if feasible_count == 0:
            warnings.append("choice set has no feasible choices")
        if choice_set_type == "moral_dilemma" and feasible_count < 2:
            warnings.append("moral dilemma needs at least two feasible options")
        if len(reports) > 7:
            warnings.append("choice set may be too broad for one scene")
        if feasible_count == len(reports) and reports and self._moral_dilemma_score(reports) < 0.35:
            warnings.append("choices may be too easy; add cost, tradeoff, or consequence")

        return warnings

    def _pressure_label(self, risk: Dict[str, Any]) -> str:
        overall = risk.get("overall_risk", 0.0)
        coercion = risk.get("coercion_pressure", 0.0)

        if coercion >= 0.65:
            return "coerced_choice"
        if overall >= 0.75:
            return "high_risk_choice"
        if overall >= 0.5:
            return "costly_choice"
        if overall >= 0.25:
            return "moderate_pressure_choice"
        return "low_pressure_choice"

    def _story_function(self, report: Dict[str, Any]) -> str:
        action_type = report.get("action_type")

        mapping = {
            "expose_secret": "truth_reveal_branch",
            "hide_truth": "secret_delay_branch",
            "betray": "relationship_rupture_branch",
            "protect": "loyalty_proof_branch",
            "sacrifice": "costly_transformation_branch",
            "negotiate": "political_strategy_branch",
            "accept_bargain": "compromise_branch",
            "reject_bargain": "defiance_branch",
            "resist_blackmail": "agency_reclamation_branch",
            "repair_relationship": "repair_branch",
            "forgive": "forgiveness_branch",
        }

        return mapping.get(action_type, "general_story_branch")

    def _choice_visibility(self, report: Dict[str, Any]) -> str:
        if report.get("feasibility_label") == "blocked":
            return "locked_visible"
        if report.get("feasibility_label") == "risky":
            return "visible_risky"
        if report.get("agency_score", 0.0) < 0.35:
            return "hidden_until_motivated"
        return "visible"

    def _consequence_preview(self, report: Dict[str, Any]) -> Dict[str, Any]:
        action_type = report.get("action_type")
        risk = report.get("risk_profile", {})
        overall = risk.get("overall_risk", 0.0)

        preview = {
            "likely_consequence_scale": "low",
            "relationship_consequence": False,
            "reputation_consequence": False,
            "knowledge_consequence": False,
            "branch_consequence": False,
        }

        if overall >= 0.7:
            preview["likely_consequence_scale"] = "high"
        elif overall >= 0.45:
            preview["likely_consequence_scale"] = "medium"

        if action_type in {"betray", "protect", "repair_relationship", "forgive", "resist_blackmail"}:
            preview["relationship_consequence"] = True
        if action_type in {"expose_secret", "spread_rumor", "attempt_blackmail"}:
            preview["reputation_consequence"] = True
            preview["knowledge_consequence"] = True
        if action_type in {"sacrifice", "break_oath", "accept_bargain", "reject_bargain"}:
            preview["branch_consequence"] = True

        return preview

    def _dilemma_axes(self, visible_choices: List[Dict[str, Any]]) -> Dict[str, Any]:
        return {
            "truth_vs_safety": any(choice["action_type"] in {"expose_secret", "confess"} for choice in visible_choices)
            and any(choice["action_type"] in {"hide_truth", "lie", "retreat"} for choice in visible_choices),
            "loyalty_vs_self_preservation": any(choice["action_type"] in {"protect", "fulfill_oath"} for choice in visible_choices)
            and any(choice["action_type"] in {"betray", "break_oath", "accept_bargain"} for choice in visible_choices),
            "love_vs_status": any("romance" in str(choice).lower() or "love" in str(choice).lower() for choice in visible_choices)
            and any("status" in str(choice).lower() or "family" in str(choice).lower() for choice in visible_choices),
            "public_truth_vs_private_cost": any(choice.get("risk_profile", {}).get("social_risk", 0.0) >= 0.6 for choice in visible_choices)
            and any(choice.get("risk_profile", {}).get("emotional_cost", 0.0) >= 0.6 for choice in visible_choices),
        }

    def _dilemma_quality(self, choice_set: Dict[str, Any]) -> float:
        axes = choice_set.get("dilemma_axes", {})
        axes_score = sum(1 for value in axes.values() if value) * 0.18
        moral = choice_set.get("moral_dilemma_score", 0.0) * 0.40
        branch = choice_set.get("branch_complexity_score", 0.0) * 0.22
        forced = choice_set.get("forced_choice_pressure", 0.0) * 0.20
        return round(min(1.0, axes_score + moral + branch + forced), 3)

    def _choice_set_quality(self, choice_set: Dict[str, Any]) -> float:
        balance = choice_set.get("choice_balance_report", {})
        real_choice_bonus = 0.20 if balance.get("has_real_choice") else 0.0
        locked_bonus = 0.08 if balance.get("has_locked_choice") else 0.0
        risky_bonus = 0.08 if balance.get("has_risky_choice") else 0.0

        return round(
            min(
                1.0,
                choice_set.get("moral_dilemma_score", 0.0) * 0.28
                + choice_set.get("branch_complexity_score", 0.0) * 0.28
                + choice_set.get("forced_choice_pressure", 0.0) * 0.16
                + real_choice_bonus
                + locked_bonus
                + risky_bonus,
            ),
            3,
        )

    def _chunk5_handoff(self, architecture: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "choice_set_id": architecture["choice_set_id"],
            "scene_type": self._scene_type_from_choice_set(architecture["choice_set_type"]),
            "recommended_choice_id": architecture.get("recommended_choice_id"),
            "visible_choice_count": len(architecture.get("visible_choices", [])),
            "moral_dilemma_score": architecture.get("moral_dilemma_score"),
            "branch_complexity_score": architecture.get("branch_complexity_score"),
            "stakes_profile": architecture.get("stakes_profile"),
            "scene_requirements": self._scene_requirements(architecture),
            "plot_branch_tags": self._plot_branch_tags(architecture),
        }

    def _scene_type_from_choice_set(self, choice_set_type: str) -> str:
        mapping = {
            "moral_dilemma": "moral_dilemma_scene",
            "blackmail_response": "coercion_response_scene",
            "trial_choice": "trial_decision_scene",
            "relationship_choice": "relationship_turning_point_scene",
            "secret_reveal_choice": "secret_reveal_decision_scene",
            "sacrifice_choice": "sacrifice_decision_scene",
            "negotiation_choice": "negotiation_scene",
        }
        return mapping.get(choice_set_type, "choice_scene")

    def _scene_requirements(self, architecture: Dict[str, Any]) -> List[str]:
        requirements = []
        if architecture.get("forced_choice_pressure", 0.0) >= 0.55:
            requirements.append("show pressure narrowing options")
        if architecture.get("moral_dilemma_score", 0.0) >= 0.55:
            requirements.append("make each option emotionally costly")
        if architecture.get("choice_balance_report", {}).get("has_locked_choice"):
            requirements.append("show why locked choices are unavailable")
        if architecture.get("branch_complexity_score", 0.0) >= 0.6:
            requirements.append("make branch consequences legible")
        return requirements or ["present clear choice and consequence"]

    def _plot_branch_tags(self, architecture: Dict[str, Any]) -> List[str]:
        tags = [architecture.get("choice_set_type", "choice")]
        for choice in architecture.get("visible_choices", []):
            function = choice.get("story_function")
            if function:
                tags.append(function)
        return list(dict.fromkeys(tags))

    def _compare_warnings(self, ranked: List[Dict[str, Any]]) -> List[str]:
        if not ranked:
            return ["no choice sets compared"]
        if ranked[0]["quality_score"] < 0.35:
            return ["all choice sets are weak; add stronger costs, stakes, or branch consequences"]
        return []

    def _average(self, values: List[float]) -> float:
        if not values:
            return 0.0
        return round(sum(values) / len(values), 3)

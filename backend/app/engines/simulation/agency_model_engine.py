from typing import Any, Dict, List, Optional

from backend.app.schemas.simulation import (
    SimulationCharacterState,
    SimulationRelationshipState,
    SimulationState,
)


class AgencyModelEngine:
    """Scores whether a character can believably choose an action.

    This is the bridge between character psychology and simulation choices.
    MythOS should not make a character do something only because the plot needs it.
    The action must fit goals, pressure, knowledge, relationships, obligations,
    leverage, fear, morality, resources, and emotional state.
    """

    engine_name = "simulation.agency_model_engine"

    ACTION_TYPES = {
        "protect",
        "betray",
        "confess",
        "lie",
        "hide_truth",
        "expose_secret",
        "accept_bargain",
        "reject_bargain",
        "attempt_blackmail",
        "resist_blackmail",
        "fulfill_oath",
        "break_oath",
        "repair_relationship",
        "escalate_conflict",
        "retreat",
        "sacrifice",
        "seek_evidence",
        "spread_rumor",
        "negotiate",
        "attack",
        "forgive",
    }

    def build_agency_profile(
        self,
        *,
        state: SimulationState,
        character_id: str,
    ) -> Dict[str, Any]:
        character = state.character_states.get(character_id)
        if not character:
            return {
                "success": False,
                "engine_name": self.engine_name,
                "character_id": character_id,
                "errors": [f"character {character_id} not found"],
            }

        metadata = character.metadata or {}
        psychological = metadata.get("psychology", {})
        goals = metadata.get("goals", {})
        constraints = metadata.get("agency_constraints", {})

        knowledge = state.knowledge_states.get(character_id)
        active_obligations = self._active_obligations(state, character_id)
        active_leverage = self._active_leverage_against_character(state, character_id)
        held_leverage = self._active_leverage_held_by_character(state, character_id)
        relationship_pressure = self._relationship_pressure(state, character_id)

        profile = {
            "character_id": character_id,
            "current_location_id": character.current_location_id,
            "surface_goal": goals.get("surface_goal") or metadata.get("surface_goal"),
            "hidden_goal": goals.get("hidden_goal") or metadata.get("hidden_goal"),
            "true_need": goals.get("true_need") or metadata.get("true_need"),
            "core_wound": psychological.get("core_wound") or metadata.get("core_wound"),
            "dominant_moral_value": psychological.get("dominant_moral_value") or metadata.get("dominant_moral_value"),
            "fear_profile": psychological.get("fear_profile") or metadata.get("fear_profile", {}),
            "public_mask": psychological.get("public_mask") or metadata.get("public_mask"),
            "private_truth": psychological.get("private_truth") or metadata.get("private_truth"),
            "agency_constraints": constraints,
            "known_secret_count": len(knowledge.known_secret_ids) if knowledge else 0,
            "suspected_secret_count": len(knowledge.suspected_secret_ids) if knowledge else 0,
            "evidence_seen_count": len(knowledge.evidence_seen_ids) if knowledge else 0,
            "active_obligation_count": len(active_obligations),
            "active_leverage_against_count": len(active_leverage),
            "active_leverage_held_count": len(held_leverage),
            "relationship_pressure": relationship_pressure,
            "agency_freedom_score": self._agency_freedom_score(
                character=character,
                active_obligations=active_obligations,
                active_leverage=active_leverage,
                relationship_pressure=relationship_pressure,
            ),
            "coercion_pressure": self._coercion_pressure(active_leverage, active_obligations),
            "choice_complexity": self._choice_complexity(knowledge, active_obligations, active_leverage, relationship_pressure),
        }

        return {
            "success": True,
            "engine_name": self.engine_name,
            "character_id": character_id,
            "agency_profile": profile,
            "warnings": self._profile_warnings(profile),
        }

    def evaluate_action_agency(
        self,
        *,
        state: SimulationState,
        character_id: str,
        action_type: str,
        action_summary: str,
        target_id: Optional[str] = None,
        required_secret_ids: List[str] | None = None,
        required_evidence_ids: List[str] | None = None,
        required_resource_ids: List[str] | None = None,
        moral_cost: float = 0.4,
        social_risk: float = 0.4,
        emotional_cost: float = 0.4,
        external_pressure: float = 0.0,
        user_intent: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        if action_type not in self.ACTION_TYPES:
            action_type = "negotiate"

        character = state.character_states.get(character_id)
        if not character:
            return {
                "success": False,
                "engine_name": self.engine_name,
                "character_id": character_id,
                "action_type": action_type,
                "viable": False,
                "blockers": [f"character {character_id} not found"],
                "warnings": [],
            }

        profile_result = self.build_agency_profile(state=state, character_id=character_id)
        profile = profile_result["agency_profile"]

        blockers: List[str] = []
        warnings: List[str] = []
        passed: List[str] = []

        knowledge_report = self._validate_knowledge_requirements(
            state=state,
            character_id=character_id,
            required_secret_ids=required_secret_ids or [],
            required_evidence_ids=required_evidence_ids or [],
        )
        blockers.extend(knowledge_report["blockers"])
        warnings.extend(knowledge_report["warnings"])
        passed.extend(knowledge_report["passed_checks"])

        resource_report = self._validate_resource_requirements(
            character=character,
            required_resource_ids=required_resource_ids or [],
        )
        blockers.extend(resource_report["blockers"])
        warnings.extend(resource_report["warnings"])
        passed.extend(resource_report["passed_checks"])

        relationship_fit = self._relationship_fit_for_action(
            state=state,
            actor_id=character_id,
            target_id=target_id,
            action_type=action_type,
        )

        goal_fit = self._goal_fit(profile, action_summary, action_type)
        moral_fit = self._moral_fit(profile, action_type, moral_cost)
        pressure_fit = self._pressure_fit(
            profile=profile,
            action_type=action_type,
            external_pressure=external_pressure,
        )
        emotional_fit = self._emotional_fit(profile, action_type, emotional_cost)
        intent_fit = self._intent_fit(user_intent or {}, action_type, action_summary)

        agency_score = round(
            max(
                0.0,
                min(
                    1.0,
                    goal_fit * 0.22
                    + moral_fit * 0.16
                    + pressure_fit * 0.18
                    + relationship_fit * 0.18
                    + emotional_fit * 0.14
                    + intent_fit * 0.08
                    + profile["agency_freedom_score"] * 0.04
                    - len(blockers) * 0.18,
                ),
            ),
            3,
        )

        if agency_score < 0.35:
            warnings.append("action has weak agency fit; may feel plot-forced")
        if profile["coercion_pressure"] > 0.65 and action_type not in {"resist_blackmail", "accept_bargain", "hide_truth", "lie", "retreat"}:
            warnings.append("character is highly coerced; action should reflect pressure or resistance")
        if action_type in {"betray", "break_oath"} and not self._has_betrayal_trigger(state, character_id):
            warnings.append("betrayal/broken oath should have a clear trigger")

        viable = len(blockers) == 0 and agency_score >= 0.25

        return {
            "success": True,
            "engine_name": self.engine_name,
            "character_id": character_id,
            "action_type": action_type,
            "action_summary": action_summary,
            "target_id": target_id,
            "viable": viable,
            "agency_score": agency_score,
            "score_components": {
                "goal_fit": goal_fit,
                "moral_fit": moral_fit,
                "pressure_fit": pressure_fit,
                "relationship_fit": relationship_fit,
                "emotional_fit": emotional_fit,
                "intent_fit": intent_fit,
                "agency_freedom_score": profile["agency_freedom_score"],
                "coercion_pressure": profile["coercion_pressure"],
            },
            "passed_checks": passed,
            "blockers": blockers,
            "warnings": warnings,
            "recommendation": self._recommendation(viable, agency_score, blockers, warnings),
            "chunk5_handoff": {
                "agency_scene_requirement": self._scene_requirement(action_type, agency_score, profile),
                "must_show_pressure": profile["coercion_pressure"] > 0.55,
                "must_show_motive": agency_score < 0.55,
                "avoid_plot_forcing": agency_score < 0.45,
            },
        }

    def rank_actions_for_character(
        self,
        *,
        state: SimulationState,
        character_id: str,
        candidate_actions: List[Dict[str, Any]],
        user_intent: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        scored = []

        for action in candidate_actions:
            scored.append(
                self.evaluate_action_agency(
                    state=state,
                    character_id=character_id,
                    action_type=action.get("action_type", "negotiate"),
                    action_summary=action.get("action_summary", ""),
                    target_id=action.get("target_id"),
                    required_secret_ids=action.get("required_secret_ids", []),
                    required_evidence_ids=action.get("required_evidence_ids", []),
                    required_resource_ids=action.get("required_resource_ids", []),
                    moral_cost=float(action.get("moral_cost", 0.4)),
                    social_risk=float(action.get("social_risk", 0.4)),
                    emotional_cost=float(action.get("emotional_cost", 0.4)),
                    external_pressure=float(action.get("external_pressure", 0.0)),
                    user_intent=user_intent or {},
                )
            )

        ranked = sorted(scored, key=lambda item: item["agency_score"], reverse=True)

        return {
            "success": True,
            "engine_name": self.engine_name,
            "character_id": character_id,
            "action_count": len(candidate_actions),
            "ranked_actions": ranked,
            "best_action": ranked[0] if ranked else None,
            "warnings": self._ranking_warnings(ranked),
        }

    def build_agency_map(self, *, state: SimulationState) -> Dict[str, Any]:
        profiles = {}
        warnings = []

        for character_id in state.character_states:
            result = self.build_agency_profile(state=state, character_id=character_id)
            if result["success"]:
                profiles[character_id] = result["agency_profile"]
                warnings.extend(result.get("warnings", []))

        return {
            "success": True,
            "engine_name": self.engine_name,
            "character_count": len(profiles),
            "agency_profiles": profiles,
            "average_agency_freedom": self._average([p["agency_freedom_score"] for p in profiles.values()]),
            "average_coercion_pressure": self._average([p["coercion_pressure"] for p in profiles.values()]),
            "warnings": list(dict.fromkeys(warnings)),
        }

    def _validate_knowledge_requirements(
        self,
        *,
        state: SimulationState,
        character_id: str,
        required_secret_ids: List[str],
        required_evidence_ids: List[str],
    ) -> Dict[str, Any]:
        blockers: List[str] = []
        warnings: List[str] = []
        passed: List[str] = []

        knowledge = state.knowledge_states.get(character_id)

        if not required_secret_ids and not required_evidence_ids:
            passed.append("no_knowledge_requirements")
            return {"blockers": blockers, "warnings": warnings, "passed_checks": passed}

        if not knowledge:
            blockers.append("character has no knowledge state for required knowledge")
            return {"blockers": blockers, "warnings": warnings, "passed_checks": passed}

        for secret_id in required_secret_ids:
            if secret_id in knowledge.known_secret_ids:
                passed.append(f"knows_{secret_id}")
            elif secret_id in knowledge.suspected_secret_ids:
                warnings.append(f"only suspects required secret {secret_id}")
            else:
                blockers.append(f"does not know required secret {secret_id}")

        for evidence_id in required_evidence_ids:
            if evidence_id in knowledge.evidence_seen_ids:
                passed.append(f"saw_{evidence_id}")
            else:
                blockers.append(f"has not seen required evidence {evidence_id}")

        return {"blockers": blockers, "warnings": warnings, "passed_checks": passed}

    def _validate_resource_requirements(
        self,
        *,
        character: SimulationCharacterState,
        required_resource_ids: List[str],
    ) -> Dict[str, Any]:
        blockers: List[str] = []
        warnings: List[str] = []
        passed: List[str] = []

        if not required_resource_ids:
            passed.append("no_resource_requirements")
            return {"blockers": blockers, "warnings": warnings, "passed_checks": passed}

        owned = set(character.metadata.get("resource_ids", []))
        for resource_id in required_resource_ids:
            if resource_id in owned:
                passed.append(f"has_resource_{resource_id}")
            else:
                blockers.append(f"missing required resource {resource_id}")

        return {"blockers": blockers, "warnings": warnings, "passed_checks": passed}

    def _goal_fit(self, profile: Dict[str, Any], action_summary: str, action_type: str) -> float:
        text = f"{profile.get('surface_goal')} {profile.get('hidden_goal')} {profile.get('true_need')} {action_summary}".lower()

        if action_type in {"protect", "seek_evidence", "expose_secret", "fulfill_oath"}:
            tokens = ["protect", "truth", "evidence", "testimony", "belong", "prove", "save"]
        elif action_type in {"betray", "lie", "hide_truth", "break_oath"}:
            tokens = ["survive", "protect", "family", "fear", "position", "safety"]
        elif action_type in {"negotiate", "accept_bargain", "reject_bargain"}:
            tokens = ["deal", "bargain", "protect", "survive", "truth", "source"]
        elif action_type in {"repair_relationship", "forgive"}:
            tokens = ["belong", "truth", "forgive", "repair", "need", "love"]
        else:
            tokens = ["survive", "truth", "protect", "power"]

        matches = sum(1 for token in tokens if token in text)
        return round(min(1.0, 0.25 + matches * 0.15), 3)

    def _moral_fit(self, profile: Dict[str, Any], action_type: str, moral_cost: float) -> float:
        morality = str(profile.get("dominant_moral_value") or "").lower()
        moral_cost = self._bounded(moral_cost)

        truth_aligned = any(token in morality for token in ["truth", "justice", "honor", "protect"])
        survival_aligned = any(token in morality for token in ["survive", "family", "loyalty", "power"])

        if action_type in {"confess", "expose_secret", "fulfill_oath", "repair_relationship", "protect"}:
            base = 0.75 if truth_aligned else 0.55
        elif action_type in {"lie", "hide_truth", "betray", "break_oath", "attempt_blackmail"}:
            base = 0.55 if survival_aligned else 0.35
        else:
            base = 0.55

        return round(max(0.0, min(1.0, base - moral_cost * 0.25)), 3)

    def _pressure_fit(self, profile: Dict[str, Any], action_type: str, external_pressure: float) -> float:
        coercion = profile.get("coercion_pressure", 0.0)
        pressure = self._bounded(external_pressure)

        pressure_total = min(1.0, coercion * 0.65 + pressure * 0.35)

        if action_type in {"accept_bargain", "lie", "hide_truth", "retreat", "resist_blackmail"}:
            return round(max(0.35, pressure_total), 3)

        if action_type in {"confess", "expose_secret", "sacrifice", "fulfill_oath"}:
            return round(max(0.2, 1.0 - pressure_total * 0.45), 3)

        return round(max(0.25, 0.6 - pressure_total * 0.2), 3)

    def _relationship_fit_for_action(
        self,
        *,
        state: SimulationState,
        actor_id: str,
        target_id: Optional[str],
        action_type: str,
    ) -> float:
        if not target_id:
            return 0.5

        rel = self._relationship_between(state, actor_id, target_id)
        if not rel:
            return 0.4

        if action_type in {"protect", "repair_relationship", "forgive", "fulfill_oath"}:
            return round(min(1.0, rel.trust * 0.35 + rel.affection * 0.25 + rel.loyalty * 0.20 + rel.repair_potential * 0.20), 3)

        if action_type in {"betray", "break_oath", "attempt_blackmail", "expose_secret"}:
            return round(min(1.0, rel.resentment * 0.28 + rel.betrayal_risk * 0.30 + rel.knowledge_asymmetry * 0.22 + rel.rivalry * 0.20), 3)

        if action_type in {"negotiate", "accept_bargain", "reject_bargain"}:
            return round(min(1.0, rel.trust * 0.28 + rel.respect * 0.28 + rel.power_imbalance * 0.16 + rel.repair_potential * 0.12 + 0.16), 3)

        return round(min(1.0, rel.trust * 0.3 + rel.respect * 0.3 + rel.rivalry * 0.15 + 0.2), 3)

    def _emotional_fit(self, profile: Dict[str, Any], action_type: str, emotional_cost: float) -> float:
        emotional_cost = self._bounded(emotional_cost)
        wound = str(profile.get("core_wound") or "").lower()
        fear_profile = str(profile.get("fear_profile") or "").lower()

        vulnerability_actions = {"confess", "repair_relationship", "forgive", "sacrifice"}
        control_actions = {"lie", "hide_truth", "retreat", "attempt_blackmail"}

        if action_type in vulnerability_actions:
            base = 0.45
            if "abandon" in wound or "belong" in wound or "unreal" in wound:
                base += 0.15
            return round(max(0.0, min(1.0, base - emotional_cost * 0.18)), 3)

        if action_type in control_actions:
            base = 0.55
            if "fear" in fear_profile or "failure" in wound or "revoked" in wound:
                base += 0.15
            return round(max(0.0, min(1.0, base - emotional_cost * 0.10)), 3)

        return round(max(0.1, 0.55 - emotional_cost * 0.12), 3)

    def _intent_fit(self, user_intent: Dict[str, Any], action_type: str, action_summary: str) -> float:
        text = f"{user_intent} {action_summary}".lower()

        mapping = {
            "betray": ["betrayal", "traitor", "blackmail"],
            "confess": ["confession", "truth", "vulnerability"],
            "protect": ["protect", "sacrifice", "loyalty"],
            "expose_secret": ["secret", "trial", "truth", "reveal"],
            "repair_relationship": ["repair", "forgiveness", "romance"],
            "negotiate": ["political", "bargain", "court"],
        }

        tokens = mapping.get(action_type, [action_type])
        return 1.0 if any(token in text for token in tokens) else 0.45

    def _agency_freedom_score(
        self,
        *,
        character: SimulationCharacterState,
        active_obligations: List[Dict[str, Any]],
        active_leverage: List[Dict[str, Any]],
        relationship_pressure: float,
    ) -> float:
        constraints = character.metadata.get("agency_constraints", {})
        hard_limit = float(constraints.get("hard_limit_score", 0.0) or 0.0)
        obligation_pressure = min(0.35, len(active_obligations) * 0.08)
        leverage_pressure = min(0.40, len(active_leverage) * 0.14)
        return round(max(0.0, min(1.0, 1.0 - hard_limit - obligation_pressure - leverage_pressure - relationship_pressure * 0.15)), 3)

    def _coercion_pressure(self, active_leverage: List[Dict[str, Any]], active_obligations: List[Dict[str, Any]]) -> float:
        leverage_pressure = sum(float(item.get("pressure_level", 0.5)) for item in active_leverage) * 0.18
        obligation_pressure = sum(float(item.get("pressure_score", 0.5)) for item in active_obligations) * 0.08
        return round(min(1.0, leverage_pressure + obligation_pressure), 3)

    def _choice_complexity(
        self,
        knowledge: Any,
        active_obligations: List[Dict[str, Any]],
        active_leverage: List[Dict[str, Any]],
        relationship_pressure: float,
    ) -> float:
        knowledge_count = 0
        if knowledge:
            knowledge_count = len(knowledge.known_secret_ids) + len(knowledge.suspected_secret_ids) + len(knowledge.evidence_seen_ids)
        return round(min(1.0, knowledge_count * 0.04 + len(active_obligations) * 0.08 + len(active_leverage) * 0.12 + relationship_pressure * 0.2), 3)

    def _active_obligations(self, state: SimulationState, character_id: str) -> List[Dict[str, Any]]:
        results = []
        for obligation in state.metadata.get("obligation_registry", {}).values():
            if obligation.get("status") == "active" and character_id in {obligation.get("promiser_id"), obligation.get("promisee_id")}:
                results.append(obligation)
        return results

    def _active_leverage_against_character(self, state: SimulationState, character_id: str) -> List[Dict[str, Any]]:
        return [
            leverage
            for leverage in state.metadata.get("leverage_registry", {}).values()
            if leverage.get("status") == "active" and leverage.get("target_id") == character_id
        ]

    def _active_leverage_held_by_character(self, state: SimulationState, character_id: str) -> List[Dict[str, Any]]:
        return [
            leverage
            for leverage in state.metadata.get("leverage_registry", {}).values()
            if leverage.get("status") == "active" and leverage.get("holder_id") == character_id
        ]

    def _relationship_pressure(self, state: SimulationState, character_id: str) -> float:
        pressure = 0.0
        count = 0
        for rel in state.relationship_states.values():
            if character_id in {rel.character_a_id, rel.character_b_id}:
                pressure += rel.resentment * 0.22 + rel.betrayal_risk * 0.24 + rel.knowledge_asymmetry * 0.18 + rel.rivalry * 0.14
                count += 1
        if count == 0:
            return 0.0
        return round(min(1.0, pressure / count), 3)

    def _relationship_between(self, state: SimulationState, a: str, b: str) -> Optional[SimulationRelationshipState]:
        for rel in state.relationship_states.values():
            if {rel.character_a_id, rel.character_b_id} == {a, b}:
                return rel
        return None

    def _has_betrayal_trigger(self, state: SimulationState, character_id: str) -> bool:
        for leverage in state.metadata.get("leverage_registry", {}).values():
            if leverage.get("target_id") == character_id and leverage.get("status") == "active":
                return True
        for obligation in state.metadata.get("obligation_registry", {}).values():
            if obligation.get("promiser_id") == character_id and obligation.get("status") == "active":
                return True
        return False

    def _profile_warnings(self, profile: Dict[str, Any]) -> List[str]:
        warnings = []
        if profile["agency_freedom_score"] < 0.25:
            warnings.append(f"{profile['character_id']} has very low agency freedom")
        if profile["coercion_pressure"] > 0.75:
            warnings.append(f"{profile['character_id']} is under high coercion pressure")
        if profile["choice_complexity"] > 0.8:
            warnings.append(f"{profile['character_id']} has high choice complexity")
        return warnings

    def _ranking_warnings(self, ranked: List[Dict[str, Any]]) -> List[str]:
        warnings = []
        if not ranked:
            warnings.append("no candidate actions were ranked")
        elif ranked[0]["agency_score"] < 0.35:
            warnings.append("all candidate actions have weak agency fit")
        return warnings

    def _recommendation(self, viable: bool, agency_score: float, blockers: List[str], warnings: List[str]) -> str:
        if blockers:
            return "fix_missing_knowledge_resources_or_character_state"
        if not viable:
            return "strengthen_motive_pressure_or_relationship_context"
        if agency_score < 0.45:
            return "allow_only_if_scene_shows_motive_and_pressure"
        return "allow_action"

    def _scene_requirement(self, action_type: str, agency_score: float, profile: Dict[str, Any]) -> str:
        if agency_score < 0.45:
            return f"show clear motive before {action_type}"
        if profile["coercion_pressure"] > 0.55:
            return f"show coercion pressure shaping {action_type}"
        if action_type in {"betray", "confess", "sacrifice", "break_oath"}:
            return f"make {action_type} emotionally costly and causally motivated"
        return "standard causal setup sufficient"

    def _average(self, values: List[float]) -> float:
        if not values:
            return 0.0
        return round(sum(values) / len(values), 3)

    def _bounded(self, value: float) -> float:
        return round(max(0.0, min(1.0, float(value))), 3)

from typing import Any, Dict, List
from uuid import uuid4

from backend.app.engines.base import BaseEngine
from backend.app.schemas.character import CharacterAgentState
from backend.app.schemas.foundation import EngineRunResult


class CharacterAgentStateEngine(BaseEngine):
    """Builds runtime state for a character as a simulation-ready agent.

    Chunk 3 characters are not static cards. They must become stateful agents
    that future chunks can use for relationship simulation, conflict decisions,
    plot movement, emotional continuity, and adaptive behavior.

    This engine creates the central runtime state object used by later systems.
    """

    engine_name = "character.agent_state_engine"

    def run(self, payload: Dict[str, Any]) -> EngineRunResult:
        character_seed = payload.get("character_seed", {})
        world_grounding = payload.get("world_grounding", {})
        people_type = payload.get("people_type", {})
        constraints = payload.get("constraint_checks", [])
        existing_profile = payload.get("character_profile", {})

        warnings: List[str] = []

        if not character_seed and not existing_profile:
            warnings.append("No character_seed or character_profile provided; agent state uses draft defaults.")

        character_id = self._infer_character_id(character_seed, existing_profile)
        name = self._infer_name(character_seed, existing_profile)
        role = self._infer_role(character_seed, existing_profile)
        people_type_id = people_type.get("people_type_id") or people_type.get("id")

        internal_state = self._build_internal_state(character_seed, existing_profile, people_type)
        external_state = self._build_external_state(character_seed, existing_profile, world_grounding)
        social_state = self._build_social_state(character_seed, existing_profile, people_type, world_grounding)
        emotional_state = self._build_emotional_state(character_seed, existing_profile, people_type)
        memory_state = self._build_memory_state(character_seed, existing_profile)
        goal_state = self._build_goal_state(character_seed, existing_profile, people_type)
        moral_state = self._build_moral_state(character_seed, existing_profile)
        skill_state = self._build_skill_state(character_seed, existing_profile)
        destiny_state = self._build_destiny_state(character_seed, existing_profile, world_grounding)
        adaptability_state = self._build_adaptability_state(character_seed, existing_profile, people_type)
        agency_state = self._build_agency_state(
            character_seed=character_seed,
            role=role,
            constraints=constraints,
            goal_state=goal_state,
            emotional_state=emotional_state,
            adaptability_state=adaptability_state,
        )

        simulation_readiness = self._score_simulation_readiness(
            internal_state=internal_state,
            external_state=external_state,
            social_state=social_state,
            emotional_state=emotional_state,
            memory_state=memory_state,
            goal_state=goal_state,
            moral_state=moral_state,
            skill_state=skill_state,
            destiny_state=destiny_state,
            adaptability_state=adaptability_state,
            agency_state=agency_state,
            constraints=constraints,
        )

        agent_state = CharacterAgentState(
            agent_state_id=f"agent_{uuid4().hex[:12]}",
            character_id=character_id,
            internal_state=internal_state,
            external_state=external_state,
            social_state=social_state,
            emotional_state=emotional_state,
            memory_state=memory_state,
            goal_state=goal_state,
            moral_state=moral_state,
            skill_state=skill_state,
            destiny_state=destiny_state,
            adaptability_state=adaptability_state,
            agency_state=agency_state,
            simulation_readiness=simulation_readiness,
        )

        state_diagnostics = self._build_state_diagnostics(agent_state, constraints)

        return self.build_result(
            success=True,
            data={
                "agent_state": agent_state.model_dump(),
                "state_diagnostics": state_diagnostics,
                "character_agent_summary": {
                    "character_id": character_id,
                    "name": name,
                    "role": role,
                    "people_type_id": people_type_id,
                    "simulation_readiness": simulation_readiness,
                    "can_enter_relationship_simulation": simulation_readiness >= 0.65,
                    "can_enter_plot_simulation": simulation_readiness >= 0.75,
                    "requires_revision_before_simulation": simulation_readiness < 0.65,
                },
                "training_notes": [
                    "Agent state is the bridge between character profiles and later relationship/plot simulation.",
                    "Future Chunk 8 models can learn state transitions from curated event-character data.",
                    "Characters should not emotionally reset between scenes; this state object preserves continuity.",
                    "Adaptability state is included so limit-break behavior remains condition/cost/risk/consequence based.",
                ],
            },
            warnings=warnings,
            errors=[],
            generated_object_ids=[agent_state.agent_state_id],
        )

    def _infer_character_id(self, character_seed: Dict[str, Any], existing_profile: Dict[str, Any]) -> str:
        return (
            character_seed.get("character_id")
            or character_seed.get("identity", {}).get("character_id")
            or existing_profile.get("identity", {}).get("character_id")
            or f"char_{uuid4().hex[:12]}"
        )

    def _infer_name(self, character_seed: Dict[str, Any], existing_profile: Dict[str, Any]) -> str:
        return (
            character_seed.get("name")
            or character_seed.get("identity", {}).get("name")
            or existing_profile.get("identity", {}).get("name")
            or "Unnamed Character"
        )

    def _infer_role(self, character_seed: Dict[str, Any], existing_profile: Dict[str, Any]) -> str:
        return (
            character_seed.get("role")
            or character_seed.get("identity", {}).get("role")
            or existing_profile.get("identity", {}).get("role")
            or "draft_character"
        )

    def _get_nested(self, source: Dict[str, Any], section: str, field: str, default: Any = None) -> Any:
        section_data = source.get(section, {})
        if isinstance(section_data, dict):
            return section_data.get(field, default)
        return default

    def _build_internal_state(
        self,
        character_seed: Dict[str, Any],
        existing_profile: Dict[str, Any],
        people_type: Dict[str, Any],
    ) -> Dict[str, Any]:
        core_wound = (
            character_seed.get("core_wound")
            or self._get_nested(existing_profile, "psychology", "core_wound")
            or self._first(people_type.get("likely_wounds"))
            or "unresolved need for identity"
        )

        core_desire = (
            character_seed.get("core_desire")
            or self._get_nested(existing_profile, "psychology", "core_desire")
            or self._first(people_type.get("likely_goals"))
            or "to become more than assigned role"
        )

        core_fear = (
            character_seed.get("core_fear")
            or self._get_nested(existing_profile, "psychology", "core_fear")
            or "being trapped by the system"
        )

        return {
            "core_wound": core_wound,
            "core_desire": core_desire,
            "core_fear": core_fear,
            "core_lie": character_seed.get("core_lie") or self._get_nested(existing_profile, "psychology", "core_lie"),
            "core_truth": character_seed.get("core_truth") or self._get_nested(existing_profile, "psychology", "core_truth"),
            "defense_mechanism": (
                character_seed.get("defense_mechanism")
                or self._get_nested(existing_profile, "psychology", "defense_mechanism")
                or "controlled distance"
            ),
            "private_need": character_seed.get("private_need") or "to be seen accurately",
            "identity_pressure": character_seed.get("identity_pressure") or "must choose between assigned role and private truth",
        }

    def _build_external_state(
        self,
        character_seed: Dict[str, Any],
        existing_profile: Dict[str, Any],
        world_grounding: Dict[str, Any],
    ) -> Dict[str, Any]:
        return {
            "social_class": (
                character_seed.get("social_class")
                or self._get_nested(existing_profile, "origin", "social_class")
                or "unknown"
            ),
            "legal_status": (
                character_seed.get("legal_status")
                or self._get_nested(existing_profile, "identity", "legal_status")
                or "unverified"
            ),
            "public_status": (
                character_seed.get("public_status")
                or self._get_nested(existing_profile, "identity", "public_status")
                or "not yet established"
            ),
            "institution_access": character_seed.get("institution_access")
            or self._get_nested(existing_profile, "origin", "institution_access", []),
            "resource_access": character_seed.get("resource_access")
            or self._get_nested(existing_profile, "origin", "resource_access", []),
            "world_dependency_tags": world_grounding.get("world_dependency_tags", []),
            "active_story_hooks": world_grounding.get("active_story_hooks", []),
        }

    def _build_social_state(
        self,
        character_seed: Dict[str, Any],
        existing_profile: Dict[str, Any],
        people_type: Dict[str, Any],
        world_grounding: Dict[str, Any],
    ) -> Dict[str, Any]:
        return {
            "family_name_status": character_seed.get("family_name_status")
            or self._get_nested(existing_profile, "origin", "family_name_status")
            or "unknown",
            "faction": character_seed.get("faction")
            or self._get_nested(existing_profile, "identity", "faction"),
            "relationship_tendencies": people_type.get("relationship_tendencies", []),
            "trust_triggers": character_seed.get("trust_triggers", ["consistent protection", "truth under pressure"]),
            "betrayal_triggers": character_seed.get("betrayal_triggers", ["public abandonment", "being used as a symbol"]),
            "conflict_style": character_seed.get("conflict_style", "observes first, acts later"),
            "dialogue_style": character_seed.get("dialogue_style", "controlled and specific"),
            "reputation_risk": world_grounding.get("requires_human_review", False),
        }

    def _build_emotional_state(
        self,
        character_seed: Dict[str, Any],
        existing_profile: Dict[str, Any],
        people_type: Dict[str, Any],
    ) -> Dict[str, Any]:
        wounds = people_type.get("likely_wounds", [])
        wound_text = " ".join(wounds).lower()

        shame = 0.55 if "shame" in wound_text or "humiliation" in wound_text or character_seed.get("core_wound") else 0.35
        anger = 0.55 if "injustice" in str(character_seed).lower() else 0.3
        hope = 0.45 if character_seed.get("role") in {"protagonist", "love_interest"} else 0.35
        fear = 0.55 if "erased" in str(character_seed).lower() or "forbidden" in str(character_seed).lower() else 0.35

        return {
            "dominant_emotion": character_seed.get("dominant_emotion") or "controlled tension",
            "baseline": {
                "anger": round(anger, 2),
                "fear": round(fear, 2),
                "hope": round(hope, 2),
                "shame": round(shame, 2),
                "trust": 0.3,
                "purpose": 0.55,
            },
            "current": character_seed.get("current_emotion") or {
                "anger": round(anger, 2),
                "fear": round(fear, 2),
                "hope": round(hope, 2),
                "shame": round(shame, 2),
                "trust": 0.3,
                "purpose": 0.55,
            },
            "volatility": character_seed.get("emotional_volatility", 0.45),
            "suppressed_emotions": character_seed.get("suppressed_emotions", ["fear", "need"]),
            "recovery_rate": character_seed.get("recovery_rate", 0.35),
        }

    def _build_memory_state(
        self,
        character_seed: Dict[str, Any],
        existing_profile: Dict[str, Any],
    ) -> Dict[str, Any]:
        memories = existing_profile.get("memories", []) if isinstance(existing_profile, dict) else []
        seed_memories = character_seed.get("memories", [])

        combined_memories = seed_memories or memories

        return {
            "memory_count": len(combined_memories),
            "core_memory": character_seed.get("core_memory") or "a defining moment has not yet been fully surfaced",
            "trigger_terms": character_seed.get("trigger_terms", ["ranking", "oath", "family name"]),
            "memory_reliability": character_seed.get("memory_reliability", 0.8),
            "behavioral_influence": character_seed.get("memory_behavioral_influence", ["hesitates before public exposure"]),
            "needs_memory_expansion": len(combined_memories) == 0,
        }

    def _build_goal_state(
        self,
        character_seed: Dict[str, Any],
        existing_profile: Dict[str, Any],
        people_type: Dict[str, Any],
    ) -> Dict[str, Any]:
        likely_goals = people_type.get("likely_goals", [])

        return {
            "surface_goal": character_seed.get("surface_goal") or self._first(likely_goals) or "survive the current system",
            "hidden_goal": character_seed.get("hidden_goal") or "prove private worth",
            "true_need": character_seed.get("true_need") or "be loved without performance",
            "goal_conflicts": character_seed.get("goal_conflicts", ["safety versus truth"]),
            "current_priority": character_seed.get("current_priority", 0.65),
            "failure_consequence": character_seed.get("failure_consequence") or "identity wound deepens",
            "agency_driver": character_seed.get("agency_driver") or "acts when someone else is about to be erased",
        }

    def _build_moral_state(
        self,
        character_seed: Dict[str, Any],
        existing_profile: Dict[str, Any],
    ) -> Dict[str, Any]:
        return {
            "compassion": character_seed.get("compassion", 0.65),
            "justice": character_seed.get("justice", 0.7),
            "loyalty": character_seed.get("loyalty", 0.6),
            "ambition": character_seed.get("ambition", 0.55),
            "revenge": character_seed.get("revenge", 0.25),
            "manipulation_tolerance": character_seed.get("manipulation_tolerance", 0.35),
            "violence_tolerance": character_seed.get("violence_tolerance", 0.25),
            "forbidden_lines": character_seed.get("forbidden_lines", ["will not betray someone powerless for status"]),
            "corruption_risk": character_seed.get("corruption_risk", 0.35),
            "redemption_potential": character_seed.get("redemption_potential", 0.65),
        }

    def _build_skill_state(
        self,
        character_seed: Dict[str, Any],
        existing_profile: Dict[str, Any],
    ) -> Dict[str, Any]:
        skill_rarity = character_seed.get("skill_rarity", "common")

        return {
            "primary_skill": character_seed.get("primary_skill") or "pattern reading",
            "skill_domain": character_seed.get("skill_domain") or "observation",
            "skill_rank": character_seed.get("skill_rank") or character_seed.get("rank") or "C",
            "skill_rarity": skill_rarity,
            "mastery": character_seed.get("mastery", 0.45),
            "skill_cost": character_seed.get("skill_cost"),
            "limitation": character_seed.get("limitation"),
            "counter": character_seed.get("counter"),
            "needs_cost_if_rare": str(skill_rarity).lower() in {"rare", "elite", "legendary", "mythic", "anomaly", "s", "ss", "sss"},
        }

    def _build_destiny_state(
        self,
        character_seed: Dict[str, Any],
        existing_profile: Dict[str, Any],
        world_grounding: Dict[str, Any],
    ) -> Dict[str, Any]:
        destiny_type = character_seed.get("destiny_type")

        return {
            "destiny_type": destiny_type,
            "destiny_active": bool(destiny_type),
            "destiny_score": character_seed.get("destiny_score", 0.0 if not destiny_type else 0.65),
            "visibility": character_seed.get("destiny_visibility", "hidden"),
            "burden": character_seed.get("destiny_burden"),
            "failure_condition": character_seed.get("destiny_failure_condition"),
            "world_dependency_tags": world_grounding.get("world_dependency_tags", []),
            "destiny_requires_cost": bool(destiny_type),
        }

    def _build_adaptability_state(
        self,
        character_seed: Dict[str, Any],
        existing_profile: Dict[str, Any],
        people_type: Dict[str, Any],
    ) -> Dict[str, Any]:
        people_text = str(people_type).lower()
        seed_text = str(character_seed).lower()

        has_limit_break = (
            "limit_break" in seed_text
            or "limit-break" in seed_text
            or "limit_break" in people_text
            or "limit-break" in people_text
            or character_seed.get("adaptability_type") is not None
        )

        return {
            "adaptability_score": character_seed.get("adaptability_score", 0.55 if not has_limit_break else 0.82),
            "limit_break_potential": character_seed.get("limit_break_potential", 0.2 if not has_limit_break else 0.78),
            "has_limit_break_concept": has_limit_break,
            "breakthrough_condition": character_seed.get("breakthrough_condition"),
            "adaptation_cost": character_seed.get("adaptation_cost"),
            "adaptation_risk": character_seed.get("adaptation_risk"),
            "post_break_consequence": character_seed.get("post_break_consequence"),
            "domains": character_seed.get("adaptation_domains", ["emotional", "social"]),
            "limit_break_locked": has_limit_break and not all(
                character_seed.get(key)
                for key in [
                    "breakthrough_condition",
                    "adaptation_cost",
                    "adaptation_risk",
                    "post_break_consequence",
                ]
            ),
            "rule": "No limit-break without condition, cost, risk, and consequence.",
        }

    def _build_agency_state(
        self,
        *,
        character_seed: Dict[str, Any],
        role: str,
        constraints: List[Dict[str, Any]],
        goal_state: Dict[str, Any],
        emotional_state: Dict[str, Any],
        adaptability_state: Dict[str, Any],
    ) -> Dict[str, Any]:
        violation_count = sum(1 for check in constraints if check.get("status") == "violation")
        agency_score = 0.55

        if role in {"protagonist", "deuteragonist", "villain", "antagonist"}:
            agency_score += 0.15

        if goal_state.get("surface_goal") and goal_state.get("hidden_goal"):
            agency_score += 0.1

        if adaptability_state.get("has_limit_break_concept") and not adaptability_state.get("limit_break_locked"):
            agency_score += 0.08

        agency_score -= violation_count * 0.12
        agency_score = max(0.0, min(1.0, agency_score))

        return {
            "agency_score": round(agency_score, 3),
            "choice_style": character_seed.get("choice_style", "delayed but decisive under moral pressure"),
            "decision_triggers": character_seed.get("decision_triggers", ["injustice against weaker person", "truth about family status"]),
            "avoidance_pattern": character_seed.get("avoidance_pattern", "avoids public exposure until forced"),
            "action_threshold": character_seed.get("action_threshold", 0.65),
            "can_initiate_plot": agency_score >= 0.65,
            "can_resist_pressure": emotional_state.get("baseline", {}).get("purpose", 0.0) >= 0.5,
            "constraint_violations_affecting_agency": violation_count,
        }

    def _score_simulation_readiness(
        self,
        *,
        internal_state: Dict[str, Any],
        external_state: Dict[str, Any],
        social_state: Dict[str, Any],
        emotional_state: Dict[str, Any],
        memory_state: Dict[str, Any],
        goal_state: Dict[str, Any],
        moral_state: Dict[str, Any],
        skill_state: Dict[str, Any],
        destiny_state: Dict[str, Any],
        adaptability_state: Dict[str, Any],
        agency_state: Dict[str, Any],
        constraints: List[Dict[str, Any]],
    ) -> float:
        score = 0.0

        score += 0.1 if internal_state.get("core_wound") else 0.0
        score += 0.1 if internal_state.get("core_desire") else 0.0
        score += 0.08 if external_state.get("social_class") != "unknown" else 0.0
        score += 0.08 if social_state.get("conflict_style") else 0.0
        score += 0.1 if emotional_state.get("baseline") else 0.0
        score += 0.08 if memory_state.get("trigger_terms") else 0.0
        score += 0.1 if goal_state.get("surface_goal") and goal_state.get("hidden_goal") else 0.0
        score += 0.08 if moral_state.get("forbidden_lines") else 0.0
        score += 0.08 if skill_state.get("primary_skill") else 0.0
        score += 0.06 if "destiny_type" in destiny_state else 0.0
        score += 0.08 if adaptability_state.get("adaptability_score", 0.0) > 0.0 else 0.0
        score += 0.1 * agency_state.get("agency_score", 0.0)

        violation_count = sum(1 for check in constraints if check.get("status") == "violation")
        needs_detail_count = sum(1 for check in constraints if check.get("status") == "needs_detail")

        score -= violation_count * 0.08
        score -= needs_detail_count * 0.03

        if adaptability_state.get("limit_break_locked"):
            score -= 0.06

        return round(max(0.0, min(1.0, score)), 3)

    def _build_state_diagnostics(
        self,
        agent_state: CharacterAgentState,
        constraints: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        missing_sections = []

        for section_name in [
            "internal_state",
            "external_state",
            "social_state",
            "emotional_state",
            "memory_state",
            "goal_state",
            "moral_state",
            "skill_state",
            "adaptability_state",
            "agency_state",
        ]:
            if not getattr(agent_state, section_name):
                missing_sections.append(section_name)

        violation_checks = [
            check["check_id"]
            for check in constraints
            if check.get("status") == "violation"
        ]

        return {
            "missing_sections": missing_sections,
            "constraint_violations": violation_checks,
            "limit_break_locked": agent_state.adaptability_state.get("limit_break_locked", False),
            "agency_score": agent_state.agency_state.get("agency_score"),
            "simulation_readiness": agent_state.simulation_readiness,
            "readiness_tier": self._readiness_tier(agent_state.simulation_readiness),
            "next_recommended_step": (
                "advance_to_character_genesis"
                if agent_state.simulation_readiness >= 0.65 and not violation_checks
                else "repair_character_state_before_simulation"
            ),
        }

    def _readiness_tier(self, score: float) -> str:
        if score >= 0.85:
            return "simulation_ready"
        if score >= 0.65:
            return "usable_with_minor_gaps"
        if score >= 0.4:
            return "needs_state_expansion"
        return "insufficient_agent_state"

    def _first(self, values: Any) -> Any:
        if isinstance(values, list) and values:
            return values[0]
        return None

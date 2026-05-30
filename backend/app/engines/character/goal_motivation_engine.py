from typing import Any, Dict, List
from uuid import uuid4

from backend.app.engines.base import BaseEngine
from backend.app.schemas.foundation import EngineRunResult


class GoalMotivationEngine(BaseEngine):
    """Builds goal, motivation, need, and agency logic for a character.

    This engine separates:
    - surface goal
    - hidden goal
    - false need
    - true need
    - stakes
    - sacrifices
    - blockers
    - escalation rules
    - relationship/plot hooks

    It prepares characters to move story instead of simply existing inside it.
    """

    engine_name = "character.goal_motivation_engine"

    def run(self, payload: Dict[str, Any]) -> EngineRunResult:
        character_seed = payload.get("character_seed", {})
        psychology_profile = payload.get("psychology_profile") or character_seed.get("psychology", {})
        emotional_arc_profile = payload.get("emotional_arc_profile") or character_seed.get("emotional_arc", {})
        memory_records = payload.get("memory_records") or character_seed.get("memories", [])
        reputation_profile = payload.get("reputation_profile") or character_seed.get("reputation", {})
        consequence_hooks = payload.get("consequence_hooks") or character_seed.get("reputation_consequence_hooks", [])
        world_grounding = payload.get("world_grounding", {})

        warnings: List[str] = []

        if not character_seed:
            warnings.append("No character_seed provided; goal engine used draft defaults.")

        character_id = (
            character_seed.get("character_id")
            or psychology_profile.get("character_id")
            or reputation_profile.get("character_id")
            or f"char_{uuid4().hex[:12]}"
        )

        goal_profile = self._build_goal_profile(
            character_id=character_id,
            character_seed=character_seed,
            psychology_profile=psychology_profile,
            emotional_arc_profile=emotional_arc_profile,
            memory_records=memory_records,
            reputation_profile=reputation_profile,
            consequence_hooks=consequence_hooks,
            world_grounding=world_grounding,
        )

        motivation_stack = self._build_motivation_stack(
            goal_profile=goal_profile,
            psychology_profile=psychology_profile,
            memory_records=memory_records,
            reputation_profile=reputation_profile,
        )

        agency_rules = self._build_agency_rules(
            goal_profile=goal_profile,
            character_seed=character_seed,
            psychology_profile=psychology_profile,
            emotional_arc_profile=emotional_arc_profile,
        )

        conflict_hooks = self._build_conflict_hooks(
            goal_profile=goal_profile,
            motivation_stack=motivation_stack,
            reputation_profile=reputation_profile,
            consequence_hooks=consequence_hooks,
        )

        goal_diagnostics = self._build_diagnostics(goal_profile, motivation_stack, agency_rules, conflict_hooks)

        next_engine_payload = self._build_next_engine_payload(
            character_seed=character_seed,
            goal_profile=goal_profile,
            motivation_stack=motivation_stack,
            agency_rules=agency_rules,
            conflict_hooks=conflict_hooks,
        )

        return self.build_result(
            success=True,
            data={
                "goal_profile": goal_profile,
                "motivation_stack": motivation_stack,
                "agency_rules": agency_rules,
                "conflict_hooks": conflict_hooks,
                "goal_diagnostics": goal_diagnostics,
                "next_engine_payload": next_engine_payload,
                "goal_summary": {
                    "character_id": character_id,
                    "surface_goal": goal_profile["surface_goal"],
                    "hidden_goal": goal_profile["hidden_goal"],
                    "true_need": goal_profile["true_need"],
                    "primary_stake": goal_profile["primary_stake"],
                    "agency_score": goal_profile["agency_score"],
                    "goal_conflict_count": len(goal_profile["goal_conflicts"]),
                    "has_escalation_logic": len(agency_rules["escalation_rules"]) > 0,
                    "ready_for_moral_engine": True,
                    "ready_for_skill_engine": True,
                    "ready_for_plot_engine_later": True,
                },
                "training_notes": [
                    "Goals must create decisions, sacrifices, and consequences.",
                    "Surface goal and true need should often conflict for stronger drama.",
                    "Agency rules prevent characters from becoming passive lore containers.",
                    "Future Chunk 8 can learn goal-shift models from curated character arc data.",
                ],
            },
            warnings=warnings,
            errors=[],
            generated_object_ids=[goal_profile["goal_profile_id"]],
        )

    def _build_goal_profile(
        self,
        *,
        character_id: str,
        character_seed: Dict[str, Any],
        psychology_profile: Dict[str, Any],
        emotional_arc_profile: Dict[str, Any],
        memory_records: List[Dict[str, Any]],
        reputation_profile: Dict[str, Any],
        consequence_hooks: List[Dict[str, Any]],
        world_grounding: Dict[str, Any],
    ) -> Dict[str, Any]:
        surface_goal = self._surface_goal(character_seed, psychology_profile, reputation_profile)
        hidden_goal = self._hidden_goal(character_seed, psychology_profile, memory_records)
        false_need = self._false_need(psychology_profile, character_seed)
        true_need = self._true_need(psychology_profile, character_seed)
        primary_stake = self._primary_stake(character_seed, reputation_profile, consequence_hooks)
        external_blockers = self._external_blockers(character_seed, reputation_profile, world_grounding)
        internal_blockers = self._internal_blockers(psychology_profile, character_seed)
        sacrifices = self._sacrifices(character_seed, psychology_profile, reputation_profile)
        goal_conflicts = self._goal_conflicts(surface_goal, hidden_goal, false_need, true_need, character_seed)
        agency_score = self._agency_score(surface_goal, hidden_goal, true_need, external_blockers, internal_blockers, character_seed)

        return {
            "goal_profile_id": f"goal_{uuid4().hex[:12]}",
            "character_id": character_id,
            "surface_goal": surface_goal,
            "hidden_goal": hidden_goal,
            "false_need": false_need,
            "true_need": true_need,
            "primary_stake": primary_stake,
            "external_blockers": external_blockers,
            "internal_blockers": internal_blockers,
            "sacrifices_required": sacrifices,
            "goal_conflicts": goal_conflicts,
            "failure_consequence": self._failure_consequence(character_seed, psychology_profile, reputation_profile),
            "success_cost": self._success_cost(character_seed, psychology_profile, reputation_profile),
            "choice_pressure": self._choice_pressure(character_seed, psychology_profile, emotional_arc_profile),
            "agency_score": agency_score,
            "plot_function": self._plot_function(character_seed, surface_goal, hidden_goal),
            "relationship_goal_effects": self._relationship_goal_effects(character_seed, psychology_profile),
            "world_goal_dependencies": world_grounding.get("world_dependency_tags", []),
        }

    def _surface_goal(self, seed: Dict[str, Any], psychology: Dict[str, Any], reputation: Dict[str, Any]) -> str:
        if seed.get("surface_goal"):
            return seed["surface_goal"]

        role = seed.get("role", "")

        if role == "villain":
            return "preserve the system that gives them authority"

        if role == "love_interest":
            return "complete their own mission without becoming someone else's reward"

        if role == "rival":
            return "prove they cannot be replaced"

        if seed.get("destiny_type"):
            return "understand why destiny has marked them"

        if reputation.get("exposure_risk", 0.0) >= 0.55:
            return "avoid exposure while gaining enough power to survive"

        return "survive the current pressure without losing selfhood"

    def _hidden_goal(self, seed: Dict[str, Any], psychology: Dict[str, Any], memories: List[Dict[str, Any]]) -> str:
        if seed.get("hidden_goal"):
            return seed["hidden_goal"]

        if psychology.get("core_desire"):
            return psychology["core_desire"]

        if any("family secret" in str(memory).lower() for memory in memories):
            return "make the family truth safe enough to be known"

        return "be seen accurately without needing to perform worth"

    def _false_need(self, psychology: Dict[str, Any], seed: Dict[str, Any]) -> str:
        if seed.get("false_need"):
            return seed["false_need"]

        lie = psychology.get("core_lie")

        if lie:
            return lie

        if seed.get("family_name_status") in {"distrusted", "erased", "unknown"}:
            return "must earn official recognition before truth matters"

        if seed.get("role") == "villain":
            return "must control others to keep the world safe"

        return "must stay useful to stay safe"

    def _true_need(self, psychology: Dict[str, Any], seed: Dict[str, Any]) -> str:
        if seed.get("true_need"):
            return seed["true_need"]

        truth = psychology.get("core_truth")

        if truth:
            return truth

        if seed.get("role") == "villain":
            return "accept accountability before control becomes identity"

        return "be seen without performance"

    def _primary_stake(
        self,
        seed: Dict[str, Any],
        reputation: Dict[str, Any],
        consequence_hooks: List[Dict[str, Any]],
    ) -> str:
        if seed.get("primary_stake"):
            return seed["primary_stake"]

        if consequence_hooks:
            hook_type = consequence_hooks[0].get("hook_type", "social consequence")
            return f"risk of {hook_type} changing their access, safety, or identity"

        if reputation.get("exposure_risk", 0.0) >= 0.55:
            return "public exposure could destroy safety, trust, or institutional access"

        if seed.get("breakthrough_condition"):
            return "failure to act may let someone weaker be harmed"

        return "failure means the old wound becomes more true"

    def _external_blockers(
        self,
        seed: Dict[str, Any],
        reputation: Dict[str, Any],
        world_grounding: Dict[str, Any],
    ) -> List[str]:
        blockers = []

        if reputation.get("institutional_reputation", 1.0) <= 0.35:
            blockers.append("institutions do not trust them")

        if reputation.get("exposure_risk", 0.0) >= 0.55:
            blockers.append("public exposure risk")

        if "academy_gatekeeping" in world_grounding.get("world_dependency_tags", []):
            blockers.append("academy gatekeeping")

        if "family_name_legal_trust" in world_grounding.get("world_dependency_tags", []):
            blockers.append("family-name legal trust system")

        if seed.get("family_name_status") in {"distrusted", "erased", "unknown"}:
            blockers.append("low-trust family name")

        if seed.get("family", {}).get("family_debt"):
            blockers.append("family debt")

        if not blockers:
            blockers.append("social expectation and limited information")

        return sorted(set(blockers))

    def _internal_blockers(self, psychology: Dict[str, Any], seed: Dict[str, Any]) -> List[str]:
        blockers = []

        if psychology.get("core_fear"):
            blockers.append(psychology["core_fear"])

        if psychology.get("defense_mechanism"):
            blockers.append(f"defense mechanism: {psychology['defense_mechanism']}")

        if psychology.get("shame_trigger"):
            blockers.append(f"shame trigger: {psychology['shame_trigger']}")

        if seed.get("adaptation_cost"):
            blockers.append(f"adaptation cost: {seed['adaptation_cost']}")

        if not blockers:
            blockers.append("fear of being misread")

        return blockers

    def _sacrifices(self, seed: Dict[str, Any], psychology: Dict[str, Any], reputation: Dict[str, Any]) -> List[str]:
        sacrifices = []

        if reputation.get("exposure_risk", 0.0) >= 0.55:
            sacrifices.append("safe anonymity")

        if psychology.get("healing_condition"):
            sacrifices.append("control over disclosure timing")

        if seed.get("breakthrough_condition"):
            sacrifices.append("comfort of staying passive during injustice")

        if seed.get("role") == "villain":
            sacrifices.append("belief that authority equals goodness")

        if seed.get("family", {}).get("inherited_obligations"):
            sacrifices.append("family approval")

        if not sacrifices:
            sacrifices.append("old defense mechanism")

        return sacrifices

    def _goal_conflicts(
        self,
        surface_goal: str,
        hidden_goal: str,
        false_need: str,
        true_need: str,
        seed: Dict[str, Any],
    ) -> List[str]:
        conflicts = [
            f"Surface goal conflicts with hidden goal: {surface_goal} vs {hidden_goal}.",
            f"False need conflicts with true need: {false_need} vs {true_need}.",
        ]

        if seed.get("breakthrough_condition"):
            conflicts.append("Safety conflicts with acting when a weaker person is threatened.")

        if seed.get("family_name_status") in {"distrusted", "erased", "unknown"}:
            conflicts.append("Truth conflicts with whether institutions will believe them.")

        if seed.get("role") == "love_interest":
            conflicts.append("Romance conflicts with independent agency.")

        if seed.get("role") == "villain":
            conflicts.append("Order conflicts with mercy.")

        return conflicts

    def _failure_consequence(
        self,
        seed: Dict[str, Any],
        psychology: Dict[str, Any],
        reputation: Dict[str, Any],
    ) -> str:
        if seed.get("failure_consequence"):
            return seed["failure_consequence"]

        if reputation.get("exposure_risk", 0.0) >= 0.55:
            return "exposure confirms the public label they fear most"

        if psychology.get("core_lie"):
            return f"failure strengthens the lie: {psychology['core_lie']}"

        return "the old wound becomes harder to challenge"

    def _success_cost(
        self,
        seed: Dict[str, Any],
        psychology: Dict[str, Any],
        reputation: Dict[str, Any],
    ) -> str:
        if seed.get("success_cost"):
            return seed["success_cost"]

        if seed.get("adaptation_cost"):
            return seed["adaptation_cost"]

        if reputation.get("enemy_threat_reputation", 0.0) >= 0.55:
            return "success attracts enemy attention"

        if psychology.get("healing_condition"):
            return "success requires vulnerability instead of performance"

        return "success makes the character more visible"

    def _choice_pressure(
        self,
        seed: Dict[str, Any],
        psychology: Dict[str, Any],
        arc: Dict[str, Any],
    ) -> str:
        if seed.get("breakthrough_condition"):
            return f"Choice pressure peaks when: {seed['breakthrough_condition']}"

        if arc.get("emotional_climax"):
            return arc["emotional_climax"]

        if psychology.get("corruption_condition"):
            return psychology["corruption_condition"]

        return "must choose between safety and truth"

    def _agency_score(
        self,
        surface_goal: str,
        hidden_goal: str,
        true_need: str,
        external_blockers: List[str],
        internal_blockers: List[str],
        seed: Dict[str, Any],
    ) -> float:
        score = 0.45

        if surface_goal:
            score += 0.12

        if hidden_goal:
            score += 0.12

        if true_need:
            score += 0.1

        if seed.get("role") in {"protagonist", "deuteragonist", "villain", "rival"}:
            score += 0.1

        if seed.get("breakthrough_condition"):
            score += 0.08

        score -= min(0.16, len(external_blockers) * 0.02)
        score -= min(0.12, len(internal_blockers) * 0.02)

        return self._clamp(score)

    def _plot_function(self, seed: Dict[str, Any], surface_goal: str, hidden_goal: str) -> str:
        role = seed.get("role", "")

        if role == "protagonist":
            return "drives the main emotional and causal story through active choices"

        if role == "villain":
            return "forces the story to define what order costs"

        if role == "rival":
            return "externalizes the protagonist's fear of replacement or failure"

        if role == "love_interest":
            return "tests whether intimacy can coexist with independent agency"

        return "adds pressure, witness, contrast, or consequence to the story"

    def _relationship_goal_effects(self, seed: Dict[str, Any], psychology: Dict[str, Any]) -> Dict[str, str]:
        return {
            "friendship": "tests whether support is accepted without debt",
            "romance": psychology.get("love_response", "tests whether vulnerability can survive conflict"),
            "rivalry": "turns comparison into either growth or obsession",
            "betrayal": psychology.get("betrayal_response", "withdraws trust and remembers the exact wound"),
            "mentorship": "tests whether guidance becomes control or liberation",
        }

    def _build_motivation_stack(
        self,
        *,
        goal_profile: Dict[str, Any],
        psychology_profile: Dict[str, Any],
        memory_records: List[Dict[str, Any]],
        reputation_profile: Dict[str, Any],
    ) -> Dict[str, Any]:
        memory_drivers = [
            {
                "memory_id": record.get("memory_id"),
                "weight": record.get("emotional_weight", 0.0),
                "influence": record.get("behavioral_influence", []),
            }
            for record in sorted(
                memory_records,
                key=lambda item: item.get("emotional_weight", 0.0),
                reverse=True,
            )[:5]
        ]

        return {
            "primary_motivation": goal_profile["hidden_goal"],
            "secondary_motivation": goal_profile["surface_goal"],
            "fear_motivation": psychology_profile.get("core_fear") or "avoid becoming the old wound",
            "shame_motivation": psychology_profile.get("shame_trigger") or "avoid public misreading",
            "reputation_motivation": self._reputation_motivation(reputation_profile),
            "memory_drivers": memory_drivers,
            "need_hierarchy": [
                goal_profile["false_need"],
                goal_profile["surface_goal"],
                goal_profile["hidden_goal"],
                goal_profile["true_need"],
            ],
            "motivation_conflict": "the character wants safety but needs truth",
        }

    def _reputation_motivation(self, reputation: Dict[str, Any]) -> str:
        if reputation.get("exposure_risk", 0.0) >= 0.55:
            return "avoid exposure while shaping public interpretation"

        if reputation.get("institutional_reputation", 1.0) <= 0.35:
            return "gain enough proof to be believed"

        if reputation.get("enemy_threat_reputation", 0.0) >= 0.55:
            return "stay ahead of enemies who now recognize threat"

        return "be known accurately by the right audience"

    def _build_agency_rules(
        self,
        *,
        goal_profile: Dict[str, Any],
        character_seed: Dict[str, Any],
        psychology_profile: Dict[str, Any],
        emotional_arc_profile: Dict[str, Any],
    ) -> Dict[str, Any]:
        escalation_rules = [
            {
                "condition": "external blocker prevents surface goal",
                "response": "use indirect strategy before direct confrontation",
            },
            {
                "condition": "hidden goal is threatened",
                "response": "risk reputation or safety to preserve truth",
            },
            {
                "condition": "false need is rewarded",
                "response": "short-term success increases long-term emotional cost",
            },
            {
                "condition": "true need becomes visible",
                "response": "character hesitates, then chooses vulnerability if trust has been earned",
            },
        ]

        if character_seed.get("breakthrough_condition"):
            escalation_rules.append(
                {
                    "condition": character_seed["breakthrough_condition"],
                    "response": "adaptability or limit-break pressure activates only with cost and consequence",
                }
            )

        return {
            "can_initiate_plot": goal_profile["agency_score"] >= 0.6,
            "can_resist_plot": len(goal_profile["internal_blockers"]) <= 4,
            "can_escalate_conflict": True,
            "escalation_rules": escalation_rules,
            "decision_style": self._decision_style(character_seed, psychology_profile),
            "risk_tolerance": self._risk_tolerance(character_seed, goal_profile),
            "agency_failure_mode": self._agency_failure_mode(psychology_profile, character_seed),
            "agency_growth_condition": goal_profile["true_need"],
        }

    def _decision_style(self, seed: Dict[str, Any], psychology: Dict[str, Any]) -> str:
        if seed.get("role") == "villain":
            return "decides through control, order, and institutional leverage"

        if "controlled" in str(psychology).lower():
            return "observes first, acts precisely when moral threshold is crossed"

        if seed.get("breakthrough_condition"):
            return "avoids escalation until someone vulnerable is threatened"

        return "delays action until the emotional cost of inaction becomes too high"

    def _risk_tolerance(self, seed: Dict[str, Any], goal_profile: Dict[str, Any]) -> float:
        score = 0.35

        if seed.get("role") in {"protagonist", "villain", "rival"}:
            score += 0.15

        if seed.get("breakthrough_condition"):
            score += 0.15

        if "safe anonymity" in goal_profile.get("sacrifices_required", []):
            score -= 0.05

        if seed.get("destiny_type"):
            score += 0.08

        return self._clamp(score)

    def _agency_failure_mode(self, psychology: Dict[str, Any], seed: Dict[str, Any]) -> str:
        if seed.get("role") == "villain":
            return "mistakes control for moral clarity"

        if psychology.get("defense_mechanism"):
            return f"retreats into defense mechanism: {psychology['defense_mechanism']}"

        return "becomes passive until forced by consequence"

    def _build_conflict_hooks(
        self,
        *,
        goal_profile: Dict[str, Any],
        motivation_stack: Dict[str, Any],
        reputation_profile: Dict[str, Any],
        consequence_hooks: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        hooks = []

        hooks.append(
            {
                "hook_type": "want_vs_need",
                "description": f"{goal_profile['surface_goal']} conflicts with {goal_profile['true_need']}.",
                "story_use": "core internal arc",
            }
        )

        if reputation_profile.get("exposure_risk", 0.0) >= 0.55:
            hooks.append(
                {
                    "hook_type": "goal_vs_exposure",
                    "description": "Pursuing the goal increases exposure risk.",
                    "story_use": "social consequence escalation",
                }
            )

        if goal_profile.get("choice_pressure"):
            hooks.append(
                {
                    "hook_type": "choice_pressure",
                    "description": goal_profile["choice_pressure"],
                    "story_use": "midpoint or climax decision",
                }
            )

        for hook in consequence_hooks[:2]:
            hooks.append(
                {
                    "hook_type": f"reputation_{hook.get('hook_type', 'consequence')}",
                    "description": hook.get("description", "Reputation consequence affects goal."),
                    "story_use": hook.get("story_use", "social pressure"),
                }
            )

        return hooks

    def _build_diagnostics(
        self,
        goal_profile: Dict[str, Any],
        motivation_stack: Dict[str, Any],
        agency_rules: Dict[str, Any],
        conflict_hooks: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        completeness = sum(
            [
                bool(goal_profile["surface_goal"]),
                bool(goal_profile["hidden_goal"]),
                bool(goal_profile["false_need"]),
                bool(goal_profile["true_need"]),
                bool(goal_profile["primary_stake"]),
                bool(goal_profile["failure_consequence"]),
                bool(goal_profile["success_cost"]),
                len(goal_profile["goal_conflicts"]) > 0,
                len(agency_rules["escalation_rules"]) > 0,
                len(conflict_hooks) > 0,
            ]
        ) / 10

        return {
            "goal_completeness_score": round(completeness, 3),
            "has_want_need_split": goal_profile["surface_goal"] != goal_profile["true_need"],
            "has_false_true_need_split": goal_profile["false_need"] != goal_profile["true_need"],
            "has_external_blockers": len(goal_profile["external_blockers"]) > 0,
            "has_internal_blockers": len(goal_profile["internal_blockers"]) > 0,
            "has_sacrifices": len(goal_profile["sacrifices_required"]) > 0,
            "has_escalation_rules": len(agency_rules["escalation_rules"]) > 0,
            "has_conflict_hooks": len(conflict_hooks) > 0,
            "agency_ready": goal_profile["agency_score"] >= 0.6,
            "plot_ready": completeness >= 0.85 and len(conflict_hooks) > 0,
        }

    def _build_next_engine_payload(
        self,
        *,
        character_seed: Dict[str, Any],
        goal_profile: Dict[str, Any],
        motivation_stack: Dict[str, Any],
        agency_rules: Dict[str, Any],
        conflict_hooks: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        merged_seed = dict(character_seed)
        merged_seed["goal_profile"] = goal_profile
        merged_seed["motivation_stack"] = motivation_stack
        merged_seed["agency_rules"] = agency_rules
        merged_seed["goal_conflict_hooks"] = conflict_hooks

        return {
            "character_seed": merged_seed,
            "moral_engine_payload": {
                "character_seed": merged_seed,
                "goal_profile": goal_profile,
                "motivation_stack": motivation_stack,
                "agency_rules": agency_rules,
            },
            "skill_engine_payload": {
                "character_seed": merged_seed,
                "goal_profile": goal_profile,
                "agency_rules": agency_rules,
            },
            "adaptability_engine_payload": {
                "character_seed": merged_seed,
                "goal_profile": goal_profile,
                "agency_rules": agency_rules,
                "conflict_hooks": conflict_hooks,
            },
            "plot_engine_payload_later": {
                "character_id": goal_profile["character_id"],
                "goal_profile": goal_profile,
                "agency_rules": agency_rules,
                "conflict_hooks": conflict_hooks,
            },
        }

    def _clamp(self, value: float) -> float:
        return round(max(0.0, min(1.0, value)), 3)

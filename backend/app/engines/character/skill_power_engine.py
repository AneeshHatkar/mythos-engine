from typing import Any, Dict, List
from uuid import uuid4

from backend.app.engines.base import BaseEngine
from backend.app.schemas.foundation import EngineRunResult


class SkillPowerEngine(BaseEngine):
    """Builds skill, ability, power, limitation, training, and counterplay logic.

    MythOS abilities should never be unlimited. Every skill/power must have:
    - domain
    - rank
    - rarity
    - cost
    - limitation
    - counterplay
    - training path
    - misuse risk
    - narrative function
    - relationship/social consequences

    This engine prepares the character for adaptability, destiny, conflict, and plot simulation.
    """

    engine_name = "character.skill_power_engine"

    def run(self, payload: Dict[str, Any]) -> EngineRunResult:
        character_seed = payload.get("character_seed", {})
        goal_profile = payload.get("goal_profile") or character_seed.get("goal_profile", {})
        moral_profile = payload.get("moral_profile") or character_seed.get("moral_profile", {})
        dilemma_matrix = payload.get("dilemma_matrix") or character_seed.get("dilemma_matrix", {})
        agency_rules = payload.get("agency_rules") or character_seed.get("agency_rules", {})
        world_grounding = payload.get("world_grounding", {})
        world_constraints = payload.get("world_constraints", {})

        warnings: List[str] = []

        if not character_seed:
            warnings.append("No character_seed provided; skill engine used draft defaults.")

        character_id = (
            character_seed.get("character_id")
            or goal_profile.get("character_id")
            or moral_profile.get("character_id")
            or f"char_{uuid4().hex[:12]}"
        )

        skill_profile = self._build_skill_profile(
            character_id=character_id,
            character_seed=character_seed,
            goal_profile=goal_profile,
            moral_profile=moral_profile,
            world_grounding=world_grounding,
            world_constraints=world_constraints,
        )

        power_limits = self._build_power_limits(
            skill_profile=skill_profile,
            character_seed=character_seed,
            moral_profile=moral_profile,
            world_constraints=world_constraints,
        )

        training_path = self._build_training_path(
            skill_profile=skill_profile,
            power_limits=power_limits,
            character_seed=character_seed,
            goal_profile=goal_profile,
        )

        counterplay_matrix = self._build_counterplay_matrix(
            skill_profile=skill_profile,
            power_limits=power_limits,
            moral_profile=moral_profile,
            dilemma_matrix=dilemma_matrix,
        )

        ability_diagnostics = self._build_diagnostics(
            skill_profile=skill_profile,
            power_limits=power_limits,
            training_path=training_path,
            counterplay_matrix=counterplay_matrix,
        )

        next_engine_payload = self._build_next_engine_payload(
            character_seed=character_seed,
            skill_profile=skill_profile,
            power_limits=power_limits,
            training_path=training_path,
            counterplay_matrix=counterplay_matrix,
        )

        return self.build_result(
            success=True,
            data={
                "skill_profile": skill_profile,
                "power_limits": power_limits,
                "training_path": training_path,
                "counterplay_matrix": counterplay_matrix,
                "ability_diagnostics": ability_diagnostics,
                "next_engine_payload": next_engine_payload,
                "skill_summary": {
                    "character_id": character_id,
                    "primary_skill": skill_profile["primary_skill"],
                    "skill_domain": skill_profile["skill_domain"],
                    "skill_rank": skill_profile["skill_rank"],
                    "skill_rarity": skill_profile["skill_rarity"],
                    "mastery_score": skill_profile["mastery_score"],
                    "has_cost": bool(power_limits["costs"]),
                    "has_counterplay": bool(counterplay_matrix["direct_counters"]),
                    "has_training_path": bool(training_path["training_stages"]),
                    "ready_for_adaptability_engine": True,
                    "ready_for_destiny_engine": True,
                    "ready_for_conflict_simulation_later": True,
                },
                "training_notes": [
                    "Ability design must preserve limits, cost, counterplay, and training logic.",
                    "Rare skills should create social and moral consequences, not just power fantasy.",
                    "Skill growth is designed as staged progression for plot and relationship beats.",
                    "Future Chunk 8 can learn ability-balancing patterns from curated ability/outcome data.",
                ],
            },
            warnings=warnings,
            errors=[],
            generated_object_ids=[skill_profile["skill_profile_id"]],
        )

    def _build_skill_profile(
        self,
        *,
        character_id: str,
        character_seed: Dict[str, Any],
        goal_profile: Dict[str, Any],
        moral_profile: Dict[str, Any],
        world_grounding: Dict[str, Any],
        world_constraints: Dict[str, Any],
    ) -> Dict[str, Any]:
        primary_skill = self._primary_skill(character_seed)
        skill_domain = self._skill_domain(character_seed, primary_skill)
        skill_rank = self._skill_rank(character_seed)
        skill_rarity = self._skill_rarity(character_seed, skill_rank)

        return {
            "skill_profile_id": f"skill_{uuid4().hex[:12]}",
            "character_id": character_id,
            "primary_skill": primary_skill,
            "secondary_skills": self._secondary_skills(character_seed, skill_domain),
            "skill_domain": skill_domain,
            "skill_rank": skill_rank,
            "skill_rarity": skill_rarity,
            "mastery_score": self._mastery_score(skill_rank, skill_rarity, character_seed),
            "raw_potential_score": self._raw_potential_score(skill_rank, skill_rarity, character_seed),
            "control_score": self._control_score(character_seed, moral_profile),
            "growth_ceiling": self._growth_ceiling(skill_rarity, character_seed),
            "narrative_function": self._narrative_function(character_seed, goal_profile, primary_skill),
            "world_legality": self._world_legality(character_seed, skill_domain, world_constraints),
            "social_visibility": self._social_visibility(character_seed, skill_rarity, world_grounding),
            "relationship_effects": self._relationship_effects(character_seed, primary_skill),
            "world_dependency_tags": world_grounding.get("world_dependency_tags", []),
        }

    def _primary_skill(self, seed: Dict[str, Any]) -> str:
        if seed.get("primary_skill"):
            return seed["primary_skill"]

        text = str(seed).lower()

        if "hidden_kingmaker" in text:
            return "Pattern Reading"

        if "limit_break" in text or "anomaly" in text:
            return "Pressure Adaptation"

        if seed.get("role") == "villain":
            return "Legal Weaponization"

        if seed.get("role") == "rival":
            return "Disciplined Technique"

        if seed.get("role") == "love_interest":
            return "Social-Strategic Perception"

        return "Adaptive Observation"

    def _skill_domain(self, seed: Dict[str, Any], primary_skill: str) -> str:
        if seed.get("skill_domain"):
            return seed["skill_domain"]

        text = primary_skill.lower()

        if "pattern" in text or "observation" in text:
            return "cognitive"

        if "legal" in text:
            return "institutional"

        if "pressure" in text or "adaptation" in text:
            return "adaptive"

        if "technique" in text:
            return "combat"

        if "social" in text:
            return "social"

        return "general"

    def _skill_rank(self, seed: Dict[str, Any]) -> str:
        return seed.get("skill_rank") or seed.get("rank") or ("S" if seed.get("role") in {"protagonist", "villain"} else "C")

    def _skill_rarity(self, seed: Dict[str, Any], rank: str) -> str:
        if seed.get("skill_rarity"):
            return seed["skill_rarity"]

        if rank in {"S", "SS", "SSS"}:
            return "rare"

        if seed.get("adaptability_type") == "limit_break_anomaly":
            return "anomaly"

        return "common"

    def _secondary_skills(self, seed: Dict[str, Any], domain: str) -> List[str]:
        if seed.get("secondary_skills"):
            return seed["secondary_skills"]

        by_domain = {
            "cognitive": ["micro-expression reading", "probability intuition", "institutional pattern mapping"],
            "adaptive": ["stress learning", "pain translation", "threshold response"],
            "institutional": ["procedural manipulation", "oath clause reading", "public intimidation"],
            "combat": ["stance discipline", "timing analysis", "counter-form recognition"],
            "social": ["tone reading", "status navigation", "controlled vulnerability"],
            "general": ["situational awareness", "basic survival", "improvisation"],
        }

        return by_domain.get(domain, by_domain["general"])

    def _mastery_score(self, rank: str, rarity: str, seed: Dict[str, Any]) -> float:
        rank_scores = {
            "F": 0.05,
            "D": 0.18,
            "C": 0.32,
            "B": 0.48,
            "A": 0.64,
            "S": 0.78,
            "SS": 0.88,
            "SSS": 0.94,
        }

        score = rank_scores.get(str(rank), 0.35)

        if rarity in {"anomaly", "mythic"}:
            score -= 0.08

        if seed.get("training_needed"):
            score -= 0.08

        if seed.get("limitation"):
            score -= 0.02

        return self._clamp(score)

    def _raw_potential_score(self, rank: str, rarity: str, seed: Dict[str, Any]) -> float:
        score = self._mastery_score(rank, rarity, seed) + 0.12

        if rarity in {"rare", "elite", "legendary", "mythic", "anomaly"}:
            score += 0.12

        if seed.get("destiny_type"):
            score += 0.06

        if seed.get("adaptability_type"):
            score += 0.08

        return self._clamp(score)

    def _control_score(self, seed: Dict[str, Any], moral_profile: Dict[str, Any]) -> float:
        score = 0.5

        if seed.get("skill_cost"):
            score += 0.08

        if seed.get("limitation"):
            score += 0.08

        if seed.get("adaptability_type"):
            score -= 0.08

        if moral_profile.get("moral_flexibility", 0.5) >= 0.55:
            score += 0.04

        if moral_profile.get("corruption_risk", 0.0) >= 0.6:
            score -= 0.12

        return self._clamp(score)

    def _growth_ceiling(self, rarity: str, seed: Dict[str, Any]) -> float:
        score = 0.65

        if rarity in {"rare", "elite"}:
            score += 0.15

        if rarity in {"legendary", "mythic", "anomaly"}:
            score += 0.25

        if seed.get("adaptability_type"):
            score += 0.08

        if seed.get("skill_cost") is None and rarity != "common":
            score -= 0.1

        return self._clamp(score)

    def _narrative_function(self, seed: Dict[str, Any], goal_profile: Dict[str, Any], primary_skill: str) -> str:
        if seed.get("role") == "villain":
            return "turns institutional power into story pressure and moral dilemma"

        if "pattern" in primary_skill.lower():
            return "lets the character see hidden systems before others believe them"

        if seed.get("breakthrough_condition"):
            return "activates under moral pressure but creates consequence after victory"

        if goal_profile.get("hidden_goal"):
            return f"serves hidden goal: {goal_profile['hidden_goal']}"

        return "creates agency while requiring limitation"

    def _world_legality(self, seed: Dict[str, Any], domain: str, world_constraints: Dict[str, Any]) -> str:
        text = str(seed).lower()

        if seed.get("illegal_tutor") or seed.get("forged_identity"):
            return "illegal_or_hidden"

        if world_constraints.get("commoner_royal_magic_restricted") and "royal magic" in text:
            return "restricted"

        if domain in {"institutional"}:
            return "regulated"

        if domain == "adaptive" and seed.get("adaptability_type"):
            return "unclassified_by_current_law"

        return "legal_or_unregulated"

    def _social_visibility(self, seed: Dict[str, Any], rarity: str, world_grounding: Dict[str, Any]) -> str:
        if rarity in {"mythic", "anomaly"}:
            return "dangerously_visible_after_use"

        if rarity in {"rare", "elite", "legendary"}:
            return "visible_if_demonstrated"

        if "academy_gatekeeping" in world_grounding.get("world_dependency_tags", []):
            return "visible_through_exam_or_rank"

        return "low_visibility"

    def _relationship_effects(self, seed: Dict[str, Any], primary_skill: str) -> Dict[str, str]:
        return {
            "friendship": "skill may create reliance, admiration, or fear depending on cost",
            "romance": "skill creates intimacy risk if it reads too much or hides too much",
            "rivalry": "skill invites comparison and counter-training",
            "enemy": "skill makes the character a tactical target",
            "mentor": "skill requires guidance that may become control",
        }

    def _build_power_limits(
        self,
        *,
        skill_profile: Dict[str, Any],
        character_seed: Dict[str, Any],
        moral_profile: Dict[str, Any],
        world_constraints: Dict[str, Any],
    ) -> Dict[str, Any]:
        rarity = skill_profile["skill_rarity"]

        costs = self._costs(character_seed, skill_profile)
        limitations = self._limitations(character_seed, skill_profile)
        misuse_risks = self._misuse_risks(character_seed, moral_profile, skill_profile)

        return {
            "costs": costs,
            "limitations": limitations,
            "failure_modes": self._failure_modes(character_seed, skill_profile),
            "misuse_risks": misuse_risks,
            "cooldown_or_recovery": self._cooldown(character_seed, rarity),
            "environmental_constraints": self._environmental_constraints(skill_profile, character_seed),
            "social_constraints": self._social_constraints(skill_profile, character_seed),
            "moral_constraints": self._moral_constraints(moral_profile, character_seed),
            "cannot_do": self._cannot_do(character_seed, skill_profile),
            "balance_notes": self._balance_notes(costs, limitations, misuse_risks, rarity),
        }

    def _costs(self, seed: Dict[str, Any], skill_profile: Dict[str, Any]) -> List[str]:
        costs = []

        if seed.get("skill_cost"):
            costs.append(seed["skill_cost"])

        if seed.get("adaptation_cost"):
            costs.append(seed["adaptation_cost"])

        if skill_profile["skill_rarity"] != "common" and not costs:
            costs.append("emotional exhaustion after overuse")

        if skill_profile["skill_domain"] == "cognitive":
            costs.append("decision fatigue and social isolation")

        if skill_profile["skill_domain"] == "adaptive":
            costs.append("instability after pressure spike")

        if skill_profile["skill_domain"] == "institutional":
            costs.append("public legitimacy risk")

        return sorted(set(costs))

    def _limitations(self, seed: Dict[str, Any], skill_profile: Dict[str, Any]) -> List[str]:
        limits = []

        if seed.get("limitation"):
            limits.append(seed["limitation"])

        if skill_profile["skill_domain"] == "cognitive":
            limits.append("fails when emotionally attached or deliberately misinformed")

        if skill_profile["skill_domain"] == "adaptive":
            limits.append("cannot repeat breakthrough safely without recovery")

        if skill_profile["skill_domain"] == "institutional":
            limits.append("weak when authority structure loses legitimacy")

        if skill_profile["skill_domain"] == "combat":
            limits.append("requires physical condition and readable opponent rhythm")

        if not limits:
            limits.append("requires context and cannot solve every problem directly")

        return sorted(set(limits))

    def _failure_modes(self, seed: Dict[str, Any], skill_profile: Dict[str, Any]) -> List[str]:
        modes = [
            "overconfidence creates wrong read",
            "public use increases enemy attention",
            "success solves immediate problem but worsens social consequence",
        ]

        if skill_profile["skill_domain"] == "adaptive":
            modes.append("breakthrough occurs too late or leaves instability")

        if skill_profile["skill_domain"] == "institutional":
            modes.append("legal leverage backfires through public witness")

        return modes

    def _misuse_risks(
        self,
        seed: Dict[str, Any],
        moral_profile: Dict[str, Any],
        skill_profile: Dict[str, Any],
    ) -> List[str]:
        risks = []

        if moral_profile.get("corruption_risk", 0.0) >= 0.5:
            risks.append("uses ability to justify control")

        if skill_profile["skill_domain"] == "cognitive":
            risks.append("treats people as systems instead of people")

        if skill_profile["skill_domain"] == "institutional":
            risks.append("turns law into weapon instead of protection")

        if skill_profile["skill_domain"] == "adaptive":
            risks.append("chases breakthrough instead of solving root problem")

        if seed.get("role") == "villain":
            risks.append("frames harm as necessary order")

        return sorted(set(risks))

    def _cooldown(self, seed: Dict[str, Any], rarity: str) -> Dict[str, Any]:
        if seed.get("cooldown_or_recovery"):
            return seed["cooldown_or_recovery"]

        if rarity in {"mythic", "anomaly", "SS", "SSS"}:
            return {
                "type": "major_recovery",
                "duration": "scene_to_arc_scale",
                "recovery_need": "emotional stabilization and physical/social consequence handling",
            }

        if rarity in {"rare", "elite", "legendary", "S"}:
            return {
                "type": "moderate_recovery",
                "duration": "scene_scale",
                "recovery_need": "rest, emotional processing, or tactical recalibration",
            }

        return {
            "type": "minor_recovery",
            "duration": "short_pause",
            "recovery_need": "attention and energy reset",
        }

    def _environmental_constraints(self, skill_profile: Dict[str, Any], seed: Dict[str, Any]) -> List[str]:
        domain = skill_profile["skill_domain"]

        if domain == "cognitive":
            return ["requires observable patterns", "weakened by chaos with no signal"]

        if domain == "institutional":
            return ["requires functioning legal/institutional structure", "weakened in border or collapse zones"]

        if domain == "adaptive":
            return ["requires meaningful pressure", "cannot activate casually"]

        if domain == "combat":
            return ["requires physical space", "weakened by exhaustion or injury"]

        return ["requires relevant context"]

    def _social_constraints(self, skill_profile: Dict[str, Any], seed: Dict[str, Any]) -> List[str]:
        constraints = []

        if skill_profile["social_visibility"] in {"dangerously_visible_after_use", "visible_if_demonstrated"}:
            constraints.append("public use changes reputation")

        if seed.get("family_name_status") in {"distrusted", "erased", "unknown"}:
            constraints.append("low-trust name makes explanations harder to believe")

        if skill_profile["world_legality"] in {"illegal_or_hidden", "restricted", "unclassified_by_current_law"}:
            constraints.append("legal scrutiny after use")

        return constraints or ["social consequence depends on audience"]

    def _moral_constraints(self, moral_profile: Dict[str, Any], seed: Dict[str, Any]) -> List[str]:
        constraints = []

        for line in moral_profile.get("forbidden_lines", [])[:3]:
            constraints.append(f"must not violate forbidden line: {line}")

        if seed.get("breakthrough_condition"):
            constraints.append("breakthrough should activate only under stated moral pressure")

        if not constraints:
            constraints.append("must preserve agency and consequence")

        return constraints

    def _cannot_do(self, seed: Dict[str, Any], skill_profile: Dict[str, Any]) -> List[str]:
        cannot = [
            "cannot solve every conflict without cost",
            "cannot erase emotional consequence",
            "cannot remove the need for relationship repair",
        ]

        if skill_profile["skill_domain"] == "cognitive":
            cannot.append("cannot read completely hidden information without evidence")

        if skill_profile["skill_domain"] == "adaptive":
            cannot.append("cannot break limits repeatedly without worsening instability")

        if skill_profile["skill_domain"] == "institutional":
            cannot.append("cannot control people who reject the institution's legitimacy")

        return cannot

    def _balance_notes(self, costs: List[str], limits: List[str], risks: List[str], rarity: str) -> List[str]:
        notes = []

        if rarity != "common":
            notes.append("Rare ability must always use cost, limit, and counterplay.")

        if not costs:
            notes.append("Add explicit cost before using in major plot resolution.")

        if not limits:
            notes.append("Add limitation before conflict simulation.")

        if risks:
            notes.append("Misuse risk should appear in at least one moral or relationship scene.")

        return notes

    def _build_training_path(
        self,
        *,
        skill_profile: Dict[str, Any],
        power_limits: Dict[str, Any],
        character_seed: Dict[str, Any],
        goal_profile: Dict[str, Any],
    ) -> Dict[str, Any]:
        stages = [
            {
                "stage": "recognition",
                "description": "character identifies what the skill actually is, not what others labeled it",
                "failure_lesson": "mislabeling causes misuse",
            },
            {
                "stage": "control",
                "description": "character learns cost, limit, and safe activation conditions",
                "failure_lesson": "power without control increases exposure and harm",
            },
            {
                "stage": "counterplay",
                "description": "character learns how enemies can read, block, or exploit the skill",
                "failure_lesson": "winning once makes the pattern visible",
            },
            {
                "stage": "ethical_use",
                "description": "character chooses when not to use the skill",
                "failure_lesson": "ability is not permission",
            },
            {
                "stage": "integrated_mastery",
                "description": "character uses the skill while accepting consequence and relationship repair",
                "failure_lesson": "victory without repair becomes corruption",
            },
        ]

        if skill_profile["skill_domain"] == "adaptive":
            stages.append(
                {
                    "stage": "post_break_recovery",
                    "description": "character learns how to recover after exceeding a limit",
                    "failure_lesson": "breakthrough without recovery damages future agency",
                }
            )

        return {
            "training_stages": stages,
            "mentor_needed": skill_profile["mastery_score"] < 0.7 or skill_profile["skill_rarity"] != "common",
            "practice_methods": self._practice_methods(skill_profile),
            "required_failures": self._required_failures(skill_profile, power_limits),
            "mastery_gate": self._mastery_gate(skill_profile, goal_profile),
            "training_story_hooks": self._training_story_hooks(skill_profile, character_seed),
        }

    def _practice_methods(self, skill_profile: Dict[str, Any]) -> List[str]:
        domain = skill_profile["skill_domain"]

        if domain == "cognitive":
            return ["case reconstruction", "pattern journals", "false-signal drills"]

        if domain == "adaptive":
            return ["controlled pressure exposure", "post-break recovery logging", "moral threshold rehearsal"]

        if domain == "institutional":
            return ["mock hearings", "oath clause analysis", "public legitimacy trials"]

        if domain == "combat":
            return ["counter-form sparring", "fatigue drills", "opponent rhythm study"]

        return ["scenario practice", "reflection", "controlled failure"]

    def _required_failures(self, skill_profile: Dict[str, Any], power_limits: Dict[str, Any]) -> List[str]:
        return [
            "skill succeeds tactically but creates social cost",
            "enemy identifies a counter",
            "character violates or nearly violates a moral constraint",
            "cost forces recovery instead of immediate next victory",
        ]

    def _mastery_gate(self, skill_profile: Dict[str, Any], goal_profile: Dict[str, Any]) -> str:
        if skill_profile["skill_domain"] == "adaptive":
            return "mastery requires choosing consequence after breakthrough instead of chasing power"

        if goal_profile.get("true_need"):
            return f"mastery requires alignment with true need: {goal_profile['true_need']}"

        return "mastery requires restraint, not only stronger output"

    def _training_story_hooks(self, skill_profile: Dict[str, Any], seed: Dict[str, Any]) -> List[str]:
        hooks = [
            "mentor warns that the skill will make enemies adapt",
            "first public success creates admiration and fear",
            "failure reveals hidden limitation",
        ]

        if skill_profile["skill_domain"] == "adaptive":
            hooks.append("limit-break training causes instability that must be handled after the scene")

        if seed.get("family_name_status") in {"distrusted", "erased", "unknown"}:
            hooks.append("low-trust family name makes achievements easier to question")

        return hooks

    def _build_counterplay_matrix(
        self,
        *,
        skill_profile: Dict[str, Any],
        power_limits: Dict[str, Any],
        moral_profile: Dict[str, Any],
        dilemma_matrix: Dict[str, Any],
    ) -> Dict[str, Any]:
        domain = skill_profile["skill_domain"]

        counters = {
            "cognitive": [
                "feed false patterns",
                "remove observable evidence",
                "force emotional attachment into the read",
            ],
            "adaptive": [
                "deny meaningful pressure until too late",
                "trigger repeated breakthroughs to cause instability",
                "attack recovery window",
            ],
            "institutional": [
                "move conflict outside jurisdiction",
                "publicly invalidate authority structure",
                "turn procedure against user",
            ],
            "combat": [
                "break rhythm",
                "force exhaustion",
                "change terrain",
            ],
            "social": [
                "isolate from trusted witnesses",
                "weaponize public misunderstanding",
                "fake vulnerability",
            ],
            "general": [
                "deny context",
                "increase cost",
                "attack reputation",
            ],
        }

        direct_counters = counters.get(domain, counters["general"])

        return {
            "direct_counters": direct_counters,
            "soft_counters": [
                "public rumor changes audience interpretation",
                "relationship betrayal weakens focus",
                "moral dilemma delays use",
            ],
            "enemy_learning_risk": self._enemy_learning_risk(skill_profile),
            "counter_training_needed": True,
            "dilemma_links": [
                dilemma.get("dilemma_id")
                for dilemma in dilemma_matrix.get("dilemmas", [])
            ],
            "counterplay_story_hooks": [
                "enemy counters the ability after seeing it once",
                "ally fears the ability after witnessing the cost",
                "character must win without using the power",
            ],
        }

    def _enemy_learning_risk(self, skill_profile: Dict[str, Any]) -> float:
        risk = 0.35

        if skill_profile["social_visibility"] in {"visible_if_demonstrated", "dangerously_visible_after_use"}:
            risk += 0.25

        if skill_profile["skill_rarity"] != "common":
            risk += 0.15

        if skill_profile["skill_domain"] in {"cognitive", "adaptive", "institutional"}:
            risk += 0.08

        return self._clamp(risk)

    def _build_diagnostics(
        self,
        *,
        skill_profile: Dict[str, Any],
        power_limits: Dict[str, Any],
        training_path: Dict[str, Any],
        counterplay_matrix: Dict[str, Any],
    ) -> Dict[str, Any]:
        completeness = sum(
            [
                bool(skill_profile["primary_skill"]),
                bool(skill_profile["skill_domain"]),
                bool(skill_profile["skill_rank"]),
                bool(skill_profile["skill_rarity"]),
                bool(power_limits["costs"]),
                bool(power_limits["limitations"]),
                bool(power_limits["failure_modes"]),
                bool(power_limits["misuse_risks"]),
                bool(training_path["training_stages"]),
                bool(counterplay_matrix["direct_counters"]),
                bool(counterplay_matrix["soft_counters"]),
                bool(power_limits["cannot_do"]),
            ]
        ) / 12

        return {
            "ability_completeness_score": round(completeness, 3),
            "has_cost": bool(power_limits["costs"]),
            "has_limitations": bool(power_limits["limitations"]),
            "has_counterplay": bool(counterplay_matrix["direct_counters"]),
            "has_training_path": bool(training_path["training_stages"]),
            "has_misuse_risk": bool(power_limits["misuse_risks"]),
            "has_cannot_do_rules": bool(power_limits["cannot_do"]),
            "is_balanced": completeness >= 0.9,
            "conflict_ready": bool(counterplay_matrix["direct_counters"] and power_limits["failure_modes"]),
            "adaptability_ready": skill_profile["growth_ceiling"] >= 0.6,
        }

    def _build_next_engine_payload(
        self,
        *,
        character_seed: Dict[str, Any],
        skill_profile: Dict[str, Any],
        power_limits: Dict[str, Any],
        training_path: Dict[str, Any],
        counterplay_matrix: Dict[str, Any],
    ) -> Dict[str, Any]:
        merged_seed = dict(character_seed)
        merged_seed["skill_profile"] = skill_profile
        merged_seed["power_limits"] = power_limits
        merged_seed["training_path"] = training_path
        merged_seed["counterplay_matrix"] = counterplay_matrix

        return {
            "character_seed": merged_seed,
            "adaptability_engine_payload": {
                "character_seed": merged_seed,
                "skill_profile": skill_profile,
                "power_limits": power_limits,
                "training_path": training_path,
            },
            "destiny_engine_payload": {
                "character_seed": merged_seed,
                "skill_profile": skill_profile,
                "power_limits": power_limits,
            },
            "relationship_readiness_payload": {
                "character_seed": merged_seed,
                "skill_profile": skill_profile,
                "relationship_effects": skill_profile["relationship_effects"],
            },
            "conflict_simulation_payload_later": {
                "character_id": skill_profile["character_id"],
                "skill_profile": skill_profile,
                "power_limits": power_limits,
                "counterplay_matrix": counterplay_matrix,
            },
        }

    def _clamp(self, value: float) -> float:
        return round(max(0.0, min(1.0, value)), 3)

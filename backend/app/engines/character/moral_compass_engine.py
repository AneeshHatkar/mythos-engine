from typing import Any, Dict, List
from uuid import uuid4

from backend.app.engines.base import BaseEngine
from backend.app.schemas.foundation import EngineRunResult


class MoralCompassEngine(BaseEngine):
    """Builds moral compass, ethics, corruption, and redemption logic.

    This engine defines:
    - moral values
    - forbidden lines
    - justifications
    - pressure-based exceptions
    - corruption path
    - redemption path
    - moral dilemma behavior
    - relationship effects

    It prepares characters for deep conflict, betrayal, sacrifice, villainy,
    redemption, and meaningful plot choices.
    """

    engine_name = "character.moral_compass_engine"

    def run(self, payload: Dict[str, Any]) -> EngineRunResult:
        character_seed = payload.get("character_seed", {})
        psychology_profile = payload.get("psychology_profile") or character_seed.get("psychology", {})
        goal_profile = payload.get("goal_profile") or character_seed.get("goal_profile", {})
        motivation_stack = payload.get("motivation_stack") or character_seed.get("motivation_stack", {})
        agency_rules = payload.get("agency_rules") or character_seed.get("agency_rules", {})
        reputation_profile = payload.get("reputation_profile") or character_seed.get("reputation", {})
        world_grounding = payload.get("world_grounding", {})

        warnings: List[str] = []

        if not character_seed:
            warnings.append("No character_seed provided; moral engine used draft defaults.")

        character_id = (
            character_seed.get("character_id")
            or psychology_profile.get("character_id")
            or goal_profile.get("character_id")
            or reputation_profile.get("character_id")
            or f"char_{uuid4().hex[:12]}"
        )

        moral_profile = self._build_moral_profile(
            character_id=character_id,
            character_seed=character_seed,
            psychology_profile=psychology_profile,
            goal_profile=goal_profile,
            motivation_stack=motivation_stack,
            reputation_profile=reputation_profile,
            world_grounding=world_grounding,
        )

        dilemma_matrix = self._build_dilemma_matrix(
            moral_profile=moral_profile,
            character_seed=character_seed,
            psychology_profile=psychology_profile,
            goal_profile=goal_profile,
            agency_rules=agency_rules,
        )

        moral_arc = self._build_moral_arc(
            moral_profile=moral_profile,
            psychology_profile=psychology_profile,
            goal_profile=goal_profile,
            character_seed=character_seed,
        )

        relationship_ethics = self._build_relationship_ethics(
            moral_profile=moral_profile,
            psychology_profile=psychology_profile,
            character_seed=character_seed,
        )

        moral_diagnostics = self._build_diagnostics(
            moral_profile=moral_profile,
            dilemma_matrix=dilemma_matrix,
            moral_arc=moral_arc,
            relationship_ethics=relationship_ethics,
        )

        next_engine_payload = self._build_next_engine_payload(
            character_seed=character_seed,
            moral_profile=moral_profile,
            dilemma_matrix=dilemma_matrix,
            moral_arc=moral_arc,
            relationship_ethics=relationship_ethics,
        )

        return self.build_result(
            success=True,
            data={
                "moral_profile": moral_profile,
                "dilemma_matrix": dilemma_matrix,
                "moral_arc": moral_arc,
                "relationship_ethics": relationship_ethics,
                "moral_diagnostics": moral_diagnostics,
                "next_engine_payload": next_engine_payload,
                "moral_summary": {
                    "character_id": character_id,
                    "dominant_moral_value": moral_profile["dominant_moral_value"],
                    "primary_forbidden_line": moral_profile["forbidden_lines"][0],
                    "corruption_risk": moral_profile["corruption_risk"],
                    "redemption_potential": moral_profile["redemption_potential"],
                    "moral_flexibility": moral_profile["moral_flexibility"],
                    "dilemma_count": len(dilemma_matrix["dilemmas"]),
                    "ready_for_skill_engine": True,
                    "ready_for_adaptability_engine": True,
                    "ready_for_relationship_simulation_later": True,
                },
                "training_notes": [
                    "Moral compass turns goals into meaningful choices with cost.",
                    "Forbidden lines prevent characters from becoming arbitrary under pressure.",
                    "Corruption and redemption are modeled as paths, not sudden personality flips.",
                    "Future Chunk 8 can learn moral transition patterns from curated dilemma/outcome data.",
                ],
            },
            warnings=warnings,
            errors=[],
            generated_object_ids=[moral_profile["moral_profile_id"]],
        )

    def _build_moral_profile(
        self,
        *,
        character_id: str,
        character_seed: Dict[str, Any],
        psychology_profile: Dict[str, Any],
        goal_profile: Dict[str, Any],
        motivation_stack: Dict[str, Any],
        reputation_profile: Dict[str, Any],
        world_grounding: Dict[str, Any],
    ) -> Dict[str, Any]:
        role = character_seed.get("role", "draft_character")
        social_class = character_seed.get("social_class", "unknown")

        values = self._moral_values(character_seed, psychology_profile, goal_profile)
        dominant = max(values, key=values.get)

        return {
            "moral_profile_id": f"moral_{uuid4().hex[:12]}",
            "character_id": character_id,
            "dominant_moral_value": dominant,
            "moral_values": values,
            "ethical_code": self._ethical_code(role, social_class, psychology_profile, goal_profile),
            "forbidden_lines": self._forbidden_lines(character_seed, psychology_profile, role),
            "conditional_exceptions": self._conditional_exceptions(character_seed, goal_profile, reputation_profile),
            "moral_blind_spots": self._moral_blind_spots(character_seed, psychology_profile, reputation_profile),
            "self_justifications": self._self_justifications(character_seed, psychology_profile, goal_profile),
            "guilt_triggers": self._guilt_triggers(character_seed, psychology_profile, goal_profile),
            "mercy_triggers": self._mercy_triggers(character_seed, psychology_profile),
            "cruelty_triggers": self._cruelty_triggers(character_seed, psychology_profile, reputation_profile),
            "corruption_risk": self._corruption_risk(character_seed, psychology_profile, goal_profile, reputation_profile),
            "redemption_potential": self._redemption_potential(character_seed, psychology_profile, goal_profile),
            "moral_flexibility": self._moral_flexibility(character_seed, values, reputation_profile),
            "world_ethics_dependencies": world_grounding.get("world_dependency_tags", []),
        }

    def _moral_values(
        self,
        seed: Dict[str, Any],
        psychology: Dict[str, Any],
        goal: Dict[str, Any],
    ) -> Dict[str, float]:
        role = seed.get("role", "")

        values = {
            "compassion": 0.55,
            "justice": 0.6,
            "loyalty": 0.52,
            "truth": 0.58,
            "order": 0.38,
            "freedom": 0.46,
            "ambition": 0.42,
            "duty": 0.44,
            "vengeance": 0.18,
            "mercy": 0.5,
        }

        text = (str(seed) + " " + str(psychology) + " " + str(goal)).lower()

        if "protects someone weaker" in text or "powerless" in text:
            values["compassion"] += 0.2
            values["justice"] += 0.15

        if "truth" in text or "proof" in text:
            values["truth"] += 0.2

        if role == "villain":
            values["order"] += 0.35
            values["duty"] += 0.15
            values["mercy"] -= 0.15

        if role == "rival":
            values["ambition"] += 0.18
            values["justice"] += 0.08

        if seed.get("family", {}).get("inherited_obligations"):
            values["duty"] += 0.18
            values["loyalty"] += 0.12

        if psychology.get("corruption_condition"):
            values["vengeance"] += 0.08
            values["ambition"] += 0.06

        return {key: self._clamp(value) for key, value in values.items()}

    def _ethical_code(self, role: str, social_class: str, psychology: Dict[str, Any], goal: Dict[str, Any]) -> str:
        if role == "villain":
            return "order is moral only when it prevents chaos, but this belief can excuse cruelty"

        if social_class in {"erased", "underclass", "relic_miner", "commoner"}:
            return "truth and protection matter more than institutional permission"

        if social_class in {"imperial_elite", "old_nobility"}:
            return "inherited power must be judged by whom it protects and whom it sacrifices"

        if goal.get("true_need"):
            return f"must learn to live by this truth: {goal['true_need']}"

        return "protect dignity without turning pain into permission to harm"

    def _forbidden_lines(self, seed: Dict[str, Any], psychology: Dict[str, Any], role: str) -> List[str]:
        if seed.get("forbidden_lines"):
            return seed["forbidden_lines"]

        lines = []

        if role == "villain":
            lines.append("will not admit the system itself may be immoral until forced by undeniable consequence")
        else:
            lines.append("will not knowingly sacrifice someone powerless for personal advancement")

        if seed.get("breakthrough_condition"):
            lines.append("will not ignore someone weaker being publicly harmed")

        if "family secrets" in str(psychology).lower() or seed.get("family", {}).get("family_secrets"):
            lines.append("will not expose another person's private truth for convenience")

        if seed.get("role") == "love_interest":
            lines.append("will not become a reward at the cost of selfhood")

        return lines

    def _conditional_exceptions(
        self,
        seed: Dict[str, Any],
        goal: Dict[str, Any],
        reputation: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        exceptions = []

        if reputation.get("exposure_risk", 0.0) >= 0.55:
            exceptions.append(
                {
                    "condition": "identity or family truth is about to be weaponized",
                    "exception": "may lie, misdirect, or withhold truth temporarily",
                    "required_cost": "trust damage or later confession",
                }
            )

        if seed.get("breakthrough_condition"):
            exceptions.append(
                {
                    "condition": seed["breakthrough_condition"],
                    "exception": "may break normal rules to protect someone weaker",
                    "required_cost": seed.get("adaptation_cost", "loss of safety or public exposure"),
                }
            )

        if seed.get("role") == "villain":
            exceptions.append(
                {
                    "condition": "order is threatened",
                    "exception": "may justify harming exceptions to preserve structure",
                    "required_cost": "moral corrosion and loss of mercy",
                }
            )

        if not exceptions:
            exceptions.append(
                {
                    "condition": "someone is harmed by silence",
                    "exception": "may break social expectation to tell truth",
                    "required_cost": "reputation damage",
                }
            )

        return exceptions

    def _moral_blind_spots(
        self,
        seed: Dict[str, Any],
        psychology: Dict[str, Any],
        reputation: Dict[str, Any],
    ) -> List[str]:
        blind_spots = []

        if seed.get("role") == "villain":
            blind_spots.append("confuses order with goodness")

        if "controlled" in str(psychology).lower():
            blind_spots.append("mistakes emotional control for moral clarity")

        if reputation.get("institutional_reputation", 1.0) <= 0.35:
            blind_spots.append("may assume every institution is acting in bad faith")

        if seed.get("family", {}).get("inherited_obligations"):
            blind_spots.append("confuses family duty with moral duty")

        if seed.get("skill_rarity") in {"rare", "elite", "legendary", "mythic", "anomaly", "S", "SS", "SSS"}:
            blind_spots.append("may confuse capability with permission")

        if not blind_spots:
            blind_spots.append("may mistake survival habits for moral principles")

        return blind_spots

    def _self_justifications(self, seed: Dict[str, Any], psychology: Dict[str, Any], goal: Dict[str, Any]) -> List[str]:
        justifications = []

        if goal.get("false_need"):
            justifications.append(f"If I follow this belief, I can stay safe: {goal['false_need']}")

        if psychology.get("core_fear"):
            justifications.append(f"My fear makes this choice feel necessary: {psychology['core_fear']}")

        if seed.get("role") == "villain":
            justifications.append("Cruelty is acceptable if it prevents a larger collapse.")

        if seed.get("breakthrough_condition"):
            justifications.append("Breaking the rule is acceptable if inaction harms someone weaker.")

        if not justifications:
            justifications.append("I did what was necessary to survive.")

        return justifications

    def _guilt_triggers(self, seed: Dict[str, Any], psychology: Dict[str, Any], goal: Dict[str, Any]) -> List[str]:
        triggers = []

        if "protects someone weaker" in str(seed).lower():
            triggers.append("fails to protect someone weaker")

        if goal.get("true_need"):
            triggers.append(f"acts against true need: {goal['true_need']}")

        if psychology.get("healing_condition"):
            triggers.append("rejects the healing condition when it becomes possible")

        if seed.get("family", {}).get("family_debt"):
            triggers.append("chooses personal desire while family debt remains unresolved")

        if not triggers:
            triggers.append("hurts someone who trusted them")

        return triggers

    def _mercy_triggers(self, seed: Dict[str, Any], psychology: Dict[str, Any]) -> List[str]:
        triggers = []

        if seed.get("breakthrough_condition"):
            triggers.append(seed["breakthrough_condition"])

        if psychology.get("core_wound"):
            triggers.append(f"sees their own wound in someone else: {psychology['core_wound']}")

        if seed.get("role") == "villain":
            triggers.append("sees evidence that an exception is innocent")

        if not triggers:
            triggers.append("witnesses undeserved humiliation")

        return triggers

    def _cruelty_triggers(
        self,
        seed: Dict[str, Any],
        psychology: Dict[str, Any],
        reputation: Dict[str, Any],
    ) -> List[str]:
        triggers = []

        if psychology.get("corruption_condition"):
            triggers.append(psychology["corruption_condition"])

        if reputation.get("exposure_risk", 0.0) >= 0.55:
            triggers.append("exposure risk threatens safety or identity")

        if seed.get("role") == "villain":
            triggers.append("someone proves the system is morally inconsistent")

        if psychology.get("shame_trigger"):
            triggers.append(f"shame trigger weaponized: {psychology['shame_trigger']}")

        if not triggers:
            triggers.append("fear becomes stronger than compassion")

        return triggers

    def _corruption_risk(
        self,
        seed: Dict[str, Any],
        psychology: Dict[str, Any],
        goal: Dict[str, Any],
        reputation: Dict[str, Any],
    ) -> float:
        risk = 0.25

        if seed.get("role") == "villain":
            risk += 0.35

        if psychology.get("corruption_condition"):
            risk += 0.18

        if reputation.get("exposure_risk", 0.0) >= 0.55:
            risk += 0.08

        if goal.get("agency_score", 1.0) < 0.5:
            risk += 0.08

        if seed.get("skill_rarity") in {"anomaly", "mythic", "SS", "SSS"}:
            risk += 0.08

        return self._clamp(risk)

    def _redemption_potential(self, seed: Dict[str, Any], psychology: Dict[str, Any], goal: Dict[str, Any]) -> float:
        potential = 0.45

        if psychology.get("healing_condition"):
            potential += 0.18

        if goal.get("true_need"):
            potential += 0.12

        if seed.get("role") == "villain":
            potential -= 0.12

        if seed.get("forbidden_lines"):
            potential += 0.08

        if seed.get("breakthrough_condition"):
            potential += 0.06

        return self._clamp(potential)

    def _moral_flexibility(self, seed: Dict[str, Any], values: Dict[str, float], reputation: Dict[str, Any]) -> float:
        flexibility = 0.45

        if seed.get("adaptability_type") or seed.get("breakthrough_condition"):
            flexibility += 0.12

        if values.get("order", 0.0) >= 0.7:
            flexibility -= 0.12

        if reputation.get("exposure_risk", 0.0) >= 0.55:
            flexibility += 0.05

        return self._clamp(flexibility)

    def _build_dilemma_matrix(
        self,
        *,
        moral_profile: Dict[str, Any],
        character_seed: Dict[str, Any],
        psychology_profile: Dict[str, Any],
        goal_profile: Dict[str, Any],
        agency_rules: Dict[str, Any],
    ) -> Dict[str, Any]:
        dilemmas = [
            {
                "dilemma_id": "truth_vs_safety",
                "choice_a": "tell truth and risk exposure",
                "choice_b": "hide truth and preserve safety",
                "likely_choice": self._likely_choice_truth_safety(moral_profile, goal_profile),
                "cost": "trust, reputation, or safety changes",
            },
            {
                "dilemma_id": "mercy_vs_order",
                "choice_a": "show mercy to exception",
                "choice_b": "enforce order even when it harms",
                "likely_choice": self._likely_choice_mercy_order(moral_profile, character_seed),
                "cost": "moral identity becomes clearer or more corrupt",
            },
            {
                "dilemma_id": "loyalty_vs_true_need",
                "choice_a": "protect family/faction expectation",
                "choice_b": "act according to true need",
                "likely_choice": self._likely_choice_loyalty_need(moral_profile, goal_profile),
                "cost": "family trust or selfhood is damaged",
            },
            {
                "dilemma_id": "power_vs_restraint",
                "choice_a": "use ability to solve immediate problem",
                "choice_b": "accept limitation and seek another path",
                "likely_choice": self._likely_choice_power_restraint(moral_profile, character_seed),
                "cost": "public exposure, collateral damage, or delayed victory",
            },
        ]

        return {
            "dilemmas": dilemmas,
            "highest_risk_dilemma": self._highest_risk_dilemma(moral_profile, dilemmas),
            "moral_test_sequence": [item["dilemma_id"] for item in dilemmas],
            "dilemma_simulation_ready": True,
        }

    def _likely_choice_truth_safety(self, moral: Dict[str, Any], goal: Dict[str, Any]) -> str:
        if moral["moral_values"]["truth"] >= 0.7:
            return "tell truth, but strategically"
        if moral["corruption_risk"] >= 0.6:
            return "hide truth until forced"
        return "withhold temporarily, then repair"

    def _likely_choice_mercy_order(self, moral: Dict[str, Any], seed: Dict[str, Any]) -> str:
        if seed.get("role") == "villain":
            return "enforce order until personal contradiction is undeniable"
        if moral["moral_values"]["mercy"] >= moral["moral_values"]["order"]:
            return "show mercy with cost"
        return "obey order and feel guilt"

    def _likely_choice_loyalty_need(self, moral: Dict[str, Any], goal: Dict[str, Any]) -> str:
        if moral["moral_values"]["loyalty"] > moral["moral_values"]["freedom"]:
            return "protect loyalty first, then suffer inner conflict"
        return "choose true need and risk relationship damage"

    def _likely_choice_power_restraint(self, moral: Dict[str, Any], seed: Dict[str, Any]) -> str:
        if seed.get("breakthrough_condition"):
            return "use power only when condition is met"
        if moral["moral_blind_spots"] and "capability with permission" in " ".join(moral["moral_blind_spots"]):
            return "overuse ability and learn consequence"
        return "choose restraint unless stakes rise"

    def _highest_risk_dilemma(self, moral: Dict[str, Any], dilemmas: List[Dict[str, Any]]) -> str:
        if moral["corruption_risk"] >= 0.6:
            return "mercy_vs_order"
        if moral["moral_values"]["truth"] >= 0.7:
            return "truth_vs_safety"
        return dilemmas[0]["dilemma_id"]

    def _build_moral_arc(
        self,
        *,
        moral_profile: Dict[str, Any],
        psychology_profile: Dict[str, Any],
        goal_profile: Dict[str, Any],
        character_seed: Dict[str, Any],
    ) -> Dict[str, Any]:
        role = character_seed.get("role", "")

        if role == "villain":
            arc_type = "order_to_accountability_or_collapse"
        elif moral_profile["corruption_risk"] >= 0.55:
            arc_type = "temptation_to_integrity"
        else:
            arc_type = "wound_to_chosen_ethics"

        return {
            "moral_arc_id": f"marc_{uuid4().hex[:12]}",
            "arc_type": arc_type,
            "starting_moral_position": moral_profile["ethical_code"],
            "moral_pressure_points": [
                moral_profile["cruelty_triggers"][0],
                moral_profile["guilt_triggers"][0],
                moral_profile["mercy_triggers"][0],
            ],
            "corruption_path": [
                "justifies exception",
                "repeats exception under less pressure",
                "rewrites self-image to avoid guilt",
                "harms someone who trusted them",
            ],
            "redemption_path": [
                "names the harm clearly",
                "accepts consequence without demanding forgiveness",
                "repairs damage with cost",
                "chooses true need over false need",
            ],
            "moral_climax": self._moral_climax(moral_profile, psychology_profile, goal_profile, character_seed),
            "moral_resolution": self._moral_resolution(moral_profile, psychology_profile, goal_profile, character_seed),
        }

    def _moral_climax(
        self,
        moral: Dict[str, Any],
        psychology: Dict[str, Any],
        goal: Dict[str, Any],
        seed: Dict[str, Any],
    ) -> str:
        if seed.get("breakthrough_condition"):
            return f"Moral climax occurs when {seed['breakthrough_condition']} and the character must choose cost over safety."

        if seed.get("role") == "villain":
            return "Moral climax occurs when the system demands an innocent sacrifice."

        if psychology.get("corruption_condition"):
            return f"Moral climax tests corruption condition: {psychology['corruption_condition']}"

        return "Moral climax forces the character to choose true need over false need."

    def _moral_resolution(
        self,
        moral: Dict[str, Any],
        psychology: Dict[str, Any],
        goal: Dict[str, Any],
        seed: Dict[str, Any],
    ) -> str:
        if seed.get("role") == "villain":
            return "Resolution depends on whether accountability becomes stronger than control."

        if goal.get("true_need"):
            return f"Resolution requires living by true need: {goal['true_need']}"

        return "Resolution requires choosing ethics without needing public validation."

    def _build_relationship_ethics(
        self,
        *,
        moral_profile: Dict[str, Any],
        psychology_profile: Dict[str, Any],
        character_seed: Dict[str, Any],
    ) -> Dict[str, Any]:
        return {
            "friendship_ethic": "protects friends through action, but may hide truth if afraid of exposure",
            "romance_ethic": "love must preserve agency, truth, and selfhood",
            "rivalry_ethic": "competition is acceptable until it becomes humiliation or sabotage",
            "enemy_ethic": self._enemy_ethic(character_seed, moral_profile),
            "betrayal_boundary": moral_profile["forbidden_lines"][0],
            "forgiveness_condition": psychology_profile.get("healing_condition") or "repair must include cost and changed behavior",
            "relationship_simulation_notes": [
                "Use moral blind spots to create conflict without random cruelty.",
                "Use forbidden lines to determine when trust breaks permanently.",
                "Use guilt triggers to create believable repair attempts.",
            ],
        }

    def _enemy_ethic(self, seed: Dict[str, Any], moral: Dict[str, Any]) -> str:
        if seed.get("role") == "villain":
            return "treats enemies as threats to order rather than full people"

        if moral["moral_values"]["mercy"] >= 0.5:
            return "can oppose enemies without needing to dehumanize them"

        return "may use enemies as containers for unresolved anger"

    def _build_diagnostics(
        self,
        *,
        moral_profile: Dict[str, Any],
        dilemma_matrix: Dict[str, Any],
        moral_arc: Dict[str, Any],
        relationship_ethics: Dict[str, Any],
    ) -> Dict[str, Any]:
        completeness = sum(
            [
                bool(moral_profile["moral_values"]),
                bool(moral_profile["ethical_code"]),
                bool(moral_profile["forbidden_lines"]),
                bool(moral_profile["conditional_exceptions"]),
                bool(moral_profile["moral_blind_spots"]),
                bool(moral_profile["self_justifications"]),
                bool(moral_profile["guilt_triggers"]),
                bool(moral_profile["mercy_triggers"]),
                bool(moral_profile["cruelty_triggers"]),
                bool(dilemma_matrix["dilemmas"]),
                bool(moral_arc["moral_climax"]),
                bool(moral_arc["moral_resolution"]),
            ]
        ) / 12

        return {
            "moral_completeness_score": round(completeness, 3),
            "has_forbidden_lines": len(moral_profile["forbidden_lines"]) > 0,
            "has_conditional_exceptions": len(moral_profile["conditional_exceptions"]) > 0,
            "has_dilemma_matrix": len(dilemma_matrix["dilemmas"]) >= 4,
            "has_corruption_path": len(moral_arc["corruption_path"]) > 0,
            "has_redemption_path": len(moral_arc["redemption_path"]) > 0,
            "has_relationship_ethics": bool(relationship_ethics),
            "moral_simulation_ready": completeness >= 0.9,
            "plot_ready": bool(moral_arc["moral_climax"] and moral_arc["moral_resolution"]),
        }

    def _build_next_engine_payload(
        self,
        *,
        character_seed: Dict[str, Any],
        moral_profile: Dict[str, Any],
        dilemma_matrix: Dict[str, Any],
        moral_arc: Dict[str, Any],
        relationship_ethics: Dict[str, Any],
    ) -> Dict[str, Any]:
        merged_seed = dict(character_seed)
        merged_seed["moral_profile"] = moral_profile
        merged_seed["dilemma_matrix"] = dilemma_matrix
        merged_seed["moral_arc"] = moral_arc
        merged_seed["relationship_ethics"] = relationship_ethics

        return {
            "character_seed": merged_seed,
            "skill_engine_payload": {
                "character_seed": merged_seed,
                "moral_profile": moral_profile,
                "dilemma_matrix": dilemma_matrix,
            },
            "adaptability_engine_payload": {
                "character_seed": merged_seed,
                "moral_profile": moral_profile,
                "moral_arc": moral_arc,
            },
            "destiny_engine_payload": {
                "character_seed": merged_seed,
                "moral_profile": moral_profile,
                "moral_arc": moral_arc,
            },
            "relationship_simulation_payload_later": {
                "character_id": moral_profile["character_id"],
                "moral_profile": moral_profile,
                "relationship_ethics": relationship_ethics,
                "dilemma_matrix": dilemma_matrix,
            },
            "plot_engine_payload_later": {
                "character_id": moral_profile["character_id"],
                "moral_arc": moral_arc,
                "dilemma_matrix": dilemma_matrix,
            },
        }

    def _clamp(self, value: float) -> float:
        return round(max(0.0, min(1.0, value)), 3)

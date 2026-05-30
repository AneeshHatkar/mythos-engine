from typing import Any, Dict, List
from uuid import uuid4

from backend.app.engines.base import BaseEngine
from backend.app.schemas.character import PsychologyProfile
from backend.app.schemas.foundation import EngineRunResult


class PsychologyEngine(BaseEngine):
    """Builds deep psychological architecture for a character.

    This engine turns origin and family pressure into behavior logic.
    It answers why a character acts the way they do under shame, love,
    betrayal, power, fear, and social pressure.
    """

    engine_name = "character.psychology_engine"

    def run(self, payload: Dict[str, Any]) -> EngineRunResult:
        character_seed = payload.get("character_seed", {})
        origin_profile = payload.get("origin_profile") or character_seed.get("origin", {})
        family_profile = payload.get("family_profile") or character_seed.get("family", {})
        family_pressure = payload.get("family_pressure") or character_seed.get("family_pressure", {})
        origin_story_hooks = payload.get("origin_story_hooks") or character_seed.get("origin_story_hooks", [])
        family_story_hooks = payload.get("family_story_hooks") or character_seed.get("family_story_hooks", [])

        warnings: List[str] = []

        if not character_seed:
            warnings.append("No character_seed provided; psychology engine used draft defaults.")

        character_id = character_seed.get("character_id") or origin_profile.get("character_id") or family_profile.get("character_id") or f"char_{uuid4().hex[:12]}"

        psychology = PsychologyProfile(
            psychology_id=f"psy_{uuid4().hex[:12]}",
            character_id=character_id,
            core_wound=self._core_wound(character_seed, origin_profile, family_profile),
            core_desire=self._core_desire(character_seed, family_pressure),
            core_fear=self._core_fear(character_seed, origin_profile, family_profile),
            core_lie=self._core_lie(character_seed, origin_profile, family_profile),
            core_truth=self._core_truth(character_seed, origin_profile, family_profile),
            defense_mechanism=self._defense_mechanism(character_seed, origin_profile, family_pressure),
            attachment_tendency=self._attachment_tendency(character_seed, family_profile),
            shame_trigger=self._shame_trigger(character_seed, origin_profile, family_profile),
            stress_response=self._stress_response(character_seed, origin_profile, family_pressure),
            love_response=self._love_response(character_seed, family_profile),
            betrayal_response=self._betrayal_response(character_seed, family_profile),
            power_response=self._power_response(character_seed, origin_profile, family_profile),
            healing_condition=self._healing_condition(character_seed, family_profile),
            corruption_condition=self._corruption_condition(character_seed, origin_profile, family_pressure),
            contradiction_notes=self._contradiction_notes(character_seed, origin_profile, family_profile),
            behavior_rules=self._behavior_rules(character_seed, origin_profile, family_profile, family_pressure),
        )

        psychology_diagnostics = self._build_psychology_diagnostics(psychology, origin_profile, family_profile)
        interaction_readiness = self._build_interaction_readiness(psychology, character_seed)
        next_engine_payload = self._build_next_engine_payload(
            character_seed=character_seed,
            psychology=psychology,
            origin_profile=origin_profile,
            family_profile=family_profile,
            origin_story_hooks=origin_story_hooks,
            family_story_hooks=family_story_hooks,
        )

        return self.build_result(
            success=True,
            data={
                "psychology_profile": psychology.model_dump(),
                "psychology_diagnostics": psychology_diagnostics,
                "interaction_readiness": interaction_readiness,
                "next_engine_payload": next_engine_payload,
                "psychology_summary": {
                    "character_id": character_id,
                    "core_wound": psychology.core_wound,
                    "core_desire": psychology.core_desire,
                    "core_fear": psychology.core_fear,
                    "defense_mechanism": psychology.defense_mechanism,
                    "has_healing_condition": psychology.healing_condition is not None,
                    "has_corruption_condition": psychology.corruption_condition is not None,
                    "behavior_rule_count": len(psychology.behavior_rules),
                    "ready_for_trauma_engine": True,
                    "ready_for_emotion_engine": True,
                    "ready_for_goal_engine": True,
                },
                "training_notes": [
                    "Psychology should explain behavior, not merely label personality.",
                    "Core wound, lie, and defense mechanism are causal inputs for later emotion, memory, and plot engines.",
                    "Love, betrayal, stress, and power responses prepare Chunk 4 relationship simulation.",
                    "Future training should learn behavior transitions from curated psychology-event pairs.",
                ],
            },
            warnings=warnings,
            errors=[],
            generated_object_ids=[psychology.psychology_id],
        )

    def _core_wound(self, seed: Dict[str, Any], origin: Dict[str, Any], family: Dict[str, Any]) -> str:
        if seed.get("core_wound"):
            return seed["core_wound"]

        class_wound = origin.get("class_wound")
        if class_wound:
            return class_wound

        inherited = family.get("inherited_trauma", [])
        if inherited:
            return inherited[0]

        return "being assigned a role before being known"

    def _core_desire(self, seed: Dict[str, Any], family_pressure: Dict[str, Any]) -> str:
        if seed.get("core_desire"):
            return seed["core_desire"]

        if seed.get("hidden_goal"):
            return seed["hidden_goal"]

        pressure_sources = family_pressure.get("main_pressure_sources", [])
        if pressure_sources:
            return "to make one choice not controlled by inherited pressure"

        return "to be seen accurately without performance"

    def _core_fear(self, seed: Dict[str, Any], origin: Dict[str, Any], family: Dict[str, Any]) -> str:
        if seed.get("core_fear"):
            return seed["core_fear"]

        social_class = origin.get("social_class") or seed.get("social_class")
        family_status = family.get("family_status", "")

        if social_class in {"erased", "underclass"} or family_status == "erased_or_unverified":
            return "being exposed and erased by legal authority"

        if social_class in {"imperial_elite", "old_nobility"}:
            return "becoming a disgrace to the family name"

        if social_class == "academy_sponsored":
            return "belonging being revoked after one visible failure"

        if social_class == "relic_miner":
            return "being spent by the world and forgotten"

        return "being disposable"

    def _core_lie(self, seed: Dict[str, Any], origin: Dict[str, Any], family: Dict[str, Any]) -> str:
        if seed.get("core_lie"):
            return seed["core_lie"]

        social_class = origin.get("social_class") or seed.get("social_class")
        family_status = family.get("family_status", "")

        if social_class in {"imperial_elite", "old_nobility"}:
            return "love must be earned by preserving reputation"

        if social_class == "academy_sponsored":
            return "worth can be revoked by public failure"

        if social_class in {"erased", "underclass"} or family_status == "erased_or_unverified":
            return "truth only matters when powerful people recognize it"

        if social_class == "relic_miner":
            return "pain is only valuable when it is useful"

        return "safety requires being useful"

    def _core_truth(self, seed: Dict[str, Any], origin: Dict[str, Any], family: Dict[str, Any]) -> str:
        if seed.get("core_truth"):
            return seed["core_truth"]

        social_class = origin.get("social_class") or seed.get("social_class")

        if social_class in {"imperial_elite", "old_nobility"}:
            return "a name is not worth more than the people harmed to preserve it"

        if social_class == "academy_sponsored":
            return "belonging is not the same as permission"

        if social_class in {"erased", "underclass"}:
            return "truth exists before institutions certify it"

        if social_class == "relic_miner":
            return "survival is not the same as consent to be used"

        return "worth exists before usefulness"

    def _defense_mechanism(self, seed: Dict[str, Any], origin: Dict[str, Any], family_pressure: Dict[str, Any]) -> str:
        if seed.get("defense_mechanism"):
            return seed["defense_mechanism"]

        social_class = origin.get("social_class") or seed.get("social_class")
        pressure_tier = family_pressure.get("pressure_tier", "")

        if pressure_tier in {"high_family_pressure", "extreme_family_pressure"}:
            return "controlled self-erasure"

        if social_class in {"imperial_elite", "old_nobility"}:
            return "polished emotional concealment"

        if social_class == "academy_sponsored":
            return "perfectionism and strategic silence"

        if social_class in {"erased", "underclass"}:
            return "avoidance of official attention"

        if social_class == "relic_miner":
            return "hard practicality"

        return "controlled distance"

    def _attachment_tendency(self, seed: Dict[str, Any], family: Dict[str, Any]) -> str:
        if seed.get("attachment_tendency"):
            return seed["attachment_tendency"]

        secrets = family.get("family_secrets", [])

        if secrets:
            return "slow trust with secrecy tests"

        status = family.get("family_status")

        if status in {"erased_or_unverified", "legally_false"}:
            return "avoidant under scrutiny, loyal when protected"

        return "guarded but bond-capable"

    def _shame_trigger(self, seed: Dict[str, Any], origin: Dict[str, Any], family: Dict[str, Any]) -> str:
        if seed.get("shame_trigger"):
            return seed["shame_trigger"]

        public_assumptions = origin.get("public_assumptions", [])

        if public_assumptions:
            return f"being treated as {public_assumptions[0]}"

        if family.get("family_reputation"):
            return f"public mention of family reputation: {family['family_reputation']}"

        return "being evaluated before being understood"

    def _stress_response(self, seed: Dict[str, Any], origin: Dict[str, Any], family_pressure: Dict[str, Any]) -> str:
        if seed.get("stress_response"):
            return seed["stress_response"]

        pressure_tier = family_pressure.get("pressure_tier")

        if pressure_tier in {"high_family_pressure", "extreme_family_pressure"}:
            return "becomes quiet, over-controlled, and hyper-observant"

        social_class = origin.get("social_class") or seed.get("social_class")

        if social_class in {"imperial_elite", "old_nobility"}:
            return "uses etiquette to delay emotional truth"

        if social_class in {"erased", "underclass"}:
            return "moves toward exits, silence, and plausible deniability"

        return "withdraws, studies the threat, then acts indirectly"

    def _love_response(self, seed: Dict[str, Any], family: Dict[str, Any]) -> str:
        if seed.get("love_response"):
            return seed["love_response"]

        if family.get("family_secrets"):
            return "wants closeness but fears what intimacy will expose"

        if family.get("inherited_obligations"):
            return "tests whether love survives duty, debt, and public pressure"

        return "shows love through protection before confession"

    def _betrayal_response(self, seed: Dict[str, Any], family: Dict[str, Any]) -> str:
        if seed.get("betrayal_response"):
            return seed["betrayal_response"]

        if family.get("family_secrets"):
            return "goes cold, protects family secrets, and remembers exact words"

        return "withdraws trust and waits for proof under pressure"

    def _power_response(self, seed: Dict[str, Any], origin: Dict[str, Any], family: Dict[str, Any]) -> str:
        if seed.get("power_response"):
            return seed["power_response"]

        social_class = origin.get("social_class") or seed.get("social_class")

        if social_class in {"imperial_elite", "old_nobility"}:
            return "treats power as duty until forced to see its harm"

        if social_class in {"erased", "underclass", "commoner", "relic_miner"}:
            return "distrusts power unless it protects someone powerless"

        if social_class == "academy_sponsored":
            return "uses power carefully because access can be revoked"

        return "tests whether power changes how others treat truth"

    def _healing_condition(self, seed: Dict[str, Any], family: Dict[str, Any]) -> str:
        if seed.get("healing_condition"):
            return seed["healing_condition"]

        if family.get("family_secrets"):
            return "someone learns the family truth and protects them without using it"

        if family.get("family_debt"):
            return "chooses a desire that is not repayment"

        return "is seen accurately during failure and not abandoned"

    def _corruption_condition(self, seed: Dict[str, Any], origin: Dict[str, Any], family_pressure: Dict[str, Any]) -> str:
        if seed.get("corruption_condition"):
            return seed["corruption_condition"]

        social_class = origin.get("social_class") or seed.get("social_class")

        if social_class in {"imperial_elite", "old_nobility"}:
            return "chooses reputation over a person who trusted them"

        if social_class in {"erased", "underclass"}:
            return "decides truth only matters when weaponized"

        if family_pressure.get("pressure_tier") in {"high_family_pressure", "extreme_family_pressure"}:
            return "sacrifices another person to escape family pressure"

        return "uses pain as proof that they deserve control"

    def _contradiction_notes(self, seed: Dict[str, Any], origin: Dict[str, Any], family: Dict[str, Any]) -> List[str]:
        notes = []

        if seed.get("skill_rarity") in {"rare", "elite", "legendary", "mythic", "anomaly", "S", "SS", "SSS"} and not seed.get("skill_cost"):
            notes.append("Rare skill should affect psychology through cost, fear, or social exposure.")

        if seed.get("destiny_type") and not seed.get("destiny_burden"):
            notes.append("Destiny should create burden, not guaranteed superiority.")

        if family.get("family_secrets") and not family.get("family_debt") and not family.get("inherited_obligations"):
            notes.append("Family secret should create pressure, debt, or obligation.")

        if seed.get("adaptability_type") and not seed.get("adaptation_cost"):
            notes.append("Adaptability must include cost to avoid unearned limit-break behavior.")

        return notes

    def _behavior_rules(
        self,
        seed: Dict[str, Any],
        origin: Dict[str, Any],
        family: Dict[str, Any],
        family_pressure: Dict[str, Any],
    ) -> List[str]:
        rules = []

        class_wound = origin.get("class_wound")
        if class_wound:
            rules.append(f"When class status is questioned, behavior is shaped by this wound: {class_wound}")

        if family.get("family_secrets"):
            rules.append("When intimacy threatens family secrets, the character becomes precise, guarded, and evasive.")

        if family_pressure.get("pressure_tier") in {"high_family_pressure", "extreme_family_pressure"}:
            rules.append("When family pressure rises, the character prioritizes control over emotional honesty.")

        if seed.get("breakthrough_condition"):
            rules.append(f"When this condition occurs, adaptability may activate: {seed['breakthrough_condition']}")

        if seed.get("hidden_goal"):
            rules.append(f"When blocked from the hidden goal, the character escalates indirectly: {seed['hidden_goal']}")

        if not rules:
            rules.append("Under pressure, the character protects dignity before comfort.")

        return rules

    def _build_psychology_diagnostics(
        self,
        psychology: PsychologyProfile,
        origin: Dict[str, Any],
        family: Dict[str, Any],
    ) -> Dict[str, Any]:
        depth_score = 0.0

        fields = [
            psychology.core_wound,
            psychology.core_desire,
            psychology.core_fear,
            psychology.core_lie,
            psychology.core_truth,
            psychology.defense_mechanism,
            psychology.attachment_tendency,
            psychology.shame_trigger,
            psychology.stress_response,
            psychology.love_response,
            psychology.betrayal_response,
            psychology.power_response,
            psychology.healing_condition,
            psychology.corruption_condition,
        ]

        depth_score += sum(1 for field in fields if field) / len(fields) * 0.75
        depth_score += min(0.25, len(psychology.behavior_rules) * 0.06)

        return {
            "psychological_depth_score": round(min(1.0, depth_score), 3),
            "behavior_rule_count": len(psychology.behavior_rules),
            "contradiction_count": len(psychology.contradiction_notes),
            "has_origin_link": bool(origin),
            "has_family_link": bool(family),
            "has_healing_and_corruption_paths": bool(psychology.healing_condition and psychology.corruption_condition),
            "ready_for_emotion_engine": depth_score >= 0.65,
        }

    def _build_interaction_readiness(self, psychology: PsychologyProfile, seed: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "trust_trigger_ready": psychology.attachment_tendency is not None,
            "betrayal_response_ready": psychology.betrayal_response is not None,
            "romance_response_ready": psychology.love_response is not None,
            "conflict_response_ready": psychology.stress_response is not None,
            "power_response_ready": psychology.power_response is not None,
            "chunk4_relationship_simulation_ready": all(
                [
                    psychology.attachment_tendency,
                    psychology.betrayal_response,
                    psychology.love_response,
                    psychology.stress_response,
                    psychology.power_response,
                ]
            ),
            "interaction_notes": [
                "Use shame_trigger for conflict scene escalation.",
                "Use love_response and betrayal_response for relationship simulation.",
                "Use corruption_condition for villain/antihero path branching.",
                "Use healing_condition for earned emotional payoff.",
            ],
        }

    def _build_next_engine_payload(
        self,
        *,
        character_seed: Dict[str, Any],
        psychology: PsychologyProfile,
        origin_profile: Dict[str, Any],
        family_profile: Dict[str, Any],
        origin_story_hooks: List[str],
        family_story_hooks: List[str],
    ) -> Dict[str, Any]:
        merged_seed = dict(character_seed)
        merged_seed["psychology"] = psychology.model_dump()

        return {
            "character_seed": merged_seed,
            "trauma_engine_payload": {
                "character_seed": merged_seed,
                "psychology_profile": psychology.model_dump(),
                "origin_profile": origin_profile,
                "family_profile": family_profile,
                "origin_story_hooks": origin_story_hooks,
                "family_story_hooks": family_story_hooks,
            },
            "emotion_engine_payload": {
                "character_seed": merged_seed,
                "psychology_profile": psychology.model_dump(),
            },
            "goal_engine_payload": {
                "character_seed": merged_seed,
                "psychology_profile": psychology.model_dump(),
            },
            "adaptability_engine_payload": {
                "character_seed": merged_seed,
                "psychology_profile": psychology.model_dump(),
                "breakthrough_condition": character_seed.get("breakthrough_condition"),
            },
        }

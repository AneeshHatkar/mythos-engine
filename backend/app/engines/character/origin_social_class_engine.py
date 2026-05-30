from typing import Any, Dict, List
from uuid import uuid4

from backend.app.engines.base import BaseEngine
from backend.app.schemas.character import OriginProfile
from backend.app.schemas.foundation import EngineRunResult


class OriginSocialClassEngine(BaseEngine):
    """Builds birth, origin, and social-class logic for a character.

    This engine connects a character's personal origin to world law, class
    hierarchy, education access, family-name trust, resource access, and public
    assumptions.

    The goal is to make origin consequential, not decorative.
    """

    engine_name = "character.origin_social_class_engine"

    def run(self, payload: Dict[str, Any]) -> EngineRunResult:
        character_seed = payload.get("character_seed", {})
        world_constraints = payload.get("world_constraints", {})
        population_context = payload.get("population_context", {})
        world_grounding = payload.get("world_grounding", {})

        warnings: List[str] = []

        if not character_seed:
            warnings.append("No character_seed provided; origin engine used default draft character values.")

        character_id = character_seed.get("character_id") or f"char_{uuid4().hex[:12]}"
        social_class = character_seed.get("social_class") or self._infer_social_class(character_seed, population_context)
        birth_status = self._infer_birth_status(character_seed, social_class)
        family_name_status = character_seed.get("family_name_status", "unknown")

        profile = OriginProfile(
            origin_id=f"origin_{uuid4().hex[:12]}",
            character_id=character_id,
            birth_status=birth_status,
            social_class=social_class,
            origin_location=self._infer_origin_location(character_seed, social_class, world_constraints),
            family_name_trust=self._family_name_trust(family_name_status, social_class, world_constraints),
            wealth_rank=self._wealth_rank(social_class),
            education_access=self._education_access(social_class, character_seed, world_constraints),
            institution_access=self._institution_access(social_class, character_seed, world_constraints),
            forbidden_access=self._forbidden_access(social_class, character_seed, world_constraints),
            resource_access=self._resource_access(social_class, character_seed, world_constraints),
            inherited_privileges=self._inherited_privileges(social_class, family_name_status),
            inherited_disadvantages=self._inherited_disadvantages(social_class, family_name_status, world_constraints),
            class_wound=self._class_wound(social_class, family_name_status, character_seed),
            mobility_score=self._mobility_score(social_class, character_seed, world_constraints),
            public_assumptions=self._public_assumptions(social_class, family_name_status),
            world_constraint_notes=self._world_constraint_notes(world_constraints, world_grounding, character_seed),
        )

        access_risks = self._build_access_risks(profile, character_seed, world_constraints)
        origin_story_hooks = self._build_origin_story_hooks(profile, access_risks, character_seed)
        next_engine_payload = self._build_next_engine_payload(profile, character_seed, origin_story_hooks)

        return self.build_result(
            success=True,
            data={
                "origin_profile": profile.model_dump(),
                "access_risks": access_risks,
                "origin_story_hooks": origin_story_hooks,
                "next_engine_payload": next_engine_payload,
                "origin_summary": {
                    "character_id": character_id,
                    "birth_status": profile.birth_status,
                    "social_class": profile.social_class,
                    "family_name_trust": profile.family_name_trust,
                    "education_access": profile.education_access,
                    "mobility_score": profile.mobility_score,
                    "has_forbidden_access": len(profile.forbidden_access) > 0,
                    "has_class_wound": profile.class_wound is not None,
                    "ready_for_family_engine": True,
                    "ready_for_psychology_engine": True,
                },
                "training_notes": [
                    "Origin data should be treated as a causal layer for later psychology, goals, and relationships.",
                    "Class access is represented numerically so future models can learn constraints and privilege patterns.",
                    "Low access is not weakness; it creates pressure, creativity, social risk, and story hooks.",
                    "Future Chunk 8 training should preserve provenance and avoid learning harmful stereotypes from class labels.",
                ],
            },
            warnings=warnings,
            errors=[],
            generated_object_ids=[profile.origin_id],
        )

    def _infer_social_class(self, character_seed: Dict[str, Any], population_context: Dict[str, Any]) -> str:
        groups = population_context.get("population_groups", [])

        if groups:
            return groups[0].get("social_class", "commoner")

        role = character_seed.get("role", "")

        if role == "villain":
            return "imperial_elite"

        return "commoner"

    def _infer_birth_status(self, character_seed: Dict[str, Any], social_class: str) -> str:
        if character_seed.get("birth_status"):
            return character_seed["birth_status"]

        family_status = str(character_seed.get("family_name_status", "")).lower()

        if family_status == "erased":
            return "erased_family_record"

        if social_class in {"imperial_elite", "old_nobility"}:
            return "noble_birth"

        if social_class in {"erased", "underclass"}:
            return "unknown_origin"

        if social_class == "borderfolk":
            return "borderborn"

        if social_class == "academy_sponsored":
            return "common_birth"

        return "common_birth"

    def _infer_origin_location(
        self,
        character_seed: Dict[str, Any],
        social_class: str,
        world_constraints: Dict[str, Any],
    ) -> str:
        if character_seed.get("origin_location"):
            return character_seed["origin_location"]

        if social_class in {"imperial_elite", "old_nobility"}:
            return "capital estate district"

        if social_class == "academy_sponsored":
            return "outer academy district"

        if social_class == "relic_miner":
            return "relic-mining city"

        if social_class == "borderfolk":
            return "border ruins settlement"

        if social_class in {"erased", "underclass"}:
            return "underground market quarter"

        return "common town district"

    def _family_name_trust(self, family_name_status: str, social_class: str, world_constraints: Dict[str, Any]) -> float:
        status = str(family_name_status).lower()

        if status in {"trusted", "noble", "verified"}:
            return 0.9

        if status in {"recognized"}:
            return 0.6

        if status in {"distrusted"}:
            return 0.25

        if status in {"erased", "forged", "unknown"}:
            return 0.05

        if social_class in {"imperial_elite", "old_nobility"}:
            return 0.85

        if social_class in {"erased", "underclass"}:
            return 0.05

        if social_class == "academy_sponsored":
            return 0.45

        return 0.35

    def _wealth_rank(self, social_class: str) -> float:
        ranks = {
            "imperial_elite": 0.98,
            "old_nobility": 0.9,
            "new_money": 0.82,
            "merchant_class": 0.65,
            "professional_class": 0.55,
            "academy_sponsored": 0.32,
            "artisan_class": 0.28,
            "commoner": 0.18,
            "borderfolk": 0.2,
            "relic_miner": 0.12,
            "underclass": 0.06,
            "erased": 0.03,
        }

        return ranks.get(social_class, 0.25)

    def _education_access(
        self,
        social_class: str,
        character_seed: Dict[str, Any],
        world_constraints: Dict[str, Any],
    ) -> float:
        base = {
            "imperial_elite": 0.98,
            "old_nobility": 0.92,
            "new_money": 0.72,
            "merchant_class": 0.62,
            "professional_class": 0.65,
            "academy_sponsored": 0.74,
            "artisan_class": 0.35,
            "commoner": 0.22,
            "borderfolk": 0.28,
            "relic_miner": 0.16,
            "underclass": 0.08,
            "erased": 0.06,
        }.get(social_class, 0.25)

        if character_seed.get("scholarship"):
            base += 0.25

        if character_seed.get("sponsor") or character_seed.get("patron"):
            base += 0.18

        if character_seed.get("forged_identity"):
            base += 0.12

        return round(min(1.0, base), 3)

    def _institution_access(
        self,
        social_class: str,
        character_seed: Dict[str, Any],
        world_constraints: Dict[str, Any],
    ) -> List[str]:
        access = []

        if social_class in {"imperial_elite", "old_nobility"}:
            access.extend(["elite academy", "oath court", "private tutors", "restricted archives"])

        elif social_class == "academy_sponsored":
            access.extend(["academy lower halls", "exam offices", "sponsor classrooms"])

        elif social_class in {"merchant_class", "professional_class"}:
            access.extend(["guild schools", "public court offices"])

        elif social_class in {"commoner", "artisan_class", "borderfolk"}:
            access.extend(["local schools", "public shrines"])

        elif social_class in {"erased", "underclass", "relic_miner"}:
            access.extend(["informal tutors", "underground networks"])

        if character_seed.get("scholarship"):
            access.append("conditional academy access")

        if character_seed.get("illegal_tutor"):
            access.append("illegal private instruction")

        if character_seed.get("forged_identity"):
            access.append("false-name institutional access")

        return sorted(set(access))

    def _forbidden_access(
        self,
        social_class: str,
        character_seed: Dict[str, Any],
        world_constraints: Dict[str, Any],
    ) -> List[str]:
        forbidden = []

        low_access = social_class in {"commoner", "relic_miner", "underclass", "erased", "borderfolk"}

        if world_constraints.get("commoner_royal_magic_restricted") and low_access:
            forbidden.append("royal magic curriculum")

        if world_constraints.get("noble_academy_gatekeeping") and (
            low_access or social_class == "academy_sponsored"
        ):
            forbidden.append("elite academy upper halls")

        if world_constraints.get("family_name_affects_legal_trust") and character_seed.get("family_name_status") in {"erased", "forged", "unknown", "distrusted"}:
            forbidden.append("trusted legal witness status")

        if social_class in {"erased", "underclass"}:
            forbidden.append("official contract authority")

        return sorted(set(forbidden))

    def _resource_access(
        self,
        social_class: str,
        character_seed: Dict[str, Any],
        world_constraints: Dict[str, Any],
    ) -> List[str]:
        if social_class in {"imperial_elite", "old_nobility"}:
            return ["family wealth", "legal influence", "private guards", "elite education"]

        if social_class == "academy_sponsored":
            return ["conditional tuition", "sponsor protection", "exam access"]

        if social_class == "relic_miner":
            return ["relic labor knowledge", "worker networks", "danger survival skills"]

        if social_class == "borderfolk":
            return ["ruin routes", "border contacts", "survival knowledge"]

        if social_class in {"erased", "underclass"}:
            return ["false-name networks", "underground markets", "informal intelligence"]

        return ["local community", "labor exchange", "public markets"]

    def _inherited_privileges(self, social_class: str, family_name_status: str) -> List[str]:
        privileges = []

        if social_class in {"imperial_elite", "old_nobility"}:
            privileges.extend(["legal credibility", "institutional access", "family protection"])

        if family_name_status in {"trusted", "noble", "verified"}:
            privileges.append("trusted family-name recognition")

        if social_class == "academy_sponsored":
            privileges.append("conditional education path")

        return privileges

    def _inherited_disadvantages(
        self,
        social_class: str,
        family_name_status: str,
        world_constraints: Dict[str, Any],
    ) -> List[str]:
        disadvantages = []

        if social_class in {"commoner", "relic_miner", "underclass", "erased", "borderfolk"}:
            disadvantages.append("low institutional trust")

        if family_name_status in {"erased", "forged", "unknown", "distrusted"}:
            disadvantages.append("family-name suspicion")

        if social_class == "relic_miner":
            disadvantages.append("relic labor injury exposure")

        if social_class == "erased":
            disadvantages.append("identity instability")

        if world_constraints.get("noble_academy_gatekeeping") and social_class not in {"imperial_elite", "old_nobility"}:
            disadvantages.append("academy gatekeeping")

        return disadvantages

    def _class_wound(
        self,
        social_class: str,
        family_name_status: str,
        character_seed: Dict[str, Any],
    ) -> str:
        if character_seed.get("class_wound"):
            return character_seed["class_wound"]

        if social_class in {"erased", "underclass"}:
            return "believes visibility invites legal erasure"

        if social_class == "relic_miner":
            return "believes the world spends poor bodies to power elite comfort"

        if social_class == "academy_sponsored":
            return "believes belonging can be revoked at any public failure"

        if social_class in {"imperial_elite", "old_nobility"}:
            return "believes love and duty are impossible to separate"

        if family_name_status in {"distrusted", "erased", "unknown"}:
            return "believes names decide whether truth is believed"

        return "believes social worth must be earned repeatedly"

    def _mobility_score(
        self,
        social_class: str,
        character_seed: Dict[str, Any],
        world_constraints: Dict[str, Any],
    ) -> float:
        score = {
            "imperial_elite": 0.75,
            "old_nobility": 0.72,
            "new_money": 0.7,
            "merchant_class": 0.6,
            "professional_class": 0.58,
            "academy_sponsored": 0.52,
            "artisan_class": 0.38,
            "commoner": 0.3,
            "borderfolk": 0.34,
            "relic_miner": 0.22,
            "underclass": 0.14,
            "erased": 0.08,
        }.get(social_class, 0.3)

        if character_seed.get("scholarship"):
            score += 0.12

        if character_seed.get("sponsor") or character_seed.get("patron"):
            score += 0.1

        if character_seed.get("forged_identity"):
            score += 0.06

        if character_seed.get("destiny_type"):
            score += 0.08

        return round(min(1.0, score), 3)

    def _public_assumptions(self, social_class: str, family_name_status: str) -> List[str]:
        assumptions = []

        if social_class in {"imperial_elite", "old_nobility"}:
            assumptions.extend(["competent by birth", "legally credible", "politically protected"])

        elif social_class == "academy_sponsored":
            assumptions.extend(["useful but replaceable", "must prove merit repeatedly"])

        elif social_class in {"commoner", "artisan_class"}:
            assumptions.extend(["ordinary", "low political importance"])

        elif social_class == "relic_miner":
            assumptions.extend(["danger-hardened", "physically disposable"])

        elif social_class in {"erased", "underclass"}:
            assumptions.extend(["untrustworthy", "legally unstable", "easy to blame"])

        if family_name_status in {"erased", "forged", "unknown", "distrusted"}:
            assumptions.append("truth requires extra proof")

        return assumptions

    def _world_constraint_notes(
        self,
        world_constraints: Dict[str, Any],
        world_grounding: Dict[str, Any],
        character_seed: Dict[str, Any],
    ) -> List[str]:
        notes = []

        for tag in world_grounding.get("world_dependency_tags", []):
            notes.append(f"Character origin is shaped by {tag}.")

        if world_constraints.get("commoner_royal_magic_restricted"):
            notes.append("Magic access is class-restricted.")

        if world_constraints.get("family_name_affects_legal_trust"):
            notes.append("Family name affects legal credibility.")

        if world_constraints.get("noble_academy_gatekeeping"):
            notes.append("Academy access is gated by class and sponsorship.")

        if world_constraints.get("relic_economy_pressure"):
            notes.append("Relic economy creates labor and debt pressure.")

        if character_seed.get("active_story_hooks"):
            notes.extend(character_seed["active_story_hooks"])

        return sorted(set(notes))

    def _build_access_risks(
        self,
        profile: OriginProfile,
        character_seed: Dict[str, Any],
        world_constraints: Dict[str, Any],
    ) -> Dict[str, Any]:
        risks = []

        if profile.family_name_trust <= 0.25:
            risks.append("legal credibility risk")

        if profile.education_access <= 0.25:
            risks.append("education access risk")

        if profile.forbidden_access:
            risks.append("forbidden access temptation")

        if profile.mobility_score <= 0.25:
            risks.append("low mobility pressure")

        if profile.social_class in {"imperial_elite", "old_nobility"} and profile.wealth_rank >= 0.85:
            risks.append("privilege blindness risk")

        return {
            "risk_count": len(risks),
            "risks": risks,
            "has_story_useful_pressure": len(risks) > 0,
            "requires_explanation_for_elite_access": (
                profile.social_class not in {"imperial_elite", "old_nobility"}
                and "elite academy upper halls" in profile.forbidden_access
            ),
            "requires_legal_trust_repair": profile.family_name_trust <= 0.25,
        }

    def _build_origin_story_hooks(
        self,
        profile: OriginProfile,
        access_risks: Dict[str, Any],
        character_seed: Dict[str, Any],
    ) -> List[str]:
        hooks = []

        if "legal credibility risk" in access_risks["risks"]:
            hooks.append("Character can tell the truth and still not be believed.")

        if "education access risk" in access_risks["risks"]:
            hooks.append("Character must learn through unofficial, dangerous, or humiliating routes.")

        if "forbidden access temptation" in access_risks["risks"]:
            hooks.append("Forbidden access can create blackmail, debt, or institutional danger.")

        if "privilege blindness risk" in access_risks["risks"]:
            hooks.append("Character must confront what their status protects them from seeing.")

        if profile.class_wound:
            hooks.append(f"Class wound drives behavior: {profile.class_wound}")

        if character_seed.get("breakthrough_condition"):
            hooks.append(f"Origin pressure can trigger adaptability: {character_seed['breakthrough_condition']}")

        return hooks

    def _build_next_engine_payload(
        self,
        profile: OriginProfile,
        character_seed: Dict[str, Any],
        origin_story_hooks: List[str],
    ) -> Dict[str, Any]:
        merged_seed = dict(character_seed)
        merged_seed["origin"] = profile.model_dump()
        merged_seed["origin_story_hooks"] = origin_story_hooks

        return {
            "character_seed": merged_seed,
            "family_engine_payload": {
                "character_seed": merged_seed,
                "family_name_status": character_seed.get("family_name_status"),
                "social_class": profile.social_class,
                "family_direction": character_seed.get("family_direction"),
            },
            "psychology_engine_payload": {
                "character_seed": merged_seed,
                "class_wound": profile.class_wound,
                "public_assumptions": profile.public_assumptions,
                "origin_story_hooks": origin_story_hooks,
            },
        }

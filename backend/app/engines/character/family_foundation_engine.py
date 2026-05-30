from typing import Any, Dict, List
from uuid import uuid4

from backend.app.engines.base import BaseEngine
from backend.app.schemas.character import FamilyMember, FamilyProfile
from backend.app.schemas.foundation import EngineRunResult


class FamilyFoundationEngine(BaseEngine):
    """Builds the family pressure system for a character.

    Family in MythOS is not only backstory. It controls reputation, debt,
    inheritance, legal trust, secrets, obligations, emotional wounds,
    class pressure, enemies, allies, artifacts, and future plot hooks.
    """

    engine_name = "character.family_foundation_engine"

    def run(self, payload: Dict[str, Any]) -> EngineRunResult:
        character_seed = payload.get("character_seed", {})
        origin_profile = payload.get("origin_profile") or character_seed.get("origin", {})
        world_constraints = payload.get("world_constraints", {})
        world_grounding = payload.get("world_grounding", {})

        warnings: List[str] = []

        if not character_seed:
            warnings.append("No character_seed provided; family engine used default draft family values.")

        character_id = character_seed.get("character_id") or origin_profile.get("character_id") or f"char_{uuid4().hex[:12]}"
        social_class = character_seed.get("social_class") or origin_profile.get("social_class", "commoner")
        family_name_status = character_seed.get("family_name_status") or self._infer_family_name_status(origin_profile)

        family_profile = FamilyProfile(
            family_id=f"fam_{uuid4().hex[:12]}",
            character_id=character_id,
            family_name=self._family_name(character_seed, family_name_status, social_class),
            family_status=self._family_status(family_name_status, social_class),
            family_reputation=self._family_reputation(family_name_status, social_class, origin_profile),
            family_ideology=self._family_ideology(social_class, character_seed),
            family_debt=self._family_debt(social_class, family_name_status, origin_profile),
            family_secrets=self._family_secrets(social_class, family_name_status, character_seed, world_constraints),
            inherited_trauma=self._inherited_trauma(social_class, family_name_status, character_seed),
            inherited_privilege=self._inherited_privilege(social_class, family_name_status),
            inherited_obligations=self._inherited_obligations(social_class, family_name_status, character_seed),
            guardians=self._guardians(character_seed, social_class, family_name_status),
            parents=self._parents(character_seed, social_class, family_name_status),
            siblings=self._siblings(character_seed, social_class),
            other_relatives=self._other_relatives(social_class, family_name_status),
            family_allies=self._family_allies(social_class, family_name_status),
            family_enemies=self._family_enemies(social_class, family_name_status, world_constraints),
            family_artifact_links=self._family_artifacts(social_class, family_name_status, world_grounding),
        )

        family_graph = self._build_family_graph(family_profile)
        family_pressure = self._build_family_pressure(family_profile, origin_profile, character_seed)
        family_story_hooks = self._build_family_story_hooks(family_profile, family_pressure, character_seed)
        next_engine_payload = self._build_next_engine_payload(
            character_seed=character_seed,
            origin_profile=origin_profile,
            family_profile=family_profile,
            family_pressure=family_pressure,
            family_story_hooks=family_story_hooks,
        )

        return self.build_result(
            success=True,
            data={
                "family_profile": family_profile.model_dump(),
                "family_graph": family_graph,
                "family_pressure": family_pressure,
                "family_story_hooks": family_story_hooks,
                "next_engine_payload": next_engine_payload,
                "family_summary": {
                    "character_id": character_id,
                    "family_name": family_profile.family_name,
                    "family_status": family_profile.family_status,
                    "family_secret_count": len(family_profile.family_secrets),
                    "family_debt_count": len(family_profile.family_debt),
                    "guardian_count": len(family_profile.guardians),
                    "parent_count": len(family_profile.parents),
                    "sibling_count": len(family_profile.siblings),
                    "has_family_artifact": len(family_profile.family_artifact_links) > 0,
                    "ready_for_psychology_engine": True,
                    "ready_for_trauma_engine": True,
                    "ready_for_legacy_engine_later": True,
                },
                "training_notes": [
                    "Family profiles create causal pressure for psychology, memory, goals, and relationship simulation.",
                    "Family secrets should create consequences, not decorative mystery.",
                    "Family reputation and legal trust connect Chunk 3 characters back to Chunk 2 law and society.",
                    "Later training data should preserve family-pressure labels for character arc modeling.",
                ],
            },
            warnings=warnings,
            errors=[],
            generated_object_ids=[family_profile.family_id],
        )

    def _infer_family_name_status(self, origin_profile: Dict[str, Any]) -> str:
        trust = origin_profile.get("family_name_trust")

        if trust is None:
            return "unknown"

        if trust >= 0.8:
            return "trusted"

        if trust <= 0.1:
            return "erased"

        if trust <= 0.3:
            return "distrusted"

        return "recognized"

    def _family_name(self, character_seed: Dict[str, Any], family_name_status: str, social_class: str) -> str:
        name = character_seed.get("name", "")

        if " " in name:
            return name.split()[-1]

        if family_name_status == "erased":
            return "Unknown"

        if social_class in {"imperial_elite", "old_nobility"}:
            return "Vaul"

        if social_class == "academy_sponsored":
            return "Veyran"

        if social_class == "relic_miner":
            return "Ash"

        return "Reed"

    def _family_status(self, family_name_status: str, social_class: str) -> str:
        if family_name_status in {"erased", "unknown"}:
            return "erased_or_unverified"

        if family_name_status in {"forged"}:
            return "legally_false"

        if social_class in {"imperial_elite", "old_nobility"}:
            return "publicly_established"

        if social_class == "academy_sponsored":
            return "conditionally_recognized"

        if social_class in {"relic_miner", "underclass", "commoner"}:
            return "low_trust_working_family"

        return "recognized_but_low_power"

    def _family_reputation(self, family_name_status: str, social_class: str, origin_profile: Dict[str, Any]) -> str:
        if family_name_status == "trusted":
            return "legally credible and socially protected"

        if family_name_status == "distrusted":
            return "useful when needed but doubted in legal testimony"

        if family_name_status in {"erased", "unknown"}:
            return "records missing, testimony discounted, lineage vulnerable"

        if social_class in {"imperial_elite", "old_nobility"}:
            return "prestigious but politically watched"

        if social_class == "relic_miner":
            return "labor-stained and institutionally disposable"

        return "ordinary and easily ignored"

    def _family_ideology(self, social_class: str, character_seed: Dict[str, Any]) -> str:
        if character_seed.get("family_ideology"):
            return character_seed["family_ideology"]

        if social_class in {"imperial_elite", "old_nobility"}:
            return "family survival comes before private desire"

        if social_class == "academy_sponsored":
            return "merit must be performed perfectly or revoked"

        if social_class == "relic_miner":
            return "the family survives by enduring what elites refuse to see"

        if social_class in {"erased", "underclass"}:
            return "visibility is danger; truth must be carried quietly"

        return "protect the household even when institutions fail"

    def _family_debt(self, social_class: str, family_name_status: str, origin_profile: Dict[str, Any]) -> List[str]:
        debts = []

        if social_class == "academy_sponsored":
            debts.append("sponsor debt tied to academy access")

        if social_class == "relic_miner":
            debts.append("relic labor debt")

        if social_class in {"commoner", "artisan_class", "underclass"}:
            debts.append("household survival debt")

        if family_name_status in {"erased", "forged", "unknown", "distrusted"}:
            debts.append("legal trust debt")

        if origin_profile.get("forbidden_access"):
            debts.append("forbidden access exposure debt")

        return debts

    def _family_secrets(
        self,
        social_class: str,
        family_name_status: str,
        character_seed: Dict[str, Any],
        world_constraints: Dict[str, Any],
    ) -> List[str]:
        secrets = []

        if character_seed.get("family_secret"):
            secrets.append(character_seed["family_secret"])

        if family_name_status == "erased":
            secrets.append("family records were deliberately removed from public trust archives")

        if family_name_status == "forged":
            secrets.append("the family identity currently used is legally false")

        if social_class in {"imperial_elite", "old_nobility"}:
            secrets.append("family prestige depends on an edited historical account")

        if social_class == "academy_sponsored":
            secrets.append("sponsor support is tied to an undisclosed obligation")

        if social_class == "relic_miner":
            secrets.append("a family injury or death was hidden to protect relic production numbers")

        if world_constraints.get("family_name_affects_legal_trust") and family_name_status in {"distrusted", "erased", "unknown"}:
            secrets.append("a true family claim would change legal credibility")

        return sorted(set(secrets))

    def _inherited_trauma(self, social_class: str, family_name_status: str, character_seed: Dict[str, Any]) -> List[str]:
        trauma = []

        if social_class == "academy_sponsored":
            trauma.append("fear of public failure causing family disgrace")

        if social_class == "relic_miner":
            trauma.append("normalization of bodily sacrifice for survival")

        if social_class in {"erased", "underclass"}:
            trauma.append("learned fear of documentation and authority")

        if social_class in {"imperial_elite", "old_nobility"}:
            trauma.append("love confused with obedience to family reputation")

        if family_name_status in {"erased", "unknown"}:
            trauma.append("identity insecurity passed through silence")

        return trauma

    def _inherited_privilege(self, social_class: str, family_name_status: str) -> List[str]:
        privilege = []

        if social_class in {"imperial_elite", "old_nobility"}:
            privilege.extend(["legal credibility", "institutional access", "public benefit of the doubt"])

        if family_name_status == "trusted":
            privilege.append("trusted name opens official doors")

        if social_class == "academy_sponsored":
            privilege.append("conditional academic pathway")

        return privilege

    def _inherited_obligations(
        self,
        social_class: str,
        family_name_status: str,
        character_seed: Dict[str, Any],
    ) -> List[str]:
        obligations = []

        if social_class in {"imperial_elite", "old_nobility"}:
            obligations.extend(["protect family reputation", "marry or ally strategically", "preserve public legitimacy"])

        if social_class == "academy_sponsored":
            obligations.extend(["repay sponsor investment", "avoid public embarrassment"])

        if social_class == "relic_miner":
            obligations.extend(["send money home", "hide injury from officials"])

        if social_class in {"commoner", "underclass", "erased"}:
            obligations.extend(["protect family from institutional attention", "keep household afloat"])

        if family_name_status in {"erased", "forged", "unknown"}:
            obligations.append("avoid scrutiny of family records")

        return obligations

    def _guardians(self, character_seed: Dict[str, Any], social_class: str, family_name_status: str) -> List[FamilyMember]:
        if character_seed.get("guardians"):
            return [FamilyMember.model_validate(item) for item in character_seed["guardians"]]

        if social_class == "academy_sponsored":
            return [
                FamilyMember(
                    name="Sponsor Magister",
                    relation="academic sponsor",
                    status="alive",
                    emotional_closeness=-0.1,
                    conflict_level=0.65,
                    secret_link="controls access through debt",
                )
            ]

        if family_name_status in {"erased", "unknown"}:
            return [
                FamilyMember(
                    name="Unnamed Guardian",
                    relation="guardian",
                    status="missing",
                    emotional_closeness=0.2,
                    conflict_level=0.4,
                    secret_link="knows why records vanished",
                )
            ]

        return [
            FamilyMember(
                name="Household Elder",
                relation="guardian",
                status="alive",
                emotional_closeness=0.35,
                conflict_level=0.25,
            )
        ]

    def _parents(self, character_seed: Dict[str, Any], social_class: str, family_name_status: str) -> List[FamilyMember]:
        if character_seed.get("parents"):
            return [FamilyMember.model_validate(item) for item in character_seed["parents"]]

        if family_name_status in {"erased", "unknown"}:
            return [
                FamilyMember(name="Unknown mother", relation="mother", status="missing", emotional_closeness=0.1, conflict_level=0.3),
                FamilyMember(name="Unknown father", relation="father", status="unknown", emotional_closeness=-0.1, conflict_level=0.5),
            ]

        if social_class in {"imperial_elite", "old_nobility"}:
            return [
                FamilyMember(name="Lady of the House", relation="mother", status="alive", emotional_closeness=0.25, conflict_level=0.6),
                FamilyMember(name="Lord of the House", relation="father", status="alive", emotional_closeness=0.15, conflict_level=0.75),
            ]

        return [
            FamilyMember(name="Working parent", relation="parent", status="alive", emotional_closeness=0.55, conflict_level=0.25)
        ]

    def _siblings(self, character_seed: Dict[str, Any], social_class: str) -> List[FamilyMember]:
        if character_seed.get("siblings"):
            return [FamilyMember.model_validate(item) for item in character_seed["siblings"]]

        if social_class in {"imperial_elite", "old_nobility"}:
            return [
                FamilyMember(
                    name="Rival sibling",
                    relation="sibling",
                    status="alive",
                    emotional_closeness=0.1,
                    conflict_level=0.8,
                    secret_link="competes for inheritance",
                )
            ]

        if social_class in {"commoner", "relic_miner", "academy_sponsored"}:
            return [
                FamilyMember(
                    name="Younger sibling",
                    relation="sibling",
                    status="alive",
                    emotional_closeness=0.75,
                    conflict_level=0.2,
                    secret_link="depends on character success",
                )
            ]

        return []

    def _other_relatives(self, social_class: str, family_name_status: str) -> List[FamilyMember]:
        if family_name_status in {"erased", "unknown"}:
            return [
                FamilyMember(
                    name="Hidden relative",
                    relation="unknown relative",
                    status="hidden",
                    emotional_closeness=0.0,
                    conflict_level=0.5,
                    secret_link="holds missing family record",
                )
            ]

        return []

    def _family_allies(self, social_class: str, family_name_status: str) -> List[str]:
        if social_class in {"imperial_elite", "old_nobility"}:
            return ["old house allies", "academy board patrons"]

        if social_class == "academy_sponsored":
            return ["lower-rank study circle", "conditional sponsor network"]

        if social_class == "relic_miner":
            return ["mine workers", "injury widows", "labor runners"]

        if family_name_status in {"erased", "unknown"}:
            return ["false-name network", "underground document keepers"]

        return ["local household allies"]

    def _family_enemies(
        self,
        social_class: str,
        family_name_status: str,
        world_constraints: Dict[str, Any],
    ) -> List[str]:
        enemies = []

        if social_class in {"imperial_elite", "old_nobility"}:
            enemies.extend(["rival houses", "succession opponents"])

        if social_class == "academy_sponsored":
            enemies.extend(["elite students who resent sponsored entrants", "sponsor debt collectors"])

        if social_class == "relic_miner":
            enemies.extend(["mine office auditors", "relic quota enforcers"])

        if family_name_status in {"erased", "forged", "unknown", "distrusted"}:
            enemies.append("legal trust clerks")

        if world_constraints.get("family_name_affects_legal_trust"):
            enemies.append("archive officials")

        return sorted(set(enemies))

    def _family_artifacts(
        self,
        social_class: str,
        family_name_status: str,
        world_grounding: Dict[str, Any],
    ) -> List[str]:
        artifacts = []

        if family_name_status in {"erased", "unknown", "distrusted"}:
            artifacts.append("cracked family-name badge")

        if social_class in {"imperial_elite", "old_nobility"}:
            artifacts.append("sealed house signet")

        if social_class == "relic_miner":
            artifacts.append("relic-dusted work token")

        if "oath_religion" in world_grounding.get("world_dependency_tags", []):
            artifacts.append("broken oath thread")

        return artifacts

    def _build_family_graph(self, profile: FamilyProfile) -> Dict[str, Any]:
        nodes = []

        for member in profile.guardians + profile.parents + profile.siblings + profile.other_relatives:
            nodes.append(
                {
                    "name": member.name,
                    "relation": member.relation,
                    "status": member.status,
                    "emotional_closeness": member.emotional_closeness,
                    "conflict_level": member.conflict_level,
                    "secret_link": member.secret_link,
                }
            )

        return {
            "character_id": profile.character_id,
            "family_id": profile.family_id,
            "family_name": profile.family_name,
            "nodes": nodes,
            "edge_count": len(nodes),
            "highest_conflict_relation": self._highest_conflict_relation(nodes),
            "closest_relation": self._closest_relation(nodes),
        }

    def _highest_conflict_relation(self, nodes: List[Dict[str, Any]]) -> str | None:
        if not nodes:
            return None

        return max(nodes, key=lambda item: item["conflict_level"])["relation"]

    def _closest_relation(self, nodes: List[Dict[str, Any]]) -> str | None:
        if not nodes:
            return None

        return max(nodes, key=lambda item: item["emotional_closeness"])["relation"]

    def _build_family_pressure(
        self,
        profile: FamilyProfile,
        origin_profile: Dict[str, Any],
        character_seed: Dict[str, Any],
    ) -> Dict[str, Any]:
        pressure_score = 0.0

        pressure_score += len(profile.family_debt) * 0.08
        pressure_score += len(profile.family_secrets) * 0.1
        pressure_score += len(profile.inherited_obligations) * 0.05
        pressure_score += len(profile.inherited_trauma) * 0.07

        if profile.family_status in {"erased_or_unverified", "legally_false"}:
            pressure_score += 0.18

        if origin_profile.get("family_name_trust", 0.5) <= 0.25:
            pressure_score += 0.12

        pressure_score = round(min(1.0, pressure_score), 3)

        return {
            "family_pressure_score": pressure_score,
            "pressure_tier": self._pressure_tier(pressure_score),
            "main_pressure_sources": profile.family_debt + profile.family_secrets + profile.inherited_obligations,
            "likely_behavioral_effects": self._likely_behavioral_effects(profile, pressure_score),
            "relationship_risks": self._relationship_risks(profile),
            "plot_risks": self._plot_risks(profile),
        }

    def _pressure_tier(self, score: float) -> str:
        if score >= 0.75:
            return "extreme_family_pressure"
        if score >= 0.5:
            return "high_family_pressure"
        if score >= 0.25:
            return "moderate_family_pressure"
        return "low_family_pressure"

    def _likely_behavioral_effects(self, profile: FamilyProfile, pressure_score: float) -> List[str]:
        effects = []

        if pressure_score >= 0.5:
            effects.append("hesitates before choices that expose family records")

        if profile.family_status in {"erased_or_unverified", "legally_false"}:
            effects.append("guards identity details and avoids official scrutiny")

        if profile.inherited_obligations:
            effects.append("confuses personal desire with family duty")

        if profile.family_debt:
            effects.append("treats opportunity as something that must be repaid")

        if not effects:
            effects.append("family pressure is present but not dominant yet")

        return effects

    def _relationship_risks(self, profile: FamilyProfile) -> List[str]:
        risks = []

        if profile.family_secrets:
            risks.append("intimacy may expose family secrets")

        if profile.family_debt:
            risks.append("relationships can be manipulated through family debt")

        if profile.family_enemies:
            risks.append("allies may inherit family enemies")

        if profile.inherited_obligations:
            risks.append("romance or friendship may conflict with family duty")

        return risks

    def _plot_risks(self, profile: FamilyProfile) -> List[str]:
        risks = []

        if profile.family_secrets:
            risks.append("secret revelation can alter legal/social status")

        if profile.family_artifact_links:
            risks.append("family artifact can unlock memory, proof, or accusation")

        if profile.family_enemies:
            risks.append("family enemies can force public confrontation")

        if profile.inherited_obligations:
            risks.append("family obligation can block the character's true goal")

        return risks

    def _build_family_story_hooks(
        self,
        profile: FamilyProfile,
        pressure: Dict[str, Any],
        character_seed: Dict[str, Any],
    ) -> List[str]:
        hooks = []

        if profile.family_secrets:
            hooks.append(f"Family secret can reshape identity: {profile.family_secrets[0]}")

        if profile.family_debt:
            hooks.append(f"Family debt pressures choices: {profile.family_debt[0]}")

        if profile.family_artifact_links:
            hooks.append(f"Family artifact can become proof or symbol: {profile.family_artifact_links[0]}")

        if profile.family_enemies:
            hooks.append(f"Family enemy can trigger public conflict: {profile.family_enemies[0]}")

        if pressure["pressure_tier"] in {"high_family_pressure", "extreme_family_pressure"}:
            hooks.append("Family pressure should directly affect at least one major decision.")

        if character_seed.get("breakthrough_condition"):
            hooks.append("Family pressure can intensify the character's limit-break condition.")

        return hooks

    def _build_next_engine_payload(
        self,
        *,
        character_seed: Dict[str, Any],
        origin_profile: Dict[str, Any],
        family_profile: FamilyProfile,
        family_pressure: Dict[str, Any],
        family_story_hooks: List[str],
    ) -> Dict[str, Any]:
        merged_seed = dict(character_seed)
        merged_seed["family"] = family_profile.model_dump()
        merged_seed["family_pressure"] = family_pressure
        merged_seed["family_story_hooks"] = family_story_hooks

        return {
            "character_seed": merged_seed,
            "psychology_engine_payload": {
                "character_seed": merged_seed,
                "origin_profile": origin_profile,
                "family_profile": family_profile.model_dump(),
                "family_pressure": family_pressure,
                "family_story_hooks": family_story_hooks,
            },
            "trauma_engine_payload": {
                "character_seed": merged_seed,
                "inherited_trauma": family_profile.inherited_trauma,
                "family_secrets": family_profile.family_secrets,
                "family_pressure": family_pressure,
            },
            "legacy_engine_payload": {
                "character_seed": merged_seed,
                "family_profile": family_profile.model_dump(),
                "family_artifact_links": family_profile.family_artifact_links,
                "family_secrets": family_profile.family_secrets,
            },
        }

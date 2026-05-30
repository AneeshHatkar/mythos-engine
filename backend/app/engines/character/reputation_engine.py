from typing import Any, Dict, List
from uuid import uuid4

from backend.app.engines.base import BaseEngine
from backend.app.schemas.foundation import EngineRunResult


class ReputationEngine(BaseEngine):
    """Builds dynamic reputation state for a character.

    Reputation is not a static label. It changes by class, faction, rumor,
    institution, family name, memory, public behavior, secrecy, scandal, and
    relationship context.

    This engine prepares characters for Chunk 4 social simulation and later
    plot consequences.
    """

    engine_name = "character.reputation_engine"

    def run(self, payload: Dict[str, Any]) -> EngineRunResult:
        character_seed = payload.get("character_seed", {})
        origin_profile = payload.get("origin_profile") or character_seed.get("origin", {})
        family_profile = payload.get("family_profile") or character_seed.get("family", {})
        memory_records = payload.get("memory_records") or character_seed.get("memories", [])
        memory_network = payload.get("memory_network") or character_seed.get("memory_network", {})
        world_grounding = payload.get("world_grounding", {})
        world_constraints = payload.get("world_constraints", {})

        warnings: List[str] = []

        if not character_seed:
            warnings.append("No character_seed provided; reputation engine used draft defaults.")

        character_id = (
            character_seed.get("character_id")
            or origin_profile.get("character_id")
            or family_profile.get("character_id")
            or memory_network.get("character_id")
            or f"char_{uuid4().hex[:12]}"
        )

        reputation_profile = self._build_reputation_profile(
            character_id=character_id,
            character_seed=character_seed,
            origin_profile=origin_profile,
            family_profile=family_profile,
            memory_records=memory_records,
            memory_network=memory_network,
            world_grounding=world_grounding,
            world_constraints=world_constraints,
        )

        reputation_dynamics = self._build_reputation_dynamics(
            reputation_profile=reputation_profile,
            character_seed=character_seed,
            memory_records=memory_records,
            world_constraints=world_constraints,
        )

        rumor_network = self._build_rumor_network(
            character_id=character_id,
            reputation_profile=reputation_profile,
            family_profile=family_profile,
            memory_network=memory_network,
            character_seed=character_seed,
        )

        consequence_hooks = self._build_consequence_hooks(
            reputation_profile=reputation_profile,
            reputation_dynamics=reputation_dynamics,
            rumor_network=rumor_network,
            character_seed=character_seed,
        )

        next_engine_payload = self._build_next_engine_payload(
            character_seed=character_seed,
            reputation_profile=reputation_profile,
            reputation_dynamics=reputation_dynamics,
            rumor_network=rumor_network,
            consequence_hooks=consequence_hooks,
        )

        return self.build_result(
            success=True,
            data={
                "reputation_profile": reputation_profile,
                "reputation_dynamics": reputation_dynamics,
                "rumor_network": rumor_network,
                "consequence_hooks": consequence_hooks,
                "next_engine_payload": next_engine_payload,
                "reputation_summary": {
                    "character_id": character_id,
                    "public_reputation": reputation_profile["public_reputation"],
                    "institutional_reputation": reputation_profile["institutional_reputation"],
                    "elite_reputation": reputation_profile["elite_reputation"],
                    "commoner_reputation": reputation_profile["commoner_reputation"],
                    "reputation_volatility": reputation_profile["reputation_volatility"],
                    "rumor_count": len(rumor_network["active_rumors"]),
                    "has_social_consequence_hooks": len(consequence_hooks) > 0,
                    "ready_for_goal_engine": True,
                    "ready_for_relationship_simulation_later": True,
                    "ready_for_faction_simulation_later": True,
                },
                "training_notes": [
                    "Reputation creates social consequences for character actions.",
                    "Chunk 4 relationship simulation should treat reputation differently by audience.",
                    "Rumors can be true, false, partial, or weaponized by factions.",
                    "Future Chunk 8 can learn reputation shifts from curated event-social-response data.",
                ],
            },
            warnings=warnings,
            errors=[],
            generated_object_ids=[reputation_profile["reputation_id"]],
        )

    def _build_reputation_profile(
        self,
        *,
        character_id: str,
        character_seed: Dict[str, Any],
        origin_profile: Dict[str, Any],
        family_profile: Dict[str, Any],
        memory_records: List[Dict[str, Any]],
        memory_network: Dict[str, Any],
        world_grounding: Dict[str, Any],
        world_constraints: Dict[str, Any],
    ) -> Dict[str, Any]:
        social_class = character_seed.get("social_class") or origin_profile.get("social_class", "unknown")
        family_name_status = character_seed.get("family_name_status") or self._family_name_status_from_origin(origin_profile)
        role = character_seed.get("role", "draft_character")
        public_status = character_seed.get("public_status") or character_seed.get("identity", {}).get("public_status")
        family_status = family_profile.get("family_status", "unknown_family_status")

        base_public = self._base_public_score(social_class, family_name_status, role)
        institutional = self._institutional_score(social_class, family_name_status, world_constraints, character_seed)
        elite = self._elite_score(social_class, family_name_status, family_status)
        commoner = self._commoner_score(social_class, role, character_seed)
        family = self._family_score(family_profile, character_seed)
        peer = self._peer_score(character_seed, memory_records)
        enemy = self._enemy_threat_score(character_seed, origin_profile, family_profile)
        romantic = self._romantic_reputation(character_seed, memory_records, family_profile)
        faction = self._faction_reputation(character_seed, family_profile)

        exposure_risk = self._exposure_risk(
            character_seed=character_seed,
            origin_profile=origin_profile,
            family_profile=family_profile,
            memory_records=memory_records,
            world_grounding=world_grounding,
        )

        reputation_volatility = self._reputation_volatility(
            exposure_risk=exposure_risk,
            memory_records=memory_records,
            family_profile=family_profile,
            character_seed=character_seed,
        )

        return {
            "reputation_id": f"rep_{uuid4().hex[:12]}",
            "character_id": character_id,
            "public_reputation": self._clamp(base_public),
            "institutional_reputation": self._clamp(institutional),
            "elite_reputation": self._clamp(elite),
            "commoner_reputation": self._clamp(commoner),
            "family_reputation_score": self._clamp(family),
            "peer_reputation": self._clamp(peer),
            "enemy_threat_reputation": self._clamp(enemy),
            "romantic_reputation": self._clamp(romantic),
            "faction_reputation": self._clamp(faction),
            "exposure_risk": self._clamp(exposure_risk),
            "reputation_volatility": self._clamp(reputation_volatility),
            "public_labels": self._public_labels(social_class, family_name_status, role, public_status),
            "private_labels": self._private_labels(character_seed, family_profile, memory_records),
            "audience_biases": self._audience_biases(social_class, family_name_status, world_constraints),
            "reputation_assets": self._reputation_assets(character_seed, origin_profile, family_profile),
            "reputation_liabilities": self._reputation_liabilities(character_seed, origin_profile, family_profile, memory_records),
            "world_dependency_tags": world_grounding.get("world_dependency_tags", []),
        }

    def _family_name_status_from_origin(self, origin_profile: Dict[str, Any]) -> str:
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

    def _base_public_score(self, social_class: str, family_name_status: str, role: str) -> float:
        score = 0.45

        if social_class in {"imperial_elite", "old_nobility"}:
            score += 0.25

        if social_class in {"erased", "underclass", "relic_miner"}:
            score -= 0.18

        if social_class == "academy_sponsored":
            score += 0.05

        if family_name_status in {"trusted", "verified", "noble"}:
            score += 0.2

        if family_name_status in {"distrusted", "erased", "unknown", "forged"}:
            score -= 0.2

        if role in {"protagonist", "deuteragonist", "love_interest", "rival"}:
            score += 0.04

        if role in {"villain", "antagonist"}:
            score += 0.08

        return score

    def _institutional_score(
        self,
        social_class: str,
        family_name_status: str,
        world_constraints: Dict[str, Any],
        seed: Dict[str, Any],
    ) -> float:
        score = 0.42

        if social_class in {"imperial_elite", "old_nobility"}:
            score += 0.35

        if social_class == "academy_sponsored":
            score += 0.08

        if social_class in {"erased", "underclass", "commoner", "relic_miner"}:
            score -= 0.16

        if family_name_status in {"erased", "forged", "unknown", "distrusted"}:
            score -= 0.22

        if seed.get("scholarship") or seed.get("sponsor"):
            score += 0.1

        if seed.get("forged_identity") or seed.get("illegal_tutor"):
            score -= 0.12

        if world_constraints.get("family_name_affects_legal_trust") and family_name_status in {"erased", "unknown", "distrusted"}:
            score -= 0.1

        return score

    def _elite_score(self, social_class: str, family_name_status: str, family_status: str) -> float:
        score = 0.35

        if social_class in {"imperial_elite", "old_nobility"}:
            score += 0.45

        if social_class == "academy_sponsored":
            score += 0.05

        if family_status == "publicly_established":
            score += 0.15

        if family_status in {"erased_or_unverified", "legally_false"}:
            score -= 0.2

        if family_name_status in {"trusted", "noble"}:
            score += 0.1

        if family_name_status in {"erased", "distrusted", "unknown"}:
            score -= 0.15

        return score

    def _commoner_score(self, social_class: str, role: str, seed: Dict[str, Any]) -> float:
        score = 0.45

        if social_class in {"commoner", "relic_miner", "artisan_class", "borderfolk", "erased"}:
            score += 0.18

        if social_class in {"imperial_elite", "old_nobility"}:
            score -= 0.12

        if seed.get("protects_commoners") or "protects someone weaker" in str(seed).lower():
            score += 0.12

        if role in {"villain", "antagonist"}:
            score -= 0.08

        return score

    def _family_score(self, family_profile: Dict[str, Any], seed: Dict[str, Any]) -> float:
        score = 0.45

        status = family_profile.get("family_status", "")

        if status == "publicly_established":
            score += 0.25

        if status == "conditionally_recognized":
            score += 0.05

        if status in {"erased_or_unverified", "legally_false"}:
            score -= 0.22

        if family_profile.get("family_secrets"):
            score -= 0.08

        if family_profile.get("inherited_privilege"):
            score += 0.08

        if family_profile.get("family_debt"):
            score -= 0.05

        return score

    def _peer_score(self, seed: Dict[str, Any], memory_records: List[Dict[str, Any]]) -> float:
        score = 0.45

        if seed.get("role") in {"protagonist", "rival", "love_interest"}:
            score += 0.08

        if seed.get("skill_rarity") in {"rare", "elite", "legendary", "mythic", "anomaly", "S", "SS", "SSS"}:
            score += 0.1

        if any("public failure" in str(record).lower() for record in memory_records):
            score -= 0.07

        if any("protects someone weaker" in str(record).lower() for record in memory_records):
            score += 0.08

        return score

    def _enemy_threat_score(self, seed: Dict[str, Any], origin: Dict[str, Any], family: Dict[str, Any]) -> float:
        score = 0.2

        if seed.get("skill_rarity") in {"rare", "elite", "legendary", "mythic", "anomaly", "S", "SS", "SSS"}:
            score += 0.22

        if seed.get("destiny_type"):
            score += 0.18

        if seed.get("adaptability_type") or seed.get("breakthrough_condition"):
            score += 0.18

        if family.get("family_secrets"):
            score += 0.08

        if origin.get("forbidden_access"):
            score += 0.08

        return score

    def _romantic_reputation(self, seed: Dict[str, Any], memory_records: List[Dict[str, Any]], family: Dict[str, Any]) -> float:
        score = 0.42

        if seed.get("role") in {"love_interest", "protagonist", "rival", "deuteragonist"}:
            score += 0.1

        if any("trust" in str(record).lower() or "intimacy" in str(record).lower() for record in memory_records):
            score += 0.08

        if family.get("family_secrets"):
            score -= 0.06

        if seed.get("betrayal_triggers"):
            score -= 0.04

        return score

    def _faction_reputation(self, seed: Dict[str, Any], family: Dict[str, Any]) -> float:
        score = 0.38

        if seed.get("faction"):
            score += 0.18

        if seed.get("role") in {"villain", "antagonist", "mentor"}:
            score += 0.08

        if family.get("family_allies"):
            score += 0.08

        if family.get("family_enemies"):
            score -= 0.06

        return score

    def _exposure_risk(
        self,
        *,
        character_seed: Dict[str, Any],
        origin_profile: Dict[str, Any],
        family_profile: Dict[str, Any],
        memory_records: List[Dict[str, Any]],
        world_grounding: Dict[str, Any],
    ) -> float:
        score = 0.25

        if family_profile.get("family_secrets"):
            score += 0.18

        if origin_profile.get("forbidden_access"):
            score += 0.15

        if character_seed.get("forged_identity") or character_seed.get("illegal_tutor"):
            score += 0.18

        if character_seed.get("destiny_type"):
            score += 0.08

        if character_seed.get("adaptability_type") or character_seed.get("breakthrough_condition"):
            score += 0.12

        if "family_name_legal_trust" in world_grounding.get("world_dependency_tags", []):
            score += 0.08

        if any("secret" in str(record).lower() for record in memory_records):
            score += 0.07

        return score

    def _reputation_volatility(
        self,
        *,
        exposure_risk: float,
        memory_records: List[Dict[str, Any]],
        family_profile: Dict[str, Any],
        character_seed: Dict[str, Any],
    ) -> float:
        score = 0.25 + exposure_risk * 0.35

        if memory_records:
            max_weight = max([float(record.get("emotional_weight", 0.0)) for record in memory_records], default=0.0)
            score += max_weight * 0.15

        if family_profile.get("family_secrets"):
            score += 0.08

        if character_seed.get("skill_rarity") in {"anomaly", "mythic", "SS", "SSS"}:
            score += 0.08

        return score

    def _public_labels(self, social_class: str, family_name_status: str, role: str, public_status: Any) -> List[str]:
        labels = []

        if public_status:
            labels.append(str(public_status))

        if social_class == "academy_sponsored":
            labels.append("conditional merit student")

        if social_class in {"imperial_elite", "old_nobility"}:
            labels.append("high-status name")

        if social_class in {"erased", "underclass"}:
            labels.append("low-trust outsider")

        if social_class == "relic_miner":
            labels.append("labor-born survivor")

        if family_name_status in {"distrusted", "erased", "unknown"}:
            labels.append("legally questionable name")

        if role == "villain":
            labels.append("public authority")

        if role == "protagonist":
            labels.append("watched anomaly candidate")

        return sorted(set(labels)) or ["unclassified public figure"]

    def _private_labels(
        self,
        seed: Dict[str, Any],
        family_profile: Dict[str, Any],
        memory_records: List[Dict[str, Any]],
    ) -> List[str]:
        labels = []

        if seed.get("private_truth"):
            labels.append(seed["private_truth"])

        if family_profile.get("family_secrets"):
            labels.append("secret-burdened")

        if seed.get("breakthrough_condition"):
            labels.append("pressure-reactive")

        if any("betrayal" in str(record).lower() for record in memory_records):
            labels.append("betrayal-sensitive")

        if seed.get("destiny_type"):
            labels.append("destiny-marked")

        return sorted(set(labels)) or ["privately unresolved"]

    def _audience_biases(
        self,
        social_class: str,
        family_name_status: str,
        world_constraints: Dict[str, Any],
    ) -> Dict[str, str]:
        biases = {
            "family": "judges through inherited obligation",
            "peers": "judges through visible performance",
            "commoners": "judges through whether power protects or exploits",
            "elites": "judges through name, etiquette, and usefulness",
            "enemies": "judges through leverage potential",
            "romantic_interest": "judges through consistency under vulnerability",
        }

        if world_constraints.get("family_name_affects_legal_trust") or family_name_status in {"erased", "distrusted", "unknown"}:
            biases["legal_authorities"] = "judges truth through family-name credibility"

        if social_class == "academy_sponsored":
            biases["institutions"] = "judges as useful but revocable"

        elif social_class in {"imperial_elite", "old_nobility"}:
            biases["institutions"] = "judges as credible until scandal"

        else:
            biases["institutions"] = "judges through suspicion and documentation"

        return biases

    def _reputation_assets(
        self,
        seed: Dict[str, Any],
        origin: Dict[str, Any],
        family: Dict[str, Any],
    ) -> List[str]:
        assets = []

        if origin.get("education_access", 0.0) >= 0.6:
            assets.append("education access")

        if seed.get("skill_rarity") in {"rare", "elite", "legendary", "mythic", "anomaly", "S", "SS", "SSS"}:
            assets.append("rare skill visibility")

        if family.get("inherited_privilege"):
            assets.append("family privilege")

        if seed.get("destiny_type"):
            assets.append("destiny significance")

        if seed.get("protects_commoners") or "protects someone weaker" in str(seed).lower():
            assets.append("protective public action")

        return sorted(set(assets))

    def _reputation_liabilities(
        self,
        seed: Dict[str, Any],
        origin: Dict[str, Any],
        family: Dict[str, Any],
        memories: List[Dict[str, Any]],
    ) -> List[str]:
        liabilities = []

        if origin.get("forbidden_access"):
            liabilities.append("forbidden access")

        if family.get("family_secrets"):
            liabilities.append("family secrets")

        if family.get("family_debt"):
            liabilities.append("family debt")

        if seed.get("forged_identity"):
            liabilities.append("forged identity")

        if seed.get("adaptability_type") or seed.get("breakthrough_condition"):
            liabilities.append("uncontrolled breakthrough risk")

        if any("public failure" in str(memory).lower() for memory in memories):
            liabilities.append("public failure memory")

        return sorted(set(liabilities))

    def _build_reputation_dynamics(
        self,
        *,
        reputation_profile: Dict[str, Any],
        character_seed: Dict[str, Any],
        memory_records: List[Dict[str, Any]],
        world_constraints: Dict[str, Any],
    ) -> Dict[str, Any]:
        return {
            "reputation_update_rules": [
                {
                    "event": "public_skill_display",
                    "audience": "peers",
                    "positive_effects": {"peer_reputation": 0.12, "enemy_threat_reputation": 0.08},
                    "negative_effects": {"exposure_risk": 0.06},
                    "notes": "Rare skill increases admiration and threat perception.",
                },
                {
                    "event": "family_secret_exposed",
                    "audience": "institutions",
                    "positive_effects": {},
                    "negative_effects": {"institutional_reputation": -0.15, "public_reputation": -0.1},
                    "notes": "Secret exposure should create legal/social consequences.",
                },
                {
                    "event": "protects_powerless_person_publicly",
                    "audience": "commoners",
                    "positive_effects": {"commoner_reputation": 0.16, "romantic_reputation": 0.08},
                    "negative_effects": {"institutional_reputation": -0.06},
                    "notes": "Protective action builds grounded public support.",
                },
                {
                    "event": "caught_using_forbidden_access",
                    "audience": "legal_authorities",
                    "positive_effects": {},
                    "negative_effects": {"institutional_reputation": -0.2, "exposure_risk": 0.18},
                    "notes": "Forbidden access should never be consequence-free.",
                },
                {
                    "event": "trusted_person_defends_character",
                    "audience": "romantic_or_peer",
                    "positive_effects": {"romantic_reputation": 0.1, "peer_reputation": 0.06},
                    "negative_effects": {},
                    "notes": "Reputation can be repaired through witnessed loyalty.",
                },
            ],
            "audience_specific_repair_paths": self._repair_paths(reputation_profile),
            "audience_specific_damage_paths": self._damage_paths(reputation_profile),
            "volatile_audiences": self._volatile_audiences(reputation_profile),
        }

    def _repair_paths(self, profile: Dict[str, Any]) -> Dict[str, List[str]]:
        return {
            "institutions": [
                "produce verified record",
                "gain sponsor protection",
                "perform public service under scrutiny",
            ],
            "peers": [
                "show competence without humiliating others",
                "protect someone during public pressure",
            ],
            "commoners": [
                "take cost for someone lower status",
                "refuse elite comfort when it requires silence",
            ],
            "romantic_interest": [
                "tell truth before being forced",
                "protect vulnerability without demanding repayment",
            ],
        }

    def _damage_paths(self, profile: Dict[str, Any]) -> Dict[str, List[str]]:
        return {
            "institutions": [
                "forbidden access revealed",
                "family name trust challenged",
                "public disobedience classified as threat",
            ],
            "peers": [
                "public failure repeated",
                "rare skill seen as unfair advantage",
            ],
            "commoners": [
                "appears to side with elite institutions",
                "uses power without visible cost",
            ],
            "romantic_interest": [
                "uses secrecy to control another person's choice",
                "chooses reputation over truth",
            ],
        }

    def _volatile_audiences(self, profile: Dict[str, Any]) -> List[str]:
        volatile = []

        if profile["institutional_reputation"] <= 0.35 or profile["exposure_risk"] >= 0.55:
            volatile.append("institutions")

        if profile["elite_reputation"] <= 0.35:
            volatile.append("elites")

        if profile["commoner_reputation"] <= 0.35:
            volatile.append("commoners")

        if profile["romantic_reputation"] <= 0.4:
            volatile.append("romantic_interest")

        if profile["enemy_threat_reputation"] >= 0.55:
            volatile.append("enemies")

        return volatile

    def _build_rumor_network(
        self,
        *,
        character_id: str,
        reputation_profile: Dict[str, Any],
        family_profile: Dict[str, Any],
        memory_network: Dict[str, Any],
        character_seed: Dict[str, Any],
    ) -> Dict[str, Any]:
        rumors = []

        if "family secrets" in reputation_profile["reputation_liabilities"]:
            rumors.append(
                {
                    "rumor_id": f"rumor_{uuid4().hex[:8]}",
                    "claim": "Their family name is not what official records say.",
                    "truth_status": "partial",
                    "source": "archive whispers",
                    "spread_risk": 0.72,
                    "damage_target": "institutional_reputation",
                }
            )

        if "rare skill visibility" in reputation_profile["reputation_assets"]:
            rumors.append(
                {
                    "rumor_id": f"rumor_{uuid4().hex[:8]}",
                    "claim": "Their ability is either illegal, sponsored, or impossible.",
                    "truth_status": "unknown",
                    "source": "peer network",
                    "spread_risk": 0.64,
                    "damage_target": "peer_reputation",
                }
            )

        if "uncontrolled breakthrough risk" in reputation_profile["reputation_liabilities"]:
            rumors.append(
                {
                    "rumor_id": f"rumor_{uuid4().hex[:8]}",
                    "claim": "Something happens around them when people are cornered.",
                    "truth_status": "partial",
                    "source": "witness accounts",
                    "spread_risk": 0.68,
                    "damage_target": "exposure_risk",
                }
            )

        if not rumors:
            rumors.append(
                {
                    "rumor_id": f"rumor_{uuid4().hex[:8]}",
                    "claim": "No one agrees on what kind of person they are yet.",
                    "truth_status": "ambiguous",
                    "source": "general public",
                    "spread_risk": 0.25,
                    "damage_target": "public_reputation",
                }
            )

        rumor_sources = sorted(set([rumor["source"] for rumor in rumors]))

        return {
            "character_id": character_id,
            "active_rumors": rumors,
            "rumor_sources": rumor_sources,
            "highest_spread_risk": max([rumor["spread_risk"] for rumor in rumors], default=0.0),
            "memory_linked_triggers": list(memory_network.get("trigger_index", {}).keys())[:10],
            "rumor_control_options": [
                "deny publicly",
                "redirect with partial truth",
                "let trusted person speak",
                "produce proof",
                "weaponize counter-rumor",
            ],
            "rumor_simulation_ready": True,
        }

    def _build_consequence_hooks(
        self,
        *,
        reputation_profile: Dict[str, Any],
        reputation_dynamics: Dict[str, Any],
        rumor_network: Dict[str, Any],
        character_seed: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        hooks = []

        if reputation_profile["exposure_risk"] >= 0.55:
            hooks.append(
                {
                    "hook_type": "exposure_event",
                    "description": "A public event can expose secret, forbidden access, family truth, or anomaly behavior.",
                    "affected_audiences": ["institutions", "peers", "enemies"],
                    "story_use": "midpoint pressure or act-two reversal",
                }
            )

        if reputation_profile["enemy_threat_reputation"] >= 0.55:
            hooks.append(
                {
                    "hook_type": "enemy_attention",
                    "description": "Enemies begin treating the character as strategically dangerous.",
                    "affected_audiences": ["enemies", "factions"],
                    "story_use": "antagonist escalation",
                }
            )

        if reputation_profile["commoner_reputation"] >= reputation_profile["institutional_reputation"] + 0.15:
            hooks.append(
                {
                    "hook_type": "people_vs_institution_split",
                    "description": "Common people trust the character more than institutions do.",
                    "affected_audiences": ["commoners", "institutions"],
                    "story_use": "public loyalty conflict",
                }
            )

        if rumor_network["highest_spread_risk"] >= 0.6:
            hooks.append(
                {
                    "hook_type": "rumor_cascade",
                    "description": "Rumors can spread fast enough to change access, trust, romance, or faction safety.",
                    "affected_audiences": rumor_network["rumor_sources"],
                    "story_use": "social complication or scandal arc",
                }
            )

        if not hooks:
            hooks.append(
                {
                    "hook_type": "reputation_unformed",
                    "description": "The character's reputation is still unstable and can be shaped by first major public action.",
                    "affected_audiences": ["peers", "public"],
                    "story_use": "early identity establishment",
                }
            )

        return hooks

    def _build_next_engine_payload(
        self,
        *,
        character_seed: Dict[str, Any],
        reputation_profile: Dict[str, Any],
        reputation_dynamics: Dict[str, Any],
        rumor_network: Dict[str, Any],
        consequence_hooks: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        merged_seed = dict(character_seed)
        merged_seed["reputation"] = reputation_profile
        merged_seed["reputation_dynamics"] = reputation_dynamics
        merged_seed["rumor_network"] = rumor_network
        merged_seed["reputation_consequence_hooks"] = consequence_hooks

        return {
            "character_seed": merged_seed,
            "goal_engine_payload": {
                "character_seed": merged_seed,
                "reputation_profile": reputation_profile,
                "consequence_hooks": consequence_hooks,
            },
            "moral_engine_payload": {
                "character_seed": merged_seed,
                "reputation_profile": reputation_profile,
                "reputation_dynamics": reputation_dynamics,
            },
            "relationship_simulation_payload_later": {
                "character_id": reputation_profile["character_id"],
                "reputation_profile": reputation_profile,
                "rumor_network": rumor_network,
                "consequence_hooks": consequence_hooks,
            },
            "plot_engine_payload_later": {
                "character_id": reputation_profile["character_id"],
                "reputation_consequence_hooks": consequence_hooks,
                "rumor_network": rumor_network,
            },
        }

    def _clamp(self, value: float) -> float:
        return round(max(0.0, min(1.0, value)), 3)

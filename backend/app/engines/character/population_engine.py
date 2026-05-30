from typing import Any, Dict, List

from backend.app.engines.base import BaseEngine
from backend.app.schemas.character import PopulationGroup
from backend.app.schemas.foundation import EngineRunResult


class PopulationEngine(BaseEngine):
    """Generates population distributions for the Character Intelligence Layer.

    This engine prevents MythOS from creating worlds where every person is a
    protagonist, genius, destined anomaly, elite noble, or overpowered fighter.

    It creates ordinary population structure first, then allows later engines
    to sample believable characters from that structure.
    """

    engine_name = "character.population_engine"

    def run(self, payload: Dict[str, Any]) -> EngineRunResult:
        world_state = payload.get("world_state", {})
        world_id = payload.get("world_id") or self._infer_world_id(world_state)
        world_name = payload.get("world_name") or self._infer_world_name(world_state)
        desired_complexity = payload.get("desired_complexity", "high")
        target_population = int(payload.get("target_population", 100_000))

        warnings: List[str] = []

        if not world_state:
            warnings.append("No world_state provided; population engine used Velmora-style defaults.")

        population_groups = self._build_population_groups(
            world_id=world_id,
            world_name=world_name,
            target_population=target_population,
            world_state=world_state,
            desired_complexity=desired_complexity,
        )

        rarity_controls = self._build_rarity_controls(population_groups)
        generation_guidance = self._build_generation_guidance(population_groups, rarity_controls)

        summary = self._build_summary(
            world_id=world_id,
            world_name=world_name,
            target_population=target_population,
            population_groups=population_groups,
            rarity_controls=rarity_controls,
        )

        return self.build_result(
            success=True,
            data={
                "population_groups": [group.model_dump() for group in population_groups],
                "population_summary": summary,
                "rarity_controls": rarity_controls,
                "character_generation_guidance": generation_guidance,
                "training_notes": [
                    "Population distributions help future models learn ordinary-to-rare ratios.",
                    "Destiny density and rare skill density prevent every generated character from becoming exceptional.",
                    "Later Chunk 8 can learn statistical character distributions from curated datasets.",
                    "Population groups should condition Character Genesis rather than merely decorate outputs.",
                ],
            },
            warnings=warnings,
            errors=[],
            generated_object_ids=[group.group_id for group in population_groups],
        )

    def _infer_world_id(self, world_state: Dict[str, Any]) -> str:
        identity = world_state.get("identity", {}) if isinstance(world_state, dict) else {}
        return identity.get("world_id") or identity.get("id") or "world_default"

    def _infer_world_name(self, world_state: Dict[str, Any]) -> str:
        identity = world_state.get("identity", {}) if isinstance(world_state, dict) else {}
        return identity.get("world_name") or identity.get("name") or "Velmora"

    def _build_population_groups(
        self,
        *,
        world_id: str,
        world_name: str,
        target_population: int,
        world_state: Dict[str, Any],
        desired_complexity: str,
    ) -> List[PopulationGroup]:
        pressure_terms = self._extract_pressure_terms(world_state)

        base_groups = [
            {
                "suffix": "imperial_elite",
                "name": "Imperial elite houses",
                "region": "capital",
                "social_class": "imperial_elite",
                "occupation_roles": ["minister", "academy patron", "oath court sponsor"],
                "factions": ["capital court", "elite academy boards"],
                "percentage": 1.5,
                "education": 0.98,
                "wealth": 0.98,
                "trust": 0.96,
                "danger": 0.25,
                "destiny": 0.015,
                "rare_skill": 0.08,
                "function": ["power brokers", "legal trust holders", "antagonist pool"],
            },
            {
                "suffix": "old_nobility",
                "name": "Old noble families",
                "region": "capital and estates",
                "social_class": "old_nobility",
                "occupation_roles": ["heir", "duelist", "academy prefect", "estate officer"],
                "factions": ["old houses", "academy honor societies"],
                "percentage": 3.5,
                "education": 0.92,
                "wealth": 0.9,
                "trust": 0.88,
                "danger": 0.35,
                "destiny": 0.02,
                "rare_skill": 0.07,
                "function": ["rivals", "love interests", "elite allies", "public pressure"],
            },
            {
                "suffix": "academy_sponsored",
                "name": "Academy-sponsored strivers",
                "region": "academy districts",
                "social_class": "academy_sponsored",
                "occupation_roles": ["scholarship student", "exam candidate", "archive aide"],
                "factions": ["academy", "sponsor houses"],
                "percentage": 4.0,
                "education": 0.72,
                "wealth": 0.35,
                "trust": 0.5,
                "danger": 0.55,
                "destiny": 0.035,
                "rare_skill": 0.06,
                "function": ["protagonist pool", "rival pool", "class tension"],
            },
            {
                "suffix": "merchant_professional",
                "name": "Merchant and professional families",
                "region": "capital trade wards",
                "social_class": "professional_class",
                "occupation_roles": ["merchant", "scribe", "doctor", "law clerk", "accountant"],
                "factions": ["trade guilds", "civic offices"],
                "percentage": 11.0,
                "education": 0.6,
                "wealth": 0.55,
                "trust": 0.58,
                "danger": 0.32,
                "destiny": 0.01,
                "rare_skill": 0.025,
                "function": ["supporting cast", "resource access", "civil society"],
            },
            {
                "suffix": "artisans_workers",
                "name": "Artisans and urban workers",
                "region": "urban wards",
                "social_class": "artisan_class",
                "occupation_roles": ["craft worker", "printer", "cook", "messenger", "tailor"],
                "factions": ["guilds", "local unions", "neighborhood shrines"],
                "percentage": 21.0,
                "education": 0.35,
                "wealth": 0.25,
                "trust": 0.4,
                "danger": 0.48,
                "destiny": 0.006,
                "rare_skill": 0.015,
                "function": ["ordinary life", "rumor network", "working pressure"],
            },
            {
                "suffix": "relic_miners",
                "name": "Relic-mining labor populations",
                "region": "relic-mining cities",
                "social_class": "relic_miner",
                "occupation_roles": ["miner", "hauler", "refiner", "injury worker", "union runner"],
                "factions": ["mine offices", "labor circles", "underground market"],
                "percentage": 16.0,
                "education": 0.18,
                "wealth": 0.12,
                "trust": 0.22,
                "danger": 0.86,
                "destiny": 0.012,
                "rare_skill": 0.02,
                "function": ["civilization cost", "revolt pressure", "trauma exposure"],
            },
            {
                "suffix": "commoners",
                "name": "General commoner households",
                "region": "towns and outer districts",
                "social_class": "commoner",
                "occupation_roles": ["farmer", "porter", "servant", "market worker", "stable hand"],
                "factions": ["local shrines", "market networks"],
                "percentage": 28.0,
                "education": 0.22,
                "wealth": 0.18,
                "trust": 0.28,
                "danger": 0.5,
                "destiny": 0.006,
                "rare_skill": 0.012,
                "function": ["ordinary citizens", "family pressure", "social grounding"],
            },
            {
                "suffix": "borderfolk",
                "name": "Borderfolk and ruin-adjacent settlements",
                "region": "border ruins",
                "social_class": "borderfolk",
                "occupation_roles": ["scout", "ruin guide", "smuggler", "border guard", "healer"],
                "factions": ["border militias", "ruin clans", "smuggling routes"],
                "percentage": 8.0,
                "education": 0.28,
                "wealth": 0.2,
                "trust": 0.18,
                "danger": 0.75,
                "destiny": 0.018,
                "rare_skill": 0.035,
                "function": ["survivors", "secret knowledge", "frontier conflict"],
            },
            {
                "suffix": "underclass_erased",
                "name": "Erased, undocumented, and underclass people",
                "region": "underground market",
                "social_class": "erased",
                "occupation_roles": ["forger", "runner", "illegal tutor", "black-market broker"],
                "factions": ["underground market", "false-name networks"],
                "percentage": 7.0,
                "education": 0.12,
                "wealth": 0.08,
                "trust": 0.02,
                "danger": 0.82,
                "destiny": 0.014,
                "rare_skill": 0.03,
                "function": ["hidden knowledge", "identity conflict", "survival cast"],
            },
        ]

        if "academy" in pressure_terms:
            self._boost_group(base_groups, "academy_sponsored", "education", 0.05)
            self._boost_group(base_groups, "academy_sponsored", "destiny", 0.01)

        if "relic" in pressure_terms or "mining" in pressure_terms:
            self._boost_group(base_groups, "relic_miners", "danger", 0.05)
            self._boost_group(base_groups, "relic_miners", "destiny", 0.004)

        if "border" in pressure_terms:
            self._boost_group(base_groups, "borderfolk", "danger", 0.05)
            self._boost_group(base_groups, "borderfolk", "rare_skill", 0.01)

        if desired_complexity in {"god_level", "research_grade"}:
            self._boost_group(base_groups, "underclass_erased", "destiny", 0.004)
            self._boost_group(base_groups, "academy_sponsored", "rare_skill", 0.01)

        groups: List[PopulationGroup] = []

        for item in base_groups:
            group_id = f"pop_{world_name.lower().replace(' ', '_')}_{item['suffix']}"
            estimated_count = int(target_population * (item["percentage"] / 100.0))

            groups.append(
                PopulationGroup(
                    group_id=group_id,
                    world_id=world_id,
                    group_name=item["name"],
                    region=item["region"],
                    social_class=item["social_class"],
                    occupation_roles=item["occupation_roles"],
                    faction_affiliations=item["factions"],
                    estimated_count=estimated_count,
                    percentage_of_population=item["percentage"],
                    education_access=min(1.0, item["education"]),
                    wealth_access=min(1.0, item["wealth"]),
                    legal_trust_level=min(1.0, item["trust"]),
                    danger_exposure=min(1.0, item["danger"]),
                    destiny_density=min(1.0, item["destiny"]),
                    rare_skill_density=min(1.0, item["rare_skill"]),
                    narrative_function=item["function"],
                )
            )

        return groups

    def _extract_pressure_terms(self, world_state: Dict[str, Any]) -> str:
        return str(world_state).lower()

    def _boost_group(self, groups: List[Dict[str, Any]], suffix: str, field: str, amount: float) -> None:
        for group in groups:
            if group["suffix"] == suffix:
                group[field] = min(1.0, group[field] + amount)

    def _build_rarity_controls(self, population_groups: List[PopulationGroup]) -> Dict[str, Any]:
        total_population = sum(group.estimated_count for group in population_groups)

        estimated_destiny_bearers = sum(
            int(group.estimated_count * group.destiny_density)
            for group in population_groups
        )

        estimated_rare_skill_people = sum(
            int(group.estimated_count * group.rare_skill_density)
            for group in population_groups
        )

        elite_population = sum(
            group.estimated_count
            for group in population_groups
            if group.social_class in {"imperial_elite", "old_nobility"}
        )

        ordinary_population = sum(
            group.estimated_count
            for group in population_groups
            if group.social_class in {"commoner", "artisan_class", "professional_class"}
        )

        return {
            "total_population_modeled": total_population,
            "estimated_destiny_bearers": estimated_destiny_bearers,
            "estimated_rare_skill_people": estimated_rare_skill_people,
            "elite_population": elite_population,
            "ordinary_population": ordinary_population,
            "destiny_ratio": round(estimated_destiny_bearers / total_population, 5) if total_population else 0.0,
            "rare_skill_ratio": round(estimated_rare_skill_people / total_population, 5) if total_population else 0.0,
            "recommended_major_character_destiny_cap": max(1, min(27, estimated_destiny_bearers // 100)),
            "recommended_main_cast_elite_cap_ratio": 0.35,
            "ordinary_character_requirement": "At least 30% of generated supporting cast should come from non-elite population groups.",
            "limit_break_anomaly_cap": max(1, estimated_destiny_bearers // 1000),
        }

    def _build_generation_guidance(
        self,
        population_groups: List[PopulationGroup],
        rarity_controls: Dict[str, Any],
    ) -> Dict[str, Any]:
        high_pressure_groups = [
            group.group_name
            for group in population_groups
            if group.danger_exposure >= 0.7
        ]

        low_access_groups = [
            group.group_name
            for group in population_groups
            if group.education_access <= 0.25
        ]

        high_trust_groups = [
            group.group_name
            for group in population_groups
            if group.legal_trust_level >= 0.8
        ]

        return {
            "main_character_sampling_strategy": [
                "Sample protagonists from pressure-bearing groups, not only elites.",
                "Use elite characters when institutional access matters.",
                "Use ordinary witnesses to reveal daily consequences of world systems.",
                "Use erased/underclass characters for identity, legality, and survival conflicts.",
            ],
            "anti_generic_rules": [
                "Do not make every major character noble, destined, or mythic.",
                "Rare skills require cost, limit, counter, and social consequence.",
                "Limit-break anomaly characters must be extremely rare.",
                "Ordinary characters must have agency, not only background utility.",
            ],
            "high_pressure_groups": high_pressure_groups,
            "low_access_groups": low_access_groups,
            "high_legal_trust_groups": high_trust_groups,
            "rarity_controls": rarity_controls,
        }

    def _build_summary(
        self,
        *,
        world_id: str,
        world_name: str,
        target_population: int,
        population_groups: List[PopulationGroup],
        rarity_controls: Dict[str, Any],
    ) -> Dict[str, Any]:
        modeled_population = sum(group.estimated_count for group in population_groups)

        return {
            "world_id": world_id,
            "world_name": world_name,
            "target_population": target_population,
            "modeled_population": modeled_population,
            "group_count": len(population_groups),
            "largest_group": max(population_groups, key=lambda group: group.estimated_count).group_name,
            "highest_danger_group": max(population_groups, key=lambda group: group.danger_exposure).group_name,
            "highest_education_access_group": max(population_groups, key=lambda group: group.education_access).group_name,
            "destiny_ratio": rarity_controls["destiny_ratio"],
            "rare_skill_ratio": rarity_controls["rare_skill_ratio"],
            "system_warning": (
                "Population model is deterministic v0.1. Later chunks can replace ratios "
                "with learned distributions from curated datasets."
            ),
        }

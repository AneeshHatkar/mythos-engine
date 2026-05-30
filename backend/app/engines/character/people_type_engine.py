from typing import Any, Dict, List

from backend.app.engines.base import BaseEngine
from backend.app.engines.character.character_registry_seed import CharacterRegistrySeedEngine
from backend.app.schemas.character import PeopleTypeProfile
from backend.app.schemas.foundation import EngineRunResult


class PeopleTypeEngine(BaseEngine):
    """Generates world-grounded people types and role classes.

    This is not a trope generator. It creates reusable character-type
    profiles that connect population groups, world constraints, social class,
    pressure responses, growth paths, adaptability, and anti-cliche rules.

    Later engines use these people types to generate protagonists, rivals,
    villains, love interests, mentors, ordinary citizens, simulation agents,
    and limit-break anomaly characters.
    """

    engine_name = "character.people_type_engine"

    def __init__(self) -> None:
        self.registry_engine = CharacterRegistrySeedEngine()

    def run(self, payload: Dict[str, Any]) -> EngineRunResult:
        world_state = payload.get("world_state", {})
        population_groups = payload.get("population_groups", [])
        target_roles = payload.get("target_roles", [])
        desired_complexity = payload.get("desired_complexity", "high")
        include_limit_break_types = payload.get("include_limit_break_types", True)

        warnings: List[str] = []

        if not world_state:
            warnings.append("No world_state provided; people types use general character intelligence defaults.")

        if not population_groups:
            warnings.append("No population_groups provided; people type engine used generic class compatibility.")

        registry = self.registry_engine.run({}).data["registry"]

        people_types = self._build_people_types(
            world_state=world_state,
            population_groups=population_groups,
            target_roles=target_roles,
            desired_complexity=desired_complexity,
            include_limit_break_types=include_limit_break_types,
            registry=registry,
        )

        role_map = self._build_role_map(people_types)
        sampling_guidance = self._build_sampling_guidance(people_types, population_groups)
        summary = self._build_summary(people_types, role_map)

        return self.build_result(
            success=True,
            data={
                "people_types": [item.model_dump() for item in people_types],
                "role_type_map": role_map,
                "people_type_summary": summary,
                "sampling_guidance": sampling_guidance,
                "training_notes": [
                    "People types are structured labels for future model conditioning and dataset tagging.",
                    "These profiles are world-grounded role classes, not generic trope labels.",
                    "Adaptability and limit-break eligibility are included so characters can evolve under pressure.",
                    "Later Chunk 8 can learn people-type distributions from curated character datasets.",
                ],
            },
            warnings=warnings,
            errors=[],
            generated_object_ids=[item.people_type_id for item in people_types],
        )

    def _build_people_types(
        self,
        *,
        world_state: Dict[str, Any],
        population_groups: List[Dict[str, Any]],
        target_roles: List[str],
        desired_complexity: str,
        include_limit_break_types: bool,
        registry: Dict[str, Any],
    ) -> List[PeopleTypeProfile]:
        world_text = str(world_state).lower()
        class_names = self._extract_social_classes(population_groups)

        types: List[PeopleTypeProfile] = []

        types.append(
            PeopleTypeProfile(
                people_type_id="ptype_hidden_kingmaker",
                name="Hidden Kingmaker",
                category="strategic_support",
                description=(
                    "A low-visibility person whose indirect choices determine who gains power, "
                    "truth, protection, or legitimacy."
                ),
                rarity="rare",
                compatible_roles=["protagonist", "deuteragonist", "mentor", "catalyst", "foil"],
                compatible_classes=self._compatible_classes(
                    class_names,
                    preferred=["commoner", "academy_sponsored", "erased", "professional_class"],
                ),
                compatible_destinies=["hidden_kingmaker", "crown_refuser", "prophecy_witness"],
                pressure_responses=[
                    "observes social systems before acting",
                    "protects through indirect moves",
                    "sacrifices visibility for influence",
                    "becomes dangerous when ignored too long",
                ],
                likely_wounds=["unseen worth", "performance-based love", "class disposability"],
                likely_goals=["prove the system is edited", "protect someone more visible", "choose who deserves power"],
                relationship_tendencies=[
                    "slow trust",
                    "protective from the shadows",
                    "attracted to people who see their private truth",
                ],
                corruption_risks=[
                    "manipulates outcomes without consent",
                    "believes only they can choose correctly",
                ],
                growth_paths=[
                    "moves from hidden influence to public moral choice",
                    "learns to be chosen rather than merely useful",
                ],
                anti_cliche_notes=[
                    "Must not become an effortless chessmaster.",
                    "Needs emotional cost for invisibility.",
                    "Should fail when attachment clouds pattern-reading.",
                ],
            )
        )

        types.append(
            PeopleTypeProfile(
                people_type_id="ptype_elite_truth_seeker",
                name="Elite Truth-Seeker",
                category="privileged_reformer",
                description=(
                    "A high-status character with access to institutions who begins questioning "
                    "the legitimacy of the system that benefits them."
                ),
                rarity="uncommon",
                compatible_roles=["protagonist", "rival", "love_interest", "deuteragonist"],
                compatible_classes=self._compatible_classes(
                    class_names,
                    preferred=["imperial_elite", "old_nobility", "academy_sponsored"],
                ),
                compatible_destinies=["oath_breaker", "crown_refuser", "world_catalyst"],
                pressure_responses=[
                    "uses privilege to ask forbidden questions",
                    "hesitates when truth threatens family status",
                    "breaks etiquette before breaking law",
                ],
                likely_wounds=["inherited guilt", "conditional family approval", "being used as symbol"],
                likely_goals=["learn what the family profited from", "prove reform is possible", "protect someone below their rank"],
                relationship_tendencies=[
                    "drawn to people harmed by their class",
                    "struggles to separate guilt from love",
                ],
                corruption_risks=[
                    "turns reform into self-redemption performance",
                    "expects forgiveness for awareness alone",
                ],
                growth_paths=[
                    "moves from guilt to material risk",
                    "gives up inherited safety to protect truth",
                ],
                anti_cliche_notes=[
                    "Privilege must have consequences, not just angst.",
                    "Truth-seeking must cost status, comfort, or family protection.",
                ],
            )
        )

        types.append(
            PeopleTypeProfile(
                people_type_id="ptype_failed_prodigy_rival",
                name="Failed Prodigy Rival",
                category="fallen_potential",
                description=(
                    "A once-celebrated talent whose public failure creates rivalry, envy, discipline, "
                    "and fear of being replaced."
                ),
                rarity="uncommon",
                compatible_roles=["rival", "deuteragonist", "antagonist", "foil"],
                compatible_classes=self._compatible_classes(
                    class_names,
                    preferred=["old_nobility", "academy_sponsored", "professional_class"],
                ),
                compatible_destinies=["failed_chosen_one", "destiny_thief", "legacy_carrier"],
                pressure_responses=[
                    "overtrains until collapse",
                    "resents effortless talent",
                    "masks fear with superiority",
                    "helps others only when no one sees",
                ],
                likely_wounds=["public humiliation", "failed destiny", "performance-based love"],
                likely_goals=["prove failure was temporary", "defeat the person who replaced them", "recover lost recognition"],
                relationship_tendencies=[
                    "competitive intimacy",
                    "respect earned through effort",
                    "fear of being pitied",
                ],
                corruption_risks=[
                    "steals opportunity from weaker characters",
                    "accepts forbidden shortcuts",
                ],
                growth_paths=[
                    "becomes mentor to someone with the same fear",
                    "learns worth outside rank and victory",
                ],
                anti_cliche_notes=[
                    "Cannot just be jealous; must have a wound tied to public loss.",
                    "Must have at least one admirable discipline or loyalty.",
                ],
            )
        )

        types.append(
            PeopleTypeProfile(
                people_type_id="ptype_institutional_villain",
                name="Institutional Villain",
                category="systemic_antagonist",
                description=(
                    "A villain whose threat comes from law, records, academy rules, courts, exams, "
                    "or public legitimacy."
                ),
                rarity="rare",
                compatible_roles=["villain", "antagonist", "mentor", "authority_figure"],
                compatible_classes=self._compatible_classes(
                    class_names,
                    preferred=["imperial_elite", "old_nobility", "professional_class"],
                ),
                compatible_destinies=["false_savior", "oath_breaker", "destiny_thief"],
                pressure_responses=[
                    "uses procedure as weapon",
                    "converts cruelty into policy language",
                    "forces victims to incriminate themselves",
                    "makes rebellion look illegal rather than moral",
                ],
                likely_wounds=["fear of chaos", "inherited ideology", "humiliation by disorder"],
                likely_goals=["preserve institutional continuity", "erase exceptions", "control public interpretation"],
                relationship_tendencies=[
                    "patronizes talented subordinates",
                    "rewards obedience as love",
                    "punishes intimacy as weakness",
                ],
                corruption_risks=[
                    "believes people are acceptable sacrifices for stability",
                    "rewrites truth for order",
                ],
                growth_paths=[
                    "doubles down when truth threatens legitimacy",
                    "can only redeem by destroying their own office",
                ],
                anti_cliche_notes=[
                    "Must have ideology beyond cruelty.",
                    "Should use systems, not random violence, as primary weapon.",
                ],
            )
        )

        types.append(
            PeopleTypeProfile(
                people_type_id="ptype_slow_burn_love_interest",
                name="Slow-Burn Love Interest With Independent Gravity",
                category="relationship_anchor",
                description=(
                    "A romantic character with independent goals, wounds, worldview, agency, and plot function."
                ),
                rarity="uncommon",
                compatible_roles=["love_interest", "deuteragonist", "rival", "foil"],
                compatible_classes=self._compatible_classes(
                    class_names,
                    preferred=["academy_sponsored", "old_nobility", "commoner", "borderfolk"],
                ),
                compatible_destinies=["prophecy_witness", "legacy_carrier", "crown_refuser"],
                pressure_responses=[
                    "withdraws when turned into emotional reward",
                    "chooses principle over romance when needed",
                    "tests whether love survives truth",
                ],
                likely_wounds=["being chosen only as symbol", "abandonment", "family obligation"],
                likely_goals=["protect personal agency", "complete own mission", "be loved without being possessed"],
                relationship_tendencies=[
                    "slow trust",
                    "high standards",
                    "emotionally precise conflict",
                    "refuses to exist only for protagonist growth",
                ],
                corruption_risks=[
                    "sacrifices selfhood to be needed",
                    "uses intimacy to control choices",
                ],
                growth_paths=[
                    "chooses selfhood and love without losing either",
                    "forces protagonist to grow without rescuing them from consequences",
                ],
                anti_cliche_notes=[
                    "Must have independent goal and failure consequence.",
                    "Must affect plot outside romance.",
                ],
            )
        )

        types.append(
            PeopleTypeProfile(
                people_type_id="ptype_ordinary_witness",
                name="Ordinary Witness",
                category="grounded_observer",
                description=(
                    "A non-special person whose perspective reveals what the world does to ordinary lives."
                ),
                rarity="common",
                compatible_roles=["ordinary_citizen", "witness", "side_character", "civilization_agent"],
                compatible_classes=self._compatible_classes(
                    class_names,
                    preferred=["commoner", "artisan_class", "professional_class", "relic_miner", "borderfolk"],
                ),
                compatible_destinies=["prophecy_witness"],
                pressure_responses=[
                    "protects small truths",
                    "notices hypocrisy in daily life",
                    "fears institutions but remembers details elites ignore",
                ],
                likely_wounds=["ignored suffering", "legal helplessness", "economic exhaustion"],
                likely_goals=["survive without being erased", "protect family", "tell one truth safely"],
                relationship_tendencies=[
                    "loyal through practical help",
                    "distrusts heroic speeches",
                    "values consistent action",
                ],
                corruption_risks=[
                    "sells truth for survival",
                    "normalizes injustice to stay safe",
                ],
                growth_paths=[
                    "becomes witness when silence costs someone else",
                    "finds courage in small public truth",
                ],
                anti_cliche_notes=[
                    "Ordinary must not mean irrelevant.",
                    "Needs agency, memory, and consequence.",
                ],
            )
        )

        if include_limit_break_types:
            types.append(
                PeopleTypeProfile(
                    people_type_id="ptype_limit_break_anomaly",
                    name="Limit-Break Anomaly",
                    category="adaptive_rule_exception",
                    description=(
                        "A rare character who can exceed normal limits under specific pressure, cost, "
                        "risk, and consequence."
                    ),
                    rarity="mythic",
                    compatible_roles=["protagonist", "antagonist", "villain", "catalyst", "game_companion"],
                    compatible_classes=self._compatible_classes(
                        class_names,
                        preferred=["academy_sponsored", "relic_miner", "borderfolk", "erased"],
                    ),
                    compatible_destinies=["anomaly_bearer", "world_catalyst", "failed_chosen_one"],
                    pressure_responses=[
                        "surges only when a threshold is crossed",
                        "destabilizes after exceeding limits",
                        "pays social, moral, physical, or emotional cost",
                    ],
                    likely_wounds=["unwanted power", "being used as symbol", "survivor guilt"],
                    likely_goals=["control the breakthrough", "avoid becoming a weapon", "protect someone without losing self"],
                    relationship_tendencies=[
                        "terrified of being needed only for power",
                        "bonds with people who see the cost",
                    ],
                    corruption_risks=[
                        "starts believing normal limits are for lesser people",
                        "uses cost as justification for cruelty",
                    ],
                    growth_paths=[
                        "learns when not to break limits",
                        "turns anomaly into responsibility rather than superiority",
                    ],
                    anti_cliche_notes=[
                        "Every limit-break requires condition, cost, risk, consequence, and post-break state change.",
                        "Must not solve every problem.",
                        "Should become more complicated after breakthrough, not simply stronger.",
                    ],
                )
            )

        if "religion" in world_text or "oath" in world_text:
            types.append(
                PeopleTypeProfile(
                    people_type_id="ptype_oath_burdened_believer",
                    name="Oath-Burdened Believer",
                    category="faith_pressure",
                    description=(
                        "A character whose faith, oath, ritual duty, or religious guilt creates moral pressure."
                    ),
                    rarity="uncommon",
                    compatible_roles=["protagonist", "mentor", "villain", "side_character", "foil"],
                    compatible_classes=self._compatible_classes(
                        class_names,
                        preferred=["commoner", "old_nobility", "professional_class", "borderfolk"],
                    ),
                    compatible_destinies=["oath_breaker", "prophecy_witness", "false_savior"],
                    pressure_responses=[
                        "treats promises as identity",
                        "experiences guilt before anger",
                        "confuses obedience with goodness",
                    ],
                    likely_wounds=["religious guilt", "broken oath", "fear of divine abandonment"],
                    likely_goals=["be worthy of the oath", "restore broken faith", "learn whether gods are silent or absent"],
                    relationship_tendencies=[
                        "loyal beyond reason",
                        "struggles with desire that contradicts duty",
                    ],
                    corruption_risks=[
                        "sanctifies harm as duty",
                        "obeys rituals over living people",
                    ],
                    growth_paths=[
                        "moves from obedience to chosen faith",
                        "breaks an oath to keep a deeper moral truth",
                    ],
                    anti_cliche_notes=[
                        "Faith must create choices, not just aesthetic symbolism.",
                    ],
                )
            )

        if target_roles:
            types = self._prioritize_for_target_roles(types, target_roles)

        return types

    def _extract_social_classes(self, population_groups: List[Dict[str, Any]]) -> List[str]:
        classes = []

        for group in population_groups:
            social_class = group.get("social_class")

            if social_class and social_class not in classes:
                classes.append(social_class)

        return classes

    def _compatible_classes(self, class_names: List[str], preferred: List[str]) -> List[str]:
        if not class_names:
            return preferred

        matched = [item for item in preferred if item in class_names]

        if matched:
            return matched

        return preferred[:3]

    def _prioritize_for_target_roles(
        self,
        people_types: List[PeopleTypeProfile],
        target_roles: List[str],
    ) -> List[PeopleTypeProfile]:
        target_set = set(target_roles)

        def priority(item: PeopleTypeProfile) -> int:
            return 0 if target_set & set(item.compatible_roles) else 1

        return sorted(people_types, key=priority)

    def _build_role_map(self, people_types: List[PeopleTypeProfile]) -> Dict[str, List[str]]:
        role_map: Dict[str, List[str]] = {}

        for people_type in people_types:
            for role in people_type.compatible_roles:
                role_map.setdefault(role, []).append(people_type.people_type_id)

        return role_map

    def _build_sampling_guidance(
        self,
        people_types: List[PeopleTypeProfile],
        population_groups: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        mythic_types = [
            item.people_type_id
            for item in people_types
            if item.rarity in {"mythic", "legendary"}
        ]

        common_types = [
            item.people_type_id
            for item in people_types
            if item.rarity == "common"
        ]

        pressure_groups = [
            group.get("group_name")
            for group in population_groups
            if group.get("danger_exposure", 0.0) >= 0.7
        ]

        return {
            "main_cast_guidance": [
                "Use no more than one mythic/anomaly people type in early main cast unless world rules justify it.",
                "Include at least one ordinary or grounded people type for social reality.",
                "Pair elite access characters with low-access characters to expose class systems.",
                "People types should condition psychology and goals, not replace them.",
            ],
            "mythic_or_anomaly_types": mythic_types,
            "common_grounding_types": common_types,
            "recommended_pressure_groups": [group for group in pressure_groups if group],
            "anti_cliche_rules": [
                "Every villain needs ideology, not just cruelty.",
                "Every love interest needs independent goals.",
                "Every limit-break character needs condition, cost, risk, and consequence.",
                "Every ordinary witness needs agency.",
            ],
        }

    def _build_summary(
        self,
        people_types: List[PeopleTypeProfile],
        role_map: Dict[str, List[str]],
    ) -> Dict[str, Any]:
        rarity_counts: Dict[str, int] = {}

        for people_type in people_types:
            rarity_counts[people_type.rarity] = rarity_counts.get(people_type.rarity, 0) + 1

        return {
            "people_type_count": len(people_types),
            "role_count": len(role_map),
            "rarity_counts": rarity_counts,
            "has_limit_break_type": any(
                item.people_type_id == "ptype_limit_break_anomaly"
                for item in people_types
            ),
            "has_ordinary_grounding_type": any(
                item.people_type_id == "ptype_ordinary_witness"
                for item in people_types
            ),
            "has_institutional_antagonist_type": any(
                item.people_type_id == "ptype_institutional_villain"
                for item in people_types
            ),
        }

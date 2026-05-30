from typing import Any, Dict, List

from backend.app.engines.base import BaseEngine
from backend.app.schemas.foundation import EngineRunResult
from backend.app.schemas.world import EconomyProfile, LawSystem, ResourceProfile


class EconomyLawEngine(BaseEngine):
    """Generates economy, resources, law, and justice logic.

    This is the material/legal layer of the world.

    It defines:
    - what people need
    - what is scarce
    - who controls resources
    - how institutions are funded
    - how debt traps people
    - what law protects
    - what law forbids
    - who law believes
    - how corruption actually works

    Later chunks will use this for character poverty, faction leverage,
    black-market arcs, villain incentives, rebellion triggers, romance class
    barriers, trial scenes, and civilization collapse logic.
    """

    engine_name = "world.economy_law_engine"

    def run(self, payload: Dict[str, Any]) -> EngineRunResult:
        seed_premise = payload.get("seed_premise", "")
        genre_tags = payload.get("genre_tags", [])
        tone_tags = payload.get("tone_tags", [])
        desired_complexity = payload.get("desired_complexity", "high")

        warnings: List[str] = []

        if not seed_premise:
            warnings.append(
                "No seed_premise provided; economy and law will use broad default structures."
            )

        economy = self._build_economy(
            seed_premise=seed_premise,
            genre_tags=genre_tags,
            tone_tags=tone_tags,
            desired_complexity=desired_complexity,
        )

        law = self._build_law(
            seed_premise=seed_premise,
            genre_tags=genre_tags,
            tone_tags=tone_tags,
            desired_complexity=desired_complexity,
        )

        return self.build_result(
            success=True,
            data={
                "economy": economy.model_dump(mode="json"),
                "law": law.model_dump(mode="json"),
                "training_notes": [
                    "Economy outputs are structured for future resource simulation and collapse modeling.",
                    "Law outputs are structured for future trial scenes, faction leverage, and social consequence checks.",
                    "Resource scarcity, debt, and legal loopholes should later feed character motivation and plot pressure.",
                    "This layer must be checked against demographics, power, geography, and institutions before training eligibility.",
                ],
            },
            warnings=warnings,
            errors=[],
            generated_object_ids=[],
        )

    def _build_economy(
        self,
        *,
        seed_premise: str,
        genre_tags: List[str],
        tone_tags: List[str],
        desired_complexity: str,
    ) -> EconomyProfile:
        seed = seed_premise.lower()

        is_academy = "academy" in seed or "dark_academy" in genre_tags
        is_empire = "empire" in seed or "political_fantasy" in genre_tags
        is_relic = "relic" in seed
        is_oath = "oath" in seed
        is_destiny = "destiny" in seed or "destined" in seed
        is_collapse = "collapse" in seed or "tragic" in tone_tags

        currency_system = (
            "The economy uses Crown Marks for public trade, House Ledgers for noble debt, "
            "and sealed promissory notes for academy sponsorship. Legal money and social debt "
            "are deliberately intertwined."
        )

        if is_oath:
            currency_system += (
                " Oath-backed contracts are treated as stronger than ordinary currency because breaking them can damage legal identity."
            )

        resources = [
            ResourceProfile(
                name="Crown Marks",
                resource_type="currency",
                scarcity_level=0.32,
                controlled_by=["tax offices", "licensed banks", "merchant houses"],
                economic_value="baseline trade currency",
                story_conflicts=[
                    "inflation after relic supply shocks",
                    "counterfeit marks in low markets",
                    "tax seizures in poor districts",
                ],
            ),
            ResourceProfile(
                name="Legal Credibility",
                resource_type="social_legal_resource",
                scarcity_level=0.78,
                controlled_by=["courts", "family registries", "academy records", "oath offices"],
                economic_value="determines who can borrow, testify, inherit, and enter elite institutions",
                story_conflicts=[
                    "erased families cannot prove ownership",
                    "commoner testimony ignored",
                    "blackmail through reputation records",
                ],
            ),
            ResourceProfile(
                name="Education Access",
                resource_type="institutional_resource",
                scarcity_level=0.84,
                controlled_by=["academy councils", "noble sponsors", "exam boards"],
                economic_value="converts talent into rank, salary, office, and marriage prospects",
                story_conflicts=[
                    "illegal tutoring",
                    "exam sabotage",
                    "sponsorship debt",
                    "class resentment",
                ],
            ),
            ResourceProfile(
                name="Healing Licenses",
                resource_type="medical_resource",
                scarcity_level=0.69,
                controlled_by=["healer guilds", "temples", "military hospitals", "academy clinics"],
                economic_value="keeps important people alive and useful",
                story_conflicts=[
                    "black-market medicine",
                    "healing denied by class",
                    "debt after treatment",
                    "forbidden treatment of condemned people",
                ],
            ),
        ]

        if is_relic:
            resources.extend(
                [
                    ResourceProfile(
                        name="Relic Ore and Memory-Stone",
                        resource_type="strategic_relic_resource",
                        scarcity_level=0.91,
                        controlled_by=[
                            "Relic Investment Consortium",
                            "mine governors",
                            "temple inspectors",
                            "academy research boards",
                        ],
                        economic_value="funds elite education, military protection, artifact production, and ritual authority",
                        story_conflicts=[
                            "mine-worker revolt",
                            "resource monopoly",
                            "artifact smuggling",
                            "religious contamination",
                            "relic debt",
                        ],
                    ),
                    ResourceProfile(
                        name="Certified Artifact Ownership",
                        resource_type="political_artifact_right",
                        scarcity_level=0.87,
                        controlled_by=["courts", "archivists", "noble houses", "artifact appraisers"],
                        economic_value="turns old objects into legal power, inheritance proof, and faction leverage",
                        story_conflicts=[
                            "forged ownership papers",
                            "stolen inheritance relic",
                            "artifact refuses legal owner",
                        ],
                    ),
                ]
            )

        if is_destiny:
            resources.append(
                ResourceProfile(
                    name="Destiny Sponsorship Rights",
                    resource_type="human_capital_control",
                    scarcity_level=0.96,
                    controlled_by=[
                        "Destiny Classification Board",
                        "academy councils",
                        "elite patrons",
                        "religious interpreters",
                    ],
                    economic_value="turns exceptional people into institutional assets before rivals can recruit them",
                    story_conflicts=[
                        "kidnapping gifted children",
                        "forced sponsorship",
                        "false ranking",
                        "auction-like patronage",
                    ],
                )
            )

        trade_routes = [
            "Relic Ridge convoy route to academy research districts",
            "Crown Road tax corridor between capital and border provinces",
            "Low Lantern black-market knowledge route",
            "healer-guild supply chain from temples to military hospitals",
            "student sponsorship payment route through noble banks",
        ]

        taxation_system = (
            "Taxes are collected through land dues, trade tariffs, academy certification fees, road permits, "
            "inheritance claims, and emergency levies. Taxes are lower for those with rank and harsher for those without representation."
        )

        debt_system = (
            "Debt is financial, social, legal, and sometimes spiritual. Poor families owe coin, minor houses owe reputation, "
            "students owe sponsors, nobles owe marriage favors, and relic users may owe forces not recognized by law."
        )

        labor_system = (
            "Labor is divided by class and region: mine workers carry physical risk, servants carry informational labor, "
            "students carry ambition debt, soldiers carry violence debt, and scholars carry institutional obedience."
        )

        black_markets = [
            "forged travel permits",
            "illegal textbooks",
            "uncertified healing",
            "relic fragments",
            "erased family records",
            "student exam answers",
            "private courier routes",
        ]

        if is_destiny:
            black_markets.append("hidden destiny test results")

        wealth_concentration = (
            "Wealth concentrates around founder houses, academy donors, relic investors, courts, and monopoly guilds. "
            "The poor possess labor and memory; the elite possess documents and permission."
        )

        academy_funding = (
            "Academies are funded by noble endowments, relic research grants, exam fees, state legitimacy contracts, "
            "sponsorship debt, and quiet black-market dependencies."
        )

        collapse_triggers = [
            "relic scarcity makes academy funding unstable",
            "debt defaults among minor houses expose elite weakness",
            "food price spikes turn class resentment into riots",
            "black-market knowledge undermines official education value",
            "healing inequality creates martyr figures",
        ]

        if is_destiny:
            collapse_triggers.append(
                "too many destiny-bearing people become too valuable for institutions to share peacefully"
            )

        if is_collapse:
            collapse_triggers.append(
                "the public realizes the economy depends on systems the law publicly condemns"
            )

        if desired_complexity in {"extreme", "god_level"}:
            collapse_triggers.extend(
                [
                    "resource, law, religion, and class systems fail together instead of separately",
                    "economic pressure should later feed causality graph and civilization pressure engines",
                ]
            )

        return EconomyProfile(
            currency_system=currency_system,
            main_resources=resources,
            trade_routes=trade_routes,
            taxation_system=taxation_system,
            debt_system=debt_system,
            labor_system=labor_system,
            black_markets=black_markets,
            wealth_concentration=wealth_concentration,
            academy_or_institution_funding=academy_funding,
            collapse_triggers=collapse_triggers,
        )

    def _build_law(
        self,
        *,
        seed_premise: str,
        genre_tags: List[str],
        tone_tags: List[str],
        desired_complexity: str,
    ) -> LawSystem:
        seed = seed_premise.lower()

        is_academy = "academy" in seed or "dark_academy" in genre_tags
        is_empire = "empire" in seed or "political_fantasy" in genre_tags
        is_relic = "relic" in seed
        is_oath = "oath" in seed
        is_destiny = "destiny" in seed or "destined" in seed
        is_magic = "magic" in seed

        legal_summary = (
            "Law presents itself as neutral order, but in practice it converts birth, documents, education, "
            "wealth, oath-status, and institutional usefulness into different levels of protection."
        )

        if is_oath:
            legal_summary += (
                " Oath-law makes promises legally alive: breaking the wrong vow can damage inheritance, rank, and testimony rights."
            )

        legal_classes = [
            "Founder-protected citizens",
            "ranked noble citizens",
            "licensed scholars and merchants",
            "registered workers and soldiers",
            "conditional students",
            "unregistered people",
            "exiled or erased persons",
        ]

        rights_by_birth = {
            "Founder-protected citizens": [
                "presumed credible in court",
                "private hearing rights",
                "inheritance protection",
                "academy sponsorship authority",
            ],
            "ranked noble citizens": [
                "court access",
                "property protection",
                "healing priority",
                "formal duel rights",
            ],
            "licensed scholars and merchants": [
                "contract rights",
                "limited testimony credibility",
                "business ownership",
                "travel permit eligibility",
            ],
            "registered workers and soldiers": [
                "basic protection",
                "wage claim rights",
                "military appeal rights",
            ],
            "conditional students": [
                "temporary institutional protection",
                "rank-dependent library access",
                "disciplinary appeal only through sponsors",
            ],
            "unregistered people": [
                "limited emergency protection",
                "almost no testimony credibility",
            ],
            "exiled or erased persons": [
                "no standard protection",
                "subject to detention, disappearance, or forced labor",
            ],
        }

        forbidden_acts = [
            "studying restricted knowledge without rank or sponsor",
            "forging family records",
            "crossing border checkpoints without permit",
            "selling uncertified healing",
            "publishing alternative founding histories",
            "impersonating a ranked citizen",
            "tampering with archive records",
        ]

        if is_magic:
            forbidden_acts.append("public use of royal-class magic without license")

        if is_relic:
            forbidden_acts.extend(
                [
                    "possessing relic fragments without certification",
                    "mining sacred relic zones without temple inspection",
                    "selling artifact ownership papers outside court registry",
                ]
            )

        if is_destiny:
            forbidden_acts.extend(
                [
                    "hiding a classified destiny-bearing person",
                    "falsifying destiny test results",
                    "unauthorized prophecy publication",
                ]
            )

        punishments = [
            "public rank reduction",
            "sponsorship removal",
            "travel permit suspension",
            "property seizure",
            "forced labor assignment",
            "memory credibility review",
            "academy expulsion",
            "exile to border service",
            "ritual apology under oath",
        ]

        if is_oath:
            punishments.append("oath-marking, which publicly records legal untrustworthiness")

        if is_relic:
            punishments.append("artifact confiscation and debt transfer")

        courts = [
            "High Crown Court",
            "Oath Court",
            "Academy Disciplinary Tribunal",
            "Inheritance Registry Court",
            "Border Military Court",
            "Market Magistrate Bench",
        ]

        if is_destiny:
            courts.append("Destiny Classification Review Chamber")

        law_enforcement_groups = [
            "Capital Watch",
            "Gate Permit Inspectors",
            "Academy Discipline Office",
            "Archive Wardens",
            "Oathguard",
            "Border March Battalions",
        ]

        legal_loopholes = [
            "A noble sponsor can temporarily legalize actions that would ruin a commoner.",
            "A sealed archive citation can overturn testimony if the judge accepts its rank.",
            "Marriage can convert some crimes into family disputes.",
            "Military emergency law can hide resource seizures.",
            "A person with no legal identity can be used without creating official liability.",
        ]

        if is_relic:
            legal_loopholes.append(
                "Relic ownership disputes can freeze criminal proceedings until artifact status is resolved."
            )

        if is_destiny:
            legal_loopholes.append(
                "Destiny classification can override ordinary court jurisdiction if officials claim public risk."
            )

        corruption_level = 0.74

        if is_empire:
            corruption_level += 0.04

        if is_relic:
            corruption_level += 0.05

        if is_destiny:
            corruption_level += 0.04

        if desired_complexity in {"extreme", "god_level"}:
            corruption_level += 0.03

        corruption_level = min(corruption_level, 0.94)

        if desired_complexity in {"extreme", "god_level"}:
            legal_loopholes.append(
                "Law should later be modeled as a tool factions use differently depending on class, evidence, money, and public symbolism."
            )

        return LawSystem(
            legal_summary=legal_summary,
            legal_classes=legal_classes,
            rights_by_birth=rights_by_birth,
            forbidden_acts=forbidden_acts,
            punishments=punishments,
            courts=courts,
            law_enforcement_groups=law_enforcement_groups,
            legal_loopholes=legal_loopholes,
            corruption_level=corruption_level,
        )

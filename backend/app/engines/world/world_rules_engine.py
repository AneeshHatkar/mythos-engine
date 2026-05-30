from typing import Any, Dict, List

from backend.app.engines.base import BaseEngine
from backend.app.schemas.foundation import EngineRunResult
from backend.app.schemas.world import (
    WorldBoundaryConstraintProfile,
    WorldContradictionIntent,
    WorldRule,
    WorldRuleSet,
)


class WorldRulesEngine(BaseEngine):
    """Generates the rule, boundary, and contradiction layer of a world.

    This engine defines what is possible, forbidden, restricted, expensive,
    socially punished, legally punished, spiritually punished, or unknown.

    The goal is not just to create cool rules. The goal is to create rules that
    future characters, factions, plots, mysteries, romances, and conflicts can
    obey, exploit, misunderstand, or break.
    """

    engine_name = "world.rules_engine"

    def run(self, payload: Dict[str, Any]) -> EngineRunResult:
        seed_premise = payload.get("seed_premise", "")
        genre_tags = payload.get("genre_tags", [])
        tone_tags = payload.get("tone_tags", [])
        desired_complexity = payload.get("desired_complexity", "high")

        warnings: List[str] = []

        if not seed_premise:
            warnings.append(
                "No seed_premise provided; rules will use broad default world logic."
            )

        rule_set = self._build_rule_set(
            seed_premise=seed_premise,
            genre_tags=genre_tags,
            tone_tags=tone_tags,
            desired_complexity=desired_complexity,
        )

        boundaries = self._build_boundaries(
            seed_premise=seed_premise,
            genre_tags=genre_tags,
            desired_complexity=desired_complexity,
        )

        contradiction_intent = self._build_contradiction_intent(
            seed_premise=seed_premise,
            genre_tags=genre_tags,
            desired_complexity=desired_complexity,
        )

        return self.build_result(
            success=True,
            data={
                "rules": rule_set.model_dump(mode="json"),
                "boundary_constraints": boundaries.model_dump(mode="json"),
                "contradiction_intent": contradiction_intent.model_dump(mode="json"),
            },
            warnings=warnings,
            errors=[],
            generated_object_ids=[],
        )

    def _build_rule_set(
        self,
        *,
        seed_premise: str,
        genre_tags: List[str],
        tone_tags: List[str],
        desired_complexity: str,
    ) -> WorldRuleSet:
        seed = seed_premise.lower()

        is_academy = "dark_academy" in genre_tags or "academy" in seed
        is_political = "political_fantasy" in genre_tags or "empire" in seed
        is_destiny = "destiny" in seed or "destined" in seed
        is_magic = "magic" in seed
        is_relic = "relic" in seed
        is_oath = "oath" in seed

        rule_set = WorldRuleSet()

        # Magic / power rules
        if is_magic or is_academy:
            rule_set.magic_rules.append(
                WorldRule(
                    rule_name="Licensed Power Access",
                    rule_category="magic",
                    description=(
                        "High-order power can only be legally practiced through approved institutions, "
                        "bloodline sponsorships, or state-sanctioned academies."
                    ),
                    applies_to=["students", "nobles", "commoners", "academy faculty"],
                    cost_or_limit=(
                        "Unlicensed use causes legal punishment, social exile, or forced enrollment."
                    ),
                    enforcement_mechanism=(
                        "Academy registries, magical audits, noble witnesses, and punishment courts."
                    ),
                    loopholes=[
                        "Forgotten rural traditions preserve unregistered forms of power.",
                        "Artifacts can temporarily bypass licensing rules.",
                    ],
                    forbidden_exceptions=[
                        "Commoners cannot publicly demonstrate royal-class techniques.",
                        "Students cannot study sealed disciplines without house approval.",
                    ],
                    contradiction_risks=[
                        "If power is too restricted, explain how illegal users survive.",
                    ],
                    story_uses=[
                        "forbidden training arc",
                        "academy trial",
                        "class conflict",
                        "secret mentor reveal",
                    ],
                )
            )

        if is_relic:
            rule_set.artifact_rules.append(
                WorldRule(
                    rule_name="Relic Debt Principle",
                    rule_category="artifact",
                    description=(
                        "Ancient relics grant influence, protection, or power, but each use creates "
                        "a debt recorded by older forces the empire no longer understands."
                    ),
                    applies_to=["relic owners", "academies", "churches", "noble houses"],
                    cost_or_limit="Repeated relic use increases spiritual, political, or historical debt.",
                    enforcement_mechanism="Relic behavior, oath records, religious courts, and hidden archivists.",
                    loopholes=[
                        "Some broken relics no longer report debt correctly.",
                        "Certain bloodlines can delay debt collection.",
                    ],
                    forbidden_exceptions=[
                        "Using relics during succession trials is officially forbidden but secretly common.",
                    ],
                    contradiction_risks=[
                        "Relics must not become unlimited solutions to every problem.",
                    ],
                    story_uses=[
                        "artifact temptation",
                        "hidden cost reveal",
                        "political bargaining",
                        "curse escalation",
                    ],
                )
            )

        # Destiny rules
        if is_destiny:
            rule_set.destiny_rules.append(
                WorldRule(
                    rule_name="Destiny Pressure Accumulation",
                    rule_category="destiny",
                    description=(
                        "Each destiny-bearing person increases pressure on the world's institutions, "
                        "because destiny bends probability around unresolved historical contradictions."
                    ),
                    applies_to=["destined people", "institutions", "factions", "prophecies"],
                    cost_or_limit=(
                        "Too many awakened destinies in one era accelerate unrest, prophecy conflict, "
                        "faction paranoia, and institutional collapse."
                    ),
                    enforcement_mechanism=(
                        "No single authority fully controls destiny; institutions try to classify and contain it."
                    ),
                    loopholes=[
                        "A destined person who refuses recognition can delay institutional reaction.",
                        "Hidden destined people can distort history quietly before being discovered.",
                    ],
                    forbidden_exceptions=[
                        "Destined commoners are often denied legal recognition.",
                    ],
                    contradiction_risks=[
                        "Destiny must not erase character agency.",
                        "Destiny must create pressure, not automatic victory.",
                    ],
                    story_uses=[
                        "chosen-one inversion",
                        "rival destiny collision",
                        "political panic",
                        "prophecy fraud",
                    ],
                )
            )

        # Oath / memory / truth rules
        if is_oath or is_political or is_academy:
            rule_set.memory_rules.append(
                WorldRule(
                    rule_name="Official Memory Doctrine",
                    rule_category="memory",
                    description=(
                        "The state preserves official memory through archives, ceremonies, school texts, "
                        "and oath-records, while suppressing memories that threaten legitimacy."
                    ),
                    applies_to=["archives", "schools", "courts", "families", "religious orders"],
                    cost_or_limit=(
                        "Contradicting official history can damage reputation, status, inheritance, or legal standing."
                    ),
                    enforcement_mechanism="Censors, academy historians, oath-priests, and noble courts.",
                    loopholes=[
                        "Oral traditions survive where official archives cannot reach.",
                        "Artifacts may preserve memories outside state control.",
                    ],
                    forbidden_exceptions=[
                        "Students cannot cite erased events in public examinations.",
                    ],
                    contradiction_risks=[
                        "If the state controls memory, define who preserves the truth.",
                    ],
                    story_uses=[
                        "forbidden archive scene",
                        "family secret",
                        "historical mystery",
                        "trial by memory",
                    ],
                )
            )

            rule_set.knowledge_rules.append(
                WorldRule(
                    rule_name="Ranked Knowledge Access",
                    rule_category="knowledge",
                    description=(
                        "Knowledge is tiered by birth, institutional rank, sponsorship, and political trust."
                    ),
                    applies_to=["students", "teachers", "scribes", "commoners", "nobles"],
                    cost_or_limit=(
                        "Learning above one's rank risks expulsion, imprisonment, memory punishment, or blackmail."
                    ),
                    enforcement_mechanism="Academy gates, sealed libraries, exams, and knowledge permits.",
                    loopholes=[
                        "Servants and archivists often overhear truths elites underestimate.",
                        "Old ruins contain pre-ranking knowledge.",
                    ],
                    forbidden_exceptions=[
                        "Commoners cannot legally access royal magic theory.",
                    ],
                    contradiction_risks=[
                        "If knowledge is restricted, explain how innovation still occurs.",
                    ],
                    story_uses=[
                        "forbidden book",
                        "secret study group",
                        "class-based education conflict",
                    ],
                )
            )

        # Social mobility rules
        if is_academy or is_political:
            rule_set.social_mobility_rules.append(
                WorldRule(
                    rule_name="Approved Ascent Rule",
                    rule_category="social_mobility",
                    description=(
                        "People may rise only through paths that preserve the legitimacy of the existing hierarchy."
                    ),
                    applies_to=["commoners", "minor nobles", "scholars", "soldiers"],
                    cost_or_limit=(
                        "Rising too quickly creates suspicion, sabotage, forced patronage, or public humiliation."
                    ),
                    enforcement_mechanism="Sponsorship systems, exams, marriage law, inheritance law, and reputation courts.",
                    loopholes=[
                        "War heroes, prodigies, and hidden heirs can bypass normal paths temporarily.",
                        "A powerful faction can sponsor an outsider for its own agenda.",
                    ],
                    forbidden_exceptions=[
                        "No one may outrank the founding bloodlines without symbolic approval.",
                    ],
                    contradiction_risks=[
                        "If mobility is impossible, explain why people still try.",
                    ],
                    story_uses=[
                        "underdog rise",
                        "patronage trap",
                        "elite resentment",
                        "identity reveal",
                    ],
                )
            )

        # Death / healing / consequence rules
        rule_set.death_rules.append(
            WorldRule(
                rule_name="Consequential Death Rule",
                rule_category="death",
                description=(
                    "Death changes inheritance, faction balance, memory, law, and public myth; it is never only personal."
                ),
                applies_to=["families", "factions", "institutions", "heirs"],
                cost_or_limit="Every major death creates a power vacancy or symbolic consequence.",
                enforcement_mechanism="Inheritance courts, funeral law, faction succession, and public mourning rituals.",
                loopholes=[
                    "Deaths can be hidden, misreported, or ritually delayed.",
                ],
                forbidden_exceptions=[
                    "Certain deaths cannot be publicly named until succession is resolved.",
                ],
                contradiction_risks=[
                    "Major deaths should not happen without social or political aftershocks.",
                ],
                story_uses=[
                    "succession crisis",
                    "funeral politics",
                    "hidden murder",
                    "legacy burden",
                ],
            )
        )

        rule_set.healing_rules.append(
            WorldRule(
                rule_name="Healing Inequality Rule",
                rule_category="healing",
                description=(
                    "Advanced healing exists but is distributed according to class, institution, wealth, or religious approval."
                ),
                applies_to=["nobles", "soldiers", "students", "commoners", "religious orders"],
                cost_or_limit="Powerful healing is expensive, politically controlled, or spiritually conditional.",
                enforcement_mechanism="Healer guilds, temples, military hospitals, and academy clinics.",
                loopholes=[
                    "Illegal healers operate in poor districts.",
                    "Old medicine survives outside official institutions.",
                ],
                forbidden_exceptions=[
                    "Healing a condemned criminal may be treated as treason.",
                ],
                contradiction_risks=[
                    "If healing is too available, injury loses narrative consequence.",
                ],
                story_uses=[
                    "medical black market",
                    "class injustice",
                    "sacrificial healing",
                    "debtor patient",
                ],
            )
        )

        # Prophecy rules
        if is_destiny or is_oath:
            rule_set.prophecy_rules.append(
                WorldRule(
                    rule_name="Interpretation War Rule",
                    rule_category="prophecy",
                    description=(
                        "Prophecies are not self-executing truths; they become political weapons through interpretation."
                    ),
                    applies_to=["churches", "courts", "academies", "destined people"],
                    cost_or_limit="Every interpretation creates winners, losers, and suppressed alternatives.",
                    enforcement_mechanism="Religious councils, royal announcements, academy classification boards.",
                    loopholes=[
                        "Private prophecies can contradict public prophecy.",
                        "False translations can redirect political events.",
                    ],
                    forbidden_exceptions=[
                        "Unlicensed prophecy publication is punishable.",
                    ],
                    contradiction_risks=[
                        "Prophecy should create ambiguity, not remove suspense.",
                    ],
                    story_uses=[
                        "false prophecy",
                        "translation mystery",
                        "chosen-one dispute",
                        "religious manipulation",
                    ],
                )
            )

        rule_set.global_constraints = [
            "Every major rule must create both power and cost.",
            "Every restriction should create at least one loophole or black market.",
            "Every law should reveal who benefits and who is harmed.",
            "Every supernatural rule must preserve character agency.",
            "Every world rule should be usable later by character, faction, plot, or mystery engines.",
        ]

        if desired_complexity in {"extreme", "god_level"}:
            rule_set.global_constraints.append(
                "Rules must interlock across society, law, economy, belief, institutions, and artifacts."
            )

        return rule_set

    def _build_boundaries(
        self,
        *,
        seed_premise: str,
        genre_tags: List[str],
        desired_complexity: str,
    ) -> WorldBoundaryConstraintProfile:
        seed = seed_premise.lower()

        known_boundaries = [
            "The mapped empire ends where official roads, tax records, and academy charters end.",
            "Border provinces know more about outside threats than the capital admits.",
        ]

        believed_outside = [
            "Citizens are taught that beyond the empire lies disorder, barbarism, or divine punishment.",
            "Academies claim outside knowledge is corrupted or academically invalid.",
        ]

        actual_outside = [
            "Outside the known map are older cultures, erased settlements, and powers not classified by imperial law.",
            "Some forbidden regions preserve the truth of the founding betrayal.",
        ]

        physical_boundaries = [
            "mountain passes controlled by military houses",
            "ruined roads from a previous empire",
            "relic-scarred wastelands",
        ]

        political_boundaries = [
            "academy jurisdictions",
            "noble house territories",
            "tax borders",
            "forbidden provinces",
        ]

        magical_boundaries = []
        if "magic" in seed or "dark_academy" in genre_tags:
            magical_boundaries.extend(
                [
                    "sealed classrooms that reject unauthorized bloodlines",
                    "old oath-lines that punish false claims of authority",
                ]
            )

        knowledge_boundaries = [
            "sealed archives",
            "ranked textbooks",
            "forbidden historical maps",
            "oral histories excluded from official education",
        ]

        exploration_limits = [
            "Travel permits restrict students and commoners.",
            "Military checkpoints control border routes.",
            "Unmapped regions are labeled spiritually unsafe.",
        ]

        sequel_expansion = [
            "unknown cultures beyond the official map",
            "lost institutions from before the empire",
            "artifact networks outside academy control",
        ]

        if desired_complexity in {"extreme", "god_level"}:
            sequel_expansion.extend(
                [
                    "cosmic boundary around destiny itself",
                    "outside-world witnesses to the empire's erased crime",
                    "civilizations with incompatible law, magic, and truth systems",
                ]
            )

        return WorldBoundaryConstraintProfile(
            known_world_boundaries=known_boundaries,
            believed_outside_world=believed_outside,
            actual_outside_world=actual_outside,
            physical_boundaries=physical_boundaries,
            political_boundaries=political_boundaries,
            magical_boundaries=magical_boundaries,
            knowledge_boundaries=knowledge_boundaries,
            exploration_limits=exploration_limits,
            sequel_expansion_potential=sequel_expansion,
        )

    def _build_contradiction_intent(
        self,
        *,
        seed_premise: str,
        genre_tags: List[str],
        desired_complexity: str,
    ) -> WorldContradictionIntent:
        seed = seed_premise.lower()

        intentional_hypocrisies = [
            "The empire praises merit while restricting education by birth.",
            "The academies claim to protect truth while censoring the history that created them.",
        ]

        social_contradictions = [
            "Commoners can be called citizens but treated as untrusted witnesses.",
            "Destined people are celebrated in myth but feared in real life.",
        ]

        legal_contradictions = [
            "Law says all oath-bound people are protected, but only nobles can afford oath-court representation.",
            "Forbidden knowledge is illegal unless a ruling institution needs it.",
        ]

        religious_contradictions = [
            "The faith teaches obedience to sacred oaths, but the ruling order was founded on a broken one.",
        ]

        economic_contradictions = [
            "The noble class condemns black markets while depending on relic smuggling.",
            "Academies call themselves sacred institutions while functioning as economic monopolies.",
        ]

        bad_contradiction_risks = [
            "Do not let rules contradict each other without deciding whether the contradiction is intentional.",
            "Do not let destiny remove free will.",
            "Do not let restricted knowledge make innovation impossible without an underground knowledge path.",
        ]

        if "romance" in genre_tags:
            social_contradictions.append(
                "Public courtship rules praise pure love but marriage law exists to preserve class power."
            )

        if "relic" in seed:
            economic_contradictions.append(
                "Relics are called holy inheritance, but their extraction destroys the poor regions that produce them."
            )

        if desired_complexity in {"extreme", "god_level"}:
            intentional_hypocrisies.append(
                "Every institution publicly solves the problem it secretly depends on."
            )
            bad_contradiction_risks.append(
                "High complexity requires tracking which contradictions are story fuel versus design errors."
            )

        return WorldContradictionIntent(
            intentional_hypocrisies=intentional_hypocrisies,
            social_contradictions=social_contradictions,
            legal_contradictions=legal_contradictions,
            religious_contradictions=religious_contradictions,
            economic_contradictions=economic_contradictions,
            bad_contradiction_risks=bad_contradiction_risks,
        )

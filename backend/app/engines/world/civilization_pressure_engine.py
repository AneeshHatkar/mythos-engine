from typing import Any, Dict, List

from backend.app.engines.base import BaseEngine
from backend.app.schemas.foundation import EngineRunResult
from backend.app.schemas.world import (
    CausalityLink,
    CivilizationPressureProfile,
    WorldCausalityGraph,
)


class CivilizationPressureEngine(BaseEngine):
    """Generates civilization pressure, world evolution risk, and causality graph.

    This engine turns the world from a static encyclopedia into a living system.

    It defines:
    - current crisis
    - hidden crisis
    - social pressure
    - economic pressure
    - spiritual pressure
    - war pressure
    - mystery pressure
    - villain pressure
    - destiny pressure
    - collapse timeline
    - breaking points
    - cause/effect links between world systems

    Later chunks use this for plot engines, faction simulation, character
    pressure, villain plans, rebellion arcs, world-state updates, and ML-style
    causal evaluation.
    """

    engine_name = "world.civilization_pressure_engine"

    def run(self, payload: Dict[str, Any]) -> EngineRunResult:
        seed_premise = payload.get("seed_premise", "")
        genre_tags = payload.get("genre_tags", [])
        tone_tags = payload.get("tone_tags", [])
        desired_complexity = payload.get("desired_complexity", "high")

        warnings: List[str] = []

        if not seed_premise:
            warnings.append(
                "No seed_premise provided; civilization pressure will use broad default structures."
            )

        pressure = self._build_civilization_pressure(
            seed_premise=seed_premise,
            genre_tags=genre_tags,
            tone_tags=tone_tags,
            desired_complexity=desired_complexity,
        )

        causality_graph = self._build_causality_graph(
            seed_premise=seed_premise,
            genre_tags=genre_tags,
            tone_tags=tone_tags,
            desired_complexity=desired_complexity,
        )

        return self.build_result(
            success=True,
            data={
                "civilization_pressure": pressure.model_dump(mode="json"),
                "causality_graph": causality_graph.model_dump(mode="json"),
                "training_notes": [
                    "Civilization pressure is structured for future world-state simulation and plot generation.",
                    "Causality links make world systems machine-readable for later consistency, impact, and evolution scoring.",
                    "This layer should later update when characters, factions, wars, laws, and artifacts change the world.",
                    "Causality graph fields prepare MythOS for future ML/RL-style world transition modeling.",
                ],
            },
            warnings=warnings,
            errors=[],
            generated_object_ids=[],
        )

    def _build_civilization_pressure(
        self,
        *,
        seed_premise: str,
        genre_tags: List[str],
        tone_tags: List[str],
        desired_complexity: str,
    ) -> CivilizationPressureProfile:
        seed = seed_premise.lower()

        is_academy = "academy" in seed or "dark_academy" in genre_tags
        is_empire = "empire" in seed or "political_fantasy" in genre_tags
        is_relic = "relic" in seed
        is_oath = "oath" in seed
        is_destiny = "destiny" in seed or "destined" in seed
        is_tragic = "tragic" in tone_tags or "collapse" in seed
        is_dystopian = "dystopian" in genre_tags or "surveillance" in seed

        current_crisis = (
            "The visible crisis is institutional strain: class resentment, student unrest, resource anxiety, "
            "elite succession fear, and public distrust are rising at the same time."
        )

        if is_destiny:
            current_crisis = (
                "The visible crisis is the abnormal clustering of destiny-bearing people. Institutions built to classify rare exceptions "
                "are failing because too many exceptional figures are awakening too close together."
            )

        hidden_crisis = (
            "The hidden crisis is that the current order depends on a false historical foundation. Law, education, religion, economy, and family legitimacy "
            "all rely on records that were edited to protect the people who gained power."
        )

        if is_relic:
            hidden_crisis += (
                " Relics are beginning to behave less like resources and more like witnesses, threatening the economy that treats them as property."
            )

        social_pressure = (
            "Lower classes know the system is unfair but lack legal credibility; minor nobles fear falling; high nobles fear exposure; "
            "students carry ambition, debt, and humiliation into every public ranking."
        )

        economic_pressure = (
            "Academy funding, relic markets, debt ledgers, tuition bonds, food prices, and border taxation are tightening together. "
            "The economy can still look elegant while becoming unstable underneath."
        )

        if is_relic:
            economic_pressure += (
                " Relic scarcity is the economic fault line: when relics become costly or dangerous, academies, banks, temples, and military convoys all panic."
            )

        spiritual_pressure = (
            "The official faith says obedience preserves civilization, but forgotten gods, erased names, broken oaths, and suppressed heresies are becoming harder to ignore."
        )

        if is_oath:
            spiritual_pressure += (
                " Every public vow now risks reminding people that the founding oath may have been broken by the rulers themselves."
            )

        war_pressure = (
            "Border commanders are more independent than the capital admits. Resource convoys, student militias, noble guards, and market networks could turn local conflict into civil war."
        )

        mystery_pressure = (
            "Too many records disagree: maps omit places, archives hide names, relics remember emotions, and official histories contradict oral memory."
        )

        villain_pressure = (
            "A strong antagonist could exploit the system by controlling records, debt, destiny classification, resource access, or public fear while claiming to preserve order."
        )

        if is_dystopian:
            villain_pressure += (
                " Surveillance systems make villainy easier to disguise as safety."
            )

        destiny_pressure = (
            "Destiny is background pressure only unless unusually gifted people appear in numbers the institutions cannot absorb."
        )

        if is_destiny:
            destiny_pressure = (
                "Destiny pressure is extreme: every destiny-bearing person becomes a strategic asset, a religious question, a legal anomaly, and a possible collapse trigger."
            )

        collapse_timeline = (
            "Short term: scandals, shortages, and student unrest. Medium term: faction recruitment, legal overreach, and archive leaks. "
            "Long term: open legitimacy crisis, succession conflict, institutional fracture, or controlled authoritarian reform."
        )

        if is_tragic:
            collapse_timeline += (
                " In a tragic arc, the world may recognize the truth only after punishing the people who tried to reveal it."
            )

        if_nobody_acts = (
            "If nobody acts, institutions will tighten control, black markets will grow, students and border groups will radicalize, "
            "and the ruling class will mistake temporary order for survival."
        )

        if_villain_wins = (
            "If the villain wins, the world becomes more efficient and less human: records are corrected, dissent is classified, education becomes containment, "
            "and truth survives only as contraband."
        )

        system_breaking_points = [
            "a public proof that founder legitimacy was built on erased testimony",
            "a relic refusing its legal owner during a public ceremony",
            "a food or tuition crisis that unites students and laborers",
            "a destiny-bearing commoner outperforming noble heirs before witnesses",
            "a border commander refusing a capital order",
            "a forbidden book becoming easier to copy than suppress",
            "a trial where legal credibility collapses because records contradict each other",
        ]

        if is_relic:
            system_breaking_points.append(
                "a mine disaster proving relic extraction causes spiritual or historical debt"
            )

        if is_destiny:
            system_breaking_points.append(
                "two or more destiny-bearing people forming an alliance outside institutional classification"
            )

        if desired_complexity in {"extreme", "god_level"}:
            system_breaking_points.extend(
                [
                    "multiple systems failing together: food, law, education, belief, finance, and military loyalty",
                    "a character decision causing a measurable world-state transition in future simulation",
                    "a consistency check discovering that the world can no longer preserve both hierarchy and truth",
                ]
            )

        return CivilizationPressureProfile(
            current_crisis=current_crisis,
            hidden_crisis=hidden_crisis,
            social_pressure=social_pressure,
            economic_pressure=economic_pressure,
            spiritual_pressure=spiritual_pressure,
            war_pressure=war_pressure,
            mystery_pressure=mystery_pressure,
            villain_pressure=villain_pressure,
            destiny_pressure=destiny_pressure,
            collapse_timeline=collapse_timeline,
            if_nobody_acts=if_nobody_acts,
            if_villain_wins=if_villain_wins,
            system_breaking_points=system_breaking_points,
        )

    def _build_causality_graph(
        self,
        *,
        seed_premise: str,
        genre_tags: List[str],
        tone_tags: List[str],
        desired_complexity: str,
    ) -> WorldCausalityGraph:
        seed = seed_premise.lower()

        is_relic = "relic" in seed
        is_destiny = "destiny" in seed or "destined" in seed
        is_oath = "oath" in seed
        is_academy = "academy" in seed or "dark_academy" in genre_tags
        is_empire = "empire" in seed or "political_fantasy" in genre_tags

        links: List[CausalityLink] = [
            CausalityLink(
                cause="Founder bloodlines control legal credibility",
                effect="Lower classes cannot easily challenge court decisions even with evidence",
                strength=0.88,
                affected_systems=["law", "society", "class", "courts", "character_motivation"],
                story_use="trial injustice, rebellion motivation, false accusation arc",
            ),
            CausalityLink(
                cause="Education access is restricted by rank and sponsorship",
                effect="Talent outside approved classes becomes illegal, hidden, or faction-recruited",
                strength=0.91,
                affected_systems=["education", "society", "factions", "characters", "villains"],
                story_use="forbidden study, secret mentor, prodigy conflict",
            ),
            CausalityLink(
                cause="Official archives preserve edited history",
                effect="Mystery pressure rises when oral memory, relics, maps, and legal records disagree",
                strength=0.86,
                affected_systems=["history", "archives", "mystery", "law", "belief"],
                story_use="archive heist, lineage reveal, historical investigation",
            ),
            CausalityLink(
                cause="Academies claim merit while depending on noble funding",
                effect="Students experience ambition as both opportunity and ownership",
                strength=0.82,
                affected_systems=["education", "economy", "society", "romance", "rivalry"],
                story_use="sponsorship debt, elite rivalry, romance obstacle",
            ),
            CausalityLink(
                cause="Black markets move knowledge faster than institutions allow",
                effect="Official censorship becomes less stable and more violent",
                strength=0.79,
                affected_systems=["knowledge", "law", "economy", "factions", "plot"],
                story_use="forbidden book spread, informant betrayal, crackdown",
            ),
            CausalityLink(
                cause="Border regions remember erased treaties",
                effect="The capital cannot fully control outside-world truth or frontier loyalty",
                strength=0.74,
                affected_systems=["geography", "military", "history", "factions", "war"],
                story_use="exile refuge, border rebellion, outside-world reveal",
            ),
            CausalityLink(
                cause="Healing is distributed by class and usefulness",
                effect="Injury creates political anger instead of only personal suffering",
                strength=0.71,
                affected_systems=["medicine", "society", "law", "economy", "character_arcs"],
                story_use="medical black market, martyr figure, class injustice",
            ),
            CausalityLink(
                cause="Public rituals require visible obedience",
                effect="Private doubt becomes dangerous when performed spaces expose contradiction",
                strength=0.68,
                affected_systems=["belief", "culture", "law", "romance", "plot"],
                story_use="wedding interruption, oath ceremony betrayal, public confession",
            ),
        ]

        if is_relic:
            links.extend(
                [
                    CausalityLink(
                        cause="Relic extraction funds academies and elite institutions",
                        effect="Education, religion, economy, and military logistics become dependent on dangerous buried objects",
                        strength=0.9,
                        affected_systems=["economy", "education", "religion", "military", "artifacts"],
                        story_use="mine revolt, relic debt, academy funding crisis",
                    ),
                    CausalityLink(
                        cause="Relics remember emotional traces of historical violence",
                        effect="The economy accidentally preserves evidence against itself",
                        strength=0.84,
                        affected_systems=["artifacts", "history", "law", "mystery", "belief"],
                        story_use="artifact testimony, public scandal, spiritual horror",
                    ),
                ]
            )

        if is_destiny:
            links.extend(
                [
                    CausalityLink(
                        cause="Too many destiny-bearing people awaken in one era",
                        effect="Classification systems, prophecy offices, noble sponsors, and factions compete faster than law can adapt",
                        strength=0.95,
                        affected_systems=["destiny", "law", "factions", "religion", "characters"],
                        story_use="chosen-one collision, faction kidnapping, prophecy war",
                    ),
                    CausalityLink(
                        cause="Destined people can outrank their birth story",
                        effect="Class hierarchy loses its claim that rank predicts worth",
                        strength=0.89,
                        affected_systems=["society", "class", "education", "law", "romance"],
                        story_use="commoner prodigy, noble insecurity, forbidden alliance",
                    ),
                ]
            )

        if is_oath:
            links.append(
                CausalityLink(
                    cause="The First Oath may have been broken by the founders",
                    effect="Every modern oath ceremony risks becoming evidence of institutional hypocrisy",
                    strength=0.87,
                    affected_systems=["belief", "law", "history", "culture", "villains"],
                    story_use="trial by oath, public ceremony collapse, religious crisis",
                )
            )

        if is_academy:
            links.append(
                CausalityLink(
                    cause="Academy ranking turns youth into public hierarchy",
                    effect="Friendship, romance, rivalry, and ambition become political before characters understand themselves",
                    strength=0.8,
                    affected_systems=["education", "society", "romance", "character_arcs", "factions"],
                    story_use="student rivalry, forbidden romance, betrayal under exam pressure",
                )
            )

        if is_empire:
            links.append(
                CausalityLink(
                    cause="The empire equates map control with truth control",
                    effect="Unknown regions and erased provinces become threats to legitimacy, not just geography",
                    strength=0.78,
                    affected_systems=["geography", "history", "law", "military", "mystery"],
                    story_use="lost province journey, forbidden map, border reveal",
                )
            )

        if desired_complexity in {"extreme", "god_level"}:
            links.extend(
                [
                    CausalityLink(
                        cause="Multiple institutions depend on each other's lies",
                        effect="A truth leak in one system can cascade through law, economy, religion, education, and military loyalty",
                        strength=0.93,
                        affected_systems=["law", "economy", "religion", "education", "military", "civilization_pressure"],
                        story_use="cascade collapse, multi-faction panic, orchestrator stress test",
                    ),
                    CausalityLink(
                        cause="User or character decisions alter faction trust and public knowledge",
                        effect="Future world states should update pressure, alliances, risk, and training metadata",
                        strength=0.77,
                        affected_systems=["simulation", "world_state", "factions", "training_metadata", "audit"],
                        story_use="future world-state engine, ML/RL transition modeling",
                    ),
                ]
            )

        root_causes = [
            "founding betrayal hidden as sacred law",
            "birth-based legitimacy",
            "controlled knowledge access",
            "economic dependency on morally unstable systems",
            "legal credibility tied to rank",
        ]

        if is_relic:
            root_causes.append("resource dependence on relics that may be witnesses rather than property")

        if is_destiny:
            root_causes.append("destiny pressure exceeding institutional containment capacity")

        likely_future_effects = [
            "student unrest becomes faction recruitment",
            "forbidden knowledge spreads through black markets",
            "minor nobles panic as legal contradictions surface",
            "border groups gain leverage by preserving erased truths",
            "public rituals become dangerous stages for revelation",
        ]

        if is_relic:
            likely_future_effects.append("relic scarcity or relic testimony destabilizes academy funding")

        if is_destiny:
            likely_future_effects.append("destiny-bearing people form alliances that break class prediction")

        if desired_complexity in {"extreme", "god_level"}:
            likely_future_effects.append(
                "the orchestrator should use this graph to score whether generated plots affect the world logically"
            )

        return WorldCausalityGraph(
            links=links,
            root_causes=root_causes,
            likely_future_effects=likely_future_effects,
        )

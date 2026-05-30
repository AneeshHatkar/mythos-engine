from typing import Any, Dict, List

from backend.app.engines.base import BaseEngine
from backend.app.schemas.foundation import EngineRunResult
from backend.app.schemas.world import SpeciesCreatureProfile, TechnologyMagicScienceProfile


class TechnologySpeciesEngine(BaseEngine):
    """Generates technology, magic, science, and species/creature ecology.

    This layer defines what the world can physically, scientifically,
    magically, medically, militarily, and biologically support.

    It answers:
    - how advanced is communication?
    - how advanced is transport?
    - can wounds be healed?
    - can knowledge be copied?
    - what research is forbidden?
    - what creatures shape trade and travel?
    - are there sentient non-human groups?
    - do monsters affect economy, religion, warfare, and folklore?

    Later chunks use this for plot feasibility, battle logic, medicine,
    mystery timing, travel constraints, monster ecology, fantasy/sci-fi rules,
    and future dataset-backed world modeling.
    """

    engine_name = "world.technology_species_engine"

    def run(self, payload: Dict[str, Any]) -> EngineRunResult:
        seed_premise = payload.get("seed_premise", "")
        genre_tags = payload.get("genre_tags", [])
        tone_tags = payload.get("tone_tags", [])
        desired_complexity = payload.get("desired_complexity", "high")

        warnings: List[str] = []

        if not seed_premise:
            warnings.append(
                "No seed_premise provided; technology/species systems will use broad default structures."
            )

        technology_magic_science = self._build_technology_magic_science(
            seed_premise=seed_premise,
            genre_tags=genre_tags,
            tone_tags=tone_tags,
            desired_complexity=desired_complexity,
        )

        species_creatures = self._build_species_creatures(
            seed_premise=seed_premise,
            genre_tags=genre_tags,
            tone_tags=tone_tags,
            desired_complexity=desired_complexity,
        )

        return self.build_result(
            success=True,
            data={
                "technology_magic_science": technology_magic_science.model_dump(mode="json"),
                "species_creatures": species_creatures.model_dump(mode="json"),
                "training_notes": [
                    "Technology and magic constraints are structured for future plot feasibility and consistency checks.",
                    "Healing, communication, and transportation levels prevent later story engines from breaking world logic.",
                    "Species and creature ecology are structured so monsters and non-human groups affect economy, law, religion, and travel instead of acting as decoration.",
                    "This layer should later be checked against geography, infrastructure, military, law, economy, and belief before training eligibility.",
                ],
            },
            warnings=warnings,
            errors=[],
            generated_object_ids=[],
        )

    def _build_technology_magic_science(
        self,
        *,
        seed_premise: str,
        genre_tags: List[str],
        tone_tags: List[str],
        desired_complexity: str,
    ) -> TechnologyMagicScienceProfile:
        seed = seed_premise.lower()

        is_academy = "academy" in seed or "dark_academy" in genre_tags
        is_magic = "magic" in seed or "fantasy" in genre_tags or "political_fantasy" in genre_tags
        is_relic = "relic" in seed
        is_oath = "oath" in seed
        is_destiny = "destiny" in seed or "destined" in seed
        is_dystopian = "dystopian" in genre_tags or "surveillance" in seed
        is_civilization = "civilization" in seed or "simulation" in seed

        technology_level = (
            "Late pre-industrial to early institutional-industrial. The world has advanced bureaucracy, printing, "
            "ledger systems, specialized medicine, engineered roads, mining equipment, and limited mechanical tools, "
            "but mass industry remains constrained by class control, resource politics, and religious suspicion."
        )

        if is_dystopian:
            technology_level += (
                " Surveillance infrastructure is unusually advanced compared with public welfare technology."
            )

        magic_development_level = (
            "Magic exists as regulated institutional practice rather than free personal expression. "
            "Advanced techniques are licensed, ranked, taught through academies, and legally tied to bloodline, sponsorship, and oath-status."
        )

        if not is_magic:
            magic_development_level = (
                "No openly dominant magic system is assumed, but ritual, symbolism, medicine, belief, and institutional power may still produce quasi-magical cultural effects."
            )

        if is_oath:
            magic_development_level += (
                " Oath-magic is semi-legal technology: vows can bind testimony, inheritance, rank, punishment, and access."
            )

        scientific_understanding = (
            "Science is observational, archival, and institutionally cautious. Scholars understand anatomy, mining hazards, weather patterns, engineering, "
            "records, and probability in practical ways, but politically inconvenient research is often renamed as heresy, superstition, or illegal speculation."
        )

        lost_technology = [
            "pre-imperial road foundations that resist collapse better than modern roads",
            "old archive indexing methods that could recover erased names",
            "witness bells capable of detecting broken oath chains",
            "memory-safe ink formulas no longer taught in public academies",
        ]

        if is_relic:
            lost_technology.extend(
                [
                    "deep relic stabilizers used by forgotten miners",
                    "artifact listening devices from before current ownership law",
                    "old extraction maps that mark places the empire denies exist",
                ]
            )

        forbidden_research = [
            "unranked royal magic theory",
            "methods for restoring erased legal identities",
            "comparative studies of official and oral history",
            "memory manipulation ethics",
            "inheritance fraud detection that could expose founder houses",
        ]

        if is_destiny:
            forbidden_research.append(
                "destiny clustering models that predict when too many world-level figures will awaken together"
            )

        if is_relic:
            forbidden_research.append(
                "relic debt mechanics and whether artifacts are resources, witnesses, or living contracts"
            )

        medicine_or_healing_level = (
            "Medicine combines practical anatomy, herbal knowledge, ritual care, regulated healing techniques, and expensive institutional clinics. "
            "Elite patients receive advanced treatment; poor patients rely on local healers, black markets, battlefield medicine, and debt."
        )

        if is_magic:
            medicine_or_healing_level += (
                " Magical healing exists but is legally controlled and cannot erase every consequence without cost."
            )

        transportation_level = (
            "Travel depends on roads, guarded convoys, canals, carriages, military routes, border passes, student permits, and smuggler paths. "
            "Movement speed is determined by class, paperwork, weather, faction control, and danger."
        )

        communication_level = (
            "Communication uses couriers, official letters, academy seals, market whisper-chains, border riders, archive notices, public proclamations, and rare ritual signals. "
            "Information can travel quickly for elites but slowly or dangerously for ordinary people."
        )

        if is_dystopian:
            communication_level += (
                " Messages are often intercepted, logged, delayed, or rewritten by security offices."
            )

        innovation_bottlenecks = [
            "knowledge licensing prevents broad experimentation",
            "class hierarchy blocks talented researchers from equipment",
            "religious courts suppress dangerous questions",
            "elite sponsors own research outcomes",
            "resource monopolies distort scientific priorities",
            "archives hide failed experiments and inconvenient discoveries",
        ]

        if is_civilization:
            innovation_bottlenecks.append(
                "civilization-scale planning is weakened by factional control over data and infrastructure"
            )

        military_technology = [
            "ranked officer training manuals",
            "fortified border roads",
            "convoy armor for relic transport",
            "signal flags and coded bells",
            "dueling weapons standardized by academy law",
            "anti-riot formations for market districts",
        ]

        if is_magic:
            military_technology.append(
                "licensed combat techniques taught only to approved students and military houses"
            )

        if is_relic:
            military_technology.append(
                "unstable relic-powered defensive devices used only under heavy supervision"
            )

        if desired_complexity in {"extreme", "god_level"}:
            innovation_bottlenecks.append(
                "future MythOS consistency checks must verify that technology, magic, communication, medicine, and military capability do not break mystery, romance, war, or survival logic"
            )

        return TechnologyMagicScienceProfile(
            technology_level=technology_level,
            magic_development_level=magic_development_level,
            scientific_understanding=scientific_understanding,
            lost_technology=lost_technology,
            forbidden_research=forbidden_research,
            medicine_or_healing_level=medicine_or_healing_level,
            transportation_level=transportation_level,
            communication_level=communication_level,
            innovation_bottlenecks=innovation_bottlenecks,
            military_technology=military_technology,
        )

    def _build_species_creatures(
        self,
        *,
        seed_premise: str,
        genre_tags: List[str],
        tone_tags: List[str],
        desired_complexity: str,
    ) -> SpeciesCreatureProfile:
        seed = seed_premise.lower()

        is_fantasy = "fantasy" in genre_tags or "magic" in seed or "relic" in seed
        is_relic = "relic" in seed
        is_oath = "oath" in seed
        is_destiny = "destiny" in seed or "destined" in seed
        is_dark = "dark_academy" in genre_tags or "tragic" in tone_tags

        sentient_species = [
            "Humans: the dominant legal and institutional population."
        ]

        if is_fantasy and desired_complexity in {"extreme", "god_level"}:
            sentient_species.extend(
                [
                    "Oathmarked: rare human-descended lineages whose bodies react strongly to broken vows.",
                    "Archive-Born: disputed people said to be born from restored names rather than ordinary family records.",
                ]
            )

        non_sentient_creatures = [
            "ledger-crows that gather around courts, archives, and inheritance disputes",
            "ridge-mules bred for dangerous relic roads",
            "canal eels in low-market waterways",
            "winterglass moths used by students to send tiny illegal notes",
            "border hounds trained to recognize forged travel papers",
        ]

        monster_ecology = [
            "Relic-burrowers live near unstable mines and feed on mineral memory, making extraction dangerous.",
            "Ashwraiths are rumored to appear where erased names were burned from records.",
            "Oath-bitten wolves haunt old promise roads and react violently to false vows.",
        ]

        if not is_fantasy:
            monster_ecology = [
                "No confirmed monsters are required, but social folklore treats disease, mine collapses, and wilderness danger as if they have moral intent."
            ]

        sacred_animals = [
            "white bell-deer associated with unbroken promises",
            "black ledger-crows associated with archives and inheritance",
            "silver canal fish released during funerals for erased people",
        ]

        if is_destiny:
            sacred_animals.append(
                "star-moths believed to gather near children whose lives will distort history"
            )

        domesticated_creatures = [
            "ridge-mules for mining roads",
            "messenger crows for short-distance coded notes",
            "academy hounds trained to guard sealed libraries",
            "canal rats used by smugglers to predict flood tunnels",
        ]

        species_relations = [
            "Most society is human-centered, but animal symbolism carries legal, religious, and class meaning.",
            "Mine workers respect relic-burrowers as warning signs while investors call them pests.",
            "Academy students treat messenger animals as tools, while low-market families treat them as partners.",
        ]

        if "Oathmarked" in sentient_species:
            species_relations.append(
                "Oathmarked people are legally human but socially treated as dangerous evidence that law can mark the body."
            )

        if "Archive-Born" in sentient_species:
            species_relations.append(
                "Archive-Born people raise legal panic because they challenge ordinary birth, family, and identity rules."
            )

        species_laws = [
            "damaging sacred bell-deer before an oath ceremony is punishable as ritual sabotage",
            "academy hounds cannot be harmed during library enforcement unless they attack a ranked citizen",
            "relic-burrower sightings must be reported before mine work continues",
            "messenger animals carrying sealed papers are treated as legal extensions of their sender",
        ]

        if "Oathmarked" in sentient_species:
            species_laws.append(
                "Oathmarked people must register unusual vow reactions with an approved institution"
            )

        dangerous_habitats = [
            "collapsed relic tunnels",
            "fog-heavy canals below the Low Lantern Market",
            "old oath roads through the borderlands",
            "sealed archive basements where names were burned",
            "winter ridges around abandoned military posts",
        ]

        if is_relic:
            dangerous_habitats.append(
                "deep memory-stone seams where relic-burrowers and debt echoes gather"
            )

        if is_oath:
            dangerous_habitats.append(
                "promise fields where false vows are believed to attract oath-bitten predators"
            )

        if is_dark:
            dangerous_habitats.append(
                "unused academy courtyards where students claim failed names still answer roll call"
            )

        if desired_complexity in {"extreme", "god_level"}:
            monster_ecology.append(
                "Creature ecology should later connect to trade routes, military planning, religion, medicine, childhood fears, and regional identity."
            )

        return SpeciesCreatureProfile(
            sentient_species=sentient_species,
            non_sentient_creatures=non_sentient_creatures,
            monster_ecology=monster_ecology,
            sacred_animals=sacred_animals,
            domesticated_creatures=domesticated_creatures,
            species_relations=species_relations,
            species_laws=species_laws,
            dangerous_habitats=dangerous_habitats,
        )

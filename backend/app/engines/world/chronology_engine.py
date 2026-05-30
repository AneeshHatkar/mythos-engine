from typing import Any, Dict, List

from backend.app.engines.base import BaseEngine
from backend.app.schemas.foundation import EngineRunResult
from backend.app.schemas.world import (
    ChronologyProfile,
    HistoricalEra,
    HistoricalEvent,
    HistoricalWound,
    WorldMemoryArchive,
)


class ChronologyEngine(BaseEngine):
    """Generates chronology, historical wounds, and world memory.

    This engine gives the world a past that actively causes the present.

    It is intentionally structured for future ML/R&D:
    - official history vs true history
    - causal events
    - historical lies
    - erased records
    - inherited wounds
    - memory archive entries
    - future consistency checking
    """

    engine_name = "world.chronology_engine"

    def run(self, payload: Dict[str, Any]) -> EngineRunResult:
        seed_premise = payload.get("seed_premise", "")
        world_name = payload.get("world_name") or payload.get("name") or "Mythraen"
        genre_tags = payload.get("genre_tags", [])
        tone_tags = payload.get("tone_tags", [])
        desired_complexity = payload.get("desired_complexity", "high")

        warnings: List[str] = []

        if not seed_premise:
            warnings.append(
                "No seed_premise provided; chronology will use broad default history."
            )

        chronology = self._build_chronology(
            world_name=world_name,
            seed_premise=seed_premise,
            genre_tags=genre_tags,
            tone_tags=tone_tags,
            desired_complexity=desired_complexity,
        )

        memory_archive = self._build_memory_archive(
            chronology=chronology,
            seed_premise=seed_premise,
            desired_complexity=desired_complexity,
        )

        return self.build_result(
            success=True,
            data={
                "chronology": chronology.model_dump(mode="json"),
                "memory_archive": memory_archive.model_dump(mode="json"),
                "training_notes": [
                    "Chronology is structured for future causality modeling.",
                    "Official history and true history are intentionally separated.",
                    "Historical wounds can feed character trauma, faction conflict, mystery, and plot engines.",
                ],
            },
            warnings=warnings,
            errors=[],
            generated_object_ids=[],
        )

    def _build_chronology(
        self,
        *,
        world_name: str,
        seed_premise: str,
        genre_tags: List[str],
        tone_tags: List[str],
        desired_complexity: str,
    ) -> ChronologyProfile:
        seed = seed_premise.lower()

        is_academy = "academy" in seed or "dark_academy" in genre_tags
        is_empire = "empire" in seed or "political_fantasy" in genre_tags
        is_destiny = "destiny" in seed or "destined" in seed
        is_relic = "relic" in seed
        is_oath = "oath" in seed
        is_collapse = "collapse" in seed or "tragic" in tone_tags

        creation_myth = (
            f"In the oldest public myth of {world_name}, the first rulers received law, language, "
            "and rank from powers beyond ordinary memory. Citizens are taught that civilization began "
            "when chaos accepted hierarchy."
        )

        if is_oath:
            creation_myth = (
                f"{world_name}'s creation myth says the first civilization was born when people swore "
                "the First Oath beneath a bell that could hear truth. Official religion claims the oath "
                "gave rulers the right to teach, judge, and name reality."
            )

        official_history_summary = (
            "Official history teaches that the current order saved the world from barbarism, disorder, "
            "false magic, and unlicensed ambition."
        )

        true_history_summary = (
            "True history suggests the current order was created not only to protect civilization, "
            "but to hide a founding betrayal and control who could access power."
        )

        if is_academy:
            official_history_summary += (
                " The academies are described as sacred guardians of merit and truth."
            )
            true_history_summary += (
                " The academies were also designed as gates that decide which families may rise."
            )

        if is_destiny:
            true_history_summary += (
                " The rise of destiny-bearing people reveals that the world was never as stable as its rulers claimed."
            )

        current_era = "Late Imperial Strain"
        if is_collapse:
            current_era = "Late Imperial Collapse"
        elif is_destiny:
            current_era = "The Era of Unstable Fates"

        current_year_label = "Year 417 After the Founding Oath"

        eras = [
            self._era_of_first_oath(is_oath=is_oath, world_name=world_name),
            self._era_of_crowned_order(is_empire=is_empire, is_academy=is_academy),
            self._era_of_hidden_betrayal(is_relic=is_relic, is_destiny=is_destiny),
            self._era_of_institutional_golden_age(is_academy=is_academy),
            self._era_of_current_fracture(
                is_destiny=is_destiny,
                is_collapse=is_collapse,
                is_relic=is_relic,
            ),
        ]

        erased_history = [
            "The original terms of the First Oath.",
            "The names of families removed from the first academy registers.",
            "Records proving commoner scholars once held legal teaching authority.",
        ]

        if is_relic:
            erased_history.append(
                "The first mining disaster that revealed relics were not inert objects."
            )

        historical_lies = [
            "The academies were founded purely for merit.",
            "All noble bloodlines descended from willing oath-keepers.",
            "The current law is older than the conflict it was created to hide.",
        ]

        if is_destiny:
            historical_lies.append(
                "Destiny-bearing people have always been rare enough for institutions to manage safely."
            )

        historical_wounds = [
            HistoricalWound(
                name="The Betrayal Beneath the First Oath",
                origin_event="The First Oath was broken by those who later wrote the law.",
                who_remembers_it=["hidden archivists", "old border families", "certain relics"],
                who_denies_it=["academy councils", "noble courts", "official historians"],
                current_effects=[
                    "law distrust",
                    "class resentment",
                    "religious hypocrisy",
                    "faction paranoia",
                ],
                emotional_charge="shame, fury, grief, and inherited silence",
                plot_potential=[
                    "forbidden archive reveal",
                    "trial scene",
                    "family lineage reversal",
                    "religious collapse",
                ],
            ),
            HistoricalWound(
                name="The Erasure of the Commoner Scholars",
                origin_event="Non-noble teachers were removed from legal memory after threatening academy monopoly.",
                who_remembers_it=["servant families", "illegal tutors", "oral historians"],
                who_denies_it=["academy boards", "noble sponsors"],
                current_effects=[
                    "commoner education bans",
                    "secret study groups",
                    "black-market textbooks",
                ],
                emotional_charge="humiliation and stubborn hope",
                plot_potential=[
                    "underground school",
                    "forbidden exam scroll",
                    "mentor execution",
                ],
            ),
        ]

        if is_destiny:
            historical_wounds.append(
                HistoricalWound(
                    name="The First Destiny Panic",
                    origin_event=(
                        "The first recorded generation of many destiny-bearing people nearly broke succession law."
                    ),
                    who_remembers_it=["prophecy offices", "sealed church councils", "retired executioners"],
                    who_denies_it=["public schools", "royal propaganda"],
                    current_effects=[
                        "destiny classification boards",
                        "fear of prodigies",
                        "political kidnapping",
                    ],
                    emotional_charge="awe, terror, jealousy, and control",
                    plot_potential=[
                        "destiny registry theft",
                        "false prophecy",
                        "rival destined people",
                    ],
                )
            )

        return ChronologyProfile(
            creation_myth=creation_myth,
            official_history_summary=official_history_summary,
            true_history_summary=true_history_summary,
            current_era=current_era,
            current_year_label=current_year_label,
            eras=eras,
            erased_history=erased_history,
            historical_lies=historical_lies,
            historical_wounds=historical_wounds,
        )

    def _era_of_first_oath(self, *, is_oath: bool, world_name: str) -> HistoricalEra:
        event = HistoricalEvent(
            name="The First Binding",
            era_name="Age of First Oaths",
            year_label="Before Recorded Law",
            public_version=(
                "The first rulers united scattered peoples through sacred promises and gave civilization form."
            ),
            true_version=(
                "The first ruling houses gained authority by controlling the record of who broke the original promise."
            ),
            causes=["fear of chaos", "need for shared law", "hunger for legitimacy"],
            consequences=["birth of oath-law", "rise of ruling houses", "suppression of rival memories"],
            affected_groups=["first families", "early priests", "future commoners"],
            unresolved_tensions=[
                "Who broke the First Oath?",
                "Why were some witnesses erased?",
            ],
            story_hooks=[
                "A relic remembers the original oath.",
                "A family name proves the official story is false.",
            ],
        )

        description = (
            "The mythic beginning of ordered society, where law, rank, and sacred memory became linked."
        )

        if is_oath:
            description += (
                " Oaths were not only promises; they became technology, religion, and government."
            )

        return HistoricalEra(
            name="Age of First Oaths",
            description=description,
            dominant_power="oath-keepers and memory witnesses",
            dominant_belief="truth must be bound before society can survive",
            major_events=[event],
            legacy=f"{world_name}'s laws still pretend to descend cleanly from this era.",
        )

    def _era_of_crowned_order(self, *, is_empire: bool, is_academy: bool) -> HistoricalEra:
        events = [
            HistoricalEvent(
                name="The Crown Consolidation",
                era_name="Age of Crowned Order",
                year_label="Year 1",
                public_version="The empire unified law, defense, education, and taxation.",
                true_version="Unification also allowed the ruling houses to standardize control over memory and rank.",
                causes=["regional conflict", "resource competition", "noble ambition"],
                consequences=["central courts", "ranked citizenship", "official tax borders"],
                affected_groups=["nobles", "merchants", "border families", "commoners"],
                unresolved_tensions=["Which regions joined willingly?", "Which treaties were forged?"],
                story_hooks=["A border treaty was signed by a dead person."],
            )
        ]

        if is_academy:
            events.append(
                HistoricalEvent(
                    name="The Founding of the High Academies",
                    era_name="Age of Crowned Order",
                    year_label="Year 39",
                    public_version="The academy system was founded to reward talent and protect civilization.",
                    true_version="The academy system became a controlled gate for knowledge, status, and legal power.",
                    causes=["fear of unregulated talent", "need for elite bureaucracy", "desire to control magic"],
                    consequences=["ranked education", "commoner exclusion", "noble sponsorship"],
                    affected_groups=["students", "teachers", "noble houses", "commoner scholars"],
                    unresolved_tensions=["Who was denied entry first?", "Which disciplines were sealed?"],
                    story_hooks=["The first academy entrance exam was designed to exclude a specific family."],
                )
            )

        return HistoricalEra(
            name="Age of Crowned Order",
            description="The era when empire, education, law, and status became one machine.",
            dominant_power="royal courts and founding houses" if is_empire else "regional rulers",
            dominant_belief="order is mercy",
            major_events=events,
            legacy="Modern institutions still quote this era to justify hierarchy.",
        )

    def _era_of_hidden_betrayal(self, *, is_relic: bool, is_destiny: bool) -> HistoricalEra:
        events = [
            HistoricalEvent(
                name="The Silent Revision",
                era_name="Age of Hidden Betrayal",
                year_label="Year 112",
                public_version="A necessary legal reform clarified inheritance, education, and oath-rights.",
                true_version="The reform erased families, witnesses, and teachings that challenged noble legitimacy.",
                causes=["commoner scholarship", "bloodline insecurity", "archive conflict"],
                consequences=["sealed archives", "illegal tutors", "family-name distrust"],
                affected_groups=["commoner scholars", "minor houses", "archivists", "students"],
                unresolved_tensions=["Who ordered the revision?", "Where are the original records?"],
                story_hooks=["A forbidden exam scroll contains pre-revision law."],
            )
        ]

        if is_relic:
            events.append(
                HistoricalEvent(
                    name="The First Relic Mine Collapse",
                    era_name="Age of Hidden Betrayal",
                    year_label="Year 128",
                    public_version="A tragic accident in a frontier mine.",
                    true_version="The collapse revealed relics could remember, punish, and bargain.",
                    causes=["resource greed", "unsafe extraction", "religious denial"],
                    consequences=["relic secrecy", "mine law", "black-market artifacts"],
                    affected_groups=["miners", "temples", "noble investors", "artifact smugglers"],
                    unresolved_tensions=["What woke beneath the mine?", "Who survived and was silenced?"],
                    story_hooks=["A survivor's descendant carries a relic debt."],
                )
            )

        if is_destiny:
            events.append(
                HistoricalEvent(
                    name="The First Destiny Census",
                    era_name="Age of Hidden Betrayal",
                    year_label="Year 141",
                    public_version="A protective registry for unusually gifted citizens.",
                    true_version="A political containment system for people whose existence threatened rank.",
                    causes=["rising prodigies", "succession anxiety", "prophecy disputes"],
                    consequences=["classification boards", "destiny fraud", "hidden children"],
                    affected_groups=["destined people", "families", "churches", "academies"],
                    unresolved_tensions=["How many were misclassified?", "Who disappeared after registration?"],
                    story_hooks=["A modern protagonist's name appears in an old census before they were born."],
                )
            )

        return HistoricalEra(
            name="Age of Hidden Betrayal",
            description="The era when official law became a mask for selective erasure.",
            dominant_power="archivists, judges, and noble reformers",
            dominant_belief="truth is dangerous without rank",
            major_events=events,
            legacy="The present world still operates on edited records from this era.",
        )

    def _era_of_institutional_golden_age(self, *, is_academy: bool) -> HistoricalEra:
        event_name = "The Golden Curriculum"
        public_version = "A flourishing age of learning, order, and civic greatness."
        true_version = "A polished era where exclusion became beautiful enough to be admired."

        if not is_academy:
            event_name = "The Age of Polished Order"
            public_version = "A flourishing age of infrastructure, law, and stable institutions."
            true_version = "An age where power learned to look benevolent."

        return HistoricalEra(
            name="Institutional Golden Age",
            description="The era people romanticize most, even though its beauty depended on controlled access.",
            dominant_power="academies and high courts" if is_academy else "courts and councils",
            dominant_belief="civilization is proven by refinement",
            major_events=[
                HistoricalEvent(
                    name=event_name,
                    era_name="Institutional Golden Age",
                    year_label="Year 230",
                    public_version=public_version,
                    true_version=true_version,
                    causes=["wealth concentration", "stable hierarchy", "controlled knowledge"],
                    consequences=["prestige culture", "elite rituals", "commoner resentment"],
                    affected_groups=["students", "artists", "nobles", "excluded families"],
                    unresolved_tensions=["Who paid the price for the golden age?"],
                    story_hooks=["A beloved tradition began as punishment."],
                )
            ],
            legacy="Modern citizens long for this era without understanding what it cost.",
        )

    def _era_of_current_fracture(
        self,
        *,
        is_destiny: bool,
        is_collapse: bool,
        is_relic: bool,
    ) -> HistoricalEra:
        events = [
            HistoricalEvent(
                name="The Fracture Year",
                era_name="Current Fracture",
                year_label="Current Era",
                public_version="A period of isolated unrest, student scandals, and border instability.",
                true_version="The old systems are failing together because the lies connecting them are losing force.",
                causes=["class pressure", "knowledge leaks", "institutional hypocrisy"],
                consequences=["faction recruitment", "academy crackdowns", "propaganda escalation"],
                affected_groups=["students", "commoners", "noble heirs", "border provinces"],
                unresolved_tensions=["Which system breaks first?", "Who benefits from collapse?"],
                story_hooks=["A small student scandal reveals a world-scale truth."],
            )
        ]

        if is_destiny:
            events.append(
                HistoricalEvent(
                    name="The Twenty-Seven Awakenings",
                    era_name="Current Fracture",
                    year_label="Current Era",
                    public_version="A rare generation of gifted individuals has appeared.",
                    true_version="Too many destiny-bearing people have awakened for the containment system to survive.",
                    causes=["old prophecy pressure", "historical contradiction", "institutional overreach"],
                    consequences=["classification panic", "faction kidnappings", "prophecy wars"],
                    affected_groups=["destined people", "academies", "churches", "families", "rival factions"],
                    unresolved_tensions=[
                        "Are the awakenings punishment, correction, or accident?",
                        "Which destinies are real?",
                    ],
                    story_hooks=[
                        "Some destined people are not heroes.",
                        "One destined person exists only in erased records.",
                    ],
                )
            )

        if is_relic:
            events.append(
                HistoricalEvent(
                    name="The Relic Price Surge",
                    era_name="Current Fracture",
                    year_label="Current Era",
                    public_version="Market instability caused by supply problems.",
                    true_version="Relics are reacting to the same historical pressure that destiny-bearing people feel.",
                    causes=["mine depletion", "artifact debt", "smuggling", "religious panic"],
                    consequences=["academy funding crisis", "black markets", "border exploitation"],
                    affected_groups=["miners", "students", "noble investors", "temples"],
                    unresolved_tensions=["Are relics resources or witnesses?"],
                    story_hooks=["A relic refuses to serve its legal owner."],
                )
            )

        era_name = "Current Fracture"
        if is_collapse:
            era_name = "Late Imperial Collapse"

        return HistoricalEra(
            name=era_name,
            description="The present era, where old systems still stand but no longer feel inevitable.",
            dominant_power="institutions under stress",
            dominant_belief="order must be preserved at any cost",
            major_events=events,
            legacy="This is the era where stories begin because the world can no longer remain itself.",
        )

    def _build_memory_archive(
        self,
        *,
        chronology: ChronologyProfile,
        seed_premise: str,
        desired_complexity: str,
    ) -> WorldMemoryArchive:
        archived_events = []
        for era in chronology.eras:
            archived_events.append(era.name)
            for event in era.major_events:
                archived_events.append(event.name)

        law_changes = [
            "The First Oath became enforceable law.",
            "Education rights were restricted by rank.",
            "Inheritance law was revised to protect founding bloodlines.",
        ]

        faction_changes = [
            "Academy councils gained power over regional tutors.",
            "Noble houses absorbed independent scholarly orders.",
            "Hidden archivists split from official historians.",
        ]

        destroyed_locations = [
            "The first commoner teaching hall.",
            "The collapsed relic mine beneath the border ridge.",
        ]

        lost_artifacts = [
            "The original oath register.",
            "The first examination bell.",
            "The witness map of erased families.",
        ]

        fulfilled_prophecies = [
            "A prophecy of the first false reform was fulfilled only after being mistranslated.",
        ]

        broken_promises = [
            "The First Oath was broken by those who later claimed to enforce it.",
            "The academies promised merit while preserving birth privilege.",
        ]

        world_state_snapshots = [
            f"{chronology.current_era}: institutions stressed, truth unstable, hierarchy defensive."
        ]

        if desired_complexity in {"extreme", "god_level"}:
            world_state_snapshots.append(
                "High-complexity tracking required: every major era must feed law, society, faction, belief, and character origin systems."
            )

        return WorldMemoryArchive(
            archived_events=archived_events,
            law_changes=law_changes,
            faction_changes=faction_changes,
            destroyed_locations=destroyed_locations,
            lost_artifacts=lost_artifacts,
            fulfilled_prophecies=fulfilled_prophecies,
            broken_promises=broken_promises,
            world_state_snapshots=world_state_snapshots,
        )

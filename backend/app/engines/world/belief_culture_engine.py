from typing import Any, Dict, List

from backend.app.engines.base import BaseEngine
from backend.app.schemas.foundation import EngineRunResult
from backend.app.schemas.world import BeliefSystem, CultureProfile


class BeliefCultureEngine(BaseEngine):
    """Generates religion, philosophy, myth, language, culture, ritual, and naming.

    This is the layer that makes the world feel lived-in.

    It defines:
    - what people worship
    - what they fear after death
    - what stories justify power
    - what heresies threaten institutions
    - how people name children
    - how class changes speech
    - how marriage, funerals, festivals, food, clothing, and taboo gestures work

    Later chunks use this for character identity, romance customs, social shame,
    villain ideology, prophecy conflicts, ritual scenes, dialogue style, and
    adaptation/world-bible richness.
    """

    engine_name = "world.belief_culture_engine"

    def run(self, payload: Dict[str, Any]) -> EngineRunResult:
        seed_premise = payload.get("seed_premise", "")
        genre_tags = payload.get("genre_tags", [])
        tone_tags = payload.get("tone_tags", [])
        desired_complexity = payload.get("desired_complexity", "high")

        warnings: List[str] = []

        if not seed_premise:
            warnings.append(
                "No seed_premise provided; belief and culture will use broad default structures."
            )

        belief = self._build_belief_system(
            seed_premise=seed_premise,
            genre_tags=genre_tags,
            tone_tags=tone_tags,
            desired_complexity=desired_complexity,
        )

        culture = self._build_culture_profile(
            seed_premise=seed_premise,
            genre_tags=genre_tags,
            tone_tags=tone_tags,
            desired_complexity=desired_complexity,
        )

        return self.build_result(
            success=True,
            data={
                "belief": belief.model_dump(mode="json"),
                "culture": culture.model_dump(mode="json"),
                "training_notes": [
                    "Belief and culture outputs are structured for future character identity, ideology, dialogue, and ritual generation.",
                    "Prophecy, destiny, free will, taboo, and naming fields should later feed plot, romance, villain, and faction engines.",
                    "Culture fields add specificity so generated worlds do not feel generic or interchangeable.",
                ],
            },
            warnings=warnings,
            errors=[],
            generated_object_ids=[],
        )

    def _build_belief_system(
        self,
        *,
        seed_premise: str,
        genre_tags: List[str],
        tone_tags: List[str],
        desired_complexity: str,
    ) -> BeliefSystem:
        seed = seed_premise.lower()

        is_academy = "academy" in seed or "dark_academy" in genre_tags
        is_empire = "empire" in seed or "political_fantasy" in genre_tags
        is_destiny = "destiny" in seed or "destined" in seed
        is_oath = "oath" in seed
        is_relic = "relic" in seed
        is_tragic = "tragic" in tone_tags or "collapse" in seed

        belief_summary = (
            "The dominant belief system teaches that civilization survives through vows, rank, memory, and controlled inheritance. "
            "Religion, law, education, and public virtue are intertwined so deeply that questioning one often threatens all."
        )

        if is_academy:
            belief_summary += (
                " Academies are treated almost like secular temples: exams become rites, rankings become moral signs, and teachers become authorized interpreters of worth."
            )

        gods_or_forces = [
            "The First Listener: the force said to hear every oath before law existed",
            "The Crowned Witness: divine image used to justify rulers and courts",
            "The Ledger-Saint: patron of contracts, debts, archives, and recorded names",
            "The Doorless Flame: symbol of forbidden knowledge and unapproved talent",
        ]

        if is_destiny:
            gods_or_forces.append(
                "The Many-Fated Star: a feared force associated with people whose lives bend history"
            )

        if is_relic:
            gods_or_forces.append(
                "The Buried Choir: voices believed to sleep inside old relics and memory-stone"
            )

        dead_or_forgotten_gods = [
            "The Nameless Tutor: forgotten patron of commoner scholars and illegal learning",
            "The Road-God of Witnesses: once worshiped by travelers who carried truth between regions",
            "The Mother of Unwritten Names: erased goddess of people removed from registries",
        ]

        if is_oath:
            dead_or_forgotten_gods.append(
                "The Broken Bell: a suppressed divine figure said to punish rulers who weaponize oaths"
            )

        holy_texts = [
            "The Book of First Vows",
            "The Crown Commentary",
            "The Register of Proper Names",
            "The Academy Litany of Merit",
        ]

        if is_destiny:
            holy_texts.append("The Fragmented Prophecy Index")

        if is_relic:
            holy_texts.append("The Miner Confession Scrolls")

        rituals = [
            "public oath renewal before major exams",
            "family-name recitation during marriage negotiations",
            "ink-washing ritual before entering archives",
            "silent seating at funerals to indicate rank and unresolved debt",
            "candle exchange between teacher and student at formal sponsorship",
        ]

        if is_destiny:
            rituals.append(
                "destiny veil ceremony, where unusually gifted people are tested before witnesses"
            )

        if is_relic:
            rituals.append(
                "relic cleansing ceremony performed after artifact extraction, often for public reassurance more than real safety"
            )

        taboos = [
            "speaking a founder house name while barefoot",
            "touching an archive door with an ungloved hand",
            "asking a teacher who sponsored their first student",
            "eating before a higher-ranked guest begins",
            "calling an erased person by their original legal name in public",
        ]

        if is_oath:
            taboos.append("making a promise under a bell without witnesses")

        if is_destiny:
            taboos.append("asking a classified person what their destiny costs")

        afterlife_beliefs = (
            "People believe the dead enter the Archive Beyond, where every promise, betrayal, lesson, and family name is read aloud. "
            "Those with erased names are feared to wander between records unless someone living remembers them correctly."
        )

        if is_tragic:
            afterlife_beliefs += (
                " In tragic regions, grief customs focus less on peace and more on whether the dead were allowed to be remembered truthfully."
            )

        heresies = [
            "The Merit Heresy: belief that talent outranks birth before the gods",
            "The Empty Crown Doctrine: belief that rulership is a temporary role, not sacred inheritance",
            "The Unsealed Archive Movement: belief that all historical records should be publicly readable",
            "The Broken Oath Theology: belief that the first rulers lost legitimacy before founding the courts",
        ]

        if is_destiny:
            heresies.append(
                "The Many-Fates Doctrine: belief that destiny belongs to the people, not institutions"
            )

        prophecy_system = (
            "Prophecy is treated as dangerous public infrastructure. Official prophecies must be translated, licensed, ranked, and interpreted by approved bodies. "
            "Private prophecy is considered socially infectious because interpretation can create political movements."
        )

        if is_destiny:
            prophecy_system += (
                " The current era's abnormal number of destiny-bearing people has made prophecy unstable, profitable, and politically explosive."
            )

        destiny_philosophy = (
            "Official doctrine says destiny is divine order recognized by lawful institutions. Dissident doctrine says destiny is the world's correction against systems that lied."
        )

        free_will_philosophy = (
            "Public teaching says free will exists only when disciplined by duty. Underground teachers argue that free will begins when a person refuses the role assigned by rank."
        )

        if desired_complexity in {"extreme", "god_level"}:
            belief_summary += (
                " Belief must later connect to law, class, artifacts, institutions, faction recruitment, villain ideology, and character self-concept."
            )

        return BeliefSystem(
            belief_summary=belief_summary,
            gods_or_forces=gods_or_forces,
            dead_or_forgotten_gods=dead_or_forgotten_gods,
            holy_texts=holy_texts,
            rituals=rituals,
            taboos=taboos,
            afterlife_beliefs=afterlife_beliefs,
            heresies=heresies,
            prophecy_system=prophecy_system,
            destiny_philosophy=destiny_philosophy,
            free_will_philosophy=free_will_philosophy,
        )

    def _build_culture_profile(
        self,
        *,
        seed_premise: str,
        genre_tags: List[str],
        tone_tags: List[str],
        desired_complexity: str,
    ) -> CultureProfile:
        seed = seed_premise.lower()

        is_academy = "academy" in seed or "dark_academy" in genre_tags
        is_empire = "empire" in seed or "political_fantasy" in genre_tags
        is_relic = "relic" in seed
        is_oath = "oath" in seed
        is_destiny = "destiny" in seed or "destined" in seed
        is_tragic = "tragic" in tone_tags or "collapse" in seed

        culture_summary = (
            "Culture is formal, status-aware, memory-obsessed, and quietly superstitious. "
            "People are trained to read rank through clothing, pauses, seating order, family names, and who is allowed to ask direct questions."
        )

        if is_academy:
            culture_summary += (
                " Academic achievement is treated as both intellectual success and moral proof, even though access to education is unequal."
            )

        naming_rules = [
            "Founder houses use two-part names combining lineage and public virtue.",
            "Minor nobles add academy honors to formal introductions.",
            "Commoners often carry place-based surnames that reveal labor origin.",
            "Unregistered people use market aliases, route names, or protective nicknames.",
            "Children named after erased ancestors may be watched by archive officials.",
        ]

        if is_oath:
            naming_rules.append(
                "A child can receive an oath-name only after a recognized witness confirms family legitimacy."
            )

        if is_destiny:
            naming_rules.append(
                "Families sometimes hide a destined child's true name to delay classification."
            )

        family_name_logic = (
            "Family names act as social currency. A name can open doors, invite suspicion, erase a person, protect inheritance, "
            "or turn ordinary behavior into political meaning."
        )

        honorifics = [
            "First-Born",
            "Oath-Seated",
            "Archive-Cleared",
            "Bell-Witnessed",
            "Sponsor-Bound",
            "Unregistered",
        ]

        if is_academy:
            honorifics.extend(["Exam-Ranked", "Faculty-Sealed", "Scholar-Recognized"])

        class_speech_differences = [
            "Founder families speak indirectly, using implication as proof of education.",
            "High nobles avoid asking direct favors; they create obligations through compliments.",
            "Academy students code insults as academic corrections.",
            "Merchants speak in contract metaphors.",
            "Mine workers and border families use practical speech and distrust decorative politeness.",
            "Unregistered people avoid permanent names in public conversation.",
        ]

        slang_and_insults = [
            "ink-blood: someone whose rank comes from documents instead of courage",
            "bell-empty: a person who makes promises without consequence",
            "borrowed-name: someone suspected of forged lineage",
            "gate-fed: an academy student protected by sponsors",
            "ledger-rat: a debt broker or social climber",
            "pretty lawful: someone cruel but technically correct",
        ]

        greetings = [
            "May your name be read kindly.",
            "Under witness, I arrive.",
            "No debt between us today.",
            "By road and record.",
            "May the bell sleep.",
        ]

        food_culture = [
            "noble meals are arranged by color, season, and family symbolism",
            "academy dining halls rank students through seating and serving order",
            "mine-region food is dense, salted, and associated with survival rather than prestige",
            "low-market food is portable, spicy, and designed for people who may need to run",
            "funeral meals are intentionally bland so memory, not pleasure, dominates the event",
        ]

        clothing_culture = [
            "founder houses wear oath-white during public ceremonies",
            "students wear uniforms with subtle rank markings",
            "archivists wear ink-dark gloves to avoid touching records directly",
            "border families wear layered travel cloth with hidden document pockets",
            "mine workers carry protective relic-dust scarves that elites imitate without understanding",
        ]

        marriage_customs = [
            "formal marriage begins with family-name compatibility review",
            "higher-status marriages require witness seating charts",
            "cross-class marriages demand legal transformation rituals",
            "secret marriages are valid spiritually but dangerous legally",
            "broken engagements are announced through returned ink ribbons",
        ]

        funeral_customs = [
            "names are read in order of legal recognition, not grief",
            "erased people receive hidden roadside memorials instead of public stones",
            "families leave one empty chair for unresolved debts",
            "students place exam ink beside dead classmates",
            "mine families bury tools when bodies cannot be recovered",
        ]

        festivals = [
            "The Founding Bell Festival",
            "The Examination Lantern Week",
            "The Road Witness Night",
            "The Archive Silence Day",
            "The Ashspring Renewal Procession",
        ]

        if is_relic:
            festivals.append("The Relic Cleansing Fair")

        if is_destiny:
            festivals.append("The Starless Vigil, when families pray their children are ordinary")

        taboo_gestures = [
            "placing a bare palm on a sealed door",
            "turning one's chair away from a speaker of higher rank",
            "offering food before name order is established",
            "ringing a bell casually",
            "writing a living person's name in ash",
        ]

        if is_tragic:
            taboo_gestures.append(
                "smiling during a vow, because old stories say broken promises began with beautiful smiles"
            )

        if desired_complexity in {"extreme", "god_level"}:
            culture_summary += (
                " Cultural rules should later feed dialogue style, romance obstacles, class signaling, disguise scenes, public shame, and adaptation design."
            )
            festivals.append(
                "The Day of Corrected Names, when official records are celebrated and hidden families mourn privately"
            )

        return CultureProfile(
            culture_summary=culture_summary,
            naming_rules=naming_rules,
            family_name_logic=family_name_logic,
            honorifics=honorifics,
            class_speech_differences=class_speech_differences,
            slang_and_insults=slang_and_insults,
            greetings=greetings,
            food_culture=food_culture,
            clothing_culture=clothing_culture,
            marriage_customs=marriage_customs,
            funeral_customs=funeral_customs,
            festivals=festivals,
            taboo_gestures=taboo_gestures,
        )

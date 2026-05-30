from typing import Any, Dict, List

from backend.app.engines.base import BaseEngine
from backend.app.schemas.foundation import EngineRunResult
from backend.app.schemas.world import (
    ClassTier,
    DemographicsProfile,
    SocietyProfile,
)


class DemographicsSocietyEngine(BaseEngine):
    """Generates demographics, society, class, hierarchy, and status logic.

    This engine defines who lives in the world and what social systems shape
    their opportunities, fears, ambitions, shame, honor, education, marriage,
    inheritance, and mobility.

    Later, Chunk 3 character generation will use this layer to decide:
    - birth status
    - class pressure
    - family expectations
    - education access
    - social wounds
    - character ambition
    - romance obstacles
    - villain resentment
    - rebellion potential
    """

    engine_name = "world.demographics_society_engine"

    def run(self, payload: Dict[str, Any]) -> EngineRunResult:
        seed_premise = payload.get("seed_premise", "")
        genre_tags = payload.get("genre_tags", [])
        tone_tags = payload.get("tone_tags", [])
        desired_complexity = payload.get("desired_complexity", "high")
        target_format = payload.get("target_format", "novel_series")

        warnings: List[str] = []

        if not seed_premise:
            warnings.append(
                "No seed_premise provided; demographics and society will use broad default hierarchy."
            )

        demographics = self._build_demographics(
            seed_premise=seed_premise,
            genre_tags=genre_tags,
            desired_complexity=desired_complexity,
            target_format=target_format,
        )

        society = self._build_society(
            seed_premise=seed_premise,
            genre_tags=genre_tags,
            tone_tags=tone_tags,
            desired_complexity=desired_complexity,
        )

        return self.build_result(
            success=True,
            data={
                "demographics": demographics.model_dump(mode="json"),
                "society": society.model_dump(mode="json"),
                "training_notes": [
                    "Demographics are structured for later population-scale simulation.",
                    "Class tiers are structured for future character birth, status, and mobility generation.",
                    "Society rules should feed romance, rivalry, villain, faction, and rebellion systems.",
                ],
            },
            warnings=warnings,
            errors=[],
            generated_object_ids=[],
        )

    def _build_demographics(
        self,
        *,
        seed_premise: str,
        genre_tags: List[str],
        desired_complexity: str,
        target_format: str,
    ) -> DemographicsProfile:
        seed = seed_premise.lower()
        format_key = target_format.lower()

        is_empire = "empire" in seed or "political_fantasy" in genre_tags
        is_academy = "academy" in seed or "dark_academy" in genre_tags
        is_destiny = "destiny" in seed or "destined" in seed
        is_civilization = "civilization" in seed or "simulation" in format_key
        is_relic = "relic" in seed

        if is_civilization:
            estimated_population = 12_500_000
            academy_eligible_population = 90_000
        elif is_empire:
            estimated_population = 38_000_000
            academy_eligible_population = 240_000
        else:
            estimated_population = 4_800_000
            academy_eligible_population = 32_000

        if desired_complexity in {"extreme", "god_level"}:
            estimated_population = int(estimated_population * 1.4)
            academy_eligible_population = int(academy_eligible_population * 1.25)

        urban_rural_split = {
            "capital_and_major_cities": 0.22,
            "academy_towns": 0.06 if is_academy else 0.02,
            "resource_regions": 0.14 if is_relic else 0.08,
            "borderlands": 0.12,
            "rural_villages": 0.38,
            "unregistered_or_hidden_populations": 0.08,
        }

        class_distribution = {
            "S_class_founder_bloodlines": 0.002,
            "A_class_high_nobility_and_top_officials": 0.018,
            "B_class_minor_nobles_licensed_scholars_elite_merchants": 0.08,
            "C_class_soldiers_artisans_low_officials_registered_students": 0.18,
            "D_class_laborers_farmers_servants_mine_workers": 0.52,
            "E_class_unregistered_exiles_debt_bound_people": 0.20,
        }

        age_distribution = {
            "children": 0.22,
            "youth_training_age": 0.16,
            "adult_working_age": 0.48,
            "elder_memory_keepers": 0.14,
        }

        migration_patterns = [
            "rural youth attempt to enter academy towns through exams, sponsorship, or forged records",
            "mine families move between resource regions after collapses, debts, and contract shifts",
            "borderland families migrate inward during military pressure but face trust restrictions",
            "unregistered families move through low-market networks to avoid classification",
        ]

        if is_destiny:
            migration_patterns.append(
                "families suspected of producing destined children relocate before classification boards arrive"
            )

        minority_groups = [
            "border oath-families whose legal status is disputed",
            "descendants of erased commoner scholars",
            "mine-worker clans marked by relic sickness",
            "low-market multilingual broker families",
            "religious minorities preserving pre-imperial prayers",
        ]

        destined_person_rarity = "not tracked publicly"

        if is_destiny:
            destined_person_rarity = (
                "extremely rare but historically disruptive: approximately 1 in 1.5 million people show world-level destiny pressure, "
                "but the current era has an abnormal cluster of 27 known or suspected destiny-bearing people"
            )

        literacy_distribution = {
            "founder_bloodlines": 0.99,
            "high_nobility": 0.96,
            "minor_nobility_and_scholars": 0.82,
            "urban_merchants": 0.61,
            "soldiers_and_artisans": 0.38,
            "rural_laborers": 0.18,
            "unregistered_populations": 0.11,
        }

        return DemographicsProfile(
            estimated_population=estimated_population,
            urban_rural_split=urban_rural_split,
            class_distribution=class_distribution,
            age_distribution=age_distribution,
            migration_patterns=migration_patterns,
            minority_groups=minority_groups,
            destined_person_rarity=destined_person_rarity,
            literacy_distribution=literacy_distribution,
            academy_eligible_population=academy_eligible_population if is_academy else None,
        )

    def _build_society(
        self,
        *,
        seed_premise: str,
        genre_tags: List[str],
        tone_tags: List[str],
        desired_complexity: str,
    ) -> SocietyProfile:
        seed = seed_premise.lower()

        is_academy = "academy" in seed or "dark_academy" in genre_tags
        is_political = "empire" in seed or "political_fantasy" in genre_tags
        is_destiny = "destiny" in seed or "destined" in seed
        is_relic = "relic" in seed
        is_oath = "oath" in seed

        class_tiers = [
            ClassTier(
                name="S-Class Founder Bloodlines",
                rank=1,
                privileges=[
                    "automatic legitimacy in courts",
                    "private academy access",
                    "right to sponsor or block elite students",
                    "protected inheritance rituals",
                    "access to sealed political knowledge",
                ],
                restrictions=[
                    "bound by public oath performance",
                    "cannot marry without house review",
                    "must preserve family myth even when false",
                ],
                status_symbols=[
                    "ancestral signet",
                    "oath-white formal clothing",
                    "private carriage route",
                    "right to speak first in public ceremonies",
                ],
                mobility_paths=[
                    "almost no upward path exists into this tier except marriage, adoption, forged lineage, or destiny crisis",
                ],
                common_conflicts=[
                    "succession rivalry",
                    "fear of exposure",
                    "family duty vs private desire",
                    "resentment toward unrankable prodigies",
                ],
            ),
            ClassTier(
                name="A-Class High Nobility and Imperial Officials",
                rank=2,
                privileges=[
                    "court access",
                    "high academy sponsorship",
                    "command over regional law",
                    "priority healing and travel",
                ],
                restrictions=[
                    "dependent on founder approval",
                    "status can collapse after scandal",
                    "children must pass reputation inspections",
                ],
                status_symbols=[
                    "colored rank sashes",
                    "court attendance seals",
                    "private tutors",
                ],
                mobility_paths=[
                    "military distinction",
                    "marriage alliance",
                    "exceptional service to founder houses",
                ],
                common_conflicts=[
                    "ambition blocked by S-Class families",
                    "political blackmail",
                    "secret debt",
                ],
            ),
            ClassTier(
                name="B-Class Minor Nobles, Licensed Scholars, and Elite Merchants",
                rank=3,
                privileges=[
                    "limited academy entrance",
                    "licensed business ownership",
                    "legal testimony credibility",
                    "some access to controlled books",
                ],
                restrictions=[
                    "requires sponsorship for high offices",
                    "cannot challenge founder bloodlines directly",
                    "wealth is respected but not trusted",
                ],
                status_symbols=[
                    "merchant house ledgers",
                    "licensed scholar pins",
                    "secondary academy uniforms",
                ],
                mobility_paths=[
                    "exam success",
                    "sponsorship",
                    "wealth conversion into marriage alliance",
                ],
                common_conflicts=[
                    "class anxiety",
                    "desire for noble recognition",
                    "resentment from lower classes",
                    "humiliation by older houses",
                ],
            ),
            ClassTier(
                name="C-Class Soldiers, Artisans, Low Officials, and Registered Students",
                rank=4,
                privileges=[
                    "registered work rights",
                    "basic legal protection",
                    "limited education access",
                    "military advancement possibility",
                ],
                restrictions=[
                    "movement often logged",
                    "speech against nobles punished faster",
                    "family reputation fragile",
                ],
                status_symbols=[
                    "work badges",
                    "unit marks",
                    "public-school certificates",
                ],
                mobility_paths=[
                    "military heroism",
                    "craft mastery",
                    "rare exam success",
                    "patronage",
                ],
                common_conflicts=[
                    "overwork",
                    "rank humiliation",
                    "family sacrifice",
                    "being used by higher factions",
                ],
            ),
            ClassTier(
                name="D-Class Laborers, Farmers, Servants, and Mine Workers",
                rank=5,
                privileges=[
                    "local community protection",
                    "informal knowledge networks",
                    "access to oral memory outside official records",
                ],
                restrictions=[
                    "restricted schooling",
                    "low legal credibility",
                    "high debt exposure",
                    "dangerous work assignments",
                ],
                status_symbols=[
                    "regional clothing",
                    "labor tokens",
                    "family work tools",
                ],
                mobility_paths=[
                    "patronage",
                    "illegal tutoring",
                    "faction recruitment",
                    "marriage into a registered family",
                ],
                common_conflicts=[
                    "exploitation",
                    "education denial",
                    "medical inequality",
                    "children taken by institutions",
                ],
            ),
            ClassTier(
                name="E-Class Unregistered, Exiled, Debt-Bound, and Erased People",
                rank=6,
                privileges=[
                    "freedom from some official tracking",
                    "access to hidden networks",
                    "knowledge of routes and truths official society ignores",
                ],
                restrictions=[
                    "almost no legal protection",
                    "cannot testify against ranked citizens",
                    "vulnerable to disappearance",
                    "barred from formal education and inheritance",
                ],
                status_symbols=[
                    "absence of legal marks",
                    "coded clothing repairs",
                    "market aliases",
                ],
                mobility_paths=[
                    "forged identity",
                    "rebel protection",
                    "exceptional usefulness",
                    "destiny shock",
                ],
                common_conflicts=[
                    "survival under invisibility",
                    "identity theft",
                    "black-market dependency",
                    "being morally judged by people who benefit from the system",
                ],
            ),
        ]

        society_summary = (
            "Society is structured as a legitimacy pyramid: birth, education, oath-status, wealth, and institutional approval "
            "decide who is believed, protected, trained, healed, married, promoted, or erased."
        )

        if is_academy:
            society_summary += (
                " Academies function as social machines that convert family status into future authority while pretending to measure pure merit."
            )

        if is_destiny:
            society_summary += (
                " Destiny-bearing people threaten this pyramid because their importance cannot be fully predicted by birth rank."
            )

        birth_privilege_rules = [
            "Family name affects legal credibility before evidence is heard.",
            "Children inherit trust or suspicion before they act.",
            "Founder bloodlines are assumed competent until publicly disproven.",
            "Lower-class talent must be repeatedly certified while noble talent is presumed latent.",
        ]

        if is_oath:
            birth_privilege_rules.append(
                "Oath-line records can protect or condemn descendants generations after the original promise."
            )

        marriage_rules = [
            "High-status marriages require house approval and reputation review.",
            "Marriage can convert money into rank but rarely into trust.",
            "Cross-class romance is tolerated only when it benefits a stronger institution.",
            "Secret marriages can destroy inheritance claims.",
        ]

        inheritance_rules = [
            "Inheritance prioritizes bloodline legitimacy, public reputation, and oath-record continuity.",
            "Adopted heirs are accepted only if a recognized house benefits.",
            "Debt, scandal, or forbidden study can weaken inheritance rights.",
            "Unregistered children cannot inherit without dangerous legal transformation.",
        ]

        reputation_rules = [
            "Public shame can damage a family more than private crime.",
            "A noble scandal is called tragedy; a commoner scandal is called proof.",
            "Academic failure follows a student into marriage, work, and legal credibility.",
            "Rumor moves faster in elite circles than official letters.",
        ]

        shame_systems = [
            "public examination rankings",
            "family disgrace ceremonies",
            "silent seating exclusions at formal events",
            "withdrawal of sponsorship",
            "marriage cancellation notices",
        ]

        honor_systems = [
            "oath performance",
            "dueling etiquette",
            "academic distinction",
            "military service",
            "public generosity from powerful families",
        ]

        discrimination_systems = [
            "education access by rank",
            "trial credibility by family name",
            "healing access by social usefulness",
            "travel permit priority",
            "knowledge licensing",
            "speech expectations by class",
        ]

        if is_relic:
            discrimination_systems.append(
                "mine-region families are treated as spiritually useful but socially contaminated"
            )

        destined_person_social_impact = "Destiny has no formal social category in stable eras."

        if is_destiny:
            destined_person_social_impact = (
                "Destined people destabilize society because they can outrank their birth story. "
                "Elites try to sponsor, classify, marry, discredit, or erase them before they form independent alliances."
            )

        if desired_complexity in {"extreme", "god_level"}:
            society_summary += (
                " Every class rule should later feed character creation, romance barriers, rivalry structures, faction recruitment, villain psychology, and rebellion pressure."
            )
            reputation_rules.append(
                "A person's social meaning is calculated from birth, visible behavior, hidden records, faction usefulness, and symbolic threat."
            )

        return SocietyProfile(
            society_summary=society_summary,
            class_tiers=class_tiers,
            birth_privilege_rules=birth_privilege_rules,
            marriage_rules=marriage_rules,
            inheritance_rules=inheritance_rules,
            reputation_rules=reputation_rules,
            shame_systems=shame_systems,
            honor_systems=honor_systems,
            discrimination_systems=discrimination_systems,
            destined_person_social_impact=destined_person_social_impact,
        )

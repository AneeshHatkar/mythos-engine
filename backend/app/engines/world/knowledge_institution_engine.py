from typing import Any, Dict, List

from backend.app.engines.base import BaseEngine
from backend.app.schemas.foundation import EngineRunResult
from backend.app.schemas.world import InstitutionProfile, KnowledgeEducationProfile


class KnowledgeInstitutionEngine(BaseEngine):
    """Generates knowledge, education, censorship, archives, and institutions.

    This is the layer that decides who is allowed to know, study, teach,
    publish, archive, research, heal, judge, imprison, finance, spy, or govern.

    It defines:
    - literacy access
    - academy gates
    - forbidden books
    - public vs secret archives
    - propaganda and censorship
    - information punishments
    - institutions and their hidden purposes
    - corruption and internal factions

    Later chunks use this for character education, mystery clues, institutional
    villains, research arcs, faction recruitment, social mobility, and AI/ML
    training metadata about knowledge systems.
    """

    engine_name = "world.knowledge_institution_engine"

    def run(self, payload: Dict[str, Any]) -> EngineRunResult:
        seed_premise = payload.get("seed_premise", "")
        genre_tags = payload.get("genre_tags", [])
        tone_tags = payload.get("tone_tags", [])
        desired_complexity = payload.get("desired_complexity", "high")

        warnings: List[str] = []

        if not seed_premise:
            warnings.append(
                "No seed_premise provided; knowledge and institutions will use broad default structures."
            )

        knowledge = self._build_knowledge_education(
            seed_premise=seed_premise,
            genre_tags=genre_tags,
            tone_tags=tone_tags,
            desired_complexity=desired_complexity,
        )

        institutions = self._build_institutions(
            seed_premise=seed_premise,
            genre_tags=genre_tags,
            tone_tags=tone_tags,
            desired_complexity=desired_complexity,
        )

        return self.build_result(
            success=True,
            data={
                "knowledge_education": knowledge.model_dump(mode="json"),
                "institutions": [institution.model_dump(mode="json") for institution in institutions],
                "training_notes": [
                    "Knowledge controls are structured for future mystery, education, censorship, and archive systems.",
                    "Institutions include public purpose and hidden purpose for future conflict generation.",
                    "Institution corruption and internal factions should later feed faction simulation and character arcs.",
                    "This layer should be checked against society, law, economy, belief, and technology before training eligibility.",
                ],
            },
            warnings=warnings,
            errors=[],
            generated_object_ids=[],
        )

    def _build_knowledge_education(
        self,
        *,
        seed_premise: str,
        genre_tags: List[str],
        tone_tags: List[str],
        desired_complexity: str,
    ) -> KnowledgeEducationProfile:
        seed = seed_premise.lower()

        is_academy = "academy" in seed or "dark_academy" in genre_tags
        is_empire = "empire" in seed or "political_fantasy" in genre_tags
        is_oath = "oath" in seed
        is_relic = "relic" in seed
        is_destiny = "destiny" in seed or "destined" in seed
        is_dystopian = "dystopian" in genre_tags or "surveillance" in seed

        literacy_rate_notes = (
            "Literacy is not just an education metric; it is a power boundary. Founder houses and high nobles are nearly fully literate, "
            "licensed scholars and merchants are selectively literate, soldiers and artisans read practical documents, and rural or erased populations rely on oral memory."
        )

        if is_academy:
            literacy_rate_notes += (
                " Academy literacy is stratified: students may read material required for rank but not necessarily the texts that explain the system controlling them."
            )

        education_access_rules = [
            "Basic literacy is permitted when it improves labor, tax compliance, or military usefulness.",
            "Advanced theory requires institutional sponsorship.",
            "Royal-class knowledge requires bloodline approval or exceptional state interest.",
            "A student can lose access because of family scandal, debt, romantic scandal, or political suspicion.",
            "Teachers who educate outside their license risk punishment even if their student succeeds.",
        ]

        if is_destiny:
            education_access_rules.append(
                "Destiny-bearing people are offered education only when institutions believe they can be contained, sponsored, or redirected."
            )

        academy_entrance_rules = [
            "Entrance requires exam performance, family verification, sponsor review, and reputation screening.",
            "Commoners may sit for public exams but require a patron to convert success into admission.",
            "A failed entrance attempt can damage a family's reputation for a generation.",
            "Certain sealed disciplines are invitation-only and never listed in public catalogs.",
            "Border applicants face additional loyalty review.",
        ]

        if is_oath:
            academy_entrance_rules.append(
                "Applicants must swear an entrance oath that can later be used in disciplinary court."
            )

        forbidden_books = [
            "The Pre-Revision Teaching Lists",
            "The Unranked Grammar of Royal Magic",
            "Treatise on Merit Before Blood",
            "The First Oath Witness Map",
            "The Low Lantern Anatomy of Class",
            "The Book of Names Removed from the Register",
        ]

        if is_relic:
            forbidden_books.append("The Miner's Guide to Relic Debt")

        if is_destiny:
            forbidden_books.append("The Unlicensed Destiny Index")

        public_archives = [
            "Crown Registry Hall",
            "Academy Public Catalog",
            "Approved Genealogy Office",
            "Tax Road Ledger",
            "Public Court Records",
        ]

        secret_archives = [
            "The Silent Register",
            "The Sealed Founder Room",
            "The Witness Vault",
            "The Misclassified Destiny Cabinet",
            "The Relic Debt Ledger",
            "The Archive of Failed Prophecies",
        ]

        propaganda_systems = [
            "school primers that describe hierarchy as civic mercy",
            "academy ceremonies that equate rank with virtue",
            "public trials staged as moral education",
            "festival speeches about unity during tax and resource crises",
            "official maps that omit rebellious or erased places",
        ]

        if is_dystopian:
            propaganda_systems.append(
                "behavior-score reports framed as public safety education"
            )

        censorship_methods = [
            "ranked library locks",
            "publication licenses",
            "teacher audits",
            "archive access oaths",
            "confiscation of family records",
            "public correction notices",
            "rumor poisoning through paid informants",
        ]

        if is_empire:
            censorship_methods.append(
                "reclassification of political testimony as regional superstition"
            )

        information_punishments = [
            "library suspension",
            "exam ban",
            "memory credibility review",
            "forced public correction",
            "sponsor withdrawal",
            "archive labor assignment",
            "travel permit cancellation",
            "family record freezing",
        ]

        if is_destiny:
            information_punishments.append(
                "destiny classification confinement after unauthorized prophecy research"
            )

        if desired_complexity in {"extreme", "god_level"}:
            literacy_rate_notes += (
                " Future systems should track knowledge access as a dynamic variable affecting social mobility, rebellion, romance, investigation, and innovation."
            )
            information_punishments.append(
                "training-ineligible mark for records proven to be intentionally corrupted"
            )

        return KnowledgeEducationProfile(
            literacy_rate_notes=literacy_rate_notes,
            education_access_rules=education_access_rules,
            academy_entrance_rules=academy_entrance_rules,
            forbidden_books=forbidden_books,
            public_archives=public_archives,
            secret_archives=secret_archives,
            propaganda_systems=propaganda_systems,
            censorship_methods=censorship_methods,
            information_punishments=information_punishments,
        )

    def _build_institutions(
        self,
        *,
        seed_premise: str,
        genre_tags: List[str],
        tone_tags: List[str],
        desired_complexity: str,
    ) -> List[InstitutionProfile]:
        seed = seed_premise.lower()

        is_academy = "academy" in seed or "dark_academy" in genre_tags
        is_empire = "empire" in seed or "political_fantasy" in genre_tags
        is_oath = "oath" in seed
        is_relic = "relic" in seed
        is_destiny = "destiny" in seed or "destined" in seed
        is_dystopian = "dystopian" in genre_tags or "surveillance" in seed

        institutions = [
            InstitutionProfile(
                name="The Ashen Crown Academy",
                institution_type="elite_academy",
                public_purpose="Educate the most promising minds for service, leadership, scholarship, and civic order.",
                hidden_purpose="Convert controlled education into future political obedience while identifying dangerous talent early.",
                entrance_rules=[
                    "exam performance",
                    "family verification",
                    "sponsor approval",
                    "reputation inspection",
                    "oath of institutional loyalty",
                ],
                rank_system=[
                    "Unseated Applicant",
                    "Conditional Student",
                    "Sponsor-Bound Student",
                    "Ranked Scholar",
                    "Faculty-Sealed Candidate",
                    "Council-Recognized Graduate",
                ],
                corruption_level=0.72,
                internal_factions=[
                    "traditionalist faculty",
                    "reformist tutors",
                    "noble student bloc",
                    "commoner scholarship circle",
                    "disciplinary office loyalists",
                ],
                story_uses=[
                    "training arc",
                    "rivalry system",
                    "forbidden romance",
                    "teacher betrayal",
                    "secret curriculum reveal",
                ],
            ),
            InstitutionProfile(
                name="The Silent Register",
                institution_type="secret_archive",
                public_purpose="Maintain accurate legal, inheritance, educational, and oath records.",
                hidden_purpose="Control which truths can become legally real and which people can be erased.",
                entrance_rules=[
                    "memory aptitude",
                    "institutional sponsorship",
                    "silence oath",
                    "family vulnerability review",
                ],
                rank_system=[
                    "Copyist",
                    "Witness Clerk",
                    "Sealed Indexer",
                    "Revision Officer",
                    "Name-Judge",
                ],
                corruption_level=0.84,
                internal_factions=[
                    "truth-preservation faction",
                    "court-loyal revisionists",
                    "blackmail archivists",
                    "hidden restorationists",
                ],
                story_uses=[
                    "lineage reveal",
                    "archive heist",
                    "mystery clue chain",
                    "legal resurrection",
                    "villain evidence",
                ],
            ),
            InstitutionProfile(
                name="The High Crown Court",
                institution_type="central_court",
                public_purpose="Interpret law, settle inheritance, preserve civil order, and arbitrate disputes.",
                hidden_purpose="Translate power into legality while protecting the appearance of neutral justice.",
                entrance_rules=[
                    "legal rank",
                    "sponsor recommendation",
                    "family credibility",
                    "court apprenticeship",
                ],
                rank_system=[
                    "Petition Clerk",
                    "Junior Advocate",
                    "Oath Advocate",
                    "Inheritance Judge",
                    "High Crown Justice",
                ],
                corruption_level=0.79,
                internal_factions=[
                    "founder-house loyalists",
                    "procedural purists",
                    "debt-influenced judges",
                    "quiet reformers",
                ],
                story_uses=[
                    "trial scene",
                    "inheritance reversal",
                    "public shame",
                    "legal trap",
                    "class injustice",
                ],
            ),
            InstitutionProfile(
                name="The Low Lantern Exchange",
                institution_type="black_market_institution",
                public_purpose="Officially nonexistent.",
                hidden_purpose="Move forbidden books, forged identities, illegal healing, private messages, and truths outside legal systems.",
                entrance_rules=[
                    "trusted introducer",
                    "debt marker",
                    "shared secret",
                    "market alias",
                ],
                rank_system=[
                    "Runner",
                    "Broker",
                    "Book-Mover",
                    "Healer-Contact",
                    "Name-Forgemaster",
                ],
                corruption_level=0.67,
                internal_factions=[
                    "survival brokers",
                    "rebel-aligned smugglers",
                    "elite-funded informants",
                    "healer underground",
                ],
                story_uses=[
                    "secret meeting",
                    "black-market deal",
                    "forged records",
                    "morally gray rescue",
                    "spy route",
                ],
            ),
            InstitutionProfile(
                name="The Temple of First Witness",
                institution_type="religious_legal_order",
                public_purpose="Preserve oath rituals, certify promises, guide funerals, and interpret sacred legitimacy.",
                hidden_purpose="Protect the approved version of the First Oath and suppress the possibility that sacred law began with betrayal.",
                entrance_rules=[
                    "ritual literacy",
                    "oath purity review",
                    "family-background inspection",
                    "temple apprenticeship",
                ],
                rank_system=[
                    "Candle-Bearer",
                    "Witness Novice",
                    "Oath Reader",
                    "Bell Interpreter",
                    "High Certifier",
                ],
                corruption_level=0.69,
                internal_factions=[
                    "orthodox oath-priests",
                    "broken-oath heresy sympathizers",
                    "court-aligned certifiers",
                    "mourning clergy",
                ],
                story_uses=[
                    "wedding vow",
                    "funeral revelation",
                    "religious trial",
                    "heresy accusation",
                    "prophecy conflict",
                ],
            ),
            InstitutionProfile(
                name="The Crown Bank of Ledgers",
                institution_type="bank_finance",
                public_purpose="Manage loans, trade credit, tuition bonds, house debts, and public finance.",
                hidden_purpose="Turn social dependency into financial control and quietly decide which families remain viable.",
                entrance_rules=[
                    "licensed accounting education",
                    "family trust review",
                    "patron recommendation",
                    "debt oath",
                ],
                rank_system=[
                    "Ledger Clerk",
                    "Debt Assessor",
                    "House Auditor",
                    "Sponsorship Broker",
                    "Crown Financier",
                ],
                corruption_level=0.76,
                internal_factions=[
                    "noble debt managers",
                    "academy finance wing",
                    "relic speculation circle",
                    "low-market laundering contacts",
                ],
                story_uses=[
                    "debt trap",
                    "tuition crisis",
                    "family ruin",
                    "economic villain",
                    "bribery trail",
                ],
            ),
            InstitutionProfile(
                name="The Border March Office",
                institution_type="military_administration",
                public_purpose="Protect borderlands, regulate travel, supervise checkpoints, and defend against external threats.",
                hidden_purpose="Control inconvenient witnesses, exile political problems, and keep the capital's map incomplete.",
                entrance_rules=[
                    "military service",
                    "regional loyalty review",
                    "oath to border command",
                    "survival certification",
                ],
                rank_system=[
                    "Road Guard",
                    "Checkpoint Scribe",
                    "Border Captain",
                    "March Commander",
                    "Frontier Marshal",
                ],
                corruption_level=0.61,
                internal_factions=[
                    "capital loyalists",
                    "border autonomy faction",
                    "smuggler-tolerant officers",
                    "anti-relic militants",
                ],
                story_uses=[
                    "exile arc",
                    "checkpoint conflict",
                    "outside-world reveal",
                    "military betrayal",
                    "refugee crisis",
                ],
            ),
        ]

        if is_relic:
            institutions.append(
                InstitutionProfile(
                    name="The Relic Appraisal and Recovery Board",
                    institution_type="research_commercial_board",
                    public_purpose="Safely classify, appraise, recover, and distribute relic materials.",
                    hidden_purpose="Hide relic debt, control artifact ownership, and protect investors before workers.",
                    entrance_rules=[
                        "technical certification",
                        "investor clearance",
                        "temple inspection license",
                        "non-disclosure oath",
                    ],
                    rank_system=[
                        "Field Appraiser",
                        "Mine Recorder",
                        "Artifact Certifier",
                        "Debt Risk Analyst",
                        "Recovery Director",
                    ],
                    corruption_level=0.86,
                    internal_factions=[
                        "profit-first investors",
                        "terrified researchers",
                        "temple purists",
                        "mine-family sympathizers",
                    ],
                    story_uses=[
                        "artifact discovery",
                        "resource coverup",
                        "mine disaster inquiry",
                        "relic corruption",
                        "scientific heresy",
                    ],
                )
            )

        if is_destiny:
            institutions.append(
                InstitutionProfile(
                    name="The Destiny Classification Board",
                    institution_type="state_classification_body",
                    public_purpose="Protect society and gifted individuals by evaluating destiny-bearing people.",
                    hidden_purpose="Prevent unapproved destiny from becoming independent political power.",
                    entrance_rules=[
                        "state appointment",
                        "academy endorsement",
                        "prophecy-literacy test",
                        "security clearance",
                    ],
                    rank_system=[
                        "Intake Examiner",
                        "Fate Scribe",
                        "Classification Advocate",
                        "Containment Magistrate",
                        "Board Oracle",
                    ],
                    corruption_level=0.81,
                    internal_factions=[
                        "containment hardliners",
                        "prophecy opportunists",
                        "student protection advocates",
                        "noble sponsor agents",
                    ],
                    story_uses=[
                        "false ranking",
                        "chosen-one containment",
                        "kidnapping threat",
                        "rival destiny file",
                        "classification trial",
                    ],
                )
            )

        if is_dystopian:
            institutions.append(
                InstitutionProfile(
                    name="The Civic Observation Bureau",
                    institution_type="surveillance_administration",
                    public_purpose="Prevent crime, rebellion, illegal study, and social destabilization.",
                    hidden_purpose="Convert ordinary behavior into political leverage.",
                    entrance_rules=[
                        "loyalty screening",
                        "data-handling license",
                        "informant sponsorship",
                        "behavioral compliance oath",
                    ],
                    rank_system=[
                        "Street Observer",
                        "Message Reader",
                        "Movement Auditor",
                        "Risk Classifier",
                        "Civic Stability Director",
                    ],
                    corruption_level=0.88,
                    internal_factions=[
                        "true believers",
                        "blackmail collectors",
                        "anti-rebellion analysts",
                        "secret reformers",
                    ],
                    story_uses=[
                        "surveillance escape",
                        "informant reveal",
                        "privacy conflict",
                        "public shame manipulation",
                        "dystopian pressure",
                    ],
                )
            )

        if desired_complexity in {"extreme", "god_level"}:
            institutions.append(
                InstitutionProfile(
                    name="The Institute of Corrected Futures",
                    institution_type="experimental_research_order",
                    public_purpose="Study long-term risk, institutional stability, prophecy failures, and social prediction.",
                    hidden_purpose="Model possible rebellions and quietly alter children, curricula, laws, and marriages before threats mature.",
                    entrance_rules=[
                        "rare analytical talent",
                        "sealed recommendation",
                        "psychological evaluation",
                        "willingness to erase failed predictions",
                    ],
                    rank_system=[
                        "Junior Scenario Clerk",
                        "Pattern Scholar",
                        "Social Forecast Analyst",
                        "Corrective Planner",
                        "Future Custodian",
                    ],
                    corruption_level=0.83,
                    internal_factions=[
                        "cold utilitarians",
                        "failed prophecy skeptics",
                        "protective interventionists",
                        "political manipulators",
                    ],
                    story_uses=[
                        "predictive villain",
                        "research horror",
                        "childhood manipulation reveal",
                        "future-choice paradox",
                        "AI/ML-like evaluation layer for later MythOS systems",
                    ],
                )
            )

        return institutions

from typing import Any, Dict, List

from backend.app.engines.base import BaseEngine
from backend.app.schemas.foundation import EngineRunResult
from backend.app.schemas.world import (
    FactionSeed,
    MilitarySecurityProfile,
    PowerStructureProfile,
)


class PowerFactionMilitaryEngine(BaseEngine):
    """Generates power structures, faction seeds, and military/security logic.

    This is the organized power layer of the world.

    It defines:
    - who appears to rule
    - who actually rules
    - who benefits from the current system
    - who wants to break it
    - who controls violence
    - who controls surveillance
    - who can betray whom
    - who can recruit future characters

    Later chunks will expand these seeds into full faction simulation, villain
    systems, rebellion arcs, political intrigue, war arcs, and character danger.
    """

    engine_name = "world.power_faction_military_engine"

    def run(self, payload: Dict[str, Any]) -> EngineRunResult:
        seed_premise = payload.get("seed_premise", "")
        genre_tags = payload.get("genre_tags", [])
        tone_tags = payload.get("tone_tags", [])
        desired_complexity = payload.get("desired_complexity", "high")

        warnings: List[str] = []

        if not seed_premise:
            warnings.append(
                "No seed_premise provided; power/faction/military systems will use broad default structure."
            )

        power_structure = self._build_power_structure(
            seed_premise=seed_premise,
            genre_tags=genre_tags,
            tone_tags=tone_tags,
            desired_complexity=desired_complexity,
        )

        military_security = self._build_military_security(
            seed_premise=seed_premise,
            genre_tags=genre_tags,
            tone_tags=tone_tags,
            desired_complexity=desired_complexity,
        )

        return self.build_result(
            success=True,
            data={
                "power_structure": power_structure.model_dump(mode="json"),
                "military_security": military_security.model_dump(mode="json"),
                "training_notes": [
                    "Faction seeds are structured for future faction simulation and character recruitment.",
                    "Betrayal probability creates future conflict modeling fields.",
                    "Military/security structures will feed law enforcement, rebellion, villain, and war systems.",
                    "Power logic should later be checked against society, economy, law, and belief systems.",
                ],
            },
            warnings=warnings,
            errors=[],
            generated_object_ids=[],
        )

    def _build_power_structure(
        self,
        *,
        seed_premise: str,
        genre_tags: List[str],
        tone_tags: List[str],
        desired_complexity: str,
    ) -> PowerStructureProfile:
        seed = seed_premise.lower()

        is_academy = "academy" in seed or "dark_academy" in genre_tags
        is_empire = "empire" in seed or "political_fantasy" in genre_tags
        is_destiny = "destiny" in seed or "destined" in seed
        is_relic = "relic" in seed
        is_oath = "oath" in seed
        is_dystopian = "dystopian" in genre_tags or "surveillance" in seed
        is_civilization = "civilization" in seed or "simulation" in seed

        public_authority = (
            "The Crown, the High Courts, the Academy Councils, and recognized noble houses publicly rule through law, rank, and ceremony."
        )

        if not is_empire:
            public_authority = (
                "A formal council of institutions, military offices, courts, and elite families publicly governs the world."
            )

        real_authority = (
            "Real power is shared between founder bloodlines, academy gatekeepers, relic financiers, archivists, military commanders, and hidden oath interpreters."
        )

        if is_dystopian:
            real_authority += (
                " Surveillance administrators and data-keepers hold informal veto power over public decisions."
            )

        ruling_groups = [
            "S-Class Founder Bloodlines",
            "High Court Families",
            "Academy Council of Authorized Knowledge",
            "Imperial Tax and Succession Office",
            "Temple-Oath Certification Orders",
        ]

        if is_relic:
            ruling_groups.append("Relic Investment Consortium")

        hidden_rulers = [
            "The Silent Register: archivists who decide which records are legally remembered",
            "The Oath Interpreters: religious-legal figures who translate sacred legitimacy into court power",
            "The Debt Houses: financiers who own noble obligations without appearing in public ceremonies",
        ]

        if is_destiny:
            hidden_rulers.append(
                "The Destiny Classification Board: officials who decide whether gifted people become assets, threats, or erased names"
            )

        kingmakers = [
            "headmasters who control future officials",
            "marriage brokers between noble houses",
            "relic financiers who decide which institutions survive",
            "border commanders who can delay or accelerate civil conflict",
            "archivists who can validate or destroy bloodline claims",
        ]

        factions = [
            FactionSeed(
                name="The Founding Houses Bloc",
                faction_type="ruling_noble_bloc",
                public_goal="Preserve legal continuity, ceremonial dignity, and imperial order.",
                hidden_goal="Keep founder bloodlines above both talent and truth.",
                resources=[
                    "inheritance law",
                    "court access",
                    "private tutors",
                    "marriage alliances",
                    "legal credibility",
                ],
                allies=[
                    "High Courts",
                    "Academy traditionalists",
                    "Oath certification priests",
                ],
                enemies=[
                    "erased families",
                    "radical students",
                    "destiny-bearing commoners",
                    "border truth-keepers",
                ],
                recruitment_method="birth, marriage, patronage, and reputation debt",
                betrayal_probability=0.42,
                story_uses=[
                    "succession conflict",
                    "elite romance obstacle",
                    "political antagonist",
                    "family duty pressure",
                ],
            ),
            FactionSeed(
                name="The Academy Orthodoxy",
                faction_type="institutional_power",
                public_goal="Protect education quality, intellectual order, and responsible power use.",
                hidden_goal="Prevent knowledge from reaching people who could overturn rank-based authority.",
                resources=[
                    "sealed libraries",
                    "exams",
                    "faculty appointments",
                    "student records",
                    "disciplinary courts",
                ],
                allies=[
                    "Founding Houses Bloc",
                    "official historians",
                    "licensed healer guilds",
                ],
                enemies=[
                    "underground tutors",
                    "commoner prodigies",
                    "forbidden archive smugglers",
                ],
                recruitment_method="scholarship dependency, faculty sponsorship, elite student grooming",
                betrayal_probability=0.35,
                story_uses=[
                    "forbidden classroom",
                    "teacher betrayal",
                    "student faction war",
                    "merit hypocrisy",
                ],
            ),
            FactionSeed(
                name="The Low Lantern Network",
                faction_type="black_market_information_network",
                public_goal="None; officially criminals, smugglers, and rumor merchants.",
                hidden_goal="Move knowledge, medicine, identities, and forbidden messages outside institutional control.",
                resources=[
                    "forged permits",
                    "servant tunnels",
                    "illegal textbooks",
                    "black-market healers",
                    "whisper chains",
                ],
                allies=[
                    "erased families",
                    "border guides",
                    "some corrupt academy officials",
                ],
                enemies=[
                    "security inspectors",
                    "official couriers",
                    "reputation courts",
                ],
                recruitment_method="debt rescue, shared secrets, family survival, and protection from legal erasure",
                betrayal_probability=0.58,
                story_uses=[
                    "secret meeting",
                    "spy route",
                    "forged identity",
                    "morally gray ally",
                    "romantic escape",
                ],
            ),
            FactionSeed(
                name="The Border Oath-Keepers",
                faction_type="frontier_memory_faction",
                public_goal="Defend border settlements and preserve local autonomy.",
                hidden_goal="Protect oral histories and treaties the capital erased.",
                resources=[
                    "border militias",
                    "old maps",
                    "oral memory",
                    "smuggling routes",
                    "local loyalty",
                ],
                allies=[
                    "mine families",
                    "hidden archivists",
                    "some rebel students",
                ],
                enemies=[
                    "capital tax offices",
                    "military centralizers",
                    "official historians",
                ],
                recruitment_method="family obligation, border survival, and distrust of the capital",
                betrayal_probability=0.29,
                story_uses=[
                    "exile refuge",
                    "outside-world reveal",
                    "war ignition",
                    "ancestral truth",
                ],
            ),
            FactionSeed(
                name="The Silent Register",
                faction_type="hidden_archive_power",
                public_goal="Maintain accurate records and protect legal continuity.",
                hidden_goal="Control which truths can become legally real.",
                resources=[
                    "inheritance records",
                    "erased names",
                    "sealed testimony",
                    "oath transcripts",
                    "classification files",
                ],
                allies=[
                    "courts",
                    "academy historians",
                    "some temple judges",
                ],
                enemies=[
                    "archive thieves",
                    "truth cults",
                    "families seeking restoration",
                ],
                recruitment_method="apprenticeship, blackmail, rare memory skill, and institutional capture",
                betrayal_probability=0.67,
                story_uses=[
                    "lineage reveal",
                    "legal reversal",
                    "mystery engine",
                    "villain evidence",
                ],
            ),
        ]

        if is_relic:
            factions.append(
                FactionSeed(
                    name="The Relic Investment Consortium",
                    faction_type="economic_power",
                    public_goal="Fund infrastructure, academy research, and national prosperity.",
                    hidden_goal="Monopolize relic extraction before relic debt becomes public knowledge.",
                    resources=[
                        "mine contracts",
                        "private guards",
                        "academy donations",
                        "temple bribes",
                        "artifact appraisers",
                    ],
                    allies=[
                        "academy research boards",
                        "mine governors",
                        "healer guild investors",
                    ],
                    enemies=[
                        "mine-worker clans",
                        "relic smugglers",
                        "religious purists",
                    ],
                    recruitment_method="money, debt, investment promises, and quiet coercion",
                    betrayal_probability=0.74,
                    story_uses=[
                        "resource war",
                        "artifact corruption",
                        "worker uprising",
                        "economic villain",
                    ],
                )
            )

        if is_destiny:
            factions.append(
                FactionSeed(
                    name="The Destiny Classification Board",
                    faction_type="state_control_body",
                    public_goal="Protect unusually gifted citizens and assign them safe institutional paths.",
                    hidden_goal="Prevent destiny-bearing people from forming alliances outside official control.",
                    resources=[
                        "testing halls",
                        "classification files",
                        "prophecy interpreters",
                        "student assignments",
                        "secret containment orders",
                    ],
                    allies=[
                        "academy councils",
                        "oath courts",
                        "elite sponsors",
                    ],
                    enemies=[
                        "unregistered destined people",
                        "families hiding children",
                        "prophecy dissenters",
                    ],
                    recruitment_method="legal compulsion, elite sponsorship, fear, and promises of protection",
                    betrayal_probability=0.63,
                    story_uses=[
                        "false ranking",
                        "chosen-one containment",
                        "rival classification",
                        "destiny kidnapping",
                    ],
                )
            )

        if is_dystopian:
            factions.append(
                FactionSeed(
                    name="The Civic Observation Bureau",
                    faction_type="surveillance_security_state",
                    public_goal="Prevent crime, rebellion, illegal magic, and social destabilization.",
                    hidden_goal="Turn citizen behavior into leverage for political control.",
                    resources=[
                        "movement logs",
                        "message interception",
                        "informants",
                        "public shame records",
                        "permit systems",
                    ],
                    allies=[
                        "law courts",
                        "security forces",
                        "academy discipline offices",
                    ],
                    enemies=[
                        "low-market couriers",
                        "student rebels",
                        "border smugglers",
                    ],
                    recruitment_method="blackmail, career benefits, fear, and ideological training",
                    betrayal_probability=0.51,
                    story_uses=[
                        "surveillance escape",
                        "informant reveal",
                        "dystopian pressure",
                        "privacy conflict",
                    ],
                )
            )

        alliance_map = {
            "The Founding Houses Bloc": [
                "The Academy Orthodoxy",
                "The Silent Register",
                "Temple-Oath Certification Orders",
            ],
            "The Academy Orthodoxy": [
                "The Founding Houses Bloc",
                "The Destiny Classification Board" if is_destiny else "High Courts",
            ],
            "The Low Lantern Network": [
                "The Border Oath-Keepers",
                "erased families",
                "some desperate students",
            ],
            "The Silent Register": [
                "High Courts",
                "Academy historians",
                "hidden oath interpreters",
            ],
        }

        if is_relic:
            alliance_map["The Relic Investment Consortium"] = [
                "academy research boards",
                "mine governors",
                "private security firms",
            ]

        if is_destiny:
            alliance_map["The Destiny Classification Board"] = [
                "The Academy Orthodoxy",
                "Oath courts",
                "elite sponsors",
            ]

        power_instability_notes = [
            "Public authority depends on the appearance that law, education, and bloodline legitimacy agree.",
            "Real authority fractures when archives, academies, courts, and financiers disagree over a person or event.",
            "Low-status groups gain leverage when they control movement, hidden records, or unofficial knowledge.",
            "Faction betrayal risk rises whenever destiny, relic debt, inheritance, or erased history becomes public.",
        ]

        if desired_complexity in {"extreme", "god_level"}:
            power_instability_notes.extend(
                [
                    "Every major faction should later recruit characters differently based on class, skill, trauma, and usefulness.",
                    "Faction similarity and alliance overlap should later feed the world-diff and originality systems.",
                    "Power structures must be checked against economy, law, belief, and demographics before training eligibility.",
                ]
            )

        return PowerStructureProfile(
            public_authority=public_authority,
            real_authority=real_authority,
            ruling_groups=ruling_groups,
            hidden_rulers=hidden_rulers,
            kingmakers=kingmakers,
            factions=factions,
            alliance_map=alliance_map,
            power_instability_notes=power_instability_notes,
        )

    def _build_military_security(
        self,
        *,
        seed_premise: str,
        genre_tags: List[str],
        tone_tags: List[str],
        desired_complexity: str,
    ) -> MilitarySecurityProfile:
        seed = seed_premise.lower()

        is_academy = "academy" in seed or "dark_academy" in genre_tags
        is_empire = "empire" in seed or "political_fantasy" in genre_tags
        is_relic = "relic" in seed
        is_destiny = "destiny" in seed or "destined" in seed
        is_dystopian = "dystopian" in genre_tags or "surveillance" in seed
        is_border = "border" in seed or is_empire

        armies = [
            "Crown Regulars: the formal army used for capital defense, ceremonial order, and imperial response",
            "Provincial Levy Forces: regional troops loyal first to local commanders, second to the capital",
            "Border March Battalions: hardened frontier soldiers who know the outside world better than court officials",
        ]

        if is_relic:
            armies.append(
                "Relic Convoy Guards: militarized private-security forces protecting mine roads and artifact shipments"
            )

        elite_units = [
            "Oathguard: elite protectors assigned to ceremonies, succession trials, and legally sensitive persons",
            "Archive Wardens: armed custodians of forbidden records and sealed testimony",
            "Academy Duel Marshals: combat-trained officials who police student conflict and formal challenges",
        ]

        if is_destiny:
            elite_units.append(
                "Fate Containment Cadre: specialized units trained to escort, test, or isolate destiny-bearing people"
            )

        police_or_security_forces = [
            "Capital Watch",
            "Academy Discipline Office",
            "Gate Permit Inspectors",
            "Market Suppression Patrols",
        ]

        if is_dystopian:
            police_or_security_forces.append("Civic Observation Bureau field officers")

        spy_networks = [
            "servant-listener networks inside noble houses",
            "academy informants among students and faculty",
            "border rider intelligence chains",
            "low-market whisper brokers",
            "archive cross-reference agents",
        ]

        assassin_or_special_orders = [
            "The Quiet Knives: unofficial political removal specialists officially denied by every house",
            "The Bell-Masked Witnesses: oath-bound observers who can ruin reputations without drawing weapons",
        ]

        if is_relic:
            assassin_or_special_orders.append(
                "Debt Collectors: enforcers who recover relic obligations through legal intimidation or disappearance"
            )

        military_ranks = [
            "Marshal of Crown Roads",
            "Border Captain",
            "Convoy Commander",
            "Oathguard Lieutenant",
            "Academy Duel Marshal",
            "Archive Warden",
            "Gate Inspector",
            "Field Informant",
        ]

        war_readiness_score = 0.62

        if is_border:
            war_readiness_score += 0.08

        if is_destiny:
            war_readiness_score += 0.07

        if is_relic:
            war_readiness_score += 0.05

        if desired_complexity in {"extreme", "god_level"}:
            war_readiness_score += 0.03

        war_readiness_score = min(war_readiness_score, 0.92)

        current_war_risks = [
            "border commanders may stop obeying capital orders",
            "resource convoys could become military targets",
            "student unrest may become faction conflict",
            "noble succession disputes could trigger private armies",
        ]

        if is_destiny:
            current_war_risks.append(
                "factions may attempt to kidnap or eliminate destiny-bearing people before alliances form"
            )

        if is_relic:
            current_war_risks.append(
                "relic scarcity may turn mining regions into flashpoints for open violence"
            )

        if is_dystopian:
            current_war_risks.append(
                "surveillance overreach may create organized resistance cells"
            )

        military_corruption = (
            "Security forces publicly serve law but privately answer to class pressure, faction money, academy influence, "
            "and archive leverage. Corruption is not only bribery; it is loyalty confusion."
        )

        if desired_complexity in {"extreme", "god_level"}:
            military_corruption += (
                " Later simulation should track which armed group obeys law, money, family, fear, ideology, or hidden truth in each crisis."
            )

        return MilitarySecurityProfile(
            armies=armies,
            elite_units=elite_units,
            police_or_security_forces=police_or_security_forces,
            spy_networks=spy_networks,
            assassin_or_special_orders=assassin_or_special_orders,
            military_ranks=military_ranks,
            war_readiness_score=war_readiness_score,
            current_war_risks=current_war_risks,
            military_corruption=military_corruption,
        )

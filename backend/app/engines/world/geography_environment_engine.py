from typing import Any, Dict, List

from backend.app.engines.base import BaseEngine
from backend.app.schemas.foundation import EngineRunResult
from backend.app.schemas.world import (
    EnvironmentProfile,
    GeographyProfile,
    InfrastructureProfile,
    LocationProfile,
    TravelRoute,
)


class GeographyEnvironmentEngine(BaseEngine):
    """Generates geography, environment, and infrastructure.

    This is the physical/logistical layer of the world.

    It decides:
    - where power sits
    - where danger lives
    - how people move
    - how messages travel
    - where secrets can hide
    - how climate shapes society
    - how terrain creates story constraints

    This matters later for character movement, war feasibility, trade routes,
    romance separation, mystery timing, faction control, and civilization logic.
    """

    engine_name = "world.geography_environment_engine"

    def run(self, payload: Dict[str, Any]) -> EngineRunResult:
        world_name = payload.get("world_name") or payload.get("name") or "Mythraen"
        seed_premise = payload.get("seed_premise", "")
        genre_tags = payload.get("genre_tags", [])
        tone_tags = payload.get("tone_tags", [])
        desired_complexity = payload.get("desired_complexity", "high")
        target_format = payload.get("target_format", "novel_series")

        warnings: List[str] = []

        if not seed_premise:
            warnings.append(
                "No seed_premise provided; geography will use broad default world structure."
            )

        geography = self._build_geography(
            world_name=world_name,
            seed_premise=seed_premise,
            genre_tags=genre_tags,
            desired_complexity=desired_complexity,
            target_format=target_format,
        )

        environment = self._build_environment(
            seed_premise=seed_premise,
            genre_tags=genre_tags,
            tone_tags=tone_tags,
            desired_complexity=desired_complexity,
        )

        infrastructure = self._build_infrastructure(
            seed_premise=seed_premise,
            genre_tags=genre_tags,
            desired_complexity=desired_complexity,
        )

        return self.build_result(
            success=True,
            data={
                "geography": geography.model_dump(mode="json"),
                "environment": environment.model_dump(mode="json"),
                "infrastructure": infrastructure.model_dump(mode="json"),
                "training_notes": [
                    "Locations include symbolic, political, economic, religious, and story-use fields.",
                    "Routes and communication delays are structured for future plot feasibility checks.",
                    "Environment pressure can feed economy, disease, famine, war, and migration systems.",
                ],
            },
            warnings=warnings,
            errors=[],
            generated_object_ids=[],
        )

    def _build_geography(
        self,
        *,
        world_name: str,
        seed_premise: str,
        genre_tags: List[str],
        desired_complexity: str,
        target_format: str,
    ) -> GeographyProfile:
        seed = seed_premise.lower()

        is_academy = "academy" in seed or "dark_academy" in genre_tags
        is_empire = "empire" in seed or "political_fantasy" in genre_tags
        is_relic = "relic" in seed
        is_oath = "oath" in seed
        is_destiny = "destiny" in seed or "destined" in seed
        is_civilization = "civilization" in seed or "simulation" in target_format.lower()

        regions = [
            "The Crownheart Capital Region",
            "The Old Academy Quarter",
            "The Border Marches",
            "The Relic Ridge Provinces",
            "The Low Market Districts",
            "The Sealed Archive Belt",
        ]

        if is_civilization:
            regions.extend(
                [
                    "The First Settlement Ring",
                    "The Outer Resource Frontiers",
                    "The Rival Colony Basin",
                    "The Unclaimed Wild Zones",
                ]
            )

        if desired_complexity in {"extreme", "god_level"}:
            regions.extend(
                [
                    "The Forgotten Treaty Lands",
                    "The Pilgrim Roads of Broken Oaths",
                    "The Dead Province Removed from Maps",
                ]
            )

        locations = [
            LocationProfile(
                name=f"{world_name} Crown Capital",
                location_type="capital",
                description=(
                    "The administrative and symbolic center of the world, where courts, academies, "
                    "temples, and old families compete behind ritual politeness."
                ),
                owner_or_controller="royal court and founding houses",
                danger_level=0.55,
                symbolic_meaning="Power disguised as order.",
                economic_role="tax coordination, elite trade, legal finance",
                political_role="center of legitimacy and succession politics",
                religious_role="site of public oath ceremonies",
                secrets=[
                    "The capital's oldest district was built over erased trial records.",
                    "Some founding statues are newer than the lies they represent.",
                ],
                story_potential=[
                    "succession crisis",
                    "court betrayal",
                    "public ceremony interruption",
                    "forbidden evidence reveal",
                ],
            ),
            LocationProfile(
                name="The Ashen Crown Academy",
                location_type="academy",
                description=(
                    "An elite institution where knowledge, status, bloodline, and ambition are refined "
                    "into legal power."
                ),
                owner_or_controller="academy council and noble sponsors",
                danger_level=0.72,
                symbolic_meaning="A beautiful gate that decides who is allowed to become exceptional.",
                economic_role="converts elite funding into future rulers, judges, mages, and strategists",
                political_role="training ground for loyal power",
                religious_role="houses oath rituals before examinations",
                secrets=[
                    "The first commoner scholars are missing from its official founder wall.",
                    "A sealed classroom reacts to names erased from history.",
                ],
                story_potential=[
                    "rivalry arc",
                    "forbidden study",
                    "student faction war",
                    "teacher betrayal",
                    "elite romance conflict",
                ],
            ),
            LocationProfile(
                name="The Relic Ridge Mines",
                location_type="resource_zone",
                description=(
                    "A chain of dangerous mines where ancient objects are extracted under military, "
                    "religious, and corporate supervision."
                ),
                owner_or_controller="noble investors, mining guilds, and temple inspectors",
                danger_level=0.86,
                symbolic_meaning="The world feeds on buried memory.",
                economic_role="primary source of relic wealth and academy funding",
                political_role="controlled by whoever can survive its debts",
                religious_role="officially purified, unofficially feared",
                secrets=[
                    "Relics from deeper layers remember events before official history.",
                    "Mine collapses are sometimes intentional erasures.",
                ],
                story_potential=[
                    "resource revolt",
                    "artifact discovery",
                    "worker uprising",
                    "curse outbreak",
                    "lost heir clue",
                ],
            ),
            LocationProfile(
                name="The Low Lantern Market",
                location_type="underground_market",
                description=(
                    "A layered black-market district beneath respectable trade streets, where banned books, "
                    "relic fragments, forged permits, and private messages circulate."
                ),
                owner_or_controller="merchant syndicates, smugglers, and informant families",
                danger_level=0.68,
                symbolic_meaning="The truth people buy when law refuses to sell it.",
                economic_role="black-market knowledge, relic fragments, healing, forged identity papers",
                political_role="meeting ground for rebels, spies, and desperate nobles",
                religious_role="home to unlicensed shrines and oath-breaker confessions",
                secrets=[
                    "Several academy officials secretly fund the market they condemn.",
                    "Some forbidden books are planted to trace readers.",
                ],
                story_potential=[
                    "secret meeting",
                    "black-market healing",
                    "forged identity",
                    "spy chase",
                    "romantic escape route",
                ],
            ),
            LocationProfile(
                name="The Border Marches",
                location_type="frontier",
                description=(
                    "A militarized frontier where official maps end, older cultures survive, and imperial truth "
                    "weakens with distance."
                ),
                owner_or_controller="border commanders and semi-independent houses",
                danger_level=0.79,
                symbolic_meaning="The edge of what the center can control.",
                economic_role="resource transit, smuggling, refugee movement",
                political_role="buffer between official empire and external unknowns",
                religious_role="old roadside shrines preserve pre-imperial prayers",
                secrets=[
                    "Border families remember treaties the capital erased.",
                    "Some destined people are hidden here before classification.",
                ],
                story_potential=[
                    "exile arc",
                    "military betrayal",
                    "outside-world reveal",
                    "hidden village",
                    "war ignition",
                ],
            ),
            LocationProfile(
                name="The Sealed Archive Vaults",
                location_type="forbidden_archive",
                description=(
                    "A restricted archive complex where official memory, censored history, and living legal records "
                    "are stored under layered authority."
                ),
                owner_or_controller="academy historians, oath courts, and crown archivists",
                danger_level=0.81,
                symbolic_meaning="A place where truth is preserved by the people who fear it.",
                economic_role="controls legal inheritance evidence and knowledge permissions",
                political_role="can legitimize or destroy families",
                religious_role="contains disputed oath transcripts",
                secrets=[
                    "Some shelves rearrange when false names are spoken.",
                    "The archive contains more deleted citizens than living nobles.",
                ],
                story_potential=[
                    "archive heist",
                    "lineage reveal",
                    "legal reversal",
                    "historical horror",
                    "mystery climax",
                ],
            ),
        ]

        if is_destiny:
            locations.append(
                LocationProfile(
                    name="The Hall of Unclaimed Fates",
                    location_type="classification_hall",
                    description=(
                        "A cold ceremonial hall where unusually gifted people are tested, ranked, contained, "
                        "or quietly redirected into institutional service."
                    ),
                    owner_or_controller="destiny classification board",
                    danger_level=0.77,
                    symbolic_meaning="The place where the world tries to measure what it cannot control.",
                    economic_role="assigns value to exceptional people",
                    political_role="decides which factions may sponsor awakened talent",
                    religious_role="interprets destiny through approved doctrine",
                    secrets=[
                        "Some names are rejected because their destinies threaten the institution itself.",
                        "A hidden list tracks people who must never meet.",
                    ],
                    story_potential=[
                        "testing scene",
                        "false ranking",
                        "destiny fraud",
                        "rival meeting",
                        "escape from classification",
                    ],
                )
            )

        if is_oath:
            locations.append(
                LocationProfile(
                    name="The First Oath Plaza",
                    location_type="sacred_civic_site",
                    description=(
                        "The public square where citizens are told the first promise was made, although the true "
                        "site may have been elsewhere."
                    ),
                    owner_or_controller="temple courts and crown ceremony officers",
                    danger_level=0.48,
                    symbolic_meaning="Public unity built over private betrayal.",
                    economic_role="festival commerce and oath certification",
                    political_role="used for legitimacy ceremonies",
                    religious_role="site of oath renewals, public vows, and state prayers",
                    secrets=[
                        "The stones are replacements; the originals were removed after a forbidden testimony.",
                    ],
                    story_potential=[
                        "public vow",
                        "ceremony sabotage",
                        "betrayal confession",
                        "romantic oath scene",
                    ],
                )
            )

        routes = [
            TravelRoute(
                from_location=f"{world_name} Crown Capital",
                to_location="The Ashen Crown Academy",
                travel_time="half a day by official carriage; two hours by elite private route",
                cost="moderate for nobles, high for commoners",
                danger_level=0.25,
                controlled_by="capital guards and academy gate officials",
                route_notes="Status determines speed; lower classes wait at inspection gates.",
            ),
            TravelRoute(
                from_location="The Ashen Crown Academy",
                to_location="The Low Lantern Market",
                travel_time="one hour through legal streets; twenty minutes through servant tunnels",
                cost="low money cost, high reputation risk",
                danger_level=0.58,
                controlled_by="market brokers and academy informants",
                route_notes="Many elite scandals begin on this route.",
            ),
            TravelRoute(
                from_location=f"{world_name} Crown Capital",
                to_location="The Border Marches",
                travel_time="six days by guarded road; three days by illegal courier route",
                cost="expensive permits or dangerous favors",
                danger_level=0.74,
                controlled_by="military checkpoints and border houses",
                route_notes="Messages can be delayed or rewritten at checkpoints.",
            ),
            TravelRoute(
                from_location="The Relic Ridge Mines",
                to_location="The Ashen Crown Academy",
                travel_time="four days by guarded convoy",
                cost="officially funded by academy contracts",
                danger_level=0.82,
                controlled_by="mining guilds, academy buyers, and armed escorts",
                route_notes="Relic shipments attract smugglers, rebels, and religious auditors.",
            ),
        ]

        if desired_complexity in {"extreme", "god_level"}:
            routes.extend(
                [
                    TravelRoute(
                        from_location="The Sealed Archive Vaults",
                        to_location="The Low Lantern Market",
                        travel_time="unknown; exists through copied records and informant chains",
                        cost="truth, favors, or blackmail",
                        danger_level=0.88,
                        controlled_by="hidden archivists and market memory brokers",
                        route_notes="This is not a physical route as much as a hidden information pipeline.",
                    ),
                    TravelRoute(
                        from_location="The Border Marches",
                        to_location="The Dead Province Removed from Maps",
                        travel_time="variable; maps lie after the third ruined bridge",
                        cost="military desertion, exile, or forbidden guide payment",
                        danger_level=0.93,
                        controlled_by="no official controller; watched by old powers",
                        route_notes="Useful for sequels, exile arcs, and outside-world mythology.",
                    ),
                ]
            )

        world_map_summary = (
            f"{world_name} is organized around a prestige-heavy capital, elite knowledge centers, "
            "resource extraction zones, controlled borders, forbidden archives, and underground routes "
            "where the official world leaks into the hidden one."
        )

        if is_empire:
            world_map_summary += (
                " The empire's map is political before it is geographic: what is drawn, named, or omitted "
                "reveals who controls truth."
            )

        if is_relic:
            world_map_summary += (
                " Relic geography shapes economics, religion, and faction power because the most valuable places "
                "are also the most dangerous."
            )

        unknown_regions = [
            "The Dead Province Removed from Maps",
            "The ruins beyond the old tax road",
            "The mountain pass where the first witnesses disappeared",
        ]

        return GeographyProfile(
            world_map_summary=world_map_summary,
            regions=regions,
            locations=locations,
            travel_routes=routes,
            unknown_regions=unknown_regions,
        )

    def _build_environment(
        self,
        *,
        seed_premise: str,
        genre_tags: List[str],
        tone_tags: List[str],
        desired_complexity: str,
    ) -> EnvironmentProfile:
        seed = seed_premise.lower()

        climate_zones = [
            "temperate capital basin with controlled gardens and ritual avenues",
            "cold highland academy zone where winter exams are treated as moral tests",
            "wet low-market canals prone to fog, rot, and hidden movement",
            "dry relic ridge terrain marked by dust storms and unstable mines",
            "borderland mixed climate with harsh roads and unpredictable seasons",
        ]

        season_patterns = [
            "Oathwinter: a formal cold season associated with exams, legal vows, and old grief.",
            "Ashspring: a season of public renewal festivals that hides tax pressure and debt collection.",
            "Relicdry: a dangerous extraction season when mines are most productive and most unstable.",
            "Lanternfall: fog-heavy months when markets, secrets, and disappearances increase.",
        ]

        natural_disasters = [
            "mine collapses in relic-rich regions",
            "capital floods in older districts built over sealed canals",
            "borderland avalanches that isolate military posts",
        ]

        anomalies = [
            "archive rooms that become colder near false records",
            "relic storms that interfere with memory and navigation",
            "oath echoes heard in places where major promises were broken",
        ]

        famine_risks = [
            "border harvest disruption during military lockdowns",
            "food price spikes when relic convoys receive road priority",
            "poor-district shortages during academy festival seasons",
        ]

        disease_risks = [
            "mine-lung sickness in relic workers",
            "canal fever in the low markets",
            "winter dormitory illness during academy exam confinement",
        ]

        dangerous_terrain = [
            "collapsed relic tunnels",
            "unmapped servant passages below academies",
            "fog canals used by smugglers",
            "border roads with abandoned checkpoints",
        ]

        environmental_pressures = [
            "Resource geography gives mining regions wealth but also exploitation.",
            "Weather delays messages, creating mystery windows and political manipulation.",
            "The capital appears orderly because environmental risk is pushed outward.",
        ]

        weather_symbolism = [
            "Fog means hidden truth is moving.",
            "Ash-gray snow signals social pressure and memory corruption.",
            "Dry red wind near relic mines suggests old debts waking.",
        ]

        if "tragic" in tone_tags:
            weather_symbolism.append("Beautiful weather often appears before betrayal, making grief feel ceremonial.")

        if desired_complexity in {"extreme", "god_level"}:
            environmental_pressures.extend(
                [
                    "Climate and infrastructure should affect migration, prices, law enforcement, class exposure, and faction timing.",
                    "Environmental anomalies must connect to history, relics, oaths, or suppressed truth instead of feeling random.",
                ]
            )

        return EnvironmentProfile(
            climate_zones=climate_zones,
            season_patterns=season_patterns,
            natural_disasters=natural_disasters,
            magical_or_environmental_anomalies=anomalies,
            famine_risks=famine_risks,
            disease_risks=disease_risks,
            dangerous_terrain=dangerous_terrain,
            environmental_pressures=environmental_pressures,
            weather_symbolism=weather_symbolism,
        )

    def _build_infrastructure(
        self,
        *,
        seed_premise: str,
        genre_tags: List[str],
        desired_complexity: str,
    ) -> InfrastructureProfile:
        roads = [
            "Crown Roads: polished, taxed, patrolled, and faster for people with rank.",
            "Old Witness Roads: broken pre-imperial routes that avoid official checkpoints.",
            "Academy Carriage Lanes: prestige routes connecting elite institutions.",
            "Mine Convoy Roads: guarded routes designed for relic transport, not public safety.",
        ]

        ports = [
            "Low Lantern Canal Docks used for legal grain by day and forbidden books by night.",
            "Crown Customs Port where trade documents are inspected for political loyalty.",
        ]

        bridges = [
            "The Seven-Tax Bridge between capital districts.",
            "The Half-Fallen Border Bridge used by smugglers and deserters.",
            "The Academy East Bridge where students are publicly ranked during entrance season.",
        ]

        transit_systems = [
            "official carriages ranked by class permit",
            "military convoy wagons",
            "student transport under academy supervision",
            "illegal tunnel guides beneath the low markets",
        ]

        postal_systems = [
            "Crown Courier Office for official letters",
            "Academy Seal Messengers for student, faculty, and sponsor communications",
            "Low Lantern whisper-chain for illegal information",
            "border rider network that often knows news before the capital admits it",
        ]

        communication_delays = [
            "Capital to academy: same day if permitted, delayed if socially inconvenient.",
            "Capital to border: three to six days depending on checkpoint politics.",
            "Academy to low market: fast physically, slow socially because discovery is dangerous.",
            "Relic mine reports are often delayed, edited, or reclassified.",
        ]

        trade_chokepoints = [
            "relic convoy gates",
            "academy supply contracts",
            "border military checkpoints",
            "canal tariff locks",
            "sealed archive copy permissions",
        ]

        border_controls = [
            "travel permits by class",
            "student movement logs",
            "border checkpoint inspection oaths",
            "resource convoy checkpoint priority law",
            "restricted map access",
        ]

        infrastructure_decay = [
            "poor districts flood because capital repairs prioritize ceremony routes",
            "old roads vanish from official maps when history becomes inconvenient",
            "mine roads are repaired faster than village bridges",
            "archive maintenance is perfect while public schools decay",
        ]

        if desired_complexity in {"extreme", "god_level"}:
            communication_delays.append(
                "Communication timing must be tracked later by plot engines so secrets, rescues, wars, and romance separations remain believable."
            )
            infrastructure_decay.append(
                "Infrastructure inequality should feed economy, law, class resentment, faction recruitment, and story pressure."
            )

        return InfrastructureProfile(
            roads=roads,
            ports=ports,
            bridges=bridges,
            transit_systems=transit_systems,
            postal_or_messenger_systems=postal_systems,
            communication_delays=communication_delays,
            trade_chokepoints=trade_chokepoints,
            border_controls=border_controls,
            infrastructure_decay=infrastructure_decay,
        )

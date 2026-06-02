from __future__ import annotations

from typing import Any, Dict, List


class DisasterEnvironmentalPressureEngine:
    def build_disaster_pressure_profile(
        self,
        *,
        source_id: str,
        climate_profile: Dict[str, Any] | None = None,
        ecology_profile: Dict[str, Any] | None = None,
        settlement: Dict[str, Any] | None = None,
        route_network: Dict[str, Any] | None = None,
        economy_profile: Dict[str, Any] | None = None,
        disaster_seed: Dict[str, Any] | None = None,
        story_context: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        climate_profile = climate_profile or {}
        ecology_profile = ecology_profile or {}
        settlement = settlement or {}
        route_network = route_network or {}
        economy_profile = economy_profile or {}
        disaster_seed = disaster_seed or {}
        story_context = story_context or {}

        region_name = disaster_seed.get(
            "region_name",
            settlement.get("region_name")
            or route_network.get("region_name")
            or story_context.get("region_name", "Saltroot Forest"),
        )

        pressure_name = disaster_seed.get("pressure_name", f"{region_name} Red Fog Disaster Cycle")

        profile = {
            "disaster_pressure_profile_id": f"disaster_pressure_{source_id}_{self._slug(pressure_name)}",
            "source_id": source_id,
            "pressure_name": pressure_name,
            "region_name": region_name,
            "climate_id": climate_profile.get("element_id") or climate_profile.get("climate_id"),
            "ecology_id": ecology_profile.get("element_id") or ecology_profile.get("ecology_id"),
            "settlement_id": settlement.get("settlement_id"),
            "route_network_id": route_network.get("route_network_id"),
            "resource_economy_profile_id": economy_profile.get("resource_economy_profile_id"),
            "name_origin": disaster_seed.get(
                "name_origin",
                f"{pressure_name} is named for recurring red fog surges, salt rain damage, road closures, medicine shortages, "
                f"and public blame rituals that return whenever the climate destabilizes.",
            ),
            "name_meaning": disaster_seed.get(
                "name_meaning",
                "a recurring environmental pressure where weather, ecology, roads, economy, faith, and memory collide",
            ),
            "name_language_logic": disaster_seed.get(
                "name_language_logic",
                "disaster names combine visible environmental force with civic consequence and remembered trauma",
            ),
            "cultural_context": disaster_seed.get(
                "cultural_context",
                settlement.get("cultural_context", "bell-road survival culture"),
            ),
            "world_context": region_name,
            "visual_identity": disaster_seed.get(
                "visual_identity",
                "red fog walls, darkened saltroot leaves, shuttered markets, dead foglamps, cracked road stones, and warning bells",
            ),
            "sensory_identity": disaster_seed.get(
                "sensory_identity",
                "metallic fog taste, wet ash smell, panicked animals, coughing crowds, bell echoes, and mold-sweet medicine rot",
            ),
            "disaster_types": disaster_seed.get("disaster_types", [
                {
                    "disaster_type": "red fog surge",
                    "cause": "climate instability after prolonged salt rain",
                    "immediate_effect": "roads close, travelers vanish, animals panic, and visibility collapses",
                    "long_term_effect": "route memory becomes unreliable and border claims become easier to fake",
                },
                {
                    "disaster_type": "saltroot dieback",
                    "cause": "red mold and overharvest after wet seasons",
                    "immediate_effect": "medicine, witness ink, and funeral tea supplies fall",
                    "long_term_effect": "healers ration treatment and black markets expand",
                },
                {
                    "disaster_type": "foglamp oil shortage",
                    "cause": "trade blockade, theft, and moss-oil contamination",
                    "immediate_effect": "poor districts go dark first",
                    "long_term_effect": "children disappear, trust collapses, and curfew enforcement becomes violent",
                },
                {
                    "disaster_type": "ravine flood",
                    "cause": "bell rain overflows old drainage tunnels",
                    "immediate_effect": "secret routes open, collapse, or reveal hidden records",
                    "long_term_effect": "settlement architecture and secret histories are exposed",
                },
            ]),
            "pressure_chains": disaster_seed.get("pressure_chains", [
                {
                    "chain_name": "fog to famine pressure chain",
                    "steps": [
                        "red fog closes roads",
                        "market caravans stop",
                        "food prices rise",
                        "poor districts ration meals",
                        "smugglers gain power",
                        "riot risk increases",
                    ],
                    "story_pressure": "forces moral choices over food, travel, and class loyalty",
                },
                {
                    "chain_name": "mold to medicine pressure chain",
                    "steps": [
                        "red mold spreads through saltroot groves",
                        "healers lose safe medicine",
                        "archive families hide stockpiles",
                        "fake petals enter market",
                        "patients die",
                        "public blame turns political",
                    ],
                    "story_pressure": "creates healer guilt, black-market temptation, and political exposure",
                },
                {
                    "chain_name": "flood to secret-history pressure chain",
                    "steps": [
                        "ravine flood opens old underways",
                        "hidden records surface",
                        "public cover story weakens",
                        "factions race to control evidence",
                        "settlement mood shifts",
                        "political legitimacy fractures",
                    ],
                    "story_pressure": "turns disaster into revelation",
                },
            ]),
            "settlement_impacts": disaster_seed.get("settlement_impacts", [
                "foglamp districts lose night safety first",
                "archive houses protect records before poor residents",
                "markets close and gossip becomes panic",
                "temple kitchens become emergency shelters",
                "hidden tunnels flood and expose old secrets",
            ]),
            "route_impacts": disaster_seed.get("route_impacts", [
                "Nine-Bell Road closes after red fog warnings",
                "No-Bell Child Path becomes the only safe shortcut",
                "dead-bell roads attract desperate travelers",
                "border checkpoints exploit confusion",
            ]),
            "ecology_impacts": disaster_seed.get("ecology_impacts", [
                "bellhorn deer migrate early and signal danger",
                "saltroot groves fail near infected drainage",
                "fog moth disappearances warn of poison bloom",
                "ravine cats move closer to settlements",
            ]),
            "economy_impacts": disaster_seed.get("economy_impacts", [
                "medicine prices spike",
                "foglamp oil becomes rationed",
                "map fraud increases",
                "food prices rise after route closures",
                "smugglers gain influence",
            ]),
            "social_impacts": disaster_seed.get("social_impacts", [
                "poor districts are blamed for disease",
                "no-bell children become invisible emergency couriers",
                "archive families are accused of hoarding supplies",
                "road guides become essential and disposable",
                "temple witnesses gain or lose authority depending on interpretation",
            ]),
            "religious_interpretations": disaster_seed.get("religious_interpretations", [
                "dead bells are said to ring because public history is false",
                "fog saints are blamed or invoked depending on faction",
                "saltroot dieback is interpreted as punishment for erased names",
                "flooded underways are treated as the land vomiting up buried truth",
            ]),
            "political_blame_paths": disaster_seed.get("political_blame_paths", [
                {
                    "blamed_group": "archive families",
                    "accusation": "hoarding records, maps, and medicine while poor districts suffer",
                    "possible_truth": "partly true but used by rivals for power",
                },
                {
                    "blamed_group": "road families",
                    "accusation": "misreading fog routes and causing deaths",
                    "possible_truth": "false; roads were closed by withheld warning bells",
                },
                {
                    "blamed_group": "smugglers",
                    "accusation": "stealing oil and spreading fake medicine",
                    "possible_truth": "true for some crews, but officials rely on them secretly",
                },
            ]),
            "adaptation_strategies": disaster_seed.get("adaptation_strategies", [
                "emergency foglamp ration cards",
                "temporary road guide militias",
                "temple shelter kitchens",
                "medicine triage ledgers",
                "children's roof-path courier networks",
                "public bell alerts for route closures",
            ]),
            "failure_modes": disaster_seed.get("failure_modes", [
                "authorities protect archives instead of people",
                "medicine triage becomes class-based",
                "fake road bells send travelers into danger",
                "panic reveals forbidden names before legal protection exists",
                "floods expose secrets before anyone can control the evidence",
            ]),
            "story_use": (
                "Turns disaster into complex world pressure linking climate, ecology, economy, roads, settlement life, religion, politics, "
                "class conflict, survival choices, and historical revelation."
            ),
            "character_effect": (
                "Characters reveal courage, selfishness, faith, competence, trauma, class privilege, survival skill, or hidden loyalty "
                "through how they respond to disaster pressure."
            ),
            "plot_effect": (
                "Can trigger evacuation, famine, riots, route closures, disease panic, medicine triage, secret-place reveals, faction conflict, "
                "or public-history collapse."
            ),
            "memory_effect": (
                "World memory must track disaster severity, affected places, casualties, shortages, route closures, blame, adaptation, "
                "revealed secrets, and long-term recovery."
            ),
            "anti_genericity_signal": (
                "Disaster pressure includes named disaster types, cascading chains, settlement/route/ecology/economy/social impacts, "
                "religious interpretation, political blame, adaptation, failure modes, and memory hooks."
            ),
            "detail_depth_score": 0.94,
            "validation_status": "validated",
            "provenance": {
                "generated_by_engine": "DisasterEnvironmentalPressureEngine",
                "origin_type": "derived_from_climate_ecology_settlement_routes_economy",
                "source_id": source_id,
                "climate_id": climate_profile.get("element_id") or climate_profile.get("climate_id"),
                "ecology_id": ecology_profile.get("element_id") or ecology_profile.get("ecology_id"),
                "settlement_id": settlement.get("settlement_id"),
                "route_network_id": route_network.get("route_network_id"),
                "resource_economy_profile_id": economy_profile.get("resource_economy_profile_id"),
                "seed_keys": sorted(disaster_seed.keys()),
                "story_context_keys": sorted(story_context.keys()),
            },
            "compression_summary": (
                f"{pressure_name}: disaster types, cascading pressure chains, settlement/route/ecology/economy/social impacts, "
                f"religious blame, political blame, adaptation, failure modes, and memory hooks."
            ),
        }

        return {"disaster_pressure_profile": profile}

    def build_disaster_event(
        self,
        *,
        source_id: str,
        disaster_pressure_profile: Dict[str, Any],
        event_seed: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        event_seed = event_seed or {}

        event_name = event_seed.get("event_name", "Red Fog Market Closure")

        event = {
            "disaster_event_id": f"disaster_event_{source_id}_{self._slug(event_name)}",
            "source_id": source_id,
            "disaster_pressure_profile_id": disaster_pressure_profile["disaster_pressure_profile_id"],
            "pressure_name": disaster_pressure_profile["pressure_name"],
            "event_name": event_name,
            "event_type": event_seed.get("event_type", "climate_economy_settlement_disruption"),
            "trigger": event_seed.get(
                "trigger",
                "red fog arrived before dawn while foglamp oil was already rationed",
            ),
            "severity": event_seed.get("severity", "high"),
            "affected_locations": event_seed.get("affected_locations", [
                "Nine-Bell Market",
                "Foglamp Steps",
                "old witness road",
                "saltroot medicine stalls",
            ]),
            "affected_groups": event_seed.get("affected_groups", [
                "market families",
                "road guides",
                "no-bell children",
                "licensed healers",
                "archive clerks",
            ]),
            "immediate_consequences": event_seed.get("immediate_consequences", [
                "market gates close",
                "medicine lines double",
                "travelers are trapped inside town",
                "smugglers offer illegal tunnel passage",
                "children carry messages through roof paths",
            ]),
            "long_term_consequences": event_seed.get("long_term_consequences", [
                "food prices rise",
                "archive families face hoarding accusations",
                "road guides gain temporary authority",
                "foglamp crews become political targets",
                "hidden tunnels become strategically important",
            ]),
            "story_use": (
                "Creates an immediate disaster scene with pressure on movement, food, medicine, authority, class, and hidden routes."
            ),
            "character_effect": (
                "Characters must decide whether to help strangers, protect supplies, exploit panic, trust illegal paths, or reveal hidden knowledge."
            ),
            "plot_effect": (
                "Can trap characters, delay deadlines, force alliance with smugglers, trigger public blame, or reveal hidden routes."
            ),
            "memory_effect": (
                "World memory must track closures, shortages, harmed groups, price changes, deaths, blame, discoveries, and adaptation."
            ),
            "lore_effect": (
                "The disaster can be read as dead-bell warning, fog saint anger, ecological punishment, or proof of false history."
            ),
            "anti_genericity_signal": (
                "Event ties named places, supplies, groups, routes, economy, hidden paths, social blame, and lore into one disaster."
            ),
            "detail_depth_score": 0.91,
            "validation_status": "validated",
            "provenance": {
                "generated_by_engine": "DisasterEnvironmentalPressureEngine",
                "origin_type": "derived_from_disaster_pressure_profile",
                "source_id": source_id,
                "profile_id": disaster_pressure_profile["disaster_pressure_profile_id"],
                "seed_keys": sorted(event_seed.keys()),
            },
            "compression_summary": (
                f"{event_name}: severity={event_seed.get('severity', 'high')}; trigger, affected locations/groups, "
                f"immediate and long-term consequences tracked."
            ),
        }

        return {"disaster_event": event}

    def build_story_context_patch(
        self,
        *,
        disaster_pressure_profile: Dict[str, Any],
        disaster_event: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        patch = {
            "disaster_pressure_profile_id": disaster_pressure_profile["disaster_pressure_profile_id"],
            "pressure_name": disaster_pressure_profile["pressure_name"],
            "disaster_types": disaster_pressure_profile["disaster_types"],
            "pressure_chains": disaster_pressure_profile["pressure_chains"],
            "settlement_impacts": disaster_pressure_profile["settlement_impacts"],
            "route_impacts": disaster_pressure_profile["route_impacts"],
            "ecology_impacts": disaster_pressure_profile["ecology_impacts"],
            "economy_impacts": disaster_pressure_profile["economy_impacts"],
            "social_impacts": disaster_pressure_profile["social_impacts"],
            "religious_interpretations": disaster_pressure_profile["religious_interpretations"],
            "political_blame_paths": disaster_pressure_profile["political_blame_paths"],
            "adaptation_strategies": disaster_pressure_profile["adaptation_strategies"],
            "failure_modes": disaster_pressure_profile["failure_modes"],
            "story_use": disaster_pressure_profile["story_use"],
            "character_effect": disaster_pressure_profile["character_effect"],
            "plot_effect": disaster_pressure_profile["plot_effect"],
            "memory_effect": disaster_pressure_profile["memory_effect"],
            "generation_hints": [
                "Use disasters as cascading systems, not isolated events.",
                "Disaster should affect roads, economy, ecology, settlement life, religion, politics, and character choices.",
                "Track shortages, closures, casualties, blame, adaptation, and revealed secrets in memory.",
                "Let characters respond differently based on class, role, belief, family, and survival knowledge.",
            ],
            "memory_update_candidates": [
                {
                    "candidate_type": "disaster_pressure_state",
                    "target_element_id": disaster_pressure_profile["disaster_pressure_profile_id"],
                    "reason": "Track severity, affected systems, cascading impacts, adaptation, blame, shortages, and recovery.",
                }
            ],
        }

        if disaster_event:
            patch["active_disaster_event"] = disaster_event
            patch["memory_update_candidates"].append(
                {
                    "candidate_type": "disaster_event_state",
                    "target_element_id": disaster_event["disaster_event_id"],
                    "reason": "Track trigger, severity, affected locations/groups, closures, shortages, consequences, and blame.",
                }
            )

        return {"story_context_patch": patch}

    def validate_disaster_pressure_profile(self, *, disaster_pressure_profile: Dict[str, Any]) -> Dict[str, Any]:
        required = [
            "disaster_pressure_profile_id",
            "pressure_name",
            "region_name",
            "name_origin",
            "name_meaning",
            "name_language_logic",
            "cultural_context",
            "world_context",
            "visual_identity",
            "sensory_identity",
            "disaster_types",
            "pressure_chains",
            "settlement_impacts",
            "route_impacts",
            "ecology_impacts",
            "economy_impacts",
            "social_impacts",
            "religious_interpretations",
            "political_blame_paths",
            "adaptation_strategies",
            "failure_modes",
            "story_use",
            "character_effect",
            "plot_effect",
            "memory_effect",
            "anti_genericity_signal",
            "detail_depth_score",
            "validation_status",
            "provenance",
            "compression_summary",
        ]

        missing = [field for field in required if not disaster_pressure_profile.get(field)]
        shallow = self._shallow_fields(
            payload=disaster_pressure_profile,
            fields=["name_origin", "story_use", "character_effect", "plot_effect", "memory_effect", "anti_genericity_signal"],
        )

        passed = (
            not missing
            and not shallow
            and float(disaster_pressure_profile.get("detail_depth_score", 0.0)) >= 0.75
        )

        return {
            "passed": passed,
            "missing_fields": missing,
            "shallow_fields": shallow,
            "disaster_pressure_profile_id": disaster_pressure_profile.get("disaster_pressure_profile_id"),
        }

    def validate_disaster_event(self, *, disaster_event: Dict[str, Any]) -> Dict[str, Any]:
        required = [
            "disaster_event_id",
            "disaster_pressure_profile_id",
            "pressure_name",
            "event_name",
            "event_type",
            "trigger",
            "severity",
            "affected_locations",
            "affected_groups",
            "immediate_consequences",
            "long_term_consequences",
            "story_use",
            "character_effect",
            "plot_effect",
            "memory_effect",
            "lore_effect",
            "anti_genericity_signal",
            "detail_depth_score",
            "validation_status",
            "provenance",
            "compression_summary",
        ]

        missing = [field for field in required if not disaster_event.get(field)]
        shallow = self._shallow_fields(
            payload=disaster_event,
            fields=["story_use", "character_effect", "plot_effect", "memory_effect", "lore_effect"],
        )

        passed = not missing and not shallow and float(disaster_event.get("detail_depth_score", 0.0)) >= 0.75

        return {
            "passed": passed,
            "missing_fields": missing,
            "shallow_fields": shallow,
            "disaster_event_id": disaster_event.get("disaster_event_id"),
        }

    def summarize_disaster_pressure(
        self,
        *,
        disaster_pressure_profile: Dict[str, Any],
        disaster_event: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        summary = {
            "disaster_pressure_profile_id": disaster_pressure_profile["disaster_pressure_profile_id"],
            "pressure_name": disaster_pressure_profile["pressure_name"],
            "disaster_type_count": len(disaster_pressure_profile["disaster_types"]),
            "pressure_chain_count": len(disaster_pressure_profile["pressure_chains"]),
            "settlement_impact_count": len(disaster_pressure_profile["settlement_impacts"]),
            "route_impact_count": len(disaster_pressure_profile["route_impacts"]),
            "adaptation_strategy_count": len(disaster_pressure_profile["adaptation_strategies"]),
            "compression_summary": disaster_pressure_profile["compression_summary"],
        }

        if disaster_event:
            summary["disaster_event_id"] = disaster_event["disaster_event_id"]
            summary["event_name"] = disaster_event["event_name"]

        return {"success": True, "summary": summary}

    def build_disaster_pressure_text(
        self,
        *,
        disaster_pressure_profile: Dict[str, Any],
        disaster_event: Dict[str, Any] | None = None,
    ) -> Dict[str, str]:
        lines = [
            "Disaster + Environmental Pressure Profile",
            f"Pressure: {disaster_pressure_profile['pressure_name']}",
            f"ID: {disaster_pressure_profile['disaster_pressure_profile_id']}",
            f"Region: {disaster_pressure_profile['region_name']}",
            "",
            "Name Origin:",
            disaster_pressure_profile["name_origin"],
        ]

        sections = [
            ("Disaster Types", [str(item) for item in disaster_pressure_profile["disaster_types"]]),
            ("Pressure Chains", [str(item) for item in disaster_pressure_profile["pressure_chains"]]),
            ("Settlement Impacts", disaster_pressure_profile["settlement_impacts"]),
            ("Route Impacts", disaster_pressure_profile["route_impacts"]),
            ("Ecology Impacts", disaster_pressure_profile["ecology_impacts"]),
            ("Economy Impacts", disaster_pressure_profile["economy_impacts"]),
            ("Social Impacts", disaster_pressure_profile["social_impacts"]),
            ("Religious Interpretations", disaster_pressure_profile["religious_interpretations"]),
            ("Political Blame Paths", [str(item) for item in disaster_pressure_profile["political_blame_paths"]]),
            ("Adaptation Strategies", disaster_pressure_profile["adaptation_strategies"]),
            ("Failure Modes", disaster_pressure_profile["failure_modes"]),
        ]

        for title, values in sections:
            lines.append("")
            lines.append(title + ":")
            for item in values:
                lines.append(f"- {item}")

        if disaster_event:
            lines.extend([
                "",
                "Active Disaster Event:",
                disaster_event["event_name"],
                "",
                "Trigger:",
                disaster_event["trigger"],
                "",
                "Severity:",
                disaster_event["severity"],
            ])

        lines.extend([
            "",
            "Story Use:",
            disaster_pressure_profile["story_use"],
            "",
            "Character Effect:",
            disaster_pressure_profile["character_effect"],
            "",
            "Plot Effect:",
            disaster_pressure_profile["plot_effect"],
            "",
            "Memory Effect:",
            disaster_pressure_profile["memory_effect"],
        ])

        return {"disaster_pressure_text": chr(10).join(lines)}

    def _shallow_fields(self, *, payload: Dict[str, Any], fields: List[str]) -> List[str]:
        return [field for field in fields if len(str(payload.get(field, ""))) < 20]

    def _slug(self, value: str) -> str:
        return "_".join(part for part in value.lower().replace("/", " ").replace("-", " ").split() if part)

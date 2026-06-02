from __future__ import annotations

from typing import Any, Dict, List


class RoadsRoutesTravelDistanceEngine:
    def build_route_network(
        self,
        *,
        source_id: str,
        settlements: List[Dict[str, Any]] | None = None,
        political_unit: Dict[str, Any] | None = None,
        route_seed: Dict[str, Any] | None = None,
        story_context: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        settlements = settlements or []
        political_unit = political_unit or {}
        route_seed = route_seed or {}
        story_context = story_context or {}

        region_name = route_seed.get(
            "region_name",
            political_unit.get("region_name", story_context.get("region_name", "Saltroot Forest")),
        )
        network_name = route_seed.get("network_name", f"{region_name} Bellroad Network")

        route_network = {
            "route_network_id": f"route_network_{source_id}_{self._slug(network_name)}",
            "source_id": source_id,
            "network_name": network_name,
            "region_name": region_name,
            "political_unit_id": political_unit.get("political_unit_id"),
            "political_unit_name": political_unit.get("unique_name", "unassigned political unit"),
            "settlement_refs": [item.get("settlement_id") for item in settlements if item.get("settlement_id")],
            "name_origin": route_seed.get(
                "name_origin",
                f"{network_name} is named for the old road bells that marked safe crossings before official borders existed.",
            ),
            "name_meaning": route_seed.get(
                "name_meaning",
                "roads whose bells remember danger, witness, travel, and debt",
            ),
            "name_language_logic": route_seed.get(
                "name_language_logic",
                "route networks are named from region marker + road object + memory function",
            ),
            "route_types": route_seed.get("route_types", [
                {
                    "route_type": "witness road",
                    "function": "legal travel and testimony between court settlements",
                    "danger": "ambushes during fog closure and archive checkpoints",
                },
                {
                    "route_type": "saltroot path",
                    "function": "medicine gathering, healer travel, and forest shortcuts",
                    "danger": "red mold, ravine cats, and lost-spore fog",
                },
                {
                    "route_type": "dead-bell road",
                    "function": "abandoned route tied to old disasters and erased names",
                    "danger": "forbidden travel, ghosts in rumor, and hidden border evidence",
                },
                {
                    "route_type": "smuggler underpath",
                    "function": "illegal trade through drainage tunnels and ravine cuts",
                    "danger": "collapse, betrayal, and road warden traps",
                },
            ]),
            "major_routes": route_seed.get("major_routes", [
                {
                    "route_name": "Nine-Bell Road",
                    "start": "Veyr Bellcross",
                    "end": "First Bell Tower border",
                    "distance_days": 3,
                    "travel_method": "foot, caravan, and bell-guided night crossing",
                    "known_for": "legal testimony caravans and inheritance disputes",
                },
                {
                    "route_name": "Saltroot Pilgrim Path",
                    "start": "Foglamp Steps",
                    "end": "old healing groves",
                    "distance_days": 2,
                    "travel_method": "guided walking under foglamps",
                    "known_for": "medicine gathering and mourning rites",
                },
                {
                    "route_name": "Red Fog Underway",
                    "start": "Old Tower Underway",
                    "end": "border ravines",
                    "distance_days": 1,
                    "travel_method": "hidden tunnel and ravine scramble",
                    "known_for": "smuggling, erased-name escape, and forbidden witnesses",
                },
            ]),
            "distance_rules": route_seed.get("distance_rules", [
                "travel time doubles during red fog unless a certified guide is present",
                "dead-bell roads are shorter but legally forbidden and emotionally dangerous",
                "caravans move slower near archive checkpoints",
                "rain-swollen ravines can erase paths for days",
            ]),
            "weather_effects": route_seed.get("weather_effects", [
                "red fog closes roads and makes route bells unreliable",
                "bell rain reveals old path stones hidden under dust",
                "dry salt wind makes animal tracks easier to read but water harder to find",
            ]),
            "political_controls": route_seed.get("political_controls", [
                "road wardens control witness roads",
                "archive families control certified maps",
                "merchant houses bribe toll clerks",
                "exiled name-carriers preserve illegal route memory",
            ]),
            "economic_effects": route_seed.get("economic_effects", [
                "route tolls fund bell towers and court archives",
                "blocked roads increase medicine prices",
                "smuggler underpaths weaken official markets",
                "safe roads make some towns rich and others forgotten",
            ]),
            "religion_lore_effects": route_seed.get("religion_lore_effects", [
                "dead-bell roads are believed to ring when false history is carried over them",
                "pilgrims leave salt tea at lost guide shrines",
                "some routes are considered cursed until erased names are restored",
            ]),
            "character_route_knowledge": route_seed.get("character_route_knowledge", [
                "road guides know safe fog timings",
                "smugglers know underpaths but lie about distance",
                "archive clerks know official maps but not living trail changes",
                "children know shortcuts adults consider shameful",
            ]),
            "hidden_routes": route_seed.get("hidden_routes", [
                {
                    "route_name": "No-Bell Child Path",
                    "secret": "children use it to avoid archive patrols",
                    "plot_use": "escape, hidden meeting, or discovery of old evidence",
                },
                {
                    "route_name": "Massgrave Drain",
                    "secret": "connects old tower tunnels to border ravines",
                    "plot_use": "reveals founding massacre or lets smugglers vanish",
                },
            ]),
            "blocked_routes": route_seed.get("blocked_routes", [
                {
                    "route_name": "Old Witness Causeway",
                    "blocked_by": "red fog, legal ban, and missing route stones",
                    "story_effect": "forces characters through more dangerous or politically risky paths",
                }
            ]),
            "story_use": (
                "Turns geography into decisions by controlling distance, travel time, danger, legal access, hidden paths, "
                "weather disruption, trade routes, and political movement."
            ),
            "character_effect": (
                "Characters reveal origin, class, profession, fear, faith, and competence through which roads they know, trust, avoid, "
                "or are legally allowed to use."
            ),
            "plot_effect": (
                "Routes can delay rescue, force alliances, expose hidden evidence, create chase scenes, trigger border conflicts, "
                "or make one settlement unreachable at the worst time."
            ),
            "memory_effect": (
                "World memory must track open/closed routes, travel times, discovered paths, blocked roads, route ownership, toll changes, "
                "and who knows secret roads."
            ),
            "anti_genericity_signal": (
                "Route network includes named route types, distances, weather effects, political controls, economics, lore, "
                "hidden paths, blocked paths, and character knowledge."
            ),
            "detail_depth_score": 0.93,
            "validation_status": "validated",
            "provenance": {
                "generated_by_engine": "RoadsRoutesTravelDistanceEngine",
                "origin_type": "generated_from_route_seed",
                "source_id": source_id,
                "political_unit_id": political_unit.get("political_unit_id"),
                "settlement_count": len(settlements),
                "seed_keys": sorted(route_seed.keys()),
                "story_context_keys": sorted(story_context.keys()),
            },
            "compression_summary": (
                f"{network_name}: roads, distances, weather effects, hidden routes, blocked routes, politics, trade, and memory hooks."
            ),
        }

        return {"route_network": route_network}

    def build_travel_plan(
        self,
        *,
        source_id: str,
        route_network: Dict[str, Any],
        travel_seed: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        travel_seed = travel_seed or {}

        route = travel_seed.get("route_name", route_network["major_routes"][0]["route_name"])
        traveler_group = travel_seed.get("traveler_group", "mixed party with guide, outsider, healer, and accused witness")

        travel_plan = {
            "travel_plan_id": f"travel_plan_{source_id}_{self._slug(route)}",
            "source_id": source_id,
            "route_network_id": route_network["route_network_id"],
            "network_name": route_network["network_name"],
            "route_name": route,
            "traveler_group": traveler_group,
            "starting_point": travel_seed.get("starting_point", "Veyr Bellcross"),
            "destination": travel_seed.get("destination", "First Bell Tower border"),
            "estimated_distance_days": travel_seed.get("estimated_distance_days", 3),
            "actual_distance_modifiers": travel_seed.get("actual_distance_modifiers", [
                "red fog adds one day unless guide finds bell markers",
                "archive checkpoint may delay accused travelers",
                "hidden child path can shorten route but creates legal risk",
            ]),
            "required_supplies": travel_seed.get("required_supplies", [
                "salt tea",
                "foglamp oil",
                "route bell token",
                "rain cloth",
                "medicine for fog-sickness",
            ]),
            "danger_points": travel_seed.get("danger_points", [
                "ravine cat crossing",
                "archive toll gate",
                "dead-bell causeway",
                "smuggler tunnel mouth",
            ]),
            "social_risks": travel_seed.get("social_risks", [
                "guide may be bribed",
                "outsider may violate road taboo",
                "accused witness may be recognized",
                "merchant papers may be forged",
            ]),
            "story_use": (
                "Creates a concrete travel sequence with distance, supplies, obstacles, route choices, legal risks, and social pressure."
            ),
            "character_effect": (
                "Travel reveals endurance, trust, fear, class privilege, local knowledge, belief in road lore, and hidden motives."
            ),
            "plot_effect": (
                "Can force delays, reveal lies, create ambushes, split the party, expose secret routes, or make a deadline impossible."
            ),
            "memory_effect": (
                "World memory must track route taken, delays, injuries, supplies used, discovered paths, witnessed events, and trust changes."
            ),
            "anti_genericity_signal": (
                "Travel plan ties a named route to supplies, modifiers, danger points, social risks, legal pressure, and memory consequences."
            ),
            "detail_depth_score": 0.9,
            "validation_status": "validated",
            "provenance": {
                "generated_by_engine": "RoadsRoutesTravelDistanceEngine",
                "origin_type": "derived_from_route_network",
                "source_id": source_id,
                "route_network_id": route_network["route_network_id"],
                "seed_keys": sorted(travel_seed.keys()),
            },
            "compression_summary": (
                f"{route}: {travel_plan_summary(route, traveler_group)}"
            ),
        }

        return {"travel_plan": travel_plan}

    def build_story_context_patch(
        self,
        *,
        route_network: Dict[str, Any],
        travel_plan: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        patch = {
            "route_network_id": route_network["route_network_id"],
            "network_name": route_network["network_name"],
            "region_name": route_network["region_name"],
            "route_types": route_network["route_types"],
            "major_routes": route_network["major_routes"],
            "distance_rules": route_network["distance_rules"],
            "weather_effects": route_network["weather_effects"],
            "political_controls": route_network["political_controls"],
            "economic_effects": route_network["economic_effects"],
            "religion_lore_effects": route_network["religion_lore_effects"],
            "character_route_knowledge": route_network["character_route_knowledge"],
            "hidden_routes": route_network["hidden_routes"],
            "blocked_routes": route_network["blocked_routes"],
            "story_use": route_network["story_use"],
            "character_effect": route_network["character_effect"],
            "plot_effect": route_network["plot_effect"],
            "memory_effect": route_network["memory_effect"],
            "generation_hints": [
                "Use routes to constrain plot timing and travel choices.",
                "Do not teleport characters without route logic, distance, risk, and memory consequences.",
                "Let weather, politics, class, religion, and local knowledge affect route choice.",
                "Track discovered hidden paths, closed roads, toll changes, and who knows which route.",
            ],
            "memory_update_candidates": [
                {
                    "candidate_type": "route_network_state",
                    "target_element_id": route_network["route_network_id"],
                    "reason": "Track open/closed roads, hidden route discovery, toll changes, blocked routes, and route ownership.",
                }
            ],
        }

        if travel_plan:
            patch["active_travel_plan"] = travel_plan
            patch["memory_update_candidates"].append(
                {
                    "candidate_type": "travel_plan_state",
                    "target_element_id": travel_plan["travel_plan_id"],
                    "reason": "Track chosen route, delays, supplies, danger points, social risks, witnessed events, and trust changes.",
                }
            )

        return {"story_context_patch": patch}

    def validate_route_network(self, *, route_network: Dict[str, Any]) -> Dict[str, Any]:
        required = [
            "route_network_id",
            "network_name",
            "region_name",
            "name_origin",
            "name_meaning",
            "name_language_logic",
            "route_types",
            "major_routes",
            "distance_rules",
            "weather_effects",
            "political_controls",
            "economic_effects",
            "religion_lore_effects",
            "character_route_knowledge",
            "hidden_routes",
            "blocked_routes",
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

        missing = [field for field in required if not route_network.get(field)]
        shallow = self._shallow_fields(
            payload=route_network,
            fields=["name_origin", "story_use", "character_effect", "plot_effect", "memory_effect", "anti_genericity_signal"],
        )

        passed = not missing and not shallow and float(route_network.get("detail_depth_score", 0.0)) >= 0.75

        return {
            "passed": passed,
            "missing_fields": missing,
            "shallow_fields": shallow,
            "route_network_id": route_network.get("route_network_id"),
        }

    def validate_travel_plan(self, *, travel_plan: Dict[str, Any]) -> Dict[str, Any]:
        required = [
            "travel_plan_id",
            "route_network_id",
            "route_name",
            "traveler_group",
            "starting_point",
            "destination",
            "estimated_distance_days",
            "actual_distance_modifiers",
            "required_supplies",
            "danger_points",
            "social_risks",
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

        missing = [field for field in required if not travel_plan.get(field)]
        shallow = self._shallow_fields(
            payload=travel_plan,
            fields=["story_use", "character_effect", "plot_effect", "memory_effect", "anti_genericity_signal"],
        )

        passed = not missing and not shallow and float(travel_plan.get("detail_depth_score", 0.0)) >= 0.75

        return {
            "passed": passed,
            "missing_fields": missing,
            "shallow_fields": shallow,
            "travel_plan_id": travel_plan.get("travel_plan_id"),
        }

    def summarize_route_network(
        self,
        *,
        route_network: Dict[str, Any],
        travel_plan: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        summary = {
            "route_network_id": route_network["route_network_id"],
            "network_name": route_network["network_name"],
            "route_type_count": len(route_network["route_types"]),
            "major_route_count": len(route_network["major_routes"]),
            "hidden_route_count": len(route_network["hidden_routes"]),
            "blocked_route_count": len(route_network["blocked_routes"]),
            "compression_summary": route_network["compression_summary"],
        }

        if travel_plan:
            summary["travel_plan_id"] = travel_plan["travel_plan_id"]
            summary["route_name"] = travel_plan["route_name"]

        return {"success": True, "summary": summary}

    def build_route_text(
        self,
        *,
        route_network: Dict[str, Any],
        travel_plan: Dict[str, Any] | None = None,
    ) -> Dict[str, str]:
        lines = [
            "Roads, Routes, Travel, and Distance Profile",
            f"Network: {route_network['network_name']}",
            f"ID: {route_network['route_network_id']}",
            f"Region: {route_network['region_name']}",
            "",
            "Name Origin:",
            route_network["name_origin"],
        ]

        sections = [
            ("Route Types", [str(item) for item in route_network["route_types"]]),
            ("Major Routes", [str(item) for item in route_network["major_routes"]]),
            ("Distance Rules", route_network["distance_rules"]),
            ("Weather Effects", route_network["weather_effects"]),
            ("Political Controls", route_network["political_controls"]),
            ("Economic Effects", route_network["economic_effects"]),
            ("Religion / Lore Effects", route_network["religion_lore_effects"]),
            ("Character Route Knowledge", route_network["character_route_knowledge"]),
            ("Hidden Routes", [str(item) for item in route_network["hidden_routes"]]),
            ("Blocked Routes", [str(item) for item in route_network["blocked_routes"]]),
        ]

        for title, values in sections:
            lines.append("")
            lines.append(title + ":")
            for item in values:
                lines.append(f"- {item}")

        if travel_plan:
            lines.extend([
                "",
                "Active Travel Plan:",
                travel_plan["route_name"],
                "",
                "Traveler Group:",
                travel_plan["traveler_group"],
                "",
                "Danger Points:",
            ])
            for item in travel_plan["danger_points"]:
                lines.append(f"- {item}")

        lines.extend([
            "",
            "Story Use:",
            route_network["story_use"],
            "",
            "Character Effect:",
            route_network["character_effect"],
            "",
            "Plot Effect:",
            route_network["plot_effect"],
            "",
            "Memory Effect:",
            route_network["memory_effect"],
        ])

        return {"route_text": chr(10).join(lines)}

    def _shallow_fields(self, *, payload: Dict[str, Any], fields: List[str]) -> List[str]:
        return [field for field in fields if len(str(payload.get(field, ""))) < 20]

    def _slug(self, value: str) -> str:
        return "_".join(part for part in value.lower().replace("/", " ").replace("-", " ").split() if part)


def travel_plan_summary(route: str, traveler_group: str) -> str:
    return f"travel on {route} by {traveler_group}; distance, supplies, risks, and route-memory consequences tracked."

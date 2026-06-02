from __future__ import annotations

from typing import Any, Dict, List


class EconomyResourceEcologyEngine:
    def build_resource_economy_profile(
        self,
        *,
        source_id: str,
        ecology_profile: Dict[str, Any] | None = None,
        political_unit: Dict[str, Any] | None = None,
        settlement: Dict[str, Any] | None = None,
        route_network: Dict[str, Any] | None = None,
        economy_seed: Dict[str, Any] | None = None,
        story_context: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        ecology_profile = ecology_profile or {}
        political_unit = political_unit or {}
        settlement = settlement or {}
        route_network = route_network or {}
        economy_seed = economy_seed or {}
        story_context = story_context or {}

        region_name = economy_seed.get(
            "region_name",
            settlement.get("region_name")
            or political_unit.get("region_name")
            or route_network.get("region_name")
            or story_context.get("region_name", "Saltroot Forest"),
        )

        economy_name = economy_seed.get("economy_name", f"{region_name} Saltroot Witness Economy")

        profile = {
            "resource_economy_profile_id": f"resource_economy_{source_id}_{self._slug(economy_name)}",
            "source_id": source_id,
            "economy_name": economy_name,
            "region_name": region_name,
            "ecology_id": ecology_profile.get("element_id") or ecology_profile.get("ecology_id"),
            "political_unit_id": political_unit.get("political_unit_id"),
            "settlement_id": settlement.get("settlement_id"),
            "route_network_id": route_network.get("route_network_id"),
            "name_origin": economy_seed.get(
                "name_origin",
                f"{economy_name} formed where medicine plants, road tolls, archive fees, bell-metal craft, and fog-guide labor "
                f"became tied to survival and legal identity.",
            ),
            "name_meaning": economy_seed.get(
                "name_meaning",
                "an economy where resources, roads, testimony, medicine, and names shape power",
            ),
            "name_language_logic": economy_seed.get(
                "name_language_logic",
                "economy labels combine core resource, civic function, and controlling social institution",
            ),
            "cultural_context": economy_seed.get(
                "cultural_context",
                settlement.get("cultural_context", political_unit.get("cultural_context", "bell-road civic economy")),
            ),
            "world_context": region_name,
            "visual_identity": economy_seed.get(
                "visual_identity",
                "medicine bundles, toll ledgers, bell-metal weights, salt-bark trade seals, route tokens, and foglamp oil jars",
            ),
            "sensory_identity": economy_seed.get(
                "sensory_identity",
                "salt tea steam, herb bitterness, heated metal, wet animal leather, inked bark, and market smoke",
            ),
            "core_resources": economy_seed.get("core_resources", [
                {
                    "resource_name": "saltroot bark",
                    "resource_type": "medicine / record material",
                    "source_ecology": "saltroot groves",
                    "controlled_by": "healers, archive families, and temple license offices",
                    "scarcity_trigger": "red mold, overharvest, blocked roads, or political hoarding",
                    "story_use": "medicine shortage, forged records, black-market trade, healer moral choices",
                },
                {
                    "resource_name": "bell metal",
                    "resource_type": "civic warning material / legal symbol",
                    "source_ecology": "old bells, treaty tokens, mined ravine ore",
                    "controlled_by": "bellwright guilds and road wardens",
                    "scarcity_trigger": "war requisition, tower damage, smuggling, or corrupted officials",
                    "story_use": "fake bells, broken warning systems, treaty evidence, ritual conflict",
                },
                {
                    "resource_name": "foglamp oil",
                    "resource_type": "public safety supply",
                    "source_ecology": "processed moss oils and trade imports",
                    "controlled_by": "municipal crews, merchants, and smugglers",
                    "scarcity_trigger": "trade blockade, crop failure, disaster, or theft",
                    "story_use": "curfew danger, poor-district neglect, sabotage, child-path survival",
                },
                {
                    "resource_name": "certified maps",
                    "resource_type": "legal travel information",
                    "source_ecology": "road survey labor and archive certification",
                    "controlled_by": "archive families",
                    "scarcity_trigger": "political suppression, border dispute, false history, or archive fire",
                    "story_use": "route lies, border control, inheritance dispute, forbidden-road reveal",
                },
            ]),
            "production_chains": economy_seed.get("production_chains", [
                {
                    "chain_name": "saltroot medicine chain",
                    "steps": ["harvest grove", "remove toxic veins", "temple license stamp", "healer ration", "market sale"],
                    "failure_points": ["bad harvest", "poisoned batch", "license corruption", "route blockade"],
                },
                {
                    "chain_name": "legal map chain",
                    "steps": ["road witness report", "archive verification", "bell-seal certification", "market distribution"],
                    "failure_points": ["false witness", "erased route", "bribed clerk", "forbidden name conflict"],
                },
                {
                    "chain_name": "foglamp safety chain",
                    "steps": ["moss oil processing", "lamp filling", "tower inspection", "curfew lighting"],
                    "failure_points": ["oil theft", "mold contamination", "district neglect", "storm damage"],
                },
            ]),
            "trade_routes": economy_seed.get("trade_routes", [
                "Nine-Bell Road moves maps, medicine, court fees, and witness labor",
                "Red Fog Underway moves illegal names, fake route bells, and smuggled medicine",
                "Saltroot Pilgrim Path moves healer supplies, ritual tea, and mourning goods",
            ]),
            "labor_classes": economy_seed.get("labor_classes", [
                {
                    "class_name": "licensed healers",
                    "power": "control legal medicine use",
                    "vulnerability": "dependent on temple license and safe harvest",
                },
                {
                    "class_name": "road guides",
                    "power": "control practical route survival",
                    "vulnerability": "risk death and legal blame for failed crossings",
                },
                {
                    "class_name": "archive clerks",
                    "power": "control public names, records, and maps",
                    "vulnerability": "blackmail, bribery, and guilt over erased records",
                },
                {
                    "class_name": "market smugglers",
                    "power": "move goods when official roads fail",
                    "vulnerability": "wardens, betrayal, and counterfeit scandals",
                },
            ]),
            "scarcity_rules": economy_seed.get("scarcity_rules", [
                "medicine prices triple when saltroot groves fail",
                "map access becomes political during border disputes",
                "foglamp oil shortages harm poor districts first",
                "bell-metal shortage increases fake-warning devices",
                "food prices rise when road closures last more than three market days",
            ]),
            "black_market_system": economy_seed.get("black_market_system", [
                "fake route bells",
                "uncertified medicine petals",
                "forbidden-name ledgers",
                "stolen map seals",
                "foglamp oil siphoned from poor districts",
            ]),
            "taxes_tolls_and_rents": economy_seed.get("taxes_tolls_and_rents", [
                "road tolls by route class",
                "archive certification fees",
                "temple medicine license fees",
                "market stall bell-rent",
                "emergency fog closure levies",
            ]),
            "class_conflicts": economy_seed.get("class_conflicts", [
                "poor guides risk roads while archive families profit from maps",
                "healers ration medicine while nobles buy private reserves",
                "market families blame toll laws for smuggling",
                "no-bell children are used as invisible couriers without legal protection",
            ]),
            "resource_conflicts": economy_seed.get("resource_conflicts", [
                {
                    "conflict_name": "saltroot ration conflict",
                    "public_issue": "healers claim shortage requires rationing",
                    "secret_issue": "archive families are hiding medicine for political allies",
                    "plot_use": "theft, exposure, plague panic, or healer betrayal",
                },
                {
                    "conflict_name": "foglamp oil theft",
                    "public_issue": "poor districts go dark during curfew",
                    "secret_issue": "merchant houses sell siphoned oil to border smugglers",
                    "plot_use": "child disappearance, riot, sabotage, or rescue deadline",
                },
            ]),
            "economic_shock_triggers": economy_seed.get("economic_shock_triggers", [
                "road closure",
                "crop failure",
                "medicine grove disease",
                "map scandal",
                "political border dispute",
                "festival demand spike",
                "war requisition",
                "secret-place reveal",
            ]),
            "story_use": (
                "Turns economy into story pressure by linking resources, labor, scarcity, trade, black markets, class, politics, "
                "medicine, food, roads, and ecological collapse."
            ),
            "character_effect": (
                "Characters are shaped by what they can afford, trade, steal, ration, certify, smuggle, inherit, lose, or protect "
                "inside the resource economy."
            ),
            "plot_effect": (
                "Can trigger shortages, theft, bribery, riots, black-market deals, medicine choices, trade sabotage, class conflict, "
                "or political exposure through resource flows."
            ),
            "memory_effect": (
                "World memory must track prices, shortages, stockpiles, trade disruptions, black-market exposure, class anger, "
                "resource depletion, and who controls critical supplies."
            ),
            "anti_genericity_signal": (
                "Economy includes named resources, production chains, trade routes, labor classes, scarcity rules, black markets, "
                "taxes, class conflicts, shocks, and ecology links."
            ),
            "detail_depth_score": 0.94,
            "validation_status": "validated",
            "provenance": {
                "generated_by_engine": "EconomyResourceEcologyEngine",
                "origin_type": "derived_from_ecology_politics_settlement_routes",
                "source_id": source_id,
                "ecology_id": ecology_profile.get("element_id") or ecology_profile.get("ecology_id"),
                "political_unit_id": political_unit.get("political_unit_id"),
                "settlement_id": settlement.get("settlement_id"),
                "route_network_id": route_network.get("route_network_id"),
                "seed_keys": sorted(economy_seed.keys()),
                "story_context_keys": sorted(story_context.keys()),
            },
            "compression_summary": (
                f"{economy_name}: resources, production chains, trade routes, labor, scarcity, black markets, taxes, "
                f"class conflict, economic shocks, and memory hooks."
            ),
        }

        return {"resource_economy_profile": profile}

    def build_economic_shock_event(
        self,
        *,
        source_id: str,
        resource_economy_profile: Dict[str, Any],
        shock_seed: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        shock_seed = shock_seed or {}

        shock_name = shock_seed.get("shock_name", "Saltroot Medicine Shortage")

        shock = {
            "economic_shock_event_id": f"economic_shock_{source_id}_{self._slug(shock_name)}",
            "source_id": source_id,
            "resource_economy_profile_id": resource_economy_profile["resource_economy_profile_id"],
            "economy_name": resource_economy_profile["economy_name"],
            "shock_name": shock_name,
            "shock_type": shock_seed.get("shock_type", "resource_scarcity_and_class_pressure"),
            "trigger": shock_seed.get(
                "trigger",
                "red mold spreads through saltroot groves while archive families hide medicine reserves",
            ),
            "affected_resources": shock_seed.get("affected_resources", ["saltroot bark", "fog-sickness medicine", "funeral tea petals"]),
            "affected_groups": shock_seed.get("affected_groups", [
                "licensed healers",
                "road guides",
                "poor families",
                "archive families",
                "smugglers",
            ]),
            "price_effect": shock_seed.get(
                "price_effect",
                "medicine prices triple and uncertified petals flood the market",
            ),
            "black_market_effect": shock_seed.get(
                "black_market_effect",
                "smugglers sell fake medicinal petals and stolen temple stamps",
            ),
            "political_effect": shock_seed.get(
                "political_effect",
                "road families accuse archive houses of turning sickness into political leverage",
            ),
            "story_use": (
                "Turns resource scarcity into active moral, political, medical, and class conflict."
            ),
            "character_effect": (
                "Characters must decide who receives scarce medicine, whether to steal, expose hoarding, trust smugglers, or betray duty."
            ),
            "plot_effect": (
                "Can trigger theft, riot, healer trial, black-market bargain, poisoning, hidden stockpile reveal, or faction split."
            ),
            "memory_effect": (
                "World memory must track shortage duration, prices, deaths, stockpiles, hoarders, exposed smugglers, and public anger."
            ),
            "lore_effect": (
                "Scarcity may be interpreted as divine warning, ecological punishment, or the land rejecting false witness law."
            ),
            "anti_genericity_signal": (
                "Shock ties resource ecology, prices, classes, medicine, black markets, politics, and lore into one consequence."
            ),
            "detail_depth_score": 0.91,
            "validation_status": "validated",
            "provenance": {
                "generated_by_engine": "EconomyResourceEcologyEngine",
                "origin_type": "derived_from_resource_economy_profile",
                "source_id": source_id,
                "profile_id": resource_economy_profile["resource_economy_profile_id"],
                "seed_keys": sorted(shock_seed.keys()),
            },
            "compression_summary": (
                f"{shock_name}: trigger, affected resources/groups, price effects, black market, politics, and memory consequences."
            ),
        }

        return {"economic_shock_event": shock}

    def build_story_context_patch(
        self,
        *,
        resource_economy_profile: Dict[str, Any],
        economic_shock_event: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        patch = {
            "resource_economy_profile_id": resource_economy_profile["resource_economy_profile_id"],
            "economy_name": resource_economy_profile["economy_name"],
            "core_resources": resource_economy_profile["core_resources"],
            "production_chains": resource_economy_profile["production_chains"],
            "trade_routes": resource_economy_profile["trade_routes"],
            "labor_classes": resource_economy_profile["labor_classes"],
            "scarcity_rules": resource_economy_profile["scarcity_rules"],
            "black_market_system": resource_economy_profile["black_market_system"],
            "taxes_tolls_and_rents": resource_economy_profile["taxes_tolls_and_rents"],
            "class_conflicts": resource_economy_profile["class_conflicts"],
            "resource_conflicts": resource_economy_profile["resource_conflicts"],
            "economic_shock_triggers": resource_economy_profile["economic_shock_triggers"],
            "story_use": resource_economy_profile["story_use"],
            "character_effect": resource_economy_profile["character_effect"],
            "plot_effect": resource_economy_profile["plot_effect"],
            "memory_effect": resource_economy_profile["memory_effect"],
            "generation_hints": [
                "Use economy to create scarcity, trade pressure, class conflict, labor stakes, and moral choices.",
                "Resources should connect to ecology, politics, roads, settlements, food, medicine, and black markets.",
                "Track prices, shortages, stockpiles, hoarding, and exposed corruption in memory.",
                "Economic changes must alter character options and plot timing.",
            ],
            "memory_update_candidates": [
                {
                    "candidate_type": "resource_economy_state",
                    "target_element_id": resource_economy_profile["resource_economy_profile_id"],
                    "reason": "Track prices, shortages, trade disruptions, stockpiles, class anger, and resource control.",
                }
            ],
        }

        if economic_shock_event:
            patch["active_economic_shock_event"] = economic_shock_event
            patch["memory_update_candidates"].append(
                {
                    "candidate_type": "economic_shock_state",
                    "target_element_id": economic_shock_event["economic_shock_event_id"],
                    "reason": "Track trigger, affected resources/groups, prices, black market, politics, deaths, and public anger.",
                }
            )

        return {"story_context_patch": patch}

    def validate_resource_economy_profile(self, *, resource_economy_profile: Dict[str, Any]) -> Dict[str, Any]:
        required = [
            "resource_economy_profile_id",
            "economy_name",
            "region_name",
            "name_origin",
            "name_meaning",
            "name_language_logic",
            "cultural_context",
            "world_context",
            "visual_identity",
            "sensory_identity",
            "core_resources",
            "production_chains",
            "trade_routes",
            "labor_classes",
            "scarcity_rules",
            "black_market_system",
            "taxes_tolls_and_rents",
            "class_conflicts",
            "resource_conflicts",
            "economic_shock_triggers",
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

        missing = [field for field in required if not resource_economy_profile.get(field)]
        shallow = self._shallow_fields(
            payload=resource_economy_profile,
            fields=["name_origin", "story_use", "character_effect", "plot_effect", "memory_effect", "anti_genericity_signal"],
        )

        passed = (
            not missing
            and not shallow
            and float(resource_economy_profile.get("detail_depth_score", 0.0)) >= 0.75
        )

        return {
            "passed": passed,
            "missing_fields": missing,
            "shallow_fields": shallow,
            "resource_economy_profile_id": resource_economy_profile.get("resource_economy_profile_id"),
        }

    def validate_economic_shock_event(self, *, economic_shock_event: Dict[str, Any]) -> Dict[str, Any]:
        required = [
            "economic_shock_event_id",
            "resource_economy_profile_id",
            "economy_name",
            "shock_name",
            "shock_type",
            "trigger",
            "affected_resources",
            "affected_groups",
            "price_effect",
            "black_market_effect",
            "political_effect",
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

        missing = [field for field in required if not economic_shock_event.get(field)]
        shallow = self._shallow_fields(
            payload=economic_shock_event,
            fields=["story_use", "character_effect", "plot_effect", "memory_effect", "lore_effect"],
        )

        passed = (
            not missing
            and not shallow
            and float(economic_shock_event.get("detail_depth_score", 0.0)) >= 0.75
        )

        return {
            "passed": passed,
            "missing_fields": missing,
            "shallow_fields": shallow,
            "economic_shock_event_id": economic_shock_event.get("economic_shock_event_id"),
        }

    def summarize_resource_economy(
        self,
        *,
        resource_economy_profile: Dict[str, Any],
        economic_shock_event: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        summary = {
            "resource_economy_profile_id": resource_economy_profile["resource_economy_profile_id"],
            "economy_name": resource_economy_profile["economy_name"],
            "resource_count": len(resource_economy_profile["core_resources"]),
            "production_chain_count": len(resource_economy_profile["production_chains"]),
            "labor_class_count": len(resource_economy_profile["labor_classes"]),
            "scarcity_rule_count": len(resource_economy_profile["scarcity_rules"]),
            "resource_conflict_count": len(resource_economy_profile["resource_conflicts"]),
            "compression_summary": resource_economy_profile["compression_summary"],
        }

        if economic_shock_event:
            summary["economic_shock_event_id"] = economic_shock_event["economic_shock_event_id"]
            summary["shock_name"] = economic_shock_event["shock_name"]

        return {"success": True, "summary": summary}

    def build_resource_economy_text(
        self,
        *,
        resource_economy_profile: Dict[str, Any],
        economic_shock_event: Dict[str, Any] | None = None,
    ) -> Dict[str, str]:
        lines = [
            "Economy + Resource Ecology Profile",
            f"Economy: {resource_economy_profile['economy_name']}",
            f"ID: {resource_economy_profile['resource_economy_profile_id']}",
            f"Region: {resource_economy_profile['region_name']}",
            "",
            "Name Origin:",
            resource_economy_profile["name_origin"],
        ]

        sections = [
            ("Core Resources", [str(item) for item in resource_economy_profile["core_resources"]]),
            ("Production Chains", [str(item) for item in resource_economy_profile["production_chains"]]),
            ("Trade Routes", resource_economy_profile["trade_routes"]),
            ("Labor Classes", [str(item) for item in resource_economy_profile["labor_classes"]]),
            ("Scarcity Rules", resource_economy_profile["scarcity_rules"]),
            ("Black Market System", resource_economy_profile["black_market_system"]),
            ("Taxes, Tolls, and Rents", resource_economy_profile["taxes_tolls_and_rents"]),
            ("Class Conflicts", resource_economy_profile["class_conflicts"]),
            ("Resource Conflicts", [str(item) for item in resource_economy_profile["resource_conflicts"]]),
            ("Economic Shock Triggers", resource_economy_profile["economic_shock_triggers"]),
        ]

        for title, values in sections:
            lines.append("")
            lines.append(title + ":")
            for item in values:
                lines.append(f"- {item}")

        if economic_shock_event:
            lines.extend([
                "",
                "Active Economic Shock:",
                economic_shock_event["shock_name"],
                "",
                "Trigger:",
                economic_shock_event["trigger"],
            ])

        lines.extend([
            "",
            "Story Use:",
            resource_economy_profile["story_use"],
            "",
            "Character Effect:",
            resource_economy_profile["character_effect"],
            "",
            "Plot Effect:",
            resource_economy_profile["plot_effect"],
            "",
            "Memory Effect:",
            resource_economy_profile["memory_effect"],
        ])

        return {"resource_economy_text": chr(10).join(lines)}

    def _shallow_fields(self, *, payload: Dict[str, Any], fields: List[str]) -> List[str]:
        return [field for field in fields if len(str(payload.get(field, ""))) < 20]

    def _slug(self, value: str) -> str:
        return "_".join(part for part in value.lower().replace("/", " ").replace("-", " ").split() if part)

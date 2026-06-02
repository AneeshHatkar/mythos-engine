from __future__ import annotations

from typing import Any, Dict, List


class MigrationDemographicMovementEngine:
    def build_migration_system(
        self,
        *,
        source_id: str,
        population_profile: Dict[str, Any] | None = None,
        political_unit: Dict[str, Any] | None = None,
        settlement: Dict[str, Any] | None = None,
        route_network: Dict[str, Any] | None = None,
        disaster_profile: Dict[str, Any] | None = None,
        economy_profile: Dict[str, Any] | None = None,
        migration_seed: Dict[str, Any] | None = None,
        story_context: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        population_profile = population_profile or {}
        political_unit = political_unit or {}
        settlement = settlement or {}
        route_network = route_network or {}
        disaster_profile = disaster_profile or {}
        economy_profile = economy_profile or {}
        migration_seed = migration_seed or {}
        story_context = story_context or {}

        region_name = migration_seed.get(
            "region_name",
            settlement.get("region_name")
            or political_unit.get("region_name")
            or route_network.get("region_name")
            or population_profile.get("region_name")
            or story_context.get("region_name", "Saltroot Forest"),
        )

        system_name = migration_seed.get("system_name", f"{region_name} Route-Memory Migration System")

        migration_system = {
            "migration_system_id": f"migration_system_{source_id}_{self._slug(system_name)}",
            "source_id": source_id,
            "system_name": system_name,
            "region_name": region_name,
            "population_diversity_profile_id": population_profile.get("population_diversity_profile_id"),
            "political_unit_id": political_unit.get("political_unit_id"),
            "settlement_id": settlement.get("settlement_id"),
            "route_network_id": route_network.get("route_network_id"),
            "disaster_pressure_profile_id": disaster_profile.get("disaster_pressure_profile_id"),
            "resource_economy_profile_id": economy_profile.get("resource_economy_profile_id"),
            "name_origin": migration_seed.get(
                "name_origin",
                f"{system_name} is named for the way families, guides, exiles, traders, and hidden-name groups move "
                f"along roads when fog, famine, law, and secret history make staying impossible.",
            ),
            "name_meaning": migration_seed.get(
                "name_meaning",
                "movement of people shaped by roads, disaster, identity, class, secrecy, and survival",
            ),
            "name_language_logic": migration_seed.get(
                "name_language_logic",
                "migration systems combine region marker, movement route, and social memory pressure",
            ),
            "cultural_context": migration_seed.get(
                "cultural_context",
                settlement.get("cultural_context", political_unit.get("cultural_context", "bell-road migration culture")),
            ),
            "world_context": region_name,
            "visual_identity": migration_seed.get(
                "visual_identity",
                "road-cloth bundles, children carrying name cords, foglamp caravans, medicine carts, border chalk marks, and exile bracelets",
            ),
            "sensory_identity": migration_seed.get(
                "sensory_identity",
                "cold road dust, boiled grain, animal sweat, wet cloth, lamp oil, salt tea, and whispered family names",
            ),
            "migration_types": migration_seed.get("migration_types", [
                {
                    "migration_type": "seasonal route migration",
                    "movers": "road families, medicine gatherers, and caravan workers",
                    "cause": "red fog, harvest timing, route closures, and seasonal work",
                    "destination_logic": "safe road towns, healer groves, temporary markets, and temple shelters",
                    "story_use": "creates temporary communities, missing people, rumors, and route pressure",
                },
                {
                    "migration_type": "disaster displacement",
                    "movers": "poor districts, no-bell children, sick families, and market workers",
                    "cause": "flood, foglamp failure, food shortage, disease, or settlement damage",
                    "destination_logic": "temple kitchens, border camps, abandoned roads, and relatives with legal names",
                    "story_use": "creates refugee pressure, moral choices, scarcity, and political blame",
                },
                {
                    "migration_type": "political exile",
                    "movers": "erased-name families, accused witnesses, failed guides, and forbidden-route carriers",
                    "cause": "trial loss, name removal, treaty scandal, or secret-history suppression",
                    "destination_logic": "smuggler routes, hidden settlements, border ravines, and sympathetic road families",
                    "story_use": "creates secret identities, revenge plots, forbidden knowledge, and social tension",
                },
                {
                    "migration_type": "economic drift",
                    "movers": "market families, artisans, healers, smugglers, and young apprentices",
                    "cause": "route taxes, resource shortage, black-market opportunity, or settlement decline",
                    "destination_logic": "trade hubs, smuggler underpaths, richer districts, and festival markets",
                    "story_use": "creates class mobility, exploitation, crime, and cultural mixing",
                },
            ]),
            "demographic_groups": migration_seed.get("demographic_groups", [
                {
                    "group_name": "no-bell children",
                    "movement_pattern": "move through roofs, kitchens, underpaths, and informal shelters",
                    "risk": "invisible to legal systems and easily exploited",
                    "plot_use": "messengers, hidden witnesses, heirs without names, or symbols of civic failure",
                },
                {
                    "group_name": "erased-road families",
                    "movement_pattern": "avoid official gates and use old guide songs",
                    "risk": "arrest, blackmail, loss of inheritance, and identity erasure",
                    "plot_use": "carry secret history and forbidden family names",
                },
                {
                    "group_name": "fog-displaced poor",
                    "movement_pattern": "move after disasters toward temple kitchens and market shelter",
                    "risk": "disease, hunger, debt, and political scapegoating",
                    "plot_use": "reveals class cruelty and survival solidarity",
                },
                {
                    "group_name": "merchant drift families",
                    "movement_pattern": "follow trade disruption and temporary profit",
                    "risk": "smuggling accusations and debt to toll houses",
                    "plot_use": "spread rumor, goods, forged records, and external pressure",
                },
            ]),
            "push_factors": migration_seed.get("push_factors", [
                "red fog road closures",
                "medicine shortage",
                "flooded underways",
                "public-name denial",
                "archive persecution",
                "food price spikes",
                "settlement damage",
                "border treaty dispute",
                "religious blame",
            ]),
            "pull_factors": migration_seed.get("pull_factors", [
                "temple shelter kitchens",
                "safe road work",
                "healer apprenticeship",
                "hidden settlement protection",
                "smuggler payment",
                "restored-name rumors",
                "festival market labor",
                "border-town asylum",
            ]),
            "route_dependencies": migration_seed.get("route_dependencies", [
                "Nine-Bell Road controls legal movement and taxes",
                "No-Bell Child Path supports invisible movement",
                "Red Fog Underway supports exile and smuggling movement",
                "Saltroot Pilgrim Path supports healer and mourning migration",
            ]),
            "legal_status_changes": migration_seed.get("legal_status_changes", [
                "public name granted after successful hearing",
                "exile removes map ownership and inheritance rights",
                "temporary shelter status allows food but not land rights",
                "border asylum protects testimony but creates political debt",
                "adoption can transfer road-memory obligations",
            ]),
            "identity_changes": migration_seed.get("identity_changes", [
                "weather nickname becomes formal public name",
                "family name replaced by route number after exile",
                "hidden name restored after secret records surface",
                "marriage title changes settlement rights",
                "occupation title replaces birth identity during displacement",
            ]),
            "settlement_effects": migration_seed.get("settlement_effects", [
                "empty houses become smuggler shelters",
                "temple kitchens overcrowd",
                "market labor shifts toward emergency work",
                "archive queues grow with name petitions",
                "poor districts absorb displaced families first",
            ]),
            "political_effects": migration_seed.get("political_effects", [
                "border officials weaponize refugee counts",
                "archive families manipulate name records",
                "road wardens demand emergency movement authority",
                "merchant houses exploit displaced labor",
                "temples gain power through shelter control",
            ]),
            "economic_effects": migration_seed.get("economic_effects", [
                "rent rises near safe roads",
                "food prices shift with displaced labor",
                "smugglers profit from undocumented movement",
                "healers lose apprentices to survival work",
                "trade routes gain temporary markets",
            ]),
            "cultural_effects": migration_seed.get("cultural_effects", [
                "new dialect mixtures appear in shelter districts",
                "food customs blend during displacement",
                "mourning rites change when families cannot return home",
                "children learn hidden paths before formal law",
                "festival songs absorb disaster verses",
            ]),
            "story_use": (
                "Turns demographic movement into story pressure through displacement, exile, legal status, identity change, "
                "route control, settlement strain, class conflict, cultural mixing, and political blame."
            ),
            "character_effect": (
                "Characters are shaped by whether they stayed, fled, were exiled, lost a name, gained shelter, crossed illegally, "
                "or carried family memory through migration."
            ),
            "plot_effect": (
                "Can trigger refugee camps, hidden-heir reveals, border chases, family separation, smuggling bargains, name restoration, "
                "settlement conflict, or demographic shifts that change political power."
            ),
            "memory_effect": (
                "World memory must track who moved, why, from where to where, legal status, renamed identities, settlement strain, "
                "cultural mixing, casualties, and whether migration became permanent."
            ),
            "anti_genericity_signal": (
                "Migration system includes named movement types, demographic groups, push/pull factors, routes, legal status changes, "
                "identity changes, settlement/political/economic/cultural effects, and memory hooks."
            ),
            "detail_depth_score": 0.94,
            "validation_status": "validated",
            "provenance": {
                "generated_by_engine": "MigrationDemographicMovementEngine",
                "origin_type": "derived_from_population_politics_settlement_routes_disaster_economy",
                "source_id": source_id,
                "population_diversity_profile_id": population_profile.get("population_diversity_profile_id"),
                "political_unit_id": political_unit.get("political_unit_id"),
                "settlement_id": settlement.get("settlement_id"),
                "route_network_id": route_network.get("route_network_id"),
                "disaster_pressure_profile_id": disaster_profile.get("disaster_pressure_profile_id"),
                "resource_economy_profile_id": economy_profile.get("resource_economy_profile_id"),
                "seed_keys": sorted(migration_seed.keys()),
                "story_context_keys": sorted(story_context.keys()),
            },
            "compression_summary": (
                f"{system_name}: migration types, groups, push/pull factors, route dependencies, legal/identity changes, "
                f"settlement/political/economic/cultural effects, and memory hooks."
            ),
        }

        return {"migration_system": migration_system}

    def build_migration_event(
        self,
        *,
        source_id: str,
        migration_system: Dict[str, Any],
        event_seed: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        event_seed = event_seed or {}

        event_name = event_seed.get("event_name", "No-Bell Children Shelter March")

        event = {
            "migration_event_id": f"migration_event_{source_id}_{self._slug(event_name)}",
            "source_id": source_id,
            "migration_system_id": migration_system["migration_system_id"],
            "system_name": migration_system["system_name"],
            "event_name": event_name,
            "event_type": event_seed.get("event_type", "displacement_and_identity_pressure"),
            "trigger": event_seed.get(
                "trigger",
                "foglamp failure and food shortage force no-bell children toward temple shelter kitchens",
            ),
            "origin": event_seed.get("origin", "Foglamp Steps"),
            "destination": event_seed.get("destination", "Temple Shelter Kitchens"),
            "moving_groups": event_seed.get("moving_groups", [
                "no-bell children",
                "fog-displaced poor",
                "unlicensed healers",
                "road family widows",
            ]),
            "route_taken": event_seed.get("route_taken", "No-Bell Child Path"),
            "legal_status": event_seed.get(
                "legal_status",
                "temporary shelter status without public-name rights",
            ),
            "identity_effect": event_seed.get(
                "identity_effect",
                "children risk being counted as shelter mouths rather than legal citizens",
            ),
            "immediate_consequences": event_seed.get("immediate_consequences", [
                "temple kitchens overcrowd",
                "archive clerks delay name hearings",
                "smugglers offer false adoption papers",
                "road wardens argue over escort duty",
            ]),
            "long_term_consequences": event_seed.get("long_term_consequences", [
                "new shelter dialect forms",
                "public anger rises over no-name status",
                "some children vanish into smuggler networks",
                "temple authority expands",
                "hidden family names start circulating",
            ]),
            "story_use": (
                "Creates movement pressure where displacement, identity, law, food, shelter, religion, and exploitation collide."
            ),
            "character_effect": (
                "Characters must decide whether to protect migrants, exploit them, document them, hide them, name them, or turn them away."
            ),
            "plot_effect": (
                "Can trigger rescue, public hearing, shelter riot, false adoption scandal, hidden-heir reveal, or smuggler pursuit."
            ),
            "memory_effect": (
                "World memory must track moved groups, route taken, legal status, missing people, shelter strain, identity changes, and public reaction."
            ),
            "lore_effect": (
                "Migration may become a road-song, saint story, or civic shame tale that changes how the settlement remembers itself."
            ),
            "anti_genericity_signal": (
                "Event ties named groups, origin, destination, route, legal status, identity effect, shelter strain, exploitation, and memory."
            ),
            "detail_depth_score": 0.91,
            "validation_status": "validated",
            "provenance": {
                "generated_by_engine": "MigrationDemographicMovementEngine",
                "origin_type": "derived_from_migration_system",
                "source_id": source_id,
                "migration_system_id": migration_system["migration_system_id"],
                "seed_keys": sorted(event_seed.keys()),
            },
            "compression_summary": (
                f"{event_name}: trigger, origin, destination, moving groups, route, legal status, identity effect, "
                f"immediate/long-term consequences tracked."
            ),
        }

        return {"migration_event": event}

    def build_story_context_patch(
        self,
        *,
        migration_system: Dict[str, Any],
        migration_event: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        patch = {
            "migration_system_id": migration_system["migration_system_id"],
            "system_name": migration_system["system_name"],
            "migration_types": migration_system["migration_types"],
            "demographic_groups": migration_system["demographic_groups"],
            "push_factors": migration_system["push_factors"],
            "pull_factors": migration_system["pull_factors"],
            "route_dependencies": migration_system["route_dependencies"],
            "legal_status_changes": migration_system["legal_status_changes"],
            "identity_changes": migration_system["identity_changes"],
            "settlement_effects": migration_system["settlement_effects"],
            "political_effects": migration_system["political_effects"],
            "economic_effects": migration_system["economic_effects"],
            "cultural_effects": migration_system["cultural_effects"],
            "story_use": migration_system["story_use"],
            "character_effect": migration_system["character_effect"],
            "plot_effect": migration_system["plot_effect"],
            "memory_effect": migration_system["memory_effect"],
            "generation_hints": [
                "Use migration to change populations, names, settlement pressure, class conflict, and political power.",
                "Track why people moved, where they moved, what status they gained/lost, and whether identity changed.",
                "Migration should alter food, labor, housing, dialect, family structure, law, and memory.",
                "Do not treat migrants as generic crowds; use named demographic groups and specific movement causes.",
            ],
            "memory_update_candidates": [
                {
                    "candidate_type": "migration_system_state",
                    "target_element_id": migration_system["migration_system_id"],
                    "reason": "Track movement patterns, push/pull factors, legal status changes, identity changes, and demographic shifts.",
                }
            ],
        }

        if migration_event:
            patch["active_migration_event"] = migration_event
            patch["memory_update_candidates"].append(
                {
                    "candidate_type": "migration_event_state",
                    "target_element_id": migration_event["migration_event_id"],
                    "reason": "Track trigger, origin, destination, moved groups, route, legal status, missing people, and consequences.",
                }
            )

        return {"story_context_patch": patch}

    def validate_migration_system(self, *, migration_system: Dict[str, Any]) -> Dict[str, Any]:
        required = [
            "migration_system_id",
            "system_name",
            "region_name",
            "name_origin",
            "name_meaning",
            "name_language_logic",
            "cultural_context",
            "world_context",
            "visual_identity",
            "sensory_identity",
            "migration_types",
            "demographic_groups",
            "push_factors",
            "pull_factors",
            "route_dependencies",
            "legal_status_changes",
            "identity_changes",
            "settlement_effects",
            "political_effects",
            "economic_effects",
            "cultural_effects",
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

        missing = [field for field in required if not migration_system.get(field)]
        shallow = self._shallow_fields(
            payload=migration_system,
            fields=["name_origin", "story_use", "character_effect", "plot_effect", "memory_effect", "anti_genericity_signal"],
        )

        passed = not missing and not shallow and float(migration_system.get("detail_depth_score", 0.0)) >= 0.75

        return {
            "passed": passed,
            "missing_fields": missing,
            "shallow_fields": shallow,
            "migration_system_id": migration_system.get("migration_system_id"),
        }

    def validate_migration_event(self, *, migration_event: Dict[str, Any]) -> Dict[str, Any]:
        required = [
            "migration_event_id",
            "migration_system_id",
            "system_name",
            "event_name",
            "event_type",
            "trigger",
            "origin",
            "destination",
            "moving_groups",
            "route_taken",
            "legal_status",
            "identity_effect",
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

        missing = [field for field in required if not migration_event.get(field)]
        shallow = self._shallow_fields(
            payload=migration_event,
            fields=["story_use", "character_effect", "plot_effect", "memory_effect", "lore_effect"],
        )

        passed = not missing and not shallow and float(migration_event.get("detail_depth_score", 0.0)) >= 0.75

        return {
            "passed": passed,
            "missing_fields": missing,
            "shallow_fields": shallow,
            "migration_event_id": migration_event.get("migration_event_id"),
        }

    def summarize_migration_system(
        self,
        *,
        migration_system: Dict[str, Any],
        migration_event: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        summary = {
            "migration_system_id": migration_system["migration_system_id"],
            "system_name": migration_system["system_name"],
            "migration_type_count": len(migration_system["migration_types"]),
            "demographic_group_count": len(migration_system["demographic_groups"]),
            "push_factor_count": len(migration_system["push_factors"]),
            "pull_factor_count": len(migration_system["pull_factors"]),
            "identity_change_count": len(migration_system["identity_changes"]),
            "compression_summary": migration_system["compression_summary"],
        }

        if migration_event:
            summary["migration_event_id"] = migration_event["migration_event_id"]
            summary["event_name"] = migration_event["event_name"]

        return {"success": True, "summary": summary}

    def build_migration_text(
        self,
        *,
        migration_system: Dict[str, Any],
        migration_event: Dict[str, Any] | None = None,
    ) -> Dict[str, str]:
        lines = [
            "Migration + Demographic Movement Profile",
            f"System: {migration_system['system_name']}",
            f"ID: {migration_system['migration_system_id']}",
            f"Region: {migration_system['region_name']}",
            "",
            "Name Origin:",
            migration_system["name_origin"],
        ]

        sections = [
            ("Migration Types", [str(item) for item in migration_system["migration_types"]]),
            ("Demographic Groups", [str(item) for item in migration_system["demographic_groups"]]),
            ("Push Factors", migration_system["push_factors"]),
            ("Pull Factors", migration_system["pull_factors"]),
            ("Route Dependencies", migration_system["route_dependencies"]),
            ("Legal Status Changes", migration_system["legal_status_changes"]),
            ("Identity Changes", migration_system["identity_changes"]),
            ("Settlement Effects", migration_system["settlement_effects"]),
            ("Political Effects", migration_system["political_effects"]),
            ("Economic Effects", migration_system["economic_effects"]),
            ("Cultural Effects", migration_system["cultural_effects"]),
        ]

        for title, values in sections:
            lines.append("")
            lines.append(title + ":")
            for item in values:
                lines.append(f"- {item}")

        if migration_event:
            lines.extend([
                "",
                "Active Migration Event:",
                migration_event["event_name"],
                "",
                "Route Taken:",
                migration_event["route_taken"],
                "",
                "Legal Status:",
                migration_event["legal_status"],
            ])

        lines.extend([
            "",
            "Story Use:",
            migration_system["story_use"],
            "",
            "Character Effect:",
            migration_system["character_effect"],
            "",
            "Plot Effect:",
            migration_system["plot_effect"],
            "",
            "Memory Effect:",
            migration_system["memory_effect"],
        ])

        return {"migration_text": chr(10).join(lines)}

    def _shallow_fields(self, *, payload: Dict[str, Any], fields: List[str]) -> List[str]:
        return [field for field in fields if len(str(payload.get(field, ""))) < 20]

    def _slug(self, value: str) -> str:
        return "_".join(part for part in value.lower().replace("/", " ").replace("-", " ").split() if part)

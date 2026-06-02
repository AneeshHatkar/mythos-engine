from __future__ import annotations

from typing import Any, Dict, List


class CivilizationLifeEngine:
    def build_civilization_life_profile(
        self,
        *,
        source_id: str,
        political_unit: Dict[str, Any] | None = None,
        settlement: Dict[str, Any] | None = None,
        population_profile: Dict[str, Any] | None = None,
        life_seed: Dict[str, Any] | None = None,
        story_context: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        political_unit = political_unit or {}
        settlement = settlement or {}
        population_profile = population_profile or {}
        life_seed = life_seed or {}
        story_context = story_context or {}

        civilization_name = life_seed.get(
            "civilization_name",
            political_unit.get("unique_name")
            or settlement.get("unique_name")
            or story_context.get("civilization_name", "The Bellroad Civilization"),
        )
        region_name = life_seed.get(
            "region_name",
            settlement.get("region_name")
            or political_unit.get("region_name")
            or population_profile.get("region_name")
            or story_context.get("region_name", "Saltroot Forest"),
        )

        profile = {
            "civilization_life_profile_id": f"civilization_life_{source_id}_{self._slug(civilization_name)}",
            "source_id": source_id,
            "civilization_name": civilization_name,
            "region_name": region_name,
            "political_unit_id": political_unit.get("political_unit_id"),
            "settlement_id": settlement.get("settlement_id"),
            "population_diversity_profile_id": population_profile.get("population_diversity_profile_id"),
            "name_origin": life_seed.get(
                "name_origin",
                f"{civilization_name} daily life formed around road law, witness bells, fog survival, archive memory, "
                f"medicine scarcity, and public naming rituals.",
            ),
            "name_meaning": life_seed.get(
                "name_meaning",
                "a civilization where ordinary life is organized around roads, names, bells, and remembered obligations",
            ),
            "name_language_logic": life_seed.get(
                "name_language_logic",
                "civilization-life labels combine political identity with the routine or duty that organizes social behavior",
            ),
            "cultural_context": life_seed.get(
                "cultural_context",
                settlement.get("cultural_context", political_unit.get("cultural_context", "bell-road civic culture")),
            ),
            "world_context": region_name,
            "visual_identity": life_seed.get(
                "visual_identity",
                "foglamp queues, road-cloth uniforms, salt tea stalls, archive ledgers, bell-thread bracelets, and market oath boards",
            ),
            "sensory_identity": life_seed.get(
                "sensory_identity",
                "salt tea steam, wet road-stone, bell-metal vibration, animal pens, inked bark, lamp oil, and crowd whispers",
            ),
            "daily_routines": life_seed.get("daily_routines", [
                {
                    "group": "road families",
                    "morning": "check foglamps, road bells, animal tracks, and traveler lists",
                    "midday": "guide caravans, repair lamps, testify in minor route disputes",
                    "evening": "share salt tea, update oral route memory, teach children weather names",
                },
                {
                    "group": "archive families",
                    "morning": "dry saltbark records and approve public name petitions",
                    "midday": "hear disputes, certify maps, restrict forbidden ledgers",
                    "evening": "host private record dinners with political allies",
                },
                {
                    "group": "market families",
                    "morning": "open road stalls after bell inspection",
                    "midday": "trade medicine, maps, food, tools, and gossip",
                    "evening": "hide accounts from toll clerks and smugglers",
                },
                {
                    "group": "no-bell children",
                    "morning": "carry messages through alleys and roof paths",
                    "midday": "work unofficial errands near markets",
                    "evening": "sleep in shared rooms and listen for restored-name rumors",
                },
            ]),
            "work_and_labor_system": life_seed.get("work_and_labor_system", [
                "road work is honorable but dangerous and underpaid",
                "archive labor is prestigious because it controls names and legal memory",
                "healer work depends on scarce flora harvests and temple licensing",
                "market work blends legal trade, rumor exchange, and quiet smuggling",
                "children without public names are pushed into invisible errands",
            ]),
            "education_and_apprenticeship": life_seed.get("education_and_apprenticeship", [
                "children learn weather nicknames before formal letters",
                "road families teach route songs as survival and legal memory",
                "archive families apprentice in ink, map seals, and public-name law",
                "temples teach bell interpretation and funeral etiquette",
                "poor children learn practical shortcuts but are denied official certification",
            ]),
            "family_and_household_customs": life_seed.get("family_and_household_customs", [
                "public names are celebrated with salt tea and bell-thread bracelets",
                "families keep route-cloth bundles for migration or exile",
                "dead relatives are remembered by road names more than birth dates",
                "adoption can transfer road-memory obligations",
                "forbidden names are whispered only during storms or mourning rites",
            ]),
            "civic_rituals": life_seed.get("civic_rituals", [
                {
                    "ritual": "public name hearing",
                    "purpose": "grant legal identity, inheritance rights, and civic recognition",
                    "story_pressure": "perfect setting for erased-family revelation or political denial",
                },
                {
                    "ritual": "road bell inspection",
                    "purpose": "certify safe travel and public trust before market opening",
                    "story_pressure": "a false bell can expose corruption or murder",
                },
                {
                    "ritual": "salt tea mourning",
                    "purpose": "turn private grief into community memory",
                    "story_pressure": "poison, false testimony, or hidden names can emerge",
                },
            ]),
            "leisure_and_entertainment": life_seed.get("leisure_and_entertainment", [
                "road-song competitions where missing verses hint at erased history",
                "bell-shadow puppet plays for children",
                "market dice games using carved route stones",
                "foglamp festivals with forbidden-name dares",
                "cooking circles where gossip moves faster than officials",
            ]),
            "food_and_public_meals": life_seed.get("food_and_public_meals", [
                "salt tea offered to travelers before questions",
                "ash grain flatbread for road workers",
                "fog moss broth for sickness and cold mornings",
                "funeral tea brewed with controlled medicinal petals",
                "market stew stretched thin during blocked-road shortages",
            ]),
            "clothing_and_status_markers": life_seed.get("clothing_and_status_markers", [
                "bell-thread bracelets mark public name status",
                "road-cloth patches identify guide families and route rights",
                "archive families wear dry white sleeves to signal record purity",
                "exiles cut bracelet knots but keep hidden name cords",
                "children without names wear unmarked cloth that adults pretend not to notice",
            ]),
            "crime_and_informal_power": life_seed.get("crime_and_informal_power", [
                "map fraud",
                "fake route bells",
                "forbidden-name blackmail",
                "medicine hoarding",
                "smuggling through underpaths",
                "archive record tampering",
            ]),
            "public_services": life_seed.get("public_services", [
                "foglamp maintenance crews",
                "road warden patrols",
                "public name registry",
                "witness court schedule",
                "temple funeral kitchens",
                "market water cistern inspection",
            ]),
            "social_mobility_paths": life_seed.get("social_mobility_paths", [
                "poor guide becomes certified road witness after saving travelers",
                "no-bell child gains public name through court risk",
                "merchant family buys archive marriage access",
                "exile regains status by revealing hidden route truth",
                "healer gains temple license during disaster",
            ]),
            "social_failure_paths": life_seed.get("social_failure_paths", [
                "false testimony causes family exile",
                "failed guide loses route rights",
                "archive scandal removes public name authority",
                "smuggler debt traps market families",
                "forbidden-name accusation blocks marriage or inheritance",
            ]),
            "gossip_and_information_flow": life_seed.get("gossip_and_information_flow", [
                "tea stalls spread rumors before courts can deny them",
                "children carry unofficial truth through roof paths",
                "archive clerks leak hints through missing ledger pages",
                "funeral kitchens hear grief-confessions",
                "market musicians encode scandals into road songs",
            ]),
            "story_use": (
                "Turns civilization into lived systems: daily work, naming, education, meals, clothing, leisure, crime, "
                "rituals, services, social mobility, and gossip that produce story pressure."
            ),
            "character_effect": (
                "Characters become shaped by routine, work, class, education, food, clothing, public-name status, family custom, "
                "crime exposure, and civic rituals."
            ),
            "plot_effect": (
                "Daily life can trigger public hearings, gossip trails, shortages, apprenticeship conflicts, forged records, "
                "identity restoration, social collapse, or quiet acts of rebellion."
            ),
            "memory_effect": (
                "World memory must track routines disrupted, public services damaged, social mobility changes, gossip shifts, "
                "food shortages, public-name status, crime exposure, and ritual outcomes."
            ),
            "anti_genericity_signal": (
                "Civilization life includes specific routines, labor, education, family customs, civic rituals, leisure, food, "
                "clothing, crime, public services, mobility paths, gossip, and memory hooks."
            ),
            "detail_depth_score": 0.94,
            "validation_status": "validated",
            "provenance": {
                "generated_by_engine": "CivilizationLifeEngine",
                "origin_type": "derived_from_world_social_context",
                "source_id": source_id,
                "political_unit_id": political_unit.get("political_unit_id"),
                "settlement_id": settlement.get("settlement_id"),
                "population_diversity_profile_id": population_profile.get("population_diversity_profile_id"),
                "seed_keys": sorted(life_seed.keys()),
                "story_context_keys": sorted(story_context.keys()),
            },
            "compression_summary": (
                f"{civilization_name} life: routines, labor, education, family, rituals, leisure, food, clothing, "
                f"crime, services, mobility, gossip, and memory hooks."
            ),
        }

        return {"civilization_life_profile": profile}

    def build_civic_life_event(
        self,
        *,
        source_id: str,
        civilization_life_profile: Dict[str, Any],
        event_seed: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        event_seed = event_seed or {}

        event_name = event_seed.get("event_name", "Public Name Hearing Disruption")

        event = {
            "civic_life_event_id": f"civic_life_event_{source_id}_{self._slug(event_name)}",
            "source_id": source_id,
            "civilization_life_profile_id": civilization_life_profile["civilization_life_profile_id"],
            "civilization_name": civilization_life_profile["civilization_name"],
            "event_name": event_name,
            "event_type": event_seed.get("event_type", "daily_life_ritual_disruption"),
            "trigger": event_seed.get(
                "trigger",
                "a no-bell child presents a hidden name cord during a public name hearing",
            ),
            "affected_routines": event_seed.get("affected_routines", [
                "archive name registry",
                "market opening",
                "road bell inspection",
                "temple witness schedule",
            ]),
            "affected_groups": event_seed.get("affected_groups", [
                "no-bell children",
                "archive families",
                "road families",
                "market crowds",
                "temple witnesses",
            ]),
            "public_reaction": event_seed.get(
                "public_reaction",
                "market crowds stop trading and begin repeating the hidden name before wardens can silence them",
            ),
            "private_reaction": event_seed.get(
                "private_reaction",
                "archive families panic because the name matches a forbidden ledger line",
            ),
            "story_use": (
                "Turns ordinary civic life into a plot event by disrupting routine, ritual, law, food, work, and public identity."
            ),
            "character_effect": (
                "Characters reveal whether they protect order, truth, children, family reputation, profit, or personal safety."
            ),
            "plot_effect": (
                "Can trigger riot, trial delay, identity restoration, market shutdown, forbidden-record search, or public confession."
            ),
            "memory_effect": (
                "World memory must track disrupted routines, affected groups, public reaction, restored names, gossip spread, and authority loss."
            ),
            "lore_effect": (
                "Daily ritual becomes mythic pressure when hidden names, bells, and civic memory collide in public."
            ),
            "anti_genericity_signal": (
                "Event ties daily life, naming law, market rhythm, public ritual, class, gossip, and memory into one conflict."
            ),
            "detail_depth_score": 0.9,
            "validation_status": "validated",
            "provenance": {
                "generated_by_engine": "CivilizationLifeEngine",
                "origin_type": "derived_from_civilization_life_profile",
                "source_id": source_id,
                "profile_id": civilization_life_profile["civilization_life_profile_id"],
                "seed_keys": sorted(event_seed.keys()),
            },
            "compression_summary": (
                f"{event_name}: trigger, affected routines, affected groups, public/private reaction, and memory consequences."
            ),
        }

        return {"civic_life_event": event}

    def build_story_context_patch(
        self,
        *,
        civilization_life_profile: Dict[str, Any],
        civic_life_event: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        patch = {
            "civilization_life_profile_id": civilization_life_profile["civilization_life_profile_id"],
            "civilization_name": civilization_life_profile["civilization_name"],
            "daily_routines": civilization_life_profile["daily_routines"],
            "work_and_labor_system": civilization_life_profile["work_and_labor_system"],
            "education_and_apprenticeship": civilization_life_profile["education_and_apprenticeship"],
            "family_and_household_customs": civilization_life_profile["family_and_household_customs"],
            "civic_rituals": civilization_life_profile["civic_rituals"],
            "leisure_and_entertainment": civilization_life_profile["leisure_and_entertainment"],
            "food_and_public_meals": civilization_life_profile["food_and_public_meals"],
            "clothing_and_status_markers": civilization_life_profile["clothing_and_status_markers"],
            "crime_and_informal_power": civilization_life_profile["crime_and_informal_power"],
            "public_services": civilization_life_profile["public_services"],
            "social_mobility_paths": civilization_life_profile["social_mobility_paths"],
            "social_failure_paths": civilization_life_profile["social_failure_paths"],
            "gossip_and_information_flow": civilization_life_profile["gossip_and_information_flow"],
            "story_use": civilization_life_profile["story_use"],
            "character_effect": civilization_life_profile["character_effect"],
            "plot_effect": civilization_life_profile["plot_effect"],
            "memory_effect": civilization_life_profile["memory_effect"],
            "generation_hints": [
                "Use daily life as plot pressure, not background filler.",
                "Let food, clothing, work, education, rituals, crime, and gossip shape characters and scenes.",
                "Ordinary routines should change after disasters, political conflict, shortages, or secret reveals.",
                "Track disruptions to services, food, social status, gossip, identity, and ritual outcomes in memory.",
            ],
            "memory_update_candidates": [
                {
                    "candidate_type": "civilization_life_state",
                    "target_element_id": civilization_life_profile["civilization_life_profile_id"],
                    "reason": "Track routine disruptions, civic services, social mobility, food shortages, gossip, and ritual outcomes.",
                }
            ],
        }

        if civic_life_event:
            patch["active_civic_life_event"] = civic_life_event
            patch["memory_update_candidates"].append(
                {
                    "candidate_type": "civic_life_event_state",
                    "target_element_id": civic_life_event["civic_life_event_id"],
                    "reason": "Track trigger, affected routines, affected groups, public/private reaction, and authority changes.",
                }
            )

        return {"story_context_patch": patch}

    def validate_civilization_life_profile(self, *, civilization_life_profile: Dict[str, Any]) -> Dict[str, Any]:
        required = [
            "civilization_life_profile_id",
            "civilization_name",
            "region_name",
            "name_origin",
            "name_meaning",
            "name_language_logic",
            "cultural_context",
            "world_context",
            "visual_identity",
            "sensory_identity",
            "daily_routines",
            "work_and_labor_system",
            "education_and_apprenticeship",
            "family_and_household_customs",
            "civic_rituals",
            "leisure_and_entertainment",
            "food_and_public_meals",
            "clothing_and_status_markers",
            "crime_and_informal_power",
            "public_services",
            "social_mobility_paths",
            "social_failure_paths",
            "gossip_and_information_flow",
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

        missing = [field for field in required if not civilization_life_profile.get(field)]
        shallow = self._shallow_fields(
            payload=civilization_life_profile,
            fields=["name_origin", "story_use", "character_effect", "plot_effect", "memory_effect", "anti_genericity_signal"],
        )

        passed = (
            not missing
            and not shallow
            and float(civilization_life_profile.get("detail_depth_score", 0.0)) >= 0.75
        )

        return {
            "passed": passed,
            "missing_fields": missing,
            "shallow_fields": shallow,
            "civilization_life_profile_id": civilization_life_profile.get("civilization_life_profile_id"),
        }

    def validate_civic_life_event(self, *, civic_life_event: Dict[str, Any]) -> Dict[str, Any]:
        required = [
            "civic_life_event_id",
            "civilization_life_profile_id",
            "civilization_name",
            "event_name",
            "event_type",
            "trigger",
            "affected_routines",
            "affected_groups",
            "public_reaction",
            "private_reaction",
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

        missing = [field for field in required if not civic_life_event.get(field)]
        shallow = self._shallow_fields(
            payload=civic_life_event,
            fields=["story_use", "character_effect", "plot_effect", "memory_effect", "lore_effect"],
        )

        passed = (
            not missing
            and not shallow
            and float(civic_life_event.get("detail_depth_score", 0.0)) >= 0.75
        )

        return {
            "passed": passed,
            "missing_fields": missing,
            "shallow_fields": shallow,
            "civic_life_event_id": civic_life_event.get("civic_life_event_id"),
        }

    def summarize_civilization_life(
        self,
        *,
        civilization_life_profile: Dict[str, Any],
        civic_life_event: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        summary = {
            "civilization_life_profile_id": civilization_life_profile["civilization_life_profile_id"],
            "civilization_name": civilization_life_profile["civilization_name"],
            "daily_routine_count": len(civilization_life_profile["daily_routines"]),
            "civic_ritual_count": len(civilization_life_profile["civic_rituals"]),
            "food_public_meal_count": len(civilization_life_profile["food_and_public_meals"]),
            "crime_pattern_count": len(civilization_life_profile["crime_and_informal_power"]),
            "public_service_count": len(civilization_life_profile["public_services"]),
            "compression_summary": civilization_life_profile["compression_summary"],
        }

        if civic_life_event:
            summary["civic_life_event_id"] = civic_life_event["civic_life_event_id"]
            summary["civic_life_event_name"] = civic_life_event["event_name"]

        return {"success": True, "summary": summary}

    def build_civilization_life_text(
        self,
        *,
        civilization_life_profile: Dict[str, Any],
        civic_life_event: Dict[str, Any] | None = None,
    ) -> Dict[str, str]:
        lines = [
            "Civilization Life Profile",
            f"Civilization: {civilization_life_profile['civilization_name']}",
            f"ID: {civilization_life_profile['civilization_life_profile_id']}",
            f"Region: {civilization_life_profile['region_name']}",
            "",
            "Name Origin:",
            civilization_life_profile["name_origin"],
        ]

        sections = [
            ("Daily Routines", [str(item) for item in civilization_life_profile["daily_routines"]]),
            ("Work and Labor System", civilization_life_profile["work_and_labor_system"]),
            ("Education and Apprenticeship", civilization_life_profile["education_and_apprenticeship"]),
            ("Family and Household Customs", civilization_life_profile["family_and_household_customs"]),
            ("Civic Rituals", [str(item) for item in civilization_life_profile["civic_rituals"]]),
            ("Leisure and Entertainment", civilization_life_profile["leisure_and_entertainment"]),
            ("Food and Public Meals", civilization_life_profile["food_and_public_meals"]),
            ("Clothing and Status Markers", civilization_life_profile["clothing_and_status_markers"]),
            ("Crime and Informal Power", civilization_life_profile["crime_and_informal_power"]),
            ("Public Services", civilization_life_profile["public_services"]),
            ("Social Mobility Paths", civilization_life_profile["social_mobility_paths"]),
            ("Social Failure Paths", civilization_life_profile["social_failure_paths"]),
            ("Gossip and Information Flow", civilization_life_profile["gossip_and_information_flow"]),
        ]

        for title, values in sections:
            lines.append("")
            lines.append(title + ":")
            for item in values:
                lines.append(f"- {item}")

        if civic_life_event:
            lines.extend([
                "",
                "Active Civic Life Event:",
                civic_life_event["event_name"],
                "",
                "Trigger:",
                civic_life_event["trigger"],
            ])

        lines.extend([
            "",
            "Story Use:",
            civilization_life_profile["story_use"],
            "",
            "Character Effect:",
            civilization_life_profile["character_effect"],
            "",
            "Plot Effect:",
            civilization_life_profile["plot_effect"],
            "",
            "Memory Effect:",
            civilization_life_profile["memory_effect"],
        ])

        return {"civilization_life_text": chr(10).join(lines)}

    def _shallow_fields(self, *, payload: Dict[str, Any], fields: List[str]) -> List[str]:
        return [field for field in fields if len(str(payload.get(field, ""))) < 20]

    def _slug(self, value: str) -> str:
        return "_".join(part for part in value.lower().replace("/", " ").replace("-", " ").split() if part)

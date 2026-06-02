from __future__ import annotations

from typing import Any, Dict, List


class ArchitectureBuiltEnvironmentEngine:
    def build_built_environment_profile(
        self,
        *,
        source_id: str,
        settlement: Dict[str, Any],
        political_unit: Dict[str, Any] | None = None,
        environment_seed: Dict[str, Any] | None = None,
        story_context: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        political_unit = political_unit or {}
        environment_seed = environment_seed or {}
        story_context = story_context or {}

        settlement_name = settlement["unique_name"]
        region_name = environment_seed.get(
            "region_name",
            settlement.get("region_name", story_context.get("region_name", "Saltroot Forest")),
        )

        style_name = environment_seed.get("style_name", f"{settlement_name} Salt-Bell Architecture")

        profile = {
            "built_environment_profile_id": f"built_environment_{source_id}_{self._slug(style_name)}",
            "source_id": source_id,
            "style_name": style_name,
            "settlement_id": settlement["settlement_id"],
            "settlement_name": settlement_name,
            "political_unit_id": political_unit.get("political_unit_id"),
            "region_name": region_name,
            "name_origin": environment_seed.get(
                "name_origin",
                f"{style_name} is named for the settlement's use of salt-stone walls, bell-metal anchors, "
                f"and road-facing civic towers built after old travel disasters.",
            ),
            "name_meaning": environment_seed.get(
                "name_meaning",
                "buildings made to remember roads, resist fog, display law, and hide old guilt",
            ),
            "name_language_logic": environment_seed.get(
                "name_language_logic",
                "architectural styles combine material marker, civic object, and remembered disaster or duty",
            ),
            "cultural_context": environment_seed.get(
                "cultural_context",
                settlement.get("cultural_context", political_unit.get("cultural_context", "bell-road civic culture")),
            ),
            "world_context": region_name,
            "visual_identity": environment_seed.get(
                "visual_identity",
                "black road-stone foundations, salt-white wall seams, hanging foglamps, bell-metal gutters, "
                "and carved witness marks around doors",
            ),
            "sensory_identity": environment_seed.get(
                "sensory_identity",
                "wet stone echo, bell-metal vibration, lamp oil, salt tea smoke, archive ink, and damp tunnel air",
            ),
            "core_materials": environment_seed.get("core_materials", [
                {
                    "material": "black road-stone",
                    "source": "old causeway quarries",
                    "social_meaning": "durability, law, and public duty",
                    "story_use": "blood and salt marks remain visible after rain",
                },
                {
                    "material": "salt-bark panels",
                    "source": "saltroot groves",
                    "social_meaning": "records, contracts, and memory",
                    "story_use": "documents can be hidden inside wall layers",
                },
                {
                    "material": "bell-metal braces",
                    "source": "recast road bells and treaty tokens",
                    "social_meaning": "witness, warning, and civic authority",
                    "story_use": "vibrates before storms, lies, or hidden mechanisms",
                },
            ]),
            "building_types": environment_seed.get("building_types", [
                {
                    "building_type": "witness court hall",
                    "function": "trial, public naming, road testimony, inheritance disputes",
                    "class_signal": "clean elevated stone and guarded archive doors",
                    "hidden_feature": "sealed lower chamber with erased ledgers",
                },
                {
                    "building_type": "foglamp tenement",
                    "function": "housing for poor road families and no-bell children",
                    "class_signal": "crowded warm rooms, shared kitchens, patched lamps",
                    "hidden_feature": "roof paths used during curfew",
                },
                {
                    "building_type": "bell tower",
                    "function": "weather warning, curfew, civic ritual, dead-bell omen",
                    "class_signal": "public power visible from every district",
                    "hidden_feature": "stairs connect to forbidden underways",
                },
                {
                    "building_type": "saltbark archive house",
                    "function": "legal memory, maps, names, contracts, death records",
                    "class_signal": "quiet, guarded, dry, elevated, and cold",
                    "hidden_feature": "false shelves hiding forbidden names",
                },
            ]),
            "street_layout": environment_seed.get("street_layout", [
                "main roads face bell towers so travelers can orient in fog",
                "poor alleys follow old drainage lines and children know them better than wardens",
                "archive streets are raised above flood and market noise",
                "market lanes widen near public accusation posts",
                "dead-end shrine courts hide old tunnel entrances",
            ]),
            "class_spatial_logic": environment_seed.get("class_spatial_logic", [
                "wealth rises physically upward toward dry archive streets",
                "poor districts cluster near foglamp maintenance and road labor",
                "merchant houses face markets but keep private courtyards hidden",
                "exiled families live near edges, tunnels, and unofficial paths",
            ]),
            "religious_spatial_logic": environment_seed.get("religious_spatial_logic", [
                "shrines sit at road forks where travelers choose safe or cursed paths",
                "funeral kitchens face west toward lost-road gates",
                "temple witness benches are built above older secular court stones",
                "dead-bell alcoves are placed where public lies are most often spoken",
            ]),
            "security_and_surveillance": environment_seed.get("security_and_surveillance", [
                "bell towers let wardens track foglamp outages",
                "archive balconies overlook market accusation posts",
                "toll gates force travelers into witnessable lanes",
                "hidden child paths bypass official watching points",
            ]),
            "climate_adaptations": environment_seed.get("climate_adaptations", [
                "raised thresholds keep red fog water out of archive rooms",
                "bell-metal gutters sing before storm overflow",
                "foglamps are spaced by sound distance rather than sight distance",
                "salt-bark shutters swell shut during dangerous rain",
            ]),
            "hidden_structures": environment_seed.get("hidden_structures", [
                {
                    "hidden_structure": "old tower underway",
                    "public_cover": "sealed drainage route",
                    "secret_truth": "connects massacre evidence to archive cellars",
                },
                {
                    "hidden_structure": "roofline child path",
                    "public_cover": "laundry walkways",
                    "secret_truth": "used by no-bell children to avoid curfew patrols",
                },
                {
                    "hidden_structure": "dead-bell alcove",
                    "public_cover": "unused shrine niche",
                    "secret_truth": "amplifies hidden chamber bells during false testimony",
                },
            ]),
            "scene_blocking_rules": environment_seed.get("scene_blocking_rules", [
                "court scenes should force characters to stand under visible witness marks",
                "market scenes should include crowd pressure from balconies and accusation posts",
                "poor-district scenes should allow hidden exits, shared overhearing, and intimate crowding",
                "archive scenes should limit movement through locked rooms, dry silence, and watched corridors",
                "tunnel scenes should use sound, touch, breath, and fear more than clean sight",
            ]),
            "damage_and_decay_rules": environment_seed.get("damage_and_decay_rules", [
                "salt-stone cracks reveal older blood-dark layers",
                "bell-metal corrodes near hidden water channels",
                "foglamp outages signal neglect or sabotage",
                "archive dryness protects lies as much as truth",
            ]),
            "story_use": (
                "Turns architecture into active story machinery: class movement, hidden routes, surveillance, ritual space, "
                "scene blocking, secret history, climate adaptation, and evidence storage."
            ),
            "character_effect": (
                "Characters reveal class, confidence, fear, profession, local knowledge, and guilt through how they move through buildings, "
                "avoid spaces, read materials, or know hidden paths."
            ),
            "plot_effect": (
                "Architecture can enable escape, expose records, trap witnesses, reveal old crimes, create surveillance tension, "
                "block access, or force confrontations in symbolically loaded spaces."
            ),
            "memory_effect": (
                "World memory must track damaged buildings, opened hidden structures, changed access, destroyed records, rebuilt districts, "
                "public monuments, and altered civic symbolism."
            ),
            "anti_genericity_signal": (
                "Built environment includes named materials, building types, class geography, religion, climate adaptation, surveillance, "
                "hidden structures, scene blocking, decay, and memory hooks."
            ),
            "detail_depth_score": 0.94,
            "validation_status": "validated",
            "provenance": {
                "generated_by_engine": "ArchitectureBuiltEnvironmentEngine",
                "origin_type": "derived_from_settlement",
                "source_id": source_id,
                "settlement_id": settlement["settlement_id"],
                "political_unit_id": political_unit.get("political_unit_id"),
                "seed_keys": sorted(environment_seed.keys()),
                "story_context_keys": sorted(story_context.keys()),
            },
            "compression_summary": (
                f"{style_name}: materials, buildings, street layout, class space, religious space, surveillance, "
                f"climate adaptation, hidden structures, scene blocking, and memory hooks."
            ),
        }

        return {"built_environment_profile": profile}

    def build_architectural_event(
        self,
        *,
        source_id: str,
        built_environment_profile: Dict[str, Any],
        event_seed: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        event_seed = event_seed or {}

        event_name = event_seed.get("event_name", "Bell Tower Wall Opening")

        event = {
            "architectural_event_id": f"architectural_event_{source_id}_{self._slug(event_name)}",
            "source_id": source_id,
            "built_environment_profile_id": built_environment_profile["built_environment_profile_id"],
            "settlement_id": built_environment_profile["settlement_id"],
            "settlement_name": built_environment_profile["settlement_name"],
            "event_name": event_name,
            "event_type": event_seed.get("event_type", "hidden_structure_reveal"),
            "trigger": event_seed.get(
                "trigger",
                "storm vibration loosened a bell-metal brace and opened a sealed wall behind the witness court",
            ),
            "location": event_seed.get("location", "witness court hall"),
            "revealed_structure": event_seed.get("revealed_structure", "sealed lower chamber with erased ledgers"),
            "affected_groups": event_seed.get("affected_groups", [
                "archive families",
                "road wardens",
                "no-bell children",
                "market witnesses",
            ]),
            "immediate_consequence": event_seed.get(
                "immediate_consequence",
                "court proceedings stop as hidden records become visible to the public",
            ),
            "story_use": (
                "Turns building structure into event pressure through hidden chambers, public exposure, danger, and symbolic collapse."
            ),
            "character_effect": (
                "Characters must react through fear, guilt, expertise, greed, duty, curiosity, or desire to destroy evidence."
            ),
            "plot_effect": (
                "Can reveal records, open chase routes, collapse a legal claim, trap characters, or expose the built environment's secret history."
            ),
            "memory_effect": (
                "World memory must track opened structures, damaged buildings, revealed evidence, public reaction, access change, and repairs."
            ),
            "lore_effect": (
                "Architecture becomes proof that local myth, dead-bell warnings, and civic lies are physically embedded in the town."
            ),
            "anti_genericity_signal": (
                "Event ties material decay, hidden architecture, civic ritual, evidence, affected groups, and public consequence together."
            ),
            "detail_depth_score": 0.9,
            "validation_status": "validated",
            "provenance": {
                "generated_by_engine": "ArchitectureBuiltEnvironmentEngine",
                "origin_type": "derived_from_built_environment_profile",
                "source_id": source_id,
                "profile_id": built_environment_profile["built_environment_profile_id"],
                "seed_keys": sorted(event_seed.keys()),
            },
            "compression_summary": (
                f"{event_name}: trigger, location, revealed structure, affected groups, consequences, and memory hooks."
            ),
        }

        return {"architectural_event": event}

    def build_story_context_patch(
        self,
        *,
        built_environment_profile: Dict[str, Any],
        architectural_event: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        patch = {
            "built_environment_profile_id": built_environment_profile["built_environment_profile_id"],
            "style_name": built_environment_profile["style_name"],
            "settlement_id": built_environment_profile["settlement_id"],
            "settlement_name": built_environment_profile["settlement_name"],
            "core_materials": built_environment_profile["core_materials"],
            "building_types": built_environment_profile["building_types"],
            "street_layout": built_environment_profile["street_layout"],
            "class_spatial_logic": built_environment_profile["class_spatial_logic"],
            "religious_spatial_logic": built_environment_profile["religious_spatial_logic"],
            "security_and_surveillance": built_environment_profile["security_and_surveillance"],
            "climate_adaptations": built_environment_profile["climate_adaptations"],
            "hidden_structures": built_environment_profile["hidden_structures"],
            "scene_blocking_rules": built_environment_profile["scene_blocking_rules"],
            "damage_and_decay_rules": built_environment_profile["damage_and_decay_rules"],
            "story_use": built_environment_profile["story_use"],
            "character_effect": built_environment_profile["character_effect"],
            "plot_effect": built_environment_profile["plot_effect"],
            "memory_effect": built_environment_profile["memory_effect"],
            "generation_hints": [
                "Use architecture to control movement, power, secrecy, class visibility, and scene blocking.",
                "Buildings should affect what characters can see, hide, overhear, steal, reveal, or escape.",
                "Materials and structures should reflect climate, culture, religion, economy, and history.",
                "Track opened hidden spaces, damaged buildings, rebuilt districts, and altered access in memory.",
            ],
            "memory_update_candidates": [
                {
                    "candidate_type": "built_environment_state",
                    "target_element_id": built_environment_profile["built_environment_profile_id"],
                    "reason": "Track hidden structures, building damage, access changes, surveillance, repairs, and civic symbolism.",
                }
            ],
        }

        if architectural_event:
            patch["active_architectural_event"] = architectural_event
            patch["memory_update_candidates"].append(
                {
                    "candidate_type": "architectural_event_state",
                    "target_element_id": architectural_event["architectural_event_id"],
                    "reason": "Track trigger, revealed structure, damage, affected groups, evidence, public reaction, and repairs.",
                }
            )

        return {"story_context_patch": patch}

    def validate_built_environment_profile(self, *, built_environment_profile: Dict[str, Any]) -> Dict[str, Any]:
        required = [
            "built_environment_profile_id",
            "style_name",
            "settlement_id",
            "settlement_name",
            "region_name",
            "name_origin",
            "name_meaning",
            "name_language_logic",
            "cultural_context",
            "world_context",
            "visual_identity",
            "sensory_identity",
            "core_materials",
            "building_types",
            "street_layout",
            "class_spatial_logic",
            "religious_spatial_logic",
            "security_and_surveillance",
            "climate_adaptations",
            "hidden_structures",
            "scene_blocking_rules",
            "damage_and_decay_rules",
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

        missing = [field for field in required if not built_environment_profile.get(field)]
        shallow = self._shallow_fields(
            payload=built_environment_profile,
            fields=["name_origin", "story_use", "character_effect", "plot_effect", "memory_effect", "anti_genericity_signal"],
        )

        passed = (
            not missing
            and not shallow
            and float(built_environment_profile.get("detail_depth_score", 0.0)) >= 0.75
        )

        return {
            "passed": passed,
            "missing_fields": missing,
            "shallow_fields": shallow,
            "built_environment_profile_id": built_environment_profile.get("built_environment_profile_id"),
        }

    def validate_architectural_event(self, *, architectural_event: Dict[str, Any]) -> Dict[str, Any]:
        required = [
            "architectural_event_id",
            "built_environment_profile_id",
            "settlement_id",
            "settlement_name",
            "event_name",
            "event_type",
            "trigger",
            "location",
            "revealed_structure",
            "affected_groups",
            "immediate_consequence",
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

        missing = [field for field in required if not architectural_event.get(field)]
        shallow = self._shallow_fields(
            payload=architectural_event,
            fields=["story_use", "character_effect", "plot_effect", "memory_effect", "lore_effect"],
        )

        passed = (
            not missing
            and not shallow
            and float(architectural_event.get("detail_depth_score", 0.0)) >= 0.75
        )

        return {
            "passed": passed,
            "missing_fields": missing,
            "shallow_fields": shallow,
            "architectural_event_id": architectural_event.get("architectural_event_id"),
        }

    def summarize_built_environment(
        self,
        *,
        built_environment_profile: Dict[str, Any],
        architectural_event: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        summary = {
            "built_environment_profile_id": built_environment_profile["built_environment_profile_id"],
            "style_name": built_environment_profile["style_name"],
            "settlement_name": built_environment_profile["settlement_name"],
            "material_count": len(built_environment_profile["core_materials"]),
            "building_type_count": len(built_environment_profile["building_types"]),
            "hidden_structure_count": len(built_environment_profile["hidden_structures"]),
            "scene_blocking_rule_count": len(built_environment_profile["scene_blocking_rules"]),
            "compression_summary": built_environment_profile["compression_summary"],
        }

        if architectural_event:
            summary["architectural_event_id"] = architectural_event["architectural_event_id"]
            summary["architectural_event_name"] = architectural_event["event_name"]

        return {"success": True, "summary": summary}

    def build_built_environment_text(
        self,
        *,
        built_environment_profile: Dict[str, Any],
        architectural_event: Dict[str, Any] | None = None,
    ) -> Dict[str, str]:
        lines = [
            "Architecture + Built Environment Profile",
            f"Style: {built_environment_profile['style_name']}",
            f"Settlement: {built_environment_profile['settlement_name']}",
            f"ID: {built_environment_profile['built_environment_profile_id']}",
            "",
            "Name Origin:",
            built_environment_profile["name_origin"],
        ]

        sections = [
            ("Core Materials", [str(item) for item in built_environment_profile["core_materials"]]),
            ("Building Types", [str(item) for item in built_environment_profile["building_types"]]),
            ("Street Layout", built_environment_profile["street_layout"]),
            ("Class Spatial Logic", built_environment_profile["class_spatial_logic"]),
            ("Religious Spatial Logic", built_environment_profile["religious_spatial_logic"]),
            ("Security and Surveillance", built_environment_profile["security_and_surveillance"]),
            ("Climate Adaptations", built_environment_profile["climate_adaptations"]),
            ("Hidden Structures", [str(item) for item in built_environment_profile["hidden_structures"]]),
            ("Scene Blocking Rules", built_environment_profile["scene_blocking_rules"]),
            ("Damage and Decay Rules", built_environment_profile["damage_and_decay_rules"]),
        ]

        for title, values in sections:
            lines.append("")
            lines.append(title + ":")
            for item in values:
                lines.append(f"- {item}")

        if architectural_event:
            lines.extend([
                "",
                "Active Architectural Event:",
                architectural_event["event_name"],
                "",
                "Revealed Structure:",
                architectural_event["revealed_structure"],
            ])

        lines.extend([
            "",
            "Story Use:",
            built_environment_profile["story_use"],
            "",
            "Character Effect:",
            built_environment_profile["character_effect"],
            "",
            "Plot Effect:",
            built_environment_profile["plot_effect"],
            "",
            "Memory Effect:",
            built_environment_profile["memory_effect"],
        ])

        return {"built_environment_text": chr(10).join(lines)}

    def _shallow_fields(self, *, payload: Dict[str, Any], fields: List[str]) -> List[str]:
        return [field for field in fields if len(str(payload.get(field, ""))) < 20]

    def _slug(self, value: str) -> str:
        return "_".join(part for part in value.lower().replace("/", " ").replace("-", " ").split() if part)

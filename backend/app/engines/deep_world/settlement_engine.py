from __future__ import annotations

from typing import Any, Dict, List


class SettlementEngine:
    def build_settlement(
        self,
        *,
        source_id: str,
        political_unit: Dict[str, Any] | None = None,
        population_profile: Dict[str, Any] | None = None,
        settlement_seed: Dict[str, Any] | None = None,
        story_context: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        political_unit = political_unit or {}
        population_profile = population_profile or {}
        settlement_seed = settlement_seed or {}
        story_context = story_context or {}

        base_name = settlement_seed.get("base_name", "Veyr")
        unique_name = settlement_seed.get("unique_name", f"{base_name} Bellcross")
        settlement_type = settlement_seed.get("settlement_type", "road-market town")
        region_name = settlement_seed.get(
            "region_name",
            political_unit.get("region_name", story_context.get("region_name", "Saltroot Forest")),
        )
        political_name = political_unit.get("unique_name", "unassigned political unit")
        population_name = population_profile.get("profile_name", f"{region_name} population")

        settlement = {
            "settlement_id": f"settlement_{source_id}_{self._slug(unique_name)}",
            "source_id": source_id,
            "unique_name": unique_name,
            "base_name": base_name,
            "settlement_type": settlement_type,
            "region_name": region_name,
            "political_unit_id": political_unit.get("political_unit_id"),
            "political_unit_name": political_name,
            "population_diversity_profile_id": population_profile.get("population_diversity_profile_id"),
            "population_profile_name": population_name,
            "name_origin": settlement_seed.get(
                "name_origin",
                f"{unique_name} is named for the old road crossing where court bells were hung after the first treaty deaths.",
            ),
            "name_meaning": settlement_seed.get("name_meaning", "crossing where bells remember the road"),
            "name_language_logic": settlement_seed.get(
                "name_language_logic",
                "settlement names combine old route roots with local civic objects, disasters, founders, or sacred duties",
            ),
            "cultural_context": settlement_seed.get(
                "cultural_context",
                political_unit.get("cultural_context", "bell-road legal culture"),
            ),
            "world_context": region_name,
            "visual_identity": settlement_seed.get(
                "visual_identity",
                "tiered road-stone streets, black bell towers, salt-bark record houses, and fog-lamps over market arches",
            ),
            "sensory_identity": settlement_seed.get(
                "sensory_identity",
                "wet stone, bell-metal hum, salt tea smoke, animal musk from caravan pens, and inked bark records",
            ),
            "founding_history": settlement_seed.get(
                "founding_history",
                "Founded as a witness stop after travelers died during a fog closure and families demanded public road law.",
            ),
            "public_history": settlement_seed.get(
                "public_history",
                "Locals say the town grew peacefully from a safe crossing guarded by honest bellkeepers.",
            ),
            "secret_history": settlement_seed.get(
                "secret_history",
                "The first bell tower was built over a mass grave from a suppressed border ambush.",
            ),
            "false_history": settlement_seed.get(
                "false_history",
                "Official plaques claim the mass grave was only a plague pit.",
            ),
            "districts": settlement_seed.get("districts", [
                {
                    "district_name": "Nine-Bell Market",
                    "function": "trade, court posting, rumor exchange, and public witness declarations",
                    "conflict": "merchants bribe clerks to alter route taxes",
                },
                {
                    "district_name": "Saltbark Archive Row",
                    "function": "stores maps, contracts, name records, and dead-bell testimony",
                    "conflict": "archive families hide forbidden names",
                },
                {
                    "district_name": "Foglamp Steps",
                    "function": "poor road families, guides, repair workers, and no-bell children live here",
                    "conflict": "often blamed for smuggling and disease",
                },
                {
                    "district_name": "Old Tower Underway",
                    "function": "sealed tunnels beneath the first bell tower",
                    "conflict": "contains hidden evidence of the founding massacre",
                },
            ]),
            "infrastructure": settlement_seed.get("infrastructure", [
                "old road gates",
                "bell towers",
                "foglamp posts",
                "saltbark archive houses",
                "caravan pens",
                "witness court hall",
                "hidden drainage tunnels",
            ]),
            "economy": settlement_seed.get("economy", [
                "road tolls",
                "map certification",
                "saltroot medicine trade",
                "bell-metal craft",
                "caravan lodging",
                "archive fees",
            ]),
            "law_and_order": settlement_seed.get("law_and_order", [
                "public names must be registered before inheritance claims",
                "route disputes require road witness testimony",
                "curfew begins when dead bells ring in fog",
                "forbidden-name speech can trigger arrest in archive districts",
            ]),
            "religion_myth_lore": settlement_seed.get("religion_myth_lore", [
                "locals believe dead bells ring when false history is spoken near the old tower",
                "fog saints are honored at road shrines outside the market gate",
                "children leave salt tea for lost guides during monsoon nights",
            ]),
            "class_layout": settlement_seed.get("class_layout", [
                "archive families occupy raised stone streets",
                "road workers live near foglamp steps",
                "merchants cluster around nine-bell market",
                "exiled name-carriers hide near sealed tunnels",
            ]),
            "food_water_supply": settlement_seed.get("food_water_supply", [
                "rain cisterns under bell towers",
                "saltroot tea houses",
                "fog moss medicine gardens",
                "ash grain brought by caravans",
            ]),
            "security_risks": settlement_seed.get("security_risks", [
                "smugglers use drainage tunnels",
                "fog closures isolate outer districts",
                "archive guards protect records more than people",
                "border agents spy on road families",
            ]),
            "current_tensions": settlement_seed.get("current_tensions", [
                "no-bell children demand public names",
                "archive families suppress tunnel rumors",
                "merchants want curfew laws removed",
                "road wardens fear another fog closure disaster",
            ]),
            "important_locations": settlement_seed.get("important_locations", [
                "First Bell Tower",
                "Saltbark Archive Court",
                "Nine-Bell Market",
                "Foglamp Steps",
                "Old Tower Underway",
            ]),
            "story_use": (
                "Creates a settlement as a living story hub with districts, class layout, economy, law, religion, "
                "secret history, conflict, infrastructure, and scene-ready locations."
            ),
            "character_effect": (
                "Characters from this settlement inherit neighborhood identity, class markers, speech habits, legal duties, "
                "religious fears, local grudges, and memories of hidden places."
            ),
            "plot_effect": (
                "Can drive trials, riots, secret-tunnel reveals, market betrayals, naming conflicts, curfew scenes, "
                "smuggling, historical evidence discovery, or religious panic."
            ),
            "memory_effect": (
                "World memory must track settlement status, district damage, law changes, public/secret history reveals, "
                "renamed places, population shifts, market shortages, and faction control."
            ),
            "anti_genericity_signal": (
                "Settlement includes unique naming, district functions, class layout, economy, infrastructure, law, religion, "
                "public/secret/false history, current tensions, and memory hooks."
            ),
            "detail_depth_score": 0.93,
            "validation_status": "validated",
            "provenance": {
                "generated_by_engine": "SettlementEngine",
                "origin_type": "generated_from_settlement_seed",
                "source_id": source_id,
                "political_unit_id": political_unit.get("political_unit_id"),
                "population_diversity_profile_id": population_profile.get("population_diversity_profile_id"),
                "seed_keys": sorted(settlement_seed.keys()),
                "story_context_keys": sorted(story_context.keys()),
            },
            "compression_summary": (
                f"{unique_name}: {settlement_type} in {region_name}; districts, law, economy, class, religion, "
                f"public/secret history, tensions, and memory hooks."
            ),
        }

        return {"settlement": settlement}

    def build_settlement_conflict(
        self,
        *,
        source_id: str,
        settlement: Dict[str, Any],
        conflict_seed: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        conflict_seed = conflict_seed or {}

        conflict_name = conflict_seed.get("conflict_name", "Old Tower Name Riot")

        conflict = {
            "settlement_conflict_id": f"settlement_conflict_{source_id}_{self._slug(conflict_name)}",
            "source_id": source_id,
            "settlement_id": settlement["settlement_id"],
            "settlement_name": settlement["unique_name"],
            "conflict_name": conflict_name,
            "conflict_type": conflict_seed.get("conflict_type", "public_name_and_secret_history_conflict"),
            "public_issue": conflict_seed.get(
                "public_issue",
                "no-bell children demand legal public names before inheritance season.",
            ),
            "secret_cause": conflict_seed.get(
                "secret_cause",
                "archive families erased their parent names to hide evidence from the old tower massacre.",
            ),
            "false_explanation": conflict_seed.get(
                "false_explanation",
                "officials claim the missing names were lost during a harmless archive flood.",
            ),
            "affected_districts": conflict_seed.get("affected_districts", [
                "Foglamp Steps",
                "Saltbark Archive Row",
                "Nine-Bell Market",
            ]),
            "affected_groups": conflict_seed.get("affected_groups", [
                "no-bell children",
                "archive families",
                "road wardens",
                "market witnesses",
                "exiled name-carriers",
            ]),
            "evidence": conflict_seed.get("evidence", [
                "sealed tunnel name tablets",
                "redacted birth ledgers",
                "dead bell that rings only near erased names",
            ]),
            "story_use": (
                "Turns settlement structure into active civic conflict through names, districts, archives, class, and hidden history."
            ),
            "character_effect": (
                "Characters must choose between safety, family truth, civic order, public shame, archive power, and children without names."
            ),
            "plot_effect": (
                "Can trigger riot, trial, tunnel exploration, record theft, public confession, massacre reveal, or political collapse."
            ),
            "memory_effect": (
                "World memory must track who learns the truth, which names are restored, which districts are damaged, and who loses power."
            ),
            "lore_effect": (
                "Dead bells and hidden names turn civic conflict into mythic proof that false history still wounds the town."
            ),
            "anti_genericity_signal": (
                "Conflict ties settlement districts, name law, secret history, class, evidence, religion, and memory into one system."
            ),
            "detail_depth_score": 0.9,
            "validation_status": "validated",
            "provenance": {
                "generated_by_engine": "SettlementEngine",
                "origin_type": "derived_from_settlement",
                "source_id": source_id,
                "settlement_id": settlement["settlement_id"],
                "seed_keys": sorted(conflict_seed.keys()),
            },
            "compression_summary": (
                f"{conflict_name}: public issue, secret cause, false explanation, affected districts, evidence, and memory effects."
            ),
        }

        return {"settlement_conflict": conflict}

    def build_story_context_patch(
        self,
        *,
        settlement: Dict[str, Any],
        settlement_conflict: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        patch = {
            "settlement_id": settlement["settlement_id"],
            "settlement_name": settlement["unique_name"],
            "settlement_type": settlement["settlement_type"],
            "region_name": settlement["region_name"],
            "political_unit_id": settlement.get("political_unit_id"),
            "districts": settlement["districts"],
            "infrastructure": settlement["infrastructure"],
            "economy": settlement["economy"],
            "law_and_order": settlement["law_and_order"],
            "religion_myth_lore": settlement["religion_myth_lore"],
            "class_layout": settlement["class_layout"],
            "food_water_supply": settlement["food_water_supply"],
            "security_risks": settlement["security_risks"],
            "current_tensions": settlement["current_tensions"],
            "important_locations": settlement["important_locations"],
            "public_history": settlement["public_history"],
            "secret_history": settlement["secret_history"],
            "false_history": settlement["false_history"],
            "story_use": settlement["story_use"],
            "character_effect": settlement["character_effect"],
            "plot_effect": settlement["plot_effect"],
            "memory_effect": settlement["memory_effect"],
            "generation_hints": [
                "Use settlements as scene systems, not map dots.",
                "Choose districts based on class, law, secrecy, economy, religion, and plot pressure.",
                "Let settlement details affect movement, dialogue, conflict, status, and sensory description.",
                "Track settlement damage, renamed places, law changes, district control, and secret-history reveals.",
            ],
            "memory_update_candidates": [
                {
                    "candidate_type": "settlement_state",
                    "target_element_id": settlement["settlement_id"],
                    "reason": "Track districts, laws, faction control, damage, renamed places, shortages, and history reveals.",
                }
            ],
        }

        if settlement_conflict:
            patch["active_settlement_conflict"] = settlement_conflict
            patch["memory_update_candidates"].append(
                {
                    "candidate_type": "settlement_conflict_state",
                    "target_element_id": settlement_conflict["settlement_conflict_id"],
                    "reason": "Track public issue, secret cause, false explanation, evidence, affected groups, and outcome.",
                }
            )

        return {"story_context_patch": patch}

    def validate_settlement(self, *, settlement: Dict[str, Any]) -> Dict[str, Any]:
        required = [
            "settlement_id",
            "unique_name",
            "settlement_type",
            "region_name",
            "name_origin",
            "name_meaning",
            "name_language_logic",
            "cultural_context",
            "world_context",
            "visual_identity",
            "sensory_identity",
            "founding_history",
            "public_history",
            "secret_history",
            "false_history",
            "districts",
            "infrastructure",
            "economy",
            "law_and_order",
            "religion_myth_lore",
            "class_layout",
            "food_water_supply",
            "security_risks",
            "current_tensions",
            "important_locations",
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

        missing = [field for field in required if not settlement.get(field)]
        shallow = self._shallow_fields(
            payload=settlement,
            fields=[
                "name_origin",
                "founding_history",
                "story_use",
                "character_effect",
                "plot_effect",
                "memory_effect",
                "anti_genericity_signal",
            ],
        )

        passed = not missing and not shallow and float(settlement.get("detail_depth_score", 0.0)) >= 0.75

        return {
            "passed": passed,
            "missing_fields": missing,
            "shallow_fields": shallow,
            "settlement_id": settlement.get("settlement_id"),
        }

    def validate_settlement_conflict(self, *, settlement_conflict: Dict[str, Any]) -> Dict[str, Any]:
        required = [
            "settlement_conflict_id",
            "settlement_id",
            "settlement_name",
            "conflict_name",
            "conflict_type",
            "public_issue",
            "secret_cause",
            "false_explanation",
            "affected_districts",
            "affected_groups",
            "evidence",
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

        missing = [field for field in required if not settlement_conflict.get(field)]
        shallow = self._shallow_fields(
            payload=settlement_conflict,
            fields=["story_use", "character_effect", "plot_effect", "memory_effect", "lore_effect"],
        )

        passed = not missing and not shallow and float(settlement_conflict.get("detail_depth_score", 0.0)) >= 0.75

        return {
            "passed": passed,
            "missing_fields": missing,
            "shallow_fields": shallow,
            "settlement_conflict_id": settlement_conflict.get("settlement_conflict_id"),
        }

    def summarize_settlement(
        self,
        *,
        settlement: Dict[str, Any],
        settlement_conflict: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        summary = {
            "settlement_id": settlement["settlement_id"],
            "unique_name": settlement["unique_name"],
            "settlement_type": settlement["settlement_type"],
            "district_count": len(settlement["districts"]),
            "infrastructure_count": len(settlement["infrastructure"]),
            "current_tension_count": len(settlement["current_tensions"]),
            "important_location_count": len(settlement["important_locations"]),
            "compression_summary": settlement["compression_summary"],
        }

        if settlement_conflict:
            summary["settlement_conflict_id"] = settlement_conflict["settlement_conflict_id"]
            summary["settlement_conflict_name"] = settlement_conflict["conflict_name"]

        return {"success": True, "summary": summary}

    def build_settlement_text(
        self,
        *,
        settlement: Dict[str, Any],
        settlement_conflict: Dict[str, Any] | None = None,
    ) -> Dict[str, str]:
        lines = [
            "Settlement Profile",
            f"Name: {settlement['unique_name']}",
            f"ID: {settlement['settlement_id']}",
            f"Type: {settlement['settlement_type']}",
            f"Region: {settlement['region_name']}",
            "",
            "Name Origin:",
            settlement["name_origin"],
        ]

        sections = [
            ("Districts", [str(item) for item in settlement["districts"]]),
            ("Infrastructure", settlement["infrastructure"]),
            ("Economy", settlement["economy"]),
            ("Law and Order", settlement["law_and_order"]),
            ("Religion / Myth / Lore", settlement["religion_myth_lore"]),
            ("Class Layout", settlement["class_layout"]),
            ("Food and Water Supply", settlement["food_water_supply"]),
            ("Security Risks", settlement["security_risks"]),
            ("Current Tensions", settlement["current_tensions"]),
            ("Important Locations", settlement["important_locations"]),
        ]

        for title, values in sections:
            lines.append("")
            lines.append(title + ":")
            for item in values:
                lines.append(f"- {item}")

        lines.extend([
            "",
            "Public History:",
            settlement["public_history"],
            "",
            "Secret History:",
            settlement["secret_history"],
            "",
            "False History:",
            settlement["false_history"],
        ])

        if settlement_conflict:
            lines.extend([
                "",
                "Active Settlement Conflict:",
                settlement_conflict["conflict_name"],
                "",
                "Secret Cause:",
                settlement_conflict["secret_cause"],
            ])

        lines.extend([
            "",
            "Story Use:",
            settlement["story_use"],
            "",
            "Character Effect:",
            settlement["character_effect"],
            "",
            "Plot Effect:",
            settlement["plot_effect"],
            "",
            "Memory Effect:",
            settlement["memory_effect"],
        ])

        return {"settlement_text": chr(10).join(lines)}

    def _shallow_fields(self, *, payload: Dict[str, Any], fields: List[str]) -> List[str]:
        return [field for field in fields if len(str(payload.get(field, ""))) < 20]

    def _slug(self, value: str) -> str:
        return "_".join(part for part in value.lower().replace("/", " ").replace("-", " ").split() if part)

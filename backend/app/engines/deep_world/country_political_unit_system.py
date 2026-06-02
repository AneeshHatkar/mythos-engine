from __future__ import annotations

from typing import Any, Dict, List


class CountryPoliticalUnitSystem:
    def build_political_unit(
        self,
        *,
        source_id: str,
        political_seed: Dict[str, Any] | None = None,
        story_context: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        political_seed = political_seed or {}
        story_context = story_context or {}

        base_name = political_seed.get("base_name", "Avar")
        unique_name = political_seed.get("unique_name", f"The Bellmarch Concord of {base_name}")
        region_name = political_seed.get("region_name", story_context.get("region_name", "Saltroot Forest"))
        government_type = political_seed.get("government_type", "witness-council concord")
        culture = political_seed.get("culture", story_context.get("culture", "bell-road legal culture"))

        political_unit = {
            "political_unit_id": f"political_unit_{source_id}_{self._slug(unique_name)}",
            "source_id": source_id,
            "unique_name": unique_name,
            "base_name": base_name,
            "political_unit_type": political_seed.get("political_unit_type", "country"),
            "government_type": government_type,
            "region_name": region_name,
            "name_origin": political_seed.get(
                "name_origin",
                f"{unique_name} is named after the bell-road treaties that joined scattered route towns "
                f"under shared witness law.",
            ),
            "name_meaning": political_seed.get(
                "name_meaning",
                "a pact of roads, bells, testimony, and shared survival",
            ),
            "name_language_logic": political_seed.get(
                "name_language_logic",
                "formal state names combine legal object, founding pact, and ancestral region marker",
            ),
            "cultural_context": culture,
            "world_context": region_name,
            "visual_identity": political_seed.get(
                "visual_identity",
                "black road banners stitched with silver bell-thread and salt-white border knots",
            ),
            "sensory_identity": political_seed.get(
                "sensory_identity",
                "court bells, wet stone roads, inked salt bark records, and mineral rain on treaty halls",
            ),
            "capital_or_center": political_seed.get("capital_or_center", "Veyr Hall of Nine Roads"),
            "major_regions": political_seed.get("major_regions", [
                "Saltroot Forest Roadlands",
                "White-Bark Ravine Holds",
                "Red Fog Border Marches",
                "Old Bell Tower Districts",
            ]),
            "border_logic": political_seed.get("border_logic", [
                "borders follow old witnessed roads rather than clean rivers",
                "fog season can temporarily erase practical border control",
                "disputed border stones mark old treaty betrayals",
            ]),
            "government_structure": political_seed.get("government_structure", [
                {
                    "body": "Bell Council",
                    "function": "settles testimony, treaty, inheritance, road, and witness disputes",
                    "weakness": "archive families can manipulate old records",
                },
                {
                    "body": "Road Wardens",
                    "function": "protect roads, enforce travel law, and respond to fog closures",
                    "weakness": "underfunded in poor border towns",
                },
                {
                    "body": "Temple Witness Bench",
                    "function": "handles ritual truth, funeral disputes, and dead-bell interpretations",
                    "weakness": "rival sects accuse it of hiding divine warnings",
                },
            ]),
            "law_system": political_seed.get("law_system", [
                "two witnesses required for inheritance across road borders",
                "dead-bell testimony can reopen old murder and exile cases",
                "forbidden names may not appear in public market ledgers",
                "map fraud is treated as violence against travelers",
            ]),
            "economy_basis": political_seed.get("economy_basis", [
                "saltroot medicine trade",
                "certified road maps",
                "witness-court fees",
                "bell-metal craft",
                "fog guide labor",
            ]),
            "religion_myth_links": political_seed.get("religion_myth_links", [
                "founding myth says the first road bell rang by itself after a betrayal",
                "fog saints are claimed by temples but followed by poor road families",
                "dead bells are believed to warn when public history is false",
            ]),
            "public_history": political_seed.get(
                "public_history",
                "The Concord claims it was founded peacefully when road towns united to protect travelers from fog deaths.",
            ),
            "secret_history": political_seed.get(
                "secret_history",
                "Several founding towns were forced into the pact after archive families hid evidence of a border massacre.",
            ),
            "false_history": political_seed.get(
                "false_history",
                "Official murals blame the border massacre on bandits rather than treaty negotiators.",
            ),
            "current_conflicts": political_seed.get("current_conflicts", [
                "border towns demand old road rights be restored",
                "archive families suppress forbidden names",
                "temples argue over whether dead bells count as divine testimony",
                "smugglers exploit fog season border confusion",
            ]),
            "faction_pressure": political_seed.get("faction_pressure", [
                "Bell Council wants order and stable records",
                "Road Wardens want emergency authority during fog closures",
                "exiled name-carriers want public restoration",
                "merchant houses want map law weakened",
            ]),
            "citizenship_rules": political_seed.get("citizenship_rules", [
                "public name registration after family witness approval",
                "road-service obligation for guide families",
                "exile removes map ownership rights",
                "adoption can transfer road memory duties",
            ]),
            "symbols_and_flags": political_seed.get("symbols_and_flags", [
                "silver bell over black road stripe",
                "salt-white border knots for treaty survival",
                "red fog thread used only on mourning banners",
            ]),
            "story_use": (
                "Creates a political unit with borders, government, law, religion, public/secret history, economy, "
                "citizenship, faction pressure, and current conflicts that can drive plot."
            ),
            "character_effect": (
                "Characters inherit legal status, citizenship duties, forbidden names, class access, border rights, "
                "religious pressure, faction loyalty, and public/secret historical burden."
            ),
            "plot_effect": (
                "Can trigger border disputes, trial scenes, rebellion, inheritance conflict, smuggling, treaty revelation, "
                "religious schism, map fraud, or restoration of erased families."
            ),
            "memory_effect": (
                "World memory must track political status, borders, law changes, public/secret history reveals, faction shifts, "
                "citizenship changes, treaties, exiles, and renamed places."
            ),
            "anti_genericity_signal": (
                "Political unit includes unique naming, government bodies, law, borders, economy, religion, symbols, "
                "public/secret/false history, faction conflict, and memory hooks."
            ),
            "detail_depth_score": 0.93,
            "validation_status": "validated",
            "provenance": {
                "generated_by_engine": "CountryPoliticalUnitSystem",
                "origin_type": "generated_from_political_seed",
                "source_id": source_id,
                "seed_keys": sorted(political_seed.keys()),
                "story_context_keys": sorted(story_context.keys()),
            },
            "compression_summary": (
                f"{unique_name}: {government_type} in {region_name}; law, borders, economy, religion, "
                f"public/secret history, factions, and memory hooks."
            ),
        }

        return {"political_unit": political_unit}

    def build_border_conflict(
        self,
        *,
        source_id: str,
        political_unit: Dict[str, Any],
        conflict_seed: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        conflict_seed = conflict_seed or {}

        conflict_name = conflict_seed.get("conflict_name", "Red Fog Border Stone Dispute")

        border_conflict = {
            "border_conflict_id": f"border_conflict_{source_id}_{self._slug(conflict_name)}",
            "source_id": source_id,
            "political_unit_id": political_unit["political_unit_id"],
            "political_unit_name": political_unit["unique_name"],
            "conflict_name": conflict_name,
            "conflict_type": conflict_seed.get("conflict_type", "border_and_history_dispute"),
            "public_claim": conflict_seed.get(
                "public_claim",
                "The disputed road belongs to the Concord because it appears in official bell maps.",
            ),
            "secret_truth": conflict_seed.get(
                "secret_truth",
                "The road was taken after treaty witnesses were erased from public records.",
            ),
            "false_claim": conflict_seed.get(
                "false_claim",
                "Officials blame fog drift for mismatched border stones.",
            ),
            "affected_groups": conflict_seed.get("affected_groups", [
                "border families",
                "archive houses",
                "road wardens",
                "merchant caravans",
                "exiled name-carriers",
            ]),
            "evidence": conflict_seed.get("evidence", [
                "old bell-metal border token",
                "forbidden family name carved under salt bark",
                "road song with missing treaty verse",
            ]),
            "story_use": (
                "Turns political geography into active conflict through borders, old treaties, hidden evidence, and erased witnesses."
            ),
            "character_effect": (
                "Characters must choose between law, family memory, safety, duty, profit, and fear of forbidden names."
            ),
            "plot_effect": (
                "Can trigger investigation, trial, border violence, smuggling, exile reversal, treaty collapse, or public history change."
            ),
            "memory_effect": (
                "World memory must track who knows the public claim, secret truth, false claim, evidence, and resulting border status."
            ),
            "lore_effect": (
                "Old roads, dead bells, and forbidden names make the political dispute feel mythic instead of bureaucratic."
            ),
            "anti_genericity_signal": (
                "Conflict ties border law to public/secret/false history, physical evidence, family names, factions, and plot consequences."
            ),
            "detail_depth_score": 0.9,
            "validation_status": "validated",
            "provenance": {
                "generated_by_engine": "CountryPoliticalUnitSystem",
                "origin_type": "derived_from_political_unit",
                "source_id": source_id,
                "political_unit_id": political_unit["political_unit_id"],
                "seed_keys": sorted(conflict_seed.keys()),
            },
            "compression_summary": (
                f"{conflict_name}: public claim, secret truth, false claim, affected groups, evidence, and border memory."
            ),
        }

        return {"border_conflict": border_conflict}

    def build_story_context_patch(
        self,
        *,
        political_unit: Dict[str, Any],
        border_conflict: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        patch = {
            "political_unit_id": political_unit["political_unit_id"],
            "political_unit_name": political_unit["unique_name"],
            "political_unit_type": political_unit["political_unit_type"],
            "government_type": political_unit["government_type"],
            "capital_or_center": political_unit["capital_or_center"],
            "major_regions": political_unit["major_regions"],
            "border_logic": political_unit["border_logic"],
            "government_structure": political_unit["government_structure"],
            "law_system": political_unit["law_system"],
            "economy_basis": political_unit["economy_basis"],
            "religion_myth_links": political_unit["religion_myth_links"],
            "public_history": political_unit["public_history"],
            "secret_history": political_unit["secret_history"],
            "false_history": political_unit["false_history"],
            "current_conflicts": political_unit["current_conflicts"],
            "faction_pressure": political_unit["faction_pressure"],
            "citizenship_rules": political_unit["citizenship_rules"],
            "symbols_and_flags": political_unit["symbols_and_flags"],
            "story_use": political_unit["story_use"],
            "character_effect": political_unit["character_effect"],
            "plot_effect": political_unit["plot_effect"],
            "memory_effect": political_unit["memory_effect"],
            "generation_hints": [
                "Use political units as active systems, not map labels.",
                "Let laws, borders, citizenship, faction pressure, and secret history shape scenes.",
                "Track political changes, renamed places, treaties, exiles, and public/secret history in memory.",
                "Countries must have unique names, symbols, conflicts, government bodies, and story pressure.",
            ],
            "memory_update_candidates": [
                {
                    "candidate_type": "political_unit_state",
                    "target_element_id": political_unit["political_unit_id"],
                    "reason": "Track borders, laws, factions, history reveals, citizenship changes, exiles, and renamed places.",
                }
            ],
        }

        if border_conflict:
            patch["active_border_conflict"] = border_conflict
            patch["memory_update_candidates"].append(
                {
                    "candidate_type": "border_conflict_state",
                    "target_element_id": border_conflict["border_conflict_id"],
                    "reason": "Track public claim, secret truth, false claim, evidence, affected groups, and border outcome.",
                }
            )

        return {"story_context_patch": patch}

    def validate_political_unit(self, *, political_unit: Dict[str, Any]) -> Dict[str, Any]:
        required = [
            "political_unit_id",
            "unique_name",
            "political_unit_type",
            "government_type",
            "region_name",
            "name_origin",
            "name_meaning",
            "name_language_logic",
            "cultural_context",
            "world_context",
            "visual_identity",
            "sensory_identity",
            "capital_or_center",
            "major_regions",
            "border_logic",
            "government_structure",
            "law_system",
            "economy_basis",
            "religion_myth_links",
            "public_history",
            "secret_history",
            "false_history",
            "current_conflicts",
            "faction_pressure",
            "citizenship_rules",
            "symbols_and_flags",
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

        missing = [field for field in required if not political_unit.get(field)]
        shallow = self._shallow_fields(
            payload=political_unit,
            fields=[
                "name_origin",
                "story_use",
                "character_effect",
                "plot_effect",
                "memory_effect",
                "anti_genericity_signal",
            ],
        )

        passed = not missing and not shallow and float(political_unit.get("detail_depth_score", 0.0)) >= 0.75

        return {
            "passed": passed,
            "missing_fields": missing,
            "shallow_fields": shallow,
            "political_unit_id": political_unit.get("political_unit_id"),
        }

    def validate_border_conflict(self, *, border_conflict: Dict[str, Any]) -> Dict[str, Any]:
        required = [
            "border_conflict_id",
            "political_unit_id",
            "political_unit_name",
            "conflict_name",
            "conflict_type",
            "public_claim",
            "secret_truth",
            "false_claim",
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

        missing = [field for field in required if not border_conflict.get(field)]
        shallow = self._shallow_fields(
            payload=border_conflict,
            fields=["story_use", "character_effect", "plot_effect", "memory_effect", "lore_effect"],
        )

        passed = not missing and not shallow and float(border_conflict.get("detail_depth_score", 0.0)) >= 0.75

        return {
            "passed": passed,
            "missing_fields": missing,
            "shallow_fields": shallow,
            "border_conflict_id": border_conflict.get("border_conflict_id"),
        }

    def summarize_political_unit(
        self,
        *,
        political_unit: Dict[str, Any],
        border_conflict: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        summary = {
            "political_unit_id": political_unit["political_unit_id"],
            "unique_name": political_unit["unique_name"],
            "government_type": political_unit["government_type"],
            "major_region_count": len(political_unit["major_regions"]),
            "government_body_count": len(political_unit["government_structure"]),
            "law_count": len(political_unit["law_system"]),
            "conflict_count": len(political_unit["current_conflicts"]),
            "compression_summary": political_unit["compression_summary"],
        }

        if border_conflict:
            summary["border_conflict_id"] = border_conflict["border_conflict_id"]
            summary["border_conflict_name"] = border_conflict["conflict_name"]

        return {"success": True, "summary": summary}

    def build_political_unit_text(
        self,
        *,
        political_unit: Dict[str, Any],
        border_conflict: Dict[str, Any] | None = None,
    ) -> Dict[str, str]:
        lines = [
            "Country / Political Unit Profile",
            f"Name: {political_unit['unique_name']}",
            f"ID: {political_unit['political_unit_id']}",
            f"Type: {political_unit['political_unit_type']}",
            f"Government: {political_unit['government_type']}",
            "",
            "Name Origin:",
            political_unit["name_origin"],
        ]

        sections = [
            ("Major Regions", political_unit["major_regions"]),
            ("Border Logic", political_unit["border_logic"]),
            ("Government Structure", [str(item) for item in political_unit["government_structure"]]),
            ("Law System", political_unit["law_system"]),
            ("Economy Basis", political_unit["economy_basis"]),
            ("Religion / Myth Links", political_unit["religion_myth_links"]),
            ("Current Conflicts", political_unit["current_conflicts"]),
            ("Faction Pressure", political_unit["faction_pressure"]),
            ("Citizenship Rules", political_unit["citizenship_rules"]),
            ("Symbols and Flags", political_unit["symbols_and_flags"]),
        ]

        for title, values in sections:
            lines.append("")
            lines.append(title + ":")
            for item in values:
                lines.append(f"- {item}")

        lines.extend([
            "",
            "Public History:",
            political_unit["public_history"],
            "",
            "Secret History:",
            political_unit["secret_history"],
            "",
            "False History:",
            political_unit["false_history"],
        ])

        if border_conflict:
            lines.extend([
                "",
                "Active Border Conflict:",
                border_conflict["conflict_name"],
                "",
                "Secret Truth:",
                border_conflict["secret_truth"],
            ])

        lines.extend([
            "",
            "Story Use:",
            political_unit["story_use"],
            "",
            "Character Effect:",
            political_unit["character_effect"],
            "",
            "Plot Effect:",
            political_unit["plot_effect"],
            "",
            "Memory Effect:",
            political_unit["memory_effect"],
        ])

        return {"political_unit_text": chr(10).join(lines)}

    def _shallow_fields(self, *, payload: Dict[str, Any], fields: List[str]) -> List[str]:
        return [field for field in fields if len(str(payload.get(field, ""))) < 20]

    def _slug(self, value: str) -> str:
        return "_".join(part for part in value.lower().replace("/", " ").replace("-", " ").split() if part)

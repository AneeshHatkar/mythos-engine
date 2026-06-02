from __future__ import annotations

from typing import Any, Dict, List


class SpeciesPeopleTypeExpansionEngine:
    def build_species_profile(
        self,
        *,
        source_id: str,
        species_seed: Dict[str, Any] | None = None,
        story_context: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        species_seed = species_seed or {}
        story_context = story_context or {}

        base_name = species_seed.get("base_name", "Aurel")
        unique_name = species_seed.get("unique_name", f"{base_name} Saltvein Kin")
        region_name = species_seed.get("region_name", story_context.get("region_name", "Saltroot Forest"))
        culture = species_seed.get("culture", story_context.get("culture", "bell-road witness culture"))

        species_profile = {
            "species_profile_id": f"species_{source_id}_{self._slug(unique_name)}",
            "source_id": source_id,
            "unique_name": unique_name,
            "base_name": base_name,
            "classification": species_seed.get("classification", "humanoid people type"),
            "name_origin": species_seed.get(
                "name_origin",
                f"{unique_name} comes from {culture}; the name refers to families marked by salt-vein skin patterns "
                f"and oath-listening customs.",
            ),
            "name_meaning": species_seed.get("name_meaning", "people whose bodies remember salt, road, and oath"),
            "name_language_logic": species_seed.get(
                "name_language_logic",
                "compound people-name: ancestral root + physical/social marker + kinship suffix",
            ),
            "cultural_context": culture,
            "world_context": region_name,
            "visual_identity": species_seed.get(
                "visual_identity",
                "faint silver salt-vein markings near the temples, dark road-cloth wraps, and bell-thread bracelets",
            ),
            "sensory_identity": species_seed.get(
                "sensory_identity",
                "smell of mineral rain, low humming speech cadence, and salt-dust on ceremonial clothing",
            ),
            "biological_traits": species_seed.get("biological_traits", [
                "salt-vein markings become brighter during fever, fear, or oath ceremonies",
                "strong resistance to fog-sickness but high sensitivity to dry salt winds",
                "children learn route-sound recognition earlier than written language",
            ]),
            "social_traits": species_seed.get("social_traits", [
                "families are organized by road-oath memory rather than only bloodline",
                "elders preserve migration songs used as legal testimony",
                "children receive public names only after surviving first fog crossing",
            ]),
            "belief_pressure": species_seed.get("belief_pressure", [
                "believe roads remember broken promises",
                "treat false testimony as a wound to both family and landscape",
                "fear dead bells because they imply erased witnesses",
            ]),
            "law_pressure": species_seed.get("law_pressure", [
                "must serve as route witnesses during trials",
                "cannot sell old road maps without elder approval",
                "exile is marked by removal of bell-thread bracelets",
            ]),
            "class_pressure": species_seed.get("class_pressure", [
                "wealthy kin control certified route archives",
                "poor kin serve as living guides and risk fog exposure",
                "exiled kin become smugglers, scouts, or forbidden-name carriers",
            ]),
            "occupation_patterns": species_seed.get("occupation_patterns", [
                "road witnesses",
                "fog guides",
                "bell archivists",
                "saltroot healers",
                "map singers",
            ]),
            "naming_rules": species_seed.get("naming_rules", [
                "child names begin as weather nicknames before formal road names",
                "family names may change after exile, adoption, or oath failure",
                "taboo names are replaced by route numbers in public records",
                "heroes may gain bell-title names after saving travelers",
            ]),
            "taboo_rules": species_seed.get("taboo_rules", [
                "speaking an erased family name during fog season is forbidden",
                "wearing dead-bell metal without witness rights is considered theft from the dead",
                "burning road cloth means rejecting kin memory",
            ]),
            "relationship_to_other_groups": species_seed.get("relationship_to_other_groups", [
                "trusted by courts but resented by merchants who dislike route taxes",
                "feared by smugglers because they can identify false road songs",
                "sought by nobles during inheritance disputes",
            ]),
            "internal_divisions": species_seed.get("internal_divisions", [
                "archive families who preserve law",
                "road families who guide travelers",
                "exile families who carry forbidden routes",
                "healer families who protect fog-sickness medicine",
            ]),
            "story_use": (
                "Creates people-group identity with naming rules, law pressure, belief pressure, class divisions, "
                "social memory, migration history, and conflict hooks."
            ),
            "character_effect": (
                "Characters from this group inherit specific fears, names, family duties, speech habits, moral pressures, "
                "legal obligations, and relationships to roads, memory, and testimony."
            ),
            "plot_effect": (
                "A member can expose false maps, carry forbidden names, trigger inheritance conflict, reveal secret roads, "
                "or force legal testimony that changes political power."
            ),
            "memory_effect": (
                "World memory must track formal names, exile names, family status, taboo names, route rights, witness duties, "
                "and whether public/secret history changed group reputation."
            ),
            "anti_genericity_signal": (
                "Species/people type has naming rules, body traits, law, class, belief, occupation, taboos, internal divisions, "
                "and cross-group conflict."
            ),
            "detail_depth_score": 0.93,
            "validation_status": "validated",
            "provenance": {
                "generated_by_engine": "SpeciesPeopleTypeExpansionEngine",
                "origin_type": "generated_from_species_seed",
                "source_id": source_id,
                "seed_keys": sorted(species_seed.keys()),
                "story_context_keys": sorted(story_context.keys()),
            },
            "compression_summary": (
                f"{unique_name}: {species_seed.get('classification', 'humanoid people type')} from {region_name}; "
                f"identity tied to naming, law, road memory, belief, class, and testimony."
            ),
        }

        return {"species_profile": species_profile}

    def build_people_type_profile(
        self,
        *,
        source_id: str,
        species_profile: Dict[str, Any],
        people_type_seed: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        people_type_seed = people_type_seed or {}

        role_name = people_type_seed.get("role_name", "Fog-Witness Guide")
        unique_name = people_type_seed.get("unique_name", f"{species_profile['unique_name']} {role_name}")

        people_type_profile = {
            "people_type_profile_id": f"people_type_{source_id}_{self._slug(unique_name)}",
            "source_id": source_id,
            "species_profile_id": species_profile["species_profile_id"],
            "species_name": species_profile["unique_name"],
            "unique_name": unique_name,
            "role_name": role_name,
            "name_origin": people_type_seed.get(
                "name_origin",
                f"{unique_name} is a role-name given to those who guide travelers through dangerous fog routes "
                f"and testify about road events.",
            ),
            "name_meaning": people_type_seed.get("name_meaning", "one trusted to guide, witness, and remember the road"),
            "name_language_logic": people_type_seed.get(
                "name_language_logic",
                "role-title attaches after proven service, public testimony, or survival of a dangerous crossing",
            ),
            "social_function": people_type_seed.get(
                "social_function",
                "guides travelers, verifies route truth, protects legal memory, and warns settlements before fog closure",
            ),
            "economic_function": people_type_seed.get(
                "economic_function",
                "paid by caravans, courts, healers, and nobles needing safe passage or verified road testimony",
            ),
            "belief_function": people_type_seed.get(
                "belief_function",
                "treated as someone who can hear whether the road is safe, cursed, false, or wounded by old crimes",
            ),
            "skill_profile": people_type_seed.get("skill_profile", [
                "reads fog density from animal movement",
                "identifies old road songs",
                "recognizes counterfeit route bells",
                "guides caravans through closed roads",
            ]),
            "social_status": people_type_seed.get(
                "social_status",
                "respected in villages, exploited by courts, targeted by smugglers, and distrusted by nobles hiding false maps",
            ),
            "failure_modes": people_type_seed.get("failure_modes", [
                "accepts bribe to mislead travelers",
                "misreads animal signs during ecological collapse",
                "reveals forbidden route name under pressure",
                "protects family reputation instead of telling truth",
            ]),
            "story_use": (
                "Creates a role-based people type that can enter scenes as guide, witness, suspect, victim, mentor, smuggler, "
                "political tool, or moral pressure point."
            ),
            "character_effect": (
                "Characters with this people type carry specific skills, speech habits, duties, fears, social costs, "
                "and moral conflicts around truth and survival."
            ),
            "plot_effect": (
                "Can start journeys, expose false maps, mislead a party, reveal hidden roads, cause trial conflict, "
                "or become the only witness to a forbidden event."
            ),
            "memory_effect": (
                "World memory must track who holds the role, failed duties, route testimony, reputation changes, "
                "bribes, exile, and public trust."
            ),
            "anti_genericity_signal": (
                "People type is connected to species identity, naming, law, economy, skill, failure, role status, and plot pressure."
            ),
            "detail_depth_score": 0.91,
            "validation_status": "validated",
            "provenance": {
                "generated_by_engine": "SpeciesPeopleTypeExpansionEngine",
                "origin_type": "derived_from_species_profile",
                "source_id": source_id,
                "species_profile_id": species_profile["species_profile_id"],
                "seed_keys": sorted(people_type_seed.keys()),
            },
            "compression_summary": (
                f"{unique_name}: role type with route guidance, testimony, economy, failure modes, and memory hooks."
            ),
        }

        return {"people_type_profile": people_type_profile}

    def build_story_context_patch(
        self,
        *,
        species_profile: Dict[str, Any],
        people_type_profile: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        patch = {
            "species_profile_id": species_profile["species_profile_id"],
            "species_name": species_profile["unique_name"],
            "classification": species_profile["classification"],
            "naming_rules": species_profile["naming_rules"],
            "taboo_rules": species_profile["taboo_rules"],
            "biological_traits": species_profile["biological_traits"],
            "social_traits": species_profile["social_traits"],
            "belief_pressure": species_profile["belief_pressure"],
            "law_pressure": species_profile["law_pressure"],
            "class_pressure": species_profile["class_pressure"],
            "occupation_patterns": species_profile["occupation_patterns"],
            "internal_divisions": species_profile["internal_divisions"],
            "relationship_to_other_groups": species_profile["relationship_to_other_groups"],
            "story_use": species_profile["story_use"],
            "character_effect": species_profile["character_effect"],
            "plot_effect": species_profile["plot_effect"],
            "memory_effect": species_profile["memory_effect"],
            "generation_hints": [
                "Use species and people type rules to shape names, dialogue, social pressure, role behavior, and conflict.",
                "Do not generate generic races/classes; every group must have law, belief, class, naming, memory, and plot function.",
                "Track taboo names, role titles, family divisions, exile names, and reputation changes in memory.",
                "Let people types create scene behavior and not just background description.",
            ],
            "memory_update_candidates": [
                {
                    "candidate_type": "species_identity_state",
                    "target_element_id": species_profile["species_profile_id"],
                    "reason": "Track naming rules, group reputation, taboo changes, law pressure, and public/secret history changes.",
                }
            ],
        }

        if people_type_profile:
            patch["people_type_profile"] = people_type_profile
            patch["memory_update_candidates"].append(
                {
                    "candidate_type": "people_type_state",
                    "target_element_id": people_type_profile["people_type_profile_id"],
                    "reason": "Track role holders, failures, public trust, exile, bribes, and testimony consequences.",
                }
            )

        return {"story_context_patch": patch}

    def validate_species_profile(self, *, species_profile: Dict[str, Any]) -> Dict[str, Any]:
        required = [
            "species_profile_id",
            "unique_name",
            "classification",
            "name_origin",
            "name_meaning",
            "name_language_logic",
            "cultural_context",
            "world_context",
            "visual_identity",
            "sensory_identity",
            "biological_traits",
            "social_traits",
            "belief_pressure",
            "law_pressure",
            "class_pressure",
            "occupation_patterns",
            "naming_rules",
            "taboo_rules",
            "relationship_to_other_groups",
            "internal_divisions",
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

        missing = [field for field in required if not species_profile.get(field)]
        shallow = self._shallow_fields(
            payload=species_profile,
            fields=[
                "name_origin",
                "story_use",
                "character_effect",
                "plot_effect",
                "memory_effect",
                "anti_genericity_signal",
            ],
        )

        passed = not missing and not shallow and float(species_profile.get("detail_depth_score", 0.0)) >= 0.75

        return {
            "passed": passed,
            "missing_fields": missing,
            "shallow_fields": shallow,
            "species_profile_id": species_profile.get("species_profile_id"),
        }

    def validate_people_type_profile(self, *, people_type_profile: Dict[str, Any]) -> Dict[str, Any]:
        required = [
            "people_type_profile_id",
            "species_profile_id",
            "species_name",
            "unique_name",
            "role_name",
            "name_origin",
            "name_meaning",
            "name_language_logic",
            "social_function",
            "economic_function",
            "belief_function",
            "skill_profile",
            "social_status",
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

        missing = [field for field in required if not people_type_profile.get(field)]
        shallow = self._shallow_fields(
            payload=people_type_profile,
            fields=[
                "name_origin",
                "social_function",
                "story_use",
                "character_effect",
                "plot_effect",
                "memory_effect",
                "anti_genericity_signal",
            ],
        )

        passed = not missing and not shallow and float(people_type_profile.get("detail_depth_score", 0.0)) >= 0.75

        return {
            "passed": passed,
            "missing_fields": missing,
            "shallow_fields": shallow,
            "people_type_profile_id": people_type_profile.get("people_type_profile_id"),
        }

    def summarize_species_and_people_type(
        self,
        *,
        species_profile: Dict[str, Any],
        people_type_profile: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        summary = {
            "species_profile_id": species_profile["species_profile_id"],
            "species_name": species_profile["unique_name"],
            "classification": species_profile["classification"],
            "biological_trait_count": len(species_profile["biological_traits"]),
            "social_trait_count": len(species_profile["social_traits"]),
            "naming_rule_count": len(species_profile["naming_rules"]),
            "occupation_pattern_count": len(species_profile["occupation_patterns"]),
            "compression_summary": species_profile["compression_summary"],
        }

        if people_type_profile:
            summary["people_type_profile_id"] = people_type_profile["people_type_profile_id"]
            summary["people_type_name"] = people_type_profile["unique_name"]
            summary["skill_count"] = len(people_type_profile["skill_profile"])
            summary["failure_mode_count"] = len(people_type_profile["failure_modes"])

        return {
            "success": True,
            "summary": summary,
        }

    def build_species_people_text(
        self,
        *,
        species_profile: Dict[str, Any],
        people_type_profile: Dict[str, Any] | None = None,
    ) -> Dict[str, str]:
        lines = [
            "Species + People Type Expansion Profile",
            f"Species: {species_profile['unique_name']}",
            f"Species ID: {species_profile['species_profile_id']}",
            f"Classification: {species_profile['classification']}",
            "",
            "Name Origin:",
            species_profile["name_origin"],
            "",
            "Biological Traits:",
        ]

        species_sections = [
            ("Biological Traits", species_profile["biological_traits"]),
            ("Social Traits", species_profile["social_traits"]),
            ("Belief Pressure", species_profile["belief_pressure"]),
            ("Law Pressure", species_profile["law_pressure"]),
            ("Class Pressure", species_profile["class_pressure"]),
            ("Occupation Patterns", species_profile["occupation_patterns"]),
            ("Naming Rules", species_profile["naming_rules"]),
            ("Taboo Rules", species_profile["taboo_rules"]),
            ("Internal Divisions", species_profile["internal_divisions"]),
        ]

        lines = lines[:-1]

        for title, values in species_sections:
            lines.append("")
            lines.append(title + ":")
            for item in values:
                lines.append(f"- {item}")

        if people_type_profile:
            lines.extend([
                "",
                "People Type:",
                people_type_profile["unique_name"],
                "",
                "Role Meaning:",
                people_type_profile["name_meaning"],
                "",
                "Skill Profile:",
            ])

            for item in people_type_profile["skill_profile"]:
                lines.append(f"- {item}")

            lines.append("")
            lines.append("Failure Modes:")
            for item in people_type_profile["failure_modes"]:
                lines.append(f"- {item}")

        lines.extend([
            "",
            "Story Use:",
            species_profile["story_use"],
            "",
            "Character Effect:",
            species_profile["character_effect"],
            "",
            "Plot Effect:",
            species_profile["plot_effect"],
            "",
            "Memory Effect:",
            species_profile["memory_effect"],
        ])

        return {"species_people_text": chr(10).join(lines)}

    def _shallow_fields(self, *, payload: Dict[str, Any], fields: List[str]) -> List[str]:
        return [field for field in fields if len(str(payload.get(field, ""))) < 20]

    def _slug(self, value: str) -> str:
        return "_".join(part for part in value.lower().replace("/", " ").replace("-", " ").split() if part)

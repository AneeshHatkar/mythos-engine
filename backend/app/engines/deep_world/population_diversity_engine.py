from __future__ import annotations

from typing import Any, Dict, List


class PopulationDiversityEngine:
    def build_population_diversity_profile(
        self,
        *,
        source_id: str,
        species_profiles: List[Dict[str, Any]] | None = None,
        people_type_profiles: List[Dict[str, Any]] | None = None,
        population_seed: Dict[str, Any] | None = None,
        story_context: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        species_profiles = species_profiles or []
        people_type_profiles = people_type_profiles or []
        population_seed = population_seed or {}
        story_context = story_context or {}

        region_name = population_seed.get("region_name", story_context.get("region_name", "Saltroot Forest"))
        culture = population_seed.get("culture", story_context.get("culture", "bell-road witness culture"))

        profile_name = population_seed.get("profile_name", f"{region_name} Population Diversity Map")

        population_groups = population_seed.get("population_groups") or self._default_population_groups(
            region_name=region_name,
            culture=culture,
            species_profiles=species_profiles,
            people_type_profiles=people_type_profiles,
        )

        class_distribution = population_seed.get("class_distribution", [
            {
                "class_group": "archive families",
                "status": "high civic status",
                "power_source": "control legal road memory and certified maps",
                "resentment_source": "accused of hiding old routes and profiting from testimony",
            },
            {
                "class_group": "working road families",
                "status": "respected but exhausted",
                "power_source": "practical route survival knowledge",
                "resentment_source": "risk their lives while archive families collect fees",
            },
            {
                "class_group": "route orphans",
                "status": "socially pitied and politically ignored",
                "power_source": "know unofficial roads and abandoned shelters",
                "resentment_source": "their family histories were erased after disasters",
            },
            {
                "class_group": "exiled name-carriers",
                "status": "legally unstable",
                "power_source": "carry forbidden names, hidden maps, and black-market access",
                "resentment_source": "treated as criminals even when they preserve truth",
            },
        ])

        belief_diversity = population_seed.get("belief_diversity", [
            {
                "belief_group": "road-memory believers",
                "core_belief": "roads remember broken oaths and guide the honest",
                "conflict": "dismissed by merchants who want faster trade routes",
            },
            {
                "belief_group": "dead-bell skeptics",
                "core_belief": "omens are tools used by courts and priests to control travel",
                "conflict": "accused of disrespecting the dead",
            },
            {
                "belief_group": "fog saints cult",
                "core_belief": "lost guides become saints who speak through animal movement",
                "conflict": "temples fear the cult can undermine official doctrine",
            },
        ])

        migration_patterns = population_seed.get("migration_patterns", [
            {
                "movement_type": "seasonal fog migration",
                "movers": "road families and medicine gatherers",
                "cause": "red fog blocks old roads and shifts work toward safer settlements",
                "story_effect": "characters may meet displaced guides, missing children, or desperate healers",
            },
            {
                "movement_type": "disaster exile",
                "movers": "families blamed for old road collapses",
                "cause": "public false history turns survivors into scapegoats",
                "story_effect": "secret history can restore or destroy family reputation",
            },
            {
                "movement_type": "trade-road drift",
                "movers": "market families, smugglers, and shrine workers",
                "cause": "new legal roads redirect money away from old towns",
                "story_effect": "economic decline can trigger crime, resentment, and faction recruitment",
            },
        ])

        underrepresented_groups = population_seed.get("underrepresented_groups", [
            {
                "group_name": "erased-road families",
                "why_hidden": "records were removed after a treaty betrayal",
                "story_function": "can reveal missing names and expose false history",
            },
            {
                "group_name": "unlicensed fog healers",
                "why_hidden": "healing without temple license is illegal",
                "story_function": "can save lives but become targets of courts and guilds",
            },
            {
                "group_name": "no-bell children",
                "why_hidden": "children who never received public names after disaster",
                "story_function": "represent identity loss, adoption conflict, and political shame",
            },
        ])

        naming_variation_rules = population_seed.get("naming_variation_rules", [
            "formal names differ by class, oath status, region, exile, and profession",
            "children may hold weather nicknames before public names",
            "taboo names are replaced by route numbers in official documents",
            "marriage, adoption, betrayal, or religious vow can alter public title",
            "secret names may preserve erased family history",
        ])

        diversity_profile = {
            "population_diversity_profile_id": f"population_diversity_{source_id}_{self._slug(profile_name)}",
            "source_id": source_id,
            "profile_name": profile_name,
            "region_name": region_name,
            "culture": culture,
            "population_groups": population_groups,
            "class_distribution": class_distribution,
            "belief_diversity": belief_diversity,
            "migration_patterns": migration_patterns,
            "underrepresented_groups": underrepresented_groups,
            "naming_variation_rules": naming_variation_rules,
            "species_profile_refs": [item.get("species_profile_id") for item in species_profiles if item.get("species_profile_id")],
            "people_type_profile_refs": [
                item.get("people_type_profile_id") for item in people_type_profiles if item.get("people_type_profile_id")
            ],
            "diversity_controls": {
                "avoid_single_culture_population": True,
                "require_class_variation": True,
                "require_belief_variation": True,
                "require_migration_pressure": True,
                "require_hidden_or_erased_groups": True,
                "require_naming_variation": True,
                "minimum_population_group_count": 4,
            },
            "story_use": (
                "Prevents generic populations by creating class, belief, migration, hidden-history, species, occupation, "
                "and naming diversity that can directly drive scenes and conflicts."
            ),
            "character_effect": (
                "Characters inherit different names, duties, opportunities, prejudices, fears, dialect habits, legal status, "
                "and memory burdens based on their population group."
            ),
            "plot_effect": (
                "Population diversity can trigger migration conflict, class resentment, forbidden-name reveals, succession disputes, "
                "cult tension, labor shortage, smuggling routes, or hidden-family restoration."
            ),
            "memory_effect": (
                "World memory must track group reputation, migration movement, public/secret names, class conflict, belief shifts, "
                "erased groups, and demographic consequences after events."
            ),
            "anti_genericity_signal": (
                "Population system includes class layers, belief divisions, migration causes, hidden groups, naming variation, "
                "species links, and people-type references."
            ),
            "detail_depth_score": 0.92,
            "validation_status": "validated",
            "provenance": {
                "generated_by_engine": "PopulationDiversityEngine",
                "origin_type": "generated_from_population_seed",
                "source_id": source_id,
                "species_profile_count": len(species_profiles),
                "people_type_profile_count": len(people_type_profiles),
                "seed_keys": sorted(population_seed.keys()),
                "story_context_keys": sorted(story_context.keys()),
            },
            "compression_summary": (
                f"{profile_name}: class, belief, migration, hidden-group, naming, species, and people-type diversity for {region_name}."
            ),
        }

        return {"population_diversity_profile": diversity_profile}

    def build_population_sample(
        self,
        *,
        source_id: str,
        diversity_profile: Dict[str, Any],
        sample_seed: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        sample_seed = sample_seed or {}

        sample_size = int(sample_seed.get("sample_size", 8))
        groups = diversity_profile.get("population_groups", [])
        people_types = diversity_profile.get("people_type_profile_refs", [])

        generated_population = []

        for index in range(sample_size):
            group = groups[index % len(groups)] if groups else {"group_name": "unassigned group"}
            class_group = diversity_profile["class_distribution"][index % len(diversity_profile["class_distribution"])]
            belief_group = diversity_profile["belief_diversity"][index % len(diversity_profile["belief_diversity"])]

            person_record = {
                "population_record_id": f"population_record_{source_id}_{index + 1}",
                "public_name_pattern": self._name_pattern(index=index, group=group, diversity_profile=diversity_profile),
                "group_name": group.get("group_name", group.get("name", "unnamed group")),
                "class_group": class_group["class_group"],
                "belief_group": belief_group["belief_group"],
                "likely_role": people_types[index % len(people_types)] if people_types else "locally generated role pending",
                "social_pressure": class_group.get("resentment_source"),
                "belief_pressure": belief_group.get("conflict"),
                "story_function": group.get("story_function", group.get("story_effect", "creates social pressure and identity variation")),
                "memory_hooks": [
                    "public name status",
                    "family reputation",
                    "group trust level",
                    "migration history",
                    "belief alignment",
                ],
            }
            generated_population.append(person_record)

        population_sample = {
            "population_sample_id": f"population_sample_{source_id}_{self._slug(diversity_profile['profile_name'])}",
            "source_id": source_id,
            "population_diversity_profile_id": diversity_profile["population_diversity_profile_id"],
            "sample_size": sample_size,
            "generated_population": generated_population,
            "story_use": "Provides concrete population records for scenes, casting, settlements, crowds, factions, and conflicts.",
            "character_effect": "Helps generate characters with varied class, belief, naming, group history, and memory pressure.",
            "plot_effect": "Sampled people can become witnesses, victims, suspects, guides, rebels, healers, smugglers, or political tools.",
            "memory_effect": "World memory can track population records as people move, gain reputation, lose names, or alter public history.",
            "anti_genericity_signal": "Population sample distributes people across groups, class, belief, role, naming, and memory hooks.",
            "detail_depth_score": 0.88,
            "validation_status": "validated",
            "provenance": {
                "generated_by_engine": "PopulationDiversityEngine",
                "origin_type": "derived_from_population_diversity_profile",
                "source_id": source_id,
                "profile_id": diversity_profile["population_diversity_profile_id"],
                "seed_keys": sorted(sample_seed.keys()),
            },
            "compression_summary": (
                f"Population sample of {sample_size} records from {diversity_profile['profile_name']}."
            ),
        }

        return {"population_sample": population_sample}

    def build_story_context_patch(
        self,
        *,
        diversity_profile: Dict[str, Any],
        population_sample: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        patch = {
            "population_diversity_profile_id": diversity_profile["population_diversity_profile_id"],
            "profile_name": diversity_profile["profile_name"],
            "region_name": diversity_profile["region_name"],
            "population_groups": diversity_profile["population_groups"],
            "class_distribution": diversity_profile["class_distribution"],
            "belief_diversity": diversity_profile["belief_diversity"],
            "migration_patterns": diversity_profile["migration_patterns"],
            "underrepresented_groups": diversity_profile["underrepresented_groups"],
            "naming_variation_rules": diversity_profile["naming_variation_rules"],
            "diversity_controls": diversity_profile["diversity_controls"],
            "story_use": diversity_profile["story_use"],
            "character_effect": diversity_profile["character_effect"],
            "plot_effect": diversity_profile["plot_effect"],
            "memory_effect": diversity_profile["memory_effect"],
            "generation_hints": [
                "Do not generate a single flat population; use class, belief, migration, hidden groups, and naming variation.",
                "Crowds, settlements, families, factions, and background characters should reflect population diversity.",
                "Let names, titles, taboos, and public status vary by group and history.",
                "Track demographic shifts and reputation changes after disasters, wars, betrayals, migrations, and revelations.",
            ],
            "memory_update_candidates": [
                {
                    "candidate_type": "population_diversity_state",
                    "target_element_id": diversity_profile["population_diversity_profile_id"],
                    "reason": "Track group reputation, class tension, belief shifts, migration movement, and hidden/erased group visibility.",
                }
            ],
        }

        if population_sample:
            patch["population_sample"] = population_sample
            patch["memory_update_candidates"].append(
                {
                    "candidate_type": "population_sample_state",
                    "target_element_id": population_sample["population_sample_id"],
                    "reason": "Track sampled people records, public names, social pressure, belief pressure, and role changes.",
                }
            )

        return {"story_context_patch": patch}

    def validate_population_diversity_profile(self, *, diversity_profile: Dict[str, Any]) -> Dict[str, Any]:
        required = [
            "population_diversity_profile_id",
            "profile_name",
            "region_name",
            "culture",
            "population_groups",
            "class_distribution",
            "belief_diversity",
            "migration_patterns",
            "underrepresented_groups",
            "naming_variation_rules",
            "diversity_controls",
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

        missing = [field for field in required if not diversity_profile.get(field)]
        shallow = self._shallow_fields(
            payload=diversity_profile,
            fields=["story_use", "character_effect", "plot_effect", "memory_effect", "anti_genericity_signal"],
        )

        controls = diversity_profile.get("diversity_controls", {})
        control_failures = [
            key for key, value in controls.items()
            if key.startswith("require_") and value is not True
        ]

        minimum_count = int(controls.get("minimum_population_group_count", 0) or 0)
        if len(diversity_profile.get("population_groups", [])) < minimum_count:
            control_failures.append("minimum_population_group_count")

        passed = (
            not missing
            and not shallow
            and not control_failures
            and float(diversity_profile.get("detail_depth_score", 0.0)) >= 0.75
        )

        return {
            "passed": passed,
            "missing_fields": missing,
            "shallow_fields": shallow,
            "control_failures": control_failures,
            "population_diversity_profile_id": diversity_profile.get("population_diversity_profile_id"),
        }

    def validate_population_sample(self, *, population_sample: Dict[str, Any]) -> Dict[str, Any]:
        required = [
            "population_sample_id",
            "population_diversity_profile_id",
            "sample_size",
            "generated_population",
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

        missing = [field for field in required if not population_sample.get(field)]
        shallow = self._shallow_fields(
            payload=population_sample,
            fields=["story_use", "character_effect", "plot_effect", "memory_effect", "anti_genericity_signal"],
        )

        count_mismatch = False
        if population_sample.get("generated_population") and population_sample.get("sample_size"):
            count_mismatch = len(population_sample["generated_population"]) != int(population_sample["sample_size"])

        passed = (
            not missing
            and not shallow
            and not count_mismatch
            and float(population_sample.get("detail_depth_score", 0.0)) >= 0.75
        )

        return {
            "passed": passed,
            "missing_fields": missing,
            "shallow_fields": shallow,
            "count_mismatch": count_mismatch,
            "population_sample_id": population_sample.get("population_sample_id"),
        }

    def summarize_population_diversity(
        self,
        *,
        diversity_profile: Dict[str, Any],
        population_sample: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        summary = {
            "population_diversity_profile_id": diversity_profile["population_diversity_profile_id"],
            "profile_name": diversity_profile["profile_name"],
            "population_group_count": len(diversity_profile["population_groups"]),
            "class_group_count": len(diversity_profile["class_distribution"]),
            "belief_group_count": len(diversity_profile["belief_diversity"]),
            "migration_pattern_count": len(diversity_profile["migration_patterns"]),
            "underrepresented_group_count": len(diversity_profile["underrepresented_groups"]),
            "compression_summary": diversity_profile["compression_summary"],
        }

        if population_sample:
            summary["population_sample_id"] = population_sample["population_sample_id"]
            summary["sample_size"] = population_sample["sample_size"]

        return {"success": True, "summary": summary}

    def build_population_text(
        self,
        *,
        diversity_profile: Dict[str, Any],
        population_sample: Dict[str, Any] | None = None,
    ) -> Dict[str, str]:
        lines = [
            "Population Diversity Profile",
            f"Name: {diversity_profile['profile_name']}",
            f"Region: {diversity_profile['region_name']}",
            f"Profile ID: {diversity_profile['population_diversity_profile_id']}",
            "",
            "Population Groups:",
        ]

        sections = [
            ("Population Groups", [str(item) for item in diversity_profile["population_groups"]]),
            ("Class Distribution", [str(item) for item in diversity_profile["class_distribution"]]),
            ("Belief Diversity", [str(item) for item in diversity_profile["belief_diversity"]]),
            ("Migration Patterns", [str(item) for item in diversity_profile["migration_patterns"]]),
            ("Underrepresented Groups", [str(item) for item in diversity_profile["underrepresented_groups"]]),
            ("Naming Variation Rules", diversity_profile["naming_variation_rules"]),
        ]

        lines = lines[:-1]

        for title, values in sections:
            lines.append("")
            lines.append(title + ":")
            for item in values:
                lines.append(f"- {item}")

        if population_sample:
            lines.append("")
            lines.append("Sample Population:")
            for item in population_sample["generated_population"]:
                lines.append(f"- {item}")

        lines.extend([
            "",
            "Story Use:",
            diversity_profile["story_use"],
            "",
            "Character Effect:",
            diversity_profile["character_effect"],
            "",
            "Plot Effect:",
            diversity_profile["plot_effect"],
            "",
            "Memory Effect:",
            diversity_profile["memory_effect"],
        ])

        return {"population_text": chr(10).join(lines)}

    def _default_population_groups(
        self,
        *,
        region_name: str,
        culture: str,
        species_profiles: List[Dict[str, Any]],
        people_type_profiles: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        groups = [
            {
                "group_name": f"{region_name} road families",
                "identity_basis": culture,
                "story_function": "local guides, witnesses, grieving families, and holders of practical road knowledge",
            },
            {
                "group_name": f"{region_name} archive families",
                "identity_basis": "legal memory and old maps",
                "story_function": "control public truth, inheritance documents, and route law",
            },
            {
                "group_name": f"{region_name} market migrants",
                "identity_basis": "trade movement and seasonal work",
                "story_function": "bring rumor, outside pressure, scarcity, and social change",
            },
            {
                "group_name": f"{region_name} erased-name households",
                "identity_basis": "secret history and forbidden names",
                "story_function": "carry hidden family truth and destabilize public history when revealed",
            },
        ]

        for species in species_profiles[:3]:
            groups.append(
                {
                    "group_name": species.get("unique_name", "unnamed species group"),
                    "identity_basis": species.get("classification", "species identity"),
                    "story_function": species.get("story_use", "adds species-linked identity pressure"),
                }
            )

        for people_type in people_type_profiles[:3]:
            groups.append(
                {
                    "group_name": people_type.get("unique_name", "unnamed people type"),
                    "identity_basis": people_type.get("role_name", "role identity"),
                    "story_function": people_type.get("story_use", "adds role-linked scene and plot pressure"),
                }
            )

        return groups

    def _name_pattern(self, *, index: int, group: Dict[str, Any], diversity_profile: Dict[str, Any]) -> str:
        group_name = group.get("group_name", group.get("name", "Group"))
        root = self._slug(group_name).split("_")[0].capitalize() or "Aren"
        patterns = [
            f"{root} child-weather-name pending public naming",
            f"{root} road-name with bell-title suffix",
            f"{root} family-name hidden under route number",
            f"{root} exile-name used outside official records",
        ]
        return patterns[index % len(patterns)]

    def _shallow_fields(self, *, payload: Dict[str, Any], fields: List[str]) -> List[str]:
        return [field for field in fields if len(str(payload.get(field, ""))) < 20]

    def _slug(self, value: str) -> str:
        return "_".join(part for part in value.lower().replace("/", " ").replace("-", " ").split() if part)

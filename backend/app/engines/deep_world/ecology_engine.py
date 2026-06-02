from __future__ import annotations

from typing import Any, Dict, List

from backend.app.schemas.deep_world import (
    DeepWorldEcologySystem,
    DeepWorldPriority,
    DeepWorldValidationStatus,
)


class EcologyEngine:
    def build_ecology_system(
        self,
        *,
        source_id: str,
        ecology_seed: Dict[str, Any] | None = None,
        story_context: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        ecology_seed = ecology_seed or {}
        story_context = story_context or {}

        name = ecology_seed.get("name", "Saltroot Fogwood Ecology")
        region_name = ecology_seed.get("region_name", story_context.get("region_name", "Saltroot Forest"))
        biome_type = ecology_seed.get("biome_type", "fog-fed salt forest biome")
        keystone_species = ecology_seed.get("keystone_species", ["saltroot trees", "fog moths", "bell-horn deer"])
        primary_resource = ecology_seed.get("primary_resource", "memory-preserving salt bark")
        ecological_pressure = ecology_seed.get("ecological_pressure", "red fog overgrowth after long monsoon")
        collapse_risk = ecology_seed.get("collapse_risk", "saltroot dieback causing medicine shortage and road confusion")
        cultural_dependency = ecology_seed.get(
            "cultural_dependency",
            "bellkeeper families rely on saltroot bark for witness ink, funeral tea, and oath records.",
        )

        food_chain_notes = ecology_seed.get("food_chain_notes", [
            "fog moss feeds glass-wing moths",
            "bell-horn deer graze fog moss and spread saltroot spores",
            "ravine cats hunt deer near old road bells",
            "saltroot trees preserve chemical traces that healers interpret as memory signs",
        ])

        predator_prey_links = ecology_seed.get("predator_prey_links", [
            {
                "predator": "ravine cat",
                "prey": "bell-horn deer",
                "story_effect": "deer migration can expose hidden paths or draw hunters into forbidden ravines.",
            },
            {
                "predator": "fog owl",
                "prey": "glass-wing moth",
                "story_effect": "moth disappearance warns locals that fog poison is rising.",
            },
        ])

        invasive_species_risks = ecology_seed.get("invasive_species_risks", [
            "ash vine can choke young saltroot groves after trade caravans import contaminated rope",
            "red mold spreads through abandoned bell towers during wet seasons",
        ])

        civilization_dependencies = ecology_seed.get("civilization_dependencies", [
            primary_resource,
            cultural_dependency,
            "fog moss medicine supports road guides and winter healers",
            "deer antler bells are used in witness courts and route rituals",
        ])

        ecology = DeepWorldEcologySystem(
            element_id=f"ecology_{source_id}_{self._slug(name)}",
            source_id=source_id,
            name=name,
            summary=(
                f"{name} is a {biome_type} in {region_name}. It depends on "
                f"{', '.join(keystone_species)} and is threatened by {collapse_risk}."
            ),
            priority=DeepWorldPriority.HIGH,
            tags=self._tags(ecology_seed=ecology_seed, story_context=story_context),
            metadata={
                "chunk6_step": "6.5",
                "engine": "EcologyEngine",
                "region_name": region_name,
                "biome_type": biome_type,
                "primary_resource": primary_resource,
                "ecological_pressure": ecological_pressure,
                "collapse_risk": collapse_risk,
                "cultural_dependency": cultural_dependency,
            },
            story_use=(
                "Turns ecology into story pressure by linking resources, species behavior, trade, medicine, "
                "rituals, food scarcity, routes, and environmental collapse to active scene conflict."
            ),
            character_effect=(
                "Characters shaped by this ecology develop survival habits, food memories, medicine knowledge, "
                "animal superstitions, class access to resources, and fears of ecological collapse."
            ),
            plot_effect=(
                "Ecological disruption can trigger famine, disease, migration, trade conflict, ritual failure, "
                "creature movement, hidden route discovery, or political blame."
            ),
            memory_effect=(
                "The simulation must remember species decline, invasive spread, resource shortage, migration shifts, "
                "healer stockpiles, damaged habitats, and who benefits from ecological crisis."
            ),
            validation_status=DeepWorldValidationStatus.VALIDATED,
            provenance={
                "origin_type": "generated_from_ecology_seed",
                "generated_by_engine": "EcologyEngine",
                "source_id": source_id,
                "seed_keys": sorted(ecology_seed.keys()),
                "story_context_keys": sorted(story_context.keys()),
            },
            compression_summary=(
                f"{name}: biome={biome_type}; keystone={', '.join(keystone_species)}; "
                f"pressure={ecological_pressure}; collapse={collapse_risk}."
            ),
            food_chain_notes=food_chain_notes,
            predator_prey_links=predator_prey_links,
            keystone_species=keystone_species,
            invasive_species_risks=invasive_species_risks,
            collapse_risks=[collapse_risk] + ecology_seed.get("extra_collapse_risks", []),
            civilization_dependencies=civilization_dependencies,
        )

        return {"deep_world_ecology_system": ecology}

    def simulate_ecological_shift(
        self,
        *,
        source_id: str,
        ecology: DeepWorldEcologySystem,
        shift_seed: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        shift_seed = shift_seed or {}

        shift_name = shift_seed.get("shift_name", "Saltroot Dieback")
        severity = shift_seed.get("severity", "high")
        trigger = shift_seed.get("trigger", "three wet seasons allowed red mold to spread through old bell towers")
        affected_species = shift_seed.get("affected_species", ecology.keystone_species[:2])
        affected_resources = shift_seed.get("affected_resources", ["salt bark medicine", "witness ink", "fog moss harvest"])
        affected_groups = shift_seed.get("affected_groups", ["road guides", "healers", "bellkeeper families", "route orphans"])

        shift = {
            "ecological_shift_id": f"ecological_shift_{source_id}_{self._slug(shift_name)}",
            "source_id": source_id,
            "ecology_id": ecology.element_id,
            "shift_name": shift_name,
            "severity": severity,
            "trigger": trigger,
            "affected_species": affected_species,
            "affected_resources": affected_resources,
            "affected_groups": affected_groups,
            "story_use": (
                "Creates active ecological crisis that affects food, medicine, trade, ritual authority, "
                "settlement trust, and survival choices."
            ),
            "character_effect": (
                "Characters must respond based on class, profession, faith, local knowledge, hunger, grief, "
                "or responsibility for the ecological damage."
            ),
            "plot_effect": (
                "Can force a journey for medicine, expose corruption in resource control, trigger migration, "
                "or reveal who caused the spread."
            ),
            "memory_effect": (
                "Future world state must remember damaged habitats, affected groups, resource shortages, "
                "species decline, and social blame."
            ),
            "lore_effect": (
                "The crisis may be interpreted as divine punishment, broken oath memory, ancestral warning, "
                "or false history returning through the land."
            ),
            "anti_genericity_signal": (
                "Ecological shift is tied to named species, local resource systems, bell towers, medicine, "
                "class pressure, and lore interpretation."
            ),
            "detail_depth_score": 0.9,
            "validation_status": "validated",
            "provenance": {
                "generated_by_engine": "EcologyEngine",
                "origin_type": "simulated_ecological_shift",
                "source_id": source_id,
                "ecology_id": ecology.element_id,
                "seed_keys": sorted(shift_seed.keys()),
            },
            "compression_summary": (
                f"{shift_name}: severity={severity}; trigger={trigger}; "
                f"species={', '.join(affected_species)}; resources={', '.join(affected_resources)}."
            ),
        }

        return {"ecological_shift": shift}

    def build_story_context_patch(
        self,
        *,
        ecology: DeepWorldEcologySystem,
        ecological_shift: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        patch = {
            "ecology_id": ecology.element_id,
            "ecology_name": ecology.name,
            "food_chain_notes": ecology.food_chain_notes,
            "predator_prey_links": ecology.predator_prey_links,
            "keystone_species": ecology.keystone_species,
            "invasive_species_risks": ecology.invasive_species_risks,
            "collapse_risks": ecology.collapse_risks,
            "civilization_dependencies": ecology.civilization_dependencies,
            "story_use": ecology.story_use,
            "character_effect": ecology.character_effect,
            "plot_effect": ecology.plot_effect,
            "memory_effect": ecology.memory_effect,
            "generation_hints": [
                "Use ecology to create food, medicine, resource, migration, and creature-pressure consequences.",
                "Do not treat plants and animals as decoration; connect them to culture, survival, and plot.",
                "Let ecological changes affect settlements, travel, class tension, religion, and memory.",
                "Track ecological shifts as stateful world memory.",
            ],
            "memory_update_candidates": [
                {
                    "candidate_type": "ecology_state",
                    "target_element_id": ecology.element_id,
                    "reason": "Track species health, resource availability, invasive spread, collapse risk, and civilization dependencies.",
                }
            ],
        }

        if ecological_shift:
            patch["active_ecological_shift"] = ecological_shift
            patch["memory_update_candidates"].append(
                {
                    "candidate_type": "ecological_shift_state",
                    "target_element_id": ecological_shift["ecological_shift_id"],
                    "reason": "Track shift severity, affected species, affected groups, shortages, blame, and recovery.",
                }
            )

        return {"story_context_patch": patch}

    def validate_ecology_system(self, *, ecology: DeepWorldEcologySystem) -> Dict[str, Any]:
        blockers: List[str] = []
        warnings: List[str] = []

        required_lists = {
            "food_chain_notes": ecology.food_chain_notes,
            "predator_prey_links": ecology.predator_prey_links,
            "keystone_species": ecology.keystone_species,
            "invasive_species_risks": ecology.invasive_species_risks,
            "collapse_risks": ecology.collapse_risks,
            "civilization_dependencies": ecology.civilization_dependencies,
        }

        for name, values in required_lists.items():
            if not values:
                blockers.append(f"Ecology system missing {name}.")

        required_text = {
            "story_use": ecology.story_use,
            "character_effect": ecology.character_effect,
            "plot_effect": ecology.plot_effect,
            "memory_effect": ecology.memory_effect,
            "compression_summary": ecology.compression_summary,
        }

        for name, value in required_text.items():
            if not value or len(value.strip()) < 20:
                blockers.append(f"Ecology system has shallow or missing {name}.")

        if len(ecology.keystone_species) < 2:
            warnings.append("Ecology has fewer than two keystone species.")

        passed = not blockers

        return {
            "passed": passed,
            "blockers": blockers,
            "warnings": warnings,
            "ecology_id": ecology.element_id,
            "ecology_name": ecology.name,
        }

    def validate_ecological_shift(self, *, ecological_shift: Dict[str, Any]) -> Dict[str, Any]:
        required = [
            "ecological_shift_id",
            "shift_name",
            "affected_species",
            "affected_resources",
            "affected_groups",
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

        missing = [field for field in required if not ecological_shift.get(field)]
        shallow = []

        for field in ["story_use", "character_effect", "plot_effect", "memory_effect", "lore_effect"]:
            if len(str(ecological_shift.get(field, ""))) < 20:
                shallow.append(field)

        passed = not missing and not shallow and float(ecological_shift.get("detail_depth_score", 0.0)) >= 0.75

        return {
            "passed": passed,
            "missing_fields": missing,
            "shallow_fields": shallow,
            "ecological_shift_id": ecological_shift.get("ecological_shift_id"),
        }

    def summarize_ecology_system(self, *, ecology: DeepWorldEcologySystem) -> Dict[str, Any]:
        return {
            "success": True,
            "summary": {
                "ecology_id": ecology.element_id,
                "name": ecology.name,
                "keystone_species_count": len(ecology.keystone_species),
                "food_chain_note_count": len(ecology.food_chain_notes),
                "predator_prey_link_count": len(ecology.predator_prey_links),
                "collapse_risk_count": len(ecology.collapse_risks),
                "civilization_dependency_count": len(ecology.civilization_dependencies),
                "compression_summary": ecology.compression_summary,
            },
        }

    def build_ecology_text(self, *, ecology: DeepWorldEcologySystem) -> Dict[str, str]:
        lines = [
            "Deep World Ecology System",
            f"Name: {ecology.name}",
            f"ID: {ecology.element_id}",
            "",
            "Summary:",
            ecology.summary,
            "",
            "Keystone Species:",
        ]

        for item in ecology.keystone_species:
            lines.append(f"- {item}")

        sections = [
            ("Food Chain Notes", ecology.food_chain_notes),
            ("Predator / Prey Links", [str(item) for item in ecology.predator_prey_links]),
            ("Invasive Species Risks", ecology.invasive_species_risks),
            ("Collapse Risks", ecology.collapse_risks),
            ("Civilization Dependencies", ecology.civilization_dependencies),
        ]

        for title, values in sections:
            lines.append("")
            lines.append(title + ":")
            for item in values:
                lines.append(f"- {item}")

        lines.extend([
            "",
            "Story Use:",
            ecology.story_use,
            "",
            "Character Effect:",
            ecology.character_effect,
            "",
            "Plot Effect:",
            ecology.plot_effect,
            "",
            "Memory Effect:",
            ecology.memory_effect,
        ])

        return {"ecology_text": chr(10).join(lines)}

    def _tags(self, *, ecology_seed: Dict[str, Any], story_context: Dict[str, Any]) -> List[str]:
        tags = ["chunk6", "deep_world", "ecology", "food_chain", "story_ecology"]

        for key in ["genre", "tone", "world_type", "region_name"]:
            if story_context.get(key):
                tags.append(str(story_context[key]))

        for item in ecology_seed.get("tags", []):
            tags.append(str(item))

        return sorted({tag.strip().lower() for tag in tags if tag and str(tag).strip()})

    def _slug(self, value: str) -> str:
        return "_".join(part for part in value.lower().replace("/", " ").replace("-", " ").split() if part)

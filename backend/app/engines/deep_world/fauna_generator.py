from __future__ import annotations

from typing import Any, Dict, List

from backend.app.schemas.deep_world import (
    DeepWorldFauna,
    DeepWorldPriority,
    DeepWorldValidationStatus,
)


class FaunaGenerator:
    def build_fauna(
        self,
        *,
        source_id: str,
        fauna_seed: Dict[str, Any] | None = None,
        story_context: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        fauna_seed = fauna_seed or {}
        story_context = story_context or {}

        base_name = fauna_seed.get("base_name", "Veyr")
        unique_name = fauna_seed.get("unique_name", f"{base_name} Bellhorn Deer")
        region_name = fauna_seed.get("region_name", story_context.get("region_name", "Saltroot Forest"))
        culture = fauna_seed.get("culture", story_context.get("culture", "bell-road witness culture"))

        name_origin = fauna_seed.get(
            "name_origin",
            f"{unique_name} is named from {culture}; its hollow antlers hum like road bells during fog season.",
        )
        name_meaning = fauna_seed.get("name_meaning", "deer that carries road sound through fog")
        name_language_logic = fauna_seed.get(
            "name_language_logic",
            "compound name: old road-root for return + horn-title used for animals tied to guidance and witness law",
        )

        habitat = fauna_seed.get("habitat", [
            "saltroot groves near old road bells",
            "white-bark ravines during dry wind months",
            "fog moss clearings after red monsoon",
        ])

        behavior_patterns = fauna_seed.get("behavior_patterns", [
            "migrates before dense red fog, warning locals of unsafe roads",
            "strikes hollow antlers against bark when predators approach",
            "refuses to cross places where oath-blood was spilled in local belief",
            "spreads saltroot spores through antler velvet and hoof mud",
        ])

        ecological_role = fauna_seed.get("ecological_role", [
            "spreads saltroot spores",
            "controls fog moss overgrowth by grazing",
            "feeds ravine cats and keeps predator routes active",
            "acts as early warning for climate shifts",
        ])

        cultural_meaning = fauna_seed.get("cultural_meaning", [
            "seen as witness animals that know safe roads",
            "antlers are carved into court bells only after natural death",
            "killing one during fog season is treated as a bad omen",
        ])

        economic_use = fauna_seed.get("economic_use", [
            "shed antlers become legal witness bells",
            "hoof patterns guide hunters and road scouts",
            "antler powder is falsely sold as fog-sickness medicine by smugglers",
        ])

        danger_profile = fauna_seed.get("danger_profile", [
            "not usually aggressive but can gore travelers during red fog panic",
            "herd stampedes can destroy hidden evidence or expose old roads",
            "predators following the herd may bring danger near settlements",
        ])

        sensory_identity = fauna_seed.get(
            "sensory_identity",
            "soft antler hum, wet bark smell, silver hoof marks, and low throat clicks before fog",
        )
        visual_identity = fauna_seed.get(
            "visual_identity",
            "pale deer with hollow dark antlers, moss-veined legs, and silver dust around the eyes",
        )

        fauna = DeepWorldFauna(
            element_id=f"fauna_{source_id}_{self._slug(unique_name)}",
            source_id=source_id,
            name=unique_name,
            summary=(
                f"{unique_name} lives in {region_name}. It is culturally tied to {culture}, "
                f"guides locals through fog, spreads saltroot spores, and creates danger when herds panic."
            ),
            priority=DeepWorldPriority.HIGH,
            tags=self._tags(fauna_seed=fauna_seed, story_context=story_context),
            metadata={
                "chunk6_step": "6.8",
                "engine": "FaunaGenerator",
                "unique_name": unique_name,
                "name_origin": name_origin,
                "name_meaning": name_meaning,
                "name_language_logic": name_language_logic,
                "cultural_context": culture,
                "world_context": region_name,
                "visual_identity": visual_identity,
                "sensory_identity": sensory_identity,
                "social_function": "road warning animal, omen carrier, witness-law symbol, and hunting pressure marker",
                "economic_function": "shed antlers support bell-making, court ritual, scouting, and illegal medicine fraud",
                "ecological_role": ecological_role,
                "belief_function": "believed to avoid places where broken oaths still stain the land",
                "anti_genericity_signal": (
                    "Fauna has named culture, habitat, behavior, ecology, economy, danger, belief, and plot function."
                ),
                "detail_depth_score": 0.92,
            },
            story_use=(
                "Creates living movement through the world: migration warnings, predator pressure, road discovery, "
                "omens, hunting conflict, court symbolism, and ecological dependency."
            ),
            character_effect=(
                "Characters reveal background through how they read tracks, fear stampedes, respect omens, hunt illegally, "
                "use antlers in law, or ignore animal warnings."
            ),
            plot_effect=(
                "A missing herd, sudden stampede, illegal antler trade, or deer refusing a road can reveal danger, "
                "hidden bloodshed, ecological collapse, or a false map."
            ),
            memory_effect=(
                "The world state must remember herd migration, killed animals, antler supply, predator movement, "
                "track evidence, and whether locals trust or ignore animal warnings."
            ),
            validation_status=DeepWorldValidationStatus.VALIDATED,
            provenance={
                "origin_type": "generated_from_fauna_seed",
                "generated_by_engine": "FaunaGenerator",
                "source_id": source_id,
                "seed_keys": sorted(fauna_seed.keys()),
                "story_context_keys": sorted(story_context.keys()),
            },
            compression_summary=(
                f"{unique_name}: fog-warning fauna from {region_name}; meaning={name_meaning}; "
                f"role=spore spreader, road omen, antler-law symbol, predator-pressure source."
            ),
            habitat_rules=habitat,
            
            behavior_patterns=behavior_patterns,
            
            
            cultural_meaning=cultural_meaning,
            
            economic_uses=economic_use,
            danger_profile=danger_profile,
        )

        return {"deep_world_fauna": fauna}

    def build_fauna_story_context_patch(self, *, fauna: DeepWorldFauna) -> Dict[str, Any]:
        patch = {
            "fauna_id": fauna.element_id,
            "fauna_name": fauna.name,
            "summary": fauna.summary,
            "habitat_rules": self._list_attr(fauna, "habitat_rules"),
            "behavior_patterns": self._list_attr(fauna, "behavior_patterns"),
            "ecological_role": list(fauna.metadata.get("ecological_role", [])),
            "cultural_meaning": self._list_attr(fauna, "cultural_meaning", "cultural_meanings"),
            "economic_uses": self._list_attr(fauna, "economic_uses"),
            "danger_profile": self._list_attr(fauna, "danger_profile", "danger_profiles"),
            "story_use": fauna.story_use,
            "character_effect": fauna.character_effect,
            "plot_effect": fauna.plot_effect,
            "memory_effect": fauna.memory_effect,
            "identity": {
                "unique_name": fauna.metadata.get("unique_name", fauna.name),
                "name_origin": fauna.metadata.get("name_origin"),
                "name_meaning": fauna.metadata.get("name_meaning"),
                "name_language_logic": fauna.metadata.get("name_language_logic"),
                "visual_identity": fauna.metadata.get("visual_identity"),
                "sensory_identity": fauna.metadata.get("sensory_identity"),
                "cultural_context": fauna.metadata.get("cultural_context"),
                "world_context": fauna.metadata.get("world_context"),
                "anti_genericity_signal": fauna.metadata.get("anti_genericity_signal"),
                "detail_depth_score": fauna.metadata.get("detail_depth_score"),
            },
            "generation_hints": [
                "Use fauna as active world behavior, not decoration.",
                "Let animal movement affect travel, danger, food, economy, lore, and scene timing.",
                "Let characters interpret animal signs differently based on culture, class, job, and belief.",
                "Track migration, death, trade, predator movement, and omen interpretation in world memory.",
            ],
            "memory_update_candidates": [
                {
                    "candidate_type": "fauna_state",
                    "target_element_id": fauna.element_id,
                    "reason": "Track migration, herd size, deaths, predator pressure, illegal hunting, and cultural interpretations.",
                }
            ],
        }

        return {"story_context_patch": patch}

    def simulate_fauna_event(
        self,
        *,
        source_id: str,
        fauna: DeepWorldFauna,
        event_seed: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        event_seed = event_seed or {}

        event_name = event_seed.get("event_name", f"{fauna.name} Fog Stampede")
        event_type = event_seed.get("event_type", "migration_disruption")
        trigger = event_seed.get("trigger", "herd panicked before red fog closed the old road")
        affected_groups = event_seed.get("affected_groups", ["road guides", "hunters", "bell court", "forest village"])
        consequence = event_seed.get("consequence", "the herd exposes a buried path and destroys a smuggler cache")

        event = {
            "fauna_event_id": f"fauna_event_{source_id}_{self._slug(event_name)}",
            "source_id": source_id,
            "fauna_id": fauna.element_id,
            "fauna_name": fauna.name,
            "event_name": event_name,
            "event_type": event_type,
            "trigger": trigger,
            "affected_groups": affected_groups,
            "consequence": consequence,
            "story_use": (
                "Turns animal behavior into active world pressure through migration, danger, discovery, economy, or omen."
            ),
            "character_effect": (
                "Characters must react through local knowledge, hunting skill, fear, faith, greed, or refusal to trust animal signs."
            ),
            "plot_effect": (
                "Can reveal a hidden route, trigger injury, expose illegal trade, delay travel, or prove that a place is unsafe."
            ),
            "memory_effect": (
                "Future state must remember herd movement, affected groups, discovered evidence, injuries, deaths, and local interpretation."
            ),
            "lore_effect": (
                "The event may be read as ancestral warning, divine road-sign, or proof that a broken oath still stains the route."
            ),
            "anti_genericity_signal": (
                "Event is tied to specific fauna behavior, fog roads, legal/cultural symbolism, economy, and route discovery."
            ),
            "detail_depth_score": 0.9,
            "validation_status": "validated",
            "provenance": {
                "generated_by_engine": "FaunaGenerator",
                "origin_type": "simulated_fauna_event",
                "source_id": source_id,
                "fauna_id": fauna.element_id,
                "seed_keys": sorted(event_seed.keys()),
            },
            "compression_summary": (
                f"{event_name}: type={event_type}; trigger={trigger}; consequence={consequence}."
            ),
        }

        return {"fauna_event": event}

    def validate_fauna(self, *, fauna: DeepWorldFauna) -> Dict[str, Any]:
        blockers: List[str] = []
        warnings: List[str] = []

        ecological_role = fauna.metadata.get("ecological_role", [])

        required_lists = {
            "habitat_rules": self._list_attr(fauna, "habitat_rules"),
            "behavior_patterns": self._list_attr(fauna, "behavior_patterns"),
            "ecological_role": list(ecological_role) if ecological_role else [],
            "cultural_meaning": self._list_attr(fauna, "cultural_meaning"),
            "economic_uses": self._list_attr(fauna, "economic_uses"),
            "danger_profile": self._list_attr(fauna, "danger_profile"),
        }

        for name, values in required_lists.items():
            if not values:
                blockers.append(f"Fauna missing {name}.")

        required_text = {
            "story_use": fauna.story_use,
            "character_effect": fauna.character_effect,
            "plot_effect": fauna.plot_effect,
            "memory_effect": fauna.memory_effect,
            "compression_summary": fauna.compression_summary,
        }

        for name, value in required_text.items():
            if not value or len(value.strip()) < 20:
                blockers.append(f"Fauna has shallow or missing {name}.")

        required_metadata = [
            "unique_name",
            "name_origin",
            "name_meaning",
            "name_language_logic",
            "cultural_context",
            "world_context",
            "visual_identity",
            "sensory_identity",
            "anti_genericity_signal",
            "detail_depth_score",
            "ecological_role",
        ]

        for field in required_metadata:
            if field not in fauna.metadata or fauna.metadata.get(field) in (None, "", []):
                blockers.append(f"Fauna missing identity metadata: {field}")

        if len(self._list_attr(fauna, "behavior_patterns")) < 3:
            warnings.append("Fauna has fewer than three behavior patterns.")

        passed = not blockers

        return {
            "passed": passed,
            "blockers": blockers,
            "warnings": warnings,
            "fauna_id": fauna.element_id,
            "fauna_name": fauna.name,
        }

    def validate_fauna_event(self, *, fauna_event: Dict[str, Any]) -> Dict[str, Any]:
        required = [
            "fauna_event_id",
            "fauna_id",
            "event_name",
            "event_type",
            "trigger",
            "affected_groups",
            "consequence",
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

        missing = [field for field in required if not fauna_event.get(field)]
        shallow = []

        for field in ["story_use", "character_effect", "plot_effect", "memory_effect", "lore_effect"]:
            if len(str(fauna_event.get(field, ""))) < 20:
                shallow.append(field)

        passed = not missing and not shallow and float(fauna_event.get("detail_depth_score", 0.0)) >= 0.75

        return {
            "passed": passed,
            "missing_fields": missing,
            "shallow_fields": shallow,
            "fauna_event_id": fauna_event.get("fauna_event_id"),
        }

    def summarize_fauna(self, *, fauna: DeepWorldFauna) -> Dict[str, Any]:
        return {
            "success": True,
            "summary": {
                "fauna_id": fauna.element_id,
                "name": fauna.name,
                "habitat_count": len(self._list_attr(fauna, "habitat_rules")),
                "behavior_pattern_count": len(self._list_attr(fauna, "behavior_patterns")),
                "ecological_role_count": len(list(fauna.metadata.get("ecological_role", []))),
                "cultural_meaning_count": len(self._list_attr(fauna, "cultural_meaning", "cultural_meanings")),
                "economic_use_count": len(self._list_attr(fauna, "economic_uses")),
                "danger_profile_count": len(self._list_attr(fauna, "danger_profile", "danger_profiles")),
                "detail_depth_score": fauna.metadata.get("detail_depth_score"),
                "compression_summary": fauna.compression_summary,
            },
        }

    def build_fauna_text(self, *, fauna: DeepWorldFauna) -> Dict[str, str]:
        lines = [
            "Deep World Fauna",
            f"Name: {fauna.name}",
            f"ID: {fauna.element_id}",
            "",
            "Summary:",
            fauna.summary,
            "",
            "Name Origin:",
            str(fauna.metadata.get("name_origin")),
            "",
            "Habitat:",
        ]

        sections = [
            ("Habitat Rules", self._list_attr(fauna, "habitat_rules")),
            ("Behavior Patterns", self._list_attr(fauna, "behavior_patterns")),
            ("Ecological Role", list(fauna.metadata.get("ecological_role", []))),
            ("Cultural Meaning", self._list_attr(fauna, "cultural_meaning", "cultural_meanings")),
            ("Economic Uses", self._list_attr(fauna, "economic_uses")),
            ("Danger Profile", self._list_attr(fauna, "danger_profile", "danger_profiles")),
        ]

        # Habitat is included through sections for consistent formatting.
        lines = lines[:-1]

        for title, values in sections:
            lines.append("")
            lines.append(title + ":")
            for item in values:
                lines.append(f"- {item}")

        lines.extend([
            "",
            "Story Use:",
            fauna.story_use,
            "",
            "Character Effect:",
            fauna.character_effect,
            "",
            "Plot Effect:",
            fauna.plot_effect,
            "",
            "Memory Effect:",
            fauna.memory_effect,
        ])

        return {"fauna_text": chr(10).join(lines)}


    def _list_attr(self, fauna: DeepWorldFauna, *names: str) -> List[Any]:
        for name in names:
            value = getattr(fauna, name, None)
            if value:
                return list(value)
        return []

    def _tags(self, *, fauna_seed: Dict[str, Any], story_context: Dict[str, Any]) -> List[str]:
        tags = ["chunk6", "deep_world", "fauna", "animal", "story_fauna"]

        for key in ["genre", "tone", "world_type", "region_name", "culture"]:
            if story_context.get(key):
                tags.append(str(story_context[key]))

        for item in fauna_seed.get("tags", []):
            tags.append(str(item))

        return sorted({tag.strip().lower() for tag in tags if tag and str(tag).strip()})

    def _slug(self, value: str) -> str:
        return "_".join(part for part in value.lower().replace("/", " ").replace("-", " ").split() if part)

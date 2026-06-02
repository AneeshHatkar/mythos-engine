from __future__ import annotations

from typing import Any, Dict, List

from backend.app.schemas.deep_world import (
    DeepWorldFlora,
    DeepWorldPriority,
    DeepWorldValidationStatus,
)


class FloraGenerator:
    def build_flora(
        self,
        *,
        source_id: str,
        flora_seed: Dict[str, Any] | None = None,
        story_context: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        flora_seed = flora_seed or {}
        story_context = story_context or {}

        base_name = flora_seed.get("base_name", "Velmarin")
        unique_name = flora_seed.get("unique_name", f"{base_name} Ashbloom")
        region_name = flora_seed.get("region_name", story_context.get("region_name", "Saltroot Forest"))
        culture = flora_seed.get("culture", story_context.get("culture", "bell-road mourning culture"))

        name_origin = flora_seed.get(
            "name_origin",
            f"{unique_name} is named from an old {culture} grief-word and its habit of blooming after ashfall or heavy salt rain.",
        )
        name_meaning = flora_seed.get("name_meaning", "grief-light bloom that appears after ruined weather")
        name_language_logic = flora_seed.get(
            "name_language_logic",
            "compound name: old mourning root + bloom suffix used for plants tied to death rites or memory rites",
        )

        lifecycle = flora_seed.get("lifecycle", {
            "sprouting_condition": "sprouts after ashfall mixes with salt-heavy rain",
            "blooming_season": "first cold dawn after Red Fog Monsoon",
            "dormancy": "sleeps under salt bark during dry wind months",
            "reproduction": "spores cling to funeral cloth and deer antlers",
            "death_cycle": "petals blacken when exposed to certain poisons or oath-blood",
        })

        uses = flora_seed.get("uses", [
            "funeral tea for mourning households",
            "poison detection in witness courts",
            "blue dye for oath ribbons",
            "medicine for fog-sickness tremors",
        ])

        medicinal_effects = flora_seed.get("medicinal_effects", [
            "calms fog-sickness tremors when brewed correctly",
            "reduces fever after salt rain exposure",
            "dangerous in high dose because it slows breathing",
        ])

        ritual_uses = flora_seed.get("ritual_uses", [
            "placed on witness bells after wrongful death",
            "burned during false-history confession rites",
            "woven into mourning cuffs for road orphans",
        ])

        ecological_dependencies = flora_seed.get("ecological_dependencies", [
            "requires ashfall or mineral-heavy storm soil",
            "depends on bell-horn deer to spread dormant spores",
            "fails when red mold overruns old bell towers",
        ])

        toxicity = flora_seed.get(
            "toxicity",
            "safe as tea only after silver veins are removed; raw petals can cause memory flashes and slowed breathing",
        )
        trade_value = flora_seed.get(
            "trade_value",
            "high value among healers, courts, funeral guilds, and smugglers seeking poison-proof testimony",
        )

        visual_identity = flora_seed.get(
            "visual_identity",
            "black stem, pale blue petals, ash-dusted leaves, and silver veins that glow near poison",
        )
        sensory_identity = flora_seed.get(
            "sensory_identity",
            "smells like rain on cold stone with a bitter smoke aftertaste",
        )

        flora = DeepWorldFlora(
            element_id=f"flora_{source_id}_{self._slug(unique_name)}",
            source_id=source_id,
            name=unique_name,
            summary=(
                f"{unique_name} grows in {region_name}. It is tied to {culture}, "
                f"blooms after ash or salt rain, and is used for mourning, medicine, poison detection, and oath rituals."
            ),
            priority=DeepWorldPriority.HIGH,
            tags=self._tags(flora_seed=flora_seed, story_context=story_context),
            metadata={
                "chunk6_step": "6.6",
                "engine": "FloraGenerator",
                "unique_name": unique_name,
                "name_origin": name_origin,
                "name_meaning": name_meaning,
                "name_language_logic": name_language_logic,
                "cultural_context": culture,
                "world_context": region_name,
                "visual_identity": visual_identity,
                "sensory_identity": sensory_identity,
                "social_function": "mourning marker, court evidence tool, healer resource, and black-market object",
                "economic_function": trade_value,
                "belief_function": "believed to darken when the dead were betrayed or poisoned",
                "anti_genericity_signal": (
                    "Flora has named culture, lifecycle, trade, medicine, ritual, toxicity, ecology, and plot function."
                ),
                "detail_depth_score": 0.92,
            },
            story_use=(
                "Creates evidence, mourning ritual, medicine scarcity, black-market trade, and symbolic scene detail. "
                "Its petals can reveal poison or hidden betrayal."
            ),
            character_effect=(
                "Characters from ashfall or saltroot regions associate its smell with funerals, family grief, "
                "court truth, healer debt, and childhood loss."
            ),
            plot_effect=(
                "A missing harvest, blackened petal, stolen seed pouch, or forbidden funeral tea can reveal poisoning, "
                "resource corruption, illegal trade, or a hidden death."
            ),
            memory_effect=(
                "The world state must remember bloom season, harvest damage, poison reactions, who controls supply, "
                "and whether fields were burned, stolen, protected, or contaminated."
            ),
            validation_status=DeepWorldValidationStatus.VALIDATED,
            provenance={
                "origin_type": "generated_from_flora_seed",
                "generated_by_engine": "FloraGenerator",
                "source_id": source_id,
                "seed_keys": sorted(flora_seed.keys()),
                "story_context_keys": sorted(story_context.keys()),
            },
            compression_summary=(
                f"{unique_name}: mourning/medicine flora from {region_name}; "
                f"meaning={name_meaning}; use=poison detection, funeral rites, fog-sickness medicine."
            ),
            lifecycle=lifecycle,
            uses=uses,
            toxicity=toxicity,
            medicinal_effects=medicinal_effects,
            ritual_uses=ritual_uses,
            trade_value=trade_value,
            ecological_dependencies=ecological_dependencies,
        )

        return {"deep_world_flora": flora}

    def build_flora_story_context_patch(self, *, flora: DeepWorldFlora) -> Dict[str, Any]:
        patch = {
            "flora_id": flora.element_id,
            "flora_name": flora.name,
            "summary": flora.summary,
            "lifecycle": flora.lifecycle,
            "uses": flora.uses,
            "toxicity": flora.toxicity,
            "medicinal_effects": flora.medicinal_effects,
            "ritual_uses": flora.ritual_uses,
            "trade_value": flora.trade_value,
            "ecological_dependencies": flora.ecological_dependencies,
            "story_use": flora.story_use,
            "character_effect": flora.character_effect,
            "plot_effect": flora.plot_effect,
            "memory_effect": flora.memory_effect,
            "identity": {
                "unique_name": flora.metadata.get("unique_name", flora.name),
                "name_origin": flora.metadata.get("name_origin"),
                "name_meaning": flora.metadata.get("name_meaning"),
                "name_language_logic": flora.metadata.get("name_language_logic"),
                "visual_identity": flora.metadata.get("visual_identity"),
                "sensory_identity": flora.metadata.get("sensory_identity"),
                "cultural_context": flora.metadata.get("cultural_context"),
                "world_context": flora.metadata.get("world_context"),
                "anti_genericity_signal": flora.metadata.get("anti_genericity_signal"),
                "detail_depth_score": flora.metadata.get("detail_depth_score"),
            },
            "generation_hints": [
                "Use flora as more than decoration; connect it to medicine, ritual, economy, evidence, and memory.",
                "Let characters react based on culture, class, profession, grief history, or healer knowledge.",
                "Track harvest damage, bloom season, poison reactions, and supply control in world memory.",
                "Use sensory identity naturally in scene prose.",
            ],
            "memory_update_candidates": [
                {
                    "candidate_type": "flora_state",
                    "target_element_id": flora.element_id,
                    "reason": "Track bloom season, harvest quantity, contamination, ownership, ritual use, and poison reactions.",
                }
            ],
        }

        return {"story_context_patch": patch}

    def simulate_flora_event(
        self,
        *,
        source_id: str,
        flora: DeepWorldFlora,
        event_seed: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        event_seed = event_seed or {}

        event_name = event_seed.get("event_name", f"{flora.name} Blackening")
        event_type = event_seed.get("event_type", "poison_reaction")
        trigger = event_seed.get("trigger", "petals darkened during a funeral tea rite")
        affected_groups = event_seed.get("affected_groups", ["mourning family", "healers", "witness court", "smugglers"])
        consequence = event_seed.get("consequence", "a supposedly natural death becomes suspicious")

        event = {
            "flora_event_id": f"flora_event_{source_id}_{self._slug(event_name)}",
            "source_id": source_id,
            "flora_id": flora.element_id,
            "flora_name": flora.name,
            "event_name": event_name,
            "event_type": event_type,
            "trigger": trigger,
            "affected_groups": affected_groups,
            "consequence": consequence,
            "story_use": "Turns a plant property into active evidence, ritual pressure, scarcity, or social conflict.",
            "character_effect": (
                "Characters must respond through grief, guilt, healer expertise, family loyalty, fear of accusation, "
                "or economic desperation."
            ),
            "plot_effect": (
                "Can expose poisoning, reveal smuggling, force testimony, create shortage, or connect a death to older lore."
            ),
            "memory_effect": (
                "Future state must remember the event, affected groups, supply changes, accusation trail, and ritual consequence."
            ),
            "lore_effect": (
                "The event may be interpreted as the dead refusing silence, a god's warning, or proof of false history."
            ),
            "anti_genericity_signal": "Event uses specific flora lifecycle/property and connects it to culture, law, grief, and plot.",
            "detail_depth_score": 0.9,
            "validation_status": "validated",
            "provenance": {
                "generated_by_engine": "FloraGenerator",
                "origin_type": "simulated_flora_event",
                "source_id": source_id,
                "flora_id": flora.element_id,
                "seed_keys": sorted(event_seed.keys()),
            },
            "compression_summary": (
                f"{event_name}: type={event_type}; trigger={trigger}; consequence={consequence}."
            ),
        }

        return {"flora_event": event}

    def validate_flora(self, *, flora: DeepWorldFlora) -> Dict[str, Any]:
        blockers: List[str] = []
        warnings: List[str] = []

        required_lists = {
            "uses": flora.uses,
            "medicinal_effects": flora.medicinal_effects,
            "ritual_uses": flora.ritual_uses,
            "ecological_dependencies": flora.ecological_dependencies,
        }

        for name, values in required_lists.items():
            if not values:
                blockers.append(f"Flora missing {name}.")

        if not flora.lifecycle:
            blockers.append("Flora missing lifecycle.")
        if not flora.toxicity:
            warnings.append("Flora has no toxicity note.")
        if not flora.trade_value:
            warnings.append("Flora has no trade value.")

        required_text = {
            "story_use": flora.story_use,
            "character_effect": flora.character_effect,
            "plot_effect": flora.plot_effect,
            "memory_effect": flora.memory_effect,
            "compression_summary": flora.compression_summary,
        }

        for name, value in required_text.items():
            if not value or len(value.strip()) < 20:
                blockers.append(f"Flora has shallow or missing {name}.")

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
        ]

        for field in required_metadata:
            if field not in flora.metadata:
                blockers.append(f"Flora missing identity metadata: {field}")

        passed = not blockers

        return {
            "passed": passed,
            "blockers": blockers,
            "warnings": warnings,
            "flora_id": flora.element_id,
            "flora_name": flora.name,
        }

    def validate_flora_event(self, *, flora_event: Dict[str, Any]) -> Dict[str, Any]:
        required = [
            "flora_event_id",
            "flora_id",
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

        missing = [field for field in required if not flora_event.get(field)]
        shallow = []

        for field in ["story_use", "character_effect", "plot_effect", "memory_effect", "lore_effect"]:
            if len(str(flora_event.get(field, ""))) < 20:
                shallow.append(field)

        passed = not missing and not shallow and float(flora_event.get("detail_depth_score", 0.0)) >= 0.75

        return {
            "passed": passed,
            "missing_fields": missing,
            "shallow_fields": shallow,
            "flora_event_id": flora_event.get("flora_event_id"),
        }

    def summarize_flora(self, *, flora: DeepWorldFlora) -> Dict[str, Any]:
        return {
            "success": True,
            "summary": {
                "flora_id": flora.element_id,
                "name": flora.name,
                "use_count": len(flora.uses),
                "medicinal_effect_count": len(flora.medicinal_effects),
                "ritual_use_count": len(flora.ritual_uses),
                "ecological_dependency_count": len(flora.ecological_dependencies),
                "detail_depth_score": flora.metadata.get("detail_depth_score"),
                "compression_summary": flora.compression_summary,
            },
        }

    def build_flora_text(self, *, flora: DeepWorldFlora) -> Dict[str, str]:
        lines = [
            "Deep World Flora",
            f"Name: {flora.name}",
            f"ID: {flora.element_id}",
            "",
            "Summary:",
            flora.summary,
            "",
            "Name Origin:",
            str(flora.metadata.get("name_origin")),
            "",
            "Lifecycle:",
        ]

        for key, value in flora.lifecycle.items():
            lines.append(f"- {key}: {value}")

        sections = [
            ("Uses", flora.uses),
            ("Medicinal Effects", flora.medicinal_effects),
            ("Ritual Uses", flora.ritual_uses),
            ("Ecological Dependencies", flora.ecological_dependencies),
        ]

        for title, values in sections:
            lines.append("")
            lines.append(title + ":")
            for item in values:
                lines.append(f"- {item}")

        lines.extend([
            "",
            "Toxicity:",
            str(flora.toxicity),
            "",
            "Trade Value:",
            str(flora.trade_value),
            "",
            "Story Use:",
            flora.story_use,
            "",
            "Character Effect:",
            flora.character_effect,
            "",
            "Plot Effect:",
            flora.plot_effect,
            "",
            "Memory Effect:",
            flora.memory_effect,
        ])

        return {"flora_text": chr(10).join(lines)}

    def _tags(self, *, flora_seed: Dict[str, Any], story_context: Dict[str, Any]) -> List[str]:
        tags = ["chunk6", "deep_world", "flora", "plant", "story_flora"]

        for key in ["genre", "tone", "world_type", "region_name", "culture"]:
            if story_context.get(key):
                tags.append(str(story_context[key]))

        for item in flora_seed.get("tags", []):
            tags.append(str(item))

        return sorted({tag.strip().lower() for tag in tags if tag and str(tag).strip()})

    def _slug(self, value: str) -> str:
        return "_".join(part for part in value.lower().replace("/", " ").replace("-", " ").split() if part)

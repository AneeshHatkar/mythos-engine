from __future__ import annotations

from typing import Any, Dict, List

from backend.app.schemas.deep_world import (
    DeepWorldPriority,
    DeepWorldRegion,
    DeepWorldValidationStatus,
)


class GeographyTerrainEngine:
    def build_region(
        self,
        *,
        source_id: str,
        region_seed: Dict[str, Any] | None = None,
        story_context: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        region_seed = region_seed or {}
        story_context = story_context or {}

        name = region_seed.get("name") or "Saltroot Forest"
        dominant_terrain = region_seed.get("dominant_terrain") or "memory-preserving salt forest"
        climate = region_seed.get("climate") or "silver fog season and dry salt winds"
        danger = region_seed.get("danger") or "memory sickness during dense fog"
        secret = region_seed.get("secret") or "a buried oath road under the oldest trees"
        settlement_logic = region_seed.get("settlement_logic") or "villages form only around bell towers that guide travelers"
        plot_pressure = region_seed.get("plot_pressure") or "fog can close routes and delay rescue, trade, and war movement"

        region = DeepWorldRegion(
            element_id=f"region_{source_id}_{self._slug(name)}",
            source_id=source_id,
            name=name,
            summary=(
                f"{name} is a {dominant_terrain} shaped by {climate}. "
                f"Its core danger is {danger}, and its hidden world layer contains {secret}."
            ),
            priority=DeepWorldPriority.HIGH,
            tags=self._tags(region_seed=region_seed, story_context=story_context),
            metadata={
                "dominant_terrain": dominant_terrain,
                "settlement_logic": settlement_logic,
                "chunk6_step": "6.2",
                "engine": "GeographyTerrainEngine",
            },
            story_use=(
                f"Provides a physical world region where terrain, fog, routes, secrets, and settlements directly affect scenes. "
                f"Primary plot pressure: {plot_pressure}."
            ),
            character_effect=(
                "Characters from this region develop terrain-shaped habits, local fears, route knowledge, "
                "weather metaphors, and survival instincts."
            ),
            plot_effect=(
                f"Geography can create delays, ambushes, isolation, discovery gates, and impossible travel constraints. "
                f"{plot_pressure}."
            ),
            memory_effect=(
                "Region state must remember route closures, discovered paths, damaged landmarks, settlement access, "
                "weather danger, and revealed secret locations."
            ),
            validation_status=DeepWorldValidationStatus.VALIDATED,
            provenance={
                "origin_type": "generated_from_seed",
                "generated_by_engine": "GeographyTerrainEngine",
                "source_id": source_id,
                "seed_keys": sorted(region_seed.keys()),
            },
            compression_summary=(
                f"{name}: {dominant_terrain}; climate={climate}; danger={danger}; secret={secret}."
            ),
            terrain_signature=[
                dominant_terrain,
                "natural barriers that shape route choices",
                "terrain landmarks usable as story anchors",
            ],
            climate_signature=[
                climate,
                "weather changes that alter travel reliability",
            ],
            visual_signature=[
                region_seed.get("visual_signature", "white bark, silver fog, and dark ravines"),
                "clear silhouette for scene description",
            ],
            emotional_signature=[
                region_seed.get("emotional_signature", "wonder mixed with dread"),
                "place-based longing and danger",
            ],
            danger_signature=[
                danger,
                "hidden terrain risk",
                "route misdirection risk",
            ],
            secret_signature=[
                secret,
                "old landmarks that become plot reveal gates",
            ],
            connected_settlement_ids=region_seed.get("connected_settlement_ids", []),
            connected_route_ids=region_seed.get("connected_route_ids", []),
        )

        return {"deep_world_region": region}

    def build_region_context_patch(self, *, region: DeepWorldRegion) -> Dict[str, Any]:
        patch = {
            "deep_world_region_id": region.element_id,
            "region_name": region.name,
            "terrain_signature": region.terrain_signature,
            "climate_signature": region.climate_signature,
            "danger_signature": region.danger_signature,
            "secret_signature": region.secret_signature,
            "story_use": region.story_use,
            "character_effect": region.character_effect,
            "plot_effect": region.plot_effect,
            "memory_effect": region.memory_effect,
            "generation_hints": [
                f"Use {region.name} terrain to constrain travel and pacing.",
                "Reflect local geography in character metaphors and decisions.",
                "Do not ignore route danger, weather closure, or hidden terrain.",
                "Use region secrets only when discovery conditions are satisfied.",
            ],
            "memory_update_candidates": [
                {
                    "candidate_type": "region_state",
                    "target_element_id": region.element_id,
                    "reason": "Track route closures, discoveries, landmark damage, and revealed secrets.",
                }
            ],
        }

        return {"story_context_patch": patch}

    def validate_region(self, *, region: DeepWorldRegion) -> Dict[str, Any]:
        blockers: List[str] = []
        warnings: List[str] = []

        if not region.terrain_signature:
            blockers.append("Region is missing terrain_signature.")
        if not region.climate_signature:
            blockers.append("Region is missing climate_signature.")
        if not region.story_use:
            blockers.append("Region is missing story_use.")
        if not region.character_effect:
            blockers.append("Region is missing character_effect.")
        if not region.plot_effect:
            blockers.append("Region is missing plot_effect.")
        if not region.memory_effect:
            blockers.append("Region is missing memory_effect.")
        if not region.secret_signature:
            warnings.append("Region has no secret_signature; mystery potential may be low.")
        if not region.danger_signature:
            warnings.append("Region has no danger_signature; plot pressure may be low.")

        passed = not blockers

        return {
            "passed": passed,
            "blockers": blockers,
            "warnings": warnings,
            "region_id": region.element_id,
            "region_name": region.name,
        }

    def summarize_region(self, *, region: DeepWorldRegion) -> Dict[str, Any]:
        return {
            "success": True,
            "summary": {
                "region_id": region.element_id,
                "name": region.name,
                "terrain_signature": region.terrain_signature,
                "climate_signature": region.climate_signature,
                "danger_signature": region.danger_signature,
                "secret_signature": region.secret_signature,
                "compression_summary": region.compression_summary,
                "validation_status": region.validation_status.value,
            },
        }

    def build_region_text(self, *, region: DeepWorldRegion) -> Dict[str, str]:
        lines = [
            "Deep World Geography Region",
            f"Name: {region.name}",
            f"ID: {region.element_id}",
            "",
            "Summary:",
            region.summary,
            "",
            "Terrain Signature:",
        ]

        for item in region.terrain_signature:
            lines.append(f"- {item}")

        lines.append("")
        lines.append("Climate Signature:")
        for item in region.climate_signature:
            lines.append(f"- {item}")

        lines.append("")
        lines.append("Danger Signature:")
        for item in region.danger_signature:
            lines.append(f"- {item}")

        lines.append("")
        lines.append("Secret Signature:")
        for item in region.secret_signature:
            lines.append(f"- {item}")

        lines.extend([
            "",
            "Story Use:",
            region.story_use,
            "",
            "Character Effect:",
            region.character_effect,
            "",
            "Plot Effect:",
            region.plot_effect,
            "",
            "Memory Effect:",
            region.memory_effect,
        ])

        return {"region_text": chr(10).join(lines)}

    def _slug(self, value: str) -> str:
        return "_".join(
            part for part in value.lower().replace("-", " ").replace("/", " ").split()
            if part
        )

    def _tags(self, *, region_seed: Dict[str, Any], story_context: Dict[str, Any]) -> List[str]:
        tags = ["chunk6", "geography", "terrain", "deep_world", "story_useful_region"]

        for key in ["genre", "tone", "world_type"]:
            if story_context.get(key):
                tags.append(str(story_context[key]))

        for item in region_seed.get("tags", []):
            tags.append(str(item))

        return tags

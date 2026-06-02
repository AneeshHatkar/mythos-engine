from __future__ import annotations

from typing import Any, Dict, List

from backend.app.schemas.deep_world import (
    DeepWorldClimateSystem,
    DeepWorldPriority,
    DeepWorldValidationStatus,
)


class ClimateWeatherSimulationEngine:
    def build_climate_system(
        self,
        *,
        source_id: str,
        climate_seed: Dict[str, Any] | None = None,
        story_context: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        climate_seed = climate_seed or {}
        story_context = story_context or {}

        name = climate_seed.get("name", "Red Fog Monsoon Cycle")
        region_name = climate_seed.get("region_name", story_context.get("region_name", "Saltroot Forest"))
        climate_type = climate_seed.get("climate_type", "seasonal fog-monsoon climate")
        dominant_weather = climate_seed.get("dominant_weather", "red dawn fog and salt-heavy rain")
        dangerous_weather = climate_seed.get("dangerous_weather", "memory-thick fog that closes roads")
        sacred_weather = climate_seed.get("sacred_weather", "first bell rain after the dry salt wind")
        disaster_risk = climate_seed.get("disaster_risk", "fog surge that erases road memory")
        climate_lore = climate_seed.get(
            "climate_lore",
            "locals believe the fog remembers broken oaths because old bells ring without hands before storms.",
        )

        seasons = climate_seed.get("seasons", [
            "Dry Salt Wind",
            "Red Fog Monsoon",
            "Bell Rain Weeks",
            "White Bark Thaw",
        ])

        weather_patterns = climate_seed.get("weather_patterns", [
            dominant_weather,
            dangerous_weather,
            sacred_weather,
            disaster_risk,
        ])

        travel_effects = climate_seed.get("travel_effects", [
            "fog season closes unmarked roads",
            "caravans require bell-guides during red dawn fog",
            "bridges become unsafe after salt-heavy rain",
        ])

        crop_effects = climate_seed.get("crop_effects", [
            "saltroot herbs bloom only after bell rain",
            "ash grain fails if dry salt wind lasts too long",
            "fog moss becomes medicinal during monsoon weeks",
        ])

        ritual_effects = climate_seed.get("ritual_effects", [
            "families hang witness bells before first rain",
            "oath trials are delayed during red fog",
            "funeral tea is brewed only after white bark thaw",
        ])

        scene_atmosphere_effects = climate_seed.get("scene_atmosphere_effects", [
            "red fog turns streets into silhouettes",
            "salt rain makes metal towers hum",
            "dry winds carry bell dust through door cracks",
        ])

        climate = DeepWorldClimateSystem(
            element_id=f"climate_{source_id}_{self._slug(name)}",
            source_id=source_id,
            name=name,
            summary=(
                f"{name} is a {climate_type} affecting {region_name}. "
                f"It is defined by {dominant_weather}, threatened by {dangerous_weather}, "
                f"and remembered through local lore: {climate_lore}"
            ),
            priority=DeepWorldPriority.HIGH,
            tags=self._tags(climate_seed=climate_seed, story_context=story_context),
            metadata={
                "chunk6_step": "6.4",
                "engine": "ClimateWeatherSimulationEngine",
                "region_name": region_name,
                "climate_type": climate_type,
                "dangerous_weather": dangerous_weather,
                "sacred_weather": sacred_weather,
                "disaster_risk": disaster_risk,
                "climate_lore": climate_lore,
            },
            story_use=(
                "Controls scene timing, route access, food scarcity, ritual timing, disaster tension, "
                "travel constraints, and mythic atmosphere."
            ),
            character_effect=(
                "Characters shaped by this climate develop weather habits, seasonal fears, harvest memory, "
                "travel caution, religious interpretations of storms, and climate-based metaphors."
            ),
            plot_effect=(
                "Weather can trap characters, expose hidden roads, delay armies, ruin crops, trigger rituals, "
                "force negotiations, or reveal old historical lies."
            ),
            memory_effect=(
                "The world state must remember current season, road closures, crop damage, disaster events, "
                "ritual timing, weather-based rumors, and climate-caused settlement changes."
            ),
            validation_status=DeepWorldValidationStatus.VALIDATED,
            provenance={
                "origin_type": "generated_from_climate_seed",
                "generated_by_engine": "ClimateWeatherSimulationEngine",
                "source_id": source_id,
                "seed_keys": sorted(climate_seed.keys()),
                "story_context_keys": sorted(story_context.keys()),
            },
            compression_summary=(
                f"{name}: {climate_type}; dominant={dominant_weather}; danger={dangerous_weather}; "
                f"sacred={sacred_weather}; disaster={disaster_risk}."
            ),
            seasons=seasons,
            weather_patterns=weather_patterns,
            travel_effects=travel_effects,
            crop_effects=crop_effects,
            ritual_effects=ritual_effects,
            scene_atmosphere_effects=scene_atmosphere_effects,
        )

        return {"deep_world_climate_system": climate}

    def simulate_weather_event(
        self,
        *,
        source_id: str,
        climate: DeepWorldClimateSystem,
        event_seed: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        event_seed = event_seed or {}

        event_name = event_seed.get("event_name", "Red Fog Road Closure")
        severity = event_seed.get("severity", "high")
        affected_locations = event_seed.get("affected_locations", ["old road", "bell tower district", "forest bridge"])
        duration = event_seed.get("duration", "three nights")
        trigger = event_seed.get("trigger", "monsoon fog thickened after salt rain")

        event = {
            "weather_event_id": f"weather_event_{source_id}_{self._slug(event_name)}",
            "source_id": source_id,
            "climate_id": climate.element_id,
            "event_name": event_name,
            "severity": severity,
            "duration": duration,
            "trigger": trigger,
            "affected_locations": affected_locations,
            "travel_effect": "Routes become delayed, blocked, watched, or unsafe.",
            "settlement_effect": "Markets close early, bells guide crowds, and rumors spread through shelters.",
            "character_effect": "Characters must reveal local knowledge, fear, impatience, faith, or desperation under pressure.",
            "plot_effect": "The weather creates a timed obstacle, forced meeting, hidden route reveal, or rescue delay.",
            "memory_effect": "Future state must remember closures, injuries, rumors, damaged landmarks, and who benefited.",
            "lore_effect": "The event may be interpreted as divine warning, ancestral anger, or proof of false history.",
            "anti_genericity_signal": "Weather is tied to roads, bells, salt rain, local fear, lore, and plot timing.",
            "detail_depth_score": 0.88,
            "validation_status": "validated",
            "provenance": {
                "generated_by_engine": "ClimateWeatherSimulationEngine",
                "origin_type": "simulated_weather_event",
                "source_id": source_id,
                "climate_id": climate.element_id,
                "seed_keys": sorted(event_seed.keys()),
            },
            "compression_summary": (
                f"{event_name}: severity={severity}; duration={duration}; trigger={trigger}; "
                f"affects {', '.join(affected_locations)}."
            ),
        }

        return {"weather_event": event}

    def build_story_context_patch(
        self,
        *,
        climate: DeepWorldClimateSystem,
        weather_event: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        patch = {
            "climate_id": climate.element_id,
            "climate_name": climate.name,
            "seasons": climate.seasons,
            "weather_patterns": climate.weather_patterns,
            "travel_effects": climate.travel_effects,
            "crop_effects": climate.crop_effects,
            "ritual_effects": climate.ritual_effects,
            "scene_atmosphere_effects": climate.scene_atmosphere_effects,
            "story_use": climate.story_use,
            "character_effect": climate.character_effect,
            "plot_effect": climate.plot_effect,
            "memory_effect": climate.memory_effect,
            "generation_hints": [
                "Use climate to affect scene timing, travel, food, clothing, ritual, and mood.",
                "Do not use generic weather; connect weather to culture, lore, and plot pressure.",
                "Let characters react differently based on birthplace, class, profession, and belief.",
                "Track major weather events as memory/state updates.",
            ],
            "memory_update_candidates": [
                {
                    "candidate_type": "climate_state",
                    "target_element_id": climate.element_id,
                    "reason": "Track current season, active weather events, route closures, crop damage, and ritual timing.",
                }
            ],
        }

        if weather_event:
            patch["active_weather_event"] = weather_event
            patch["memory_update_candidates"].append(
                {
                    "candidate_type": "weather_event_state",
                    "target_element_id": weather_event["weather_event_id"],
                    "reason": "Track event duration, affected locations, consequences, and who knows/believes what happened.",
                }
            )

        return {"story_context_patch": patch}

    def validate_climate_system(self, *, climate: DeepWorldClimateSystem) -> Dict[str, Any]:
        blockers: List[str] = []
        warnings: List[str] = []

        required_lists = {
            "seasons": climate.seasons,
            "weather_patterns": climate.weather_patterns,
            "travel_effects": climate.travel_effects,
            "crop_effects": climate.crop_effects,
            "ritual_effects": climate.ritual_effects,
            "scene_atmosphere_effects": climate.scene_atmosphere_effects,
        }

        for name, values in required_lists.items():
            if not values:
                blockers.append(f"Climate system missing {name}.")

        required_text = {
            "story_use": climate.story_use,
            "character_effect": climate.character_effect,
            "plot_effect": climate.plot_effect,
            "memory_effect": climate.memory_effect,
            "compression_summary": climate.compression_summary,
        }

        for name, value in required_text.items():
            if not value or len(value.strip()) < 20:
                blockers.append(f"Climate system has shallow or missing {name}.")

        if "climate_lore" not in climate.metadata:
            warnings.append("Climate system lacks climate_lore metadata.")

        passed = not blockers

        return {
            "passed": passed,
            "blockers": blockers,
            "warnings": warnings,
            "climate_id": climate.element_id,
            "climate_name": climate.name,
        }

    def validate_weather_event(self, *, weather_event: Dict[str, Any]) -> Dict[str, Any]:
        required = [
            "weather_event_id",
            "event_name",
            "travel_effect",
            "settlement_effect",
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

        missing = [field for field in required if not weather_event.get(field)]
        shallow = []

        for field in ["character_effect", "plot_effect", "memory_effect", "lore_effect"]:
            if len(str(weather_event.get(field, ""))) < 20:
                shallow.append(field)

        passed = not missing and not shallow and float(weather_event.get("detail_depth_score", 0.0)) >= 0.75

        return {
            "passed": passed,
            "missing_fields": missing,
            "shallow_fields": shallow,
            "weather_event_id": weather_event.get("weather_event_id"),
        }

    def summarize_climate_system(self, *, climate: DeepWorldClimateSystem) -> Dict[str, Any]:
        return {
            "success": True,
            "summary": {
                "climate_id": climate.element_id,
                "name": climate.name,
                "season_count": len(climate.seasons),
                "weather_pattern_count": len(climate.weather_patterns),
                "travel_effect_count": len(climate.travel_effects),
                "ritual_effect_count": len(climate.ritual_effects),
                "compression_summary": climate.compression_summary,
            },
        }

    def build_climate_text(self, *, climate: DeepWorldClimateSystem) -> Dict[str, str]:
        lines = [
            "Deep World Climate + Weather System",
            f"Name: {climate.name}",
            f"ID: {climate.element_id}",
            "",
            "Summary:",
            climate.summary,
            "",
            "Seasons:",
        ]

        sections = [
            ("Weather Patterns", climate.weather_patterns),
            ("Travel Effects", climate.travel_effects),
            ("Crop Effects", climate.crop_effects),
            ("Ritual Effects", climate.ritual_effects),
            ("Scene Atmosphere Effects", climate.scene_atmosphere_effects),
        ]

        for item in climate.seasons:
            lines.append(f"- {item}")

        for title, values in sections:
            lines.append("")
            lines.append(title + ":")
            for item in values:
                lines.append(f"- {item}")

        lines.extend([
            "",
            "Story Use:",
            climate.story_use,
            "",
            "Character Effect:",
            climate.character_effect,
            "",
            "Plot Effect:",
            climate.plot_effect,
            "",
            "Memory Effect:",
            climate.memory_effect,
        ])

        return {"climate_text": chr(10).join(lines)}

    def _tags(self, *, climate_seed: Dict[str, Any], story_context: Dict[str, Any]) -> List[str]:
        tags = ["chunk6", "deep_world", "climate", "weather", "story_weather"]

        for key in ["genre", "tone", "world_type", "region_name"]:
            if story_context.get(key):
                tags.append(str(story_context[key]))

        for item in climate_seed.get("tags", []):
            tags.append(str(item))

        return sorted({tag.strip().lower() for tag in tags if tag and str(tag).strip()})

    def _slug(self, value: str) -> str:
        return "_".join(part for part in value.lower().replace("/", " ").replace("-", " ").split() if part)

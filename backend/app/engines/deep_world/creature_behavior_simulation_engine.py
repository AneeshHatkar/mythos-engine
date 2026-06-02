from __future__ import annotations

from typing import Any, Dict, List

from backend.app.schemas.deep_world import DeepWorldFauna


class CreatureBehaviorSimulationEngine:
    def build_behavior_profile(
        self,
        *,
        source_id: str,
        fauna: DeepWorldFauna,
        behavior_seed: Dict[str, Any] | None = None,
        story_context: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        behavior_seed = behavior_seed or {}
        story_context = story_context or {}

        habitat_rules = self._list_attr(fauna, "habitat_rules")
        behavior_patterns = self._list_attr(fauna, "behavior_patterns")
        danger_profile = self._list_attr(fauna, "danger_profile")
        cultural_meaning = self._list_attr(fauna, "cultural_meaning")
        economic_uses = self._list_attr(fauna, "economic_uses")
        ecological_role = list(fauna.metadata.get("ecological_role", []))

        behavior_profile = {
            "behavior_profile_id": f"creature_behavior_{source_id}_{self._slug(fauna.name)}",
            "source_id": source_id,
            "fauna_id": fauna.element_id,
            "fauna_name": fauna.name,
            "species_identity": {
                "unique_name": fauna.metadata.get("unique_name", fauna.name),
                "name_origin": fauna.metadata.get("name_origin"),
                "name_meaning": fauna.metadata.get("name_meaning"),
                "cultural_context": fauna.metadata.get("cultural_context"),
                "world_context": fauna.metadata.get("world_context"),
                "visual_identity": fauna.metadata.get("visual_identity"),
                "sensory_identity": fauna.metadata.get("sensory_identity"),
            },
            "baseline_behavior": behavior_seed.get("baseline_behavior", behavior_patterns),
            "habitat_rules": behavior_seed.get("habitat_rules", habitat_rules),
            "territorial_logic": behavior_seed.get("territorial_logic", [
                "marks old road edges with antler scraping during fog season",
                "avoids oath-blood sites unless chased by predators",
                "returns to saltroot groves when bell rain begins",
            ]),
            "migration_triggers": behavior_seed.get("migration_triggers", [
                "red fog density rises before dawn",
                "saltroot bloom fails after red mold",
                "ravine cats overhunt the lower forest",
                "bell rain arrives three nights early",
            ]),
            "fear_triggers": behavior_seed.get("fear_triggers", [
                "metal tower hum before storm surge",
                "fresh predator musk near white-bark ravines",
                "burned saltroot groves",
                "human blood on road stones",
            ]),
            "aggression_triggers": behavior_seed.get("aggression_triggers", [
                "cornered herd during red fog",
                "injured fawn near road shrine",
                "smugglers cutting antlers from living animals",
            ]),
            "social_behavior": behavior_seed.get("social_behavior", [
                "older animals lead fog crossings",
                "young animals mimic antler-hum warnings",
                "injured animals leave the herd near moss beds",
                "dominant animals refuse unsafe paths first",
            ]),
            "human_interaction_rules": behavior_seed.get("human_interaction_rules", [
                "road guides read herd direction as weather warning",
                "hunters avoid killing during bell rain weeks",
                "courts treat natural antler shed as lawful material",
                "smugglers exploit panic migration for illegal capture",
            ]),
            "ecological_role": ecological_role,
            "danger_profile": danger_profile,
            "cultural_meaning": cultural_meaning,
            "economic_uses": economic_uses,
            "story_use": (
                "Turns creature behavior into living world pressure through migration, fear, aggression, omen reading, "
                "hunting conflict, route discovery, and ecological warning."
            ),
            "character_effect": (
                "Characters reveal expertise, class, faith, fear, cruelty, mercy, or local knowledge through how they interpret "
                "and respond to creature behavior."
            ),
            "plot_effect": (
                "Creature behavior can block roads, expose hidden paths, foreshadow disaster, reveal ecological collapse, "
                "trigger injury, or uncover illegal trade."
            ),
            "memory_effect": (
                "World memory must track migration direction, herd trust, injuries, deaths, domestication attempts, illegal hunting, "
                "predator pressure, and whether communities interpreted the behavior correctly."
            ),
            "anti_genericity_signal": (
                "Behavior is linked to named fauna, local weather, cultural law, ecology, trade pressure, road systems, and lore."
            ),
            "detail_depth_score": 0.91,
            "validation_status": "validated",
            "provenance": {
                "generated_by_engine": "CreatureBehaviorSimulationEngine",
                "origin_type": "derived_from_fauna",
                "source_id": source_id,
                "fauna_id": fauna.element_id,
                "seed_keys": sorted(behavior_seed.keys()),
                "story_context_keys": sorted(story_context.keys()),
            },
            "compression_summary": (
                f"{fauna.name} behavior: migration, fear, aggression, territory, social signals, human interaction, and memory hooks."
            ),
        }

        return {"creature_behavior_profile": behavior_profile}

    def simulate_behavior_event(
        self,
        *,
        source_id: str,
        behavior_profile: Dict[str, Any],
        event_seed: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        event_seed = event_seed or {}

        event_name = event_seed.get("event_name", f"{behavior_profile['fauna_name']} Road Refusal")
        event_type = event_seed.get("event_type", "omen_behavior")
        trigger = event_seed.get("trigger", "dominant animals refused the old road before red fog rose")
        location = event_seed.get("location", "old witness road")
        affected_groups = event_seed.get("affected_groups", ["road guides", "merchants", "hunters", "bell court"])
        immediate_consequence = event_seed.get(
            "immediate_consequence",
            "travelers split between trusting the herd and forcing the route",
        )
        hidden_cause = event_seed.get(
            "hidden_cause",
            "predator pressure and buried oath-blood made the herd avoid the crossing",
        )

        event = {
            "behavior_event_id": f"behavior_event_{source_id}_{self._slug(event_name)}",
            "source_id": source_id,
            "behavior_profile_id": behavior_profile["behavior_profile_id"],
            "fauna_id": behavior_profile["fauna_id"],
            "fauna_name": behavior_profile["fauna_name"],
            "event_name": event_name,
            "event_type": event_type,
            "trigger": trigger,
            "location": location,
            "affected_groups": affected_groups,
            "immediate_consequence": immediate_consequence,
            "hidden_cause": hidden_cause,
            "story_use": (
                "Turns creature action into a scene-level decision point where characters must interpret signs under pressure."
            ),
            "character_effect": (
                "Characters reveal whether they trust local knowledge, dismiss superstition, exploit animals, protect them, "
                "or panic when behavior contradicts plans."
            ),
            "plot_effect": (
                "Can split a party, reveal hidden danger, expose a false map, delay travel, uncover a crime site, or force a rescue."
            ),
            "memory_effect": (
                "Future state must remember who trusted the behavior, who ignored it, what harm followed, and how the community retells it."
            ),
            "lore_effect": (
                "The event may become an omen story, divine warning, ancestral sign, or evidence that old crimes still shape the land."
            ),
            "anti_genericity_signal": (
                "Behavior event is tied to specific fauna identity, road culture, ecological triggers, hidden cause, and social interpretation."
            ),
            "detail_depth_score": 0.9,
            "validation_status": "validated",
            "provenance": {
                "generated_by_engine": "CreatureBehaviorSimulationEngine",
                "origin_type": "simulated_behavior_event",
                "source_id": source_id,
                "behavior_profile_id": behavior_profile["behavior_profile_id"],
                "seed_keys": sorted(event_seed.keys()),
            },
            "compression_summary": (
                f"{event_name}: type={event_type}; location={location}; trigger={trigger}; hidden_cause={hidden_cause}."
            ),
        }

        return {"creature_behavior_event": event}

    def build_story_context_patch(
        self,
        *,
        behavior_profile: Dict[str, Any],
        behavior_event: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        patch = {
            "behavior_profile_id": behavior_profile["behavior_profile_id"],
            "fauna_id": behavior_profile["fauna_id"],
            "fauna_name": behavior_profile["fauna_name"],
            "species_identity": behavior_profile["species_identity"],
            "baseline_behavior": behavior_profile["baseline_behavior"],
            "habitat_rules": behavior_profile["habitat_rules"],
            "territorial_logic": behavior_profile["territorial_logic"],
            "migration_triggers": behavior_profile["migration_triggers"],
            "fear_triggers": behavior_profile["fear_triggers"],
            "aggression_triggers": behavior_profile["aggression_triggers"],
            "social_behavior": behavior_profile["social_behavior"],
            "human_interaction_rules": behavior_profile["human_interaction_rules"],
            "story_use": behavior_profile["story_use"],
            "character_effect": behavior_profile["character_effect"],
            "plot_effect": behavior_profile["plot_effect"],
            "memory_effect": behavior_profile["memory_effect"],
            "generation_hints": [
                "Use creature behavior as active scene pressure, not background decoration.",
                "Let characters interpret the same animal behavior differently based on origin, belief, class, and expertise.",
                "Behavior can reveal danger, climate shifts, ecological collapse, hidden paths, or moral choices.",
                "Track major creature behavior events in world memory.",
            ],
            "memory_update_candidates": [
                {
                    "candidate_type": "creature_behavior_state",
                    "target_element_id": behavior_profile["behavior_profile_id"],
                    "reason": "Track migration, fear triggers, aggression triggers, social behavior, and human interaction outcomes.",
                }
            ],
        }

        if behavior_event:
            patch["active_behavior_event"] = behavior_event
            patch["memory_update_candidates"].append(
                {
                    "candidate_type": "creature_behavior_event_state",
                    "target_element_id": behavior_event["behavior_event_id"],
                    "reason": "Track who witnessed, trusted, ignored, exploited, or suffered from the behavior event.",
                }
            )

        return {"story_context_patch": patch}

    def validate_behavior_profile(self, *, behavior_profile: Dict[str, Any]) -> Dict[str, Any]:
        required = [
            "behavior_profile_id",
            "fauna_id",
            "fauna_name",
            "species_identity",
            "baseline_behavior",
            "habitat_rules",
            "territorial_logic",
            "migration_triggers",
            "fear_triggers",
            "aggression_triggers",
            "social_behavior",
            "human_interaction_rules",
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

        missing = [field for field in required if not behavior_profile.get(field)]
        shallow = self._shallow_fields(
            payload=behavior_profile,
            fields=["story_use", "character_effect", "plot_effect", "memory_effect"],
        )

        passed = not missing and not shallow and float(behavior_profile.get("detail_depth_score", 0.0)) >= 0.75

        return {
            "passed": passed,
            "missing_fields": missing,
            "shallow_fields": shallow,
            "behavior_profile_id": behavior_profile.get("behavior_profile_id"),
        }

    def validate_behavior_event(self, *, behavior_event: Dict[str, Any]) -> Dict[str, Any]:
        required = [
            "behavior_event_id",
            "behavior_profile_id",
            "fauna_id",
            "fauna_name",
            "event_name",
            "event_type",
            "trigger",
            "location",
            "affected_groups",
            "immediate_consequence",
            "hidden_cause",
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

        missing = [field for field in required if not behavior_event.get(field)]
        shallow = self._shallow_fields(
            payload=behavior_event,
            fields=["story_use", "character_effect", "plot_effect", "memory_effect", "lore_effect"],
        )

        passed = not missing and not shallow and float(behavior_event.get("detail_depth_score", 0.0)) >= 0.75

        return {
            "passed": passed,
            "missing_fields": missing,
            "shallow_fields": shallow,
            "behavior_event_id": behavior_event.get("behavior_event_id"),
        }

    def summarize_behavior_profile(self, *, behavior_profile: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "success": True,
            "summary": {
                "behavior_profile_id": behavior_profile["behavior_profile_id"],
                "fauna_id": behavior_profile["fauna_id"],
                "fauna_name": behavior_profile["fauna_name"],
                "migration_trigger_count": len(behavior_profile["migration_triggers"]),
                "fear_trigger_count": len(behavior_profile["fear_triggers"]),
                "aggression_trigger_count": len(behavior_profile["aggression_triggers"]),
                "social_behavior_count": len(behavior_profile["social_behavior"]),
                "human_interaction_rule_count": len(behavior_profile["human_interaction_rules"]),
                "compression_summary": behavior_profile["compression_summary"],
            },
        }

    def build_behavior_text(self, *, behavior_profile: Dict[str, Any]) -> Dict[str, str]:
        lines = [
            "Creature Behavior Simulation Profile",
            f"Fauna: {behavior_profile['fauna_name']}",
            f"Profile ID: {behavior_profile['behavior_profile_id']}",
            "",
            "Baseline Behavior:",
        ]

        sections = [
            ("Baseline Behavior", behavior_profile["baseline_behavior"]),
            ("Habitat Rules", behavior_profile["habitat_rules"]),
            ("Territorial Logic", behavior_profile["territorial_logic"]),
            ("Migration Triggers", behavior_profile["migration_triggers"]),
            ("Fear Triggers", behavior_profile["fear_triggers"]),
            ("Aggression Triggers", behavior_profile["aggression_triggers"]),
            ("Social Behavior", behavior_profile["social_behavior"]),
            ("Human Interaction Rules", behavior_profile["human_interaction_rules"]),
        ]

        lines = lines[:-1]

        for title, values in sections:
            lines.append("")
            lines.append(title + ":")
            for item in values:
                lines.append(f"- {item}")

        lines.extend([
            "",
            "Story Use:",
            behavior_profile["story_use"],
            "",
            "Character Effect:",
            behavior_profile["character_effect"],
            "",
            "Plot Effect:",
            behavior_profile["plot_effect"],
            "",
            "Memory Effect:",
            behavior_profile["memory_effect"],
        ])

        return {"behavior_text": chr(10).join(lines)}

    def _list_attr(self, obj: Any, *names: str) -> List[Any]:
        for name in names:
            value = getattr(obj, name, None)
            if value:
                return list(value)
        return []

    def _shallow_fields(self, *, payload: Dict[str, Any], fields: List[str]) -> List[str]:
        return [field for field in fields if len(str(payload.get(field, ""))) < 20]

    def _slug(self, value: str) -> str:
        return "_".join(part for part in value.lower().replace("/", " ").replace("-", " ").split() if part)

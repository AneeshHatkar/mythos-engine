from __future__ import annotations

from typing import Any, Dict, List


class WorldDetailInjectionEngine:
    """Injects world-specific details into story generation context.

    This prevents generic scenes by converting world metadata into usable
    writing anchors: laws, rituals, locations, factions, culture, artifacts,
    skills, powers, economy pressure, belief systems, and sensory details.

    It does not write prose yet. It prepares concrete world details for later
    blueprint, beat, prose, screenplay, and episode engines.
    """

    engine_name = "story_generation.world_detail_injection_engine"

    def build_world_detail_pack(
        self,
        *,
        story_context: Dict[str, Any],
    ) -> Dict[str, Any]:
        world_rules = story_context.get("world_rules", [])
        location_anchor = story_context.get("location_anchor", {})
        active_cast = story_context.get("active_cast", [])
        large_pool_summary = story_context.get("large_pool_summary", {})
        format_requirements = story_context.get("format_requirements", {})

        detail_pack = {
            "world_detail_pack_id": f"worlddetails_{story_context.get('story_context_id', 'unknown')}",
            "source_story_context_id": story_context.get("story_context_id"),
            "law_and_rule_anchors": self._law_and_rule_anchors(world_rules),
            "location_anchors": self._location_anchors(location_anchor),
            "faction_anchors": self._faction_anchors(story_context),
            "culture_anchors": self._culture_anchors(story_context),
            "ritual_anchors": self._ritual_anchors(world_rules, location_anchor),
            "economy_resource_anchors": self._economy_resource_anchors(story_context),
            "belief_system_anchors": self._belief_system_anchors(story_context),
            "skill_power_artifact_hooks": self._skill_power_artifact_hooks(story_context),
            "character_world_links": self._character_world_links(active_cast, location_anchor),
            "sensory_detail_hints": self._sensory_detail_hints(location_anchor, world_rules),
            "format_specific_world_notes": self._format_specific_notes(format_requirements),
            "large_scale_notes": self._large_scale_notes(large_pool_summary),
        }

        detail_pack["specificity_score"] = self._specificity_score(detail_pack)
        detail_pack["warnings"] = self._warnings(detail_pack)

        return {
            "success": True,
            "engine_name": self.engine_name,
            "world_detail_pack": detail_pack,
            "handoff_to_next_engine": {
                "next_engine": "story_generation.scene_blueprint_engine",
                "payload_keys": [
                    "story_context",
                    "world_detail_pack",
                    "law_and_rule_anchors",
                    "location_anchors",
                    "faction_anchors",
                    "sensory_detail_hints",
                ],
            },
        }

    def inject_into_scene_seed(
        self,
        *,
        story_context: Dict[str, Any],
        world_detail_pack: Dict[str, Any],
        scene_seed: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        scene_seed = dict(scene_seed or {})

        scene_seed.setdefault("scene_id", "scene_seed_latest")
        scene_seed["world_detail_pack_id"] = world_detail_pack.get("world_detail_pack_id")
        scene_seed["required_world_anchors"] = self._flatten_anchors(
            world_detail_pack,
            keys=[
                "law_and_rule_anchors",
                "location_anchors",
                "faction_anchors",
                "ritual_anchors",
                "skill_power_artifact_hooks",
            ],
        )
        scene_seed["sensory_detail_hints"] = world_detail_pack.get("sensory_detail_hints", [])
        scene_seed["anti_generic_world_requirements"] = self.build_anti_generic_world_requirements(
            world_detail_pack=world_detail_pack
        )["requirements"]

        return {
            "success": True,
            "engine_name": self.engine_name,
            "scene_seed": scene_seed,
        }

    def validate_world_detail_pack(self, *, world_detail_pack: Dict[str, Any]) -> Dict[str, Any]:
        blockers: List[str] = []
        warnings: List[str] = []
        passed: List[str] = []

        if not world_detail_pack.get("world_detail_pack_id"):
            blockers.append("world_detail_pack_id is missing")
        else:
            passed.append("world_detail_pack_id_present")

        if world_detail_pack.get("law_and_rule_anchors"):
            passed.append("law_and_rule_anchors_present")
        else:
            warnings.append("No law/rule anchors found.")

        if world_detail_pack.get("location_anchors"):
            passed.append("location_anchors_present")
        else:
            warnings.append("No location anchors found.")

        if world_detail_pack.get("sensory_detail_hints"):
            passed.append("sensory_detail_hints_present")
        else:
            warnings.append("No sensory detail hints found.")

        if world_detail_pack.get("specificity_score", 0.0) < 0.45:
            warnings.append("World specificity is low; later story output may feel generic.")
        else:
            passed.append("specificity_score_usable")

        return {
            "success": True,
            "engine_name": self.engine_name,
            "valid": not blockers,
            "blockers": blockers,
            "warnings": warnings,
            "passed_checks": passed,
        }

    def build_anti_generic_world_requirements(
        self,
        *,
        world_detail_pack: Dict[str, Any],
    ) -> Dict[str, Any]:
        anchors = self._flatten_anchors(
            world_detail_pack,
            keys=[
                "law_and_rule_anchors",
                "location_anchors",
                "faction_anchors",
                "culture_anchors",
                "ritual_anchors",
                "skill_power_artifact_hooks",
            ],
        )

        requirements = [
            "Use at least one world-specific rule or social constraint.",
            "Use at least one concrete location detail.",
            "Avoid generic fantasy nouns unless tied to the current world.",
        ]

        if anchors:
            requirements.append("Include at least two concrete anchors from the world detail pack.")

        if world_detail_pack.get("faction_anchors"):
            requirements.append("Show how a faction or institution changes the scene pressure.")

        if world_detail_pack.get("ritual_anchors"):
            requirements.append("Use ritual behavior or institutional ceremony as a story detail.")

        return {
            "success": True,
            "engine_name": self.engine_name,
            "requirements": requirements,
            "candidate_anchor_count": len(anchors),
            "candidate_anchors": anchors,
        }

    def summarize_world_detail_pack(self, *, world_detail_pack: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "success": True,
            "engine_name": self.engine_name,
            "summary": {
                "world_detail_pack_id": world_detail_pack.get("world_detail_pack_id"),
                "specificity_score": world_detail_pack.get("specificity_score", 0.0),
                "law_anchor_count": len(world_detail_pack.get("law_and_rule_anchors", [])),
                "location_anchor_count": len(world_detail_pack.get("location_anchors", [])),
                "faction_anchor_count": len(world_detail_pack.get("faction_anchors", [])),
                "culture_anchor_count": len(world_detail_pack.get("culture_anchors", [])),
                "ritual_anchor_count": len(world_detail_pack.get("ritual_anchors", [])),
                "skill_power_artifact_hook_count": len(world_detail_pack.get("skill_power_artifact_hooks", [])),
                "warning_count": len(world_detail_pack.get("warnings", [])),
            },
        }

    def _law_and_rule_anchors(self, world_rules: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        anchors = []
        for rule in world_rules:
            anchors.append(
                {
                    "anchor_type": "world_rule",
                    "rule_id": rule.get("rule_id"),
                    "detail": rule.get("description", ""),
                    "story_use": "This rule should create pressure, limit choices, or shape consequences.",
                    "required": bool(rule.get("required", False)),
                }
            )
        return anchors

    def _location_anchors(self, location_anchor: Dict[str, Any]) -> List[Dict[str, Any]]:
        if not location_anchor or location_anchor.get("missing"):
            return []

        name = location_anchor.get("name", "unknown location")
        location_id = location_anchor.get("location_id")
        details = location_anchor.get("details", {}) if isinstance(location_anchor.get("details", {}), dict) else {}

        anchors = [
            {
                "anchor_type": "location",
                "location_id": location_id,
                "detail": name,
                "story_use": "Ground the scene in this exact place instead of a generic room.",
            }
        ]

        for key, value in details.items():
            if key == "name":
                continue
            anchors.append(
                {
                    "anchor_type": f"location_{key}",
                    "location_id": location_id,
                    "detail": f"{key}: {value}",
                    "story_use": "Use as concrete environmental texture.",
                }
            )

        return anchors

    def _faction_anchors(self, story_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        anchors = []
        large_pool = story_context.get("large_pool_summary", {})
        faction_count = large_pool.get("faction_count", 0)

        if faction_count:
            anchors.append(
                {
                    "anchor_type": "faction_pressure",
                    "detail": f"{faction_count} faction(s) are available in this world context.",
                    "story_use": "Use institutions or factions to create social/political pressure.",
                }
            )

        for rule in story_context.get("world_rules", []):
            detail = str(rule.get("description", "")).lower()
            if "court" in detail or "rank" in detail or "law" in detail:
                anchors.append(
                    {
                        "anchor_type": "institutional_pressure",
                        "detail": rule.get("description"),
                        "story_use": "Show how institutions shape what characters can say or do.",
                    }
                )

        return anchors

    def _culture_anchors(self, story_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        anchors = []
        world_rules = story_context.get("world_rules", [])

        for rule in world_rules:
            detail = str(rule.get("description", ""))
            lower = detail.lower()
            if any(word in lower for word in ["ritual", "rank", "oath", "house", "custom", "tradition"]):
                anchors.append(
                    {
                        "anchor_type": "culture_marker",
                        "detail": detail,
                        "story_use": "Use this as a cultural behavior, taboo, or expectation.",
                    }
                )

        return anchors

    def _ritual_anchors(
        self,
        world_rules: List[Dict[str, Any]],
        location_anchor: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        anchors = []

        for rule in world_rules:
            detail = str(rule.get("description", ""))
            lower = detail.lower()
            if any(word in lower for word in ["oath", "trial", "court", "ceremony", "ritual", "proof"]):
                anchors.append(
                    {
                        "anchor_type": "ritual_or_ceremony",
                        "detail": detail,
                        "story_use": "Turn this into a visible action, object, phrase, or social rule in the scene.",
                    }
                )

        name = str(location_anchor.get("name", "")).lower()
        if "court" in name or "temple" in name or "hall" in name:
            anchors.append(
                {
                    "anchor_type": "location_ritual_behavior",
                    "detail": f"Behavior in {location_anchor.get('name')} should feel ceremonial or socially constrained.",
                    "story_use": "Use posture, silence, witness behavior, or formal speech.",
                }
            )

        return anchors

    def _economy_resource_anchors(self, story_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        anchors = []
        large_pool = story_context.get("large_pool_summary", {})

        if large_pool.get("artifact_count", 0):
            anchors.append(
                {
                    "anchor_type": "artifact_economy",
                    "detail": f"{large_pool.get('artifact_count')} artifact(s) are available.",
                    "story_use": "Use objects as proof, leverage, scarcity, or status markers.",
                }
            )

        return anchors

    def _belief_system_anchors(self, story_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        anchors = []

        for rule in story_context.get("world_rules", []):
            detail = str(rule.get("description", ""))
            if any(word in detail.lower() for word in ["oath", "god", "belief", "faith", "sacred", "curse"]):
                anchors.append(
                    {
                        "anchor_type": "belief_system",
                        "detail": detail,
                        "story_use": "Let belief shape fear, guilt, duty, or public judgment.",
                    }
                )

        return anchors

    def _skill_power_artifact_hooks(self, story_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        large_pool = story_context.get("large_pool_summary", {})
        hooks = []

        if large_pool.get("skill_count", 0):
            hooks.append(
                {
                    "anchor_type": "skill_pool",
                    "detail": f"{large_pool.get('skill_count')} skill(s) available in system.",
                    "story_use": "Select only skills relevant to the scene objective and character identity.",
                    "requires_scaling": large_pool.get("skill_count", 0) >= 100,
                }
            )

        if large_pool.get("power_count", 0):
            hooks.append(
                {
                    "anchor_type": "power_pool",
                    "detail": f"{large_pool.get('power_count')} power(s) available in system.",
                    "story_use": "Use powers through world rules and costs, not random spectacle.",
                    "requires_scaling": large_pool.get("power_count", 0) >= 100,
                }
            )

        if large_pool.get("artifact_count", 0):
            hooks.append(
                {
                    "anchor_type": "artifact_pool",
                    "detail": f"{large_pool.get('artifact_count')} artifact(s) available in system.",
                    "story_use": "Use artifacts as evidence, symbolism, leverage, or consequence triggers.",
                    "requires_scaling": large_pool.get("artifact_count", 0) >= 100,
                }
            )

        return hooks

    def _character_world_links(
        self,
        active_cast: List[Dict[str, Any]],
        location_anchor: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        links = []

        location_id = location_anchor.get("location_id")

        for character in active_cast:
            current_location_id = character.get("current_location_id")
            links.append(
                {
                    "character_id": character.get("character_id"),
                    "display_name": character.get("display_name"),
                    "current_location_id": current_location_id,
                    "scene_location_id": location_id,
                    "is_at_scene_location": bool(location_id and current_location_id == location_id),
                    "story_use": "Use presence/location to determine who can witness, speak, or act.",
                }
            )

        return links

    def _sensory_detail_hints(
        self,
        location_anchor: Dict[str, Any],
        world_rules: List[Dict[str, Any]],
    ) -> List[str]:
        hints = []

        name = str(location_anchor.get("name", "the location"))
        if location_anchor and not location_anchor.get("missing"):
            hints.extend(
                [
                    f"Use a concrete visual detail from {name}.",
                    f"Use sound or silence to show social pressure in {name}.",
                ]
            )

        for rule in world_rules[:3]:
            detail = str(rule.get("description", ""))
            if detail:
                hints.append(f"Let this rule appear through behavior, not exposition: {detail}")

        return hints

    def _format_specific_notes(self, format_requirements: Dict[str, Any]) -> List[str]:
        selected = format_requirements.get("selected_format")
        notes = []

        if selected == "screenplay":
            notes.append("World details should be visual and filmable.")
        elif selected == "novel":
            notes.append("World details may appear through internality, sensory prose, and social pressure.")
        elif selected == "game_scene":
            notes.append("World details should support choice consequences and branch logic.")
        elif selected == "multi_book_arc":
            notes.append("World details should create long-term open loops and payoff structures.")
        else:
            notes.append("World details should be concrete and tied to character action.")

        return notes

    def _large_scale_notes(self, large_pool_summary: Dict[str, Any]) -> List[str]:
        notes = []

        if large_pool_summary.get("needs_scaling_controller"):
            notes.append("Large entity pool detected; later engines should rank/filter before selecting details.")

        if large_pool_summary.get("character_count", 0) >= 100:
            notes.append("Large character pool requires cast relevance ranking.")

        if large_pool_summary.get("skill_count", 0) >= 100:
            notes.append("Large skill pool requires skill relevance ranking.")

        return notes

    def _specificity_score(self, detail_pack: Dict[str, Any]) -> float:
        score = 0.0

        weighted_keys = {
            "law_and_rule_anchors": 0.20,
            "location_anchors": 0.20,
            "faction_anchors": 0.15,
            "culture_anchors": 0.10,
            "ritual_anchors": 0.15,
            "skill_power_artifact_hooks": 0.10,
            "sensory_detail_hints": 0.10,
        }

        for key, weight in weighted_keys.items():
            if detail_pack.get(key):
                score += weight

        return round(max(0.0, min(1.0, score)), 3)

    def _warnings(self, detail_pack: Dict[str, Any]) -> List[str]:
        warnings = []

        if not detail_pack.get("law_and_rule_anchors"):
            warnings.append("No world laws/rules available for story pressure.")

        if not detail_pack.get("location_anchors"):
            warnings.append("No location anchors available; scene may feel ungrounded.")

        if not detail_pack.get("sensory_detail_hints"):
            warnings.append("No sensory hints available; prose may become abstract.")

        if detail_pack.get("specificity_score", 0.0) < 0.45:
            warnings.append("World detail specificity is low.")

        return warnings

    def _flatten_anchors(self, world_detail_pack: Dict[str, Any], keys: List[str]) -> List[Dict[str, Any]]:
        anchors: List[Dict[str, Any]] = []
        for key in keys:
            values = world_detail_pack.get(key, [])
            if isinstance(values, list):
                anchors.extend([value for value in values if isinstance(value, dict)])
        return anchors

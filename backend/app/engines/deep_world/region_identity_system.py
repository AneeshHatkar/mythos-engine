from __future__ import annotations

from typing import Any, Dict, List

from backend.app.schemas.deep_world import DeepWorldRegion


class RegionIdentitySystem:
    def build_region_identity(
        self,
        *,
        source_id: str,
        region: DeepWorldRegion,
        identity_seed: Dict[str, Any] | None = None,
        story_context: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        identity_seed = identity_seed or {}
        story_context = story_context or {}

        terrain_signature = identity_seed.get("terrain_signature") or region.terrain_signature
        climate_signature = identity_seed.get("climate_signature") or region.climate_signature
        food_signature = identity_seed.get("food_signature") or [
            "salt-bark tea",
            "fog-preserved roots",
            "thin ash bread",
        ]
        architecture_signature = identity_seed.get("architecture_signature") or [
            "bell towers used as navigation anchors",
            "low houses sealed against fog",
            "white-bark bridges over ravines",
        ]
        belief_signature = identity_seed.get("belief_signature") or [
            "bells must never be rung without a witness",
            "fog remembers broken oaths",
        ]
        danger_signature = identity_seed.get("danger_signature") or region.danger_signature
        music_art_signature = identity_seed.get("music_art_signature") or [
            "slow bell hymns",
            "carved bark memory masks",
        ]
        conflict_signature = identity_seed.get("conflict_signature") or [
            "outsiders want the buried oath road",
            "locals fear trade will expose old crimes",
        ]
        secret_signature = identity_seed.get("secret_signature") or region.secret_signature
        emotional_signature = identity_seed.get("emotional_signature") or region.emotional_signature
        visual_signature = identity_seed.get("visual_signature") or region.visual_signature

        identity = {
            "identity_id": f"region_identity_{source_id}_{region.element_id}",
            "source_id": source_id,
            "region_id": region.element_id,
            "region_name": region.name,
            "terrain_signature": terrain_signature,
            "climate_signature": climate_signature,
            "food_signature": food_signature,
            "architecture_signature": architecture_signature,
            "belief_signature": belief_signature,
            "danger_signature": danger_signature,
            "music_art_signature": music_art_signature,
            "conflict_signature": conflict_signature,
            "secret_signature": secret_signature,
            "emotional_signature": emotional_signature,
            "visual_signature": visual_signature,
            "story_use": (
                "Gives the region a reusable identity fingerprint for scenes, dialogue, "
                "culture, architecture, food, danger, conflict, and memory."
            ),
            "character_effect": (
                "Characters from this region inherit local metaphors, fears, manners, "
                "food memory, belief pressure, and visual/cultural associations."
            ),
            "plot_effect": (
                "The region identity creates specific scene constraints, local misunderstandings, "
                "secret reveal paths, social conflict, and emotionally memorable locations."
            ),
            "memory_effect": (
                "Identity details should be remembered as canon constraints for future scenes, "
                "dialogue, settlement generation, cultural rituals, and character backstory."
            ),
            "validation_status": "validated",
            "provenance": {
                "origin_type": "derived_from_region",
                "generated_by_engine": "RegionIdentitySystem",
                "source_region_id": region.element_id,
                "seed_keys": sorted(identity_seed.keys()),
                "story_context_keys": sorted(story_context.keys()),
            },
            "compression_summary": self._compression_summary(
                region_name=region.name,
                terrain_signature=terrain_signature,
                belief_signature=belief_signature,
                danger_signature=danger_signature,
                secret_signature=secret_signature,
            ),
            "generation_hints": [
                "Use region-specific food, architecture, belief, and weather metaphors in scenes.",
                "Do not describe the region with generic fantasy/place language.",
                "Show at least one sensory detail and one cultural behavior when using this region.",
                "Let local danger or belief affect character decisions.",
            ],
        }

        return {"region_identity": identity}

    def build_story_context_patch(self, *, identity: Dict[str, Any]) -> Dict[str, Any]:
        patch = {
            "region_identity_id": identity["identity_id"],
            "region_id": identity["region_id"],
            "region_name": identity["region_name"],
            "identity_fingerprint": {
                "terrain": identity["terrain_signature"],
                "climate": identity["climate_signature"],
                "food": identity["food_signature"],
                "architecture": identity["architecture_signature"],
                "belief": identity["belief_signature"],
                "danger": identity["danger_signature"],
                "music_art": identity["music_art_signature"],
                "conflict": identity["conflict_signature"],
                "secret": identity["secret_signature"],
                "emotion": identity["emotional_signature"],
                "visual": identity["visual_signature"],
            },
            "generation_hints": identity["generation_hints"],
            "character_effect": identity["character_effect"],
            "plot_effect": identity["plot_effect"],
            "memory_effect": identity["memory_effect"],
            "memory_update_candidates": [
                {
                    "candidate_type": "region_identity_state",
                    "target_element_id": identity["region_id"],
                    "reason": "Preserve region identity as canon for future scenes and character/world consistency.",
                }
            ],
        }

        return {"story_context_patch": patch}

    def validate_identity(self, *, identity: Dict[str, Any]) -> Dict[str, Any]:
        required_lists = [
            "terrain_signature",
            "climate_signature",
            "food_signature",
            "architecture_signature",
            "belief_signature",
            "danger_signature",
            "music_art_signature",
            "conflict_signature",
            "secret_signature",
            "emotional_signature",
            "visual_signature",
        ]

        blockers: List[str] = []
        warnings: List[str] = []

        for key in required_lists:
            if not identity.get(key):
                blockers.append(f"Missing required region identity list: {key}")

        required_text = [
            "story_use",
            "character_effect",
            "plot_effect",
            "memory_effect",
            "compression_summary",
        ]

        for key in required_text:
            if not identity.get(key):
                blockers.append(f"Missing required region identity text: {key}")

        if len(identity.get("generation_hints", [])) < 3:
            warnings.append("Region identity has fewer than three generation hints.")

        passed = not blockers

        return {
            "passed": passed,
            "blockers": blockers,
            "warnings": warnings,
            "identity_id": identity.get("identity_id"),
            "region_id": identity.get("region_id"),
        }

    def summarize_identity(self, *, identity: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "success": True,
            "summary": {
                "identity_id": identity["identity_id"],
                "region_name": identity["region_name"],
                "compression_summary": identity["compression_summary"],
                "terrain_count": len(identity["terrain_signature"]),
                "culture_marker_count": (
                    len(identity["food_signature"])
                    + len(identity["architecture_signature"])
                    + len(identity["belief_signature"])
                    + len(identity["music_art_signature"])
                ),
                "conflict_count": len(identity["conflict_signature"]),
                "secret_count": len(identity["secret_signature"]),
            },
        }

    def build_identity_text(self, *, identity: Dict[str, Any]) -> Dict[str, str]:
        lines = [
            "Deep World Region Identity",
            f'Region: {identity["region_name"]}',
            f'Identity ID: {identity["identity_id"]}',
            "",
            "Compression Summary:",
            identity["compression_summary"],
            "",
            "Terrain:",
        ]

        sections = [
            ("Climate", "climate_signature"),
            ("Food", "food_signature"),
            ("Architecture", "architecture_signature"),
            ("Belief", "belief_signature"),
            ("Danger", "danger_signature"),
            ("Music/Art", "music_art_signature"),
            ("Conflict", "conflict_signature"),
            ("Secret", "secret_signature"),
            ("Emotion", "emotional_signature"),
            ("Visual", "visual_signature"),
        ]

        for item in identity["terrain_signature"]:
            lines.append(f"- {item}")

        for title, key in sections:
            lines.append("")
            lines.append(f"{title}:")
            for item in identity[key]:
                lines.append(f"- {item}")

        lines.extend([
            "",
            "Story Use:",
            identity["story_use"],
            "",
            "Character Effect:",
            identity["character_effect"],
            "",
            "Plot Effect:",
            identity["plot_effect"],
            "",
            "Memory Effect:",
            identity["memory_effect"],
        ])

        return {"identity_text": chr(10).join(lines)}

    def _compression_summary(
        self,
        *,
        region_name: str,
        terrain_signature: List[str],
        belief_signature: List[str],
        danger_signature: List[str],
        secret_signature: List[str],
    ) -> str:
        terrain = terrain_signature[0] if terrain_signature else "unknown terrain"
        belief = belief_signature[0] if belief_signature else "unknown belief"
        danger = danger_signature[0] if danger_signature else "unknown danger"
        secret = secret_signature[0] if secret_signature else "unknown secret"

        return (
            f"{region_name} identity: terrain={terrain}; belief={belief}; "
            f"danger={danger}; secret={secret}."
        )

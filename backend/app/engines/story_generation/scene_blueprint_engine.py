from __future__ import annotations

from typing import Any, Dict, List, Optional

from backend.app.schemas.story_generation import SceneBlueprint


class SceneBlueprintEngine:
    """Builds scene blueprints from story context and world detail packs.

    The blueprint is the planning bridge between simulation context and actual
    drafting. It makes sure later prose/dialogue engines know the scene's
    objective, cast, stakes, location, relationship pressure, secrets, causality,
    world details, emotional turn, tension movement, and ending hook.
    """

    engine_name = "story_generation.scene_blueprint_engine"

    def build_scene_blueprint(
        self,
        *,
        story_context: Dict[str, Any],
        world_detail_pack: Dict[str, Any],
        scene_seed: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        scene_seed = scene_seed or {}

        scene_id = scene_seed.get("scene_id", "scene_latest")
        active_cast = story_context.get("active_cast", [])
        pov_character_id = self._select_pov_character(active_cast=active_cast, scene_seed=scene_seed)
        location = story_context.get("location_anchor", {})
        relationship_pressure = story_context.get("relationship_pressure", [])
        knowledge_boundaries = story_context.get("knowledge_boundaries", [])
        causal_obligations = story_context.get("causal_obligations", [])
        emotional_pressure = story_context.get("emotional_pressure", [])

        scene_purpose = self._scene_purpose(scene_seed=scene_seed, causal_obligations=causal_obligations)
        objective = self._scene_objective(scene_seed=scene_seed, active_cast=active_cast, causal_obligations=causal_obligations)
        opposition = self._opposition(active_cast=active_cast, relationship_pressure=relationship_pressure)
        stakes = self._stakes(story_context=story_context, causal_obligations=causal_obligations)
        secret_pressure = self._secret_pressure(knowledge_boundaries=knowledge_boundaries)
        relationship_pressure_text = self._relationship_pressure_text(relationship_pressure)
        emotional_turn = self._emotional_turn(emotional_pressure=emotional_pressure, relationship_pressure=relationship_pressure)
        tension_curve = self._tension_curve(
            stakes=stakes,
            secret_pressure=secret_pressure,
            relationship_pressure=relationship_pressure,
            causal_obligations=causal_obligations,
        )
        ending_hook = self._ending_hook(
            scene_seed=scene_seed,
            secret_pressure=secret_pressure,
            causal_obligations=causal_obligations,
            relationship_pressure=relationship_pressure,
        )
        required_world_details = self._required_world_details(world_detail_pack=world_detail_pack)

        blueprint = SceneBlueprint(
            blueprint_id=scene_seed.get("blueprint_id", f"blueprint_{scene_id}"),
            scene_id=scene_id,
            scene_purpose=scene_purpose,
            opening_image=self._opening_image(location=location, world_detail_pack=world_detail_pack),
            pov_character_id=pov_character_id,
            active_character_ids=[item.get("character_id") for item in active_cast if item.get("character_id")],
            location_id=location.get("location_id"),
            scene_objective=objective,
            opposition=opposition,
            stakes=stakes,
            secret_pressure=secret_pressure,
            relationship_pressure=relationship_pressure_text,
            emotional_turn=emotional_turn,
            tension_curve=tension_curve,
            ending_hook=ending_hook,
            required_world_details=required_world_details,
        )

        warnings = self._warnings(blueprint=blueprint, story_context=story_context, world_detail_pack=world_detail_pack)

        return {
            "success": True,
            "engine_name": self.engine_name,
            "scene_blueprint": blueprint,
            "scene_blueprint_dict": blueprint.model_dump(mode="json"),
            "warnings": warnings,
            "handoff_to_next_engine": {
                "next_engine": "story_generation.scene_beat_planner",
                "payload_keys": [
                    "scene_blueprint",
                    "story_context",
                    "world_detail_pack",
                    "tension_curve",
                    "required_world_details",
                ],
            },
        }

    def validate_blueprint(self, *, blueprint: SceneBlueprint) -> Dict[str, Any]:
        blockers: List[str] = []
        warnings: List[str] = []
        passed: List[str] = []

        if not blueprint.blueprint_id:
            blockers.append("blueprint_id is missing")
        else:
            passed.append("blueprint_id_present")

        if not blueprint.scene_id:
            blockers.append("scene_id is missing")
        else:
            passed.append("scene_id_present")

        if blueprint.active_character_ids:
            passed.append("active_characters_present")
        else:
            blockers.append("no active characters in blueprint")

        if blueprint.scene_objective:
            passed.append("scene_objective_present")
        else:
            blockers.append("scene objective missing")

        if blueprint.location_id:
            passed.append("location_present")
        else:
            warnings.append("location_id missing")

        if blueprint.stakes:
            passed.append("stakes_present")
        else:
            warnings.append("stakes missing")

        if blueprint.tension_curve:
            passed.append("tension_curve_present")
        else:
            warnings.append("tension curve missing")

        if blueprint.required_world_details:
            passed.append("world_details_present")
        else:
            warnings.append("world details missing; scene may become generic")

        if blueprint.ending_hook:
            passed.append("ending_hook_present")
        else:
            warnings.append("ending hook missing")

        return {
            "success": True,
            "engine_name": self.engine_name,
            "valid": not blockers,
            "blockers": blockers,
            "warnings": warnings,
            "passed_checks": passed,
        }

    def summarize_blueprint(self, *, blueprint: SceneBlueprint) -> Dict[str, Any]:
        return {
            "success": True,
            "engine_name": self.engine_name,
            "summary": {
                "blueprint_id": blueprint.blueprint_id,
                "scene_id": blueprint.scene_id,
                "pov_character_id": blueprint.pov_character_id,
                "active_character_count": len(blueprint.active_character_ids),
                "location_id": blueprint.location_id,
                "stake_count": len(blueprint.stakes),
                "secret_pressure_count": len(blueprint.secret_pressure),
                "relationship_pressure_count": len(blueprint.relationship_pressure),
                "world_detail_count": len(blueprint.required_world_details),
                "has_ending_hook": bool(blueprint.ending_hook),
                "max_tension": max(blueprint.tension_curve) if blueprint.tension_curve else 0.0,
            },
        }

    def _select_pov_character(
        self,
        *,
        active_cast: List[Dict[str, Any]],
        scene_seed: Dict[str, Any],
    ) -> Optional[str]:
        if scene_seed.get("pov_character_id"):
            return scene_seed["pov_character_id"]

        required = [item for item in active_cast if item.get("required")]
        if required:
            return required[0].get("character_id")

        if active_cast:
            return active_cast[0].get("character_id")

        return None

    def _scene_purpose(
        self,
        *,
        scene_seed: Dict[str, Any],
        causal_obligations: List[Dict[str, Any]],
    ) -> str:
        if scene_seed.get("scene_purpose"):
            return scene_seed["scene_purpose"]

        if causal_obligations:
            first = causal_obligations[0]
            return f"Pay off or advance {first.get('obligation_type', 'causal obligation')} {first.get('id', '')}."

        return "Advance the story through character choice, pressure, and consequence."

    def _scene_objective(
        self,
        *,
        scene_seed: Dict[str, Any],
        active_cast: List[Dict[str, Any]],
        causal_obligations: List[Dict[str, Any]],
    ) -> str:
        if scene_seed.get("scene_objective"):
            return scene_seed["scene_objective"]

        protagonist = active_cast[0].get("display_name", active_cast[0].get("character_id")) if active_cast else "The lead character"

        if causal_obligations:
            return f"{protagonist} must confront the consequence tied to {causal_obligations[0].get('id')}."

        return f"{protagonist} must make a meaningful choice under pressure."

    def _opposition(
        self,
        *,
        active_cast: List[Dict[str, Any]],
        relationship_pressure: List[Dict[str, Any]],
    ) -> Optional[str]:
        if relationship_pressure:
            rel = relationship_pressure[0]
            return (
                f"Relationship pressure from {rel.get('relationship_id')} creates opposition "
                f"through trust={rel.get('trust')} and pressure={rel.get('pressure_score')}."
            )

        if len(active_cast) >= 2:
            return f"{active_cast[1].get('display_name', active_cast[1].get('character_id'))} challenges the scene objective."

        return "Internal conflict and world constraints oppose the objective."

    def _stakes(
        self,
        *,
        story_context: Dict[str, Any],
        causal_obligations: List[Dict[str, Any]],
    ) -> List[str]:
        stakes = []

        for obligation in causal_obligations:
            if obligation.get("obligation_type") == "consequence":
                stakes.append(f"Consequence {obligation.get('id')} must be acknowledged or paid off.")
            else:
                stakes.append(f"Causal thread {obligation.get('id')} must remain coherent.")

        for rule in story_context.get("world_rules", [])[:2]:
            stakes.append(f"World rule pressure: {rule.get('description')}")

        if not stakes:
            stakes.append("The scene must change a relationship, reveal pressure, or move the plot forward.")

        return stakes

    def _secret_pressure(self, *, knowledge_boundaries: List[Dict[str, Any]]) -> List[str]:
        pressure = []

        for boundary in knowledge_boundaries:
            holder = boundary.get("holder_id")
            missing = boundary.get("missing_required_secret_ids", [])
            forbidden = boundary.get("forbidden_secret_reveals", [])

            if missing:
                pressure.append(f"{holder} lacks required secret knowledge: {', '.join(missing)}.")
            if forbidden:
                pressure.append(f"{holder} must not reveal: {', '.join(forbidden)}.")

        return pressure

    def _relationship_pressure_text(self, relationship_pressure: List[Dict[str, Any]]) -> List[str]:
        result = []

        for rel in relationship_pressure[:5]:
            result.append(
                f"{rel.get('relationship_id')} has pressure={rel.get('pressure_score')} "
                f"trust={rel.get('trust')} resentment={rel.get('resentment')} "
                f"betrayal_risk={rel.get('betrayal_risk')}."
            )

        return result

    def _emotional_turn(
        self,
        *,
        emotional_pressure: List[Dict[str, Any]],
        relationship_pressure: List[Dict[str, Any]],
    ) -> Optional[str]:
        if emotional_pressure:
            top = emotional_pressure[0]
            emotion = top.get("dominant_emotion")
            character_id = top.get("character_id")
            return f"{character_id}'s {emotion} must shift or leak under pressure."

        if relationship_pressure:
            return "Relationship pressure must force an emotional reaction."

        return "The scene must create a visible emotional change."

    def _tension_curve(
        self,
        *,
        stakes: List[str],
        secret_pressure: List[str],
        relationship_pressure: List[Dict[str, Any]],
        causal_obligations: List[Dict[str, Any]],
    ) -> List[float]:
        base = 0.25
        if stakes:
            base += 0.10
        if secret_pressure:
            base += 0.15
        if relationship_pressure:
            base += min(0.20, relationship_pressure[0].get("pressure_score", 0.0) * 0.20)
        if causal_obligations:
            base += 0.10

        base = max(0.1, min(0.75, base))
        return [
            round(max(0.0, min(1.0, base - 0.15)), 3),
            round(max(0.0, min(1.0, base)), 3),
            round(max(0.0, min(1.0, base + 0.18)), 3),
            round(max(0.0, min(1.0, base + 0.30)), 3),
        ]

    def _ending_hook(
        self,
        *,
        scene_seed: Dict[str, Any],
        secret_pressure: List[str],
        causal_obligations: List[Dict[str, Any]],
        relationship_pressure: List[Dict[str, Any]],
    ) -> Optional[str]:
        if scene_seed.get("ending_hook"):
            return scene_seed["ending_hook"]

        if secret_pressure:
            return "End with the secret pressure becoming harder to hide."

        if causal_obligations:
            return f"End by making {causal_obligations[0].get('id')} impossible to ignore."

        if relationship_pressure:
            return f"End with {relationship_pressure[0].get('relationship_id')} changing direction."

        return "End with a choice that creates a new consequence."

    def _opening_image(
        self,
        *,
        location: Dict[str, Any],
        world_detail_pack: Dict[str, Any],
    ) -> Optional[str]:
        location_name = location.get("name")
        sensory = world_detail_pack.get("sensory_detail_hints", [])

        if location_name and sensory:
            return f"{location_name}: {sensory[0]}"

        if location_name:
            return f"The scene opens in {location_name}."

        if sensory:
            return sensory[0]

        return "The scene opens on a concrete world-specific detail."

    def _required_world_details(self, *, world_detail_pack: Dict[str, Any]) -> List[str]:
        details = []

        for key in [
            "law_and_rule_anchors",
            "location_anchors",
            "faction_anchors",
            "culture_anchors",
            "ritual_anchors",
            "skill_power_artifact_hooks",
        ]:
            for item in world_detail_pack.get(key, [])[:3]:
                detail = item.get("detail")
                if detail and detail not in details:
                    details.append(str(detail))

        return details[:12]

    def _warnings(
        self,
        *,
        blueprint: SceneBlueprint,
        story_context: Dict[str, Any],
        world_detail_pack: Dict[str, Any],
    ) -> List[str]:
        warnings = []

        if not blueprint.active_character_ids:
            warnings.append("Blueprint has no active characters.")

        if not blueprint.required_world_details:
            warnings.append("Blueprint has no world details; scene may become generic.")

        if not blueprint.relationship_pressure:
            warnings.append("Blueprint has no relationship pressure.")

        if not blueprint.secret_pressure:
            warnings.append("Blueprint has no secret pressure.")

        if world_detail_pack.get("specificity_score", 0.0) < 0.45:
            warnings.append("World detail pack specificity is low.")

        if story_context.get("readiness", {}).get("ready_for_blueprint") is False:
            warnings.append("Story context was not fully ready for blueprinting.")

        return warnings
